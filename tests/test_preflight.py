import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr

from _load import load

preflight = load("replica-deploy", "preflight")


def put(root, rel, text):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return path


class Preflight(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def populate_clean_clone(self):
        put(self.root, "src/index.ts", "export const app = 'Slotwise';\n")
        put(self.root, "replica/features.csv",
            "feature,area,priority,original,clone,notes\n"
            "Book a slot,booking,must,yes,yes,\n"
            "Cancel booking,booking,should,yes,yes,\n")
        put(self.root, "replica/tokens.json", json.dumps({
            "color": {"text": "#111111", "bg": "#ffffff"},
            "pairs": [["text", "bg"]]
        }))
        put(self.root, "replica/brand.json", json.dumps({
            "avoid": ["Calendly"],
            "domains": ["calendly.com"],
            "colors": ["#006bff"]
        }))
        put(self.root, "replica/launch/listing.json", json.dumps({
            "avoid": ["Calendly"],
            "app_store": {
                "name": "Slotwise: Booking Links",
                "subtitle": "Share a link, get booked",
                "promotional_text": "Fast scheduling.",
                "description": "Book meetings without back and forth.",
                "keywords": "schedule,calendar,meeting,appointment",
                "whats_new": "Initial release."
            }
        }))

    def test_all_gates_pass_on_clean_clone(self):
        self.populate_clean_clone()
        rep = preflight.run_preflight(self.root)
        self.assertTrue(rep["passed"])
        gates = {c["gate"]: c["passed"] for c in rep["checks"]}
        self.assertEqual(gates, {
            "parity": True,
            "contrast": True,
            "sweep": True,
            "listing": True,
        })
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = preflight.main([self.root])
        self.assertEqual(code, 0)
        self.assertIn("READY TO DEPLOY", buf.getvalue())

    def test_fails_when_leftover_brand_or_incomplete_must_have(self):
        self.populate_clean_clone()
        put(self.root, "src/leaked.ts", "const url = 'https://calendly.com';\n")
        with redirect_stdout(io.StringIO()):
            self.assertEqual(preflight.main([self.root]), 1)

    def test_empty_project_exits_2(self):
        with redirect_stderr(io.StringIO()):
            self.assertEqual(preflight.main([self.root]), 2)


if __name__ == "__main__":
    unittest.main()
