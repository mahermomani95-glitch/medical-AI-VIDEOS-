// Shaded (gradient-based) anatomical illustrations for the Arabic track.
// Real photographic/3D-rendered organ art isn't reachable from this sandbox
// (image CDNs are network-restricted), so these are hand-built SVGs pushed
// toward a "3D-ish" look with gradients + soft shadows rather than flat fills.

export function giTractIllustrationSvg() {
  return `<svg viewBox="0 0 560 520" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="stomachG" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#FFB4C6"/>
      <stop offset="100%" stop-color="#F0728F"/>
    </linearGradient>
    <linearGradient id="smallBowelG" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#FFD2A8"/>
      <stop offset="100%" stop-color="#F2A25C"/>
    </linearGradient>
    <linearGradient id="colonG" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#C9A6E8"/>
      <stop offset="100%" stop-color="#9A63C9"/>
    </linearGradient>
    <filter id="softShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="#000000" flood-opacity="0.25"/>
    </filter>
  </defs>

  <!-- Colon frame (outer) -->
  <path d="M60 120 h380 a40 40 0 0 1 40 40 v260 a40 40 0 0 1 -40 40 h-320 a40 40 0 0 1 -40 -40 v-40"
        fill="none" stroke="url(#colonG)" stroke-width="52" stroke-linecap="round" filter="url(#softShadow)"/>

  <!-- Stomach -->
  <path d="M90 70 c-30 10 -46 40 -34 72 c10 26 42 34 70 26 c22 -6 30 6 52 6 c26 0 40 -20 34 -44 c-6 -24 -30 -30 -46 -46 c-14 -14 -46 -26 -76 -14 z"
        fill="url(#stomachG)" stroke="#7A2E42" stroke-width="4" filter="url(#softShadow)"/>

  <!-- Small bowel coils -->
  <g fill="none" stroke="url(#smallBowelG)" stroke-width="26" stroke-linecap="round">
    <path d="M180 220 q60 -20 120 0 t120 0"/>
    <path d="M170 270 q60 20 120 0 t120 0"/>
    <path d="M180 320 q60 -20 120 0 t100 10"/>
  </g>

  <!-- Labels -->
  <g font-family="Cairo, Arial, sans-serif" font-weight="700" font-size="22" fill="#1a1a1a">
    <rect x="20" y="30" width="150" height="34" rx="8" fill="#FFFFFF" stroke="#111" stroke-width="2"/>
    <text x="35" y="53">Stomach</text>
    <line x1="60" y1="64" x2="100" y2="90" stroke="#111" stroke-width="2"/>

    <rect x="330" y="200" width="200" height="34" rx="8" fill="#FFFFFF" stroke="#111" stroke-width="2"/>
    <text x="345" y="223">Small Bowel</text>
    <line x1="330" y1="217" x2="290" y2="240" stroke="#111" stroke-width="2"/>

    <rect x="20" y="430" width="130" height="34" rx="8" fill="#FFFFFF" stroke="#111" stroke-width="2"/>
    <text x="35" y="453">Colon</text>
    <line x1="80" y1="430" x2="90" y2="400" stroke="#111" stroke-width="2"/>
  </g>
</svg>`;
}

export function biliaryMechanismArSvg() {
  return `<svg viewBox="0 0 560 420" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="liverG" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#C9705E"/>
      <stop offset="100%" stop-color="#8C4436"/>
    </linearGradient>
    <filter id="sh1" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="6" stdDeviation="7" flood-color="#000" flood-opacity="0.25"/>
    </filter>
  </defs>
  <!-- Liver -->
  <path d="M60 60 c-20 20 -20 70 20 90 c40 20 140 20 200 0 c50 -18 60 -70 20 -100 c-40 -30 -180 -30 -240 10 z"
        fill="url(#liverG)" stroke="#5c2a20" stroke-width="4" filter="url(#sh1)"/>
  <rect x="20" y="24" width="90" height="34" rx="8" fill="#fff" stroke="#111" stroke-width="2"/>
  <text x="34" y="47" font-family="Cairo, Arial" font-weight="700" font-size="20">Liver</text>

  <!-- Bile duct -->
  <path d="M220 150 q0 60 0 100" stroke="#5b7a3a" stroke-width="16" fill="none" stroke-linecap="round"/>
  <!-- Blockage -->
  <circle cx="220" cy="210" r="22" fill="#FF6B6B" stroke="#111" stroke-width="3"/>
  <text x="220" y="217" text-anchor="middle" font-family="Anton, Arial" font-size="22" fill="#fff">X</text>
  <rect x="250" y="196" width="150" height="32" rx="8" fill="#fff" stroke="#111" stroke-width="2"/>
  <text x="264" y="218" font-family="Cairo, Arial" font-weight="700" font-size="18">Bile Duct Blocked</text>

  <!-- Intestine -->
  <path d="M140 320 q40 -20 80 0 t80 0 t80 0" stroke="#F2A25C" stroke-width="20" fill="none" stroke-linecap="round"/>
  <rect x="130" y="350" width="180" height="32" rx="8" fill="#fff" stroke="#111" stroke-width="2"/>
  <text x="145" y="372" font-family="Cairo, Arial" font-weight="700" font-size="18">Small Intestine</text>

  <!-- Vitamin K fading -->
  <g opacity="0.55">
    <circle cx="380" cy="330" r="26" fill="#B9F0FD" stroke="#111" stroke-width="2.5" stroke-dasharray="4 4"/>
    <text x="380" y="336" text-anchor="middle" font-family="Anton, Arial" font-size="18">K</text>
  </g>
  <text x="330" y="400" font-family="Cairo, Arial" font-weight="700" font-size="18" fill="#7a2e2e">Vitamin K malabsorption</text>
</svg>`;
}

export function cascadeArSvg() {
  return `<svg viewBox="0 0 560 320" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="kGroupG" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#C9A6E8"/>
      <stop offset="100%" stop-color="#9A63C9"/>
    </linearGradient>
  </defs>
  <rect x="30" y="30" width="340" height="140" rx="20" fill="#F3E9FB" stroke="#111" stroke-width="3"/>
  <text x="50" y="60" font-family="Anton, Arial" font-size="22" fill="#6b3fa0">Vitamin K–Dependent</text>
  <g font-family="Anton, Arial" font-size="26" fill="#fff">
    <circle cx="80" cy="115" r="34" fill="url(#kGroupG)" stroke="#111" stroke-width="3"/>
    <text x="80" y="123" text-anchor="middle">II</text>
    <circle cx="160" cy="115" r="34" fill="url(#kGroupG)" stroke="#111" stroke-width="3"/>
    <text x="160" y="123" text-anchor="middle">VII</text>
    <circle cx="240" cy="115" r="34" fill="url(#kGroupG)" stroke="#111" stroke-width="3"/>
    <text x="240" y="123" text-anchor="middle">IX</text>
    <circle cx="320" cy="115" r="34" fill="url(#kGroupG)" stroke="#111" stroke-width="3"/>
    <text x="320" y="123" text-anchor="middle">X</text>
  </g>

  <line x1="200" y1="170" x2="200" y2="210" stroke="#111" stroke-width="3" stroke-dasharray="5 5"/>
  <text x="120" y="205" font-family="Cairo, Arial" font-weight="700" font-size="18" fill="#7a2e2e">كلها تنخفض معًا ↓</text>

  <rect x="420" y="60" width="120" height="120" rx="20" fill="#FFE7A3" stroke="#111" stroke-width="3"/>
  <circle cx="480" cy="110" r="34" fill="${'#FCC63F'}" stroke="#111" stroke-width="3"/>
  <text x="480" y="118" text-anchor="middle" font-family="Anton, Arial" font-size="24" fill="#111">VIII</text>
  <text x="420" y="205" font-family="Cairo, Arial" font-weight="700" font-size="18" fill="#5b7a3a">يبقى طبيعيًا ✓</text>
</svg>`;
}

export function factorEightArSvg() {
  return `<svg viewBox="0 0 560 300" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="vesselG" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#F5A0B8"/>
      <stop offset="100%" stop-color="#D45C82"/>
    </linearGradient>
  </defs>
  <rect x="40" y="120" width="480" height="70" rx="35" fill="url(#vesselG)" stroke="#111" stroke-width="4"/>
  <rect x="40" y="145" width="480" height="20" fill="#7a1f3d" opacity="0.35"/>
  <g font-family="Anton, Arial" font-size="20" fill="#fff">
    <circle cx="120" cy="155" r="14" fill="#FCC63F" stroke="#111" stroke-width="2"/>
    <circle cx="280" cy="155" r="14" fill="#FCC63F" stroke="#111" stroke-width="2"/>
    <circle cx="430" cy="155" r="14" fill="#FCC63F" stroke="#111" stroke-width="2"/>
  </g>
  <rect x="150" y="40" width="260" height="36" rx="8" fill="#fff" stroke="#111" stroke-width="2"/>
  <text x="165" y="64" font-family="Cairo, Arial" font-weight="700" font-size="20">Vascular Endothelium</text>
  <rect x="180" y="220" width="200" height="36" rx="8" fill="#fff" stroke="#111" stroke-width="2"/>
  <text x="195" y="244" font-family="Cairo, Arial" font-weight="700" font-size="20">Factor VIII made here</text>
</svg>`;
}

export function factorFiveArSvg() {
  return `<svg viewBox="0 0 560 260" xmlns="http://www.w3.org/2000/svg">
  <rect x="30" y="30" width="230" height="180" rx="20" fill="#FFE7A3" stroke="#111" stroke-width="3"/>
  <text x="55" y="65" font-family="Anton, Arial" font-size="22">Vitamin K low only</text>
  <text x="55" y="100" font-family="Cairo, Arial" font-weight="700" font-size="18">Factor V:</text>
  <text x="150" y="100" font-family="Anton, Arial" font-size="20" fill="#2e7a45">Normal ✓</text>
  <text x="55" y="140" font-family="Cairo, Arial" font-weight="700" font-size="16" fill="#555">(not Vitamin K–dependent)</text>

  <rect x="300" y="30" width="230" height="180" rx="20" fill="#FFD3D3" stroke="#111" stroke-width="3"/>
  <text x="325" y="65" font-family="Anton, Arial" font-size="22">True Liver Failure</text>
  <text x="325" y="100" font-family="Cairo, Arial" font-weight="700" font-size="18">Factor V:</text>
  <text x="420" y="100" font-family="Anton, Arial" font-size="20" fill="#a02a2a">Low ✕</text>
  <text x="325" y="140" font-family="Cairo, Arial" font-weight="700" font-size="16" fill="#555">(hepatocytes only)</text>
</svg>`;
}

export function timelineIllustrationSvg() {
  return `<svg viewBox="0 0 560 300" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="barG" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#F2A25C"/>
      <stop offset="100%" stop-color="#9A63C9"/>
    </linearGradient>
  </defs>
  <line x1="40" y1="260" x2="520" y2="260" stroke="#111" stroke-width="4"/>
  <g font-family="Cairo, Arial, sans-serif" font-weight="700" font-size="20" fill="#111">
    <circle cx="90" cy="150" r="16" fill="#FFD2A8" stroke="#111" stroke-width="3"/>
    <text x="40" y="200">Small Bowel</text>
    <text x="55" y="225" font-size="18" fill="#5b4a22">~24h</text>

    <circle cx="280" cy="110" r="16" fill="#FFB4C6" stroke="#111" stroke-width="3"/>
    <text x="235" y="200">Stomach</text>
    <text x="235" y="225" font-size="18" fill="#5b4a22">24–48h</text>

    <circle cx="470" cy="70" r="16" fill="#C9A6E8" stroke="#111" stroke-width="3"/>
    <text x="420" y="200">Colon</text>
    <text x="410" y="225" font-size="18" fill="#5b4a22">48–72h+</text>
  </g>
  <path d="M90 150 L280 110 L470 70" fill="none" stroke="url(#barG)" stroke-width="8" stroke-linecap="round"/>
</svg>`;
}
