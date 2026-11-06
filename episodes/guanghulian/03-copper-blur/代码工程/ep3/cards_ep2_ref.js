// 第二篇的黑卡片（3b1b 式：一次只动一样东西；米白＝电信号/比特，红＝编辑的笔）。坐标原点在卡片中心，时间点来自 ep2/desk.json 的 cue。
(() => {
const { clamp, lerp } = U; const { COL, txt, seg, S12 } = FULL;
const { bitOf, level, stroke, digit, rbox, pulses, bitTile, axis, bracket, tint, note } = FULL.H;
const ring = (c, x, y, r = 34) => { c.save(); c.strokeStyle = COL.redHi; c.lineWidth = 5; c.beginPath(); c.arc(x, y, r, 0, 7); c.stroke(); c.restore(); };
const wall = (c, y, hx, x0 = -430, x1 = 430, gap = 34) => { c.save(); c.strokeStyle = COL.cream; c.lineWidth = 6; c.lineCap = 'round'; c.beginPath(); c.moveTo(x0, y); c.lineTo(hx - gap, y); c.moveTo(hx + gap, y); c.lineTo(x1, y); c.stroke(); c.restore(); };
const cross = (c, x, y, s = 18) => { c.save(); c.strokeStyle = COL.redHi; c.lineWidth = 6; c.lineCap = 'round'; c.beginPath(); c.moveTo(x - s, y - s); c.lineTo(x + s, y + s); c.moveTo(x + s, y - s); c.lineTo(x - s, y + s); c.stroke(); c.restore(); };
const tick = (c, x, y, s = 18, col = COL.cream) => { c.save(); c.strokeStyle = col; c.lineWidth = 6; c.lineCap = 'round'; c.lineJoin = 'round'; c.beginPath(); c.moveTo(x - s, y); c.lineTo(x - s * 0.3, y + s * 0.7); c.lineTo(x + s, y - s * 0.8); c.stroke(); c.restore(); };
const meter = (c, x, y, w, q, name, col = COL.cream) => { txt(c, name, x - 20, y, { size: 32, fam: 'PuHui-Heavy', col: COL.creamDim, align: 'right' });
  c.save(); c.strokeStyle = 'rgba(236,230,218,.4)'; c.lineWidth = 3; c.strokeRect(x, y - 16, w, 32); c.fillStyle = col; c.fillRect(x + 4, y - 12, (w - 8) * clamp(q), 24); c.restore(); };

// ---------- 发货口：一大排 → 一列；收货口：一列 → 拆回一排 ----------
FULL.CARD.serdes2 = (c, t, id, cd, Q) => {
  const N = 24, cellA = k => [-120 + 70 * (k % 8), -470 + 62 * Math.floor(k / 8)], cellB = k => [-120 + 70 * (k % 8), 330 + 62 * Math.floor(k / 8)];
  // 发货口
  const HA = -380, WA = -270, OA = -190, dtA = 0.1, vA = 600, bwA = 60;
  wall(c, WA, HA);
  const FA = HA + vA * (t - Q.ser - 0.15);
  if (FA > HA - 30) stroke(c, HA - 30, Math.min(430, FA + bwA / 2), x => { const k = Math.round((FA - x) / bwA); return k >= 0 && k < N && bitOf(k) ? -130 : -80; }, { lw: 6, step: 1 });
  for (let k = 0; k < N; k++) { const r = Q.ser + k * dtA; let p, tile = true;
    if (t < r - 0.45) p = cellA(k);
    else if (t < r) { const e = MO.cubicInOut(seg(t, r - 0.45, r)), a = cellA(k); p = [lerp(a[0], HA, e), lerp(a[1], WA - 45, e) - Math.sin(Math.PI * e) * 26]; }
    else if (t < r + 0.15) p = [HA, lerp(WA - 45, OA, seg(t, r, r + 0.15))];
    else { p = [HA + vA * (t - r - 0.15), OA]; tile = false; if (p[0] > 430) continue; }
    if (tile) bitTile(c, bitOf(k), p[0], p[1], { s: 48, ring: k === 5 }); else { digit(c, String(bitOf(k)), p[0], p[1]); if (k === 5) ring(c, p[0], p[1]); } }
  // 路：右边一条虚线，把发出去的一列接到收货口
  c.save(); c.strokeStyle = 'rgba(236,230,218,.35)'; c.lineWidth = 4; c.setLineDash([10, 12]); c.beginPath(); c.moveTo(440, -105); c.lineTo(440, 150); c.stroke(); c.restore();
  // 收货口
  const HB = -380, WB = 250, IB = 160, dtB = 0.08, vB = 900;
  wall(c, WB, HB);
  for (let k = 0; k < N; k++) { const ent = Q.des + k * dtB, hole = ent + (430 - HB) / vB; let p, tile = false;
    if (t < ent) continue;
    if (t < hole) p = [430 - vB * (t - ent), IB];
    else if (t < hole + 0.4) { const e = MO.cubicInOut(seg(t, hole, hole + 0.4)), b = cellB(k); p = [lerp(HB, b[0], e), lerp(WB + 30, b[1], e) + Math.sin(Math.PI * e) * 24]; tile = true; }
    else { p = cellB(k); tile = true; }
    if (tile) bitTile(c, bitOf(k), p[0], p[1], { s: 48, ring: k === 5 }); else { digit(c, String(bitOf(k)), p[0], p[1]); if (k === 5) ring(c, p[0], p[1]); } }
};

// ---------- 出口不够：引脚就这么几个，每多一条线就多占面积、多耗电 ----------
FULL.CARD.pins = (c, t, id, cd, Q) => {
  const PINS = [-200, -120, -40, 40, 120, 200], X0 = -20, X1 = 420, n = Q.lines.filter(x => S12(t) >= x).length;
  rbox(c, -230, 0, 400, 520, { r: 18, line: 'rgba(236,230,218,.55)' }); txt(c, '芯片', -230, -200, { size: 40, fam: 'PuHui-Heavy', col: COL.creamDim, align: 'center' });
  c.save(); c.fillStyle = 'rgba(236,230,218,.5)'; PINS.forEach(y => c.fillRect(X0 - 4, y - 10, 26, 20)); c.restore();
  Q.lines.forEach((at, i) => { const q = MO.cubicInOut(seg(t, at, at + 0.25)); if (q <= 0) return;
    if (i < PINS.length) { const y = PINS[i]; c.save(); c.strokeStyle = COL.cream; c.lineWidth = 6; c.beginPath(); c.moveTo(X0 + 22, y); c.lineTo(lerp(X0 + 22, X1, q), y); c.stroke(); c.restore(); }
    else { const y = lerp(-170, 170, (i - PINS.length) / 3); c.save(); c.strokeStyle = COL.redHi; c.lineWidth = 5; c.setLineDash([10, 9]); c.beginPath(); c.moveTo(X1, y + 12); c.lineTo(lerp(X1, X0 + 40, q), y + 12); c.stroke(); c.restore();
      if (q >= 1) cross(c, X0 + 30, y + 12, 16); } });
  // 每多一条线：面积、耗电往上涨
  const g = clamp(n / Q.lines.length);
  meter(c, -260, 285, 520, 0.12 + 0.88 * g, '面积', n > 6 ? COL.redHi : COL.cream); meter(c, -260, 330, 520, 0.12 + 0.88 * g, '耗电', n > 6 ? COL.redHi : COL.cream);
};

// ---------- 很难同时到达：慢的时候还对得齐，快了以后时间窗口变窄，长一点点的那条路就晚到一步 ----------
FULL.CARD.skew = (c, t, id, cd, Q) => {
  const LANES = [-260, -180, -100, -20, 60, 140], X0 = -400, FIN = 290, v = 560, WORD = [1, 0, 1, 1, 0, 1], LATE = 3, extra = 0.16;
  const phase = t < Q.fast[0] ? Q.slow : Q.fast, fast = phase === Q.fast, win = fast ? 0.07 : 0.4;
  // 车道（第 4 条中间多绕了一小段）
  LANES.forEach((y, i) => { c.save(); c.strokeStyle = 'rgba(236,230,218,.28)'; c.lineWidth = 34; c.lineCap = 'round'; c.beginPath(); c.moveTo(X0, y);
    if (i === LATE) { c.lineTo(-40, y); c.quadraticCurveTo(0, y - 58, 40, y); } c.lineTo(FIN, y); c.stroke(); c.restore(); });
  if (S12(t) >= Q.slow[0]) { const L = MO.smooth(seg(t, Q.slow[0], Q.slow[0] + 0.3)); c.save(); c.globalAlpha = L; c.strokeStyle = COL.redHi; c.lineWidth = 5; c.setLineDash([12, 8]); c.beginPath(); c.moveTo(FIN + 34, LANES[0] - 40); c.lineTo(FIN + 34, LANES[5] + 40); c.stroke(); c.restore(); }
  // 时间窗口：终点线旁的一段亮条，慢的时候宽、快的时候窄
  const arr = phase[0] + (FIN - X0) / v;                       // 准时的那几件到达的时刻
  const open = t >= arr - 0.02 && t <= arr + win;
  txt(c, '时间窗口', FIN + 60, LANES[0] - 70, { size: 30, fam: 'PuHui-Heavy', col: COL.creamDim, align: 'center' });
  c.save(); c.fillStyle = 'rgba(236,230,218,.25)'; c.fillRect(FIN + 50, LANES[0] - 50, 20, 18); c.fillStyle = COL.cream; c.fillRect(FIN + 50, LANES[0] - 50, 20 * (fast ? 0.25 : 1) * 1, 18); c.restore();
  c.save(); c.fillStyle = open ? 'rgba(236,230,218,.22)' : 'rgba(0,0,0,0)'; c.fillRect(FIN + 14, LANES[0] - 34, 40, LANES[5] - LANES[0] + 68); c.restore();
  // 每条路一件货
  const slots = []; LANES.forEach((y, i) => { const dl = i === LATE ? extra : 0, st = phase[0], x = X0 + v * (t - st - dl);
    const arrive = st + dl + (FIN - X0) / v, inWin = arrive <= arr + win;
    if (t < st) return;
    let px = Math.min(FIN, x), py = y; if (i === LATE && px > -40 && px < 40) py = y - 58 * (1 - Math.pow((px) / 40, 2)) * 0.75;
    if (t >= arrive) { slots.push([i, inWin]); if (!inWin) { bitTile(c, WORD[i], FIN - 6, y, { s: 50, col: COL.redHi }); txt(c, '晚到', FIN - 70, y, { size: 28, fam: 'PuHui-Heavy', col: COL.redHi, align: 'right' }); } return; }
    bitTile(c, WORD[i], px, py, { s: 50 }); });
  // 拼出来的数据：右边一列
  const done = t >= arr + win + 0.05;
  LANES.forEach((y, i) => { const s = slots.find(q => q[0] === i); const x = FIN + 110;
    c.save(); c.strokeStyle = 'rgba(236,230,218,.4)'; c.lineWidth = 3; c.strokeRect(x - 25, y - 25, 50, 50); c.restore();
    if (s && s[1]) digit(c, String(WORD[i]), x, y + 2, COL.cream, 40);
    else if (done) digit(c, '?', x, y + 2, COL.redHi, 44); });
  if (done) { const ok = slots.length === LANES.length && slots.every(q => q[1]); if (ok) tick(c, FIN + 110, LANES[5] + 70, 22); else cross(c, FIN + 110, LANES[5] + 70, 20); }
};

// ---------- 很多条慢路 vs 少数几条快路 ----------
FULL.CARD.lanes = (c, t, id, cd, Q) => {
  const X0 = -400, X1 = 410;
  const many = [-240, -205, -170, -135, -100, -65, -30, 5].map(y => y - 20), few = [190, 250];
  if (t >= Q.many) many.forEach((y, i) => { c.save(); c.strokeStyle = 'rgba(236,230,218,.2)'; c.lineWidth = 3; c.beginPath(); c.moveTo(X0, y); c.lineTo(X1, y); c.stroke(); c.restore();
    pulses(c, X0 + 120 * (t - Q.many) + i * 37, 150, X0, X1, y, { h: 12, gap: 40, col: COL.cream, glow: false }); });
  if (t >= Q.few) few.forEach((y, i) => { c.save(); c.strokeStyle = 'rgba(236,230,218,.2)'; c.lineWidth = 3; c.beginPath(); c.moveTo(X0, y); c.lineTo(X1, y); c.stroke(); c.restore();
    pulses(c, X0 + 900 * (t - Q.few) + i * 11, 22, X0, Math.min(X1, X0 + 900 * (t - Q.few)), y, { h: 22, gap: 4, col: COL.cream, glow: false }); });
};

// ---------- 节拍：只看电平数不清；从高低变化推算节拍，再一个一个清点 ----------
FULL.CARD.clock = (c, t, id, cd, Q) => {
  const B = [0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 1, 0], X0 = -400, X1 = 400, bw = (X1 - X0) / B.length, HI = -230, LO = -70, xb = i => X0 + i * bw;
  const wq = MO.cubicInOut(seg(t, Q.wave, Q.wave + 0.6));
  stroke(c, X0, lerp(X0, X1, wq), x => (B[Math.min(B.length - 1, Math.floor((x - X0) / bw))] ? HI : LO), { lw: 7, step: 1 });
  txt(c, '1', X0 - 30, HI, { size: 34, fam: 'PuHui-Heavy', col: COL.creamDim, align: 'center' }); txt(c, '0', X0 - 30, LO, { size: 34, fam: 'PuHui-Heavy', col: COL.creamDim, align: 'center' });
  // 只看电平：一大段连在一起的高电平——到底几个 1？
  if (S12(t) >= Q.ask && t < Q.grid[0]) { c.save(); c.translate((xb(1) + xb(6)) / 2, HI - 70); c.rotate(Math.sin(t * 7) * 0.08); digit(c, '?', 0, 0, COL.redHi, 90); c.restore(); }
  // 高低变化的地方：先在边沿打上记号
  const edges = []; for (let i = 1; i < B.length; i++) if (B[i] !== B[i - 1]) edges.push(i);
  if (S12(t) >= Q.edges) edges.forEach(i => { c.save(); c.strokeStyle = COL.redHi; c.lineWidth = 6; c.beginPath(); c.moveTo(xb(i), HI - 40); c.lineTo(xb(i), LO + 40); c.stroke(); c.restore(); });
  // 从边沿推算出节拍：每一拍的边界（虚线）从边沿往两边铺开
  const gq = seg(t, Q.grid[0], Q.grid[1]);
  if (gq > 0) for (let i = 0; i <= B.length; i++) { const d = Math.min(...edges.map(e => Math.abs(e - i))); if (d > gq * 5 + 0.01) continue;
    c.save(); c.strokeStyle = 'rgba(236,230,218,.55)'; c.lineWidth = 3; c.setLineDash([8, 8]); c.beginPath(); c.moveTo(xb(i), HI - 60); c.lineTo(xb(i), LO + 60); c.stroke(); c.restore(); }
  // 按节拍清点：每一拍中间读一次，高电平那一段数出 1 2 3 4 5
  const cq = seg(S12(t), Q.count[0], Q.count[1]);
  if (cq > 0) { const shown = Math.floor(cq * B.length + 1e-6);
    for (let i = 0; i < Math.min(B.length, shown); i++) { const x = xb(i) + bw / 2, y = B[i] ? HI : LO;
      c.save(); c.fillStyle = COL.redHi; c.beginPath(); c.arc(x, y, 11, 0, 7); c.fill(); c.restore();
      digit(c, String(B[i]), x, LO + 70, B[i] ? COL.cream : 'rgba(236,230,218,.5)', 44);
      if (i >= 1 && i <= 5) digit(c, String(i), x, LO + 140, COL.redHi, 40); } }
};

// ---------- 速度每过几年翻一倍 → 越快越糊 → 自带「整理」，要耗电、占面积 ----------
FULL.CARD.double = (c, t, id, cd, Q) => {
  const X0 = -360, X1 = 330, ROWS = [-330, -80, 170], v = 260;
  ROWS.forEach((y, r) => { const at = Q.rows[r]; if (S12(t) < at) return; const bw = 84 / Math.pow(2, r), endS = [3, 12, 34][r];
    txt(c, ['原来', '快一倍', '再快一倍'][r], X0, y - 110, { size: 32, fam: 'PuHui-Heavy', col: COL.creamDim });
    const F = X0 + v * 3 * (t - at), sg = x => 2 + endS * Math.pow(clamp((x - X0) / (X1 - X0)), 1.4);
    const eqOn = r === 2 && t >= Q.eq, xEnd = eqOn ? X1 - 110 : X1;
    stroke(c, X0, Math.min(xEnd, F), x => y - 70 * level(x, F, bw, sg(x)) * (1 - 0.3 * clamp((x - X0) / (X1 - X0))), { lw: 5, step: 1.5 });
    if (eqOn) { const q = MO.smooth(seg(t, Q.eq, Q.eq + 0.3)); c.save(); c.globalAlpha = q; rbox(c, X1 - 40, y - 35, 120, 90, { r: 10 }); txt(c, '整理', X1 - 40, y - 35, { size: 32, fam: 'PuHui-Heavy', align: 'center' });
      if (F > X1 + 20) stroke(c, X1 + 22, Math.min(430, F), x => y - 70 * level(x, F, bw, 2) * 0.7, { lw: 5, step: 1 }); c.restore(); } });
  if (S12(t) >= Q.cost) { const q = MO.cubicInOut(seg(t, Q.cost, Q.cost + 0.8)); meter(c, -200, 360, 560, 0.2 + 0.7 * q, '耗电', COL.redHi); meter(c, -200, 410, 560, 0.2 + 0.6 * q, '面积', COL.redHi); }
};

// ---------- SerDes 嵌在各种芯片里；IP 授权 / 大公司自研 ----------
FULL.CARD.embed = (c, t, id, cd, Q) => {
  const CH = [['GPU', -200], ['交换芯片', 20], ['光模块里的芯片', 240]];
  CH.forEach(([name, y], i) => { rbox(c, -40, y, 700, 170, { r: 16, line: 'rgba(236,230,218,.55)' }); txt(c, name, -370, y, { size: 40, fam: 'PuHui-Heavy', col: COL.creamDim });
    const on = MO.smooth(seg(t, Q.blocks[i], Q.blocks[i] + 0.2));
    c.save(); c.fillStyle = on > 0 ? `rgba(236,230,218,${0.15 + 0.85 * on})` : 'rgba(236,230,218,.12)'; if (on > 0) { c.shadowColor = COL.cream; c.shadowBlur = 18 * on; }
    c.beginPath(); c.roundRect(180, y - 40, 120, 80, 10); c.fill(); c.restore();
    txt(c, 'SerDes', 240, y, { size: 28, fam: 'PuHui-Heavy', col: on > 0.5 ? COL.ink : 'rgba(236,230,218,.5)', align: 'center' }); });
  const tag = (text, x, y, at, col) => { if (S12(t) < at) return; const pop = S12(t) - at < 1 / 12 ? 1.1 : 1; c.save(); c.translate(x, y); c.scale(pop, pop); c.rotate(-0.03);
    c.fillStyle = col; c.font = '36px "PuHui-Heavy"'; const w = c.measureText(text).width + 40; c.beginPath(); c.roundRect(-w / 2, -30, w, 60, 8); c.fill();
    txt(c, text, 0, 2, { size: 36, fam: 'PuHui-Heavy', col: col === COL.red ? '#f6efe4' : COL.ink, align: 'center' }); c.restore(); };
  tag('IP 授权给芯片公司', -190, 400, Q.ip, COL.cream); tag('大公司多半自研', 230, 400, Q.own, COL.red);
};
})();
