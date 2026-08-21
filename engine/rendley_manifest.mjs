#!/usr/bin/env node
// Packages one question's rendered scene assets (PNGs from build.mjs +
// a screenshot pass) into a manifest for the Rendley MCP backend: an
// ordered file list plus a ready-to-use natural-language prompt for
// `create_video_draft`. This is the alternative to the Piper+ffmpeg
// path in generate_video.py — meant for interactive assembly in
// Rendley's editor rather than the unattended GitHub Actions render.
//
// Usage: node rendley_manifest.mjs <questions/xxx.script.json> <scenePngDir> [outFile]

import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { join } from "node:path";

const [, , scriptPathArg, pngDirArg, outFileArg] = process.argv;
if (!scriptPathArg || !pngDirArg) {
  console.error("Usage: node rendley_manifest.mjs <questions/xxx.script.json> <scenePngDir> [outFile]");
  process.exit(1);
}

const data = JSON.parse(readFileSync(scriptPathArg, "utf-8"));
const qid = data.id;

const scenes = data.scenes.map((scene, i) => {
  const file = `${qid}.scene${i + 1}-${scene.id}.png`;
  const path = join(pngDirArg, file);
  if (!existsSync(path)) {
    console.error(`[error] missing scene image ${path} -- run build.mjs and the screenshot step first`);
    process.exit(1);
  }
  return { index: i + 1, id: scene.id, heading: scene.heading, file, narration: scene.narration, caption: scene.caption };
});

const promptLines = [
  `Build a single-narrator medical teaching video for question "${qid}": ${data.question}`,
  `Use these ${scenes.length} scene images in order, one per shot, each held on screen for the length of its narration:`,
  ...scenes.map((s) => `${s.index}. ${s.file} -- "${s.heading}": ${s.narration}`),
  `The correct answer is ${data.correct_letter} (${data.correct_text}). No on-screen host or character, just the scene images with narration and captions per scene.`,
];

const manifest = {
  id: qid,
  question: data.question,
  correct_letter: data.correct_letter,
  correct_text: data.correct_text,
  scenes,
  prompt: promptLines.join("\n"),
};

const outFile = outFileArg || join(pngDirArg, `${qid}.rendley-manifest.json`);
writeFileSync(outFile, JSON.stringify(manifest, null, 2), "utf-8");
console.log(`Wrote Rendley manifest for ${qid} (${scenes.length} scenes) to ${outFile}`);
