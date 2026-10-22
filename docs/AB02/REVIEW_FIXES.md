# Review-Fixes – Branch `fix/eeprom-layout-review`

**Stand: 22.10.2026 · Basis: `main` (`52f108d`) · 4 Commits · Firmware-Build verifiziert, Hardware-Test offen**

Dieser Bericht dokumentiert die Fehler, die bei einer statischen Analyse plus manueller
Prüfung des Codes gefunden wurden, und was dagegen unternommen wurde. Jede Angabe ist
entweder durch einen Build, durch einen reproduzierenden Host-Test oder durch
Code-Referenz belegt; Aussagen ohne Nachweis sind als solche markiert.

## Behobene Fehler

| # | Bereich | Fehler | Wirkung vorher | Nachweis |
| --- | --- | --- | --- | --- |
| 1 | EEPROM-Layout | `EEPROM_SIZE` doppelt definiert: `main.h` 640, `core/Config.h` 576. Da `Config.cpp` nur `Config.h` einbindet, lief `EEPROM.begin(576)` | Die Region-Map schreibt bis Offset 580. Die Heltec-Emulation verwirft Zugriffe außerhalb des Fensters **still** und `commit()` meldet trotzdem Erfolg → 5. Region verliert Flags-Byte und Namensende, fällt auf *allow flood* zurück (fail-open) | Emulationsquellcode + Byte-Arithmetik; Build |
| 2 | EEPROM-Layout | Mailbox-Block bei Offset 340 mit angenommenen 172 Bytes — gilt nur für ein gepacktes Struct. Real (mit Padding): 340…523 | Überlappung mit dem Region-Header ab 512. **Ein einziges** zwischengespeichertes Paket für einen Offline-Knoten löschte die Region-Magic → nach Reboot alle Regionen weg, ohne Meldung | `sizeof`-Probe (88 B/Slot) + Byte-Simulation: Magic `0x5247` → `0000` |
| 3 | ADVERT | `setup()` rief `advertGen.setInterval(ADVERT_INTERVAL_MS)` unbedingt auf, **nachdem** `loadConfig()` den gespeicherten Wert gesetzt hatte | Nach jedem Reset wieder 5 min. Zusätzlich schrieb `saveConfig()` (u. a. beim ersten Admin-Login) den 5-min-Wert ins EEPROM → Wert dauerhaft verloren | Aufrufreihenfolge + `saveConfig()`-Aufruferliste |
| 4 | Krypto | `MACThenDecrypt()` schrieb `ceil(cipherLen/16)*16` Bytes ohne Ausgabegrenze. ANON_REQ mit cipherLen bis 145 lief in `uint8_t decrypted[128]` über | **Stack-Overflow bis 32 Byte, vor der Authentifizierung erreichbar** (der Sender kennt den öffentlichen Key aus dem ADVERT und kann ein gültiges MAC bilden) | Host-Test reproduziert: Canary hinter dem Puffer wird überschrieben |
| 5 | Krypto | `zeroPad()` gab bei `len == 0` eine Blocklänge zurück, ohne zu schreiben | Uninitialisierter Stack wurde verschlüsselt und gesendet | Host-Test: Ausgabe war nicht das Nullblock-Chiffrat |
| 6 | Krypto | `SessionManager::processLogin()` verdrängte bei vollem Session-Table den ältesten Eintrag, auch einen Admin | Wer das Gast-Passwort kennt, kann den Administrator wiederholt herausdrängen | Code-Referenz |
| 7 | Kontakte | `findByName()`: `contactLen - searchLen` unterläuft bei `size_t`, wenn der Suchstring länger ist als der Kontaktname | Weit reichender Out-of-Bounds-Read, erreichbar über `msg`, `report dest`, `alert dest` | Code-Referenz |
| 8 | Mailbox | `load()` prüfte `pktLen` und Slot-Zähler aus dem EEPROM nicht | Ein veralteter/fremder Wert > 76 ließ `isDuplicate()`/`popFor()` über `pktData[]` hinaus lesen | Code-Referenz |
| 9 | CLI | `(uint8_t/int8_t/uint16_t)atoi(...)` bei `set tx`, `txpower`, `set txdelay`, `set rxdelay`, `set direct.txdelay`, `set agc.reset.interval`, `setperm`, `nodes`, `set af`, `set adc.multiplier` | Werte liefen still über: `set tx 265` → **9 dBm**, `set txdelay 65536` → **0** | Code-Referenz |
| 10 | Telemetrie | `CayenneLPP::addAnalogInputInt()`: `int16_t val = value * 100` | Überlauf ab \|value\| > 327 (z. B. Uptime-Stunden nach ~13,6 Tagen) → falscher Telemetriewert | Code-Referenz |
| 11 | Config | `saveConfig()`: `(uint8_t)(floodAdvertIntervalMs / 3600000)` | Wrap-around mod 256 → Flood-Intervall änderte sich nach dem Laden still | Code-Referenz |
| 12 | Routing | `shouldForward()` sendete ein DIRECT-Paket, dessen Pfad bei uns endet (hopCount 1) und das **an uns** adressiert ist, erneut mit leerem Pfad | Reine Sendezeit-Verschwendung, `fwdCount` zu hoch | Code-Referenz; bewusst konservativ gefixt (siehe unten) |

## Bewusst nicht geändert

- **`LOG(...)`-Makro.** Es ist in beiden aktiven Zweigen ein No-Op (Quiet-Logging, `main.h`).
  Das ist Absicht und spart Flash. Nur die neuen Startmeldungen nutzen `LOG_RAW`, damit sie
  sichtbar sind. Konsequenz: Der serielle Port zeigt im Betrieb ohnehin fast nichts.
- **`%s`-Logs auf `&pkt->payload[4]`.** Formal ein Über-Lesen ohne Nullabschluss, in diesem
  Build aber **toter Code**, weil `LOG` nicht kompiliert wird. Wird erst relevant, wenn
  ANSI-Logging wieder aktiviert wird.
- **Region-/Scope-Logik und Hop-Zählung** im Forward-Pfad: zu risikoreich ohne Hardware-Test.
- **`password[pwdLen] = '\0'`** in `decryptAnonReq()`: sieht nach Off-by-One aus, die einzige
  Aufrufstelle übergibt aber `sizeof(password) - 1` und ist damit korrekt.

## Nachweise

```text
Build:           128.960 / 131.072 B Flash (98,4 %), 9.624 B RAM
Konfig-Tests:    python3 tools/test_user_config.py           -> 18/18
Krypto-Host-Test: tools/hosttest/run.sh 52f108d
   === fixed ===        oversized packet: cipherLen=145, return=0,   canary intact=yes
   === base-52f108d === oversized packet: cipherLen=145, return=145, canary intact=NO
```

## Auf Hardware zu prüfen (offen)

1. `[A] ADV: on every <Sekunden>` beim Boot zeigt den **wirksamen** Wert (nicht 300).
2. `advert interval` nach einem RESET → gleicher Wert wie vorher.
3. `region` vor und nach RESET → fünf Einträge plus `*` unverändert.
4. Ein Paket für einen Offline-Knoten puffern (`mailbox` zeigt `E1:`), dann RESET →
   `region` weiterhin vollständig (vorher zerstörte genau das die Regionsliste).
5. Login von der App (Admin und Gast) sowie `config` per Konsole.
6. Gerichteter Ping/Trace über 2+ Hops (Prüft Punkt 12; die letzte Strecke zum Ziel muss
   weiterhin gesendet werden).
7. 24-h-Lauf mit Solar/Akku: kommen ADVERTs im eingestellten Raster?

## Nebenwirkung des Upgrades

`EEPROM_VERSION` bleibt 6, die Offsets sind unverändert — ein geflashtes Bestandsgerät
behält seine Konfiguration. Ausnahme: Der Mailbox-Sub-Version stieg von 1 auf 2, was
höchstens einen zwischengespeicherten Store-and-Forward-Slot verwirft. Wer eine ältere
Firmware mit abweichendem Layout verwendet, landet im Default-Zweig von `loadConfig()`
und bekommt die eingebauten Werte bzw. `config/repeater.json` — kein Brick, aber
Einstellungen sind dann weg.
