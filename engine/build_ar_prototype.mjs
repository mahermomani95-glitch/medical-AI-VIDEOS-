#!/usr/bin/env node
// Prototype builder for the new Arabic visual system (reverse-engineered
// from the reference video: amber bg, pink/cyan neubrutalist cards, Anton
// headlines, Cairo Arabic body text, gold "correct answer" banner).
// Produces a handful of representative scenes for ONE question so the
// direction can be approved before rebuilding the whole pipeline on it.

import { writeFileSync, mkdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { BASE_STYLE_AR, trophySvg } from "./style-ar.mjs";
import { giTractIllustrationSvg, timelineIllustrationSvg } from "./visuals-ar.mjs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const outDir = join(__dirname, "out-ar-prototype");
mkdirSync(outDir, { recursive: true });

const wrap = (inner) => `<!doctype html><html><head><meta charset="utf-8"><style>${BASE_STYLE_AR}</style></head>
<body>${inner}</body></html>`;

// ---- Scene 1: QUESTION ----
const sceneQuestion = `<div class="scene">
  <div class="course-label">Course: Surgery — 6th Month 2013 Course</div>
  <div class="q-pill">السؤال 1</div>
  <div class="headline-en">What is the true order of GI recovery after abdominal surgery?</div>
  <div class="headline-ar">ما هو الترتيب الصحيح لعودة نشاط الجهاز الهضمي بعد أي عملية جراحية في البطن؟</div>
  <div class="illustration">${giTractIllustrationSvg()}</div>
  <div class="badge-course">SURGERY</div>
  <div class="caption-bar">Postoperative Ileus</div>
</div>`;

// ---- Scene 2: OPTIONS ----
const options = [
  { l: "A", t: "Stomach, then colon, then small bowel" },
  { l: "B", t: "Colon, then small bowel, then stomach" },
  { l: "C", t: "Stomach, then small bowel, then colon" },
  { l: "D", t: "Small bowel, then stomach, then colon" },
  { l: "E", t: "Small bowel, then colon, then stomach" },
];
const sceneOptions = `<div class="scene">
  <div class="q-pill" style="margin-top:0">الخيارات</div>
  <div style="max-width:900px;margin-top:24px">
    ${options.map(o => `<div class="opt-row"><div class="opt-badge">${o.l}</div><div class="opt-text">${o.t}</div></div>`).join("\n")}
  </div>
  <div class="caption-bar">اختر الترتيب الصحيح</div>
</div>`;

// ---- Scene 3: COMPARISON (misconception vs physiology) ----
const sceneCompare = `<div class="scene">
  <div class="q-pill" style="margin-top:0">لماذا يخطئ أغلب الطلاب هنا</div>
  <div class="headline-ar" style="max-width:1600px;margin-top:10px">الترتيب المنطقي "بالحدس" ليس هو الترتيب الفسيولوجي الحقيقي للعودة.</div>
  <div class="split">
    <div class="box pink">
      <h3>Common Belief</h3>
      <p>يُفترض أن المعدة أو القولون يعودان أولًا لأنهما "أكبر" أو "أقرب" لمكان الجراحة.</p>
    </div>
    <div class="vs-badge">VS</div>
    <div class="box cyan">
      <h3>Real Physiology</h3>
      <p>الأمعاء الدقيقة تملك أنشط جهاز عصبي معوي (Myenteric)، فتعود للعمل أولًا خلال ٢٤ ساعة تقريبًا.</p>
    </div>
  </div>
  <div class="caption-bar">الأمعاء الدقيقة أولًا</div>
</div>`;

// ---- Scene 4: CORRECT ANSWER ----
const sceneCorrect = `<div class="scene">
  ${trophySvg()}
  <div class="gold-banner" style="max-width:820px;margin-top:40px">
    <div class="k">الإجابة الصحيحة</div>
    <div class="v">D) Small Bowel &rarr; Stomach &rarr; Colon</div>
  </div>
  <div class="illustration" style="top:120px">${timelineIllustrationSvg()}</div>
  <div class="card" style="max-width:760px;margin-top:36px">
    <div class="card-title">الجدول الزمني للعودة</div>
    <div class="pills">
      <div class="pill">Small Bowel ~24h</div>
      <div class="pill">Stomach 24–48h</div>
      <div class="pill">Colon 48–72h+</div>
    </div>
  </div>
  <div class="caption-bar">D. Small Bowel → Stomach → Colon</div>
</div>`;

// ---- Scene 5: SUMMARY ----
const sceneSummary = `<div class="scene">
  <div class="card gold-shadow" style="max-width:1200px;margin:120px auto 0;text-align:center">
    <div class="card-title" style="text-align:center">الخلاصة السريعة</div>
    <div class="headline-ar" style="max-width:1100px;margin:0 auto;text-align:center">
      بعد جراحة البطن يتعطل الجهاز الهضمي بشكل غير متساوٍ: الأمعاء الدقيقة تعود أولًا، ثم المعدة، وأخيرًا القولون.
    </div>
  </div>
  <div class="caption-bar">نلقاكم في السؤال القادم</div>
</div>`;

const scenes = {
  "scene1-QUESTION": sceneQuestion,
  "scene2-OPTIONS": sceneOptions,
  "scene3-COMPARE": sceneCompare,
  "scene4-CORRECT": sceneCorrect,
  "scene5-SUMMARY": sceneSummary,
};

for (const [name, html] of Object.entries(scenes)) {
  writeFileSync(join(outDir, `${name}.html`), wrap(html), "utf-8");
}

console.log(`Built ${Object.keys(scenes).length} prototype scenes in ${outDir}`);
