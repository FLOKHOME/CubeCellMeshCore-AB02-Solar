# Protokollkompatibilität und Grenzen

**Stand: 22.10.2026.** Der Fork basiert auf **`atomozero/CubeCellMeshCore v0.7.0`**, nicht auf der vollständigen offiziellen MeshCore-1.x-Quellbasis. Versionsnummern sind **nicht** direkt vergleichbar.

## Variable MeshCore-Pfadkennungen

Der Fork interpretiert den kodierten Pfad-Header wie folgt:

```cpp
hashSize = (pathLen >> 6) + 1;   // 1, 2 oder 3 Byte unterstützt
hopCount = pathLen & 0x3F;
pathBytes = hopCount * hashSize;
```

Die reservierte Breite 4 Byte wird abgewiesen. Die Anpassungen betreffen Paketlängen, Serialisierung/Deserialisierung, komplettes Hash-Präfix beim Flooding, Peeling eines Hop-Hashes beim Direct-Routing und die Loop-Detection.

**Auf früherem Basisstand geprüft:** Boot, LoRa RX/TX/Forwarding, Sichtbarkeit in KiekR, direkter Ping (667 ms). **Nicht gezielt geprüft:** korrekte End-to-End-Zustellung über weitere Hops mit realen 2- und 3-Byte-Pfad-Hashes. Beobachtete `Bad pkt`-Meldungen haben keine abschließend bestätigte Ursache.

## Regionen und Flood-Entscheidung

Der Entwicklungsbranch `feature/oled-diagnostics` unterstützt **fünf benannte, flache Regions-Einträge** und eine separat gespeicherte Wildcard. Im praktischen Test wurden `*`, `de`, `de-nord`, `de-mitte`, `de-west` und `de-ni` mit Flood-Flag `A` aktiviert und mit `region save` nach RESET persistent nachgewiesen.

- `region put NAME` legt einen flachen Eintrag an; eine **Parent-Child-Hierarchie** existiert in dieser Implementation **nicht**.
- Namen beeinflussen die daraus abgeleiteten Region-Keys; im EEPROM werden maximal **11 ASCII-Bytes** je Name dauerhaft gespeichert.
- Der zusätzliche Regionsspeicher beansprucht EEPROM-Adresse **512–580** bei einer Gesamtreservierung von **640 Bytes**.
- Der direkte Test der **aktuellen** Version beim Forwarding über mehrere unterschiedliche Regionen steht noch aus.

Siehe [Konfiguration](CONFIGURATION.md) und [Featurestatus](../../FEATURES.md).

## Reproduzierbare Protokolltests

1. Ein CubeCell und mindestens zwei voneinander unabhängige MeshCore-Geräte verwenden.
2. Exakten Commit, Radioeinstellungen, Hash-Breite, Hop-Reihenfolge und Firmwarestände protokollieren.
3. Echte Routen mit 1-, 2- und 3-Byte-Pfad-Hashes testen; Zustellung **am Zielgerät** bestätigen.
4. Negative Fälle testen: falsche Route, zu langer Pfad, reservierte Kodierung, Schleifen, Duplikate, unerlaubte Regionscodes.
5. `stats` und `lifetime` vor und nach jedem Test notieren, ohne private Schlüssel, Tokens oder exakte Standortdaten öffentlich zu machen.

Erst danach belastbare Aussagen zur Mehrhop-Interoperabilität veröffentlichen.
