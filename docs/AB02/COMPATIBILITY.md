# Protokollkompatibilität und Grenzen

## Ausgangslage

Das Projekt basiert auf `atomozero/CubeCellMeshCore v0.7.0`, **nicht** auf der vollständigen offiziellen MeshCore-1.18-Quellbasis. Die Versionsnummern sind nicht unmittelbar vergleichbar.

Die ursprüngliche Paketinterpretation behandelte das Feld `pathLen` wie eine reine Bytezahl. Neuere MeshCore-Pakete verwenden darin die **Pfad-Hash-Breite** und die **Hop-Anzahl**. Der Fork führt folgende Interpretation ein:

```cpp
hashSize = (pathLen >> 6) + 1;   // 1, 2 oder 3 Byte unterstützt
hopCount = pathLen & 0x3F;
pathBytes = hopCount * hashSize;
```

Die reservierte Breite 4 Byte wird abgewiesen. Der Patch verändert darüber hinaus:

- Serialisierung/Deserialisierung und Länge auf dem Funkkanal.
- Anhängen des eigenen vollständigen Hash-Präfixes im Flood-Modus.
- Entfernen eines kompletten Hop-Hashs beim Direct-Routing.
- Schleifenerkennung anhand ganzer Hashs statt beliebiger Einzelbytes.
- Einige Airtime-/Pfadlängen-Berechnungen.

## Wichtig: implementiert ist nicht gleich nachgewiesen

- **Getestet:** Firmware baut und startet, empfängt und sendet; KiekR sieht Node und beantwortet Zero-Hop-Ping.
- **Noch nicht gezielt getestet:** Ein echtes 2-Byte- bzw. 3-Byte-Routing-Paket wird vom CubeCell über mindestens einen weiteren Hop korrekt zugestellt und bestätigt.
- Path-/TRACE-Behandlung und Kompatibilität zu beliebigen neueren Protokollfeatures wurden noch nicht vollständig geprüft.
- Früher beobachtete `Bad pkt`-Meldungen könnten verschiedene Ursachen haben. Es ist nicht nachgewiesen, dass sie sämtlich durch Mehrbyte-Hash-Unterstützung verschwinden.

## Vorschlag für reproduzierbare Protokolltests

1. Zwei oder mehr separate MeshCore-Geräte neben dem CubeCell vorsehen.
2. Aktuellen Firmwarestand, konkrete LoRa-Einstellungen, Path-Hash-Breite, Route und Hopfolge dokumentieren.
3. Route mit 1-, dann 2-, dann 3-Byte-Pfaden testen und Zustellung **am Zielgerät** bestätigen.
4. Negative Fälle: falsche Route, zu langer Pfad, reservierte Kodierung, Schleifen, Duplikate.
5. `stats` und `lifetime` vor/nach jedem Test protokollieren; Seriennummern, private Schlüssel, Standortkoordinaten und Tokens aus öffentlichen Logs entfernen.

Erst nach solchen Tests sollte ein konkretes Kompatibilitätsversprechen abgegeben werden.
