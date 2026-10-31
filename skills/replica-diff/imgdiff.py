#!/usr/bin/env python3
"""Screenshot diff for replica-diff. Standard library only.

Compares a screenshot of the original app with the same screen in your clone
and tells you how close the layout is and where it differs.

    python3 imgdiff.py original.png clone.png
    python3 imgdiff.py original.png clone.png --out diff.png --json
    python3 imgdiff.py original.png clone.png --mode pixel --fail-under 95

Two modes:

  layout (default)  Compares structure, not colour. Both images become edge
                    maps, cut into a grid, and each cell's edge density is
                    compared. Your rebrand changes every colour on purpose, so
                    colour is ignored here. Only cells with something in them
                    (in either image) are scored, so empty margins do not pad
                    the number. This is the parity number.
  pixel             Exact pixel comparison with a tolerance. Use it for your
                    own regressions (clone today vs clone yesterday), not to
                    chase the original's pixels.

Both images are scaled to the same width (--width, default 480) and compared
over the shared height. A height difference is reported, not hidden.

Reads 8 and 16 bit PNGs (grey, RGB, palette, with or without alpha). Interlaced
PNGs are refused with a message: re-save the screenshot without interlacing.
"""

import argparse
import json
import math
import struct
import sys
import zlib

SIG = b"\x89PNG\r\n\x1a\n"


class PngError(Exception):
    pass


# ----------------------------------------------------------------- PNG reading

def _paeth(a, b, c):
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def _unfilter(raw, height, stride, bpp):
    rows = []
    prev = bytearray(stride)
    pos = 0
    for _ in range(height):
        if pos + 1 + stride > len(raw):
            raise PngError("image data is truncated")
        ftype = raw[pos]
        line = bytearray(raw[pos + 1:pos + 1 + stride])
        pos += 1 + stride
        if ftype == 1:
            for i in range(bpp, stride):
                line[i] = (line[i] + line[i - bpp]) & 0xFF
        elif ftype == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 0xFF
        elif ftype == 3:
            for i in range(stride):
                left = line[i - bpp] if i >= bpp else 0
                line[i] = (line[i] + ((left + prev[i]) >> 1)) & 0xFF
        elif ftype == 4:
            for i in range(stride):
                left = line[i - bpp] if i >= bpp else 0
                upleft = prev[i - bpp] if i >= bpp else 0
                line[i] = (line[i] + _paeth(left, prev[i], upleft)) & 0xFF
        elif ftype != 0:
            raise PngError("unknown filter type %d" % ftype)
        rows.append(line)
        prev = line
    return rows


def _samples(line, width, channels, depth):
    """Unpack one unfiltered scanline into a flat list of 8 bit samples."""
    n = width * channels
    if depth == 8:
        return list(line[:n])
    if depth == 16:
        return [line[2 * i] for i in range(n)]
    out = []
    per_byte = 8 // depth
    mask = (1 << depth) - 1
    for byte in line:
        for k in range(per_byte):
            shift = 8 - depth * (k + 1)
            out.append((byte >> shift) & mask)
            if len(out) == n:
                return out
    return out


def read_png(path):
    """Return (width, height, rows). rows[y][x] is an (r, g, b) tuple.

    Alpha is composited over white, the way a screenshot of a page renders.
    """
    with open(path, "rb") as fh:
        data = fh.read()
    if data[:8] != SIG:
        raise PngError("%s is not a PNG" % path)
    pos = 8
    ihdr = None
    plte = None
    trns = None
    idat = []
    while pos + 8 <= len(data):
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        ctype = data[pos + 4:pos + 8]
        chunk = data[pos + 8:pos + 8 + length]
        pos += 12 + length
        if ctype == b"IHDR":
            ihdr = struct.unpack(">IIBBBBB", chunk)
        elif ctype == b"PLTE":
            plte = [tuple(chunk[i:i + 3]) for i in range(0, len(chunk), 3)]
        elif ctype == b"tRNS":
            trns = chunk
        elif ctype == b"IDAT":
            idat.append(chunk)
        elif ctype == b"IEND":
            break
    if ihdr is None:
        raise PngError("%s has no IHDR chunk" % path)
    width, height, depth, color, _comp, _filt, interlace = ihdr
    if interlace:
        raise PngError("%s is interlaced. Re-save it without interlacing "
                       "(on a Mac: sips -s format png in.png --out out.png)" % path)
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}.get(color)
    if channels is None:
        raise PngError("unsupported PNG colour type %d" % color)
    if depth not in (1, 2, 4, 8, 16):
        raise PngError("unsupported bit depth %d" % depth)
    if color == 3 and plte is None:
        raise PngError("palette PNG without a palette")
    bits = depth * channels
    bpp = max(1, bits // 8)
    stride = (width * bits + 7) // 8
    raw = zlib.decompress(b"".join(idat))
    lines = _unfilter(raw, height, stride, bpp)

    scale = 255 // ((1 << depth) - 1) if depth < 8 else 1
    alpha_pal = list(trns) if (color == 3 and trns) else []
    rows = []
    for line in lines:
        s = _samples(line, width, channels, depth)
        row = []
        if color == 0:
            for v in s:
                g = v * scale
                row.append((g, g, g))
        elif color == 2:
            for i in range(0, len(s), 3):
                row.append((s[i], s[i + 1], s[i + 2]))
        elif color == 3:
            for idx in s:
                r, g, b = plte[idx] if idx < len(plte) else (0, 0, 0)
                a = alpha_pal[idx] if idx < len(alpha_pal) else 255
                row.append(_over_white(r, g, b, a))
        elif color == 4:
            for i in range(0, len(s), 2):
                g = s[i]
                row.append(_over_white(g, g, g, s[i + 1]))
        else:
            for i in range(0, len(s), 4):
                row.append(_over_white(s[i], s[i + 1], s[i + 2], s[i + 3]))
        rows.append(row)
    return width, height, rows


def _over_white(r, g, b, a):
    if a == 255:
        return (r, g, b)
    inv = 255 - a
    return ((r * a + 255 * inv) // 255, (g * a + 255 * inv) // 255,
            (b * a + 255 * inv) // 255)


# ----------------------------------------------------------------- PNG writing

def write_png(path, width, height, rows):
    """Write 8 bit RGB. rows[y][x] is an (r, g, b) tuple."""
    raw = bytearray()
    for row in rows:
        raw.append(0)
        for r, g, b in row:
            raw.extend((r, g, b))

    def chunk(kind, body):
        crc = zlib.crc32(kind + body) & 0xFFFFFFFF
        return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", crc)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    with open(path, "wb") as fh:
        fh.write(SIG + chunk(b"IHDR", ihdr) +
                 chunk(b"IDAT", zlib.compress(bytes(raw), 6)) +
                 chunk(b"IEND", b""))


# ------------------------------------------------------------------- comparing

def resize(rows, width, height, new_w, new_h):
    """Nearest-neighbour resize. Good enough for structure, and fast."""
    xs = [min(width - 1, int(x * width / new_w)) for x in range(new_w)]
    ys = [min(height - 1, int(y * height / new_h)) for y in range(new_h)]
    return [[rows[y][x] for x in xs] for y in ys]


def to_width(img, target):
    w, h, rows = img
    if w == target:
        return w, h, rows
    new_h = max(1, int(round(h * target / float(w))))
    return target, new_h, resize(rows, w, h, target, new_h)


def gray(rows):
    return [[(299 * r + 587 * g + 114 * b) // 1000 for r, g, b in row] for row in rows]


def edges(g, threshold):
    h = len(g)
    w = len(g[0]) if h else 0
    out = []
    for y in range(h):
        row = g[y]
        below = g[y + 1] if y + 1 < h else row
        e = []
        for x in range(w):
            right = row[x + 1] if x + 1 < w else row[x]
            e.append(1 if abs(right - row[x]) + abs(below[x] - row[x]) > threshold else 0)
        out.append(e)
    return out


def _regions(flags, n_rows, n_cols):
    """Group flagged grid cells into rectangles (4-connected)."""
    seen = set()
    regions = []
    for r in range(n_rows):
        for c in range(n_cols):
            if not flags[r][c] or (r, c) in seen:
                continue
            stack = [(r, c)]
            seen.add((r, c))
            cells = []
            while stack:
                cr, cc = stack.pop()
                cells.append((cr, cc))
                for nr, nc in ((cr + 1, cc), (cr - 1, cc), (cr, cc + 1), (cr, cc - 1)):
                    if 0 <= nr < n_rows and 0 <= nc < n_cols and flags[nr][nc] \
                            and (nr, nc) not in seen:
                        seen.add((nr, nc))
                        stack.append((nr, nc))
            rs = [x[0] for x in cells]
            cs = [x[1] for x in cells]
            regions.append((min(rs), min(cs), max(rs), max(cs), len(cells)))
    regions.sort(key=lambda t: -t[4])
    return regions


def compare(img_a, img_b, mode="layout", width=480, cols=12, tolerance=24,
            edge_threshold=40):
    """Compare two decoded images. Returns (report dict, diff rows)."""
    wa, ha, _ = img_a
    wb, hb, _ = img_b
    target = min(width, wa, wb)
    a = to_width(img_a, target)
    b = to_width(img_b, target)
    w = target
    h = min(a[1], b[1])
    ra = a[2][:h]
    rb = b[2][:h]
    height_delta = (b[1] - a[1]) / float(a[1]) * 100.0 if a[1] else 0.0
    to_orig = wa / float(w)

    ga = gray(ra)
    dim = [[(200 + v // 5,) * 3 for v in row] for row in ga]
    report = {
        "mode": mode,
        "original": {"width": wa, "height": ha},
        "clone": {"width": wb, "height": hb},
        "compared_at": {"width": w, "height": h},
        "height_delta_pct": round(height_delta, 1),
    }

    if mode == "pixel":
        changed = 0
        flags_px = []
        for y in range(h):
            fr = []
            for x in range(w):
                pa, pb = ra[y][x], rb[y][x]
                d = max(abs(pa[0] - pb[0]), abs(pa[1] - pb[1]), abs(pa[2] - pb[2]))
                hit = d > tolerance
                fr.append(hit)
                if hit:
                    changed += 1
                    dim[y][x] = (220, 30, 30)
            flags_px.append(fr)
        total = w * h or 1
        score = 100.0 * (1 - changed / float(total))
        report["changed_pixels"] = changed
        # Summarise pixel hits as grid regions so the report stays readable.
        cell = max(1, w // cols)
        n_rows = int(math.ceil(h / float(cell)))
        flags = [[False] * cols for _ in range(n_rows)]
        for r in range(n_rows):
            for c in range(cols):
                hits = 0
                area = 0
                for y in range(r * cell, min(h, (r + 1) * cell)):
                    row = flags_px[y]
                    for x in range(c * cell, min(w, (c + 1) * cell)):
                        area += 1
                        hits += row[x]
                flags[r][c] = area > 0 and hits / float(area) > 0.02
    else:
        ea = edges(ga, edge_threshold)
        eb = edges(gray(rb), edge_threshold)
        cell = max(1, w // cols)
        n_rows = int(math.ceil(h / float(cell)))
        flags = [[False] * cols for _ in range(n_rows)]
        sims = []
        for r in range(n_rows):
            for c in range(cols):
                y0, y1 = r * cell, min(h, (r + 1) * cell)
                x0, x1 = c * cell, min(w, (c + 1) * cell)
                area = (y1 - y0) * (x1 - x0)
                if area <= 0:
                    continue
                da = sum(sum(ea[y][x0:x1]) for y in range(y0, y1)) / float(area)
                db = sum(sum(eb[y][x0:x1]) for y in range(y0, y1)) / float(area)
                top = max(da, db)
                if top < 0.01:
                    continue  # empty in both: says nothing about the layout
                sim = 1.0 - abs(da - db) / top
                sims.append(sim)
                if sim < 0.6:
                    flags[r][c] = True
                    for y in range(y0, y1):
                        for x in range(x0, x1):
                            g0 = dim[y][x][0]
                            dim[y][x] = (min(255, g0 + 30), g0 // 3, g0 // 3)
        score = 100.0 * sum(sims) / len(sims) if sims else 100.0

    regions = []
    for r0, c0, r1, c1, n in _regions(flags, len(flags), cols):
        x = int(c0 * cell * to_orig)
        y = int(r0 * cell * to_orig)
        regions.append({
            "x": x, "y": y,
            "w": min(wa - x, int((c1 - c0 + 1) * cell * to_orig)),
            "h": min(ha - y, int((r1 - r0 + 1) * cell * to_orig)),
            "cells": n,
            "where": _where(r0, c0, r1, c1, len(flags), cols),
        })
    report["score"] = round(score, 1)
    report["verdict"] = verdict(score)
    report["regions"] = regions
    return report, dim


def _where(r0, c0, r1, c1, n_rows, n_cols):
    mid_r = (r0 + r1) / 2.0 / max(1, n_rows - 1) if n_rows > 1 else 0.5
    mid_c = (c0 + c1) / 2.0 / max(1, n_cols - 1) if n_cols > 1 else 0.5
    v = "top" if mid_r < 0.34 else ("bottom" if mid_r > 0.66 else "middle")
    hz = "left" if mid_c < 0.34 else ("right" if mid_c > 0.66 else "centre")
    return "%s %s" % (v, hz)


def verdict(score):
    if score >= 90:
        return "matches"
    if score >= 75:
        return "close"
    if score >= 50:
        return "partly"
    return "different"


def render_text(report, a_name, b_name):
    lines = []
    bar = int(round(report["score"] / 100.0 * 24))
    lines.append("  %s vs %s" % (a_name, b_name))
    lines.append("  %-6s %s%s  %5.1f  %s" % (
        report["mode"].upper(), "#" * bar, "." * (24 - bar), report["score"],
        report["verdict"].upper()))
    hd = report["height_delta_pct"]
    if abs(hd) >= 5:
        lines.append("  height: the clone is %.0f%% %s than the original"
                     % (abs(hd), "taller" if hd > 0 else "shorter"))
    if report["regions"]:
        lines.append("  where they differ (original's pixels, biggest first):")
        for reg in report["regions"][:8]:
            lines.append("    %-14s x=%d y=%d w=%d h=%d" % (
                reg["where"], reg["x"], reg["y"], reg["w"], reg["h"]))
    else:
        lines.append("  no differing regions")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("original", help="screenshot of the original app (PNG)")
    ap.add_argument("clone", help="the same screen in your clone (PNG)")
    ap.add_argument("--mode", choices=("layout", "pixel"), default="layout")
    ap.add_argument("--width", type=int, default=480,
                    help="compare at this width (default 480)")
    ap.add_argument("--cols", type=int, default=12, help="grid columns (default 12)")
    ap.add_argument("--tolerance", type=int, default=24,
                    help="pixel mode: per-channel difference ignored (default 24)")
    ap.add_argument("--out", help="write a diff image here (PNG)")
    ap.add_argument("--json", action="store_true", help="print JSON instead of text")
    ap.add_argument("--fail-under", type=float,
                    help="exit 1 when the score is below this")
    args = ap.parse_args(argv)
    try:
        a = read_png(args.original)
        b = read_png(args.clone)
    except (PngError, OSError, zlib.error) as exc:
        print("imgdiff: %s" % exc, file=sys.stderr)
        return 2
    report, diff = compare(a, b, mode=args.mode, width=args.width, cols=args.cols,
                           tolerance=args.tolerance)
    report["files"] = {"original": args.original, "clone": args.clone}
    if args.out:
        write_png(args.out, report["compared_at"]["width"],
                  report["compared_at"]["height"], diff)
        report["diff_image"] = args.out
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(render_text(report, args.original, args.clone))
        if args.out:
            print("  diff image: %s" % args.out)
    if args.fail_under is not None and report["score"] < args.fail_under:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
