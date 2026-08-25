#!/usr/bin/env python3
"""Build an offline download kit for the whole video bank.

Produces, into an output directory:
  video-urls.txt        one direct URL per line (1028 lines) -- feed to any
                        download manager, including iPhone apps
  download-all.command  macOS double-clickable downloader (also a valid .sh)
  download-all.bat      Windows double-clickable downloader
  playlists/<course>.m3u  one playlist per course for VLC

Both scripts sort videos into per-course folders, name them by question
number, skip files already downloaded (so an interrupted run resumes), and
retry on network failure -- 1028 files over a phone or hotel connection will
not complete in one uninterrupted pass.

Usage: python3 engine/build_download_kit.py questions/bank.json dist/download-kit
"""
import json
import re
import sys
from pathlib import Path

REPO = "mahermomani95-glitch/medical-AI-VIDEOS-"
BASE = f"https://github.com/{REPO}/releases/download"


def slug_course(course):
    m = re.match(r"(\d+)(?:st|nd|rd|th)?\s+Month\s+(\d{4})", course)
    return f"{m.group(1)}mo{m.group(2)}" if m else re.sub(r"[^a-z0-9]+", "-", course.lower()).strip("-")


def course_sort_key(course):
    m = re.match(r"(\d+)(?:st|nd|rd|th)?\s+Month\s+(\d{4})", course)
    return (int(m.group(2)), int(m.group(1))) if m else (9999, 99)


def safe_folder(course):
    return re.sub(r"[^A-Za-z0-9]+", "-", f"Surgery {course}").strip("-")


def main():
    bank = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    out = Path(sys.argv[2])
    (out / "playlists").mkdir(parents=True, exist_ok=True)

    entries = []   # (folder, filename, url, course, number, title)
    for rec in sorted(bank, key=lambda c: course_sort_key(c["course"])):
        slug = slug_course(rec["course"])
        folder = safe_folder(rec["course"])
        for q in rec["questions"]:
            if not any(c["correct"] for c in q["choices"]):
                continue      # no confirmed answer in source; never rendered
            fn = f"surgery-{slug}-{q['number']:02d}-ar.mp4"
            entries.append((folder, fn, f"{BASE}/videos-{slug}/{fn}",
                            rec["course"], q["number"],
                            (q.get("trigger_en") or "").strip()))

    # --- plain URL list -------------------------------------------------
    (out / "video-urls.txt").write_text(
        "\n".join(e[2] for e in entries) + "\n", encoding="utf-8")

    # --- per-course M3U playlists (VLC streams or saves these) ----------
    by_course = {}
    for folder, fn, url, course, num, title in entries:
        by_course.setdefault((course, folder), []).append((num, title, url))
    for (course, folder), items in by_course.items():
        lines = ["#EXTM3U"]
        for num, title, url in sorted(items):
            lines.append(f"#EXTINF:-1,Q{num} - {title}")
            lines.append(url)
        (out / "playlists" / f"{folder}.m3u").write_text(
            "\n".join(lines) + "\n", encoding="utf-8")

    all_lines = ["#EXTM3U"]
    for folder, fn, url, course, num, title in entries:
        all_lines.append(f"#EXTINF:-1,{course} Q{num} - {title}")
        all_lines.append(url)
    (out / "playlists" / "ALL-COURSES.m3u").write_text(
        "\n".join(all_lines) + "\n", encoding="utf-8")

    # --- macOS / Linux downloader ---------------------------------------
    sh = ["#!/bin/bash",
          "# Downloads every Surgery board video into per-course folders.",
          "# Safe to stop and re-run: finished files are skipped, partial",
          "# downloads resume where they left off.",
          "cd \"$(dirname \"$0\")\" || exit 1",
          "TOTAL=%d" % len(entries),
          "i=0",
          "fail=0",
          ""]
    for folder, fn, url, *_ in entries:
        sh.append(f'i=$((i+1)); mkdir -p "{folder}"')
        sh.append(f'if [ -s "{folder}/{fn}" ]; then echo "[$i/$TOTAL] have {fn}"; else')
        sh.append(f'  echo "[$i/$TOTAL] {fn}"')
        # -C - resumes, --retry rides out flaky connections
        sh.append(f'  curl -fL -C - --retry 5 --retry-delay 3 -o "{folder}/{fn}" "{url}" || '
                  f'{{ echo "  FAILED {fn}"; fail=$((fail+1)); }}')
        sh.append("fi")
    sh += ["", 'echo ""',
           'echo "Done. $((TOTAL-fail))/$TOTAL downloaded."',
           'if [ "$fail" -gt 0 ]; then echo "$fail failed - just run this again to retry them."; fi',
           'read -n 1 -s -r -p "Press any key to close."']
    p = out / "download-all.command"
    p.write_text("\n".join(sh) + "\n", encoding="utf-8")
    p.chmod(0o755)

    # --- Windows downloader ---------------------------------------------
    bat = ["@echo off",
           "REM Downloads every Surgery board video into per-course folders.",
           "REM Safe to stop and re-run: finished files are skipped.",
           "cd /d \"%~dp0\"",
           "setlocal enabledelayedexpansion",
           "set TOTAL=%d" % len(entries),
           "set i=0", ""]
    for folder, fn, url, *_ in entries:
        bat.append("set /a i+=1")
        bat.append(f'if not exist "{folder}" mkdir "{folder}"')
        bat.append(f'if exist "{folder}\\{fn}" (echo [!i!/%TOTAL%] have {fn}) else ('
                   f'echo [!i!/%TOTAL%] {fn} ^& '
                   f'curl -fL -C - --retry 5 --retry-delay 3 -o "{folder}\\{fn}" "{url}")')
    bat += ["", "echo.", "echo Done. Re-run this file to retry anything that failed.", "pause"]
    (out / "download-all.bat").write_text("\r\n".join(bat) + "\r\n", encoding="utf-8")

    total_gb = len(entries) * 6.0 / 1024
    print(f"Wrote kit to {out}")
    print(f"  {len(entries)} videos  (~{total_gb:.1f} GB)")
    print(f"  {len(by_course)} course playlists + ALL-COURSES.m3u")


if __name__ == "__main__":
    main()
