# Prüfung 0.3.0 · 16. Oktober 2026

## Automatisch und lokal geprüft

- Installation über `python -m pip install -e .` erfolgreich unter Linux / Python 3.12.
- 30 Tests bestanden: bisherige 15 sowie 15 neue Tests für Rasterverarbeitung und Ablauf.
- Benachbarte Raster werden mit exakt erwarteten Werten und korrekten Grenzen zusammengefügt.
- Nord-Süd-Orientierung, Zuschnitt auf Rastergrenzen und mehrere Ausgabeblöcke geprüft.
- NoData und fehlende Kacheln führen zu einem unvollständigen Bericht; keine künstliche Lückenfüllung.
- Beschädigte Quellen, falsches CRS, unbekannter Höhenbezug und veraltete Konfiguration abgelehnt.
- Ergebnis-Cache, beschädigte Ausgaben, verschobene Projektordner und Offline-Ablauf geprüft.
- Status erkennt fehlende normalisierte Ausgabedateien.

## Echte Daten

- Vorhandene echte swissALTI3D-Kachel: 100 × 100 m Ausschnitt zu 50 × 50 Zellen verarbeitet.
  Höhen 634,09 bis 653,70 m LN02; keine Datenlücken.
- Zusätzlicher echter 100 × 100 m Ausschnitt über vier 1-km-Kachelgrenzen:
  STAC-Suche, vier Downloads mit Prüfsummen, Zusammenfügen, Zuschnitt, GeoTIFF und Vorschau erfolgreich.
  Kacheln 2620-1250, 2620-1251, 2621-1250 und 2621-1251, Aufnahmejahr 2025.
  Ergebnis 50 × 50 Zellen; Höhen 601,87 bis 624,30 m LN02; keine Datenlücken.

## Grenzen der Prüfung

- Brunos 42 Dateien liegen nur auf seinem PC; sie wurden hier nicht verarbeitet.
- Windows-BAT-Dateien sind enthalten, aber hier nicht unter Windows ausgeführt.
- GitHub zeigt Brunos Upload des Stands 0.2.0. Branch-Erstellung für 0.3.0 erneut mit 403 abgewiesen.
  Keine Remote-Dateien geändert; GitHub Actions von hier nicht ausgeführt.
- Kein BeamNG-Export, keine Fahrtests. Diese übernimmt Bruno manuell.

## Bisheriger Stand 0.2.0

Kartenoberfläche, Projektspeicherung, STAC-Metadaten für Gelände und Luftbilder sowie echte
Geländedownloads und Cache wurden zuvor geprüft. Luftbild-Normalisierung ist nicht enthalten.
