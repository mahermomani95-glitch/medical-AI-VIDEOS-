#!/usr/bin/env python3
"""Build the browsable video catalog (docs/index.html).

1028 MP4s spread across 22 GitHub Releases are not a usable study resource
on their own. This emits a single self-contained page that indexes every
question in the bank -- searchable, filterable by course, linking straight
to each question's video -- so a student can find "the one about Meckel's
diverticulum" without knowing which course it came from.

Questions with no confirmed answer in the source are shown and clearly
flagged rather than hidden, matching the project's rule never to guess them.

Usage: python3 engine/build_catalog.py questions/bank.json docs/index.html
"""
import json
import re
import sys
from pathlib import Path

REPO = "mahermomani95-glitch/medical-AI-VIDEOS-"


def slug_course(course):
    m = re.match(r"(\d+)(?:st|nd|rd|th)?\s+Month\s+(\d{4})", course)
    return f"{m.group(1)}mo{m.group(2)}" if m else re.sub(r"[^a-z0-9]+", "-", course.lower()).strip("-")


def course_sort_key(course):
    m = re.match(r"(\d+)(?:st|nd|rd|th)?\s+Month\s+(\d{4})", course)
    return (int(m.group(2)), int(m.group(1))) if m else (9999, 99)


def esc(s):
    return (str(s or "").replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def build_data(bank):
    courses = []
    for rec in sorted(bank, key=lambda c: course_sort_key(c["course"])):
        slug = slug_course(rec["course"])
        qs = []
        for q in rec["questions"]:
            correct = next((c for c in q["choices"] if c["correct"]), None)
            qs.append({
                "n": q["number"],
                "en": (q.get("trigger_en") or "").strip(),
                "ar": (q.get("trigger_ar") or "").strip(),
                "ans": (correct["text"].strip() if correct else ""),
                "let": correct["letter"] if correct else "",
                "vid": f"surgery-{slug}-{q['number']:02d}-ar.mp4" if correct else "",
            })
        courses.append({"name": rec["course"], "slug": slug, "qs": qs})
    return courses


PAGE = """<title>Surgery Board Video Bank</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700&family=Source+Sans+3:wght@400;600&family=Cairo:wght@400;600;700&family=IBM+Plex+Mono:wght@500&display=swap">
<style>
:root{
  --ground:#F2F5F4; --surface:#FFFFFF; --surface-2:#E9EEEC;
  --ink:#111917; --muted:#576663; --line:#D3DCD9;
  --accent:#0E6E63; --accent-soft:#D8ECE8; --amber:#A9700F; --amber-soft:#F7EAD2;
  --shadow:0 1px 2px rgba(17,25,23,.06),0 8px 24px rgba(17,25,23,.05);
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --ground:#0E1413; --surface:#161D1B; --surface-2:#1E2725;
    --ink:#E7EEEB; --muted:#93A5A1; --line:#2A3634;
    --accent:#4FBFAE; --accent-soft:#123832; --amber:#D9A62E; --amber-soft:#33280F;
    --shadow:0 1px 2px rgba(0,0,0,.4),0 8px 24px rgba(0,0,0,.32);
  }
}
:root[data-theme="dark"]{
  --ground:#0E1413; --surface:#161D1B; --surface-2:#1E2725;
  --ink:#E7EEEB; --muted:#93A5A1; --line:#2A3634;
  --accent:#4FBFAE; --accent-soft:#123832; --amber:#D9A62E; --amber-soft:#33280F;
  --shadow:0 1px 2px rgba(0,0,0,.4),0 8px 24px rgba(0,0,0,.32);
}
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);
  font-family:"Source Sans 3",system-ui,sans-serif;font-size:16px;line-height:1.55;}
.wrap{max-width:1180px;margin:0 auto;padding:0 24px 72px}

header{padding:48px 0 28px;border-bottom:1px solid var(--line);margin-bottom:28px}
h1{font-family:Archivo,system-ui,sans-serif;font-weight:700;font-size:clamp(30px,4.2vw,46px);
  line-height:1.08;margin:0 0 10px;letter-spacing:-.02em;text-wrap:balance}
.sub{color:var(--muted);max-width:62ch;margin:0}
.stats{display:flex;flex-wrap:wrap;gap:10px;margin-top:22px}
.stat{background:var(--surface);border:1px solid var(--line);border-radius:10px;
  padding:10px 14px;box-shadow:var(--shadow)}
.stat b{font-family:"IBM Plex Mono",monospace;font-size:19px;display:block;
  font-variant-numeric:tabular-nums;color:var(--accent)}
.stat span{font-size:12.5px;color:var(--muted);text-transform:uppercase;letter-spacing:.07em}

.controls{position:sticky;top:0;z-index:20;background:var(--ground);
  padding:14px 0 12px;border-bottom:1px solid var(--line);margin-bottom:22px}
.searchrow{display:flex;gap:10px;flex-wrap:wrap}
input[type=search]{flex:1;min-width:230px;font:inherit;padding:11px 14px;
  border:1px solid var(--line);border-radius:10px;background:var(--surface);color:var(--ink)}
input[type=search]:focus-visible,select:focus-visible,summary:focus-visible,a:focus-visible{
  outline:2px solid var(--accent);outline-offset:2px}
select{font:inherit;padding:11px 12px;border:1px solid var(--line);border-radius:10px;
  background:var(--surface);color:var(--ink)}
.count{color:var(--muted);font-size:14px;margin-top:9px;font-variant-numeric:tabular-nums}

details.course{background:var(--surface);border:1px solid var(--line);border-radius:12px;
  margin-bottom:12px;box-shadow:var(--shadow);overflow:hidden}
details.course[hidden]{display:none}
summary{cursor:pointer;padding:15px 18px;display:flex;align-items:baseline;gap:12px;
  font-family:Archivo,sans-serif;font-weight:600;font-size:17px;list-style:none}
summary::-webkit-details-marker{display:none}
summary::before{content:"";width:7px;height:7px;border-right:2px solid var(--muted);
  border-bottom:2px solid var(--muted);transform:rotate(-45deg);transition:transform .15s;flex:none}
details[open] summary::before{transform:rotate(45deg)}
.year{font-family:"IBM Plex Mono",monospace;color:var(--muted);font-size:13px;font-weight:500}
.qty{margin-left:auto;font-family:"IBM Plex Mono",monospace;font-size:13px;color:var(--muted);
  font-variant-numeric:tabular-nums}

ol.qs{list-style:none;margin:0;padding:0 0 6px;border-top:1px solid var(--line)}
li.q{display:grid;grid-template-columns:46px 1fr auto;gap:4px 14px;
  padding:12px 18px;border-bottom:1px solid var(--line);align-items:start}
li.q:last-child{border-bottom:none}
li.q[hidden]{display:none}
/* Every cell states its own column. Leaving .stem and .watch to
   auto-placement let the button claim column 1 (it spans three rows) and
   shoved the text across the row. */
.num{grid-column:1;grid-row:1;font-family:"IBM Plex Mono",monospace;color:var(--muted);
  font-size:13.5px;font-variant-numeric:tabular-nums;padding-top:2px}
.stem{grid-column:2;grid-row:1;font-weight:600;line-height:1.35}
.stem-ar{grid-column:2;grid-row:2;font-family:Cairo,sans-serif;direction:rtl;text-align:right;
  color:var(--muted);font-size:14.5px;line-height:1.6}
.ans{grid-column:2;grid-row:3;display:flex;align-items:baseline;gap:7px;margin-top:3px;
  font-size:14px;color:var(--muted)}
.ans .chip{background:var(--amber-soft);color:var(--amber);border-radius:5px;
  padding:1px 7px;font-family:"IBM Plex Mono",monospace;font-size:12.5px;font-weight:500}
.watch{grid-column:3;grid-row:1/span 3;align-self:center;justify-self:end;display:inline-block;white-space:nowrap;
  background:var(--accent-soft);color:var(--accent);text-decoration:none;
  border-radius:8px;padding:8px 15px;font-weight:600;font-size:14px;
  border:1px solid transparent;transition:border-color .12s}
.watch:hover{border-color:var(--accent)}
.flag{grid-column:3;grid-row:1/span 3;align-self:center;justify-self:end;white-space:nowrap;font-size:13px;
  color:var(--muted);border:1px dashed var(--line);border-radius:8px;padding:7px 12px}
.empty{padding:38px 4px;color:var(--muted)}
button.watch{font:inherit;font-weight:600;font-size:14px;cursor:pointer}
/* Player overlay: students press play here rather than being sent off to a
   file host, so the videos are usable without leaving this page. */
dialog.player{border:none;padding:0;background:transparent;max-width:min(94vw,1200px);width:100%}
dialog.player::backdrop{background:rgba(8,14,13,.78)}
.pbox{background:var(--surface);border:1px solid var(--line);border-radius:14px;
  overflow:hidden;box-shadow:0 24px 60px rgba(0,0,0,.4)}
.phead{display:flex;align-items:center;gap:12px;padding:12px 14px;border-bottom:1px solid var(--line)}
.ptitle{font-family:Archivo,sans-serif;font-weight:600;font-size:15px;color:var(--ink)}
.pclose{margin-left:auto;font:inherit;cursor:pointer;background:var(--surface-2);color:var(--ink);
  border:1px solid var(--line);border-radius:8px;padding:6px 12px}
.pdl{font-size:13.5px;color:var(--accent);text-decoration:none}
dialog.player video{display:block;width:100%;max-height:74vh;background:#000}
footer{margin-top:34px;padding-top:20px;border-top:1px solid var(--line);
  color:var(--muted);font-size:14px}
footer a{color:var(--accent)}
@media (max-width:640px){
  li.q{grid-template-columns:38px 1fr}
  .num{grid-row:1}.stem{grid-row:1}
  .watch,.flag{grid-row:4;grid-column:2;justify-self:start;margin-top:8px}
}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
</style>

<div class="wrap">
<header>
  <h1>Surgery Board Video Bank</h1>
  <p class="sub">Every question from the 2013&ndash;2021 surgery board bank, rebuilt as a narrated
  teaching video &mdash; Arabic explanation, English medical terminology, and every answer choice
  worked through: why it&rsquo;s right or wrong here, and where it would be the right answer instead.</p>
  <div class="stats">
    <div class="stat"><b>__NQ__</b><span>Questions</span></div>
    <div class="stat"><b>__NC__</b><span>Courses</span></div>
    <div class="stat"><b>__NV__</b><span>Videos</span></div>
    <div class="stat"><b>__NF__</b><span>Flagged, not guessed</span></div>
  </div>
</header>

<div class="controls">
  <div class="searchrow">
    <input type="search" id="q" placeholder="Search a topic, e.g. Meckel, hernia, thyroid, burns&hellip;" aria-label="Search questions">
    <select id="course" aria-label="Filter by course"><option value="">All courses</option>__OPTS__</select>
  </div>
  <div class="count" id="count"></div>
</div>

<main id="list"></main>

<dialog class="player" id="player" aria-label="Video player">
  <div class="pbox">
    <div class="phead">
      <span class="ptitle" id="ptitle"></span>
      <a class="pdl" id="pdl" href="#" download>Download</a>
      <button class="pclose" id="pclose" type="button">Close</button>
    </div>
    <video id="pvid" controls preload="metadata" playsinline></video>
  </div>
</dialog>

<footer>
  Videos are published as GitHub Release assets on
  <a href="https://github.com/__REPO__">__REPO__</a>. Question numbering follows the original
  source exactly. Three questions have no confirmed answer in the source document and are
  flagged rather than guessed.
</footer>
</div>

<script>
const DATA = __DATA__;
const REL = "https://github.com/__REPO__/releases/download/videos-";
const list = document.getElementById('list');
const qIn = document.getElementById('q');
const cIn = document.getElementById('course');
const countEl = document.getElementById('count');

function esc(s){const d=document.createElement('div');d.textContent=s||'';return d.innerHTML;}

list.innerHTML = DATA.map(c => `
  <details class="course" data-slug="${c.slug}">
    <summary><span>Surgery &mdash; ${esc(c.name)}</span>
      <span class="qty">${c.qs.length} questions</span></summary>
    <ol class="qs">${c.qs.map(q => `
      <li class="q" data-t="${esc((q.en+' '+q.ans+' '+q.ar).toLowerCase())}">
        <div class="num">${q.n}</div>
        <div class="stem">${esc(q.en) || '&mdash;'}</div>
        ${q.ar ? `<div class="stem-ar">${esc(q.ar)}</div>` : '<div class="stem-ar"></div>'}
        ${q.ans ? `<div class="ans"><span class="chip">${q.let}</span>${esc(q.ans)}</div>`
                : `<div class="ans">No confirmed answer in the source &mdash; not guessed</div>`}
        ${q.vid ? `<button class="watch" type="button" data-src="${REL}${c.slug}/${q.vid}"
             data-title="${esc(c.name)} &middot; Q${q.n}">Play</button>`
                : `<span class="flag">Flagged</span>`}
      </li>`).join('')}</ol>
  </details>`).join('');

function apply(){
  const term = qIn.value.trim().toLowerCase();
  const slug = cIn.value;
  let shown = 0;
  document.querySelectorAll('details.course').forEach(d => {
    const inCourse = !slug || d.dataset.slug === slug;
    let vis = 0;
    d.querySelectorAll('li.q').forEach(li => {
      const hit = inCourse && (!term || li.dataset.t.includes(term));
      li.hidden = !hit;
      if (hit) vis++;
    });
    d.hidden = vis === 0;
    if (term && vis > 0) d.open = true;
    shown += vis;
  });
  countEl.textContent = (term || slug)
    ? `${shown} question${shown === 1 ? '' : 's'} match`
    : `${shown} questions across ${DATA.length} courses`;
  if (shown === 0 && !list.querySelector('.empty')) {
    const p = document.createElement('p');
    p.className = 'empty';
    p.textContent = 'Nothing matches that search.';
    list.appendChild(p);
  } else if (shown > 0) {
    const e = list.querySelector('.empty');
    if (e) e.remove();
  }
}
const dlg = document.getElementById('player');
const pvid = document.getElementById('pvid');
const ptitle = document.getElementById('ptitle');
const pdl = document.getElementById('pdl');

list.addEventListener('click', e => {
  const btn = e.target.closest('button.watch');
  if (!btn) return;
  pvid.src = btn.dataset.src;
  pdl.href = btn.dataset.src;
  ptitle.innerHTML = btn.dataset.title;
  dlg.showModal();
  pvid.play().catch(() => {});   // autoplay may be blocked; controls still work
});
function closePlayer(){ pvid.pause(); pvid.removeAttribute('src'); pvid.load(); dlg.close(); }
document.getElementById('pclose').addEventListener('click', closePlayer);
dlg.addEventListener('close', () => { pvid.pause(); pvid.removeAttribute('src'); });
dlg.addEventListener('click', e => { if (e.target === dlg) closePlayer(); });

qIn.addEventListener('input', apply);
cIn.addEventListener('change', apply);
apply();
</script>
"""


def main():
    bank = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    out = Path(sys.argv[2])
    out.parent.mkdir(parents=True, exist_ok=True)

    courses = build_data(bank)
    nq = sum(len(c["qs"]) for c in courses)
    nv = sum(1 for c in courses for q in c["qs"] if q["vid"])
    nf = nq - nv

    opts = "".join(
        f'<option value="{esc(c["slug"])}">{esc(c["name"])}</option>' for c in courses)

    html = (PAGE
            .replace("__DATA__", json.dumps(courses, ensure_ascii=False, separators=(",", ":")))
            .replace("__OPTS__", opts)
            .replace("__NQ__", f"{nq:,}")
            .replace("__NC__", str(len(courses)))
            .replace("__NV__", f"{nv:,}")
            .replace("__NF__", str(nf))
            .replace("__REPO__", REPO))
    out.write_text(html, encoding="utf-8")
    print(f"Wrote {out}  ({out.stat().st_size/1024:.0f} KB) "
          f"-- {nq} questions, {len(courses)} courses, {nv} videos, {nf} flagged")


if __name__ == "__main__":
    main()
