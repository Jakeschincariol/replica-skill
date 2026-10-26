import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr

from _load import load
from test_imgdiff import page

sweep = load("replica-brand", "sweep")
listing = load("replica-launch", "listing")
contrast = load("replica-design", "contrast")
parity = load("replica-diff", "parity")
reviews = load("replica-entrepreneur", "reviews")
imgdiff = load("replica-diff", "imgdiff")


class SweepColours(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def put(self, rel, text):
        path = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fh:
            fh.write(text)

    def test_every_way_code_writes_a_colour(self):
        self.put("web/a.css", ".x { color: #006bffcc; }\n")             # CSS with alpha
        self.put("web/b.css", ".y { color: rgb(0, 107, 255); }\n")      # rgb()
        self.put("android/colors.xml", '<color name="a">#ff006bff</color>\n')  # ARGB
        self.put("android/Theme.kt", "val Brand = Color(0xFF006BFF)\n")
        self.put("web/c.css", ".z { color: #006bfe; }\n")               # a different blue
        hits = sweep.sweep(self.root, colors=["#006bff"])
        files = sorted(h["file"].replace(os.sep, "/") for h in hits)
        self.assertEqual(files, ["android/Theme.kt", "android/colors.xml",
                                 "web/a.css", "web/b.css"])

    def test_bad_colour_in_the_list_is_an_error_not_a_clean_pass(self):
        self.put("a.css", "body {}\n")
        err = io.StringIO()
        with redirect_stdout(io.StringIO()), redirect_stderr(err):
            code = sweep.main([self.root, "--colors", "#00zzff"])
        self.assertEqual(code, 2)
        self.assertIn("not a hex colour", err.getvalue())

    def test_colour_without_hash_is_accepted(self):
        self.put("a.css", ".x { color: #006BFF; }\n")
        self.assertEqual(len(sweep.sweep(self.root, colors=["006bff"])), 1)


class ListingFixes(unittest.TestCase):
    def test_trademark_symbols_are_not_emoji(self):
        issues = listing.lint({"app_store": {"name": "SafeApp™", "description": "x"}})
        self.assertFalse(any("emoji" in i["message"] for i in issues))

    def test_free_as_available_is_not_a_price_claim(self):
        def claims(text):
            issues = listing.lint({"google_play": {"title": "x", "full_description": "x",
                                                   "short_description": text}})
            return [i for i in issues if "claim" in i["message"]]
        self.assertEqual(claims("Book the times you are actually free."), [])
        self.assertEqual(len(claims("Free booking links for everyone")), 1)

    def test_combining_marks_count_like_the_store_counts_them(self):
        # Thai: consonant + vowel sign (a combining mark). App Store Connect counts both.
        self.assertEqual(listing.length("กิ"), 2)
        # emoji glue is still free: family emoji joined with ZWJ is one
        self.assertEqual(listing.length("\U0001F468‍\U0001F469‍\U0001F467"), 1)

    def test_avoid_name_matches_without_its_space(self):
        issues = listing.lint({"avoid": ["Acuity Scheduling"],
                               "google_play": {"title": "Better than AcuityScheduling",
                                               "full_description": "x"}})
        self.assertTrue(any("Acuity Scheduling" in i["message"] for i in issues))

    def test_locales_are_linted_and_cross_locale_keywords_flagged(self):
        data = {"app_store": {"locales": {
            "en-US": {"name": "Check In", "description": "x",
                      "keywords": "safety,alone,alert"},
            "es-MX": {"name": "Check In", "description": "x",
                      "keywords": "seguridad,alert,solo,check," + "x" * 90},
        }}}
        issues = listing.lint(data)
        stores = {i["store"] for i in issues}
        self.assertIn("app_store[es-MX]", stores)
        over = [i for i in issues if "limit is 100" in i["message"]]
        self.assertEqual([i["store"] for i in over], ["app_store[es-MX]"])
        cross = [i for i in issues if "also indexed by" in i["message"]]
        self.assertEqual(len(cross), 1)
        self.assertIn("alert", cross[0]["message"])
        self.assertIn("check", cross[0]["message"])
        out = listing.render(data, issues)
        self.assertIn("App Store[es-MX]", out)


class ContrastAlpha(unittest.TestCase):
    def test_alpha_and_rgb_values(self):
        # 50% black on white renders as mid grey: about 4:1 (#80 alpha is 50.2%)
        for fg in ("#00000080", "rgba(0, 0, 0, 0.5)", "rgba(0 0 0 / 50%)"):
            self.assertAlmostEqual(contrast.ratio(fg, "#ffffff"), 3.99, delta=0.03)
        self.assertAlmostEqual(contrast.ratio("rgb(0,0,0)", "#fff"), 21.0, places=2)

    def test_alpha_tokens_are_checked_not_unknown(self):
        cols = contrast.colours({"color": {"text-muted": "#14171c99", "bg": "#ffffff"}})
        rows = contrast.check(cols, [["text-muted", "bg"]])
        self.assertNotIn("error", rows[0])


class ParityGlob(unittest.TestCase):
    def test_visual_glob_is_expanded_here_not_by_the_shell(self):
        with tempfile.TemporaryDirectory() as d:
            for name, score in (("S01.json", 80.0), ("S02.json", 90.0)):
                with open(os.path.join(d, name), "w") as fh:
                    json.dump({"score": score}, fh)
            scores = parity.visual_scores([os.path.join(d, "*.json")])
            self.assertEqual(sorted(s["score"] for s in scores), [80.0, 90.0])
            with self.assertRaises(parity.MatrixError):
                parity.visual_scores([os.path.join(d, "*.nothing")])


class ReviewNegation(unittest.TestCase):
    def rows(self, items):
        return [{"source": "s%d" % i, "url": "https://x/%d" % i, "date": None,
                 "rating": r, "text": t, "line": i} for i, (r, t) in enumerate(items)]

    def test_praise_is_not_a_complaint_but_complaints_still_are(self):
        themes, req = reviews.load_themes()
        res = reviews.analyse(self.rows([
            (5, "No ads, no bugs, never crashes. Love it."),
            (1, "Crashes every time I open it."),
            (2, "I don't like the price at all."),
            (4, "Great app, but there are ads everywhere."),
        ]), themes, req)
        counts = {t["id"]: t["count"] for t in res["themes"]}
        self.assertEqual(counts.get("bugs"), 1)
        self.assertEqual(counts.get("ads"), 1)
        self.assertEqual(counts.get("pricing"), 1)

    def test_support_team_is_not_a_teams_request(self):
        themes, req = reviews.load_themes()
        res = reviews.analyse(self.rows([(1, "The support team never replied.")]),
                              themes, req)
        ids = {t["id"] for t in res["themes"]}
        self.assertIn("support", ids)
        self.assertNotIn("collaboration", ids)


class ImgdiffHeight(unittest.TestCase):
    def test_half_built_page_does_not_score_as_a_match(self):
        w, h, rows = page(h=360)
        half = (w, 180, [list(r) for r in rows[:180]])
        report, _ = imgdiff.compare((w, h, rows), half)
        self.assertGreater(report["unmatched_cells"], 0)
        self.assertLess(report["score"], 90)
        same, _ = imgdiff.compare((w, h, rows), (w, h, rows))
        self.assertEqual(same["score"], 100.0)
        self.assertEqual(same["unmatched_cells"], 0)


if __name__ == "__main__":
    unittest.main()
