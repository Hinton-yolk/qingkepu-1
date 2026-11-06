// 第 3 条：号称每条通道 200G 的芯片，该问它哪三个问题？（只讲怎么问，不点名、不荐股）
(() => {
const { clamp, lerp } = U; const { W, H, COL, kw, txt, tape, tag, pop, ease, seg, darkBg, deskShot, hookText, endCard, L } = SP;
const R = (s) => U.rng(s);
const chip = (c, x, y, w, h, label, { glow = 0, alpha = 1, size } = {}) => { c.save(); c.globalAlpha *= alpha; c.shadowColor = 'rgba(0,0,0,.5)'; c.shadowBlur = 24; c.shadowOffsetY = 8;
  c.fillStyle = '#34322e'; c.beginPath(); c.roundRect(x - w / 2, y - h / 2, w, h, 14); c.fill(); c.shadowColor = 'transparent';
  c.strokeStyle = glow ? `rgba(245,215,126,${0.5 + 0.5 * glow})` : 'rgba(236,230,218,.35)'; c.lineWidth = 3; c.stroke();
  c.fillStyle = '#45423c'; c.beginPath(); c.roundRect(x - w * 0.32, y - h * 0.32, w * 0.64, h * 0.64, 8); c.fill();
  if (label) txt(c, label, x, y + 2, { size: size || Math.min(44, h * 0.3), fam: 'PuHui-Heavy', col: COL.cream, align: 'center' }); c.restore(); };
// 信号：理想方波经过「路」以后变模糊（一阶低通 + 衰减）；blur 0 = 方方正正
const BITS = [1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1];
const sig = (c, x0, x1, yC, amp, blur, { off = 0, col = COL.goldHi, lw = 7, bw = 70, alpha = 1, glow = 0.6 } = {}) => { c.save(); c.globalAlpha *= alpha; c.strokeStyle = col; c.lineWidth = lw; c.lineJoin = 'round';
  if (glow) { c.shadowColor = COL.gold; c.shadowBlur = 16 * glow; }
  const tau = 2 + blur * bw * 0.9, a = Math.exp(-3 / tau); let y = 0; c.beginPath();
  for (let x = x0 - 400; x <= x1; x += 3) { const k = Math.floor((x + off) / bw), target = BITS[((k % BITS.length) + BITS.length) % BITS.length] ? 1 : -1; y = blur < 0.01 ? target : a * y + (1 - a) * target;
    if (x >= x0) { const yy = yC - y * amp * (1 - 0.45 * blur); x === x0 || x < x0 + 3 ? c.moveTo(x, yy) : c.lineTo(x, yy); } }
  c.stroke(); c.restore(); };
const meter = (c, x, y, lab, q, col) => { txt(c, lab, x, y - 300, { size: 38, fam: 'PuHui-Heavy', col: COL.cream, align: 'center' }); c.strokeStyle = COL.creamDim; c.lineWidth = 3; c.strokeRect(x - 36, y - 260, 72, 260);
  c.fillStyle = col; c.fillRect(x - 28, y - 8 - 244 * q, 56, 244 * q); };
const qcard = (c, n, s, x, y, t, at, { on = true, w = 900 } = {}) => { if (t < at) return; const q = pop(t, at, 0.25);
  c.save(); c.translate(x, y); c.scale(0.85 + 0.15 * Math.min(1, q), 0.85 + 0.15 * Math.min(1, q)); c.globalAlpha = Math.min(1, q) * (on ? 1 : 0.45);
  c.fillStyle = COL.cream; CL.tornRect(c, w, 96, n * 13 + 3, 3); c.translate(-w / 2, -48); CL.tornRect(c, w, 96, n * 13 + 3, 3); c.fill();
  c.fillStyle = COL.red; c.beginPath(); c.arc(56, 48, 34, 0, 7); c.fill(); txt(c, String(n), 56, 50, { size: 44, fam: 'PuHui-Heavy', col: '#f6efe4', align: 'center' });
  txt(c, s, 112, 50, { size: 46, fam: 'PuHui-Heavy', col: COL.ink }); c.restore(); };

// ---------- 1. 第一帧：芯片上打着「224G」+ 大字问题 ----------
SP.MECH.spec = (c, t, sh) => {
  darkBg(c);
  const z = 1 + 0.05 * MO.sineInOut(clamp(t / 4.4)), tQ = kw('c03', '三个问题');
  c.save(); c.translate(W / 2, 900); c.scale(z, z); c.translate(-W / 2, -900);
  // 封装 + 顶盖：激光刻字的型号和速度
  c.save(); c.shadowColor = 'rgba(0,0,0,.6)'; c.shadowBlur = 40; c.shadowOffsetY = 16; c.fillStyle = '#2d3a2a'; c.beginPath(); c.roundRect(170, 560, 740, 740, 22); c.fill(); c.restore();
  const lid = c.createLinearGradient(260, 650, 820, 1210); lid.addColorStop(0, '#b9b6ae'); lid.addColorStop(0.5, '#8d8a83'); lid.addColorStop(1, '#a9a69e');
  c.fillStyle = lid; c.beginPath(); c.roundRect(250, 640, 580, 580, 16); c.fill();
  c.save(); c.globalAlpha = 0.15 + 0.08 * Math.sin(t * 1.5); c.fillStyle = '#fff'; c.beginPath(); c.moveTo(250 + ((t * 90) % 900) - 300, 640); c.lineTo(250 + ((t * 90) % 900) - 160, 640); c.lineTo(250 + ((t * 90) % 900) - 460, 1220); c.lineTo(250 + ((t * 90) % 900) - 600, 1220); c.closePath(); c.fill(); c.restore();
  txt(c, '224G', 540, 880, { size: 170, fam: 'PuHui-Heavy', col: 'rgba(40,38,34,.78)', align: 'center' });
  txt(c, 'SerDes · 每条通道', 540, 1010, { size: 46, fam: 'PuHui-Heavy', col: 'rgba(40,38,34,.7)', align: 'center' });
  c.fillStyle = 'rgba(40,38,34,.6)'; c.beginPath(); c.arc(300, 690, 14, 0, 7); c.fill();
  c.restore();
  hookText(c, t, ['跑得快，', '就够了吗？'], { y: 290, size: 100 });
  hookText(c, t, ['“能跑 224G”，', '只说了一半。'], { y: 1300, size: 70, ids: ['c01', 'c02'], bg: '#0f0f0e' });
  if (t > tQ - 0.3) ['①', '②', '③'].forEach((s, i) => { const at = tQ - 0.3 + i * 0.15; if (t < at) return; const q = pop(t, at);
    c.save(); c.translate(250 + i * 290, 1530); c.scale(Math.min(1, q), Math.min(1, q)); c.fillStyle = COL.cream; c.beginPath(); c.roundRect(-110, -60, 220, 120, 14); c.fill();
    txt(c, `${s} ？`, 0, 4, { size: 56, fam: 'PuHui-Heavy', col: COL.red, align: 'center' }); c.restore(); });
};

// ---------- 2. 数据越来越多、出口涨不动 → 每条路跑更快；每几年翻一倍 ----------
SP.MECH.lanes = (c, t, sh) => {
  darkBg(c);
  const tData = kw('c04', '越来越多'), tExit = kw('c04', '出口'), tFast = kw('c04', '每条路跑多快'), tDbl = kw('c05', '翻一倍');
  const step = ease(t, tDbl - 1.6, tDbl + 0.4, 'c');
  if (step < 1) { c.save(); c.globalAlpha = 1 - step;
    // 左：要传的数据（柱子往上冲）；右：芯片出口数量（几乎不涨）
    const hD = 760 * ease(t, tData - 0.3, tData + 1.6, 'o'), hE = 160 + 60 * ease(t, tExit, tExit + 1.2);
    c.fillStyle = COL.goldHi; c.fillRect(220, 1250 - hD, 220, hD); c.fillStyle = COL.cream; c.fillRect(640, 1250 - hE, 220, hE);
    txt(c, '要传的数据', 330, 1310, { size: 42, fam: 'PuHui-Heavy', col: COL.cream, align: 'center' }); txt(c, '芯片的出口', 750, 1310, { size: 42, fam: 'PuHui-Heavy', col: COL.cream, align: 'center' });
    if (t > tExit) tag(c, '涨得很慢', 750, 1250 - hE - 70, { size: 40, bg: COL.red, fg: '#f6efe4', t, at: tExit });
    if (t > tFast - 0.3) { tape(c, '只能让每条路跑得更快', W / 2, 380, { size: 54, t, at: tFast - 0.3 });
      for (let n = 0; n < 16; n++) { const x = 640 + ((t - tFast) * 1400 + n * 50) % 220; c.fillStyle = COL.goldHi; c.fillRect(x, 1250 - hE - 40, 26, 14); } }
    c.restore(); }
  if (step > 0) { c.save(); c.globalAlpha = step;
    const V = [['28G', 1], ['56G', 2], ['112G', 4], ['224G', 8]], base = 1300, unit = 95;
    V.forEach(([s, v], i) => { const at = tDbl - 1.2 + i * 0.35, q = ease(t, at, at + 0.4, 'o'), x = 200 + i * 230, h = v * unit * q;
      c.fillStyle = i === 3 ? COL.goldHi : COL.gold; c.fillRect(x - 70, base - h, 140, h); if (q > 0.3) txt(c, s, x, base - h - 45, { size: 48, fam: 'PuHui-Heavy', col: COL.cream, align: 'center' });
      if (i && q > 0.6) txt(c, '×2', x - 115, base - V[i - 1][1] * unit - 90, { size: 36, fam: 'PuHui-Heavy', col: COL.redHi, align: 'center' }); });
    c.strokeStyle = COL.creamDim; c.lineWidth = 3; c.beginPath(); c.moveTo(100, base); c.lineTo(980, base); c.stroke();
    txt(c, '每条通道的速度（大约每代翻一倍）', W / 2, base + 60, { size: 38, fam: 'PuHui-Heavy', col: COL.creamDim, align: 'center' }); c.restore(); }
};

// ---------- 3. 越快越模糊 → SerDes 自己带「整理」→ 要耗电、占面积 ----------
SP.MECH.blur = (c, t, sh) => {
  darkBg(c);
  const tBlur = kw('c06', '模糊'), tBeat = kw('c06', '听准节拍'), tFix = kw('c07', '整理'), tTx = kw('c07', '发出'), tRx = kw('c07', '收进'), tPow = kw('c08', '耗电'), tArea = kw('c08', '面积');
  const off = (t - sh.t0) * 160;
  // 上：发出的信号（干净）；下：收到的信号（变糊）；中间一段路
  txt(c, '发出', 90, 400, { size: 40, fam: 'PuHui-Heavy', col: COL.creamDim });
  const txFix = ease(t, tTx - 0.2, tTx + 0.5), rxFix = ease(t, tRx - 0.2, tRx + 0.6);
  sig(c, 90, 990, 520, 80, 0, { off, bw: 70 });
  c.save(); c.strokeStyle = 'rgba(226,181,74,.25)'; c.lineWidth = 40; c.beginPath(); c.moveTo(W / 2, 640); c.bezierCurveTo(200, 760, 880, 860, W / 2, 1000); c.stroke(); c.restore();
  for (let n = 0; n < 8; n++) { const p = ((t - sh.t0) * 0.5 + n / 8) % 1; const x = W / 2 + Math.sin(p * Math.PI * 2) * 140 * Math.sin(p * Math.PI), y = 640 + p * 360; c.fillStyle = COL.goldHi; c.globalAlpha = 0.6; c.beginPath(); c.arc(x, y, 9, 0, 7); c.fill(); c.globalAlpha = 1; }
  txt(c, '收到', 90, 1080, { size: 40, fam: 'PuHui-Heavy', col: COL.creamDim });
  const blur = ease(t, tBlur - 0.6, tBlur + 0.6) * (1 - rxFix * 0.85);
  sig(c, 90, 990, 1200, 80, blur, { off: off - 200, bw: 70, col: blur > 0.5 ? COL.coral : COL.goldHi });
  // 节拍刻度对不准
  if (t > tBeat - 0.3) { const mis = (1 - rxFix); for (let k = 0; k < 13; k++) { const x = 90 + (k + 0.5) * 70 - ((off - 200) % 70) + mis * 18 * Math.sin(t * 4 + k); if (x > 990) continue; c.strokeStyle = mis > 0.5 ? COL.coral : COL.mint; c.lineWidth = 4; c.beginPath(); c.moveTo(x, 1300); c.lineTo(x, 1340); c.stroke(); } }
  // 发出端、收进端各一个「修」的工位
  const station = (y, lab, q, at) => { if (q <= 0) return; c.save(); c.globalAlpha = q; c.fillStyle = 'rgba(15,15,14,.9)'; c.beginPath(); c.roundRect(700, y - 50, 300, 100, 16); c.fill(); c.strokeStyle = COL.mint; c.lineWidth = 4; c.stroke();
    txt(c, lab, 850, y + 2, { size: 40, fam: 'PuHui-Heavy', col: COL.mint, align: 'center' }); c.restore(); };
  station(420, '发出时修', txFix); station(1100, '收进时修', rxFix);
  if (t > tFix - 0.2) tape(c, 'SerDes 自带「整理」能力', W / 2, 300 + 0 * 0, { size: 50, t, at: tFix - 0.2 });
  // 代价：耗电、占面积
  if (t > tPow - 0.5) { c.save(); c.globalAlpha = ease(t, tPow - 0.5, tPow - 0.2); c.fillStyle = 'rgba(15,15,14,.92)'; c.fillRect(0, 1360, W, 400); c.restore();
    c.save(); c.globalAlpha = ease(t, tPow - 0.5, tPow - 0.2); meter(c, 380, 1700 - 20, '耗电', ease(t, tPow, tPow + 0.8, 'o') * 0.75, COL.coral); meter(c, 700, 1700 - 20, '面积', ease(t, tArea, tArea + 0.8, 'o') * 0.6, COL.cream); c.restore(); }
};

// ---------- 4. 跷跷板：跑得更快 vs 每个比特更省电 ----------
SP.MECH.seesaw = (c, t, sh) => {
  darkBg(c);
  const tPj = kw('c09', '每送出一个比特'), tGen = kw('c09', '每一代');
  const a = 0.16 * Math.sin((t - sh.t0) * 1.6);
  c.save(); c.translate(W / 2, 1000); c.fillStyle = '#4a463f'; c.beginPath(); c.moveTo(-70, 120); c.lineTo(70, 120); c.lineTo(0, 0); c.closePath(); c.fill();
  c.rotate(a); c.fillStyle = COL.cream; c.fillRect(-440, -16, 880, 24);
  const pan = (x, lab, col) => { c.save(); c.translate(x, -16); c.rotate(-a); c.fillStyle = col; c.beginPath(); c.roundRect(-150, -130, 300, 120, 16); c.fill(); txt(c, lab, 0, -68, { size: 46, fam: 'PuHui-Heavy', col: COL.ink, align: 'center' }); c.restore(); };
  pan(-300, '跑得更快', COL.goldHi); if (t > tPj - 0.3) pan(300, '每比特更省电', COL.mint); c.restore();
  if (t > tPj) tag(c, '业内看 pJ/bit：每传一个比特耗多少能量', W / 2, 1300, { size: 38, t, at: tPj + 0.3, rate: 30 });
  if (t > tGen - 0.2) tape(c, '每一代都要面对的难题', W / 2, 520, { size: 56, t, at: tGen - 0.2 });
};

// ---------- 5. 嵌在别的芯片里；IP 授权或自研 ----------
SP.MECH.inside = (c, t, sh) => {
  darkBg(c);
  const tAb = kw('c11', '能力'), tG = kw('c11', 'GPU'), tS = kw('c11', '交换芯片'), tO = kw('c11', '光模块'), tIP = kw('c12', 'IP'), tLic = kw('c12', '授权'), tSelf = kw('c12', '自己研发');
  const C = [['GPU', 270, 500, tG], ['交换芯片', 810, 500, tS], ['光模块里的芯片', 540, 900, tO]];
  C.forEach(([lab, x, y, at], i) => { if (t < at - 0.4) return; const q = Math.min(1, pop(t, at - 0.4)); c.save(); c.translate(x, y); c.scale(q, q); c.translate(-x, -y);
    chip(c, x, y, 380, 330, null, {}); txt(c, lab, x, y + 200, { size: 40, fam: 'PuHui-Heavy', col: COL.cream, align: 'center' });
    // 芯片边上一圈 SerDes（金色小块，一闪一闪）
    const ring = ease(t, at, at + 0.8);
    for (let k = 0; k < 20; k++) { const side = Math.floor(k / 5), f = (k % 5 + 0.5) / 5, px = side === 0 ? x - 150 + 300 * f : side === 1 ? x + 150 : side === 2 ? x + 150 - 300 * f : x - 150, py = side === 0 ? y - 130 : side === 1 ? y - 130 + 260 * f : side === 2 ? y + 130 : y + 130 - 260 * f;
      if (k / 20 > ring) continue; c.fillStyle = (Math.floor(t * 6) + k) % 7 === 0 ? '#fff6d6' : COL.goldHi; c.fillRect(px - 14, py - 14, 28, 28); }
    c.restore(); });
  if (t > tAb - 0.2) tape(c, 'SerDes 是一种「能力」', W / 2, 300, { size: 52, t, at: tAb - 0.2 });
  // IP：一块「设计模块」被复制进别家的芯片
  if (t > tIP - 0.3) { const q = ease(t, tIP - 0.3, tIP + 0.2), bx = 280, by = 1230; c.save(); c.globalAlpha = q; c.fillStyle = COL.goldHi; c.beginPath(); c.roundRect(bx - 130, by - 70, 260, 140, 16); c.fill();
    txt(c, 'SerDes IP', bx, by + 2, { size: 44, fam: 'PuHui-Heavy', col: COL.ink, align: 'center' }); txt(c, '设计模块', bx, by + 110, { size: 36, fam: 'PuHui-Heavy', col: COL.creamDim, align: 'center' }); c.restore();
    if (t > tLic - 0.2) for (let k = 0; k < 3; k++) { const at = tLic - 0.2 + k * 0.25, p = MO.cubicInOut(seg(t, at, at + 0.6)); if (p <= 0) continue; const tx = [270, 810, 540][k], ty = [500, 500, 900][k];
      c.save(); c.globalAlpha = 1 - p * 0.6; c.fillStyle = COL.goldHi; c.fillRect(lerp(bx, tx, p) - 40, lerp(by, ty, p) - 24, 80, 48); c.restore(); }
    if (t > tLic) tag(c, '授权给芯片公司', 280, 1390, { size: 38, t, at: tLic }); }
  if (t > tSelf - 0.3) { const q = ease(t, tSelf - 0.3, tSelf + 0.3); c.save(); c.globalAlpha = q; c.strokeStyle = COL.cream; c.lineWidth = 4; c.setLineDash([10, 8]); c.beginPath(); c.roundRect(640, 1140, 300, 180, 16); c.stroke();
    const p = seg(t, tSelf, tSelf + 1.2); c.setLineDash([]); c.strokeStyle = COL.goldHi; c.lineWidth = 8; c.beginPath(); c.moveTo(670, 1280); c.lineTo(670 + 240 * p, 1280 - 100 * Math.sin(p * 3)); c.stroke(); c.restore();
    tag(c, '大公司：自己研发', 790, 1390, { size: 38, bg: COL.red, fg: '#f6efe4', t, at: tSelf }); }
};

// ---------- 6. 三个问题 ----------
SP.MECH.three = (c, t, sh) => {
  darkBg(c);
  const tClaim = kw('c13', '宣称'), t1 = kw('c14', '第一'), t2 = L.c15.t0, t3 = L.c16.t0, t4 = kw('c17', '自研'), t5 = L.c18.t0;
  const cur = t >= t5 ? 5 : t >= t4 ? 4 : t >= t3 ? 3 : t >= t2 ? 2 : t >= t1 ? 1 : 0;
  // 上方：问题卡一张张贴上来
  qcard(c, 1, '什么路况下跑到的？', W / 2, 330, t, t1 - 0.2, { on: cur === 1 || cur >= 4 });
  qcard(c, 2, '每个比特花多少电？', W / 2, 450, t, t2 - 0.1, { on: cur === 2 || cur >= 4 });
  qcard(c, 3, '真实芯片上跑通了吗？', W / 2, 570, t, t3 - 0.1, { on: cur === 3 || cur >= 4 });
  const Y = 1050;
  if (cur === 0) { const z = 1 + 0.04 * Math.sin(t * 2); txt(c, '224G', W / 2, Y - 60, { size: 220 * z, fam: 'PuHui-Heavy', col: COL.goldHi, align: 'center' }); txt(c, '宣称的速度', W / 2, Y + 110, { size: 44, fam: 'PuHui-Heavy', col: COL.creamDim, align: 'center' });
    if (t > tClaim) { const q = ease(t, tClaim, tClaim + 0.5); c.save(); c.strokeStyle = COL.redHi; c.lineWidth = 8; c.beginPath(); c.ellipse(W / 2, Y - 60, 330, 150, -0.05, 0, Math.PI * 2 * q); c.stroke(); c.restore();
      if (q > 0.9) txt(c, '？', 860, Y - 210, { size: 140, fam: 'PuHui-Heavy', col: COL.redHi, align: 'center' }); } }
  // ① 路况：同一个速度，短而平的路 vs 长而损耗大的路
  if (cur === 1) { const off = (t - t1) * 160;
    txt(c, '短、损耗小的路', 90, 760, { size: 40, fam: 'PuHui-Heavy', col: COL.cream }); sig(c, 90, 990, 880, 80, 0.12, { off, bw: 70 });
    txt(c, '长、损耗大的路', 90, 1100, { size: 40, fam: 'PuHui-Heavy', col: COL.cream }); sig(c, 90, 990, 1230, 80, 0.85, { off, bw: 70, col: COL.coral });
    tag(c, '同一个「224G」，难度差很多', W / 2, 1370, { size: 40, bg: COL.coral, fg: COL.ink, t, at: kw('c14', '路况') }); }
  // ② 每个比特的电：一个表盘
  if (cur === 2) { const v = ease(t, t2, t2 + 1.0, 'o'); c.save(); c.translate(W / 2, 1200); c.strokeStyle = COL.creamDim; c.lineWidth = 18; c.beginPath(); c.arc(0, 0, 300, Math.PI, 2 * Math.PI); c.stroke();
    c.strokeStyle = COL.mint; c.beginPath(); c.arc(0, 0, 300, Math.PI, Math.PI * 1.33); c.stroke(); c.strokeStyle = COL.coral; c.beginPath(); c.arc(0, 0, 300, Math.PI * 1.67, 2 * Math.PI); c.stroke();
    const ang = Math.PI * (1.1 + 0.6 * v + 0.03 * Math.sin(t * 9)); c.strokeStyle = COL.cream; c.lineWidth = 10; c.lineCap = 'round'; c.beginPath(); c.moveTo(0, 0); c.lineTo(Math.cos(ang) * 260, Math.sin(ang) * 260); c.stroke(); c.restore();
    txt(c, 'pJ / bit', W / 2, 1290, { size: 64, fam: 'PuHui-Heavy', col: COL.cream, align: 'center' }); txt(c, '省电', 230, 1260, { size: 38, fam: 'PuHui-Heavy', col: COL.mint, align: 'center' }); txt(c, '费电', 850, 1260, { size: 38, fam: 'PuHui-Heavy', col: COL.coral, align: 'center' }); }
  // ③ 仿真 → 真实芯片测出来的信号
  if (cur === 3) { const p = ease(t, t3 + 0.4, t3 + 1.4, 'c');
    c.save(); c.globalAlpha = 1 - p * 0.5; c.strokeStyle = COL.cream; c.lineWidth = 4; c.setLineDash([12, 10]); c.beginPath(); c.roundRect(120, 800, 360, 360, 18); c.stroke(); c.restore();
    txt(c, '纸面 / 仿真', 300, 1210, { size: 40, fam: 'PuHui-Heavy', col: COL.creamDim, align: 'center' });
    c.save(); c.globalAlpha = p; chip(c, 780, 980, 360, 360, '真实芯片'); c.restore();
    if (p > 0) { c.save(); c.translate(lerp(300, 780, p), 980); c.fillStyle = COL.goldHi; c.globalAlpha = 1 - p; c.fillRect(-30, -30, 60, 60); c.restore(); }
    if (t > t3 + 1.3) { txt(c, '测通了 ✓', 780, 1210, { size: 46, fam: 'PuHui-Heavy', col: COL.mint, align: 'center', alpha: ease(t, t3 + 1.3, t3 + 1.6) }); } }
  // 然后：自研还是授权
  if (cur === 4) { const q = pop(t, t4 - 0.2); ['自研', '授权 IP'].forEach((s, i) => { c.save(); c.translate(320 + i * 440, 1050); c.scale(Math.min(1, q), Math.min(1, q)); c.fillStyle = i ? COL.goldHi : COL.cream; c.beginPath(); c.roundRect(-170, -90, 340, 180, 18); c.fill();
      txt(c, s, 0, 4, { size: 60, fam: 'PuHui-Heavy', col: COL.ink, align: 'center' }); c.restore(); }); txt(c, '还是', W / 2, 1054, { size: 46, fam: 'PuHui-Heavy', col: COL.cream, align: 'center' });
    tag(c, '问完三个问题，再看这个', W / 2, 1300, { size: 40, t, at: t4 }); }
  // 以后看 DSP、光模块：同样三问
  if (cur === 5) { const D = [['DSP', 300], ['光模块', 780]]; D.forEach(([s, x], i) => { const at = kw('c18', s) - 0.2, q = Math.min(1, pop(t, at)); if (t < at) return; c.save(); c.translate(x, 1050); c.scale(q, q); chip(c, 0, 0, 360, 280, s, { size: 52, glow: 0.6 }); c.restore();
      for (let k = 0; k < 3; k++) { const p = MO.cubicInOut(seg(t, at + 0.3 + k * 0.15, at + 0.9 + k * 0.15)); c.save(); c.fillStyle = COL.red; c.globalAlpha = p; c.beginPath(); c.arc(x - 90 + k * 90, 1250, 30, 0, 7); c.fill(); txt(c, String(k + 1), x - 90 + k * 90, 1252, { size: 34, fam: 'PuHui-Heavy', col: '#f6efe4', align: 'center' }); c.restore(); } }); }
};

SP.MECH.take = (c, t, sh) => { deskShot(c, t, sh); endCard(c, t, L.c21); };

// ---------- 新开头（大框架）：AI 芯片新闻天天说速度翻倍 → 汽车最高时速 300、没说什么路 → 同样 224G，一米还是几厘米 → 三个问题 ----------
SP.MECH.spec = (c, t, sh) => {
  darkBg(c);
  const t3 = L.c03.t0, tRoad = kw('c03', '什么路上'), t4 = L.c03b.t0, tM = kw('c03b', '一米'), tCm = kw('c03b', '几厘米'), t5 = L.c03c.t0;
  // 一叠新闻卡（虚构标题，不点名）
  const nq = 1 - ease(t, t3 - 0.2, t3 + 0.4, 'c');
  if (nq > 0) { c.save(); c.globalAlpha = nq; const H_ = ['新一代 AI 芯片：互连速度翻倍', '传输速度再翻一倍！', '每条通道冲上 200G'];
    H_.forEach((s, i) => { const at = -1 + i * 0.6 * 0 + (i === 2 ? L.c02.t0 : i === 1 ? L.c01.t1 : -1); if (t < at) return; const q = Math.min(1, pop(t, at)), y = 640 + i * 230, r = (i - 1) * 0.04 + 0.01 * Math.sin(t * 1.3 + i);
      c.save(); c.translate(W / 2, y); c.rotate(r); c.scale(q, q); c.shadowColor = 'rgba(0,0,0,.5)'; c.shadowBlur = 20; c.shadowOffsetY = 8; c.fillStyle = '#f6f2ea'; c.beginPath(); c.roundRect(-430, -95, 860, 190, 12); c.fill(); c.shadowColor = 'transparent';
      c.fillStyle = COL.red; c.fillRect(-430, -95, 14, 190); txt(c, '科技快讯', -390, -48, { size: 28, fam: 'PuHui-Heavy', col: COL.red }); txt(c, s, -390, 18, { size: 48, fam: 'PuHui-Heavy', col: COL.ink });
      c.fillStyle = 'rgba(27,27,26,.15)'; c.fillRect(-390, 60, 520, 12); c.restore(); });
    if (t > L.c02.t0) { const q = pop(t, kw('c02', '翻倍')); c.save(); c.translate(860, 560); c.rotate(-0.15); c.scale(Math.min(1.1, q), Math.min(1.1, q)); txt(c, '×2', 0, 0, { size: 150, fam: 'PuHui-Heavy', col: COL.goldHi, align: 'center' }); c.restore(); }
    c.restore(); }
  // 最高时速 300：表盘指针拉满；下面两条路：平坦的高速 vs 坑洼的土路
  const q3 = ease(t, t3 - 0.2, t3 + 0.3) * (1 - ease(t, t4 - 0.2, t4 + 0.3));
  if (q3 > 0) { c.save(); c.globalAlpha = q3; c.translate(W / 2, 760); c.strokeStyle = COL.creamDim; c.lineWidth = 16; c.beginPath(); c.arc(0, 0, 260, Math.PI * 0.8, Math.PI * 2.2); c.stroke();
    const v = ease(t, t3, t3 + 1.2, 'o'), ang = Math.PI * (0.8 + 1.4 * v); c.strokeStyle = COL.redHi; c.lineWidth = 10; c.lineCap = 'round'; c.beginPath(); c.moveTo(0, 0); c.lineTo(Math.cos(ang) * 230, Math.sin(ang) * 230); c.stroke();
    txt(c, `${Math.round(300 * v)}`, 0, 120, { size: 96, fam: 'PuHui-Heavy', col: COL.cream, align: 'center' }); txt(c, '最高时速 km/h', 0, 200, { size: 34, col: COL.creamDim, align: 'center' }); c.restore();
    if (t > tRoad - 0.3) { const q = ease(t, tRoad - 0.3, tRoad + 0.3); c.save(); c.globalAlpha = q3 * q;
      c.fillStyle = '#3d3b37'; c.fillRect(80, 1130, 420, 120); c.fillStyle = COL.cream; for (let k = 0; k < 6; k++) c.fillRect(100 + k * 70 - ((t * 200) % 70), 1186, 40, 8); txt(c, '平坦的高速', 290, 1300, { size: 38, fam: 'PuHui-Heavy', col: COL.cream, align: 'center' });
      c.fillStyle = '#5a4532'; c.beginPath(); c.moveTo(580, 1250); for (let k = 0; k <= 14; k++) c.lineTo(580 + k * 30, 1140 + 25 * Math.sin(k * 1.9 + t * 3)); c.lineTo(1000, 1250); c.closePath(); c.fill(); txt(c, '坑坑洼洼的土路', 790, 1300, { size: 38, fam: 'PuHui-Heavy', col: COL.coral, align: 'center' });
      c.restore(); } }
  // 同样写着 224G：一颗推过一米长的铜缆，一颗只跑几厘米
  const q4 = ease(t, t4 - 0.2, t4 + 0.3);
  if (q4 > 0) { c.save(); c.globalAlpha = q4; const lid = (x, y) => { c.save(); c.shadowColor = 'rgba(0,0,0,.5)'; c.shadowBlur = 24; c.fillStyle = '#2d3a2a'; c.beginPath(); c.roundRect(x - 170, y - 170, 340, 340, 14); c.fill(); c.restore();
      const g = c.createLinearGradient(x - 130, y - 130, x + 130, y + 130); g.addColorStop(0, '#b9b6ae'); g.addColorStop(1, '#8d8a83'); c.fillStyle = g; c.beginPath(); c.roundRect(x - 130, y - 130, 260, 260, 10); c.fill();
      txt(c, '224G', x, y + 4, { size: 78, fam: 'PuHui-Heavy', col: 'rgba(40,38,34,.8)', align: 'center' }); };
    lid(280, 560); lid(800, 560);
    // 左：一米长的铜缆（盘一圈），信号一路跑
    const pm = ease(t, tM - 0.4, tM + 1.0, 'c'); c.save(); c.strokeStyle = '#c47a3c'; c.lineWidth = 22; c.lineCap = 'round'; c.beginPath(); const pts = []; for (let k = 0; k <= 60; k++) { const u = k / 60; pts.push([280 + 150 * Math.sin(u * Math.PI * 2.2), 760 + u * 560]); }
    pts.slice(0, Math.max(2, Math.round(60 * pm) + 1)).forEach((p, i) => i ? c.lineTo(...p) : c.moveTo(...p)); c.stroke(); c.restore();
    if (pm > 0.9) { txt(c, '约 1 米铜缆', 280, 1400, { size: 44, fam: 'PuHui-Heavy', col: COL.goldHi, align: 'center' }); }
    // 右：几厘米的走线
    const pc = ease(t, tCm - 0.3, tCm + 0.4, 'o'); c.save(); c.strokeStyle = COL.gold; c.lineWidth = 10; c.beginPath(); c.moveTo(800, 730); c.lineTo(800, 730 + 140 * pc); c.stroke(); c.restore();
    if (pc > 0.5) { c.fillStyle = '#34322e'; c.beginPath(); c.roundRect(700, 870, 200, 90, 10); c.fill(); txt(c, '几厘米', 800, 1010, { size: 44, fam: 'PuHui-Heavy', col: COL.goldHi, align: 'center' }); }
    c.restore(); }
  // 要会问三个问题
  if (t > t5 - 0.2) ['①', '②', '③'].forEach((s, i) => { const at = t5 - 0.2 + i * 0.18; if (t < at) return; const q = pop(t, at);
    c.save(); c.translate(250 + i * 290, 1360); c.scale(Math.min(1, q), Math.min(1, q)); c.fillStyle = COL.cream; c.beginPath(); c.roundRect(-110, -60, 220, 120, 14); c.fill();
    txt(c, `${s} ？`, 0, 4, { size: 56, fam: 'PuHui-Heavy', col: COL.red, align: 'center' }); c.restore(); });
  const up = ease(t, t3 - 0.3, t3 + 0.3, 'c');
  if (up < 1) { c.save(); c.globalAlpha = 1 - up; hookText(c, t, ['速度翻倍，', '该信几分？'], { y: 220, size: 88 });
    hookText(c, t, ['AI 芯片的新闻，', '天天在说速度翻倍。'], { y: 1520, size: 62, ids: ['c01', 'c02'], bg: '#0f0f0e' }); c.restore(); }
};
})();
