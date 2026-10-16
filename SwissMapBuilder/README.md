# SwissMapBuilder 0.3.0

Universeller, lokal ausführbarer Schweizer Geodaten-zu-BeamNG-Generator in Entwicklung.
Freie Gebietsauswahl, keine feste Ortskarte. Entwicklung auf GitHub, Ausführung und große Daten lokal.
Fahrtests übernimmt Bruno manuell.

## Update von 0.2.0

**[Anleitung mit Erhalt vorhandener Projekte und GitHub-Upload](docs/UPDATE_0.3.0.md)**
Vorhandene Downloads müssen nicht neu geladen werden. Die neue Datei `Gelaende_vorbereiten.bat`
führt Kachelsuche, Download/Cacheprüfung und Geländeaufbereitung für das gewählte Projekt aus.

## Windows: neuer Einstieg

Python 3.10 oder neuer installieren; für die GIS-Bibliotheken empfiehlt sich 64-Bit-Python 3.12.

1. `Start_MapBuilder.bat` doppelklicken: lokale Karte öffnet sich.
2. Zwei gegenüberliegende Ecken anklicken, Eckpunkte verschieben, Projekt speichern.
3. Kartenfenster schließen und den Server im Terminal mit Strg+C beenden.
4. `Gelaende_vorbereiten.bat` doppelklicken. Bei mehreren gespeicherten Projekten Nummer wählen.
5. Ergebnis unter `projects/PROJEKT/work/normalized/` ansehen.

Internet ist für Installation, Kartenansicht und neue Downloads nötig. Vorhandene Geländedaten
können nach Installation der Abhängigkeiten mit `prepare ... --offline` verarbeitet werden.

## Stand

- Kartenwahl und Speicherung als isoliertes LV95-Projekt.
- swisstopo-STAC-Adapter: swissALTI3D in 2 m/0,5 m und SWISSIMAGE in 10 cm.
- Downloads mit Prüfsummen, Metadaten und Cache; Fortsetzen zwischen vollständigen Dateien.
- Automatischer Ablauf für jedes gespeicherte Gebiet: `prepare`.
- Blockweises Zusammenfügen und Zuschnitt von swissALTI3D; Integritäts-, CRS-, Auflösungs- und
  NoData-Prüfung; bestätigter LN02-Höhenbezug aus Quellmetadaten erforderlich.
- Nordorientiertes Gelände-GeoTIFF, Höhenvorschau und Qualitätsbericht.
- Ergebnisse werden nur bei vollständiger Rasterabdeckung veröffentlicht. Keine künstliche Lückenfüllung.
- Erneuter Lauf verwendet unveränderte, erneut geprüfte Ergebnisse.

**Noch kein BeamNG-Export.** Gebäude, Straßen, Tunnel, Brücken, Vegetation und Details fehlen.
Die Vorschau ist eine Graustufen-Höhenübersicht, kein Luftbild und keine fertige 3D-Karte.
Rasterauflösung ist nicht Messgenauigkeit. Der Verarbeitungsbericht dokumentiert den auf volle
Rasterzellen gerundeten Ausschnitt. Höhen werden nicht zwischen Bezugssystemen umgerechnet.
Gleichzeitige Verarbeitung desselben Projekts in mehreren Prozessen wird nicht unterstützt.

## Terminal

Im Ordner mit der BAT-Datei:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m swissmapbuilder ui
.\.venv\Scripts\python.exe -m swissmapbuilder prepare projects/meine_karte
```

Nur vorhandene Downloads verarbeiten:

```powershell
.\.venv\Scripts\python.exe -m swissmapbuilder prepare projects/meine_karte --offline
```

Einzelschritte bleiben verfügbar:

```powershell
.\.venv\Scripts\python.exe -m swissmapbuilder discover projects/meine_karte
.\.venv\Scripts\python.exe -m swissmapbuilder download projects/meine_karte
.\.venv\Scripts\python.exe -m swissmapbuilder normalize projects/meine_karte
.\.venv\Scripts\python.exe -m swissmapbuilder status projects/meine_karte
```

Feineres Gelände: `discover ... --resolution 0.5`. Luftbilder: `discover` und `download` jeweils mit
`--layer orthophoto`. Luftbilder werden noch nicht normalisiert und sind für diesen Schritt nicht nötig.
Standardlimit: 100 Downloaddateien, mit `--max-files` änderbar. Maximal 100 Millionen Geländerasterzellen.

## Entwicklung

```powershell
python -m pip install -e .
python -m unittest discover -s tests -v
```

[Prüfbericht](docs/VALIDATION.md) · [Entwicklungsplan](docs/ROADMAP.md) · [Architektur](docs/ARCHITECTURE.md)

GitHub soll Programmcode, Dokumentation und Tests enthalten. Projekte, Downloads und Builds
bleiben lokal; `.gitignore` schließt diese aus. GitHub Actions ist vorbereitet, wurde vom Assistenten
aber noch nicht auf GitHub ausgeführt. Manuelle Browser-Uploads können Punktdateien auslassen.

[magliasinaNG](https://github.com/wintrymichi/magliasinaNG) dient als technische Referenz.
Dieser Stand übernimmt keinen Code, Modelle oder Original-Geodaten daraus. Geodaten behalten
ihre eigenen Bedingungen; vollständige Katalogmetadaten liegen in `reports/acquire_*.json`.

Kartenansicht: © OpenStreetMap contributors. Daten: © swisstopo.
STAC: https://docs.geo.admin.ch/download-data/stac-api/overview.html
Rasterverarbeitung: https://rasterio.readthedocs.io/en/stable/topics/reproject.html
