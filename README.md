# CubeCellMeshCore – HTCC-AB02 Solar Repeater

> **Experimenteller Community-Fork**, keine offizielle MeshCore-Firmware und kein vollständiger Port der offiziellen MeshCore-1.x-Firmware. Grundlage ist [atomozero/CubeCellMeshCore](https://github.com/atomozero/CubeCellMeshCore) v0.7.0 (MIT). Stand der Projektdokumentation: **22.10.2026**.

Dieser Fork entwickelt einen kostengünstigen MeshCore-kompatiblen **EU868-Repeater** auf Basis des **Heltec CubeCell HTCC-AB02 V1.0** (ASR6502, SX1262) mit bedarfsgesteuerter OLED-Diagnose und dem Ziel eines späteren solarversorgten Outdoor-Betriebs.

**Aktueller Entwicklungsstand:** [`feature/oled-diagnostics`](https://github.com/FLOKHOME/CubeCellMeshCore-AB02-Solar/tree/feature/oled-diagnostics), Firmware-Commit [`bf9c48b`](https://github.com/FLOKHOME/CubeCellMeshCore-AB02-Solar/commit/bf9c48b). Der Branch ist mit GitHub synchronisiert, **aber noch nicht nach `main` übernommen**. `main` bleibt die zuvor getestete Funk-Basis.

## Projektstatus

| Funktion | Status / Nachweis |
| --- | --- |
| Basisrepeater: LoRa-Empfang, Senden, Weiterleitung, KiekR-Ping | **Auf Hardware getestet**, auf Basis `v0.7.0-ph123` vor den jüngsten OLED-/EEPROM-Änderungen |
| Variable MeshCore-Pfad-Hashes (1, 2, 3 Byte) | **Implementiert**, Basisfunk getestet; gezielter Mehrhop-End-to-End-Nachweis fehlt |
| SH1107-OLED über USER-Taster | **Auf Hardware getestet**, reagiert auf Tastendruck und schaltet nach ca. 10 s wieder ab |
| OLED-Tasterentprellung | **Auf Hardware bestätigt**; keine unbeabsichtigten OLED-Aktivierungen im Test |
| RGB-/NeoPixel-Status-LED | **Im getesteten Entwicklungsstand deaktiviert** |
| Regionen `*`, `de`, `de-nord`, `de-mitte`, `de-west`, `de-ni` | **Auf Hardware angelegt und nach RESET wieder aus EEPROM geladen** |
| Identität `DE-NI-HARSUM01` | **Persistenz auf Hardware bestätigt** |
| Solar-/Akku-Dauerbetrieb | **Noch nicht nachgewiesen**; Panel-Leerlaufspannung im Sonnenschein ca. 6,52 V gemessen |
| Funkweiterleitung **nach** dem letzten EEPROM-/OLED-Update | **Noch gesondert zu testen** |

Details und Grenzen: [Feature-Übersicht](FEATURES.md) · [Testbericht](docs/AB02/TEST_REPORT.md) · [Changelog](CHANGELOG.md).

## Entwicklungszweige und Speicherbedarf

| Firmwarestand | Flash | RAM | Einordnung |
| --- | ---: | ---: | --- |
| `main`, `v0.7.0-ph123` mit Quiet-Logging | 126.712 / 131.072 B (96,7 %) | 8.584 / 16.384 B (52,4 %) | Basis mit nachgewiesenem Funkverkehr |
| `feature/oled-diagnostics`, **nach Erhöhung auf fünf Regionen, vor dem letzten Persistenz-Fix** | 127.384 / 131.072 B (97,2 %) | 9.648 / 16.384 B (58,9 %) | Build erfolgreich; nachfolgende Persistenzkorrektur auf Hardware getestet |

**Wichtig:** Diese zweite Größenmessung stammt *vor* dem letzten Patch der seriellen Regionsspeicherung. Die endgültige Größe des Commits `bf9c48b` wurde im Gespräch nicht separat protokolliert; ein frischer Build liefert sie. Ein erfolgreicher Build allein garantiert wegen des CubeCell-Bootloaders noch keinen erfolgreichen Upload.

## Hardware

- Heltec **HTCC-AB02 V1.0** (Board-ID `cubecell_board_plus`), ASR6502 / SX1262, 868-MHz-Antenne.
- Integriertes **SH1107-OLED** mit Software-I²C; Anzeige nur auf Anforderung via USER-Taster, automatisches Abschalten nach etwa 10 Sekunden.
- RGB-LED/NeoPixel im getesteten Stand abgeschaltet.
- Geplanter Solarbetrieb mit vorhandenem Panel und 18650-Zelle(n); **keine freigegebene Verschaltung oder Frost-Ladeabschaltung**.

[Hardware und Solarplanung](docs/AB02/HARDWARE_SOLAR.md).

## Bauen und flashen (Windows CMD)

Git, Python 3 und PlatformIO Core werden benötigt. **Vor Funkbetrieb eine geeignete Antenne anschließen.**

```cmd
py -m pip install --user -U platformio

git clone https://github.com/FLOKHOME/CubeCellMeshCore-AB02-Solar.git
cd CubeCellMeshCore-AB02-Solar

REM Getesteten Entwicklungszweig auswählen
git switch feature/oled-diagnostics
py -m platformio run -e cubecell_board_plus
```

Bei erfolgreichem Build den tatsächlichen seriellen Port ermitteln und die Firmware bewusst hochladen (hier nur ein **Beispielport**):

```cmd
py -m platformio device list
py -m platformio run -e cubecell_board_plus -t upload --upload-port COM3
py -m platformio device monitor --port COM3 --baud 115200 --echo
```

Der Fork enthält die PathHash-/Quiet-Logging-Anpassungen bereits: **Historische Patch-Skripte nicht erneut anwenden.** Siehe [Windows-Build, Flash und Recovery](docs/AB02/BUILD_WINDOWS.md).

## Zentrale Konfiguration `config/repeater.json`

Statt jede Einstellung nach dem Flashen über die serielle Konsole einzugeben, wird **vor dem Kompilieren** die Datei `config/repeater.json` bearbeitet:

```cmd
REM 1) Repo klonen   2) config\repeater.json bearbeiten   3) bauen   4) flashen
notepad config\repeater.json
py -m platformio run -e cubecell_board_plus -t upload --upload-port COM3
```

Beim ersten Start übernimmt die Firmware die Werte automatisch und speichert sie dauerhaft im EEPROM. Enthalten sind Name, Standort, Funkparameter (Frequenz, Bandbreite, SF, CR, Sendeleistung), ADVERT-Intervalle, Regionenliste (inkl. `*`/Deny), Flood-/Loop-Grenzen, Energieoptionen und optional Admin-/Gast-Passwort.

```json
{
  "name": "DE-NI-HARSUM01",
  "radio": { "frequency_mhz": 869.618, "bandwidth_khz": 62.5, "spreading_factor": 8, "coding_rate": 8, "tx_power_dbm": 21 },
  "regions": { "allow": ["*", "de", "de-nord", "de-mitte", "de-west", "de-ni"], "deny_flood": [] }
}
```

- Die Datei wird beim Build von `tools/gen_user_config.py` validiert und in `src/generated/UserConfigData.{h,cpp}` übersetzt — **kein JSON-Parser in der Firmware** (das Image ist mit 98,1 % fast voll).
- Ungültige Werte brechen den Build mit Klartextmeldung ab (`[userconfig] CHECK FAILED: …`).
- Übernommen wird nur, wenn sich die Datei geändert hat (Fingerabdruck im EEPROM, `NodeConfig.configHash`). Manuell per Konsole gesetzte Werte bleiben sonst unangetastet.
- Prüfbefehle: `config` (Status `applied`/`stale`), `config apply` (erzwingt erneutes Anwenden).
- Ohne `config/repeater.json` baut die Firmware unverändert mit den eingebauten Vorgaben.

Speicherbedarf des Beispiel-Builds mit Konfigurationsdatei: **128.544 / 131.072 B Flash (98,1 %)**, 9.624 B RAM. Details: [Konfiguration, Regionen und EEPROM](docs/AB02/CONFIGURATION.md).

## Serielle Regionskonfiguration

Die aktuelle CubeCell-Implementierung verwaltet eine separat vorhandene Wildcard und **fünf benannte Regionen**. Die Einträge sind **flach**: Ein vermeintlicher Parent-Parameter aus einem JSON-Profil wird von dieser Firmware **nicht als Regionshierarchie interpretiert**.

```text
get name
region
region put de
region put de-nord
region put de-mitte
region put de-west
region put de-ni
region
region save
```

Erfolgreich getestete Regionsliste:

```text
*:A
de:A
de-nord:A
de-mitte:A
de-west:A
de-ni:A
```

Nach `region save` wurden die Einträge durch **RESET und anschließendes `region`** erfolgreich verifiziert. **`save` und `region save` sind nicht gleichbedeutend:** Zur eindeutigen Speicherung der Regionsliste `region save` verwenden. Regionsnamen sollten im aktuellen EEPROM-Format maximal **11 ASCII-Bytes** lang sein (zwölf Bytes inklusive Nullabschluss); längere Namen können beim Wiederladen abgeschnitten werden. Der Repeater-/Gerätename ist davon unabhängig.

[Konfiguration und Persistenz](docs/AB02/CONFIGURATION.md).

## Funk, Kompatibilität und Einschränkungen

Im ursprünglichen Funk-Praxistest wurden `869.618 MHz`, Bandbreite `62.5 kHz`, `SF8`, `CR8` und eine im Log gemeldete Sendeleistung von `21 dBm` beobachtet; der Ping über KiekR erreichte **667 ms**. Die aktuelle OLED-/EEPROM-Firmware muss im Funkbetrieb erneut geprüft werden. Insbesondere ist noch **kein gezielter Zustellnachweis über 2-/3-Byte-Multihop-Pfade** dokumentiert.

Die gemeldete Sendeleistung ist **keine Bestätigung der zulässigen EIRP oder Duty-Cycle-Konformität**. Vor unbeaufsichtigtem Betrieb Funkrecht, Antennengewinn, Strombedarf, Li-Ion-Schutz und temperaturabhängiges Laden prüfen. Kein ganzjähriger Solar-Dauerbetrieb ist nachgewiesen.

## Dokumentation

- [Features und Teststatus](FEATURES.md)
- [Changelog](CHANGELOG.md)
- [Windows-Build / Flash / Recovery](docs/AB02/BUILD_WINDOWS.md)
- [Regionen, EEPROM und CLI](docs/AB02/CONFIGURATION.md)
- [Testbericht](docs/AB02/TEST_REPORT.md)
- [Hardware und Solarplanung](docs/AB02/HARDWARE_SOLAR.md)
- [Protokollkompatibilität](docs/AB02/COMPATIBILITY.md)
- [Roadmap](docs/AB02/ROADMAP.md)
- [Git-Workflow](docs/AB02/GIT_WORKFLOW.md)
- [Original-README des Upstream-Projekts](docs/UPSTREAM_README.md)

## Herkunft und Lizenz

Original von [Andrea Bernardi / atomozero](https://github.com/atomozero/CubeCellMeshCore), **MIT-Lizenz**. Original-Lizenz- und Copyright-Hinweise bleiben erhalten; die bisherige Upstream-Dokumentation ist unter [`docs/UPSTREAM_README.md`](docs/UPSTREAM_README.md) archiviert. Dieser Community-Fork wird unabhängig vom offiziellen [MeshCore-Projekt](https://github.com/meshcore-dev/MeshCore) entwickelt und ist nicht mit offiziellen MeshCore-Releases gleichzusetzen.
