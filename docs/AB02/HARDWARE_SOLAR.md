# Hardware und Solarplanung

**Status: 22.10.2026.** Der Repeater funktioniert als USB-versorgtes Entwicklungsgerät. Ein sicherer, unbeaufsichtigter Solar-/Akku-Dauerbetrieb ist **nicht** validiert.

## Vorhandene oder betrachtete Komponenten

| Komponente | Beobachtung / Status |
| --- | --- |
| **Heltec CubeCell HTCC-AB02 V1.0** mit ASR6502, SX1262, SH1107-OLED | Funk auf Basisstand, OLED/Taster und EEPROM auf Entwicklungsstand getestet |
| Externe 868-MHz-Antenne | Im Funk-Test verwendet; Stecker, Gewinn und Montage noch zu prüfen |
| **Solarpanel ca. 8 × 11 cm** | **Leerlaufspannung ca. 6,52 V bei Sonnenschein gemessen**; Kennlinie/Leistung nicht bekannt |
| 18650-Akkuhalter und Li-Ion-Zellen | Vorhanden/betrachtet; konkrete Zellen, Schaltung und Schutz nicht validiert |
| Ladeplatinen bzw. CubeCell-Ladepfad | Auswahl und Eignung für das genaue Panel/Zellmodell noch nicht bestätigt |
| Outdoor-Gehäuse | Noch kein validierter Wetterschutz |

Das CubeCell besitzt je nach Boardrevision einen Lade-/Solareingang. **Die gemessenen 6,52 V sind Leerlaufspannung, keine zulässige Anschlussfreigabe.** Vor Verdrahtung die Herstellerangaben für exakte Platinenrevision, zulässige Spannung/Strom, Polarität, Ladeschaltung und Akkutyp überprüfen.

## Bestätigte Diagnosefunktionen

- OLED **SH1107** erscheint auf USER-Tasterdruck und schaltet nach ca. **10 s** wieder ab.
- Tasterentprellung erfolgreich auf dem Entwicklungsgerät getestet.
- RGB-/NeoPixel-LED ist im getesteten Firmwarestand deaktiviert.
- **Nicht gemessen:** ob die OLED-Versorgung tatsächlich abgeschaltet wird, der Stromverbrauch im Normalbetrieb, das Aufwecken aus jedem Sleep-Zustand und die Systemleistung unter Akkuspannung.

## Mess- und Sicherheitsplan

1. Solarpanel **unter Last** messen: Spannung, Strom, Leistungsmaximum und Verhalten bei schwachem Licht; besondere Aufmerksamkeit der maximalen Leerlaufspannung bei Kälte.
2. Ladeeingang und elektrisches Datenblatt des **HTCC-AB02 V1.0** vergleichen. Kein direkter Anschluss allein aufgrund einer gemessenen `Voc`.
3. Akkutyp, Polung, Kapazität, Über-/Tiefentladeschutz und Sicherung klären. Mehrfachhalter auf Reihen-/Parallelschaltung prüfen – **keinen Reihensatz an einen 1S-Ladeeingang** anschließen.
4. Batterie-seitige Stromaufnahme messen: Sleep an/aus, OLED aus/an, RGB deaktiviert, serieller Monitor, Funk-Bursts. **USB-Strom ist nicht gleich Batterie-Strom.**
5. Wh/Tag ermitteln und die Winter-Energiebilanz mit mehrtägigen Schlechtwetterreserven dimensionieren.
6. **Temperaturüberwachte Ladesperre bei Frost** vorsehen; übliche Li-Ion-Zellen ohne explizite Freigabe nicht unter 0 °C laden.
7. Unterspannungsabschaltung, Wiederanlauf nach Tiefentladung, mechanischen Zellschutz und Schaltungsfehler prüfen.
8. Gehäuse, Kondensation, Leitungsdurchführungen, Antennenzuleitung und EMV/Funkabstrahlung testen.

## Funkrecht und Betrieb

Der ältere Test verwendete **869.618 MHz**, **BW 62.5 kHz**, **SF8**, **CR8**; im Log wurden **21 dBm** gemeldet. Das belegt **keine** zulässige EIRP, maximale Sendezeit oder Einhaltung geltender Frequenzregelungen. Antennengewinn, Betriebsdauer und aktuelle Vorschriften vor dauerhaftem Einsatz kontrollieren.

**Nicht behauptet:** zertifiziertes Funkgerät, geprüfte Solar-Ladeschaltung, wintertaugliche Ladung, wasserdichter Aufbau oder ganztägig/ganzjährig autarker Betrieb.
