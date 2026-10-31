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

Thresholds (WCAG 2.2): normal text AA 4.5, AAA 7. Large text AA 3, AAA 4.5.
UI parts and focus rings ("ui" as the third item) need 3.
Exit code 1 when any pair fails AA, so it can gate a build.
"""

import argparse
import json
import re
import sys

HEX = re.compile(r"^#?([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
NEEDS = {"normal": (4.5, 7.0), "large": (3.0, 4.5), "ui": (3.0, 3.0)}


def parse_hex(value):
    m = HEX.match(value.strip())
    if not m:
        raise ValueError("not a hex colour: %r" % value)
    h = m.group(1)
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def luminance(rgb):
    def chan(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (chan(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(fg, bg):
    la, lb = luminance(parse_hex(fg)), luminance(parse_hex(bg))
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
    elif isinstance(obj, str) and HEX.match(obj.strip()):
        out[prefix] = obj.strip()
    return out


def colours(tokens):
    src = tokens.get("color", tokens.get("colors", tokens.get("colour", {})))
    return {k: v for k, v in flatten(src).items() if HEX.match(v)}


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
            rows.append({"fg": fg, "bg": bg, "size": size, "error": "unknown token"})
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
    ap.add_argument("args", nargs="+", help="tokens.json, or two hex colours")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        if len(a.args) == 2 and all(HEX.match(x) for x in a.args):
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
