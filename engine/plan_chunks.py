#!/usr/bin/env python3
"""Plan the render matrix: group question scripts into per-course chunks.

GitHub Actions caps a workflow run at 256 matrix jobs, so one job per
question is impossible at 1031 questions. This splits each course's
questions into fixed-size chunks (default 20), giving ~60 jobs total --
well under the cap, while keeping every chunk inside a single course so
each job uploads to that course's own Release.

Emits a JSON array of {course, slug, index, ids} to stdout.

Usage: python3 engine/plan_chunks.py questions [--size 20] [--course SLUG]
                                      [--only-missing rendered_manifest.txt]
"""
import argparse
import json
import re
import sys
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("qdir")
    ap.add_argument("--size", type=int, default=20)
    ap.add_argument("--course", help="restrict to this course slug, e.g. 6mo2013")
    args = ap.parse_args()

    qdir = Path(args.qdir)
    scripts = sorted(qdir.glob("*.ar.script.json"))

    # Group by course slug parsed out of the filename:
    #   surgery-<courseslug>-<NN>.ar.script.json
    by_course = {}
    for p in scripts:
        name = p.name[: -len(".ar.script.json")]
        m = re.match(r"surgery-(.+)-(\d+)$", name)
        if not m:
            # Non-conforming ids (e.g. legacy samples) get their own bucket.
            slug, num = name, 0
        else:
            slug, num = m.group(1), int(m.group(2))
        if args.course and slug != args.course:
            continue
        by_course.setdefault(slug, []).append((num, name))

    chunks = []
    for slug in sorted(by_course):
        items = [n for _, n in sorted(by_course[slug])]
        for i in range(0, len(items), args.size):
            chunks.append({
                "slug": slug,
                "index": i // args.size,
                "ids": items[i:i + args.size],
            })

    json.dump(chunks, sys.stdout, ensure_ascii=False)
    print(file=sys.stderr)
    print(f"{len(scripts)} scripts -> {len(chunks)} chunks "
          f"across {len(by_course)} courses", file=sys.stderr)


if __name__ == "__main__":
    main()
