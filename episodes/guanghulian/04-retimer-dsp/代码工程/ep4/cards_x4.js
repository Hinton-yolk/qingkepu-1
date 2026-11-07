// 光互连 04 · 小红书版新增的卡片：手机均衡器（上集实物开场）、整体放大 vs 只补被吞的、快递转运中心、光模块透视（下集实物开场 + 结尾拿掉 DSP）、糊掉的字条、成千上万个光模块。
// 坐标原点在卡片中心；时间点来自 desk_u.json / desk_d.json 的 cue。纯时间函数，随机数用种子。
(() => {
const { clamp, lerp } = U; const { COL, txt, seg, S12 } = FULL;
const H = FULL.H, GOLD = '#f5d77e';
const Phi = x => 1 / (1 + Math.exp(-1.702 * x));
const BITS = [1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1];
const bitOf = k => (k < 0 ? 0 : BITS[((k % 30) + 30) % 30]);
const level = (x, F, bw, sg) => { let y = 0; const kLo = Math.max(0, Math.floor((F - x - 4 * sg) / bw) - 1), kHi = Math.ceil((F - x + 4 * sg) / bw) + 1;
  for (let k = kLo; k <= kHi; k++) if (bitOf(k)) y += Phi((F - k * bw - x) / sg) - Phi((F - (k + 1) * bw - x) / sg); return y; };
const tag = (c, s, x, y, { size = 38, bg = COL.cream, fg = COL.ink, r = 0 } = {}) => { c.save(); c.translate(x, y); c.rotate(r); c.font = `${size}px "PuHui-Heavy"`; const w = c.measureText(s).width + size * 1.0;
  c.save(); c.translate(-w / 2, -size * 0.8); c.fillStyle = bg; CL.tornRect(c, w, size * 1.6, s.length * 7 + 3, 3); c.fill(); c.restore(); txt(c, s, 0, 2, { size, fam: 'PuHui-Heavy', col: fg, align: 'center' }); c.restore(); };

// ---------- 上集第一帧：手机上的音乐均衡器；推子一推，旁边铜线出口的信号就变清楚 ----------
FULL.CARD.eqapp = (c, t, id, cd, Q) => {
  // 分两步演示（用户 2026-11-07：均衡器和波形分开演示，别 0.5 秒就变好）：先只有手机均衡器，推子各自上下动；
  // Q.show 时手机往左让、右边出现铜线出口的信号（糊的）；Q.push 时推子把高音推上去，信号变清楚。回扣（Q.again）：信号一直在，推子先回平再推一次。
  const show = Q.show != null ? MO.cubicInOut(seg(t, Q.show, Q.show + 0.7)) : 1;
  const k = Q.again != null ? (t < Q.again ? 1 - MO.cubicInOut(seg(t, Q.again - 0.6, Q.again)) : MO.cubicInOut(seg(t, Q.again, Q.again + 0.9))) : (Q.push != null ? MO.cubicInOut(seg(t, Q.push, Q.push + 0.9)) : 0);
  const mv = Q.eqmove != null ? MO.cubicInOut(seg(t, Q.eqmove, Q.eqmove + 1.2)) : 0;
  const PX = lerp(0, -270, show), PY = 0, PW = 440, PH = 860;
  c.save(); c.shadowColor = 'rgba(40,30,15,.4)'; c.shadowBlur = 30; c.shadowOffsetY = 14; c.fillStyle = '#151514'; c.beginPath(); c.roundRect(PX - PW / 2, PY - PH / 2, PW, PH, 56); c.fill(); c.restore();
  c.fillStyle = '#1d2226'; c.beginPath(); c.roundRect(PX - PW / 2 + 18, PY - PH / 2 + 26, PW - 36, PH - 52, 40); c.fill();
  c.fillStyle = '#151514'; c.beginPath(); c.roundRect(PX - 50, PY - PH / 2 + 34, 100, 22, 11); c.fill();
  txt(c, '均衡器', PX, PY - 320, { size: 40, fam: 'PuHui-Heavy', col: '#eef2f2', align: 'center' });
  // 正在播放的音乐：一排跳动的频谱条（高音那几根随推子变高）
  const N = 5, top = PY - 200, bot = PY + 240, flat = [0.5, 0.5, 0.5, 0.5, 0.5], g1 = [0.32, 0.4, 0.5, 0.66, 0.74], g2 = [0.34, 0.42, 0.55, 0.8, 0.9];
  const pos = flat.map((v, i) => lerp(lerp(v, g1[i], clamp(mv * 1.6 - i * 0.15)), g2[i], k));
  for (let b = 0; b < 12; b++) { const x = PX - 170 + b * 31, hgt = 18 + 34 * Math.abs(Math.sin(t * (3 + b * 0.37) + b)) * (0.6 + 0.6 * pos[Math.min(4, Math.floor(b / 2.4))]);
    c.fillStyle = 'rgba(127,214,180,.55)'; c.fillRect(x - 9, PY - 245 - hgt, 18, hgt); }
  for (let i = 0; i < N; i++) { const x = PX - 160 + i * 80, v = pos[i] + 0.012 * Math.sin(t * 2.3 + i * 1.7), y = lerp(bot, top, v);
    c.strokeStyle = 'rgba(238,242,242,.25)'; c.lineWidth = 8; c.lineCap = 'round'; c.beginPath(); c.moveTo(x, top); c.lineTo(x, bot); c.stroke();
    c.strokeStyle = i >= 3 ? '#7fd6b4' : 'rgba(127,214,180,.6)'; c.beginPath(); c.moveTo(x, bot); c.lineTo(x, y); c.stroke();
    c.fillStyle = '#eef2f2'; c.beginPath(); c.arc(x, y, 20, 0, 7); c.fill(); }
  txt(c, '低音', PX - 160, bot + 60, { size: 30, fam: 'PuHui-Heavy', col: 'rgba(238,242,242,.6)', align: 'center' }); txt(c, '高音', PX + 160, bot + 60, { size: 30, fam: 'PuHui-Heavy', col: 'rgba(238,242,242,.6)', align: 'center' });
  // 铜线出口的信号（右边）：show 时出现（糊的），推子推上去以后变清楚
  if (show > 0) { c.save(); c.globalAlpha = show; const SX0 = 40, SX1 = 420, SY = 40, F = SX0 + 4000 + t * 240, sg = lerp(24, 2.5, k);
    c.fillStyle = 'rgba(29,29,28,.92)'; c.beginPath(); c.roundRect(SX0 - 30, SY - 190, SX1 - SX0 + 60, 300, 24); c.fill();
    c.strokeStyle = 'rgba(236,230,218,.2)'; c.lineWidth = 2; c.setLineDash([6, 8]); c.beginPath(); c.moveTo(SX0, SY + 40); c.lineTo(SX1, SY + 40); c.stroke(); c.setLineDash([]);
    H.stroke(c, SX0, SX1, x => SY + 40 - 140 * lerp(0.85, 1, k) * level(x, F, 46, sg), { col: k > 0.5 ? GOLD : '#e0654f', lw: 7, step: 2 });
    txt(c, '铜线出口的信号', (SX0 + SX1) / 2, SY - 150, { size: 32, fam: 'PuHui-Heavy', col: 'rgba(236,230,218,.7)', align: 'center' }); c.restore(); }
};

// ---------- 整体放大（尾巴也一起变大）✗ vs 只补被吞的部分 ✓ ----------
FULL.CARD.whole = (c, t, id, cd, Q) => {
  const bw = 70, x0 = -400, x1 = 400, n = Math.floor((x1 - x0) / bw);
  const g1 = (u, tau) => (u <= 0 ? 0 : 1 - Math.exp(-u / tau)), resp = (x, kk) => (g1(x - kk * bw, 60) - g1(x - (kk + 1) * bw, 60)) / (1 - Math.exp(-bw / 60)) * 0.85;
  const SEQ = [1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0], blurred = x => SEQ.reduce((a, b, kk) => a + (b ? resp(x - x0, kk) : 0), 0);
  [[-200, Q.a, '整体放大：尾巴也跟着变大', x => 1.6 * blurred(x), false], [230, Q.b, '只补被吞掉的：方方正正', x => level(x, x0 + SEQ.length * bw, bw, 2.5) * 0 + (SEQ[Math.floor((x - x0) / bw)] || 0), true]].forEach(([y, at, lab, fy, ok]) => {
    if (at == null || t < at) return; const q = seg(t, at, at + 0.8), xe = lerp(x0, x1, q);
    c.save(); c.strokeStyle = 'rgba(236,230,218,.25)'; c.lineWidth = 2; c.setLineDash([6, 8]); c.beginPath(); c.moveTo(x0, y); c.lineTo(x1, y); c.stroke(); c.restore();
    H.stroke(c, x0, xe, x => y - 110 * Math.min(1.6, fy(x)), { col: ok ? GOLD : '#e0654f', lw: 6, step: 2 });
    tag(c, lab, 0, y - 230, { size: 36, bg: ok ? '#7fd6b4' : '#ef7d62' });
    if (q >= 1) txt(c, ok ? '✓' : '✗', 430, y - 150, { size: 64, fam: 'PuHui-Heavy', col: ok ? '#7fd6b4' : '#ef7d62', align: 'center' }); });
};

// ---------- 快递转运中心：压坏的箱子进去，拆开核对、重新打包，新箱子出来 ----------
FULL.CARD.hub = (c, t, id, cd, Q) => {
  const Y = 80, X0 = -440, X1 = 440, per = 1.8, speed = 260;
  c.save(); c.fillStyle = '#2c2c2a'; c.fillRect(X0, Y + 50, X1 - X0, 26); c.strokeStyle = 'rgba(236,230,218,.25)'; c.lineWidth = 2; for (let x = X0 + ((t * speed) % 40); x < X1; x += 40) { c.beginPath(); c.moveTo(x, Y + 52); c.lineTo(x - 10, Y + 74); c.stroke(); } c.restore();
  // 转运中心
  c.save(); c.fillStyle = '#3a3a37'; c.strokeStyle = 'rgba(245,215,126,.8)'; c.lineWidth = 4; c.beginPath(); c.roundRect(-120, Y - 200, 240, 250, 18); c.fill(); c.stroke(); c.restore();
  txt(c, '转运中心', 0, Y - 150, { size: 36, fam: 'PuHui-Heavy', col: GOLD, align: 'center' });
  const glow = 0.5 + 0.5 * Math.sin(t * 6); c.save(); c.fillStyle = `rgba(245,215,126,${0.15 + 0.2 * glow})`; c.fillRect(-100, Y - 110, 200, 140); c.restore();
  txt(c, '拆开 · 核对 · 重新打包', 0, Y - 40, { size: 26, fam: 'PuHui-Heavy', col: 'rgba(236,230,218,.75)', align: 'center' });
  const box = (x, bad) => { c.save(); c.translate(x, Y); if (bad) { c.rotate(-0.12); c.fillStyle = '#9a7442'; c.beginPath(); c.moveTo(-50, 40); c.lineTo(-38, -30); c.lineTo(10, -46); c.lineTo(48, -24); c.lineTo(52, 40); c.closePath(); c.fill();
      c.strokeStyle = '#5a4120'; c.lineWidth = 3; c.stroke(); c.strokeStyle = '#e0654f'; c.lineWidth = 4; c.beginPath(); c.moveTo(-20, -30); c.lineTo(-5, -5); c.lineTo(-18, 18); c.stroke(); }
    else { c.fillStyle = '#c99a4a'; c.fillRect(-50, -40, 100, 80); c.strokeStyle = '#7a5a2a'; c.lineWidth = 3; c.strokeRect(-50, -40, 100, 80); c.fillStyle = '#e9d3a8'; c.fillRect(-8, -40, 16, 80); c.fillStyle = '#fff'; c.fillRect(14, -18, 28, 20); }
    c.restore(); };
  for (let n = 0; n < 6; n++) { const u = ((t - (Q.t0 || 0)) / per + n / 3) % 2, x = X0 + 40 + u * (X1 - X0 - 80) / 2; if (x > -150 && x < 150) continue; box(x, x < 0); }
  if (t >= (Q.t0 || 0) + 0.3) { tag(c, '压坏的箱子', -300, Y + 170, { size: 34, bg: '#ef7d62' }); tag(c, '重新打包的新箱子', 300, Y + 170, { size: 34, bg: '#7fd6b4' }); }
};

// ---------- 光模块透视：激光器小小一个，DSP 发烫；耗电条约一半是 DSP。lpo：DSP 拿掉，耗电条掉一半；move：「修」挪到主芯片 ----------
FULL.CARD.module = (c, t, id, cd, Q) => {
  const lpo = Q.lpo != null ? MO.cubicInOut(seg(t, Q.lpo, Q.lpo + 0.8)) : 0, mv = Q.move != null ? MO.cubicInOut(seg(t, Q.move, Q.move + 1.0)) : 0;
  const Y = -120;
  // 外壳
  c.save(); c.shadowColor = 'rgba(40,30,15,.4)'; c.shadowBlur = 30; c.shadowOffsetY = 12; const g = c.createLinearGradient(0, Y - 150, 0, Y + 150); g.addColorStop(0, '#d9d6cf'); g.addColorStop(0.5, '#a9a69e'); g.addColorStop(1, '#c8c5be');
  c.fillStyle = g; c.beginPath(); c.roundRect(-460, Y - 150, 920, 300, 28); c.fill(); c.restore();
  c.fillStyle = '#2b3a46'; c.beginPath(); c.roundRect(-560, Y - 30, 110, 60, 14); c.fill();                                   // 拉环
  c.fillStyle = '#d7b257'; for (let i = 0; i < 9; i++) c.fillRect(440, Y - 110 + i * 26, 40, 14);                                // 金手指（插进交换机那头）
  // 透视窗
  c.save(); c.fillStyle = '#16191b'; c.beginPath(); c.roundRect(-420, Y - 120, 830, 240, 18); c.fill(); c.restore();
  // 激光器（小）+ 光纤口
  c.save(); c.fillStyle = '#4a4f55'; c.fillRect(-330, Y - 40, 90, 80); c.restore(); txt(c, '激光器', -285, Y + 75, { size: 26, fam: 'PuHui-Heavy', col: 'rgba(236,230,218,.75)', align: 'center' });
  c.save(); c.globalCompositeOperation = 'lighter'; for (let k = 0; k < 6; k++) { const u = ((t * 1.4 + k / 6) % 1), x = -340 - u * 100; c.fillStyle = `rgba(155,232,219,${0.9 * (1 - u)})`; c.beginPath(); c.arc(x, Y, 8, 0, 7); c.fill(); } c.restore();
  // DSP（发烫）
  if (lpo < 1) { const heat = 0.6 + 0.4 * Math.sin(t * 5); c.save(); c.globalAlpha = 1 - lpo; const hg = c.createRadialGradient(80, Y, 10, 80, Y, 210); hg.addColorStop(0, `rgba(255,120,60,${0.55 * heat})`); hg.addColorStop(1, 'rgba(255,120,60,0)'); c.fillStyle = hg; c.fillRect(-140, Y - 120, 440, 240);
    c.fillStyle = '#2b2a27'; c.strokeStyle = GOLD; c.lineWidth = 4; c.beginPath(); c.roundRect(0, Y - 70, 160, 140, 12); c.fill(); c.stroke(); txt(c, 'DSP', 80, Y + 2, { size: 44, fam: 'PuHui-Heavy', col: GOLD, align: 'center' }); c.restore(); }
  // 信号：从金手指进来（糊）→ DSP → 出来（清楚）→ 激光器
  const F = 400 + 4000 + t * 220;
  H.stroke(c, 175, 420, x => Y + 30 - 60 * level(-x + 600, F, 30, 14), { col: '#e0654f', lw: 5, step: 2 });
  H.stroke(c, -230, 0, x => Y + 30 - 60 * level(-x + 600, F, 30, lerp(2.5, 14, lpo)), { col: lpo > 0.5 ? '#e0654f' : GOLD, lw: 5, step: 2 });
  // 耗电条
  const BY = Y + 260, BX0 = -420, BW = 840, dspW = BW * 0.5 * (1 - lpo), rest = BW * 0.5;
  c.save(); c.fillStyle = 'rgba(27,27,26,.12)'; c.beginPath(); c.roundRect(BX0, BY, BW, 56, 14); c.fill(); c.restore();
  c.fillStyle = '#8a8780'; c.beginPath(); c.roundRect(BX0, BY, rest, 56, 14); c.fill(); if (dspW > 2) { c.fillStyle = '#e0654f'; c.beginPath(); c.roundRect(BX0 + rest, BY, dspW, 56, 14); c.fill(); }
  txt(c, '其他', BX0 + rest / 2, BY + 30, { size: 28, fam: 'PuHui-Heavy', col: '#f3efe6', align: 'center' }); if (dspW > 120) txt(c, 'DSP', BX0 + rest + dspW / 2, BY + 30, { size: 28, fam: 'PuHui-Heavy', col: '#f3efe6', align: 'center' });
  txt(c, '光模块耗电（示意）', BX0, BY - 30, { size: 28, fam: 'PuHui-Heavy', col: 'rgba(27,27,26,.6)' });
  // 主芯片（结尾：「修」挪过来）
  if (Q.move != null && t >= Q.move - 0.6) { const a = seg(t, Q.move - 0.6, Q.move - 0.1); c.save(); c.globalAlpha = a; H.rbox(c, 0, BY + 250, 380, 150, { r: 16, line: GOLD, lw: 4, fill: '#2b2a27' });
    txt(c, '主芯片 · SerDes', 0, BY + 250, { size: 36, fam: 'PuHui-Heavy', col: GOLD, align: 'center' }); c.restore();
    const fx = lerp(80, 150, mv), fy = lerp(Y - 110, BY + 160, mv); tag(c, '修', fx, fy, { size: 40, bg: '#ef7d62' }); }
};

// ---------- 糊掉的字条：结合前后几个字，猜出中间那个 ----------
FULL.CARD.note = (c, t, id, cd, Q) => {
  c.save(); c.rotate(-0.02); c.shadowColor = 'rgba(0,0,0,.4)'; c.shadowBlur = 18; c.fillStyle = '#f3efe6'; c.beginPath(); c.roundRect(-380, -150, 760, 300, 12); c.fill(); c.restore();
  const s = ['今', '晚', '?', '点', '见'], gq = Q.guess != null ? MO.smooth(seg(t, Q.guess, Q.guess + 0.5)) : 0;
  s.forEach((ch, i) => { const x = -240 + i * 120; if (i === 2) { c.save(); c.filter = `blur(${lerp(10, 0, gq)}px)`; txt(c, gq > 0.5 ? '七' : '七', x, 0, { size: 96, fam: 'PuHui-Heavy', col: gq > 0.5 ? COL.red : 'rgba(27,27,26,.55)', align: 'center' }); c.restore(); }
    else txt(c, ch, x, 0, { size: 96, fam: 'PuHui-Heavy', col: '#1b1b1a', align: 'center' }); });
  if (t >= (Q.ctx ?? 1e9)) { const q = seg(t, Q.ctx, Q.ctx + 0.5); c.save(); c.strokeStyle = COL.red; c.lineWidth = 5; c.globalAlpha = q; c.setLineDash([10, 8]);
    for (const x of [-240, -120, 120, 240]) { c.beginPath(); c.moveTo(x, 70); c.quadraticCurveTo((x) / 2, 200, 0, 80); c.stroke(); } c.restore(); }
};

// ---------- 成千上万：一个光模块变成一片，耗电往上涨 ----------
FULL.CARD.many = (c, t, id, cd, Q) => {
  const q = seg(t, Q.grow, Q.grow + 2.0), cols = 10, rows = 7, n = Math.floor(1 + q * (cols * rows - 1));
  for (let i = 0; i < n; i++) { const x = -405 + (i % cols) * 90, y = -330 + Math.floor(i / cols) * 70, hot = 0.5 + 0.5 * Math.sin(t * 5 + i);
    c.fillStyle = '#a9a69e'; c.beginPath(); c.roundRect(x - 34, y - 18, 68, 36, 8); c.fill(); c.fillStyle = `rgba(224,101,79,${0.5 + 0.4 * hot})`; c.fillRect(x - 6, y - 10, 18, 20); }
  const lv = q; c.save(); c.fillStyle = 'rgba(236,230,218,.15)'; c.beginPath(); c.roundRect(-400, 230, 800, 50, 12); c.fill(); c.fillStyle = '#e0654f'; c.beginPath(); c.roundRect(-400, 230, 800 * Math.max(0.03, lv), 50, 12); c.fill(); c.restore();
  txt(c, '耗电', -400, 200, { size: 30, fam: 'PuHui-Heavy', col: 'rgba(236,230,218,.7)' });
};

// ---------- 机房里的一台交换机：一排排光模块插在口上，光纤垂下来；圈出其中一个，拔出来一点（下集第一帧，用户 2026-11-07） ----------
const RMU = [-400, -210, -20, 170, 360], RMX = k => -300 + k * 86, RM_PICK = [2, 5];
const bz = (q, u) => { const v = 1 - u; return [v * v * v * q[0][0] + 3 * v * v * u * q[1][0] + 3 * v * u * u * q[2][0] + u * u * u * q[3][0], v * v * v * q[0][1] + 3 * v * v * u * q[1][1] + 3 * v * u * u * q[2][1] + u * u * u * q[3][1]]; };
const fib = (i, k) => { const x = RMX(k), y = RMU[i]; return [[x, y + 26], [x, y + 92], [x + 70, y + 98 + k * 1.6], [470, y + 98 + k * 1.6]]; };
const modFace = (c, x, y, s, hot) => { c.save(); c.translate(x, y); c.scale(s, s);
  const g = c.createLinearGradient(0, -30, 0, 30); g.addColorStop(0, '#dedbd3'); g.addColorStop(0.5, '#a9a69e'); g.addColorStop(1, '#c9c6bf'); c.fillStyle = g; c.beginPath(); c.roundRect(-35, -30, 70, 60, 6); c.fill();
  if (hot) { c.strokeStyle = COL.red; c.lineWidth = 4; c.stroke(); }
  c.fillStyle = '#2b3a46'; c.beginPath(); c.roundRect(-30, -44, 60, 16, 5); c.fill();                       // 拉环
  c.fillStyle = '#26292c'; c.fillRect(-20, -14, 16, 26); c.fillRect(4, -14, 16, 26);                           // 两个光口
  c.fillStyle = '#3fb5a5'; c.fillRect(-18, 0, 12, 24); c.fillRect(6, 0, 12, 24); c.restore(); };              // 插着的光纤头
FULL.CARD.room = (c, t, id, cd, Q) => {
  const X0 = -440, X1 = 500, Y0 = -500, Y1 = 500, fon = Q.fib != null ? MO.smooth(seg(t, Q.fib, Q.fib + 0.5)) : 0;
  const pk = Q.pick != null ? MO.backOut(clamp((S12(t) - Q.pick) / 0.4), 1.4) : 0;
  c.save(); c.shadowColor = 'rgba(40,30,15,.45)'; c.shadowBlur = 30; c.shadowOffsetY = 14; c.fillStyle = '#1f1f1e'; c.beginPath(); c.roundRect(X0, Y0, X1 - X0, Y1 - Y0, 18); c.fill(); c.restore();
  c.fillStyle = '#2b2b29'; c.fillRect(X0 + 12, Y0 + 14, 26, Y1 - Y0 - 28); c.fillRect(X1 - 38, Y0 + 14, 26, Y1 - Y0 - 28);   // 立柱
  RMU.forEach((y, i) => { c.fillStyle = '#323230'; c.fillRect(X0 + 44, y - 60, X1 - X0 - 88, 120);                         // 交换机
    txt(c, '交换机', 358, y - 40, { size: 24, fam: 'PuHui-Heavy', col: 'rgba(236,230,218,.5)' });
    for (let k = 0; k < 8; k++) { const ph = U.rng(i * 17 + k * 5 + 3)(), on = ((t * (1.3 + ph * 1.9) + ph) % 1) < 0.62;
      c.fillStyle = on ? '#7fd6b4' : 'rgba(127,214,180,.18)'; c.beginPath(); c.arc(RMX(k) - 30, y - 50, 4.5, 0, 7); c.fill();
      c.fillStyle = '#141413'; c.fillRect(RMX(k) - 39, y - 34, 78, 68);                                                       // 端口笼子
      if (!(i === RM_PICK[0] && k === RM_PICK[1])) modFace(c, RMX(k), y, 1, false); } });
  // 光纤：从每个模块垂下来，沿着缝走到右边的走线槽
  c.save(); c.lineCap = 'round';
  RMU.forEach((y, i) => { for (let k = 0; k < 8; k++) { const q = fib(i, k); c.strokeStyle = `rgba(63,181,165,${0.55 + 0.35 * fon})`; c.lineWidth = 4; c.beginPath(); c.moveTo(...q[0]); c.bezierCurveTo(...q[1], ...q[2], ...q[3]); c.stroke(); } });
  c.fillStyle = '#2b2b29'; c.fillRect(X1 - 44, Y0 + 40, 40, Y1 - Y0 - 80); c.restore();                                        // 走线槽
  c.save(); c.globalCompositeOperation = 'lighter';
  RMU.forEach((y, i) => { for (let k = 0; k < 8; k++) { const ph = U.rng(i * 31 + k * 7 + 11)(), u = (t * 0.7 + ph) % 1, [x, yy] = bz(fib(i, k), u), r = 9 + 5 * fon;
    const g = c.createRadialGradient(x, yy, 0, x, yy, r); g.addColorStop(0, `rgba(230,255,250,${0.55 + 0.4 * fon})`); g.addColorStop(0.45, 'rgba(155,232,219,.6)'); g.addColorStop(1, 'rgba(0,0,0,0)'); c.fillStyle = g; c.beginPath(); c.arc(x, yy, r, 0, 7); c.fill(); } });
  c.restore();
  // 被圈出的那一个：往外拔出来一点、放大
  const [pi, pkk] = RM_PICK, px = RMX(pkk), py = RMU[pi];
  c.save(); if (pk > 0) { c.shadowColor = 'rgba(0,0,0,.6)'; c.shadowBlur = 24 * pk; c.shadowOffsetY = 10 * pk; } modFace(c, px, py + 6 * pk, 1 + 0.35 * pk, pk > 0); c.restore();
  if (pk > 0) { const q = MO.smooth(seg(t, Q.pick, Q.pick + 0.5)); c.save(); c.strokeStyle = COL.red; c.lineWidth = 7; c.beginPath(); c.ellipse(px, py + 4, 78, 70, 0, -1.6, -1.6 + Math.PI * 2 * q); c.stroke(); c.restore(); }
};
})();
