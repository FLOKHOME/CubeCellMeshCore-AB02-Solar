# Testbericht – HTCC-AB02

**Stand: 22.10.2026.** Die Testergebnisse stammen aus mehreren Entwicklungsständen. **Ein älterer erfolgreicher Funk-Test ist kein Nachweis für einen neueren Commit.**

## Hardware und Testumgebung

- Heltec CubeCell **HTCC-AB02 V1.0**, ASR6502/SX1262, SH1107-OLED, EU868.
- Windows CMD, PlatformIO Core **6.2.0** im ursprünglichen Test; spätere Tests am selben Projekt auf Windows.
- COM-Port wechselte zwischen Testrechnern (u. a. COM9 und COM3); angegebenen Port immer verifizieren.
- Funkparameter laut älterem Log: **869.618 MHz**, BW **62.5 kHz**, **SF8**, **CR8**, gemeldete Ausgangsleistung **21 dBm**.
- Gegenstelle: **Seeed Wio Tracker L1 Pro** über KiekR.

## Basisfunk: `v0.7.0-ph123` (vor OLED-/Regionspatch)

- Ursprungsversion mit AB02-Unterstützung: **130.536 B Flash / 8.584 B RAM**.
- SX1262-Initialisierung, `RX`, `TX` und `FWD` beobachtet; Repeater wurde von KiekR erkannt.
- Ping über KiekR: **RTT 667 ms**; gemessene SNR-Werte zunächst Up **+13,0 dB** / Down **+12,0 dB**, später Up **+11,7 dB** / Down **+13,0 dB**.
- Nach PathHash-v3- und Quiet-Logging-Patch: Build **126.712 B Flash / 8.584 B RAM**, Upload/Boot erfolgreich.
- Eine frühere 130.784-B-Version schlug beim Flashen mit `Checksum does not verify! Aborting.` fehl.

### Zähler aus einem Basislauf

| Uptime (s) | RX | TX | FWD | Fehler `E` | Queue `Q` |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 209 | 13 | 13 | 13 | 0 | 0 |
| 247 | 16 | 16 | 16 | 0 | 0 |
| 294 | 19 | 18 | 19 | 0 | 1 |

Die Zähler zeigen nur einen **kurzen** Praxistest. `FWD` beweist die interne Bearbeitung/Weiterleitung, aber nicht die erfolgreiche Zustellung am Zielgerät. Ein gezielter End-to-End-Nachweis mit echten 2- und 3-Byte-Mehrhop-Pfaden steht aus.

## Zeitübernahme

- `time <Unix-Zeit>` setzte die Uhr im Basisstand erfolgreich.
- Nach RESET zunächst `T:nosync`; ein **Zero-Hop-Advert** von KiekR/Wio Tracker L1 Pro führte zu `T:sync`.
- Reproduzierbarkeit über viele Neustarts wurde nicht geprüft.

## OLED und Taster – aktueller Entwicklungszweig

**Quellstand:** [`feature/oled-diagnostics`](https://github.com/FLOKHOME/CubeCellMeshCore-AB02-Solar/tree/feature/oled-diagnostics), Commit [`bf9c48b`](https://github.com/FLOKHOME/CubeCellMeshCore-AB02-Solar/commit/bf9c48b).

**Auf Hardware bestätigt:**

- OLED **SH1107** wird mittels Software-I²C bei USER-Tasterdruck aktiviert.
- Anzeige schaltet nach ca. **10 s** wieder ab.
- Verbesserte Tasterentprellung funktionierte im Test; keine ungewollte Aktivierung mehr beobachtet.
- RGB-/NeoPixel-LED blieb im getesteten Firmwarestand **aus**.

**Nicht gemessen:** absolute Stromaufnahme, Trennung der OLED-Versorgung, Wake-up aus jedem Sleep-Zustand, Verhalten im Dauerbetrieb und Einfluss auf Paketverluste.

Frühere OLED-Fehlversuche (Heltec-Library/TinyOLED-Speicherüberschreitung, fehlerhafter Timeout) sind im [Changelog](../../CHANGELOG.md) als **historisch** dokumentiert, nicht als aktuelle Defekte.

## Regionen – aktueller Entwicklungszweig

Ursprünglich war `REGION_MAX_ENTRIES=4`; eine fünfte benannte Region lieferte `ERR`. Danach:

- `REGION_MAX_ENTRIES=5` und `EEPROM_SIZE=640` implementiert.
- Firmware nach Kapazitätserweiterung kompiliert mit **127.384 / 131.072 B Flash** und **9.648 / 16.384 B RAM**, Status `SUCCESS`.
- **Achtung:** Diese Größen stammen **vor** der letzten Korrektur der Regionsspeicherung.
- Der Repeater startete mit Firmwarekennung `v0.7.0-ph123-oled` und gespeichertem Namen **`DE-NI-HARSUM01`**.
- `region put de`, `region put de-nord`, `region put de-mitte`, `region put de-west` und `region put de-ni` meldeten jeweils `OK`.
- `region` zeigte:

```text
*:A
de:A
de-nord:A
de-mitte:A
de-west:A
de-ni:A
```

**Persistenzfehler und Behebung:** Zunächst antwortete die Firmware auf `region save` mit `Unknown`; ein normales `save` führte nach RESET nur zu `*:A`. Nach Korrektur der Befehlsverarbeitung und EEPROM-Speicherung funktionierte **`region save`**. Der Anwender bestätigte, dass **alle Regionen nach RESET erhalten blieben**. Der Name blieb ebenfalls erhalten.

Das ist ein Hardware-Nachweis für **diese fünf flachen Regionen**, nicht für Eltern-Kind-Hierarchien oder zusätzliche Regionseinträge.

## Weitere Hardwarebeobachtung: Solarpanel

Für das vorhandene Panel (ungefähr **8 × 11 cm**) wurde im Sonnenlicht eine **Leerlaufspannung von ca. 6,52 V** gemessen. Das ist **kein** Nachweis für Strom, Ladeleistung oder Eignung für den direkten Anschluss. Akku- und Langzeittest fehlen.

## Noch offene Abnahmen

1. **Nach diesem Commit**: KiekR-Ping, LoRa-RX/TX/Forwarding und Fehlerzähler erneut prüfen.
2. Mehrhop-End-to-End mit 2-/3-Byte-Pfad-Hashes inklusive Zustellung am Zielgerät.
3. Sleep-/OLED-/LED-Stromaufnahme an der Batterie und Aufweckverhalten messen.
4. 24h+-Stabilität, Restart nach Unterspannung, Solarleistung, sichere Ladeabschaltung bei Frost und Wetterschutz testen.
5. Reale EIRP, Duty-Cycle und anwendbare Regeln vor öffentlichem Dauerbetrieb überprüfen.
