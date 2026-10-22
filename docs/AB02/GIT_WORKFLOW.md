# Git-Workflow für mehrere Windows-Rechner

**Stand: 22.10.2026.** Fork: `FLOKHOME/CubeCellMeshCore-AB02-Solar`.

## Branches und Herkunft

- `origin`: eigener Fork auf GitHub.
- `upstream`: [`atomozero/CubeCellMeshCore`](https://github.com/atomozero/CubeCellMeshCore) (MIT).
- `main`: funkerprobte Basis `v0.7.0-ph123`, inklusive bereits integrierter Projektdokumentation.
- `feature/oled-diagnostics`: **OLED-Taster, LED-Abschaltung, fünf Regionen und EEPROM-Persistenz**, auf GitHub gesichert mit Commit `bf9c48b`.
- `docs/project-documentation`: früherer Dokumentationszweig; dessen Inhalte wurden im Projekt bereits nach `main` übernommen.

```cmd
git status -sb
git remote -v
git branch -vv
```

## Änderungen sicher committen

Vor Branchwechsel `git status -sb` prüfen. Nicht versionierte Skripte und Backups (`??`) bleiben lokal, können aber bei Dateikonflikten stören.

Dieses Dokumentationspaket wird **auf `feature/oled-diagnostics`** angewendet. Vor `--apply` bietet das mitgelieferte Python-Skript eine reine Prüfung und eine Schutzkopie; bei unerwartet geänderten Dokumentationsdateien bricht es ab.

Anschließend nur die inhaltlich geprüften Dateien hinzufügen:

```cmd
git add README.md CHANGELOG.md FEATURES.md docs/AB02/BUILD_WINDOWS.md docs/AB02/CONFIGURATION.md docs/AB02/TEST_REPORT.md docs/AB02/ROADMAP.md docs/AB02/HARDWARE_SOLAR.md docs/AB02/COMPATIBILITY.md docs/AB02/GIT_WORKFLOW.md
git diff --cached --check
git diff --cached --stat
git commit -m "Document verified OLED and persistent region features"
git push origin feature/oled-diagnostics
```

**Nicht** `git add .` verwenden, solange lokale Recovery-, Provisionierungs- oder Profildateien nicht auditiert wurden. Keine `.bak`-Dateien, lokalen Flash-Binaries, privaten Schlüssel, Tokens, Passwörter, personenbezogenen Logs oder sensiblen Koordinaten veröffentlichen.

## Pull Request und Release

Nach einem neuen Funk-Regressionstest für den aktuellen Firmware-Commit kann ein Pull Request von `feature/oled-diagnostics` nach `main` vorbereitet werden. Erst nach Review und Test ein Release-Tag vergeben. Ein grüner Build und ein funktionierendes OLED allein sind noch **keine vollständige Funk-/Solar-Freigabe**.

## Git-Identität und Lizenz

Für öffentliche Commits bewusst eine GitHub-`noreply`-Adresse oder geeignete öffentliche Adresse verwenden. Die MIT-Lizenz und Copyright-Hinweise des Upstream-Projekts nicht entfernen; die ursprüngliche README liegt unter `docs/UPSTREAM_README.md`.
