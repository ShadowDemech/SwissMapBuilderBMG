# Von 0.2.0 auf 0.3.0 wechseln

Die Version ist eine Erweiterung des universellen Generators. Es ist kein fest eingebautes Ortsprojekt.
Jeder gespeicherte Ausschnitt wird mit demselben Code verarbeitet.

## Auf deinem PC

1. Kartenserver und laufende Python-Verarbeitung schließen.
2. Sicherheitskopie des bisherigen Ordners `SwissMapBuilder` erstellen.
3. ZIP in den bisherigen übergeordneten Ordner entpacken, sodass der enthaltene Ordner
   `SwissMapBuilder` mit deinem vorhandenen Ordner zusammengeführt wird. Bei Programmdateien
   „Dateien ersetzen“ wählen. **Den bestehenden Ordner nicht vorher löschen.**
4. Der bestehende Unterordner `projects` bleibt erhalten. Das Paket enthält weder Projekte noch Geodaten.
5. Im aktualisierten Ordner `SwissMapBuilder` die Datei `Gelaende_vorbereiten.bat` doppelklicken.
   Sie aktualisiert die Python-Abhängigkeiten, findet gespeicherte Projekte und lässt dich bei mehreren
   Projekten eine Nummer wählen. Vorhandene Daten werden geprüft und weiterverwendet.
6. Die ausgegebenen Pfade zum GeoTIFF und Vorschaubild stehen unter `work/normalized/...` im Projekt.
   Das Vorschaubild kann im Explorer geöffnet werden. Es zeigt Höhen als Graustufen, kein Luftbild.

Für Brunos bestehenden Downloadordner ist das ZIP-Ziel:
`C:\Users\bruno\Downloads\SwissMapBuilder_0.2.0`
Der Ordnername darf trotz aktualisiertem Code zunächst so bleiben.

Bei Erfolg erscheint „Gelände erfolgreich vorbereitet“. Bei einem Fehler bitte den vollständigen
Fehlertext kopieren. Die Verarbeitung verändert keine BeamNG-Installation.

## Auf GitHub

Das Repository wurde vor der Erweiterung gelesen und entspricht dem bekannten Stand 0.2.0.
GitHub-Schreibzugriff des Assistenten ist weiterhin mit 403 blockiert; nichts wurde dort geändert.

1. Das ZIP zusätzlich in einen frischen Ordner entpacken.
2. Im Repository **Add file → Upload files** wählen.
3. Die oberste README.md und den frischen Ordner SwissMapBuilder hochladen.
   Nicht die lokale Arbeitskopie mit .venv oder projects hochladen.
4. Commit-Nachricht: `Version 0.3.0: universelle Geländenormalisierung und automatischer Ablauf`.

Zusätzlich enthält das ZIP `.gitignore` und `.github/workflows/tests.yml`.
Der Explorer zeigt sie eventuell nicht an. Bei Bedarf auf GitHub über **Add file → Create new file**
mit genau diesen Pfaden anlegen und den Text der enthaltenen Dateien einfügen.
Der Workflow muss im Repository-Hauptordner unter `.github/workflows/` liegen, nicht unter SwissMapBuilder.

## Ergebnis

- `terrain_lv95.tif`: nordorientiertes Float32-Gelände in LV95, Höhen in Metern LN02.
- `terrain_preview.png`: Höhenübersicht bis 1024 Pixel Kantenlänge.
- `reports/normalize_terrain.json`: Abdeckung, Höhenbereich, Quellen und Ausgabedateien.

Das Raster wird auf volle Zellen nach außen gerundet; der zusätzliche Rand bleibt kleiner als eine
Rasterzelle pro Seite. Löcher werden nicht künstlich aufgefüllt. Bei fehlenden Rasterwerten wird
kein erfolgreiches Gelände veröffentlicht. Ein Diagnosbericht nennt die Anzahl der fehlenden Zellen.
Noch kein spielbarer BeamNG-Level; das Terrain muss im nächsten Entwicklungsschritt in das
BeamNG-Format überführt werden. Gebäude, Straßen, Bauwerke und Details folgen danach.
