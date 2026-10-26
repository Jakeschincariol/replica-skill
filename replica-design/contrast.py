#!/usr/bin/env python3
"""Contrast check for replica-design tokens. Standard library only.

Every text colour in your token file, checked against the backgrounds it sits
on, with the WCAG 2 contrast ratio. Run it after every palette change,
including the rebrand, because a new palette is where contrast breaks.

    python3 contrast.py replica/design/tokens.json
    python3 contrast.py tokens.json --json
    python3 contrast.py "#6b7280" "#ffffff"        # one pair

Pairs come from the token file's "pairs" list: [["text", "bg"], ...], or
[["text-muted", "surface", "large"], ...] for text 24px and up (or 18.66px
bold), which only needs 3:1. Without a pairs list, every colour whose name
has text, fg or on- in it is checked against every colour whose name has bg,
background or surface in it.

Colours can be #rgb, #rrggbb, with alpha (#rrggbbaa, #rgba), or rgb() / rgba().
A translucent text colour is blended onto its background before measuring,
the way it renders; a translucent background is blended onto white.

Thresholds (WCAG 2.2): normal text AA 4.5, AAA 7. Large text AA 3, AAA 4.5.
UI parts and focus rings ("ui" as the third item) need 3.
Exit code 1 when any pair fails AA, so it can gate a build.
"""

import argparse
import json
import re
import sys

HEX = re.compile(r"^#?([0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")
RGB = re.compile(r"^rgba?\(\s*(\d{1,3})\s*[, ]\s*(\d{1,3})\s*[, ]\s*(\d{1,3})"
                 r"\s*(?:[,/]\s*([\d.]+)(%?))?\s*\)$", re.I)
NEEDS = {"normal": (4.5, 7.0), "large": (3.0, 4.5), "ui": (3.0, 3.0)}


def parse_colour(value):
    """#rgb, #rgba, #rrggbb, #rrggbbaa, rgb() or rgba() -> (r, g, b, alpha 0-1)."""
    value = value.strip()
    m = HEX.match(value)
    if m:
        h = m.group(1)
        if len(h) in (3, 4):
            h = "".join(c * 2 for c in h)
        a = int(h[6:8], 16) / 255.0 if len(h) == 8 else 1.0
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (a,)
    m = RGB.match(value)
    if m and all(int(v) <= 255 for v in m.groups()[:3]):
        a = 1.0
        if m.group(4):
            a = float(m.group(4)) / (100.0 if m.group(5) else 1.0)
        return tuple(int(v) for v in m.groups()[:3]) + (min(1.0, a),)
    raise ValueError("not a colour: %r" % value)


def is_colour(value):
    try:
        parse_colour(value)
        return True
    except ValueError:
        return False


def parse_hex(value):
    return parse_colour(value)[:3]


def over(fg, bg):
    """Composite a translucent colour onto an opaque one, the way it renders."""
    a = fg[3]
    return tuple(fg[i] * a + bg[i] * (1 - a) for i in range(3))


def luminance(rgb):
    def chan(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (chan(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(fg, bg):
    # a translucent background sits on the page (white); translucent text on its background
    b = over(parse_colour(bg), (255, 255, 255))
    f = over(parse_colour(fg), b)
    la, lb = luminance(f), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def flatten(obj, prefix=""):
    """{"color": {"text": {"muted": "#..."}}} -> {"text-muted": "#..."}."""
    out = {}
    if isinstance(obj, dict):
        if "value" in obj and isinstance(obj["value"], str):
            out[prefix] = obj["value"]
            return out
        if "$value" in obj and isinstance(obj["$value"], str):
            out[prefix] = obj["$value"]
            return out
        for k, v in obj.items():
            if k.startswith("$") or k.startswith("_"):
                continue
            key = "%s-%s" % (prefix, k) if prefix else k
            out.update(flatten(v, key))
    elif isinstance(obj, str) and is_colour(obj):
        out[prefix] = obj.strip()
    return out


def colours(tokens):
    src = tokens.get("color", tokens.get("colors", tokens.get("colour", {})))
    return {k: v for k, v in flatten(src).items() if is_colour(v)}


def default_pairs(cols):
    fg = [k for k in cols if re.search(r"(^|-)(text|fg|on)(-|$)", k)]
    bg = [k for k in cols if re.search(r"(^|-)(bg|background|surface)(-|$)", k)]
    return [[f, b] for f in fg for b in bg]


def check(cols, pairs):
    rows = []
    for p in pairs:
        if len(p) < 2:
            continue
        fg, bg = p[0], p[1]
        size = p[2] if len(p) > 2 else "normal"
        if size not in NEEDS:
            size = "normal"
        if fg not in cols or bg not in cols:
            rows.append({"fg": fg, "bg": bg, "size": size,
                         "error": "unknown token, or its value is not a hex or rgb() colour"})
            continue
        r = ratio(cols[fg], cols[bg])
        aa, aaa = NEEDS[size]
        rows.append({"fg": fg, "bg": bg, "size": size, "ratio": round(r, 2),
                     "aa": r >= aa, "aaa": r >= aaa,
                     "fg_hex": cols[fg], "bg_hex": cols[bg]})
    return rows


def render(rows):
    out = []
    for r in rows:
        if "error" in r:
            out.append("  ??    %-24s on %-20s %s" % (r["fg"], r["bg"], r["error"]))
            continue
        if r["size"] == "ui":
            grade = "PASS" if r["aa"] else "FAIL"
        else:
            grade = "AAA" if r["aaa"] else ("AA" if r["aa"] else "FAIL")
        out.append("  %-5s %5.2f:1  %-24s on %-20s %s" % (
            grade, r["ratio"], r["fg"], r["bg"], "" if r["size"] == "normal" else r["size"]))
    fails = sum(1 for r in rows if "error" in r or not r["aa"])
    out.append("")
    out.append("  %d pairs, %d failing AA" % (len(rows), fails))
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("args", nargs="+", help="tokens.json, or two colours (hex or rgb())")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        if len(a.args) == 2 and all(is_colour(x) for x in a.args):
            cols = {"fg": a.args[0], "bg": a.args[1]}
            pairs = [["fg", "bg"]]
        else:
            with open(a.args[0], encoding="utf-8") as fh:
                tokens = json.load(fh)
            cols = colours(tokens)
            pairs = tokens.get("pairs") or default_pairs(cols)
    except (OSError, ValueError) as exc:
        print("contrast: %s" % exc, file=sys.stderr)
        return 2
    if not pairs:
        print("contrast: no pairs to check. Add a \"pairs\" list to the token file.",
              file=sys.stderr)
        return 2
    rows = check(cols, pairs)
    print(json.dumps(rows, indent=2) if a.json else render(rows))
    return 1 if any("error" in r or not r["aa"] for r in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
