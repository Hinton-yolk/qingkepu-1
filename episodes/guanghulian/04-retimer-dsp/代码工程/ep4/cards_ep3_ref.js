// 第三篇的黑卡片（3b1b 式：一次只动一样东西；米白＝电信号，青绿＝光，红＝编辑的笔）。坐标原点在卡片中心，时间点来自 ep3/desk.json 的 cue。
(() => {
const { clamp, lerp } = U; const { COL, txt, seg, S12 } = FULL;
const { bitOf, level, stroke, digit, rbox, axis, bracket, tint } = FULL.H;
const cross = (c, x, y, s = 20) => { c.save(); c.strokeStyle = COL.redHi; c.lineWidth = 7; c.lineCap = 'round'; c.beginPath(); c.moveTo(x - s, y - s); c.lineTo(x + s, y + s); c.moveTo(x + s, y - s); c.lineTo(x - s, y + s); c.stroke(); c.restore(); };
const tick = (c, x, y, s = 20) => { c.save(); c.strokeStyle = COL.cream; c.lineWidth = 7; c.lineCap = 'round'; c.lineJoin = 'round'; c.beginPath(); c.moveTo(x - s, y); c.lineTo(x - s * 0.3, y + s * 0.7); c.lineTo(x + s, y - s * 0.8); c.stroke(); c.restore(); };
const chip = (c, x, y, name) => { rbox(c, x, y, 120, 120, { r: 12, line: 'rgba(236,230,218,.6)' }); txt(c, name, x, y, { size: 30, fam: 'PuHui-Heavy', col: COL.creamDim, align: 'center' }); };
// 一阶低通的比特响应：第 k 位占 [k·bw, (k+1)·bw]，τ 越大拖尾越长
const g1 = (u, tau) => (u <= 0 ? 0 : 1 - Math.exp(-u / tau));
const bitResp = (x, k, bw, tau) => g1(x - k * bw, tau) - g1(x - (k + 1) * bw, tau);

// ---------- 走廊里喊话：字越走越小，余音拖在后面，下一个字又到了 ----------
FULL.CARD.corridor = (c, t, id, cd, Q) => {
  const X0 = -400, X1 = 410, Y = 10, v = 230, WORDS = ['数', '据', '出', '发', '了', '吗'];
  c.save(); c.strokeStyle = 'rgba(236,230,218,.4)'; c.lineWidth = 4;
  c.beginPath(); c.moveTo(X0, Y - 120); c.lineTo(X1, Y - 120); c.moveTo(X0, Y + 120); c.lineTo(X1, Y + 120); c.stroke();
  for (let x = X0 + 60; x < X1; x += 120) { c.globalAlpha = 0.25; c.beginPath(); c.moveTo(x, Y - 120); c.lineTo(x, Y - 104); c.moveTo(x, Y + 120); c.lineTo(x, Y + 104); c.stroke(); }
  c.restore();
  txt(c, '听', X0 + 10, Y - 170, { size: 34, fam: 'PuHui-Heavy', col: COL.creamDim, align: 'center' }); txt(c, '喊', X1 - 10, Y - 170, { size: 34, fam: 'PuHui-Heavy', col: COL.creamDim, align: 'center' });
  Q.words.forEach((at, i) => { if (t < at) return; const d = v * (t - at), x = X1 - 30 - d; if (x < X0 - 40) return;
    const f = clamp(d / (X1 - X0)), size = lerp(96, 40, f), a = lerp(1, 0.45, f);
    // 余音：身后一串越来越淡的影子，跑得越远拖得越长
    const n = 6; for (let j = n; j >= 1; j--) { const back = -j * lerp(10, 34, f); c.save(); c.globalAlpha = a * 0.22 * (1 - j / (n + 1)); txt(c, WORDS[i], x - back, Y, { size, fam: 'PuHui-Heavy', col: COL.cream, align: 'center' }); c.restore(); }
    c.save(); c.globalAlpha = a; txt(c, WORDS[i], x, Y, { size, fam: 'PuHui-Heavy', col: COL.cream, align: 'center' }); c.restore(); });
  // 走廊尽头：前一个字的余音和后一个字叠在一起
  if (t >= Q.words[3]) { const q = MO.smooth(seg(t, Q.words[3], Q.words[3] + 0.4)); c.save(); c.globalAlpha = q; c.strokeStyle = COL.redHi; c.lineWidth = 5; c.setLineDash([10, 8]); c.strokeRect(X0 + 10, Y - 90, 190, 180); c.restore(); }
};

// ---------- 变弱：理想的方正台阶，跑远了高低差距被压缩 ----------
FULL.CARD.weaken = (c, t, id, cd, Q) => {
  const X0 = -400, X1 = 400, MID = -40, A = 150, bw = 80, v = 520;
  const amp = x => lerp(1, 0.32, clamp((x - X0) / (X1 - X0)));
  const F = X0 + v * (t - Q.wave);
  if (t > Q.wave) stroke(c, X0, Math.min(X1, F), x => { const k = Math.floor((F - x) / bw), b = F - x < 0 ? 0 : bitOf(k); return MID - (b - 0.5) * 2 * (A / 2) * amp(x); }, { lw: 7, step: 1 });
  // 高、低电平的包络（虚线）往中间收拢
  const e = MO.cubicInOut(seg(t, Q.env, Q.env + 0.8));
  if (e > 0) { c.save(); c.strokeStyle = COL.redHi; c.lineWidth = 4; c.setLineDash([12, 9]); c.beginPath();
    for (const sgn of [1, -1]) { c.moveTo(X0, MID - sgn * A / 2); for (let x = X0; x <= lerp(X0, X1, e); x += 8) c.lineTo(x, MID - sgn * (A / 2) * amp(x)); } c.stroke(); c.restore();
    if (e >= 1) { c.save(); c.strokeStyle = COL.cream; c.lineWidth = 5; c.lineCap = 'round';
      const arrow = (x, h) => { c.beginPath(); c.moveTo(x, MID - h); c.lineTo(x, MID + h); c.stroke(); c.beginPath(); c.moveTo(x - 12, MID - h + 14); c.lineTo(x, MID - h); c.lineTo(x + 12, MID - h + 14); c.moveTo(x - 12, MID + h - 14); c.lineTo(x, MID + h); c.lineTo(x + 12, MID + h - 14); c.stroke(); };
      arrow(X0 + 40, A / 2 * amp(X0 + 40) + 6); arrow(X1 - 30, A / 2 * amp(X1 - 30) + 6); c.restore(); } }
  axis(c, X0, X1, 200, MO.smooth(seg(t, Q.wave, Q.wave + 0.5)));
};

// ---------- 拖尾：一个比特拖出尾巴；一串比特的尾巴叠在一起 = 码间干扰 ----------
FULL.CARD.tail = (c, t, id, cd, Q) => {
  const X0 = -400, bw = 100, tau = 72, Y1 = -280, H = 150, Y2 = 300, H2 = 150, SEQ = [1, 0, 0, 1, 1, 0, 1, 0];
  // 上：一个比特。先是方正的，再变成拖着尾巴的
  const slots = (y, n, hgt) => { c.save(); c.strokeStyle = 'rgba(236,230,218,.25)'; c.lineWidth = 2; c.setLineDash([6, 8]); for (let k = 0; k <= n; k++) { c.beginPath(); c.moveTo(X0 + k * bw, y + 20); c.lineTo(X0 + k * bw, y - hgt - 30); c.stroke(); } c.restore();
    c.save(); c.strokeStyle = 'rgba(236,230,218,.35)'; c.lineWidth = 3; c.beginPath(); c.moveTo(X0, y); c.lineTo(X0 + n * bw, y); c.stroke(); c.restore(); };
  if (t >= Q.single) { slots(Y1, 8, H); const m = MO.cubicInOut(seg(t, Q.morph[0], Q.morph[1]));
    const f = x => { const sq = x >= X0 && x < X0 + bw ? 1 : 0, r = bitResp(x - X0, 0, bw, tau) / (1 - Math.exp(-bw / tau)) * 0.92; return lerp(sq, r, m); };
    if (m > 0.98) { c.save(); c.fillStyle = 'rgba(217,96,79,.28)'; c.beginPath(); c.moveTo(X0 + bw, Y1); for (let x = X0 + bw; x <= X0 + 8 * bw; x += 3) c.lineTo(x, Y1 - H * f(x)); c.lineTo(X0 + 8 * bw, Y1); c.closePath(); c.fill(); c.restore(); }
    stroke(c, X0, X0 + 8 * bw, x => Y1 - H * f(x), { lw: 7, step: 2 });
    digit(c, '1', X0 + bw / 2, Y1 + 50, COL.cream, 44);
    if (m > 0.98) txt(c, '尾巴', X0 + 2.6 * bw, Y1 - 60, { size: 36, fam: 'PuHui-Heavy', col: COL.redHi, align: 'center' }); }
  // 下：一串比特。各自的响应（淡），叠加以后的实际波形（粗）
  if (t >= Q.seq) { slots(Y2, SEQ.length, H2); const q = seg(t, Q.seq, Q.seq + 0.9);
    SEQ.forEach((b, k) => { if (!b) return; const qk = clamp(q * SEQ.length - k * 0.6); if (qk <= 0) return;
      c.save(); c.globalAlpha = 0.55 * qk; stroke(c, X0, X0 + SEQ.length * bw, x => Y2 - H2 * 0.92 * bitResp(x - X0, k, bw, tau) / (1 - Math.exp(-bw / tau)), { lw: 3, step: 2, col: k % 2 ? 'rgba(236,230,218,.9)' : 'rgba(217,96,79,.95)' }); c.restore(); });
    SEQ.forEach((b, k) => digit(c, String(b), X0 + (k + 0.5) * bw, Y2 + 50, b ? COL.cream : 'rgba(236,230,218,.5)', 42));
    if (t >= Q.sum) { const sq = MO.smooth(seg(t, Q.sum, Q.sum + 0.5)); const sum = x => SEQ.reduce((a, b, k) => a + (b ? bitResp(x - X0, k, bw, tau) / (1 - Math.exp(-bw / tau)) * 0.92 : 0), 0);
      c.save(); c.globalAlpha = sq; stroke(c, X0, X0 + SEQ.length * bw, x => Y2 - H2 * Math.min(1.25, sum(x)), { lw: 7, step: 2 }); c.restore();
      // 本该是 0 的格子被尾巴抬了起来
      SEQ.forEach((b, k) => { if (b) return; const xc = X0 + (k + 0.5) * bw, lift = sum(xc); if (lift < 0.12) return; c.save(); c.globalAlpha = sq * 0.3; c.fillStyle = COL.redHi; c.fillRect(X0 + k * bw + 3, Y2 - H2 * lift, bw - 6, H2 * lift); c.restore(); }); }
    if (t >= Q.ask) SEQ.forEach((b, k) => { if (b) return; const xc = X0 + (k + 0.5) * bw; c.save(); c.translate(xc, Y2 - H2 - 50); c.rotate(Math.sin(t * 8 + k) * 0.1); digit(c, '?', 0, 0, COL.redHi, 50); c.restore(); }); }
};

// ---------- 越快越糟：台阶窄了一半，尾巴还是那么长，压到更多比特上 ----------
FULL.CARD.faster = (c, t, id, cd, Q) => {
  const X0 = -400, X1 = 400, tau = 70;
  const row = (y, bw, tauR, at, hitAt) => { if (t < at) return; const n = Math.round((X1 - X0) / bw), H = 140, q = seg(t, at, at + 0.6);
    c.save(); c.strokeStyle = 'rgba(236,230,218,.25)'; c.lineWidth = 2; c.setLineDash([6, 8]); for (let k = 0; k <= n; k++) { c.beginPath(); c.moveTo(X0 + k * bw, y + 16); c.lineTo(X0 + k * bw, y - H - 20); c.stroke(); } c.restore();
    const f = x => bitResp(x - X0, 0, bw, tauR) / (1 - Math.exp(-bw / tauR));
    stroke(c, X0, lerp(X0, X1, q), x => y - H * 0.9 * Math.min(1, f(x)), { lw: 6, step: 1.5 });
    if (t >= hitAt) { const hq = MO.smooth(seg(t, hitAt, hitAt + 0.4)); let k = 1;
      for (; k < n; k++) { const xc = X0 + (k + 0.5) * bw; if (f(xc) < 0.1) break; c.save(); c.globalAlpha = 0.32 * hq; c.fillStyle = COL.redHi; c.fillRect(X0 + k * bw + 2, y - H, bw - 4, H); c.restore(); }
      bracket(c, X0 + bw, X0 + k * bw, y + 40, COL.redHi); } };
  row(-250, 160, tau, Q.rowA, Q.hitA);
  row(150, 80, tau * 1.15, Q.rowB, Q.hitB);
};

// ---------- 三种思路之一、二：把路修短、把路修好 ----------
FULL.CARD.fixes = (c, t, id, cd, Q) => {
  const ROWS = [{ y: -310, len: 620, loss: 1.0 }, { y: 20, len: 260, loss: 1.0 }, { y: 350, len: 620, loss: 0.3 }], bw = 46, v = 700;
  ROWS.forEach((R, i) => { const at = Q.rows[i]; if (t < at) return; const xa = -330, xb = xa + R.len;
    chip(c, xa - 70, R.y, 'A'); chip(c, xb + 70, R.y, 'B');
    c.save(); c.strokeStyle = i === 2 ? 'rgba(236,230,218,.75)' : 'rgba(236,230,218,.3)'; c.lineWidth = i === 2 ? 14 : 8; c.beginPath(); c.moveTo(xa, R.y + 40); c.lineTo(xb, R.y + 40); c.stroke(); c.restore();
    const F = xa + v * (t - at), sg = x => 2 + 34 * R.loss * Math.pow(clamp((x - xa) / 620), 1.3), am = x => 1 - 0.55 * R.loss * clamp((x - xa) / 620);
    stroke(c, xa, Math.min(xb, F), x => R.y + 10 - 60 * am(x) * level(x, F, bw, sg(x)), { lw: 5, step: 1.5 });
    if (F > xb + 20) { const ok = sg(xb) < 16; if (ok) tick(c, xb + 70, R.y - 100, 22); else cross(c, xb + 70, R.y - 100, 20); } });
};

// ---------- 三：在路上修信号（检修站）；模糊到一定程度就修不回来 ----------
FULL.CARD.repair = (c, t, id, cd, Q) => {
  const bw = 46, v = 700;
  const run = (y, at, blurIn, fixable) => { if (t < at) return; const xa = -330, mid = 20, xb = 330;
    chip(c, xa - 70, y, 'A'); chip(c, xb + 70, y, 'B');
    c.save(); c.strokeStyle = 'rgba(236,230,218,.3)'; c.lineWidth = 8; c.beginPath(); c.moveTo(xa, y + 40); c.lineTo(xb, y + 40); c.stroke(); c.restore();
    const F = xa + v * (t - at), sgIn = x => 2 + blurIn * Math.pow(clamp((x - xa) / (mid - 60 - xa)), 1.2);
    stroke(c, xa, Math.min(mid - 60, F), x => y + 10 - 60 * (1 - 0.4 * clamp((x - xa) / (mid - xa))) * level(x, F, bw, sgIn(x)), { lw: 5, step: 1.5 });
    const arrived = F > mid - 60, flash = arrived && t < at + (mid - 60 - xa) / v + 0.25;
    rbox(c, mid, y + 10, 110, 110, { r: 12, line: flash ? COL.redHi : 'rgba(236,230,218,.75)', lw: flash ? 6 : 3 }); txt(c, '检修', mid, y + 10, { size: 30, fam: 'PuHui-Heavy', align: 'center' });
    if (arrived && F > mid + 60) {
      if (fixable) stroke(c, mid + 60, Math.min(xb, F), x => y + 10 - 60 * level(x, F, bw, 2 + 10 * clamp((x - mid - 60) / (xb - mid - 60))), { lw: 5, step: 1.5 });
      else { cross(c, mid, y - 80, 22); for (let x = mid + 90; x < Math.min(xb, F); x += 70) digit(c, '?', x, y - 20, COL.redHi, 44); } }
    if (F > xb + 30) { if (fixable) tick(c, xb + 70, y - 100, 22); else cross(c, xb + 70, y - 100, 20); } };
  run(-180, Q.ok, 26, true);
  run(230, Q.bad, 90, false);
};

// ---------- 铜线没有被淘汰：短距离用铜线，铜线力不从心的那一段交给光 ----------
FULL.CARD.split = (c, t, id, cd, Q) => {
  const X0 = -400, X1 = 410, XL = -40, Y = 0, bw = 46;
  const cq = MO.cubicInOut(seg(t, Q.copper, Q.copper + 0.8));
  if (cq > 0) { c.save(); c.strokeStyle = 'rgba(236,230,218,.5)'; c.lineWidth = 22; c.lineCap = 'round'; c.beginPath(); c.moveTo(X0, Y); c.lineTo(lerp(X0, X1, cq), Y); c.stroke(); c.restore();
    const F = X0 + 700 * (t - Q.copper), sg = x => (x < XL ? 3 : 3 + (x - XL) * 0.22);
    stroke(c, X0, Math.min(lerp(X0, X1, cq), F), x => Y - 50 - 55 * level(x, F, bw, sg(x)) * (x < XL ? 1 : Math.max(0.4, 1 - (x - XL) / 600)), { lw: 5, step: 1.5 }); }
  if (t >= Q.limit) { const q = MO.smooth(seg(t, Q.limit, Q.limit + 0.3)); c.save(); c.globalAlpha = q; c.strokeStyle = COL.redHi; c.lineWidth = 5; c.setLineDash([12, 9]); c.beginPath(); c.moveTo(XL, Y - 170); c.lineTo(XL, Y + 120); c.stroke(); c.restore(); }
  if (t >= Q.light) { const q = MO.cubicInOut(seg(t, Q.light, Q.light + 0.7)); c.save(); c.shadowColor = COL.teal; c.shadowBlur = 20; c.strokeStyle = COL.tealHi; c.lineWidth = 14; c.lineCap = 'round';
    c.beginPath(); c.moveTo(XL, Y + 70); c.lineTo(lerp(XL, X1, q), Y + 70); c.stroke(); c.restore();
    FULL.H.pulses(c, XL + 800 * (t - Q.light), 46, XL, lerp(XL, X1, q), Y + 70, { h: 22 }); }
  axis(c, X0, X1, 330, MO.smooth(seg(t, Q.copper, Q.copper + 0.5)));
  FULL.H.note(c, 410);
};

// ---------- 「我们的芯片能跑 200G」：还要追问四件事 ----------
FULL.CARD.claim = (c, t, id, cd, Q) => {
  const tag = (text, x, y, at, bg, fg, size = 40, r = 0) => { if (S12(t) < at) return; const pop = S12(t) - at < 1 / 12 ? 1.12 : 1; c.save(); c.translate(x, y); c.rotate(r); c.scale(pop, pop);
    c.font = `${size}px "PuHui-Heavy"`; const w = c.measureText(text).width + size * 1.1;
    c.save(); c.translate(-w / 2, -size * 0.8); c.fillStyle = bg; CL.tornRect(c, w, size * 1.6, text.length * 7 + 3, 3); c.fill(); c.restore();
    txt(c, text, 0, 2, { size, fam: 'PuHui-Heavy', col: fg, align: 'center' }); c.restore(); };
  tag('“我们的芯片能跑 200G”', 0, -320, Q.claim, COL.cream, COL.ink, 50, -0.015);
  const QS = ['这是每条通道的速度吗？', '在多大损耗、什么条件下跑通？', '出错率多少？', '每个比特花多少电？'];
  QS.forEach((s, i) => tag(s, 0, -150 + i * 120, Q.qs[i], COL.red, '#f6efe4', 40, (i % 2 ? 0.012 : -0.012)));
  tag('速度只是结果', 0, 380, Q.res, COL.cream, COL.ink, 44, 0.01);
};
})();
