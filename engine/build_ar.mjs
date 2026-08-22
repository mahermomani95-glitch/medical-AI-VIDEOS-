#!/usr/bin/env node
// Builds the Arabic-track scene HTML (new visual system matched to the
// user's reference video) from a *.ar.script.json file.
//
// Usage: node build_ar.mjs <questions/xxx.ar.script.json> <outDir>

import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { BASE_STYLE_AR, trophySvg } from "./style-ar.mjs";
import {
  giTractIllustrationSvg, timelineIllustrationSvg,
  biliaryMechanismArSvg, cascadeArSvg, factorEightArSvg, factorFiveArSvg,
} from "./visuals-ar.mjs";

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

// Question-specific illustration choice (question bank is small enough to
// key by id for now; generalize once there are more illustration types).
const QUESTION_ILLUSTRATION = data.id.startsWith("surgery-6mo2013")
  ? giTractIllustrationSvg()
  : biliaryMechanismArSvg();

const MECHANISM_ILLUSTRATION = data.id.startsWith("surgery-6mo2013")
  ? giTractIllustrationSvg()
  : biliaryMechanismArSvg();

function sceneQuestion(scene, index, total) {
  const pillLabel = data.question_number ? `السؤال ${data.question_number}` : "سؤال تدريبي";
  return `<div class="scene">
    <div class="course-label">${esc(data.course_label || "")}</div>
    <div class="q-pill">${pillLabel}</div>
    <div class="headline-en">${esc(data.question)}</div>
    <div class="headline-ar">${esc(data.question_ar)}</div>
    <div class="illustration">${QUESTION_ILLUSTRATION}</div>
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

function sceneCardIllustration(scene, illustrationSvg, illoTop = 340) {
  return `<div class="scene">
    <div class="scene-heading">${esc(scene.heading_ar || "")}</div>
    <div class="card" style="max-width:1000px;margin-top:18px">
      <p class="ar">${esc(scene.card_text || scene.caption)}</p>
    </div>
    <div class="illustration" style="top:${illoTop}px">${illustrationSvg}</div>
    <div class="caption-bar">${esc(scene.caption)}</div>
  </div>`;
}

function sceneVerdictList(scene) {
  const rows = (scene.verdicts || []).map(v => `
    <div class="verdict-row">
      <div class="verdict-top">
        <div class="verdict-badge ${v.verdict === "correct" ? "correct" : "wrong"}">${v.verdict === "correct" ? "✓" : "✕"}</div>
        <div class="verdict-en">${esc(v.letter)}) ${esc(v.text)}</div>
      </div>
      <div class="verdict-ar">${esc(v.reason)}</div>
    </div>`).join("\n");
  return `<div class="scene">
    <div class="scene-heading">${esc(scene.heading_ar || "")}</div>
    <div style="max-width:1150px;margin-top:14px">${rows}</div>
    <div class="caption-bar">${esc(scene.caption)}</div>
  </div>`;
}

function sceneCorrectGold(scene) {
  // Generic gold "correct answer" banner + timeline pills (used by the GI question)
  return `<div class="scene">
    ${trophySvg()}
    <div class="gold-banner" style="max-width:900px;margin-top:40px">
      <div class="k">الإجابة الصحيحة</div>
      <div class="v">${esc(data.correct_letter)}) ${esc(data.correct_text)}</div>
    </div>
    <div class="illustration" style="top:120px">${timelineIllustrationSvg()}</div>
    <div class="card" style="max-width:820px;margin-top:36px">
      <div class="card-title">الجدول الزمني للعودة</div>
      <div class="pills">
        <div class="pill">Small Bowel ~24h</div>
        <div class="pill">Stomach 24–48h</div>
        <div class="pill">Colon 48–72h+</div>
      </div>
    </div>
    <div class="caption-bar">${esc(scene.caption)}</div>
  </div>`;
}

function sceneFactorEight(scene) {
  return `<div class="scene">
    ${trophySvg()}
    <div class="gold-banner" style="max-width:900px;margin-top:40px">
      <div class="k">الإجابة الصحيحة</div>
      <div class="v">${esc(data.correct_letter)}) ${esc(data.correct_text)}</div>
    </div>
    <div class="illustration" style="top:150px;width:480px">${factorEightArSvg()}</div>
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

function renderScene(scene, index, total) {
  switch (scene.visual) {
    case "question_card":
    case "question_card_factor8":
      return sceneQuestion(scene, index, total);
    case "options_list":
      return sceneOptions(scene);
    case "gi_mechanism":
      return sceneCardIllustration(scene, MECHANISM_ILLUSTRATION, 380);
    case "biliary_mechanism":
      return sceneCardIllustration(scene, biliaryMechanismArSvg(), 380);
    case "gi_timeline":
      return sceneCardIllustration(scene, timelineIllustrationSvg(), 380);
    case "cascade_ar":
      return sceneCardIllustration(scene, cascadeArSvg(), 380);
    case "verdict_list":
      return sceneVerdictList(scene);
    case "correct_gold":
      return sceneCorrectGold(scene);
    case "factor_eight_ar":
      return sceneFactorEight(scene);
    case "factor_five_ar":
      return sceneCardIllustration(scene, factorFiveArSvg(), 340);
    case "pearl_card":
      return sceneCardIllustration(scene, timelineIllustrationSvg(), 380);
    case "summary_card":
      return sceneSummary(scene);
    default:
      return `<div class="scene"><div class="scene-heading">${esc(scene.heading_ar || scene.id)}</div></div>`;
  }
}

data.scenes.forEach((scene, i) => {
  const html = wrap(renderScene(scene, i, data.scenes.length));
  writeFileSync(join(outDir, `${data.id}.scene${i + 1}-${scene.id}.html`), html, "utf-8");
});

console.log(`Built ${data.scenes.length} Arabic scenes for ${data.id} in ${outDir}`);
