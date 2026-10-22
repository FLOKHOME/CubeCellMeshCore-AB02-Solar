# CubeCellMeshCore – HTCC-AB02 Solar Repeater

> **Community-Fork / experimentell.** Diese Firmware ist **nicht** die offizielle MeshCore-Firmware und auch kein vollständiger Port von MeshCore 1.18. Bisher bestätigt sind Betrieb, Funkverkehr und Fern-Ping mit einem **Heltec CubeCell HTCC-AB02 V1.0**. Gezielte 2-/3-Byte-Multihop-Tests und ein sicherer Solar-Dauerbetrieb stehen noch aus.

Dieses Repository ist ein Fork von **[atomozero/CubeCellMeshCore](https://github.com/atomozero/CubeCellMeshCore)**. Es dokumentiert die Weiterentwicklung für das **HTCC-AB02 (ASR6502/SX1262, EU868)** mit erweiterten MeshCore-Pfadkennungen und dem Ziel, einen möglichst günstigen Solar-Repeater aus vorhandenen Bauteilen zu bauen.

## Status (22.10.2026)

| Bereich | Stand |
| --- | --- |
| Repeater auf HTCC-AB02, LoRa RX/TX/Forward | **Auf Hardware getestet** |
| MeshCore-Erkennung und Ping mit KiekR | **Auf Hardware getestet** (RTT 667 ms) |
| Automatischer Clock-Sync über Zero-Hop-Advert | **Auf Hardware beobachtet** |
| Erweiterte 1-/2-/3-Byte-Pfadkennungen | **Implementiert, Build und Basisfunk getestet** – gezielter Multihop-Nachweis fehlt |
| OLED auf USER, Abschalten nach ca. 10 s | **Auf früherem Entwicklungsgerät bestätigt**, Quellstand **noch nicht** im aktuellen `main`-Branch |
| RGB-Status-LED | **Noch aktiv**; Abschaltung offen |
| Solarpanel, Akkus, Langzeitbetrieb | **Noch nicht elektrisch erprobt** |

### Nachweislich reproduzierbarer Basis-Build (`main`)

- Firmwarekennung: `CubeCellMeshCore v0.7.0-ph123 EU868`.
- Board-ID: `cubecell_board_plus`.
- Build: **126.712 / 131.072 Byte Flash (96,7 %)** und **8.584 / 16.384 Byte RAM (52,4 %)**.
- Das Build-Ergebnis wurde am 22.10.2026 auf einem zweiten Windows-PC **bytegenau für RAM/Flash reproduziert**.
- Commit der ursprünglichen AB02-Anpassung im Fork: `99e369f`.
- Ein erfolgreicher Build belegt noch keine vollständige Funk- oder Protokollkompatibilität.

## Schnellstart – Windows CMD

Benötigt werden **Git**, **Python 3** und **PlatformIO Core**, außerdem vor Funkbetrieb eine geeignete **868-MHz-Antenne**.

```cmd
py --version
py -m platformio --version
git --version
git clone https://github.com/FLOKHOME/CubeCellMeshCore-AB02-Solar.git
cd CubeCellMeshCore-AB02-Solar
py -m platformio run -e cubecell_board_plus
```

Falls PlatformIO fehlt:

```cmd
py -m pip install --user -U platformio
```

Nur nach erfolgreichem Build und Prüfung des richtigen Boards und COM-Ports flashen:

```cmd
py -m platformio device list
py -m platformio run -e cubecell_board_plus -t upload --upload-port COM9
py -m platformio device monitor --port COM9 --baud 115200 --echo
```

`COM9` ist nur der damalige Testport. Im eigenen System den tatsächlich angezeigten Port einsetzen. **Nicht das Upstream-Projekt erneut patchen, wenn du bereits diesen Fork klonst:** Die AB02-Änderungen sind in `main` enthalten.

Detaillierte Anleitung: [Windows-Build und Recovery](docs/AB02/BUILD_WINDOWS.md).

## Verifizierte Tests

- KiekR erkennt den Repeater als MeshCore-Knoten.
- Erfolgreicher direkter Ping: **RTT 667 ms**, gemessene SNR-Paare **+13/+12 dB** und später **+11,7/+13 dB** (Up/Down).
- Nach 294 Sekunden Laufzeit im Test: **RX 19, TX 18, FWD 19, Fehler 0**, Boot-Zähler unverändert.
- Ein **Zero-Hop-Advert** vom Wio Tracker L1 Pro in KiekR wechselte die Statusanzeige von `T:nosync` zu `T:sync`.
- **Nicht** daraus ableiten: vollständiger End-to-End-Nachweis für Mehrbyte-Pfade, Langzeitstabilität, wetterfesten Betrieb oder regulatorische Konformität.

[Messprotokoll und Fehlversuche](docs/AB02/TEST_REPORT.md)

## Dokumentation

- [Windows: Build, Flash, Diagnose und Recovery](docs/AB02/BUILD_WINDOWS.md)
- [Entwicklungshistorie des Forks](CHANGELOG.md)
- [Messprotokoll inklusive der fehlerhaften OLED-Versuche](docs/AB02/TEST_REPORT.md)
- [Hardware und geplanter Solaraufbau](docs/AB02/HARDWARE_SOLAR.md)
- [Paketformat und technische Grenzen](docs/AB02/COMPATIBILITY.md)
- [Roadmap und Abnahmekriterien](docs/AB02/ROADMAP.md)
- [Git-Workflow für mehrere PCs](docs/AB02/GIT_WORKFLOW.md)
- [Original-README inklusive ursprünglicher Versionshistorie](docs/UPSTREAM_README.md)
- [Originaldokumentation im Ordner `docs/`](docs/)

## Unterschied zum Original

Das Ausgangsprojekt stammt von **Andrea Bernardi (`atomozero`)** und steht unter der **MIT-Lizenz**. Dieser Fork ergänzt die AB02-Boardkonfiguration, die Interpretation variabler Pfadkennungen und eine Flash-Speicheroptimierung. Die eigentliche OLED-Entwicklung läuft getrennt auf `feature/oled-diagnostics`. Änderungen am Funkprotokoll sind experimentell und sollten vor dem öffentlichen Einsatz überprüft werden.

Alle ursprünglichen Lizenz- und Copyright-Hinweise bleiben erhalten. Siehe [LICENSE](LICENSE). Der originale README-Text wurde beim Umstellen der Dokumentation unverändert unter [`docs/UPSTREAM_README.md`](docs/UPSTREAM_README.md) gesichert. Er beschreibt den Stand des **Originalprojekts**, nicht notwendigerweise den aktuellen Entwicklungsstand dieses Forks.

## Sicherheit und Grenzen

**868-MHz-Betrieb:** Die im Test protokollierten Funkparameter waren `869.618 MHz`, `BW 62.5 kHz`, `SF8`, `CR8`; im Log wurde **21 dBm** angezeigt. Dies ist **keine Bestätigung der zulässigen EIRP, Sendezeit oder EU-Konformität**. Frequenz, Antennengewinn, Leistung, Duty-Cycle und die anwendbaren Regeln müssen vor dem Outdoor-Betrieb geprüft werden.

**Stromversorgung:** Solarpanel, Zellschutz, Ladeunterbrechung bei Frost, Verdrahtung und Gehäuse sind nicht validiert. Li-Ion-Zellen im Außenbereich nicht ohne geeignete temperaturabhängige Ladefreigabe betreiben.

**Fernverwaltung:** Vor öffentlichem Einsatz Passwörter/Schlüssel und Zugriffsberechtigungen prüfen. Keine privaten Schlüssel, Tokens oder persönlichen Diagnoselogs ins öffentliche Repository stellen.
