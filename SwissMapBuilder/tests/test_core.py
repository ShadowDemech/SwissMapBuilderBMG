import tempfile
import unittest
from pathlib import Path
from swissmapbuilder.core import init, plan, register, status, tiles, validate

class ProjectTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)/"project"
        self.config = init(self.root, "test_area", [2620000, 1250000, 2621000, 1251000])

    def test_exact_boundaries_and_origin(self):
        self.assertEqual(len(tiles(self.config)), 1)
        self.assertEqual(plan(self.config)["origin_lv95"], [2620500, 1250500])
        self.assertEqual(plan(self.config)["area_km2"], 1)

    def test_crossing_boundary(self):
        self.config["bbox"] = [2620999, 1250999, 2621001, 1251001]
        self.assertEqual(len(tiles(self.config)), 4)

    def test_bad_bounds_and_names(self):
        for bbox in ([2621000, 1250000, 2620000, 1251000], [float("nan"), 0, 1, 2]):
            with self.assertRaises(ValueError):
                validate(dict(self.config, bbox=bbox))
        with self.assertRaises(ValueError):
            validate(dict(self.config, name="../escape"))

    def test_no_overwrite(self):
        with self.assertRaises(ValueError):
            init(self.root, "replacement", self.config["bbox"])
        self.assertEqual(status(self.root)["project"], "test_area")

    def test_provenance_changes_missing_and_deduplication(self):
        data = Path(self.temp.name)/"sample.tif"
        data.write_bytes(b"test fixture, not real GIS data")
        for _ in range(2):
            register(self.root, "terrain", data, "test-source", "test-license", "2026-01-01", "measured")
        self.assertEqual(len(status(self.root)["inputs"]), 1)
        self.assertEqual(status(self.root)["inputs"][0]["status"], "registered_only")
        data.write_bytes(b"changed")
        self.assertEqual(status(self.root)["inputs"][0]["status"], "changed_file")
        data.unlink()
        self.assertEqual(status(self.root)["inputs"][0]["status"], "missing_file")

    def test_config_change_invalidates_inputs(self):
        import json
        data = Path(self.temp.name)/"sample.laz"
        data.write_bytes(b"fixture")
        register(self.root, "surface", data, "test", "test", "2026-01-01", "measured")
        config = dict(self.config, bbox=[2620000, 1250000, 2622000, 1252000])
        (self.root/"project.json").write_text(json.dumps(config))
        self.assertEqual(status(self.root)["inputs"][0]["status"], "stale_config")

if __name__ == "__main__":
    unittest.main()
