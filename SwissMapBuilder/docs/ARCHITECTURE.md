# Architektur

Projektkonfiguration → Datenbeschaffung → Normalisierung → Generierung → Qualitätsprüfung → BeamNG-Export.

Jedes Projekt besitzt eigene inputs/, cache/, work/, reports/ und export/-Ordner. Keine globalen
Tessiner Referenzrouten, gepinnten OSM-Ausschnitte oder fremden Markierungsdaten als Standard.

## Verträge für kommende Module

- Provider liefert Quelldateien mit Quelle, Lizenz, Aufnahmezeitpunkt, CRS und vertikalem Bezug.
- Normalisierung prüft Abdeckung, NoData, Einheiten und Höhenbezug. EPSG:2056 allein beschreibt
  nicht den Höhenbezug. Rasterauflösung wird getrennt von Messgenauigkeit dokumentiert.
- Objekte tragen stabile IDs, Herkunft (`measured`, `detected`, `inferred`) und ggf. Unsicherheit.
- Cache-Schlüssel umfassen Gebiet, Quelle/Version, Parameter und Generatorversion.
- Stufen schreiben erst nach erfolgreichem Abschluss einen atomaren Abschlussdatensatz.
- Straßen verbinden sich nur auf gleicher Verkehrsebene. Tunnel und Unterführungen dürfen nicht
  wie normale Terrainstraßen behandelt werden. Höhenfelder allein bilden keine Hohlräume ab.
- Details aus Regeln bleiben als geschätzt erkennbar; ein fehlendes Schildinventar wird nicht
  als vollständig originalgetreuer Schilderbestand ausgegeben.
- Export erzeugt zunächst einen separaten Levelordner. Eine bestehende installierte Map wird
  nicht automatisch überschrieben.

## Zielobjekte

Straßenflächen, Geh-/Velowege, Markierungen, Schilder, Haltestellen, Gleise, Brücken, Tunnel,
Unter-/Überführungen, Tiefgaragenrampen, Gebäudekörper, Fassaden, Gärten, Bäume und Hecken.
Für jedes Objekt müssen Geometrie, Material, Kollision, Detailstufen und Datenherkunft definiert werden.
