// 光互连 03 · 抖音第 1 条（无旁白 · 科技感）：线长一点，速度砍半？
// 结构借鉴小红书版：实物开场且第一帧就有演示（两根雷电线的出口一清一糊）→ 路线图 → 「静一拍」大字卡 → 演示 → … → 回到开头那两根线 → 一句话 + 你在这里。
// 时间点全部来自 D.cue（tools/build_g.py，吸附到 120 BPM 的拍点上）。纯时间函数，随机数全用种子。
(() => {
const { clamp, lerp } = U; const { W, H, COL, T, txt, tag, pop, ease, seg } = SP;
SP.END = null;
const C = SP.D.cue;
const GOLD = [245, 215, 126], CORAL = [239, 125, 98], TEAL = [155, 232, 219];
// ---------- 公用：比特波形 ----------
const BITS = [1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1];
const bitOf = k => (k < 0 ? 0 : BITS[((k % 30) + 30) % 30]);
const Phi = x => 1 / (1 + Math.exp(-1.702 * x));
const level = (x, F, bw, sg) => { let y = 0; const kLo = Math.max(0, Math.floor((F - x - 4 * sg) / bw) - 1), kHi = Math.ceil((F - x + 4 * sg) / bw) + 1;
  for (let k = kLo; k <= kHi; k++) if (bitOf(k)) y += Phi((F - k * bw - x) / sg) - Phi((F - (k + 1) * bw - x) / sg); return y; };
const g1 = (u, tau) => (u <= 0 ? 0 : 1 - Math.exp(-u / tau));
const resp = (x, k, bw, tau) => (g1(x - k * bw, tau) - g1(x - (k + 1) * bw, tau)) / (1 - Math.exp(-bw / tau)) * 0.92;
const wave = (c, x0, x1, fy, o = {}) => { const pts = []; for (let x = x0; x <= x1; x += 3) pts.push([x, fy(x)]); T.glowLine(c, pts, o); };
// 环境动态：一颗亮点沿着波形一直扫（像示波器的扫描点），画面在「看」的时候也不静止
const probe = (c, t, x0, x1, fy, sp = 0.55, ph = 0) => { const u = ((t * sp + ph) % 1 + 1) % 1, x = lerp(x0, x1, u), y = fy(x); c.save(); c.globalCompositeOperation = 'lighter'; const g = c.createRadialGradient(x, y, 0, x, y, 30); g.addColorStop(0, 'rgba(255,250,235,.95)'); g.addColorStop(0.35, 'rgba(155,232,219,.6)'); g.addColorStop(1, 'rgba(0,0,0,0)'); c.fillStyle = g; c.beginPath(); c.arc(x, y, 30, 0, 7); c.fill(); c.restore(); };
const panel = (c, x, y, w, h, a = 1) => { c.save(); c.globalAlpha *= a; c.fillStyle = 'rgba(8,11,12,.72)'; c.strokeStyle = 'rgba(155,232,219,.22)'; c.lineWidth = 2; c.beginPath(); c.roundRect(x, y, w, h, 22); c.fill(); c.stroke();
  c.strokeStyle = 'rgba(155,232,219,.06)'; for (let gx = x + 40; gx < x + w; gx += 40) { c.beginPath(); c.moveTo(gx, y + 8); c.lineTo(gx, y + h - 8); c.stroke(); } c.restore(); };
const ring = (c, x, y, rx, ry, q, col = COL.redHi) => { if (q <= 0) return; c.save(); c.strokeStyle = col; c.lineWidth = 7; c.shadowColor = col; c.shadowBlur = 16; c.beginPath(); c.ellipse(x, y, rx, ry, -0.04, -1.6, -1.6 + Math.PI * 2 * q); c.stroke(); c.restore(); };
const qmarks = (c, t, x, y, n = 3) => { for (let k = 0; k < n; k++) { c.save(); c.translate(x + k * 64, y); c.rotate(Math.sin(t * 9 + k * 2) * 0.15); txt(c, '?', 0, 0, { size: 54, fam: 'PuHui-Heavy', col: COL.redHi, align: 'center' }); c.restore(); } };
const mark = (c, ok, x, y, s = 64) => txt(c, ok ? '✓' : '✗', x, y, { size: s, fam: 'PuHui-Heavy', col: ok ? COL.mint : COL.coral, align: 'center' });
const floatY = (t, ph = 0) => 10 * Math.sin(t * 1.7 + ph) + 5 * Math.sin(t * 3.1 + ph * 2);      // 环境动态：卡片和面板轻轻浮动

// ---------- 发光的雷电线（屏幕坐标） ----------
const cablePath = (kind, x0, x1, y) => { const P = []; const N = kind === 'short' ? 40 : 140;
  for (let i = 0; i <= N; i++) { const s = i / N; P.push(kind === 'short' ? [lerp(x0, x1, s), y + 14 * Math.sin(Math.PI * s)] : [lerp(x0, x1, s), y + 120 * Math.sin(Math.PI * 2 * 1.25 * s) * (0.55 + 0.45 * Math.sin(Math.PI * s))]); }
  return P; };
const cum = P => { const a = [0]; for (let i = 1; i < P.length; i++) a.push(a[i - 1] + Math.hypot(P[i][0] - P[i - 1][0], P[i][1] - P[i - 1][1])); return a; };
const along = (P, A, d) => { let i = 1; while (i < A.length - 1 && A[i] < d) i++; const f = (d - A[i - 1]) / (A[i] - A[i - 1] || 1); return [lerp(P[i - 1][0], P[i][0], f), lerp(P[i - 1][1], P[i][1], f)]; };
const plug = (c, x, y, ang, { chip = 0 } = {}) => { c.save(); c.translate(x, y); c.rotate(ang);
  c.fillStyle = '#1a1b1c'; c.strokeStyle = 'rgba(236,230,218,.35)'; c.lineWidth = 2; c.beginPath(); c.roundRect(-8, -26, 76, 52, 12); c.fill(); c.stroke();
  const g = c.createLinearGradient(0, -16, 0, 16); g.addColorStop(0, '#e2dfd8'); g.addColorStop(0.5, '#8d8a84'); g.addColorStop(1, '#cfccc5'); c.fillStyle = g; c.beginPath(); c.roundRect(66, -15, 46, 30, 9); c.fill();
  c.fillStyle = '#f3efe5'; c.beginPath(); c.moveTo(24, -15); c.lineTo(13, 3); c.lineTo(24, 3); c.lineTo(17, 17); c.lineTo(34, -4); c.lineTo(24, -4); c.lineTo(30, -15); c.closePath(); c.fill();
  if (chip > 0) { c.save(); c.globalAlpha = chip; c.shadowColor = '#f5d77e'; c.shadowBlur = 26; c.fillStyle = '#2b2a27'; c.strokeStyle = '#f5d77e'; c.lineWidth = 3; c.beginPath(); c.roundRect(38, -12, 22, 24, 4); c.fill(); c.stroke(); c.restore(); }
  c.restore(); };
const cable = (c, t, P, { gap = 30, fiber = 0, speed = 420, chip = 0 } = {}) => { const A = cum(P), L = A[A.length - 1];
  c.save(); c.lineCap = 'round'; c.lineJoin = 'round'; c.strokeStyle = '#141516'; c.lineWidth = 30; c.beginPath(); P.forEach(([x, y], i) => i ? c.lineTo(x, y) : c.moveTo(x, y)); c.stroke();
  c.strokeStyle = fiber > 0 ? `rgba(155,232,219,${0.15 + 0.5 * fiber})` : 'rgba(236,230,218,.14)'; c.lineWidth = 6; c.beginPath(); P.forEach(([x, y], i) => i ? c.lineTo(x, y - 7) : c.moveTo(x, y - 7)); c.stroke(); c.restore();
  if (fiber > 0) T.glowLine(c, P, { col: TEAL, lw: 5, a: fiber * 0.8 });
  const col = fiber > 0.5 ? TEAL : GOLD; c.save(); c.globalCompositeOperation = 'lighter';
  for (let d = (t * speed) % gap; d < L; d += gap) { const [x, y] = along(P, A, d), r = 8; const gr = c.createRadialGradient(x, y, 0, x, y, r * 2.8); gr.addColorStop(0, 'rgba(255,250,235,.95)'); gr.addColorStop(0.4, `rgba(${col},.8)`); gr.addColorStop(1, 'rgba(0,0,0,0)'); c.fillStyle = gr; c.beginPath(); c.arc(x, y, r * 2.8, 0, 7); c.fill(); }
  c.restore();
  const n = P.length - 1; plug(c, P[0][0], P[0][1], Math.atan2(P[1][1] - P[0][1], P[1][0] - P[0][0]) + Math.PI, { chip }); plug(c, P[n][0], P[n][1], Math.atan2(P[n][1] - P[n - 1][1], P[n][0] - P[n - 1][0]), { chip }); };
const SHORT = cablePath('short', 110, 520, 700), LONG = cablePath('long', 70, 610, 1080);
// 出口的信号：从插头往右冒出来（方波往右走）
const outWave = (c, t, x0, x1, y, sg, col, amp = 80) => { const F = x0 + 4000 + t * 260; c.save(); c.strokeStyle = 'rgba(236,230,218,.18)'; c.lineWidth = 2; c.setLineDash([6, 8]); c.beginPath(); c.moveTo(x0, y); c.lineTo(x1, y); c.stroke(); c.restore();
  wave(c, x0, x1, x => y - amp * level(x, F, 44, sg), { col, lw: 6 }); };

// ---------- 1. 第一帧：两根雷电线，出口一清一糊 ----------
const cablesScene = (c, t, sh, recall) => {
  const k = T.cam({ hy: 1560, camH: 300 }); T.bg(c, k, { grid: 0.45, scroll: t * 120 }); T.streams(c, t, { a: 0.1, seed: 5 });
  const fy = floatY(t); c.save(); c.translate(0, fy);
  const fib = recall && C.fiber2 != null ? ease(t, C.fiber2, C.fiber2 + 0.6) : 0;
  cable(c, t, SHORT, { gap: 30 }); cable(c, t, LONG, { gap: lerp(60, 30, fib), fiber: fib });
  outWave(c, t, 650, 1030, 700, 2, GOLD);
  outWave(c, t, 700, 1030, 1080, lerp(15, 2, fib), fib > 0.5 ? TEAL : CORAL, lerp(70, 80, fib));
  const a0 = recall ? sh.t0 : C.tag1, a1 = recall ? sh.t0 : C.tag2;
  if (t >= a0) tag(c, '0.8 米 · 40G', 315, 590, { size: 40, bg: COL.cream, fg: COL.ink, t, at: a0 });
  const rg = recall ? C.ring2 : C.ring1;
  if (!recall) {
    if (t >= a1) tag(c, '2 米 · 20G', 340, 1300, { size: 40, bg: COL.coral, fg: COL.ink, t, at: a1 });
    if (t >= rg) { ring(c, 870, 1060, 200, 110, ease(t, rg, rg + 0.5)); if (t > rg + 0.5) qmarks(c, t, 800, 920); tag(c, '清楚', 840, 590, { size: 40, bg: COL.mint, fg: COL.ink, t, at: rg }); tag(c, '糊了', 870, 1230, { size: 40, bg: COL.coral, fg: COL.ink, t, at: rg + 0.2 }); }
  } else {
    if (t >= rg) { ring(c, 340, 1080, 320, 170, ease(t, rg, rg + 0.5)); tag(c, '2 米：只剩 20G', 340, 1310, { size: 46, bg: COL.coral, fg: COL.ink, t, at: rg }); }
    if (fib > 0.5) tag(c, '所以：越来越多的连接换成光', 540, 1440, { size: 42, bg: COL.mint, fg: COL.ink, t, at: C.fiber2 + 0.6 });
  }
  c.restore();
  if (!recall) SP.hookText(c, t, ['长一点，速度砍半？'], { y: 360, size: 96 });
};
SP.MECH.cables = (c, t, sh) => cablesScene(c, t, sh, false);
SP.MECH.cables2 = (c, t, sh) => cablesScene(c, t, sh, true);

// ---------- 「静一拍」：一张大字卡（关键句 + 荧光笔），镜头不动，只有背景缓缓流动 ----------
SP.MECH.beat = (c, t, sh) => {
  const k = T.cam({ hy: 1560, camH: 300 }); T.bg(c, k, { grid: 0.45, scroll: t * 220 }); T.streams(c, t, { a: 0.14, seed: 11 });
  const rows = sh.text, fy = floatY(t, 1), q = Math.min(1, pop(t, sh.t0, 0.25));
  const br = 1 + 0.012 * Math.sin(t * 2.2); c.save(); c.translate(W / 2 + 6 * Math.sin(t * 1.1), 860 + fy); c.scale((0.92 + 0.08 * q) * br, (0.92 + 0.08 * q) * br); c.rotate(-0.012 + 0.008 * Math.sin(t * 1.3));
  const size = sh.size || 84; c.font = `${size}px "PuHui-Heavy"`; const w = Math.max(...rows.map(r => c.measureText(r).width)) + size * 1.2, h = rows.length * size * 1.45 + size * 0.7;
  c.save(); c.translate(-w / 2, -h / 2); c.shadowColor = 'rgba(0,0,0,.6)'; c.shadowBlur = 30; c.shadowOffsetY = 10; c.fillStyle = '#f3efe6'; CL.tornRect(c, w, h, rows.join('').length * 7 + 3, 6); c.fill(); c.restore();
  rows.forEach((r, i) => { const y = -h / 2 + size * 0.35 + size * 1.45 * (i + 0.5) + size * 0.1, x = -c.measureText(r).width / 2;
    const hl = sh.hl && sh.hl[i]; if (hl) { const j = r.indexOf(hl); if (j >= 0) { const hx0 = x + c.measureText(r.slice(0, j)).width, hw = c.measureText(hl).width; SP.hlBand(c, hx0 - 6, y - size * 0.55, hx0 + hw + 6, y + size * 0.5, MO.step(seg(t, sh.t0 + 0.25 + i * 0.3, sh.t0 + 0.75 + i * 0.3), 24), i * 3 + 1); } }
    c.fillStyle = COL.ink; c.textBaseline = 'middle'; c.fillText(r, x, y); });
  c.restore();
  if (sh.kicker) tag(c, sh.kicker, W / 2, 860 + fy - h / 2 - 70, { size: 40, bg: COL.red, fg: '#f6efe4', t, at: sh.t0 });
};

// ---------- 演示：一个比特拖出尾巴 → 一串比特的尾巴叠在一起 ----------
SP.MECH.tail = (c, t, sh) => {
  const k = T.cam({ hy: 1560, camH: 300 }); T.bg(c, k, { grid: 0.4, scroll: t * 160 }); T.streams(c, t, { a: 0.08, seed: 13 });
  const fy = floatY(t, 2), X0 = 90, bw = 112, tau = 78, SEQ = [1, 0, 0, 1, 1, 0, 1, 0];
  c.save(); c.translate(0, fy);
  // 上：一个比特
  panel(c, 60, 430, 960, 340); const Y1 = 690, H1 = 190, m = ease(t, C.morph, C.morph + 0.8, 'c');
  wave(c, X0, X0 + 8 * bw, x => Y1 - H1 * lerp(x >= X0 && x < X0 + bw ? 1 : 0, resp(x - X0, 0, bw, tau), m), { col: GOLD, lw: 6 });
  if (m > 0.95) { c.save(); c.globalCompositeOperation = 'lighter'; c.fillStyle = 'rgba(239,125,98,.28)'; c.beginPath(); c.moveTo(X0 + bw, Y1); for (let x = X0 + bw; x <= X0 + 8 * bw; x += 4) c.lineTo(x, Y1 - H1 * resp(x - X0, 0, bw, tau)); c.lineTo(X0 + 8 * bw, Y1); c.closePath(); c.fill(); c.restore();
    tag(c, '尾巴', X0 + 2.7 * bw, Y1 - 120, { size: 40, bg: COL.coral, fg: COL.ink, t, at: C.morph + 0.8 }); }
  probe(c, t, X0, X0 + 8 * bw, x => Y1 - H1 * lerp(x >= X0 && x < X0 + bw ? 1 : 0, resp(x - X0, 0, bw, tau), m));
  txt(c, '1', X0 + bw / 2, Y1 + 46, { size: 42, fam: 'PuHui-Heavy', col: COL.cream, align: 'center' });
  if (t >= C.morph) tag(c, '一个比特，拖出一条尾巴', 540, 470, { size: 40, bg: COL.cream, fg: COL.ink, t, at: C.morph });
  // 下：一串比特
  if (t >= C.seq) { panel(c, 60, 860, 960, 470); const Y2 = 1210, H2 = 200, q = seg(t, C.seq, C.seq + 1.0);
    SEQ.forEach((b, j) => { if (!b) return; const qj = clamp(q * SEQ.length - j * 0.6); if (qj <= 0) return; c.save(); c.globalAlpha = 0.45 * qj; wave(c, X0, X0 + 8 * bw, x => Y2 - H2 * resp(x - X0, j, bw, tau), { col: j % 2 ? TEAL : GOLD, lw: 3 }); c.restore(); });
    SEQ.forEach((b, j) => txt(c, String(b), X0 + (j + 0.5) * bw, Y2 + 48, { size: 40, fam: 'PuHui-Heavy', col: b ? COL.cream : 'rgba(236,230,218,.45)', align: 'center' }));
    if (t >= C.sum) { const sq = ease(t, C.sum, C.sum + 0.5), sum = x => SEQ.reduce((a, b, j) => a + (b ? resp(x - X0, j, bw, tau) : 0), 0);
      c.save(); c.globalAlpha = sq; wave(c, X0, X0 + 8 * bw, x => Y2 - H2 * Math.min(1.25, sum(x)), { col: GOLD, lw: 7 }); c.restore();
      SEQ.forEach((b, j) => { if (b) return; const xc = X0 + (j + 0.5) * bw; if (sum(xc) < 0.12) return; c.save(); c.globalAlpha = 0.28 * sq; c.fillStyle = COL.redHi; c.fillRect(X0 + j * bw + 4, Y2 - H2 - 10, bw - 8, H2 + 10); c.restore();
        c.save(); c.translate(xc, Y2 - H2 - 40); c.rotate(Math.sin(t * 8 + j) * 0.12); txt(c, '?', 0, 0, { size: 50, fam: 'PuHui-Heavy', col: COL.redHi, align: 'center' }); c.restore(); });
      probe(c, t, X0, X0 + 8 * bw, x => Y2 - H2 * Math.min(1.25, sum(x)), 0.45, 0.5);
      tag(c, '前一个的尾巴，压到后一个', 540, 900, { size: 40, bg: COL.coral, fg: COL.ink, t, at: C.sum }); } }
  c.restore();
  if (t >= C.ana) tag(c, '像空车库说话：回音把字糊成一片', 540, 1430, { size: 40, bg: COL.cream, fg: COL.ink, t, at: C.ana, r: -0.01 });
};

// ---------- 演示：认错一个——照片花了一块、消息冒出乱码 ----------
const photo = (g, x, y, w, h) => { const sky = g.createLinearGradient(0, y, 0, y + h); sky.addColorStop(0, '#f2c27a'); sky.addColorStop(0.55, '#e98a5c'); sky.addColorStop(1, '#5c3a52'); g.fillStyle = sky; g.fillRect(x, y, w, h);
  g.fillStyle = '#fff2c9'; g.beginPath(); g.arc(x + w * 0.62, y + h * 0.36, w * 0.11, 0, 7); g.fill();
  g.fillStyle = '#3b2a3c'; g.beginPath(); g.moveTo(x, y + h * 0.66); for (let n = 0; n <= 12; n++) g.lineTo(x + w * n / 12, y + h * (0.58 + 0.08 * Math.sin(n * 1.7 + 1))); g.lineTo(x + w, y + h); g.lineTo(x, y + h); g.fill();
  g.fillStyle = '#241a27'; g.fillRect(x, y + h * 0.82, w, h * 0.18); };
SP.MECH.glitch = (c, t, sh) => {
  const k = T.cam({ hy: 1560, camH: 300 }); T.bg(c, k, { grid: 0.4, scroll: t * 120 }); T.streams(c, t, { a: 0.08, seed: 17 });
  const gq = ease(t, C.photo, C.photo + 0.25), mq = ease(t, C.msg, C.msg + 0.2), fy = floatY(t, 3);
  c.save(); c.translate(540 + 8 * Math.sin(t * 1.2), 880 + fy); c.rotate(-0.02 + 0.012 * Math.sin(t * 1.4));
  SP.phone(c, 0, 0, 560, 1000, (g, X, Y, w, h) => { g.fillStyle = '#ededed'; g.fillRect(X, Y, w, h); g.fillStyle = '#f7f7f7'; g.fillRect(X, Y, w, 100); txt(g, '小林', X + w / 2, Y + 64, { size: 32, fam: 'PuHui-Heavy', col: '#222', align: 'center' });
    const px = X + 40, py = Y + 150, pw = w - 160, ph = pw * 1.15, NS = 12, bad = 5;
    for (let i = 0; i < NS; i++) { const sy = py + ph * i / NS; g.save(); g.beginPath(); g.rect(px, sy, pw, ph / NS + 0.5); g.clip(); const s = i === bad ? 44 * gq : 0; photo(g, px + s, py, pw, ph); if (i === bad && gq > 0) { g.globalAlpha = 0.6 * gq; g.fillStyle = '#5fb0d8'; g.fillRect(px, sy, s, ph / NS + 1); } g.restore(); }
    if (gq > 0.5) { g.save(); g.strokeStyle = COL.redHi; g.lineWidth = 6; g.strokeRect(px - 10, py + ph * bad / NS - 8, pw + 20, ph / NS + 16); g.restore(); }
    const bx = X + w - 330, by = py + ph + 50, bwid = 300, bh = 100; g.fillStyle = '#95ec69'; g.beginPath(); g.roundRect(bx, by, bwid, bh, 20); g.fill();
    ['今', '晚', '七', '点', '见'].forEach((ch, i) => { const x = bx + 30 + i * 50; if (i === 3 && mq > 0) { g.save(); g.translate(x + 24, by + bh / 2 + 2); g.rotate(Math.sin(t * 10) * 0.15); txt(g, '?', 0, 0, { size: 54, fam: 'PuHui-Heavy', col: COL.red, align: 'center' }); g.restore(); }
      else txt(g, ch, x, by + bh / 2 + 2, { size: 46, fam: 'PuHui-Heavy', col: '#1b1b1a' }); });
    if (mq > 0.5) { g.save(); g.strokeStyle = COL.redHi; g.lineWidth = 5; g.beginPath(); g.arc(bx + 30 + 150 + 24, by + bh / 2, 40, 0, 7); g.stroke(); g.restore(); } });
  c.restore();
  if (t >= C.photo) tag(c, '照片花了一块', 260, 520, { size: 42, bg: COL.coral, fg: COL.ink, t, at: C.photo, r: -0.02 });
  if (t >= C.msg) tag(c, '消息冒出乱码', 820, 1300, { size: 42, bg: COL.coral, fg: COL.ink, t, at: C.msg, r: 0.02 });
  if (t >= C.photo) tag(c, '认错一个比特', 540, 1440, { size: 42, bg: COL.cream, fg: COL.ink, t, at: C.photo + 0.4 });
};

// ---------- 演示：速度翻倍，台阶变窄，尾巴还那么长 → 同一条尾巴压住两个比特（子弹时间） ----------
SP.MECH.faster = (c, t, sh) => {
  const bt = C.bt0 != null && t > C.bt0 && t < C.bt1 ? Math.min(seg(t, C.bt0, C.bt0 + 0.25), 1 - seg(t, C.bt1 - 0.25, C.bt1)) : 0;
  const warp = x => x < C.bt0 ? x : x < C.bt1 ? C.bt0 + (x - C.bt0) * 0.18 : C.bt0 + (C.bt1 - C.bt0) * 0.18 + (x - C.bt1);
  const te = warp(t), k = T.cam({ hy: 1560, camH: 300 }); T.bg(c, k, { grid: 0.4, scroll: te * 200 }); T.streams(c, te, { a: 0.08, seed: 19 });
  const X0 = 90, tau = 78, fy = floatY(t, 4);
  c.save(); c.translate(0, fy);
  [[460, 120, '原来', C.rowA], [930, 60, '快一倍：台阶更窄', C.rowB]].forEach(([y0, bw, lab, at]) => { if (t < at) return; panel(c, 60, y0, 960, 380); const Y = y0 + 300, Hh = 200, F = X0 + (te - at) * 900;
    const n = Math.ceil(900 / bw); const seq = [1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0].slice(0, n);
    const s = x => seq.reduce((a, b, j) => a + (b ? resp(x - X0, j, bw, tau) : 0), 0);
    wave(c, X0, Math.min(X0 + n * bw, F), x => Y - Hh * Math.min(1.3, s(x)), { col: GOLD, lw: 6 });
    if (F > X0 + n * bw) probe(c, t, X0, X0 + n * bw, x => Y - Hh * Math.min(1.3, s(x)), 0.4, bw / 100);
    for (let j = 0; j <= n; j++) { c.strokeStyle = 'rgba(236,230,218,.12)'; c.lineWidth = 2; c.beginPath(); c.moveTo(X0 + j * bw, Y - Hh - 20); c.lineTo(X0 + j * bw, Y + 10); c.stroke(); }
    tag(c, lab, 60 + 20, y0 - 4, { size: 38, bg: COL.cream, fg: COL.ink, t, at, align: 'left' }); });
  // 第一个比特的尾巴：两行一样长（括号），快的那行盖住两个比特
  if (t >= C.same) { const q = ease(t, C.same, C.same + 0.4); c.save(); c.strokeStyle = COL.redHi; c.lineWidth = 6; c.globalAlpha = q;
    for (const [y, bw] of [[790, 120], [1260, 60]]) { c.beginPath(); c.moveTo(X0 + bw, y); c.lineTo(X0 + bw, y + 16); c.lineTo(X0 + bw + 240, y + 16); c.lineTo(X0 + bw + 240, y); c.stroke(); } c.restore();
    tag(c, '尾巴一样长', 820, 790, { size: 40, bg: COL.coral, fg: COL.ink, t, at: C.same }); }
  if (t >= C.hit) { const q = ease(t, C.hit, C.hit + 0.3); c.save(); c.globalAlpha = 0.35 * q; c.fillStyle = COL.redHi; c.fillRect(X0 + 120, 1010, 240, 280); c.restore();
    tag(c, '同一条尾巴，压住两个比特', 540, 1420, { size: 46, bg: COL.coral, fg: COL.ink, t, at: C.hit }); }
  c.restore();
  if (bt > 0) { c.save(); const vg = c.createRadialGradient(W / 2, 1000, 200, W / 2, 1000, 1200); vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, `rgba(20,0,0,${0.55 * bt})`); c.fillStyle = vg; c.fillRect(0, 0, W, H); c.restore(); }
};
SP.G = { ring, floatY, wave, level, mark, panel, qmarks, probe };          // g2.js 也用这几个画法
SP.ROUTE_EXTRA = (c, t, sh) => tag(c, 'AI 芯片之间寄快递 · 第二站：路上', 540, 1500, { size: 44, bg: COL.cream, fg: COL.ink, t, at: sh.t0 + 0.2 });
})();
