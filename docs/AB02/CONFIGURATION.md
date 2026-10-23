# Konfiguration, Regionen und EEPROM – HTCC-AB02

**Stand: 23.10.2026 · Release `v0.8.2` (`main`, Firmwarekennung `0.8.2`)**

## Zentrale Konfigurationsdatei `config/repeater.json`

**Ablauf:** 1. Repository klonen · 2. `config/repeater.json` bearbeiten · 3. Firmware bauen · 4. CubeCell flashen · 5. Beim ersten Start werden die Einstellungen automatisch übernommen und dauerhaft im EEPROM gespeichert. Eine Sitzung an der seriellen Konsole ist danach nicht mehr nötig.

Die Datei wird **beim Kompilieren** von `tools/gen_user_config.py` gelesen, validiert und in `src/generated/UserConfigData.h` sowie `.cpp` übersetzt (eingebunden über `extra_scripts` in `platformio.ini`). Es gibt bewusst **keinen JSON-Parser in der Firmware**: das Image ist zu ~98 % gefüllt, ein Parser plus JSON-Text würde nicht mehr hineinpassen.

| Feld | Bereich / Wirkung |
| --- | --- |
| `name` | max. 15 Zeichen, Gerätename (Identitätsblock) |
| `location.latitude` / `.longitude` | Dezimalgrad; `0.0`/`0.0` = Standort nicht setzen bzw. beibehalten |
| `radio.frequency_mhz` | 400–960 MHz, Kompilierzeit-Konstante `MC_FREQUENCY` |
| `radio.bandwidth_khz` | nur SX1262-Stützwerte (7.8 … 500 kHz), `MC_BANDWIDTH` |
| `radio.spreading_factor` | 5–12, `MC_SPREADING` |
| `radio.coding_rate` | 5–8 (4/5 … 4/8), `MC_CODING_RATE` |
| `radio.tx_power_dbm` | −9…22 dBm, `MC_TX_POWER` |
| `advertising.local_interval_minutes` | 1–240; ADVERT-Intervall, Vorgabe **120** (2 h) |
| `advertising.flood_interval_hours` | `0` = aus, sonst 3–48 (getrenntes Flood-ADVERT), Vorgabe **6** |
| `regions.allow` | 1–5 benannte Regionen (max. 11 Zeichen) plus optional `*`; ersetzt die gespeicherte Liste vollständig |
| `regions.deny_flood` | Namen aus `allow`, die Flood verweigern (`D`); `*` nur statt, nicht zusätzlich zu `allow` |
| `regions.default` | Heimatregion des Repeaters (max. 11 Zeichen, muss in `allow` stehen); scope für **eigene ADVERTs**, leer = ungescoped |
| `network.max_flood_hops` | 1–15 |
| `network.loop_detect` | 0=aus, 1=minimal, 2=moderat, 3=strikt |
| `network.auto_add_max_hops` | 0–64, `0` = kein Limit |
| `power.power_saving` | 0=Performance, 1=balanced, 2=sparsam |
| `power.deep_sleep` / `.rx_boost` | `true`/`false` |
| `security.admin_password` / `guest_password` | max. 15 Zeichen; **leer = vorhandenes Passwort im EEPROM bleibt erhalten** |

Ungültige Werte brechen den Build mit Klartextmeldung ab, z. B.:

```text
[userconfig] CHECK FAILED: radio.spreading_factor: must be between 5 and 12, got 13
[userconfig] CHECK FAILED: regions.allow: 6 named regions, at most 5 are supported by this firmware
```

**Übernahme:** Ein Fingerabdruck (FNV-1a über die normalisierte JSON) wird fest in die Firmware eingebaut und im EEPROM als `NodeConfig.configHash` gespeichert. Stimmen beide überein, passiert beim Start **nichts** – manuell über die Konsole geänderte Werte bleiben also erhalten. Erst nach einer Änderung an der Datei (und erneutem Flashen) werden die Werte einmalig geschrieben.

```text
config            -> Cfg:built-in fp:B926A193 stored:applied
config apply      -> erzwingt erneutes Anwenden (überschreibt manuelle Änderungen)
```

Nach dem Update auf diese Firmware zeigt `config` einmalig `stored:stale`, bis `config apply` gelaufen ist oder der erste Start das Anwenden erledigt hat. Radio-Parameter sind Kompilierzeit-Konstanten und daher nicht per `radio`/`tempradio` veränderbar; alles andere lässt sich weiterhin zur Laufzeit überschreiben.

**Ohne `config/repeater.json`** (oder ohne Python) baut die Firmware unverändert mit den eingebauten Vorgaben; der Generator schreibt dann nur einen Stub.

## Regionen: Allow-Liste und Heimatregion

Zwei Begriffe, die leicht verwechselt werden:

- **`regions.allow`** ist die Weiterleitungs-Policy. Sie bestimmt, welche regional gescopten Flood-Pakete der Repeater annimmt und weiterleitet. Der Wildcard-Eintrag `*` schaltet die Regionenfilterung praktisch ab: Pakete ohne Treffer in der Allow-Liste werden trotzdem gefloodet. `deny_flood` nimmt einzelne Namen wieder aus.
- **`regions.default`** ist die **Heimatregion** und betrifft nur Pakete, die der Repeater **selbst** erzeugt (v. a. ADVERTs). Der Repeater berechnet den 4-Byte-Transport-Code über das fertige Paket und stellt den Header auf den Transport-Routentyp um; beim Serialisieren steht der Code dann vor `pathLen`. Ohne diese Angabe werden eigene ADVERTs ungescoped gefloodet. Der Name muss in `allow` stehen, sonst bricht der Build mit Klartextmeldung ab.

Für ein Solar-Gerät im Feld ist die übliche Kombination:

```json
"regions": { "allow": ["*", "de-mitte"], "deny_flood": [], "default": "de-mitte" }
```

Damit wird fremder Verkehr aus allen Regionen weitergeleitet, während eigene ADVERTs sauber in `de-mitte` laufen. `region` auf der Konsole zeigt beides getrennt (`*:A` / `de-mitte:A`).

## Vorgaben für den Solarbetrieb (ab `v0.8.2`)

Die ausgelieferten Vorgaben sind auf Dauerbetrieb mit kleiner Zelle ausgelegt:

| Feld | Wert | Begründung |
| --- | --- | --- |
| `power.deep_sleep` | `true` | Repeater schläft zwischen den Empfangsfenstern; die Konsole ist dann stumm, das ist normal |
| `power.power_saving` | `1` | balanced: Empfangsfenster groß genug für Mesh-Verkehr, ohne dauerhaft wach zu sein |
| `power.rx_boost` | `false` | spart Strom; nur bei sehr schwacher Gegenstelle sinnvoll |
| `advertising.local_interval_minutes` | `120` | ein ADVERT alle 2 h genügt, um in der App sichtbar zu bleiben |
| `advertising.flood_interval_hours` | `6` | zusätzliches Flood-ADVERT alle 6 h für die Netzweite |
| `radio.tx_power_dbm` | `21` | Hardware-Maximum; bei schlechter Abdeckung bewusst ausgereizt |

Wer die Konsole bei aktivem Deep Sleep braucht, weckt das Gerät über den USER-Taster (boot-safe window) oder setzt vorübergehend `power.deep_sleep` auf `false`.

## ADVERT-Intervall

Reihenfolge der Wirksamkeit: **EEPROM-Wert** (aus `loadConfig()`) → **kompilierte Konfiguration** (`advertising.local_interval_minutes`) → **eingebauter Vorgabewert** 5 min. Das Intervall wird beim Start **nicht mehr** überschrieben; die Startmeldung nennt den tatsächlich wirksamen Wert:

```text
[I] ADV: on every 7200s
```

```text
advert interval          -> Int:120m next:61s      (Ist-Wert + Restzeit)
set advert.interval 120  -> 1-255 Minuten, wird gespeichert
advert interval 7200     -> 60-15300 Sekunden, wird gespeichert
```

Gespeichert wird das Intervall in `NodeConfig.advertIntervalMin` (**1 Byte**). Deshalb liegt die dauerhaft speicherbare Obergrenze bei **255 Minuten** (4,25 h); größere Werte werden von den Befehlen abgelehnt (`E:1-255`), statt nach dem nächsten Neustart still gekürzt zu werden. `speichern` erfolgt über `saveConfig()` – jeder spätere `save`-Vorgang schreibt den aktuell wirksamen Wert zurück.

**Hinweis für die Inbetriebnahme:** Nach dem Flashen dieser Firmware einmal `advert interval` prüfen. Vorher galt nach jedem RESET wieder 5 min, und der erste Admin-Login schrieb diesen Wert zusätzlich ins EEPROM.

## Serielle Konsole

```cmd
py -m platformio device monitor --port COM3 --baud 115200 --echo
```

`COM3` ist ein Beispiel vom Testrechner. Den tatsächlichen COM-Port über `py -m platformio device list` ermitteln. Monitor vor Upload beenden.

## Gerätename

Der getestete Name lautet `DE-NI-HARSUM01`. Er war nach dem Neustart unverändert:

```text
get name
Name:DE-NI-HARSUM01
```

Das **Gerätenamensfeld** ist getrennt von den **Regionsnamen** zu betrachten. Konfigurations- und Identitätsdaten müssen beim Flashen und nach einem RESET überprüft werden.

## Regionen (flaches Modell)

Die CubeCell-Firmware unterstützt **fünf benannte Einträge plus eine separat verwaltete Wildcard**. Für die Testkonfiguration:

```text
region
region put de
region put de-nord
region put de-mitte
region put de-west
region put de-ni
region
```

Erwartete, auf Hardware bestätigte Ausgabe:

```text
*:A
de:A
de-nord:A
de-mitte:A
de-west:A
de-ni:A
```

`A` = Flood erlaubt; `D` = Flood verweigert. Frisch angelegte Einträge waren im Test direkt `A` – `region allowf NAME` war nicht nötig.

**Keine Elternhierarchie:** Die ursprüngliche Provisionierung hat `region put de-nord de` gesendet und ist gescheitert. Der bestätigte Befehl lautet `region put de-nord`. Elternfelder (`parent`) aus JSON-Profilen werden von der CubeCell-Regionsverwaltung **nicht unterstützt**. Die Namen bilden nur textuell eine Hierarchie ab.

## Dauerhaft speichern

```text
region save
```

Dieser Befehl wurde nach dem Persistenz-Fix erfolgreich ausgeführt. Danach: **RESET** drücken und erneut `region` prüfen. Sämtliche sechs Einträge blieben auf dem Testgerät erhalten.

**Vorsicht:** In einem Zwischenstand wurde `region save` als `Unknown` erkannt; der generische Befehl `save` speicherte damals nur die allgemeine Konfiguration. Das wurde im Entwicklungsbranch korrigiert. Für die Regionsliste explizit `region save` verwenden.

## Speicherlayout und Grenzen

Die Layout-Konstanten stehen seit dem Layout-Fix **einmalig** in `src/core/StorageLayout.h`; `main.h`, `Config.h`, `Identity.h`, `Mailbox.h` und `RegionMap.h` binden diese Datei ein. Ein `#error` bricht den Build ab, sobald ein Block aus dem EEPROM-Fenster läuft oder zwei Blöcke sich überlappen. `static_assert` sichert die Größen der gespeicherten Strukturen (112/116 B Config, 132 B Identität, 52 B Statistik, 8 + 2 × 84 B Mailbox).

| Block | Offset | Größe | Ende |
| --- | ---: | ---: | ---: |
| `NodeConfig` (inkl. `configHash`) | 0 | 116 B | 115 |
| `NodeIdentity` | 128 | 132 B | 259 |
| `PersistentStats` | 280 | 52 B | 331 |
| Mailbox (Header + 2 Slots) | 336 | 176 B | 511 |
| Regionen | 512 | 69 B | 580 |

`EEPROM_SIZE` ist **640**; die Emulation nutzt drei Nutzer-Flash-Zeilen (max. 768 B). Nicht über `EEPROM.begin()` abgedeckte Schreibzugriffe werden von der Heltec-Emulation **still verworfen**, `commit()` meldet trotzdem Erfolg (`libraries/EEPROM/EEPROM.cpp`: `if (address >= _size) return;`). Genau deshalb sind die Prüfungen in `StorageLayout.h` notwendig.

- Regionen ab Offset 512: Magic (2 B), Anzahl (1 B), Wildcard-Flags (1 B), **5 × (Name 12 B + Flags 1 B)** = 69 B.
- Regionsnamen werden beim Anlegen auf **11 ASCII-Bytes plus `\0`** gekürzt, damit der aus dem Namen abgeleitete Transport-Key einen Neustart übersteht.
- `region save` schreibt den Block; schlägt das Speichern fehl (z. B. Layout passt nicht ins EEPROM-Fenster), meldet die Firmware jetzt `ERR` statt still Erfolg.
- Die Statistik wird alle **30 Minuten** gespeichert (jeder Commit schreibt das gesamte EEPROM-Fenster und kostet Flash-Zyklen).

## Automatische Provisionierung

Das lokal getestete `provision_ab02_v4.py` sendete fünf `region put NAME`-Befehle. **Vor der Regionskapazitätsänderung** wurde die fünfte Region mit `ERR` abgewiesen; die neue Firmware akzeptiert sie. Das Profil `harsum01.json` enthält ggf. Parent-Angaben, die v4 absichtlich **nicht** verwendet.

Die Provisionierungsskripte und Profile sind im Branch `bf9c48b` **noch nicht automatisch enthalten**. Vor einer öffentlichen Veröffentlichung keine privaten Schlüssel, Passwörter oder exakten Standortkoordinaten übernehmen. Der manuelle CLI-Weg oben ist der auf Hardware bestätigte Referenzablauf.
