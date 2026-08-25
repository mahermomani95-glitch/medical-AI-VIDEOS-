// Shared design system for the Arabic track, reverse-engineered from the
// reference video the user sent (warm amber background, pink/cyan
// "neubrutalist" cards with black borders + offset color shadows, bold
// condensed Anton headlines, Cairo for Arabic text, black pill caption bar).

export const TOKENS = {
  bg: "#FFD988",
  pink: "#FF9FE9",
  cyan: "#B9F0FD",
  gold: "#FCC63F",
  ink: "#111111",
  white: "#FFFFFF",
};

export const FONT_FACES = `
@font-face {
  font-family: "Anton";
  src: url("../assets/fonts/Anton-Regular.ttf") format("truetype");
  font-weight: 400;
}
@font-face {
  font-family: "Cairo";
  src: url("../assets/fonts/Cairo-Variable.ttf") format("truetype-variations");
  font-weight: 200 900;
}
`;

export const BASE_STYLE_AR = `
${FONT_FACES}
:root{
  --bg:${TOKENS.bg}; --pink:${TOKENS.pink}; --cyan:${TOKENS.cyan};
  --gold:${TOKENS.gold}; --ink:${TOKENS.ink}; --white:${TOKENS.white};
}
*{box-sizing:border-box}
html,body{margin:0;width:1920px;height:1080px;background:var(--bg);color:var(--ink);font-family:Cairo,Arial,sans-serif;overflow:hidden}
.scene{position:relative;width:1920px;height:1080px;padding:70px 90px;background:var(--bg)}
.course-label{font-family:Cairo,Arial,sans-serif;font-size:22px;font-weight:600;color:#5b4a22;letter-spacing:.02em}
.q-pill{font-family:Anton,Arial,sans-serif;font-size:34px;color:var(--pink);letter-spacing:.03em;margin-top:14px}
.headline-en{font-family:Anton,Arial,sans-serif;font-size:58px;line-height:1.14;color:var(--ink);max-width:1080px;margin-top:18px}
.headline-ar{direction:rtl;text-align:right;font-family:Cairo,Arial,sans-serif;font-weight:700;font-size:36px;line-height:1.55;color:#1a1a1a;max-width:1080px;margin-top:26px}
.card{background:var(--white);border:4px solid var(--ink);border-radius:22px;box-shadow:10px 10px 0 var(--pink);padding:34px 40px}
.card.cyan-shadow{box-shadow:10px 10px 0 var(--cyan)}
.card.gold-shadow{box-shadow:10px 10px 0 var(--gold)}
.card-title{font-family:Anton,Arial,sans-serif;font-size:32px;color:var(--pink);margin-bottom:18px}
.opt-row{display:flex;align-items:center;gap:22px;background:var(--white);border:3px solid var(--ink);border-radius:16px;padding:18px 28px;margin-bottom:16px}
.opt-badge{font-family:Anton,Arial,sans-serif;font-size:26px;color:var(--white);background:var(--pink);border:3px solid var(--ink);border-radius:999px;width:46px;height:46px;display:flex;align-items:center;justify-content:center;flex:none}
.opt-badge.correct{background:var(--gold)}
.opt-text{font-family:Cairo,Arial,sans-serif;font-weight:700;font-size:28px;color:var(--ink)}
.split{display:flex;gap:36px;margin-top:40px}
.split .box{flex:1;border:4px solid var(--ink);border-radius:22px;padding:30px 34px}
.split .box.pink{background:var(--pink)}
.split .box.cyan{background:var(--cyan)}
.split .box h3{font-family:Anton,Arial,sans-serif;font-size:34px;margin:0 0 6px}
.split .box p{direction:rtl;text-align:right;font-family:Cairo,Arial,sans-serif;font-weight:600;font-size:24px;margin:6px 0 0;line-height:1.5}
.vs-badge{align-self:center;font-family:Anton,Arial,sans-serif;background:var(--ink);color:var(--white);border-radius:999px;width:64px;height:64px;display:flex;align-items:center;justify-content:center;font-size:22px}
/* unicode-bidi:plaintext picks the base direction from the first strong
   character of the text itself. Hard-coding direction:rtl here reversed
   Latin-only captions -- "30 mL" rendered as "mL 30" -- and most captions in
   this deck are English medical terms. plaintext keeps Arabic captions RTL
   and English captions LTR without needing to tag each one. */
.caption-bar{position:absolute;left:50%;bottom:56px;transform:translateX(-50%);background:var(--ink);color:var(--white);border:3px solid var(--ink);border-radius:999px;padding:16px 40px;font-family:Cairo,Arial,sans-serif;font-weight:800;font-size:26px;box-shadow:8px 8px 0 var(--pink);unicode-bidi:plaintext;white-space:nowrap}
.badge-course{position:absolute;left:90px;bottom:56px;background:var(--white);border:3px solid var(--ink);border-radius:10px;padding:10px 22px;font-family:Anton,Arial,sans-serif;font-size:22px;box-shadow:6px 6px 0 var(--gold)}
.pills{display:flex;flex-wrap:wrap;gap:14px;margin-top:16px}
.pill{background:var(--cyan);border:3px solid var(--ink);border-radius:999px;padding:10px 22px;font-family:Cairo,Arial,sans-serif;font-weight:700;font-size:22px}
.gold-banner{background:var(--gold);border:4px solid var(--ink);border-radius:22px;padding:28px 36px;box-shadow:10px 10px 0 var(--ink)}
.gold-banner .k{font-family:Cairo,Arial,sans-serif;font-weight:800;font-size:22px;direction:rtl;text-align:right}
.gold-banner .v{font-family:Anton,Arial,sans-serif;font-size:44px;margin-top:8px}
.illustration{position:absolute;right:90px;top:360px;width:520px}
.trophy{position:absolute;right:100px;top:80px;width:130px}
.card p.ar{direction:rtl;text-align:right;font-family:Cairo,Arial,sans-serif;font-weight:600;font-size:27px;line-height:1.7;color:#1a1a1a;margin:0}
.verdict-row{background:var(--white);border:3px solid var(--ink);border-radius:14px;padding:13px 26px;margin-bottom:9px}
.verdict-top{display:flex;align-items:center;gap:14px}
.verdict-badge{width:32px;height:32px;border-radius:999px;border:3px solid var(--ink);display:flex;align-items:center;justify-content:center;font-family:Anton,Arial,sans-serif;font-size:16px;color:var(--white);flex:none}
.verdict-badge.wrong{background:#FF6B6B}
.verdict-badge.correct{background:var(--gold);color:var(--ink)}
.verdict-en{font-family:Cairo,Arial,sans-serif;font-weight:800;font-size:20px;color:var(--ink)}
.verdict-ar{direction:rtl;text-align:right;font-family:Cairo,Arial,sans-serif;font-weight:600;font-size:17px;color:#3a3a3a;margin-top:5px;line-height:1.4}
.verdict-elsewhere{direction:rtl;text-align:right;font-family:Cairo,Arial,sans-serif;font-weight:600;font-size:15px;color:#5b4a22;margin-top:4px;line-height:1.4;padding-top:4px;border-top:2px dashed #ddd}
.scene-heading{font-family:Anton,Arial,sans-serif;font-size:36px;color:var(--ink);margin-bottom:6px}
.card.warn-shadow{box-shadow:10px 10px 0 #FF6B6B}
.card-label{display:inline-block;font-family:Anton,Arial,sans-serif;font-size:24px;color:var(--white);background:var(--ink);border-radius:999px;padding:8px 26px;margin-bottom:16px}
.card-label.warn{background:#B8362E}
`;

export function trophySvg() {
  return `<svg class="trophy" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M30 15h40v22c0 13-9 24-20 24s-20-11-20-24V15z" fill="${TOKENS.gold}" stroke="${TOKENS.ink}" stroke-width="3"/>
    <path d="M30 20H16c0 12 6 20 14 22" stroke="${TOKENS.ink}" stroke-width="3" fill="none"/>
    <path d="M70 20h14c0 12-6 20-14 22" stroke="${TOKENS.ink}" stroke-width="3" fill="none"/>
    <rect x="44" y="60" width="12" height="14" fill="${TOKENS.gold}" stroke="${TOKENS.ink}" stroke-width="3"/>
    <rect x="32" y="74" width="36" height="10" rx="3" fill="${TOKENS.gold}" stroke="${TOKENS.ink}" stroke-width="3"/>
  </svg>`;
}
