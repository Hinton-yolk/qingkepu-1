// 光互连 03 · 抖音第 2 条（无旁白 · 科技感）：最贵的 AI 机柜，为什么塞满铜线？
// 实物开场（机柜背面，2 秒放大镜钻进一根铜缆：柜里距离短，信号还清楚）→ 路线图 → ① 修短 ② 修好 ③ 路上修（高潮：检修站原来在雷电线插头里）→ 所以铜线没被淘汰 → 回到机柜 → 一句话。
// 依赖 g1.js 里的公用画法（SP.G）。时间点来自 D.cue。
(() => {
const { clamp, lerp } = U; const { W, H, COL, T, txt, tag, pop, ease, seg } = SP;
SP.END = null;
const C = SP.D.cue, G = SP.G;
const GOLD = [245, 215, 126], CORAL = [239, 125, 98], TEAL = [155, 232, 219];

// ---------- AI 机柜背面（屏幕坐标） ----------
const RKC = (() => { const r = U.rng(77), cab = []; for (let i = 0; i < 52; i++) { const ty = 520 + Math.floor(r() * 9) * 100 + 40, sy = 500 + r() * 880, x0 = 300 + r() * 60, xs = 650 + r() * 140;
  cab.push({ x0, y0: ty, x1: xs, y1: sy, bend: 60 + r() * 140, w: 7 + r() * 5, hi: r() > 0.55, ph: r() }); } return cab; })();
const bez = (q, u) => { const m = 1 - u; return [m * m * m * q[0][0] + 3 * m * m * u * q[1][0] + 3 * m * u * u * q[2][0] + u * u * u * q[3][0], m * m * m * q[0][1] + 3 * m * m * u * q[1][1] + 3 * m * u * u * q[2][1] + u * u * u * q[3][1]]; };
const rack = (c, t, { ring = -1, fiber = -1, far = -1 } = {}) => {
  const X0 = 240, X1 = 840, Y0 = 470, Y1 = 1430;
  c.save(); c.shadowColor = 'rgba(0,0,0,.7)'; c.shadowBlur = 50; c.fillStyle = '#16181a'; c.beginPath(); c.roundRect(X0, Y0, X1 - X0, Y1 - Y0, 18); c.fill(); c.restore();
  c.strokeStyle = 'rgba(155,232,219,.25)'; c.lineWidth = 3; c.beginPath(); c.roundRect(X0, Y0, X1 - X0, Y1 - Y0, 18); c.stroke();
  for (let i = 0; i < 9; i++) { const y = 510 + i * 100; c.fillStyle = '#23272a'; c.fillRect(X0 + 40, y, X1 - X0 - 80, 72);
    for (let k = 0; k < 4; k++) { const on = 0.5 + 0.5 * Math.sin(t * 3 + i * 1.7 + k * 2.3); c.fillStyle = `rgba(127,214,180,${0.35 + 0.6 * on})`; c.beginPath(); c.arc(X0 + 62 + k * 16, y + 16, 4, 0, 7); c.fill(); } }
  c.save(); c.lineCap = 'round';
  RKC.forEach((k, n) => { const q = [[k.x0, k.y0 + 52], [k.x0 + k.bend, k.y0 + 52], [k.x1 - k.bend * 0.6, k.y1], [k.x1, k.y1]];
    c.strokeStyle = '#0c0d0e'; c.lineWidth = k.w + 3; c.beginPath(); c.moveTo(...q[0]); c.bezierCurveTo(...q[1], ...q[2], ...q[3]); c.stroke();
    c.strokeStyle = k.hi ? '#b87a48' : '#7a5034'; c.lineWidth = k.w; c.beginPath(); c.moveTo(...q[0]); c.bezierCurveTo(...q[1], ...q[2], ...q[3]); c.stroke();
    if (n % 3 === 0) { const [x, y] = bez(q, (t * 0.6 + k.ph) % 1); c.save(); c.globalCompositeOperation = 'lighter'; const g = c.createRadialGradient(x, y, 0, x, y, 16); g.addColorStop(0, 'rgba(255,250,235,.95)'); g.addColorStop(0.4, 'rgba(226,181,74,.8)'); g.addColorStop(1, 'rgba(0,0,0,0)'); c.fillStyle = g; c.beginPath(); c.arc(x, y, 16, 0, 7); c.fill(); c.restore(); } });
  c.restore(); c.fillStyle = '#23272a'; c.fillRect(760, 500, 50, 900);
  if (fiber >= 0 && t >= fiber) { const q = ease(t, fiber, fiber + 0.4), fade = far >= 0 ? 1 : 1 - 0.75 * ease(t, fiber + 1.2, fiber + 2.0);
    const pts = []; for (let i = 0; i <= 30; i++) { const u = i / 30 * q; pts.push(far >= 0 ? [lerp(800, 1000, u), lerp(470, 300, u) - 60 * Math.sin(Math.PI * u)] : [lerp(780, 1080, u), lerp(470, 330, u) - 80 * Math.sin(Math.PI * u)]); }
    T.glowLine(c, pts, { col: TEAL, lw: 7, a: fade }); if (far >= 0 && q >= 1) { c.save(); c.globalAlpha = 0.9; c.fillStyle = '#16181a'; c.strokeStyle = 'rgba(155,232,219,.6)'; c.lineWidth = 3; c.beginPath(); c.roundRect(960, 180, 110, 200, 10); c.fill(); c.stroke(); c.restore(); } }
  if (ring >= 0 && t >= ring) G.ring(c, 560, 950, 330, 480, ease(t, ring, ring + 0.5)); };
SP.MECH.rack = (c, t, sh) => {
  const k = T.cam({ hy: 1600, camH: 300 }); T.bg(c, k, { grid: 0.45, scroll: t * 100 }); T.streams(c, t, { a: 0.1, seed: 23 });
  const fy = G.floatY(t); c.save(); c.translate(0, fy); rack(c, t, { fiber: C.fiber });
  if (t >= C.mag) { const q = MO.backOut(clamp((MO.step(t, 24) - C.mag) / 0.3), 1.6), MX = 720, MY = 820, R = 190;
    c.save(); c.translate(MX, MY); c.scale(Math.min(1.05, q), Math.min(1.05, q));
    c.save(); c.rotate(0.75); c.fillStyle = '#2b2a27'; c.fillRect(R - 10, -16, 150, 32); c.strokeStyle = COL.cream; c.lineWidth = 4; c.strokeRect(R - 10, -16, 150, 32); c.restore();
    c.save(); c.beginPath(); c.arc(0, 0, R, 0, 7); c.clip(); c.fillStyle = '#0b0c0d'; c.fillRect(-R, -R, 2 * R, 2 * R);
    const g = c.createLinearGradient(0, 40, 0, 110); g.addColorStop(0, '#b87a48'); g.addColorStop(0.5, '#8a5634'); g.addColorStop(1, '#5e3a24'); c.fillStyle = g; c.fillRect(-R, 50, 2 * R, 60);
    const F = -R + 4000 + (t - C.mag) * 260; G.wave(c, -R, R, x => 20 - 90 * G.level(x, F, 46, 2.5), { col: GOLD, lw: 6 });
    c.restore(); c.strokeStyle = COL.cream; c.lineWidth = 9; c.beginPath(); c.arc(0, 0, R, 0, 7); c.stroke(); c.restore();
    tag(c, '柜里距离短：信号还清楚', 620, 1070, { size: 40, bg: COL.mint, fg: COL.ink, t, at: C.mag + 0.4 }); }
  if (t >= C.fiber) tag(c, '不是都说要换成光？', 760, 440, { size: 42, bg: COL.tealHi, fg: COL.ink, t, at: C.fiber });
  c.restore();
  SP.hookText(c, t, ['最贵的 AI 机柜', '为什么塞满铜线？'], { y: 200, size: 72 });
};
SP.MECH.rack2 = (c, t, sh) => {
  const k = T.cam({ hy: 1600, camH: 300 }); T.bg(c, k, { grid: 0.45, scroll: t * 100 }); T.streams(c, t, { a: 0.1, seed: 23 });
  const fy = G.floatY(t); c.save(); c.translate(0, fy); rack(c, t, { ring: C.ring, fiber: C.far, far: 1 });
  if (t >= C.ring) tag(c, '柜内短距离：几千根铜缆', 540, 1460, { size: 46, bg: COL.coral, fg: COL.ink, t, at: C.ring });
  if (t >= C.far + 0.4) tag(c, '远的那段：交给光', 820, 420, { size: 42, bg: COL.tealHi, fg: COL.ink, t, at: C.far + 0.4 });
  c.restore();
};

// ---------- 两颗芯片之间的一条路：信号沿路走，越远越糊（blur 随距离增长，loss 控制增长快慢） ----------
const road = (c, t, xa, xb, y, { loss = 1, mat = 0, at = 0, mid = null } = {}) => {
  const L = xb - xa; c.save(); c.lineCap = 'round';
  c.strokeStyle = '#0c0d0e'; c.lineWidth = 34; c.beginPath(); c.moveTo(xa, y + 70); c.lineTo(xb, y + 70); c.stroke();
  const g = c.createLinearGradient(0, y + 56, 0, y + 84); g.addColorStop(0, lerp(0, 1, mat) > 0.5 ? '#f5d77e' : '#8a6a4a'); g.addColorStop(1, lerp(0, 1, mat) > 0.5 ? '#b8860b' : '#4a3626'); c.strokeStyle = g; c.lineWidth = 24; c.beginPath(); c.moveTo(xa, y + 70); c.lineTo(xb, y + 70); c.stroke();
  if (mat > 0) { c.globalAlpha = mat; c.strokeStyle = 'rgba(255,250,235,.55)'; c.lineWidth = 4; c.beginPath(); c.moveTo(xa, y + 62); c.lineTo(xb, y + 62); c.stroke(); } c.restore();
  const F = xa + 4000 + (t - at) * 300, sg = x => { const d = (x - xa) / 900; if (mid != null && x > mid) return 2 + 2 * (x - mid) / 900; return 2 + 34 * loss * Math.pow(Math.max(0, d), 1.2); },
    am = x => { if (mid != null && x > mid) return 1; return 1 - 0.45 * loss * clamp((x - xa) / 900); };
  G.wave(c, xa, xb, x => y - 80 * am(x) * G.level(x, F, 46, sg(x)), { col: GOLD, lw: 6 });
  return sg(xb) < 10; };
const ZOOM = 1.35;   // 演示放大一点，手机上看得清
const scene = (c, t, sh, draw) => { const k = T.cam({ hy: 1600, camH: 300 }); T.bg(c, k, { grid: 0.45, scroll: t * 140 }); T.streams(c, t, { a: 0.08, seed: 29 }); c.save(); c.translate(540, 880 + G.floatY(t, 2)); c.scale(ZOOM, ZOOM); c.translate(-540, -880); draw(); c.restore(); };
// ① 修短：两颗芯片隔得远 → 滑到一起
SP.MECH.short = (c, t, sh) => scene(c, t, sh, () => {
  const s = ease(t, C.slide, C.slide + 0.8, 'c'), xa = lerp(250, 390, s), xb = lerp(830, 690, s), y = 900;
  const ok = road(c, t, xa + 90, xb - 90, y, { loss: 1, at: sh.t0 });
  T.chip(c, xa, y + 70, 150, 120, { label: 'A', t }); T.chip(c, xb, y + 70, 150, 120, { label: 'B', t: t + 0.4 });
  G.mark(c, ok, xb, y - 80, 70);
  tag(c, s < 0.5 ? '路长：到了就糊' : '修短：芯片离得更近', 540, 700, { size: 46, bg: s < 0.5 ? COL.coral : COL.mint, fg: COL.ink, t, at: s < 0.5 ? sh.t0 : C.slide });
});
// ② 修好：同一条路，换成损耗更低的材料
SP.MECH.better = (c, t, sh) => scene(c, t, sh, () => {
  const m = ease(t, C.swap, C.swap + 0.6), y = 900;
  const ok = road(c, t, 330, 750, y, { loss: lerp(1.3, 0.2, m), mat: m, at: sh.t0 });
  T.chip(c, 250, y + 70, 150, 120, { label: 'A', t }); T.chip(c, 830, y + 70, 150, 120, { label: 'B', t: t + 0.4 });
  G.mark(c, ok, 830, y - 80, 70);
  tag(c, m < 0.5 ? '普通板材：一路掉' : '损耗更低的板材、铜缆', 540, 700, { size: 46, bg: m < 0.5 ? COL.coral : COL.mint, fg: COL.ink, t, at: m < 0.5 ? sh.t0 : C.swap });
});
// ③ 路上修信号：中途立一个「检修」芯片；镜头拉远——它原来在一根雷电线的插头里（高潮，子弹时间）
SP.MECH.repair = (c, t, sh) => {
  const z = ease(t, C.reveal, C.reveal + 1.0, 'c'), bt = C.reveal != null && t > C.reveal - 0.5 && t < C.reveal + 1.2 ? Math.min(seg(t, C.reveal - 0.5, C.reveal - 0.25), 1 - seg(t, C.reveal + 0.9, C.reveal + 1.2)) : 0;
  const k = T.cam({ hy: 1600, camH: 300 }); T.bg(c, k, { grid: 0.45, scroll: t * 140 }); T.streams(c, t, { a: 0.08, seed: 31 });
  const fy = G.floatY(t, 3);
  // 拉远后：一根雷电线从左边进来，插头在画面中间；检修站那条路缩进插头的窗口里
  if (z > 0) { c.save(); c.globalAlpha = z; c.translate(0, fy);
    c.save(); c.lineCap = 'round'; c.strokeStyle = '#3a3d40'; c.lineWidth = 64; c.beginPath(); c.moveTo(-60, 1300); c.bezierCurveTo(120, 1300, 180, 1120, 330, 1120); c.stroke();
    c.strokeStyle = 'rgba(236,230,218,.25)'; c.lineWidth = 10; c.beginPath(); c.moveTo(-60, 1286); c.bezierCurveTo(120, 1286, 180, 1106, 330, 1106); c.stroke(); c.restore();
    for (let d = 0; d < 1; d += 0.08) { const u = (d + t * 0.4) % 1, m = 1 - u, x = m * m * m * -60 + 3 * m * m * u * 120 + 3 * m * u * u * 180 + u * u * u * 330, y = m * m * m * 1300 + 3 * m * m * u * 1300 + 3 * m * u * u * 1120 + u * u * u * 1120;
      c.save(); c.globalCompositeOperation = 'lighter'; const g = c.createRadialGradient(x, y, 0, x, y, 18); g.addColorStop(0, 'rgba(255,250,235,.95)'); g.addColorStop(0.4, 'rgba(226,181,74,.8)'); g.addColorStop(1, 'rgba(0,0,0,0)'); c.fillStyle = g; c.beginPath(); c.arc(x, y, 18, 0, 7); c.fill(); c.restore(); }
    c.save(); c.shadowColor = 'rgba(0,0,0,.6)'; c.shadowBlur = 30; c.fillStyle = '#2a2d30'; c.strokeStyle = 'rgba(236,230,218,.55)'; c.lineWidth = 4; c.beginPath(); c.roundRect(310, 990, 450, 260, 46); c.fill(); c.stroke(); c.restore();
    const gg = c.createLinearGradient(0, 1070, 0, 1170); gg.addColorStop(0, '#eceae4'); gg.addColorStop(0.5, '#9a978f'); gg.addColorStop(1, '#d8d5ce'); c.fillStyle = gg; c.beginPath(); c.roundRect(752, 1070, 150, 100, 24); c.fill();
    c.fillStyle = '#f3efe5'; c.beginPath(); c.moveTo(352, 1030); c.lineTo(334, 1062); c.lineTo(352, 1062); c.lineTo(340, 1088); c.lineTo(370, 1052); c.lineTo(352, 1052); c.lineTo(362, 1030); c.closePath(); c.fill();
    c.restore(); }
  // 路 + 检修站（拉远时缩进插头的窗口里）
  c.save(); c.translate(0, fy); const s = lerp(ZOOM, 0.36, z), cx = lerp(540, 545, z), cy = lerp(900, 1130, z); c.translate(cx, cy); c.scale(s, s); c.translate(-540, -900);
  if (z > 0) { c.save(); c.globalAlpha = z; c.fillStyle = 'rgba(8,11,12,.9)'; c.beginPath(); c.roundRect(60, 700, 960, 420, 40); c.fill(); c.strokeStyle = '#f5d77e'; c.lineWidth = 10; c.stroke(); c.restore(); }
  const y = 880, ok = road(c, t, 300, 780, y, { loss: 1.4, at: sh.t0, mid: 540 });
  T.chip(c, 220, y + 70, 140, 115, { label: 'A', t }); T.chip(c, 860, y + 70, 140, 115, { label: 'B', t: t + 0.4 });
  if (t >= C.station) { const q = MO.backOut(clamp((MO.step(t, 24) - C.station) / 0.3), 1.8); c.save(); c.translate(540, y + 40); c.scale(q, q); T.chip(c, 0, 0, 180, 140, { label: '检修', t, glow: 0.6 + 0.4 * Math.sin(t * 4) }); c.restore(); }
  G.mark(c, ok && t >= C.station, 860, y - 90, 70); c.restore();
  if (t >= C.station && z < 0.5) tag(c, '检修站：认出来、整理干净', 540, 640, { size: 46, bg: COL.mint, fg: COL.ink, t, at: C.station });
  if (z > 0.6) { tag(c, '带芯片的雷电线', 540, 560, { size: 48, bg: COL.cream, fg: COL.ink, t, at: C.reveal + 0.6 }); tag(c, '2 米也能跑满 40G', 540, 1440, { size: 48, bg: COL.mint, fg: COL.ink, t, at: C.reveal + 1.0 }); }
  if (bt > 0) { c.save(); const vg = c.createRadialGradient(W / 2, 1000, 200, W / 2, 1000, 1200); vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, `rgba(20,0,0,${0.5 * bt})`); c.fillStyle = vg; c.fillRect(0, 0, W, H); c.restore(); }
};
})();
