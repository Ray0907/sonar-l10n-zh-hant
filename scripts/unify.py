"""Make one term use one zh form across the whole translation.

unify.tsv has one rule per line: english-regex <TAB> from <TAB> to.
A rule only touches keys whose English value matches the regex, so the same zh
word in an unrelated sentence stays as it is. Use --preview to see the changes
without writing.
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check import readProps  # noqa: E402


def loadRules(path_file: Path) -> list[tuple[re.Pattern, str, str]]:
	list_rule = []
	for line in path_file.read_text(encoding="utf-8").splitlines():
		if line.strip() and not line.startswith("#"):
			pattern, text_from, text_to = line.split("\t")[:3]
			list_rule.append((re.compile(pattern, re.I), text_from, text_to))
	return list_rule


def applyRules(map_en: dict[str, str], map_zh: dict[str, str], list_rule) -> tuple[dict, list]:
	map_new, list_log = dict(map_zh), []
	for pattern, text_from, text_to in list_rule:
		for key, text_zh in map_new.items():
			if key in map_en and pattern.search(map_en[key]) and text_from in text_zh:
				map_new[key] = text_zh.replace(text_from, text_to)
				list_log.append((pattern.pattern, text_from, text_to, key))
	return map_new, list_log


def writeProps(path_out: Path, path_in: Path, map_new: dict[str, str]) -> None:
	"""Rewrite only the changed values and keep every other line byte for byte."""
	list_line = []
	for line in path_in.read_text(encoding="utf-8").splitlines():
		key = line.split("=", 1)[0].strip() if "=" in line else None
		list_line.append(f"{key}={map_new[key]}" if key in map_new else line)
	path_out.write_text("\n".join(list_line) + "\n", encoding="utf-8")


def main() -> None:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("rules", type=Path)
	parser.add_argument("--en", type=Path, required=True)
	parser.add_argument("--zh", type=Path, required=True)
	parser.add_argument("--preview", action="store_true")
	args = parser.parse_args()
	map_en, map_zh = readProps(args.en), readProps(args.zh)
	map_new, list_log = applyRules(map_en, map_zh, loadRules(args.rules))
	for pattern, text_from, text_to, key in list_log[:400]:
		print(f"{pattern:16} {text_from} -> {text_to}   {key}")
	print(f"{len(list_log)} replacements in {len({k for *_, k in list_log})} keys")
	if not args.preview:
		writeProps(args.zh, args.zh, map_new)


if __name__ == "__main__":
	main()
