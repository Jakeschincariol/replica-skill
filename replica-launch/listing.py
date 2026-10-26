#!/usr/bin/env python3
"""Store listing linter for replica-launch. Standard library only.

Checks an App Store and Google Play listing against the stores' field limits
and the mistakes that get a clone rejected: the original app's name in your
metadata, ranking claims in the title, wasted keyword characters.

    python3 listing.py replica/launch/listing.json
    python3 listing.py listing.json --avoid "Calendly,Acuity Scheduling"
    python3 listing.py listing.json --json

listing.json (see listing.example.json):

    {
      "avoid": ["Original App Name", "Its Company"],
      "app_store":   {"name", "subtitle", "promotional_text", "description",
                      "keywords", "whats_new"},
      "google_play": {"title", "short_description", "full_description"}
    }

More than one language: put each under "locales", for example
"app_store": {"locales": {"en-US": {...}, "es-MX": {...}}}. Each locale is
linted on its own, and App Store keywords repeated across locales are flagged,
because a storefront that indexes both counts a word once.

Leave out a store you are not shipping to. Exit code 1 on any error, 0 when
there are only warnings.
"""

import argparse
import json
import re
import sys
import unicodedata

LIMITS = {
    "app_store": {"name": 30, "subtitle": 30, "promotional_text": 170,
                  "description": 4000, "keywords": 100, "whats_new": 4000},
    "google_play": {"title": 30, "short_description": 80, "full_description": 4000},
}
SHORT_FIELDS = {"name", "subtitle", "title", "short_description"}
CLAIMS = re.compile(
    r"(#\s?1\b|\bnumber one\b|\bno\.? ?1\b|\bbest\b|\btop[- ]rated\b|\b(app|game) of the year\b"
    # "free" as a price, not as in "times you are actually free"
    r"|(?<!actually )(?<!you are )(?<!you're )(?<!when )(?<!are )\bfree\b|\bdiscount\b|\bsale\b|\b\d+% off\b|\bnew!?$)", re.I)
STOP = {"a", "an", "and", "app", "for", "the", "to", "of", "with", "your", "you", "in", "on", "&"}


def length(text):
    """Characters the way the stores count them.

    Combining marks count: Thai and Hindi vowel signs are separate characters
    to App Store Connect, and a Thai keyword string that "looks" like 91
    characters is rejected as over 100. Only emoji glue is free: a sequence
    joined with ZWJ, skin tones and variation selectors count as one.
    """
    text = unicodedata.normalize("NFC", text or "")
    count = 0
    prev_joiner = False
    for ch in text:
        if ch == "‍":
            prev_joiner = True
            continue
        if ch in ("️", "︎", "⃣") or 0x1F3FB <= ord(ch) <= 0x1F3FF:
            continue
        if prev_joiner:
            prev_joiner = False
            continue
        count += 1
    return count


# (c) (r) and (tm) are symbols a listing may legitimately carry, not emoji
NOT_EMOJI = {"©", "®", "™"}


def has_emoji(text):
    return any(ch not in NOT_EMOJI and (unicodedata.category(ch) == "So" or ord(ch) >= 0x1F000)
               for ch in text or "")


def words(text):
    return [w for w in re.findall(r"[^\W_]+(?:'[^\W_]+)?", (text or "").lower())
            if w not in STOP]


def name_pattern(name):
    """'Acuity Scheduling' also catches AcuityScheduling and acuity-scheduling."""
    parts = [re.escape(p) for p in re.split(r"[\s_-]+", name) if p]
    return re.compile(r"(?<!\w)%s(?!\w)" % r"[\s_-]?".join(parts), re.I)


def sections(listing):
    """Yield (store, label, fields) for each store, and each locale inside it.

    A store is either the fields themselves, or {"locales": {"en-US": {...},
    "es-MX": {...}}} when you ship more than one language.
    """
    for store in LIMITS:
        data = listing.get(store)
        if not data:
            continue
        locales = data.get("locales")
        if isinstance(locales, dict) and locales:
            for loc, fields in locales.items():
                yield store, "%s[%s]" % (store, loc), fields or {}
        else:
            yield store, store, data


def lint(listing, avoid=None):
    issues = []
    avoid = [a.strip() for a in (avoid or listing.get("avoid") or []) if a.strip()]
    avoid_rx = [(a, name_pattern(a)) for a in avoid]

    def add(level, store, field, msg):
        issues.append({"level": level, "store": store, "field": field, "message": msg})

    found_store = False
    keyword_sets = []  # (label, keyword words, name+subtitle words) per App Store locale
    for store, label, data in sections(listing):
        limits = LIMITS[store]
        found_store = True
        for field, limit in limits.items():
            value = data.get(field, "")
            n = length(value)
            if not value:
                level = "error" if field in ("name", "title", "description",
                                             "full_description") else "warn"
                add(level, label, field, "empty")
                continue
            if n > limit:
                add("error", label, field, "%d characters, limit is %d (%d over)"
                    % (n, limit, n - limit))
            for name, rx in avoid_rx:
                if rx.search(value):
                    add("error", label, field,
                        "mentions '%s'. Another app's name or trademark in your "
                        "metadata gets the listing rejected and invites a takedown. "
                        "Describe what yours does instead." % name)
            if field in SHORT_FIELDS:
                m = CLAIMS.search(value)
                if m:
                    add("warn", label, field,
                        "'%s' reads as a ranking or price claim. Google Play bans "
                        "these in the title and short description, and Apple "
                        "rejects claims you cannot back up." % m.group(0).strip())
                if has_emoji(value):
                    add("warn", label, field, "emoji in a short field. Play rejects "
                        "them in titles; App Store reviewers often do too.")
                caps = re.findall(r"\b[A-Z]{4,}\b", value)
                if caps:
                    add("warn", label, field, "all-caps word(s): %s" % ", ".join(caps))
        if store == "app_store" and data.get("keywords"):
            kw_raw = data["keywords"]
            parts = [k.strip().lower() for k in kw_raw.split(",")]
            if re.search(r",\s", kw_raw):
                add("warn", label, "keywords", "spaces after commas waste characters. "
                    "Use word1,word2,word3")
            dupes = sorted({k for k in parts if k and parts.count(k) > 1})
            if dupes:
                add("warn", label, "keywords", "repeated: %s" % ", ".join(dupes))
            in_name = set(words(data.get("name", "")) + words(data.get("subtitle", "")))
            kw_words = {w for k in parts for w in words(k)}
            wasted = sorted(kw_words & in_name)
            if wasted:
                add("warn", label, "keywords", "already in the name or subtitle, so "
                    "these characters are wasted: %s" % ", ".join(wasted))
            if any(not k for k in parts):
                add("warn", label, "keywords", "empty entry (double comma or trailing comma)")
            keyword_sets.append((label, kw_words, in_name))
    # Apple indexes some locales together on one storefront (the US store reads
    # en-US and es-MX). A word indexed by one locale is wasted in the other.
    for i, (label_a, kw_a, name_a) in enumerate(keyword_sets):
        for label_b, kw_b, name_b in keyword_sets[i + 1:]:
            shared = sorted(kw_b & (kw_a | name_a))
            if shared:
                add("warn", label_b, "keywords",
                    "also indexed by %s: %s. If both locales share a storefront "
                    "(the US store reads en-US and es-MX), these characters are "
                    "wasted here" % (label_a, ", ".join(shared)))
    if not found_store:
        add("error", "-", "-", "no app_store or google_play section found")
    return issues


def render(listing, issues):
    out = []
    for store, label, data in sections(listing):
        limits = LIMITS[store]
        out.append(store.replace("_", " ").title() + label[len(store):])
        for field, limit in limits.items():
            n = length(data.get(field, ""))
            mark = "OVER" if n > limit else ("ok" if n else "--")
            out.append("  %-18s %5d / %-5d %s" % (field, n, limit, mark))
        out.append("")
    if not issues:
        out.append("No issues.")
    for i in issues:
        out.append("%-5s %s.%s: %s" % (i["level"].upper(), i["store"], i["field"],
                                       i["message"]))
    errs = sum(1 for i in issues if i["level"] == "error")
    warns = len(issues) - errs
    out.append("")
    out.append("%d errors, %d warnings" % (errs, warns))
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("listing", help="listing.json")
    ap.add_argument("--avoid", help="comma-separated names that must not appear "
                                    "(the original app, its company)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    try:
        with open(args.listing, encoding="utf-8") as fh:
            listing = json.load(fh)
    except (OSError, ValueError) as exc:
        print("listing: %s" % exc, file=sys.stderr)
        return 2
    avoid = args.avoid.split(",") if args.avoid else None
    issues = lint(listing, avoid)
    if args.json:
        print(json.dumps(issues, indent=2))
    else:
        print(render(listing, issues))
    return 1 if any(i["level"] == "error" for i in issues) else 0


if __name__ == "__main__":
    sys.exit(main())
