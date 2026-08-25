#!/usr/bin/env node
// Screenshot every scene HTML for one or more questions into PNGs.
//
// The scene PNGs are build output, not source: at 1031 questions they'd be
// 8000+ binary files (~1GB) in git. So CI builds and shoots them on the fly
// instead, and only the finished MP4s are published (as Release assets).
//
// Usage: node shoot_scenes.mjs <sceneDir> <id> [<id> ...]
//   Shoots <sceneDir>/<id>-ar.scene*.html -> matching .png

import { chromium } from "playwright";
import { readdirSync } from "node:fs";
import { resolve } from "node:path";

const [, , sceneDirArg, ...ids] = process.argv;
if (!sceneDirArg || ids.length === 0) {
  console.error("Usage: node shoot_scenes.mjs <sceneDir> <id> [<id> ...]");
  process.exit(1);
}
const sceneDir = resolve(sceneDirArg);

const browser = await chromium.launch({
  executablePath: process.env.PLAYWRIGHT_CHROMIUM_PATH || undefined,
});
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });

let shot = 0;
for (const id of ids) {
  const prefix = `${id}-ar.scene`;
  const files = readdirSync(sceneDir)
    .filter((f) => f.startsWith(prefix) && f.endsWith(".html"))
    .sort();
  if (files.length === 0) {
    console.error(`::warning::no scene HTML found for ${id} in ${sceneDir}`);
    continue;
  }
  for (const f of files) {
    await page.goto(`file://${sceneDir}/${f}`, { waitUntil: "load" });
    // Give webfonts a beat to settle so text isn't shot mid-swap.
    await page.evaluate(() => document.fonts && document.fonts.ready);
    await page.screenshot({ path: `${sceneDir}/${f.replace(/\.html$/, ".png")}` });
    shot++;
  }
}

await browser.close();
console.log(`Shot ${shot} scene PNGs for ${ids.length} question(s)`);
