"""List proper-noun candidates found in the English bundles.

A candidate is a CamelCase word, an ALL-CAPS word, or a capitalized word that
appears mid-sentence and never appears in lower case anywhere in the baseline.
A human reviews the output and saves the approved terms to protected.txt.
"""

import argparse
import re
from collections import Counter
from pathlib import Path

CAMEL = re.compile(r"\b[A-Z][a-z0-9]+(?:[A-Z][A-Za-z0-9]*)+\b")
ALLCAPS = re.compile(r"\b[A-Z]{2,}[0-9]*\b")
MID_CAP = re.compile(r"(?<=[a-z,] )[A-Z][a-z]{2,}\b")
PLACEHOLDER = re.compile(r"\{[^}]*\}|<[^>]*>|%[sd]|\\n")


def readValues(path_file: Path) -> list[str]:
	list_value = []
	for line in path_file.read_text(encoding="utf-8").splitlines():
		if line and not line.startswith("#") and "=" in line:
			list_value.append(PLACEHOLDER.sub(" ", line.split("=", 1)[1]))
	return list_value


def mine(list_value: list[str]) -> Counter:
	text_all = "\n".join(list_value)
	set_lower = set(re.findall(r"\b[a-z][a-z]+\b", text_all))
	count_term: Counter = Counter()
	for value in list_value:
		count_term.update(CAMEL.findall(value))
		count_term.update(ALLCAPS.findall(value))
		for word in MID_CAP.findall(value):
			if word.lower() not in set_lower:
				count_term[word] += 1
	return count_term


def main() -> None:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("bundles", nargs="+", type=Path)
	parser.add_argument("--min", type=int, default=1, dest="count_min")
	args = parser.parse_args()
	list_value = [v for path in args.bundles for v in readValues(path)]
	for term, count in sorted(mine(list_value).items(), key=lambda kv: (-kv[1], kv[0])):
		if count >= args.count_min:
			print(f"{count}\t{term}")


if __name__ == "__main__":
	main()
