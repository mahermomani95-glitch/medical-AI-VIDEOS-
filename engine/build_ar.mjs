#!/usr/bin/env node
// Builds the Arabic-track scene HTML (new visual system matched to the
// user's reference video) from a *.ar.script.json file.
//
// Fully generic/data-driven so it scales to all 1031 questions: every
// scene's illustration is described by an `illustration` object in the
// script JSON (see visuals-ar.mjs), not hardcoded per question id.
//
// Usage: node build_ar.mjs <questions/xxx.ar.script.json> <outDir>

import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { BASE_STYLE_AR, trophySvg } from "./style-ar.mjs";
import { illustrationSvg } from "./visuals-ar.mjs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const [, , scriptPathArg, outDirArg] = process.argv;
if (!scriptPathArg) { console.error("Usage: node build_ar.mjs <script.ar.script.json> <outDir>"); process.exit(1); }
const outDir = outDirArg || join(__dirname, "out-ar");
mkdirSync(outDir, { recursive: true });

const data = JSON.parse(readFileSync(scriptPathArg, "utf-8"));

const esc = (s = "") => String(s)
  .replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;");

const wrap = (inner) => `<!doctype html><html><head><meta charset="utf-8"><style>${BASE_STYLE_AR}</style></head>
<body>${inner}</body></html>`;

function sceneQuestion(scene) {
  const pillLabel = data.question_number ? `السؤال ${data.question_number}` : "سؤال تدريبي";
  return `<div class="scene">
    <div class="course-label">${esc(data.course_label || "")}</div>
    <div class="q-pill">${pillLabel}</div>
    <div class="headline-en">${esc(data.question)}</div>
    <div class="headline-ar">${esc(data.question_ar)}</div>
    <div class="illustration">${illustrationSvg(scene.illustration)}</div>
    <div class="badge-course">SURGERY</div>
    <div class="caption-bar">${esc(scene.caption)}</div>
  </div>`;
}

function sceneOptions(scene) {
  return `<div class="scene">
    <div class="q-pill" style="margin-top:0">الخيارات</div>
    <div style="max-width:980px;margin-top:24px">
      ${data.options.map(o => `<div class="opt-row"><div class="opt-badge">${o.letter}</div><div class="opt-text">${esc(o.text)}</div></div>`).join("\n")}
    </div>
    <div class="caption-bar">${esc(scene.caption)}</div>
  </div>`;
}

// Generic content card + illustration -- used for MECHANISM, TIMELINE,
// CASCADE, CLINICAL_PEARL, and any other explanatory scene. The
// illustration is whatever `scene.illustration` describes; a scene with
// no illustration data just gets the generic brand icon.
function sceneCardIllustration(scene, illoTop = 380) {
  return `<div class="scene">
    <div class="scene-heading">${esc(scene.heading_ar || "")}</div>
    <div class="card" style="max-width:1000px;margin-top:18px">
      <p class="ar">${esc(scene.card_text || scene.caption)}</p>
    </div>
    <div class="illustration" style="top:${illoTop}px">${illustrationSvg(scene.illustration)}</div>
    <div class="caption-bar">${esc(scene.caption)}</div>
  </div>`;
}

// Purpose (مغزى) and Trap (الفخ) cards -- mandatory per project rules,
// shown/narrated VERBATIM from the source docx, never reworded/shortened.
function scenePurpose(scene) {
  return `<div class="scene">
    <div class="scene-heading">${esc(scene.heading_ar || "مغزى السؤال")}</div>
    <div class="card gold-shadow" style="max-width:1300px;margin-top:18px">
      <div class="card-label">مغزى السؤال</div>
      <p class="ar">${esc(scene.text_ar)}</p>
    </div>
    <div class="caption-bar">${esc(scene.caption)}</div>
  </div>`;
}

function sceneTrap(scene) {
  return `<div class="scene">
    <div class="scene-heading">${esc(scene.heading_ar || "الفخ")}</div>
    <div class="card warn-shadow" style="max-width:1300px;margin-top:18px">
      <div class="card-label warn">الفخ</div>
      <p class="ar">${esc(scene.text_ar)}</p>
    </div>
    <div class="caption-bar">${esc(scene.caption)}</div>
  </div>`;
}

// Per-choice verdict list. Every choice gets: right/wrong for THIS
// question (badge + reason), and where else it WOULD be correct
// (`elsewhere`) -- the project's mandatory per-choice rule.
function sceneVerdictList(scene) {
  const rows = (scene.verdicts || []).map(v => `
    <div class="verdict-row">
      <div class="verdict-top">
        <div class="verdict-badge ${v.verdict === "correct" ? "correct" : "wrong"}">${v.verdict === "correct" ? "✓" : "✕"}</div>
        <div class="verdict-en">${esc(v.letter)}) ${esc(v.text)}</div>
      </div>
      <div class="verdict-ar">${esc(v.reason)}</div>
      ${v.elsewhere ? `<div class="verdict-elsewhere">📍 ${esc(v.elsewhere)}</div>` : ""}
    </div>`).join("\n");
  return `<div class="scene">
    <div class="scene-heading">${esc(scene.heading_ar || "")}</div>
    <div style="max-width:1150px;margin-top:8px">${rows}</div>
    <div class="caption-bar">${esc(scene.caption)}</div>
  </div>`;
}

// Generic "correct answer" gold banner + trophy + optional supporting
// pills (`scene.pills: string[]`) -- pills are whatever short facts the
// script wants to highlight (a timeline, a set of values, etc.), not
// hardcoded to any one question's content.
function sceneCorrectGold(scene) {
  const pills = (scene.pills || []).map(p => `<div class="pill">${esc(p)}</div>`).join("\n");
  return `<div class="scene">
    ${trophySvg()}
    <div class="gold-banner" style="max-width:900px;margin-top:40px">
      <div class="k">الإجابة الصحيحة</div>
      <div class="v">${esc(data.correct_letter)}) ${esc(data.correct_text)}</div>
    </div>
    ${scene.illustration ? `<div class="illustration" style="top:250px">${illustrationSvg(scene.illustration)}</div>` : ""}
    ${pills ? `<div class="card" style="max-width:820px;margin-top:36px">
      <div class="card-title">نقاط أساسية</div>
      <div class="pills">${pills}</div>
    </div>` : ""}
    <div class="caption-bar">${esc(scene.caption)}</div>
  </div>`;
}

function sceneSummary(scene) {
  return `<div class="scene">
    <div class="card gold-shadow" style="max-width:1300px;margin:120px auto 0;text-align:center">
      <div class="card-title" style="text-align:center">الخلاصة السريعة</div>
      <div class="headline-ar" style="max-width:1150px;margin:0 auto;text-align:center">${esc(data.summary_ar)}</div>
    </div>
    <div class="caption-bar">${esc(scene.caption)}</div>
  </div>`;
}

function renderScene(scene) {
  switch (scene.visual) {
    case "question_card":
      return sceneQuestion(scene);
    case "options_list":
      return sceneOptions(scene);
    case "mechanism_card":
      return sceneCardIllustration(scene, 380);
    case "purpose_card":
      return scenePurpose(scene);
    case "trap_card":
      return sceneTrap(scene);
    case "verdict_list":
      return sceneVerdictList(scene);
    case "correct_gold":
      return sceneCorrectGold(scene);
    case "pearl_card":
      return sceneCardIllustration(scene, 380);
    case "summary_card":
      return sceneSummary(scene);
    default:
      return `<div class="scene"><div class="scene-heading">${esc(scene.heading_ar || scene.id)}</div></div>`;
  }
}

data.scenes.forEach((scene, i) => {
  const html = wrap(renderScene(scene));
  writeFileSync(join(outDir, `${data.id}.scene${i + 1}-${scene.id}.html`), html, "utf-8");
});

console.log(`Built ${data.scenes.length} Arabic scenes for ${data.id} in ${outDir}`);
