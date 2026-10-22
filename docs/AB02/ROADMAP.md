# Roadmap – CubeCellMeshCore AB02 Solar

Priorität bedeutet Reihenfolge für dieses Projekt, nicht allgemeine Produktreife des Originalprojekts.

## P0 – Reproduzierbarkeit und Basis sichern

- [x] HTCC-AB02 in PlatformIO (`cubecell_board_plus`) kompilieren.
- [x] Empfang, Aussendung, Repeater-Erkennung und KiekR-Ping durchführen.
- [x] PathHash v3 + Quiet-Logging integrieren; 126.712-B-Flash-Build.
- [x] Buildwerte auf zweitem Windows-Rechner reproduzieren.
- [x] GitHub-Fork anlegen und Commit `99e369f` auf `main` pushen.
- [ ] Dokumentations-Branch prüfen und nach `main` mergen.
- [ ] Funktionierenden Basisstand mit Git-Tag kennzeichnen, **erst nach Dokumentationsprüfung**.

## P1 – OLED/LED als separater Branch

- [x] OLED reagierte auf USER-Taster im ersten Hardwaretest.
- [x] **Laut aktualisierter Nutzerbeobachtung:** OLED schaltet nach ca. 10 Sekunden ab.
- [ ] Zu dieser funktionierenden OLED-Version die **exakten Quelländerungen rekonstruieren** und committen.
- [ ] RGB-LED (rot/violett) im Normalbetrieb abschalten; `MC_SIGNAL_NEOPIXEL` und `Vext`-Wirkung überprüfen.
- [ ] Stromversorgung des OLEDs nach Timeout überprüfen, nicht nur Displaybild.
- [ ] Mehrfach drücken, Bounce, CPU-Sleep, Watchdog und erneutes Aufwecken testen.
- [ ] Funkbetrieb vor/während/nach OLED-Anzeige ohne Regression nachweisen.

## P2 – Protokoll

- [ ] 1-/2-/3-Byte-Pfad-End-to-End-Test mit mindestens einem zusätzlichen Hop.
- [ ] Fremd-/Fehlerpakete auf reproduzierbare Ursachen prüfen.
- [ ] Ping-Adressierung, Trace, Direct/Flood, Loop-Detection und Retry-Logik testen.
- [ ] 24h+ Stabilitäts- und Paketverlusttest.

## P3 – Solar und Outdoor

- [ ] Panelspannung und Akkuzustand messen.
- [ ] Li-Ion-Ladesicherheit einschließlich Frost-Ladesperre klären.
- [ ] Stromverbrauch mit/ohne LED/OLED und verschiedenen Sleep-Modi messen.
- [ ] Panel-/Akku-Dimensionierung anhand Winterverbrauch auslegen.
- [ ] Gehäuse, Antenne, Dichtungen, Kondensation und Wiederanlauf testen.
- [ ] Funkrechtliche EIRP-/Duty-Cycle-Prüfung dokumentieren.

## Release-Kriterien

Ein Release darf erst als **hardwaregetestet** bezeichnet werden, wenn Build, Upload, Funk, User-Taster/LED-Funktionen und jeweilige Einschränkungen für genau diesen Quellcommit dokumentiert sind. **Solar-autonom** erst nach mehrtägigem Versorgungstest; **vollständige MeshCore-1.18-Kompatibilität** wird derzeit ausdrücklich **nicht** behauptet.
