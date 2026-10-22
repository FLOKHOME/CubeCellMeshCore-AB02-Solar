# Windows – Build, Flash, Diagnose und Recovery

## Voraussetzungen

- Windows 10/11, Python 3, Git und **PlatformIO Core**.
- CubeCell **HTCC-AB02 V1.0** und passende **868-MHz-Antenne**.
- Micro-USB-**Datenkabel** (ein reines Ladekabel war beim ersten Test Ursache des fehlenden COM-Ports).
- CP210x-VCP-Treiber nur dann nachinstallieren, wenn Windows nachweislich ein USB-Gerät erkennt, es aber keinen funktionierenden COM-Port bereitstellt.

```cmd
py --version
py -m platformio --version
git --version
```

Wenn PlatformIO nicht installiert ist:

```cmd
py -m pip install --user -U platformio
py -m platformio --version
```

Getestet wurde **PlatformIO Core 6.2.0**. Bibliotheks- und Plattformversionen im Projekt können die Imagegröße beeinflussen.

## Quelle: Fork statt Original

```cmd
git clone https://github.com/FLOKHOME/CubeCellMeshCore-AB02-Solar.git
cd CubeCellMeshCore-AB02-Solar
```

**Wichtig:** Die Änderungen aus dem PathHash-v3- und Quiet-Logging-Patch sind bereits im `main`-Branch enthalten. Wer diesen Fork klont, darf die historischen Patch-Skripte **nicht erneut** anwenden.

```cmd
git status -sb
git branch --show-current
py -m platformio run -e cubecell_board_plus
```

Erst nach dem vollständigen `[SUCCESS]` gilt der Build als erfolgreich. Der am 22.10.2026 reproduzierte Basis-Build verwendete **126.712 B Flash** und **8.584 B RAM**. Leichte Abweichungen können auf Versionsunterschiede hindeuten; erhebliche Abweichungen nachprüfen.

## Upload (bewusst, nicht automatisch)

```cmd
py -m platformio device list
py -m platformio run -e cubecell_board_plus -t upload --upload-port COM9
```

`COM9` durch den tatsächlich erkannten Port ersetzen. Vor Senden stets passende Antenne anschließen. Upload überschreibt die auf dem Board vorhandene Firmware.

Falls der Bootloader nicht reagiert, dokumentierte Heltec-Tastenkombination **USER gedrückt halten, RESET kurz drücken, USER loslassen** verwenden und den Upload wiederholen. Falls Windows überhaupt kein USB-Gerät erkennt, zuerst Kabel/Port/Buchse prüfen.

## Monitor und serielle Befehle

```cmd
py -m platformio device monitor --port COM9 --baud 115200 --echo
```

Mit `Ctrl+C` verlassen. Bei fehlender Eingabeanzeige `--echo` verwenden. Solange der Repeater in den Sleep-Modus wechseln kann, reagiert UART nach einiger Zeit eventuell nicht. Nach RESET innerhalb der Wachphase:

```text
sleep off
status
stats
lifetime
radio
```

`sleep off` wurde im Test in EEPROM gespeichert und ist **nicht** für den späteren Solarbetrieb als Standardempfehlung gedacht. Den tatsächlichen Stromverbrauch mit Sleep an/aus messen.

Manuelle Uhr über Unix-Zeit (nur für Test):

```cmd
powershell -NoProfile -Command "'time ' + [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()"
```

Die ausgegebene `time <timestamp>`-Zeile in den seriellen Monitor eingeben. Für automatische Zeitübernahme wurde nach RESET ein **Zero-Hop-Advert** via KiekR/Wio Tracker L1 Pro ausgelöst; anschließend wechselte `T:nosync` zu `T:sync`.

## Bekannter Bootloader-/Speicherfehler

Das ursprüngliche PathHash-v3-Build belegte **130.784 B** Flash, kompilierte zwar, brach aber beim Upload mit `Checksum does not verify` ab. Ein Build fast an der Flash-Grenze kann trotz `[SUCCESS]` nicht flashbar sein. **Weder Checksummenprüfung noch Bootloader umgehen.**

## Recovery bei Firmwareproblemen

1. Build stoppen, Konsole schließen, USB/COM-Port prüfen.
2. Mit `git switch main` zu der reproduzierten Basis wechseln **nur bei sauberem Git-Arbeitsbaum** (vorher `git status`).
3. `py -m platformio run -e cubecell_board_plus` ausführen und den Speicherbericht prüfen.
4. Mit dokumentiertem Bootloader-Verfahren neu hochladen und über UART/KiekR kontrollieren.
5. Bei Änderungen für OLED/LED ausschließlich im Branch `feature/oled-diagnostics` arbeiten; keine ungetesteten Binaries als stabil veröffentlichen.

## Test nach Upload

- Boot/CLI/`status`, `stats`, `lifetime` prüfen.
- KiekR-Kontakt erkennt Repeater, `Ping (Zero Hop)` antwortet.
- 5 Pings in Abständen, keine Fehlermeldungen und keine unerwarteten Reboots.
- Mehrhop-Test separat durchführen; direkter Ping prüft **keine** 2-/3-Byte-Pfadverarbeitung.
