import json
import tempfile
import unittest
from pathlib import Path
import numpy as np
import rasterio
from rasterio.transform import from_origin
from swissmapbuilder.acquire import digest
from swissmapbuilder.core import init, fingerprint, write_json, status
from swissmapbuilder.normalize import normalize
from swissmapbuilder.workflow import prepare

class TerrainTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  self.config=init(self.root,'test',[2620000,1250000,2620016,1250008]);self.records=[]
  self.tile('west.tif',2620000,np.full((4,4),450,dtype='float32'))
  self.tile('east.tif',2620008,np.full((4,4),500,dtype='float32'));self.manifest()
 def tile(self,name,left,data,crs='EPSG:2056'):
  folder=self.root/'inputs'/'terrain';folder.mkdir(parents=True,exist_ok=True);path=folder/name
  with rasterio.open(path,'w',driver='GTiff',width=4,height=4,count=1,dtype='float32',crs=crs,transform=from_origin(left,1250008,2,2),nodata=-9999) as dst:dst.write(data,1)
  record={'layer':'terrain','asset':name,'path':str(path),'sha256':digest(path),'config_sha256':fingerprint(self.config),'crs':'EPSG:2056','vertical_crs':'EPSG:5728','resolution_m':2.0,'datetime':'2025-01-01','url':'https://data.geo.admin.ch/'+name}
  self.records=[r for r in self.records if r['asset']!=name]+[record]
 def manifest(self):write_json(self.root/'inputs'/'downloads.json',{'files':self.records})
 def test_mosaic_values_bounds(self):
  result=normalize(self.root)
  with rasterio.open(self.root/result['outputs'][0]['path']) as src:
   data=src.read(1);np.testing.assert_array_equal(data[:,:4],450);np.testing.assert_array_equal(data[:,4:],500)
   self.assertEqual(tuple(src.bounds),tuple(self.config['bbox']));self.assertEqual(src.tags()['vertical_crs'],'EPSG:5728')
  self.assertEqual(result['missing_cells'],0);self.assertEqual(result['height_min_m'],450);self.assertEqual(result['height_max_m'],500)
 def test_cache_corruption(self):
  first=normalize(self.root);self.assertEqual(normalize(self.root),first)
  (self.root/first['outputs'][1]['path']).write_bytes(b'corrupt');second=normalize(self.root)
  self.assertNotEqual(first['outputs'][0]['path'],second['outputs'][0]['path'])
 def test_missing_tile(self):
  self.records=self.records[:1];self.manifest()
  with self.assertRaisesRegex(ValueError,'unvollständig'):normalize(self.root)
  report=json.loads((self.root/'reports'/'normalize_terrain.json').read_text());self.assertEqual(report['missing_cells'],16);self.assertEqual(report['outputs'],[])
  self.assertFalse(list((self.root/'work'/'normalized').glob('*-complete')))
 def test_nodata(self):
  data=np.full((4,4),450,dtype='float32');data[1,1]=-9999;self.tile('west.tif',2620000,data);self.manifest()
  with self.assertRaisesRegex(ValueError,'1 Rasterzellen'):normalize(self.root)
 def test_north_orientation(self):
  values=np.arange(16,dtype='float32').reshape(4,4)+450;self.tile('west.tif',2620000,values);self.manifest();result=normalize(self.root)
  with rasterio.open(self.root/result['outputs'][0]['path']) as src:np.testing.assert_array_equal(src.read(1)[:,:4],values)
 def test_crs(self):
  self.tile('west.tif',2620000,np.zeros((4,4),dtype='float32'),crs='EPSG:3857');self.manifest()
  with self.assertRaisesRegex(ValueError,'GeoTIFF'):normalize(self.root)
 def test_checksum(self):
  (self.root/'inputs'/'terrain'/'west.tif').write_bytes(b'bad')
  with self.assertRaisesRegex(ValueError,'beschädigt'):normalize(self.root)
 def test_vertical_reference(self):
  self.records[0]['vertical_crs']='EPSG:5703';self.manifest()
  with self.assertRaisesRegex(ValueError,'Höhenbezug'):normalize(self.root)
 def test_stale(self):
  write_json(self.root/'project.json',dict(self.config,bbox=[2620000,1250000,2620008,1250008]))
  with self.assertRaisesRegex(ValueError,'Gebiet'):normalize(self.root)
 def test_selection_complete(self):
  write_json(self.root/'reports'/'acquire_terrain.json',{'config_sha256':fingerprint(self.config),'assets':[{'asset':'absent.tif'}]})
  with self.assertRaisesRegex(ValueError,'Nicht alle'):normalize(self.root)
 def test_moved_folder(self):
  for record in self.records:record['path']='Z:/unavailable/'+record['asset']
  self.manifest();self.assertEqual(normalize(self.root)['status'],'complete')
 def test_offline(self):self.assertEqual(prepare(self.root,offline=True)['coverage_fraction'],1)
 def test_outward_rounding(self):
  self.config['bbox']=[2620001,1250001,2620015,1250007];write_json(self.root/'project.json',self.config)
  for record in self.records:record['config_sha256']=fingerprint(self.config)
  self.manifest();self.assertEqual(normalize(self.root)['raster_bbox_lv95'],[2620000,1250000,2620016,1250008])

 def test_status_output_integrity(self):
  result=normalize(self.root)
  self.assertEqual(status(self.root)['terrain_normalization']['status'],'complete')
  (self.root/result['outputs'][0]['path']).unlink()
  self.assertEqual(status(self.root)['terrain_normalization']['status'],'missing_output')
 def test_multiple_output_blocks(self):
  self.config['bbox']=[2620000,1250000,2621040,1251040]
  write_json(self.root/'project.json',self.config)
  path=self.root/'inputs'/'terrain'/'large.tif'
  data=np.arange(520*520,dtype='float32').reshape(520,520)/1000
  with rasterio.open(path,'w',driver='GTiff',width=520,height=520,count=1,dtype='float32',crs='EPSG:2056',transform=from_origin(2620000,1251040,2,2)) as dst:dst.write(data,1)
  record=dict(self.records[0],asset='large.tif',path=str(path),sha256=digest(path),config_sha256=fingerprint(self.config))
  self.records=[record];self.manifest()
  result=normalize(self.root)
  with rasterio.open(self.root/result['outputs'][0]['path']) as src:np.testing.assert_array_equal(src.read(1),data)
