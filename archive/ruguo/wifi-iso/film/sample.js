// 如果你的眼睛能看见 Wi-Fi — 10 s style sample.
// An isometric cutaway flat (infographic: three flat tones, leaders, a floating slab with a hatched section),
// a scan plane sweeps it into Wi-Fi vision (hologram: scan front, target brackets, numbers that roll into place),
// and Wi-Fi vision is a blueprint sheet (white line work on Prussian blue, hidden walls dashed, dimension lines).
// Pure function of time: seek(t) paints frame t. Seeded noise only.
'use strict';
const W = 1080, H = 1920, FPS = 30, DUR = 11.6;
const cv = document.getElementById('c'); cv.width = W; cv.height = H;
let ctx = cv.getContext('2d');
function withCtx(g, fn) { const r = ctx; ctx = g; fn(); ctx = r; }
const UI = '"Noto Sans Mono CJK SC"', FIG = '"Inter Tight"';
const ACC = '#FF6A1A', HOT = '#FFD9B8';
const LINE = '#DCEBFA';                       // blueprint white line
const C30 = Math.cos(Math.PI / 6), TAU = Math.PI * 2;
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, k) => a + (b - a) * k;
const ev = (t, t0, d) => clamp((t - t0) / d);
const smooth = x => { x = clamp(x); return x * x * (3 - 2 * x); };
const ease = x => { x = clamp(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
const expoOut = x => { x = clamp(x); return x === 1 ? 1 : 1 - Math.pow(2, -10 * x); };
function mulberry32(a) { return () => { a |= 0; a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }

// ------------------------------------------------------------------ timing (from the approved script's voice layout)
const T = { scan: 0.5, router: 1.5, wall: 3.0, you: 4.0, light: 6.0, lam: 8.0, lens: 9.0, ratio: 10.0 };
const SUBS = [[0.45, 1.89, '如果你的眼睛能看见 Wi-Fi'], [1.91, 2.85, '你家会变成这样'], [2.87, 5.28, '墙是透明的，你却是黑的'],
  [5.95, 7.19, 'Wi-Fi 其实也是光'], [7.21, 8.77, '只是波长有 12 厘米'], [8.79, 11.4, '比你看见的光长了约 25 万倍']];

// ------------------------------------------------------------------ isometric camera: world metres (x down-right, y down-left, z up)
let CU = 0, CV = 0, K = 90, OY = 0;
const iso = (x, y, z) => [W / 2 + ((x - y) * C30 - CU) * K, H / 2 + OY + ((x + y) * .5 - z - CV) * K];
const KEYS = [   // t, cu, cv, k
  [0, .2, 1.55, 128], [1.9, .45, 1.7, 110], [2.8, .7, 1.8, 104], [3.9, 1.0, 1.95, 112], [5.0, .45, .45, 205],
  [6.0, -1.9, 1.2, 250], [8.6, -1.75, 1.22, 270], [11.6, -1.7, 1.25, 285],
];
function camAt(t) {
  let i = 0; while (i < KEYS.length - 2 && t > KEYS[i + 1][0]) i++;
  const a = KEYS[i], b = KEYS[i + 1], p = ease(ev(t, a[0], b[0] - a[0]));
  // continuous drift so the frame never stops dead
  return [lerp(a[1], b[1], p), lerp(a[2], b[2], p), lerp(a[3], b[3], p) * (1 + .004 * Math.sin(t * .9))];
}

// ------------------------------------------------------------------ the flat: 7 × 5 m, two back walls, a cut partition with a doorway
const ROOM = { X: 7, Y: 5, H: 2.7, slab: .35 };
const ROUTER = [0.17, 3.5, 1.5];
const PERSON = { x: 1.35, y: .72 };
// boxes: [x0, x1, y0, y1, z0, z1, base colour, material: 'wood' | 'fabric' | 'metal' | 'wall' | 'dark']
const BOX = [
  [-0.16, 0, 0, ROOM.Y, 0, ROOM.H, '#E4DDD2', 'wall'],              // back wall (x = 0)
  [0, ROOM.X, -0.16, 0, 0, ROOM.H, '#E9E3D9', 'wall'],              // back wall (y = 0)
  [4.1, 4.28, 0, 2.0, 0, 1.15, '#E9E3D9', 'wall', 'cut'],           // partition, cut at 1.15 m
  [4.1, 4.28, 2.95, ROOM.Y, 0, 1.15, '#E9E3D9', 'wall', 'cut'],
  [0.35, 2.45, 0.15, 1.05, 0, .42, '#7F8FA6', 'fabric'],            // sofa seat
  [0.35, 2.45, 0.05, 0.3, 0, .9, '#7F8FA6', 'fabric'],              // sofa back
  [0.2, 0.38, 0.05, 1.05, 0, .62, '#76859C', 'fabric'], [2.42, 2.6, 0.05, 1.05, 0, .62, '#76859C', 'fabric'],
  [1.0, 2.05, 1.75, 2.45, 0, .42, '#B98E66', 'wood'],               // coffee table
  [0, .38, 3.2, 3.8, 1.36, 1.42, '#B98E66', 'wood'],                // shelf
  [.04, .3, 3.37, 3.63, 1.42, 1.48, '#2F3238', 'dark', 'router'],   // router
  [4.45, 6.0, .05, .7, 0, .9, '#A7A097', 'wood'],                   // kitchen counter
  [4.75, 5.35, .1, .55, .9, 1.22, '#C6CCD5', 'metal'],              // microwave
  [6.1, 6.9, .05, .8, 0, 1.85, '#C3C9D2', 'metal'],                 // fridge
  [6.3, 6.75, 3.9, 4.6, 0, .35, '#8E7C6A', 'wood'],                 // plant pot
];
const shade = (hex, k) => { const n = parseInt(hex.slice(1), 16); const r = n >> 16, g = n >> 8 & 255, b = n & 255;
  const to = k > 0 ? [255, 250, 240] : [35, 28, 48], a = Math.abs(k); return `rgb(${lerp(r, to[0], a) | 0},${lerp(g, to[1], a) | 0},${lerp(b, to[2], a) | 0})`; };
function poly(pts, fill, stroke, lw, dash) {
  ctx.beginPath(); pts.forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)); ctx.closePath();
  if (fill) { ctx.fillStyle = fill; ctx.fill(); }
  if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = lw; ctx.setLineDash(dash || []); ctx.stroke(); ctx.setLineDash([]); }
}
const faces = b => {
  const [x0, x1, y0, y1, z0, z1] = b;
  return {
    top: [iso(x0, y0, z1), iso(x1, y0, z1), iso(x1, y1, z1), iso(x0, y1, z1)],
    px: [iso(x1, y0, z0), iso(x1, y1, z0), iso(x1, y1, z1), iso(x1, y0, z1)],
    py: [iso(x0, y1, z0), iso(x1, y1, z0), iso(x1, y1, z1), iso(x0, y1, z1)],
  };
};
const depth = b => (b[7] === 'wall' && b[8] !== 'cut') ? -100 : (b[0] + b[1]) / 2 + (b[2] + b[3]) / 2 + b[4] * .1;   // back walls first
const ORDER = BOX.map((b, i) => i).sort((a, b) => depth(BOX[a]) - depth(BOX[b]));

// hatched section (a cut face): 45° hatching clipped to the face
function hatchFace(pts, col, gap, lw) {
  ctx.save(); poly(pts); ctx.clip();
  const xs = pts.map(p => p[0]), ys = pts.map(p => p[1]);
  const x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = Math.min(...ys), y1 = Math.max(...ys);
  ctx.strokeStyle = col; ctx.lineWidth = lw; ctx.beginPath();
  for (let s = x0 - (y1 - y0); s < x1; s += gap) { ctx.moveTo(s, y1); ctx.lineTo(s + (y1 - y0), y0); }
  ctx.stroke(); ctx.restore();
}

// ------------------------------------------------------------------ the person: a minimal billboard, seated, phone in hand
function personPts() {
  const k = K / 80, [bx, by] = iso(PERSON.x, PERSON.y, .42);
  return { bx, by, k };
}
function drawPerson(mode) {
  const { bx, by, k } = personPts();
  const body = mode === 'wifi' ? '#000' : '#2E7A78', legs = mode === 'wifi' ? '#000' : '#34383F', skin = mode === 'wifi' ? '#000' : '#E5C2A6';
  ctx.save(); ctx.translate(bx, by); ctx.scale(k, k);
  ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  if (mode === 'wifi') { ctx.shadowColor = ACC; ctx.shadowBlur = 18; }
  ctx.fillStyle = body;
  ctx.beginPath(); ctx.moveTo(-20, 0); ctx.lineTo(-14, -92); ctx.quadraticCurveTo(0, -104, 14, -92); ctx.lineTo(22, 0); ctx.closePath(); ctx.fill();   // torso
  ctx.strokeStyle = legs; ctx.lineWidth = 22; ctx.beginPath(); ctx.moveTo(-6, -4); ctx.lineTo(34, 18); ctx.lineTo(34, 66); ctx.stroke();               // legs
  ctx.strokeStyle = body; ctx.lineWidth = 12; ctx.beginPath(); ctx.moveTo(6, -78); ctx.lineTo(30, -46); ctx.lineTo(44, -62); ctx.stroke();                                     // arm
  ctx.fillStyle = skin; ctx.beginPath(); ctx.arc(2, -122, 21, 0, TAU); ctx.fill();
  if (mode !== 'wifi') { ctx.fillStyle = '#2A2522'; ctx.beginPath(); ctx.arc(2, -126, 22, Math.PI * 1.05, Math.PI * 2.05); ctx.fill(); }   // head, hair
  ctx.shadowBlur = 0;
  ctx.fillStyle = mode === 'wifi' ? HOT : '#22262C'; ctx.save(); ctx.translate(46, -66); ctx.rotate(-.5); ctx.fillRect(-7, -12, 14, 24); ctx.restore();   // phone
  if (mode === 'wifi') { ctx.strokeStyle = ACC; ctx.lineWidth = 2.5; ctx.globalAlpha = .9;
    ctx.beginPath(); ctx.moveTo(-20, 0); ctx.lineTo(-14, -92); ctx.quadraticCurveTo(0, -104, 14, -92); ctx.stroke(); ctx.beginPath(); ctx.arc(2, -122, 21, Math.PI * .7, Math.PI * 1.9); ctx.stroke(); ctx.globalAlpha = 1; }
  ctx.restore();
}

// ------------------------------------------------------------------ backgrounds
const DOTS = (() => { const r = mulberry32(3), a = []; for (let i = 0; i < 900; i++) a.push([r(), r(), r()]); return a; })();
function paperBG() {
  ctx.fillStyle = '#EEE8DC'; ctx.fillRect(0, 0, W, H);
  ctx.fillStyle = 'rgba(60,50,40,.10)';
  for (let x = -4; x <= 12; x++) for (let y = -6; y <= 10; y++) { const [sx, sy] = iso(x, y, -0.35); if (sx > -10 && sx < W + 10 && sy > -10 && sy < H + 10) { ctx.beginPath(); ctx.arc(sx, sy, 2.2, 0, TAU); ctx.fill(); } }
}
const SHEET = (() => {   // a cyanotype sheet: two Prussian blues, soft streaks and specks (seeded, built once)
  const c = document.createElement('canvas'); c.width = 540; c.height = 960; const g = c.getContext('2d');
  const gr = g.createLinearGradient(0, 0, 540, 960); gr.addColorStop(0, '#16336B'); gr.addColorStop(1, '#10285A'); g.fillStyle = gr; g.fillRect(0, 0, 540, 960);
  const r = mulberry32(11);
  for (let i = 0; i < 70; i++) { g.fillStyle = `rgba(${r() < .5 ? '40,88,166' : '10,26,60'},${.05 + r() * .08})`; g.fillRect(0, r() * 960, 540, 2 + r() * 14); }
  for (let i = 0; i < 1600; i++) { g.fillStyle = `rgba(220,235,250,${r() * .12})`; g.fillRect(r() * 540, r() * 960, 1, 1); }
  return c;
})();
function sheetBG() {
  ctx.drawImage(SHEET, 0, 0, W, H);
  ctx.strokeStyle = 'rgba(220,235,250,.07)'; ctx.lineWidth = 1;   // the sheet's iso grid, every metre
  ctx.beginPath();
  for (let i = -6; i <= 14; i++) { let a = iso(i, -6, 0), b = iso(i, 12, 0); ctx.moveTo(...a); ctx.lineTo(...b); a = iso(-6, i, 0); b = iso(14, i, 0); ctx.moveTo(...a); ctx.lineTo(...b); }
  ctx.stroke();
}

// ------------------------------------------------------------------ human view: flat three-tone diorama on a floating slab
function slab(mode) {
  const { X, Y, slab: s } = ROOM;
  const top = [iso(0, 0, 0), iso(X, 0, 0), iso(X, Y, 0), iso(0, Y, 0)];
  const fx = [iso(X, 0, -s), iso(X, Y, -s), iso(X, Y, 0), iso(X, 0, 0)], fy = [iso(0, Y, -s), iso(X, Y, -s), iso(X, Y, 0), iso(0, Y, 0)];
  if (mode === 'human') {
    ctx.save(); ctx.shadowColor = 'rgba(40,30,20,.25)'; ctx.shadowBlur = 60; ctx.shadowOffsetY = 40; poly([iso(0, 0, -s), iso(X, 0, -s), iso(X, Y, -s), iso(0, Y, -s)], '#000'); ctx.restore();
    poly(top, '#D8C4A4'); poly(fx, '#8F8A84'); poly(fy, '#A9A39C');
    hatchFace(fx, 'rgba(40,36,32,.35)', 9, 1.2); hatchFace(fy, 'rgba(40,36,32,.3)', 9, 1.2);
    ctx.strokeStyle = 'rgba(80,60,40,.12)'; ctx.lineWidth = 1; ctx.beginPath();     // floor boards
    for (let x = .25; x < X; x += .25) { ctx.moveTo(...iso(x, 0, 0)); ctx.lineTo(...iso(x, Y, 0)); } ctx.stroke();
  } else {
    poly(top, 'rgba(220,235,250,.03)', 'rgba(220,235,250,.55)', 1.6);
    poly(fx, null, 'rgba(220,235,250,.45)', 1.2); poly(fy, null, 'rgba(220,235,250,.45)', 1.2);
    hatchFace(fx, 'rgba(220,235,250,.25)', 10, 1); hatchFace(fy, 'rgba(220,235,250,.25)', 10, 1);
  }
}
function drawBoxHuman(b) {
  const f = faces(b), col = b[6];
  poly(f.py, shade(col, -.06)); poly(f.px, shade(col, -.22)); poly(f.top, shade(col, .2));
  if (b[8] === 'cut') hatchFace(f.top, 'rgba(40,36,32,.55)', 7, 1.3);
  if (b[8] === 'router') { const [sx, sy] = iso(.17, 3.5, 1.48); ctx.strokeStyle = '#2F3238'; ctx.lineWidth = 3 * K / 92; ctx.beginPath(); ctx.moveTo(sx - 8 * K / 92, sy); ctx.lineTo(sx - 12 * K / 92, sy - 26 * K / 92); ctx.moveTo(sx + 8 * K / 92, sy); ctx.lineTo(sx + 12 * K / 92, sy - 26 * K / 92); ctx.stroke(); }
}
function windowHuman() {   // a window in the y = 0 wall
  const q = [iso(2.7, 0, .95), iso(3.8, 0, .95), iso(3.8, 0, 2.15), iso(2.7, 0, 2.15)];
  poly(q, '#BFD4E2', '#9DA9B2', 3);
  ctx.strokeStyle = '#9DA9B2'; ctx.lineWidth = 2.5; ctx.beginPath(); ctx.moveTo(...iso(3.25, 0, .95)); ctx.lineTo(...iso(3.25, 0, 2.15)); ctx.stroke();
}
function humanView(t) {
  paperBG(); slab('human');
  for (const i of ORDER) {
    const b = BOX[i];
    drawBoxHuman(b);
    if (i === 1) windowHuman();
    if (b[7] === 'fabric' && b[0] === 0.35 && b[4] === 0 && b[5] === .42) drawPerson('human');    // the person sits on the seat
  }
}

// ------------------------------------------------------------------ Wi-Fi view: the same flat as a blueprint, lit only by the router
const LAM = 0.125, VEL = 0.25;      // true wavelength; shells drift outward slowly so they can be seen
function wifiField(t, wallK) {
  const [rx, ry] = iso(...ROUTER), s = 1.2247 * K;
  ctx.save(); ctx.globalCompositeOperation = 'lighter';
  const lod = clamp((LAM * s - 6) / 16);
  // a soft glow: the field itself
  const g = ctx.createRadialGradient(rx, ry, 0, rx, ry, 6.5 * s);
  g.addColorStop(0, 'rgba(255,150,80,.55)'); g.addColorStop(.12, 'rgba(255,106,26,.26)'); g.addColorStop(.5, 'rgba(255,106,26,.07)'); g.addColorStop(1, 'rgba(255,106,26,0)');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  // spherical shells: a sphere in isometric projection is a circle; one every wavelength
  const off = (t * VEL) % LAM;
  for (let r = off + .05; r < 7; r += LAM) {
    const a = .9 / (1 + r / .9) * (.25 + .75 * lod);
    ctx.strokeStyle = `rgba(255,${130 + 80 * Math.exp(-r)},${60 + 60 * Math.exp(-r)},${a})`; ctx.lineWidth = 1.6;
    ctx.beginPath(); ctx.arc(rx, ry, r * s, 0, TAU); ctx.stroke();
  }
  // where the shells meet the floor: ellipses around the point under the router
  const [fx, fy] = iso(ROUTER[0], ROUTER[1], 0);
  ctx.save(); poly([iso(0, 0, 0), iso(ROOM.X, 0, 0), iso(ROOM.X, ROOM.Y, 0), iso(0, ROOM.Y, 0)]); ctx.clip();
  for (let r = off + ROUTER[2]; r < 8; r += LAM) {
    const rr = Math.sqrt(r * r - ROUTER[2] * ROUTER[2]); if (rr <= 0) continue;
    const a = 1.4 / (1 + r / 1.1) * (.2 + .8 * lod);
    ctx.strokeStyle = `rgba(255,150,80,${a})`; ctx.lineWidth = 2.2;
    ctx.beginPath(); ctx.ellipse(fx, fy, 1.2247 * rr * K, .7071 * rr * K, 0, 0, TAU); ctx.stroke();
  }
  ctx.restore();
  ctx.restore();
  // you absorb it: a dark wedge on the floor behind you, away from the router
  const P0 = [PERSON.x, PERSON.y], d = [P0[0] - ROUTER[0], P0[1] - ROUTER[1]], L = Math.hypot(...d), u = [d[0] / L, d[1] / L], n = [-u[1], u[0]];
  const w0 = .28, w1 = 1.1, l = 3;
  const sh = [[P0[0] + n[0] * w0, P0[1] + n[1] * w0], [P0[0] - n[0] * w0, P0[1] - n[1] * w0], [P0[0] + u[0] * l - n[0] * w1, P0[1] + u[1] * l - n[1] * w1], [P0[0] + u[0] * l + n[0] * w1, P0[1] + u[1] * l + n[1] * w1]];
  ctx.save(); poly([iso(0, 0, 0), iso(ROOM.X, 0, 0), iso(ROOM.X, ROOM.Y, 0), iso(0, ROOM.Y, 0)]); ctx.clip();
  const gp = sh.map(p => iso(p[0], p[1], 0));
  ctx.fillStyle = 'rgba(8,16,36,.72)'; poly(gp, 'rgba(8,16,36,.72)');
  ctx.restore();
}
function drawBoxWifi(b, wallK) {
  const f = faces(b), mat = b[7];
  if (mat === 'metal') {        // metal: a mirror, the brightest thing after the router
    poly(f.py, 'rgba(220,235,250,.55)'); poly(f.px, 'rgba(220,235,250,.35)'); poly(f.top, 'rgba(255,240,225,.75)');
    for (const q of [f.py, f.px, f.top]) poly(q, null, '#FFFFFF', 2);
    return;
  }
  if (b[8] === 'router') {
    ctx.save(); ctx.shadowColor = ACC; ctx.shadowBlur = 30; for (const q of [f.py, f.px, f.top]) poly(q, HOT); ctx.restore();
    return;
  }
  if (mat === 'wall') {         // walls: hidden-line dashes once they turn transparent
    const a = lerp(.6, .45, wallK), dash = wallK > .5 ? [10, 8] : [];
    for (const q of [f.py, f.px, f.top]) poly(q, `rgba(220,235,250,${.05 * (1 - wallK)})`, `rgba(220,235,250,${a})`, 1.4, dash);
    if (b[8] === 'cut') hatchFace(f.top, `rgba(220,235,250,${.3 * (1 - wallK)})`, 7, 1);
    return;
  }
  for (const q of [f.py, f.px, f.top]) poly(q, null, 'rgba(220,235,250,.42)', 1.2);   // wood, fabric: almost clear
}
function wifiView(t) {
  sheetBG();
  const wallK = smooth(ev(t, T.wall, .6));
  slab('wifi');
  wifiField(t, wallK);
  for (const i of ORDER) {
    const b = BOX[i];
    drawBoxWifi(b, wallK);
    if (i === 1) { const q = [iso(2.7, 0, .95), iso(3.8, 0, .95), iso(3.8, 0, 2.15), iso(2.7, 0, 2.15)]; poly(q, null, `rgba(220,235,250,${.4 * (1 - wallK) + .2})`, 1.2, wallK > .5 ? [10, 8] : []); }
    if (b[7] === 'fabric' && b[0] === 0.35 && b[4] === 0 && b[5] === .42) drawPerson('wifi');
  }
}

// ------------------------------------------------------------------ hologram furniture: a scan front, target brackets, rolling numbers
const GLY = '0123456789#%&@$<>/\\=+*';
function roll(str, t, t0, dur = .45) {          // characters settle left to right from garbage glyphs
  if (t < t0) return '';
  const p = (t - t0) / dur;
  return [...str].map((ch, i) => {
    const settle = (i + 1) / str.length;
    if (p >= settle || ch === ' ' || /[\u3000-\u9fff·]/.test(ch)) return ch;
    const r = mulberry32(i * 97 + Math.floor(t * 30))(); return GLY[Math.floor(r * GLY.length)];
  }).join('');
}
function bracket(cx, cy, w, h, t, t0, label, o = {}) {
  if (t < t0) return;
  const k = expoOut(ev(t, t0, .35)), s = lerp(2.2, 1, k), ww = w * s / 2, hh = h * s / 2, L = 26;
  const col = o.col ?? LINE;
  ctx.strokeStyle = col; ctx.lineWidth = 3; ctx.globalAlpha = lerp(.3, 1, k);
  ctx.beginPath();
  for (const [sx, sy] of [[-1, -1], [1, -1], [1, 1], [-1, 1]]) { const x = cx + sx * ww, y = cy + sy * hh; ctx.moveTo(x, y + -sy * L); ctx.lineTo(x, y); ctx.lineTo(x + -sx * L, y); }
  ctx.stroke(); ctx.globalAlpha = 1;
  if (k < .6) return;
  // a leader out to a dark plate
  const lx = cx + (o.dx ?? ww + 40), ly = cy + (o.dy ?? -hh - 60);
  ctx.strokeStyle = col; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(cx + Math.sign(o.dx ?? 1) * ww, cy - hh); ctx.lineTo(lx, ly); ctx.stroke();
  ctx.font = `700 44px ${UI}`; const txt = roll(label, t, t0 + .2, .5), tw = ctx.measureText(label).width;
  const px = clamp((o.dx ?? 1) < 0 ? lx - tw - 36 : lx, 24, W - 24 - tw - 36), py = ly - 34;
  ctx.fillStyle = 'rgba(6,12,28,.82)'; ctx.fillRect(px, py, tw + 36, 68);
  ctx.strokeStyle = 'rgba(220,235,250,.6)'; ctx.lineWidth = 1; ctx.strokeRect(px + .5, py + .5, tw + 35, 67);
  ctx.fillStyle = o.accent ? ACC : '#F4F8FC'; ctx.textBaseline = 'middle'; ctx.textAlign = 'left'; ctx.fillText(txt, px + 18, py + 35);
}

// ------------------------------------------------------------------ part 2: Wi-Fi is light too — measure it, then look at visible light
function ruler(t) {        // a blueprint scale at the top: wavelength, log scale, Wi-Fi far right and visible light far left
  if (t < T.light) return;
  const k = expoOut(ev(t, T.light, .7)), x0 = 90, x1 = 990, y = 300;
  const X = lam => lerp(x0, x1, (Math.log10(lam) + 7) / 7);         // 1e-7 m … 1 m
  ctx.fillStyle = 'rgba(6,12,28,.78)'; ctx.fillRect(60, 170, 960, 290 * k);
  if (k < .3) return;
  ctx.strokeStyle = LINE; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(x0, y); ctx.lineTo(lerp(x0, x1, k), y); ctx.stroke();
  ctx.font = `400 26px ${UI}`; ctx.fillStyle = 'rgba(220,235,250,.75)'; ctx.textAlign = 'center'; ctx.textBaseline = 'top';
  [[1e-6, '1 µm'], [1e-4, '0.1 mm'], [1e-2, '1 cm'], [1, '1 m']].forEach(([l, s]) => { const x = X(l); if (x > lerp(x0, x1, k)) return; ctx.beginPath(); ctx.moveTo(x, y - 10); ctx.lineTo(x, y + 10); ctx.stroke(); ctx.fillText(s, x, y + 18); });
  // visible light: a thin rainbow
  const v0 = X(380e-9), v1 = X(750e-9), gr = ctx.createLinearGradient(v0, 0, v1, 0);
  ['#8B5CF6', '#3B82F6', '#22C55E', '#EAB308', '#F97316', '#EF4444'].forEach((c, i) => gr.addColorStop(i / 5, c));
  ctx.fillStyle = gr; ctx.fillRect(v0, y - 16, v1 - v0, 32);
  ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic'; ctx.font = `700 34px ${UI}`; ctx.fillStyle = '#F4F8FC'; ctx.fillText('可见光', v0 - 6, y - 34);
  const wx = X(.125);
  ctx.fillStyle = ACC; ctx.beginPath(); ctx.arc(wx, y, 11, 0, TAU); ctx.fill();
  ctx.textAlign = 'right'; ctx.fillStyle = ACC; ctx.fillText('Wi-Fi', wx + 30, y - 34);
  ctx.textAlign = 'left'; ctx.font = `400 28px ${UI}`; ctx.fillStyle = 'rgba(220,235,250,.75)'; ctx.fillText('电磁波 · 波长', 90, 210);
  if (t >= T.ratio) {      // the gap between them, measured
    const q = expoOut(ev(t, T.ratio, .5));
    ctx.strokeStyle = ACC; ctx.lineWidth = 2.5; ctx.beginPath(); ctx.moveTo(v1 + 8, y + 52); ctx.lineTo(lerp(v1 + 8, wx, q), y + 52); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(v1 + 8, y + 42); ctx.lineTo(v1 + 8, y + 62); ctx.moveTo(lerp(v1 + 8, wx, q), y + 42); ctx.lineTo(lerp(v1 + 8, wx, q), y + 62); ctx.stroke();
    ctx.font = `200 64px ${FIG}`; ctx.fillStyle = ACC; ctx.textAlign = 'center'; ctx.textBaseline = 'top';
    ctx.fillText(roll('× 250 000', t, T.ratio, .6), (v1 + wx) / 2, y + 70);
  }
}
function dimension(t) {    // λ measured between two shells, on a horizontal ray out of the router
  if (t < T.lam) return;
  const [rx, ry] = iso(...ROUTER), s = 1.2247 * K, off = (t * VEL) % LAM;
  const n = 4, r0 = off + .05 + LAM * n, a = rx + r0 * s, b = a + LAM * s, y = ry + 2;
  const k = expoOut(ev(t, T.lam, .45));
  ctx.strokeStyle = LINE; ctx.lineWidth = 2;
  ctx.beginPath(); ctx.moveTo(a, y + 6); ctx.lineTo(a, y + 170); ctx.moveTo(b, y + 6); ctx.lineTo(b, y + 170); ctx.stroke();       // extension lines, below
  const ym = y + 140, m = (a + b) / 2, hw = (b - a) / 2 * k;
  ctx.beginPath(); ctx.moveTo(m - hw, ym); ctx.lineTo(m + hw, ym); ctx.stroke();
  for (const [x, d] of [[m - hw, 1], [m + hw, -1]]) { ctx.fillStyle = LINE; ctx.beginPath(); ctx.moveTo(x, ym); ctx.lineTo(x + d * 16, ym - 6); ctx.lineTo(x + d * 16, ym + 6); ctx.closePath(); ctx.fill(); }
  ctx.strokeStyle = LINE; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.moveTo(m, ym + 8); ctx.lineTo(m + 40, ym + 60); ctx.stroke();
  ctx.fillStyle = 'rgba(6,12,28,.82)'; ctx.fillRect(m + 40, ym + 40, 440, 104);
  ctx.font = `200 84px ${FIG}`; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.fillStyle = ACC;
  ctx.fillText(roll('λ = 12.5 cm', t, T.lam + .1, .6), m + 58, ym + 94);
}
function lens(t) {         // a hologram loupe on one shell: inside, visible light — too fine to see at this scale
  if (t < T.lens) return;
  const k = expoOut(ev(t, T.lens, .45)), cx = 760, cy = 1180, R = 190 * k;
  ctx.save(); ctx.beginPath(); ctx.arc(cx, cy, R, 0, TAU); ctx.clip();
  ctx.fillStyle = 'rgba(6,12,28,.92)'; ctx.fillRect(cx - R, cy - R, 2 * R, 2 * R);
  ctx.strokeStyle = '#F4F8FC'; ctx.lineWidth = 2; ctx.beginPath();
  for (let x = cx - R; x <= cx + R; x += 1) { const y = cy + 26 * Math.sin((x - cx) / 5.5 - t * 6); x === cx - R ? ctx.moveTo(x, y) : ctx.lineTo(x, y); }
  ctx.stroke();
  ctx.font = `700 30px ${UI}`; ctx.fillStyle = '#F4F8FC'; ctx.textAlign = 'center'; ctx.fillText('可见光', cx, cy - 70); ctx.font = `400 26px ${UI}`; ctx.fillText(roll('λ ≈ 0.0005 mm', t, T.lens + .2, .5), cx, cy + 92);
  ctx.restore();
  ctx.strokeStyle = LINE; ctx.lineWidth = 3; ctx.beginPath(); ctx.arc(cx, cy, R, 0, TAU); ctx.stroke();
  ctx.lineWidth = 1.2; ctx.setLineDash([6, 8]); ctx.beginPath(); ctx.arc(cx, cy, R + 16, t * .6, t * .6 + 5); ctx.stroke(); ctx.setLineDash([]);
  for (let i = 0; i < 4; i++) { const a = i * Math.PI / 2 + Math.PI / 4; ctx.beginPath(); ctx.moveTo(cx + Math.cos(a) * (R + 6), cy + Math.sin(a) * (R + 6)); ctx.lineTo(cx + Math.cos(a) * (R + 30), cy + Math.sin(a) * (R + 30)); ctx.stroke(); }
}

// ------------------------------------------------------------------ the scan: a vertical plane sweeping along x; behind it, Wi-Fi vision
const OFFH = document.createElement('canvas'); OFFH.width = W; OFFH.height = H;
function scanX(t) { return lerp(-2.2, 9.5, ease(ev(t, T.scan, .95))); }
function scanPlane(s, t) {
  const q = [iso(s, -.3, 0), iso(s, ROOM.Y + .3, 0), iso(s, ROOM.Y + .3, 3.1), iso(s, -.3, 3.1)];
  ctx.save(); ctx.globalCompositeOperation = 'lighter';
  poly(q, 'rgba(255,140,70,.10)');
  ctx.strokeStyle = HOT; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(...q[0]); ctx.lineTo(...q[1]); ctx.stroke();
  ctx.strokeStyle = 'rgba(255,217,184,.5)'; ctx.lineWidth = 1.5; ctx.beginPath();
  for (let z = .25; z < 3.1; z += .25) { ctx.moveTo(...iso(s, -.3, z)); ctx.lineTo(...iso(s, ROOM.Y + .3, z)); }
  ctx.stroke(); ctx.restore();
}

// ------------------------------------------------------------------ subtitles
function subtitles(t) {
  const c = SUBS.find(c => t >= c[0] && t < c[1]); if (!c) return;
  ctx.font = `700 56px ${UI}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.lineJoin = 'round';
  ctx.lineWidth = 12; ctx.strokeStyle = '#0B1328'; ctx.strokeText(c[2], W / 2, 1600);
  ctx.fillStyle = '#F7F4EE'; ctx.fillText(c[2], W / 2, 1600);
}

// ------------------------------------------------------------------ seek
window.seek = function (t) {
  t = clamp(t, 0, DUR - 1 / FPS);
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over';
  [CU, CV, K] = camAt(t); OY = -60;
  const s = scanX(t);
  if (t < T.scan) humanView(t);
  else if (s < ROOM.X + 2.4) {
    wifiView(t);
    const g = OFFH.getContext('2d'); g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = 1; g.globalCompositeOperation = 'source-over';
    withCtx(g, () => humanView(t));
    ctx.save(); ctx.beginPath(); ctx.rect(0, 0, W, H); scanClipInv(s); ctx.clip('evenodd'); ctx.drawImage(OFFH, 0, 0); ctx.restore();
    scanPlane(s, t);
  } else wifiView(t);
  if (t >= T.scan + 1.0 && t < T.light + .2) {
    const [rx, ry] = iso(...ROUTER);
    if (t < T.you + .2) bracket(rx, ry - 10, 70, 60, t, T.router, '路由器 · 2.4 GHz', { dx: 60, dy: -120 });
    const [wx, wy] = iso(4.19, 1.0, .6);
    if (t < T.you + .2) bracket(wx, wy, 70, 150, t, T.wall, '墙 · 透明', { dx: 80, dy: -170 });
    const { bx, by, k } = personPts();
    bracket(bx + 10 * k, by - 60 * k, 120 * k, 200 * k, t, T.you, '你 · 黑的', { dx: 120 * k, dy: -170 * k, accent: true });
  }
  ruler(t); dimension(t); lens(t);
  subtitles(t);
  return true;
};
function scanClipInv(s) { const a = iso(s, -20, 0), b = iso(s, 30, 0); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.lineTo(b[0] - 4000, b[1] - 2300); ctx.lineTo(a[0] - 4000, a[1] - 2300); ctx.closePath(); }
window.DURATION = DUR; window.FPS = FPS;
window.ready = document.fonts.load(`200 84px ${FIG}`).then(() => document.fonts.load(`700 56px ${UI}`));
