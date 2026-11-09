"""Override chosen keys in a translation with values from a patch file.

Every patched key must exist in the English baseline, so a typo in a key name
fails loudly instead of adding a dead line.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check import readProps  # noqa: E402
from unify import writeProps  # noqa: E402


def main() -> None:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("patch", type=Path)
	parser.add_argument("--en", type=Path, required=True)
	parser.add_argument("--zh", type=Path, required=True)
	args = parser.parse_args()
	map_en, map_zh, map_patch = readProps(args.en), readProps(args.zh), readProps(args.patch)
	list_unknown = [k for k in map_patch if k not in map_en or k not in map_zh]
	if list_unknown:
		sys.exit("unknown keys: " + ", ".join(list_unknown))
	writeProps(args.zh, args.zh, {**map_zh, **map_patch})
	print(f"{len(map_patch)} keys patched")


if __name__ == "__main__":
	main()
