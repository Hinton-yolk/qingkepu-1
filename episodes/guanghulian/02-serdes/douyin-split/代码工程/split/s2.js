// 第 2 条：连续五个 1，芯片怎么知道是五个、不是四个？（节拍恢复 / CDR）
(() => {
const { clamp, lerp } = U; const { W, H, COL, kw, txt, tape, tag, pop, ease, seg, darkBg, deskShot, hookText, endCard, L } = SP;
const R = (s) => U.rng(s);
const box = (c, x, y, b, { s = 64, col = COL.cream, ink = COL.ink, alpha = 1, bad = false, edge = 1 } = {}) => { if (alpha <= 0) return; c.save(); c.globalAlpha *= alpha; c.translate(x, y);
  c.fillStyle = bad ? COL.coral : col; c.beginPath(); c.roundRect(-s / 2, -s / 2, s, s, s * 0.14); c.fill();
  if (b != null) { c.font = `${Math.round(s * 0.66)}px "PuHui-Heavy"`; c.fillStyle = ink; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText(String(b), 0, s * 0.04); } c.restore(); };
const chip = (c, x, y, w, h, label, { glow = 0, alpha = 1 } = {}) => { c.save(); c.globalAlpha *= alpha; c.shadowColor = 'rgba(0,0,0,.5)'; c.shadowBlur = 24; c.shadowOffsetY = 8;
  c.fillStyle = '#34322e'; c.beginPath(); c.roundRect(x - w / 2, y - h / 2, w, h, 14); c.fill(); c.shadowColor = 'transparent';
  c.strokeStyle = glow ? `rgba(245,215,126,${0.5 + 0.5 * glow})` : 'rgba(236,230,218,.35)'; c.lineWidth = 3; c.stroke();
  c.fillStyle = '#45423c'; c.beginPath(); c.roundRect(x - w * 0.32, y - h * 0.32, w * 0.64, h * 0.64, 8); c.fill();
  if (label) txt(c, label, x, y + 2, { size: Math.min(44, h * 0.32), fam: 'PuHui-Heavy', col: COL.cream, align: 'center' }); c.restore(); };
// 两电平的方波：bits 从 x0 开始，每位宽 bw；edge 是跳变的斜率宽度（0 = 理想方波）
const wave = (c, bits, x0, bw, yHi, yLo, { col = COL.gold, lw = 8, glow = 0.7, x1 = 1e9, alpha = 1 } = {}) => { c.save(); c.globalAlpha *= alpha; c.strokeStyle = col; c.lineWidth = lw; c.lineJoin = 'round'; c.lineCap = 'round';
  if (glow) { c.shadowColor = COL.gold; c.shadowBlur = 18 * glow; } c.beginPath(); let first = true;
  bits.forEach((b, i) => { const xa = x0 + i * bw, xb = Math.min(x1, xa + bw), y = b ? yHi : yLo; if (xa > x1) return; if (first) { c.moveTo(xa, y); first = false; } else c.lineTo(xa, y); c.lineTo(xb, y); });
  c.stroke(); c.restore(); };
const metronome = (c, x, y, s, t) => { c.save(); c.translate(x, y); c.fillStyle = '#4a463f'; c.beginPath(); c.moveTo(-s * 0.5, s * 0.6); c.lineTo(s * 0.5, s * 0.6); c.lineTo(s * 0.22, -s * 0.6); c.lineTo(-s * 0.22, -s * 0.6); c.closePath(); c.fill();
  c.strokeStyle = COL.cream; c.lineWidth = 6; c.lineCap = 'round'; const a = 0.45 * Math.sin(t * Math.PI * 2 * 1.2); c.beginPath(); c.moveTo(0, s * 0.45); c.lineTo(Math.sin(a) * s * 0.9, s * 0.45 - Math.cos(a) * s * 0.9); c.stroke(); c.restore(); };

// ---------- 1. 第一帧：示波器上一段平平的高电平 + 「这里有几个 1？」 ----------
const FIVE = [0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0];
const scope = (c, t, { x = 90, y = 700, w = 900, h = 640, bits = FIVE } = {}) => {
  // 仪器外壳 + 屏幕网格 + 旋钮：一眼认出是示波器
  c.save(); c.shadowColor = 'rgba(0,0,0,.6)'; c.shadowBlur = 40; c.shadowOffsetY = 14; c.fillStyle = '#3a3833'; c.beginPath(); c.roundRect(x - 40, y - 40, w + 80, h + 210, 28); c.fill(); c.restore();
  c.fillStyle = '#10140f'; c.beginPath(); c.roundRect(x, y, w, h, 12); c.fill();
  c.strokeStyle = 'rgba(127,214,180,.12)'; c.lineWidth = 2; for (let i = 1; i < 10; i++) { c.beginPath(); c.moveTo(x + w * i / 10, y); c.lineTo(x + w * i / 10, y + h); c.stroke(); } for (let j = 1; j < 8; j++) { c.beginPath(); c.moveTo(x, y + h * j / 8); c.lineTo(x + w, y + h * j / 8); c.stroke(); }
  for (let k = 0; k < 5; k++) { const kx = x + 90 + k * 180, ky = y + h + 95; c.fillStyle = '#25231f'; c.beginPath(); c.arc(kx, ky, 34, 0, 7); c.fill(); c.strokeStyle = COL.creamDim; c.lineWidth = 4; const a = k * 1.3 + 0.2 * Math.sin(t * 0.8 + k); c.beginPath(); c.moveTo(kx, ky); c.lineTo(kx + Math.cos(a) * 26, ky + Math.sin(a) * 26); c.stroke(); }
  const bw = w / (bits.length - 0.4), x0 = x + 10 - (t * 6) % 3;
  c.save(); c.beginPath(); c.rect(x, y, w, h); c.clip(); wave(c, bits, x0, bw, y + h * 0.3, y + h * 0.72, { col: COL.goldHi }); c.restore();
  return { bw, x0, yHi: y + h * 0.3, yLo: y + h * 0.72 };
};
SP.MECH.scope = (c, t, sh) => {
  darkBg(c);
  const S = scope(c, t), a = S.x0 + 3 * S.bw, b = S.x0 + 8 * S.bw;
  hookText(c, t, ['五个 1 连在一起，', '就是一条直线。'], { y: 330, size: 92, ids: ['b01', 'b02'] });
  // 第一帧就有的大字问题：贴在那段高电平上
  tag(c, '这里有几个 1？', (a + b) / 2, S.yHi - 110, { size: 64, bg: COL.cream, fg: COL.ink, r: -0.02 });
  c.save(); c.strokeStyle = COL.redHi; c.lineWidth = 5; c.setLineDash([12, 10]); c.lineDashOffset = -t * 30; c.beginPath(); c.roundRect(a, S.yHi - 40, b - a, 80, 14); c.stroke(); c.restore();
  // 听出节拍：下面一排刻度把这段切成 5 格，数 1-2-3-4-5
  const tb = kw('b03', '节拍');
  if (t > tb - 0.3) { for (let k = 0; k <= 5; k++) { const q = ease(t, tb - 0.3 + k * 0.08, tb + k * 0.08, 'o'); const xx = a + k * S.bw; c.save(); c.globalAlpha = q; c.strokeStyle = COL.mint; c.lineWidth = 5; c.beginPath(); c.moveTo(xx, S.yLo + 70); c.lineTo(xx, S.yLo + 70 - 60 * q); c.stroke(); c.restore(); }
    const tc = kw('b03', '数得清'); for (let k = 0; k < 5; k++) { const at = tb + 0.4 + k * ((tc - tb - 0.2) / 5); if (t > at) txt(c, String(k + 1), a + (k + 0.5) * S.bw, S.yHi + 70, { size: 64, fam: 'PuHui-Heavy', col: COL.mint, align: 'center', alpha: ease(t, at, at + 0.15) }); } }
};

// ---------- 2. 排成一列送过去；一条通道每秒上千亿个比特 ----------
SP.MECH.stream = (c, t, sh) => {
  darkBg(c);
  const tRow = kw('b05', '并排'), tFast = kw('b05', '极快'), tNum = kw('b06', '上千亿');
  chip(c, W / 2, 360, 860, 170, '芯片 A'); chip(c, W / 2, 1300, 860, 170, '芯片 B');
  c.save(); c.strokeStyle = 'rgba(226,181,74,.55)'; c.lineWidth = 6; c.shadowColor = COL.gold; c.shadowBlur = 12; c.beginPath(); c.moveTo(W / 2, 450); c.lineTo(W / 2, 1210); c.stroke(); c.restore();
  const sp = lerp(380, 1500, ease(t, tFast - 0.3, tFast + 1.2, 'c')), gap = lerp(80, 46, ease(t, tFast - 0.3, tFast + 1.2));
  const BITS = [1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1];
  let base = 0; { const t0 = sh.t0 + 0.3; base = (t - t0) * 380 + Math.max(0, t - tFast) * (sp - 380) * 0.6; }
  for (let n = 0; n < 40; n++) { const y = 480 + ((base + n * gap) % 720); const b = BITS[(n + Math.floor((base) / (gap * 12))) % 12]; box(c, W / 2, y, b, { s: 40, col: COL.goldHi, alpha: seg(y, 470, 520) * (1 - seg(y, 1150, 1200)) }); }
  // 「并排的数据」：芯片 A 里一排货，一件件滑进出口
  if (t > tRow - 0.3 && t < tFast + 1.5) { const q = ease(t, tRow - 0.3, tRow + 0.2) * (1 - ease(t, tFast + 0.8, tFast + 1.5));
    for (let j = 0; j < 8; j++) box(c, W / 2 + (j - 3.5) * 92, 590, [1, 0, 1, 1, 0, 0, 1, 0][j], { s: 66, alpha: q * (1 - seg(t, tRow + 0.3 + j * 0.25, tRow + 0.5 + j * 0.25) * 0.7) }); }
  if (t > tNum - 0.5) { const q = pop(t, tNum - 0.5), n = Math.round(lerp(0, 1120, ease(t, tNum - 0.5, tNum + 0.6, 'o')));
    c.save(); c.globalAlpha = Math.min(1, q); c.fillStyle = 'rgba(15,15,14,.92)'; c.beginPath(); c.roundRect(140, 700, 800, 260, 20); c.fill();
    txt(c, `${n} 亿`, W / 2, 800, { size: 120, fam: 'PuHui-Heavy', col: COL.goldHi, align: 'center' }); txt(c, '个比特 / 秒 · 每条通道', W / 2, 905, { size: 44, fam: 'PuHui-Heavy', col: COL.cream, align: 'center' }); c.restore(); }
};

// ---------- 3. 把一秒放大、再放大、再放大，才看得见一个个比特 ----------
SP.MECH.zoom = (c, t, sh) => {
  darkBg(c);
  const Z = [kw('b07', '放大'), kw('b07', '再放大'), kw('b07', '再放大', 1)], tBits = kw('b08', '一个个比特'), tLbl = kw('b08', '这一秒里');
  const LV = ['1 秒', '1 毫秒', '1 微秒', '1 纳秒'];
  const bx0 = 90, bx1 = 990, by = 900, bh = 330, cx = W / 2;
  let lv = 0; Z.forEach((z, i) => { if (t >= z) lv = i + 1; });
  const zp = lv > 0 ? MO.cubicInOut(seg(t, Z[lv - 1], Z[lv - 1] + 0.55)) : 1, final = t >= tBits;
  const dense = (layer, sx, alpha) => { const r = R(101 + layer * 17); c.save(); c.globalAlpha *= alpha; c.fillStyle = 'rgba(245,215,126,.8)';
    const n = 300, w = (bx1 - bx0) / n; for (let i = 0; i < n; i++) { const hgt = r() < 0.5 ? bh * 0.85 : bh * 0.12 + r() * 0.1 * bh; const x = cx + ((bx0 + i * w) - cx) * sx; if (x + w * sx < bx0 - 5 || x > bx1 + 5) continue; c.fillRect(x, by + bh / 2 - hgt, Math.max(1, w * sx * 0.62), hgt); } c.restore(); };
  c.save(); c.beginPath(); c.rect(bx0, by - bh / 2 - 20, bx1 - bx0, bh + 40); c.clip();
  // 平时也在慢慢往左流，画面不停
  c.translate(-((t * 18) % 6), 0);
  if (!final) { if (lv === 0 || zp >= 1) dense(lv, 1, 1); else { dense(lv - 1, 1 + 9 * zp, 1 - zp * 0.6); dense(lv, 0.1 + 0.9 * zp, zp); } }
  else { const q = MO.cubicInOut(seg(t, tBits, tBits + 0.5)), B = [1, 0, 1, 1, 0, 1, 0, 0, 1, 1], w = (bx1 - bx0) / B.length;
    dense(9, 1 + 4 * q, 1 - q); wave(c, B, bx0, w, by - bh / 2 + 20, by + bh / 2 - 20, { alpha: q, col: COL.goldHi });
    B.forEach((b, i) => txt(c, String(b), bx0 + (i + 0.5) * w, by - bh / 2 + 90, { size: 60, fam: 'PuHui-Heavy', col: COL.cream, align: 'center', alpha: q })); }
  c.restore();
  // 刻度尺：这一段有多长
  const lab = final ? '不到 0.1 纳秒里的 10 个比特' : LV[lv];
  tag(c, lab, cx, by - bh / 2 - 110, { size: 52, t, at: lv ? Z[lv - 1] : sh.t0 + 0.1 });
  if (!final && lv < 3) { const pre = seg(t, (Z[lv] ?? 1e9) - 0.6, (Z[lv] ?? 1e9) - 0.2); if (pre > 0) { c.save(); c.globalAlpha = pre; c.strokeStyle = COL.redHi; c.lineWidth = 6; c.strokeRect(cx - 45, by - bh / 2 - 14, 90, bh + 28); c.restore(); } }
  Z.forEach((z, i) => { if (t >= z && t < z + 1.1 && !final) tape(c, i ? '再放大' : '放大', cx, by + bh / 2 + 120, { size: 56, t, at: z }); });
  if (t > tLbl) tag(c, '这一秒里，有上千亿个这样的比特', cx, by + bh / 2 + 130, { size: 44, t, at: tLbl, rate: 26 });
};

// ---------- 4. 到了收货端拆回一排；0 和 1 不是一件件分开的包裹 ----------
SP.MECH.unpack = (c, t, sh) => {
  darkBg(c);
  const B = [1, 0, 1, 1, 1, 1, 1, 0], xs = j => W / 2 + (j - 3.5) * 110, rowY = 820;
  const tFan = kw('b09', '拆开'), tHard = kw('b10', '难处'), tSig = kw('b10', '0 和 1'), tPkg = kw('b10', '包裹');
  chip(c, W / 2, 1300, 860, 170, '芯片 B（收货端）');
  // 一列货从上面下来，拆回一排
  for (let j = 0; j < 8; j++) { const arr = sh.t0 + 0.2 + j * 0.18, q = MO.cubicInOut(seg(t, arr, arr + 0.45)), fan = MO.cubicInOut(seg(t, tFan - 0.2 + j * 0.05, tFan + 0.4 + j * 0.05));
    const x = lerp(W / 2, xs(j), fan), y = lerp(lerp(300, 560, q), rowY, fan); const melt = ease(t, tSig, tSig + 1.0);
    if (q > 0) { const s = 96; c.save(); c.globalAlpha = 1 - melt; box(c, x, y, B[j], { s }); c.restore(); } }
  // 包裹的边框消失，变成一条连在一起的电压线
  const melt = ease(t, tSig, tSig + 1.0);
  if (melt > 0) { wave(c, B, xs(0) - 55, 110, rowY - 60, rowY + 60, { alpha: melt, col: COL.goldHi });
    B.forEach((b, j) => { c.save(); c.globalAlpha = (1 - melt) * 0.9; c.strokeStyle = COL.cream; c.lineWidth = 3; c.setLineDash([8, 6]); c.strokeRect(xs(j) - 48, rowY - 48, 96, 96); c.restore(); });
    if (t > tPkg - 0.2) { const q = ease(t, tPkg - 0.2, tPkg + 0.3); c.save(); c.globalAlpha = q; c.strokeStyle = COL.redHi; c.lineWidth = 6; c.beginPath(); c.roundRect(xs(2) - 60, rowY - 110, 5 * 110 + 10, 220, 20); c.stroke(); c.restore();
      tag(c, '没有一件件分开的包裹', W / 2, rowY + 220, { size: 44, bg: COL.red, fg: '#f6efe4', t, at: tPkg }); } }
  if (t > tHard - 0.2 && t < tSig + 0.5) tape(c, '难处在哪？', W / 2, 560, { size: 56, t, at: tHard - 0.2 });
};

// ---------- 5. 要数清就得知道每个比特多长（节拍）；只看高低数不清 ----------
SP.MECH.level = (c, t, sh) => {
  darkBg(c);
  const B = [0, 1, 1, 1, 1, 1, 0], x0 = 120, bw = 120, yHi = 700, yLo = 960;
  const tLen = kw('b12', '多长时间'), tBeat = kw('b12', '节拍'), tOnly = kw('b13', '只看高低');
  wave(c, B, x0, bw, yHi, yLo, { col: COL.goldHi, lw: 10 });
  tag(c, '这里有几个 1？', x0 + 3.5 * bw, yHi - 110, { size: 56, t, at: sh.t0 + 0.1 });
  // 正确节拍：每格 bw，数出 5；节拍拉长一点点：只剩 4 格，就数错了
  const stretch = ease(t, tOnly - 0.1, tOnly + 0.6, 'c'), bwT = lerp(bw, bw * 1.25, stretch), show = ease(t, tLen - 0.4, tLen + 0.2);
  if (show > 0) { c.save(); c.globalAlpha = show; for (let k = 0; k <= 8; k++) { const xx = x0 + bw + k * bwT; if (xx > x0 + 6 * bw + 2) break; c.strokeStyle = stretch > 0.5 ? COL.coral : COL.mint; c.lineWidth = 5; c.beginPath(); c.moveTo(xx, yLo + 60); c.lineTo(xx, yLo + 120); c.stroke();
      if (xx + bwT <= x0 + 6 * bw + 2) txt(c, String(k + 1), xx + bwT / 2, yLo + 180, { size: 60, fam: 'PuHui-Heavy', col: stretch > 0.5 ? COL.coral : COL.mint, align: 'center' }); }
    // 一格的宽度
    c.strokeStyle = COL.cream; c.lineWidth = 4; c.beginPath(); c.moveTo(x0 + bw, yLo + 250); c.lineTo(x0 + bw + bwT, yLo + 250); c.stroke(); txt(c, '一个比特多长', x0 + bw + bwT + 20, yLo + 252, { size: 38, fam: 'PuHui-Heavy', col: COL.cream });
    c.restore(); }
  if (t > tBeat - 0.1 && stretch < 0.5) tape(c, '这就是「节拍」', W / 2, 1360, { size: 58, t, at: tBeat - 0.1 });
  if (stretch >= 0.5) { tag(c, '节拍差一点，就数成 4 个', W / 2, 1360, { size: 46, bg: COL.coral, fg: COL.ink, t, at: tOnly + 0.3 }); }
};

// ---------- 6. 不送节拍器：从跳变里推算节拍；先打乱；按节拍清点；CDR ----------
SP.MECH.cdr = (c, t, sh) => {
  darkBg(c);
  const tNo = kw('b14', '节拍器'), tEdge = kw('b14', '高低变化'), tSelf = kw('b14', '推算'), tMix = kw('b15', '打乱'), tMany = kw('b15', '变化够多'), tCount = kw('b16', '一个一个'), tName = kw('b17', 'CDR'), tAll = L.b18.t0;
  const recap = ease(t, tAll - 0.2, tAll + 0.5, 'c');
  // 上半：发货端的节拍器被划掉
  if (t < tMix - 1.6) { metronome(c, 260, 470, 120, t); txt(c, '节拍器', 260, 620, { size: 40, fam: 'PuHui-Heavy', col: COL.cream, align: 'center' });
    if (t > tNo) { const q = ease(t, tNo, tNo + 0.3); c.save(); c.strokeStyle = COL.redHi; c.lineWidth = 12; c.lineCap = 'round'; c.globalAlpha = q; c.beginPath(); c.moveTo(150, 360); c.lineTo(370, 600); c.moveTo(370, 360); c.lineTo(150, 600); c.stroke(); c.restore();
      tag(c, '不另外送', 660, 470, { size: 48, bg: COL.red, fg: '#f6efe4', t, at: tNo }); } }
  // 中间：一段一直在往左流的信号；跳变处闪一下；下面一排节拍刻度先是乱的，慢慢对齐跳变（锁定）
  const BITS = []; { const r = R(5); for (let i = 0; i < 400; i++) BITS.push(r() < 0.5 ? 1 : 0); }
  const RUN = [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1];   // 打乱之前：一长串 1
  const bw = 96, yHi = 820, yLo = 1000, speed = 150, off = (t - sh.t0) * speed;
  const i0 = Math.floor(off / bw), fx = -(off % bw);
  const mixed = t > tMix, showRun = t > tMix - 0.2 && t < tMix + 0.6;
  const bitAt = i => (mixed || t < tMix - 1.5) ? BITS[(i + 1000) % 400] : RUN[(i - i0 + 20) % RUN.length];
  const seq = []; for (let k = -1; k < 13; k++) seq.push(bitAt(i0 + k));
  const yOff = recap * 380;
  c.save(); c.translate(0, -yOff * 0.0); c.globalAlpha = 1 - recap;
  wave(c, seq, fx - bw, bw, yHi, yLo, { col: COL.goldHi, lw: 9 });
  // 跳变闪光
  if (t > tEdge - 0.2) for (let k = 0; k < seq.length - 1; k++) if (seq[k] !== seq[k + 1]) { const x = fx + k * bw; const fl = 0.5 + 0.5 * Math.sin(t * 8 + k); c.save(); c.globalAlpha *= ease(t, tEdge - 0.2, tEdge + 0.3) * (0.4 + 0.6 * fl); c.fillStyle = COL.mint; c.shadowColor = COL.mint; c.shadowBlur = 24; c.beginPath(); c.arc(x, (yHi + yLo) / 2, 14, 0, 7); c.fill(); c.restore(); }
  // 节拍刻度：推算出来以前相位乱跑，推算出来以后对齐每一位的中间
  if (t > tEdge) { const lock = ease(t, tSelf - 0.3, tSelf + 1.2, 'c'), drift = (1 - lock) * (40 * Math.sin(t * 3.1) + 25 * Math.sin(t * 5.3)), per = bw * (1 + (1 - lock) * 0.18 * Math.sin(t * 1.7));
    for (let k = -1; k < 14; k++) { const x = fx + (k + 0.5) * per + drift; if (x < 40 || x > W - 40) continue; c.save(); c.strokeStyle = lock > 0.9 ? COL.mint : COL.creamDim; c.lineWidth = 5; c.beginPath(); c.moveTo(x, yLo + 70); c.lineTo(x, yLo + 130); c.stroke(); c.restore(); }
    txt(c, lock > 0.9 ? '收货端自己推算出的节拍' : '收货端：节拍还没对准', W / 2, yLo + 190, { size: 40, fam: 'PuHui-Heavy', col: lock > 0.9 ? COL.mint : COL.creamDim, align: 'center' }); }
  // 打乱：一长串 1（没有跳变，节拍会丢）→ 打乱以后跳变很多
  if (t > tMix - 1.5 && t < tCount) { const q = ease(t, tMix - 1.5, tMix - 1.1); tag(c, t < tMix ? '一长串 1：没有跳变，节拍会跑丢' : '先打乱：高低变化够多', W / 2, 560, { size: 46, bg: t < tMix ? COL.coral : COL.cream, fg: COL.ink, t, at: t < tMix ? tMix - 1.5 : tMix }); }
  // 按节拍清点：每个刻度落下，计数加一
  if (t > tCount - 0.2) { const n = Math.min(99, Math.floor((t - tCount) * 3.5) + 1); c.save(); c.fillStyle = 'rgba(15,15,14,.9)'; c.beginPath(); c.roundRect(W / 2 - 200, 470, 400, 170, 20); c.fill(); c.restore();
    txt(c, `清点：${n}`, W / 2, 560, { size: 72, fam: 'PuHui-Heavy', col: COL.mint, align: 'center' }); }
  c.restore();
  if (t > tName - 0.6 && recap < 1) tape(c, '时钟数据恢复 CDR', W / 2, 360, { size: 62, t, at: tName - 0.6 });
  // 收尾：整个框架回放一遍——排成一列 → 路上 → 听准节拍 → 拆回一排
  if (recap > 0) { c.save(); c.globalAlpha = recap; const tA = kw('b18', '排成一列'), tB = kw('b18', '听准节拍'), tC = kw('b18', '拆回一排');
    for (let j = 0; j < 6; j++) box(c, 270 + j * 108, 520, [1, 0, 1, 1, 0, 1][j], { s: 80, alpha: 1 - 0.6 * ease(t, tA, tA + 0.6) });
    for (let n = 0; n < 12; n++) { const y = 620 + ((t - tAll) * 400 + n * 70) % 460; box(c, W / 2, y, null, { s: 40, col: COL.goldHi, alpha: seg(y, 610, 660) * (1 - seg(y, 1030, 1080)) }); }
    MD.label(c, '发出去：排成一列', 70, 400, { size: 44, bg: COL.red, fg: '#f6efe4', t, at: tA - 0.1 });
    if (t > tB - 0.2) { for (let k = 0; k < 7; k++) { const x = 300 + k * 80; c.strokeStyle = COL.mint; c.lineWidth = 5; c.beginPath(); c.moveTo(x, 1110); c.lineTo(x, 1160); c.stroke(); } MD.label(c, '收进来：听准节拍', 70, 1220, { size: 44, bg: COL.mint, fg: COL.ink, t, at: tB - 0.1 }); }
    if (t > tC - 0.2) { for (let j = 0; j < 6; j++) box(c, 270 + j * 108, 1340, [1, 0, 1, 1, 0, 1][j], { s: 80, alpha: ease(t, tC - 0.2 + j * 0.06, tC + 0.1 + j * 0.06) }); MD.label(c, '拆回一排', 70, 1440, { size: 44, bg: COL.cream, fg: COL.ink, t, at: tC - 0.1 }); }
    c.restore(); }
};

SP.MECH.take = (c, t, sh) => { deskShot(c, t, sh); endCard(c, t, L.b21); };
})();
