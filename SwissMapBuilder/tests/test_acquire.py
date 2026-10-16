import hashlib, io, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from swissmapbuilder.core import init, fingerprint, write_json, status
from swissmapbuilder.acquire import download, discover, select_assets, trusted

class AcquisitionTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
  self.config=init(self.root,'demo',[2620000,1250000,2620100,1250100]);self.payload=b'fixture'
  self.record={'asset':'tile_2_2056_5728.tif','url':'https://data.geo.admin.ch/tile.tif','checksum':'1220'+hashlib.sha256(self.payload).hexdigest(),'layer':'terrain'}
  self.report()
 def report(self):
  write_json(self.root/'reports/acquire_terrain.json',{'config_sha256':fingerprint(self.config),'assets':[self.record],'license':'test'})
 def test_cache_and_corruption(self):
  calls=[]
  def opener(url):calls.append(url);return io.BytesIO(self.payload)
  download(self.root,opener=opener);download(self.root,opener=opener);self.assertEqual(len(calls),1)
  (self.root/'inputs/terrain'/self.record['asset']).write_bytes(b'corrupt')
  download(self.root,opener=opener);self.assertEqual(len(calls),2)
 def test_download_status(self):
  download(self.root,opener=lambda _:io.BytesIO(self.payload))
  self.assertEqual(status(self.root)["inputs"][0]["status"],"checksum_only")
  (self.root/"inputs/terrain"/self.record["asset"]).unlink()
  self.assertEqual(status(self.root)["inputs"][0]["status"],"missing_file")
 def test_bad_checksum(self):
  with self.assertRaises(ValueError):download(self.root,opener=lambda _:io.BytesIO(b'wrong'))
  self.assertFalse((self.root/'inputs/terrain'/self.record['asset']).exists());self.assertFalse(list(self.root.glob('inputs/terrain/*.part')))
 def test_stale(self):
  write_json(self.root/'project.json',dict(self.config,bbox=[2620000,1250000,2620200,1250200]))
  with self.assertRaises(ValueError):download(self.root)
 def test_limit(self):
  with self.assertRaises(ValueError):download(self.root,max_files=0)
 def test_trust(self):
  for url in ['http://data.geo.admin.ch/a','https://evil.example/a','https://data.geo.admin.ch.evil/a']:
   with self.assertRaises(ValueError):trusted(url)
 def test_latest_resolution(self):
  def item(year):return {'id':str(year),'bbox':[7,47,7.1,47.1],'properties':{'datetime':str(year)},'assets':{'tile_2_2056_5728.tif':{'href':self.record['url'],'proj:epsg':2056,'gsd':2},'tile_0.5_2056_5728.tif':{'href':self.record['url'],'proj:epsg':2056,'gsd':0.5}}}
  result=select_assets([item(2020),item(2023)],'terrain',2);self.assertEqual(len(result),1);self.assertEqual(result[0]['item'],'2023')
 def test_pagination_cycle(self):
  page={'features':[],'links':[{'rel':'next','href':'https://data.geo.admin.ch/next'}]}
  with patch('swissmapbuilder.acquire.wgs_bounds',return_value=[7,47,7.1,47.1]):
   with self.assertRaisesRegex(ValueError,'Seitenfolge'):discover(self.root,get_json=lambda _:page)
 def test_unsafe_name(self):
  self.record['asset']='../bad.tif';self.report()
  with self.assertRaises(ValueError):download(self.root)
