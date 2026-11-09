"""Count which zh variant each translated string uses for a term.

variants.tsv has one term per line: english <TAB> variant1|variant2|...
For every term the script counts the keys whose English value contains the term
(whole word, any case) and, per variant, how many of those keys use it.
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check import readProps  # noqa: E402


def loadTerms(path_file: Path) -> list[tuple[str, list[str]]]:
	list_term = []
	for line in path_file.read_text(encoding="utf-8").splitlines():
		if line.strip() and not line.startswith("#"):
			term, variants = line.split("\t", 1)
			list_term.append((term.strip(), [v.strip() for v in variants.split("|")]))
	return list_term


def report(map_en: dict[str, str], map_zh: dict[str, str], term: str, list_variant: list[str]):
	pattern = re.compile(rf"(?<![A-Za-z]){re.escape(term)}s?(?![A-Za-z])", re.I)
	list_key = [k for k, v in map_en.items() if k in map_zh and pattern.search(v)]
	print(f"{term}  ({len(list_key)} keys)")
	for variant in list_variant:
		list_hit = [k for k in list_key if variant in map_zh[k]]
		sample = ", ".join(list_hit[:3])
		print(f"  {len(list_hit):4d}  {variant}   e.g. {sample}")
	count_other = sum(1 for k in list_key if not any(v in map_zh[k] for v in list_variant))
	print(f"  {count_other:4d}  (none of the variants)")


def main() -> None:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("variants", type=Path)
	parser.add_argument("--en", type=Path, required=True)
	parser.add_argument("--zh", type=Path, required=True)
	args = parser.parse_args()
	map_en, map_zh = readProps(args.en), readProps(args.zh)
	for term, list_variant in loadTerms(args.variants):
		report(map_en, map_zh, term, list_variant)


if __name__ == "__main__":
	main()
