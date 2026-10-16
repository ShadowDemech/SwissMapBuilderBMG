"""One command prepares any selected project; no game installation required."""
import json
from pathlib import Path
from .core import load, fingerprint
from .acquire import discover, download
from .normalize import normalize


def choose_project(directory=None):
    if directory:
        return Path(directory).resolve()
    projects = sorted(p.parent for p in Path('projects').glob('*/project.json'))
    if not projects:
        raise ValueError('Noch kein gespeichertes Projekt. Zuerst Start_MapBuilder.bat öffnen und ein Gebiet speichern.')
    if len(projects) == 1:
        print('Projekt: '+projects[0].name, flush=True)
        return projects[0].resolve()
    for index, project in enumerate(projects, 1):
        print(f'{index}: {project.name}')
    try:
        index = int(input('Projektnummer eingeben: '))
    except (ValueError, EOFError):
        raise ValueError('Bitte eine gültige Projektnummer eingeben') from None
    if not 1 <= index <= len(projects):
        raise ValueError('Projektnummer außerhalb der Liste')
    return projects[index-1].resolve()


def prepare(directory=None, offline=False, max_files=100):
    root = choose_project(directory)
    config = load(root)
    report = root/'reports'/'acquire_terrain.json'
    if not offline:
        prior = json.loads(report.read_text(encoding='utf-8')) if report.exists() else {}
        if prior.get('config_sha256') != fingerprint(config):
            print('1/3: swisstopo-Kacheln suchen …', flush=True)
            discover(root)
        else:
            print('1/3: vorhandenen Kachelplan verwenden.', flush=True)
        print('2/3: Geländedateien laden oder prüfen …', flush=True)
        download(root, max_files=max_files)
    else:
        print('Offline: nur vorhandene Dateien prüfen und verarbeiten.', flush=True)
    print('3/3: Gelände zusammenfügen und prüfen …', flush=True)
    result = normalize(root)
    print('Ergebnisbericht: '+str(root/'reports'/'normalize_terrain.json'), flush=True)
    return result
