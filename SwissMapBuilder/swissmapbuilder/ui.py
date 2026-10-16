"""Loopback-only selection UI. No game files are touched."""
import json
import secrets
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from .core import init

HTML = '''<!doctype html><html lang="de"><meta charset="utf-8"><title>SwissMapBuilder</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<style>body{margin:0;font:16px system-ui;background:#eef3f7;color:#142636}header{padding:16px}h1{margin:0}#map{height:65vh}button,input{padding:10px;margin:5px}#status{white-space:pre-wrap;padding:12px}small{display:block}</style>
<header><h1>SwissMapBuilder · Gebiet wählen</h1><p>Zwei gegenüberliegende Ecken anklicken. Danach beide Eckpunkte ziehen, um die Auswahl zu ändern.</p>
<input id="name" value="meine_karte" aria-label="Projektname"><button id="reset">Neue Auswahl</button><button id="save">Gebiet speichern</button>
<small>Projektname: Kleinbuchstaben, Zahlen, _ oder -. Für den ersten Download etwa 1 km² auswählen.</small></header>
<div id="map"></div><div id="status">Karte lädt … Internet wird für Kartenkacheln und Leaflet benötigt.</div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script><script>
const token='__TOKEN__'; const status=document.getElementById('status');
if(typeof L==='undefined'){status.textContent='Kartenbibliothek nicht geladen. Internetverbindung prüfen.';}else{
const map=L.map('map').setView([46.8,8.2],8);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'© OpenStreetMap contributors'}).addTo(map);
let markers=[], rectangle;
function update(){if(markers.length===2){const b=L.latLngBounds(markers.map(m=>m.getLatLng()));if(rectangle)rectangle.setBounds(b);else rectangle=L.rectangle(b,{color:'#006eae',weight:3}).addTo(map);const size=map.distance(b.getSouthWest(),b.getSouthEast())*map.distance(b.getSouthWest(),b.getNorthWest())/1e6;status.textContent='Auswahl: ungefähr '+size.toFixed(2)+' km². Eckpunkte sind verschiebbar.';}}
map.on('click',e=>{if(markers.length===2)return;const m=L.marker(e.latlng,{draggable:true}).addTo(map);m.on('drag',update);markers.push(m);status.textContent='Jetzt die gegenüberliegende Ecke anklicken.';update();});
document.getElementById('reset').onclick=()=>{markers.forEach(m=>map.removeLayer(m));markers=[];if(rectangle)map.removeLayer(rectangle);rectangle=null;status.textContent='Erste Ecke anklicken.';};
document.getElementById('save').onclick=async()=>{if(markers.length!==2){status.textContent='Bitte zuerst zwei Ecken auswählen.';return;}const b=rectangle.getBounds();try{const r=await fetch('/project',{method:'POST',headers:{'Content-Type':'application/json','X-Selection-Token':token},body:JSON.stringify({name:document.getElementById('name').value,bbox:[b.getWest(),b.getSouth(),b.getEast(),b.getNorth()]})});const result=await r.json();status.textContent=result.message||result.error;}catch(e){status.textContent='Speichern fehlgeschlagen: '+e.message;}};
status.textContent='Erste Ecke auf der Karte anklicken.';
}
</script></html>'''

def serve(directory='projects'):
    from pyproj import Transformer
    base = Path(directory).resolve()
    token = secrets.token_urlsafe(32)
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path != '/':
                self.send_error(404); return
            body = HTML.replace('__TOKEN__', token).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers(); self.wfile.write(body)
        def do_POST(self):
            if self.path != '/project' or self.headers.get('X-Selection-Token') != token:
                self.send_error(403); return
            try:
                size = int(self.headers.get('Content-Length', '0'))
                if not 0 < size <= 4096:
                    raise ValueError('Ungültige Anfragegröße')
                data = json.loads(self.rfile.read(size))
                bbox = data['bbox']
                if len(bbox) != 4 or not (5.9 <= bbox[0] < bbox[2] <= 10.6 and 45.7 <= bbox[1] < bbox[3] <= 47.9):
                    raise ValueError('Bitte ein Gebiet innerhalb der Schweiz auswählen')
                # init validates the name before creating any directories.
                lv95 = list(Transformer.from_crs(4326, 2056, always_xy=True).transform_bounds(*bbox, densify_pts=21))
                from .core import validate
                validate({'schema_version':1,'name':data['name'],'crs':'EPSG:2056','bbox':lv95})
                project = base/data['name']
                init(project, data['name'], lv95)
                result = {'message': 'Gespeichert: '+str(project)+'\nWeiter im Terminal: python -m swissmapbuilder discover "'+str(project)+'"'}
                code = 201
            except (ValueError, TypeError, KeyError, OSError) as error:
                result = {'error': str(error)}; code = 400
            body = json.dumps(result, ensure_ascii=False).encode()
            self.send_response(code); self.send_header('Content-Type','application/json; charset=utf-8')
            self.end_headers(); self.wfile.write(body)
    server = HTTPServer(('127.0.0.1', 0), Handler)
    url = 'http://127.0.0.1:'+str(server.server_port)+'/'
    print('Kartenoberfläche: '+url+' · Beenden mit Strg+C', flush=True)
    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
