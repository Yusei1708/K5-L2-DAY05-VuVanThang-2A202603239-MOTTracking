import argparse
import json
from pathlib import Path
import sys
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import setup_local_lab as lab


class LocalLabTests(unittest.TestCase):
    def test_same_mssv_keeps_its_assignment(self):
        expected = {"20241231": "A", "20241237": "B", "20241234": "C"}
        for mssv, variant in expected.items():
            self.assertEqual(lab.variant_for(mssv), variant)
        self.assertEqual(lab.variant_for(" k5-001 "), lab.variant_for("K5-001"))

    def test_each_variant_has_five_distinct_targets_and_same_cp2_target(self):
        config = json.loads((lab.ROOT / "src" / "lab_variants.json").read_text())
        groups = config["variants"]
        self.assertEqual(set(groups), set("ABC"))
        self.assertEqual(len({frozenset(group) for group in groups.values()}), 3)
        self.assertEqual(len({group[0] for group in groups.values()}), 1)
        for group in groups.values():
            self.assertEqual(len(group), 5)
            self.assertEqual(len(set(group)), 5)
            for target in group:
                image = config["targets"][str(target)]["image"]
                self.assertIn(image, range(1, 151))

    def test_cvat_destination_must_be_loopback(self):
        self.assertEqual(lab.local_server("http://localhost:8080/"), "http://localhost:8080")
        self.assertEqual(lab.local_server("http://[::1]:8080"), "http://[::1]:8080")
        for server in ("https://app.cvat.ai", "http://localhost@cvat.ai", "http://localhost/upload"):
            with self.assertRaises(argparse.ArgumentTypeError):
                lab.local_server(server)


if __name__ == "__main__":
    unittest.main()
