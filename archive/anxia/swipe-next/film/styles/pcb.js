// Style 2 · 电路板世界 — the world behind the screen is a circuit board. Green solder mask, silver pads, white silkscreen;
// the phone is a chip, the blanket is a copper pour, the data centre is a processor die. The one accent: your signal,
// a gold pulse running along the copper (the only thing that glows).
'use strict';
const PB = { board: '#0B3627', board2: '#0E4231', pour: '#13543E', trace: '#1D6F52', traceHi: '#2A8A66', silk: '#E7EEE7', pad: '#C3C9C0', padD: '#7F877E', chip: '#121514', chipHi: '#2A302D', gold: '#FFC24A', goldL: '#FFE9B0', die: '#07120D' };
const BSANS = '"Noto Sans CJK SC"', BMONO = '"Noto Sans Mono CJK SC"';
function bpoly(pts) { ctx.beginPath(); pts.forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)); ctx.closePath(); }
function glow(on, b = 18) { if (on) { ctx.shadowColor = 'rgba(255,194,74,.9)'; ctx.shadowBlur = b; } else { ctx.shadowColor = 'transparent'; ctx.shadowBlur = 0; } }
// glass-fibre weave under the mask, one tile, used as a pattern that moves with the board
const WEAVE = (() => { const c = document.createElement('canvas'); c.width = c.height = 24; const g = c.getContext('2d'); g.fillStyle = PB.board; g.fillRect(0, 0, 24, 24); g.strokeStyle = 'rgba(255,255,255,.035)'; g.lineWidth = 3; for (let i = 0; i < 2; i++) { g.beginPath(); g.moveTo(0, 6 + i * 12); g.lineTo(24, 6 + i * 12); g.stroke(); g.beginPath(); g.moveTo(6 + i * 12, 0); g.lineTo(6 + i * 12, 24); g.stroke(); } return c; })();
let WEAVE_P = null;
function boardFill(z) {
  if (!WEAVE_P) WEAVE_P = ctx.createPattern(WEAVE, 'repeat');
  const o = P(0, 0, z), s = o[2] / 40; WEAVE_P.setTransform(new DOMMatrix([s, 0, 0, s, o[0], o[1]]));
  ctx.fillStyle = WEAVE_P; ctx.fillRect(0, 0, W, H);
}
// a seeded trace network on a plane: 45° routing, pads and vias at the ends
function makeTraces(seed, n, x0, x1, y0, y1, grid) {
  const r = mulberry32(seed), out = [];
  for (let i = 0; i < n; i++) {
    let x = Math.round(lerp(x0, x1, r()) / grid) * grid, y = Math.round(lerp(y0, y1, r()) / grid) * grid; const pts = [[x, y]];
    let dir = Math.floor(r() * 8); const m = 2 + Math.floor(r() * 4);
    for (let k = 0; k < m; k++) { const L = grid * (3 + Math.floor(r() * 8)), a = dir * Math.PI / 4, d = dir % 2 ? L / Math.SQRT2 : L; x += Math.round(Math.cos(a)) * d; y += Math.round(Math.sin(a)) * d; pts.push([x, y]); dir = (dir + (r() < .5 ? 1 : 7)) % 8; }
    out.push({ pts, w: r() < .3 ? .34 : .2, end: r() < .5 ? 'pad' : 'via', ph: r() });
  }
  return out;
}
function drawTraces(list, z, t, o = {}) {
  ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  for (const tr of list) {
    const q = tr.pts.map(([x, y]) => P(x, y, z)); if (q.some(v => !v)) continue; const s = q[0][2];
    const path = () => { ctx.beginPath(); q.forEach((v, i) => i ? ctx.lineTo(v[0], v[1]) : ctx.moveTo(v[0], v[1])); };
    if (o.clear) { path(); ctx.strokeStyle = o.clear; ctx.lineWidth = (tr.w + .3) * s; ctx.stroke(); }
    path(); ctx.strokeStyle = PB.trace; ctx.lineWidth = tr.w * s; ctx.stroke();
    for (const [i, v] of [[0, q[0]], [1, q[q.length - 1]]]) {
      if (tr.end === 'pad' || i === 0) { ctx.fillStyle = PB.pad; ctx.beginPath(); ctx.arc(v[0], v[1], tr.w * 1.6 * s, 0, TAU); ctx.fill(); ctx.fillStyle = PB.padD; ctx.beginPath(); ctx.arc(v[0], v[1], tr.w * .6 * s, 0, TAU); ctx.fill(); }
      else { ctx.strokeStyle = PB.traceHi; ctx.lineWidth = tr.w * .7 * s; ctx.beginPath(); ctx.arc(v[0], v[1], tr.w * 1.3 * s, 0, TAU); ctx.stroke(); ctx.fillStyle = '#04100A'; ctx.beginPath(); ctx.arc(v[0], v[1], tr.w * .8 * s, 0, TAU); ctx.fill(); }
    }
  }
}
function silk(txt, x, y, sz, o = {}) { ctx.font = `${o.w ?? 500} ${sz}px ${o.f ?? BMONO}`; ctx.fillStyle = o.c ?? PB.silk; ctx.globalAlpha = o.a ?? .85; ctx.textAlign = o.al ?? 'left'; ctx.textBaseline = 'middle'; ctx.fillText(txt, x, y); ctx.globalAlpha = 1; }

// ---------- S0 · the bed is a board
const BT0 = makeTraces(5, 110, -16, 16, -14, 14, .8).filter(tr => tr.pts.every(([x, y]) => y < 10.2 && y > -12)).slice(0, 44);
const BT1 = makeTraces(9, 7, -15, 15, -26, -15, .8);
const BOARD_Z = 6;
const POUR = (() => { const pts = []; let y = -11; for (let x = -18; x <= 18; x += 1.6) { pts.push([x, y]); const s = Math.sin(x * .35) > 0 ? 1 : -1; y += (Math.abs(x) % 4.8 < 1.6 ? s * 1.6 : 0); } pts.push([18, -40], [-18, -40]); return pts; })();
const PILLOW = [[-18, -3], [-9.6, -3], [-8, -4.6], [-8, -9.4], [-9.6, -11], [-18, -11]];
function bedroom(t) {
  boardFill(BOARD_Z);
  drawTraces(BT0, BOARD_Z, t, { clear: PB.board });
  // the blanket and the pillow: copper pours with clearance, laid over the routing
  for (const [pts, col] of [[PILLOW, '#17604A'], [POUR, '#1B694F']]) {
    const q = pts.map(([x, y]) => P(x, y, BOARD_Z)); if (q.some(v => !v)) continue; const s = q[0][2];
    bpoly(q); ctx.fillStyle = col; ctx.fill(); ctx.strokeStyle = '#3FA57E'; ctx.globalAlpha = .9; ctx.lineWidth = .16 * s; ctx.stroke(); ctx.globalAlpha = 1;
    ctx.save(); bpoly(q); ctx.clip(); ctx.strokeStyle = 'rgba(255,255,255,.04)'; ctx.lineWidth = .1 * s; for (let k = -40; k < 40; k += .8) { const a = P(k, -40, BOARD_Z), b = P(k + 40, 0, BOARD_Z); ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.stroke(); } ctx.restore();
  }
  drawTraces(BT1, BOARD_Z, t, { clear: '#1B694F' });
  // silkscreen on the board
  const a = P(-9.6, -13.6, BOARD_Z), b = P(-15.5, -5, BOARD_Z), c = P(8.6, 9.2, BOARD_Z);
  if (a) silk('J1  被窝', a[0], a[1], Math.round(.75 * a[2]));
  if (b) silk('J2  枕头', b[0], b[1], Math.round(.6 * b[2]), { a: .6 });
  if (c) silk('22:47', c[0], c[1], Math.round(.7 * c[2]), { a: .6 });
  // a slow pulse on one trace: the board is alive (idle copper, not the signal)
  const tr = BT0[(Math.floor(t / 1.6)) % BT0.length], k = (t / 1.6) % 1; const q0 = tr.pts[0], q1 = tr.pts[1]; const p = P(lerp(q0[0], q1[0], k), lerp(q0[1], q1[1], k), BOARD_Z);
  if (p) { ctx.fillStyle = 'rgba(160,230,200,.35)'; ctx.beginPath(); ctx.arc(p[0], p[1], .3 * p[2], 0, TAU); ctx.fill(); }
}
function phoneAt(t, o = {}) {
  card(0, 0, 0, PHONE.w, PHONE.h, (w, h) => {
    // footprint silkscreen, pin-1 dot, designator
    ctx.strokeStyle = PB.silk; ctx.globalAlpha = .8; ctx.lineWidth = .07; ctx.strokeRect(-1.0, -.6, w + 2.0, h + 1.2); ctx.fillStyle = PB.silk; ctx.beginPath(); ctx.arc(-.55, -.15, .16, 0, TAU); ctx.fill(); ctx.globalAlpha = 1;
    ctx.font = `500 .62px ${BMONO}`; ctx.fillStyle = PB.silk; ctx.textBaseline = 'top'; ctx.textAlign = 'left'; ctx.fillText('U1  手机', -1.0, h + .85);
    // gull-wing pins on both sides
    for (let i = 0; i < 16; i++) { const y = 1.0 + i * (h - 2.0) / 15; ctx.fillStyle = PB.pad; ctx.fillRect(-.75, y - .14, .8, .28); ctx.fillRect(w - .05, y - .14, .8, .28); ctx.fillStyle = 'rgba(0,0,0,.35)'; ctx.fillRect(-.75, y + .06, .8, .08); ctx.fillRect(w - .05, y + .06, .8, .08); }
    ctx.fillStyle = 'rgba(0,0,0,.45)'; rr(.25, .35, w, h, .55); ctx.fill();
    ctx.fillStyle = PB.chip; rr(0, 0, w, h, .55); ctx.fill(); ctx.strokeStyle = PB.chipHi; ctx.lineWidth = .08; rr(.1, .1, w - .2, h - .2, .5); ctx.stroke();
  });
  card(0, 0, -.01, SCREEN.w, SCREEN.h, (w, h) => {
    ctx.save(); rr(0, 0, w, h, .5); ctx.clip(); ctx.scale(1 / 100, 1 / 100); catGag(w * 100, h * 100, t);
    const prog = o.prog ?? ((t * .09) % 1); chrome(w * 100, h * 100, t, 0);
    ctx.fillStyle = 'rgba(255,255,255,.25)'; ctx.fillRect(0, h * 100 - 12, w * 100, 12); glow(true, 14); ctx.fillStyle = PB.gold; ctx.fillRect(0, h * 100 - 12, w * 100 * prog, 12); glow(false);
    ctx.restore();
  });
}
// hand: unchanged from the night look (the one real thing in front of the board)

STY.title = t => {
  ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic';
  ctx.font = `900 112px ${BSANS}`; ctx.lineJoin = 'round'; ctx.lineWidth = 16; ctx.strokeStyle = PB.board; ctx.strokeText('你上划之前', 72, 230); ctx.fillStyle = PB.silk; ctx.fillText('你上划之前', 72, 230);
  ctx.font = `500 34px ${BMONO}`; ctx.fillStyle = PB.silk; ctx.globalAlpha = .7; ctx.fillText('▲ 你按下去之后 · REV 04', 76, 300); ctx.globalAlpha = 1;
};
STY.hero = (t, t0, lines, x, y) => {
  ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic';
  lines.forEach((ln, i) => {
    const { k, show } = heroK(t, t0, i); if (k <= 0) return; const sz = ln.size ?? 120, yy = y - (1 - k) * 36;
    const nC = ln.parts.reduce((a, p) => a + [...p[0]].length, 0), n = show(nC); let cx = x, used = 0;
    for (const [s, role] of ln.parts) {
      ctx.font = `900 ${sz}px ${BSANS}`; const vis = [...s].slice(0, Math.max(0, n - used)).join(''); used += [...s].length;
      ctx.lineJoin = 'round'; ctx.lineWidth = sz * .16; ctx.strokeStyle = 'rgba(4,16,11,.92)'; ctx.strokeText(vis, cx, yy);
      ctx.fillStyle = role === 'a' ? PB.gold : PB.silk; ctx.fillText(vis, cx, yy); cx += ctx.measureText(s).width;
    }
    // a silkscreen reference line under the hero, like a net label
    ctx.strokeStyle = PB.silk; ctx.globalAlpha = .5; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(x, yy + 30); ctx.lineTo(x + (cx - x) * k, yy + 30); ctx.lineTo(x + (cx - x) * k + 22, yy + 52); ctx.stroke(); ctx.globalAlpha = 1;
  });
};
STY.sub = txt => { ctx.font = `700 52px ${BSANS}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.lineJoin = 'round'; ctx.lineWidth = 14; ctx.strokeStyle = '#04100B'; ctx.strokeText(txt, W / 2, 1640); ctx.fillStyle = PB.silk; ctx.fillText(txt, W / 2, 1640); };

// ---------- the data centre is a processor: the wall of videos = the die's cells; the funnel = a bus of copper
const MUTE = THEMES.map(([a]) => { const n = parseInt(a.slice(1), 16), r = n >> 16, g = (n >> 8) & 255, b = n & 255; const m = (v, w) => Math.round(v * .38 + w * .62); return `rgb(${m(r, 16)},${m(g, 52)},${m(b, 40)})`; });
STY.wallBg = t => { ctx.fillStyle = PB.die; ctx.fillRect(0, 0, W, H); };
STY.wallCard = (x, y, w, h, idx, t) => {
  ctx.fillStyle = MUTE[idx % MUTE.length]; ctx.fillRect(x, y, w, h);
  ctx.strokeStyle = 'rgba(160,220,190,.18)'; ctx.lineWidth = Math.max(1, w * .03); ctx.strokeRect(x - w * .08, y - w * .08, w * 1.16, h + w * .16);      // metal ring between cells
  if (w > 20) { ctx.fillStyle = 'rgba(200,240,220,.35)'; const k = THEMES[idx % THEMES.length][2]; const cx = x + w / 2, cy = y + h * .45, r = w * .2; ctx.beginPath(); if (k === 'ball' || k === 'cat') ctx.arc(cx, cy, r, 0, TAU); else ctx.rect(cx - r, cy - r * .6, r * 2, r * 1.2); ctx.fill(); }
  const on = hash(idx, Math.floor(t * 3 + hash(idx, 2) * 3)) > .6; ctx.fillStyle = on ? 'rgba(170,240,210,.9)' : 'rgba(60,90,80,.8)'; ctx.fillRect(x + w * .1, y + h * .08, Math.max(2, w * .1), Math.max(2, w * .1));      // a status LED per cell
};
// the bus: one trace per column of the funnel mouth, routed at 45°
const NBUS = 18, LANE = .42;
function busPath(i) {
  const x0 = lerp(-FUN.wTop + .6, FUN.wTop - .6, (i + .5) / NBUS), lane = (i - (NBUS - 1) / 2) * LANE * (FUN.wMouth * 2 / (LANE * NBUS)), y1 = FUN.yTop - .6, dx = lane - x0, y2 = y1 - Math.abs(dx);
  return [[x0, FUN.yTop + 1.2], [x0, y1], [lane, y2], [lane, FUN.yMouth - 4]];
}
function along(pts, u) { const L = []; let T = 0; for (let i = 1; i < pts.length; i++) { const l = Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]); L.push(l); T += l; } let d = u * T; for (let i = 0; i < L.length; i++) { if (d <= L[i]) { const k = d / L[i]; return [lerp(pts[i][0], pts[i + 1][0], k), lerp(pts[i][1], pts[i + 1][1], k)]; } d -= L[i]; } return pts[pts.length - 1]; }
STY.funnelBack = (q, k, t) => {
  const z = FUN.z - .3; ctx.save(); ctx.globalAlpha = k; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  // the funnel region is routed board on top of the die
  const env = [P(-FUN.wTop - 1.2, FUN.yTop + 2.4, z), P(FUN.wTop + 1.2, FUN.yTop + 2.4, z), P(FUN.wMouth + 1.2, FUN.yTop - FUN.wTop - .4, z), P(FUN.wMouth + 1.2, FUN.yMouth - 5, z), P(-FUN.wMouth - 1.2, FUN.yMouth - 5, z), P(-FUN.wMouth - 1.2, FUN.yTop - FUN.wTop - .4, z)];
  if (env.every(Boolean)) { ctx.fillStyle = 'rgba(11,54,39,.94)'; bpoly(env); ctx.fill(); ctx.strokeStyle = PB.silk; ctx.globalAlpha = .55 * k; ctx.lineWidth = 3; ctx.stroke(); ctx.globalAlpha = k; }
  for (let i = 0; i < NBUS; i++) {
    const pts = busPath(i).map(([x, y]) => P(x, y, z)); if (pts.some(v => !v)) continue; const s = pts[0][2];
    ctx.beginPath(); pts.forEach((v, j) => j ? ctx.lineTo(v[0], v[1]) : ctx.moveTo(v[0], v[1])); ctx.strokeStyle = PB.traceHi; ctx.lineWidth = .3 * s; ctx.stroke();
    ctx.fillStyle = PB.pad; ctx.beginPath(); ctx.arc(pts[0][0], pts[0][1], .42 * s, 0, TAU); ctx.fill(); ctx.fillStyle = PB.padD; ctx.beginPath(); ctx.arc(pts[0][0], pts[0][1], .16 * s, 0, TAU); ctx.fill();
  }
  // silkscreen on the bus
  const lb = P(FUN.wMouth + 2, FUN.yMouth + 3, z); if (lb) silk('BUS[17:0]  召回', lb[0], lb[1], Math.round(.75 * lb[2]), { a: .7 * k });
  const lt = P(-FUN.wTop - .6, FUN.yTop + 3.4, z); if (lt) silk('U7  候选池 · 海量', lt[0], lt[1], Math.round(.75 * lt[2]), { a: .7 * k });
  ctx.restore();
};
STY.streamCard = null;      // on the board, what flows down the funnel is pulses, not cards
STY.funnelFront = (q, k, t) => {
  const z = FUN.z - .35; ctx.save(); ctx.globalAlpha = k; ctx.lineCap = 'round';
  for (let i = 0; i < NBUS; i++) {
    const path = busPath(i);
    for (let m = 0; m < 2; m++) {
      const u = ((t * .42 + hash(i, 61) + m * .5) % 1), a = along(path, u), b = along(path, Math.max(0, u - .06));
      const pa = P(a[0], a[1], z), pb = P(b[0], b[1], z); if (!pa || !pb) continue;
      glow(true, 16); ctx.strokeStyle = PB.gold; ctx.lineWidth = .34 * pa[2]; ctx.beginPath(); ctx.moveTo(pb[0], pb[1]); ctx.lineTo(pa[0], pa[1]); ctx.stroke(); glow(false);
      ctx.fillStyle = PB.goldL; ctx.beginPath(); ctx.arc(pa[0], pa[1], .2 * pa[2], 0, TAU); ctx.fill();
    }
  }
  ctx.restore();
};
STY.dim = (t, k) => { ctx.fillStyle = `rgba(3,10,7,${.62 * k})`; ctx.fillRect(0, 0, W, H); };
// the batch: each candidate is a chip; its four odds are LED bar graphs
STY.batchCard = (W1, H1, k, odds, t, back, i) => {
  // pins
  for (let j = 0; j < 10; j++) { const y = 70 + j * (H1 - 140) / 9; ctx.fillStyle = PB.pad; ctx.fillRect(-30, y - 9, 36, 18); ctx.fillRect(W1 - 6, y - 9, 36, 18); }
  ctx.fillStyle = 'rgba(0,0,0,.5)'; rr(14, 18, W1, H1, 18); ctx.fill();
  ctx.fillStyle = PB.chip; rr(0, 0, W1, H1, 18); ctx.fill(); ctx.strokeStyle = PB.chipHi; ctx.lineWidth = 5; rr(8, 8, W1 - 16, H1 - 16, 14); ctx.stroke();
  ctx.fillStyle = '#060807'; ctx.beginPath(); ctx.arc(40, 40, 12, 0, TAU); ctx.fill();      // pin-1 dimple
  // the candidate video, behind a window in the package
  ctx.save(); ctx.translate(34, 66); ctx.beginPath(); ctx.rect(0, 0, W1 - 68, H1 * .33); ctx.clip(); thumb(W1 - 68, H1 * .33 + 30, k); ctx.restore();
  ctx.strokeStyle = PB.pad; ctx.lineWidth = 4; ctx.strokeRect(34, 66, W1 - 68, H1 * .33);
  ctx.font = `500 28px ${BMONO}`; ctx.fillStyle = '#7E8782'; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.fillText(`候选 #${2041 + k * 317}`, 36, H1 * .33 + 100);
  if (!back) oddsRows(t, odds).forEach((r, j) => {
    if (!r.on) return; const y0 = H1 * .56 + j * 76, bx = 104, bw = W1 - 214, n = 10, gap = 6, sw = (bw - gap * (n - 1)) / n, lit = r.v * 10 * r.k;
    ctx.font = `500 36px ${BMONO}`; ctx.fillStyle = PB.silk; ctx.textAlign = 'left'; ctx.fillText(r.lab, 24, y0);
    for (let s = 0; s < n; s++) { const f = clamp(lit - s); ctx.fillStyle = '#26302C'; ctx.fillRect(bx + s * (sw + gap), y0 - 14, sw, 28); if (f > 0) { glow(true, 12); ctx.globalAlpha = .35 + .65 * f; ctx.fillStyle = PB.gold; ctx.fillRect(bx + s * (sw + gap), y0 - 14, sw, 28); ctx.globalAlpha = 1; glow(false); } }
    if (lit < .5) { glow(true, 10); ctx.fillStyle = PB.gold; ctx.fillRect(bx, y0 - 14, 4, 28); glow(false); }
    ctx.font = `700 40px ${BMONO}`; ctx.textAlign = 'right'; ctx.fillStyle = PB.silk; ctx.fillText(r.txt, W1 - 16, y0 + 1);
  });
  if (back) { ctx.fillStyle = 'rgba(3,10,7,.35)'; ctx.fillRect(-40, -10, W1 + 80, H1 + 20); }
};
window.ready = Promise.all([`900 84px ${BSANS}`, `700 54px ${BSANS}`, `500 40px ${BMONO}`, `700 40px ${BMONO}`].map(f => document.fonts.load(f)));
