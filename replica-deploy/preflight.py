#!/usr/bin/env python3
"""Preflight gate runner for replica-deploy. Standard library only.

Runs all automated replica-skill gates in one command before you deploy:
  1. Feature parity (must-have features complete in replica/features.csv)
  2. WCAG AA colour contrast (replica/tokens.json or replica/design/tokens.json)
  3. Rebrand sweep (zero leftover original names/domains/colours via replica/brand.json)
  4. Store listing lint (zero errors in replica/launch/listing.json or replica/listing.json)

Usage:
    python3 preflight.py .
    python3 preflight.py /path/to/clone --json
"""

import argparse
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILLS_ROOT = os.path.dirname(HERE)


def _load_tool(folder, name):
    path = os.path.join(SKILLS_ROOT, folder, name + ".py")
    spec = importlib.util.spec_from_file_location("replica_" + name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _first_existing(base, candidates):
    for rel in candidates:
        p = os.path.join(base, rel)
        if os.path.isfile(p):
            return p
    return None


def run_preflight(root):
    root = os.path.abspath(root)
    rep_dir = os.path.join(root, "replica")
    checks = []

    # 1. Feature Parity
    features_path = _first_existing(rep_dir, ["features.csv"])
    if features_path:
        parity = _load_tool("replica-diff", "parity")
        try:
            res = parity.score(parity.load(features_path))
            passed = (res["must_have_done"] == res["must_have_total"]
                      and len(res["problems"]) == 0)
            detail = ("score %.1f%%, must-haves %d/%d"
                      % (res["feature_score"], res["must_have_done"], res["must_have_total"]))
            checks.append({"gate": "parity", "passed": passed, "detail": detail})
        except Exception as exc:
            checks.append({"gate": "parity", "passed": False, "detail": str(exc)})

    # 2. Design Contrast
    tokens_path = _first_existing(rep_dir, ["tokens.json", os.path.join("design", "tokens.json")])
    if tokens_path:
        contrast = _load_tool("replica-design", "contrast")
        try:
            with open(tokens_path, encoding="utf-8-sig") as fh:
                tokens = json.load(fh)
            cols = contrast.colours(tokens)
            pairs = tokens.get("pairs") or contrast.default_pairs(cols)
            rows = contrast.check(cols, pairs)
            fails = sum(1 for r in rows if "error" in r or not r["aa"])
            checks.append({
                "gate": "contrast",
                "passed": len(rows) > 0 and fails == 0,
                "detail": "%d pairs checked, %d failing AA" % (len(rows), fails),
            })
        except Exception as exc:
            checks.append({"gate": "contrast", "passed": False, "detail": str(exc)})

    # 3. Rebrand Sweep
    brand_path = _first_existing(rep_dir, ["brand.json"])
    if brand_path:
        sweep_mod = _load_tool("replica-brand", "sweep")
        try:
            with open(brand_path, encoding="utf-8-sig") as fh:
                cfg = json.load(fh)
            avoid = cfg.get("avoid", [])
            domains = cfg.get("domains", [])
            colors = cfg.get("colors", [])
            hits = sweep_mod.sweep(root, avoid=avoid, domains=domains, colors=colors)
            checks.append({
                "gate": "sweep",
                "passed": len(hits) == 0,
                "detail": "%d leftover brand hits" % len(hits),
            })
        except Exception as exc:
            checks.append({"gate": "sweep", "passed": False, "detail": str(exc)})

    # 4. Store Listing Lint
    listing_path = _first_existing(
        rep_dir, [os.path.join("launch", "listing.json"), "listing.json"]
    )
    if listing_path:
        listing_mod = _load_tool("replica-launch", "listing")
        try:
            with open(listing_path, encoding="utf-8-sig") as fh:
                listing_data = json.load(fh)
            issues = listing_mod.lint(listing_data)
            errs = sum(1 for i in issues if i["level"] == "error")
            warns = len(issues) - errs
            checks.append({
                "gate": "listing",
                "passed": errs == 0,
                "detail": "%d errors, %d warnings" % (errs, warns),
            })
        except Exception as exc:
            checks.append({"gate": "listing", "passed": False, "detail": str(exc)})

    return {
        "root": root,
        "passed": len(checks) > 0 and all(c["passed"] for c in checks),
        "checks": checks,
    }


def render(report):
    if not report["checks"]:
        return "No replica/ artifacts found to check."
    out = ["Preflight summary:"]
    for c in report["checks"]:
        mark = "PASS" if c["passed"] else "FAIL"
        out.append("  %-6s %-10s %s" % (mark, c["gate"], c["detail"]))
    out.append("")
    out.append("Result: %s" % ("READY TO DEPLOY" if report["passed"] else "BLOCKED"))
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("root", nargs="?", default=".", help="project root containing replica/")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    report = run_preflight(args.root)
    if not report["checks"]:
        print("preflight: no replica/ artifacts found in %s" % args.root, file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(render(report))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
