# Prüfung 0.2.0 · 14. Oktober 2026

- 15 lokale automatische Tests: Projektvalidierung, Kachelgrenzen, Herkunft, Cache,
  Dateibeschädigung, Prüfsummenfehler, Gebietsinvalidierung, Downloadlimit,
  vertrauenswürdige URLs, Assetauswahl, STAC-Seitenzyklen und Dateinamen.
- Echter STAC-Abruf für frei gewähltes 100 × 100 m Testgebiet.
- Echte swissALTI3D-Kachel `swissalti3d_2025_2620-1250_2_2056_5728.tif`:
  1.135.790 Bytes heruntergeladen; offizielle SHA-256-Prüfsumme stimmt.
- Zweiter Downloadaufruf verwendet die Kachel aus dem Cache.
- SWISSIMAGE-Katalog live abgefragt: passende 10-cm-Kachel gefunden;
  vollständiger Luftbild-Download nicht ausgeführt.
- Lokale UI per HTTP geöffnet: Projekt-Speicherung liefert 201;
  erneutes Speichern unter gleichem Namen liefert 400 und schützt das Projekt.
- Kartenbedienung im grafischen Browser und Windows-Doppelklickstart hier noch nicht geprüft.
- GitHub-Branch-Erstellung: 403 Resource not accessible by integration.
  Keine Änderungen am Remote-Repository; Actions noch nicht ausgeführt.
- Keine BeamNG-Generierung und kein Fahrtest. Fahrtests übernimmt Bruno manuell.
