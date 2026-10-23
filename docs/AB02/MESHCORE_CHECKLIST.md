# MeshCore-Repeater-Checkliste – Abgleich mit diesem Fork

**Quelle:** „Meshcore Repeater-Checkliste“, Stand 08.10.2026 (PDF, 12 Seiten).
**Geprüfter Stand:** `main`, Firmware `v0.8.1`, Board HTCC-AB02 (ASR6502 + SX1262).

Die Checkliste ist für MeshCore-Repeater allgemein geschrieben; einige Punkte
(z. B. nRF-OTAFIX-Bootloader, BLE-OTA) treffen auf den CubeCell nicht zu. Dieses
Dokument hält fest, was der Fork bereits erfüllt, wo er abweicht und was daraus
folgt. Status: ✓ erfüllt, ⚠️ teilweise / dokumentationspflichtig, ✗ nicht umgesetzt.

## Funkparameter und Regulatorik

| Punkt | Checkliste | Umsetzung im Fork | Status |
| --- | --- | --- | --- |
| Preset EU/UK narrow | 869,618 MHz / SF 8 / CR 8 / BW 62,5 kHz | `config/repeater.json`: 869.618 MHz, BW 62.5, SF 8, CR 8 | ✓ |
| Sendeleistung | max. 500 mW ERP; bei Heltec entspricht 18 dBm ca. 462 mW | Default 21 dBm (`MC_TX_POWER`), einstellbar per `set tx` | ⚠️ |
| Arbeitszyklus | 10 % (BNetzA, Vfg. 91/2025) | Kein TX-Duty-Cycle-Limiter, kein `set dutycycle`; nur RX-Duty-Cycle | ✗ |
| Preambel | 16 Symbole | `preamble_len: 16` | ✓ |
| AGC-Reset | Default 0 (aus) | `configAgcResetInterval = 0` | ✓ |
| CAD | Empfehlung: aus | Nicht implementiert | ✓ (de facto) |
| Multi-ACK | Empfehlung: an | Kein `multi.acks`-Kommando gefunden | ⚠️ |
| Flood-Limits | advert 3, unscoped 3, flood 10 | `max_flood_hops` (Default 8), `auto_add_max_hops` | ⚠️ |

**Kritisch:** Ohne TX-Duty-Cycle-Begrenzung kann ein Repeater unter Last die
10-%-Grenze überschreiten. Das ist kein Komfort-, sondern ein Regulatorikpunkt.
Bei 21 dBm und einer 2–3-dBi-Antenne liegt die ERP bereits nahe bzw. über 500 mW.
Vor dem Aufstellen im Feld ist eine Leistungsmessung oder eine konservative
Einstellung (14–18 dBm) sinnvoll. Das README warnt bereits, aber ohne Zahl.

## Adressierung, Hashes, Regionen

| Punkt | Checkliste | Umsetzung im Fork | Status |
| --- | --- | --- | --- |
| Path-Hash | 2 oder 3 Byte; 1 Byte veraltet | Wire-Format unterstützt 1/2/3 Byte (`pathLen`-Bits); kein CLI-Schalter für die Sende-Größe | ⚠️ |
| Default-Region | `region default <Name>` für eigene Aussendungen | Kein `region default`; nur `region put/remove/allowf/denyf` | ✗ |
| Regionen | so klein wie nötig | `config/repeater.json`: `*`, `de`, `de-nord`, `de-mitte`, `de-west`, `de-ni` | ✓ |
| Unscoped-Flood | über `flood.max.unscoped` begrenzen | Kein eigener Grenzwert; `auto_add_max_hops` deckt nur einen Teil ab | ⚠️ |

## Sicherheit und Betrieb

| Punkt | Checkliste | Umsetzung im Fork | Status |
| --- | --- | --- | --- |
| Gastzugang | individuelles Passwort, kein Default | Default `guest` in `defaultConfig`; `config/repeater.json` erlaubt Setzen, warnt aber nicht beim Start | ⚠️ |
| Admin-Passwort | individuell setzen | Default `admin`; gleiche Situation | ⚠️ |
| Owner-Info | Kontaktinfo per Zero-Hop abrufbar | `set owner.info` / `get owner.info` vorhanden | ✓ |
| Private Key | sicher hinterlegen, per USB abfragbar | Identität in EEPROM; kein `get prv.key`-Äquivalent gefunden | ⚠️ |
| Uhrzeit | GPS oder RTC (DS3231) | Kein GPS am AB02; Sync über ADVERT-Zeitstempel, ohne Quelle kein Sync | ⚠️ |
| Standort | ungefähre Position setzen | `location.latitude/longitude` in Config, Default 0.0 | ⚠️ |

## Namensgebung, Antennen, Dokumentation

| Punkt | Checkliste | Umsetzung im Fork | Status |
| --- | --- | --- | --- |
| Repeater-Name | Schema Land.Bundesland.KFZ.Name o. Ä. | `DE-NI-HARSUM01` (Land + Bundesland + Ort) | ✓ |
| Antenne | höchster, freier Punkt; 2–3 dBi für dichte Netze | Hardware-Doku vorhanden, aber ohne SAW-Filter- und Montagehinweise | ⚠️ |
| SAW-/Cavity-Filter | bei Störungen empfohlen | Nicht dokumentiert | ✗ |
| Erase vor Erstflash | sauberer Zustand | Nicht dokumentiert; PlatformIO-Upload erhält EEPROM | ⚠️ |

## Konkrete Empfehlungen für dieses Repo

1. **Duty-Cycle-Limiter oder wenigstens ein `set dutycycle`-Kommando.** Ohne
   Begrenzung ist der Betrieb in EU868 regulatorisch nicht sauber. Wegen des
   vollen Flashs (98,6 %) zuerst prüfen, ob ein Airtime-Budget ohne neue
   Funktion sinnvoll untergebracht werden kann.
2. **`set path.hash.mode` (1/2/3 Byte) als CLI und Config-Feld.** Die
   Wire-Format-Unterstützung ist da; es fehlt nur der Schalter. 2 Byte als
   Default wäre checklistenkonform.
3. **`region default <Name>` implementieren.** Eigene ADVERTs sollten eine
   Default-Region tragen, sonst flooden sie ungescoped.
4. **Warnung beim Start, wenn `admin`/`guest` noch Default sind.** Ein
   Log-Eintrag genügt; das kostet wenig Flash.
5. **Default-Sendeleistung überdenken.** 21 dBm sind am AB02 Hardware-Maximum,
   aber mit PA und Antennengewinn schnell über 500 mW ERP. 14–18 dBm als
   Default und `set tx` für Leistungsträger wäre sicherer.
6. **Advert-Intervalle an die Checkliste annähern.** Empfohlen: 240 min
   Zero-Hop, 150 h Flood. Der Fork klemmt Flood derzeit bei 48 h; das Intervall
   sollte bis 168 h erlaubt sein. Für den Testbetrieb bleiben kurze Werte ok.
7. **Dokumentation ergänzen:** SAW-Filter, Antennenmontage, Erase vor Erstflash,
   Private-Key-Backup. Diese Punkte fehlen im Hardware-Kapitel.

## Nicht anwendbar

- **nRF-OTAFIX-Bootloader / BLE-OTA:** Der CubeCell nutzt den Heltec-Bootloader
  und wird per USB (PlatformIO oder Release-Hex) geflasht. Ein OTA-Weg per
  Bluetooth existiert nicht.
- **`get bootloader.version`:** Nicht Teil dieser Firmware.
