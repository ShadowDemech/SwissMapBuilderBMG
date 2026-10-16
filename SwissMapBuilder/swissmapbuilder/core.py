"""Validated LV95 projects, data requirements and provenance; no game writes."""
import hashlib
import json
import math
import re
from pathlib import Path

LAYERS = {
    "terrain": ["baselland.dtm", "swisstopo.swissalti3d"],
    "surface": ["baselland.lidar", "swisstopo.swisssurface3d"],
    "orthophoto": ["baselland.orthophoto", "swisstopo.swissimage"],
    "buildings": ["swisstopo.swissbuildings3d", "baselland.buildings"],
    "survey": ["baselland.official_survey"],
    "network": ["swisstopo.swisstlm3d"],
    "osm": ["openstreetmap"],
}
STAGES = ["acquire", "normalize", "terrain", "roads", "structures", "buildings",
          "vegetation", "details", "validate", "export_beamng"]

def validate(config):
    if config.get("schema_version") != 1:
        raise ValueError("Unbekannte schema_version")
    if not re.fullmatch(r"[a-z][a-z0-9_-]{0,63}", config.get("name", "")):
        raise ValueError("Name: Kleinbuchstaben, Zahlen, _ oder -; erster Buchstabe a-z")
    if config.get("crs") != "EPSG:2056":
        raise ValueError("Dieser Stand unterstützt EPSG:2056 (LV95)")
    bbox = config.get("bbox")
    if not isinstance(bbox, list) or len(bbox) != 4 or any(
        isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in bbox
    ):
        raise ValueError("bbox muss vier endliche Zahlen enthalten")
    e0, n0, e1, n1 = bbox
    if not (e0 < e1 and n0 < n1):
        raise ValueError("bbox: E_min, N_min, E_max, N_max; Minimum kleiner Maximum")
    if not (2400000 <= e0 < e1 <= 2900000 and 1000000 <= n0 < n1 <= 1400000):
        raise ValueError("bbox liegt außerhalb des unterstützten Schweizer LV95-Bereichs")
    size = config.get("tile_size_m", 1000)
    if isinstance(size, bool) or not isinstance(size, int) or size <= 0:
        raise ValueError("tile_size_m muss eine positive ganze Zahl sein")
    if math.ceil((e1-e0)/size + 1) * math.ceil((n1-n0)/size + 1) > 100000:
        raise ValueError("Zu viele Kacheln; Gebiet verkleinern oder tile_size_m erhöhen")
    return config

def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    temporary.replace(path)

def load(root):
    return validate(json.loads((Path(root)/"project.json").read_text(encoding="utf-8")))

def fingerprint(config):
    return hashlib.sha256(json.dumps(config, sort_keys=True, allow_nan=False).encode()).hexdigest()

def tiles(config):
    """Half-open project bounds: no extra tile on an exact maximum boundary."""
    e0, n0, e1, n1 = config["bbox"]
    size = config.get("tile_size_m", 1000)
    return [{"id": f"{e}-{n}", "bbox": [e*size, n*size, (e+1)*size, (n+1)*size]}
            for e in range(math.floor(e0/size), math.ceil(e1/size))
            for n in range(math.floor(n0/size), math.ceil(n1/size))]

def plan(config):
    validate(config)
    e0, n0, e1, n1 = config["bbox"]
    return {"schema_version": 1, "project": config["name"], "config_sha256": fingerprint(config),
            "crs": config["crs"], "origin_lv95": [(e0+e1)/2, (n0+n1)/2],
            "area_km2": (e1-e0)*(n1-n0)/1e6, "tiles": tiles(config),
            "data_requirements": [{"layer": k, "provider_priority": v, "status": "not_acquired"}
                                  for k, v in LAYERS.items()],
            "stages": [{"name": stage, "status": "not_implemented"} for stage in STAGES],
            "note": "Dies ist ein Vorbereitungsplan, kein fertiger BeamNG-Level."}

def init(root, name, bbox):
    root = Path(root)
    config = validate({"schema_version": 1, "name": name, "crs": "EPSG:2056",
                       "bbox": list(bbox), "tile_size_m": 1000})
    if (root/"project.json").exists():
        raise ValueError("Projekt existiert bereits; project.json wird nicht überschrieben")
    for directory in ("inputs", "cache", "work", "reports", "export"):
        (root/directory).mkdir(parents=True, exist_ok=True)
    write_json(root/"project.json", config)
    write_json(root/"reports"/"plan.json", plan(config))
    return config

def register(root, layer, file, source, license_text, acquisition_date, confidence):
    """Record external files without copying huge datasets or losing provenance."""
    config = load(root)
    if layer not in LAYERS:
        raise ValueError("Unbekannte Datenebene")
    if confidence not in ("measured", "detected", "inferred"):
        raise ValueError("Ungültige Herkunftsklasse")
    from datetime import date
    date.fromisoformat(acquisition_date)
    path = Path(file).resolve(strict=True)
    if not path.is_file():
        raise ValueError("Eingabe muss eine Datei sein")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b""):
            digest.update(chunk)
    manifest_path = Path(root)/"inputs"/"manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {"files": []}
    record = {"layer": layer, "path": str(path), "size_bytes": path.stat().st_size,
              "sha256": digest.hexdigest(), "source": source, "license": license_text,
              "acquisition_date": acquisition_date, "confidence": confidence,
              "project_config_sha256": fingerprint(config), "validation": "registered_only"}
    manifest["files"] = [r for r in manifest["files"] if not (r["layer"] == layer and r["path"] == str(path))]
    manifest["files"].append(record)
    write_json(manifest_path, manifest)
    return record

def status(root):
    config = load(root)
    manifest = Path(root)/"inputs"/"manifest.json"
    records = json.loads(manifest.read_text(encoding="utf-8"))["files"] if manifest.exists() else []
    results = []
    for record in records:
        path = Path(record["path"])
        issue = "registered_only"
        if record["project_config_sha256"] != fingerprint(config):
            issue = "stale_config"
        elif not path.is_file():
            issue = "missing_file"
        else:
            digest = hashlib.sha256()
            with path.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024*1024), b""):
                    digest.update(chunk)
            if digest.hexdigest() != record["sha256"]:
                issue = "changed_file"
        results.append({"layer": record["layer"], "path": str(path), "status": issue})
    downloads = Path(root)/"inputs"/"downloads.json"
    acquired = json.loads(downloads.read_text(encoding="utf-8"))["files"] if downloads.exists() else []
    for record in acquired:
        local = Path(root)/"inputs"/record["layer"]/record["asset"]
        path = local if local.is_file() else Path(record["path"])
        issue = "checksum_only"
        if record["config_sha256"] != fingerprint(config):
            issue = "stale_config"
        elif not path.is_file():
            issue = "missing_file"
        else:
            digest = hashlib.sha256()
            with path.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024*1024), b""):
                    digest.update(chunk)
            if digest.hexdigest() != record["sha256"]:
                issue = "changed_file"
        results.append({"layer": record["layer"], "path": str(path), "status": issue})
    normalized = {"status": "not_started"}
    report_path = Path(root)/"reports"/"normalize_terrain.json"
    if report_path.exists():
        report = json.loads(report_path.read_text(encoding="utf-8"))
        stage_status = report.get("status", "unknown")
        if report.get("config_sha256") != fingerprint(config):
            stage_status = "stale_config"
        elif stage_status == "complete":
            for output in report["outputs"]:
                path = Path(root)/output["path"]
                if not path.is_file():
                    stage_status = "missing_output"
                    break
                digest = hashlib.sha256()
                with path.open("rb") as stream:
                    for chunk in iter(lambda: stream.read(1024*1024), b""):
                        digest.update(chunk)
                if digest.hexdigest() != output["sha256"]:
                    stage_status = "changed_output"
                    break
            if stage_status == "complete" and any(r["layer"] == "terrain" and r["status"] != "checksum_only" for r in results):
                stage_status = "inputs_changed"
        normalized = {"status": stage_status, "missing_cells": report.get("missing_cells"),
                      "report": str(report_path)}
    return {"project": config["name"], "inputs": results,
            "terrain_normalization": normalized, "beamng_export_available": False}
