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
