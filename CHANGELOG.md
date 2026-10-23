# Changelog – FLOKHOME HTCC-AB02 Fork

Dieses Changelog beschreibt **Entwicklungsstände dieses Community-Forks**, nicht offizielle MeshCore-Releases. Die Originalhistorie von [atomozero/CubeCellMeshCore](https://github.com/atomozero/CubeCellMeshCore) steht in [`docs/UPSTREAM_README.md`](docs/UPSTREAM_README.md) und in der Git-Historie.

## [v0.8.1] – 22.10.2026

**Sichtbarkeit ohne Zeitquelle.** Behebt den Zirkelschluss, durch den ein Repeater ohne Zeit-Sync dauerhaft unsichtbar blieb, und macht den ADVERT-Takt über einen RESET hinweg stabil. Noch **nicht auf Hardware verifiziert** — der Build ist sauber, die Logik ist aber nur im Code geprüft.

### Added

- **Fallback-ADVERT ohne Zeit-Sync.** Bisher kehrte `checkAdvertBeacon()` bei fehlender Synchronisation sofort zurück: kein ADVERT → kein Public Key in der App → keine Fernkonsole, keine Diagnose. Nach **2 Stunden** ohne Sync wird jetzt ein Zero-Hop-ADVERT gesendet, danach stündlich (`ADVERT_FALLBACK_NO_SYNC_MS`, `ADVERT_FALLBACK_INTERVAL_MS`). Der Zeitstempel darin ist uptime-basiert; strenge Peers können das Paket verwerfen, aber direkte Nachbarn lernen den Schlüssel kennen. Auf einem versiegelten Solar-Gerät ist das der einzige Weg zurück.
- **ADVERT-Takt übersteht einen RESET.** Der Zeitpunkt des letzten ADVERT wird als Unix-Zeit in `PersistentStats.lastAdvertUnix` gespeichert. Nach dem Zeit-Sync wird der Zeitplan daraus wiederhergestellt (`AdvertGenerator::setElapsedSeconds()`). Ein Neustart beginnt also nicht mehr bei null. War der letzte ADVERT jünger als 10 Minuten, wird der zusätzliche Sofort-ADVERT nach dem Sync unterdrückt (`ADVERT_POST_SYNC_MIN_AGE_MS`).
- **Diagnose-Zeile für den ersten empfangenen ADVERT.** Einmal pro Start erscheint `[ADV] rx ts=<unix> len=<bytes>` über `LOG_RAW`. Der Wert `0` bedeutet: der Absender hat keine gültige Uhr, aus diesem Paket lässt sich keine Zeit ziehen — genau der Fall, der das ADVERT-Gate geschlossen hält. Damit ist die Ursache in Sekunden erkennbar.
- Prüfsummen-/Layout-Absicherung: `static_assert` stellt sicher, dass der Statistikblock den Mailbox-Block nicht überlappt.

### Changed

- `PersistentStats` auf **Version 2** und **56 Byte** erweitert (vorher 52). Die vier zusätzlichen Bytes lagen vorher ungenutzt bei Offset 332–335; der Block endet jetzt exakt bei 335, die Mailbox bei 336 bleibt unberührt. **Beim ersten Start nach dem Update werden die gespeicherten Zähler einmalig zurückgesetzt** (Versionswechsel) — Einstellungen, Identität, Regionen und Mailbox sind nicht betroffen.
- Firmwarekennung auf **`0.8.1`** gesetzt (`ver`, Boot-Banner).

### Build

- `v0.8.1` **mit** `config/repeater.json`: **129.248 / 131.072 B Flash (98,6 %)**, **9.632 / 16.384 B RAM (58,8 %)**, `SUCCESS`, keine Warnungen. Reserve: **1.824 B**.
- Konfig-Tests `python3 tools/test_user_config.py` → **18/18**; Krypto-Host-Test `tools/hosttest/run.sh` → alle Fälle grün.

### Still open

- Hardware-Gegenprobe im Feld: erscheint der Knoten nach dem Fallback in der App, und wächst `ADV:tx` in `stats`?
- Regionen nach Store-and-Forward, gerichteter Ping über 2+ Hops (unverändert offen aus v0.8.0).

## [v0.8.0] – 22.10.2026

**Erstes stabiles Release dieses Forks auf `main`.** Es fasst die bedarfsgesteuerte OLED-Diagnose, die persistente Regionsspeicherung, das korrigierte EEPROM-Layout, die zentrale Konfiguration `config/repeater.json` sowie mehrere Puffer- und CLI-Korrekturen zusammen. Die Arbeitszweige `feature/oled-diagnostics` (`bf9c48b`) und `docs/project-documentation` sind vollständig in `main` aufgegangen; der Review-Zweig `fix/eeprom-layout-review` wurde nach `main` gemergt.

### Added

- Zentrale Build-Zeit-Konfiguration **`config/repeater.json`**: `tools/gen_user_config.py` validiert die Datei beim Kompilieren und übersetzt sie in `src/generated/UserConfigData.{h,cpp}` — bewusst **ohne JSON-Parser in der Firmware** (das Image ist zu ~98 % gefüllt). Übernommen wird nur bei geändertem Fingerabdruck (`NodeConfig.configHash`); Prüfbefehle `config` und `config apply`. (`a674a17`)
- Diagnoseanzeige auf dem **SH1107-OLED** per **USER-Taster** mit Software-I²C und automatischem Abschalten nach ungefähr **10 Sekunden**.
- Tasterentprellung gegen ungewollte bzw. mehrfach ausgelöste Displayaktivierung.
- Regionenkapazität von **4 auf 5 benannte Einträge** erweitert; Wildcard `*` wird zusätzlich separat geführt.
- EEPROM-Reservierung von **576 auf 640 Bytes** erhöht (drei Flash-Zeilen à 256 Byte).
- Host-Regressionstest `tools/hosttest/run.sh`, der die echten Krypto-Header gegen eine portable Crypto-Bibliothek auf dem PC kompiliert.

### Fixed

- **EEPROM-Layout:** `EEPROM_SIZE` war doppelt definiert (640 in `main.h`, 576 in `core/Config.h`); die Region-Map schrieb bis Offset 580, wobei die 5. Region Flags und Namensende verlor. Jetzt eine einzige Quelle (`core/StorageLayout.h`) mit `static_assert`- und `#error`-Schutz. (`c9cbde8`)
- **Mailbox:** Der Mailbox-Block überlappte den Region-Header; ein einziges zwischengespeichertes Paket löschte die Region-Magic, nach RESET waren alle Regionen weg. Mailbox auf 84-Byte-Slots bei Offset 336 verlegt. (`a674a17`)
- **ADVERT-Intervall:** `setup()` setzte das Intervall nach `loadConfig()` unbedingt auf 5 min zurück und schrieb das ins EEPROM. Reihenfolge korrigiert; der gespeicherte Wert bleibt nach RESET erhalten. (`cc95656`)
- **Krypto/Stack:** `MACThenDecrypt()` begrenzte die Ausgabe nicht — ein ANON_REQ mit bis zu 145 Byte lief in einen 128-Byte-Puffer über, vor der Authentifizierung erreichbar. `zeroPad()` verschlüsselte bei leerer Eingabe uninitialisierten Stack. (`5362dad`, mit Host-Regressionstest)
- **Sitzungsverwaltung:** Ein Admin konnte durch wiederholte Gast-Logins aus der Sitzungstabelle verdrängt werden.
- **Weitere:** `findByName()`-Unterlauf, Mailbox-`load()`-Validierung, Werte-Wrap bei `set tx`/`txdelay` u. a., CayenneLPP-Überlauf, `floodAdvertHrs`-Wrap, unnötiges Re-Broadcast eines eigenen DIRECT-Pakets.

Details und Nachweise: [Review-Fixes](docs/AB02/REVIEW_FIXES.md).

### Changed

- Firmwarekennung auf **`0.8.0`** gesetzt (`ver`, Boot-Banner).
- RGB-/NeoPixel-LED ist in der getesteten Entwicklungsfirmware deaktiviert.
- Serielle Befehlsverarbeitung für die Regionsspeicherung korrigiert. Allgemeines `save` nicht mit `region save` verwechseln.
- Geräteprofil: `DE-NI-HARSUM01`; getestete Regionen `*`, `de`, `de-nord`, `de-mitte`, `de-west`, `de-ni`, jeweils Flood erlaubt (`A`).
- Regionen werden **flach** verwaltet. `region put NAME` ist der bestätigte Befehl; Parent-Angaben in Profilen erzeugen **keine** Regionshierarchie.

### Verified on hardware

- **Das ADVERT-Intervall übersteht einen RESET.** Boot-Log der geflashten Firmware (der Versionsstring darin war noch der alte; der Code enthielt die Review-Korrekturen bereits):

  ```text
  CubeCellMeshCore v0.7.0-ph123-oled EU868
  [C] Loaded (report=off, alert=off)
  [S] Stats loaded (boots=23, rx=185, tx=186, nodes=80)
  [ID] Loaded
  [A] ADV: on every 7200s
  config
  Cfg:built-in fp:4AF69790 stored:applied
  advert interval
  Int:120m next:7165s
  region
  *:A
  de:A
  de-nord:A
  de-mitte:A
  de-west:A
  de-ni:A
  ```

  Entscheidend ist die **fehlende** Zeile `[C] User config applied`: die `config/repeater.json` wurde in diesem Boot **nicht erneut** angewendet. Der Wert `7200 s` stammt damit aus `loadConfig()` (EEPROM) und nicht aus der Build-Konfiguration — genau der Fall, den `cc95656` repariert hat. Zusätzlich belegt `[A] ADV:` (Tag erst ab `cc95656` vorhanden), dass der gefixte Code läuft.
- **Zentrale Konfiguration wird übernommen:** `Cfg:… stored:applied`, und `advert interval` liest `Int:120m` entsprechend `advertising.local_interval_minutes: 120`. Der abweichende Fingerabdruck `4AF69790` gehört zum angepassten lokalen `config/repeater.json` des Betreibers, nicht zur Beispielkonfiguration im Repo.
- **Regionen:** alle sechs Einträge (`*` plus fünf benannte) sind nach dem RESET unverändert vorhanden.
- **Deep Sleep im Akku-/Solarbetrieb** (`power.deep_sleep: true`) läuft; die serielle Konsole ist nur innerhalb von `BOOT_SAFE_PERIOD_MS` (2 min) nach dem RESET erreichbar.
- OLED lässt sich per USER aktivieren, schaltet nach ca. 10 s wieder aus und zeigte nach Entprellung keine unbeabsichtigten Aktivierungen im Test.
- RGB-LED bleibt im getesteten Zustand aus.
- Gerätekennung und Name `DE-NI-HARSUM01` bleiben erhalten.

### Build

- `v0.8.0` **ohne** `config/repeater.json`: **128.200 / 131.072 B Flash (97,8 %)**, **9.624 / 16.384 B RAM (58,7 %)**, `SUCCESS`.
- `v0.8.0` **mit** `config/repeater.json`: **128.936 / 131.072 B Flash (98,4 %)**, **9.624 / 16.384 B RAM (58,7 %)**, `SUCCESS`.

Beide Werte wurden mit dem Release-Stand `v0.8.0` **neu gemessen**. Frühere Angaben (127.472 B ohne / 128.960 B mit Konfiguration) stammten aus einem Zwischenstand vor den Krypto-/CLI-Fixes und sind überholt. Die eingebaute Konfiguration kostet rund **736 B** Flash. Wegen des CubeCell-Bootloaders sagt ein erfolgreicher Build noch nichts über einen erfolgreichen Upload oder Funkbetrieb. Der Flash ist mit 98,4 % nahezu voll — neue Funktionen brauchen vorher Platz.

### Pending / limitations

- **Regionen nach einem Store-and-Forward** (`mailbox` zeigt `E1:`, danach RESET) sind auf Hardware noch nicht gegengeprüft.
- **Gerichteter Ping/Trace über 2+ Hops** fehlt weiterhin (Prüft den DIRECT-Forward-Fix).
- **24-h-Lauf mit Solar/Akku** sowie Frost-Ladeschutz sind nicht gemessen/validiert.
- Funkweiterleitung **nach** dem letzten EEPROM-/OLED-Update ist nicht erneut end-to-end nachgewiesen.
- Regionsnamen im EEPROM maximal **11 ASCII-Bytes**, da `REGION_SAVE_NAME_LEN=12` den Terminator einschließt. Größere Werte können beim Neustart gekürzt werden.
- **Mit `deep_sleep: true` ist die serielle Konsole nur 2 Minuten nach RESET erreichbar** (`BOOT_SAFE_PERIOD_MS`). Für Messungen am Tisch `sleep off` eingeben (bleibt im EEPROM) oder die USER-Taste für ein ca. 10-sekündiges Konsolenfenster nutzen.
- Der Health-Monitor führt Knoten nach **30 Minuten** ohne Kontakt als offline (`HEALTH_OFFLINE_MS`). Bei ADVERT-Intervallen über 30 min erscheint der Repeater für andere Knoten entsprechend lange als offline.
- Ob der ADVERT im Deep Sleep **tatsächlich im Raster gesendet** wird, ist noch nicht gemessen. Prüfweg: `stats` liefert `ADV:<tx>/<rx>`; zweimal mit Abstand von über einem Advert-Intervall aufrufen, ohne dazwischen zu resetten (USER-Taste öffnet das Konsolenfenster).

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
