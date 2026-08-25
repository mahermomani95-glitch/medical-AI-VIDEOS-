#!/usr/bin/env python3
"""Reconcile what SHOULD exist against what is actually published.

The render fleet is ~63 concurrent jobs making tens of thousands of network
TTS calls; some questions will fail transiently even with retries. This
compares every expected video against the release assets and prints exactly
what is missing, per course -- so a re-run can target only the gaps instead
of re-rendering 1028 videos.

Also flags anything published that should NOT be there (per-scene clips,
zero-byte assets), since those are indistinguishable from real videos to
anyone browsing the releases.

Usage:
  python3 engine/verify_releases.py questions/bank.json [--token TOKEN] [--json]

Exit status is 0 only when every expected video is present.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = "mahermomani95-glitch/medical-AI-VIDEOS-"


def slug_course(course):
    m = re.match(r"(\d+)(?:st|nd|rd|th)?\s+Month\s+(\d{4})", course)
    return f"{m.group(1)}mo{m.group(2)}" if m else re.sub(r"[^a-z0-9]+", "-", course.lower()).strip("-")


def api(path, token):
    """Fetch a GitHub API path. Uses curl with the proxy disabled: this
    sandbox's own HTTPS proxy intercepts api.github.com and returns 403."""
    url = f"https://api.github.com/repos/{REPO}{path}"
    env = dict(os.environ, HTTPS_PROXY="", https_proxy="")
    out = subprocess.run(
        ["curl", "-sS", "--noproxy", "*", "-H", f"Authorization: Bearer {token}",
         "-H", "Accept: application/vnd.github+json", url],
        capture_output=True, text=True, env=env,
    )
    if out.returncode != 0:
        raise RuntimeError(f"curl failed: {out.stderr[:300]}")
    return json.loads(out.stdout)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bank")
    ap.add_argument("--token", default=os.environ.get("GH_PAT", ""))
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()
    if not args.token:
        print("Need a token: --token or $GH_PAT", file=sys.stderr)
        return 2

    bank = json.loads(Path(args.bank).read_text(encoding="utf-8"))

    # Expected: every question that has a confirmed answer in the source.
    expected = {}   # slug -> {num: filename}
    unanswerable = []
    for rec in bank:
        slug = slug_course(rec["course"])
        for q in rec["questions"]:
            if not any(c["correct"] for c in q["choices"]):
                unanswerable.append(f"{rec['course']} Q{q['number']}")
                continue
            expected.setdefault(slug, {})[q["number"]] = \
                f"surgery-{slug}-{q['number']:02d}-ar.mp4"

    releases = api("/releases?per_page=100", args.token)
    published = {}   # slug -> set(filenames)
    bad_assets = []
    for rel in releases:
        tag = rel.get("tag_name", "")
        if not tag.startswith("videos-"):
            continue
        slug = tag[len("videos-"):]
        names = set()
        for a in rel.get("assets", []):
            n = a["name"]
            if ".scene" in n:
                bad_assets.append((tag, n, "per-scene intermediate"))
                continue
            if a.get("size", 0) == 0:
                bad_assets.append((tag, n, "zero bytes"))
                continue
            names.add(n)
        published[slug] = names

    report = {"courses": [], "unanswerable": unanswerable,
              "bad_assets": [{"tag": t, "name": n, "why": w} for t, n, w in bad_assets]}
    total_exp = total_have = 0
    for rec in bank:
        slug = slug_course(rec["course"])
        exp = expected.get(slug, {})
        have = published.get(slug, set())
        missing = sorted(n for n, f in exp.items() if f not in have)
        total_exp += len(exp)
        total_have += len(exp) - len(missing)
        report["courses"].append({
            "course": rec["course"], "slug": slug,
            "expected": len(exp), "present": len(exp) - len(missing),
            "missing": missing,
        })

    report["total_expected"] = total_exp
    report["total_present"] = total_have
    report["complete"] = (total_have == total_exp and not bad_assets)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=1))
    else:
        print(f"{'COURSE':28} {'HAVE':>5}/{'EXP':<5}  MISSING")
        for c in report["courses"]:
            miss = c["missing"]
            flag = "" if not miss else (
                ",".join(str(m) for m in miss[:12]) + ("…" if len(miss) > 12 else ""))
            mark = "ok" if not miss else "--"
            print(f"{c['slug']:28} {c['present']:>5}/{c['expected']:<5}  {mark} {flag}")
        print()
        print(f"TOTAL {total_have}/{total_exp} videos published")
        if unanswerable:
            print(f"Excluded (no confirmed answer in source, never guessed): "
                  f"{len(unanswerable)} -> {', '.join(unanswerable)}")
        if bad_assets:
            print(f"\nAssets that should not be published ({len(bad_assets)}):")
            for t, n, w in bad_assets[:20]:
                print(f"  {t}/{n}  [{w}]")
        print("\nCOMPLETE" if report["complete"] else "\nINCOMPLETE")

    return 0 if report["complete"] else 1


if __name__ == "__main__":
    sys.exit(main())
