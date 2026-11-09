"""Split the English bundle into work batches, and merge translated batches.

split: writes work/batch_NN.properties (key=value, English) in baseline order.
merge: reads work/out_NN.properties and writes zh/<bundle>_zh_Hant.properties
in baseline order. Keys missing from the outputs stay untranslated.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check import readProps  # noqa: E402


def splitBundle(path_root: Path, name_bundle: str, size_batch: int) -> int:
	map_en = readProps(path_root / "en" / f"{name_bundle}.properties")
	list_key = list(map_en)
	path_work = path_root / "work"
	path_work.mkdir(exist_ok=True)
	count_batch = 0
	for start in range(0, len(list_key), size_batch):
		list_line = [f"{k}={map_en[k]}" for k in list_key[start:start + size_batch]]
		count_batch += 1
		(path_work / f"batch_{count_batch:02d}.properties").write_text(
			"\n".join(list_line) + "\n", encoding="utf-8")
	return count_batch


def mergeBundle(path_root: Path, name_bundle: str) -> int:
	map_en = readProps(path_root / "en" / f"{name_bundle}.properties")
	map_zh: dict[str, str] = {}
	for path_out in sorted((path_root / "work").glob("out_*.properties")):
		map_zh.update(readProps(path_out))
	list_line = [f"{k}={map_zh[k]}" for k in map_en if k in map_zh]
	(path_root / "zh" / f"{name_bundle}_zh_Hant.properties").write_text(
		"\n".join(list_line) + "\n", encoding="utf-8")
	return len(list_line)


def main() -> None:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("action", choices=["split", "merge"])
	parser.add_argument("name_bundle")
	parser.add_argument("--size", type=int, default=640)
	parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
	args = parser.parse_args()
	if args.action == "split":
		print(splitBundle(args.root, args.name_bundle, args.size), "batches")
	else:
		print(mergeBundle(args.root, args.name_bundle), "keys merged")


if __name__ == "__main__":
	main()
