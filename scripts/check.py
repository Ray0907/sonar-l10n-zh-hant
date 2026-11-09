"""Check a zh_Hant bundle against its English baseline. No AI involved.

Errors (exit code 1): placeholder mismatch, protected term not kept verbatim,
key that does not exist in the baseline. Reports: missing and untranslated keys.
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

PRINTF = re.compile(r"%[sd]")
ICU_TYPES = ("select", "plural", "selectordinal")
TAG = re.compile(
	r"</?(?:a|b|br|code|em|i|kbd|li|link|ol|p|pre|small|span|strong|sub|sup|u|ul|div|h[1-6])"
	r"(?:\s[^>]*)?/?>"
)


def readProps(path_file: Path) -> dict[str, str]:
	"""Parse a .properties file: comments, continuation lines, key=value."""
	map_prop: dict[str, str] = {}
	text_buffer = ""
	for line in path_file.read_text(encoding="utf-8").splitlines():
		line = text_buffer + line.lstrip() if text_buffer else line
		text_buffer = ""
		count_slash = len(line) - len(line.rstrip("\\"))
		if count_slash % 2 == 1:
			text_buffer = line[:-1]
			continue
		if not line or line[0] in "#!" or "=" not in line:
			continue
		key, value = line.split("=", 1)
		map_prop[key.strip()] = value
	return map_prop


def readProtected(path_file: Path) -> list[str]:
	if not path_file.exists():
		return []
	return [t.strip() for t in path_file.read_text(encoding="utf-8").splitlines() if t.strip()]


def hasTerm(term: str, text: str) -> bool:
	return re.search(rf"(?<![A-Za-z0-9]){re.escape(term)}(?![A-Za-z0-9])", text) is not None


def branchBodies(text: str) -> list[str]:
	"""Return the {body} of each branch in the tail of an ICU select or plural."""
	list_body, depth, start = [], 0, 0
	for pos, char in enumerate(text):
		if char == "{":
			if depth == 0:
				start = pos + 1
			depth += 1
		elif char == "}" and depth > 0:
			depth -= 1
			if depth == 0:
				list_body.append(text[start:pos])
	return list_body


def extractArgs(text: str) -> set[str]:
	"""Argument names of a MessageFormat string. Words inside branch bodies are text."""
	set_name = set(PRINTF.findall(text))
	pos = 0
	while pos < len(text):
		if text[pos] != "{":
			pos += 1
			continue
		depth, end = 1, pos + 1
		while end < len(text) and depth:
			depth += (text[end] == "{") - (text[end] == "}")
			end += 1
		list_part = text[pos + 1:end - 1].split(",", 2)
		set_name.add(list_part[0].strip())
		if len(list_part) == 3 and list_part[1].strip() in ICU_TYPES:
			for body in branchBodies(list_part[2]):
				set_name |= extractArgs(body)
		pos = end
	return set_name


def checkKey(key: str, text_en: str, text_zh: str, list_protected: list[str]) -> list[str]:
	list_error = []
	if extractArgs(text_en) != extractArgs(text_zh):
		list_error.append(f"placeholder mismatch: {key}")
	if sorted(TAG.findall(text_en)) != sorted(TAG.findall(text_zh)):
		list_error.append(f"html tag mismatch: {key}")
	if text_en[len(text_en.rstrip()):] != text_zh[len(text_zh.rstrip()):]:
		list_error.append(f"trailing whitespace differs: {key}")
	for term in list_protected:
		if hasTerm(term, text_en) and term not in text_zh:
			list_error.append(f"protected term '{term}' missing: {key}")
	return list_error


def readForbidden(path_ruleset: Path, path_glossary: Path) -> list[tuple[str, str]]:
	"""Unambiguous zhtw-mcp cross-strait rules, minus the terms the glossary avoids."""
	list_avoid = [r.split("\t")[1].lower() for r in path_glossary.read_text(encoding="utf-8")
		.splitlines() if r.startswith("avoid\t")]
	list_rule = json.loads(path_ruleset.read_text(encoding="utf-8"))["spelling_rules"]
	list_pair = []
	for rule in list_rule:
		english = rule.get("english", "").lower()
		if (rule.get("type") != "cross_strait" or not rule.get("to") or rule.get("context_clues")
			or len(rule["from"]) < 2 or rule["from"] in rule["to"][0]
			or any(a in english for a in list_avoid)):
			continue
		list_pair.append((rule["from"], rule["to"][0]))
	return list_pair


def countForbidden(map_zh: dict[str, str], list_pair: list[tuple[str, str]]) -> Counter:
	count_hit: Counter = Counter()
	for text_zh in map_zh.values():
		for term_from, term_to in list_pair:
			if term_from in text_zh:
				count_hit[f"{term_from} -> {term_to}"] += 1
	return count_hit


def main() -> None:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("name_bundle", help="for example: core")
	parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
	parser.add_argument("--ruleset", type=Path, help="zhtw-mcp assets/ruleset.json")
	parser.add_argument("--en", type=Path, help="override English file, for one batch")
	parser.add_argument("--zh", type=Path, help="override translation file, for one batch")
	args = parser.parse_args()
	map_en = readProps(args.en or args.root / "en" / f"{args.name_bundle}.properties")
	map_zh = readProps(args.zh or args.root / "zh" / f"{args.name_bundle}_zh_Hant.properties")
	list_protected = readProtected(args.root / "protected.txt")
	list_error = [f"unknown key: {k}" for k in map_zh if k not in map_en]
	for key, text_zh in map_zh.items():
		if key in map_en:
			list_error += checkKey(key, map_en[key], text_zh, list_protected)
	list_missing = [k for k in map_en if k not in map_zh]
	list_same = [k for k in map_zh if k in map_en and map_zh[k] == map_en[k]]
	print(f"keys {len(map_en)}  translated {len(map_zh)}  missing {len(list_missing)}"
		f"  identical-to-English {len(list_same)}  errors {len(list_error)}")
	print("\n".join(list_error[:50]))
	if args.ruleset:
		count_hit = countForbidden(map_zh, readForbidden(args.ruleset, args.root / "glossary.tsv"))
		print(f"forbidden-term lines {sum(count_hit.values())}  distinct {len(count_hit)}")
		print("\n".join(f"{n:4d}  {t}" for t, n in count_hit.most_common(15)))
	sys.exit(1 if list_error else 0)


if __name__ == "__main__":
	main()
