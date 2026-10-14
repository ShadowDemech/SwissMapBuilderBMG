# Entwicklungsplan

1. **Grundlage (dieser Stand):** Gebiet, Ursprung, Kacheln, Datenherkunft, isolierte Projekte und Tests.
2. **Karte und Provider:** einfach verschieb-/skalierbares Rechteck; Auswahl speichern; swisstopo-
   Download und BL-Zugänge anhand realer Metadaten implementieren; Wiederholungen und lokale Cache-Nutzung.
3. **Erster echter Export:** beliebiges kleines Gebiet mit Terrain und Gebäudekörpern erzeugen,
   in BeamNG laden und Maßstab/Höhen überprüfen. Kein festes Ortsprojekt.
4. **Befahrbare Infrastruktur:** Straßenflächen und Kreuzungen, getrennte Höhenebenen, KI-Netz,
   Brücken, Tunnel und Unterführungen. Testgebiet gezielt nach vorhandenen Bauwerken wählen.
5. **Details:** Luftbild-Markierungen, Geh-/Velowege, Gleise, Haltestellen, Schilder, Vegetation,
   Fassaden und Gärten. Unsichere Details kennzeichnen.
6. **Betrieb:** lokale Windows-Startoberfläche, fortsetzbare Builds, begrenzte Speicherlast,
   automatische Geometrieprüfungen und dokumentierte Fahrtests.

Abnahme eines ersten spielbaren Builds: keine Terrain-Durchdringungen auf Teststraßen,
verbundene Kreuzungen ohne Höhenstufen, korrekte Brücken-/Tunnel-Durchfahrt, keine Vegetation
im Fahrraum und ein ladbarer Mod mit bekannten verbleibenden Fehlern. Dateiprüfungen ersetzen
keinen Fahrtest. Bauwerke und Tiefgaragen dürfen bei unzureichenden Daten als unvollständig gemeldet werden.
