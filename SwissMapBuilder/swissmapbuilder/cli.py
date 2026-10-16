import argparse
import json
import sys
from .core import LAYERS, init, load, plan, register, status, write_json

def main(argv=None):
    parser = argparse.ArgumentParser(description="SwissMapBuilder – Geodaten-Grundlage für BeamNG")
    commands = parser.add_subparsers(dest="command", required=True)
    start = commands.add_parser("init", help="Gebiet als isoliertes Projekt anlegen")
    start.add_argument("directory")
    start.add_argument("--name", required=True)
    start.add_argument("--bbox", nargs=4, type=float, required=True, metavar=("E_MIN", "N_MIN", "E_MAX", "N_MAX"))
    for command in ("plan", "status"):
        sub = commands.add_parser(command)
        sub.add_argument("directory")
    add = commands.add_parser("register", help="Lokale Quelldatei mit Herkunft registrieren")
    add.add_argument("directory")
    add.add_argument("--layer", choices=LAYERS, required=True)
    add.add_argument("--file", required=True)
    add.add_argument("--source", required=True)
    add.add_argument("--license", required=True)
    add.add_argument("--date", required=True, help="Aufnahmedatum YYYY-MM-DD; kein erfundenes Datum verwenden")
    add.add_argument("--confidence", choices=["measured", "detected", "inferred"], default="measured")
    ui = commands.add_parser("ui", help="Lokale Kartenoberfläche öffnen")
    ui.add_argument("--directory", default="projects")
    find = commands.add_parser("discover", help="swisstopo-Kacheln suchen; noch kein Download")
    find.add_argument("directory")
    find.add_argument("--layer", choices=["terrain", "orthophoto"], default="terrain")
    find.add_argument("--resolution", type=float)
    down = commands.add_parser("download", help="Gefundene Kacheln herunterladen; Cache nutzen")
    down.add_argument("directory")
    down.add_argument("--layer", choices=["terrain", "orthophoto"], default="terrain")
    down.add_argument("--max-files", type=int, default=100)
    args = parser.parse_args(argv)
    try:
        if args.command == "ui":
            from .ui import serve
            serve(args.directory)
            return 0
        elif args.command == "discover":
            from .acquire import discover
            result = discover(args.directory, args.layer, args.resolution if args.resolution is not None else (2.0 if args.layer == "terrain" else 0.1))
        elif args.command == "download":
            from .acquire import download
            result = download(args.directory, args.layer, args.max_files)
        elif args.command == "init":
            result = init(args.directory, args.name, args.bbox)
        elif args.command == "plan":
            result = plan(load(args.directory))
            write_json(f"{args.directory}/reports/plan.json", result)
        elif args.command == "status":
            result = status(args.directory)
        else:
            result = register(args.directory, args.layer, args.file, args.source, args.license, args.date, args.confidence)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except (ValueError, OSError, KeyError, ImportError) as error:
        print(f"Fehler: {error}", file=sys.stderr)
        return 1
