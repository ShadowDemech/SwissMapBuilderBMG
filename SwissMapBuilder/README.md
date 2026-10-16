# SwissMapBuilder 0.2.0

Universeller lokaler Schweizer Geodaten-zu-BeamNG-Generator in Entwicklung.
Keine feste Ortskarte, keine Tessiner Referenzrouten. Fahrtests führt Bruno manuell durch.

## Was jetzt funktioniert

- Gebiet auf einer Karte durch zwei Klicks wählen; Eckpunkte anschließend verschieben.
- LV95-Projekt mit eigenem Ursprung, Kachelplan und getrennten Datenordnern speichern.
- swissALTI3D-Geländekacheln in 2 m oder 0,5 m suchen und herunterladen.
- SWISSIMAGE-10-cm-Dateien suchen und herunterladen (Adapter vorhanden, noch kein Live-Download geprüft).
- STAC-Seiten durchlaufen; pro räumlicher Kachel den neuesten passenden Aufnahmezeitpunkt wählen.
- Originalmetadaten, Lizenzangabe, Datum, Höhenbezug und Herkunft aufbewahren.
- Prüfsummen kontrollieren; vollständige Dateien im Cache weiterverwenden; beschädigte erneut laden.
- Wiederaufnahme zwischen vollständigen Dateien. Abgebrochene einzelne Dateien werden erneut geladen.

Noch keine spielbare BeamNG-Map. GIS-Zuschnitt, Gelände-/Straßengenerierung, Gebäude, Brücken,
Tunnel, Markierungen, Vegetation und Export sind weitere Entwicklungsstufen.
Rasterauflösung sagt nicht die Messgenauigkeit aus. Download-Prüfsummen ersetzen keine GIS-Abdeckungsprüfung.

## Windows: erster Start

Python 3.10 oder neuer installieren. `Start_MapBuilder.bat` im Ordner `SwissMapBuilder` doppelklicken.
Es wird eine lokale Python-Umgebung eingerichtet und die Karte im Browser geöffnet.
Internet ist für Installation, Kartenansicht und Geodaten nötig.

1. Zur gewünschten Stelle zoomen.
2. Zwei gegenüberliegende Ecken anklicken; Eckpunkte bei Bedarf ziehen.
3. Projektnamen eingeben und **Gebiet speichern** drücken. Mit etwa 1 km² beginnen.
4. Kartenserver mit Strg+C beenden. Im Paketordner ein Terminal öffnen:

```powershell
.venv\Scripts\python -m swissmapbuilder discover projects/meine_karte
.venv\Scripts\python -m swissmapbuilder download projects/meine_karte
.venv\Scripts\python -m swissmapbuilder status projects/meine_karte
```

Für feinere Geländedaten `discover ... --resolution 0.5` verwenden.
Für Luftbilder beide Befehle mit `--layer orthophoto` ausführen. 10-cm-Luftbilder können sehr groß sein.
`discover` lädt nur Metadaten; `download` lädt die vollständigen Kacheln. Standardlimit: 100 Dateien.
Der Cache ist pro Projekt getrennt; erneutes `download` kontrolliert vorhandene Dateien.
Eine Neu-Auswahl mit bestehendem Projektnamen überschreibt das Projekt nicht.

## Terminal und Entwicklung

```powershell
py -3 -m venv .venv
.venv\Scripts\python -m pip install -e .
.venv\Scripts\python -m swissmapbuilder ui
.venv\Scripts\python -m unittest discover -s tests -v
```

Alternativ funktioniert die LV95-Eingabe weiterhin:
`python -m swissmapbuilder init projects/demo --name demo --bbox 2620000 1250000 2621000 1251000`.

GitHub-Actions-Konfiguration ist im Paket enthalten, aber wegen blockiertem GitHub-Schreibzugriff
noch nicht auf GitHub installiert oder dort ausgeführt. Lokale Prüfergebnisse: `docs/VALIDATION.md`.

## Nächste Stufen

1. Daten normalisieren: Zuschnitt, Abdeckung, NoData und Höhenbezug prüfen; BL-Provider ergänzen.
2. Ersten BeamNG-Export mit Terrain und Gebäudekörpern erzeugen.
3. Straßen und Kreuzungen, Fuß-/Velowege sowie getrennte Verkehrsebenen bauen.
4. Brücken, Unterführungen und Tunnel mit Kollision und Durchfahrt ergänzen.
5. Markierungen, Schilder, Haltestellen, Gleise, Vegetation, Fassaden und Gärten ergänzen.
6. Lokale fortsetzbare Builds, technische Qualitätsprüfungen und manuelle Fahrtests.

Das Quellenprojekt [magliasinaNG](https://github.com/wintrymichi/magliasinaNG) dient als Referenz.
Dieser Stand übernimmt keinen Quellcode, keine Modelle oder Originaldaten daraus.
Daten behalten ihre eigenen Nutzungsbedingungen. Provider-Metadaten stehen in `reports/acquire_*.json`.
STAC-Dokumentation: https://docs.geo.admin.ch/download-data/stac-api/overview.html

Kartenansicht: © OpenStreetMap contributors. Daten: © swisstopo.
