# SwissMapBuilder

Grundlage für einen universellen, lokal ausführbaren Schweizer Geodaten-zu-BeamNG-Generator.
Ein Gebiet soll später auf einer Karte auswählbar sein. Amtliche Schweizer Daten bilden die
Basis; genauere kantonale Quellen ergänzen sie, beginnend mit Basel-Landschaft.

## Stand 0.1.0: funktionsfähige Projektvorbereitung

Implementiert: validierte rechteckige LV95-Gebiete, automatisch berechneter lokaler Ursprung,
Kachelplanung, getrennte Projektordner, Datenquellen-Prioritäten, Quelldatei-Registrierung mit
SHA-256, Herkunft und Aufnahmezeitpunkt sowie Erkennung geänderter oder fehlender Eingaben.

**Noch nicht implementiert:** Kartenoberfläche, Downloads, GIS-Konvertierung, Straßen- und
Gebäudegenerierung, Tunnel, BeamNG-Export und Wiederaufnahme eines Map-Builds. Der Plan kennzeichnet
diese Schritte ausdrücklich als `not_implemented`. Dieses Paket erstellt noch keine spielbare Map.

## Auf Windows starten

Python 3.10 oder neuer installieren. Den Paketordner entpacken, dort ein Terminal öffnen.
Für die folgenden Befehle sind keine Zusatzbibliotheken nötig. Falls `python` nicht erkannt wird,
stattdessen `py` verwenden.

```powershell
python -m swissmapbuilder --help
python -m swissmapbuilder init projects/demo --name demo --bbox 2620000 1250000 2621000 1251000
python -m swissmapbuilder plan projects/demo
python -m swissmapbuilder status projects/demo
```

Das Beispiel ist ein frei austauschbares 1-km²-Testrechteck, kein festgelegtes Zielgebiet.
`bbox` ist: Ost-Minimum, Nord-Minimum, Ost-Maximum, Nord-Maximum in **LV95-Metern**, keine
Breiten-/Längengrade. Die spätere Kartenoberfläche übernimmt diese Eingabe automatisch.
Die Einstellungen stehen in `projects/demo/project.json`; der Plan in `reports/plan.json`.
Nach Änderungen `plan` erneut ausführen. Bereits registrierte Eingaben werden bei veränderter
Projektkonfiguration als veraltet gemeldet.

Eine vorhandene Geodatendatei registrieren:

```powershell
python -m swissmapbuilder register projects/demo --layer terrain --file "C:\Geodaten\terrain.tif" --source "Name oder URL der tatsächlichen Datenquelle" --license "Tatsächliche Nutzungsbedingungen" --date 2024-01-01
```

Datum und Lizenz sind Platzhalter im Beispiel und müssen durch die echten Metadaten ersetzt werden.
Die Datei bleibt am ursprünglichen Ort. Registrierung prüft Integrität, **nicht** Georeferenzierung,
Abdeckung, Genauigkeit oder Eignung. Das kommt im Normalisierungsschritt.

## Entwicklung

```powershell
python -m unittest discover -s tests -v
```

Tests laufen zusätzlich über GitHub Actions unter Windows und Linux. Große Geodaten, Cache und
Builds bleiben lokal und werden nicht in Git aufgenommen. Details: [Architektur](docs/ARCHITECTURE.md),
[Entwicklungsplan](docs/ROADMAP.md), [Datenquellen](docs/DATA_SOURCES.md).

## Bezug zu magliasinaNG

Das untersuchte Projekt [Malcantone / magliasinaNG von wintrymichi](https://github.com/wintrymichi/magliasinaNG)
und der [verlinkte Fork](https://github.com/ShadowDemech/magliasinaNG) dienen als technische Referenz.
Dieser erste Stand enthält keinen übernommenen Code, keine Modelle und keine Original-Geodaten daraus.
Vor späterer Übernahme müssen Herkunft und CC-BY-NC-4.0-Bedingungen berücksichtigt werden.
Die Lizenzen zukünftiger Geodaten und BeamNG-Assets werden separat dokumentiert.

## Neues GitHub-Repository

Repositoryname: `SwissMapBuilder`. Empfehlung: zunächst **privat**.
Auf GitHub ein leeres Repository ohne automatisch erzeugte README anlegen.
Danach kann dieses Paket als erster Commit hochgeladen werden. GitHub-Zugangsdaten gehören nie
in Konfigurationsdateien oder in dieses Repository.
