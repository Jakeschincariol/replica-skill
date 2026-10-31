import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr

from _load import load, ROOT

parity = load("replica-diff", "parity")

MATRIX = """feature,area,priority,original,clone,notes
Pick a time slot,booking page,must,yes,yes,
Confirmation email,booking page,must,yes,partial,no calendar file yet
Reschedule link,booking page,must,yes,no,
Round-robin across a team,team,should,yes,no,
Custom booking questions,booking page,should,yes,yes,
Embed on a website,sharing,could,yes,no,
Their partner marketplace,integrations,could,yes,skip,their network not ours
SMS reminders,notifications,should,no,yes,ours: the top request in reviews
"""


def write(d, name, text):
    path = os.path.join(d, name)
    with open(path, "w") as fh:
        fh.write(text)
    return path


class Score(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = write(self.tmp.name, "features.csv", MATRIX)

    def tearDown(self):
        self.tmp.cleanup()

    def test_weighted_score(self):
        r = parity.score(parity.load(self.path))
        # counted weights: 3+3+3+2+2+1 = 14, earned: 3 + 1.5 + 0 + 0 + 2 + 0 = 6.5
        self.assertAlmostEqual(r["feature_score"], round(100 * 6.5 / 14, 1))
        self.assertEqual(r["counted"], 6)
        self.assertEqual((r["must_have_done"], r["must_have_total"]), (1, 3))

    def test_skip_and_extras_are_not_scored_but_listed(self):
        r = parity.score(parity.load(self.path))
        self.assertEqual([m["feature"] for m in r["skipped"]], ["Their partner marketplace"])
        self.assertEqual([m["feature"] for m in r["extras"]], ["SMS reminders"])

    def test_missing_is_in_build_order(self):
        r = parity.score(parity.load(self.path))
        order = [m["feature"] for m in r["missing"]]
        self.assertEqual(order[0], "Reschedule link")          # must, not started
        self.assertEqual(order[1], "Confirmation email")       # must, partial
        self.assertEqual(order[2], "Round-robin across a team")
        self.assertEqual(order[-1], "Embed on a website")
        self.assertEqual(r["missing"][0]["priority"], "must")

    def test_weakest_area_first(self):
        r = parity.score(parity.load(self.path))
        self.assertEqual(r["by_area"][0]["score"], 0.0)
        self.assertIn(r["by_area"][0]["area"], ("team", "sharing"))

    def test_render_says_not_shippable(self):
        r = parity.combine(parity.score(parity.load(self.path)), [])
        text = parity.render(r)
        self.assertIn("Not shippable yet: 2 must-have", text)
        self.assertIn("their network not ours", text)

    def test_visual_folds_in_at_20_percent(self):
        d = self.tmp.name
        v1 = write(d, "a.json", json.dumps({"score": 80.0, "mode": "layout",
                                            "files": {"clone": "clone/home.png"}}))
        v2 = write(d, "b.json", json.dumps({"score": 60.0, "mode": "layout"}))
        r = parity.combine(parity.score(parity.load(self.path)),
                           parity.visual_scores([v1, v2]))
        self.assertEqual(r["layout_score"], 70.0)
        self.assertAlmostEqual(r["overall"], round(0.8 * r["feature_score"] + 14.0, 1))

    def test_bad_values_are_reported_not_fatal(self):
        p = write(self.tmp.name, "bad.csv",
                  "feature,priority,clone\nThing,urgent,maybe\n")
        r = parity.score(parity.load(p))
        self.assertEqual(len(r["problems"]), 2)
        self.assertEqual(r["feature_score"], 0.0)

    def test_missing_column_is_an_error(self):
        p = write(self.tmp.name, "nocol.csv", "feature,area\nx,y\n")
        with redirect_stderr(io.StringIO()):
            self.assertEqual(parity.main([p]), 2)

    def test_cli_fail_under(self):
        with redirect_stdout(io.StringIO()):
            self.assertEqual(parity.main([self.path, "--fail-under", "80"]), 1)
            self.assertEqual(parity.main([self.path, "--fail-under", "10"]), 0)

    def test_shipped_template_parses(self):
        path = os.path.join(ROOT, "skills", "replica-recon", "features.csv")
        r = parity.score(parity.load(path))
        self.assertGreater(r["counted"], 0)
        self.assertEqual(r["problems"], [])


if __name__ == "__main__":
    unittest.main()
