"""Windowed LV95 terrain mosaic, integrity checks and explicit coverage gate."""
import json
import math
import tempfile
from contextlib import ExitStack
from pathlib import Path

from .core import load, fingerprint, write_json
from .acquire import digest

VERSION = 1
MAX_PIXELS = 100_000_000


def normalize(root):
    import numpy as np
    import rasterio
    from rasterio.enums import Resampling
    from rasterio.transform import from_origin
    from rasterio.vrt import WarpedVRT
    from rasterio.windows import bounds as window_bounds
    from PIL import Image

    root = Path(root).resolve()
    config = load(root)
    manifest = root/'inputs'/'downloads.json'
    if not manifest.is_file():
        raise ValueError('Noch keine Downloads vorhanden. Zuerst prepare oder download ausführen.')
    records = [r for r in json.loads(manifest.read_text(encoding='utf-8'))['files'] if r['layer'] == 'terrain']
    if not records:
        raise ValueError('Keine Geländedateien registriert')
    selection_path = root/'reports'/'acquire_terrain.json'
    if selection_path.is_file():
        selection = json.loads(selection_path.read_text(encoding='utf-8'))
        if selection['config_sha256'] != fingerprint(config):
            raise ValueError('Kachelplan passt nicht zum aktuellen Gebiet')
        wanted = {a['asset'] for a in selection['assets']}
        records = [r for r in records if r['asset'] in wanted]
        if {r['asset'] for r in records} != wanted:
            raise ValueError('Nicht alle geplanten Geländekacheln heruntergeladen')
    sources = []
    for record in records:
        if record['config_sha256'] != fingerprint(config):
            raise ValueError('Gebiet nach dem Download geändert. Neue Kachelsuche und Download nötig.')
        # Relative project-local copies take precedence, allowing a project folder to be moved.
        name = record['asset']
        if Path(name).name != name or '\\' in name:
            raise ValueError('Ungültiger Dateiname im Downloadverzeichnis')
        local = root/'inputs'/'terrain'/name
        path = local if local.is_file() else Path(record['path'])
        if not path.is_file():
            raise ValueError('Geländedatei fehlt: '+name)
        if digest(path) != record['sha256']:
            raise ValueError('Geländedatei verändert oder beschädigt: '+name)
        if record.get('crs') != 'EPSG:2056' or record.get('vertical_crs') != 'EPSG:5728':
            raise ValueError('Gelände benötigt LV95 und bestätigten LN02-Höhenbezug: '+name)
        sources.append((record, path))
    sources.sort(key=lambda pair: pair[0]['asset'])
    signature = fingerprint({'config': config, 'normalizer': VERSION,
                             'sources': [(r['asset'], r['sha256']) for r, _ in sources]})
    report_path = root/'reports'/'normalize_terrain.json'
    if report_path.is_file():
        prior = json.loads(report_path.read_text(encoding='utf-8'))
        if prior.get('signature') == signature and prior.get('status') == 'complete':
            if all((root/f['path']).is_file() and digest(root/f['path']) == f['sha256'] for f in prior['outputs']):
                print('Normalisierung: vorhandenes geprüftes Ergebnis wird verwendet.', flush=True)
                return prior
    folder = root/'work'/'normalized'
    folder.mkdir(parents=True, exist_ok=True)
    # Every attempt gets a new directory. Only a complete report publishes a successful run.
    with tempfile.TemporaryDirectory(prefix='terrain-', dir=folder) as staging, ExitStack() as stack:
        staging = Path(staging)
        stack.enter_context(rasterio.Env(GDAL_CACHEMAX=64*1024*1024))
        datasets = []
        resolutions = set()
        for record, path in sources:
            src = stack.enter_context(rasterio.open(path))
            if src.crs != rasterio.crs.CRS.from_epsg(2056) or src.count != 1:
                raise ValueError('Ungültiges Gelände-GeoTIFF: '+path.name)
            t = src.transform
            if t.b != 0 or t.d != 0 or t.a <= 0 or t.e >= 0 or abs(t.a+t.e) > 1e-7:
                raise ValueError('Geländeraster muss nordorientiert mit quadratischen Zellen sein: '+path.name)
            res = round(t.a, 8)
            if abs(res-float(record['resolution_m'])) > 1e-6:
                raise ValueError('Rasterauflösung widerspricht Metadaten: '+path.name)
            if src.scales[0] != 1 or src.offsets[0] != 0 or src.units[0] not in (None, 'm', 'metre', 'meter'):
                raise ValueError('Unbekannte Höheneinheit oder Skalierung: '+path.name)
            resolutions.add(res)
            datasets.append(src)
        if len(resolutions) != 1:
            raise ValueError('Gemischte Geländeauflösungen. Ein einheitliches Downloadset verwenden.')
        resolution = resolutions.pop()
        e0, n0, e1, n1 = config['bbox']
        left = math.floor(e0/resolution)*resolution
        bottom = math.floor(n0/resolution)*resolution
        right = math.ceil(e1/resolution)*resolution
        top = math.ceil(n1/resolution)*resolution
        width = round((right-left)/resolution)
        height = round((top-bottom)/resolution)
        if width*height > MAX_PIXELS:
            raise ValueError('Mehr als 100 Millionen Rasterzellen. Gebiet verkleinern oder gröbere Quelldaten verwenden.')
        transform = from_origin(left, top, resolution, resolution)
        vrts = [stack.enter_context(WarpedVRT(src, crs='EPSG:2056', transform=transform,
                  width=width, height=height, nodata=float('nan'), dtype='float32',
                  resampling=Resampling.nearest, warp_mem_limit=32)) for src in datasets]
        output = staging/'terrain_lv95.tif'
        profile = dict(driver='GTiff', width=width, height=height, count=1, dtype='float32',
                       crs='EPSG:2056', transform=transform, nodata=float('nan'),
                       tiled=True, blockxsize=512, blockysize=512, compress='deflate', BIGTIFF='IF_SAFER')
        missing, valid_count = 0, 0
        minimum, maximum = float('inf'), -float('inf')
        print(f'Gelände: {len(datasets)} Kacheln → {width} × {height} Zellen, {resolution:g} m.', flush=True)
        with rasterio.open(output, 'w', **profile) as dst:
            dst.update_tags(vertical_crs='EPSG:5728', vertical_unit='metre',
                            source='swissALTI3D; © swisstopo', resampling='nearest',
                            requested_bbox=json.dumps(config['bbox']))
            for _, window in dst.block_windows(1):
                tile = np.full((int(window.height), int(window.width)), np.nan, dtype='float32')
                wl, wb, wr, wt = window_bounds(window, transform)
                for src, vrt in zip(datasets, vrts):
                    sl, sb, sr, st = src.bounds
                    if sl >= wr or sr <= wl or sb >= wt or st <= wb:
                        continue
                    data = vrt.read(1, window=window, masked=True).filled(np.nan)
                    valid = np.isfinite(data) & ~np.isfinite(tile)
                    tile[valid] = data[valid]
                ok = np.isfinite(tile)
                valid_count += int(ok.sum())
                missing += int((~ok).sum())
                if ok.any():
                    minimum = min(minimum, float(tile[ok].min()))
                    maximum = max(maximum, float(tile[ok].max()))
                dst.write(tile, 1, window=window)
        details = {'schema_version': 1, 'signature': signature, 'config_sha256': fingerprint(config),
                   'requested_bbox_lv95': config['bbox'], 'raster_bbox_lv95': [left,bottom,right,top],
                   'resolution_m': resolution, 'width': width, 'height': height,
                   'vertical_crs': 'EPSG:5728', 'vertical_unit': 'metre',
                   'missing_cells': missing, 'valid_cells': valid_count,
                   'coverage_fraction': valid_count/(width*height),
                   'height_min_m': minimum if valid_count else None,
                   'height_max_m': maximum if valid_count else None,
                   'source_count': len(sources),
                   'sources': [{'asset':r['asset'], 'sha256':r['sha256'], 'datetime':r.get('datetime'),
                                'license':r.get('license'), 'attribution':r.get('attribution')} for r,_ in sources],
                   'note': 'Raster auf volle Zellen nach außen gerundet; maximal eine Zelle Rand. Keine Lückenfüllung. Kein BeamNG-Level.'}
        if missing:
            details.update(status='incomplete', outputs=[])
            write_json(report_path, details)
            raise ValueError(f'Gelände unvollständig: {missing} Rasterzellen ohne Höhe. Bericht: {report_path}')
        with rasterio.open(output) as src:
            scale = min(1, 1024/max(width,height))
            preview = src.read(1, out_shape=(max(1,round(height*scale)), max(1,round(width*scale))),
                               resampling=Resampling.nearest)
        span = max(maximum-minimum, 1)
        grey = (40+205*np.clip((preview-minimum)/span,0,1)).astype('uint8')
        Image.fromarray(grey).save(staging/'terrain_preview.png')
        # Close VRTs and source handles before publishing on Windows.
        stack.close()
        destination = folder/(staging.name+'-complete')
        staging.rename(destination)
        details.update(status='complete', outputs=[
            {'path':str((destination/name).relative_to(root)), 'sha256':digest(destination/name)}
            for name in ('terrain_lv95.tif','terrain_preview.png')])
        write_json(report_path, details)
        print(f'Gelände vollständig: Höhe {minimum:.2f} bis {maximum:.2f} m LN02.', flush=True)
        return details
