// 光互连 03 · 小红书改版新增的卡片：雷电线（实物开场）、快递路线图、照片花了 / 消息乱码、高速还是山路、「你在这里」小路线图。
// 坐标原点在卡片中心；时间点全部来自 desk_x.json 的 cue（tools/build_desk_x.py）。纯时间函数，随机数用种子。
(() => {
const { clamp, lerp } = U; const { COL, txt, seg, S12 } = FULL;
const GOLD = '#f5d77e';
const STN5 = ['打包出发', '路上', '中转', '干线', '签收'];

// ---------- 雷电线：短的一根、长的一根；线上跑着的小光点越密 = 速度越快 ----------
const cablePts = (kind) => { const P = [];
  if (kind === 'short') for (let i = 0; i <= 40; i++) { const s = i / 40; P.push([lerp(-250, 250, s), -250 + 18 * Math.sin(Math.PI * s)]); }
  else for (let i = 0; i <= 160; i++) { const s = i / 160; P.push([lerp(-400, 400, s), 170 + 120 * Math.sin(Math.PI * 2 * 1.25 * s) * (0.55 + 0.45 * Math.sin(Math.PI * s))]); }
  return P; };
const CP = { short: cablePts('short'), long: cablePts('long') };
const cum = P => { const a = [0]; for (let i = 1; i < P.length; i++) a.push(a[i - 1] + Math.hypot(P[i][0] - P[i - 1][0], P[i][1] - P[i - 1][1])); return a; };
const CU = { short: cum(CP.short), long: cum(CP.long) };
const at = (k, d) => { const P = CP[k], A = CU[k]; let i = 1; while (i < A.length - 1 && A[i] < d) i++; const f = (d - A[i - 1]) / (A[i] - A[i - 1] || 1); return [lerp(P[i - 1][0], P[i][0], f), lerp(P[i - 1][1], P[i][1], f)]; };
const plug = (c, x, y, ang, { chip = 0, fiber = 0 } = {}) => { c.save(); c.translate(x, y); c.rotate(ang);
  c.fillStyle = '#1e1e1d'; c.beginPath(); c.roundRect(-8, -24, 70, 48, 12); c.fill();                          // 插头外壳
  const g = c.createLinearGradient(0, -16, 0, 16); g.addColorStop(0, '#d9d6cf'); g.addColorStop(0.5, '#8d8a84'); g.addColorStop(1, '#c9c6bf');
  c.fillStyle = g; c.beginPath(); c.roundRect(60, -14, 44, 28, 9); c.fill();                                        // USB-C 金属头
  c.fillStyle = '#f3efe5'; c.beginPath(); c.moveTo(22, -14); c.lineTo(12, 3); c.lineTo(22, 3); c.lineTo(16, 16); c.lineTo(32, -4); c.lineTo(22, -4); c.lineTo(28, -14); c.closePath(); c.fill();   // 闪电标
  if (chip > 0) { c.save(); c.globalAlpha = chip; c.shadowColor = GOLD; c.shadowBlur = 26; c.fillStyle = '#2b2a27'; c.strokeStyle = GOLD; c.lineWidth = 3; c.beginPath(); c.roundRect(34, -12, 22, 24, 4); c.fill(); c.stroke();
    for (let k = 0; k < 3; k++) { c.beginPath(); c.moveTo(38 + k * 7, -16); c.lineTo(38 + k * 7, -12); c.moveTo(38 + k * 7, 12); c.lineTo(38 + k * 7, 16); c.stroke(); } c.restore(); }
  c.restore(); };
const cable = (c, k, t, { gap, speed = 520, fiber = 0, chip = 0, dim = 0 }) => { const P = CP[k], L = CU[k][CU[k].length - 1];
  c.save(); c.lineCap = 'round'; c.lineJoin = 'round';
  c.shadowColor = 'rgba(40,30,15,.35)'; c.shadowBlur = 14; c.shadowOffsetY = 8;
  c.strokeStyle = fiber > 0 ? `rgb(${lerp(42, 30, fiber)},${lerp(42, 70, fiber)},${lerp(40, 68, fiber)})` : '#2a2a28'; c.lineWidth = 26; c.beginPath(); P.forEach(([x, y], i) => i ? c.lineTo(x, y) : c.moveTo(x, y)); c.stroke();
  c.shadowColor = 'transparent'; c.strokeStyle = 'rgba(255,255,255,.13)'; c.lineWidth = 6; c.beginPath(); P.forEach(([x, y], i) => i ? c.lineTo(x, y - 6) : c.moveTo(x, y - 6)); c.stroke();
  if (fiber > 0) { c.save(); c.globalAlpha = fiber; c.shadowColor = COL.teal; c.shadowBlur = 22; c.strokeStyle = 'rgba(155,232,219,.55)'; c.lineWidth = 6; c.beginPath(); P.forEach(([x, y], i) => i ? c.lineTo(x, y) : c.moveTo(x, y)); c.stroke(); c.restore(); }
  // 跑着的数据：光点之间的间隔 gap 越小，每秒送的越多
  const col = fiber > 0.5 ? COL.tealHi : GOLD, off = (t * speed) % gap;
  c.globalCompositeOperation = 'lighter';
  for (let d = off; d < L; d += gap) { const [x, y] = at(k, d), r = 7; const gr = c.createRadialGradient(x, y, 0, x, y, r * 2.6); gr.addColorStop(0, `rgba(255,250,235,${0.95 * (1 - dim)})`); gr.addColorStop(0.4, fiber > 0.5 ? `rgba(63,181,165,${0.8 * (1 - dim)})` : `rgba(226,181,74,${0.8 * (1 - dim)})`); gr.addColorStop(1, 'rgba(0,0,0,0)'); c.fillStyle = gr; c.beginPath(); c.arc(x, y, r * 2.6, 0, 7); c.fill(); }
  c.restore();
  const a0 = Math.atan2(P[1][1] - P[0][1], P[1][0] - P[0][0]) + Math.PI, n = P.length - 1, a1 = Math.atan2(P[n][1] - P[n - 1][1], P[n][0] - P[n - 1][0]);
  plug(c, P[0][0], P[0][1], a0, { chip }); plug(c, P[n][0], P[n][1], a1, { chip }); };
FULL.CARD.cables = (c, t, id, cd, Q) => {
  const chip = Q.chip != null ? MO.smooth(seg(t, Q.chip, Q.chip + 0.4)) : 0, fiber = Q.fiber != null ? MO.smooth(seg(t, Q.fiber, Q.fiber + 0.5)) : 0;
  const lg = lerp(64, 32, Math.max(chip, fiber));                 // 带芯片 / 光纤线：长线也能跑满速
  if (Q.out) {     // 抖音版第一帧：线缩到左边，两根线的出口直接冒出信号——短线出来方方正正，长线出来已经糊了（机制演示从第 0 秒就在动）
    c.save(); c.translate(-150, 0); c.scale(0.7, 0.7); cable(c, 'short', t, { gap: 32 }); cable(c, 'long', t, { gap: lg }); c.restore();
    const H = FULL.H, bw = 40, X1 = 470;
    [[115, -175, 2, 1], [220, 119, 13, 0.9]].forEach(([x0, y, sg, am], j) => { const F = x0 + 4000 + t * 240;
      c.save(); c.strokeStyle = 'rgba(27,27,26,.25)'; c.lineWidth = 3; c.setLineDash([6, 8]); c.beginPath(); c.moveTo(x0, y); c.lineTo(X1, y); c.stroke(); c.restore();
      H.stroke(c, x0, X1, x => y - 70 * am * H.level(x, F, bw, sg), { col: j ? '#b8433f' : '#1b1b1a', lw: 7, step: 2 }); });
    if (Q.ring2 != null && t >= Q.ring2) { const q = MO.smooth(seg(t, Q.ring2, Q.ring2 + 0.5)); c.save(); c.strokeStyle = COL.red; c.lineWidth = 7; c.beginPath(); c.ellipse(345, 90, 175, 95, -0.03, -1.6, -1.6 + Math.PI * 2 * q); c.stroke(); c.restore();
      if (q >= 1) for (let k = 0; k < 3; k++) { c.save(); c.translate(270 + k * 70, 0); c.rotate(Math.sin(t * 9 + k * 2) * 0.15); txt(c, '?', 0, 0, { size: 46, fam: 'PuHui-Heavy', col: COL.red, align: 'center' }); c.restore(); } }
    if (Q.ring != null && t >= Q.ring) { const q = MO.smooth(seg(t, Q.ring, Q.ring + 0.5)); c.save(); c.strokeStyle = COL.red; c.lineWidth = 7; c.beginPath(); c.ellipse(-150, 122, 330, 150, -0.03, -1.6, -1.6 + Math.PI * 2 * q); c.stroke(); c.restore(); }
    return; }
  if (!Q.noshort) cable(c, 'short', t, { gap: 32 });
  cable(c, 'long', t, { gap: lg, fiber, chip: chip * (1 - fiber) });
  if (Q.ring != null && t >= Q.ring) { const q = MO.smooth(seg(t, Q.ring, Q.ring + 0.5)); c.save(); c.strokeStyle = COL.red; c.lineWidth = 7; c.beginPath(); c.ellipse(0, 175, 470, 200, -0.03, -1.6, -1.6 + Math.PI * 2 * q); c.stroke(); c.restore(); }
  if (Q.inset != null && t >= Q.inset) {           // 放大插头里面：糊的信号进芯片（检修站），清楚的出来
    const q = MO.backOut(clamp((S12(t) - Q.inset) / 0.3), 1.6), P = CP.long[CP.long.length - 1], PX = 0, PY = -300, PW = 820, PH = 300;
    c.save(); c.strokeStyle = 'rgba(236,230,218,.75)'; c.lineWidth = 4; c.setLineDash([12, 10]); c.globalAlpha = Math.min(1, q); c.beginPath(); c.moveTo(PX + PW / 2 - 60, PY + PH / 2); c.lineTo(P[0] - 10, P[1] - 40); c.stroke(); c.restore();
    c.save(); c.translate(PX, PY); c.scale(Math.min(1, q), Math.min(1, q)); c.shadowColor = 'rgba(40,30,15,.4)'; c.shadowBlur = 18; c.shadowOffsetY = 8; c.fillStyle = COL.card; c.beginPath(); c.roundRect(-PW / 2, -PH / 2, PW, PH, 22); c.fill(); c.shadowColor = 'transparent';
    const H = FULL.H, F = -PW / 2 + 40 + ((t - Q.inset) * 260) % 64 + 64 * 6, bw = 64;
    H.stroke(c, -PW / 2 + 40, -90, x => 20 - 60 * H.level(x, F + 64 * 20, bw, 26), { lw: 5, step: 2 });                // 进来：糊的
    H.rbox(c, 0, 0, 130, 130, { r: 14, line: GOLD, lw: 5 }); txt(c, '检修', 0, 2, { size: 38, fam: 'PuHui-Heavy', col: GOLD, align: 'center' });
    H.stroke(c, 90, PW / 2 - 40, x => 20 - 60 * H.level(x, F + 64 * 20, bw, 2), { lw: 5, step: 2 });                    // 出去：清楚的
    txt(c, '进来：糊的', -PW / 2 + 40, -112, { size: 30, fam: 'PuHui-Heavy', col: COL.creamDim }); txt(c, '出去：清楚的', PW / 2 - 40, -112, { size: 30, fam: 'PuHui-Heavy', col: COL.cream, align: 'right' });
    c.restore(); }
  if (Q.chipRing != null && t >= Q.chipRing) { const q = MO.smooth(seg(t, Q.chipRing, Q.chipRing + 0.4)), P = CP.long[CP.long.length - 1]; c.save(); c.strokeStyle = COL.red; c.lineWidth = 7; c.beginPath(); c.arc(P[0] - 10, P[1], 62, -1.6, -1.6 + Math.PI * 2 * q); c.stroke(); c.restore(); }
};

// ---------- AI 机柜背面：一层层的计算托盘，中间密密麻麻的铜缆把它们连在一起（下集第一帧；回扣时再出现一次） ----------
const RK = (() => { const r = U.rng(77), cab = []; for (let i = 0; i < 46; i++) { const ty = -400 + Math.floor(r() * 9) * 100 + 40, sy = -420 + r() * 840, x0 = -250 + r() * 60, xs = 120 + r() * 120;
  cab.push({ x0, y0: ty, x1: xs, y1: sy, bend: 60 + r() * 120, w: 7 + r() * 5, hi: r() > 0.55, ph: r() }); } return cab; })();
const bez = (q, t) => { const u = 1 - t; return [u * u * u * q[0][0] + 3 * u * u * t * q[1][0] + 3 * u * t * t * q[2][0] + t * t * t * q[3][0], u * u * u * q[0][1] + 3 * u * u * t * q[1][1] + 3 * u * t * t * q[2][1] + t * t * t * q[3][1]]; };
FULL.CARD.rack = (c, t, id, cd, Q) => {
  const X0 = -330, X1 = 330, Y0 = -480, Y1 = 560;
  c.save(); c.shadowColor = 'rgba(40,30,15,.45)'; c.shadowBlur = 30; c.shadowOffsetY = 14; c.fillStyle = '#1f1f1e'; c.beginPath(); c.roundRect(X0, Y0, X1 - X0, Y1 - Y0, 18); c.fill(); c.restore();
  c.fillStyle = '#2b2b29'; c.fillRect(X0 + 14, Y0 + 14, 30, Y1 - Y0 - 28); c.fillRect(X1 - 44, Y0 + 14, 30, Y1 - Y0 - 28);       // 两侧立柱
  for (let i = 0; i < 9; i++) { const y = -440 + i * 100; c.fillStyle = '#323230'; c.fillRect(X0 + 50, y, X1 - X0 - 100, 70);           // 计算托盘
    for (let k = 0; k < 4; k++) { const on = 0.5 + 0.5 * Math.sin(t * 3 + i * 1.7 + k * 2.3); c.fillStyle = `rgba(127,214,180,${0.35 + 0.6 * on})`; c.beginPath(); c.arc(X0 + 70 + k * 16, y + 14, 4, 0, 7); c.fill(); }
    c.fillStyle = '#4a4a46'; for (let k = 0; k < 6; k++) c.fillRect(X0 + 140 + k * 24, y + 46, 16, 14); }                              // 接口
  // 铜缆：从托盘的接口出来，汇到右边的「背板」
  c.save(); c.lineCap = 'round';
  RK.forEach((k, n) => { const q = [[k.x0, k.y0 + 52], [k.x0 + k.bend, k.y0 + 52], [k.x1 - k.bend * 0.6, k.y1], [k.x1, k.y1]];
    c.strokeStyle = '#141413'; c.lineWidth = k.w + 3; c.beginPath(); c.moveTo(...q[0]); c.bezierCurveTo(...q[1], ...q[2], ...q[3]); c.stroke();
    c.strokeStyle = k.hi ? '#a8683a' : '#6e4a30'; c.lineWidth = k.w; c.beginPath(); c.moveTo(...q[0]); c.bezierCurveTo(...q[1], ...q[2], ...q[3]); c.stroke();
    if (n % 3 === 0) { const u = (t * 0.6 + k.ph) % 1, [x, y] = bez(q, u); c.save(); c.globalCompositeOperation = 'lighter'; const g = c.createRadialGradient(x, y, 0, x, y, 16); g.addColorStop(0, 'rgba(255,250,235,.95)'); g.addColorStop(0.4, 'rgba(226,181,74,.8)'); g.addColorStop(1, 'rgba(0,0,0,0)'); c.fillStyle = g; c.beginPath(); c.arc(x, y, 16, 0, 7); c.fill(); c.restore(); } });
  c.restore();
  c.fillStyle = '#2b2b29'; c.fillRect(230, -440, 60, 880);                                                                               // 背板
  // 「不是说要换成光吗」：一根光纤从机柜顶上亮一下，又暗下去
  if (Q.fiber != null && t >= Q.fiber) { const q = MO.smooth(seg(t, Q.fiber, Q.fiber + 0.4)), fade = 1 - 0.75 * MO.smooth(seg(t, Q.fiber + 1.2, Q.fiber + 2.0));
    c.save(); c.globalAlpha = q * fade; c.shadowColor = COL.teal; c.shadowBlur = 24; c.strokeStyle = COL.tealHi; c.lineWidth = 8; c.lineCap = 'round'; c.beginPath(); c.moveTo(260, -480); c.bezierCurveTo(260, -560, 380, -560, 470, -520); c.stroke(); c.restore(); }
  if (Q.mag != null && t >= Q.mag) {            // 放大镜钻进一根铜缆：柜里距离短，台阶跑到头还方方正正
    const q = MO.backOut(clamp((S12(t) - Q.mag) / 0.3), 1.6), MX = 120, MY = -150, R = 200;
    c.save(); c.translate(MX, MY); c.scale(Math.min(1.05, q), Math.min(1.05, q));
    c.save(); c.rotate(0.75); c.fillStyle = '#2b2a27'; c.fillRect(R - 10, -16, 150, 32); c.strokeStyle = COL.cream; c.lineWidth = 4; c.strokeRect(R - 10, -16, 150, 32); c.restore();
    c.save(); c.beginPath(); c.arc(0, 0, R, 0, 7); c.clip(); c.fillStyle = '#141413'; c.fillRect(-R, -R, 2 * R, 2 * R);
    const g = c.createLinearGradient(0, 30, 0, 110); g.addColorStop(0, '#b87a48'); g.addColorStop(0.5, '#8a5634'); g.addColorStop(1, '#5e3a24'); c.fillStyle = g; c.fillRect(-R, 40, 2 * R, 64);
    const H = FULL.H, F = -R + 4000 + (t - Q.mag) * 260; H.stroke(c, -R, R, x => 10 - 80 * H.level(x, F, 46, 2.5), { lw: 6, step: 2 });
    c.restore(); c.strokeStyle = COL.cream; c.lineWidth = 9; c.beginPath(); c.arc(0, 0, R, 0, 7); c.stroke(); c.restore(); }
  if (Q.ring != null && t >= Q.ring) { const q = MO.smooth(seg(t, Q.ring, Q.ring + 0.5)); c.save(); c.strokeStyle = COL.red; c.lineWidth = 8; c.beginPath(); c.ellipse(20, 0, 300, 470, 0, -1.6, -1.6 + Math.PI * 2 * q); c.stroke(); c.restore(); }
};

// ---------- 快递路线图：发件的 AI 芯片 → 五站 → 收件的 AI 芯片；包裹一直在路上跑；亮第二站「路上」 ----------
FULL.CARD.route = (c, t, id, cd, Q) => {
  const x0 = -330, x1 = 330, y = 10, chipBox = (x, s) => { FULL.H.rbox(c, x, y, 110, 110, { r: 12, line: GOLD, lw: 4 }); txt(c, s, x, y + 2, { size: 26, fam: 'PuHui-Heavy', col: COL.cream, align: 'center' }); };
  txt(c, 'AI 芯片之间寄快递', 0, -250, { size: 46, fam: 'PuHui-Heavy', col: COL.cream, align: 'center' });
  c.save(); c.strokeStyle = 'rgba(236,230,218,.5)'; c.lineWidth = 6; c.setLineDash([18, 12]); c.lineDashOffset = -t * 60; c.beginPath(); c.moveTo(x0, y); c.lineTo(x1, y); c.stroke(); c.restore();
  chipBox(x0 - 70, '发件'); chipBox(x1 + 70, '收件');
  const lit = MO.smooth(seg(t, Q.lit, Q.lit + 0.3));
  STN5.forEach((s, i) => { const x = lerp(x0 + 50, x1 - 50, i / 4), on = i === 1 && lit > 0;
    c.save(); c.fillStyle = on ? COL.redHi : '#2c2c2a'; c.strokeStyle = on ? COL.redHi : 'rgba(236,230,218,.6)'; c.lineWidth = 4; c.beginPath(); c.arc(x, y, on ? 20 + 6 * lit : 16, 0, 7); c.fill(); c.stroke(); c.restore();
    txt(c, s, x, y + 62, { size: on ? 40 : 30, fam: 'PuHui-Heavy', col: on ? COL.redHi : COL.creamDim, align: 'center' }); });
  // 包裹：从发件跑到第二站停一下（亮站时）
  const u = Q.lit != null && t >= Q.lit ? 1 : clamp((t - Q.t0) / Math.max(0.3, (Q.lit ?? Q.t0 + 1) - Q.t0)), px = lerp(x0 - 10, lerp(x0 + 50, x1 - 50, 0.25), u) + (t > Q.lit ? 6 * Math.sin(t * 9) : 0);
  c.save(); c.shadowColor = GOLD; c.shadowBlur = 18; c.fillStyle = '#c99a4a'; c.fillRect(px - 22, y - 70, 44, 36); c.strokeStyle = '#7a5a2a'; c.lineWidth = 3; c.strokeRect(px - 22, y - 70, 44, 36); c.beginPath(); c.moveTo(px, y - 70); c.lineTo(px, y - 34); c.stroke(); c.restore();
};

// ---------- 认错一个：照片花了一块、消息里冒出一个乱码（示意） ----------
const photo = (g, x, y, w, h) => { const sky = g.createLinearGradient(0, y, 0, y + h); sky.addColorStop(0, '#f2c27a'); sky.addColorStop(0.55, '#e98a5c'); sky.addColorStop(1, '#5c3a52'); g.fillStyle = sky; g.fillRect(x, y, w, h);
  g.fillStyle = '#fff2c9'; g.beginPath(); g.arc(x + w * 0.62, y + h * 0.36, w * 0.11, 0, 7); g.fill();
  g.fillStyle = '#3b2a3c'; g.beginPath(); g.moveTo(x, y + h * 0.66); for (let n = 0; n <= 12; n++) g.lineTo(x + w * n / 12, y + h * (0.58 + 0.08 * Math.sin(n * 1.7 + 1))); g.lineTo(x + w, y + h); g.lineTo(x, y + h); g.fill();
  g.fillStyle = '#241a27'; g.fillRect(x, y + h * 0.82, w, h * 0.18); };
FULL.CARD.glitch = (c, t, id, cd, Q) => {
  const X = -400, Y = -330, w = 380, h = 470, NS = 12, bad = 5, gq = MO.smooth(seg(t, Q.photo, Q.photo + 0.25));
  c.save(); c.fillStyle = '#f6f2ea'; c.fillRect(X - 12, Y - 12, w + 24, h + 24); c.restore();
  for (let i = 0; i < NS; i++) { const sy = Y + h * i / NS; c.save(); c.beginPath(); c.rect(X, sy, w, h / NS + 0.5); c.clip();
    const sh = i === bad ? 46 * gq + (gq > 0 && gq < 1 ? 10 * Math.sin(t * 60) : 0) : 0; photo(c, X + sh, Y, w, h);
    if (i === bad && gq > 0) { c.globalAlpha = 0.55 * gq; c.fillStyle = '#5fb0d8'; c.fillRect(X, sy, sh, h / NS + 1); } c.restore(); }
  if (gq > 0.5) { c.save(); c.strokeStyle = COL.redHi; c.lineWidth = 6; c.strokeRect(X - 16, Y + h * bad / NS - 8, w + 32, h / NS + 16); c.restore(); }
  // 消息气泡
  const bx = 40, by = -200, bw = 360, bh = 120, mq = MO.smooth(seg(t, Q.msg, Q.msg + 0.2));
  c.save(); c.fillStyle = '#95ec69'; c.beginPath(); c.roundRect(bx, by, bw, bh, 22); c.fill(); c.beginPath(); c.moveTo(bx + bw, by + 40); c.lineTo(bx + bw + 22, by + 52); c.lineTo(bx + bw, by + 64); c.fill(); c.restore();
  const s = ['今', '晚', '七', '点', '见'], fx = bx + 40; c.font = '56px "PuHui-Heavy"';
  s.forEach((ch, i) => { const x = fx + i * 60; if (i === 3 && mq > 0) { c.save(); c.translate(x + 28, by + bh / 2 + 2); c.rotate(Math.sin(t * 10) * 0.15); txt(c, '?', 0, 0, { size: 60, fam: 'PuHui-Heavy', col: COL.red, align: 'center' }); c.restore(); }
    else txt(c, ch, x, by + bh / 2 + 2, { size: 56, fam: 'PuHui-Heavy', col: '#1b1b1a' }); });
  if (mq > 0.5) { c.save(); c.strokeStyle = COL.redHi; c.lineWidth = 6; c.beginPath(); c.arc(fx + 3 * 60 + 28, by + bh / 2, 46, 0, 7); c.stroke(); c.restore(); }
  FULL.H.note && txt(c, '示意', 380, 440, { size: 26, col: 'rgba(236,230,218,.4)', align: 'right' });
};

// ---------- 能跑 200 公里每小时：在高速上，还是在山路上？ ----------
const car = (c, x, y, ang, col) => { c.save(); c.translate(x, y); c.rotate(ang); c.fillStyle = col; c.beginPath(); c.roundRect(-44, -20, 88, 34, 10); c.fill(); c.beginPath(); c.roundRect(-24, -38, 50, 24, 8); c.fill();
  c.fillStyle = '#111'; c.beginPath(); c.arc(-24, 16, 11, 0, 7); c.arc(26, 16, 11, 0, 7); c.fill(); c.restore(); };
FULL.CARD.road = (c, t, id, cd, Q) => {
  // 上：高速，直、宽
  if (t >= Q.hw) { const q = MO.smooth(seg(t, Q.hw, Q.hw + 0.4)); c.save(); c.globalAlpha = q; c.fillStyle = '#3a3a37'; c.fillRect(-420, -300, 840, 150);
    c.strokeStyle = 'rgba(236,230,218,.7)'; c.lineWidth = 6; c.setLineDash([40, 30]); c.lineDashOffset = t * 600; c.beginPath(); c.moveTo(-420, -225); c.lineTo(420, -225); c.stroke(); c.restore();
    const x = -380 + ((t - Q.hw) * 520) % 760; car(c, x, -255, 0, GOLD); txt(c, '高速', -420, -350, { size: 34, fam: 'PuHui-Heavy', col: COL.creamDim }); }
  // 下：山路，弯、窄
  if (t >= Q.mt) { const q = MO.smooth(seg(t, Q.mt, Q.mt + 0.4)), yAt = x => 200 + 120 * Math.sin((x + 420) / 840 * Math.PI * 3);
    c.save(); c.globalAlpha = q; c.strokeStyle = '#3a3a37'; c.lineWidth = 70; c.lineCap = 'round'; c.beginPath(); for (let x = -420; x <= 420; x += 8) x === -420 ? c.moveTo(x, yAt(x)) : c.lineTo(x, yAt(x)); c.stroke();
    c.strokeStyle = 'rgba(236,230,218,.5)'; c.lineWidth = 4; c.setLineDash([16, 16]); c.beginPath(); for (let x = -420; x <= 420; x += 8) x === -420 ? c.moveTo(x, yAt(x)) : c.lineTo(x, yAt(x)); c.stroke(); c.restore();
    const x = -380 + ((t - Q.mt) * 110) % 760, a = Math.atan2(yAt(x + 4) - yAt(x - 4), 8); car(c, x, yAt(x) - 22, a, COL.redHi); txt(c, '山路', -420, 40, { size: 34, fam: 'PuHui-Heavy', col: COL.creamDim }); }
};

// ---------- 「你在这里」：桌上的小路线图（结尾） ----------
FULL.CARD.here = (c, t, id, cd, Q) => { if (t < Q.t0) return; const q = clamp((S12(t) - Q.t0) / 0.3), x0 = -380, x1 = 380, y = 0;
  c.save(); c.globalAlpha = q; c.strokeStyle = COL.ink; c.lineWidth = 5; c.setLineDash([16, 12]); c.beginPath(); c.moveTo(x0, y); c.lineTo(x1, y); c.stroke(); c.setLineDash([]);
  STN5.forEach((s, i) => { const x = lerp(x0, x1, i / 4), on = i === 1; c.fillStyle = on ? COL.red : COL.paper; c.strokeStyle = COL.ink; c.lineWidth = 4; c.beginPath(); c.arc(x, y, on ? 22 : 16, 0, 7); c.fill(); c.stroke();
    txt(c, s, x, y + 56, { size: on ? 36 : 30, fam: 'PuHui-Heavy', col: on ? COL.red : 'rgba(27,27,26,.55)', align: 'center' }); });
  const xh = lerp(x0, x1, 0.25); c.strokeStyle = COL.red; c.lineWidth = 5; c.beginPath(); c.ellipse(xh, y + 20, 100, 80, -0.1, 0, Math.PI * 2 * clamp((S12(t) - Q.t0 - 0.2) / 0.4)); c.stroke();
  txt(c, '你在这里', xh, y - 128, { size: 38, fam: 'PuHui-Heavy', col: COL.red, align: 'center' }); txt(c, 'AI 芯片之间寄快递', x1, y - 128, { size: 30, fam: 'PuHui-Heavy', col: 'rgba(27,27,26,.5)', align: 'right' }); c.restore(); };
})();
