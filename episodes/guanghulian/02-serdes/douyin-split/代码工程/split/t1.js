// 第 1 条（第三稿）：为什么芯片之间最快的连接只修几条路？——速度一高，几十条路很难「一起到」。科技感画风：透视地面 + 发光光尾 + 金属芯片。
(() => {
const { clamp, lerp } = U; const { W, H, COL, T, kw, txt, tape, tag, pop, ease, seg, hookText, L } = SP;
SP.END = 'x16';
const R = (s) => U.rng(s);
const glowDot = (c, x, y, r, col = [245, 215, 126], a = 1) => { c.save(); c.globalCompositeOperation = 'lighter'; const g = c.createRadialGradient(x, y, 0, x, y, r * 3); g.addColorStop(0, `rgba(255,250,235,${a})`); g.addColorStop(0.3, `rgba(${col},${0.85 * a})`); g.addColorStop(1, `rgba(${col},0)`); c.fillStyle = g; c.beginPath(); c.arc(x, y, r * 3, 0, 7); c.fill(); c.restore(); };

// ---------- 1. AI 越来越聪明 → 上万颗芯片一起练 → 每算一步都要交换数据 ----------
SP.MECH.ai = (c, t, sh) => {
  const t2 = L.x02.t0, tEx = kw('x03', '交换数据'), out = ease(t, t2 - 0.1, t2 + 1.4, 'c');
  const k = T.cam({ hy: lerp(380, 520, out), camH: lerp(900, 420, out), f: 900 }); T.bg(c, k, { scroll: t * 260, grid: 0.4 + 0.6 * out });
  if (out < 1) T.streams(c, t, { a: 0.24 * (1 - out) });
  // 地面上一大片芯片（透视），每算一步光点在相邻芯片之间来回
  if (out > 0) { c.save(); c.globalAlpha = Math.min(1, out * 1.4); const S = 280;
    const wave = t > tEx - 0.4 ? ((t - (tEx - 0.4)) % 1.2) / 1.2 : -1;
    for (let j = 18; j >= 0; j--) for (let i = -6; i <= 6; i++) { const x = i * S, z = 500 + j * S - ((t * 120) % S); if (z < 300) continue;
      const a = T.P(k, x - 80, 0, z - 80), b = T.P(k, x + 80, 0, z - 80), cc = T.P(k, x + 80, 0, z + 80), d = T.P(k, x - 80, 0, z + 80), fade = clamp(1 - z / 5600);
      c.fillStyle = `rgba(52,50,46,${fade})`; c.strokeStyle = `rgba(226,181,74,${0.55 * fade})`; c.lineWidth = 1.5; c.beginPath(); [a, b, cc, d].forEach((p, n) => n ? c.lineTo(p[0], p[1]) : c.moveTo(p[0], p[1])); c.closePath(); c.fill(); c.stroke();
      if (wave >= 0 && fade > 0.05) { const m = MO.cubicInOut(Math.min(1, wave / 0.75)), al = Math.sin(Math.PI * Math.min(1, wave / 0.85)) * fade;
        if (i < 6) { const p = T.P(k, x + 80 + (S - 160) * m, 10, z); glowDot(c, p[0], p[1], 7 * p[2], [245, 215, 126], al); const p2 = T.P(k, x + S - 80 - (S - 160) * m, 10, z + 40); glowDot(c, p2[0], p2[1], 7 * p2[2], [245, 215, 126], al); }
        if (j < 18) { const p = T.P(k, x, 10, z + 80 + (S - 160) * m); glowDot(c, p[0], p[1], 7 * p[2], [245, 215, 126], al); } } }
    c.restore();
    if (t > t2 + 0.4) tag(c, '上万颗芯片，一起训练一个模型', W / 2, 1300, { size: 42, t, at: t2 + 0.4 });
    if (t > tEx - 0.4) tape(c, '每算一步，都要互相交换数据', W / 2, 330, { size: 52, t, at: tEx - 0.4 }); }
  // 手机里和 AI 对话（不出现品牌），往地面上缩下去
  if (out < 1) { const s = lerp(1, 0.25, out); c.save(); c.globalAlpha = 1 - out; c.translate(W / 2, 900 + 300 * out + 12 * Math.sin(t * 2.2)); c.rotate(0.015 * Math.sin(t * 1.4)); c.scale(s, s); c.translate(-W / 2, -900);
    SP.phone(c, W / 2, 900, 560, 980, (g, x, y, w, h) => { const bg = g.createLinearGradient(0, y, 0, y + h); bg.addColorStop(0, '#11181a'); bg.addColorStop(1, '#0a0d0e'); g.fillStyle = bg; g.fillRect(x, y, w, h);
      txt(g, 'AI 助手', x + w / 2, y + 60, { size: 34, fam: 'PuHui-Heavy', col: COL.cream, align: 'center' });
      g.font = '32px "PuHui-Medium"'; g.fillStyle = COL.goldHi; g.beginPath(); g.roundRect(x + w - 380, y + 120, 350, 70, 22); g.fill(); g.fillStyle = COL.ink; g.textBaseline = 'middle'; g.fillText('帮我把这段话翻成英文', x + w - 362, y + 156);
      g.fillStyle = '#26302f'; g.beginPath(); g.roundRect(x + 30, y + 220, w - 110, 300, 22); g.fill();
      for (let n = 0; n < 5; n++) { const q = clamp(t * 2.4 - n * 0.4); g.fillStyle = 'rgba(155,232,219,.35)'; g.beginPath(); g.roundRect(x + 56, y + 256 + n * 50, (w - 170) * (n === 4 ? 0.5 : 1) * q, 24, 8); g.fill(); }
      const cur = (Math.floor(t * 3) % 2) ? 1 : 0.2; g.fillStyle = `rgba(155,232,219,${cur})`; g.fillRect(x + 56 + (w - 170) * clamp(t * 2.4 - 1.6) * 0.5, y + 456, 4, 28); }); c.restore(); }
  const up = ease(t, L.x03.t0 - 0.3, L.x03.t0 + 0.3, 'c');
  if (up < 1) { c.save(); c.globalAlpha = 1 - up; hookText(c, t, ['AI 越来越快，', '芯片之间的路却越修越少？'], { y: 230, size: 64 });
    hookText(c, t, ['AI 越来越聪明，', '靠的是上万颗芯片一起练。'], { y: 1500, size: 58, ids: ['x01', 'x02'], bg: '#0f0f0e' }); c.restore(); }
};

// ---------- 2. 最快的连接只修几条路；打印机线 vs USB；为什么？ ----------
SP.MECH.few = (c, t, sh) => {
  const k = T.cam({ hy: 960, camH: 300 }); T.bg(c, k, { scroll: t * 300, grid: 0.6 }); T.streams(c, t, { a: 0.14, seed: 5 });
  const t4 = L.x04.t0, t5 = L.x05.t0, tPr = kw('x05', '打印机线'), tUsb = kw('x05', 'USB'), t6 = L.x06.t0;
  const q4 = 1 - ease(t, t5 - 0.3, t5 + 0.2);
  if (q4 > 0) { c.save(); c.globalAlpha = q4;
    for (let i = 0; i < 16; i++) { const x = 180 + i * 48; c.strokeStyle = 'rgba(236,230,218,.12)'; c.lineWidth = 3; c.setLineDash([10, 12]); c.beginPath(); c.moveTo(x, 560); c.lineTo(x, 1220); c.stroke(); } c.setLineDash([]);
    for (const x of [W / 2 - 70, W / 2 + 70]) { T.glowLine(c, [[x, 560], [x, 1220]], { lw: 8 }); for (let n = 0; n < 10; n++) { const y = 560 + ((t * 1100 + n * 66 + (x > W / 2 ? 33 : 0)) % 660); glowDot(c, x, y, 7); } }
    T.chip(c, W / 2, 440, 760, 240, { label: '芯片', t }); T.chip(c, W / 2, 1340, 760, 240, { label: '芯片', t: t + 0.6 }); c.restore();
    if (t > kw('x04', '几条路') - 0.2) tape(c, '只修几条路', W / 2, 890, { size: 56, t, at: kw('x04', '几条路') - 0.2, r: -0.03 }); }
  const q5 = ease(t, t5 - 0.2, t5 + 0.4);
  if (q5 > 0) { c.save(); c.globalAlpha = q5; const yC = 700;
    const dx = 290; c.fillStyle = '#8a877f'; c.beginPath(); c.moveTo(dx - 200, yC - 70); c.lineTo(dx + 200, yC - 70); c.lineTo(dx + 175, yC + 70); c.lineTo(dx - 175, yC + 70); c.closePath(); c.fill();
    c.fillStyle = '#1b1a18'; c.beginPath(); c.moveTo(dx - 175, yC - 50); c.lineTo(dx + 175, yC - 50); c.lineTo(dx + 155, yC + 50); c.lineTo(dx - 155, yC + 50); c.closePath(); c.fill();
    for (let n = 0; n < 13; n++) glowDot(c, dx - 156 + n * 26, yC - 20, 4); for (let n = 0; n < 12; n++) glowDot(c, dx - 143 + n * 26, yC + 20, 4);
    c.fillStyle = '#4a4741'; c.fillRect(dx - 70, yC + 70, 140, 260); txt(c, '25 针', dx, yC - 130, { size: 52, fam: 'PuHui-Heavy', col: COL.cream, align: 'center' });
    const ux = 790; c.fillStyle = '#c9c6be'; c.beginPath(); c.roundRect(ux - 70, yC - 50, 140, 110, 6); c.fill(); c.fillStyle = '#1b1a18'; c.fillRect(ux - 56, yC - 36, 112, 40);
    for (let n = 0; n < 4; n++) { c.fillStyle = COL.goldHi; c.fillRect(ux - 46 + n * 26, yC - 30, 16, 26); } c.fillStyle = '#3a3833'; c.fillRect(ux - 22, yC + 60, 44, 270);
    txt(c, '4 根线', ux, yC - 130, { size: 52, fam: 'PuHui-Heavy', col: COL.cream, align: 'center' });
    for (let n = 0; n < 3; n++) glowDot(c, dx, yC + 90 + ((t * 70 + n * 90) % 240), 9, [245, 215, 126], 0.8); for (let n = 0; n < 14; n++) glowDot(c, ux, yC + 75 + ((t * 520 + n * 18) % 255), 5, [245, 215, 126], 0.9);
    const qa = ease(t, tPr, tPr + 0.6, 'o'), qb = ease(t, tUsb - 0.3, tUsb + 0.8, 'o'), by = 1300;
    c.fillStyle = COL.creamDim; c.fillRect(dx - 70, by - 16 * qa, 140, 16 * qa);
    if (qb > 0) { c.save(); c.globalCompositeOperation = 'lighter'; const g = c.createLinearGradient(0, by - 330 * qb, 0, by); g.addColorStop(0, 'rgba(255,240,190,.95)'); g.addColorStop(1, 'rgba(226,181,74,.5)'); c.fillStyle = g; c.shadowColor = COL.gold; c.shadowBlur = 30; c.fillRect(ux - 70, by - 330 * qb, 140, 330 * qb); c.restore(); }
    txt(c, '每秒约 2 兆字节', dx, by + 50, { size: 34, fam: 'PuHui-Heavy', col: COL.creamDim, align: 'center' }); if (qb > 0.2) txt(c, '每秒几十兆字节', ux, by + 50, { size: 34, fam: 'PuHui-Heavy', col: COL.goldHi, align: 'center' });
    txt(c, '老打印机线', dx, by + 98, { size: 30, col: COL.creamDim, align: 'center' }); txt(c, 'USB 2.0', ux, by + 98, { size: 30, col: COL.creamDim, align: 'center' }); c.restore(); }
  if (t > t6 - 0.15) tape(c, '为什么路少了，反而快？', W / 2, 360, { size: 66, t, at: t6 - 0.15, r: -0.02 });
};

// ---------- 3. 透视通道：路越多送得越多 → 每批必须一起到 → 慢时不难 → 快了窗口变窄 → 一条长一点就混进下一批 → 路越多越难一样长 ----------
SP.MECH.lanes = (c, t, sh) => {
  const tMore = kw('x07', '路越多'), tGate = kw('x08', '一起到'), tJoin = kw('x08', '拼出'), tSlow = L.x09.t0, tFast = kw('x10', '速度一快'), tShort = kw('x10', '越来越短'), tLong = kw('x11', '长了一点点'), tMix = kw('x11', '混进了下一批'), tWrong = kw('x11', '拼错'), tAll = L.x12.t0;
  const k = T.cam({ hy: 520, camH: 320, f: 950 }), V = 1500;                      // V：信号在路上的速度（固定；变快的是「一批接一批」）
  T.bg(c, k, { scroll: t * V });
  const N = 12, X = i => (i - (N - 1) / 2) * 110;
  const nOn = Math.round(lerp(2, N, ease(t, tMore - 0.4, tMore + 1.2, 'o')));      // 路一条条亮起来
  const on = i => Math.abs(i - (N - 1) / 2) < nOn / 2;
  const bendAmp = ease(t, tLong - 0.5, tLong + 0.3), allBend = ease(t, tAll - 0.2, tAll + 0.8);
  const bendOf = i => z => { const a = i === 7 ? 70 * bendAmp : 0, r = R(i * 13 + 5), b = allBend * (25 + 40 * r()) * (i === 7 ? 0 : 1); const z0 = 1300 + r() * 600;
    return (z > 1300 && z < 2100 ? a * Math.sin(Math.PI * (z - 1300) / 800) : 0) + (z > z0 && z < z0 + 700 ? b * Math.sin(Math.PI * (z - z0) / 700) : 0); };
  const extra = i => (i === 7 ? 0.24 * bendAmp : 0) + (i !== 7 ? allBend * 0.04 * (0.4 + R(i * 13 + 5)()) : 0);   // 多走的那段，换算成晚到的秒数
  for (let i = 0; i < N; i++) T.lane(c, k, X(i), 120, 6000, { a: on(i) ? 0.55 : 0.08, bend: bendOf(i) });
  // 批次：周期 P 从 1.5 s 降到 0.42 s；窗口 = 0.6 P，以 z 方向的厚度画成一道门
  const pAt = s => lerp(1.5, 0.42, ease(s, tFast - 0.2, tShort + 0.3, 'c'));
  const heats = []; { let s = tMore - 0.2; while (s < sh.t1 + 2) { heats.push(s); s += pAt(s); } }
  const zGate = 430, Pnow = pAt(t), win = 0.6 * Pnow, gateQ = ease(t, tGate - 0.4, tGate + 0.2);
  if (gateQ > 0) T.gate(c, k, zGate - win * V / 2, nOn * 110 + 40, 160, win * V, { a: gateQ, flash: 0 });
  const ARR = 5600 / V;                                                              // 从远处到门口的时间
  let lastCap = null;
  heats.forEach((s, h) => { const cap = s + ARR, winH = 0.6 * pAt(s);
    for (let i = 0; i < N; i++) { if (!on(i)) continue; const late = extra(i), z = zGate + (cap + late - t) * V; if (z < zGate - (gateQ > 0 ? winH * V / 2 + 40 : 120) || z > 6000) continue;
      const bad = gateQ > 0 && late > winH / 2 && t > cap + winH / 2 - 0.05; T.bit(c, k, X(i) + bendOf(i)(z), 14, z, { len: 240, bad }); }
    if (t >= cap) lastCap = { cap, h, winH }; });
  // 门口拼出来的这一批数据：一排小方块；落在窗口外的那一位变红、打叉
  if (lastCap && gateQ > 0 && t > tGate) { const { cap, h, winH } = lastCap, q = clamp((t - cap) / 0.12); let anyBad = false;
    const ids = [...Array(N).keys()].filter(on), w = Math.min(70, 900 / ids.length);
    ids.forEach((i, n) => { const late = extra(i), bad = late > winH / 2, x = W / 2 + (n - (ids.length - 1) / 2) * (w + 8), y = 1210; anyBad = anyBad || bad;
      c.save(); c.globalAlpha = q; c.fillStyle = bad ? COL.coral : 'rgba(245,215,126,.95)'; c.shadowColor = bad ? COL.coral : COL.gold; c.shadowBlur = 16; c.beginPath(); c.roundRect(x - w / 2, y - w / 2, w, w, 8); c.fill(); c.shadowBlur = 0;
      txt(c, bad ? '?' : String(R(h * 31 + i)() < 0.5 ? 0 : 1), x, y + 2, { size: w * 0.62, fam: 'PuHui-Heavy', col: COL.ink, align: 'center' }); c.restore(); });
    txt(c, anyBad ? '✗ 拼错了' : '✓ 拼出一批', W / 2, 1300, { size: 44, fam: 'PuHui-Heavy', col: anyBad ? COL.coral : COL.mint, align: 'center', alpha: q }); }
  // 文字标签
  if (t > tMore - 0.3 && t < tGate) MD.label(c, `一次送 ${nOn} 个`, W / 2, 330, { size: 52, align: 'center', bg: COL.cream, fg: COL.ink });
  if (t > tGate - 0.3 && t < tSlow) tape(c, '每一批，必须一起到', W / 2, 330, { size: 56, t, at: tGate - 0.3 });
  if (t > tSlow && t < tFast) tag(c, '慢的时候：批和批隔得远，窗口很宽', W / 2, 330, { size: 42, t, at: tSlow });
  if (t > tFast && t < tLong - 0.3) tape(c, '越快，窗口越窄', W / 2, 330, { size: 58, t, at: tFast });
  if (t > tLong - 0.3) { const [ex, ey] = T.P(k, X(7) + 40, 0, 1700); c.save(); c.strokeStyle = COL.redHi; c.lineWidth = 5; c.shadowColor = COL.redHi; c.shadowBlur = 16; c.beginPath(); c.ellipse(ex, ey, 70, 34, 0, 0, 7 * ease(t, tLong - 0.3, tLong + 0.3)); c.stroke(); c.restore();
    if (t < tAll) tape(c, t > tMix - 0.1 ? '晚到一步，混进了下一批' : '这条路长了一点点', W / 2, 330, { size: 54, t, at: t > tMix - 0.1 ? tMix - 0.1 : tLong - 0.3 }); }
  if (t > tWrong - 0.1 && t < tWrong + 0.25) { c.save(); c.fillStyle = `rgba(239,125,98,${0.18 * (1 - seg(t, tWrong - 0.1, tWrong + 0.25))})`; c.fillRect(0, 0, W, H); c.restore(); }
  if (t > tAll - 0.2) tape(c, '路越多，越难每条都一样长', W / 2, 330, { size: 54, t, at: tAll - 0.2 });
};

// ---------- 4. 只修几条路、排成一列，一路提速 ----------
SP.MECH.serial = (c, t, sh) => {
  const tFew = kw('x13', '只修几条路'), tLine = kw('x13', '排成一列'), tUp = kw('x13', '一路提速');
  const merge = ease(t, tFew - 0.3, tFew + 0.9, 'c'), sp = lerp(1500, 4200, ease(t, tUp - 0.6, tUp + 0.8, 'c'));
  const k = T.cam({ hy: 520, camH: lerp(320, 220, merge), f: 950 }); T.bg(c, k, { scroll: t * sp });
  const N = 12, X0 = i => (i - (N - 1) / 2) * 110, X = i => lerp(X0(i), i < N / 2 ? -80 : 80, merge);
  for (let i = 0; i < N; i++) { const keep = i === 0 || i === N - 1; T.lane(c, k, X(i), 120, 6000, { a: keep ? lerp(0.5, 0.9, merge) : 0.5 * (1 - merge), w: keep ? lerp(26, 40, merge) : 26 }); }
  const lq = ease(t, tLine - 0.3, tLine + 0.3);
  // 合并前：参差的一排；排成一列后：两条路上光点一个接一个，光尾越拉越长
  if (lq < 1) for (let i = 0; i < N; i++) { const z = 520 + ((t * 1500 + R(i + 3)() * 900) % 5000); T.bit(c, k, X(i), 14, z, { len: 240 }); }
  if (lq > 0) for (const lane of [0, 1]) for (let n = 0; n < 60; n++) { const z = 520 + ((t * sp + n * 120 + lane * 60) % 5500); c.save(); c.globalAlpha = lq; T.bit(c, k, lane ? 80 : -80, 14, z, { len: lerp(240, 700, (sp - 1500) / 2700) }); c.restore(); }
  if (t > tLine - 0.3) tape(c, '排成一列，一个接一个', W / 2, 330, { size: 56, t, at: tLine - 0.3 });
  if (t > tUp - 0.3) { tag(c, '不用等谁，一路提速', W / 2, 1300, { size: 48, bg: COL.goldHi, fg: COL.ink, t, at: tUp - 0.3 });
    // 速度线：屏幕边缘的放射状光线
    const q = ease(t, tUp - 0.3, tUp + 0.6); c.save(); c.globalCompositeOperation = 'lighter'; for (let n = 0; n < 40; n++) { const r = R(n + Math.floor(t * 20) * 7), a = r() * Math.PI * 2, r0 = 380 + r() * 300, r1 = r0 + 200 + r() * 400;
      c.strokeStyle = `rgba(245,215,126,${0.25 * q})`; c.lineWidth = 2; c.beginPath(); c.moveTo(W / 2 + Math.cos(a) * r0, 520 + Math.sin(a) * r0 * 1.6); c.lineTo(W / 2 + Math.cos(a) * r1, 520 + Math.sin(a) * r1 * 1.6); c.stroke(); } c.restore(); }
};
})();
