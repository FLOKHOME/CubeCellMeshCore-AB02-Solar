# Testbericht – HTCC-AB02

Stand: 22.10.2026. Testwerte stammen aus der praktischen Session am **21.10.2026** und dem reproduzierten Build am **22.10.2026**. Unbestätigte Annahmen sind ausdrücklich gekennzeichnet.

## Plattform

- Heltec CubeCell **HTCC-AB02 V1.0**, ASR6502, SX1262, EU868.
- Windows-CMD; PlatformIO Core **6.2.0** auf erstem System; USB-UART via CP210x, ursprünglich `COM9`.
- Funkparameter im Startlog: **869.618 MHz / BW 62.5 kHz / SF8 / CR8**, gemeldete Ausgangsleistung **21 dBm**.
- Testclient **Seeed Wio Tracker L1 Pro**, Steuerung über **KiekR**.
- Firmwarebasis `CubeCellMeshCore v0.7.0` von `atomozero`.

## Basisbetrieb (Upstream 0.7.0 mit AB02-Boardkonfiguration)

- Build: **130.536 B Flash / 8.584 B RAM**.
- `SX1262 init` und `[S] Ready` nach Boot.
- Paketempfang und Forwarding im Log: `RX:1 TX:1 FWD:1`.
- Repeater-ADVERT via UART (`advert`) wurde gesendet und in KiekR erkannt.
- Nach anfänglichem Timeout gelang ein direkter Ping: **RTT 667 ms**, SNR **Up +13,0 dB / Down +12,0 dB**.
- `Bad pkt`-Meldungen wurden beobachtet, aber nicht abschließend einer Ursache zugeordnet.

## Modifikation PathHash 1/2/3 Byte

- Patch v3: Paketdecoder/Encoder, Forwarding, Schleifenerkennung und Airtime-Berechnung angepasst.
- Erstes Build: **130.784 B Flash**; Upload meldete nach 100 %: **`Checksum does not verify! Aborting.`**
- Danach Quiet-Logging: **126.712 B Flash / 8.584 B RAM**, Upload und Boot erfolgreich.
- Neue Kennung: `v0.7.0-ph123`.
- KiekR-Ping erneut erfolgreich: **RTT 667 ms, Up +11,7 dB / Down +13,0 dB**.

### Statistik während eines Laufs

| Uptime (s) | RX | TX | FWD | Fehler `E` | Queue `Q` |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 209 | 13 | 13 | 13 | 0 | 0 |
| 247 | 16 | 16 | 16 | 0 | 0 |
| 294 | 19 | 18 | 19 | 0 | 1 |

Gesamtstatistik bei letzter Abfrage: `Boots:5 Up:1507s RX:61 TX:58 FWD:46`. Das ist ein **kurzer Feldtest**; keine 24h-Stabilitätsmessung.

Ein Zähler `FWD` dokumentiert, dass der Repeater ein Paket zur Weiterleitung verarbeitet/eingeplant hat. Er beweist **nicht**, dass ein entferntes Endgerät dieses Paket erhalten hat. `E:0` in diesem Lauf heißt nicht, dass künftig keine inkompatiblen Pakete auftreten.

## Zeit-Synchronisierung

- Manuell per `time <Unix-Zeit>`: `Time set: ...`, danach `status` mit `T:sync` und fortlaufendem `time`.
- Nach Neustart `T:nosync`; anschließend **Zero-Hop-Advert** auf dem Wio Tracker L1 Pro in KiekR ausgelöst.
- CubeCell wechselte nachweislich wieder auf `T:sync`.
- Wiederholbarkeit über viele Neustarts und Zeitquellen noch nicht getestet.

## Diagnose-Sleep

- Anfangs nahm UART nach einiger Laufzeit keine Befehle an.
- `sleep off` direkt nach Reset ergab `sleep:off` und gespeicherte Konfiguration.
- Danach war die serielle Konsole über mindestens 294 Sekunden erreichbar.
- Aussage zum Stromverbrauch bei `sleep off` ist **noch nicht** durch Messung gedeckt.

## OLED-Experimente – aktueller Kenntnisstand

1. Heltec-DISPLAY-Bibliothek: Linker meldete `region 'rom' overflowed by 0 bytes`.
2. TinyOLED mit `Wire.h`: ebenfalls zu groß.
3. Soft-I²C: Build **128.120 B Flash / 9.624 B RAM**, OLED wurde durch USER sichtbar aktiviert; zunächst kein Timeout.
4. Früher Timeout-Fix: Regression, OLED reagierte nicht mehr; RGB-LED weiterhin rot/violett aktiv.
5. **Aktualisierte Nutzerbeobachtung vom 22.10.: OLED schaltet nun nach ca. 10 Sekunden aus.** Der exakte dazugehörige Quellstand ist auf dem neuen Windows-PC **nicht vorhanden bzw. nicht wiederhergestellt**. Die RGB-LED bleibt aktiv.

Keinen dieser OLED-Stände ohne Abgleich des tatsächlichen Sourcecodes als freigegebenen Branch/Release deklarieren.

## Zweitrechner / Reproduzierbarkeit

Am **22.10.2026** wurde die Funk-Basis aus Upstream-Clone plus PathHash-v3- und Quiet-Logging-Patch auf anderem Windows-Rechner erfolgreich gebaut:

```text
RAM:   52.4% (8584 / 16384 B)
Flash: 96.7% (126712 / 131072 B)
```

Der so erzeugte Sourcecode wurde in Git-Commit **`99e369f`** ins Fork-Repository auf `main` hochgeladen. Reproduzierte **Buildwerte** sind kein automatischer Binär-Hash-Nachweis.

## Noch fehlende Nachweise

- Echte 2-/3-Byte-Pfadrouten über mehrere MeshCore-Knoten mit verifizierter Zustellung.
- Längere Laufzeit, Resetverhalten, Schleifenerkennung, Überlast und Deduplizierung.
- OLED + LED-Zustand direkt aus einem gesicherten Commit nachvollziehen und auf derselben Hardware testen.
- Batteriespannung/-strom, Sleep-Strom, Energiebilanz, Frost-Ladeabschaltung und wasserdichter Solar-Aufbau.
