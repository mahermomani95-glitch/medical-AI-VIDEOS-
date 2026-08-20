#!/usr/bin/env node
// Builds the single-narrator English scene HTML (one combined auto-playing
// file for review, plus one static file per scene for screenshotting /
// video assembly) from a *.script.json teaching script.
//
// Usage: node build.mjs <questions/xxx.script.json> <outDir>

import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { VISUAL_MAP, questionCardSvg } from "./visuals.mjs";

const __dirname = dirname(fileURLToPath(import.meta.url));

const [, , scriptPathArg, outDirArg] = process.argv;
const scriptPath = scriptPathArg || join(__dirname, "..", "questions", "surgery-1-0001.script.json");
const outDir = outDirArg || join(__dirname, "out");
mkdirSync(outDir, { recursive: true });

const data = JSON.parse(readFileSync(scriptPath, "utf-8"));

const esc = (s = "") => String(s)
  .replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;");

function visualFor(scene) {
  if (scene.visual === "question_card") return questionCardSvg(data.options, data.correct_letter);
  const fn = VISUAL_MAP[scene.visual];
  return fn ? fn() : "";
}

const BASE_STYLE = `
:root{--bg:#07111F;--panel:#10243D;--text:#F5F8FC;--cyan:#55D6E8;--cyan2:#19C3B1;--amber:#FFB454;--muted:#7C93AC}
*{box-sizing:border-box}
html,body{margin:0;width:1920px;height:1080px;background:var(--bg);color:var(--text);font-family:Inter,Arial,sans-serif;overflow:hidden}
.scene{width:1920px;height:1080px;display:flex;flex-direction:column;justify-content:center;gap:36px;padding:90px 130px;background:radial-gradient(circle at 50% 15%,#10243D 0,#07111F 60%)}
.kicker{font-size:26px;color:var(--cyan);font-weight:800;letter-spacing:.06em;text-transform:uppercase}
.heading{font-size:56px;font-weight:800;line-height:1.12;max-width:1500px}
.caption{font-size:34px;line-height:1.4;color:var(--text);max-width:1600px;border-left:5px solid var(--cyan2);padding-left:26px}
.visual{margin-top:10px}
.visual svg{width:100%;max-width:1600px;height:auto;display:block}
.footer{position:absolute;left:80px;right:80px;bottom:50px;display:flex;justify-content:space-between;font-size:20px;color:var(--muted)}
.badge{display:inline-block;padding:6px 16px;border-radius:999px;border:1px solid var(--cyan);color:var(--cyan);font-size:18px;font-weight:700}
`;

function sceneHtml(scene, index, total) {
  return `<!doctype html><html><head><meta charset="utf-8"><style>${BASE_STYLE}</style></head>
<body><div class="scene">
  <div class="kicker">Scene ${index + 1} of ${total} · ${esc(scene.heading)}</div>
  <div class="caption">${esc(scene.caption)}</div>
  <div class="visual">${visualFor(scene)}</div>
  <div class="footer"><span>Medical AI Videos — Single Narrator</span><span class="badge">${esc(data.id)}</span></div>
</div></body></html>`;
}

// One file per scene (for Playwright screenshots / video frames)
data.scenes.forEach((scene, i) => {
  const html = sceneHtml(scene, i, data.scenes.length);
  writeFileSync(join(outDir, `${data.id}.scene${i + 1}-${scene.id}.html`), html, "utf-8");
});

// One combined auto-advancing file for quick browser review
const combined = `<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${esc(data.id)} — single narrator preview</title>
<style>${BASE_STYLE.replace(/1920px/g, "100vw").replace(/1080px/g, "100vh")}
.scene{display:none;position:absolute;inset:0}
.scene.active{display:flex}
</style></head>
<body>
${data.scenes.map((s, i) => `<section class="scene${i === 0 ? " active" : ""}" data-duration="${Math.max(6, Math.round(s.narration.split(" ").length / 2.5))}">
  <div class="kicker">Scene ${i + 1} of ${data.scenes.length} · ${esc(s.heading)}</div>
  <div class="caption">${esc(s.caption)}</div>
  <div class="visual">${visualFor(s)}</div>
  <div class="footer"><span>Medical AI Videos — Single Narrator</span><span class="badge">${esc(data.id)}</span></div>
</section>`).join("\n")}
<script>
const scenes=[...document.querySelectorAll('.scene')];let i=0;
function show(){scenes.forEach((s,n)=>s.classList.toggle('active',n===i));
  const d=(Number(scenes[i].dataset.duration)||8)*1000;
  setTimeout(()=>{if(i<scenes.length-1){i++;show();}},d);}
show();
</script>
</body></html>`;
writeFileSync(join(outDir, `${data.id}.preview.html`), combined, "utf-8");

console.log(`Built ${data.scenes.length} scene files + 1 preview file in ${outDir}`);
