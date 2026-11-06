// 白话光互连 02 · Vox 竖屏：通用渲染器（沿用第一篇）。布局、标注、标签、红线、照片、相机全部来自 ep2/desk.json（tools/build_desk.py 生成）；
// 卡片里的机制动画在 full/cards.js（FULL.CARD[kind]）。规矩同样片：相机平滑（快的帧渲染时加运动模糊）；桌上的纸片按 12fps 步进；卡片里是 3b1b 式平滑运动。
(() => {
const { clamp, lerp } = U; const seg = MO.seg;
const D = (() => { const x = new XMLHttpRequest(); x.open('GET', window.DESK_PATH || 'ep2/desk.json', false); x.send(); return JSON.parse(x.responseText); })();
const [W, H] = (window.FILM_SIZE || [1080, 1920]).map(Number), LAND = W > H, K = D.K, PX = 600 / 72;   // LAND：B站横屏版（1920×1080）
const COL = { desk: '#e4ddcf', ink: '#1b1b1a', red: '#b8433f', redHi: '#d9604f', card: '#1d1d1c', cream: '#ece6da', creamDim: 'rgba(236,230,218,.38)',
  teal: '#3fb5a5', tealHi: '#9be8db', tealDim: 'rgba(63,181,165,.28)', hl: 'rgba(222,208,20,.88)', paper: '#f3efe5' };
const S12 = t => MO.step(t, 12);
const q12 = (t, [a, b]) => seg(S12(t), a, b);
const rot = (x, y, r) => [x * Math.cos(r) - y * Math.sin(r), x * Math.sin(r) + y * Math.cos(r)];
const PC = (id, cx, cy) => { const c = D.cards[id], [rx, ry] = rot(cx, cy, c.r); return [c.at[0] + rx, c.at[1] + ry]; };
const txt = (c, s, x, y, { size = 40, fam = 'PuHui-Medium', col = COL.cream, align = 'left', base = 'middle' } = {}) => { c.font = `${size}px "${fam}"`; c.fillStyle = col; c.textAlign = align; c.textBaseline = base; c.fillText(s, x, y); };
const lab = (c, L, t) => { const bg = L.bg === 'red' ? COL.red : L.bg === 'cream' ? COL.cream : L.bg || undefined, fg = L.bg === 'cream' ? COL.ink : L.fg || undefined;
  MD.label(c, L.text, L.x, L.y, { size: L.size, align: L.align, r: L.r, bg, fg: fg || (L.bg === 'red' ? '#f6efe4' : undefined), t, at: L.at, rate: L.rate }); };
window.FULL = { D, COL, S12, q12, txt, lab, PC, seg, CARD: {} };

// ---------- 相机 ----------
const EASE = { lin: x => x, sine: MO.sineInOut, long: MO.longTail, cubic: MO.cubicInOut };
const between = (a, b, e) => {
  const z = CAM.zlerp(a.z, b.z, e), lr = Math.abs(Math.log(b.z / a.z)), lin = { x: lerp(a.x, b.x, e), y: lerp(a.y, b.y, e), z };
  if (lr < 0.05) return lin;
  const px = (b.z * b.x - a.z * a.x) / (b.z - a.z), py = (b.z * b.y - a.z * a.y) / (b.z - a.z);
  const fx = { x: px + (a.x - px) * a.z / z, y: py + (a.y - py) * a.z / z, z }, w = clamp((lr - 0.05) / 0.3);
  return { x: lerp(lin.x, fx.x, w), y: lerp(lin.y, fx.y, w), z };
};
const camAt = t => { const ks = D.cam; if (t <= ks[0].t) return ks[0];
  for (let i = 1; i < ks.length; i++) if (t <= ks[i].t) { const a = ks[i - 1], b = ks[i]; return between(a, b, EASE[b.e]((t - a.t) / (b.t - a.t))); }
  return ks[ks.length - 1]; };
const toS = (k, x, y) => [(x - k.x) * k.z + W / 2, (y - k.y) * k.z + H / 2];
window.CAM_SPEED = t => { const a = camAt(t - 1 / 60), b = camAt(t + 1 / 60), z = (a.z + b.z) / 2; return Math.hypot(b.x - a.x, b.y - a.y) * z + Math.abs(Math.log(b.z / a.z)) * 1100; };

// ---------- 剪报 ----------
const cache = {};
const clipCanvas = id => cache[id] || (cache[id] = (() => {
  const cl = D.clips[id], img = IMG[cl.src]; MD.size(img);
  const pad = 30, cw = img.width, ch = img.height, cv = document.createElement('canvas'); cv.width = cw + pad * 2; cv.height = ch + pad * 2;
  const g = cv.getContext('2d'); g.translate(pad, pad); CL.tornRect(g, cw, ch, cl.seed, 14); g.save(); g.clip();
  g.fillStyle = COL.paper; g.fillRect(-pad, -pad, cv.width, cv.height); g.globalCompositeOperation = 'multiply'; g.drawImage(img, 0, 0);
  g.fillStyle = g.createPattern(CL.paperTile('clip', '#f6f2ea', { amt: 9, grain: 9, seed: 7 }), 'repeat'); g.fillRect(-pad, -pad, cv.width, cv.height); g.restore();
  return { cv, pad };
})());
const hl = (c, x0, y0, x1, y1, q, seed = 1) => { if (q <= 0) return; const x = lerp(x0, x1, q), r = U.rng(seed), n = Math.max(2, Math.ceil((x - x0) / 2.5));
  const top = [], bot = []; for (let i = 0; i <= n; i++) { const xx = lerp(x0, x, i / n); top.push([xx, y0 + (r() - .5) * 0.9]); bot.push([xx, y1 + (r() - .5) * 0.9]); }
  c.save(); c.globalCompositeOperation = 'multiply'; c.fillStyle = COL.hl; c.beginPath(); c.moveTo(x0 - 0.6, y0 + 1.2);
  top.forEach(p => c.lineTo(p[0], p[1])); c.quadraticCurveTo(x + 1.6, (y0 + y1) / 2, bot[n][0], bot[n][1]); for (let i = n; i >= 0; i--) c.lineTo(bot[i][0], bot[i][1]); c.closePath(); c.fill(); c.restore(); };
const circle = (c, x0, y0, x1, y1, q, seed = 3) => { if (q <= 0) return;
  const cx = (x0 + x1) / 2, cy = (y0 + y1) / 2, rx = (x1 - x0) / 2 + 4, ry = (y1 - y0) / 2 + 3.5, th0 = -2.5, span = Math.PI * 2 * 1.1 * q, n = Math.ceil(90 * q) + 2;
  c.save(); c.strokeStyle = COL.red; c.lineWidth = 1.5; c.lineCap = 'round'; c.lineJoin = 'round'; c.beginPath();
  for (let i = 0; i <= n; i++) { const a = th0 + span * i / n, g = 1 + 0.07 * (a - th0) / (Math.PI * 2) + 0.025 * Math.sin(a * 3 + seed); const x = cx + Math.cos(a) * rx * g, y = cy + Math.sin(a) * ry * g; i ? c.lineTo(x, y) : c.moveTo(x, y); }
  c.stroke(); c.restore(); };
const under = (c, x0, x1, y, q, seed = 5) => { if (q <= 0) return; const x = lerp(x0, x1, q), n = Math.ceil((x - x0) / 3) + 1;
  c.save(); c.strokeStyle = COL.red; c.lineWidth = 1.4; c.lineCap = 'round'; c.beginPath();
  for (let i = 0; i <= n; i++) { const xx = lerp(x0, x, i / n), yy = y + Math.sin(xx * 0.21 + seed) * 0.45 + (xx - x0) * 0.008; i ? c.lineTo(xx, yy) : c.moveTo(xx, yy); } c.stroke(); c.restore(); };
// 一个标注可能跨两行：进度按每段宽度分配
const drawMark = (c, m, t) => { const q = q12(t, m.t); if (q <= 0) return;
  const ws = m.segs.map(s => s[2] - s[0]), tot = ws.reduce((a, b) => a + b, 0); let acc = 0;
  m.segs.forEach((s, i) => { const qi = clamp((q * tot - acc) / ws[i]); acc += ws[i]; if (qi <= 0) return;
    if (m.kind === 'hl') hl(c, s[0] - 0.4, s[1] - 0.6, s[2] + 0.4, s[3] + 0.4, qi, m.seed + i);
    else if (m.kind === 'under') under(c, s[0], s[2], s[3] + 1.6, qi, m.seed + i);
    else circle(c, s[0], s[1], s[2], s[3], qi, m.seed); }); };
const MARKS_BY = {}; D.marks.forEach(m => (MARKS_BY[m.clip] = MARKS_BY[m.clip] || []).push(m));
// 旁白版：一摞纸条里只亮正在讲的那几条，其余压暗（desk.json 的 focus；正片没有 focus，不受影响）
const STACK_OF = {}; Object.entries(D.stacks || {}).forEach(([n, st]) => st.ids.forEach(i => STACK_OF[i] = n));
const dimOf = (id, t) => { if (!D.focus) return 0; let k = 0; const st = STACK_OF[id];
  for (const f of D.focus) { if (f.stack !== st || f.ids.includes(id)) continue; const e = Math.min(seg(t, f.t[0] - 0.15, f.t[0]), 1 - seg(t, f.t[1], f.t[1] + 0.2)); k = Math.max(k, e); }
  return k; };
const drawClip = (c, id, t, view) => {
  const cl = D.clips[id], k = cl.k || K, [x0, y0, x1, y1] = cl.crop, sw = (x1 - x0) * k, sh = (y1 - y0) * k;
  if (cl.at[0] + sw / 2 + 60 < view[0] || cl.at[0] - sw / 2 - 60 > view[2] || cl.at[1] + sh / 2 + 60 < view[1] || cl.at[1] - sh / 2 - 60 > view[3]) return;
  const { cv, pad } = clipCanvas(id), s = k / PX;
  c.save(); c.translate(cl.at[0], cl.at[1]); c.rotate(cl.r); c.globalAlpha *= 1 - 0.68 * dimOf(id, t);
  c.save(); c.shadowColor = 'rgba(50,40,25,.28)'; c.shadowBlur = 10; c.shadowOffsetX = 3; c.shadowOffsetY = 6; c.drawImage(cv, -sw / 2 - pad * s, -sh / 2 - pad * s, cv.width * s, cv.height * s); c.restore();
  c.translate(-sw / 2, -sh / 2); c.scale(k, k); c.translate(-x0, -y0); (MARKS_BY[id] || []).forEach(m => drawMark(c, m, t));
  c.restore();
};

// ---------- 卡片 ----------
const drawCard = (c, id, t, view) => {
  const cd = D.cards[id]; if (cd.at[0] + cd.w / 2 + 80 < view[0] || cd.at[0] - cd.w / 2 - 80 > view[2] || cd.at[1] + cd.h / 2 + 80 < view[1] || cd.at[1] - cd.h / 2 - 80 > view[3]) return;
  c.save(); c.translate(cd.at[0], cd.at[1]); c.rotate(cd.r);
  c.save(); c.translate(-cd.w / 2, -cd.h / 2); c.shadowColor = 'rgba(40,30,15,.35)'; c.shadowBlur = 12; c.shadowOffsetX = 3; c.shadowOffsetY = 7; c.fillStyle = COL.card;
  CL.tornRect(c, cd.w, cd.h, 70 + id.length * 7 + id.charCodeAt(id.length - 1), 4); c.fill(); c.restore();
  CL.tape(c, -cd.w / 2 + 60, -cd.h / 2 + 8, -0.62, 150); CL.tape(c, cd.w / 2 - 60, -cd.h / 2 + 8, 0.6, 150);
  const fn = D.cue[id] ? FULL.CARD[cd.kind] : null; if (fn) { c.save(); fn(c, t, id, cd, D.cue[id] || {}); c.restore(); }   // 样片里没用到的卡片（没有 cue）只画空卡片
  D.cardLabels[id].forEach(L => lab(c, L, t));
  c.restore();
};

// ---------- 照片：文章里的信息图，冲印成带白边的照片贴在桌上（MD.print），按两倍分辨率缓存 ----------
const PM_BY = {}; (D.pmarks || []).forEach(m => (PM_BY[m.print] = PM_BY[m.print] || []).push(m));
const drawPrint = (c, id, t, view) => {
  const p = D.prints[id]; if (p.at[0] + p.w / 2 + 80 < view[0] || p.at[0] - p.w / 2 - 80 > view[2] || p.at[1] + p.h / 2 + 80 < view[1] || p.at[1] - p.h / 2 - 80 > view[3]) return;
  c.save(); c.translate(p.at[0], p.at[1]); c.rotate(p.r);
  c.save(); c.scale(0.5, 0.5); MD.print(c, IMG[p.src], p.w * 2, p.h * 2, { key: id, border: 30, tape: false }); c.restore();
  CL.tape(c, -p.w / 2 + 70, -p.h / 2 - 4, -0.6, 150); CL.tape(c, p.w / 2 - 70, -p.h / 2 - 4, 0.55, 150);
  (PM_BY[id] || []).forEach(m => { const q = q12(t, m.t); if (q <= 0) return; const [u0, v0, u1, v1] = m.box;
    c.save(); c.translate(-p.w / 2, -p.h / 2); c.scale(p.w / 100, p.h / 100); c.lineWidth = 6 / (p.w / 100);
    circleRaw(c, u0 * 100, v0 * 100, u1 * 100, v1 * 100, q, m.seed); c.restore(); });
  c.restore();
};
const circleRaw = (c, x0, y0, x1, y1, q, seed) => { const cx = (x0 + x1) / 2, cy = (y0 + y1) / 2, rx = (x1 - x0) / 2 + 1.2, ry = (y1 - y0) / 2 + 1.2, th0 = -2.5, span = Math.PI * 2 * 1.1 * q, n = Math.ceil(90 * q) + 2;
  c.strokeStyle = COL.red; c.lineCap = 'round'; c.lineJoin = 'round'; c.beginPath();
  for (let i = 0; i <= n; i++) { const a = th0 + span * i / n, g = 1 + 0.07 * (a - th0) / (Math.PI * 2) + 0.025 * Math.sin(a * 3 + seed); const x = cx + Math.cos(a) * rx * g, y = cy + Math.sin(a) * ry * g; i ? c.lineTo(x, y) : c.moveTo(x, y); }
  c.stroke(); };

// ---------- 红线、贴纸、小比特、进度条 ----------
const STR = {};
const strPts = s => STR[s.key] || (STR[s.key] = (() => { const pts = CL.stringPts(s.a, s.b, s.sag, 60); return { pts, cum: DG.cum(pts) }; })());
const drawString = (c, s, t, z) => { const q = MO.longTail(q12(t, s.t)); if (q <= 0) return; const { pts, cum } = strPts(s), L = cum[cum.length - 1];
  CL.string(c, pts, cum, L * q, { col: COL.red, lw: s.route ? Math.max(6, 2.4 / z) : 5 }); CL.pin(c, s.a[0], s.a[1]); if (q >= 1) CL.pin(c, s.b[0], s.b[1]); };
const along = (s, q) => { const { pts, cum } = strPts(s), d = cum[cum.length - 1] * q;
  for (let i = 1; i < pts.length; i++) if (cum[i] >= d) { const f = (d - cum[i - 1]) / (cum[i] - cum[i - 1] || 1); return [lerp(pts[i - 1][0], pts[i][0], f), lerp(pts[i - 1][1], pts[i][1], f)]; }
  return pts[pts.length - 1]; };
const ROUTE = {}; D.strings.filter(s => s.route).forEach(s => ROUTE[s.key] = s);
const drawSticker = (c, n, t) => { const at = D.pops[n - 1]; if (at == null || !D.stick[n] || S12(t) < at) return; const p = D.stick[n], pop = S12(t) - at < 1 / 12 ? 1.15 : 1;
  c.save(); c.translate(p[0], p[1]); c.scale(pop, pop); c.rotate(-0.08 + n * 0.03); c.fillStyle = 'rgba(40,30,15,.25)'; c.beginPath(); c.arc(4, 7, 84, 0, 7); c.fill();
  c.fillStyle = COL.red; c.beginPath(); c.arc(0, 0, 84, 0, 7); c.fill(); c.strokeStyle = '#f6efe4'; c.lineWidth = 6; c.beginPath(); c.arc(0, 0, 72, 0, 7); c.stroke();
  txt(c, String(n), 0, 6, { size: 110, fam: 'PuHui-Black', col: '#f6efe4', align: 'center' }); c.restore(); };
const tokenAt = t => {        // 小比特：路线预览时停在开头，每段路程沿红线滑过去
  if (t < D.hudIn) return null;
  for (const tr of D.travel) { const [a, b] = tr.t; if (t >= a - 0.25 && t <= b + 0.75) { const s = ROUTE['route' + tr.route]; return { p: along(s, MO.sineInOut(seg(t, a, b))), pop: Math.abs(t - (a - 0.25)) < 1 / 12 }; } }
  if (D.travel.length && t < D.travel[0].t[0]) return { p: ROUTE.route0.a, pop: S12(t) - D.hudIn < 1 / 12 };
  return null; };
const drawToken = (c, t, z) => { const tk = tokenAt(t); if (!tk) return; const s = Math.max(1, 0.5 / z) * (tk.pop ? 1.15 : 1);
  c.save(); c.translate(tk.p[0], tk.p[1]); c.scale(s, s); c.rotate(-0.06); c.fillStyle = 'rgba(40,30,15,.3)'; c.fillRect(-38, -32, 82, 82);
  c.fillStyle = '#f6efe4'; c.fillRect(-42, -42, 84, 84); c.strokeStyle = COL.red; c.lineWidth = 7; c.strokeRect(-42, -42, 84, 84);
  txt(c, '1', 0, 4, { size: 66, fam: 'PuHui-Black', col: COL.ink, align: 'center' }); c.restore(); };
const STN = ['出发', '电的路', '换乘', '光的路', '抵达'];
const drawHud = (c, t) => { if (S12(t) < D.hudIn) return;
  let cur = 0; D.station.forEach(([n, at]) => { if (t >= at - 1.5) cur = n; });         // 出发前 1.5 s（路程中）就切到下一站
  const lit = n => cur >= n || D.pops.some((p, i) => i + 1 === n && S12(t) >= p);
  const w = 1000, h = LAND ? 70 : 92, x0 = (W - w) / 2, y0 = LAND ? 22 : 70, inset = LAND ? 14 : 18, pop = S12(t) - D.hudIn < 1 / 12 ? 1.06 : 1;
  c.save(); c.translate(W / 2, y0 + h / 2); c.scale(pop, pop); c.translate(-W / 2, -(y0 + h / 2));
  c.save(); c.translate(x0, y0); c.shadowColor = 'rgba(40,30,15,.3)'; c.shadowBlur = 8; c.shadowOffsetY = 4; c.fillStyle = '#f1ece1'; CL.tornRect(c, w, h, 91, 4); c.fill(); c.restore();
  const cw = w / 5;
  for (let i = 0; i < 5; i++) { const n = i + 1, cx = x0 + cw * i + cw / 2, on = cur === n;
    if (on) { c.save(); c.globalCompositeOperation = 'multiply'; c.fillStyle = COL.hl; c.fillRect(cx - cw / 2 + 10, y0 + inset, cw - 20, h - 2 * inset); c.restore(); }
    txt(c, `${n} ${STN[i]}`, cx, y0 + h / 2 + 2, { size: LAND ? 28 : 32, fam: 'PuHui-Heavy', col: lit(n) ? COL.ink : 'rgba(27,27,26,.35)', align: 'center' });
    if (cur > n && cur <= 6) { c.save(); c.strokeStyle = COL.red; c.lineWidth = 4; c.beginPath(); c.moveTo(cx - 52, y0 + h - inset); c.lineTo(cx + 52, y0 + h - inset - 2); c.stroke(); c.restore(); }
    if (on) CL.pin(c, cx - cw / 2 + 18, y0 + 16); }
  c.restore(); };

// ---------- Kurzgesagt：钻进「芯」字 ----------
const drawCross = (c, t) => {
  const L = D.lens, cx = W / 2, by = LAND ? 470 : 930, bx0 = LAND ? cx - 750 : 90, bx1 = LAND ? cx + 750 : 990, bh = 150, BITS = [1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1];
  const g = c.createRadialGradient(cx, by, 0, cx, by, 900); g.addColorStop(0, '#273034'); g.addColorStop(1, '#141618'); c.fillStyle = g; c.fillRect(-20000, -20000, 40000, 40000);
  // 第几层（每「放大」一次换一层）、这一层里放大的进度
  const Z = L.zooms; let lv = 0; for (const z of Z) if (t >= z) lv++;
  const zp = lv > 0 && lv <= Z.length ? MO.cubicInOut(seg(t, Z[lv - 1], Z[lv - 1] + 0.5)) : 1;
  const final = t >= L.bits;
  // 密密麻麻的竖条：一层一层的「信号」，每层用不同的种子；放大时以中间一小段为中心横向拉开
  const dense = (layer, sx, alpha) => { const r = U.rng(101 + layer * 17); c.save(); c.globalAlpha *= alpha; c.fillStyle = 'rgba(236,230,218,.82)';
    const n = 300, w = (bx1 - bx0) / n; for (let i = 0; i < n; i++) { const hgt = r() < 0.5 ? bh * 0.85 : bh * 0.12 + r() * 0.1 * bh; const x = cx + ((bx0 + i * w) - cx) * sx; if (x + w * sx < bx0 - 5 || x > bx1 + 5) continue; c.fillRect(x, by + bh / 2 - hgt, Math.max(1, w * sx * 0.62), hgt); } c.restore(); };
  c.save(); c.beginPath(); c.rect(bx0, by - bh / 2 - 20, bx1 - bx0, bh + 40); c.clip();
  if (!final) {
    if (lv === 0 || zp >= 1) dense(lv, 1, 1);
    else { dense(lv - 1, 1 + 9 * zp, 1 - zp * 0.6); dense(lv, 0.1 + 0.9 * zp, zp); }
  } else {
    const q = MO.cubicInOut(seg(t, L.bits, L.bits + 0.5)), w = (bx1 - bx0) / BITS.length;
    dense(Z.length, 1 + 4 * q, 1 - q);
    c.save(); c.globalAlpha = q; c.strokeStyle = COL.cream; c.lineWidth = 7; c.lineJoin = 'round'; c.beginPath();
    BITS.forEach((b, i) => { const x0 = bx0 + i * w, y = b ? by - bh / 2 + 10 : by + bh / 2 - 10; i ? c.lineTo(x0, y) : c.moveTo(x0, y); c.lineTo(x0 + w, y); }); c.stroke();
    BITS.forEach((b, i) => txt(c, String(b), bx0 + (i + 0.5) * w, by - bh / 2 - 50, { size: 54, fam: 'PuHui-Heavy', col: COL.cream, align: 'center' })); c.restore();
  }
  c.restore();
  // 放大框：每层中间那一小段
  if (!final && lv < Z.length + 1) { const pre = lv < Z.length ? seg(t, Z[lv] - 0.6, Z[lv] - 0.25) : 0;
    if (pre > 0) { c.save(); c.globalAlpha = pre; c.strokeStyle = COL.redHi; c.lineWidth = 5; c.strokeRect(cx - (bx1 - bx0) * 0.05, by - bh / 2 - 12, (bx1 - bx0) * 0.1, bh + 24); c.restore(); } }
  if (t < Z[0]) { c.save(); c.strokeStyle = 'rgba(236,230,218,.5)'; c.lineWidth = 3; c.beginPath(); c.moveTo(bx0, by + bh / 2 + 40); c.lineTo(bx0, by + bh / 2 + 56); c.lineTo(bx1, by + bh / 2 + 56); c.lineTo(bx1, by + bh / 2 + 40); c.stroke(); c.restore(); }
  MD.label(c, '1 秒', cx, by - bh / 2 - 130, { size: 60, align: 'center', bg: COL.cream, fg: COL.ink, t: t < Z[0] ? t : -1, at: L.band });
  Z.forEach((z, i) => MD.label(c, i ? '再放大' : '放大', cx, by + bh / 2 + 130 + i * 0, { size: 48, align: 'center', bg: COL.red, fg: '#f6efe4', t: t < (Z[i + 1] ?? L.bits) ? t : -1, at: z }));
  MD.label(c, '这一秒里，有上千亿个这样的比特', cx, by + bh / 2 + 150, { size: 48, align: 'center', bg: COL.cream, fg: COL.ink, t, at: L.lbl });
};
const drawLens = (c, t, k) => {
  const L = D.lens, zs = toS(k, L.at[0], L.at[1]); let R = 0, lc = zs, sc = 1;
  if (t > L.open[0] && t < L.out[0]) { const e = MO.cubicInOut(seg(t, L.open[0], L.open[1])); R = 1300 * Math.pow(e, 2.2); lc = [lerp(zs[0], W / 2, MO.smooth(e)), lerp(zs[1], H / 2, MO.smooth(e))]; sc = lerp(0.3, 1, e); }
  else if (t >= L.out[0] && t < L.out[1]) { R = 1300 * Math.pow(k.z / L.zmax, 1.15) * (1 - seg(t, L.out[1] - 0.25, L.out[1] - 0.05)); sc = Math.max(0.02, R / 1300); }
  if (R <= 1) return;
  c.save(); c.beginPath(); c.arc(lc[0], lc[1], R, 0, 7); c.clip(); c.translate(lc[0], lc[1]); c.scale(sc, sc); c.translate(-W / 2, -H / 2); drawCross(c, t); c.restore();
  c.save(); c.strokeStyle = COL.tealHi; c.lineWidth = 6; c.beginPath(); c.arc(lc[0], lc[1], R, 0, 7); c.stroke(); c.restore();
};

let deskPat = null;
// 旁白字幕（只在旁白版、且 SHOW_SUBS 时画）：画面下部铺一条桌面纸色的淡带（上下渐隐），把后面的纸条压下去；字用墨黑，和剪报的字分开（剪报是宋体，字幕是黑体）
const SUB_Y = LAND ? H - 92 : 1565, SUB_MAXW = LAND ? 1500 : 940; let SUB_BAND = null;
const subBand = () => SUB_BAND || (SUB_BAND = (() => { const cv = document.createElement('canvas'); cv.width = W; cv.height = 230; const g = cv.getContext('2d');
  g.fillStyle = g.createPattern(CL.paperTile('desk', COL.desk, { amt: 12, grain: 10, fibers: 320, seed: 5 }), 'repeat'); g.fillRect(0, 0, W, 230);
  const gr = g.createLinearGradient(0, 0, 0, 230); gr.addColorStop(0, 'rgba(0,0,0,0)'); gr.addColorStop(0.28, 'rgba(0,0,0,.93)'); gr.addColorStop(0.72, 'rgba(0,0,0,.93)'); gr.addColorStop(1, 'rgba(0,0,0,0)');
  g.globalCompositeOperation = 'destination-in'; g.fillStyle = gr; g.fillRect(0, 0, W, 230); return cv; })());
const camMoving = t => { const a = camAt(t - 0.04), b = camAt(t + 0.04); return Math.hypot(b.x - a.x, b.y - a.y) * b.z > 3 || Math.abs(Math.log(b.z / a.z)) > 0.004; };
const drawSubs = (c, t) => { const s_ = D.subs.find(x => x.show !== false && t >= x.t[0] && t < x.t[1]); if (!s_) return;   // 第四版：和眼前纸条重复的字幕不出（show=false）
  // 镜头移动时（下一摞纸条正经过字幕带）淡出字幕，停稳后再出来；连续几条字幕合成一段，纸色带整段只淡入淡出一次
  let k = 1; for (const dt of [-0.12, -0.06, 0, 0.06, 0.12]) if (camMoving(t + dt)) k = Math.min(k, Math.abs(dt) / 0.18);
  if (s_.run) k = Math.min(k, seg(t, s_.run[0] - 0.02, s_.run[0] + 0.15), 1 - seg(t, s_.run[1] - 0.12, s_.run[1] + 0.03)); if (k <= 0.02) return;
  c.save(); c.globalAlpha = k; c.drawImage(subBand(), 0, SUB_Y - 115); c.restore();
  // 第五版：字幕反过来——深色撕边条＋米白字（原文纸条是米白纸＋黑字），一眼分得开；深色和黑卡片同属「讲解」那一层
  let size = 46; c.save(); c.font = `${size}px "PuHui-Heavy"`; let w = c.measureText(s_.text).width; if (w > SUB_MAXW) { size = Math.floor(size * SUB_MAXW / w); c.font = `${size}px "PuHui-Heavy"`; w = c.measureText(s_.text).width; }
  const bw = Math.round(w + size * 1.3), bh = Math.round(size * 1.75);
  c.globalAlpha = k; c.save(); c.translate(W / 2 - bw / 2, SUB_Y - bh / 2); c.shadowColor = 'rgba(40,30,15,.3)'; c.shadowBlur = 10; c.shadowOffsetY = 4;
  c.fillStyle = 'rgba(29,29,28,.94)'; CL.tornRect(c, bw, bh, [...s_.text].length * 7 + 11, 3); c.fill(); c.restore();
  c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillStyle = '#f3efe6'; c.fillText(s_.text, W / 2, SUB_Y + size * 0.04); c.restore(); };

SCENES.ep2 = {
  init() { for (const id in D.clips) clipCanvas(id);
    const all = [...(D.subs || []).map(x => x.text), ...D.labels.map(l => l.text), ...Object.values(D.cardLabels).flat().map(l => l.text), ...STN, '0123456789?1秒放大再放大这一秒里，有上千亿个这样的比特颜色仅为示意'].join('').replace(/\s/g, '');
    U.assertGlyphs('PuHui-Heavy', all, 'ep2'); },
  draw(c, lt, t) {
    const k = window.CAM_OVERRIDE || camAt(t + (window.CAM_DT || 0));   // CAM_OVERRIDE / NO_HUD：只给出封面用，渲片子时不设
    const view = [k.x - W / 2 / k.z, k.y - H / 2 / k.z, k.x + W / 2 / k.z, k.y + H / 2 / k.z];
    c.save(); c.translate(W / 2, H / 2); c.scale(k.z, k.z); c.translate(-k.x, -k.y);
    deskPat = deskPat || c.createPattern(CL.paperTile('desk', COL.desk, { amt: 12, grain: 10, fibers: 320, seed: 5 }), 'repeat');
    c.fillStyle = deskPat; c.fillRect(view[0] - 4, view[1] - 4, view[2] - view[0] + 8, view[3] - view[1] + 8);
    for (const id in D.clips) drawClip(c, id, t, view);
    for (const id in D.prints) drawPrint(c, id, t, view);
    for (const id in D.cards) drawCard(c, id, t, view);
    for (const s of D.strings) drawString(c, s, t, k.z);
    for (let n = 1; n <= 5; n++) drawSticker(c, n, t);
    for (const L of D.labels) lab(c, L, t);
    drawToken(c, t, k.z);
    c.restore();
    drawLens(c, t, k);
    const VM = Math.max(W, H), vg = c.createRadialGradient(W / 2, H * 0.45, VM * 0.35, W / 2, H / 2, VM * 0.78); vg.addColorStop(0, 'rgba(40,30,15,0)'); vg.addColorStop(1, 'rgba(40,30,15,.22)'); c.fillStyle = vg; c.fillRect(0, 0, W, H);
    if (!window.NO_HUD) drawHud(c, t);
    if (window.SHOW_SUBS && D.subs) drawSubs(c, t);
  },
};
})();
