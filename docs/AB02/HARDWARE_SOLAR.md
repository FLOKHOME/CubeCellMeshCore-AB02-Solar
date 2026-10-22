# Hardware und Solarplanung

## Vorhandene bzw. betrachtete Komponenten

| Bauteil | Stand |
| --- | --- |
| **Heltec CubeCell HTCC-AB02 V1.0** mit ASR6502, SX1262 und SH1107-OLED | Funkbetrieb nachgewiesen |
| Externe 868-MHz-Antenne und Anschlusskabel | Im Test benutzt; Stecker/Antennenanpassung prüfen |
| Solarpanel | Vorhanden, genaue Spannung/Leistung **noch nicht gemessen** |
| 18650-Akkuhalter, Einzel- und Mehrfachausführung | Vorhanden, Verschaltung und Akkuzustand **noch nicht geprüft** |
| TP4056-/weitere Ladeplatinen | Vorhanden, **noch keine freigegebene Solarverschaltung** |
| Outdoor-Gehäuse | Noch nicht konstruktiv/elektrisch freigegeben |

Das HTCC-AB02 besitzt eine integrierte Ladeschaltung und einen vorgesehenen Solareingang. **Vor einem Anschluss** die aktuelle offizielle Heltec-Schaltung/Dokumentation, zulässige Eingangsspannung, Polarität und Akkutechnologie für die exakte Platinenrevision prüfen. Es liegt noch **kein getesteter Verdrahtungsplan** vor.

## Erforderliche Messungen

1. Paneltyp, Leerlaufspannung `Voc`, Leistung am Arbeitspunkt und Spannung unter Last feststellen. Besonders wichtig: Die Leerlaufspannung kann über der nominellen Modulspannung liegen.
2. Akkutyp, Kapazität, Gesundheitszustand, Verpolschutz und Schutz vor Über-/Tiefentladung bestimmen.
3. Mehrfachhalter: Reihen-/Parallelschaltung mit Multimeter eindeutig bestimmen; **keinen Reihensatz an einen 1S-Anschluss** anschließen.
4. Stromaufnahme an der Batterie messen: Repeater mit `sleep on/off`, RGB-LED, OLED aus, OLED an, TX-Bursts. **USB-Strom ist nicht automatisch identisch mit Batterie-Strom.**
5. Lastprofil in Wh/Tag aus realen Messungen ermitteln; Winter-Einstrahlung und tagelange Dunkelphasen berücksichtigen.
6. Sicheren Start bei leerem Akku und bei Unterspannung nachweisen; Regenwasser, Kondensat und Kabeldurchführungen berücksichtigen.
7. Geeignete temperaturabhängige Ladeunterbrechung vorsehen. **Normale Li-Ion-Zellen nicht bei Temperaturen unter 0 °C laden**, sofern Zelle/Ladetechnik dies nicht ausdrücklich zulassen.
8. Antenne, Massebezug und Montageabstand zu leitenden Gehäuseteilen prüfen.

## Geplante Diagnosefunktion

- OLED im Normalbetrieb aus; USER-Taster zeigt Status für **ca. 10 Sekunden**.
- RGB-LED im Normalbetrieb aus. **Derzeit noch aktiv**, selbst nach nachgewiesenem OLED-Timeout.
- Kein dauerhafter Display- oder LED-Verbrauch im Zielbetrieb.
- Ob USER zuverlässig aus der gewählten Sleep-Konfiguration aufweckt, muss geprüft werden.

## Sicherheit / Funkrecht

- Keine ungeprüfte Ladeschaltung dauerhaft im Außenbereich betreiben, insbesondere nicht mit ungeschützten 18650-Zellen.
- Eine 868-MHz-Frequenz allein erlaubt keine beliebige Leistung oder Sendezeit. Antennengewinn/EIRP, Duty-Cycle und geltende Frequenznutzungsbedingungen vor Installation überprüfen.
- Für einen öffentlich genutzten Repeater Fernadministration absichern; keine Schlüssel oder personenbezogenen Logs veröffentlichen.

## Noch nicht behaupten

**Weder 0-€-Solaraufbau noch ganzjähriger unbeaufsichtigter Betrieb sind bisher nachgewiesen.** Das Projektziel ist eine kostengünstige Konstruktion mit möglichst vielen bereits vorhandenen Bauteilen, nicht ein fertiges und zertifiziertes Outdoor-Gerät.
