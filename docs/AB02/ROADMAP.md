# Roadmap – CubeCellMeshCore AB02 Solar

**Stand: 22.10.2026.** Prioritäten beziehen sich auf dieses konkrete Testgerät, nicht auf allgemeine Produktreife.

## P0 – Basis reproduzieren und sichern

- [x] HTCC-AB02 via PlatformIO `cubecell_board_plus` bauen und flashen.
- [x] SX1262-Empfang/Senden, Forwarding, KiekR-Sichtbarkeit und Ping auf Basisfirmware bestätigen.
- [x] 1-/2-/3-Byte-PathHash und Quiet-Logging integrieren; Basis-Build 126.712 B Flash.
- [x] Basis-Build auf zweitem Windows-Rechner mit identischer Größe reproduzieren.
- [x] Fork `FLOKHOME/CubeCellMeshCore-AB02-Solar` und Basis-Commit `99e369f` auf GitHub sichern.
- [x] Projektdokumentation auf `main` übernehmen (laut durchgeführtem Projektworkflow).
- [x] OLED-/Regionsquellstand mit Commit `bf9c48b` auf `feature/oled-diagnostics` pushen.
- [ ] Feature-Branch **nach letztem Funk-Regressionstest** per PR reviewen und nach `main` übernehmen.
- [ ] Geprüften Stand als Version/Tag kennzeichnen; noch **keine** stabile oder solarautonome Version behaupten.

## P1 – OLED, LED und Regionenkonfiguration

- [x] USER-Taster aktiviert SH1107-OLED mit Software-I²C.
- [x] OLED schaltet nach ca. 10 Sekunden ab.
- [x] Tasterentprellung im Hardwaretest bestätigt.
- [x] RGB-/NeoPixel-LED im getesteten Firmwarestand deaktiviert.
- [x] `REGION_MAX_ENTRIES` auf fünf benannte Regionen erweitert; EEPROM auf 640 Bytes angepasst.
- [x] `region save` repariert; alle benannten Regionen und Wildcard nach RESET erhalten.
- [x] Gerätekonfiguration `DE-NI-HARSUM01` nach RESET bestätigt.
- [ ] Mit **aktuellem** Commit RX/TX/FWD, Ping, Uhrzeitübernahme und unerwartete Resets prüfen.
- [ ] OLED-Versorgung/Stromaufnahme **messen** und Taster-Wake-up aus Sleep prüfen.
- [ ] Debounce/Timeout unter mehrfacher Betätigung und bei längerer Laufzeit dokumentieren.
- [ ] Provisionierung v4 und geprüftes Profil ohne sensible Informationen versionieren.

## P2 – Protokoll und Stabilität

- [ ] Echten 1-/2-/3-Byte-Multihop-End-to-End-Test mit unabhängiger Zustellbestätigung durchführen.
- [ ] Trace, Direct/Flood, Loop-Detection, Retries sowie ungültige Pakete prüfen.
- [ ] 24h+-Stabilitäts- und Paketverlusttest mit aktuellem Commit.
- [ ] Bei Bedarf Eltern-Kind-Regionshierarchie als **neue Funktion** spezifizieren; aktuelle Namen sind flach.
- [ ] EEPROM-Format-/Migrationstests für zukünftige Kapazitätsänderungen vorbereiten.

## P3 – Solar und Outdoor

- [x] Leerlaufspannung des vorhandenen ca. 8 × 11 cm-Panels im Sonnenlicht erfasst (**ca. 6,52 V**).
- [ ] Panelspannung **unter Last**, Strom und tatsächliche Ladeleistung messen.
- [ ] 18650-Zelle(n), Schutz, Ladeschaltung, Polarität und zulässige Eingangsspannung validieren.
- [ ] **Ladesperre bei Frost** für verwendete Li-Ion-Zelle/Lader sicherstellen.
- [ ] Verbrauch mit OLED an/aus, RGB aus, Sleep und TX-Bursts messen.
- [ ] Aus Winter-Energiebilanz nötige Kapazität und Reserven berechnen.
- [ ] Gehäuse, Dichtungen, Kondensation, Antennenführung und Wiederanlauf nach Entladung prüfen.
- [ ] EIRP, Duty-Cycle und lokale Funkregeln dokumentieren.

## Abnahmekriterien

Ein Funktionsstand ist nur dann als **hardwaregetestet** zu bezeichnen, wenn Quellcommit, Build, Upload und der konkrete Test nachweisbar zusammenpassen. Ein Build ist nicht gleich Funkabnahme; ein sichtbares OLED-Timeout ist kein Strommesswert. **Solarautonom** erst nach einem mehrtägigen, abgesicherten Versorgungs- und Temperaturtest. Der Fork beansprucht keine vollständige Kompatibilität mit offiziellen MeshCore-1.x-Releases.
