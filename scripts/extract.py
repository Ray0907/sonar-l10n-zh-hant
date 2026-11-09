"""Copy the English l10n bundles out of a SonarQube install, byte for byte.

The English bundles are the baseline. Re-run this against a newer SonarQube to
get the new baseline, then run check.py to see what is missing.
"""

import argparse
import re
import zipfile
from pathlib import Path

BUNDLE_PATTERN = re.compile(r"^org/sonar/l10n/([A-Za-z0-9_]+)\.properties$")


def listJars(path_app: Path, path_ext: Path) -> list[Path]:
	return [path_app, *sorted(path_ext.glob("*.jar"))]


def extractBundles(path_jar: Path, path_out: Path) -> list[str]:
	list_name = []
	with zipfile.ZipFile(path_jar) as zip_jar:
		for name_entry in zip_jar.namelist():
			match = BUNDLE_PATTERN.match(name_entry)
			if not match:
				continue
			name_bundle = match.group(1)
			(path_out / f"{name_bundle}.properties").write_bytes(zip_jar.read(name_entry))
			list_name.append(f"{name_bundle}  <-  {path_jar.name}")
	return list_name


def main() -> None:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("--app-jar", type=Path, required=True)
	parser.add_argument("--ext-dir", type=Path, required=True)
	parser.add_argument("--out", type=Path, default=Path("en"))
	args = parser.parse_args()
	args.out.mkdir(parents=True, exist_ok=True)
	list_all = []
	for path_jar in listJars(args.app_jar, args.ext_dir):
		list_all += extractBundles(path_jar, args.out)
	(args.out / "SOURCES.txt").write_text("\n".join(sorted(list_all)) + "\n", encoding="utf-8")
	print("\n".join(sorted(list_all)))


if __name__ == "__main__":
	main()
