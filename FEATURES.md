# Features – CubeCellMeshCore HTCC-AB02 Solar

**Stand: 22.10.2026** · Entwicklungszweig [`feature/oled-diagnostics`](https://github.com/FLOKHOME/CubeCellMeshCore-AB02-Solar/tree/feature/oled-diagnostics) · Firmware-Commit `bf9c48b`.

Diese Liste trennt **implementierte Funktionen**, **auf Hardware bestätigte Beobachtungen** und **noch ausstehende Validierung**. Sie beschreibt den Entwicklungszweig; auf `main` kann der Funktionsumfang abweichen.

## Funk und MeshCore

| Merkmal | Status | Anmerkung |
| --- | --- | --- |
| SX1262 / EU868 auf Heltec HTCC-AB02 V1.0 | ✅ Basishardware getestet | Boot, Empfang und Senden |
| MeshCore-Repeater/Forwarding | ✅ Auf früherem Basisstand getestet | KiekR erkannte Repeater; `RX`/`TX`/`FWD` reagierten |
| Direkt-Ping über KiekR | ✅ Auf früherem Basisstand getestet | RTT ca. 667 ms |
| 1-/2-/3-Byte-Pfad-Hashes | 🟡 Implementiert | Gezielte echte 2-/3-Byte-Multihop-Tests fehlen |
| Zeitübernahme per Zero-Hop-Advert | ✅ Auf Basisstand beobachtet | Nach Neustart erneuter Sync möglich/nötig |
| Funk nach **aktuellem** EEPROM-/OLED-Patch | ⏳ Ausstehend | Regressions-Ping/Forwarding noch durchführen |

## Benutzeroberfläche und Stromsparziel

| Merkmal | Status | Anmerkung |
| --- | --- | --- |
| SH1107-OLED via Software-I²C | ✅ Hardwaretest | Passt ins knappe Flash-Budget |
| USER-Taster aktiviert OLED | ✅ Hardwaretest | Bedienung bestätigt |
| Automatisches Abschalten nach ca. 10 s | ✅ Hardwaretest | Sichtbares Abschalten bestätigt |
| Tasterentprellung | ✅ Hardwaretest | Keine unbeabsichtigte Aktivierung im Test |
| RGB-/NeoPixel-LED deaktiviert | ✅ Hardwaretest | LED im getesteten Stand aus |
| Physische Abschaltung der OLED-Versorgung | ⏳ Nicht gemessen | Dunkles Display ist kein Stromnachweis |
| Energieaufnahme im Sleep-/Solarbetrieb | ⏳ Nicht gemessen | Strommessung an Batterie notwendig |

## Regionen und Konfiguration

| Merkmal | Status | Anmerkung |
| --- | --- | --- |
| Fünf benannte Regionen + Wildcard `*` | ✅ Hardwaretest | `REGION_MAX_ENTRIES=5` |
| Einträge `de`, `de-nord`, `de-mitte`, `de-west`, `de-ni` | ✅ Hardwaretest | Alle fünf in der aktiven Regionsliste |
| Flood-Freigabe (`A`) | ✅ Hardwaretest | `*:A` und alle benannten Regionen `:A` |
| `region save` / Restore nach RESET | ✅ Hardwaretest | Alle sechs Einträge nach Neustart wieder sichtbar |
| Gerätekennung `DE-NI-HARSUM01` | ✅ Hardwaretest | Nach Neustart erhalten |
| Regionshierarchie / Parent-Child-Logik | ❌ Nicht implementiert | `region put NAME` erzeugt **flache** Einträge |
| Regionen mit mehr als 11 ASCII-Bytes | ⚠️ Eingeschränkt | EEPROM speichert nur `name[12]`, inklusive Nullabschluss |

## Build und Grenzen

- Board: `cubecell_board_plus` / HTCC-AB02 V1.0 (ASR6502, SX1262).
- Basis `main`: **126.712 B Flash**, **8.584 B RAM**.
- Erweiterter Entwicklungsstand **vor dem letzten Regions-Persistenz-Fix**: **127.384 / 131.072 B Flash** und **9.648 / 16.384 B RAM**. Der abschließende Commit benötigt für belastbare Werte einen erneuten Build.
- Regionseinträge: EEPROM-Block ab **Offset 512**, fünf Einträge à 13 Bytes zuzüglich 4-Byte-Header = **69 Bytes**, letzter Byteindex **580**; EEPROM-Reservierung **640 Bytes**.
- Regionsnamen: im RAM bis 15 Zeichen; beim Speichern höchstens 11 ASCII-Bytes ohne Abschneiden. Hashschlüssel werden beim Laden aus dem gespeicherten Namen neu berechnet.
- UART: `status`, `stats`, `get name`, `region`, `region put NAME`, `region save` (bestätigte Beispielsitzung). Weitere Befehle siehe Quellcode.
- Kein offizieller MeshCore-1.x-Port, kein vollständiger Interoperabilitätsnachweis, kein validierter Langzeit-/Solarbetrieb.

## Nächste Prüfungen

1. Repeater über Wio Tracker L1 Pro / KiekR mit **aktuellem** Commit anpingen; `RX`, `TX`, `FWD`, Fehler und Neustarts protokollieren.
2. Mehrhop-End-to-End-Test mit 2- und 3-Byte-Pfadkennung durchführen.
3. Akkustrom mit OLED an/aus, RGB aus, Sleep sowie bei LoRa-TX messen.
4. Solarpanel und Li-Ion-Ladung einschließlich Frostschutz sicher auslegen und im Dauerbetrieb prüfen.

Weitere Details: [README](README.md) · [Testbericht](docs/AB02/TEST_REPORT.md) · [Roadmap](docs/AB02/ROADMAP.md) · [Konfiguration](docs/AB02/CONFIGURATION.md).
