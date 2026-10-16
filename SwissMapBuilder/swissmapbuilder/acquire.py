"""swisstopo STAC discovery and atomic, checksum-verified downloads."""
import hashlib
import json
import time
from pathlib import Path
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from .core import load, fingerprint, write_json

API = 'https://data.geo.admin.ch/api/stac/v1'
COLLECTIONS = {'terrain': 'ch.swisstopo.swissalti3d',
               'orthophoto': 'ch.swisstopo.swissimage-dop10'}

def trusted(url):
    p = urlparse(url)
    if p.scheme != 'https' or p.hostname != 'data.geo.admin.ch' or p.username or p.password:
        raise ValueError('Unzulässiger swisstopo-Link')
    return url

def request(url, attempts=3):
    trusted(url)
    for attempt in range(attempts):
        try:
            return urlopen(Request(url, headers={'User-Agent': 'SwissMapBuilder/0.2'}), timeout=45)
        except (URLError, TimeoutError) as error:
            if isinstance(error, HTTPError) and error.code not in (429, 500, 502, 503, 504):
                raise
            if attempt == attempts - 1:
                raise
            time.sleep(2 ** attempt)

def fetch_json(url):
    with request(url) as response:
        return json.load(response)

def wgs_bounds(bbox):
    from pyproj import Transformer
    # Densified edges also cover projection curvature.
    return list(Transformer.from_crs(2056, 4326, always_xy=True).transform_bounds(*bbox, densify_pts=21))

def select_assets(items, layer, resolution):
    """One latest acquisition per spatial tile, in LV95 GeoTIFF at chosen GSD."""
    selected = {}
    for item in items:
        for key, asset in item.get('assets', {}).items():
            if not key.lower().endswith('.tif') or asset.get('proj:epsg') != 2056:
                continue
            if abs(float(asset.get('gsd', -1)) - resolution) > 1e-6:
                continue
            # swissALTI3D filenames carry LN02 EPSG:5728.
            if layer == 'terrain' and '_5728.' not in key:
                continue
            trusted(asset['href'])
            bbox = item.get('bbox')
            if not bbox or len(bbox) != 4:
                raise ValueError('STAC-Kachel ohne gültige räumliche Abdeckung')
            tile = tuple(bbox)
            date = item.get('properties', {}).get('datetime')
            if not date:
                raise ValueError('STAC-Kachel ohne Aufnahmezeitpunkt')
            record = {'item': item['id'], 'asset': key, 'url': asset['href'],
                      'bbox_wgs84': bbox, 'datetime': date, 'resolution_m': resolution,
                      'crs': 'EPSG:2056', 'vertical_crs': 'EPSG:5728' if layer == 'terrain' else None,
                      'checksum': asset.get('file:checksum'), 'size_bytes': asset.get('file:size'),
                      'layer': layer}
            if tile not in selected or date > selected[tile]['datetime']:
                selected[tile] = record
    return sorted(selected.values(), key=lambda r: r['asset'])

def discover(root, layer='terrain', resolution=2.0, get_json=fetch_json):
    config = load(root)
    if layer not in COLLECTIONS:
        raise ValueError('Download-Adapter unterstützt terrain und orthophoto')
    allowed = (0.5, 2.0) if layer == 'terrain' else (0.1,)
    if resolution not in allowed:
        raise ValueError('Nicht unterstützte Auflösung: ' + str(allowed))
    collection = COLLECTIONS[layer]
    bbox = wgs_bounds(config['bbox'])
    url = API + '/collections/' + collection + '/items?' + urlencode({'bbox': ','.join(map(str, bbox)), 'limit': 100})
    items, seen = [], set()
    while url:
        trusted(url)
        if url in seen or len(seen) >= 1000:
            raise ValueError('Ungültige oder zu große STAC-Seitenfolge')
        seen.add(url)
        page = get_json(url)
        items.extend(page['features'])
        url = next((link['href'] for link in page.get('links', []) if link.get('rel') == 'next'), None)
    assets = select_assets(items, layer, resolution)
    if not assets:
        raise ValueError('Keine passenden Datenkacheln gefunden')
    metadata = get_json(API + '/collections/' + collection)
    result = {'schema_version': 1, 'config_sha256': fingerprint(config), 'collection': collection,
              'license': metadata.get('license', 'unknown'), 'collection_metadata': metadata,
              'bbox_wgs84': bbox, 'assets': assets,
              'note': 'Vollständige Kacheln; Zuschnitt und GIS-Abdeckungsprüfung folgen bei Normalisierung.'}
    write_json(Path(root)/'reports'/('acquire_' + layer + '.json'), result)
    return result

def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()

def expected_sha(record):
    checksum = record.get('checksum')
    if checksum and checksum.lower().startswith('1220') and len(checksum) == 68:
        return checksum[4:].lower() # SHA-256 multihash
    return None

def download(root, layer='terrain', max_files=100, opener=request):
    config = load(root)
    report = json.loads((Path(root)/'reports'/('acquire_' + layer + '.json')).read_text(encoding='utf-8'))
    if report['config_sha256'] != fingerprint(config):
        raise ValueError('Gebiet geändert: discover erneut ausführen')
    assets = report['assets']
    if max_files < 1 or len(assets) > max_files:
        raise ValueError('Download überschreitet Dateilimit; Gebiet verkleinern oder --max-files erhöhen')
    manifest_path = Path(root)/'inputs'/'downloads.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8')) if manifest_path.exists() else {'files': []}
    folder = Path(root)/'inputs'/layer
    folder.mkdir(parents=True, exist_ok=True)
    for record in assets:
        name = record['asset']
        if Path(name).name != name or '\\' in name or name in ('.', '..'):
            raise ValueError('Unsicherer Asset-Dateiname')
        target = folder/name
        expected = expected_sha(record)
        prior = next((r for r in manifest['files'] if r['url'] == record['url']), None)
        checksum = digest(target) if target.is_file() else None
        cached = checksum is not None and checksum == (expected or (prior or {}).get('sha256'))
        if not cached:
            temporary = target.with_suffix(target.suffix + '.part')
            try:
                with opener(trusted(record['url'])) as response, temporary.open('wb') as stream:
                    for block in iter(lambda: response.read(1024*1024), b''):
                        stream.write(block)
                checksum = digest(temporary)
                if expected and checksum != expected:
                    raise ValueError('Prüfsumme stimmt nicht: ' + name)
                if record.get('size_bytes') is not None and temporary.stat().st_size != record['size_bytes']:
                    raise ValueError('Unvollständiger Download: ' + name)
                temporary.replace(target)
            finally:
                temporary.unlink(missing_ok=True)
        entry = dict(record, path=str(target.resolve()), sha256=checksum,
                     config_sha256=fingerprint(config), license=report['license'],
                     attribution='© swisstopo', validation='checksum_only',
                     checksum_verified=bool(expected))
        manifest['files'] = [r for r in manifest['files'] if r['url'] != record['url']]
        manifest['files'].append(entry)
        write_json(manifest_path, manifest)
        print(('Cache: ' if cached else 'Geladen: ') + name, flush=True)
    return manifest
