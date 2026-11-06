// 白话光互连 · Vox 风格样片。全片是一张连续的调查桌（世界坐标），相机在上面走；时间点全在 vox/cues.json（配乐读同一份）：
//  0–3.5    剪报 A：先贴近「不是光跑得更快」上荧光笔，再松开一点，红笔圈「更适合高速、长距离」
//  3.5–7.5  红线从 A 拉到 B，镜头跟着线走；荧光笔扫「速度越高、距离越远，到达时就越模糊」，红笔划「分不清哪个是0」
//  7.5–12.5 红线引到一张黑卡片，镜头推进卡片：3b1b 式两条道，电的方波越跑越糊、数字变问号；同一串数据复制到光上，一样快，还清楚
//  12.5–17  Kurzgesagt 式：钻进光那条道，圆形镜头打开光纤的芯，拿头发丝比尺度（10 个芯排满直径），再一路拉回整张桌子
//  17–21.5  红线连到结论剪报 C → 推近：荧光笔扫「所以数据要换乘光」，黑标签写代价
// 规矩：相机平滑；桌上的纸片、荧光笔、红笔、标签按 12fps 步进（MO.step）；卡片里的机制动画是 3b1b 的平滑运动。纯时间函数，无随机（只用 U.rng 种子）。
(() => {
const { clamp, lerp } = U; const seg = MO.seg;
const Q = (() => { const x = new XMLHttpRequest(); x.open('GET', 'vox/cues.json', false); x.send(); return JSON.parse(x.responseText); })();
window.CUES = Q;
const W = 1080, H = 1920, K = 2.5, PX = 600 / 72;          // 世界单位/pt；素材像素/pt
const COL = { desk: '#e4ddcf', ink: '#1b1b1a', red: '#b8433f', redHi: '#d9604f', card: '#1d1d1c', cream: '#ece6da', creamDim: 'rgba(236,230,218,.38)',
  teal: '#3fb5a5', tealHi: '#9be8db', tealDim: 'rgba(63,181,165,.28)', hl: 'rgba(222,208,20,.88)' };
const S12 = t => MO.step(t, 12);
const q12 = (t, [a, b]) => seg(S12(t), a, b);

// ---------- 世界：剪报和卡片 ----------
const CLIPS = {
  T: { src: 'assets/clipT.png', o: [62, 86], w: 346, h: 28, x: -250, y: -1150, r: -0.035, seed: 11 },
  A: { src: 'assets/clipA.png', o: [62, 369], w: 490, h: 76, x: -40, y: -900, r: -0.018, seed: 21 },
  B: { src: 'assets/clipB.png', o: [62, 669.5], w: 490, h: 52.5, x: 70, y: -560, r: 0.022, seed: 31 },
  C: { src: 'assets/clipC.png', o: [62, 67], w: 490, h: 60, x: 30, y: 1430, r: -0.015, seed: 41 },
};
const CARD = { x: 0, y: 420, w: 900, h: 1300, r: -0.008 };
const rot = (x, y, r) => [x * Math.cos(r) - y * Math.sin(r), x * Math.sin(r) + y * Math.cos(r)];
// 剪报上的页面坐标（pt）→ 世界
const P = (id, px, py) => { const cl = CLIPS[id]; const [rx, ry] = rot((px - cl.o[0]) * K - cl.w * K / 2, (py - cl.o[1]) * K - cl.h * K / 2, cl.r); return [cl.x + rx, cl.y + ry]; };
const PC = (cx, cy) => { const [rx, ry] = rot(cx, cy, CARD.r); return [CARD.x + rx, CARD.y + ry]; };

// ---------- 相机 ----------
const toS = (k, x, y) => [(x - k.x) * k.z + W / 2, (y - k.y) * k.z + H / 2];
const ck = (p, z) => ({ x: p[0], y: p[1], z });
const LANE = { x0: -330, x1: 380, yE: -200, yL: 190, bw: 64, A: 82, v: 320 };
const ZT = PC(LANE.x1 - 40, LANE.yL);                          // 钻进去的那一点：光那条道的右段
const OVER = { x: 0, y: 160, z: 0.634 };
let KEYS = null;
const buildKeys = () => [
  { t: 0, ...ck(P('A', 178, 410), 2.55) },
  { t: Q.camOut[0], ...ck(P('A', 180, 409), 2.62) },
  { t: Q.camOut[1], ...ck(P('A', 306, 406), 2.4), e: MO.sineInOut },
  { t: Q.camB[0], ...ck(P('A', 308, 406), 2.42) },
  { t: Q.camB[1], ...ck(P('B', 230, 696), 2.3), e: MO.longTail },
  { t: Q.underB[1] - 0.05, ...ck(P('B', 445, 696), 2.3), e: MO.sineInOut },
  { t: Q.camCard[0], ...ck(P('B', 447, 696), 2.3) },
  { t: Q.camCard[1], ...ck(PC(0, -20), 1.12), e: MO.longTail },
  { t: Q.zoom[0], ...ck(PC(0, -20), 1.15) },
  { t: Q.zoom[1], ...ck(ZT, 16), e: MO.cubicInOut },
  { t: Q.pullOut[0], ...ck(ZT, 16) },
  { t: Q.pullOut[1], ...OVER, e: MO.cubicInOut },
  { t: Q.pushC[0], ...OVER },
  { t: Q.pushC[1], ...ck(P('C', 330, 131), 2.45), e: MO.longTail },
  { t: Q.dur, ...ck(P('C', 330, 132), 2.5) },
];
// 两个关键帧之间：z 按对数插值；缩放比较大时绕「两头画面里不动的那一点」缩放（每个点在屏上走直线），小时直接插值
const between = (a, b, e) => {
  const z = CAM.zlerp(a.z, b.z, e), lr = Math.abs(Math.log(b.z / a.z));
  const lin = { x: lerp(a.x, b.x, e), y: lerp(a.y, b.y, e), z };
  if (lr < 0.05) return lin;
  const px = (b.z * b.x - a.z * a.x) / (b.z - a.z), py = (b.z * b.y - a.z * a.y) / (b.z - a.z);
  const fx = { x: px + (a.x - px) * a.z / z, y: py + (a.y - py) * a.z / z, z }, w = clamp((lr - 0.05) / 0.3);
  return { x: lerp(lin.x, fx.x, w), y: lerp(lin.y, fx.y, w), z };
};
const camAt = t => {
  const ks = KEYS || (KEYS = buildKeys());
  if (t <= ks[0].t) return ks[0];
  for (let i = 1; i < ks.length; i++) if (t <= ks[i].t) { const a = ks[i - 1], b = ks[i], p = (t - a.t) / (b.t - a.t); return between(a, b, (b.e || (x => x))(p)); }
  return ks[ks.length - 1];
};

// ---------- 素材缓存 ----------
const cache = {};
const clipCanvas = (id) => cache[id] || (cache[id] = (() => {
  const cl = CLIPS[id], img = IMG[cl.src]; MD.size(img);
  const pad = 30, cw = img.width, ch = img.height, cv = document.createElement('canvas'); cv.width = cw + pad * 2; cv.height = ch + pad * 2;
  const g = cv.getContext('2d'); g.translate(pad, pad);
  CL.tornRect(g, cw, ch, cl.seed, 14); g.save(); g.clip();
  g.fillStyle = '#f3efe5'; g.fillRect(-pad, -pad, cv.width, cv.height);
  g.globalCompositeOperation = 'multiply'; g.drawImage(img, 0, 0);
  g.fillStyle = g.createPattern(CL.paperTile('clip', '#f6f2ea', { amt: 9, grain: 9, seed: 7 }), 'repeat'); g.fillRect(-pad, -pad, cv.width, cv.height);
  g.restore();
  return { cv, pad };
})());
let deskPat = null, deskTile = null;

// ---------- 小工具（剪报坐标里画，单位 pt） ----------
// 毛边荧光笔：q 0..1 从左扫到右（multiply 压在印刷字下）
const hl = (c, x0, y0, x1, y1, q, seed = 1) => { if (q <= 0) return; const x = lerp(x0, x1, q), r = U.rng(seed), n = Math.max(2, Math.ceil((x - x0) / 2.5));
  const top = [], bot = []; for (let i = 0; i <= n; i++) { const xx = lerp(x0, x, i / n); top.push([xx, y0 + (r() - .5) * 0.9]); bot.push([xx, y1 + (r() - .5) * 0.9]); }
  c.save(); c.globalCompositeOperation = 'multiply'; c.fillStyle = COL.hl; c.beginPath(); c.moveTo(x0 - 0.6, y0 + 1.2);
  top.forEach(p => c.lineTo(p[0], p[1])); c.quadraticCurveTo(x + 1.6, (y0 + y1) / 2, bot[n][0], bot[n][1]); for (let i = n; i >= 0; i--) c.lineTo(bot[i][0], bot[i][1]); c.closePath(); c.fill(); c.restore(); };
// 红笔圈（开口、略带螺旋的手绘椭圆）
const circle = (c, x0, y0, x1, y1, q, { lw = 1.5, col = COL.red, seed = 3 } = {}) => { if (q <= 0) return;
  const cx = (x0 + x1) / 2, cy = (y0 + y1) / 2, rx = (x1 - x0) / 2 + 4, ry = (y1 - y0) / 2 + 3.5, th0 = -2.5, span = Math.PI * 2 * 1.1 * q, n = Math.ceil(90 * q) + 2;
  c.save(); c.strokeStyle = col; c.lineWidth = lw; c.lineCap = 'round'; c.lineJoin = 'round'; c.beginPath();
  for (let i = 0; i <= n; i++) { const a = th0 + span * i / n, g = 1 + 0.07 * (a - th0) / (Math.PI * 2) + 0.025 * Math.sin(a * 3 + seed);
    const x = cx + Math.cos(a) * rx * g, y = cy + Math.sin(a) * ry * g; i ? c.lineTo(x, y) : c.moveTo(x, y); }
  c.stroke(); c.restore(); };
// 红笔下划线（微抖）
const under = (c, x0, x1, y, q, { lw = 1.4, col = COL.red, seed = 5 } = {}) => { if (q <= 0) return; const x = lerp(x0, x1, q), n = Math.ceil((x - x0) / 3) + 1;
  c.save(); c.strokeStyle = col; c.lineWidth = lw; c.lineCap = 'round'; c.beginPath();
  for (let i = 0; i <= n; i++) { const xx = lerp(x0, x, i / n), yy = y + Math.sin(xx * 0.21 + seed) * 0.45 + (xx - x0) * 0.008; i ? c.lineTo(xx, yy) : c.moveTo(xx, yy); } c.stroke(); c.restore(); };

const drawClip = (c, id, extra) => {
  const cl = CLIPS[id], { cv, pad } = clipCanvas(id), s = K / PX, sw = cl.w * K, sh = cl.h * K;
  c.save(); c.translate(cl.x, cl.y); c.rotate(cl.r);
  c.save(); c.shadowColor = 'rgba(50,40,25,.28)'; c.shadowBlur = 10; c.shadowOffsetX = 3; c.shadowOffsetY = 6;
  c.drawImage(cv, -sw / 2 - pad * s, -sh / 2 - pad * s, cv.width * s, cv.height * s); c.restore();
  if (extra) { c.save(); c.translate(-sw / 2, -sh / 2); c.scale(K, K); c.translate(-cl.o[0], -cl.o[1]); extra(c); c.restore(); }
  c.restore();
};

// 红线（世界坐标）：从 a 到 b 下垂，按 12fps 一节节描出；两头图钉
const STR = {};
const string = (c, key, a, b, q, sag = 0.06) => { if (q <= 0) return;
  const s = STR[key] || (STR[key] = (() => { const pts = CL.stringPts(a, b, sag, 60); return { pts, cum: DG.cum(pts) }; })());
  const L = s.cum[s.cum.length - 1]; CL.string(c, s.pts, s.cum, L * q, { col: COL.red, lw: 5 });
  CL.pin(c, a[0], a[1]); if (q >= 1) CL.pin(c, b[0], b[1]); };

// ---------- 黑卡片（3b1b 机制） ----------
const BITS = [1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1];
const bitOf = k => (k < 0 ? 0 : BITS[k % BITS.length]);
const Phi = x => 1 / (1 + Math.exp(-1.702 * x));
const sigmaAt = d => 2 + 60 * Math.pow(clamp(d / (LANE.x1 - LANE.x0)), 1.6);
// 电那条道：位置 x 上的电压（0..1），越远越糊、越弱
const elecY = (x, F) => { const { x0, bw } = LANE, d = x - x0, sg = sigmaAt(d), amp = 1 - 0.32 * clamp(d / (LANE.x1 - x0));
  const kLo = Math.max(0, Math.floor((F - x - 4 * sg) / bw) - 1), kHi = Math.ceil((F - x + 4 * sg) / bw) + 1; let y = 0;
  for (let k = kLo; k <= kHi; k++) if (bitOf(k)) y += Phi((F - k * bw - x) / sg) - Phi((F - (k + 1) * bw - x) / sg);
  return y * amp; };
const sq = (x, F) => { const k = Math.floor((F - x) / LANE.bw); return F - x < 0 ? 0 : bitOf(k); };
const kTie = (() => { for (let dk = 0; dk < 6; dk++) { const k = Math.floor((LANE.v * (Q.tie - Q.tE0) - 290) / LANE.bw) + dk; if (bitOf(k)) return k; } return 0; })();
const tieX = t => LANE.x0 + LANE.v * (t - Q.tE0) - (kTie + 0.5) * LANE.bw;
window.VOX_DBG = { kTie, blurAt: Q.tE0 + 400 / LANE.v };

const txt = (c, s, x, y, { size = 40, fam = 'PuHui-Medium', col = COL.cream, align = 'left', base = 'middle' } = {}) => { c.font = `${size}px "${fam}"`; c.fillStyle = col; c.textAlign = align; c.textBaseline = base; c.fillText(s, x, y); };
const typed = (s, t, at, rate = 14) => t < at ? '' : [...s].slice(0, Math.ceil((S12(t - at + 1e-6) + 1 / 12) * rate)).join('');

const drawCard = (c, t) => {
  const { x0, x1, yE, yL, bw, A, v } = LANE, tM = Q.morph;
  c.save(); c.translate(CARD.x, CARD.y); c.rotate(CARD.r);
  c.save(); c.translate(-CARD.w / 2, -CARD.h / 2); c.shadowColor = 'rgba(40,30,15,.35)'; c.shadowBlur = 12; c.shadowOffsetX = 3; c.shadowOffsetY = 7; c.fillStyle = COL.card; CL.tornRect(c, CARD.w, CARD.h, 77, 4); c.fill(); c.restore();
  CL.tape(c, -CARD.w / 2 + 60, -CARD.h / 2 + 8, -0.62, 150); CL.tape(c, CARD.w / 2 - 60, -CARD.h / 2 + 8, 0.6, 150);
  // 标题（打字，12fps）
  txt(c, typed('同一串数据，跑同一段路', t, Q.heading), -390, -520, { size: 44, col: COL.cream });
  // 距离轴
  const ax = MO.smooth(seg(t, Q.axis[0], Q.axis[1]));
  if (ax > 0) { c.save(); c.strokeStyle = COL.creamDim; c.fillStyle = COL.creamDim; c.lineWidth = 3; c.beginPath(); c.moveTo(x0, 430); c.lineTo(lerp(x0, x1 + 20, ax), 430); c.stroke();
    if (ax > 0.95) { c.beginPath(); c.moveTo(x1 + 34, 430); c.lineTo(x1 + 10, 418); c.lineTo(x1 + 10, 442); c.closePath(); c.fill(); }
    c.globalAlpha = clamp((ax - 0.6) / 0.4); txt(c, '出发', x0, 470, { size: 34, col: COL.creamDim }); txt(c, '跑得越远', x1 + 30, 470, { size: 34, col: COL.creamDim, align: 'right' }); c.restore(); }
  // 两条道的名字和轨道
  const la = MO.smooth(seg(t, Q.tE0 - 0.05, Q.tE0 + 0.25)), lb = MO.smooth(seg(t, tM[0], tM[0] + 0.3));
  if (la > 0) { c.save(); c.globalAlpha = la; txt(c, '电', -395, yE - A / 2, { size: 64, fam: 'PuHui-Heavy', align: 'center' });
    c.setLineDash([4, 10]); c.strokeStyle = COL.creamDim; c.lineWidth = 3; c.beginPath(); c.moveTo(x0, yE); c.lineTo(x1, yE); c.stroke(); c.restore(); }
  if (lb > 0) { c.save(); c.globalAlpha = lb; txt(c, '光', -395, yL, { size: 64, fam: 'PuHui-Heavy', col: COL.teal, align: 'center' });
    c.strokeStyle = COL.tealDim; c.lineWidth = 12; c.lineCap = 'round'; c.beginPath(); c.moveTo(x0, yL); c.lineTo(x1 + 30, yL); c.stroke(); c.restore(); }
  // 电：方波越跑越糊（3b1b 平滑运动）
  const F = x0 + v * (t - Q.tE0);
  if (t > Q.tE0) {
    const xe = Math.min(x1, F + 4 * sigmaAt(F - x0));
    c.save(); c.beginPath(); for (let x = x0; x <= xe; x += 2) { const y = yE - A * elecY(x, F); x === x0 ? c.moveTo(x, y) : c.lineTo(x, y); }
    c.strokeStyle = COL.cream; c.lineWidth = 6; c.lineJoin = 'round'; c.stroke(); c.restore();
    // 数字：近处清楚，远了变红问号
    for (let k = 0; k < 40; k++) { const xc = F - (k + 0.5) * bw; if (xc < x0 + 10 || xc > x1 - 4) continue;
      const sg = sigmaAt(xc - x0); c.save();
      if (sg < 26) { c.globalAlpha = clamp(1 - (sg - 14) / 14); txt(c, String(bitOf(k)), xc, yE - A - 42, { size: 46, fam: 'PuHui-Heavy', align: 'center' }); }
      else { const wob = Math.sin(t * 9 + k * 2.1) * 0.12; c.translate(xc, yE - A - 42); c.rotate(wob); txt(c, '?', 0, 0, { size: 50, fam: 'PuHui-Heavy', col: COL.redHi, align: 'center' }); }
      c.restore(); }
  }
  // 复制到光上：同一段方波从电那条道落下来，变成一明一暗的光脉冲
  const FL = x0 + v * (t - Q.tL0);
  if (t > tM[0] && t < tM[1]) { const e = MO.cubicInOut(seg(t, tM[0], tM[1])), xr = Math.min(x1, FL);
    c.save(); c.beginPath(); for (let x = x0; x <= xr; x += 2) { const b = sq(x, F), y = lerp(yE - A * b, yL - 26 * b, e); x === x0 ? c.moveTo(x, y) : c.lineTo(x, y); }
    c.strokeStyle = e < 0.5 ? COL.cream : COL.tealHi; c.lineWidth = lerp(6, 4, e); c.globalAlpha = 0.9; c.stroke(); c.restore(); }
  if (t >= tM[1] - 0.05) {
    const pa = clamp((t - (tM[1] - 0.05)) / 0.12);
    c.save(); c.globalAlpha = pa; c.shadowColor = COL.teal; c.shadowBlur = 22; c.fillStyle = COL.tealHi;
    for (let k = 0; k < 40; k++) { const fr = F - k * bw, bk = fr - bw; if (!bitOf(k) || fr < x0 || bk > Math.min(x1 + 30, FL)) continue;
      const a0 = Math.max(x0, bk + 5), a1 = Math.min(x1 + 30, fr - 5, FL); if (a1 - a0 > 14) { c.beginPath(); c.roundRect(a0, yL - 12, a1 - a0, 24, 12); c.fill(); } }
    c.restore();
    c.save(); c.globalAlpha = pa;
    for (let k = 0; k < 40; k++) { const xc = F - (k + 0.5) * bw; if (xc < x0 + 10 || xc > Math.min(x1 - 4, FL)) continue;
      txt(c, String(bitOf(k)), xc, yL - 58, { size: 46, fam: 'PuHui-Heavy', col: bitOf(k) ? COL.tealHi : 'rgba(155,232,219,.55)', align: 'center' }); }
    c.restore();
  }
  // 一样快：同一个比特，两条道上并排走（红色虚线把它们连起来）
  const xt = tieX(t), ta = seg(t, Q.tie, Q.tie + 0.2) * (1 - seg(xt, x1 - 30, x1 - 5));
  if (ta > 0) { c.save(); c.globalAlpha = ta; c.strokeStyle = COL.redHi; c.lineWidth = 4; c.setLineDash([10, 9]);
    c.beginPath(); c.moveTo(xt, yL - 90); c.lineTo(xt, yE - A - 80); c.stroke(); c.setLineDash([]);
    c.beginPath(); c.arc(xt, yL - 58, 32, 0, 7); c.stroke(); c.beginPath(); c.arc(xt, yE - A - 42, 34, 0, 7); c.stroke(); c.restore();
    MD.label(c, '一样快', xt - 22, (yE + yL) / 2 - 10, { size: 40, align: 'right', bg: COL.red, fg: '#f6efe4', t, at: Q.tie + 0.0833, r: -0.03 }); }
  // 结论标签
  MD.label(c, '跑远了：认不清', x1 + 10, yE - A - 118, { size: 40, align: 'right', bg: COL.red, fg: '#f6efe4', t, at: Q.lblBlur, r: 0.02 });
  MD.label(c, '光：一样快，还清楚', -370, yL + 100, { size: 40, align: 'left', bg: COL.cream, fg: COL.ink, t, at: Q.lblClear, r: -0.02 });
  c.restore();
};

// ---------- 光纤的芯 vs 头发丝（屏幕坐标里的独立小世界，镜头圈里看） ----------
const drawCross = (c, t) => {
  const cx = 540, cy = 930, R = 320, rc = R / 10;
  const g = c.createRadialGradient(cx, cy, 0, cx, cy, 900); g.addColorStop(0, '#273034'); g.addColorStop(1, '#141618'); c.fillStyle = g; c.fillRect(-20000, -20000, 40000, 40000);
  // 头发丝截面：描边、再整块填色（Kurzgesagt 式两色分面）
  const hq = q12(t, Q.hair), hf = S12(t) >= Q.hair[1] ? 1 : 0;
  if (hf) { c.save(); c.beginPath(); c.arc(cx, cy, R, 0, 7); c.fillStyle = '#a88d6a'; c.fill(); c.clip();
    c.beginPath(); c.arc(cx + 70, cy + 80, R, 0, 7); c.fillStyle = '#8f7556'; c.fill();
    c.strokeStyle = 'rgba(70,52,34,.35)'; c.lineWidth = 3; for (const rr of [0.78, 0.55]) { c.beginPath(); c.arc(cx + 10, cy + 6, R * rr, 0, 7); c.stroke(); }
    c.restore(); }
  if (hq > 0) { c.save(); c.strokeStyle = '#d8c3a2'; c.lineWidth = 12; c.lineCap = 'round'; c.beginPath(); c.arc(cx, cy, R, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * hq); c.stroke(); c.restore(); }
  // 芯：一明一暗地闪（光脉冲迎面穿过）；先一分为二，再一对对往外排，10 个芯正好排满头发丝的直径
  const slot = i => cx - R + rc + i * 2 * rc;
  const sp = MO.cubicInOut(seg(t, Q.split[0], Q.split[1])), np = t >= Q.pairs ? Math.min(4, Math.floor((t - Q.pairs) / 0.125 + 1e-6) + 1) : 0;   // 一对一对按十六分音符冒出来（和音效同格）
  const blink = BITS[Math.floor(t * 8) % BITS.length];
  const dot = (x, on) => { c.save(); if (on) TOON.glow(c, x, cy, rc * 3.2, COL.teal, 0.5); c.beginPath(); c.arc(x, cy, rc, 0, 7); c.fillStyle = on ? COL.tealHi : '#2f7d73'; c.fill();
    c.lineWidth = 3; c.strokeStyle = COL.tealHi; c.stroke(); c.restore(); };
  for (let j = 1; j <= np; j++) { dot(slot(4 - j), 1); dot(slot(5 + j), 1); }
  if (sp > 0) { dot(lerp(cx, slot(4), sp), 1); dot(lerp(cx, slot(5), sp), 1); } else dot(cx, blink);
  // 标签
  MD.label(c, '光纤的芯', cx, cy - rc - 70, { size: 48, align: 'center', bg: COL.cream, fg: COL.ink, t, at: Q.lblCore });
  MD.label(c, '一根头发丝（截面）', cx, cy - R - 80, { size: 48, align: 'center', bg: '#d8c3a2', fg: COL.ink, t, at: Q.hair[0] });
  if (S12(t) >= Q.lblTenth) { c.save(); c.strokeStyle = COL.cream; c.lineWidth = 4; const y = cy + R + 60; c.beginPath(); c.moveTo(cx - R, y - 16); c.lineTo(cx - R, y); c.lineTo(cx + R, y); c.lineTo(cx + R, y - 16); c.stroke(); c.restore(); }
  MD.label(c, '芯 ≈ 头发丝的 1/10', cx, cy + R + 140, { size: 56, align: 'center', bg: COL.cream, fg: COL.ink, t, at: Q.lblTenth, rate: 20 });
  txt(c, '颜色仅为示意', W - 60, H - 150, { size: 30, col: 'rgba(236,230,218,.45)', align: 'right' });
};

// 相机速度（屏幕上大约每帧移动多少像素），渲染器据此决定这一帧要不要做运动模糊
window.CAM_SPEED = t => { const a = camAt(t - 1 / 60), b = camAt(t + 1 / 60), z = (a.z + b.z) / 2;
  return Math.hypot(b.x - a.x, b.y - a.y) * z + Math.abs(Math.log(b.z / a.z)) * 1100; };

SCENES.vox = {
  init() { for (const id in CLIPS) clipCanvas(id);
    U.assertGlyphs('PuHui-Heavy', '同一串数据，跑同一段路电光一样快跑远了：认不清光：一样快，还清楚光纤的芯一根头发丝（截面）芯≈头发丝的1/10AI机房为啥要换成光？代价：电光转换+精密对接白话光互连·01?', 'vox');
    U.assertGlyphs('PuHui-Medium', '同一串数据，跑同一段路出发跑得越远颜色仅为示意', 'vox'); },
  draw(c, lt, t) {
    const k = camAt(t + (window.CAM_DT || 0));                  // CAM_DT：渲染时只给相机做运动模糊（纸片仍按 12fps 清楚地步进）
    // 桌面（纸纹贴死在世界里）
    c.save(); c.translate(W / 2, H / 2); c.scale(k.z, k.z); c.translate(-k.x, -k.y);
    deskTile = deskTile || CL.paperTile('desk', COL.desk, { amt: 12, grain: 10, fibers: 320, seed: 5 }); deskPat = deskPat || c.createPattern(deskTile, 'repeat');
    const vx0 = k.x - W / 2 / k.z, vy0 = k.y - H / 2 / k.z; c.fillStyle = deskPat; c.fillRect(vx0 - 4, vy0 - 4, W / k.z + 8, H / k.z + 8);

    drawClip(c, 'T');
    drawClip(c, 'A', g => {
      hl(g, 136.2, 388.2, 213.4, 403.4, q12(t, Q.hlA), 2);
      circle(g, 257.0, 388.6, 356.2, 403.2, q12(t, Q.circA), { seed: 1.3 });
    });
    drawClip(c, 'B', g => {
      hl(g, 181.8, 688.4, 368.8, 703.6, q12(t, Q.hlB), 4);
      under(g, 435.2, 513.5, 705.2, q12(t, Q.underB));
    });
    drawClip(c, 'C', g => { hl(g, 284.6, 95.8, 375.4, 108.8, q12(t, Q.hlC), 6); });
    drawCard(c, t);
    // 红线（12fps 一节节描出）
    string(c, 'ab', P('A', 306, 404.5), P('B', 176, 686.5), MO.longTail(q12(t, Q.strAB)), 0.05);
    string(c, 'bc', P('B', 509, 708), PC(-120, -CARD.h / 2 + 40), MO.longTail(q12(t, Q.strBC)), 0.05);
    string(c, 'cc', PC(300, CARD.h / 2 - 40), P('C', 280, 92), MO.longTail(q12(t, Q.strCC)), 0.08);
    // 桌上的黑标签
    { const p = P('A', 178, 356); MD.label(c, 'AI 机房为啥要换成光？', p[0], p[1], { size: 30, align: 'center', t, at: Q.lblQ, rate: 20, r: -0.025 }); }
    { const p = P('C', 330, 146); MD.label(c, '代价：电光转换 + 精密对接', p[0], p[1], { size: 29, align: 'center', t, at: Q.lblCost, r: 0.015 }); }
    { const p = P('C', 330, 171); MD.label(c, '白话光互连 · 01', p[0], p[1], { size: 22, align: 'center', bg: COL.red, t, at: Q.lblSeries, r: -0.02 }); }
    c.restore();

    // Kurzgesagt：镜头圈打开光纤的芯，拉远时跟着那一点缩回去
    const zs = toS(k, ZT[0], ZT[1]);
    let R = 0, lc = zs, sc = 1;
    if (t > Q.lens[0] && t < Q.pullOut[0]) { const e = MO.cubicInOut(seg(t, Q.lens[0], Q.lens[1]));
      R = 1300 * Math.pow(e, 2.2); lc = [lerp(zs[0], 540, MO.smooth(e)), lerp(zs[1], 960, MO.smooth(e))]; sc = lerp(0.3, 1, e); }
    else if (t >= Q.pullOut[0] && t < Q.pullOut[1]) { R = 1300 * Math.pow(k.z / 16, 1.15) * (1 - seg(t, Q.pullOut[1] - 0.25, Q.pullOut[1] - 0.05)); sc = Math.max(0.02, R / 1300); }
    if (R > 1) {
      c.save(); c.beginPath(); c.arc(lc[0], lc[1], R, 0, 7); c.clip();
      c.translate(lc[0], lc[1]); c.scale(sc, sc); c.translate(-540, -960);
      drawCross(c, t); c.restore();
      c.save(); c.strokeStyle = COL.tealHi; c.lineWidth = 6; c.beginPath(); c.arc(lc[0], lc[1], R, 0, 7); c.stroke(); c.restore();
    }
    // 轻暗角（桌面像拍出来的）
    const vg = c.createRadialGradient(W / 2, H * 0.45, H * 0.35, W / 2, H / 2, H * 0.78); vg.addColorStop(0, 'rgba(40,30,15,0)'); vg.addColorStop(1, 'rgba(40,30,15,.22)');
    c.fillStyle = vg; c.fillRect(0, 0, W, H);
  },
};
})();
