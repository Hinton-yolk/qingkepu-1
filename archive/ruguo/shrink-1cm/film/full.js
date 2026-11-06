// 如果……会怎样 03 · 如果你突然缩小到一厘米. One core rule: the smaller you are, the more the surface wins.
// One continuous shot: the desk on a rainy night → 啪, you shrink and the camera dives with you → the rice grain → the paper clip →
// off the edge, a slow fall → the floor: a drop wraps you, rain, the draught, hunger → the same cause → an ant → the camera rises back
// to the first frame, you grow back, the ant walks round a drop. Pure function of time; seeded noise only.
'use strict';
const W = 1080, H = 1920, FPS = 30;
const C = CUES.c, DUR = TL.duration;
const cv = document.getElementById('c'); cv.width = W; cv.height = H;
let ctx = cv.getContext('2d');
const UI = '"Noto Sans Mono CJK SC"', DSP = '"Noto Sans CJK SC"';
const ACC = '#FF7A2E', WHITE = '#F4F6FA', INK = '#0E1426', LINE = '#DCEBFA', COLD = '#5AA2FF';
const C30 = Math.cos(Math.PI / 6), TAU = Math.PI * 2;
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, k) => a + (b - a) * k;
const ev = (t, t0, d) => clamp((t - t0) / d);
const smooth = x => { x = clamp(x); return x * x * (3 - 2 * x); };
const ease = x => { x = clamp(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
const expoOut = x => { x = clamp(x); return x === 1 ? 1 : 1 - Math.pow(2, -10 * x); };
function mulberry32(a) { return () => { a |= 0; a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
const hash = (i, s = 1) => mulberry32(i * 7919 + s * 104729)();

// ------------------------------------------------------------------ camera: one shot for the whole film (world metres; x down-right, y down-left, z up)
let CU = 0, CV = 0, K = 330, OY = 0;
const iso = (x, y, z) => [W / 2 + ((x - y) * C30 - CU) * K, H / 2 + OY + ((x + y) * .5 - z - CV) * K];
const setCam = (x, y, z, k) => { CU = (x - y) * C30; CV = (x + y) * .5 - z; K = k; };
const P0 = [0.86, 0.64, 0.75], CLIP = [0.93, 0.60, 0.75], J = [0.99, 0.695, 0.75], F0 = [1.01, 0.80, 0];
const CHAIR = [0.62, 1.08];
const ROOM = [0.85, 0.62, 0.72];
const ROOM0 = [0, ...ROOM, 280], ROOM1 = [C.pak, 0.9, 0.78, 0.82, 520];
const KZ = [      // [t, K] while the camera rides with you
  [C.pak + 1.7, 28000], [C.half + .5, 26000], [C.clip - .3, 15500], [C.lift + .6, 17000], [C.jump + .6, 20000], [C.land, 24000],
  [C.rule, 27000], [C.drop + .3, 30000], [C.rain + .3, 21000], [C.wind + .5, 30000], [C.food + .8, 30000], [C.hero + .5, 17000],
  [C.ant + .3, 24000], [C.back + .2, 24000],
];
function kAt(t) {      // Catmull-Rom through log K: the zoom never comes to a dead stop between keys
  let i = 0; while (i < KZ.length - 2 && t > KZ[i + 1][0]) i++;
  const g = j => Math.log(KZ[clamp(j, 0, KZ.length - 1)][1]), p = ev(t, KZ[i][0], KZ[i + 1][0] - KZ[i][0]);
  const p0 = g(i - 1), p1 = g(i), p2 = g(i + 1), p3 = g(i + 2), p2_ = p * p, p3_ = p2_ * p;
  return Math.exp(.5 * (2 * p1 + (-p0 + p2) * p + (2 * p0 - 5 * p1 + 4 * p2 - p3) * p2_ + (-p0 + 3 * p1 - 3 * p2 + p3) * p3_));
}
function camAt(t, Y) {
  const drift = (k) => [.0016 * Math.sin(t * .43) * 22000 / k, .0013 * Math.cos(t * .37) * 22000 / k];
  if (t < C.pak) { const p = ev(t, 0, C.pak), k = Math.exp(lerp(Math.log(ROOM0[4]), Math.log(ROOM1[4]), p)), o = .05 * Math.sin(t * .5); setCam(lerp(ROOM0[1], ROOM1[1], p) + o, lerp(ROOM0[2], ROOM1[2], p) - o, lerp(ROOM0[3], ROOM1[3], p), k); OY = 0; return; }      // a steady push from frame 0
  const yt = [Y.x, Y.y, Y.z + Y.h * .5];
  if (t < C.pak + 1.7) {      // dive with you
    const e = ease(ev(t, C.pak, 1.7)), k = Math.exp(lerp(Math.log(ROOM1[4]), Math.log(28000), e));
    setCam(lerp(ROOM1[1], yt[0], e), lerp(ROOM1[2], yt[1], e), lerp(ROOM1[3], yt[2], e), k); OY = lerp(0, 140, e); return;
  }
  if (t < C.back + .2) { const k = kAt(t), [dx, dy] = drift(k); setCam(yt[0] + dx, yt[1] + dy, yt[2], k); OY = 140; return; }
  const e = ease(ev(t, C.back + .2, 2.4)), q = ev(t, C.back + 2.6, C.black - C.back - 2.6), [ax, ay, az] = deskAnt(t);      // rise back to the first frame, then lean in to the ant
  const k = Math.exp(lerp(Math.log(24000), Math.log(280), e)) * (1 + .45 * q), [dx, dy] = drift(k);
  setCam(lerp(yt[0], lerp(ROOM[0], ax, .35 * q), e) + dx, lerp(yt[1], lerp(ROOM[1], ay, .35 * q), e) + dy, lerp(yt[2], lerp(ROOM[2], az, .35 * q), e), k); OY = lerp(140, 0, e);
}
const inv = (sx, sy, z) => { const u = (sx - W / 2) / K + CU, v = (sy - H / 2 - OY) / K + CV + z; const d = u / C30, s = 2 * v; return [(d + s) / 2, (s - d) / 2]; };

// ------------------------------------------------------------------ drawing helpers
function poly(pts, fill, stroke, lw) { ctx.beginPath(); pts.forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)); ctx.closePath(); if (fill) { ctx.fillStyle = fill; ctx.fill(); } if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = lw ?? 1; ctx.stroke(); } }
const shade = (hex, k) => { const n = parseInt(hex.slice(1), 16); const r = n >> 16, g = n >> 8 & 255, b = n & 255; const to = k > 0 ? [255, 236, 210] : [8, 12, 28], a = Math.abs(k); return `rgb(${lerp(r, to[0], a) | 0},${lerp(g, to[1], a) | 0},${lerp(b, to[2], a) | 0})`; };
function box(x0, x1, y0, y1, z0, z1, col, o = {}) {
  const top = [iso(x0, y0, z1), iso(x1, y0, z1), iso(x1, y1, z1), iso(x0, y1, z1)];
  const px = [iso(x1, y0, z0), iso(x1, y1, z0), iso(x1, y1, z1), iso(x1, y0, z1)];
  const py = [iso(x0, y1, z0), iso(x1, y1, z0), iso(x1, y1, z1), iso(x0, y1, z1)];
  poly(py, shade(col, o.ly ?? .05)); poly(px, shade(col, o.lx ?? -.3)); poly(top, shade(col, o.lt ?? .12));
  return { top, px, py };
}
// parallel lines on a horizontal rectangle, at the spacing that reads at this zoom (levels fade in and out, no popping)
function grain(x0, x1, y0, y1, z, col, seed, dir = 'x') {
  const c = [inv(0, 0, z), inv(W, 0, z), inv(0, H, z), inv(W, H, z)];
  const vx0 = Math.max(x0, Math.min(...c.map(p => p[0]))), vx1 = Math.min(x1, Math.max(...c.map(p => p[0])));
  const vy0 = Math.max(y0, Math.min(...c.map(p => p[1]))), vy1 = Math.min(y1, Math.max(...c.map(p => p[1])));
  if (vx0 >= vx1 || vy0 >= vy1) return;
  for (const sp of [.04, .004, .0004]) {
    const px = sp * K, a = clamp((px - 10) / 30) * (1 - clamp((px - 240) / 400));
    if (a <= 0) continue;
    ctx.strokeStyle = col; ctx.globalAlpha = a; ctx.lineWidth = Math.max(1, Math.min(3, px * .03)); ctx.beginPath();
    const [lo, hi] = dir === 'x' ? [vy0, vy1] : [vx0, vx1];
    for (let i = Math.floor(lo / sp); i <= Math.ceil(hi / sp); i++) {
      const w = (hash(i, seed + sp * 1e4) - .5) * sp * .6, q = i * sp + w;
      if (dir === 'x') { const a0 = iso(vx0, q, z), a1 = iso(vx1, q, z); ctx.moveTo(...a0); ctx.lineTo(...a1); }
      else { const a0 = iso(q, vy0, z), a1 = iso(q, vy1, z); ctx.moveTo(...a0); ctx.lineTo(...a1); }
    }
    ctx.stroke(); ctx.globalAlpha = 1;
  }
}
function isoEllipse(cx, cy, z, rx, ry, rot = 0, n = 40) { const pts = []; for (let i = 0; i < n; i++) { const a = i / n * TAU, x = Math.cos(a) * rx, y = Math.sin(a) * ry; pts.push(iso(cx + x * Math.cos(rot) - y * Math.sin(rot), cy + x * Math.sin(rot) + y * Math.cos(rot), z)); } return pts; }
// type
const GLY = '0123456789';
function roll(str, t, t0, dur = .4) { if (t < t0) return ''; const p = (t - t0) / dur; return [...str].map((ch, i) => (p >= (i + 1) / str.length || !/[0-9]/.test(ch)) ? ch : GLY[Math.floor(mulberry32(i * 97 + Math.floor(t * 30))() * 10)]).join(''); }
function plateText(txt, x, y, o = {}) {
  ctx.font = `700 ${o.size ?? 40}px ${UI}`; const tw = ctx.measureText(txt).width, hh = (o.size ?? 40) * 1.6;
  const px = clamp(o.right ? x - tw - 36 : x, 24, W - 24 - tw - 36), py = y - hh / 2;
  ctx.fillStyle = 'rgba(8,12,28,.82)'; ctx.fillRect(px, py, tw + 36, hh); ctx.strokeStyle = 'rgba(220,235,250,.55)'; ctx.lineWidth = 1; ctx.strokeRect(px + .5, py + .5, tw + 35, hh - 1);
  ctx.fillStyle = o.accent ? ACC : WHITE; ctx.textBaseline = 'middle'; ctx.textAlign = 'left'; ctx.fillText(txt, px + 18, py + hh / 2 + 2);
}
function hero(t, t0, lines, x, y, o = {}) {      // the number the line is about, big; lands with a short drop and types in (no fade)
  if (t < t0 || (o.t1 && t >= o.t1)) return;
  ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic';
  lines.forEach((ln, i) => {
    const k = expoOut(ev(t, t0 + i * .15, .32)); if (k <= 0) return;
    const sz = ln.size ?? 140, yy = y + (o.lh ? i * o.lh : 0) - (1 - k) * 40;
    const nChars = ln.parts.reduce((a, p) => a + [...p[0]].length, 0), show = Math.ceil(nChars * clamp((t - t0 - i * .15) / .35));
    let cx = x, used = 0;
    for (const [s, col] of ln.parts) {
      ctx.font = `${ln.ui ? 700 : 900} ${sz}px ${ln.ui ? UI : DSP}`;
      const vis = [...s].slice(0, Math.max(0, show - used)).join(''); used += [...s].length;
      ctx.lineJoin = 'round'; ctx.lineWidth = sz * .16; ctx.strokeStyle = 'rgba(8,12,28,.85)'; ctx.strokeText(vis, cx, yy);
      ctx.fillStyle = col; ctx.fillText(vis, cx, yy); cx += ctx.measureText(s).width;
    }
  });
}
function bracket(cx, cy, w, h, label, o = {}) {
  const ww = w / 2, hh = h / 2, L = Math.min(22, w / 3);
  ctx.strokeStyle = o.accent ? ACC : LINE; ctx.lineWidth = 3; ctx.beginPath();
  for (const [sx, sy] of [[-1, -1], [1, -1], [1, 1], [-1, 1]]) { const x = cx + sx * ww, y = cy + sy * hh; ctx.moveTo(x, y - sy * L); ctx.lineTo(x, y); ctx.lineTo(x - sx * L, y); }
  ctx.stroke();
  if (!label) return;
  const dx = o.dx ?? ww + 40, dy = o.dy ?? -hh - 60, lx = cx + dx, ly = cy + dy;
  ctx.strokeStyle = LINE; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(cx + Math.sign(dx) * ww, cy - hh); ctx.lineTo(lx, ly); ctx.stroke();
  plateText(label, lx, ly, { right: dx < 0, accent: o.accent, size: o.size ?? 38 });
}
function subtitle(txt) {
  ctx.font = `700 54px ${UI}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.lineJoin = 'round';
  ctx.lineWidth = 12; ctx.strokeStyle = '#080C1C'; ctx.strokeText(txt, W / 2, 1600); ctx.fillStyle = '#F7F4EE'; ctx.fillText(txt, W / 2, 1600);
}

// ------------------------------------------------------------------ the person (series character), poses in figure units (170 = height)
function figure(sx, sy, px170, pose, o = {}) {
  const k = px170 / 170; if (k * 170 < 2) return;
  const t = o.t ?? 0, col = o.col ?? '#2E7A78', skin = o.skin ?? '#E5C2A6', pants = '#2C3240';
  ctx.save(); ctx.translate(sx, sy); ctx.scale(k * (o.flip ? -1 : 1), k); ctx.rotate(o.rot ?? 0);
  ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  const br = pose === 'stand' ? Math.sin(t * 2.4) * 2.5 : 0;
  let J = { hip: [0, -86], neck: [0, -140 + br], head: [Math.sin(t * .9) * 3, -156 + br], lh: [-26, -92], rh: [26, -92], lf: [-12, 0], rf: [12, 0], le: [-24, -116], re: [24, -116], lk: [-10, -44], rk: [10, -44] };
  if (pose === 'walk') { const s = Math.sin(o.ph ?? 0); J.lf = [-18 * s, 0]; J.rf = [18 * s, 0]; J.lk = [-12 * s, -44]; J.rk = [12 * s, -44]; J.lh = [20 * s, -92]; J.rh = [-20 * s, -92]; }
  if (pose === 'lift') { const b = Math.sin(t * 5) * 8; J.le = [-26, -170 - b]; J.re = [26, -170 - b]; J.lh = [-22, -206 - b]; J.rh = [22, -206 - b]; }
  if (pose === 'fall') { const w = Math.sin(t * 7) * 6; J.le = [-48, -150]; J.re = [48, -150]; J.lh = [-70, -176 + w]; J.rh = [70, -176 - w]; J.lk = [-22, -46]; J.rk = [20, -52]; J.lf = [-30, -8]; J.rf = [26, -14]; }
  if (pose === 'cold') { const sh = Math.sin(t * 40) * 2.5; ctx.translate(sh, 0); J.le = [-14, -110]; J.re = [14, -110]; J.lh = [16, -124]; J.rh = [-16, -124]; J.lk = [-6, -44]; J.rk = [6, -44]; J.lf = [-6, 0]; J.rf = [6, 0]; }
  if (pose === 'hug') { J.le = [-30, -112]; J.re = [30, -112]; J.lh = [4, -104]; J.rh = [40, -96]; }
  if (pose === 'sit') { J.hip = [0, -40]; J.neck = [-4, -96]; J.head = [-6, -112]; J.lk = [44, -40]; J.rk = [46, -36]; J.lf = [44, 0]; J.rf = [48, 2]; J.le = [20, -70]; J.re = [24, -66]; J.lh = [48, -80]; J.rh = [52, -76]; }
  const limb = (a, b, c, w, cl) => { ctx.strokeStyle = cl; ctx.lineWidth = w; ctx.beginPath(); ctx.moveTo(...a); ctx.lineTo(...b); ctx.lineTo(...c); ctx.stroke(); };
  limb(J.hip, J.lk, J.lf, 20, pants); limb(J.hip, J.rk, J.rf, 20, pants);
  ctx.strokeStyle = col; ctx.lineWidth = 40; ctx.beginPath(); ctx.moveTo(...J.hip); ctx.lineTo(...J.neck); ctx.stroke();
  limb(J.neck, J.le, J.lh, 13, col); limb(J.neck, J.re, J.rh, 13, col);
  ctx.fillStyle = skin; ctx.beginPath(); ctx.arc(J.head[0], J.head[1], 19, 0, TAU); ctx.fill();
  ctx.fillStyle = '#2A2522'; ctx.beginPath(); ctx.arc(J.head[0], J.head[1] - 4, 20, Math.PI * 1.02, Math.PI * 2.02); ctx.fill();
  if (o.glow) {      // the surface: the whole skin outline lights up
    ctx.globalAlpha = o.glow; ctx.strokeStyle = ACC; ctx.lineWidth = 5 / Math.max(k, .05) * .25;
    ctx.beginPath(); ctx.arc(J.head[0], J.head[1], 23, 0, TAU); ctx.stroke();
    ctx.lineWidth = 3.2; for (const [a, b, c] of [[J.hip, J.lk, J.lf], [J.hip, J.rk, J.rf], [J.neck, J.le, J.lh], [J.neck, J.re, J.rh]]) { ctx.beginPath(); ctx.moveTo(...a); ctx.lineTo(...b); ctx.lineTo(...c); ctx.stroke(); }
    ctx.lineWidth = 3.2; ctx.strokeRect(-22, J.neck[1], 44, J.hip[1] - J.neck[1]); ctx.globalAlpha = 1;
  }
  ctx.restore();
  return J;
}

// ------------------------------------------------------------------ the room
const RAINW = (() => { const r = mulberry32(5), a = []; for (let i = 0; i < 90; i++) a.push([r(), r(), .4 + r() * .6]); return a; })();
const CITY = (() => { const r = mulberry32(9), a = []; for (let i = 0; i < 26; i++) a.push([r(), .55 + r() * .4, 2 + r() * 5, r() < .6 ? '255,196,120' : '170,200,255']); return a; })();
const RICE = [[0.868, 0.646, 0.4], [0.874, 0.638, 1.6], [0.853, 0.652, 2.4], [1.0165, 0.7975, 0.5]];      // [x, y, rot]; the last one is on the floor
function rice(x, y, z, rot, a = 1, bite = 0) {
  const pts = isoEllipse(x, y, z + .0012, .0031 * (1 - bite * .7), .00125 * (1 - bite * .3), rot);
  ctx.globalAlpha = a; poly(pts, '#F2EBDD'); poly(isoEllipse(x, y, z + .0016, .0026 * (1 - bite * .7), .0008, rot), '#FFFDF6'); ctx.globalAlpha = 1;
}
function clipShape(x, y, z, a = 1) {      // a paper clip lying on the desk: 32 × 8 mm wire loops
  const P = [[0, 0], [.03, 0], [.032, .004], [.03, .008], [.002, .008], [0, .006], [.002, .0015], [.026, .0015], [.028, .004], [.026, .0062], [.006, .0062]];
  ctx.globalAlpha = a; ctx.strokeStyle = '#C9D2DC'; ctx.lineWidth = Math.max(1.2, .0009 * K); ctx.lineJoin = 'round'; ctx.beginPath();
  P.forEach(([u, v], i) => { const q = iso(x - .015 + u, y - .004 + v, z + .0005); i ? ctx.lineTo(...q) : ctx.moveTo(...q); }); ctx.stroke(); ctx.globalAlpha = 1;
}
function room(t, o = {}) {
  // night room
  ctx.fillStyle = '#121A30'; ctx.fillRect(0, 0, W, H);
  poly([iso(0, 0, 0), iso(2.4, 0, 0), iso(2.4, 2.2, 0), iso(0, 2.2, 0)], '#4A3A30');                 // floor
  { const fp = iso(1.0, .8, 0), g2 = ctx.createRadialGradient(fp[0], fp[1], 0, fp[0], fp[1], .45 * K); g2.addColorStop(0, 'rgba(255,190,120,.30)'); g2.addColorStop(1, 'rgba(255,190,120,0)'); ctx.fillStyle = g2; ctx.save(); poly([iso(0, 0, 0), iso(2.4, 0, 0), iso(2.4, 2.2, 0), iso(0, 2.2, 0)]); ctx.clip(); ctx.fillRect(fp[0] - .5 * K, fp[1] - .5 * K, K, K); ctx.restore(); }
  grain(0, 2.4, 0, 2.2, 0, 'rgba(20,12,8,.5)', 3, 'y');
  poly([iso(0, 0, 0), iso(0, 2.2, 0), iso(0, 2.2, 2.4), iso(0, 0, 2.4)], '#1C2440');                 // left wall
  poly([iso(0, 0, 0), iso(2.4, 0, 0), iso(2.4, 0, 2.4), iso(0, 0, 2.4)], '#222C4C');                 // back wall
  // window in the back wall: rain, the city
  const wx0 = .38, wx1 = 1.42, wz0 = .98, wz1 = 1.9, win = [iso(wx0, 0, wz0), iso(wx1, 0, wz0), iso(wx1, 0, wz1), iso(wx0, 0, wz1)];
  poly(win, '#0B1226');
  ctx.save(); poly(win); ctx.clip();
  for (const [u, v, s] of CITY) { const p = iso(lerp(wx0, wx1, u), 0, lerp(wz0, wz1, v - .45)); ctx.fillStyle = `rgba(${s},.55)`; ctx.beginPath(); ctx.arc(p[0], p[1], s * K / 300 * 3, 0, TAU); ctx.fill(); }
  ctx.strokeStyle = 'rgba(200,220,250,.7)'; ctx.lineWidth = Math.max(1.5, K / 220); ctx.beginPath();
  for (const [u, v, s] of RAINW) { const z = wz1 - ((v + t * 1.6 * s) % 1) * (wz1 - wz0), x = lerp(wx0, wx1, u); const a = iso(x, 0, z), b = iso(x - .008, 0, z - .09 * s); ctx.moveTo(...a); ctx.lineTo(...b); }
  ctx.stroke(); ctx.restore();
  poly(win, null, '#46506E', Math.max(2, K / 120)); { const a = iso(.9, 0, wz0), b = iso(.9, 0, wz1); ctx.strokeStyle = '#46506E'; ctx.lineWidth = Math.max(2, K / 160); ctx.beginPath(); ctx.moveTo(...a); ctx.lineTo(...b); ctx.stroke(); }
  // window sill
  box(.3, 1.5, -.02, .06, .93, .96, '#5B5D6C');
  // desk
  for (const [x, y] of [[.33, .08], [1.44, .08], [.33, .64], [1.44, .64]]) box(x, x + .04, y, y + .04, 0, .72, '#5A4232');
  const d = box(.3, 1.5, .05, .70, .72, .75, '#7A5A40', { lt: .16 });
  grain(.3, 1.5, .05, .70, .75, 'rgba(60,38,22,.5)', 11, 'x');
  // lamp light pool
  const lp = iso(1.2, .3, .75), g = ctx.createRadialGradient(lp[0], lp[1], 0, lp[0], lp[1], .55 * K);
  g.addColorStop(0, 'rgba(255,200,130,.42)'); g.addColorStop(1, 'rgba(255,200,130,0)'); ctx.fillStyle = g; ctx.save(); poly(d.top); ctx.clip(); ctx.fillRect(lp[0] - .6 * K, lp[1] - .6 * K, 1.2 * K, 1.2 * K); ctx.restore();
  // lamp
  box(1.15, 1.27, .22, .34, .75, .765, '#2B2E36');
  { const a = iso(1.21, .28, .765), b = iso(1.21, .28, 1.12); ctx.strokeStyle = '#2B2E36'; ctx.lineWidth = Math.max(2, .012 * K); ctx.beginPath(); ctx.moveTo(...a); ctx.lineTo(...b); ctx.stroke();
    const sh = [iso(1.12, .22, 1.08), iso(1.3, .22, 1.08), iso(1.26, .26, 1.2), iso(1.16, .26, 1.2)]; poly(sh, '#E9D6B4'); }
  // books
  box(.42, .62, .12, .36, .75, .79, '#3E5A7A'); box(.44, .6, .14, .34, .79, .815, '#9A4A3A');
  // the tea cup + steam
  const cpos = [.62, .5, .75], ctop = isoEllipse(cpos[0], cpos[1], .84, .04, .04), cbot = isoEllipse(cpos[0], cpos[1], .75, .036, .036);
  poly([...cbot.slice(0, 21), ...ctop.slice(0, 21).reverse()], '#E8E2D8'); poly(ctop, '#7A4E2A');
  ctx.strokeStyle = 'rgba(255,250,240,.5)'; ctx.lineWidth = Math.max(1.5, .004 * K); ctx.lineCap = 'round';
  for (let i = 0; i < 3; i++) { ctx.beginPath(); for (let k = 0; k <= 16; k++) { const u = k / 16, p = iso(cpos[0] + Math.sin(u * 5 + t * 2 + i * 2) * .008 * u + (i - 1) * .01, cpos[1], .85 + u * .16); k ? ctx.lineTo(...p) : ctx.moveTo(...p); } ctx.stroke(); }
  // things on the desk
  for (const [x, y, r] of RICE.slice(0, 3)) rice(x, y, .75, r);
  if (!o.clipLifted) clipShape(...CLIP);
  if (o.deskDrop !== false) { const p = isoEllipse(1.0, .66, .7505, .006, .006); poly(p, 'rgba(150,190,230,.55)', 'rgba(220,235,250,.6)', 1); }
  // the chair
  box(CHAIR[0] - .2, CHAIR[0] + .2, CHAIR[1] - .2, CHAIR[1] + .2, .42, .46, '#3C3A44'); box(CHAIR[0] - .2, CHAIR[0] + .2, CHAIR[1] + .17, CHAIR[1] + .2, .46, .95, '#34323C');
  for (const [dx, dy] of [[-.19, -.19], [.17, -.19], [-.19, .17], [.17, .17]]) box(CHAIR[0] + dx, CHAIR[0] + dx + .02, CHAIR[1] + dy, CHAIR[1] + dy + .02, 0, .42, '#2A2830');
  // the floor drop and rice (seen up close later)
  if (!o.hugRice) rice(...RICE[3].slice(0, 2), 0, RICE[3][2], 1, o.bite ?? 0);
}

// ------------------------------------------------------------------ the ant (≈ 6 mm), walking along a heading
function ant(x, y, z, head, t, o = {}) {
  const L = .006, s = K * L / 60; if (s * 60 < 3) { const p = iso(x, y, z); ctx.fillStyle = '#1A1210'; ctx.fillRect(p[0] - 1, p[1] - 1, 2, 2); return; }
  const p = iso(x, y, z + .0012), q = iso(x + Math.cos(head) * .01, y + Math.sin(head) * .01, z + .0012), a = Math.atan2(q[1] - p[1], q[0] - p[0]);
  ctx.save(); ctx.translate(p[0], p[1]); ctx.rotate(a); ctx.scale(s, s * .7);
  const ph = t * 14;
  ctx.strokeStyle = '#1A1210'; ctx.lineWidth = 2.2; ctx.lineCap = 'round';
  for (let i = 0; i < 3; i++) for (const sd of [-1, 1]) { const w = Math.sin(ph + i * 2.1 + (sd > 0 ? Math.PI : 0)) * 6; ctx.beginPath(); ctx.moveTo(-6 + i * 8, 0); ctx.lineTo(-10 + i * 10 + w, sd * 16); ctx.lineTo(-16 + i * 12 + w, sd * 24); ctx.stroke(); }
  ctx.fillStyle = '#1E120E'; ctx.strokeStyle = 'rgba(255,220,190,.45)'; ctx.lineWidth = 1.2;
  for (const [ex, rx, ry] of [[-20, 15, 10], [2, 9, 6], [18, 8, 7]]) { ctx.beginPath(); ctx.ellipse(ex, 0, rx, ry, 0, 0, TAU); ctx.fill(); ctx.stroke(); }
  ctx.strokeStyle = '#1A1210'; ctx.lineWidth = 2.2;
  ctx.beginPath(); ctx.moveTo(24, -3); ctx.quadraticCurveTo(34, -14, 40, -10 + Math.sin(ph) * 2); ctx.moveTo(24, 3); ctx.quadraticCurveTo(34, 14, 40, 10 - Math.sin(ph) * 2); ctx.stroke();
  if (o.beads) { ctx.fillStyle = 'rgba(200,225,255,.8)'; for (const [bx, by, r] of [[-22, -6, 3], [-14, 4, 2.4], [-26, 5, 2]]) { const u = (t * .8 + bx * .01) % 1; ctx.beginPath(); ctx.arc(bx - u * 18, by + Math.sign(by) * u * 10, r, 0, TAU); ctx.fill(); } }
  ctx.restore();
}
const deskAnt = t => { const u = (t * .0096) % 1, x = lerp(.45, 1.45, u), bump = Math.max(0, 1 - Math.abs(x - 1.0) / .02); return [x, .672 + .012 * Math.sin(bump * Math.PI / 2), .75, 0]; };

// ------------------------------------------------------------------ where you are and how big you are
const H0 = 1.7, H1 = .01;
function you(t) {      // → {x, y, z, h, pose, ...}
  const sh = ease(ev(t, C.pak, 1.6)), gr = ease(ev(t, C.back + .2, 2.4));
  const scale = Math.exp(lerp(Math.log(1), Math.log(H1 / H0), sh) + lerp(0, Math.log(H0 / H1), gr));
  const h = H0 * scale;
  if (t < C.pak || gr >= 1) return { x: CHAIR[0], y: CHAIR[1], z: .45, h, pose: 'sit' };
  if (t < C.pak + 1.6) { const u = sh; return { x: lerp(CHAIR[0], P0[0], u), y: lerp(CHAIR[1], P0[1], u), z: lerp(.45, .75, u), h, pose: u < .7 ? 'sit' : 'stand' }; }
  if (t < C.strong + .5) return { x: P0[0], y: P0[1], z: .75, h, pose: 'stand' };
  if (t < C.lift) { const u = ease(ev(t, C.strong + .5, C.lift - C.strong - .7)); return { x: lerp(P0[0], CLIP[0] - .002, u), y: lerp(P0[1], CLIP[1] + .012, u), z: .75, h, pose: u < 1 ? 'walk' : 'stand', ph: t * 9 }; }
  if (t < C.jump) return { x: CLIP[0] - .002, y: CLIP[1] + .012, z: .75, h, pose: 'lift' };
  if (t < C.jump + .8) { const u = ease(ev(t, C.jump, .8)); return { x: lerp(CLIP[0] - .002, J[0], u), y: lerp(CLIP[1] + .012, J[1], u), z: .75 + Math.sin(u * Math.PI) * .004 * (u > .7), h, pose: 'walk', ph: t * 12 }; }
  if (t < C.land) { const u = ev(t, C.jump + .8, C.land - C.jump - .8); return { x: lerp(J[0], F0[0], u), y: lerp(J[1] + .004, F0[1], smooth(u)), z: lerp(.75, 0, u), h, pose: 'fall', rot: Math.sin(t * 2) * .2 }; }
  if (t < C.wind) return { x: F0[0], y: F0[1], z: 0, h, pose: 'stand' };
  if (t < C.food) return { x: F0[0], y: F0[1], z: 0, h, pose: 'cold' };
  if (t < C.hero) return { x: F0[0], y: F0[1], z: 0, h, pose: 'hug' };
  if (t < C.back + .2) return { x: F0[0], y: F0[1], z: 0, h, pose: 'stand' };
  const u = gr; return { x: lerp(F0[0], CHAIR[0], u), y: lerp(F0[1], CHAIR[1], u), z: lerp(0, .45, u), h, pose: u < .3 ? 'stand' : 'sit' };
}
function drawYou(t, Y, o = {}) {
  const p = iso(Y.x, Y.y, Y.z), px = Y.h * K;
  const cold = smooth(ev(t, C.heat, 1.6)) * (1 - smooth(ev(t, C.food + .5, 1)));
  const col = cold > 0 ? `rgb(${lerp(46, 70, cold) | 0},${lerp(122, 140, cold) | 0},${lerp(120, 255, cold) | 0})` : '#2E7A78';
  return figure(p[0], p[1], px, Y.pose, { t, ph: Y.ph, rot: Y.rot, col, glow: o.glow, skin: cold > .5 ? '#BFD2EE' : '#E5C2A6' });
}

// ------------------------------------------------------------------ the beats that sit on top of the shot
const DRIPS = (() => { const r = mulberry32(33), a = []; for (let i = 0; i < 20; i++) a.push([C.x5 - 1 + i * .5 - .55, (r() - .5) * .05, (r() - .5) * .03, r()]); return a; })();      // impacts land on the beat
function waterOnFloor(t) {
  // the drop that lands on you
  if (t >= C.drop - .6 && t < C.hero) {
    const f = ev(t, C.drop - .6, .6), z = lerp(.35, 0, f * f);
    if (f < 1) { const p = iso(F0[0] + .001, F0[1], z + .005); ctx.fillStyle = 'rgba(170,205,245,.85)'; ctx.beginPath(); ctx.ellipse(p[0], p[1], .0035 * K, .0045 * K, 0, 0, TAU); ctx.fill(); }
  }
}
function wrapBlob(t, Y) {      // the water skin around you, trembling
  const w = ev(t, C.drop, .35) * (1 - ev(t, C.wind, .5)); if (w <= 0) return;
  const p = iso(Y.x, Y.y, Y.z), R = Y.h * K * .62 * (.6 + .4 * w);
  ctx.save(); ctx.globalAlpha = .55 * w; ctx.fillStyle = '#9CC8F2'; ctx.beginPath();
  for (let i = 0; i <= 48; i++) { const a = i / 48 * TAU, r = R * (1 + .05 * Math.sin(a * 5 + t * 9) + .03 * Math.sin(a * 3 - t * 6)); const x = p[0] + Math.cos(a) * r * .82, y = p[1] - Y.h * K * .48 + Math.sin(a) * r; i ? ctx.lineTo(x, y) : ctx.moveTo(x, y); }
  ctx.closePath(); ctx.fill(); ctx.globalAlpha = .9 * w; ctx.strokeStyle = '#E4F1FF'; ctx.lineWidth = 3; ctx.stroke();
  ctx.globalAlpha = .6 * w; ctx.fillStyle = '#FFFFFF'; ctx.beginPath(); ctx.ellipse(p[0] - R * .3, p[1] - Y.h * K * .48 - R * .55, R * .14, R * .07, -.5, 0, TAU); ctx.fill();
  ctx.restore();
}
function rainDrops(t) {      // big drops falling around you (slowed for the eye), each one bigger than half of you
  if (t < C.rain - .4 || t >= C.hero) return;
  for (const [t0, dx, dy, s] of DRIPS) {
    const u = (t - t0) / .55; if (u < -1 || u > 1.6) continue;
    const x = F0[0] + dx * .55, y = F0[1] + dy * .5;
    if (u < 1) { const z = lerp(.06, 0, Math.max(0, u)); if (u < 0) continue; const p = iso(x, y, z + .0025); ctx.fillStyle = 'rgba(160,200,245,.9)'; ctx.beginPath(); ctx.ellipse(p[0], p[1], .0025 * K, .0034 * K, 0, 0, TAU); ctx.fill(); ctx.fillStyle = 'rgba(255,255,255,.7)'; ctx.beginPath(); ctx.ellipse(p[0] - .0008 * K, p[1] - .0012 * K, .0006 * K, .0004 * K, -.5, 0, TAU); ctx.fill(); }
    else { const v = u - 1, ring = isoEllipse(x, y, 0, .002 + v * .01, .002 + v * .01); ctx.globalAlpha = 1 - v / .6; poly(ring, null, 'rgba(200,225,255,.9)', 3); const c = iso(x, y, 0); ctx.fillStyle = 'rgba(180,210,250,.8)'; for (let i = 0; i < 7; i++) { const a = i / 7 * TAU; ctx.beginPath(); ctx.arc(c[0] + Math.cos(a) * v * .012 * K, c[1] + Math.sin(a) * v * .006 * K - Math.sin(v / .6 * Math.PI) * .006 * K, .0005 * K, 0, TAU); ctx.fill(); } ctx.globalAlpha = 1; }
  }
}
function windLines(t) {
  if (t < C.wind - .3 || t >= C.food + .6) return;
  const k = ev(t, C.wind - .3, .6) * (1 - ev(t, C.food, .6));
  ctx.save(); ctx.globalAlpha = .55 * k; ctx.strokeStyle = '#CFE2FF'; ctx.lineWidth = 3; ctx.setLineDash([140, 90]);
  for (let i = 0; i < 16; i++) { const y = 420 + i * 70; ctx.lineDashOffset = -(t * 900 + i * 77); ctx.beginPath(); ctx.moveTo(-40, y); ctx.bezierCurveTo(300, y - 30 * Math.sin(t + i), 700, y + 30 * Math.cos(t + i), 1120, y); ctx.stroke(); }
  ctx.restore();
}
function heatOut(t, Y) {      // heat leaving through the skin
  if (t < C.heat || t >= C.food + .3) return;
  const p = iso(Y.x, Y.y, Y.z), hpx = Y.h * K;
  ctx.save(); ctx.strokeStyle = ACC; ctx.lineWidth = 4; ctx.lineCap = 'round';
  for (let i = 0; i < 14; i++) { const a = i / 14 * TAU, ph = (t * 1.4 + i * .37) % 1, r0 = hpx * (.32 + ph * .5); ctx.globalAlpha = 1 - ph; ctx.beginPath(); ctx.moveTo(p[0] + Math.cos(a) * r0, p[1] - hpx * .5 + Math.sin(a) * r0 * 1.2); ctx.lineTo(p[0] + Math.cos(a) * (r0 + hpx * .1), p[1] - hpx * .5 + Math.sin(a) * (r0 + hpx * .1) * 1.2); ctx.stroke(); }
  ctx.restore();
}
function readout(t, Y) {      // the parameter: height, rolling with the shrink (and back)
  const on = (t >= C.pak + .15 && t < C.pak + 2.6) || (t >= C.back + .2 && t < C.back + 3.3);
  if (!on) return;
  const cm = Y.h * 100, txt = cm >= 10 ? `${Math.round(cm)} cm` : `${cm.toFixed(1)} cm`;
  const p = iso(Y.x, Y.y, Y.z), top = p[1] - Y.h * K - 40;
  hero(t, t >= C.back ? C.back + .2 : C.pak, [{ parts: [['身高  ', WHITE], [txt, ACC]], size: 70 }], 72, 300);
  ctx.strokeStyle = 'rgba(255,122,46,.8)'; ctx.lineWidth = 2; ctx.setLineDash([8, 6]); ctx.beginPath(); ctx.moveTo(p[0] + 30, top + 40); ctx.lineTo(p[0] + 30, p[1]); ctx.stroke(); ctx.setLineDash([]);
}
function flash(t, t0, a = .5) { const k = 1 - ev(t, t0, .35); if (t >= t0 && k > 0) { ctx.fillStyle = `rgba(255,244,232,${a * k * k})`; ctx.fillRect(0, 0, W, H); } }

// ------------------------------------------------------------------ the frame
const CLEAN = location.search.includes('clean');
function subtitles(t) { if (CLEAN) return; const c = CUES.subs.find(c => t >= c.t0 && t < c.t1); if (!c || t >= C.next - .2) return; subtitle(c.text); }
function endCard(t) {
  ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);
  if (t < C.next) return;
  hero(t, C.next, [{ parts: [['下一个「如果」，', '#F4F4F2']], size: 96 }, { parts: [['你想看什么？', ACC]], size: 96 }], 72, 860, { lh: 128 });
  ctx.font = `400 32px ${UI}`; ctx.fillStyle = 'rgba(244,244,242,.6)'; ctx.textAlign = 'left'; ctx.fillText('如果……会怎样 · 03', 76, 1130);
}
window.seek = function (t) {
  t = clamp(t, 0, DUR - 1 / FPS);
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over'; OY = 0;
  if (t >= C.black) { endCard(t); subtitles(t); return true; }
  const Y = you(t);
  camAt(t, Y);
  const lifted = t >= C.lift - .15 && t < C.back + .2;
  const hugging = t >= C.food && t < C.hero;
  room(t, { clipLifted: lifted, bite: ev(t, C.eat, 2.6) * .85, deskDrop: true, hugRice: hugging });
  // the desk ant walks from the first frame to the last
  { const [x, y, z] = deskAnt(t); ant(x, y, z, 0, t, {}); }
  // the floor ant (L13): walks past you
  if (t >= C.ant - .5 && t < C.back + 1.5) { const u = (t - C.ant + .5) * .006; ant(F0[0] + .025 - u, F0[1] + .006, 0, Math.PI, t, { beads: t >= C.antp + .8 }); }
  waterOnFloor(t); rainDrops(t);
  // you
  const glow = (t >= C.rule && t < C.drop) ? .5 + .5 * Math.sin((t - C.rule) * 6) : (t >= C.cause - .5 && t < C.ant) ? .6 + .4 * Math.sin(t * 6) : 0;
  if (t >= C.hero && t < C.ant) {      // the reversal: the same cause behind the superpower and the danger
    const p = iso(Y.x, Y.y, Y.z), px = Y.h * K, k = expoOut(ev(t, C.same, .5));
    figure(p[0] - 300 * k, p[1] - 40 * k, px, 'fall', { t, glow, col: '#2E7A78' });
    figure(p[0] + 300 * k, p[1], px, 'cold', { t, glow, col: '#4A8BFF', skin: '#BFD2EE' });
    if (k > .5) { plateText('摔不坏 · 力气大', p[0] - 300 - 150, p[1] + 80, { size: 34 }); plateText('挂水 · 失温', p[0] + 300 - 110, p[1] + 80, { size: 34 }); }
  }
  const J = drawYou(t, Y, { glow });
  if (hugging) {      // you hold the grain upright and eat into it
    const p = iso(Y.x, Y.y, Y.z), hp = Y.h * K, b = ev(t, C.eat, 2.6) * .7, cx = p[0] + hp * .2, cy = p[1] - hp * .42;
    ctx.save(); ctx.translate(cx, cy); ctx.rotate(.25); ctx.fillStyle = '#F2EBDD'; ctx.beginPath(); ctx.ellipse(0, 0, hp * .13, hp * .31 * (1 - b), 0, 0, TAU); ctx.fill();
    ctx.fillStyle = '#FFFDF6'; ctx.beginPath(); ctx.ellipse(-hp * .03, -hp * .05 * (1 - b), hp * .06, hp * .2 * (1 - b), 0, 0, TAU); ctx.fill();
    if (b > 0) { ctx.fillStyle = 'rgba(242,235,221,.9)'; for (let i = 0; i < 5; i++) { const a = hash(i, 7) * TAU, r = hp * (.15 + .1 * hash(i, 8)); ctx.beginPath(); ctx.arc(Math.cos(a) * r, hp * .35 + Math.sin(a) * r * .3, hp * .015, 0, TAU); ctx.fill(); } }
    ctx.restore();
  }
  if (Y.pose === 'lift' || (t >= C.lift - .15 && t < C.jump + .4)) {      // the paper clip above your head
    const p = iso(Y.x, Y.y, Y.z), k = Y.h * K / 170, b = Math.sin(t * 5) * 8 * k;
    ctx.save(); ctx.translate(p[0], p[1] - 212 * k - b); ctx.rotate(-.08); ctx.strokeStyle = '#D5DEE8'; ctx.lineWidth = Math.max(2, 6 * k); ctx.lineJoin = 'round';
    ctx.lineWidth = Math.max(2, .0009 * K); ctx.beginPath(); ctx.roundRect(-.016 * K, -.004 * K, .032 * K, .008 * K, .004 * K); ctx.roundRect(-.012 * K, -.0024 * K, .025 * K, .0048 * K, .0024 * K); ctx.stroke(); ctx.restore();
  }
  wrapBlob(t, Y); heatOut(t, Y); windLines(t);
  // fall streamlines
  if (Y.pose === 'fall') { const p = iso(Y.x, Y.y, Y.z); ctx.strokeStyle = 'rgba(220,235,250,.55)'; ctx.lineWidth = 2; for (let i = 0; i < 9; i++) { const x = p[0] - 120 + i * 30, y0 = p[1] - Y.h * K * .5 + ((t * 600 + i * 90) % 400) - 200; ctx.beginPath(); ctx.moveTo(x, y0); ctx.lineTo(x, y0 + 90); ctx.stroke(); } }
  // the day/night cycle while you eat
  if (t >= C.eat && t < C.hero) { const d = (t - C.eat) * .9, n = .5 - .5 * Math.cos(d * TAU); ctx.fillStyle = `rgba(4,8,22,${.45 * n})`; ctx.fillRect(0, 0, W, H); }
  // ----- type: the numbers each line is about
  readout(t, Y);
  if (t < C.pak + .2) {      // first frame is the title
    ctx.fillStyle = 'rgba(8,12,28,.45)'; ctx.fillRect(0, 0, W, 470);
    hero(t, -1, [{ parts: [['如果你突然', WHITE]], size: 96 }, { parts: [['缩小到', WHITE], ['一厘米', ACC], ['？', WHITE]], size: 96 }], 72, 250, { lh: 124 });
  }
  hero(t, C.half, [{ parts: [['体重 ', WHITE], [roll('12', t, C.half, .5), ACC], [' 毫克', ACC]], size: 120 }, { parts: [['一颗米粒约 25 毫克', WHITE]], size: 40, ui: true }], 72, 330, { lh: 90, t1: C.strong });
  if (t >= C.clip && t < C.jump) { const c = iso(...CLIP); if (t < C.lift) bracket(c[0], c[1], .034 * K * .9, .012 * K, '回形针 · 1 克', { dx: 60, dy: -160 }); hero(t, C.clip, [{ parts: [['你体重的 ', WHITE], ['82', ACC], [' 倍', ACC]], size: 110 }], 72, 330); }
  if (t >= C.jump + .8 && t < C.turn) { hero(t, C.leaf, [{ parts: [['下落速度  约 ', WHITE], ['3 m/s', ACC]], size: 64, ui: false }], 72, 300); ctx.font = `400 30px ${UI}`; ctx.fillStyle = 'rgba(220,235,250,.75)'; ctx.textAlign = 'left'; ctx.fillText('画面已慢放', 76, 360); }
  if (t >= C.rule + .25 && t < C.drop) hero(t, C.rule + .25, [{ parts: [['表面 ', WHITE], ['÷ ' + roll('29000', t, C.rule + .25, 1.2), ACC]], size: 100 }, { parts: [['体重 ', WHITE], ['÷ ' + roll('4900000', t, C.rule + .6, 1.4), WHITE]], size: 100 }], 72, 280, { lh: 120 });
  if (t >= C.heavy && t < C.rain) hero(t, C.heavy, [{ parts: [['水 ', WHITE], ['31', ACC], [' 毫克', ACC]], size: 110 }, { parts: [['你 12 毫克', WHITE]], size: 56, ui: true }], 72, 300, { lh: 90 });
  if (t >= C.x5 && t < C.wind) hero(t, C.x5, [{ parts: [['雨滴 = 你 × ', WHITE], ['5', ACC]], size: 110 }], 72, 300);
  if (t >= C.minutes && t < C.food) hero(t, C.minutes, [{ parts: [['37 °C → ', WHITE], ['27 °C', COLD]], size: 100 }, { parts: [['约 2 分钟', WHITE]], size: 56, ui: true }], 72, 300, { lh: 90 });
  if (t >= C.eat && t < C.hero) { const d = 1 + Math.floor((t - C.eat) * .9); hero(t, C.eat, [{ parts: [['第 ' + d + ' 天', ACC]], size: 110 }, { parts: [['一天吃掉 ≥ 1 个你', WHITE]], size: 48, ui: true }], 72, 300, { lh: 84 }); plateText('最小的温血动物：小臭鼩 1.8 克 = 你 × 150', 72, 520, { size: 32 }); }
  if (t >= C.cause && t < C.ant) hero(t, C.cause, [{ parts: [['同一个原因：', WHITE], ['表面', ACC]], size: 96 }], 72, 300);
  if (t >= C.antp && t < C.back) ['冷血', '不沾水', '不怕摔'].forEach((s, i) => hero(t, C.antp + i * .5, [{ parts: [[s, i === 1 ? ACC : WHITE]], size: 96 }], 72, 260 + i * 112));
  if (t >= C.back + 2.6) { const [x, y, z] = deskAnt(t), p = iso(x, y, z); bracket(p[0], p[1], 40, 30, '', { accent: true }); }
  flash(t, C.pak, .4);
  subtitles(t);
  return true;
};
window.DURATION = DUR; window.FPS = FPS;
window.ready = Promise.all([`700 54px ${UI}`, `900 84px ${DSP}`].map(f => document.fonts.load(f)));
