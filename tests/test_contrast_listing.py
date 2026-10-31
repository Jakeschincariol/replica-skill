import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from _load import load, ROOT

contrast = load("replica-design", "contrast")
listing = load("replica-launch", "listing")


class Contrast(unittest.TestCase):
    def test_known_ratios(self):
        self.assertAlmostEqual(contrast.ratio("#000", "#fff"), 21.0, places=2)
        self.assertAlmostEqual(contrast.ratio("#ffffff", "#ffffff"), 1.0, places=2)
        # #767676 on white is the classic just-passes-AA grey
        self.assertGreaterEqual(contrast.ratio("#767676", "#ffffff"), 4.5)
        self.assertLess(contrast.ratio("#777777", "#ffffff"), 4.5)

    def test_nested_tokens_flatten(self):
        cols = contrast.colours({"color": {"text": {"default": "#111", "muted": {"value": "#999"}},
                                           "bg": "#fff", "$type": "color"}})
        self.assertEqual(cols, {"text-default": "#111", "text-muted": "#999", "bg": "#fff"})

    def test_default_pairs_and_large_text(self):
        cols = {"text": "#111111", "text-muted": "#949494", "bg": "#ffffff", "accent": "#2563eb"}
        pairs = contrast.default_pairs(cols)
        self.assertIn(["text", "bg"], pairs)
        self.assertNotIn(["accent", "bg"], pairs)
        rows = contrast.check(cols, [["text-muted", "bg"], ["text-muted", "bg", "large"]])
        self.assertFalse(rows[0]["aa"])
        self.assertTrue(rows[1]["aa"])

    def test_shipped_tokens_template_passes(self):
        path = os.path.join(ROOT, "skills", "replica-design", "tokens.json")
        with redirect_stdout(io.StringIO()):
            self.assertEqual(contrast.main([path]), 0)

    def test_cli_pair_failure_exit_code(self):
        with redirect_stdout(io.StringIO()):
            self.assertEqual(contrast.main(["#aaaaaa", "#ffffff"]), 1)
            self.assertEqual(contrast.main(["#222222", "#ffffff"]), 0)


class Listing(unittest.TestCase):
    def good(self):
        return {
            "avoid": ["Calendly"],
            "app_store": {
                "name": "Slotwise: Booking Links",
                "subtitle": "Share a link, get booked",
                "promotional_text": "Text reminders are here.",
                "description": "Share one link. Clients pick a time that works.",
                "keywords": "scheduler,appointment,calendar,meetings,reminders",
                "whats_new": "Text reminders.",
            },
            "google_play": {
                "title": "Slotwise: Booking Links",
                "short_description": "Share one link and let clients book a time.",
                "full_description": "Share one link. Clients pick a time that works.",
            },
        }

    def test_clean_listing_has_no_errors(self):
        issues = listing.lint(self.good())
        self.assertEqual([i for i in issues if i["level"] == "error"], [])

    def test_over_limit(self):
        data = self.good()
        data["app_store"]["subtitle"] = "x" * 31
        issues = listing.lint(data)
        self.assertTrue(any(i["field"] == "subtitle" and "1 over" in i["message"]
                            for i in issues))

    def test_original_app_name_is_an_error_anywhere(self):
        data = self.good()
        data["google_play"]["full_description"] = "A better calendly alternative."
        issues = listing.lint(data)
        self.assertTrue(any(i["level"] == "error" and "Calendly" in i["message"]
                            for i in issues))

    def test_claims_and_keyword_waste(self):
        data = self.good()
        data["google_play"]["title"] = "#1 Best Booking App"
        data["app_store"]["keywords"] = "booking, links,calendar,calendar"
        issues = listing.lint(data)
        msgs = " | ".join(i["message"] for i in issues)
        self.assertIn("ranking or price claim", msgs)
        self.assertIn("spaces after commas", msgs)
        self.assertIn("repeated: calendar", msgs)
        self.assertIn("already in the name", msgs)

    def test_emoji_counts_as_one(self):
        self.assertEqual(listing.length("a\U0001F468‍\U0001F4BBb"), 3)
        self.assertEqual(listing.length("café"), 4)

    def test_shipped_example_is_clean(self):
        path = os.path.join(ROOT, "skills", "replica-launch", "listing.example.json")
        with redirect_stdout(io.StringIO()):
            self.assertEqual(listing.main([path]), 0)

    def test_cli_avoid_flag(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "l.json")
            data = self.good()
            data.pop("avoid")
            data["app_store"]["description"] += " Like Acuity, but simple."
            with open(p, "w") as fh:
                json.dump(data, fh)
            with redirect_stdout(io.StringIO()):
                self.assertEqual(listing.main([p]), 0)
                self.assertEqual(listing.main([p, "--avoid", "Acuity"]), 1)


if __name__ == "__main__":
    unittest.main()
