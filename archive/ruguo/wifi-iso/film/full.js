// 如果……会怎样 01 · 如果你的眼睛突然能看见 Wi-Fi — draft.
// One core rule: Wi-Fi waves are long (~12.5 cm). Six beats: the ask → reality edited → wish fulfilled → "not so neat"
// → it gets bigger (room, building, net, street, city) → reversal (your eye is too small) → an open ending.
// Look: isometric cutaway (flat three-tone) → hologram scan → blueprint Wi-Fi vision. Pure function of time; seeded noise only.
'use strict';
const W = 1080, H = 1920, FPS = 30;
const C = CUES.c, DUR = TL.duration;
const cv = document.getElementById('c'); cv.width = W; cv.height = H;
let ctx = cv.getContext('2d');
function withCtx(g, fn) { const r = ctx; ctx = g; fn(); ctx = r; }
const UI = '"Noto Sans Mono CJK SC"', FIG = '"Inter Tight"', DSP = '"Noto Sans CJK SC"';
const ACC = '#FF6A1A', HOT = '#FFD9B8', LINE = '#DCEBFA', INK = '#2A2622';
const C30 = Math.cos(Math.PI / 6), TAU = Math.PI * 2;
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, k) => a + (b - a) * k;
const ev = (t, t0, d) => clamp((t - t0) / d);
const smooth = x => { x = clamp(x); return x * x * (3 - 2 * x); };
const ease = x => { x = clamp(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
const expoOut = x => { x = clamp(x); return x === 1 ? 1 : 1 - Math.pow(2, -10 * x); };
function mulberry32(a) { return () => { a |= 0; a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }

// ------------------------------------------------------------------ isometric camera (world metres: x down-right, y down-left, z up)
let CU = 0, CV = 0, K = 90, OY = -60;
const iso = (x, y, z) => [W / 2 + ((x - y) * C30 - CU) * K, H / 2 + OY + ((x + y) * .5 - z - CV) * K];
function camFrom(keys, t) {
  let i = 0; while (i < keys.length - 2 && t > keys[i + 1][0]) i++;
  const a = keys[i], b = keys[i + 1], p = ease(ev(t, a[0], b[0] - a[0]));
  return [lerp(a[1], b[1], p), lerp(a[2], b[2], p), lerp(a[3], b[3], p) * (1 + .004 * Math.sin(t * .9))];
}
const CAM_ROOM = [
  [0, .2, 1.55, 124], [C.pak, .35, 1.65, 140], [C.router + .3, .1, 1.9, 150], [C.phone, .5, 1.6, 156], [C.neighbor, .6, 1.85, 118],
  [C.building - .2, .9, 1.9, 100], [C.building + 1.4, 4.1, .4, 52], [C.turn - .1, 4.1, .35, 50],
  [C.turn + .9, .7, 1.8, 118], [C.wall - .3, 1.0, 1.9, 120], [C.wall + .4, 2.35, 2.2, 165], [C.body + .3, .55, .25, 195], [C.fridge + .3, 5.0, 2.3, 160], [C.net + .2, 1.0, 1.2, 150], [C.move, .75, .9, 200], [C.street, .75, .9, 205],
];
let CAM_STREET = [[C.street, 18, 6.5, 44], [C.city, 26, 6.5, 44]];
const CAM_CITY = [[C.city, 0, -15, 7.2], [C.fog, 0, -17, 5.0], [C.freeze + 3, 0, -17.5, 4.7]];
const CAM_FAST = [[C.fastIn, 0, 122.45, .4899], [C.fastIn + .5, 0, 60, .62], [C.fast + .5, 0, -55, 1.4], [C.fear, 0, -50, 1.45], [C.km5, 0, 0, .075], [C.sea, 0, 0, .07]];

// ------------------------------------------------------------------ the flat (7 × 5 m), with a parametric offset so the building can repeat it
const ROOM = { X: 7, Y: 5, H: 2.7, slab: .35 };
const ROUTER = [0.17, 3.5, 1.5];
const PERSON = { x: 1.35, y: .72 };
const PHONE = [1.55, .95, .95];
const BOX = [
  [-0.16, 0, 0, ROOM.Y, 0, ROOM.H, '#E4DDD2', 'wall'], [0, ROOM.X, -0.16, 0, 0, ROOM.H, '#E9E3D9', 'wall'],
  [4.1, 4.28, 0, 2.0, 0, 1.15, '#E9E3D9', 'wall', 'cut'], [4.1, 4.28, 2.95, ROOM.Y, 0, 1.15, '#E9E3D9', 'wall', 'cut'],
  [0.35, 2.45, 0.15, 1.05, 0, .42, '#7F8FA6', 'fabric', 'seat'], [0.35, 2.45, 0.05, 0.3, 0, .9, '#7F8FA6', 'fabric'],
  [0.2, 0.38, 0.05, 1.05, 0, .62, '#76859C', 'fabric'], [2.42, 2.6, 0.05, 1.05, 0, .62, '#76859C', 'fabric'],
  [1.0, 2.05, 1.75, 2.45, 0, .42, '#B98E66', 'wood'], [0, .38, 3.2, 3.8, 1.36, 1.42, '#B98E66', 'wood'],
  [.04, .3, 3.37, 3.63, 1.42, 1.48, '#2F3238', 'dark', 'router'],
  [4.45, 6.0, .05, .7, 0, .9, '#A7A097', 'wood'], [4.75, 5.35, .1, .55, .9, 1.22, '#C6CCD5', 'metal'],
  [6.1, 6.9, .05, .8, 0, 1.85, '#C3C9D2', 'metal', 'fridge'], [6.3, 6.75, 3.9, 4.6, 0, .35, '#8E7C6A', 'wood'],
];
const depth = b => (b[7] === 'wall' && b[8] !== 'cut') ? -100 : (b[0] + b[1]) / 2 + (b[2] + b[3]) / 2 + b[4] * .1;
const ORDER = BOX.map((b, i) => i).sort((a, b) => depth(BOX[a]) - depth(BOX[b]));
const shade = (hex, k) => { const n = parseInt(hex.slice(1), 16); const r = n >> 16, g = n >> 8 & 255, b = n & 255;
  const to = k > 0 ? [255, 250, 240] : [35, 28, 48], a = Math.abs(k); return `rgb(${lerp(r, to[0], a) | 0},${lerp(g, to[1], a) | 0},${lerp(b, to[2], a) | 0})`; };
function poly(pts, fill, stroke, lw, dash) {
  ctx.beginPath(); pts.forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)); ctx.closePath();
  if (fill) { ctx.fillStyle = fill; ctx.fill(); }
  if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = lw; ctx.setLineDash(dash || []); ctx.stroke(); ctx.setLineDash([]); }
}
const faces = (b, o = [0, 0, 0]) => {
  const [x0, x1, y0, y1, z0, z1] = b, [ox, oy, oz] = o, P = (x, y, z) => iso(x + ox, y + oy, z + oz);
  return { top: [P(x0, y0, z1), P(x1, y0, z1), P(x1, y1, z1), P(x0, y1, z1)], px: [P(x1, y0, z0), P(x1, y1, z0), P(x1, y1, z1), P(x1, y0, z1)], py: [P(x0, y1, z0), P(x1, y1, z0), P(x1, y1, z1), P(x0, y1, z1)] };
};
function hatchFace(pts, col, gap, lw) {
  ctx.save(); poly(pts); ctx.clip();
  const xs = pts.map(p => p[0]), ys = pts.map(p => p[1]);
  const x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = Math.min(...ys), y1 = Math.max(...ys);
  ctx.strokeStyle = col; ctx.lineWidth = lw; ctx.beginPath();
  for (let s = x0 - (y1 - y0); s < x1; s += gap) { ctx.moveTo(s, y1); ctx.lineTo(s + (y1 - y0), y0); }
  ctx.stroke(); ctx.restore();
}
const floorPoly = (o = [0, 0, 0]) => [iso(o[0], o[1], o[2]), iso(o[0] + ROOM.X, o[1], o[2]), iso(o[0] + ROOM.X, o[1] + ROOM.Y, o[2]), iso(o[0], o[1] + ROOM.Y, o[2])];

// ------------------------------------------------------------------ a person: a minimal billboard (seated, or walking)
function drawPerson(x, y, z, mode, o = {}) {
  const k = K / 80 * (o.s ?? 1), [bx, by] = iso(x, y, z);
  const wifi = mode === 'wifi', body = wifi ? '#000' : '#2E7A78', legs = wifi ? '#000' : '#34383F', skin = wifi ? '#000' : '#E5C2A6';
  ctx.save(); ctx.translate(bx, by); ctx.scale(k * (o.flip ? -1 : 1), k);
  ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  if (wifi) { ctx.shadowColor = ACC; ctx.shadowBlur = 16; }
  const walk = o.walk ?? null;
  if (walk === null) {
    ctx.fillStyle = body; ctx.beginPath(); ctx.moveTo(-20, 0); ctx.lineTo(-14, -92); ctx.quadraticCurveTo(0, -104, 14, -92); ctx.lineTo(22, 0); ctx.closePath(); ctx.fill();
    ctx.strokeStyle = legs; ctx.lineWidth = 22; ctx.beginPath(); ctx.moveTo(-6, -4); ctx.lineTo(34, 18); ctx.lineTo(34, 66); ctx.stroke();
    ctx.strokeStyle = body; ctx.lineWidth = 12; ctx.beginPath(); ctx.moveTo(6, -78); ctx.lineTo(30, -46); ctx.lineTo(44, -62); ctx.stroke();
  } else {
    const s = Math.sin(walk) * 16;
    ctx.strokeStyle = legs; ctx.lineWidth = 20; ctx.beginPath(); ctx.moveTo(0, -60); ctx.lineTo(s, 30); ctx.moveTo(0, -60); ctx.lineTo(-s, 30); ctx.stroke();
    ctx.fillStyle = body; ctx.beginPath(); ctx.moveTo(-20, -50); ctx.lineTo(-14, -142); ctx.quadraticCurveTo(0, -154, 14, -142); ctx.lineTo(22, -50); ctx.closePath(); ctx.fill();
    ctx.strokeStyle = body; ctx.lineWidth = 12; ctx.beginPath(); ctx.moveTo(6, -128); ctx.lineTo(24, -96); ctx.lineTo(34, -112); ctx.stroke();
  }
  const hy = walk === null ? -122 : -172;
  ctx.fillStyle = skin; ctx.beginPath(); ctx.arc(2, hy, 21, 0, TAU); ctx.fill();
  ctx.shadowBlur = 0;
  if (!wifi) { ctx.fillStyle = '#2A2522'; ctx.beginPath(); ctx.arc(2, hy - 4, 22, Math.PI * 1.05, Math.PI * 2.05); ctx.fill(); }
  const ph = walk === null ? [46, -66] : [36, -116];
  ctx.fillStyle = wifi ? HOT : '#22262C'; ctx.save(); ctx.translate(ph[0], ph[1]); ctx.rotate(-.5); ctx.fillRect(-7, -12, 14, 24); ctx.restore();
  if (wifi) {
    ctx.strokeStyle = ACC; ctx.lineWidth = 2.5; ctx.globalAlpha = .9; ctx.beginPath(); ctx.arc(2, hy, 21, Math.PI * .7, Math.PI * 1.9); ctx.stroke(); ctx.globalAlpha = 1;
    if (o.buds) { ctx.globalCompositeOperation = 'lighter'; for (const dx of [-19, 23]) { const g = ctx.createRadialGradient(dx, hy + 4, 0, dx, hy + 4, 30); g.addColorStop(0, 'rgba(255,240,225,1)'); g.addColorStop(1, 'rgba(255,106,26,0)'); ctx.fillStyle = g; ctx.fillRect(dx - 30, hy - 26, 60, 60); ctx.fillStyle = '#FFF4EA'; ctx.beginPath(); ctx.arc(dx, hy + 4, 5, 0, TAU); ctx.fill(); } ctx.globalCompositeOperation = 'source-over'; }
  }
  ctx.restore();
  return [bx, by, k];
}

// ------------------------------------------------------------------ backgrounds
function paperBG() {
  ctx.fillStyle = '#EEE8DC'; ctx.fillRect(0, 0, W, H);
  ctx.fillStyle = 'rgba(60,50,40,.10)';
  for (let x = -4; x <= 12; x++) for (let y = -6; y <= 10; y++) { const [sx, sy] = iso(x, y, -0.35); if (sx > -10 && sx < W + 10 && sy > -10 && sy < H + 10) { ctx.beginPath(); ctx.arc(sx, sy, 2.2, 0, TAU); ctx.fill(); } }
}
const SHEET = (() => {
  const c = document.createElement('canvas'); c.width = 540; c.height = 960; const g = c.getContext('2d');
  const gr = g.createLinearGradient(0, 0, 540, 960); gr.addColorStop(0, '#16336B'); gr.addColorStop(1, '#10285A'); g.fillStyle = gr; g.fillRect(0, 0, 540, 960);
  const r = mulberry32(11);
  for (let i = 0; i < 70; i++) { g.fillStyle = `rgba(${r() < .5 ? '40,88,166' : '10,26,60'},${.05 + r() * .08})`; g.fillRect(0, r() * 960, 540, 2 + r() * 14); }
  for (let i = 0; i < 1600; i++) { g.fillStyle = `rgba(220,235,250,${r() * .12})`; g.fillRect(r() * 540, r() * 960, 1, 1); }
  return c;
})();
function sheetBG(grid = true) {
  ctx.drawImage(SHEET, 0, 0, W, H);
  if (!grid) return;
  ctx.strokeStyle = 'rgba(220,235,250,.07)'; ctx.lineWidth = 1; ctx.beginPath();
  const st = K < 30 ? 10 : 1;
  for (let i = -60; i <= 80; i += st) { let a = iso(i, -60, 0), b = iso(i, 80, 0); ctx.moveTo(...a); ctx.lineTo(...b); a = iso(-60, i, 0); b = iso(80, i, 0); ctx.moveTo(...a); ctx.lineTo(...b); }
  ctx.stroke();
}

// ------------------------------------------------------------------ human view of the flat
function drawBoxHuman(b) {
  const f = faces(b), col = b[6];
  poly(f.py, shade(col, -.06)); poly(f.px, shade(col, -.22)); poly(f.top, shade(col, .2));
  if (b[8] === 'cut') hatchFace(f.top, 'rgba(40,36,32,.55)', 7, 1.3);
  if (b[8] === 'router') { const [sx, sy] = iso(.17, 3.5, 1.48), s = K / 92; ctx.strokeStyle = '#2F3238'; ctx.lineWidth = 3 * s; ctx.beginPath(); ctx.moveTo(sx - 8 * s, sy); ctx.lineTo(sx - 12 * s, sy - 26 * s); ctx.moveTo(sx + 8 * s, sy); ctx.lineTo(sx + 12 * s, sy - 26 * s); ctx.stroke(); }
}
function humanView(t) {
  paperBG();
  const { X, Y, slab: s } = ROOM;
  const top = floorPoly(), fx = [iso(X, 0, -s), iso(X, Y, -s), iso(X, Y, 0), iso(X, 0, 0)], fy = [iso(0, Y, -s), iso(X, Y, -s), iso(X, Y, 0), iso(0, Y, 0)];
  ctx.save(); ctx.shadowColor = 'rgba(40,30,20,.25)'; ctx.shadowBlur = 60; ctx.shadowOffsetY = 40; poly([iso(0, 0, -s), iso(X, 0, -s), iso(X, Y, -s), iso(0, Y, -s)], '#000'); ctx.restore();
  poly(top, '#D8C4A4'); poly(fx, '#8F8A84'); poly(fy, '#A9A39C');
  hatchFace(fx, 'rgba(40,36,32,.35)', 9, 1.2); hatchFace(fy, 'rgba(40,36,32,.3)', 9, 1.2);
  ctx.strokeStyle = 'rgba(80,60,40,.12)'; ctx.lineWidth = 1; ctx.beginPath(); for (let x = .25; x < X; x += .25) { ctx.moveTo(...iso(x, 0, 0)); ctx.lineTo(...iso(x, Y, 0)); } ctx.stroke();
  for (const i of ORDER) {
    const b = BOX[i]; drawBoxHuman(b);
    if (i === 1) { poly([iso(2.7, 0, .95), iso(3.8, 0, .95), iso(3.8, 0, 2.15), iso(2.7, 0, 2.15)], '#BFD4E2', '#9DA9B2', 3); }
    if (b[8] === 'seat') drawPerson(PERSON.x, PERSON.y, .42, 'human');
  }
  { const [lx, ly] = iso(.3, 3.45, 1.46); for (let i = 0; i < 3; i++) { const on = Math.sin(t * 9 + i * 2.1) > -.2; ctx.fillStyle = on ? '#7CFF9B' : '#2A3A2E'; ctx.beginPath(); ctx.arc(lx + i * 6 * K / 92, ly - i * 3 * K / 92, 2.6 * K / 92, 0, TAU); ctx.fill(); } }
  const fl = .5 + .25 * Math.sin(t * 7) + .15 * Math.sin(t * 17);
  const [px, py] = iso(...PHONE), rr = 70 * K / 92; const g = ctx.createRadialGradient(px, py, 0, px, py, rr); g.addColorStop(0, `rgba(210,235,255,${fl})`); g.addColorStop(1, 'rgba(210,235,255,0)'); ctx.fillStyle = g; ctx.fillRect(px - rr, py - rr, 2 * rr, 2 * rr);
}

// ------------------------------------------------------------------ Wi-Fi view: shells (a sphere in isometric is a circle), floor rings, wobble
const LAM = 0.125, VEL = 0.25;
let BOOST = 1;
function shells(src, t, o = {}) {
  const [rx, ry] = iso(...src), s = 1.2247 * K, t0 = o.t0 ?? -99, front = (t - t0) * (o.fv ?? 3);
  if (front <= 0) return;
  const lod = clamp((LAM * s - 6) / 16), rmax = Math.min(o.rmax ?? 7, front), amp = (o.amp ?? 1) * BOOST, wob = o.wob ?? 0, brk = o.brk ?? 0;
  ctx.save(); ctx.globalCompositeOperation = 'lighter';
  if (o.clip) { o.clip(); ctx.clip(); }
  const g = ctx.createRadialGradient(rx, ry, 0, rx, ry, Math.max(1, rmax * s));
  g.addColorStop(0, `rgba(255,150,80,${.55 * amp})`); g.addColorStop(.15, `rgba(255,106,26,${.24 * amp})`); g.addColorStop(1, 'rgba(255,106,26,0)');
  ctx.fillStyle = g; ctx.beginPath(); ctx.arc(rx, ry, Math.max(1, rmax * s), 0, TAU); ctx.fill();
  const step = o.step ?? 1, off = (t * VEL) % LAM;
  for (let r = off + .05, n = 0; r < rmax; r += LAM, n++) {
    if (n % step) continue;
    const a = amp * .9 / (1 + r / .9) * (.25 + .75 * lod) * (r > front - .4 ? clamp((front - r) / .4) : 1);
    const lw = (o.lw ?? 1.6) * clamp(K / 95, 1, 2.4), col = `${255},${130 + 80 * Math.exp(-r) | 0},${60 + 60 * Math.exp(-r) | 0}`;
    if (brk > 0) {      // shattered: arcs with gaps, knocked off their circle
      const R0 = mulberry32(n * 131 + 7);
      for (let q = 0; q < 7; q++) { const a0 = R0() * TAU, len = (.25 + .5 * R0()) * (1 - .6 * brk), dr = (R0() - .5) * .12 * brk * s;
        ctx.strokeStyle = `rgba(${col},${a})`; ctx.lineWidth = lw; ctx.beginPath(); ctx.arc(rx + (R0() - .5) * 20 * brk, ry + (R0() - .5) * 20 * brk, Math.max(1, r * s + dr), a0, a0 + len); ctx.stroke(); }
      continue;
    }
    ctx.strokeStyle = `rgba(${col},${a * .28})`; ctx.lineWidth = lw * 3.2; ctx.beginPath(); ctx.arc(rx, ry, r * s, 0, TAU); ctx.stroke();
    ctx.strokeStyle = `rgba(${col},${a})`; ctx.lineWidth = lw;
    ctx.beginPath();
    if (wob > 0) {
      for (let i = 0; i <= 64; i++) { const th = i / 64 * TAU, rr = (r + wob * (.05 * Math.sin(th * 5 + t * 3 + r * 9) + .03 * Math.sin(th * 11 - t * 4))) * s; i ? ctx.lineTo(rx + rr * Math.cos(th), ry + rr * Math.sin(th)) : ctx.moveTo(rx + rr * Math.cos(th), ry + rr * Math.sin(th)); }
    } else ctx.arc(rx, ry, r * s, 0, TAU);
    ctx.stroke();
  }
  ctx.restore();
}
function floorRings(src, t, o = {}) {
  const front = (t - (o.t0 ?? -99)) * (o.fv ?? 3); if (front <= 0) return;
  const [fx, fy] = iso(src[0], src[1], 0), h = src[2], lod = clamp((LAM * 1.2247 * K - 6) / 16);
  ctx.save(); ctx.globalCompositeOperation = 'lighter'; poly(floorPoly()); ctx.clip();
  const off = (t * VEL) % LAM;
  for (let r = off + h; r < Math.min(8, front); r += LAM) {
    const rr = Math.sqrt(r * r - h * h); if (rr <= 0) continue;
    const a = (o.amp ?? 1) * 1.4 / (1 + r / 1.1) * (.2 + .8 * lod);
    ctx.strokeStyle = `rgba(255,150,80,${a})`; ctx.lineWidth = 2.2;
    ctx.beginPath(); ctx.ellipse(fx, fy, 1.2247 * rr * K, .7071 * rr * K, 0, 0, TAU); ctx.stroke();
  }
  ctx.restore();
}
function drawBoxWifi(b, o = [0, 0, 0], lit = 1) {
  const f = faces(b, o), mat = b[7];
  if (mat === 'metal') { poly(f.py, 'rgba(220,235,250,.5)'); poly(f.px, 'rgba(220,235,250,.32)'); poly(f.top, 'rgba(255,240,225,.7)'); for (const q of [f.py, f.px, f.top]) poly(q, null, '#FFFFFF', 1.6); return; }
  if (b[8] === 'router') { ctx.save(); if (lit > .05) { ctx.shadowColor = ACC; ctx.shadowBlur = 30 * lit; } for (const q of [f.py, f.px, f.top]) poly(q, lit > .05 ? HOT : 'rgba(220,235,250,.5)'); ctx.restore(); return; }
  if (mat === 'wall') { for (const q of [f.py, f.px, f.top]) poly(q, null, 'rgba(220,235,250,.45)', 1.3, [10, 8]); return; }
  for (const q of [f.py, f.px, f.top]) poly(q, null, 'rgba(220,235,250,.4)', 1.1);
}
function roomWifi(o, lit, person) {
  poly(floorPoly(o), 'rgba(220,235,250,.03)', 'rgba(220,235,250,.5)', 1.4);
  for (const i of ORDER) {
    const b = BOX[i]; drawBoxWifi(b, o, lit);
    if (b[8] === 'seat' && person) drawPerson(PERSON.x + o[0], PERSON.y + o[1], .42 + o[2], 'wifi');
  }
}
function slabWifi() {
  const { X, Y, slab: s } = ROOM, fx = [iso(X, 0, -s), iso(X, Y, -s), iso(X, Y, 0), iso(X, 0, 0)], fy = [iso(0, Y, -s), iso(X, Y, -s), iso(X, Y, 0), iso(0, Y, 0)];
  poly(fx, null, 'rgba(220,235,250,.45)', 1.2); poly(fy, null, 'rgba(220,235,250,.45)', 1.2);
  hatchFace(fx, 'rgba(220,235,250,.25)', 10, 1); hatchFace(fy, 'rgba(220,235,250,.25)', 10, 1);
}

// ------------------------------------------------------------------ hologram furniture
const GLY = '0123456789';
function roll(str, t, t0, dur = .3) {
  if (t < t0) return '';
  const p = (t - t0) / dur;
  return [...str].map((ch, i) => (p >= (i + 1) / str.length || ch === ' ' || /[　-鿿·：，？]/.test(ch)) ? ch : GLY[Math.floor(mulberry32(i * 97 + Math.floor(t * 30))() * GLY.length)]).join('');
}
function plateText(txt, x, y, o = {}) {
  ctx.font = `700 ${o.size ?? 42}px ${UI}`; const tw = ctx.measureText(txt).width;
  const hh = (o.size ?? 42) * 1.6, px = clamp(o.right ? x - tw - 36 : x, 24, W - 24 - tw - 36), py = y - hh / 2;
  ctx.fillStyle = 'rgba(6,12,28,.86)'; ctx.fillRect(px, py, tw + 36, hh);
  ctx.strokeStyle = 'rgba(220,235,250,.6)'; ctx.lineWidth = 1; ctx.strokeRect(px + .5, py + .5, tw + 35, hh - 1);
  ctx.fillStyle = o.accent ? ACC : '#F4F8FC'; ctx.textBaseline = 'middle'; ctx.textAlign = 'left'; ctx.fillText(txt, px + 18, py + hh / 2 + 2);
}
function bracket(cx, cy, w, h, t, t0, label, o = {}) {
  if (t < t0 || (o.t1 && t > o.t1)) return;
  const k = expoOut(ev(t, t0, .35)), s = lerp(2.2, 1, k), ww = w * s / 2, hh = h * s / 2, L = 24;
  ctx.strokeStyle = LINE; ctx.lineWidth = 3; ctx.globalAlpha = lerp(.3, 1, k); ctx.beginPath();
  for (const [sx, sy] of [[-1, -1], [1, -1], [1, 1], [-1, 1]]) { const x = cx + sx * ww, y = cy + sy * hh; ctx.moveTo(x, y - sy * L); ctx.lineTo(x, y); ctx.lineTo(x - sx * L, y); }
  ctx.stroke(); ctx.globalAlpha = 1;
  if (k < .6) return;
  const dx = o.dx ?? ww + 40, dy = o.dy ?? -hh - 60, lx = cx + dx, ly = cy + dy;
  ctx.strokeStyle = LINE; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(cx + Math.sign(dx) * ww, cy - hh); ctx.lineTo(lx, ly); ctx.stroke();
  plateText(roll(label, t, t0 + .2, .5), lx, ly, { right: dx < 0, accent: o.accent, size: o.big ? 60 : 42 });
}
function display(lines, x, y, t, t0, o = {}) {      // big left-aligned type; lines land one by one (a drop, not a fade)
  if (t < t0) return;
  ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic';
  lines.forEach((ln, i) => {
    const k = expoOut(ev(t, t0 + i * .18, .35)); if (k <= 0) return;
    ctx.save(); ctx.translate(x, y + i * (o.lh ?? 118) - (1 - k) * 40);
    ctx.font = `900 ${o.size ?? 100}px ${DSP}`;
    let cx = 0;
    for (const [s, col] of ln) { ctx.fillStyle = col; ctx.fillText(s, cx, 0); cx += ctx.measureText(s).width; }
    ctx.restore();
  });
}

// ------------------------------------------------------------------ the parameter panel: the series' signature move
function panel(t) {
  if (t < C.panel || t > C.pak + 1.2) return;
  const k = expoOut(ev(t, C.panel, .4)) * (1 - smooth(ev(t, C.pak + .6, .5)));
  const x = 72, y = lerp(1700, 1180, k), w = 936, h = 270;
  ctx.save();
  ctx.fillStyle = 'rgba(8,14,30,.92)'; ctx.fillRect(x, y, w, h);
  ctx.strokeStyle = 'rgba(220,235,250,.7)'; ctx.lineWidth = 1.5; ctx.strokeRect(x + .5, y + .5, w - 1, h - 1);
  ctx.font = `400 30px ${UI}`; ctx.fillStyle = 'rgba(220,235,250,.7)'; ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic';
  ctx.fillText('现实参数', x + 32, y + 52);
  ctx.font = `700 44px ${UI}`; ctx.fillStyle = '#F4F8FC'; ctx.fillText('你的眼睛能看见', x + 32, y + 130);
  const flip = t >= C.pak - .25, sw = expoOut(ev(t, C.pak - .25, .25));
  const tx = x + w - 200, ty = y + 112;
  ctx.fillStyle = flip ? ACC : 'rgba(220,235,250,.25)'; ctx.beginPath(); ctx.roundRect(tx, ty - 26, 140, 52, 26); ctx.fill();
  ctx.fillStyle = '#F4F8FC'; ctx.beginPath(); ctx.arc(tx + 26 + 88 * sw, ty, 20, 0, TAU); ctx.fill();
  ctx.font = `700 46px ${UI}`; ctx.fillStyle = flip ? ACC : '#F4F8FC';
  ctx.fillText(flip ? '可见光 + Wi-Fi' : '可见光', x + 32, y + 212);
  ctx.restore();
}

// ------------------------------------------------------------------ scenes A–C: your flat, the building around it, and what the real world does
const UNITS = [];
for (const f of [-1, 0, 1, 2]) for (const c of [0, 1]) UNITS.push({ o: [c * 7.6, 0, f * 3.1], f, c, own: f === 0 && c === 0 });
const NEIGH = [[-3.2, 2.6, 1.3], [8.6, 4.2, 1.4], [3.2, -2.8, 1.2]];
const IMG_FRIDGE = [2 * 6.1 - ROUTER[0], ROUTER[1], ROUTER[2]];
function building(t) {
  const k = smooth(ev(t, C.building - .3, .8)) * (1 - smooth(ev(t, C.turn, .8)));
  if (k <= 0) return;
  { const fl = smooth(ev(t, C.glowAll + .3, .5)) * (1 - smooth(ev(t, C.turn - .6, .8))), [cx, cy] = iso(7.3, 2.5, 4.5);
    if (fl > 0) { ctx.save(); ctx.globalCompositeOperation = 'lighter'; const g = ctx.createRadialGradient(cx, cy, 0, cx, cy, 900); g.addColorStop(0, `rgba(255,160,90,${.45 * fl})`); g.addColorStop(.5, `rgba(255,106,26,${.18 * fl})`); g.addColorStop(1, 'rgba(255,106,26,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); ctx.restore(); } }
  for (const u of UNITS) {
    if (u.own) continue;
    const lt = C.glowAll + (u.f + 1) * .18 + u.c * .07, lit = smooth(ev(t, lt - .6, .4));
    ctx.save(); ctx.globalAlpha = k; roomWifi(u.o, lit, true); ctx.restore();
    if (k > .3) shells([ROUTER[0] + u.o[0], ROUTER[1] + u.o[1], ROUTER[2] + u.o[2]], t, { t0: lt - .6, amp: .8 * k, step: 3, rmax: 4, lw: 1.2 });
  }
}
const halfPlaneX = x0 => () => { ctx.beginPath(); const a = iso(x0, -20, 0), b = iso(x0, 30, 0); ctx.moveTo(...a); ctx.lineTo(...b); ctx.lineTo(b[0] - 4000, b[1] - 2300); ctx.lineTo(a[0] - 4000, a[1] - 2300); ctx.closePath(); };
function roomScene(t) {
  const wob = smooth(ev(t, C.wobble + .4, 1.2)), net = smooth(ev(t, C.net - .2, .8)), brk = t >= C.wobble ? 1 - smooth(ev(t, C.wobble + .5, 1.2)) * .6 : 0;
  sheetBG(); slabWifi();
  building(t);
  const neat = 1 - net;
  if (neat > 0) {
    ctx.save(); ctx.globalAlpha = neat;
    floorRings(ROUTER, t, { t0: C.router });
    shells(ROUTER, t, { t0: C.router, wob, brk });
    shells(PHONE, t, { t0: C.phone, amp: .6, rmax: 3, fv: 2.4, wob, brk });
    for (const n of NEIGH) shells(n, t, { t0: C.neighbor, amp: .7, rmax: 6, wob, brk });
    if (t >= C.fridge) shells(IMG_FRIDGE, t, { t0: C.fridge, amp: .6, fv: 4, wob, clip: halfPlaneX(6.1) });
    ctx.restore();
  }
  if (net > 0) netField(t, net);
  const wk = smooth(ev(t, C.wall, .5));
  if (wk > 0) poly([iso(4.28, 0, 0), iso(7, 0, 0), iso(7, 5, 0), iso(4.28, 5, 0)], `rgba(8,18,44,${.5 * wk})`);
  const bk = smooth(ev(t, C.body, .5));
  {
    const P0 = [PERSON.x, PERSON.y], d = [P0[0] - ROUTER[0], P0[1] - ROUTER[1]], L = Math.hypot(...d), u = [d[0] / L, d[1] / L], n = [-u[1], u[0]];
    const sh = [[P0[0] + n[0] * .28, P0[1] + n[1] * .28], [P0[0] - n[0] * .28, P0[1] - n[1] * .28], [P0[0] + u[0] * 3 - n[0] * 1.1, P0[1] + u[1] * 3 - n[1] * 1.1], [P0[0] + u[0] * 3 + n[0] * 1.1, P0[1] + u[1] * 3 + n[1] * 1.1]];
    ctx.save(); poly(floorPoly()); ctx.clip(); poly(sh.map(p => iso(p[0], p[1], 0)), `rgba(4,10,26,${.25 + .55 * bk})`); ctx.restore();
  }
  roomWifi([0, 0, 0], smooth(ev(t, C.router - .3, .4)), true);
  const [rx, ry] = iso(...ROUTER), [px, py] = iso(...PHONE);
  if (t < C.building) {
    bracket(rx, ry - 10, 70, 60, t, C.router + .1, '路由器', { dx: 60, dy: -120 });
    bracket(px, py, 60, 60, t, C.phone + .1, '手机 · 回应', { dx: 60, dy: -110 });
    if (t >= C.neighbor) { const [nx, ny] = iso(-.1, 1.6, 1.4); bracket(nx, ny, 80, 120, t, C.neighbor, '隔壁', { dx: -60, dy: -140 }); }
  }
  if (t > C.turn && t < C.net + .2) {
    const [wx, wy] = iso(4.19, 1.5, .6); bracket(wx, wy, 110, 230, t, C.wall + .1, '墙：削弱', { dx: 90, dy: -230, t1: C.body - .1, big: true });
    const [bx, by] = iso(PERSON.x, PERSON.y, 1.0); bracket(bx, by, 170, 300, t, C.body + .1, '你：挡住', { dx: -120, dy: -230, t1: C.fridge - .1, big: true });
    const [fx, fy] = iso(6.5, .45, 1.0); bracket(fx, fy, 150, 320, t, C.fridge + .1, '冰箱：弹回', { dx: -160, dy: -260, t1: C.net, big: true });
  }
  if (net > .6 && t < C.street) {
    let best = [-1, 0], worst = [1e9, 0];
    for (let i = 0; i <= 48; i++) { const dx = -.15 + .3 * i / 48, I = fieldAtFloor(PHONE[0] + dx, PHONE[1] + .25, t); if (I > best[0]) best = [I, dx]; if (I < worst[0]) worst = [I, dx]; }
    for (const [dx, lab, acc] of [[best[1], '强', true], [worst[1], '弱', false]]) {
      const [sx, sy] = iso(PHONE[0] + dx, PHONE[1] + .25, 0);
      ctx.strokeStyle = acc ? HOT : LINE; ctx.lineWidth = 3; ctx.beginPath(); ctx.arc(sx, sy, 12, 0, TAU); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(sx, sy - 12); ctx.lineTo(sx, sy - 70); ctx.stroke();
      plateText(lab, sx - 30, sy - 100, { size: 46, accent: acc });
    }
  }
  if (t >= C.move - .2 && t < C.street) plateText('同一个房间，差几厘米', 72, 430, { size: 54 });
  if (t >= C.move) phoneLens(t);
}
// the net: the true field of a few coherent sources (the router and its mirror images) on the floor — cells ~λ/2 ≈ 6 cm
const NETC = document.createElement('canvas'); NETC.width = 360; NETC.height = 640;
const NETS = [[ROUTER, 1], [IMG_FRIDGE, .7], [[ROUTER[0], -ROUTER[1], ROUTER[2]], .55], [[-ROUTER[0] - .3, ROUTER[1], ROUTER[2]], .5]];
function fieldAtFloor(x, y, t) {
  let re = 0, im = 0;
  for (const [s, a] of NETS) { const r = Math.hypot(x - s[0], y - s[1], s[2]); const ph = TAU * r / LAM - t * 2.2; re += a * Math.cos(ph) / (1 + r * .3); im += a * Math.sin(ph) / (1 + r * .3); }
  return re * re + im * im;
}
function netField(t, k) {
  const g = NETC.getContext('2d'), im = g.createImageData(360, 640), d = im.data, sx = W / 360, sy = H / 640;
  for (let j = 0; j < 640; j++) for (let i = 0; i < 360; i++) {
    const u = ((i + .5) * sx - W / 2) / K + CU, v = ((j + .5) * sy - H / 2 - OY) / K + CV;
    const x = (u / C30 + 2 * v) / 2, y = (2 * v - u / C30) / 2, o = (j * 360 + i) * 4;
    if (x < 0 || y < 0 || x > ROOM.X || y > ROOM.Y) { d[o + 3] = 0; continue; }
    const I = fieldAtFloor(x, y, t), v2 = 1 - Math.exp(-I * .9);
    d[o] = 255; d[o + 1] = 90 + 150 * v2; d[o + 2] = 30 + 170 * v2 * v2; d[o + 3] = 255 * v2 * k;
  }
  g.putImageData(im, 0, 0);
  ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.imageSmoothingEnabled = true; ctx.drawImage(NETC, 0, 0, W, H); ctx.restore();
}
function phoneLens(t) {
  const k = expoOut(ev(t, C.move, .4)), cx = 760, cy = 1180, R = 200 * k;
  if (R < 2) return;
  const dx = .09 * Math.sin((t - C.move) * 1.6);
  ctx.save(); ctx.beginPath(); ctx.arc(cx, cy, R, 0, TAU); ctx.clip();
  ctx.fillStyle = 'rgba(6,12,28,.94)'; ctx.fillRect(cx - R, cy - R, 2 * R, 2 * R);
  const sc = 1400, step = 6;
  for (let y = -R; y < R; y += step) for (let x = -R; x < R; x += step) {
    const I = fieldAtFloor(PHONE[0] + x / sc, PHONE[1] + y / sc, t), v2 = 1 - Math.exp(-I * .9);
    ctx.fillStyle = `rgba(255,${90 + 150 * v2 | 0},${30 + 170 * v2 * v2 | 0},${v2})`; ctx.fillRect(cx + x, cy + y, step, step);
  }
  const pxs = cx + dx * sc;
  ctx.fillStyle = '#0B1328'; ctx.strokeStyle = HOT; ctx.lineWidth = 3; ctx.beginPath(); ctx.roundRect(pxs - 40, cy - 75, 80, 150, 12); ctx.fill(); ctx.stroke();
  const I = fieldAtFloor(PHONE[0] + dx, PHONE[1], t), bars = clamp(Math.round((1 - Math.exp(-I * .9)) * 4.4), 0, 4);
  for (let i = 0; i < 4; i++) { ctx.fillStyle = i < bars ? ACC : 'rgba(220,235,250,.25)'; ctx.fillRect(pxs - 26 + i * 15, cy + 40 - i * 12, 11, 12 + i * 12); }
  ctx.restore();
  ctx.strokeStyle = LINE; ctx.lineWidth = 3; ctx.beginPath(); ctx.arc(cx, cy, R, 0, TAU); ctx.stroke();
  if (k > .9) { plateText('挪几厘米', cx - 160, cy - R - 50); ctx.strokeStyle = LINE; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(cx - 42, cy + R + 30); ctx.lineTo(cx + 42, cy + R + 30); ctx.stroke(); ctx.font = `400 28px ${UI}`; ctx.fillStyle = LINE; ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic'; ctx.fillText('≈ 6 cm', cx, cy + R + 68); }
}

// ------------------------------------------------------------------ scene D: the street
const STREET = (() => {
  const r = mulberry32(21), B = [], P = [], CARS = [];
  let x = 0; while (x < 50) { const w = 5 + r() * 6, h = 8 + r() * 22; B.push({ x0: x, x1: x + w, h, seed: r() * 1e6 }); x += w + .8 + r() * 1.5; }
  for (let i = 0; i < 14; i++) P.push({ x: 4 + i * 3.2 + r() * 2, y: 6.2 + r() * 1.2, v: (r() < .5 ? -1 : 1) * (.8 + r() * .5), ph: r() * 6 });
  for (let i = 0; i < 4; i++) CARS.push({ x: r() * 50, y: 9 + (i % 2) * 2.2, v: (i % 2 ? -1 : 1) * (5 + r() * 3) });
  return { B, P, CARS };
})();
const TAG = 6;
{ const p = STREET.P[TAG], x = p.x + p.v * (C.bt - C.street), y = p.y, u = (x - y) * C30, v = (x + y) / 2 - 1.9;
  CAM_STREET = [[C.street, 18, 6.5, 44], [C.bt - .5, u + 2, v + 1, 52], [C.bt + .5, u, v, 175], [C.city, u - .3, v, 190]]; }
function streetScene(t) {
  sheetBG();
  const lt = t - C.street;
  ctx.strokeStyle = 'rgba(220,235,250,.4)'; ctx.lineWidth = 1.2;
  for (const yy of [5.5, 8.4, 13]) { ctx.beginPath(); ctx.moveTo(...iso(-5, yy, 0)); ctx.lineTo(...iso(60, yy, 0)); ctx.stroke(); }
  ctx.setLineDash([16, 14]); ctx.beginPath(); ctx.moveTo(...iso(-5, 10.7, 0)); ctx.lineTo(...iso(60, 10.7, 0)); ctx.stroke(); ctx.setLineDash([]);
  for (const b of STREET.B) {
    const f = faces([b.x0, b.x1, 0, 5, 0, b.h]);
    for (const q of [f.py, f.px, f.top]) poly(q, 'rgba(14,30,66,.6)', 'rgba(220,235,250,.55)', 1.2);
    const r = mulberry32(b.seed | 0);
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    for (let z = 1.2; z < b.h - .5; z += 3.1) for (let x = b.x0 + .9; x < b.x1 - .5; x += 2.2) {
      const on = r() < .8, ph = r() * 6; if (!on) continue;
      const [sx, sy] = iso(x, 5, z), a = .55 + .35 * Math.sin(t * 3 + ph), rr = 3.2 * K;
      const g = ctx.createRadialGradient(sx, sy, 0, sx, sy, rr); g.addColorStop(0, `rgba(255,160,90,${.45 * a})`); g.addColorStop(.25, `rgba(255,106,26,${.12 * a})`); g.addColorStop(1, 'rgba(255,106,26,0)');
      ctx.fillStyle = g; ctx.fillRect(sx - rr, sy - rr, 2 * rr, 2 * rr);
      ctx.fillStyle = `rgba(255,217,184,${.7 + .3 * a})`; ctx.fillRect(sx - .35 * K, sy - .5 * K, .7 * K, .9 * K);
    }
    ctx.restore();
  }
  for (const c of STREET.CARS) {
    const x = ((c.x + c.v * lt) % 60 + 60) % 60 - 5, f = faces([x, x + 4.2, c.y, c.y + 1.8, 0, 1.4]);
    for (const q of [f.py, f.px, f.top]) poly(q, 'rgba(14,30,66,.7)', 'rgba(220,235,250,.6)', 1.2);
    shells([x + 2.1, c.y + .9, 1.2], t, { amp: .45, rmax: 2.2, step: 2, lw: 1 });
  }
  let tagged = null;
  for (const p of STREET.P.slice().sort((a, b) => a.y - b.y)) {
    const x = p.x + p.v * lt;
    shells([x + .15, p.y, 1.25], t, { amp: .5, rmax: 1.6, step: 2, lw: 1 });
    const r = drawPerson(x, p.y, 0, 'wifi', { walk: (t * 5 + p.ph) * Math.sign(p.v), flip: p.v < 0, buds: t >= C.bt - .3, s: .9 });
    if (p === STREET.P[TAG]) tagged = r;
  }
  if (tagged) { const [bx, by, k] = tagged; bracket(bx, by - 172 * k, 140 * k / 2, 70 * k / 2, t, C.bt + .3, '蓝牙耳机：也在 2.4 GHz', { dx: -40, dy: -220, big: true }); }
}

// ------------------------------------------------------------------ scene E: the city in a fog of light
const CITY = (() => { const r = mulberry32(31), b = []; for (let i = -9; i <= 9; i++) for (let j = -9; j <= 9; j++) if (r() < .82) b.push([i * 9 + r() * 2, j * 9 + r() * 2, 4 + r() * 4, 4 + r() * 4, 6 + Math.pow(r(), 2) * 70]); return b.sort((a, c) => (a[0] + a[1]) - (c[0] + c[1])); })();
const FOG = (() => { const r = mulberry32(77), a = []; for (let i = 0; i < 260; i++) a.push([(r() - .5) * 170, (r() - .5) * 170, r() * 30, r() * 6, 8 + r() * 18]); return a; })();
function cityScene(t) {
  sheetBG();
  const fog = .25 + smooth(ev(t, C.city, 1.4)) * .5 + smooth(ev(t, C.fog - .3, 1.2)) * .25;
  for (const [x, y, w, d, h] of CITY) { const f = faces([x, x + w, y, y + d, 0, h]); for (const q of [f.py, f.px, f.top]) poly(q, 'rgba(12,26,60,.72)', 'rgba(220,235,250,.35)', 1); }
  ctx.save(); ctx.globalCompositeOperation = 'lighter';
  for (const [x, y, z, ph, rad0] of FOG) {
    const [sx, sy] = iso(x + 6 * Math.sin(t * .3 + ph), y + 6 * Math.cos(t * .25 + ph), z), rad = rad0 * K;
    const a = fog * (.08 + .06 * Math.sin(t * 1.3 + ph));
    const g = ctx.createRadialGradient(sx, sy, 0, sx, sy, rad); g.addColorStop(0, `rgba(255,150,80,${a})`); g.addColorStop(1, 'rgba(255,106,26,0)');
    ctx.fillStyle = g; ctx.fillRect(sx - rad, sy - rad, rad * 2, rad * 2);
  }
  ctx.restore();
}

// ------------------------------------------------------------------ scenes G–I: the reversal, on a blueprint sheet, at true size
function ruler(x0, y, mm, pxmm, t, t0) {
  const k = expoOut(ev(t, t0, .6)), n = Math.floor(mm * k);
  ctx.fillStyle = 'rgba(220,235,250,.08)'; ctx.fillRect(x0 - 10, y, mm * pxmm * k + 20, 70);
  ctx.strokeStyle = LINE; ctx.lineWidth = 1.5; ctx.beginPath();
  for (let i = 0; i <= n; i++) { const x = x0 + i * pxmm, h = i % 10 === 0 ? 34 : i % 5 === 0 ? 22 : 12; ctx.moveTo(x, y); ctx.lineTo(x, y + h); }
  ctx.stroke();
  ctx.font = `400 26px ${UI}`; ctx.fillStyle = LINE; ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
  for (let i = 0; i <= n; i += 10) ctx.fillText(String(i / 10), x0 + i * pxmm, y + 62);
  if (k > .9) { ctx.textAlign = 'left'; ctx.fillText('cm', x0 + mm * pxmm + 16, y + 62); }
}
function wave(x0, y, len, amp, col, lw) {
  ctx.strokeStyle = col; ctx.lineWidth = lw; ctx.lineCap = 'round'; ctx.beginPath();
  for (let i = 0; i <= 200; i++) { const u = i / 200, x = x0 + u * len, yy = y - amp * Math.sin(TAU * u); i ? ctx.lineTo(x, yy) : ctx.moveTo(x, yy); }
  ctx.stroke();
}
function eye(cx, cy, s) {     // s = px per mm; the pupil is 3 mm
  ctx.strokeStyle = LINE; ctx.lineWidth = 3; ctx.beginPath();
  ctx.moveTo(cx - 13 * s, cy); ctx.quadraticCurveTo(cx, cy - 11 * s, cx + 13 * s, cy); ctx.quadraticCurveTo(cx, cy + 11 * s, cx - 13 * s, cy); ctx.stroke();
  ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(cx, cy, 5.5 * s, 0, TAU); ctx.stroke();
  ctx.fillStyle = '#060C1C'; ctx.beginPath(); ctx.arc(cx, cy, 1.5 * s, 0, TAU); ctx.fill(); ctx.strokeStyle = HOT; ctx.lineWidth = 2; ctx.stroke();
}
const SNAP = [0, 1, 2].map(() => { const c = document.createElement('canvas'); c.width = W / 3; c.height = H / 3; return c; });
const MIP = [1, 2, 3, 4, 5, 6].map(k => { const c = document.createElement('canvas'); c.width = Math.max(2, (W / 3) >> k); c.height = Math.max(2, (H / 3) >> k); return c; });
function blurDraw(src, lv, x, y, w, h) {
  let prev = src; const n = Math.min(6, Math.floor(lv));
  for (let i = 0; i < n; i++) { const g = MIP[i].getContext('2d'); g.imageSmoothingEnabled = true; g.clearRect(0, 0, MIP[i].width, MIP[i].height); g.drawImage(prev, 0, 0, MIP[i].width, MIP[i].height); prev = MIP[i]; }
  ctx.imageSmoothingEnabled = true; ctx.imageSmoothingQuality = 'high'; ctx.drawImage(prev, x, y, w, h);
}
function revealScene(t) {
  sheetBG(false);
  const pxmm = 6.4, x0 = (W - 125 * pxmm) / 2, wy = 700;
  const grow = expoOut(ev(t, C.ruler - .2, 1.0));
  if (t < C.ruler) {      // what you think: a tiny wave, held up in a loupe
    const k = expoOut(ev(t, C.prop, .4)), cx = 540, cy = wy, R = 190 * k;
    ctx.fillStyle = 'rgba(6,12,28,.9)'; ctx.beginPath(); ctx.arc(cx, cy, R, 0, TAU); ctx.fill();
    ctx.strokeStyle = LINE; ctx.lineWidth = 3; ctx.stroke();
    ctx.save(); ctx.beginPath(); ctx.arc(cx, cy, R, 0, TAU); ctx.clip(); wave(cx - R * .8, cy, R * 1.6, 26, ACC, 4); ctx.restore();
    for (let i = 0; i < 4; i++) { const a = i * Math.PI / 2 + Math.PI / 4; ctx.beginPath(); ctx.moveTo(cx + Math.cos(a) * (R + 6), cy + Math.sin(a) * (R + 6)); ctx.lineTo(cx + Math.cos(a) * (R + 30), cy + Math.sin(a) * (R + 30)); ctx.stroke(); }
    if (k > .9) plateText('你以为的 Wi-Fi 波：很小', 160, cy + R + 90, { size: 50 });
  }
  if (t >= C.ruler && t < C.flash) {
    const pw = 150 * pxmm, ph = 72 * pxmm, px = (W - pw) / 2, py = 1000;      // the phone at true size: 150 × 72 mm
    ctx.strokeStyle = LINE; ctx.lineWidth = 2.5; ctx.beginPath(); ctx.roundRect(px, py, pw, ph, 50); ctx.stroke();
    ctx.lineWidth = 1.2; ctx.beginPath(); ctx.roundRect(px + 16, py + 16, pw - 32, ph - 32, 36); ctx.stroke();
    ctx.font = `400 28px ${UI}`; ctx.fillStyle = 'rgba(220,235,250,.7)'; ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic'; ctx.fillText('一部手机 · 约 15 cm', px, py + ph + 44);
  }
  const len = lerp(3 * pxmm, 125 * pxmm, grow), amp = lerp(8, 110, grow);
  if (t >= C.ruler - .2 && t < C.pupil + .35) wave((W - len) / 2, wy, len, amp, ACC, 7);
  if (t >= C.ruler) ruler(x0, wy + 150, 130, pxmm, t, C.ruler);
  if (t >= C.long) {
    const k = expoOut(ev(t, C.long, .4)), a = x0, b = x0 + 125 * pxmm * k, y = wy - 160;
    ctx.strokeStyle = LINE; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(a, y); ctx.lineTo(b, y); ctx.moveTo(a, y - 14); ctx.lineTo(a, y + 14); ctx.moveTo(b, y - 14); ctx.lineTo(b, y + 14); ctx.stroke();
    ctx.font = `200 96px ${FIG}`; ctx.fillStyle = ACC; ctx.textAlign = 'center'; ctx.fillText(roll('12.5 cm', t, C.long, .5), W / 2, y - 30);
  }
  if (t >= C.pupil && t < C.flash) {      // your pupil at true size; the wave comes down and cannot get in
    const k = expoOut(ev(t, C.pupil, .4)), ex = 540, ey = 1240;
    ctx.fillStyle = '#0E2250'; ctx.fillRect(0, 900, W, 700);
    eye(ex, ey, pxmm);
    ctx.strokeStyle = HOT; ctx.lineWidth = 2; ctx.setLineDash([8, 8]); ctx.beginPath(); ctx.arc(ex, ey, 40 + 30 * (1 - k), 0, TAU); ctx.stroke(); ctx.setLineDash([]);
    plateText('瞳孔 ≈ 3 mm', ex + 70, ey - 90, { size: 50 });
    const d = ev(t, C.pupil + .35, C.flash - C.pupil - .5);       // the wave descends onto the eye
    const wy2 = lerp(wy, ey, ease(d)), sq = 1 - .35 * smooth((d - .7) / .3);
    if (d > 0) {
      ctx.save(); ctx.globalAlpha = 1 - smooth((d - .85) / .15);
      wave(ex - 125 * pxmm * sq / 2, wy2, 125 * pxmm * sq, 110 * (1 + .4 * smooth((d - .7) / .3)), ACC, 7);
      ctx.restore();
      if (d > .85) { const g = ctx.createRadialGradient(ex, ey, 0, ex, ey, 420); g.addColorStop(0, 'rgba(255,170,100,.55)'); g.addColorStop(1, 'rgba(255,106,26,0)'); ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.fillStyle = g; ctx.fillRect(ex - 420, ey - 420, 840, 840); ctx.restore(); plateText('挤不进去', ex - 380, ey + 160, { size: 54, accent: true }); }
    }
  }
  if (t >= C.flash) {      // the clear pictures you were shown, full screen, one by one, each going to blur
    const shots = [7.6, 12.6, 29.9], span = (C.blind + .6 - C.flash) / 3, i = Math.min(2, Math.floor((t - C.flash) / span));
    const lt = (t - C.flash - i * span) / span, lv = i < 2 ? 1.5 + 3.5 * smooth(lt) : 2 + 4 * smooth((t - C.blind + .2) / .8);
    const c = SNAP[0], g = c.getContext('2d'); g.setTransform(1 / 3, 0, 0, 1 / 3, 0, 0);
    withCtx(g, () => { frameIso(shots[i]); }); g.setTransform(1, 0, 0, 1, 0, 0);
    blurDraw(c, lv, 0, 0, W, H);
    ctx.fillStyle = 'rgba(8,14,30,.25)'; ctx.fillRect(0, 0, W, H);
  }
}
function growScene(t) {      // the pupil you would need grows from 3 mm to 500 m; the world passes it at true scale
  sheetBG(false);
  const GE = C.q + 1.0, p = smooth(ev(t, C.grow + .1, GE - C.grow - .1));
  const pupilM = Math.exp(lerp(Math.log(.003), Math.log(500), p)), done = t >= GE;
  const scale = 300 / pupilM, cx = 540, ey = 840, ground = 1250;
  const m = smooth(ev(t, C.fastIn - .8, .8));          // the morph: the pupil becomes the rim of a dish
  ctx.strokeStyle = 'rgba(220,235,250,.5)'; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(0, ground); ctx.lineTo(W, ground); ctx.stroke();
  // things at true scale standing on the ground under the eye: they go by as the eye grows
  ctx.font = `700 34px ${UI}`; ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
  for (const [w, h, lab, kind] of [[.07, .15, '手机 15 cm', 'phone'], [.5, 1.7, '人 1.7 m', 'person'], [30, 45, '一栋楼 45 m', 'bld'], [300, 24, '一条街 300 m', 'street']]) {
    const wp = w * scale, hp = h * scale; if (hp > 1150 || wp < 6) continue;
    const a = clamp(Math.min((1150 - hp) / 250, wp / 30)) * (1 - m);
    if (a <= 0) continue;
    ctx.save(); ctx.globalAlpha = a; ctx.strokeStyle = LINE; ctx.lineWidth = 2.5;
    if (kind === 'phone') { ctx.beginPath(); ctx.roundRect(cx - wp / 2, ground - hp, wp, hp, wp * .18); ctx.stroke(); }
    else if (kind === 'person') { const r = wp * .22; ctx.beginPath(); ctx.arc(cx, ground - hp + r, r, 0, TAU); ctx.moveTo(cx, ground - hp + 2 * r); ctx.lineTo(cx, ground - hp * .45); ctx.lineTo(cx - wp * .3, ground); ctx.moveTo(cx, ground - hp * .45); ctx.lineTo(cx + wp * .3, ground); ctx.moveTo(cx - wp * .45, ground - hp * .7); ctx.lineTo(cx + wp * .45, ground - hp * .7); ctx.stroke(); }
    else if (kind === 'bld') { ctx.strokeRect(cx - wp / 2, ground - hp, wp, hp); for (let f = 1; f < 15; f++) { ctx.beginPath(); ctx.moveTo(cx - wp / 2, ground - hp * f / 15); ctx.lineTo(cx + wp / 2, ground - hp * f / 15); ctx.stroke(); } }
    else { const n = 9; for (let k = 0; k < n; k++) { const bw = wp / n * .8, bh = hp * (.5 + .5 * Math.abs(Math.sin(k * 2.3))); ctx.strokeRect(cx - wp / 2 + k * wp / n, ground - bh, bw, bh); } }
    if (hp > 40 || wp > 80) { ctx.fillStyle = LINE; ctx.fillText(lab, cx, ground - hp - 16); }
    ctx.restore();
  }
  // the eye: lids and iris fade as the pupil turns into the dish's rim
  ctx.save(); ctx.globalAlpha = 1 - m;
  ctx.strokeStyle = LINE; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(cx - 400, ey); ctx.quadraticCurveTo(cx, ey - 330, cx + 400, ey); ctx.quadraticCurveTo(cx, ey + 330, cx - 400, ey); ctx.stroke();
  ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(cx, ey, 250, 0, TAU); ctx.stroke();
  ctx.restore();
  const ry = lerp(150, 150 * .5774, m);
  ctx.fillStyle = `rgba(6,12,28,${1 - .6 * m})`; ctx.beginPath(); ctx.ellipse(cx, ey, 150, ry, 0, 0, TAU); ctx.fill();
  ctx.strokeStyle = HOT; ctx.lineWidth = 2 + 2 * m; ctx.stroke();
  ctx.strokeStyle = LINE; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(cx - 150, ey + 175); ctx.lineTo(cx + 150, ey + 175); ctx.moveTo(cx - 150, ey + 161); ctx.lineTo(cx - 150, ey + 189); ctx.moveTo(cx + 150, ey + 161); ctx.lineTo(cx + 150, ey + 189); ctx.stroke();
  const lab = pupilM < 1 ? `${Math.round(pupilM * 1000)} mm` : `${Math.round(pupilM)} m`;
  ctx.font = `200 96px ${FIG}`; ctx.fillStyle = done ? ACC : '#F4F8FC'; ctx.textAlign = 'center'; ctx.fillText(done ? '≈ 500 m' : lab, cx, ey + 285);
  if (done) { ctx.font = `400 30px ${UI}`; ctx.fillStyle = 'rgba(220,235,250,.75)'; ctx.fillText('需要的瞳孔 · 按人眼的清晰度估算', cx, ey + 335); }
  display([[['什么样的眼睛，', '#F4F8FC']], [['才有资格看见 ', '#F4F8FC'], ['Wi-Fi', ACC], ['？', '#F4F8FC']]], 72, 330, t, C.q + .2, { size: 88, lh: 116 });
}

// ------------------------------------------------------------------ scene K: 中国天眼 — the eye big enough to see Wi-Fi, and the one thing it fears
const KARST = (() => { const r = mulberry32(41), a = []; for (let i = 0; i < 70; i++) { const th = r() * TAU, d = 330 + r() * 900; a.push([Math.cos(th) * d, Math.sin(th) * d, 60 + r() * 140, 90 + r() * 160]); } return a.sort((p, q) => (p[0] + p[1]) - (q[0] + q[1])); })();
const PHONES = (() => { const r = mulberry32(43), a = []; for (let i = 0; i < 46; i++) { const th = r() * TAU, d = 600 + Math.sqrt(r()) * 8000; a.push([Math.cos(th) * d, Math.sin(th) * d, r()]); } return a; })();
function fastScene(t) {
  sheetBG(false);
  ctx.fillStyle = 'rgba(2,8,24,.35)'; ctx.fillRect(0, 0, W, H);
  const ring = (R, z, col, lw, dash) => { const [cx, cy] = iso(0, 0, z); ctx.strokeStyle = col; ctx.lineWidth = lw; ctx.setLineDash(dash || []); ctx.beginPath(); ctx.ellipse(cx, cy, 1.2247 * R * K, .7071 * R * K, 0, 0, TAU); ctx.stroke(); ctx.setLineDash([]); };
  // the karst hills around it
  for (const [x, y, h, w] of KARST) { const [bx, by] = iso(x, y, 0), [tx, ty] = iso(x, y, h); ctx.fillStyle = 'rgba(10,24,58,.85)'; ctx.strokeStyle = 'rgba(220,235,250,.35)'; ctx.lineWidth = 1.2; ctx.beginPath(); ctx.moveTo(bx - w * K * .6, by); ctx.quadraticCurveTo(tx - w * K * .1, ty, tx, ty); ctx.quadraticCurveTo(tx + w * K * .1, ty, bx + w * K * .6, by); ctx.closePath(); ctx.fill(); ctx.stroke(); }
  // the dish: 500 m across — the one real thing on the sheet: lit panels, a bright rim, a glowing cabin
  { const [cx, cy] = iso(0, 0, -40), rx = 1.2247 * 250 * K, ryy = .7071 * 250 * K;
    ctx.save(); ctx.beginPath(); ctx.ellipse(...iso(0, 0, 0), rx, ryy, 0, 0, TAU); ctx.clip();
    const g = ctx.createRadialGradient(cx, cy + ryy * .2, 0, cx, cy, rx); g.addColorStop(0, 'rgba(230,240,252,.55)'); g.addColorStop(.6, 'rgba(160,190,230,.35)'); g.addColorStop(1, 'rgba(90,120,170,.25)');
    ctx.fillStyle = g; ctx.fillRect(cx - rx, cy - rx, 2 * rx, 2 * rx); ctx.restore(); }
  for (let R = 30; R <= 250; R += 22) ring(R, -R * R / 600, `rgba(240,248,255,${R === 250 ? 1 : .55})`, R === 250 ? 4 : 1.4);
  { ctx.save(); ctx.shadowColor = '#DCEBFA'; ctx.shadowBlur = 24; ring(250, 0, '#FFFFFF', 3); ctx.restore(); }
  ctx.strokeStyle = 'rgba(240,248,255,.45)'; ctx.lineWidth = 1.2; ctx.beginPath();
  for (let i = 0; i < 24; i++) { const a = i / 24 * TAU; for (let R = 30; R <= 250; R += 22) { const p = iso(Math.cos(a) * R, Math.sin(a) * R, -R * R / 600); R === 30 ? ctx.moveTo(...p) : ctx.lineTo(...p); } } ctx.stroke();
  const cab = [0, 0, 140];
  for (let i = 0; i < 6; i++) { const a = i / 6 * TAU + .3, tw = [Math.cos(a) * 300, Math.sin(a) * 300]; const [bx, by] = iso(tw[0], tw[1], 0), [tx, ty] = iso(tw[0], tw[1], 170), [cx, cy] = iso(...cab);
    ctx.strokeStyle = 'rgba(240,248,255,.9)'; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(bx, by); ctx.lineTo(tx, ty); ctx.stroke(); ctx.lineWidth = 1.6; ctx.beginPath(); ctx.moveTo(tx, ty); ctx.lineTo(cx, cy); ctx.stroke(); }
  { const [cx, cy] = iso(...cab); ctx.save(); ctx.shadowColor = HOT; ctx.shadowBlur = 30; ctx.fillStyle = HOT; ctx.fillRect(cx - 9, cy - 9, 18, 18); ctx.restore(); }
  if (t >= C.d500) {     // dimension across the dish
    const k = expoOut(ev(t, C.d500, .45)), [ax, ay] = iso(-250 / 1.2247 * .816, 250 / 1.2247 * .816, 0), [cx, cy] = iso(0, 0, 0), y = cy + .7071 * 250 * K + 60;
    const x0 = cx - 1.2247 * 250 * K * k, x1 = cx + 1.2247 * 250 * K * k;
    ctx.strokeStyle = LINE; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(x0, y); ctx.lineTo(x1, y); ctx.moveTo(x0, y - 14); ctx.lineTo(x0, y + 14); ctx.moveTo(x1, y - 14); ctx.lineTo(x1, y + 14); ctx.stroke();
    ctx.font = `200 90px ${FIG}`; ctx.fillStyle = ACC; ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic'; ctx.fillText(roll('500 m', t, C.d500, .4), cx, y + 100);
  }
  // phones around it: to this eye each one is a small sun
  const pk = smooth(ev(t, C.phones - .3, .6));
  if (pk > 0) {
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    for (const [x, y, ph] of PHONES) {
      const off = t >= C.ban + ph * .9; const [sx, sy] = iso(x, y, 0);
      const inside = Math.hypot(x, y) < 5000;
      const a = pk * (off && inside ? 0 : .9), rad = Math.max(10, 600 * K);
      if (a > 0) { const g = ctx.createRadialGradient(sx, sy, 0, sx, sy, rad); g.addColorStop(0, `rgba(255,235,215,${a})`); g.addColorStop(.2, `rgba(255,140,60,${a * .5})`); g.addColorStop(1, 'rgba(255,106,26,0)'); ctx.fillStyle = g; ctx.fillRect(sx - rad, sy - rad, 2 * rad, 2 * rad); }
      if (off && inside) { ctx.globalCompositeOperation = 'source-over'; ctx.strokeStyle = ACC; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(sx - 8, sy - 8); ctx.lineTo(sx + 8, sy + 8); ctx.moveTo(sx + 8, sy - 8); ctx.lineTo(sx - 8, sy + 8); ctx.stroke(); ctx.globalCompositeOperation = 'lighter'; }
    }
    ctx.restore();
  }
  if (t >= C.km5) { const k = expoOut(ev(t, C.km5, .6)); ring(5000 * k, 0, HOT, 3, [14, 10]); if (k > .9) { const [cx, cy] = iso(0, 0, 0); plateText('方圆 5 km', cx + 1.2247 * 5000 * K * .55, cy - .7071 * 5000 * K * .85, { size: 50 }); } }
  if (t >= C.ban) { const [cx, cy] = iso(0, 0, 0); plateText('禁止带手机', cx - 1.2247 * 5000 * K * .9, cy + .7071 * 5000 * K + 90, { size: 56, accent: true }); }
  display([[['中国天眼', '#F4F8FC']]], 72, 320, t, C.fast, { size: 110 });
  if (t > C.fast + .3) { ctx.font = `400 34px ${UI}`; ctx.fillStyle = 'rgba(220,235,250,.75)'; ctx.textAlign = 'left'; ctx.fillText('FAST · 贵州平塘 · 收得到 2.4 GHz', 76, 380); }
}

// ------------------------------------------------------------------ scene J: the sea — blurred, crowded, never still; then black
const SEA = document.createElement('canvas'); SEA.width = 108; SEA.height = 192;
const SEAS = (() => { const r = mulberry32(5), S = []; for (let i = 0; i < 40; i++) S.push([r() * 108, r() * 192, .6 + r(), r() * 6, .3 + r() * .7]); return S; })();
function seaScene(t) {
  const g = SEA.getContext('2d'), im = g.createImageData(108, 192), d = im.data;
  for (let j = 0; j < 192; j++) for (let i = 0; i < 108; i++) {
    let re = 0, im2 = 0;
    for (const [x, y, a, ph, sp] of SEAS) { const xx = x + 8 * Math.sin(t * .3 * sp + ph), yy = y + 8 * Math.cos(t * .27 * sp + ph); const rr = Math.hypot(i - xx, j - yy); const p2 = rr * .5 - t * 3 * sp + ph; re += a * Math.cos(p2) / (1 + rr * .08); im2 += a * Math.sin(p2) / (1 + rr * .08); }
    const I = 1 - Math.exp(-(re * re + im2 * im2) * .06), o = (j * 108 + i) * 4;
    d[o] = 20 + 235 * I; d[o + 1] = 40 + 120 * I * I; d[o + 2] = 90 + 10 * I - 60 * I * I; d[o + 3] = 255;
  }
  g.putImageData(im, 0, 0);
  ctx.imageSmoothingEnabled = true; ctx.imageSmoothingQuality = 'high'; ctx.drawImage(SEA, -40, -40, W + 80, H + 80);
  const blk = smooth(ev(t, C.black - .6, .6));
  if (blk > 0) { ctx.fillStyle = `rgba(0,0,0,${blk})`; ctx.fillRect(0, 0, W, H); }
}
function endScene(t) {
  ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);
  if (t < C.next) return;
  display([[['下一个「如果」，', '#F4F4F2']], [['你想看什么？', ACC]]], 72, 860, t, C.next, { size: 96, lh: 128 });
  ctx.font = `400 32px ${UI}`; ctx.fillStyle = 'rgba(244,244,242,.6)'; ctx.textAlign = 'left'; ctx.fillText('如果……会怎样 · 01', 76, 1130);
}

// ------------------------------------------------------------------ the whole frame
const OFFH = document.createElement('canvas'); OFFH.width = W; OFFH.height = H;
function frameIso(t) {
  if (t < C.street) {
    [CU, CV, K] = camFrom(CAM_ROOM, t);
    const s = lerp(-2.2, 9.5, ease(ev(t, C.pak, .95)));
    if (t < C.pak) humanView(t);
    else if (s < ROOM.X + 2.4) {
      roomScene(t);
      const g = OFFH.getContext('2d'); g.setTransform(1, 0, 0, 1, 0, 0);
      withCtx(g, () => humanView(t));
      ctx.save(); ctx.beginPath(); ctx.rect(0, 0, W, H); const a = iso(s, -20, 0), b = iso(s, 30, 0); ctx.moveTo(...a); ctx.lineTo(...b); ctx.lineTo(b[0] - 4000, b[1] - 2300); ctx.lineTo(a[0] - 4000, a[1] - 2300); ctx.closePath(); ctx.clip('evenodd'); ctx.drawImage(OFFH, 0, 0); ctx.restore();
      const q = [iso(s, -.3, 0), iso(s, ROOM.Y + .3, 0), iso(s, ROOM.Y + .3, 3.1), iso(s, -.3, 3.1)];
      ctx.save(); ctx.globalCompositeOperation = 'lighter'; poly(q, 'rgba(255,140,70,.10)'); ctx.strokeStyle = HOT; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(...q[0]); ctx.lineTo(...q[1]); ctx.stroke(); ctx.restore();
    } else roomScene(t);
  } else if (t < C.city) { [CU, CV, K] = camFrom(CAM_STREET, t); streetScene(t); }
  else { [CU, CV, K] = camFrom(CAM_CITY, t); cityScene(t); }
}
const SKIP = new Set(['如果你的眼睛，突然能看见 Wi-Fi？', '什么样的眼睛，才有资格看见 Wi-Fi？', '下一个如果，你想看什么？']);
const CLEAN = location.search.includes('clean');
function subtitles(t) {
  if (CLEAN) return;
  const c = CUES.subs.find(c => t >= c.t0 && t < c.t1); if (!c || SKIP.has(c.text)) return;
  ctx.font = `700 54px ${UI}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.lineJoin = 'round';
  ctx.lineWidth = 12; ctx.strokeStyle = '#0B1328'; ctx.strokeText(c.text, W / 2, 1600); ctx.fillStyle = '#F7F4EE'; ctx.fillText(c.text, W / 2, 1600);
}
function mood(t) {      // one colour feeling per act: warm life → bright orange wonder → darker, redder unease → cold reversal
  const wish = smooth(ev(t, C.pak + .4, 1)) * (1 - smooth(ev(t, C.turn, 1.2)));
  const uneasy = smooth(ev(t, C.turn, 1.5)) * (1 - smooth(ev(t, C.freeze, .2)));
  const cold = t >= C.prop && t < C.sea ? 1 : 0;
  if (wish > 0) { ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.fillStyle = `rgba(255,120,40,${.07 * wish})`; ctx.fillRect(0, 0, W, H); ctx.restore(); }
  if (uneasy > 0) { ctx.fillStyle = `rgba(40,4,30,${.22 * uneasy})`; ctx.fillRect(0, 0, W, H); }
  if (cold > 0) { ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.fillStyle = 'rgba(150,215,235,1)'; ctx.globalAlpha = .35; ctx.fillRect(0, 0, W, H); ctx.restore(); }
}
window.seek = function (t) {
  t = clamp(t, 0, DUR - 1 / FPS);
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over';
  BOOST = 1 + .7 * smooth(ev(t, C.router, 1)) * (1 - smooth(ev(t, C.wobble, .4)));
  if (t < C.freeze) {
    const jolt = t >= C.wobble && t < C.wobble + .35 ? (1 - (t - C.wobble) / .35) : 0;
    if (jolt > 0) { ctx.save(); ctx.translate(18 * jolt * Math.sin(t * 90), 12 * jolt * Math.cos(t * 77)); }
    frameIso(t);
    if (jolt > 0) { ctx.restore(); ctx.fillStyle = `rgba(255,240,230,${.55 * jolt * jolt})`; ctx.fillRect(0, 0, W, H); }
  }
  else if (t < C.prop) {      // wait: the city freezes and the colour drains out
    frameIso(C.freeze);
    const k = smooth(ev(t, C.freeze, .35));
    ctx.save(); ctx.globalCompositeOperation = 'saturation'; ctx.fillStyle = `rgba(128,128,128,${k})`; ctx.fillRect(0, 0, W, H); ctx.restore();
    ctx.fillStyle = `rgba(4,8,20,${.4 * k})`; ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = 'rgba(220,235,250,.06)'; for (let y = (t * 300) % 8; y < H; y += 8) ctx.fillRect(0, y, W, 1);
  }
  else if (t < C.grow) revealScene(t);
  else if (t < C.fastIn) growScene(t);
  else if (t < C.sea) { [CU, CV, K] = camFrom(CAM_FAST, t); fastScene(t); }
  else if (t < C.next - .4) seaScene(t);
  else endScene(t);
  mood(t);
  if (t < C.pak + .25) display([[['如果你的眼睛，', INK]], [['突然能看见 ', INK], ['Wi-Fi', ACC], ['？', INK]]], 72, 300, t, -1, { size: 84, lh: 110 });
  panel(t);
  subtitles(t);
  return true;
};
window.DURATION = DUR; window.FPS = FPS;
window.ready = Promise.all([`200 84px ${FIG}`, `700 54px ${UI}`, `900 84px ${DSP}`].map(f => document.fonts.load(f)));
