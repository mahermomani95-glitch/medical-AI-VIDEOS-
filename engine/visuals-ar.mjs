// Generic, DATA-DRIVEN illustrations for the Arabic track. Real
// photographic/3D-rendered organ art isn't reachable from this sandbox
// (image CDNs are network-restricted), so these are hand-built SVGs pushed
// toward a "3D-ish" look with gradients + soft shadows rather than flat
// fills -- but unlike the original prototype (one bespoke SVG per
// question), every function here is parameterized so it can serve any of
// the 1031 questions, not just the two hand-illustrated samples.
//
// Each scene's script.json supplies an `illustration` object describing
// WHAT to draw generically:
//   { "type": "sequence", "steps": ["Small Bowel", "Stomach", "Colon"] }
//   { "type": "ladder", "items": [{"label":"II","active":false}, ...] }
//   { "type": "comparison", "left": {...}, "right": {...} }
//   { "type": "body", "region": "abdomen"|"chest"|"pelvis"|"limb"|"head", "label": "..." }
//   { "type": "icon" }  // generic fallback
// build_ar.mjs dispatches on `illustration.type` to the matching function
// below -- no per-question code needed for a new topic.

const PALETTE = ["#FFB4C6", "#FFD2A8", "#C9A6E8", "#B9F0FD", "#FCC63F", "#A8E6B0"];
const esc = (s = "") => String(s)
  .replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;");

// A left-to-right (or wrapped) chain of labeled steps connected by arrows.
// Optional per-step `sub` (small caption, e.g. a timing) and `blocked`
// (renders a red X over the connector, for "X prevents Y" mechanism scenes).
export function sequenceDiagramSvg(steps = []) {
  const n = steps.length || 1;
  const w = 560, h = 320;
  const boxW = Math.min(160, (w - 40) / n - 20);
  const gap = (w - 40 - boxW * n) / Math.max(1, n - 1);
  const y = 140;
  let boxes = "", arrows = "";
  steps.forEach((step, i) => {
    const label = typeof step === "string" ? step : step.label;
    const sub = typeof step === "object" ? step.sub : null;
    const blocked = typeof step === "object" && step.blocked;
    const x = 20 + i * (boxW + gap);
    const fill = PALETTE[i % PALETTE.length];
    boxes += `
      <rect x="${x}" y="${y}" width="${boxW}" height="86" rx="16" fill="${fill}" stroke="#111" stroke-width="3.5"/>
      <text x="${x + boxW / 2}" y="${y + 40}" text-anchor="middle" font-family="Anton, Arial" font-size="19" fill="#111">${esc(label)}</text>
      ${sub ? `<text x="${x + boxW / 2}" y="${y + 66}" text-anchor="middle" font-family="Cairo, Arial" font-weight="700" font-size="15" fill="#3a3a3a">${esc(sub)}</text>` : ""}
    `;
    if (i < n - 1) {
      const ax = x + boxW, bx = x + boxW + gap;
      arrows += `<line x1="${ax + 4}" y1="${y + 43}" x2="${bx - 4}" y2="${y + 43}" stroke="#111" stroke-width="4" marker-end="url(#arrowHead)"/>`;
      if (blocked) {
        const mx = (ax + bx) / 2;
        arrows += `<circle cx="${mx}" cy="${y + 43}" r="16" fill="#FF6B6B" stroke="#111" stroke-width="3"/><text x="${mx}" y="${y + 50}" text-anchor="middle" font-family="Anton, Arial" font-size="18" fill="#fff">X</text>`;
      }
    }
  });
  return `<svg viewBox="0 0 ${w} ${h}" xmlns="http://www.w3.org/2000/svg">
    <defs><marker id="arrowHead" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#111"/></marker></defs>
    ${arrows}
    ${boxes}
  </svg>`;
}

// A row of circular "markers" where one or more are highlighted (active)
// vs. muted -- generalizes "which of these N things is the exception".
export function ladderSvg(items = []) {
  const n = items.length || 1;
  const w = 560, h = 260;
  const r = 40;
  const spacing = (w - 80) / Math.max(1, n - 1 || 1);
  let circles = "";
  items.forEach((item, i) => {
    const label = typeof item === "string" ? item : item.label;
    const active = typeof item === "object" && item.active;
    const cx = n === 1 ? w / 2 : 40 + i * spacing;
    const cy = active ? 90 : 130;
    circles += `
      <circle cx="${cx}" cy="${cy}" r="${r}" fill="${active ? "#FCC63F" : "#C9A6E8"}" stroke="#111" stroke-width="3.5"/>
      <text x="${cx}" y="${cy + 8}" text-anchor="middle" font-family="Anton, Arial" font-size="22" fill="#111">${esc(label)}</text>
      <text x="${cx}" y="${cy + r + 30}" text-anchor="middle" font-family="Cairo, Arial" font-weight="700" font-size="16" fill="${active ? "#8a6a00" : "#5b3f8a"}">${active ? "✓" : ""}</text>
    `;
  });
  return `<svg viewBox="0 0 ${w} ${h}" xmlns="http://www.w3.org/2000/svg">
    <line x1="20" y1="180" x2="${w - 20}" y2="180" stroke="#111" stroke-width="2" stroke-dasharray="6 6" opacity="0.4"/>
    ${circles}
  </svg>`;
}

// Greedy word-wrap for SVG <text> (which never wraps on its own) -- splits
// on spaces so long Arabic/English notes render as multiple short lines
// instead of overflowing the card horizontally.
function wrapWords(str = "", maxChars = 20) {
  const words = String(str).split(" ").filter(Boolean);
  const lines = [];
  let cur = "";
  for (const word of words) {
    const test = cur ? `${cur} ${word}` : word;
    if (test.length > maxChars && cur) { lines.push(cur); cur = word; }
    else cur = test;
  }
  if (cur) lines.push(cur);
  return lines;
}

// Two side-by-side boxes (normal vs. disease, option vs. option, before vs. after).
// Box height grows with the wrapped note length so longer explanations (any
// of the 1031 questions' own wording, not just short demo text) never spill
// out of the card.
export function comparisonDiagramSvg(left = {}, right = {}) {
  const boxW = 250;
  const leftLines = wrapWords(left.note, 20);
  const rightLines = wrapWords(right.note, 20);
  const maxLines = Math.max(leftLines.length, rightLines.length, 1);
  const boxH = Math.min(340, 150 + maxLines * 24);
  const w = 560, h = boxH + 60;
  const box = (x, data, good, lines) => {
    const noteTop = boxH - (lines.length - 1) * 24 - 34;
    const noteTspans = lines.map((line, i) =>
      `<tspan x="${x + boxW - 20}" dy="${i === 0 ? 0 : 24}">${esc(line)}</tspan>`).join("");
    return `
    <rect x="${x}" y="30" width="${boxW}" height="${boxH}" rx="20" fill="${good === true ? "#DFF5E1" : good === false ? "#FFD9D9" : "#F3E9FB"}" stroke="#111" stroke-width="3.5"/>
    <text x="${x + 20}" y="70" font-family="Anton, Arial" font-size="22" fill="#111">${esc(data.title || "")}</text>
    <text text-anchor="end" font-family="Cairo, Arial" font-weight="700" font-size="17" fill="#333" y="${30 + noteTop}">${noteTspans}</text>
    ${good !== undefined ? `<text x="${x + boxW - 40}" y="70" font-family="Anton, Arial" font-size="26" fill="${good ? "#2e7a45" : "#a02a2a"}">${good ? "✓" : "✕"}</text>` : ""}
  `;
  };
  return `<svg viewBox="0 0 ${w} ${h}" xmlns="http://www.w3.org/2000/svg">
    ${box(20, left, left.good, leftLines)}
    ${box(290, right, right.good, rightLines)}
  </svg>`;
}

// Generic body-region silhouette with a highlighted spot + label -- not
// anatomically detailed (no real medical image assets are reachable), but
// gives a consistent, on-brand visual anchor for "where in the body" per
// question without needing bespoke art each time.
const BODY_SHAPES = {
  abdomen: `<ellipse cx="280" cy="230" rx="120" ry="150" fill="#FFD2A8" stroke="#111" stroke-width="3.5"/>`,
  chest: `<path d="M180 100 q100 -50 200 0 v180 q-100 50 -200 0 z" fill="#FFB4C6" stroke="#111" stroke-width="3.5"/>`,
  pelvis: `<path d="M200 150 q80 -30 160 0 v100 q-30 60 -80 60 t-80 -60 z" fill="#C9A6E8" stroke="#111" stroke-width="3.5"/>`,
  limb: `<rect x="240" y="60" width="80" height="320" rx="40" fill="#B9F0FD" stroke="#111" stroke-width="3.5"/>`,
  head: `<circle cx="280" cy="200" r="130" fill="#FFD988" stroke="#111" stroke-width="3.5"/>`,
  generic: `<rect x="160" y="100" width="240" height="240" rx="30" fill="#B9F0FD" stroke="#111" stroke-width="3.5"/>`,
};
export function bodyRegionSvg(region = "generic", label = "") {
  const shape = BODY_SHAPES[region] || BODY_SHAPES.generic;
  return `<svg viewBox="0 0 560 420" xmlns="http://www.w3.org/2000/svg">
    ${shape}
    <circle cx="280" cy="230" r="18" fill="#FF6B6B" stroke="#111" stroke-width="3"/>
    ${label ? `<rect x="130" y="360" width="300" height="40" rx="10" fill="#fff" stroke="#111" stroke-width="2.5"/>
    <text x="150" y="386" font-family="Cairo, Arial" font-weight="700" font-size="19" fill="#111">${esc(label)}</text>` : ""}
  </svg>`;
}

// Generic fallback icon (a caduceus-ish cross-in-circle) for a scene with
// no specific illustration data -- keeps the visual brand consistent
// without implying a diagram that isn't actually there.
export function genericIconSvg() {
  return `<svg viewBox="0 0 300 300" xmlns="http://www.w3.org/2000/svg">
    <circle cx="150" cy="150" r="120" fill="#B9F0FD" stroke="#111" stroke-width="4"/>
    <rect x="130" y="80" width="40" height="140" rx="8" fill="#111"/>
    <rect x="80" y="130" width="140" height="40" rx="8" fill="#111"/>
  </svg>`;
}

export function illustrationSvg(illustration) {
  if (!illustration || !illustration.type) return genericIconSvg();
  switch (illustration.type) {
    case "sequence": return sequenceDiagramSvg(illustration.steps || []);
    case "ladder": return ladderSvg(illustration.items || []);
    case "comparison": return comparisonDiagramSvg(illustration.left || {}, illustration.right || {});
    case "body": return bodyRegionSvg(illustration.region, illustration.label);
    case "icon":
    default: return genericIconSvg();
  }
}
