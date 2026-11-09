# sonar-l10n-zhtw

A Traditional Chinese (Taiwan) language pack for SonarQube Community Build.

## Terminology

- Terms follow [zhtw-mcp](https://github.com/sysprog21/zhtw-mcp). When zhtw-mcp has a suggestion, the pack uses it.
- When a term is hard to translate, the pack keeps the English original.
- Proper nouns, such as GitHub and GitLab, stay in English. See `protected.txt`.
- Chosen terms are in `glossary.tsv`. Rules that make one term look the same everywhere are in `unify.tsv`.

## Scope

The pack translates these bundles:

| Bundle | Keys |
|---|---|
| `core` | 5,089 |
| `php` | 40 (rule parameter descriptions) |
| `authbitbucket` | 2 |

The translations are model drafts. A person has not reviewed each line.

## Limits

SonarQube sends to the browser only the keys that exist in its English bundle. The web frontend also has text that is fixed in its JavaScript, for example `Analysis`, `Policies`, `Reporting` and `Quality gate history`. A language pack cannot translate this text.

Rule names and rule descriptions are inside the analyzer plugins. This pack does not translate them.

## Build

Requirements: JDK 21 and Python 3.

```bash
./build.sh <path-to-sonar-application.jar> <version>
```

The jar is written to `dist/sonar-l10n-zhtwpack-<version>.jar`.

To install it, put the jar in `extensions/plugins/` and restart SonarQube. Install only one pack at a time. Other packs also define `core_zh_Hant`.

## Check

```bash
python3 scripts/check.py core --ruleset <zhtw-mcp>/assets/ruleset.json
```

The check compares each translation with the English key. It reports changed placeholders, changed HTML tags, trailing spaces, unprotected proper nouns, and terms that zhtw-mcp does not allow.

## Update for a new SonarQube version

1. Run `scripts/extract.py --app-jar <sonar-application.jar> --ext-dir <plugin jar folder>` to copy the English bundles from the new install.
2. Translate the new or changed keys. Use `scripts/patch.py` to apply them.
3. Run `scripts/unify.py unify.tsv --en <en file> --zh <zh file>` and `scripts/check.py core`.
4. Run `./build.sh` against the new jar.

## License

GNU LGPL 3. See `LICENSE`.
