"""Check a zh_Hant bundle against its English baseline. No AI involved.

Errors (exit code 1): placeholder mismatch, protected term not kept verbatim,
key that does not exist in the baseline. Reports: missing and untranslated keys.
"""

import argparse
import re
import sys
from pathlib import Path

PLACEHOLDER = re.compile(r"\{[^}]*\}|%[sd]")


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


def checkKey(key: str, text_en: str, text_zh: str, list_protected: list[str]) -> list[str]:
	list_error = []
	if sorted(PLACEHOLDER.findall(text_en)) != sorted(PLACEHOLDER.findall(text_zh)):
		list_error.append(f"placeholder mismatch: {key}")
	for term in list_protected:
		if hasTerm(term, text_en) and term not in text_zh:
			list_error.append(f"protected term '{term}' missing: {key}")
	return list_error


def main() -> None:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("name_bundle", help="for example: core")
	parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
	args = parser.parse_args()
	map_en = readProps(args.root / "en" / f"{args.name_bundle}.properties")
	map_zh = readProps(args.root / "zh" / f"{args.name_bundle}_zh_Hant.properties")
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
	sys.exit(1 if list_error else 0)


if __name__ == "__main__":
	main()
