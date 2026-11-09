#!/bin/sh
# Build the language pack jar with javac and jar. No Maven.
# Usage: ./build.sh <sonar-application.jar> <version>
set -eu

APP_JAR="$1"
VERSION="$2"
ROOT="$(cd "$(dirname "$0")" && pwd)"
WORK="$ROOT/dist/work"
OUT="$ROOT/dist/sonar-l10n-zhhant-$VERSION.jar"

rm -rf "$WORK" && mkdir -p "$WORK/classes" "$WORK/res/org/sonar/l10n"

javac --release 21 -cp "$APP_JAR" -d "$WORK/classes" \
	"$ROOT"/plugin/org/sonar/plugins/l10nzhhant/*.java

for f in "$ROOT"/zh/*_zh_Hant.properties; do
	[ -e "$f" ] && cp "$f" "$WORK/res/org/sonar/l10n/"
done

cat > "$WORK/MANIFEST.MF" <<EOF
Manifest-Version: 1.0
Plugin-Key: l10nzhhant
Plugin-Name: Traditional Chinese Pack (zh-TW)
Plugin-Version: $VERSION
Plugin-Class: org.sonar.plugins.l10nzhhant.L10nZhHantPlugin
Plugin-Description: Traditional Chinese (Taiwan) language pack
Plugin-Homepage: https://github.com/Ray0907/sonar-l10n-zh-hant
Plugin-License: GNU LGPL 3
Plugin-Organization: Ray Tien
Sonar-Version: 9.8.0.203
EOF

jar --create --file "$OUT" --manifest "$WORK/MANIFEST.MF" \
	-C "$WORK/classes" . -C "$WORK/res" .
echo "$OUT"
