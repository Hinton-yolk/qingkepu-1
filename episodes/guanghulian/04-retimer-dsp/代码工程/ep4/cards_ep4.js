// 第四篇的黑卡片（3b1b 式：一次只动一样东西；米白＝电信号，红＝编辑的笔）。坐标原点在卡片中心，时间点来自 ep4/desk.json 的 cue。
(() => {
const { clamp, lerp } = U; const { COL, txt, seg, S12 } = FULL;
const { bitOf, level, stroke, digit, rbox, axis, bracket } = FULL.H;
const cross = (c, x, y, s = 20) => { c.save(); c.strokeStyle = COL.redHi; c.lineWidth = 7; c.lineCap = 'round'; c.beginPath(); c.moveTo(x - s, y - s); c.lineTo(x + s, y + s); c.moveTo(x + s, y - s); c.lineTo(x - s, y + s); c.stroke(); c.restore(); };
const tick = (c, x, y, s = 20) => { c.save(); c.strokeStyle = COL.cream; c.lineWidth = 7; c.lineCap = 'round'; c.lineJoin = 'round'; c.beginPath(); c.moveTo(x - s, y); c.lineTo(x - s * 0.3, y + s * 0.7); c.lineTo(x + s, y - s * 0.8); c.stroke(); c.restore(); };
const box = (c, x, y, w, h, name, { hot = 0, size = 32 } = {}) => { rbox(c, x, y, w, h, { r: 12, line: hot > 0.05 ? `rgba(217,96,79,${0.5 + 0.5 * hot})` : 'rgba(236,230,218,.75)', lw: 3 + 3 * hot }); txt(c, name, x, y, { size, fam: 'PuHui-Heavy', align: 'center' }); };
const meter = (c, x, y, w, q, name, col = COL.cream) => { txt(c, name, x - 18, y, { size: 30, fam: 'PuHui-Heavy', col: COL.creamDim, align: 'right' });
  c.save(); c.strokeStyle = 'rgba(236,230,218,.4)'; c.lineWidth = 3; c.strokeRect(x, y - 15, w, 30); c.fillStyle = col; c.fillRect(x + 4, y - 11, (w - 8) * clamp(q), 22); c.restore(); };
const BITS2 = [1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0];
const bitAt = k => BITS2[((k % 16) + 16) % 16];

// ---------- 钩子：糊的信号进检修站，出来又清楚了 ----------
FULL.CARD.hook4 = (c, t, id, cd, Q) => {
  const X0 = -400, X1 = 400, BX = 0, Y = -30, A = 90, bw = 56, v = 360, sgIn = 34;
  const F = X0 + v * (t - Q.e0), Fo = (BX + 90) + v * (t - Q.e0 - (BX - 90 - X0) / v - 0.2);
  if (t > Q.e0) stroke(c, X0, Math.min(BX - 92, F + 4 * sgIn), x => Y - A * 0.62 * level(x, F, bw, sgIn * clamp((x - X0) / 120 + 0.3)), { lw: 6 });
  for (let k = 0; k < 40; k++) { const xc = F - (k + 0.5) * bw; if (xc < X0 + 60 || xc > BX - 100) continue; c.save(); c.translate(xc, Y - A - 40); c.rotate(Math.sin(t * 9 + k) * 0.12); digit(c, '?', 0, 0, COL.redHi, 46); c.restore(); }
  if (Fo > BX + 90) { stroke(c, BX + 92, Math.min(X1, Fo), x => Y - A * level(x, Fo, bw, 2), { lw: 6, step: 1 });
    for (let k = 0; k < 40; k++) { const xc = Fo - (k + 0.5) * bw; if (xc < BX + 110 || xc > X1 - 10) continue; digit(c, String(bitOf(k)), xc, Y - A - 40, COL.cream, 46); } }
  const hot = F > BX - 92 ? Math.max(0, 1 - Math.abs(((t - Q.e0) * 2) % 1 - 0.5) * 2) * 0.6 : 0;
  box(c, BX, Y - 30, 180, 150, '检修站', { hot });
  axis(c, X0, X1, 330, MO.smooth(seg(t, Q.e0, Q.e0 + 0.5)));
};

// ---------- 走廊里的传话员：前半程越走越小越糊；传话员听清以后，用自己的嗓子重新喊 ----------
FULL.CARD.relay = (c, t, id, cd, Q) => {
  const X0 = -400, X1 = 410, Y = 10, v = 230, MID = 0, WORDS = ['数', '据', '到', '站', '了', '吗'];
  c.save(); c.strokeStyle = 'rgba(236,230,218,.4)'; c.lineWidth = 4; c.beginPath(); c.moveTo(X0, Y - 120); c.lineTo(X1, Y - 120); c.moveTo(X0, Y + 120); c.lineTo(X1, Y + 120); c.stroke(); c.restore();
  txt(c, '听', X0 + 10, Y - 170, { size: 34, fam: 'PuHui-Heavy', col: COL.creamDim, align: 'center' }); txt(c, '喊', X1 - 10, Y - 170, { size: 34, fam: 'PuHui-Heavy', col: COL.creamDim, align: 'center' });
  // 传话员（中间）：开始工作以后亮起来
  const on = t >= Q.relay, oq = MO.smooth(seg(t, Q.relay, Q.relay + 0.3));
  c.save(); c.globalAlpha = 0.45 + 0.55 * oq; c.fillStyle = on ? COL.red : 'rgba(236,230,218,.35)';
  c.beginPath(); c.arc(MID, Y + 150, 22, 0, 7); c.fill(); c.beginPath(); c.roundRect(MID - 26, Y + 176, 52, 60, 14); c.fill(); c.restore();
  txt(c, '传话员', MID, Y + 270, { size: 28, fam: 'PuHui-Heavy', col: on ? COL.redHi : COL.creamDim, align: 'center' });
  if (on) { c.save(); c.strokeStyle = COL.redHi; c.lineWidth = 4; c.setLineDash([8, 8]); c.beginPath(); c.moveTo(MID, Y - 120); c.lineTo(MID, Y + 120); c.stroke(); c.restore(); }
  Q.words.forEach((at, i) => { if (t < at) return; const d = v * (t - at), x = X1 - 30 - d; if (x < X0 - 40) return;
    const passed = x < MID, relayed = passed && (at + (X1 - 30 - MID) / v) >= Q.relay;
    let f = clamp((X1 - 30 - Math.max(x, MID)) / (X1 - 30 - MID));
    if (passed) f = relayed ? clamp((MID - x) / (MID - X0)) * 0.7 : clamp(1 + (MID - x) / (MID - X0) * 0.6);
    const size = lerp(96, 46, f), a = lerp(1, 0.4, f);
    for (let j = 6; j >= 1; j--) { const back = -j * lerp(8, 32, f); c.save(); c.globalAlpha = a * 0.22 * (1 - j / 7); txt(c, WORDS[i], x - back, Y, { size, fam: 'PuHui-Heavy', col: COL.cream, align: 'center' }); c.restore(); }
    c.save(); c.globalAlpha = a; txt(c, WORDS[i], x, Y, { size, fam: 'PuHui-Heavy', col: relayed ? COL.cream : COL.cream, align: 'center' }); c.restore(); });
};

// ---------- 均衡：不补 → 发送端先把跳变加强 → 接收端再补回来 ----------
const EQ = (() => { const B = [0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 1], bw = 70, n = B.length * bw, tau = 55, a = 1 - Math.exp(-1 / tau), A = 0.6, cc = 0.8;
  const x = Array.from({ length: n }, (_, i) => B[Math.floor(i / bw)]);
  const ch = s => { const y = new Array(s.length); let v = 0; for (let i = 0; i < s.length; i++) { v += (s[i] - v) * a; y[i] = v; } return y; };
  const xpe = x.map((v, i) => (v + A * (v - (i >= bw ? x[i - bw] : 0))) / (1 + A));
  const y0 = ch(x), y1 = ch(xpe), z = y1.map((v, i) => v + cc * tau * ((y1[Math.min(n - 1, i + 1)] - y1[Math.max(0, i - 1)]) / 2));
  const norm = arr => { const lo = Math.min(...arr), hi = Math.max(...arr); return arr.map(v => (v - lo) / (hi - lo)); };
  return { B, bw, n, x, xpe: xpe.map(v => (v + A / (1 + A)) / ((1 + 2 * A) / (1 + A))), y0: norm(y0), z: norm(z) }; })();
FULL.CARD.eq = (c, t, id, cd, Q) => {
  const X0 = -420, H = 150, sc = 840 / EQ.n, rows = [{ y: -350, arr: EQ.y0 }, { y: 50, arr: EQ.xpe }, { y: 450, arr: EQ.z }];
  rows.forEach((R, i) => { const at = Q.rows[i]; if (t < at) return; const q = MO.smooth(seg(t, at, at + 1.2)), xe = Math.floor(EQ.n * q);
    // 理想的方正台阶（虚线，对照）
    c.save(); c.strokeStyle = 'rgba(236,230,218,.3)'; c.lineWidth = 3; c.setLineDash([10, 10]); c.beginPath(); for (let k = 0; k < EQ.n; k += 2) { const yy = R.y - H * EQ.x[k]; k ? c.lineTo(X0 + k * sc, yy) : c.moveTo(X0, yy); } c.stroke(); c.restore();
    c.save(); c.strokeStyle = i === 1 ? COL.cream : COL.cream; c.lineWidth = 6; c.lineJoin = 'round'; c.beginPath();
    for (let k = 0; k < xe; k += 2) { const yy = R.y - H * R.arr[k]; k ? c.lineTo(X0 + k * sc, yy) : c.moveTo(X0, yy); } c.stroke(); c.restore();
    if (i === 1 && q > 0.3) { for (let k = 1; k < EQ.B.length; k++) { if (EQ.B[k] === EQ.B[k - 1] || k * EQ.bw > xe) continue; const xx = X0 + (k * EQ.bw + 6) * sc, yy = R.y - H * EQ.xpe[k * EQ.bw + 2];
      c.save(); c.fillStyle = COL.redHi; c.beginPath(); c.arc(xx, yy, 9, 0, 7); c.fill(); c.restore(); } }
    if (q >= 1) { if (i === 0) cross(c, 395, R.y - H - 30, 18); if (i === 2) tick(c, 395, R.y - H - 30, 22); } });
};

// ---------- Retimer：路中间重新出发；原话听错时，清楚地发出错的 ----------
FULL.CARD.retimer = (c, t, id, cd, Q) => {
  const run = (y, at, blurMax, flipK) => { if (t < at) return; const xa = -400, bx = 0, xb = 400, bw = 50, v = 500, A = 70;
    c.save(); c.strokeStyle = 'rgba(236,230,218,.25)'; c.lineWidth = 8; c.beginPath(); c.moveTo(xa, y + 40); c.lineTo(xb, y + 40); c.stroke(); c.restore();
    const F = xa + v * (t - at), sg = x => 2 + blurMax * Math.pow(clamp((x - xa) / (bx - 80 - xa)), 1.3);
    stroke(c, xa, Math.min(bx - 82, F), x => y - A * (1 - 0.35 * clamp((x - xa) / (bx - xa))) * level(x, F, bw, sg(x)), { lw: 5, step: 1.5 });
    const arr = at + (bx - 80 - xa) / v, Fo = bx + 80 + v * (t - arr - 0.25);
    const outBit = k => (k === flipK ? 1 - bitOf(k) : bitOf(k));
    const read = Math.max(0, Math.min(14, Math.floor((t - arr) / (bw / v))));
    if (t > arr) for (let k = 0; k < Math.min(read, 7); k++) digit(c, String(outBit(k)), bx - 66 + k * 22, y - 100, k === flipK ? COL.redHi : COL.cream, 26);
    box(c, bx, y, 160, 110, 'Retimer', { hot: t > arr && t < arr + 0.4 ? 0.8 : 0, size: 30 });
    if (Fo > bx + 80) { stroke(c, bx + 80, Math.min(xb, Fo), x => { const k = Math.floor((Fo - x) / bw); return Fo - x < 0 ? y : y - A * outBit(k); }, { lw: 5, step: 1 });
      for (let k = 0; k < 12; k++) { const xc = Fo - (k + 0.5) * bw; if (xc < bx + 100 || xc > xb - 10) continue;
        if (k === flipK) { c.save(); c.fillStyle = 'rgba(217,96,79,.35)'; c.fillRect(xc - bw / 2 + 2, y - A - 8, bw - 4, A + 16); c.restore(); }
        digit(c, String(outBit(k)), xc, y - A - 38, k === flipK ? COL.redHi : COL.cream, 40); } }
    if (Fo > xb + 40) { if (flipK < 0) tick(c, xb - 10, y + 100, 22); else cross(c, xb - 10, y + 100, 20); } };
  run(-260, Q.ok, 28, -1);
  run(260, Q.bad, 80, 2);
};

// ---------- Redriver vs Retimer ----------
FULL.CARD.redriver = (c, t, id, cd, Q) => {
  const pipe = (y, at, name, outSg, steps) => { if (t < at) return; const xa = -400, bx = 0, xb = 400, bw = 50, v = 600, A = 64;
    const F = xa + v * (t - at), Fo = bx + 120 + v * (t - at - (bx - 120 - xa) / v - 0.2);
    stroke(c, xa, Math.min(bx - 122, F), x => y - A * 0.62 * level(x, F, bw, 30), { lw: 5, step: 1.5 });
    rbox(c, bx, y - 30, 240, 120, { r: 12, line: 'rgba(236,230,218,.75)' }); txt(c, name, bx, y - 62, { size: 30, fam: 'PuHui-Heavy', align: 'center' });
    steps.forEach((s, i) => { const on = t >= at + 0.6 + i * 0.5; c.save(); c.globalAlpha = on ? 1 : 0.3; txt(c, s, bx - (steps.length - 1) * 38 + i * 76, y - 14, { size: 22, fam: 'PuHui-Heavy', col: on ? COL.redHi : COL.cream, align: 'center' }); c.restore(); });
    if (Fo > bx + 120) stroke(c, bx + 122, Math.min(xb, Fo), x => y - A * level(x, Fo, bw, outSg), { lw: 5, step: 1.5 }); };
  pipe(-300, Q.rd, 'Redriver', 13, ['均衡']);
  pipe(100, Q.rt, 'Retimer', 2, ['均衡', '认0/1', '打节拍']);
  if (t >= Q.meters) { const q = MO.cubicInOut(seg(t, Q.meters, Q.meters + 0.8));
    txt(c, 'Redriver', -200, 300, { size: 28, fam: 'PuHui-Heavy', col: COL.creamDim, align: 'center' }); txt(c, 'Retimer', 230, 300, { size: 28, fam: 'PuHui-Heavy', col: COL.creamDim, align: 'center' });
    meter(c, -330, 350, 260, 0.25 * q, '耗电'); meter(c, -330, 400, 260, 0.2 * q, '延迟');
    meter(c, 110, 350, 260, 0.7 * q, '', COL.redHi); meter(c, 110, 400, 260, 0.62 * q, '', COL.redHi); }
};

// ---------- DSP：采样成数字 → 前后几个一起算 → 原本的数据 ----------
FULL.CARD.dspcalc = (c, t, id, cd, Q) => {
  const B = [1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1], X0 = -400, X1 = 400, bw = (X1 - X0) / B.length, Y = -380, A = 120, sg = 24;
  const P = x => 1 / (1 + Math.exp(-1.702 * x));
  const lvl = x => { let y = 0; for (let k = 0; k < B.length; k++) if (B[k]) y += P((x - (X0 + k * bw)) / sg) - P((x - (X0 + (k + 1) * bw)) / sg); return 0.12 + 0.76 * y; };
  const wq = MO.smooth(seg(t, Q.wave, Q.wave + 0.6)); if (wq > 0) stroke(c, X0, lerp(X0, X1, wq), x => Y + A / 2 - A * lvl(x), { lw: 6 });
  const ns = t < Q.samples[0] ? 0 : Math.min(B.length, Math.floor((t - Q.samples[0]) / ((Q.samples[1] - Q.samples[0]) / B.length)) + 1);
  for (let k = 0; k < ns; k++) { const x = X0 + (k + 0.5) * bw, v = lvl(x); c.save(); c.fillStyle = COL.redHi; c.beginPath(); c.arc(x, Y + A / 2 - A * v, 9, 0, 7); c.fill(); c.restore();
    txt(c, v.toFixed(2), x, Y + A / 2 + 50 + (k % 2) * 34, { size: 26, fam: 'PuHui-Heavy', col: COL.cream, align: 'center' }); }
  // 计算：一个窗口框住前后几个采样，推算中间那一位
  const nb = t < Q.bits[0] ? 0 : Math.min(B.length, Math.floor((t - Q.bits[0]) / ((Q.bits[1] - Q.bits[0]) / B.length)) + 1);
  if (t >= Q.win) { const k = Math.min(B.length - 1, Math.max(0, nb - 1)), xc = X0 + (k + 0.5) * bw;
    c.save(); c.strokeStyle = COL.redHi; c.lineWidth = 5; c.strokeRect(Math.max(X0, xc - 2.5 * bw), Y - A / 2 - 20, Math.min(X1, xc + 2.5 * bw) - Math.max(X0, xc - 2.5 * bw), A + 140); c.restore();
    box(c, 0, 240, 200, 110, '计算', { hot: 0.5 });
    c.save(); c.strokeStyle = 'rgba(217,96,79,.6)'; c.lineWidth = 3; c.setLineDash([8, 8]); c.beginPath(); c.moveTo(xc, Y + A / 2 + 110); c.lineTo(0, 185); c.stroke(); c.restore(); }
  for (let k = 0; k < nb; k++) { const x = X0 + (k + 0.5) * bw; digit(c, String(B[k]), x, 380, COL.cream, 52); }
};

// ---------- DSP 在哪：SerDes 里、Retimer 里、光模块里的 DSP 芯片 ----------
FULL.CARD.where = (c, t, id, cd, Q) => {
  const ROWS = [['SerDes', -200], ['Retimer', 20], ['光模块里的芯片', 240]];
  ROWS.forEach(([name, y], i) => { rbox(c, -40, y, 700, 170, { r: 16, line: 'rgba(236,230,218,.55)' }); txt(c, name, -370, y, { size: 38, fam: 'PuHui-Heavy', col: COL.creamDim });
    const on = MO.smooth(seg(t, Q.blocks[i], Q.blocks[i] + 0.2));
    c.save(); c.fillStyle = on > 0 ? `rgba(236,230,218,${0.15 + 0.85 * on})` : 'rgba(236,230,218,.12)'; if (on > 0) { c.shadowColor = COL.cream; c.shadowBlur = 18 * on; }
    c.beginPath(); c.roundRect(180, y - 40, 120, 80, 10); c.fill(); c.restore();
    txt(c, i === 2 ? 'oDSP' : 'DSP', 240, y, { size: 30, fam: 'PuHui-Heavy', col: on > 0.5 ? COL.ink : 'rgba(236,230,218,.5)', align: 'center' }); });   // 光模块里的那颗写 oDSP（用户 2026-11-07：以作区分）
};

// ---------- 代价：路况越差，处理越重，越耗电、延迟越多 ----------
FULL.CARD.cost = (c, t, id, cd, Q) => {
  const ROWS = [{ y: -300, name: '路况好', sg: 3, steps: ['均衡'], p: 0.22 }, { y: -40, name: '路况一般', sg: 14, steps: ['均衡', '打节拍'], p: 0.5 }, { y: 220, name: '路况差', sg: 30, steps: ['均衡', '打节拍', 'DSP'], p: 0.85 }];
  ROWS.forEach((R, i) => { const at = Q.rows[i]; if (t < at) return; const q = MO.cubicInOut(seg(t, at, at + 0.6));
    txt(c, R.name, -420, R.y - 75, { size: 30, fam: 'PuHui-Heavy', col: COL.creamDim });
    stroke(c, -420, -200, x => R.y - 50 * level(x, -200 + 400 * (t - at), 34, R.sg) * (1 - R.sg / 60), { lw: 4, step: 1.5 });
    R.steps.forEach((s, j) => { const on = t >= at + 0.2 + j * 0.25; if (!on) return; rbox(c, -120 + j * 105, R.y - 25, 96, 66, { r: 10, line: COL.redHi }); txt(c, s, -120 + j * 105, R.y - 25, { size: s.length > 2 ? 22 : 26, fam: 'PuHui-Heavy', align: 'center' }); });
    meter(c, 250, R.y - 45, 160, R.p * q, '耗电', i === 2 ? COL.redHi : COL.cream); meter(c, 250, R.y, 160, R.p * 0.9 * q, '延迟', i === 2 ? COL.redHi : COL.cream); });
};

// ---------- 范围：核心电路 ⊂ 整颗芯片 ⊂ 整条链路；少放一颗 DSP，工作转给了主芯片 ----------
FULL.CARD.scope = (c, t, id, cd, Q) => {
  const mv = MO.cubicInOut(seg(t, Q.move[0], Q.move[1])), gone = seg(t, Q.move[1] - 0.2, Q.move[1] + 0.3);
  const frame = (x0, y0, x1, y1, name, at, col) => { if (S12(t) < at) return; const pop = S12(t) - at < 1 / 12 ? 1.04 : 1; c.save(); c.translate((x0 + x1) / 2, (y0 + y1) / 2); c.scale(pop, pop); c.translate(-(x0 + x1) / 2, -(y0 + y1) / 2);
    c.strokeStyle = col; c.lineWidth = 4; c.setLineDash([12, 8]); c.strokeRect(x0, y0, x1 - x0, y1 - y0); c.setLineDash([]); txt(c, name, x0 + 14, y0 + 24, { size: 26, fam: 'PuHui-Heavy', col }); c.restore(); };
  // 两颗芯片和中间的链路
  rbox(c, -230, -80, 300, 420, { r: 14, line: 'rgba(236,230,218,.7)' }); txt(c, '主芯片', -230, 90, { size: 32, fam: 'PuHui-Heavy', col: COL.creamDim, align: 'center' });
  c.save(); c.globalAlpha = 1 - gone * 0.75; rbox(c, 250, -80, 240, 300, { r: 14, line: 'rgba(236,230,218,.7)' }); txt(c, 'DSP 芯片', 250, 40, { size: 30, fam: 'PuHui-Heavy', col: COL.creamDim, align: 'center' }); c.restore();
  if (gone > 0.5) cross(c, 250, -80, 40);
  c.save(); c.strokeStyle = 'rgba(236,230,218,.5)'; c.lineWidth = 8; c.beginPath(); c.moveTo(-80, -80); c.lineTo(130, -80); c.stroke(); c.restore();
  // DSP 这份工作：从 DSP 芯片挪进主芯片
  const bx = lerp(250, -230, mv), by = lerp(-130, -10, mv);
  c.save(); c.fillStyle = COL.cream; c.beginPath(); c.roundRect(bx - 60, by - 30, 120, 60, 10); c.fill(); c.restore(); txt(c, 'DSP 工作', bx, by, { size: 24, fam: 'PuHui-Heavy', col: COL.ink, align: 'center' });
  frame(-340, -260, -120, -160, '核心电路', Q.core, COL.cream);
  frame(-400, -310, -60, 150, '整颗芯片', Q.chip, COL.creamDim);
  frame(-430, -360, 430, 210, '整条链路', Q.link, COL.redHi);
  if (S12(t) >= Q.link) { const up = mv;
    meter(c, -120, 290, 420, 0.35 + 0.3 * up, '主芯片报的功耗', up > 0.5 ? COL.redHi : COL.cream);
    meter(c, -120, 350, 420, 0.7, '整条链路的功耗'); if (up >= 1) txt(c, '≈ 不变', 312, 350, { size: 26, fam: 'PuHui-Heavy', col: COL.creamDim, align: 'left' }); }
};
})();
