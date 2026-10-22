# Changelog – FLOKHOME HTCC-AB02 Fork

Dieses Changelog beschreibt **Entwicklungsstände dieses Community-Forks**, nicht offizielle MeshCore-Releases. Die Originalhistorie von [atomozero/CubeCellMeshCore](https://github.com/atomozero/CubeCellMeshCore) steht in [`docs/UPSTREAM_README.md`](docs/UPSTREAM_README.md) und in der Git-Historie.

## [Unreleased] – 22.10.2026, `main` + `fix/eeprom-layout-review`

Die OLED-Diagnose und die persistente Regionsspeicherung sind inzwischen in `main` (`52f108d`) enthalten; der frühere Zweig `feature/oled-diagnostics` (`bf9c48b`) ist dort vollständig aufgegangen. Darauf aufbauend korrigiert der Review-Branch **`fix/eeprom-layout-review`** (4 Commits, Tip `5362dad`) zusätzliche Fehler. **Kein freigegebenes stabiles Release; die Review-Korrekturen sind noch nicht auf Hardware getestet.**

### Fixed – Review-Branch `fix/eeprom-layout-review`

- **EEPROM-Layout:** `EEPROM_SIZE` war doppelt definiert (640 in `main.h`, 576 in `Config.h`); die Region-Map schrieb bis Offset 580, wobei die 5. Region Flags und Namensende verlor. Jetzt eine einzige Quelle (`core/StorageLayout.h`) mit `static_assert`- und `#error`-Schutz. (`c9cbde8`)
- **Mailbox:** Der Mailbox-Block überlappte den Region-Header; ein einziges zwischengespeichertes Paket löschte die Region-Magic, nach RESET waren alle Regionen weg. Mailbox auf 84-Byte-Slots bei Offset 336 verlegt. (`a674a17`)
- **ADVERT-Intervall:** `setup()` setzte das Intervall nach `loadConfig()` unbedingt auf 5 min zurück und schrieb das ins EEPROM. Reihenfolge korrigiert; der gespeicherte Wert bleibt nach RESET erhalten. (`cc95656`)
- **Krypto/Stack:** `MACThenDecrypt()` begrenzte die Ausgabe nicht — ein ANON_REQ mit bis zu 145 Byte lief in einen 128-Byte-Puffer über, vor der Authentifizierung erreichbar. `zeroPad()` verschlüsselte bei leerer Eingabe uninitialisierten Stack. (`5362dad`, mit Host-Regressionstest)
- **Sitzungsverwaltung:** Ein Admin konnte durch wiederholte Gast-Logins aus der Sitzungstabelle verdrängt werden.
- **Weitere:** `findByName()`-Unterlauf, Mailbox-`load()`-Validierung, Werte-Wrap bei `set tx`/`txdelay` u. a., CayenneLPP-Überlauf, `floodAdvertHrs`-Wrap, unnötiges Re-Broadcast eines eigenen DIRECT-Pakets.

Details und Nachweise: [Review-Fixes](docs/AB02/REVIEW_FIXES.md).

### Added

- Diagnoseanzeige auf dem **SH1107-OLED** per **USER-Taster** mit Software-I²C und automatischem Abschalten nach ungefähr **10 Sekunden**.
- Tasterentprellung gegen ungewollte bzw. mehrfach ausgelöste Displayaktivierung.
- Regionenkapazität von **4 auf 5 benannte Einträge** erweitert; Wildcard `*` wird zusätzlich separat geführt.
- EEPROM-Reservierung von **576 auf 640 Bytes** erhöht. Regionsblock: Offset **512–580** (69 Bytes, fünf Einträge).
- Persistenz der Regionskonfiguration repariert: `region save` wird erkannt; nach RESET können alle fünf benannten Regionen und `*` wieder geladen werden.

### Changed

- RGB-/NeoPixel-LED ist in der getesteten Entwicklungsfirmware deaktiviert.
- Serielle Befehlsverarbeitung für die Regionsspeicherung korrigiert. Allgemeines `save` nicht mit `region save` verwechseln.
- Geräteprofil: `DE-NI-HARSUM01`; getestete Regionen `*`, `de`, `de-nord`, `de-mitte`, `de-west`, `de-ni`, jeweils Flood erlaubt (`A`).
- Regionen werden **flach** verwaltet. `region put NAME` ist der bestätigte Befehl; Parent-Angaben in Profilen erzeugen **keine** Regionshierarchie.

### Verified on hardware

- OLED lässt sich per USER aktivieren, schaltet nach ca. 10 s wieder aus und zeigte nach Entprellung keine unbeabsichtigten Aktivierungen im Test.
- RGB-LED bleibt im getesteten Zustand aus.
- `region put` akzeptiert jetzt auch die fünfte benannte Region `de-ni`.
- `region save` erfolgreich; alle sechs Einträge einschließlich `*` bleiben **nach RESET** vorhanden.
- Gerätekennung und Name `DE-NI-HARSUM01` bleiben erhalten.
- Build **nach Kapazitätserweiterung, aber vor letzter Persistenzkorrektur**: **127.384 / 131.072 B Flash (97,2 %)**, **9.648 / 16.384 B RAM (58,9 %)**, `SUCCESS`. Endgültige Größe des Commits `bf9c48b` nicht separat protokolliert.

### Pending / limitations

- Funkweiterleitung und Ping **mit dem letzten OLED-/EEPROM-Stand** erneut testen; frühere Funkerfolge stammen von der Basisfirmware.
- Gezielte Zustelltests über echte 2-/3-Byte-Multihop-Pfade sowie längere Laufzeit fehlen.
- OLED-Stromabschaltung, Schlafmodus, Batterie-/Solar-Energiebilanz und Frost-Ladeschutz nicht gemessen/validiert.
- Regionsnamen im EEPROM maximal **11 ASCII-Bytes**, da `REGION_SAVE_NAME_LEN=12` den Terminator einschließt. Größere Werte können beim Neustart gekürzt werden.

## [v0.7.0-ph123] – getestet am 21.–22.10.2026

### Added

- `cubecell_board_plus` / HTCC-AB02-Konfiguration in PlatformIO.
- Unterstützung von variablen **1-/2-/3-Byte-Pfad-Hashes** in Paketverarbeitung und Teilen der Weiterleitungslogik.
- Angepasste Serialisierung/Deserialisierung, Routing-Pfadverarbeitung, Flood-Fortschreibung und Schleifenerkennung.
- Firmwarekennung `v0.7.0-ph123` als experimentelle Erweiterung des Upstream-Releases `v0.7.0`.

### Changed

- Umfangreiches serielles Debug-Logging reduziert, damit die Firmware die Flash-Grenze einhält.
- Reproduzierter Basis-Build: **126.712 B Flash / 8.584 B RAM**.

### Verified

- SX1262-Boot, Empfang, Senden, Forwarding, KiekR-Erkennung, direkter Ping (**RTT 667 ms**).
- Zeitübernahme über `time <unix>` und beobachteter Sync nach Zero-Hop-Advert des Wio Tracker L1 Pro.
- Gleich großer Build auf einem zweiten Windows-Rechner am 22.10.2026.
- Basis-Commit [`99e369f`](https://github.com/FLOKHOME/CubeCellMeshCore-AB02-Solar/commit/99e369f).

### Known limitations

- Kein gezielter End-to-End-Nachweis mit 2-/3-Byte-Pfaden über mehrere Hops.
- Kein validierter unbeaufsichtigter Solar-/Winterbetrieb.

## Historische Fehlversuche (nicht der aktuelle Status)

- Erster PathHash-v3-Build mit **130.784 B Flash**: Bootloader meldete `Checksum does not verify` trotz erfolgreicher Kompilierung.
- Quiet-Logging reduzierte den Flashbedarf auf **126.712 B** und ermöglichte einen erfolgreichen Upload.
- Heltec-OLED-Library: Linkergrenze erreicht; TinyOLED mit `Wire.h` ebenfalls zu groß.
- Software-I²C ermöglichte erstmals die OLED-Ausgabe (früher Build **128.120 B Flash / 9.624 B RAM**), zunächst noch ohne funktionsfähigen Timeout.
- Ein früher Timeout-Patch erzeugte eine Regression; die später integrierte OLED-/Tasterlösung **funktioniert** und ist im Branch `feature/oled-diagnostics` gesichert.
- Ein früher Provisionierungsversuch verwendete `region put NAME PARENT`; die Firmware versteht jedoch nur das **flache** Modell `region put NAME`.
- Vor der Regionskapazitätserweiterung wurde der fünfte benannte Eintrag (`de-ni`) mit `ERR` abgewiesen.
- Vor dem Persistenz-Fix meldete `region save` `Unknown`; das allgemeine `save` sicherte die Regionsliste nicht. **Im aktuellen Stand behoben.**

## Herkunft

Upstream: [atomozero/CubeCellMeshCore](https://github.com/atomozero/CubeCellMeshCore), MIT. Die hier genannten Versionsnummern sind **nicht** mit offiziellen MeshCore-1.x-Versionen gleichzusetzen.
