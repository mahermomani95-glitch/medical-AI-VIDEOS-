// Hand-built, dependency-free SVG diagrams for the single-narrator
// English teaching pipeline. Style follows DESIGN.md: dark navy canvas,
// cyan clinical accent, amber for exam-trap/warning emphasis, clean 2D
// medical diagrams, no clutter.

const CYAN = "#55D6E8";
const CYAN2 = "#19C3B1";
const AMBER = "#FFB454";
const TEXT = "#F5F8FC";
const PANEL = "#10243D";
const MUTED = "#7C93AC";

export function biliaryMechanismSvg() {
  return `
  <svg viewBox="0 0 900 420" xmlns="http://www.w3.org/2000/svg">
    <!-- Liver -->
    <path d="M120 120 Q80 90 130 60 Q220 20 320 60 Q380 85 360 150 Q340 210 250 210 Q140 210 120 120 Z"
          fill="${PANEL}" stroke="${CYAN}" stroke-width="3"/>
    <text x="230" y="130" text-anchor="middle" fill="${TEXT}" font-size="26" font-weight="700">LIVER</text>

    <!-- Bile duct -->
    <path d="M230 210 L230 260 L400 260" fill="none" stroke="${CYAN2}" stroke-width="10" stroke-linecap="round"/>
    <!-- Obstruction (stone) -->
    <circle cx="400" cy="260" r="22" fill="${AMBER}"/>
    <text x="400" y="230" text-anchor="middle" fill="${AMBER}" font-size="20" font-weight="700">Gallstone / Obstruction</text>
    <!-- Blocked path (dashed, faded) -->
    <path d="M422 260 L620 260" fill="none" stroke="${MUTED}" stroke-width="10" stroke-linecap="round" stroke-dasharray="4 14" opacity="0.5"/>
    <text x="520" y="240" text-anchor="middle" fill="${MUTED}" font-size="18">bile flow blocked</text>

    <!-- Intestine -->
    <path d="M620 220 q40 -20 80 0 q40 20 0 40 q-40 20 0 40 q40 20 -20 40 q-60 20 -60 -30"
          fill="none" stroke="${CYAN}" stroke-width="8"/>
    <text x="660" y="180" text-anchor="middle" fill="${TEXT}" font-size="22" font-weight="700">SMALL INTESTINE</text>

    <!-- Fat + Vitamin K absorption, crossed out -->
    <g transform="translate(700,290)">
      <rect x="-90" y="-30" width="220" height="80" rx="14" fill="${PANEL}" stroke="${AMBER}" stroke-width="2"/>
      <text x="20" y="0" text-anchor="middle" fill="${TEXT}" font-size="18" font-weight="700">Fat + Vitamin K</text>
      <text x="20" y="26" text-anchor="middle" fill="${AMBER}" font-size="18" font-weight="800">absorption ✕</text>
    </g>

    <!-- Downstream: liver can't activate II VII IX X -->
    <g transform="translate(140,330)">
      <text x="0" y="0" fill="${MUTED}" font-size="20">No Vitamin K reaching the liver →</text>
      <text x="0" y="30" fill="${AMBER}" font-size="24" font-weight="800">Factors II · VII · IX · X stay INACTIVE</text>
    </g>
  </svg>`;
}

export function cascadeDiagramSvg() {
  const factors = [
    { n: "II", note: "Prothrombin", dep: true },
    { n: "VII", note: "shortest half-life", dep: true },
    { n: "IX", note: "", dep: true },
    { n: "X", note: "", dep: true },
    { n: "VIII", note: "NOT Vitamin K-dependent", dep: false },
  ];
  const boxes = factors.map((f, i) => {
    const x = 60 + i * 165;
    const color = f.dep ? AMBER : CYAN;
    return `
    <g transform="translate(${x},60)">
      <rect width="140" height="140" rx="16" fill="${PANEL}" stroke="${color}" stroke-width="${f.dep ? 3 : 4}"/>
      <text x="70" y="60" text-anchor="middle" fill="${color}" font-size="34" font-weight="800">${f.n}</text>
      <text x="70" y="90" text-anchor="middle" fill="${TEXT}" font-size="13">${f.dep ? "Vitamin K-dependent" : "Independent"}</text>
      ${f.note ? `<text x="70" y="112" text-anchor="middle" fill="${MUTED}" font-size="11">${f.note}</text>` : ""}
    </g>`;
  }).join("");

  return `
  <svg viewBox="0 0 900 260" xmlns="http://www.w3.org/2000/svg">
    <text x="450" y="30" text-anchor="middle" fill="${TEXT}" font-size="20" font-weight="700">Vitamin K-Dependent Factors vs. Factor VIII</text>
    ${boxes}
    <text x="285" y="230" text-anchor="middle" fill="${AMBER}" font-size="16" font-weight="700">↓ all reduced in obstructive jaundice</text>
    <text x="750" y="230" text-anchor="middle" fill="${CYAN}" font-size="16" font-weight="700">stays normal / ↑</text>
  </svg>`;
}

export function wrongOptionsSvg() {
  const rows = [
    ["A", "Factor II", "Vitamin K-dependent → reduced"],
    ["B", "Factor VII", "Vitamin K-dependent → reduced"],
    ["D", "Factor IX", "Vitamin K-dependent → reduced"],
    ["E", "Factor X", "Vitamin K-dependent → reduced"],
  ];
  const items = rows.map((r, i) => `
    <g transform="translate(0, ${i * 66})">
      <rect width="820" height="52" rx="12" fill="${PANEL}" stroke="${AMBER}" stroke-width="2" opacity="0.85"/>
      <text x="24" y="34" fill="${AMBER}" font-size="22" font-weight="800">${r[0]}</text>
      <text x="70" y="34" fill="${TEXT}" font-size="20" font-weight="700">${r[1]}</text>
      <text x="820" y="34" text-anchor="end" fill="${MUTED}" font-size="16">${r[2]}</text>
    </g>`).join("");
  return `
  <svg viewBox="0 0 860 300" xmlns="http://www.w3.org/2000/svg">
    ${items}
  </svg>`;
}

export function factorEightSvg() {
  return `
  <svg viewBox="0 0 900 340" xmlns="http://www.w3.org/2000/svg">
    <!-- Vessel wall -->
    <rect x="80" y="120" width="740" height="60" rx="30" fill="none" stroke="${CYAN}" stroke-width="4"/>
    <text x="450" y="105" text-anchor="middle" fill="${TEXT}" font-size="20" font-weight="700">Vascular Endothelium (blood vessel lining)</text>
    <!-- Factor VIII released -->
    <g fill="${CYAN}">
      <circle cx="220" cy="150" r="10"/><circle cx="330" cy="150" r="10"/>
      <circle cx="450" cy="150" r="10"/><circle cx="570" cy="150" r="10"/><circle cx="680" cy="150" r="10"/>
    </g>
    <text x="450" y="230" text-anchor="middle" fill="${CYAN}" font-size="24" font-weight="800">Factor VIII made here — not by hepatocytes</text>
    <text x="450" y="264" text-anchor="middle" fill="${TEXT}" font-size="18">No Vitamin K needed → unaffected by obstructive jaundice</text>
    <text x="450" y="300" text-anchor="middle" fill="${AMBER}" font-size="18" font-weight="700">Often normal, sometimes even elevated</text>
  </svg>`;
}

export function factorFiveSvg() {
  return `
  <svg viewBox="0 0 900 300" xmlns="http://www.w3.org/2000/svg">
    <g transform="translate(60,50)">
      <rect width="360" height="200" rx="16" fill="${PANEL}" stroke="${CYAN}" stroke-width="3"/>
      <text x="180" y="42" text-anchor="middle" fill="${CYAN}" font-size="20" font-weight="800">Vitamin K Deficiency</text>
      <text x="180" y="90" text-anchor="middle" fill="${TEXT}" font-size="18">Factor V: NORMAL</text>
      <text x="180" y="120" text-anchor="middle" fill="${MUTED}" font-size="14">liver cells intact,</text>
      <text x="180" y="140" text-anchor="middle" fill="${MUTED}" font-size="14">just missing Vitamin K</text>
      <text x="180" y="175" text-anchor="middle" fill="${TEXT}" font-size="16">→ obstructive jaundice</text>
    </g>
    <g transform="translate(480,50)">
      <rect width="360" height="200" rx="16" fill="${PANEL}" stroke="${AMBER}" stroke-width="3"/>
      <text x="180" y="42" text-anchor="middle" fill="${AMBER}" font-size="20" font-weight="800">True Liver Failure</text>
      <text x="180" y="90" text-anchor="middle" fill="${TEXT}" font-size="18">Factor V: LOW</text>
      <text x="180" y="120" text-anchor="middle" fill="${MUTED}" font-size="14">hepatocytes themselves</text>
      <text x="180" y="140" text-anchor="middle" fill="${MUTED}" font-size="14">can't synthesize it</text>
      <text x="180" y="175" text-anchor="middle" fill="${TEXT}" font-size="16">→ synthetic failure</text>
    </g>
  </svg>`;
}

export function questionCardSvg(options, correctLetter) {
  const items = options.map((o, i) => {
    const isCorrect = o.letter === correctLetter;
    return `
    <g transform="translate(0, ${i * 52})">
      <rect width="640" height="42" rx="10" fill="${PANEL}" stroke="${MUTED}" stroke-width="1.5" opacity="0.9"/>
      <text x="18" y="28" fill="${TEXT}" font-size="18" font-weight="700">${o.letter}.</text>
      <text x="55" y="28" fill="${TEXT}" font-size="18">${o.text}</text>
    </g>`;
  }).join("");
  return `<svg viewBox="0 0 660 ${options.length * 52 + 10}" xmlns="http://www.w3.org/2000/svg">${items}</svg>`;
}

export function summaryCardSvg(summaryLine, correctLetter, correctText) {
  return `
  <svg viewBox="0 0 900 220" xmlns="http://www.w3.org/2000/svg">
    <rect x="150" y="30" width="600" height="160" rx="20" fill="${PANEL}" stroke="${CYAN}" stroke-width="3"/>
    <text x="450" y="80" text-anchor="middle" fill="${MUTED}" font-size="17">${summaryLine}</text>
    <text x="450" y="130" text-anchor="middle" fill="${CYAN}" font-size="26" font-weight="800">${correctText}</text>
    <text x="450" y="165" text-anchor="middle" fill="${AMBER}" font-size="20" font-weight="700">Correct answer: ${correctLetter}</text>
  </svg>`;
}

// ---- GI motility recovery question (surgery-6mo2013-01) ----

export function postopIleusMechanismSvg() {
  const causes = ["Surgical\nhandling", "Sympathetic\nactivation", "Inflammatory\nmediators", "Opioid\nanalgesia"];
  const boxes = causes.map((c, i) => `
    <g transform="translate(${20 + i * 200},20)">
      <rect width="170" height="70" rx="14" fill="${PANEL}" stroke="${AMBER}" stroke-width="2"/>
      ${c.split("\n").map((line, li) => `<text x="85" y="${32 + li * 20}" text-anchor="middle" fill="${TEXT}" font-size="15" font-weight="700">${line}</text>`).join("")}
    </g>`).join("");
  return `
  <svg viewBox="0 0 900 260" xmlns="http://www.w3.org/2000/svg">
    ${boxes}
    <text x="450" y="130" text-anchor="middle" fill="${MUTED}" font-size="20">↓ all feed into ↓</text>
    <rect x="280" y="150" width="340" height="60" rx="30" fill="${PANEL}" stroke="${AMBER}" stroke-width="3"/>
    <text x="450" y="187" text-anchor="middle" fill="${AMBER}" font-size="22" font-weight="800">Postoperative Ileus</text>
    <text x="450" y="240" text-anchor="middle" fill="${CYAN}" font-size="17">but NOT uniform — each gut segment recovers on its own clock</text>
  </svg>`;
}

export function giTimelineSvg() {
  const stops = [
    { organ: "Small Bowel", time: "~24 hours", x: 140, color: CYAN },
    { organ: "Stomach", time: "~24–48 hours", x: 450, color: CYAN2 },
    { organ: "Colon", time: "~48–72+ hours", x: 760, color: AMBER },
  ];
  const line = `<line x1="90" y1="130" x2="810" y2="130" stroke="${MUTED}" stroke-width="4"/>`;
  const nodes = stops.map((s) => `
    <g>
      <circle cx="${s.x}" cy="130" r="14" fill="${s.color}"/>
      <text x="${s.x}" y="95" text-anchor="middle" fill="${TEXT}" font-size="22" font-weight="800">${s.organ}</text>
      <text x="${s.x}" y="165" text-anchor="middle" fill="${s.color}" font-size="18" font-weight="700">${s.time}</text>
    </g>`).join("");
  return `
  <svg viewBox="0 0 900 220" xmlns="http://www.w3.org/2000/svg">
    <text x="450" y="30" text-anchor="middle" fill="${TEXT}" font-size="20" font-weight="700">Recovery Timeline — Fastest to Slowest</text>
    ${line}${nodes}
    <text x="140" y="200" text-anchor="middle" fill="${MUTED}" font-size="14">1st</text>
    <text x="450" y="200" text-anchor="middle" fill="${MUTED}" font-size="14">2nd</text>
    <text x="760" y="200" text-anchor="middle" fill="${MUTED}" font-size="14">3rd (last)</text>
  </svg>`;
}

export function wrongOptionsGiSvg() {
  const rows = [
    ["A", "Stomach → Colon → Small bowel", "Reverses the entire order"],
    ["B", "Colon → Small bowel → Stomach", "Colon is actually last, not first"],
    ["C", "Stomach → Small bowel → Colon", "Swaps the 1st and 2nd organs"],
    ["E", "Small bowel → Colon → Stomach", "Swaps the 2nd and 3rd organs"],
  ];
  const items = rows.map((r, i) => `
    <g transform="translate(0, ${i * 66})">
      <rect width="860" height="52" rx="12" fill="${PANEL}" stroke="${AMBER}" stroke-width="2" opacity="0.85"/>
      <text x="24" y="34" fill="${AMBER}" font-size="22" font-weight="800">${r[0]}</text>
      <text x="70" y="34" fill="${TEXT}" font-size="19" font-weight="700">${r[1]}</text>
      <text x="850" y="34" text-anchor="end" fill="${MUTED}" font-size="15">${r[2]}</text>
    </g>`).join("");
  return `<svg viewBox="0 0 900 300" xmlns="http://www.w3.org/2000/svg">${items}</svg>`;
}

export function correctAnswerGiSvg() {
  return `
  <svg viewBox="0 0 900 260" xmlns="http://www.w3.org/2000/svg">
    <g transform="translate(60,60)">
      <rect width="230" height="130" rx="16" fill="${PANEL}" stroke="${CYAN}" stroke-width="4"/>
      <text x="115" y="55" text-anchor="middle" fill="${CYAN}" font-size="22" font-weight="800">Small Bowel</text>
      <text x="115" y="90" text-anchor="middle" fill="${TEXT}" font-size="16">most active myenteric</text>
      <text x="115" y="110" text-anchor="middle" fill="${TEXT}" font-size="16">activity → recovers 1st</text>
    </g>
    <text x="330" y="130" text-anchor="middle" fill="${MUTED}" font-size="26">→</text>
    <g transform="translate(360,60)">
      <rect width="230" height="130" rx="16" fill="${PANEL}" stroke="${CYAN2}" stroke-width="3"/>
      <text x="115" y="55" text-anchor="middle" fill="${CYAN2}" font-size="22" font-weight="800">Stomach</text>
      <text x="115" y="90" text-anchor="middle" fill="${TEXT}" font-size="16">slower peristalsis</text>
      <text x="115" y="110" text-anchor="middle" fill="${TEXT}" font-size="16">return → 2nd</text>
    </g>
    <text x="630" y="130" text-anchor="middle" fill="${MUTED}" font-size="26">→</text>
    <g transform="translate(660,60)">
      <rect width="230" height="130" rx="16" fill="${PANEL}" stroke="${AMBER}" stroke-width="3"/>
      <text x="115" y="55" text-anchor="middle" fill="${AMBER}" font-size="22" font-weight="800">Colon</text>
      <text x="115" y="90" text-anchor="middle" fill="${TEXT}" font-size="16">slowest baseline</text>
      <text x="115" y="110" text-anchor="middle" fill="${TEXT}" font-size="16">motility → last</text>
    </g>
    <text x="450" y="235" text-anchor="middle" fill="${CYAN}" font-size="22" font-weight="800">= Option D</text>
  </svg>`;
}

export function erasPearlSvg() {
  return `
  <svg viewBox="0 0 900 260" xmlns="http://www.w3.org/2000/svg">
    <g transform="translate(60,40)">
      <rect width="360" height="180" rx="16" fill="${PANEL}" stroke="${CYAN}" stroke-width="3"/>
      <text x="180" y="42" text-anchor="middle" fill="${CYAN}" font-size="20" font-weight="800">ERAS Protocols</text>
      <text x="180" y="90" text-anchor="middle" fill="${TEXT}" font-size="16">Start early enteral feeding</text>
      <text x="180" y="115" text-anchor="middle" fill="${TEXT}" font-size="16">within ~24h — before bowel</text>
      <text x="180" y="140" text-anchor="middle" fill="${TEXT}" font-size="16">sounds or flatus return</text>
    </g>
    <g transform="translate(480,40)">
      <rect width="360" height="180" rx="16" fill="${PANEL}" stroke="${AMBER}" stroke-width="3"/>
      <text x="180" y="42" text-anchor="middle" fill="${AMBER}" font-size="20" font-weight="800">Bedside Signs</text>
      <text x="180" y="90" text-anchor="middle" fill="${TEXT}" font-size="16">Bowel sounds / flatus reflect</text>
      <text x="180" y="115" text-anchor="middle" fill="${TEXT}" font-size="16">STOMACH & COLON recovery —</text>
      <text x="180" y="140" text-anchor="middle" fill="${TEXT}" font-size="16">small bowel return is silent</text>
    </g>
  </svg>`;
}

export const VISUAL_MAP = {
  biliary_mechanism: () => biliaryMechanismSvg(),
  cascade_diagram: () => cascadeDiagramSvg(),
  wrong_options: () => wrongOptionsSvg(),
  factor_eight_highlight: () => factorEightSvg(),
  factor_five_pearl: () => factorFiveSvg(),
  postop_ileus_mechanism: () => postopIleusMechanismSvg(),
  gi_timeline_diagram: () => giTimelineSvg(),
  wrong_options_gi: () => wrongOptionsGiSvg(),
  correct_answer_gi: () => correctAnswerGiSvg(),
  eras_pearl: () => erasPearlSvg(),
};
