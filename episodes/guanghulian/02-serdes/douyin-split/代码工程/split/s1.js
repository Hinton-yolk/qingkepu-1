// 第 1 条：芯片之间传数据，为什么不修几十条路一起送？ 每个镜头一个函数，时间点全部来自口播（SP.kw）。
(() => {
const { clamp, lerp } = U; const { W, H, COL, kw, txt, tape, tag, pop, ease, seg, darkBg, deskShot, hookText, endCard, L } = SP;
const BITS = [1, 0, 1, 1, 0, 0, 1, 0];
const R = (s) => U.rng(s);
// 小方块「货」：奶油色撕边小纸块，上面一个 0/1
const box = (c, x, y, b, { s = 64, col = COL.cream, ink = COL.ink, alpha = 1, rot = 0, bad = false } = {}) => { if (alpha <= 0) return; c.save(); c.globalAlpha *= alpha; c.translate(x, y); c.rotate(rot);
  c.fillStyle = bad ? COL.coral : col; c.beginPath(); c.roundRect(-s / 2, -s / 2, s, s, s * 0.14); c.fill();
  if (b != null) { c.font = `${Math.round(s * 0.66)}px "PuHui-Heavy"`; c.fillStyle = ink; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText(String(b), 0, s * 0.04); } c.restore(); };
const chip = (c, x, y, w, h, label, { glow = 0, alpha = 1 } = {}) => { c.save(); c.globalAlpha *= alpha; c.shadowColor = 'rgba(0,0,0,.5)'; c.shadowBlur = 24; c.shadowOffsetY = 8;
  c.fillStyle = '#34322e'; c.beginPath(); c.roundRect(x - w / 2, y - h / 2, w, h, 14); c.fill(); c.shadowColor = 'transparent';
  c.strokeStyle = glow ? `rgba(245,215,126,${0.5 + 0.5 * glow})` : 'rgba(236,230,218,.35)'; c.lineWidth = 3; c.stroke();
  c.fillStyle = '#45423c'; c.beginPath(); c.roundRect(x - w * 0.32, y - h * 0.32, w * 0.64, h * 0.64, 8); c.fill();
  if (label) txt(c, label, x, y + 2, { size: Math.min(44, h * 0.32), fam: 'PuHui-Heavy', col: COL.cream, align: 'center' }); c.restore(); };
// 金色走线（电），带一点光
const trace = (c, pts, { col = COL.gold, lw = 6, alpha = 1, glow = 0.6, q = 1 } = {}) => { if (q <= 0) return; c.save(); c.globalAlpha *= alpha; c.strokeStyle = col; c.lineWidth = lw; c.lineCap = 'round'; c.lineJoin = 'round';
  if (glow) { c.shadowColor = COL.gold; c.shadowBlur = 14 * glow; }
  let tot = 0; const ls = []; for (let i = 1; i < pts.length; i++) { const d = Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]); ls.push(d); tot += d; }
  let rem = tot * q; c.beginPath(); c.moveTo(...pts[0]); for (let i = 1; i < pts.length && rem > 0; i++) { const f = Math.min(1, rem / ls[i - 1]); c.lineTo(lerp(pts[i - 1][0], pts[i][0], f), lerp(pts[i - 1][1], pts[i][1], f)); rem -= ls[i - 1]; }
  c.stroke(); c.restore(); };
const pulse = (c, x, y, r = 10, col = COL.goldHi) => { c.save(); c.shadowColor = COL.gold; c.shadowBlur = 22; c.fillStyle = col; c.beginPath(); c.arc(x, y, r, 0, 7); c.fill(); c.restore(); };

// ---------- 1. 第一帧：芯片底面密密麻麻的锡球 + 大字问题 ----------
SP.MECH.bga = (c, t, sh) => {
  darkBg(c);
  const z = 1 + 0.06 * MO.sineInOut(clamp(t / 5.5)), zo = ease(t, L.a03.t0 + 0.2, L.a03.t0 + 1.4, 'c');
  const P = 34, cols = 25, rows = 35, cx = W / 2, cy = 1080, pw = cols * P + 50, ph = rows * P + 50;
  const fast = [[10, 30], [11, 30], [13, 30], [14, 30]];
  const dim = ease(t, L.a03.t0, L.a03.t0 + 0.6);
  c.save(); c.translate(cx, cy); c.scale(z * (1 - 0.3 * zo), z * (1 - 0.3 * zo)); c.translate(-cx, -cy - 120 * zo);
  // 封装底板：圆角、1 号脚的缺角标记，一看就是一颗芯片翻过来
  c.save(); c.shadowColor = 'rgba(0,0,0,.6)'; c.shadowBlur = 40; c.shadowOffsetY = 16; c.fillStyle = '#2d3a2a'; c.beginPath(); c.roundRect(cx - pw / 2, cy - ph / 2, pw, ph, 18); c.fill(); c.restore();
  c.strokeStyle = 'rgba(226,181,74,.35)'; c.lineWidth = 3; c.beginPath(); c.roundRect(cx - pw / 2 + 8, cy - ph / 2 + 8, pw - 16, ph - 16, 12); c.stroke();
  c.fillStyle = COL.gold; c.beginPath(); c.moveTo(cx - pw / 2 + 14, cy - ph / 2 + 14); c.lineTo(cx - pw / 2 + 64, cy - ph / 2 + 14); c.lineTo(cx - pw / 2 + 14, cy - ph / 2 + 64); c.closePath(); c.fill();
  for (let i = 0; i < cols; i++) for (let j = 0; j < rows; j++) { const x = cx + (i - cols / 2 + 0.5) * P, y = cy + (j - rows / 2 + 0.5) * P;
    if (i < 1 && j < 1) continue;
    const isF = fast.some(([a, b]) => a === i && b === j), shimmer = 0.5 + 0.5 * Math.sin(t * 2.2 + i * 0.7 + j * 0.45);
    const g = c.createRadialGradient(x - 4, y - 5, 1, x, y, 12); const a = isF ? 1 : 1 - 0.7 * dim;
    g.addColorStop(0, `rgba(250,248,240,${a})`); g.addColorStop(0.45, `rgba(${isF && dim > 0 ? '245,215,126' : '190,188,180'},${a})`); g.addColorStop(1, `rgba(90,88,84,${a})`);
    c.fillStyle = g; c.beginPath(); c.arc(x, y, 12, 0, 7); c.fill();
    if (!isF && dim < 0.5) { c.fillStyle = `rgba(255,255,255,${0.14 * shimmer})`; c.beginPath(); c.arc(x - 4, y - 4, 3, 0, 7); c.fill(); }
    if (isF && dim > 0) { c.save(); c.globalAlpha = dim; c.strokeStyle = COL.goldHi; c.lineWidth = 4; c.shadowColor = COL.gold; c.shadowBlur = 20; c.beginPath(); c.arc(x, y, 17, 0, 7); c.stroke(); c.restore(); } }
  c.restore();
  // 从亮起来的针脚，一个接一个的比特排成一列往下跑
  if (t > L.a03.t0 + 0.8) { const x0 = W / 2, yS = 1110, yE = 1700, sp = 620;
    for (let n = 0; n < 40; n++) { const tt = t - (L.a03.t0 + 0.8) - n * 0.11; if (tt < 0) continue; const y = yS + tt * sp; if (y > yE) continue;
      box(c, x0, y, BITS[n % 8], { s: 46, col: COL.goldHi, alpha: 1 - seg(y, yE - 120, yE) }); } }
  if (dim > 0) tag(c, '大多数针脚：供电、接地', W / 2, 700, { size: 36, t, at: L.a03.t0 + 0.3, rate: 40 });
  if (t < L.a03.t0) tag(c, '芯片底面（示意）', W / 2, 1830 - 40, { size: 30, bg: 'rgba(236,230,218,.85)' });
  const up = ease(t, L.a03.t0 - 0.1, L.a03.t0 + 0.5, 'c');
  c.save(); c.translate(0, -260 * up); c.globalAlpha = 1 - up * 0.0; hookText(c, t, ['几千个针脚，', '还是不够用？'], { y: 470, size: 108, ids: ['a01', 'a02'] }); c.restore();
};

// ---------- 2. 修几十条路，几十件货同时出发；速度一高就乱了 ----------
const twoChips = (c, t, labA = '芯片 A', labB = '芯片 B', g = 0) => { chip(c, W / 2, 360, 860, 170, labA, { glow: g }); chip(c, W / 2, 1300, 860, 170, labB, { glow: g }); };
SP.MECH.parallel = (c, t, sh) => {
  darkBg(c); const N = 20, xs = i => 150 + i * (780 / (N - 1)), yA = 450, yB = 1210;
  const tRoad = kw('a04', '修几十条路'), tGo = kw('a04', '几十件货'), tFast = kw('a04', '速度一高'), tHard = kw('a04', '吃力');
  for (let i = 0; i < N; i++) { const q = ease(t, tRoad + i * 0.03, tRoad + 0.5 + i * 0.03, 'o'); trace(c, [[xs(i), yA], [xs(i), yB]], { lw: 5, q, glow: 0.3, alpha: 0.75 }); }
  twoChips(c, t);
  // 一波一波地发；速度一高：发得更密、到得参差不齐
  const fast = ease(t, tFast, tFast + 1.2), period = lerp(1.25, 0.55, fast);
  for (let w = 0; w < 30; w++) { const s0 = tGo + w * 1.25 * (w < 3 ? 1 : 0) + (w >= 3 ? 3 * 1.25 + (w - 3) * 0.55 : 0); if (t < s0) break;
    const ff = clamp((s0 - tFast) / 1.2), spd = lerp(1.0, 1.9, ff);
    for (let i = 0; i < N; i++) { const r = R(w * 97 + i * 13), sk = (r() - 0.5) * 0.9 * ff, tt = (t - s0) * spd - sk; const y = yA + 40 + tt * 520;
      if (tt < 0 || y > yB - 30) continue; box(c, xs(i), y, null, { s: 26, col: ff > 0.3 && Math.abs(sk) > 0.25 ? COL.coral : COL.cream }); } }
  if (t > tFast - 0.2) { const q = pop(t, tFast - 0.2); MD.label(c, `速度 ×${Math.round(lerp(1, 8, fast))}`, 960, 560, { size: 40, align: 'right', bg: COL.red, fg: '#f6efe4', t, at: tFast - 0.2, r: -0.03 }); }
  if (t > tHard) { const q = ease(t, tHard, tHard + 0.4); c.save(); c.strokeStyle = COL.coral; c.lineWidth = 6; c.globalAlpha = q; c.setLineDash([18, 12]); c.lineDashOffset = -t * 40; c.beginPath(); c.roundRect(110, 820, 860, 300, 30); c.stroke(); c.restore();
    tag(c, '到得参差不齐', W / 2, 1160, { size: 40, bg: COL.coral, fg: COL.ink, t, at: tHard }); }
};

// ---------- 3. 仓库：并排 → 排成一列 → 拆回一排；SerDes ----------
SP.MECH.serdes = (c, t, sh) => {
  darkBg(c);
  const t0 = L.a05.t0, tFun = kw('a06', '发货口'), tDst = kw('a07', '对方仓库'), tChip = kw('a08', '芯片'), tSD = kw('a09', 'SerDes'), tSer = kw('a09', 'Ser', 1), tDes = kw('a09', 'Des', 1);
  const rowY = 470, funY = 700, roadA = 800, roadB = 1120, fanY = 1210, outY = 1330, s = 70, xs = j => W / 2 + (j - 3.5) * 98;
  const toChip = ease(t, tChip, tChip + 0.6, 'c');
  // 两个仓库 → 两颗芯片
  const house = (y, lab, labC) => { c.save(); c.strokeStyle = `rgba(236,230,218,${0.5 - 0.3 * toChip})`; c.lineWidth = 4; c.setLineDash([14, 10]); c.beginPath(); c.roundRect(110, y - 85, 860, 170, 18); c.stroke(); c.restore();
    if (toChip > 0) chip(c, W / 2, y, 860, 170, null, { alpha: toChip * 0.9 }); MD.label(c, toChip < 0.5 ? lab : labC, 120, y - 120, { size: 36, bg: COL.cream, fg: COL.ink, t, at: t0 }); };
  house(rowY, '仓库', '芯片 A'); if (t > tDst - 0.4) house(outY, '对方仓库', '芯片 B');
  // 发货口（漏斗）和拆分口
  const qF = ease(t, tFun - 0.3, tFun + 0.3, 'o'), qD = ease(t, tDst - 0.3, tDst + 0.3, 'o');
  if (qF > 0) { c.save(); c.globalAlpha = qF; c.fillStyle = '#3a3833'; c.beginPath(); c.moveTo(150, funY - 70); c.lineTo(930, funY - 70); c.lineTo(W / 2 + 46, funY + 60); c.lineTo(W / 2 - 46, funY + 60); c.closePath(); c.fill(); c.strokeStyle = COL.goldDim; c.lineWidth = 3; c.stroke(); c.restore();
    trace(c, [[W / 2, funY + 60], [W / 2, roadB]], { lw: 66, col: '#3a3833', glow: 0, q: qF }); trace(c, [[W / 2, funY + 60], [W / 2, roadB]], { lw: 4, q: qF, alpha: 0.7 }); }
  if (qD > 0) { c.save(); c.globalAlpha = qD; c.fillStyle = '#3a3833'; c.beginPath(); c.moveTo(W / 2 - 46, roadB); c.lineTo(W / 2 + 46, roadB); c.lineTo(930, fanY + 40); c.lineTo(150, fanY + 40); c.closePath(); c.fill(); c.strokeStyle = COL.goldDim; c.lineWidth = 3; c.stroke(); c.restore(); }
  // 一组一组的货
  const T = 2.4;
  for (let g = 0; g < 9; g++) { const sg = t0 + 0.15 + g * T; if (t < sg) break;
    for (let j = 0; j < 8; j++) { const b = BITS[(j + g * 3) % 8], drop = clamp((t - sg - j * 0.05) / 0.25);
      if (g === 0 && t < tFun) { box(c, xs(j), rowY - 60 * (1 - MO.backOut(drop)), b, { s, alpha: drop }); continue; }
      const sgg = g === 0 ? tFun : sg; const e = sgg + 0.35 + j * 0.16, a = e + 0.55, d = a + 0.25, gone = sgg + T * 1.6;
      if (sgg > t && g > 0) break;
      if (t < e) { box(c, xs(j), rowY - (g > 0 ? 60 * (1 - MO.backOut(clamp((t - sgg - j * 0.05) / 0.25))) : 0), b, { s, alpha: g > 0 ? clamp((t - sgg - j * 0.05) / 0.25) : 1 }); continue; }
      if (t < a) { const q = (t - e) / (a - e); const x = q < 0.3 ? lerp(xs(j), W / 2, MO.cubicInOut(q / 0.3)) : W / 2, y = q < 0.3 ? lerp(rowY, funY + 60, MO.cubicInOut(q / 0.3)) : lerp(funY + 60, roadB, (q - 0.3) / 0.7);
        box(c, x, y, b, { s: s * 0.8, col: q > 0.3 ? COL.goldHi : COL.cream }); continue; }
      if (t < tDst - 0.1 && g < 3) { const y = roadB + (t - a) * 900; if (y < H) box(c, W / 2, y, b, { s: s * 0.8, col: COL.goldHi, alpha: 1 - seg(y, 1300, 1500) }); continue; }
      if (t < d) { const q = MO.cubicInOut((t - a) / (d - a)); box(c, lerp(W / 2, xs(j), q), lerp(roadB, outY, q), b, { s: lerp(s * 0.8, s, q), col: COL.goldHi }); continue; }
      if (t < gone) box(c, xs(j), outY, b, { s, alpha: 1 - seg(t, gone - 0.3, gone) }); } }
  // SerDes 名字：说到「SerDes」中间贴一条大胶带；说到 Ser / Des 分别贴在漏斗和拆分口上
  if (t > tSD - 0.1) tape(c, 'SerDes', W / 2, 960, { size: 76, t, at: tSD - 0.1, r: -0.02 });
  if (t > tSer - 0.1) MD.label(c, 'Ser 串行化 · 排成一列', 990, 790, { size: 38, align: 'right', bg: COL.red, fg: '#f6efe4', t, at: tSer - 0.1, r: 0.02 });
  if (t > tDes - 0.1) MD.label(c, 'Des 解串 · 拆回一排', 990, 1130, { size: 38, align: 'right', bg: COL.red, fg: '#f6efe4', t, at: tDes - 0.1, r: -0.02 });
};

// ---------- 4. 出口不够：引脚有限，每多一条线就多占面积、多耗电 ----------
SP.MECH.pins = (c, t, sh) => {
  darkBg(c);
  const tLim = kw('a11', '有限'), tMore = kw('a11', '每多一条线'), tArea = kw('a11', '面积'), tPow = kw('a11', '耗电'), tPile = L.a12.t0;
  chip(c, 420, 520, 640, 420, '芯片', {});
  const N = 10, px = i => 420 - 270 + i * 60, py = 730;
  for (let i = 0; i < N; i++) { const at = L.a11.t0 + 0.15 + i * 0.2, q = ease(t, at, at + 0.35, 'o');
    c.fillStyle = q > 0 ? COL.goldHi : 'rgba(236,230,218,.25)'; c.fillRect(px(i) - 18, py - 12, 36, 24);
    trace(c, [[px(i), py + 12], [px(i), 1250]], { lw: 6, q, glow: 0.4 }); }
  if (t > tLim) { const q = ease(t, tLim, tLim + 0.3); c.save(); c.globalAlpha = q; c.strokeStyle = COL.redHi; c.lineWidth = 6; c.beginPath(); c.moveTo(px(0) - 30, py + 40); c.lineTo(px(0) - 30, py + 60); c.lineTo(px(N - 1) + 30, py + 60); c.lineTo(px(N - 1) + 30, py + 40); c.stroke(); c.restore();
    tag(c, '出口就这么多', 420, py + 120, { size: 40, bg: COL.red, fg: '#f6efe4', t, at: tLim }); }
  // 右边两根计量条：面积、耗电，每多一条线涨一格
  const n = t < tMore ? 0 : Math.min(6, 1 + Math.floor((t - tMore) / 0.45));
  const bar = (x, lab, at, col) => { if (t < at - 0.6) return; const a = ease(t, at - 0.6, at - 0.3); c.save(); c.globalAlpha = a;
    txt(c, lab, x, 300, { size: 40, fam: 'PuHui-Heavy', col: COL.cream, align: 'center' }); c.strokeStyle = COL.creamDim; c.lineWidth = 3; c.strokeRect(x - 40, 340, 80, 560);
    for (let k = 0; k < n; k++) { const q = clamp((t - tMore - k * 0.45) / 0.2); c.fillStyle = col; c.fillRect(x - 32, 892 - (k + 1) * 88 + 8 + (1 - q) * 30, 64, 76 * q); } c.restore(); };
  bar(830, '面积', tArea, COL.cream); bar(960, '耗电', tPow, COL.coral);
  if (t > tMore) { for (let k = 0; k < n; k++) { const x = 420 + 300 + k * 0; } MD.label(c, `+${n} 条线`, 420, 960, { size: 40, align: 'center', bg: COL.cream, fg: COL.ink, t, at: tMore }); }
  // 不可能为每一件货都修一条路：货堆在出口上方，多出来的打红叉
  if (t > tPile - 0.2) { for (let k = 0; k < 28; k++) { const r = R(k + 5), at = tPile - 0.2 + k * 0.05, q = clamp((t - at) / 0.3); if (q <= 0) continue;
      const x = 140 + (k % 14) * 58 + (r() - .5) * 10, y = 1330 + Math.floor(k / 14) * 64 - 40 * (1 - MO.backOut(q)); box(c, x, y, BITS[k % 8], { s: 50, alpha: q, bad: k >= 10 }); }
    if (t > kw('a12', '一条路')) { const q = ease(t, kw('a12', '一条路'), kw('a12', '一条路') + 0.3); c.save(); c.globalAlpha = q; c.strokeStyle = COL.redHi; c.lineWidth = 9; c.lineCap = 'round';
      c.beginPath(); c.moveTo(700, 1270); c.lineTo(960, 1430); c.moveTo(960, 1270); c.lineTo(700, 1430); c.stroke(); c.restore(); } }
};

// ---------- 5. 很难同时到达：赛道 + 时间窗口 ----------
SP.MECH.race = (c, t, sh) => {
  darkBg(c);
  const N = 8, xs = i => 190 + i * 100, yS = 330, yF = 960, tWin = kw('a14', '时间窗口'), tJoin = kw('a14', '拼成'), tRun = kw('a15', '运动员'), tSlow = kw('a15', '跑得慢'),
    tFast = kw('a16', '跑得越快'), tLong = kw('a16', '长了一点点'), tLate = kw('a16', '晚到一步'), tWrong = kw('a16', '拼错');
  // 赛道：跑道线 + 道次号 + 终点线
  c.save(); c.strokeStyle = 'rgba(236,230,218,.22)'; c.lineWidth = 3; for (let i = 0; i <= N; i++) { c.beginPath(); c.moveTo(xs(0) - 50 + i * 100, yS - 30); c.lineTo(xs(0) - 50 + i * 100, yF + 30); c.stroke(); } c.restore();
  for (let i = 0; i < N; i++) txt(c, String(i + 1), xs(i), yS - 60, { size: 34, fam: 'PuHui-Heavy', col: COL.creamDim, align: 'center' });
  c.save(); for (let i = 0; i < 16; i++) { c.fillStyle = i % 2 ? COL.cream : '#111'; c.fillRect(xs(0) - 50 + i * 50, yF - 8, 50, 16); } c.restore();
  // 第 5 道多绕一小段（说到「长了一点点」时画红圈）
  const bump = 1;  // 一直都有；跑得慢时看不出来
  const lane5 = (y) => { const k = 4; return xs(k) + (y > 560 && y < 760 ? 34 * Math.sin(Math.PI * (y - 560) / 200) : 0); };
  c.save(); c.strokeStyle = 'rgba(245,215,126,.35)'; c.lineWidth = 3; c.setLineDash([6, 8]); c.beginPath(); for (let y = yS; y <= yF; y += 6) y === yS ? c.moveTo(lane5(y), y) : c.lineTo(lane5(y), y); c.stroke(); c.restore();
  if (t > tLong - 0.2) { const q = ease(t, tLong - 0.2, tLong + 0.3); c.save(); c.globalAlpha = q; c.strokeStyle = COL.redHi; c.lineWidth = 6; c.beginPath(); c.ellipse(xs(4) + 20, 660, 70, 130, 0, 0, Math.PI * 2 * q); c.stroke(); c.restore();
    tag(c, '长了一点点', xs(4) + 110, 520, { size: 36, align: 'left', bg: COL.red, fg: '#f6efe4', t, at: tLong }); }
  // 一轮一轮地发：周期 P（跑得越快，P 越短，时间窗口 = 0.7 P），第 5 道固定晚 Δ
  const DL = 0.13, TR = 1.05;           // Δ：多绕那段的时间；TR：跑完全程的时间
  const fastQ = ease(t, tFast, tFast + 1.6, 'c'), P = lerp(1.7, 0.42, fastQ);
  const heats = []; { let s = L.a14.t0 + 0.2; while (s < sh.t1) { heats.push(s); const pf = ease(s, tFast, tFast + 1.6, 'c'); s += lerp(1.7, 0.42, pf); } }
  // 底部：到达时刻的刻度尺 + 时间窗口
  const gy = 1290, gx0 = 160, gx1 = 920, gcx = (gx0 + gx1) / 2, pxPerS = 1500;
  const showG = ease(t, tWin - 0.3, tWin + 0.2);
  let cur = null; for (const s of heats) if (t >= s + TR - 0.4) cur = s;
  heats.forEach((s, h) => { const pf = ease(s, tFast, tFast + 1.6, 'c'), Ph = lerp(1.7, 0.42, pf);
    for (let i = 0; i < N; i++) { const late = i === 4 ? DL : 0, tt = (t - s) / (TR + late); if (tt < 0 || tt > 1.25) continue;
      const y = lerp(yS, yF, Math.min(tt, 1)) + (tt > 1 ? (tt - 1) * 0 : 0), x = i === 4 ? lane5(y) : xs(i);
      if (tt <= 1) box(c, x, y, BITS[(i + h) % 8], { s: 54, col: COL.cream }); } });
  // 拼出来的字节（终点下方）：本轮落在窗口里的位亮奶油色，落在窗口外的变珊瑚色
  if (cur != null && t > tJoin - 1.2) { const pf = ease(cur, tFast, tFast + 1.6, 'c'), Ph = lerp(1.7, 0.42, pf), win = 0.7 * Ph, ok = DL < win / 2 + 0.005;
    const h = heats.indexOf(cur), arr = cur + TR, q = clamp((t - arr) / 0.12);
    for (let i = 0; i < N; i++) { const bad = i === 4 && !ok && t > tFast + 0.6, show = i === 4 ? clamp((t - arr - DL) / 0.12) : q;
      box(c, xs(i), yF + 110, bad ? '?' : BITS[(i + h) % 8], { s: 64, alpha: show, bad }); }
    if (q > 0.5) { const a = clamp((t - arr - DL - 0.1) / 0.15); if (ok || t < tFast + 0.6) txt(c, '✓', 990, yF + 110, { size: 60, fam: 'PuHui-Heavy', col: COL.mint, align: 'center', alpha: a });
      else txt(c, '✗', 990, yF + 110, { size: 64, fam: 'PuHui-Heavy', col: COL.coral, align: 'center', alpha: a }); } }
  if (showG > 0) { c.save(); c.globalAlpha = showG; c.strokeStyle = COL.creamDim; c.lineWidth = 3; c.beginPath(); c.moveTo(gx0, gy); c.lineTo(gx1, gy); c.stroke();
    txt(c, '到达时刻', gx0, gy + 52, { size: 32, col: COL.creamDim });
    const pf = cur == null ? 0 : ease(cur, tFast, tFast + 1.6, 'c'), Pc = lerp(1.7, 0.42, Math.max(pf, fastQ * 0.0 + pf)), win = 0.7 * lerp(1.7, 0.42, fastQ);
    const ww = Math.min(gx1 - gx0, win * pxPerS * 0.5);
    c.fillStyle = 'rgba(127,214,180,.22)'; c.fillRect(gcx - ww / 2, gy - 50, ww, 100); c.strokeStyle = COL.mint; c.lineWidth = 4; c.strokeRect(gcx - ww / 2, gy - 50, ww, 100);
    txt(c, '时间窗口', gcx, gy - 78, { size: 34, fam: 'PuHui-Heavy', col: COL.mint, align: 'center' });
    // 每道一个点：其他道落在中线，第 5 道偏右 Δ
    for (let i = 0; i < N; i++) { const dx = (i === 4 ? DL : 0) * pxPerS * 0.5 + (i - 3.5) * 3, out = Math.abs(dx) > ww / 2;
      c.fillStyle = out ? COL.coral : COL.cream; c.beginPath(); c.arc(gcx + dx, gy + (i - 3.5) * 9, 9, 0, 7); c.fill(); }
    c.restore(); }
  if (t > tRun - 0.2 && t < tFast) tag(c, '像一排运动员同时冲线', W / 2, 250, { size: 38, t, at: tRun - 0.2 });
  if (t > tLate) { const pf = fastQ; if (pf > 0.7) tag(c, '晚到一步 → 落在窗口外', W / 2, 1420, { size: 38, bg: COL.coral, fg: COL.ink, t, at: tLate }); }
};

// ---------- 6. 只修几条路，排成一列跑到极快；镜头拉远看见电路板 ----------
SP.MECH.serial = (c, t, sh) => {
  darkBg(c);
  const tFew = kw('a17', '少数几条路'), tLine = kw('a17', '排成一列'), tFast = kw('a17', '极快'), tPcb = L.a17.t1 - 1.6;
  const zo = ease(t, tPcb - 0.2, tPcb + 1.0, 'c');
  c.save(); c.translate(W / 2, H / 2); c.scale(1 - 0.55 * zo, 1 - 0.55 * zo); c.translate(-W / 2, -H / 2);
  if (zo > 0) { c.save(); c.globalAlpha = zo; c.fillStyle = '#26301f'; c.beginPath(); c.roundRect(-700, -400, W + 1400, H + 800, 40); c.fill();
    c.strokeStyle = 'rgba(226,181,74,.18)'; c.lineWidth = 5; for (let k = 0; k < 26; k++) { const r = R(k + 40); const y = -300 + k * 105; c.beginPath(); c.moveTo(-650, y); c.lineTo(-650 + 400 + r() * 300, y); c.lineTo(-650 + 500 + r() * 300, y + 60); c.stroke();
      c.beginPath(); c.moveTo(W + 650, y); c.lineTo(W + 250 - r() * 300, y); c.stroke(); } c.restore(); }
  const N = 8, merge = ease(t, tFew, tFew + 1.0, 'c');
  const lx = i => { const from = 190 + i * 100, to = W / 2 + (i < 4 ? -70 : 70); return lerp(from, to, merge); };
  for (let i = 0; i < N; i++) trace(c, [[lx(i), 460], [lx(i), 1200]], { lw: lerp(4, 10, merge), alpha: i === 0 || i === 7 || merge < 0.95 ? lerp(0.6, 1, merge) : 0, glow: merge });
  chip(c, W / 2, 360, 860, 170, '芯片 A', { glow: merge }); chip(c, W / 2, 1300, 860, 170, '芯片 B', { glow: merge });
  // 货：先是参差不齐的一排；排成一列以后两条路上一串一串地飞
  const speed = lerp(500, 2600, ease(t, tFast - 0.4, tFast + 0.8, 'c'));
  if (t < tLine) { for (let i = 0; i < N; i++) { const r = R(i * 7 + 2), y = 520 + ((t - sh.t0) * 260 + r() * 300) % 640; box(c, lx(i), y, null, { s: 28, alpha: 1 - merge }); } }
  const lineQ = ease(t, tLine - 0.2, tLine + 0.4);
  if (lineQ > 0) for (const lane of [0, 1]) { const x = W / 2 + (lane ? 70 : -70), base = (t - tLine) * speed;
    for (let n = 0; n < 40; n++) { const y = 470 + ((base + n * 60 + lane * 30) % 740); const sp = speed / 2600;
      c.save(); c.globalAlpha = lineQ; c.fillStyle = COL.goldHi; c.shadowColor = COL.gold; c.shadowBlur = 16; c.beginPath(); c.roundRect(x - 12, y - 12 - 30 * sp, 24, 24 + 30 * sp, 8); c.fill(); c.restore(); } }
  c.restore();
  if (zo > 0.6) tag(c, '电路板上，芯片之间只有几条高速通道', W / 2, 1180, { size: 36, t, at: tPcb + 0.6 });
};

// ---------- 7. 一句话带走 + 下一条 ----------
SP.MECH.take = (c, t, sh) => { deskShot(c, t, sh); endCard(c, t, L.a21); };

// ---------- 新开头（大框架）：AI 越来越聪明 → 上万颗芯片一起练、每步都要交换数据 → 最快的连接只修几条路 → 打印机线 vs USB → 为什么？ ----------
SP.MECH.bga = (c, t, sh) => {
  darkBg(c); const { phone } = SP;
  const t2 = L.a02.t0, t3 = L.a03.t0, tEx = kw('a03', '交换数据'), tFast = kw('a03', '传得多快'), t4 = L.a03b.t0, t5 = L.a03c.t0, tPr = kw('a03c', '打印机线'), tUsb = kw('a03c', 'USB'), t6 = L.a03d.t0;
  const out = ease(t, t2 - 0.1, t2 + 1.3, 'c');                 // 从手机拉远到机房
  // 机房：一大片芯片，每算一步互相交换数据
  if (out > 0 && t < t4 + 0.6) { const cols = 9, rows = 13, P = 104, gx = i => W / 2 + (i - (cols - 1) / 2) * P, gy = j => 960 + (j - (rows - 1) / 2) * P;
    const zz = lerp(2.6, 1, out) * (1 + 0.03 * Math.sin(t * 0.7)), fade = 1 - ease(t, t4, t4 + 0.6);
    c.save(); c.globalAlpha = Math.min(1, out * 1.5) * fade; c.translate(W / 2, 960); c.scale(zz, zz); c.translate(-W / 2, -960);
    const wave = t > tEx - 0.3 ? ((t - (tEx - 0.3)) % 1.1) / 1.1 : -1, glow = ease(t, tFast - 0.3, tFast + 0.4);
    for (let i = 0; i < cols; i++) for (let j = 0; j < rows; j++) { const x = gx(i), y = gy(j);
      if (wave >= 0) { const m = MO.cubicInOut(Math.min(1, wave / 0.7)), a = Math.sin(Math.PI * Math.min(1, wave / 0.8));
        c.save(); c.globalAlpha *= a; c.fillStyle = glow > 0.5 ? COL.goldHi : COL.cream;
        if (i < cols - 1) { c.fillRect(lerp(x + 34, x + P - 34, m) - 6, y - 10, 12, 7); c.fillRect(lerp(x + P - 34, x + 34, m) - 6, y + 3, 12, 7); }
        if (j < rows - 1) { c.fillRect(x - 10, lerp(y + 34, y + P - 34, m) - 6, 7, 12); c.fillRect(x + 3, lerp(y + P - 34, y + 34, m) - 6, 7, 12); } c.restore(); }
      const busy = wave >= 0 && wave > 0.75 ? 1 : 0; c.fillStyle = busy ? '#4a463f' : '#34322e'; c.beginPath(); c.roundRect(x - 34, y - 34, 68, 68, 8); c.fill();
      c.strokeStyle = glow > 0.5 ? COL.gold : 'rgba(236,230,218,.3)'; c.lineWidth = 2; c.stroke(); c.fillStyle = '#45423c'; c.fillRect(x - 18, y - 18, 36, 36); }
    c.restore();
    if (t > t2 + 0.3 && t < t4) tag(c, '上万颗芯片，一起训练一个模型', W / 2, 1300, { size: 40, t, at: t2 + 0.3 });
    if (t > tEx - 0.3 && t < t4) tape(c, '每算一步，都要互相交换数据', W / 2, 520, { size: 50, t, at: tEx - 0.3 }); }
  // 手机：和 AI 的对话（不出现品牌）
  if (out < 1) { const s = lerp(1, 0.35, out); c.save(); c.globalAlpha = 1 - out; c.translate(W / 2, 880); c.scale(s, s); c.translate(-W / 2, -880);
    phone(c, W / 2, 880, 560, 1000, (g, x, y, w, h) => { g.fillStyle = '#f1ece1'; g.fillRect(x, y, w, h);
      const bub = (s_, bx, by, mine, at) => { if (t < at) return; g.font = '34px "PuHui-Medium"'; const tw = Math.min(380, g.measureText(s_).width); const q = Math.min(1, pop(t, at, 0.2));
        g.save(); g.globalAlpha = q; g.fillStyle = mine ? COL.goldHi : '#ffffff'; g.beginPath(); g.roundRect(mine ? x + w - tw - 70 : x + 30, by, tw + 40, 70, 22); g.fill(); g.fillStyle = COL.ink; g.textBaseline = 'middle'; g.fillText(s_, mine ? x + w - tw - 50 : x + 50, by + 36); g.restore(); };
      bub('帮我把这段话翻成英文', 0, y + 120, true, -1); bub('好的，翻译如下：', 0, y + 220, false, -1);
      for (let k = 0; k < 5; k++) { const q = clamp((t * 2.2 - k * 0.35)); g.fillStyle = 'rgba(27,27,26,.18)'; g.beginPath(); g.roundRect(x + 30, y + 320 + k * 52, (w - 140) * (k === 4 ? 0.55 : 1) * q, 30, 10); g.fill(); }
      txt(g, 'AI', x + w / 2, y + 60, { size: 36, fam: 'PuHui-Heavy', col: COL.ink, align: 'center' }); });
    c.restore(); }
  // 最快的连接，只修几条路：两颗芯片、两条亮线；后面一排虚线表示「本可以修几十条」
  const q4 = ease(t, t4 - 0.2, t4 + 0.4) * (1 - ease(t, t5 - 0.2, t5 + 0.3));
  if (q4 > 0) { c.save(); c.globalAlpha = q4; for (let i = 0; i < 16; i++) { const x = 200 + i * 45; c.strokeStyle = 'rgba(236,230,218,.14)'; c.lineWidth = 3; c.setLineDash([10, 12]); c.beginPath(); c.moveTo(x, 600); c.lineTo(x, 1220); c.stroke(); } c.setLineDash([]);
    for (const x of [W / 2 - 60, W / 2 + 60]) { trace(c, [[x, 600], [x, 1220]], { lw: 10 }); for (let n = 0; n < 9; n++) { const y = 600 + ((t * 900 + n * 70 + (x > W / 2 ? 35 : 0)) % 620); pulse(c, x, y, 8); } }
    chip(c, W / 2, 520, 820, 160, '芯片'); chip(c, W / 2, 1300, 820, 160, '芯片'); c.restore(); }
  // 25 针打印机线 vs 4 根线的 USB
  const q5 = ease(t, t5 - 0.2, t5 + 0.4);
  if (q5 > 0) { c.save(); c.globalAlpha = q5; const shrink = ease(t, t6 - 0.1, t6 + 0.5, 'c'), yC = lerp(820, 760, shrink);
    // DB-25：梯形外壳 + 13/12 两排针 + 粗电缆
    const dx = 290; c.fillStyle = '#7b7870'; c.beginPath(); c.moveTo(dx - 200, yC - 70); c.lineTo(dx + 200, yC - 70); c.lineTo(dx + 175, yC + 70); c.lineTo(dx - 175, yC + 70); c.closePath(); c.fill();
    c.fillStyle = '#2a2927'; c.beginPath(); c.moveTo(dx - 175, yC - 50); c.lineTo(dx + 175, yC - 50); c.lineTo(dx + 155, yC + 50); c.lineTo(dx - 155, yC + 50); c.closePath(); c.fill();
    for (let k = 0; k < 13; k++) { c.fillStyle = COL.goldHi; c.beginPath(); c.arc(dx - 156 + k * 26, yC - 20, 7, 0, 7); c.fill(); } for (let k = 0; k < 12; k++) { c.beginPath(); c.arc(dx - 143 + k * 26, yC + 20, 7, 0, 7); c.fill(); }
    c.fillStyle = '#4a4741'; c.fillRect(dx - 70, yC + 70, 140, 300); txt(c, '25 针', dx, yC - 120, { size: 48, fam: 'PuHui-Heavy', col: COL.cream, align: 'center' });
    // USB-A：细线 + 4 个触点
    const ux = 790; c.fillStyle = '#b9b6ae'; c.beginPath(); c.roundRect(ux - 70, yC - 50, 140, 110, 6); c.fill(); c.fillStyle = '#2a2927'; c.fillRect(ux - 56, yC - 36, 112, 40);
    for (let k = 0; k < 4; k++) { c.fillStyle = COL.goldHi; c.fillRect(ux - 46 + k * 26, yC - 30, 16, 26); } c.fillStyle = '#3a3833'; c.fillRect(ux - 22, yC + 60, 44, 310);
    txt(c, '4 根线', ux, yC - 120, { size: 48, fam: 'PuHui-Heavy', col: COL.cream, align: 'center' });
    // 速度条：说到「跑不过」时 USB 那根冲上去
    const qa = ease(t, tPr, tPr + 0.6, 'o'), qb = ease(t, tUsb - 0.2, tUsb + 0.8, 'o'), by = yC + 470;
    c.fillStyle = COL.creamDim; c.fillRect(dx - 70, by - 18 * qa, 140, 18 * qa); c.fillStyle = COL.goldHi; c.fillRect(ux - 70, by - 330 * qb, 140, 330 * qb);
    txt(c, '每秒约 2 兆字节', dx, by + 50, { size: 34, fam: 'PuHui-Heavy', col: COL.creamDim, align: 'center' }); if (qb > 0.2) txt(c, '每秒几十兆字节', ux, by + 50, { size: 34, fam: 'PuHui-Heavy', col: COL.goldHi, align: 'center' });
    txt(c, '老打印机线（并口）', dx, by + 100, { size: 30, col: COL.creamDim, align: 'center' }); txt(c, 'USB 2.0', ux, by + 100, { size: 30, col: COL.creamDim, align: 'center' });
    c.restore(); }
  if (t > t6 - 0.15) tape(c, '为什么路少了，反而快？', W / 2, 400, { size: 64, t, at: t6 - 0.15, r: -0.02 });
  // 第一帧就在的大字问题 + 开头两句的卡拉 OK 大字
  const up = ease(t, t3 - 0.3, t3 + 0.3, 'c');
  if (up < 1) { c.save(); c.globalAlpha = 1 - up; hookText(c, t, ['AI 越来越快，', '芯片之间的路却越修越少？'], { y: 230, size: 64 });
    hookText(c, t, ['AI 越来越聪明，', '靠的是上万颗芯片一起练。'], { y: 1500, size: 58, ids: ['a01', 'a02'], bg: '#0f0f0e' }); c.restore(); }
};
})();
