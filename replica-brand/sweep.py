#!/usr/bin/env python3
"""Rebrand sweep for replica-brand and replica-deploy. Standard library only.

Searches your clone's codebase for anything that still belongs to the original
app: its name, its domain, its brand colours. Run it before every launch. It
exits 1 if it finds anything, so it can block a deploy.

    python3 sweep.py . --avoid "Calendly"
    python3 sweep.py . --avoid "Calendly,Calendly LLC" --domains calendly.com \\
        --colors "#006bff,#0ae8f0"
    python3 sweep.py . --config replica/brand.json --json

--config reads {"avoid": [...], "domains": [...], "colors": [...]}, the same
"avoid" list listing.py uses.

Names match case-insensitively anywhere, including inside identifiers
(CalendlyButton, calendly_sync), because those ship too. Colours match in any
case and in every form a codebase writes them: #06f, #0066ff, with alpha
(#0066ffcc, #06fc), Android ARGB (#ff0066ff, 0xFF0066FF, Color(0xFF0066FF)) and
rgb(0, 102, 255) / rgba(...). File and folder names are checked as well as
contents.

Skipped: .git, node_modules, build output folders, lock files, binary files,
and the replica/ planning folder (where the original's name belongs). Pass
--include-replica to check that too, for example if it sits inside public/.
"""

import argparse
import json
import os
import re
import sys

SKIP_DIRS = {".git", "node_modules", ".next", ".nuxt", ".svelte-kit", "dist", "build",
             "out", ".vercel", ".turbo", ".cache", "coverage", "__pycache__", ".venv",
             "venv", "Pods", ".expo", "DerivedData", ".gradle"}
SKIP_FILES = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lockb",
              "Podfile.lock", "Cargo.lock", "poetry.lock"}
BINARY_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".icns", ".pdf", ".zip",
              ".gz", ".woff", ".woff2", ".ttf", ".otf", ".eot", ".mp4", ".mov", ".mp3",
              ".wav", ".avif", ".heic", ".psd", ".sketch", ".fig", ".jar", ".so", ".dylib"}
HEX = re.compile(r"#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{4}|[0-9a-fA-F]{3})"
                 r"(?![0-9a-zA-Z])")
ARGB_INT = re.compile(r"\b0x([0-9a-fA-F]{8}|[0-9a-fA-F]{6})\b")
RGB_FN = re.compile(r"\brgba?\(\s*(\d{1,3})\s*[, ]\s*(\d{1,3})\s*[, ]\s*(\d{1,3})", re.I)


def norm_hex(h):
    h = h.strip().lower().lstrip("#")
    if len(h) in (3, 4):
        h = "".join(c * 2 for c in h)
    return "#" + h


def colour_keys(token):
    """The #rrggbb values a colour written in code could mean.

    8 digits is ambiguous: CSS writes #RRGGBBAA, Android writes #AARRGGBB, so
    both readings are returned. Alpha is ignored: the brand colour at 80% is
    still the brand colour.
    """
    h = norm_hex(token)[1:]
    if len(h) == 6:
        return {"#" + h}
    if len(h) == 8:
        return {"#" + h[:6], "#" + h[2:]}
    return set()


def colours_in(line):
    """Yield (as written, set of #rrggbb it could be) for every colour on a line."""
    for m in HEX.finditer(line):
        yield m.group(0), colour_keys(m.group(0))
    for m in ARGB_INT.finditer(line):
        h = m.group(1).lower()
        yield m.group(0), {"#" + (h[2:] if len(h) == 8 else h)}
    for m in RGB_FN.finditer(line):
        rgb = [int(v) for v in m.groups()]
        if all(v <= 255 for v in rgb):
            yield m.group(0), {"#%02x%02x%02x" % tuple(rgb)}


def build_patterns(avoid, domains):
    pats = []
    for name in avoid:
        name = name.strip()
        if not name:
            continue
        # "Acuity Scheduling" also matches AcuityScheduling and acuity-scheduling
        parts = [re.escape(p) for p in re.split(r"[\s_-]+", name) if p]
        pats.append(("name", name, re.compile(r"[\s_-]?".join(parts), re.I)))
    for d in domains:
        d = d.strip().lower()
        if d:
            pats.append(("domain", d, re.compile(re.escape(d), re.I)))
    return pats


def is_binary(path):
    if os.path.splitext(path)[1].lower() in BINARY_EXT:
        return True
    try:
        with open(path, "rb") as fh:
            return b"\0" in fh.read(4096)
    except OSError:
        return True


def sweep(root, avoid=(), domains=(), colors=(), include_replica=False, max_size=2_000_000):
    pats = build_patterns(avoid, domains)
    cols = set()
    for c in colors:
        c = c.strip()
        if not c.startswith("#"):
            c = "#" + c
        if not HEX.fullmatch(c):
            raise ValueError("not a hex colour: %r" % c)
        cols.add(norm_hex(c)[:7])  # the brand list is CSS: drop any alpha
    hits = []
    root = os.path.abspath(root)
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)
        keep = []
        for d in dirnames:
            if d in SKIP_DIRS:
                continue
            if d == "replica" and rel_dir == "." and not include_replica:
                continue
            keep.append(d)
        dirnames[:] = sorted(keep)
        for d in dirnames:
            for kind, label, rx in pats:
                if kind == "name" and rx.search(d):
                    hits.append({"file": os.path.normpath(os.path.join(rel_dir, d)) + "/",
                                 "line": 0, "kind": "path", "match": label,
                                 "text": "folder name"})
        for fn in sorted(filenames):
            if fn in SKIP_FILES:
                continue
            path = os.path.join(dirpath, fn)
            rel = os.path.normpath(os.path.join(rel_dir, fn))
            for kind, label, rx in pats:
                if kind == "name" and rx.search(fn):
                    hits.append({"file": rel, "line": 0, "kind": "path", "match": label,
                                 "text": "file name"})
            try:
                if os.path.getsize(path) > max_size or is_binary(path):
                    continue
                with open(path, encoding="utf-8", errors="replace") as fh:
                    lines = fh.readlines()
            except OSError:
                continue
            for i, line in enumerate(lines, 1):
                for kind, label, rx in pats:
                    if rx.search(line):
                        hits.append({"file": rel, "line": i, "kind": kind, "match": label,
                                     "text": line.strip()[:160]})
                if cols:
                    for written, keys in colours_in(line):
                        found = keys & cols
                        if found:
                            hits.append({"file": rel, "line": i, "kind": "color",
                                         "match": sorted(found)[0],
                                         "text": line.strip()[:160]})
    return hits


def render(hits):
    if not hits:
        return "Clean. Nothing of the original's name, domain or colours found."
    out = []
    by_kind = {}
    for h in hits:
        by_kind.setdefault(h["kind"], 0)
        by_kind[h["kind"]] += 1
        loc = h["file"] if not h["line"] else "%s:%d" % (h["file"], h["line"])
        out.append("%-7s %-18s %s  %s" % (h["kind"], h["match"][:18], loc, h["text"]))
    out.append("")
    out.append("%d hits (%s). Replace every one before you launch."
               % (len(hits), ", ".join("%s %d" % kv for kv in sorted(by_kind.items()))))
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--avoid", default="", help="comma-separated names")
    ap.add_argument("--domains", default="", help="comma-separated domains")
    ap.add_argument("--colors", default="", help="comma-separated hex colours")
    ap.add_argument("--config", help="JSON with avoid / domains / colors lists")
    ap.add_argument("--include-replica", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    avoid = [x for x in args.avoid.split(",") if x.strip()]
    domains = [x for x in args.domains.split(",") if x.strip()]
    colors = [x for x in args.colors.split(",") if x.strip()]
    if args.config:
        try:
            with open(args.config, encoding="utf-8") as fh:
                cfg = json.load(fh)
        except (OSError, ValueError) as exc:
            print("sweep: %s" % exc, file=sys.stderr)
            return 2
        avoid += cfg.get("avoid", [])
        domains += cfg.get("domains", [])
        colors += cfg.get("colors", [])
    if not (avoid or domains or colors):
        print("sweep: nothing to look for. Pass --avoid with the original app's name.",
              file=sys.stderr)
        return 2
    try:
        hits = sweep(args.root, avoid, domains, colors, args.include_replica)
    except ValueError as exc:
        # a typo in the colour list must not turn into a silent "Clean"
        print("sweep: %s" % exc, file=sys.stderr)
        return 2
    print(json.dumps(hits, indent=2) if args.json else render(hits))
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
