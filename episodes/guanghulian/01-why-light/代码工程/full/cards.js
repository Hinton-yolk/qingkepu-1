// 黑卡片上的机制动画（3b1b 式：一次只动一样东西；米白＝电，青绿＝光，红＝编辑的笔）。坐标原点在卡片中心，时间点全部来自 desk.json 的 cue。
(() => {
const { clamp, lerp } = U; const { COL, txt, seg, S12, D } = FULL;
const BITS = [1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1];
const bitOf = k => (k < 0 ? 0 : BITS[k % BITS.length]);
const Phi = x => 1 / (1 + Math.exp(-1.702 * x));
// 方波电平（带模糊）：F = 第 0 位的前沿，第 k 位占 [F-(k+1)bw, F-k bw]
const level = (x, F, bw, sg) => { let y = 0; const kLo = Math.max(0, Math.floor((F - x - 4 * sg) / bw) - 1), kHi = Math.ceil((F - x + 4 * sg) / bw) + 1;
  for (let k = kLo; k <= kHi; k++) if (bitOf(k)) y += Phi((F - k * bw - x) / sg) - Phi((F - (k + 1) * bw - x) / sg); return y; };
const sqAt = (x, F, bw) => (F - x < 0 ? 0 : bitOf(Math.floor((F - x) / bw)));
const stroke = (c, x0, x1, fy, { col = COL.cream, lw = 6, step = 2, alpha = 1 } = {}) => { if (x1 <= x0) return; c.save(); c.globalAlpha *= alpha; c.beginPath();
  for (let x = x0; x <= x1 + 1e-6; x += step) { const y = fy(Math.min(x, x1)); x === x0 ? c.moveTo(x, y) : c.lineTo(x, y); } c.strokeStyle = col; c.lineWidth = lw; c.lineJoin = 'round'; c.stroke(); c.restore(); };
const digit = (c, s, x, y, col = COL.cream, size = 44) => txt(c, s, x, y, { size, fam: 'PuHui-Heavy', col, align: 'center' });
const rbox = (c, x, y, w, h, { fill = '#2c2c2a', line = 'rgba(236,230,218,.7)', lw = 3, r = 16 } = {}) => { c.beginPath(); c.roundRect(x - w / 2, y - h / 2, w, h, r); c.fillStyle = fill; c.fill(); c.strokeStyle = line; c.lineWidth = lw; c.stroke(); };
const pulses = (c, F, bw, xa, xb, y, { h = 24, gap = 5, col = COL.tealHi, glow = true, alpha = 1 } = {}) => { c.save(); c.globalAlpha *= alpha; if (glow) { c.shadowColor = COL.teal; c.shadowBlur = 20; } c.fillStyle = col;
  const kLo = Math.max(0, Math.floor((F - xb) / bw) - 1), kHi = Math.floor((F - xa) / bw) + 1;
  for (let k = kLo; k <= kHi; k++) { if (!bitOf(k)) continue; const a0 = Math.max(xa, F - (k + 1) * bw + gap), a1 = Math.min(xb, F - k * bw - gap); if (a1 - a0 > 10) { c.beginPath(); c.roundRect(a0, y - h / 2, a1 - a0, h, h / 2); c.fill(); } }
  c.restore(); };
const bitTile = (c, b, x, y, { s = 52, col = COL.cream, ring = false, fill = '#2c2c2a' } = {}) => { c.save(); c.beginPath(); c.roundRect(x - s / 2, y - s / 2, s, s, 10); c.fillStyle = fill; c.fill(); c.lineWidth = 3; c.strokeStyle = col; c.stroke();
  digit(c, String(b), x, y + 2, col, s * 0.72); if (ring) { c.strokeStyle = COL.redHi; c.lineWidth = 5; c.beginPath(); c.arc(x, y, s * 0.82, 0, 7); c.stroke(); } c.restore(); };
const axis = (c, x0, x1, y, a) => { if (a <= 0) return; c.save(); c.globalAlpha *= a; c.strokeStyle = COL.creamDim; c.fillStyle = COL.creamDim; c.lineWidth = 3; c.beginPath(); c.moveTo(x0, y); c.lineTo(x1, y); c.stroke();
  c.beginPath(); c.moveTo(x1 + 22, y); c.lineTo(x1, y - 12); c.lineTo(x1, y + 12); c.closePath(); c.fill(); txt(c, '出发', x0, y + 40, { size: 34, col: COL.creamDim }); txt(c, '跑得越远', x1 + 20, y + 40, { size: 34, col: COL.creamDim, align: 'right' }); c.restore(); };
const bracket = (c, x0, x1, y, col) => { c.save(); c.strokeStyle = col; c.lineWidth = 5; c.lineCap = 'round'; c.beginPath(); c.moveTo(x0, y - 18); c.lineTo(x0, y); c.lineTo(x1, y); c.lineTo(x1, y - 18); c.stroke(); c.restore(); };
const tint = (c, x0, y0, x1, y1, col) => { c.save(); c.fillStyle = col; c.beginPath(); c.roundRect(x0, y0, x1 - x0, y1 - y0, 18); c.fill(); c.restore(); };
const note = (c, y) => txt(c, '颜色仅为示意', -420, y, { size: 26, col: 'rgba(236,230,218,.4)' });

// ---------- 开场：成千上万颗 GPU，每算一步都要交换结果 ----------
FULL.CARD.gpu = (c, t, id, cd, cue) => {
  const X = cue.x, cols = 7, rows = 5, gx = i => -330 + 110 * i, gy = j => -270 + 110 * j;
  const last = X.filter(x => x <= t).pop();
  for (const x0 of X) { const q = t - x0; if (q < 0 || q > 0.55) continue; const m = MO.cubicInOut(clamp(q / 0.45)), a = Math.sin(Math.PI * clamp(q / 0.55));
    c.save(); c.globalAlpha = a; c.fillStyle = COL.cream;
    for (let i = 0; i < cols; i++) for (let j = 0; j < rows; j++) {
      if (i < cols - 1) { c.fillRect(lerp(gx(i) + 40, gx(i + 1) - 40, m) - 7, gy(j) - 13, 14, 9); c.fillRect(lerp(gx(i + 1) - 40, gx(i) + 40, m) - 7, gy(j) + 4, 14, 9); }
      if (j < rows - 1) { c.fillRect(gx(i) - 13, lerp(gy(j) + 40, gy(j + 1) - 40, m) - 7, 9, 14); c.fillRect(gx(i) + 4, lerp(gy(j + 1) - 40, gy(j) + 40, m) - 7, 9, 14); } }
    c.restore(); }
  for (let i = 0; i < cols; i++) for (let j = 0; j < rows; j++) { const r = U.rng(i * 7 + j * 13 + 3)();
    const h = last == null ? seg(t, X[0] - 0.9 + 0.4 * r, X[0] - 0.2 + 0.15 * r) : seg(t, last + 0.5, last + 0.85 + 0.25 * r);
    rbox(c, gx(i), gy(j), 78, 78, { r: 10, line: 'rgba(236,230,218,.55)' });
    c.fillStyle = 'rgba(236,230,218,.62)'; c.fillRect(gx(i) - 26, gy(j) + 28 - 52 * h, 52, 52 * h);
    txt(c, 'GPU', gx(i), gy(j) - 22, { size: 15, fam: 'PuHui-Heavy', col: 'rgba(236,230,218,.6)', align: 'center' }); }
};

// ---------- ① 出发：一大排 → 一列 → 高速电信号（SerDes） ----------
FULL.CARD.serdes = (c, t, id, cd, cue) => {
  const go = cue.go, dt = 0.143, N = 24, bw = 60, v = bw / dt, HOLE = -380, WY = -150, OY = 200, BY = 330, HI = 268;
  const cell = k => [-120 + 70 * (k % 8), -360 + 70 * Math.floor(k / 8)], rel = k => go + k * dt;
  // 墙和出口
  c.save(); c.strokeStyle = COL.cream; c.lineWidth = 6; c.lineCap = 'round'; c.beginPath(); c.moveTo(-430, WY); c.lineTo(HOLE - 34, WY); c.moveTo(HOLE + 34, WY); c.lineTo(430, WY); c.stroke(); c.restore();
  // 输出的方波（各位按顺序排成一列以后）
  const F = HOLE + v * (t - go - 0.15);
  if (F > HOLE - 30) { const xb = Math.min(430, F + bw / 2);
    stroke(c, HOLE - 30, xb, x => { const k = Math.round((F - x) / bw); return k >= 0 && k < N && bitOf(k) ? HI : BY; }, { lw: 6, step: 1 }); }
  for (let k = 0; k < N; k++) { const r = rel(k), b = bitOf(k), hero = k === 5; let p, tile = true;
    if (t < r - 0.45) p = cell(k);
    else if (t < r) { const e = MO.cubicInOut(seg(t, r - 0.45, r)), a = cell(k); p = [lerp(a[0], HOLE, e), lerp(a[1], WY - 50, e) - Math.sin(Math.PI * e) * 30]; }
    else if (t < r + 0.15) { const e = seg(t, r, r + 0.15); p = [HOLE, lerp(WY - 50, OY, e)]; }
    else { p = [HOLE + v * (t - r - 0.15), OY]; tile = false; if (p[0] > 430) continue; }
    if (tile) bitTile(c, b, p[0], p[1], { ring: hero }); else { digit(c, String(b), p[0], p[1]); if (hero) { c.save(); c.strokeStyle = COL.redHi; c.lineWidth = 5; c.beginPath(); c.arc(p[0], p[1], 34, 0, 7); c.stroke(); c.restore(); } }
  }
};

// ---------- ② 电的路：跑得越远越糊（清楚的一段、糊掉的一段分别标出来） ----------
FULL.CARD.blur = (c, t, id, cd, cue) => {
  const x0 = -380, x1 = 400, yb = 20, A = 90, bw = 64, v = 320, L = x1 - x0, e0 = cue.e0;
  const sg = x => 2 + 60 * Math.pow(clamp((x - x0) / L), 1.6), am = x => 1 - 0.32 * clamp((x - x0) / L);
  const lz = D.cardLabels[id], tA = lz[0].at, tB = lz[1].at;
  if (S12(t) >= tA) tint(c, x0 - 20, yb - A - 100, x0 + 0.34 * L, yb + 30, 'rgba(236,230,218,.07)');
  if (S12(t) >= tB) tint(c, x0 + 0.56 * L, yb - A - 100, x1 + 20, yb + 30, 'rgba(217,96,79,.13)');
  txt(c, '电信号', x0, -300, { size: 40, fam: 'PuHui-Heavy' });
  c.save(); c.setLineDash([4, 10]); c.strokeStyle = COL.creamDim; c.lineWidth = 3; c.beginPath(); c.moveTo(x0, yb); c.lineTo(x1, yb); c.stroke(); c.restore();
  const F = x0 + v * (t - e0);
  if (t > e0) { stroke(c, x0, Math.min(x1, F + 4 * sg(Math.min(F, x1))), x => yb - A * am(x) * level(x, F, bw, sg(x)));
    for (let k = 0; k < 40; k++) { const xc = F - (k + 0.5) * bw; if (xc < x0 + 10 || xc > x1 - 4) continue; const s = sg(xc); c.save();
      if (s < 26) { c.globalAlpha = clamp(1 - (s - 14) / 14); digit(c, String(bitOf(k)), xc, yb - A - 44, COL.cream, 46); }
      else { c.translate(xc, yb - A - 44); c.rotate(Math.sin(t * 9 + k * 2.1) * 0.12); digit(c, '?', 0, 0, COL.redHi, 50); }
      c.restore(); } }
  if (S12(t) >= tA) bracket(c, x0, x0 + 0.32 * L, yb + 110, COL.cream);
  if (S12(t) >= tB) bracket(c, x0 + 0.58 * L, x1, yb + 110, COL.redHi);
  axis(c, x0, x1, 330, MO.smooth(seg(t, e0, e0 + 0.5)));
};

// ---------- ② DSP：糊的进站，清楚的出站，每整理一组耗一格电 ----------
FULL.CARD.dsp = (c, t, id, cd, cue) => {
  const y = -60, A = 70, bw = 56, v = 260, t0 = cue.t0, G = cue.groups;
  const Fi = -430 + v * (t - t0 + 2.2), Fo = 130 + v * (t - t0 - 0.4);
  stroke(c, -430, -128, x => y - A * 0.62 * level(x, Fi, bw, 30));
  for (let k = 0; k < 40; k++) { const xc = Fi - (k + 0.5) * bw; if (xc < -410 || xc > -150) continue; c.save(); c.translate(xc, y - A - 40); c.rotate(Math.sin(t * 9 + k * 2.1) * 0.12); digit(c, '?', 0, 0, COL.redHi, 46); c.restore(); }
  if (Fo > 130) { stroke(c, 128, Math.min(430, Fo), x => y - A * level(x, Fo, bw, 2));
    for (let k = 0; k < 40; k++) { const xc = Fo - (k + 0.5) * bw; if (xc < 150 || xc > 420) continue; digit(c, String(bitOf(k)), xc, y - A - 40, COL.cream, 46); } }
  const fl = G.reduce((m, g) => Math.max(m, t >= g ? Math.exp(-(t - g) * 7) : 0), 0);
  rbox(c, 0, -80, 250, 230, { line: fl > 0.05 ? `rgba(217,96,79,${0.5 + 0.5 * fl})` : 'rgba(236,230,218,.75)', lw: 4 + 4 * fl });
  txt(c, 'DSP', 0, -112, { size: 74, fam: 'PuHui-Heavy', align: 'center' }); txt(c, '检修站', 0, -38, { size: 34, col: 'rgba(236,230,218,.7)', align: 'center' });
  // 电池：5 格，每整理一组少一格
  const used = G.filter(g => S12(t) >= g).length, bx = -150, by = 190, bwid = 300, bh = 100;
  c.save(); c.strokeStyle = COL.cream; c.lineWidth = 5; c.beginPath(); c.roundRect(bx, by - bh / 2, bwid, bh, 12); c.stroke(); c.fillStyle = COL.cream; c.fillRect(bx + bwid, by - 18, 14, 36);
  for (let i = 0; i < 5; i++) { const gone = i >= 5 - used, flash = i === 5 - used && used < 5 && G.some(g => S12(t) >= g - 1 / 12 && S12(t) < g);
    if (gone) continue; c.fillStyle = flash ? COL.redHi : (5 - used <= 2 ? COL.redHi : COL.cream); c.fillRect(bx + 12 + i * 56, by - bh / 2 + 12, 46, bh - 24); }
  c.restore();
};

// ---------- ② 速度越高，能可靠跑的路越短 ----------
FULL.CARD.reach = (c, t, id, cd, cue) => {
  const x0 = -400, x1 = 410, v = 900;
  [{ y: -140, bw: 72, at: cue.slow, reach: 250 }, { y: 100, bw: 30, at: cue.fast, reach: -150 }].forEach(R => { if (t < R.at) return;
    const F = x0 + v * (t - R.at), sg = x => x < R.reach ? 2 : 2 + (x - R.reach) * 0.35;
    stroke(c, x0, Math.min(x1, F), x => R.y - 46 * level(x, F, R.bw, sg(x)) * (x < R.reach ? 1 : Math.max(0.45, 1 - (x - R.reach) / 300)), { lw: 5, step: 1.5 });
    const e = Math.min(F, R.reach); if (e > x0 + 10) bracket(c, x0, e, R.y + 48, COL.cream);
    if (F > R.reach + 60) for (let x = R.reach + 50; x < Math.min(x1, F) - 10; x += 70) { c.save(); c.translate(x, R.y - 80); c.rotate(Math.sin(t * 9 + x) * 0.12); digit(c, '?', 0, 0, COL.redHi, 40); c.restore(); } });
};

// ---------- ③ 换乘：激光器、调制器、驱动器；比特从电换到光上 ----------
FULL.CARD.transfer = (c, t, id, cd, cue) => {
  const LY = -320, v = 300, bw = 60, MX = 90, DY = 140, mod = cue.mod, drv = cue.drv, [h0, h1] = cue.hero;
  const on = t >= cue.laser, lit = MO.smooth(seg(t, cue.laser, cue.laser + 0.3));
  const ms = t < mod ? 1 : bitOf(Math.floor((t - mod) * v / bw));
  // 激光器 → 调制器的光
  if (on) { c.save(); c.shadowColor = COL.teal; c.shadowBlur = 24; c.strokeStyle = COL.tealHi; c.globalAlpha = lit; c.lineWidth = 16; c.lineCap = 'round'; c.beginPath(); c.moveTo(-205, LY); c.lineTo(lerp(-205, MX - 90, clamp((t - cue.laser) / 0.3)), LY); c.stroke(); c.restore(); }
  // 调制器之后：开始调制以前是一束常亮的光，之后一明一暗
  if (on && t >= cue.laser + 0.3) {
    if (t < mod) { const fr = Math.min(450, MX + 90 + (t - cue.laser - 0.3) * 900); c.save(); c.shadowColor = COL.teal; c.shadowBlur = 24; c.strokeStyle = COL.tealHi; c.lineWidth = 16; c.lineCap = 'round'; c.beginPath(); c.moveTo(MX + 90, LY); c.lineTo(fr, LY); c.stroke(); c.restore(); }
    else { const F = MX + 90 + v * (t - mod); const tail = MX + 90 + v * (t - mod) - (450 - MX - 90);
      if (t - mod < (450 - MX - 90) / v) { c.save(); c.shadowColor = COL.teal; c.shadowBlur = 24; c.strokeStyle = COL.tealHi; c.lineWidth = 16; c.lineCap = 'round'; c.beginPath(); c.moveTo(Math.max(MX + 90, F), LY); c.lineTo(450, LY); c.stroke(); c.restore(); }
      pulses(c, F, bw, MX + 90, 450, LY, { h: 26 });
      const la = seg(t, mod + 0.3, mod + 0.6) * (1 - seg(t, drv - 0.2, drv));
      if (la > 0) { c.save(); c.globalAlpha = la; for (let k = 0; k < 10; k++) { const xc = F - (k + 0.5) * bw; if (xc < MX + 110 || xc > 430) continue; txt(c, bitOf(k) ? '1亮' : '0暗', xc, LY - 52, { size: 30, fam: 'PuHui-Heavy', col: bitOf(k) ? COL.tealHi : 'rgba(155,232,219,.5)', align: 'center' }); } c.restore(); } } }
  rbox(c, -300, LY, 190, 130); txt(c, '激光器', -300, LY, { size: 38, fam: 'PuHui-Heavy', align: 'center' });
  rbox(c, MX, LY + 10, 180, 190); c.fillStyle = '#111'; c.fillRect(MX - 26, LY - 50, 52, 100);
  if (on) { c.save(); if (ms) { c.shadowColor = COL.teal; c.shadowBlur = 26; c.fillStyle = COL.tealHi; } else c.fillStyle = '#245c55'; c.globalAlpha = lit; c.fillRect(MX - 20, LY - 44, 40, 88); c.restore(); }
  txt(c, '调制器', MX, LY + 78, { size: 30, fam: 'PuHui-Heavy', align: 'center', col: 'rgba(236,230,218,.8)' });
  // 驱动器：进来细、弱；出去粗、强（推动调制器）
  if (t >= mod) { const Fin = -10 + v * (t - mod); stroke(c, -450, -12, x => DY - 14 * sqAt(x, Fin, bw), { lw: 2.5, step: 1, alpha: 0.75 }); }
  const dh = seg(t, drv, drv + 0.3), cur = t >= mod ? ms : 0;
  c.save(); c.strokeStyle = cur ? COL.cream : 'rgba(236,230,218,.25)'; c.lineWidth = lerp(5, cur ? 16 : 6, Math.max(dh, t >= mod ? 0.4 : 0)); if (cur && dh > 0) { c.shadowColor = COL.cream; c.shadowBlur = 14 * dh; }
  c.beginPath(); c.moveTo(MX, DY - 62); c.lineTo(MX, LY + 106); c.stroke(); c.restore();
  rbox(c, MX, DY, 200, 120, { line: dh > 0 ? COL.cream : 'rgba(236,230,218,.7)', lw: 3 + 2 * dh }); txt(c, '驱动器', MX, DY, { size: 38, fam: 'PuHui-Heavy', align: 'center' });
  // 那个比特：走线 → 驱动器 → 调制器（一闪）→ 骑着光出去
  if (t >= h0 && t < h1 + 1.4) { let p, teal = false;
    if (t < h0 + 0.45) p = [lerp(-450, MX - 100, MO.sineInOut(seg(t, h0, h0 + 0.45))), DY];
    else if (t < h1 - 0.2) { const e = MO.sineInOut(seg(t, h0 + 0.45, h1 - 0.2)); p = [MX, lerp(DY, LY + 10, e)]; }
    else if (t < h1) p = [MX, LY];
    else { p = [MX + 90 + v * 1.2 * (t - h1), LY]; teal = true; }
    if (p[0] < 440) bitTile(c, 1, p[0], p[1] + (teal ? -52 : 0), { col: teal ? COL.tealHi : COL.cream, ring: true, s: 58 }); }
  const fl = Math.exp(-Math.abs(t - h1) * 9) * (t > h1 - 0.15 ? 1 : 0); if (fl > 0.02) TOON.glow(c, MX, LY, 240, COL.tealHi, 0.9 * fl);
  note(c, 515);
};

// ---------- ④ 光的路：一样快，还清楚（两条道并排） ----------
FULL.CARD.race = (c, t, id, cd, Q) => {
  // 第三版：不讲「一样快」，讲损耗和稳定——同一串数据跑同一段路：电越跑越弱、越乱、越糊；光几乎不衰减、形状不变
  const x0 = -330, x1 = 380, yE = -150, yL = 220, bw = 64, A = 82, v = 320, tM = Q.morph, Lx = x1 - x0;
  const sigmaAt = d => 2 + 60 * Math.pow(clamp(d / Lx), 1.6);
  const ampE = x => 1 - 0.65 * clamp((x - x0) / Lx), ampL = x => 1 - 0.08 * clamp((x - x0) / Lx);
  const jit = (x, k) => 11 * Math.pow(clamp((x - x0) / Lx), 1.5) * (Math.sin(x * 0.13 + t * 23 + k) + 0.6 * Math.sin(x * 0.29 - t * 31));
  const typed = (s, at, rate = 14) => t < at ? '' : [...s].slice(0, Math.ceil((S12(t - at + 1e-6) + 1 / 12) * rate)).join('');
  txt(c, typed('同一串数据，跑同一段路', Q.heading), -390, -420, { size: 44 });
  axis(c, x0, x1, 400, MO.smooth(seg(t, Q.tE0, Q.tE0 + 0.5)));
  const la = MO.smooth(seg(t, Q.tE0 - 0.05, Q.tE0 + 0.25)), lb = MO.smooth(seg(t, tM[0], tM[0] + 0.3));
  if (la > 0) { c.save(); c.globalAlpha = la; txt(c, '电', -395, yE - A / 2, { size: 64, fam: 'PuHui-Heavy', align: 'center' }); c.setLineDash([4, 10]); c.strokeStyle = COL.creamDim; c.lineWidth = 3; c.beginPath(); c.moveTo(x0, yE); c.lineTo(x1, yE); c.stroke(); c.restore(); }
  if (lb > 0) { c.save(); c.globalAlpha = lb; txt(c, '光', -395, yL, { size: 64, fam: 'PuHui-Heavy', col: COL.teal, align: 'center' }); c.strokeStyle = COL.tealDim; c.lineWidth = 12; c.lineCap = 'round'; c.beginPath(); c.moveTo(x0, yL); c.lineTo(x1 + 30, yL); c.stroke(); c.restore(); }
  // 电：越跑越弱（幅度往下掉）、越乱（抖动越来越大）、越糊（边沿越来越圆）
  const F = x0 + v * (t - Q.tE0);
  if (t > Q.tE0) { const xe = Math.min(x1, F + 4 * sigmaAt(F - x0));
    stroke(c, x0, xe, x => yE - A * ampE(x) * level(x, F, bw, sigmaAt(x - x0)) + jit(x, 0), { step: 3 });
    for (let k = 0; k < 40; k++) { const xc = F - (k + 0.5) * bw; if (xc < x0 + 10 || xc > x1 - 4) continue; const sg = sigmaAt(xc - x0); c.save();
      if (sg < 26) { c.globalAlpha = clamp(1 - (sg - 14) / 14); digit(c, String(bitOf(k)), xc, yE - A - 42, COL.cream, 46); }
      else { c.translate(xc, yE - A - 42); c.rotate(Math.sin(t * 9 + k * 2.1) * 0.12); digit(c, '?', 0, 0, COL.redHi, 50); }
      c.restore(); } }
  // 同一段波复制到光上
  const FL = x0 + v * (t - Q.tL0);
  if (t > tM[0] && t < tM[1]) { const e = MO.cubicInOut(seg(t, tM[0], tM[1])), xr = Math.min(x1, FL);
    stroke(c, x0, xr, x => lerp(yE - A * sqAt(x, F, bw), yL - 26 * sqAt(x, F, bw), e), { col: e < 0.5 ? COL.cream : COL.tealHi, lw: lerp(6, 4, e), alpha: 0.9 }); }
  // 光：几乎不衰减、形状不变（每个脉冲的高度只比出发时低一点点）
  if (t >= tM[1] - 0.05) { const pa = clamp((t - (tM[1] - 0.05)) / 0.12);
    c.save(); c.globalAlpha = pa; c.shadowColor = COL.teal; c.shadowBlur = 20; c.fillStyle = COL.tealHi;
    for (let k = 0; k < 40; k++) { if (!bitOf(k)) continue; const a0 = Math.max(x0, F - (k + 1) * bw + 5), a1 = Math.min(x1 + 30, F - k * bw - 5, FL); if (a1 - a0 <= 10) continue;
      const h = 26 * ampL((a0 + a1) / 2); c.beginPath(); c.roundRect(a0, yL - h / 2, a1 - a0, h, h / 2); c.fill(); }
    c.restore();
    c.save(); c.globalAlpha = pa; for (let k = 0; k < 40; k++) { const xc = F - (k + 0.5) * bw; if (xc < x0 + 10 || xc > Math.min(x1 - 4, FL)) continue; digit(c, String(bitOf(k)), xc, yL - 58, bitOf(k) ? COL.tealHi : 'rgba(155,232,219,.55)', 46); } c.restore(); }
  // 信号强度的包络线：电一路往下掉（损耗大），光几乎是平的（损耗少）
  const env = (y0, y1, at, col, word, wy) => { const q = MO.cubicInOut(seg(t, at, at + 0.6)); if (q <= 0) return;
    c.save(); c.strokeStyle = col; c.lineWidth = 4; c.setLineDash([12, 9]); c.beginPath(); c.moveTo(x0, y0); c.lineTo(lerp(x0, x1, q), lerp(y0, y1, q)); c.stroke(); c.restore();
    if (q >= 1) txt(c, word, x1 + 8, wy, { size: 36, fam: 'PuHui-Heavy', col, align: 'right' }); };
  env(yE - A - 4, yE - A * 0.35 - 4, Q.envE, COL.redHi, '损耗大', yE + 40);
  env(yL - 24, yL - 24 * 0.92, Q.envL, COL.tealHi, '损耗少', yL + 52);
};

// ---------- ④ 对接：歪一点光就漏；对准了才进得去 ----------
FULL.CARD.align = (c, t, id, cd, cue) => {
  const v = 320, bw = 60, t0 = cue.t0, F = -430 + v * (t - t0 + 0.6), dy = lerp(78, 0, MO.cubicInOut(seg(t, cue.slide[0], cue.slide[1]))), ov = clamp(1 - dy / 24);
  rbox(c, -245, 0, 410, 300, { r: 14, line: 'rgba(236,230,218,.5)' }); txt(c, '芯片', -420, -115, { size: 32, col: COL.creamDim });
  c.save(); c.strokeStyle = COL.tealDim; c.lineWidth = 18; c.beginPath(); c.moveTo(-430, 0); c.lineTo(-40, 0); c.stroke(); c.restore();
  // 光纤（包层＋芯）
  c.save(); c.fillStyle = 'rgba(207,216,214,.16)'; c.strokeStyle = 'rgba(207,216,214,.5)'; c.lineWidth = 3; c.beginPath(); c.roundRect(0, dy - 62, 460, 124, 10); c.fill(); c.stroke();
  c.fillStyle = 'rgba(63,181,165,.22)'; c.fillRect(0, dy - 11, 460, 22); c.restore(); txt(c, '光纤', 420, dy - 92, { size: 32, col: COL.creamDim, align: 'right' });
  pulses(c, F, bw, -430, -40, 0, { h: 16 });
  if (ov > 0.02) pulses(c, F, bw, 0, 450, dy, { h: 16, alpha: ov });
  // 漏光：从芯片边上散出去的几道光
  if (ov < 0.98) { const ex = Math.max(0, F + 40); for (let k = 0; k < 30; k++) { if (!bitOf(k)) continue; const age = (F - k * bw - (-40)) / v; if (age < 0 || age > 0.9) continue;
      c.save(); c.globalAlpha = (1 - ov) * (1 - age / 0.9); c.strokeStyle = COL.tealHi; c.lineWidth = 5; c.lineCap = 'round';
      for (const a of [-0.75, -0.38, 0.38, 0.75, 0.15]) { const r0 = 20 + age * 240, r1 = r0 + 40; c.beginPath(); c.moveTo(-40 + Math.cos(a) * r0, Math.sin(a) * r0); c.lineTo(-40 + Math.cos(a) * r1, Math.sin(a) * r1); c.stroke(); }
      c.restore(); } }
};

// ---------- ⑤ 抵达：光 → 电流（很弱）→ 放大 → 一列拆回一排 ----------
FULL.CARD.arrive = (c, t, id, cd, cue) => {
  const LY = -330, v = 300, bw = 60, t0 = cue.t0, F = -450 + v * (t - t0 + 1.0);
  c.save(); c.strokeStyle = COL.tealDim; c.lineWidth = 14; c.lineCap = 'round'; c.beginPath(); c.moveTo(-450, LY); c.lineTo(-222, LY); c.stroke(); c.restore();
  pulses(c, F, bw, -450, -222, LY, { h: 22 });
  const bPD = sqAt(-222, F, bw);
  rbox(c, -150, LY, 140, 140, { line: bPD ? COL.tealHi : 'rgba(236,230,218,.7)', lw: bPD ? 5 : 3 }); txt(c, '感光', -150, LY, { size: 36, fam: 'PuHui-Heavy', align: 'center' });
  // 很弱的电流
  stroke(c, -80, 58, x => LY + 16 - 20 * sqAt(x, F + 142, bw), { lw: 3, step: 1, alpha: 0.9 });
  // 放大器（三角）
  const ah = seg(t, cue.amp, cue.amp + 0.3);
  c.save(); c.strokeStyle = ah > 0 ? COL.cream : 'rgba(236,230,218,.7)'; c.lineWidth = 3 + 2 * ah; c.fillStyle = '#2c2c2a'; c.beginPath(); c.moveTo(62, LY - 62); c.lineTo(178, LY); c.lineTo(62, LY + 62); c.closePath(); c.fill(); c.stroke(); c.restore();
  txt(c, '放大', 100, LY, { size: 28, fam: 'PuHui-Heavy', align: 'center' });
  if (t >= cue.amp) stroke(c, 180, 380, x => LY + 30 - 64 * sqAt(x, F + 402, bw), { lw: 6, step: 1 });
  // 拆开：一列 → 一排（GPU B）
  const [fa, fb] = cue.fan, N = 24, di = (fb - fa) / N, HX = 380, WY = 150, vd = 900;
  c.save(); c.strokeStyle = COL.cream; c.lineWidth = 6; c.lineCap = 'round'; c.beginPath(); c.moveTo(-430, WY); c.lineTo(HX - 34, WY); c.moveTo(HX + 34, WY); c.lineTo(430, WY); c.stroke(); c.restore();
  c.save(); c.strokeStyle = 'rgba(236,230,218,.5)'; c.lineWidth = 3; c.setLineDash([8, 10]); c.strokeRect(-300, 190, 600, 220); c.restore(); txt(c, 'GPU B', -290, 214, { size: 28, fam: 'PuHui-Heavy', col: COL.creamDim });
  c.save(); c.strokeStyle = 'rgba(236,230,218,.3)'; c.lineWidth = 3; c.setLineDash([6, 10]); c.beginPath(); c.moveTo(HX, LY + 40); c.lineTo(HX, WY - 6); c.stroke(); c.restore();
  const cell = k => [-245 + 70 * (k % 8), 250 + 70 * Math.floor(k / 8)];
  if (t >= cue.amp) for (let k = 0; k < N; k++) { const r = fa + k * di, b = bitOf(k); let p, tile = true;
    if (t < r) { const y = WY - vd * (r - t); if (y < LY + 40) continue; p = [HX, y]; tile = false; }
    else if (t < r + 0.4) { const e = MO.cubicInOut(seg(t, r, r + 0.4)), a = cell(k); p = [lerp(HX, a[0], e), lerp(WY + 40, a[1], e)]; }
    else p = cell(k);
    if (tile) bitTile(c, b, p[0], p[1], { ring: k === 5 }); else digit(c, String(b), p[0], p[1]); }
  note(c, 515);
};
})();
