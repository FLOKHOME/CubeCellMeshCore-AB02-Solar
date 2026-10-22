# Git-Workflow für mehrere Windows-Rechner

## Repository und Remotes

- `origin`: `https://github.com/FLOKHOME/CubeCellMeshCore-AB02-Solar.git` – eigener Fork.
- `upstream`: `https://github.com/atomozero/CubeCellMeshCore.git` – Originalprojekt.
- `main`: Referenz der nachgewiesen funktionierenden Funk-Basis.
- `feature/oled-diagnostics`: OLED-/LED-Entwicklung, anfangs identisch zu `main`.
- `docs/project-documentation`: Dokumentationsänderungen separat von der Firmware.

```cmd
git status -sb
git remote -v
git branch -vv
```

## Neue Arbeit beginnen

Vor Branch-Wechsel stets `git status` kontrollieren. Untracked lokale Skripte (`??`) werden durch `git switch` **nicht automatisch gelöscht**, können aber bei Namenskonflikten stören.

```cmd
git switch main
git pull --ff-only origin main
git switch -c feature/name
```

Falls der Branch schon existiert, `git switch feature/name` verwenden, nicht nochmals `-c`.

## Dateien gezielt committen

```cmd
git status
git add src/main.cpp src/main.h
git diff --cached
git commit -m "Explain change"
git push -u origin HEAD
```

**Keine** temporären `.bak-*`-Dateien, `firmware.*`-Buildoutputs, privaten Schlüssel, Passwortdateien, USB-Logs mit personenbezogenen Informationen oder Token-Dateien veröffentlichen. `git add -A` vor dem Commit nur nach bewusstem Audit verwenden.

## Pull Request

Änderungen auf Feature-Branch pushen, in GitHub **Compare & pull request** wählen und nach Review nach `main` übernehmen. Bei Zweitrechner nach Merge:

```cmd
git switch main
git pull --ff-only origin main
```

## Commit-E-Mail prüfen

Der ursprüngliche Git-Commit wurde mit einer von Windows automatisch ermittelten **geschäftlichen E-Mail-Adresse** erstellt. Bei öffentlichen Repositories können Commit-Adressen dauerhaft sichtbar sein. Für zukünftige Commits eine GitHub-`noreply`-Adresse oder eine bewusst gewählte öffentliche Adresse setzen:

```cmd
git config --global user.name "Dein Anzeigename"
git config --global user.email "deine-noreply-adresse"
```

Die vorhandene Commit-Historie nicht unüberlegt per Force-Push überschreiben; bei Bedarf erst einen kontrollierten Plan zur Änderung der Autorinformationen festlegen.

## Lizenz und Herkunft

Der Fork behält den Upstream-MIT-Lizenztext und die Git-Historie. Lizenznotizen und historische Changelog-Einträge nicht löschen. Quelle der ursprünglichen Dokumentation: `docs/UPSTREAM_README.md`.
