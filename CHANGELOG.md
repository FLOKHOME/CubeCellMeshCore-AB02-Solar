# Changelog – FLOKHOME HTCC-AB02 Fork

Dieses Dokument beschreibt **nur die Änderungen und Teststände dieses Forks**. Die ältere Versionshistorie von `atomozero/CubeCellMeshCore` steht weiterhin in [`docs/UPSTREAM_README.md`](docs/UPSTREAM_README.md) und in der ursprünglichen Git-Historie.

Format: dokumentierte Entwicklungsereignisse, **nicht** automatisch als stabile Releases zu verstehen. Die Firmware-Nummer `v0.7.0-ph123` gehört zu einer experimentellen Erweiterung des Upstream-Releases `v0.7.0`; sie ist **nicht** mit offiziellen MeshCore-1.x-Versionen gleichzusetzen.

## [Unreleased] – Stand 22.10.2026

### Dokumentation
- Fork-spezifische Dokumentation, Windows-Buildanleitung, Testprotokoll, Solarplanung und Roadmap angelegt.
- Original-README einschließlich Upstream-Changelog unverändert archiviert.

### OLED-Diagnose (separater Entwicklungszweig)
- SH1107-OLED-Anzeige über USER-Taster wurde auf dem ursprünglichen Testgerät zum Einschalten gebracht.
- **Nach Nutzerbestätigung am 22.10.: OLED schaltet nach ca. 10 Sekunden wieder aus.**
- **RGB-LED weiterhin aktiv.** Stromersparnis und korrekte `Vext`-Steuerung noch nicht bestätigt.
- **Wichtig:** Der zugehörige letzte funktionierende OLED-Quellstand liegt zum Dokumentationszeitpunkt **nicht** im Fork-`main`; der neue PC verfügt nur über den reproduzierten Basis-Build. Bis zu einem neuen erfolgreichen Build/Flash keine OLED-Funktion für `main` behaupten.

## [v0.7.0-ph123] – getestet am 21.–22.10.2026

### Added
- `cubecell_board_plus` / HTCC-AB02-Konfiguration in PlatformIO.
- Unterstützung variabler MeshCore-Pfadkennungen mit 1, 2 oder 3 Bytes je Hop im Parser und in Teilen der Weiterleitungslogik.
- Angepasste Paketgrößenberechnung, Direct-Routing-Peeling, Flood-Pfadfortschreibung und Pfadvergleich zur Schleifenerkennung.
- Eigenständige Firmwarekennung `0.7.0-ph123`.

### Changed
- Ausführliches Debug-Logging reduziert, um Platz für die Protokollerweiterung zu gewinnen; die serielle Kommandoausgabe bleibt nutzbar.
- Finaler Basis-Build: **126.712 Byte Flash, 8.584 Byte RAM**.

### Verified
- Erster Testaufbau: Boot, SX1262-Initialisierung, Empfang, Senden, Weiterleitung, KiekR-Sichtbarkeit und direkter Ping.
- Zeitübernahme über manuelles `time <unix>` sowie per Zero-Hop-Advert beobachtet.
- Am 22.10.2026 reproduzierter PlatformIO-Build auf einem zweiten Windows-PC mit identischen Speicherwerten.
- Commit: [`99e369f`](https://github.com/FLOKHOME/CubeCellMeshCore-AB02-Solar/commit/99e369f).

### Known limitations
- **2- und 3-Byte-Pfade**: Implementierung und lokale Logiktests, jedoch kein gezielter unabhängiger Mehrhop-Praxistest dokumentiert.
- Noch kein validierter unbeaufsichtigter Solar-/Winterbetrieb.

## Entwicklungsfehler, bewusst dokumentiert

- Erste v3-Version vor der Speicheroptimierung: **130.784 Byte Flash**, Upload endet nach 100 % mit `Checksum does not verify`.
- Quiet-Logging führt zu **126.712 Byte Flash** und ermöglicht erfolgreichen Upload.
- Frühe OLED-Variante mit Heltec-Displaybibliothek: Linkerfehler `region 'rom' overflowed by 0 bytes`.
- TinyOLED mit `Wire.h`: weiterhin zu groß.
- Software-I²C: Build mit **128.120 Byte Flash / 9.624 Byte RAM** und zunächst Einschalten der Anzeige auf Tastendruck möglich.
- Zwischenzeitlicher Timeout-Fix: Regression (OLED reagierte nicht mehr); spätere Meldung des Anwenders bestätigt ein funktionierendes 10-Sekunden-Timeout, **ohne gesicherten Quellstand im neuen Arbeitsverzeichnis**.

## Ursprungsprojekt

Basis: [atomozero/CubeCellMeshCore](https://github.com/atomozero/CubeCellMeshCore) unter MIT-Lizenz. Dessen Changelog und ursprüngliche Releaseangaben sind **nicht** durch die Versionsnummern dieses Forks ersetzt.
