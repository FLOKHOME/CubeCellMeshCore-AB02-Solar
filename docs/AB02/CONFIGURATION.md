# Konfiguration, Regionen und EEPROM – HTCC-AB02

**Stand: 22.10.2026 · Firmwarezweig `feature/oled-diagnostics` (`bf9c48b`)**

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

In `src/mesh/RegionMap.h`:

```cpp
#define REGION_MAX_ENTRIES 5
#define REGION_SAVE_NAME_LEN 12
#define REGION_EEPROM_OFFSET 512
```

In `src/main.h`: `EEPROM_SIZE 640`.

- Speicherung ab Offset 512: Magic (2 B), Anzahl (1 B), Wildcard-Flags (1 B), **5 × (Name 12 B + Flags 1 B)**.
- Größe: `4 + 5 * 13 = 69 B`; letzter verwendeter Byteindex 580.
- Namen werden im EEPROM auf maximal **11 ASCII-Bytes plus `\0`** begrenzt. Längere Namen können beim Laden verändert werden und dadurch andere Region-Keys ergeben.
- Der Schlüssel einer Region wird **aus dem Namen** abgeleitet; er wird beim Laden neu berechnet.
- Ein Wechsel der EEPROM-Struktur und spätere Änderungen am Format benötigen gesonderte Migrationstests.

## Automatische Provisionierung

Das lokal getestete `provision_ab02_v4.py` sendete fünf `region put NAME`-Befehle. **Vor der Regionskapazitätsänderung** wurde die fünfte Region mit `ERR` abgewiesen; die neue Firmware akzeptiert sie. Das Profil `harsum01.json` enthält ggf. Parent-Angaben, die v4 absichtlich **nicht** verwendet.

Die Provisionierungsskripte und Profile sind im Branch `bf9c48b` **noch nicht automatisch enthalten**. Vor einer öffentlichen Veröffentlichung keine privaten Schlüssel, Passwörter oder exakten Standortkoordinaten übernehmen. Der manuelle CLI-Weg oben ist der auf Hardware bestätigte Referenzablauf.
