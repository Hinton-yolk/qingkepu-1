// 光互连 02 · 抖音版（小红书纸桌讲解风格）新增的卡片：并口线 vs USB（上集实物开场 + 回扣）、聊天消息少一位变乱码（下集实物开场 + 回扣）、跟着歌拍手、打乱再还原。
// 坐标原点在卡片中心；时间点来自 desk_u.json / desk_d.json 的 cue。纯时间函数，随机数用种子。
(() => {
const { clamp, lerp } = U; const { COL, txt, seg, S12 } = FULL;
const { bitOf, level, stroke, digit, rbox, bitTile } = FULL.H;
const INK = '#1b1b1a', GOLD = '#f5d77e';
const cross = (c, x, y, s = 18, col = COL.redHi) => { c.save(); c.strokeStyle = col; c.lineWidth = 6; c.lineCap = 'round'; c.beginPath(); c.moveTo(x - s, y - s); c.lineTo(x + s, y + s); c.moveTo(x + s, y - s); c.lineTo(x - s, y + s); c.stroke(); c.restore(); };
const tick = (c, x, y, s = 18, col = COL.cream) => { c.save(); c.strokeStyle = col; c.lineWidth = 6; c.lineCap = 'round'; c.lineJoin = 'round'; c.beginPath(); c.moveTo(x - s, y); c.lineTo(x - s * 0.3, y + s * 0.7); c.lineTo(x + s, y - s * 0.8); c.stroke(); c.restore(); };

// ---------- 并口线（25 根线）vs USB（4 根线）：同样传照片，USB 一张接一张，并口线还在爬（速度比例示意） ----------
// Q.t0 开跑；Q.recall（回扣）：USB 线里的数据显出「排成一列」的 0 和 1
FULL.CARD.wires = (c, t, id, cd, Q) => {
  const T = Math.max(0, t - Q.t0), X0 = -250, X1 = 470, rec = Q.recall != null ? MO.smooth(seg(t, Q.recall, Q.recall + 0.5)) : 0;
  // —— 并口线 ——
  const YA = -250;
  c.save(); c.shadowColor = 'rgba(40,30,15,.35)'; c.shadowBlur = 16; c.shadowOffsetY = 8; c.fillStyle = '#b9b4a8'; c.beginPath(); c.roundRect(X0 - 10, YA - 30, X1 - X0 + 10, 60, 14); c.fill(); c.restore();
  c.strokeStyle = 'rgba(80,74,64,.25)'; c.lineWidth = 2; for (let k = 0; k < 9; k++) { c.beginPath(); c.moveTo(X0, YA - 24 + k * 6); c.lineTo(X1, YA - 24 + k * 6); c.stroke(); }
  // DB-25 插头
  c.save(); c.shadowColor = 'rgba(40,30,15,.4)'; c.shadowBlur = 18; c.shadowOffsetY = 8; const g = c.createLinearGradient(0, YA - 70, 0, YA + 70); g.addColorStop(0, '#dcd9d1'); g.addColorStop(1, '#9d9a92'); c.fillStyle = g;
  c.beginPath(); c.roundRect(-480, YA - 75, 230, 150, 12); c.fill(); c.restore();
  c.fillStyle = '#2a2a28'; c.beginPath(); c.moveTo(-462, YA - 44); c.lineTo(-268, YA - 44); c.lineTo(-282, YA + 44); c.lineTo(-448, YA + 44); c.closePath(); c.fill();
  c.fillStyle = '#d7b257'; for (let k = 0; k < 13; k++) { c.beginPath(); c.arc(-445 + k * 13.5, YA - 18, 4.2, 0, 7); c.fill(); } for (let k = 0; k < 12; k++) { c.beginPath(); c.arc(-438 + k * 13.5, YA + 18, 4.2, 0, 7); c.fill(); }
  txt(c, '打印机并口线 · 25 根线', -480, YA - 115, { size: 40, fam: 'PuHui-Heavy', col: INK });
  // 数据：并排一列列地慢慢挪（8 条代表很多条）
  for (let k = 0; k < 12; k++) { const x = X0 + ((T * 42 + k * 64) % (X1 - X0)); for (let j = 0; j < 8; j++) { c.fillStyle = 'rgba(60,54,46,.75)'; c.fillRect(x, YA - 23 + j * 6, 18, 4); } }
  // —— USB ——
  const YB = 150;
  c.save(); c.shadowColor = 'rgba(40,30,15,.35)'; c.shadowBlur = 14; c.shadowOffsetY = 6; c.fillStyle = '#222220'; c.beginPath(); c.roundRect(X0 - 10, YB - 13, X1 - X0 + 10, 26, 13); c.fill(); c.restore();
  c.save(); c.shadowColor = 'rgba(40,30,15,.4)'; c.shadowBlur = 16; c.shadowOffsetY = 8; c.fillStyle = '#2b2b29'; c.beginPath(); c.roundRect(-330, YB - 45, 90, 90, 14); c.fill(); c.restore();
  const g2 = c.createLinearGradient(0, YB - 40, 0, YB + 40); g2.addColorStop(0, '#e6e4de'); g2.addColorStop(1, '#a7a49c'); c.fillStyle = g2; c.beginPath(); c.roundRect(-480, YB - 40, 160, 80, 6); c.fill();
  c.fillStyle = '#2a2a28'; c.fillRect(-466, YB - 26, 130, 30); c.fillStyle = '#d7b257'; for (let k = 0; k < 4; k++) c.fillRect(-455 + k * 30, YB - 22, 18, 14);
  txt(c, 'USB · 4 根线', -480, YB - 85, { size: 40, fam: 'PuHui-Heavy', col: INK });
  // 数据：排成一列飞快地跑；回扣时显出 0 和 1
  for (let k = 0; k < 60; k++) { const x = X0 + ((T * 700 + k * 24) % (X1 - X0)); const b = bitOf(k);
    if (rec > 0.5) { txt(c, String(b), x + 6, YB - 42, { size: 30, fam: 'PuHui-Heavy', col: COL.red, align: 'center' }); }
    c.fillStyle = `rgba(245,215,126,${0.9})`; c.fillRect(x, YB - 4, 14, 8); }
  if (rec > 0) { c.save(); c.globalAlpha = rec; c.strokeStyle = COL.red; c.lineWidth = 7; c.beginPath(); c.ellipse(110, YB - 18, 400, 82, 0, 0, Math.PI * 2 * rec); c.stroke(); c.restore(); }
  // —— 传照片的进度：USB 一秒一张，并口线大约二十秒一张（比例示意） ——
  const bar = (y, q, n, col) => { c.save(); c.strokeStyle = 'rgba(27,27,26,.45)'; c.lineWidth = 3; c.beginPath(); c.roundRect(-480, y - 22, 760, 44, 10); c.stroke();
    c.fillStyle = col; c.beginPath(); c.roundRect(-476, y - 18, 752 * clamp(q), 36, 8); c.fill(); c.restore();
    txt(c, `已传 ${n} 张`, 300, y + 2, { size: 36, fam: 'PuHui-Heavy', col: INK }); };
  bar(YA + 125, (T / 20) % 1, Math.floor(T / 20), '#8a8780'); bar(YB + 105, T % 1, Math.floor(T), COL.red);
  // 照片小图标：USB 每传完一张，弹出一张
  const nB = Math.floor(T); for (let k = 0; k < Math.min(6, nB); k++) { const age = T - (nB - k), s = k === Math.min(6, nB) - 1 ? MO.backOut(clamp(age / 0.25), 1.6) : 1, x = -440 + k * 70, y = YB + 200;
    c.save(); c.translate(x, y); c.scale(s, s); c.rotate(-0.06 + 0.04 * k); c.fillStyle = '#f6efe4'; c.fillRect(-28, -22, 56, 44); const sk = c.createLinearGradient(0, -18, 0, 18); sk.addColorStop(0, '#f2c27a'); sk.addColorStop(1, '#5c3a52'); c.fillStyle = sk; c.fillRect(-24, -18, 48, 36); c.restore(); }
};

// ---------- 聊天消息：少数一个比特，后面全错位，整句变乱码；回扣时一格格还原 ----------
// Q.drop：线上那一串比特里少了一位，后面整体往前挪一格；Q.fix：这一位回来，消息一格格还原
const MSG = '今晚七点，老地方见', BAD = '浠婃櫄涓冪偣锛岃€佸';
FULL.CARD.chat = (c, t, id, cd, Q) => {
  const PW = 640, PH = 800, drop = Q.drop != null ? MO.cubicInOut(seg(t, Q.drop, Q.drop + 0.5)) : 0, fix = Q.fix != null ? MO.cubicInOut(seg(t, Q.fix, Q.fix + 0.5)) : 0, gone = drop * (1 - fix);
  c.save(); c.shadowColor = 'rgba(40,30,15,.4)'; c.shadowBlur = 30; c.shadowOffsetY = 14; c.fillStyle = '#151514'; c.beginPath(); c.roundRect(-PW / 2, -PH / 2, PW, PH, 60); c.fill(); c.restore();
  c.fillStyle = '#ece7dd'; c.beginPath(); c.roundRect(-PW / 2 + 18, -PH / 2 + 26, PW - 36, PH - 52, 42); c.fill();
  c.fillStyle = '#151514'; c.beginPath(); c.roundRect(-50, -PH / 2 + 34, 100, 22, 11); c.fill();
  c.fillStyle = '#ddd6c8'; c.fillRect(-PW / 2 + 18, -PH / 2 + 80, PW - 36, 70); txt(c, '小林', 0, -PH / 2 + 116, { size: 34, fam: 'PuHui-Heavy', col: INK, align: 'center' });
  // 发出去的（右边，绿色）
  const bub = (x, y, s, col, right, fg = INK) => { c.font = '40px "PuHui-Heavy"'; const w = c.measureText(s).width + 50, x0 = right ? x - w : x;
    c.fillStyle = col; c.beginPath(); c.roundRect(x0, y - 38, w, 76, 16); c.fill(); txt(c, s, x0 + 25, y + 2, { size: 40, fam: 'PuHui-Heavy', col: fg }); return w; };
  txt(c, '你发出的', PW / 2 - 50, -205, { size: 26, fam: 'PuHui-Heavy', col: 'rgba(27,27,26,.45)', align: 'right' });
  bub(PW / 2 - 50, -150, MSG, '#9fe07a', true);
  // 对方收到的（左边，白色）：从第 3 个字开始乱掉；还原时一格格变回来
  const nBad = Q.drop != null && t >= Q.drop ? Math.floor(clamp((t - Q.drop - 0.25) / 0.5) * (MSG.length - 2)) : 0;
  const nFix = Q.fix != null && t >= Q.fix ? Math.floor(clamp((t - Q.fix - 0.3) / 0.9) * (MSG.length + 1)) : 0;
  let s = ''; for (let i = 0; i < MSG.length; i++) { const bad = i >= 2 && i - 2 < nBad && i >= nFix; s += bad ? BAD[i] : MSG[i]; }
  txt(c, '对方收到的', -PW / 2 + 50, -60, { size: 26, fam: 'PuHui-Heavy', col: 'rgba(27,27,26,.45)' });
  const shake = nBad > 0 && nFix === 0 ? Math.sin(t * 40) * 3 * clamp(1 - (t - Q.drop - 0.75) / 0.5) : 0;
  c.save(); c.translate(shake, 0); bub(-PW / 2 + 50, 0, s, '#fbf8f2', false, nBad > 0 && nFix < MSG.length ? '#b8433f' : INK); c.restore();
  if (nFix >= MSG.length + 1) tick(c, PW / 2 - 70, 0, 20, '#3f9a6a'); else if (nBad > 0) cross(c, PW / 2 - 70, 0, 18, '#b8433f');
  // 线上的比特：少了一位（红框空了），后面整体往前挪一格
  const NB = 12, sz = 40, gap = 5, X0 = -((NB * (sz + gap)) / 2) + sz / 2, Y = 190, MISS = 4;
  txt(c, '线上的比特', 0, Y - 80, { size: 28, fam: 'PuHui-Heavy', col: 'rgba(27,27,26,.55)', align: 'center' });
  c.save(); c.fillStyle = '#26292c'; c.beginPath(); c.roundRect(-PW / 2 + 40, Y - 40, PW - 80, 80, 14); c.fill(); c.restore();
  for (let k = 0; k < NB; k++) { const b = bitOf(k + 3); let x = X0 + k * (sz + gap);
    if (k === MISS) { c.save(); c.globalAlpha = 1 - gone; bitTile(c, b, x, Y, { s: sz, col: COL.cream }); c.restore();
      const box = gone * (1 - clamp((t - (Q.drop ?? 0) - 1.2) / 0.5)); if (box > 0.05) { c.save(); c.globalAlpha = box; c.strokeStyle = COL.redHi; c.lineWidth = 4; c.setLineDash([6, 5]); c.strokeRect(x - sz / 2 - 2, Y - sz / 2 - 2, sz + 4, sz + 4); c.restore(); } continue; }
    if (k > MISS) x -= (sz + gap) * gone;
    bitTile(c, b, x, Y, { s: sz, col: k > MISS && gone > 0.5 ? COL.redHi : COL.cream }); }
  // 下面一道一直往前跑的光，表示比特在线上一直在流
  c.save(); c.globalCompositeOperation = 'lighter'; const u = (t * 0.8) % 1, gx = lerp(-PW / 2 + 60, PW / 2 - 60, u), gg = c.createRadialGradient(gx, Y + 52, 0, gx, Y + 52, 40); gg.addColorStop(0, 'rgba(245,215,126,.7)'); gg.addColorStop(1, 'rgba(0,0,0,0)'); c.fillStyle = gg; c.fillRect(gx - 40, Y + 30, 80, 44); c.restore();
};

// ---------- 跟着一首歌拍手：没人打拍子，听着鼓点就跟上了 ----------
FULL.CARD.clap = (c, t, id, cd, Q) => { if (t < Q.t0) return;
  const T = t - Q.t0, P = 0.5, X0 = -400, X1 = 400, Y = -120, PH = 0;      // 每 0.5 秒一个鼓点，鼓点从右往左流过播放头（x = 0）
  txt(c, '一首歌', X0, -300, { size: 34, fam: 'PuHui-Heavy', col: COL.creamDim });
  for (let x = X0; x <= X1; x += 12) { const tau = T + (x - PH) / 400, beat = Math.abs(tau / P - Math.round(tau / P)) < 0.05, a = beat ? 150 : 20 + 45 * Math.abs(Math.sin(tau * 23.7) * Math.sin(tau * 7.3));
    c.fillStyle = beat ? COL.redHi : 'rgba(236,230,218,.45)'; c.fillRect(x - 4, Y - a / 2, 8, a); }
  c.save(); c.strokeStyle = COL.cream; c.lineWidth = 4; c.beginPath(); c.moveTo(PH, Y - 110); c.lineTo(PH, Y + 110); c.stroke(); c.restore();
  // 手：在每个鼓点合上
  const ph = ((T % P) + P) % P / P, close = ph < 0.12 ? 1 - ph / 0.12 : clamp((ph - 0.75) / 0.25), gap = 14 + 90 * (1 - close), HY = 180;
  const palm = (sx) => { c.save(); c.translate(sx * gap, HY); c.rotate(sx * 0.18); c.fillStyle = '#e8c9a8'; c.beginPath(); c.roundRect(-38, -80, 76, 160, 34); c.fill(); c.restore(); };
  palm(-1); palm(1);
  if (ph < 0.15) { const k = 1 - ph / 0.15; c.save(); c.globalAlpha = k; txt(c, '啪', 150, HY - 30, { size: 64, fam: 'PuHui-Black', col: COL.redHi, align: 'center' }); c.restore(); }
  // 节拍器：没有，被划掉
  rbox(c, -320, HY, 120, 150, { r: 14 }); txt(c, '节拍器', -320, HY - 105, { size: 28, fam: 'PuHui-Heavy', col: COL.creamDim, align: 'center' });
  c.save(); c.strokeStyle = COL.cream; c.lineWidth = 5; c.beginPath(); c.moveTo(-320, HY + 50); c.lineTo(-320 + 40 * Math.sin(T * 3), HY - 50); c.stroke(); c.restore(); cross(c, -320, HY, 60);
};

// ---------- 一长串全是 1：没有跳变，拍子慢慢跑偏；先打乱、让跳变一直在，收到再还原 ----------
// Q.flat 开始画长串 1；Q.mix 打乱后的信号；Q.back 还原
FULL.CARD.scramble = (c, t, id, cd, Q) => {
  const X0 = -400, X1 = 400, N = 16, bw = (X1 - X0) / N, xb = i => X0 + i * bw;
  // 第一行：0 后面一长串 1
  const YA = -330, HI = YA - 60, LO = YA + 30;
  txt(c, '原来的数据', X0, YA - 140, { size: 30, fam: 'PuHui-Heavy', col: COL.creamDim });
  const qa = MO.cubicInOut(seg(t, Q.flat, Q.flat + 0.8));
  stroke(c, X0, lerp(X0, X1, qa), x => (x < xb(1) ? LO : HI), { lw: 6, step: 1 });
  if (qa >= 1) { c.save(); c.globalCompositeOperation = 'lighter'; const gx = X0 + ((t - Q.flat) * 420) % (X1 - X0), gg = c.createRadialGradient(gx, HI, 0, gx, HI, 30); gg.addColorStop(0, 'rgba(245,215,126,.8)'); gg.addColorStop(1, 'rgba(0,0,0,0)'); c.fillStyle = gg; c.fillRect(gx - 30, HI - 30, 60, 60); c.restore(); }   // 数据一直在线上流
  // 本地的拍子：从唯一的跳变出发，越往后越偏（红）
  const drift = MO.smooth(seg(t, Q.flat + 0.4, Q.flat + 2.6));
  for (let i = 0; i < N; i++) { if (xb(i) > lerp(X0, X1, qa)) break; const off = drift * 0.055 * bw * Math.pow(Math.max(0, i - 1), 1.35), x = xb(i) + bw / 2 + off, bad = Math.abs(off) > bw * 0.45;
    c.save(); c.strokeStyle = 'rgba(236,230,218,.25)'; c.lineWidth = 2; c.setLineDash([6, 6]); c.beginPath(); c.moveTo(xb(i) + bw / 2, LO + 30); c.lineTo(xb(i) + bw / 2, LO + 60); c.stroke(); c.restore();
    c.save(); c.strokeStyle = bad ? COL.redHi : COL.cream; c.lineWidth = 5; c.beginPath(); c.moveTo(x, LO + 34); c.lineTo(x, LO + 62); c.stroke(); c.restore();
    if (x < X1 + 10) digit(c, bad ? '?' : (i ? '1' : '0'), x, LO + 95, bad ? COL.redHi : COL.cream, 32); }
  if (drift > 0.6) txt(c, '拍子跑偏', X1, YA - 140, { size: 32, fam: 'PuHui-Heavy', col: COL.redHi, align: 'right' });
  // 第二行：打乱以后，一直有跳变；每个跳变是一个鼓点，拍子踩得很准
  if (Q.mix != null && t >= Q.mix) { const YB = 60, H2 = YB - 60, L2 = YB + 30, SB = [0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1], qb = MO.cubicInOut(seg(t, Q.mix, Q.mix + 1.0)), xe = lerp(X0, X1, qb);
    txt(c, '打乱以后', X0, YB - 140, { size: 30, fam: 'PuHui-Heavy', col: COL.creamDim });
    stroke(c, X0, xe, x => (SB[Math.min(N - 1, Math.floor((x - X0) / bw))] ? H2 : L2), { lw: 6, step: 1 });
    for (let i = 1; i < N; i++) if (SB[i] !== SB[i - 1] && xb(i) < xe) { const age = (xe - xb(i)) / 300, f = clamp(1 - age); c.save(); c.globalCompositeOperation = 'lighter'; c.fillStyle = `rgba(245,215,126,${0.8 * f})`; c.beginPath(); c.arc(xb(i), (H2 + L2) / 2, 16 + 20 * (1 - f), 0, 7); c.fill(); c.restore(); }
    for (let i = 0; i < N; i++) { const x = xb(i) + bw / 2; if (x > xe) break; c.save(); c.strokeStyle = COL.tealHi; c.lineWidth = 5; c.beginPath(); c.moveTo(x, L2 + 34); c.lineTo(x, L2 + 62); c.stroke(); c.restore(); digit(c, String(SB[i]), x, L2 + 95, COL.cream, 32); }
    if (qb >= 1) tick(c, X1 - 10, YB - 140, 20, COL.tealHi); }
  // 第三行：收到以后按同样的规则还原
  if (Q.back != null && t >= Q.back) { const YC = 410, qc = MO.cubicInOut(seg(t, Q.back, Q.back + 0.8));
    txt(c, '收到以后：还原', X0, YC - 90, { size: 30, fam: 'PuHui-Heavy', col: COL.creamDim });
    for (let i = 0; i < N; i++) { if (i / N > qc) break; digit(c, i ? '1' : '0', xb(i) + bw / 2, YC, COL.cream, 40); }
    if (qc >= 1) tick(c, X1 - 10, YC - 90, 20, COL.tealHi); }
};
})();
