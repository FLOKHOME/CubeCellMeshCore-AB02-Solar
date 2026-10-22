# Windows – Build, Flash, Diagnose und Recovery

**Stand: 22.10.2026.** Unterscheide die bereits funkerprobte Basis `main` vom neueren Entwicklungszweig `feature/oled-diagnostics`.

## Voraussetzungen

- Windows 10/11, Git, Python 3 und PlatformIO Core (im Test **6.2.0**).
- Heltec **CubeCell HTCC-AB02 V1.0**, eine passende 868-MHz-Antenne und ein **USB-Datenkabel**.
- Bei fehlendem COM-Port zunächst Kabel und Windows-Geräte-Manager kontrollieren; CP210x-Treiber nur falls erforderlich.

```cmd
py --version
py -m platformio --version
git --version
```

Falls PlatformIO fehlt:

```cmd
py -m pip install --user -U platformio
```

## Fork holen, Branch auswählen

```cmd
git clone https://github.com/FLOKHOME/CubeCellMeshCore-AB02-Solar.git
cd CubeCellMeshCore-AB02-Solar
git status -sb
```

Die bereits erprobte Funk-Basis liegt auf `main`. Die **OLED-/LED-/Regionsfunktionen inklusive EEPROM-Speicherung** liegen auf `feature/oled-diagnostics`, Firmware-Commit `bf9c48b`:

```cmd
git switch feature/oled-diagnostics
py -m platformio run -e cubecell_board_plus
```

**Historische PathHash- und Quiet-Logging-Patches nicht erneut anwenden** – der Fork enthält diese Änderungen bereits. Beim Wechsel zwischen Branches zuerst mit `git status -sb` prüfen, ob der Arbeitsbaum sauber ist.

## Bekannte Build-Messwerte

| Stand | Flash | RAM | Interpretation |
| --- | ---: | ---: | --- |
| `main`, Basis `v0.7.0-ph123` | 126.712 B | 8.584 B | Erfolgreicher Build/Upload und Basis-Funkpraxis |
| Entwicklungsbranch, **nach Region5, vor Persistenz-Fix** | 127.384 B | 9.648 B | Erfolgreicher Build und später hardwaregetestete Regionskonfiguration |

Für `bf9c48b` liegt noch **kein separat protokollierter exakter Flash-/RAM-Bericht** vor; den Wert lokal mit neuem Build prüfen. Frühere Firmware mit **130.784 B Flash** scheiterte trotz `[SUCCESS]` am Bootloader (`Checksum does not verify`). Linkererfolg ist daher kein Uploadbeweis.

## Upload und Monitor

```cmd
py -m platformio device list
py -m platformio run -e cubecell_board_plus -t upload --upload-port COM3
py -m platformio device monitor --port COM3 --baud 115200 --echo
```

**COM3** ist nur ein Testbeispiel. COM-Port im Geräte-Manager/PlatformIO prüfen und vor dem Flashen den Monitor schließen. 868-MHz-Antenne **vor** Funkbetrieb anschließen. Das Flashen überschreibt die aktuelle Firmware.

Wenn der Bootloader nicht reagiert: das dokumentierte Heltec-Verfahren **USER halten, RESET kurz drücken, USER loslassen** testen; vorher Kabel/Port prüfen.

## Serielle Diagnose

```text
status
stats
lifetime
get name
region
```

Der bestätigte Name war `DE-NI-HARSUM01`. Für die fünf benannten Regionen:

```text
region put de
region put de-nord
region put de-mitte
region put de-west
region put de-ni
region
region save
```

Nach **RESET** erneut `region` eingeben. Im Hardwaretest blieben die fünf Namen sowie die Wildcard `*` erhalten. Die Firmware bietet **keine** Parent-Child-Regionsverwaltung; `region put NAME` verwenden, nicht `region put NAME PARENT`. Weitere Informationen: [Konfiguration](CONFIGURATION.md).

Falls UART in den Sleep-Modus übergeht, unmittelbar nach RESET testweise `sleep off` eingeben. Für den Solarbetrieb **nicht ungemessen dauerhaft deaktivieren**.

Manuelle Uhr zum Funktionstest:

```cmd
powershell -NoProfile -Command "'time ' + [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()"
```

Die erzeugte Befehlszeile im seriellen Monitor eingeben. Im älteren Funk-Test führte auch ein **Zero-Hop-Advert** über KiekR/Wio Tracker L1 Pro zur Synchronisierung (`T:sync`).

## OLED-Test

1. Nach Boot OLED im Normalzustand **aus**.
2. USER drücken: SH1107-Anzeige erscheint.
3. Ca. **10 Sekunden** später Anzeige aus.
4. Wiederholte Betätigung: keine ungewollten Aktivierungen im bekannten Test.
5. RGB-/NeoPixel-LED im getesteten Entwicklungsstand aus.

Das Sichtbarwerden/Abschalten beweist **keine vollständige Stromabschaltung**. Strom- und Sleep-Messungen bleiben nötig.

## Regressionstest nach neuer Firmware

- Boot, `status`, `stats`, `lifetime`, Gerätename und `region` prüfen.
- OLED-Taster und Timeout auf dem **geflashten** Commit erneut prüfen.
- Funk mit Wio Tracker L1 Pro und KiekR testen: Repeater-Sichtbarkeit, Ping, `RX`/`TX`/`FWD`, Fehlerzähler.
- Fünf Pings mit Abständen durchführen, unerwartete Neustarts dokumentieren.
- Echte 2-/3-Byte-Mehrhop-Routen **separat** prüfen; ein direkter Ping reicht dafür nicht.

**Aktueller Nachweisstand:** Nach dem letzten OLED-/Regions-Persistenz-Fix wurde die EEPROM-Persistenz auf Hardware bestätigt; ein neuer Funkweiterleitungstest für genau diesen Stand steht noch aus.

## Recovery

1. `git status -sb` prüfen; uncommittete Änderungen vor Branchwechsel sichern.
2. Monitor schließen, korrektes USB-Datenkabel und COM-Port sicherstellen.
3. Für die ältere Basis `git switch main` nur bei sicherem Arbeitsbaum; danach bauen und Flashgröße prüfen.
4. Bei Bootloaderproblemen dokumentiertes USER/RESET-Verfahren einsetzen.
5. Identität, EEPROM-Einstellungen, OLED und Funk nach dem Flashen prüfen.

**Keine** geheimen Geräteschlüssel, Zugangsdaten oder privaten Standortdaten in Issues oder Logs veröffentlichen.
