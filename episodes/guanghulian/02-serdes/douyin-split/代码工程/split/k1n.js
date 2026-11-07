// 第 1 条 · 纯动画版 v2：两种送法从头到尾摆在一起比。
// 上：几十条路一起送（照片切成 12 条，各走一条）；下：排成一队送（像素一个接一个）。
// 慢：两边都行 → 一快：上面一条晚到半步、拼进下一张 ✗，下面一个不乱 ✓ → 路越多越难一样长 → 所以只修几条路。
// 时间点全部来自 D.cue（tools/build_nv2.py：按秒设计，吸附到这首曲子的拍点上）。
(() => {
const { clamp, lerp } = U; const { W, H, COL, T, txt, tag, tape, pop, ease, seg, L } = SP;
SP.END = 'z2';
const C = SP.D.cue, R = s => U.rng(s);
const GOLD = [245, 215, 126];
const glowDot = (c, x, y, r, col = GOLD, a = 1) => { c.save(); c.globalCompositeOperation = 'lighter'; const g = c.createRadialGradient(x, y, 0, x, y, r * 3); g.addColorStop(0, `rgba(255,250,235,${a})`); g.addColorStop(0.3, `rgba(${col},${0.85 * a})`); g.addColorStop(1, `rgba(${col},0)`); c.fillStyle = g; c.beginPath(); c.arc(x, y, r * 3, 0, 7); c.fill(); c.restore(); };
const photo = (g, x, y, w, h, v = 0) => { const sky = g.createLinearGradient(0, y, 0, y + h);
  if (v) { sky.addColorStop(0, '#7fc8f0'); sky.addColorStop(1, '#2f6f9a'); } else { sky.addColorStop(0, '#f2c27a'); sky.addColorStop(0.55, '#e98a5c'); sky.addColorStop(1, '#5c3a52'); }
  g.fillStyle = sky; g.fillRect(x, y, w, h); g.fillStyle = v ? '#ffffff' : '#fff2c9'; g.beginPath(); g.arc(x + w * 0.62, y + h * 0.36, w * 0.11, 0, 7); g.fill();
  g.fillStyle = v ? '#2e5b3a' : '#3b2a3c'; g.beginPath(); g.moveTo(x, y + h * 0.66); for (let n = 0; n <= 12; n++) g.lineTo(x + w * n / 12, y + h * (0.58 + 0.08 * Math.sin(n * 1.7 + 1))); g.lineTo(x + w, y + h); g.lineTo(x, y + h); g.fill();
  g.fillStyle = v ? '#1f4029' : '#241a27'; g.fillRect(x, y + h * 0.82, w, h * 0.18); };
const NS = 12;
const stripCol = (i, v) => v ? ['#7fc8f0', '#76bfe7', '#6db5dd', '#64abd3', '#5ba1c9', '#5297bf', '#4a8db5', '#3f7e9f', '#2e5b3a', '#2a5536', '#1f4029', '#1f4029'][i] : ['#f2c27a', '#f0b672', '#eea96a', '#ec9c62', '#ea905b', '#e2865b', '#c06f58', '#9c5a56', '#3b2a3c', '#352638', '#241a27', '#241a27'][i];
const assembled = (c, x, y, w, h, rows, { bad = -1, frame = true, shift = 26 } = {}) => { if (frame) { c.save(); c.shadowColor = 'rgba(0,0,0,.6)'; c.shadowBlur = 24; c.fillStyle = '#f6f2ea'; c.fillRect(x - 10, y - 10, w + 20, h + 20); c.restore(); }
  c.fillStyle = '#1b1a18'; c.fillRect(x, y, w, h);
  rows.forEach((v, i) => { if (v == null) return; const sy = y + h * i / NS, sh = h / NS + 0.5; c.save(); c.beginPath(); c.rect(x, sy, w, sh); c.clip(); photo(c, x + (i === bad ? shift : 0), y, w, h, v); c.restore(); }); };
const chatBg = (g, x, y, w, h) => { g.fillStyle = '#ededed'; g.fillRect(x, y, w, h); g.fillStyle = '#f7f7f7'; g.fillRect(x, y, w, 90); txt(g, '小林', x + w / 2, y + 58, { size: 30, fam: 'PuHui-Heavy', col: '#222', align: 'center' }); };
const mark = (c, ok, x, y, s = 70) => txt(c, ok ? '✓' : '✗', x, y, { size: s, fam: 'PuHui-Heavy', col: ok ? COL.mint : COL.coral, align: 'center' });

// ---------- 1. 第一帧：两部手机收到同一张照片，一张错位、一张完好 ----------
SP.MECH.hook = (c, t, sh) => {
  const k = T.cam({ hy: 1500, camH: 300 }); T.bg(c, k, { grid: 0.5, scroll: t * 200 }); T.streams(c, t, { a: 0.14 });
  const bad = Array(NS).fill(0); bad[6] = 1;
  [[290, bad, 6, '几十条路一起送', false], [790, Array(NS).fill(0), -1, '排成一队送', true]].forEach(([x, rows, b, lab, ok], j) => {
    c.save(); c.translate(x, 900 + 10 * Math.sin(t * 2 + j * 1.6)); c.rotate((j ? 1 : -1) * 0.02 + 0.01 * Math.sin(t * 1.3 + j));
    SP.phone(c, 0, 0, 440, 780, (g, X, Y, w, h) => { chatBg(g, X, Y, w, h); const px = X + 40, py = Y + 140, pw = w - 80, ph = pw * 1.25; assembled(g, px, py, pw, ph, rows, { bad: b, frame: false, shift: 34 });
      if (b >= 0) { const q = ease(t, 0.25, 0.55, 'o'); g.save(); g.strokeStyle = COL.redHi; g.lineWidth = 6; g.beginPath(); g.ellipse(px + pw / 2 + 10, py + ph * (b + 0.5) / NS, (pw / 2 + 30) * (0.6 + 0.4 * q), 34, 0, 0, 7 * q); g.stroke(); g.restore(); } });
    c.restore();
    tag(c, lab, x, 1360, { size: 46, bg: ok ? COL.mint : COL.coral, fg: COL.ink }); mark(c, ok, x, 1460, 84); });
};

// ---------- 2. 两条流水线：上 12 条路并排，下 1 条路排成一队；两边一样的照片、一样的节奏 ----------
const TOP = { y0: 430, y1: 760, x0: 140, xR: 790, recv: [810, 445, 230, 290] }, BOT = { y: 1180, x0: 140, xR: 790, recv: [810, 1035, 230, 290] };
const period = (s) => s < C.fast ? 1.5 : s < C.faster ? 0.62 : 0.36;            // 一张照片接一张照片的间隔（「一快」那一拍立刻变密）
const heatsOf = (from, to) => { const a = []; let s = from; while (s < to) { a.push(s); s += period(s); } return a; };
// 子弹时间：「晚到半步」那几拍，画面里的时间放慢
const warp = (t) => { const a = C.late, b = C.lateEnd, S = 0.15; return t < a ? t : t < b ? a + (t - a) * S : a + (b - a) * S + (t - b); };
SP.MECH.pipes = (c, t, sh) => {
  const te = warp(t), bt = t > C.late && t < C.lateEnd ? Math.min(seg(t, C.late, C.late + 0.25), 1 - seg(t, C.lateEnd - 0.25, C.lateEnd)) : 0;
  const k = T.cam({ hy: 1500, camH: 300 }); T.bg(c, k, { grid: 0.4, scroll: te * 300 }); T.streams(c, te, { a: 0.1 });
  const appear = ease(t, sh.t0, sh.t0 + 0.6, 'o'), bend = ease(t, C.bend - 0.3, C.bend + 0.4), allBend = ease(t, C.faster - 0.2, C.faster + 0.6);
  const ly = i => lerp(TOP.y0, TOP.y1, i / (NS - 1));
  const late = i => (i === 6 ? 0.42 * bend : 0) + (i !== 6 && allBend > 0 && R(i * 13 + 5)() > 0.6 ? 0.3 * allBend : 0);
  const hump = (i, x) => { const amp = (i === 6 ? 34 * bend : 0) + (i !== 6 && late(i) > 0 ? 22 * allBend : 0), a = 380 + (i % 3) * 40; return x > a && x < a + 160 ? -amp * Math.sin(Math.PI * (x - a) / 160) : 0; };
  // 面板外框和标题
  c.save(); c.globalAlpha = appear; c.fillStyle = 'rgba(8,10,11,.55)'; c.beginPath(); c.roundRect(40, 330, 1000, 500, 24); c.fill(); c.beginPath(); c.roundRect(40, 900, 1000, 500, 24); c.fill(); c.restore();
  tag(c, '几十条路一起送', 270, 330, { size: 42, bg: COL.cream, fg: COL.ink }); tag(c, '排成一队送', 230, 900, { size: 42, bg: COL.cream, fg: COL.ink });
  // 发件芯片（左）
  for (const [y0, h] of [[TOP.y0 - 30, TOP.y1 - TOP.y0 + 60], [BOT.y - 90, 180]]) { c.fillStyle = '#2b2a27'; c.beginPath(); c.roundRect(60, y0, 70, h, 10); c.fill(); c.strokeStyle = 'rgba(245,215,126,.6)'; c.lineWidth = 3; c.stroke(); }
  // 上：12 条路
  for (let i = 0; i < NS; i++) { c.save(); c.strokeStyle = i === 6 && bend > 0.1 ? `rgba(239,125,98,${0.6 + 0.4 * bt})` : 'rgba(226,181,74,.45)'; c.lineWidth = 3; c.beginPath(); for (let x = TOP.x0; x <= TOP.xR; x += 8) { const y = ly(i) + hump(i, x); x === TOP.x0 ? c.moveTo(x, y) : c.lineTo(x, y); } c.stroke(); c.restore(); }
  const VX = 720, tops = heatsOf(sh.t0 + 0.4, sh.t1 + 3);
  tops.forEach((a, h) => { for (let i = 0; i < NS; i++) { const x = TOP.xR - (a + late(i) - te) * VX; if (x < TOP.x0 || x > TOP.xR + 4) continue; const y = ly(i) + hump(i, x), lateNow = late(i) > period(a) / 2;
    c.save(); c.fillStyle = stripCol(i, h % 2); c.shadowColor = lateNow ? COL.coral : 'rgba(245,215,126,.7)'; c.shadowBlur = lateNow ? 22 : 10; c.fillRect(x - 28, y - 10, 56, 20); c.restore(); } });
  let cur = -1; tops.forEach((a, h) => { if (te >= a) cur = h; });
  const rowsTop = Array(NS).fill(null); let badRow = -1;
  if (cur >= 0) for (let i = 0; i < NS; i++) { if (late(i) > period(tops[cur]) / 2) { rowsTop[i] = cur > 0 ? (cur - 1) % 2 : null; if (cur > 0 && (cur - 1) % 2 !== cur % 2) badRow = i; } else rowsTop[i] = te >= tops[cur] + late(i) ? cur % 2 : (cur > 0 ? (cur - 1) % 2 : null); }
  // 下：一条路，像素一个接一个；对面一行一行拼出来（同一张照片，同样的间隔）
  c.save(); c.strokeStyle = 'rgba(226,181,74,.8)'; c.lineWidth = 6; c.shadowColor = COL.gold; c.shadowBlur = 12; c.beginPath(); c.moveTo(BOT.x0, BOT.y); c.lineTo(BOT.xR, BOT.y); c.stroke(); c.restore();
  const bots = heatsOf(sh.t0 + 0.4, sh.t1 + 3);
  bots.forEach((a, h) => { const P = period(a); for (let r = 0; r < NS; r++) for (let q = 0; q < 3; q++) { const ta = a + (r * 3 + q) / (NS * 3) * P * 0.95, x = BOT.xR - (ta - te) * VX * 1.6; if (x < BOT.x0 || x > BOT.xR) continue;
    c.fillStyle = stripCol(r, h % 2); c.fillRect(x - 7, BOT.y - 7, 14, 14); } });
  let bcur = -1; bots.forEach((a, h) => { if (te >= a) bcur = h; });
  const rowsBot = Array(NS).fill(null); if (bcur >= 0) { const a = bots[bcur], P = period(a); for (let r = 0; r < NS; r++) rowsBot[r] = te >= a + (r * 3 + 2) / (NS * 3) * P * 0.95 ? bcur % 2 : (bcur > 0 ? (bcur - 1) % 2 : null); }
  // 接收的相框
  const zoom = ease(t, C.compare - 0.2, C.compare + 0.5, 'c') * (1 - ease(t, C.faster - 0.5, C.faster));
  const RT = TOP.recv.map((v, j) => lerp(v, [70, 600, 440, 560][j], zoom)), RB = BOT.recv.map((v, j) => lerp(v, [570, 600, 440, 560][j], zoom));
  if (zoom > 0) { c.save(); c.fillStyle = `rgba(4,5,6,${0.8 * zoom})`; c.fillRect(0, 0, W, H); c.restore(); }
  assembled(c, ...RT, rowsTop, { bad: badRow, shift: 22 + 20 * zoom }); assembled(c, ...RB, rowsBot);
  const okTop = badRow < 0 && rowsTop.every(v => v != null), okBot = rowsBot.every(v => v != null);
  if (t > sh.t0 + 1.4) { mark(c, okTop, RT[0] + RT[2] / 2, RT[1] + RT[3] + 70, 64 + 30 * zoom); mark(c, okBot, RB[0] + RB[2] / 2, RB[1] + RB[3] + 70, 64 + 30 * zoom); }
  if (zoom > 0.5) { c.save(); c.strokeStyle = COL.redHi; c.lineWidth = 6; if (badRow >= 0) c.strokeRect(RT[0] - 14, RT[1] + RT[3] * badRow / NS - 8, RT[2] + 50, RT[3] / NS + 16); c.restore();
    tag(c, '几十条路一起送', RT[0] + RT[2] / 2, RT[1] - 60, { size: 40, bg: COL.coral, fg: COL.ink }); tag(c, '排成一队送', RB[0] + RB[2] / 2, RB[1] - 60, { size: 40, bg: COL.mint, fg: COL.ink }); }
  // 标注：贴在发生事情的地方
  if (t > C.bend - 0.2 && t < C.compare - 0.2) { const x = 380 + (6 % 3) * 40 + 80; c.save(); c.strokeStyle = COL.redHi; c.lineWidth = 5; c.beginPath(); c.ellipse(x, ly(6) - 20, 110, 46, 0, 0, 7 * ease(t, C.bend - 0.2, C.bend + 0.3)); c.stroke(); c.restore();
    tag(c, t > C.late - 0.1 ? '晚到半步，拼进下一张' : '这条长了一点点', x, ly(6) - 110, { size: 44, bg: COL.coral, fg: COL.ink, t, at: t > C.late - 0.1 ? C.late - 0.1 : C.bend - 0.2 }); }
  if (t > C.fast - 0.05 && t < C.fast + 1.6) { c.save(); c.globalCompositeOperation = 'lighter'; const q = 1 - seg(t, C.fast, C.fast + 1.6); for (let n = 0; n < 40; n++) { const r = R(n + Math.floor(t * 20) * 7), y = 360 + r() * 1040, x0 = r() * W; c.strokeStyle = `rgba(245,215,126,${0.35 * q})`; c.lineWidth = 2; c.beginPath(); c.moveTo(x0, y); c.lineTo(x0 + 120 + r() * 200, y); c.stroke(); } c.restore(); }
  if (bt > 0) { c.save(); const vg = c.createRadialGradient(W / 2, 600, 200, W / 2, 900, 1200); vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, `rgba(20,0,0,${0.55 * bt})`); c.fillStyle = vg; c.fillRect(0, 0, W, H); c.restore(); }
  if (t > C.faster + 0.4 && zoom < 0.1) { c.save(); c.globalCompositeOperation = 'lighter'; for (let n = 0; n < 24; n++) { const r = R(n + Math.floor(t * 24) * 5), x0 = BOT.x0 + r() * 600; c.strokeStyle = 'rgba(245,215,126,.4)'; c.lineWidth = 3; c.beginPath(); c.moveTo(x0, BOT.y - 30 + r() * 60); c.lineTo(x0 + 140, BOT.y - 30 + r() * 60); c.stroke(); } c.restore(); }
};
})();
