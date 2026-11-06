// 「你按下去之后」· 你刚说完 — shared base: canvas, timing, easing, seeded noise, 2.5D camera, cards.
'use strict';
const W = 1080, H = 1920, FPS = 30;
const C = CUES.c, DUR = TL.duration;
const cv = document.getElementById('c'); cv.width = W; cv.height = H;
let ctx = cv.getContext('2d');
const UI = '"Noto Sans Mono CJK SC"', DSP = '"Noto Sans CJK SC"';
const AMB = '#FFB23E', INK = '#0A0F1E', NAVY = '#16203A', SLATE = '#2A3554', MIST = '#9AA6C4', WHITE = '#F3F5FA';
const TAU = Math.PI * 2;
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, k) => a + (b - a) * k;
const ev = (t, t0, d) => clamp((t - t0) / d);
const smooth = x => { x = clamp(x); return x * x * (3 - 2 * x); };
const ease = x => { x = clamp(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
const expoOut = x => { x = clamp(x); return x === 1 ? 1 : 1 - Math.pow(2, -10 * x); };
const expoIn = x => { x = clamp(x); return x === 0 ? 0 : Math.pow(2, 10 * x - 10); };
function mulberry32(a) { return () => { a |= 0; a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
const hash = (i, s = 1) => mulberry32(i * 7919 + s * 104729)();

// ------------------------------------------------------------------ 2.5D camera: x right, y up, z into the screen
let CX = 0, CY = 0, CZ = -10, F = 1000;
const P = (x, y, z) => { const d = z - CZ; if (d <= .01) return null; const s = F / d; return [W / 2 + (x - CX) * s, H / 2 - (y - CY) * s, s]; };
function rr(x, y, w, h, r) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); }
// a flat card facing the camera at depth z, centred on (x, y), size w × h (world units); draw(fn) gets a local 0..w, 0..h space
function card(x, y, z, w, h, fn, o = {}) {
  const p = P(x, y, z); if (!p) return null; const s = p[2];
  if (p[0] + w * s / 2 < -200 || p[0] - w * s / 2 > W + 200 || p[1] + h * s / 2 < -200 || p[1] - h * s / 2 > H + 200) return p;
  ctx.save(); ctx.translate(p[0] - w * s / 2, p[1] - h * s / 2); ctx.scale(s, s); ctx.globalAlpha = o.alpha ?? 1; fn(w, h, s); ctx.restore();
  return p;
}

// ------------------------------------------------------------------ type
const GLY = '0123456789';
function roll(str, t, t0, dur = .4) { if (t < t0) return ''; const p = (t - t0) / dur; return [...str].map((ch, i) => (p >= (i + 1) / str.length || !/[0-9]/.test(ch)) ? ch : GLY[Math.floor(mulberry32(i * 97 + Math.floor(t * 30))() * 10)]).join(''); }
// thumbnails' subjects, the phone's size (cm), shared state used by the paper style
const THEMES = [['#3B6FD8', '#7FB0FF', 'ball'], ['#D85A8A', '#FFB0C8', 'bowl'], ['#2F9E7A', '#8FE0C0', 'hill'], ['#8A5AD8', '#C9A8FF', 'note'], ['#D8843B', '#FFC98F', 'sun'], ['#3BA9C8', '#9FE6F5', 'wave'], ['#C84A4A', '#FF9F9F', 'car'], ['#5A6AD8', '#B0BAFF', 'cat']];
const PHONE = { w: 7.2, h: 15.6 }, SCREEN = { w: 6.6, h: 14.4 };
const STY = {};
function heroK(t, t0, i) { return { k: expoOut(ev(t, t0 + i * .15, .32)), show: c => Math.ceil(c * clamp((t - t0 - i * .15) / .3)) }; }
const CLEAN_ = location.search.includes('clean');
