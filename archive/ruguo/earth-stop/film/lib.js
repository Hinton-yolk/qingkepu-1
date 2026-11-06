// 如果……会怎样 02 · shared drawing library (isometric diorama, blueprint sheet, hologram plates, orthographic globe).
// Same grammar as episode 01: isometric diorama (human view) → blueprint sheet + hologram plates; one accent.
'use strict';
const W = 1080, H = 1920;
const cv = document.getElementById('c'); cv.width = W; cv.height = H;
let ctx = cv.getContext('2d');
const UI = '"Noto Sans Mono CJK SC"', DSP = '"Noto Sans CJK SC"';
const ACC = '#FF6A1A', HOT = '#FFD9B8', LINE = '#DCEBFA', INK = '#2A2622';
const C30 = Math.cos(Math.PI / 6), TAU = Math.PI * 2, D2R = Math.PI / 180;
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, k) => a + (b - a) * k;
const ev = (t, t0, d) => clamp((t - t0) / d);
const smooth = x => { x = clamp(x); return x * x * (3 - 2 * x); };
const expoOut = x => { x = clamp(x); return x === 1 ? 1 : 1 - Math.pow(2, -10 * x); };
function mulberry32(a) { return () => { a |= 0; a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }

// ------------------------------------------------------------------ isometric camera (metres: x down-right, y down-left, z up). East = screen right = (1,-1)/√2.
let CU = 0, CV = 0, K = 90, OY = 0;
const iso = (x, y, z) => [W / 2 + ((x - y) * C30 - CU) * K, H / 2 + OY + ((x + y) * .5 - z - CV) * K];
const cam = (x, y, z, k) => { CU = (x - y) * C30; CV = (x + y) * .5 - z; K = k; };
function poly(pts, fill, stroke, lw, dash) {
  ctx.beginPath(); pts.forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)); ctx.closePath();
  if (fill) { ctx.fillStyle = fill; ctx.fill(); }
  if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = lw; ctx.setLineDash(dash || []); ctx.stroke(); ctx.setLineDash([]); }
}
const shade = (hex, k) => { const n = parseInt(hex.slice(1), 16); const r = n >> 16, g = n >> 8 & 255, b = n & 255;
  const to = k > 0 ? [255, 246, 232] : [52, 30, 48], a = Math.abs(k); return `rgb(${lerp(r, to[0], a) | 0},${lerp(g, to[1], a) | 0},${lerp(b, to[2], a) | 0})`; };
function box(x0, x1, y0, y1, z0, z1, col, mode = 'human') {
  const top = [iso(x0, y0, z1), iso(x1, y0, z1), iso(x1, y1, z1), iso(x0, y1, z1)];
  const px = [iso(x1, y0, z0), iso(x1, y1, z0), iso(x1, y1, z1), iso(x1, y0, z1)];
  const py = [iso(x0, y1, z0), iso(x1, y1, z0), iso(x1, y1, z1), iso(x0, y1, z1)];
  if (mode === 'human') { poly(py, shade(col, .16)); poly(px, shade(col, -.34)); poly(top, shade(col, .05)); }
  else { const f = 'rgba(16,40,90,.92)'; poly(py, f, LINE, 2); poly(px, f, LINE, 2); poly(top, f, LINE, 2); }
}
function hatch(pts, col, gap, lw, ang = 1) {
  ctx.save(); poly(pts); ctx.clip();
  const xs = pts.map(p => p[0]), ys = pts.map(p => p[1]);
  const x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = Math.min(...ys), y1 = Math.max(...ys);
  ctx.strokeStyle = col; ctx.lineWidth = lw; ctx.beginPath();
  for (let s = x0 - (y1 - y0); s < x1; s += gap) { ctx.moveTo(s, y1); ctx.lineTo(s + (y1 - y0) * ang, y0); }
  ctx.stroke(); ctx.restore();
}

// ------------------------------------------------------------------ type + hologram furniture (as in 01)
const GLY = '0123456789';
function roll(str, t, t0, dur = .3) {
  if (t < t0) return '';
  const p = (t - t0) / dur;
  return [...str].map((ch, i) => (p >= (i + 1) / str.length || !/[0-9]/.test(ch)) ? ch : GLY[Math.floor(mulberry32(i * 97 + Math.floor(t * 30))() * 10)]).join('');
}
function plateText(txt, x, y, o = {}) {
  ctx.font = `700 ${o.size ?? 42}px ${UI}`; const tw = ctx.measureText(txt).width;
  const hh = (o.size ?? 42) * 1.6, px = clamp(o.right ? x - tw - 36 : x, 24, W - 24 - tw - 36), py = y - hh / 2;
  ctx.fillStyle = 'rgba(6,12,28,.86)'; ctx.fillRect(px, py, tw + 36, hh);
  ctx.strokeStyle = 'rgba(220,235,250,.6)'; ctx.lineWidth = 1; ctx.strokeRect(px + .5, py + .5, tw + 35, hh - 1);
  ctx.fillStyle = o.accent ? ACC : '#F4F8FC'; ctx.textBaseline = 'middle'; ctx.textAlign = 'left'; ctx.fillText(txt, px + 18, py + hh / 2 + 2);
  return [px, py, tw + 36, hh];
}
function bracket(cx, cy, w, h, label, o = {}) {
  const ww = w / 2, hh = h / 2, L = 22;
  ctx.strokeStyle = o.accent ? ACC : LINE; ctx.lineWidth = 3; ctx.beginPath();
  for (const [sx, sy] of [[-1, -1], [1, -1], [1, 1], [-1, 1]]) { const x = cx + sx * ww, y = cy + sy * hh; ctx.moveTo(x, y - sy * L); ctx.lineTo(x, y); ctx.lineTo(x - sx * L, y); }
  ctx.stroke();
  if (!label) return;
  const dx = o.dx ?? ww + 40, dy = o.dy ?? -hh - 60, lx = cx + dx, ly = cy + dy;
  ctx.strokeStyle = LINE; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(cx + Math.sign(dx) * ww, cy - hh); ctx.lineTo(lx, ly); ctx.stroke();
  plateText(label, lx, ly, { right: dx < 0, accent: o.accent, size: o.size ?? 42 });
}
function display(lines, x, y, o = {}) {
  ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic';
  lines.forEach((ln, i) => {
    ctx.font = `900 ${o.size ?? 100}px ${DSP}`; let cx = x;
    for (const [s, col] of ln) { ctx.fillStyle = col; ctx.fillText(s, cx, y + i * (o.lh ?? 118)); cx += ctx.measureText(s).width; }
  });
}
function subtitle(txt) {
  ctx.font = `700 54px ${UI}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.lineJoin = 'round';
  ctx.lineWidth = 12; ctx.strokeStyle = '#0B1328'; ctx.strokeText(txt, W / 2, 1600); ctx.fillStyle = '#F7F4EE'; ctx.fillText(txt, W / 2, 1600);
}
// the series panel: one real-world parameter, flipped
function panel(name, from, to, flipped) {
  const x = 72, y = 1150, w = 936, h = 270;
  ctx.fillStyle = 'rgba(8,14,30,.92)'; ctx.fillRect(x, y, w, h);
  ctx.strokeStyle = 'rgba(220,235,250,.7)'; ctx.lineWidth = 1.5; ctx.strokeRect(x + .5, y + .5, w - 1, h - 1);
  ctx.font = `400 30px ${UI}`; ctx.fillStyle = 'rgba(220,235,250,.7)'; ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic';
  ctx.fillText('现实参数', x + 32, y + 52);
  ctx.font = `700 44px ${UI}`; ctx.fillStyle = '#F4F8FC'; ctx.fillText(name, x + 32, y + 130);
  const tx = x + w - 200, ty = y + 112;
  ctx.fillStyle = flipped ? ACC : 'rgba(220,235,250,.25)'; ctx.beginPath(); ctx.roundRect(tx, ty - 26, 140, 52, 26); ctx.fill();
  ctx.fillStyle = '#F4F8FC'; ctx.beginPath(); ctx.arc(tx + 26 + (flipped ? 88 : 0), ty, 20, 0, TAU); ctx.fill();
  ctx.font = `700 46px ${UI}`;
  ctx.fillStyle = 'rgba(220,235,250,.45)'; ctx.fillText(from, x + 32, y + 212);
  const fw = ctx.measureText(from).width;
  ctx.fillStyle = 'rgba(220,235,250,.45)'; ctx.fillText('  →  ', x + 32 + fw, y + 212);
  ctx.fillStyle = flipped ? ACC : '#F4F8FC'; ctx.fillText(to, x + 32 + fw + ctx.measureText('  →  ').width, y + 212);
}

// ------------------------------------------------------------------ backgrounds
function duskBG() {
  const g = ctx.createLinearGradient(0, 0, 0, H); g.addColorStop(0, '#EBD9C9'); g.addColorStop(.45, '#F2E2CF'); g.addColorStop(1, '#EDE3D6');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  ctx.fillStyle = 'rgba(80,50,40,.10)';
  for (let x = -40; x <= 20; x++) for (let y = -40; y <= 20; y++) { const [sx, sy] = iso(x, y, -0.3); if (sx > -10 && sx < W + 10 && sy > -10 && sy < H + 10) { ctx.beginPath(); ctx.arc(sx, sy, 2.2, 0, TAU); ctx.fill(); } }
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
  for (let i = -40; i <= 40; i++) { let a = iso(i, -40, 0), b = iso(i, 40, 0); ctx.moveTo(...a); ctx.lineTo(...b); a = iso(-40, i, 0); b = iso(40, i, 0); ctx.moveTo(...a); ctx.lineTo(...b); }
  ctx.stroke();
}

// ------------------------------------------------------------------ the balcony at dusk
const SKY = (() => { const r = mulberry32(7), b = []; for (let x = -40; x <= 4; x += 4.2) for (let y = -40; y <= 4; y += 4.2) { if (x > -7 && y > -7) continue; if (r() < .7) { const xx = x + r() * 1.5, yy = y + r() * 1.5; b.push([xx, xx + 2.4 + r() * 1.6, yy, yy + 2.4 + r() * 1.6, -90, (xx + yy) * .5 + 3 + Math.pow(r(), 1.4) * 3.5]); } } return b.sort((a, c) => (a[0] + a[2]) - (c[0] + c[2])); })();
const BAL = { X: 6.4, Y: 4.4 };
const EAST = [Math.SQRT1_2, -Math.SQRT1_2];
let SHANG = 0, LIT_T = 1e9;      // shadow angle; windows with an on-time below LIT_T are lit
const CUPW = [2.95, 2.0, .74], DRIPW = [3.6, 2.3, .74];
function moved(anchor, off, fn) {      // draw fn displaced by off = [dx, dy, rot] (screen), with streaks back to where it was
  if (!off || (!off[0] && !off[1] && !off[2])) return fn();
  const [ax, ay] = anchor, d = Math.hypot(off[0], off[1]);
  if (d > 4) { ctx.strokeStyle = ACC; ctx.lineWidth = 3; for (let i = 0; i < 5; i++) { const o = (i - 2) * 9; ctx.globalAlpha = .25 + .12 * i; ctx.beginPath(); ctx.moveTo(ax + off[0] * Math.max(0, 1 - 380 / d), ay + off[1] * Math.max(0, 1 - 380 / d) + o); ctx.lineTo(ax + off[0] - 20, ay + off[1] + o); ctx.stroke(); } ctx.globalAlpha = 1; }
  ctx.save(); ctx.translate(ax + off[0], ay + off[1]); ctx.rotate(off[2] || 0); ctx.translate(-ax, -ay); fn(); ctx.restore();
}
function shadowOf(x0, x1, y0, y1, h, len) {      // a long floor shadow thrown east by a low western sun
  const L = h * len, ca = Math.cos(SHANG), sa = Math.sin(SHANG), ex = EAST[0] * ca - EAST[1] * sa, ey = EAST[0] * sa + EAST[1] * ca;
  const pts = [[x0, y1], [x1, y1], [x1, y0], [x0, y0]].map(([x, y]) => [x, y]);
  const hull = [[x0, y1], [x0, y0], [x1, y0], [x1 + ex * L, y0 + ey * L], [x1 + ex * L, y1 + ey * L], [x0 + ex * L, y1 + ey * L]];
  ctx.save(); ctx.beginPath(); const f = [iso(0, 0, 0), iso(BAL.X, 0, 0), iso(BAL.X, BAL.Y, 0), iso(0, BAL.Y, 0)]; f.forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)); ctx.closePath(); ctx.clip();
  poly(hull.map(([x, y]) => iso(x, y, .002)), 'rgba(90,50,60,.22)'); ctx.restore(); void pts;
}
function cup(x, y, z, mode, s = 1) {
  const [cx, cy] = iso(x, y, z), r = .09 * K * 1.22 * s, hgt = .12 * K * s;
  if (mode === 'human') {
    ctx.fillStyle = '#F4EEE6'; ctx.fillRect(cx - r, cy - hgt, 2 * r, hgt);
    ctx.beginPath(); ctx.ellipse(cx, cy, r, r * .58, 0, 0, Math.PI); ctx.fill();
    ctx.fillStyle = '#5A3A2A'; ctx.beginPath(); ctx.ellipse(cx, cy - hgt, r, r * .58, 0, 0, TAU); ctx.fill();
    ctx.strokeStyle = '#E2D8CC'; ctx.lineWidth = 2; ctx.stroke();
    ctx.strokeStyle = '#F4EEE6'; ctx.lineWidth = r * .32; ctx.beginPath(); ctx.arc(cx + r * 1.15, cy - hgt * .5, r * .42, -1.3, 1.3); ctx.stroke();
  } else {
    ctx.strokeStyle = LINE; ctx.lineWidth = 2.5; ctx.fillStyle = 'rgba(16,40,90,.95)';
    ctx.beginPath(); ctx.moveTo(cx - r, cy - hgt); ctx.lineTo(cx - r, cy); ctx.ellipse(cx, cy, r, r * .58, 0, Math.PI, 0, true); ctx.lineTo(cx + r, cy - hgt); ctx.closePath(); ctx.fill(); ctx.stroke();
    ctx.beginPath(); ctx.ellipse(cx, cy - hgt, r, r * .58, 0, 0, TAU); ctx.stroke();
    ctx.beginPath(); ctx.arc(cx + r * 1.15, cy - hgt * .5, r * .42, -1.3, 1.3); ctx.stroke();
  }
}
function dripper(x, y, z, mode) {      // a pour-over cone on a small server
  const [cx, cy] = iso(x, y, z), s = K / 100, hum = mode === 'human';
  ctx.lineWidth = 2; ctx.strokeStyle = hum ? '#8C7F7A' : LINE;
  ctx.fillStyle = hum ? 'rgba(200,220,228,.75)' : 'rgba(16,40,90,.95)';
  ctx.beginPath(); ctx.moveTo(cx - 11 * s, cy); ctx.lineTo(cx - 13 * s, cy - 18 * s); ctx.lineTo(cx + 13 * s, cy - 18 * s); ctx.lineTo(cx + 11 * s, cy); ctx.closePath(); ctx.fill(); ctx.stroke();
  ctx.fillStyle = hum ? '#F4EEE6' : 'rgba(16,40,90,.95)';
  ctx.beginPath(); ctx.moveTo(cx - 6 * s, cy - 18 * s); ctx.lineTo(cx - 17 * s, cy - 36 * s); ctx.lineTo(cx + 17 * s, cy - 36 * s); ctx.lineTo(cx + 6 * s, cy - 18 * s); ctx.closePath(); ctx.fill(); ctx.stroke();
}
function table(mode) {
  const [cx, cy] = iso(3.3, 2.1, .74), rx = .55 * K * 1.22, ry = rx * .58;
  const [bx, by] = iso(3.3, 2.1, 0);
  if (mode === 'human') {
    ctx.strokeStyle = '#3E3A38'; ctx.lineWidth = .06 * K; ctx.beginPath(); ctx.moveTo(bx, by); ctx.lineTo(cx, cy); ctx.stroke();
    ctx.fillStyle = '#3E3A38'; ctx.beginPath(); ctx.ellipse(bx, by, rx * .45, ry * .45, 0, 0, TAU); ctx.fill();
    ctx.fillStyle = '#B98E66'; ctx.beginPath(); ctx.ellipse(cx, cy + .04 * K, rx, ry, 0, 0, TAU); ctx.fill();
    ctx.fillStyle = '#D4AD82'; ctx.beginPath(); ctx.ellipse(cx, cy, rx, ry, 0, 0, TAU); ctx.fill();
  } else {
    ctx.strokeStyle = LINE; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(bx, by); ctx.lineTo(cx, cy); ctx.stroke();
    ctx.beginPath(); ctx.ellipse(bx, by, rx * .45, ry * .45, 0, 0, TAU); ctx.stroke();
    ctx.fillStyle = 'rgba(16,40,90,.95)'; ctx.beginPath(); ctx.ellipse(cx, cy, rx, ry, 0, 0, TAU); ctx.fill(); ctx.stroke();
  }
}
function person(x, y, z, mode, fl = 0) {
  const k = K / 80, [bx0, by0] = iso(x, y, z), bx = bx0 + fl, by = by0 - fl * .18;
  if (fl > 0) { ctx.strokeStyle = 'rgba(255,106,26,.8)'; ctx.lineWidth = 3; for (let i = 0; i < 7; i++) { const yy = by - (10 + i * 16) * k; ctx.globalAlpha = .25 + .1 * i; ctx.beginPath(); ctx.moveTo(Math.max(bx0, bx - fl * (.5 + .07 * i)), yy + fl * .05); ctx.lineTo(bx - 24 * k, yy); ctx.stroke(); } ctx.globalAlpha = 1; }
  ctx.save(); ctx.translate(bx, by); ctx.scale(k, k); ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  const hum = mode === 'human', body = hum ? '#2E7A78' : 'rgba(16,40,90,.95)', legs = hum ? '#34383F' : 'rgba(16,40,90,.95)', skin = hum ? '#E5C2A6' : 'rgba(16,40,90,.95)';
  const st = (fn) => { fn(); if (!hum) { ctx.strokeStyle = LINE; ctx.lineWidth = 2.5 / k; ctx.stroke(); } };
  ctx.fillStyle = body; st(() => { ctx.beginPath(); ctx.moveTo(-20, 0); ctx.lineTo(-14, -92); ctx.quadraticCurveTo(0, -104, 14, -92); ctx.lineTo(22, 0); ctx.closePath(); ctx.fill(); });
  if (hum) { ctx.strokeStyle = legs; ctx.lineWidth = 22; ctx.beginPath(); ctx.moveTo(-6, -4); ctx.lineTo(34, 18); ctx.lineTo(34, 66); ctx.stroke(); }
  else { ctx.strokeStyle = LINE; ctx.lineWidth = 2.5; ctx.beginPath(); ctx.moveTo(-6, -4); ctx.lineTo(34, 18); ctx.lineTo(34, 66); ctx.stroke(); }
  ctx.fillStyle = skin; st(() => { ctx.beginPath(); ctx.arc(2, -122, 21, 0, TAU); ctx.fill(); });
  if (hum) { ctx.fillStyle = '#2A2522'; ctx.beginPath(); ctx.arc(2, -126, 22, Math.PI * 1.05, Math.PI * 2.05); ctx.fill(); }
  ctx.restore();
  return [bx, by - 70 * k, bx0, by0 - 70 * k];
}
function plant(mode) {
  box(5.35, 5.85, .35, .85, 0, .55, '#9C6B4E', mode);
  const [cx, cy] = iso(5.6, .6, 1.25), r = .5 * K;
  if (mode === 'human') { for (const [dx, dy, rr, c] of [[-.4, .2, .7, '#5F7F55'], [.35, .1, .65, '#6E8F5F'], [0, -.35, .75, '#7FA06A']]) { ctx.fillStyle = c; ctx.beginPath(); ctx.arc(cx + dx * r, cy + dy * r, rr * r, 0, TAU); ctx.fill(); } }
  else { ctx.strokeStyle = LINE; ctx.lineWidth = 2; for (const [dx, dy, rr] of [[-.4, .2, .7], [.35, .1, .65], [0, -.35, .75]]) { ctx.fillStyle = 'rgba(16,40,90,.95)'; ctx.beginPath(); ctx.arc(cx + dx * r, cy + dy * r, rr * r, 0, TAU); ctx.fill(); ctx.stroke(); } }
}
function railing(mode) {
  const col = mode === 'human' ? '#3E3A38' : LINE, glass = mode === 'human' ? 'rgba(190,215,225,.28)' : 'rgba(220,235,250,.06)';
  const top = 1.05;
  poly([iso(0, BAL.Y, 0), iso(BAL.X, BAL.Y, 0), iso(BAL.X, BAL.Y, top), iso(0, BAL.Y, top)], glass);
  poly([iso(BAL.X, 0, 0), iso(BAL.X, BAL.Y, 0), iso(BAL.X, BAL.Y, top), iso(BAL.X, 0, top)], glass);
  ctx.strokeStyle = col; ctx.lineWidth = mode === 'human' ? .05 * K : 2.5; ctx.beginPath();
  ctx.moveTo(...iso(0, BAL.Y, top)); ctx.lineTo(...iso(BAL.X, BAL.Y, top)); ctx.lineTo(...iso(BAL.X, 0, top)); ctx.stroke();
  ctx.lineWidth = mode === 'human' ? .03 * K : 1.5; ctx.beginPath();
  for (let x = 0; x <= BAL.X + .01; x += BAL.X / 4) { ctx.moveTo(...iso(x, BAL.Y, 0)); ctx.lineTo(...iso(x, BAL.Y, top)); }
  for (let y = 0; y <= BAL.Y + .01; y += BAL.Y / 3) { ctx.moveTo(...iso(BAL.X, y, 0)); ctx.lineTo(...iso(BAL.X, y, top)); }
  ctx.stroke();
}
function balcony(mode, o = {}) {
  if (mode === 'human' && o.sun !== false) sun(...(o.sunAt ?? [250, 560]), 64);
  // skyline behind
  if (o.sky !== false) for (const b of SKY) {
    const [x0, x1, y0, y1, z0, z1] = b;
    if (mode === 'human') { box(x0, x1, y0, y1, z0, z1, '#B88F92');
      const py = [iso(x0, y1, z0), iso(x1, y1, z0), iso(x1, y1, z1), iso(x0, y1, z1)];
      ctx.save(); poly(py); ctx.clip(); const r = mulberry32((x0 * 13 + y0 * 7) | 0);
      for (let z = z1 - 1.2; z > z1 - 30; z -= 1.1) for (let x = x0 + .35; x < x1 - .3; x += .7) if (r() < .2 && r() * 12 < LIT_T) poly([iso(x, y1, z), iso(x + .35, y1, z), iso(x + .35, y1, z + .5), iso(x, y1, z + .5)], 'rgba(255,220,160,.85)');
      ctx.restore(); }
    else { ctx.globalAlpha = .2; box(x0, x1, y0, y1, z0, z1, '', 'line'); ctx.globalAlpha = 1; }
  }
  if (mode === 'human') { const g = ctx.createLinearGradient(0, 400, 0, 1300); g.addColorStop(0, 'rgba(244,222,200,.15)'); g.addColorStop(1, 'rgba(244,222,200,.6)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); }      // distance haze
  // building facade (y = 0 plane) and slab
  const s = .3;
  if (mode === 'human') {
    ctx.save(); ctx.shadowColor = 'rgba(60,30,30,.25)'; ctx.shadowBlur = 60; ctx.shadowOffsetY = 40; poly([iso(0, 0, -s), iso(BAL.X, 0, -s), iso(BAL.X, BAL.Y, -s), iso(0, BAL.Y, -s)], '#000'); ctx.restore();
    poly([iso(0, 0, 0), iso(BAL.X, 0, 0), iso(BAL.X, BAL.Y, 0), iso(0, BAL.Y, 0)], '#DCC3A6');
    ctx.strokeStyle = 'rgba(90,60,40,.14)'; ctx.lineWidth = 1; ctx.beginPath(); for (let x = .4; x < BAL.X; x += .4) { ctx.moveTo(...iso(x, 0, 0)); ctx.lineTo(...iso(x, BAL.Y, 0)); } for (let y = .4; y < BAL.Y; y += .4) { ctx.moveTo(...iso(0, y, 0)); ctx.lineTo(...iso(BAL.X, y, 0)); } ctx.stroke();
    poly([iso(BAL.X, 0, -s), iso(BAL.X, BAL.Y, -s), iso(BAL.X, BAL.Y, 0), iso(BAL.X, 0, 0)], '#8C7F7A'); poly([iso(0, BAL.Y, -s), iso(BAL.X, BAL.Y, -s), iso(BAL.X, BAL.Y, 0), iso(0, BAL.Y, 0)], '#B6A69C');
    const wall = [iso(0, -.2, 0), iso(BAL.X, -.2, 0), iso(BAL.X, -.2, 3.2), iso(0, -.2, 3.2)];
    poly(wall, '#E8CDB4'); poly([iso(1.2, -.2, 0), iso(2.6, -.2, 0), iso(2.6, -.2, 2.3), iso(1.2, -.2, 2.3)], '#9FB3BF', '#7C6E66', 3);
    poly([iso(3.6, -.2, .9), iso(5.4, -.2, .9), iso(5.4, -.2, 2.3), iso(3.6, -.2, 2.3)], '#A9BCC6', '#7C6E66', 3);
    if (o.shadows !== false) { const len = o.shadowLen ?? 3.2; shadowOf(3.0, 3.6, 1.8, 2.4, .74, len); shadowOf(1.9, 2.5, 2.1, 2.7, 1.3, len); shadowOf(5.35, 5.85, .35, .85, 1.6, len); }
  } else {
    poly([iso(0, 0, 0), iso(BAL.X, 0, 0), iso(BAL.X, BAL.Y, 0), iso(0, BAL.Y, 0)], 'rgba(16,40,90,.9)', LINE, 2.5);
    poly([iso(BAL.X, 0, -s), iso(BAL.X, BAL.Y, -s), iso(BAL.X, BAL.Y, 0), iso(BAL.X, 0, 0)], 'rgba(16,40,90,.9)', LINE, 2);
    poly([iso(0, BAL.Y, -s), iso(BAL.X, BAL.Y, -s), iso(BAL.X, BAL.Y, 0), iso(0, BAL.Y, 0)], 'rgba(16,40,90,.9)', LINE, 2);
    poly([iso(0, -.2, 0), iso(BAL.X, -.2, 0), iso(BAL.X, -.2, 3.2), iso(0, -.2, 3.2)], 'rgba(16,40,90,.9)', LINE, 2);
    poly([iso(1.2, -.2, 0), iso(2.6, -.2, 0), iso(2.6, -.2, 2.3), iso(1.2, -.2, 2.3)], null, LINE, 1.5, [8, 6]);
    poly([iso(3.6, -.2, .9), iso(5.4, -.2, .9), iso(5.4, -.2, 2.3), iso(3.6, -.2, 2.3)], null, LINE, 1.5, [8, 6]);
  }
  const off = o.off || {};
  if (o.plant !== false) moved(iso(5.6, .6, .5), off.plant, () => plant(mode));
  if (o.bare) { railing(mode); return { head: iso(2.25, 2.35, 1.3) }; }
  moved(iso(2.2, 2.4, .2), off.chair, () => box(1.85, 2.55, 2.05, 2.75, 0, .45, '#6F625C', mode));           // chair
  let head = iso(2.25, 2.35, 1.3);
  if (o.person !== false) moved(iso(2.25, 2.35, .9), off.person, () => { head = person(2.25, 2.35, .45, mode, o.fling ?? 0); });
  if (off.person) head = [head[0] + off.person[0], head[1] + off.person[1]];
  moved(iso(3.3, 2.1, .4), off.table, () => table(mode));
  if (o.dripper !== false) moved(iso(...DRIPW), off.dripper, () => dripper(...DRIPW, mode));
  if (o.cup !== false) moved(iso(...CUPW), off.cup, () => cup(...CUPW, mode));
  railing(mode);
  return { head };
}
function sun(x, y, r) {
  const g = ctx.createRadialGradient(x, y, r * .6, x, y, r * 4); g.addColorStop(0, 'rgba(255,170,110,.55)'); g.addColorStop(1, 'rgba(255,170,110,0)');
  ctx.fillStyle = g; ctx.fillRect(x - r * 4, y - r * 4, r * 8, r * 8);
  ctx.fillStyle = '#FF9A55'; ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.fill();
}
// hologram velocity arrow, pointing east (screen right)
function vArrow(x, y, len, o = {}) {
  const col = o.col ?? LINE, lw = o.lw ?? 5;
  ctx.strokeStyle = col; ctx.fillStyle = col; ctx.lineWidth = lw; ctx.lineCap = 'butt';
  ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x + len - 22, y); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(x + len, y); ctx.lineTo(x + len - 30, y - 15); ctx.lineTo(x + len - 30, y + 15); ctx.closePath(); ctx.fill();
  if (o.ticks) { ctx.lineWidth = 2; ctx.beginPath(); for (let i = 1; i < 6; i++) { const xx = x + i * (len - 30) / 6; ctx.moveTo(xx, y - 8); ctx.lineTo(xx, y + 8); } ctx.stroke(); }
}
function floorArrow(o) {      // a big arrow painted on the floor plane, pointing east
  const [ex, ey] = EAST, c = [3.2, 2.2], L = 2.6, Wd = .5;
  const n = [ey, -ex];
  const P = (a, b) => iso(c[0] + ex * a + n[0] * b, c[1] + ey * a + n[1] * b, .01);
  const pts = [P(-L, -Wd / 2), P(L - .9, -Wd / 2), P(L - .9, -Wd), P(L, 0), P(L - .9, Wd), P(L - .9, Wd / 2), P(-L, Wd / 2)];
  poly(pts, o.fill, o.stroke, 3, o.dash);
}

// ------------------------------------------------------------------ globe (orthographic)
const ZD = (() => { const s = atob(ETOPO.b64), b = new Uint8Array(s.length); for (let i = 0; i < s.length; i++) b[i] = s.charCodeAt(i); return new Int16Array(b.buffer); })();
const zAt = (la, lo) => { let i = Math.floor((la + 90) * 2), j = Math.floor((lo + 180) * 2); i = clamp(i, 0, 359); j = ((j % 720) + 720) % 720; return ZD[i * 720 + j]; };
function ortho(lo0, la0, R, cx, cy) {
  const s0 = Math.sin(la0 * D2R), c0 = Math.cos(la0 * D2R);
  return {
    f(lo, la) { const l = (lo - lo0) * D2R, p = la * D2R; const cc = s0 * Math.sin(p) + c0 * Math.cos(p) * Math.cos(l);
      return [cx + R * Math.cos(p) * Math.sin(l), cy - R * (c0 * Math.sin(p) - s0 * Math.cos(p) * Math.cos(l)), cc]; },
    inv(x, y) { x = (x - cx) / R; y = -(y - cy) / R; const rho = Math.hypot(x, y); if (rho > 1) return null; const c = Math.asin(rho);
      if (rho < 1e-9) return [lo0, la0];
      const la = Math.asin(Math.cos(c) * s0 + y * Math.sin(c) * c0 / rho), lo = lo0 + Math.atan2(x * Math.sin(c), rho * c0 * Math.cos(c) - y * s0 * Math.sin(c)) / D2R;
      return [((lo + 540) % 360) - 180, la / D2R, Math.cos(c)]; },
    R, cx, cy,
  };
}
const RAST = document.createElement('canvas');
function globeRaster(P, p, colors) {      // per-pixel classes from ETOPO; p = how far the oceans have moved (0..1)
  const N = 540, sc = 2 * P.R / N; RAST.width = N; RAST.height = N; const g = RAST.getContext('2d'), im = g.createImageData(N, N), d = im.data;
  for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) {
    const q = P.inv(P.cx - P.R + (x + .5) * sc, P.cy - P.R + (y + .5) * sc); const k = (y * N + x) * 4;
    if (!q) { d[k + 3] = 0; continue; }
    const [lo, la, mu] = q, z = zAt(la, lo), cl = Math.cos(la * D2R), S = p * (NOSPIN.C - NOSPIN.A * cl * cl);
    const cls = z < 0 ? (z < S ? 'sea' : 'bed') : (z < S ? 'flood' : 'land');
    let c = colors[cls]; const lit = .72 + .28 * mu;
    let rr = c[0] * lit, gg = c[1] * lit, bb = c[2] * lit;
    if (cls === 'sea' && colors.depth) { const dd = clamp((S - z) / 6000); rr *= 1 - .35 * dd; gg *= 1 - .35 * dd; bb *= 1 - .2 * dd; }
    if (cls === 'flood' && ((x + y) % 7 < 2)) { rr = lerp(rr, 220, .35); gg = lerp(gg, 235, .35); bb = lerp(bb, 250, .35); }
    d[k] = rr; d[k + 1] = gg; d[k + 2] = bb; d[k + 3] = 255;
  }
  g.putImageData(im, 0, 0);
  ctx.save(); ctx.beginPath(); ctx.arc(P.cx, P.cy, P.R, 0, TAU); ctx.clip(); ctx.imageSmoothingEnabled = true; ctx.drawImage(RAST, P.cx - P.R, P.cy - P.R, 2 * P.R, 2 * P.R); ctx.restore();
}
function coast(P, col, lw) {
  ctx.strokeStyle = col; ctx.lineWidth = lw; ctx.lineJoin = 'round'; ctx.beginPath();
  for (const ring of LAND) { let pen = false; for (const [lo, la] of ring) { const [x, y, c] = P.f(lo, la); if (c > 0) { pen ? ctx.lineTo(x, y) : ctx.moveTo(x, y); pen = true; } else pen = false; } }
  ctx.stroke();
}
function graticule(P, col) {
  ctx.strokeStyle = col; ctx.lineWidth = 1.2; ctx.beginPath();
  for (let la = -60; la <= 60; la += 30) { let pen = false; for (let lo = -180; lo <= 180; lo += 2) { const [x, y, c] = P.f(lo, la); if (c > 0) { pen ? ctx.lineTo(x, y) : ctx.moveTo(x, y); pen = true; } else pen = false; } }
  for (let lo = -180; lo < 180; lo += 30) { let pen = false; for (let la = -90; la <= 90; la += 2) { const [x, y, c] = P.f(lo, la); if (c > 0) { pen ? ctx.lineTo(x, y) : ctx.moveTo(x, y); pen = true; } else pen = false; } }
  ctx.stroke();
  ctx.strokeStyle = LINE; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(P.cx, P.cy, P.R, 0, TAU); ctx.stroke();
}
function latArrow(P, la, lo0, span, col, lw) {      // an eastward arrow drawn along a parallel; length ∝ cos(lat) (= the speed)
  const pts = []; for (let lo = lo0; lo <= lo0 + span; lo += 1) { const q = P.f(lo, la); if (q[2] > 0) pts.push(q); }
  if (pts.length < 2) return;
  ctx.strokeStyle = col; ctx.lineWidth = lw; ctx.lineCap = 'round'; ctx.beginPath(); pts.forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)); ctx.stroke();
  const [x1, y1] = pts[pts.length - 1], [x0, y0] = pts[pts.length - 2], a = Math.atan2(y1 - y0, x1 - x0);
  ctx.fillStyle = col; ctx.beginPath(); ctx.moveTo(x1 + Math.cos(a) * 14, y1 + Math.sin(a) * 14); ctx.lineTo(x1 + Math.cos(a + 2.5) * 22, y1 + Math.sin(a + 2.5) * 22); ctx.lineTo(x1 + Math.cos(a - 2.5) * 22, y1 + Math.sin(a - 2.5) * 22); ctx.closePath(); ctx.fill();
}

