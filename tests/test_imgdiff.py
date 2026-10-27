import io
import json
import os
import struct
import tempfile
import unittest
import zlib
from contextlib import redirect_stdout, redirect_stderr

from _load import load

imgdiff = load("replica-diff", "imgdiff")


def canvas(w, h, colour=(255, 255, 255)):
    return [[colour for _ in range(w)] for _ in range(h)]


def rect(rows, x, y, w, h, colour):
    for yy in range(y, min(len(rows), y + h)):
        for xx in range(x, min(len(rows[0]), x + w)):
            rows[yy][xx] = colour


def page(w=240, h=360, header=(20, 20, 60), accent=(40, 110, 230), text=(30, 30, 30),
         button_y=250):
    """A fake app screen: header bar, lines of 'text', a button."""
    rows = canvas(w, h)
    rect(rows, 0, 0, w, 40, header)
    for i in range(6):
        rect(rows, 20, 70 + i * 22, w - 60 - (i % 3) * 30, 8, text)
    rect(rows, 20, button_y, 120, 36, accent)
    return (w, h, rows)


def encode(path, w, h, samples_rows, colour_type, depth=8, ftype=0, plte=None,
           trns=None, interlace=0):
    """Tiny PNG encoder for the tests, with a chosen filter on every row."""
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[colour_type]
    bpp = max(1, depth * channels // 8)
    raw = bytearray()
    prev = bytearray(w * bpp)
    for srow in samples_rows:
        line = bytearray(srow)
        out = bytearray()
        for i, v in enumerate(line):
            left = line[i - bpp] if i >= bpp else 0
            up = prev[i]
            ul = prev[i - bpp] if i >= bpp else 0
            if ftype == 0:
                f = v
            elif ftype == 1:
                f = v - left
            elif ftype == 2:
                f = v - up
            elif ftype == 3:
                f = v - ((left + up) >> 1)
            else:
                f = v - imgdiff._paeth(left, up, ul)
            out.append(f & 0xFF)
        raw.append(ftype)
        raw.extend(out)
        prev = line

    def chunk(kind, body):
        return (struct.pack(">I", len(body)) + kind + body +
                struct.pack(">I", zlib.crc32(kind + body) & 0xFFFFFFFF))

    data = imgdiff.SIG + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, depth,
                                                    colour_type, 0, 0, interlace))
    if plte:
        data += chunk(b"PLTE", bytes(c for rgb in plte for c in rgb))
    if trns:
        data += chunk(b"tRNS", bytes(trns))
    data += chunk(b"IDAT", zlib.compress(bytes(raw))) + chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(data)


class ReadWrite(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def p(self, name):
        return os.path.join(self.dir, name)

    def test_roundtrip_rgb(self):
        w, h, rows = page(40, 30)
        imgdiff.write_png(self.p("a.png"), w, h, rows)
        w2, h2, rows2 = imgdiff.read_png(self.p("a.png"))
        self.assertEqual((w2, h2), (w, h))
        self.assertEqual(rows2, rows)

    def test_every_filter_type_rgba(self):
        w, h = 7, 5
        src = [[(x * 30 % 256, y * 50 % 256, (x * y * 17) % 256, 255) for x in range(w)]
               for y in range(h)]
        flat = [[c for px in row for c in px] for row in src]
        for ftype in range(5):
            encode(self.p("f.png"), w, h, flat, 6, ftype=ftype)
            _, _, rows = imgdiff.read_png(self.p("f.png"))
            self.assertEqual(rows, [[px[:3] for px in row] for row in src],
                             "filter %d" % ftype)

    def test_alpha_composites_over_white(self):
        encode(self.p("a.png"), 1, 1, [[0, 0, 0, 0]], 6)
        self.assertEqual(imgdiff.read_png(self.p("a.png"))[2][0][0], (255, 255, 255))

    def test_grey_palette_and_16_bit(self):
        encode(self.p("g.png"), 3, 1, [[0, 128, 255]], 0)
        self.assertEqual(imgdiff.read_png(self.p("g.png"))[2][0],
                         [(0, 0, 0), (128, 128, 128), (255, 255, 255)])
        encode(self.p("p.png"), 4, 1, [[0b00011011]], 3, depth=2,
               plte=[(255, 0, 0), (0, 255, 0), (0, 0, 255), (9, 9, 9)])
        self.assertEqual(imgdiff.read_png(self.p("p.png"))[2][0],
                         [(255, 0, 0), (0, 255, 0), (0, 0, 255), (9, 9, 9)])
        encode(self.p("s.png"), 1, 1, [[0x12, 0x34, 0xAB, 0xCD, 0xEF, 0x01]], 2, depth=16)
        self.assertEqual(imgdiff.read_png(self.p("s.png"))[2][0][0], (0x12, 0xAB, 0xEF))

    def test_interlaced_is_refused_with_advice(self):
        encode(self.p("i.png"), 1, 1, [[1, 2, 3]], 2, interlace=1)
        with self.assertRaises(imgdiff.PngError) as ctx:
            imgdiff.read_png(self.p("i.png"))
        self.assertIn("interlac", str(ctx.exception))

    def test_not_a_png(self):
        with open(self.p("x.png"), "wb") as fh:
            fh.write(b"GIF89a")
        with self.assertRaises(imgdiff.PngError):
            imgdiff.read_png(self.p("x.png"))

    def test_truncated_ihdr_is_a_clean_error(self):
        imgdiff.write_png(self.p("good.png"), *page(4, 2))
        with open(self.p("good.png"), "rb") as fh:
            good = fh.read()
        # Cut mid-save: signature + IHDR header + 4 of its 13 data bytes.
        with open(self.p("cut.png"), "wb") as fh:
            fh.write(good[:20])
        with self.assertRaises(imgdiff.PngError) as ctx:
            imgdiff.read_png(self.p("cut.png"))
        self.assertIn("malformed IHDR", str(ctx.exception))
        # An IHDR chunk that declares a short length is the same error.
        ihdr = struct.pack(">IIBBBBB", 4, 2, 8, 2, 0, 0, 0)[:12]
        bad = (imgdiff.SIG + struct.pack(">I", 12) + b"IHDR" + ihdr +
               struct.pack(">I", zlib.crc32(b"IHDR" + ihdr) & 0xFFFFFFFF))
        with open(self.p("short.png"), "wb") as fh:
            fh.write(bad)
        with self.assertRaises(imgdiff.PngError) as ctx:
            imgdiff.read_png(self.p("short.png"))
        self.assertIn("malformed IHDR", str(ctx.exception))


class Compare(unittest.TestCase):
    def test_identical_is_100_with_no_regions(self):
        for mode in ("layout", "pixel"):
            rep, _ = imgdiff.compare(page(), page(), mode=mode)
            self.assertEqual(rep["score"], 100.0, mode)
            self.assertEqual(rep["regions"], [], mode)
            self.assertEqual(rep["verdict"], "matches")

    def test_rebrand_keeps_layout_score_but_not_pixel_score(self):
        original = page()
        rebranded = page(header=(120, 20, 40), accent=(20, 160, 90), text=(60, 50, 40))
        layout, _ = imgdiff.compare(original, rebranded, mode="layout")
        pixel, _ = imgdiff.compare(original, rebranded, mode="pixel")
        self.assertGreaterEqual(layout["score"], 90.0)
        self.assertLess(pixel["score"], layout["score"])
        self.assertTrue(pixel["regions"])

    def test_moved_button_is_found_where_it_is(self):
        rep, _ = imgdiff.compare(page(), page(button_y=310), mode="layout")
        self.assertLess(rep["score"], 100.0)
        self.assertTrue(rep["regions"])
        ys = [r["y"] for r in rep["regions"]]
        self.assertTrue(all(y >= 200 for y in ys), ys)
        self.assertTrue(all(r["x"] < 160 for r in rep["regions"]))
        self.assertTrue(any("bottom" in r["where"] or "middle" in r["where"]
                            for r in rep["regions"]))

    def test_blank_clone_is_different(self):
        w, h, _ = page()
        rep, _ = imgdiff.compare(page(), (w, h, canvas(w, h)), mode="layout")
        self.assertLess(rep["score"], 50.0)
        self.assertEqual(rep["verdict"], "different")

    def test_retina_screenshot_compares_at_same_width(self):
        w, h, rows = page(120, 180)
        big = imgdiff.resize(rows, w, h, 240, 360)
        rep, _ = imgdiff.compare((w, h, rows), (240, 360, big), mode="layout")
        self.assertGreaterEqual(rep["score"], 90.0)
        self.assertEqual(rep["compared_at"]["width"], 120)

    def test_height_difference_is_reported(self):
        w, h, rows = page()
        taller = rows + canvas(w, 90)
        rep, _ = imgdiff.compare((w, h, rows), (w, h + 90, taller))
        self.assertEqual(rep["height_delta_pct"], 25.0)
        self.assertIn("taller", imgdiff.render_text(rep, "a", "b"))


class Cli(unittest.TestCase):
    def test_json_out_and_fail_under(self):
        with tempfile.TemporaryDirectory() as d:
            a, b, out = (os.path.join(d, n) for n in ("a.png", "b.png", "diff.png"))
            imgdiff.write_png(a, *page())
            imgdiff.write_png(b, *page(button_y=310))
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = imgdiff.main([a, b, "--json", "--out", out])
            self.assertEqual(code, 0)
            rep = json.loads(buf.getvalue())
            self.assertIn("score", rep)
            self.assertEqual(rep["files"]["clone"], b)
            w, h, _ = imgdiff.read_png(out)
            self.assertEqual((w, h), (rep["compared_at"]["width"], rep["compared_at"]["height"]))
            with redirect_stdout(io.StringIO()):
                self.assertEqual(imgdiff.main([a, b, "--fail-under", "99.9"]), 1)
                self.assertEqual(imgdiff.main([a, a, "--fail-under", "99.9"]), 0)

    def test_bad_file_exits_2(self):
        with redirect_stderr(io.StringIO()):
            self.assertEqual(imgdiff.main(["/nope/a.png", "/nope/b.png"]), 2)

    def test_truncated_ihdr_exits_2_with_one_line(self):
        with tempfile.TemporaryDirectory() as d:
            good = os.path.join(d, "good.png")
            cut = os.path.join(d, "cut.png")
            imgdiff.write_png(good, *page())
            with open(good, "rb") as fh:
                data = fh.read()
            with open(cut, "wb") as fh:
                fh.write(data[:20])
            err = io.StringIO()
            with redirect_stderr(err):
                self.assertEqual(imgdiff.main([cut, good]), 2)
            self.assertEqual(err.getvalue(), "imgdiff: %s has a malformed IHDR chunk\n" % cut)


if __name__ == "__main__":
    unittest.main()
