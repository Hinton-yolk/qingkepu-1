// 光互连 02 · 抖音拆解版：全屏机制动画的通用框架。时间表 split/<name>.json（tools/build_split.py 从配音生成）。
// 画面 = 一串镜头（shot）：机制镜头全屏黑底（系列的黑卡片放大到整屏），纸桌镜头只用在转场和「一句话带走」（原稿剪下的文字条 + 黄色荧光笔）。
// 纯时间函数：每帧只由 t 决定；随机数全用种子。
(() => {
const { clamp, lerp } = U; const seg = MO.seg;
const D = (() => { const x = new XMLHttpRequest(); x.open('GET', window.SPLIT_PATH, false); x.send(); return JSON.parse(x.responseText); })();
const [W, H] = [1080, 1920];
const COL = { desk: '#e4ddcf', ink: '#1b1b1a', red: '#b8433f', redHi: '#e0654f', card: '#1d1d1c', card2: '#2a2927', cream: '#ece6da', creamDim: 'rgba(236,230,218,.38)',
  creamFaint: 'rgba(236,230,218,.14)', gold: '#e2b54a', goldHi: '#f5d77e', goldDim: 'rgba(226,181,74,.3)', coral: '#ef7d62', mint: '#7fd6b4', teal: '#3fb5a5', tealHi: '#9be8db',
  hl: 'rgba(222,208,20,.88)', paper: '#f3efe5' };
const L = {}; D.lines.forEach(l => { L[l.id] = l; });
const strip = s => s.replace(/[\s，。、：；？！“”「」（）,.:;?!]/g, '');
// kw(id, '词', k)：说到第 k 次出现的这个词的时刻；找不到就返回句首
const kw = (id, w, k = 0, end = false) => { const l = L[id]; if (!l) throw new Error('no line ' + id); if (w == null) return end ? l.t1 : l.t0;
  let i = -1; for (let j = 0; j <= k; j++) i = l.text.indexOf(w, i + 1); if (i < 0) { console.warn('kw miss', id, w); return l.t0; }
  const ii = end ? Math.min(l.ch.length - 1, i + w.length - 1) : i; return end ? Math.min(l.t1, l.ch[ii] + 0.12) : l.ch[ii]; };
const txt = (c, s, x, y, { size = 40, fam = 'PuHui-Medium', col = COL.cream, align = 'left', base = 'middle', alpha = 1 } = {}) => {
  c.save(); c.globalAlpha *= alpha; c.font = `${size}px "${fam}"`; c.fillStyle = col; c.textAlign = align; c.textBaseline = base; c.fillText(s, x, y); c.restore(); };
const tape = (c, s, x, y, o = {}) => MD.label(c, s, x, y, { size: 52, align: 'center', bg: COL.red, fg: '#f6efe4', ...o });
const tag = (c, s, x, y, o = {}) => MD.label(c, s, x, y, { size: 44, align: 'center', bg: COL.cream, fg: COL.ink, ...o });
// 弹出：0→1，带一点回弹（12 fps 步进，像纸片被按上去）
const pop = (t, at, d = 0.25) => MO.backOut(clamp((MO.step(t, 24) - at) / d), 2.2);
const E = { s: MO.smooth, c: MO.cubicInOut, o: MO.quintOut, l: MO.longTail, b: MO.backOut };
const ease = (t, a, b, e = 's') => E[e](seg(t, a, b));

// ---------- 背景 ----------
let PAT = {};
const darkBg = (c) => { PAT.dark = PAT.dark || c.createPattern(CL.paperTile('splitdark', COL.card, { amt: 5, grain: 5, fibers: 90, fiberCol: [60, 55, 45], seed: 9 }), 'repeat');
  c.fillStyle = PAT.dark; c.fillRect(0, 0, W, H);
  const vg = c.createRadialGradient(W / 2, H * 0.45, 300, W / 2, H / 2, 1250); vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,.42)'); c.fillStyle = vg; c.fillRect(0, 0, W, H); };
const deskBg = (c) => { PAT.desk = PAT.desk || c.createPattern(CL.paperTile('desk', COL.desk, { amt: 12, grain: 10, fibers: 320, seed: 5 }), 'repeat');
  c.fillStyle = PAT.desk; c.fillRect(0, 0, W, H);
  const vg = c.createRadialGradient(W / 2, H * 0.45, 500, W / 2, H / 2, 1300); vg.addColorStop(0, 'rgba(40,30,15,0)'); vg.addColorStop(1, 'rgba(40,30,15,.25)'); c.fillStyle = vg; c.fillRect(0, 0, W, H); };

// ---------- 纸桌：原稿剪下的文字条 ----------
const clipCache = {};
const clipCanvas = (id) => clipCache[id] || (clipCache[id] = (() => {
  const img = IMG[`assets/strips/${id}.png`]; const pad = 30, cw = img.width, ch = img.height, cv = document.createElement('canvas'); cv.width = cw + pad * 2; cv.height = ch + pad * 2;
  const g = cv.getContext('2d'); g.translate(pad, pad); CL.tornRect(g, cw, ch, id.charCodeAt(0) * 7 + (+id.slice(1) || 1) * 13, 14); g.save(); g.clip();
  g.fillStyle = COL.paper; g.fillRect(-pad, -pad, cv.width, cv.height); g.globalCompositeOperation = 'multiply'; g.drawImage(img, 0, 0);
  g.fillStyle = g.createPattern(CL.paperTile('clip', '#f6f2ea', { amt: 9, grain: 9, seed: 7 }), 'repeat'); g.fillRect(-pad, -pad, cv.width, cv.height); g.restore();
  return { cv, pad, w: cw, h: ch };
})());
// 荧光笔：一条略抖的黄带，从左往右涂
const hlBand = (c, x0, y0, x1, y1, q, seed = 1, col = COL.hl) => { if (q <= 0) return; const x = lerp(x0, x1, q), r = U.rng(seed), n = Math.max(2, Math.ceil((x - x0) / 8));
  c.save(); c.globalCompositeOperation = 'multiply'; c.fillStyle = col; c.beginPath(); c.moveTo(x0, y0 + 3);
  for (let i = 0; i <= n; i++) c.lineTo(lerp(x0, x, i / n), y0 + (r() - .5) * 4); c.quadraticCurveTo(x + 6, (y0 + y1) / 2, x, y1); for (let i = n; i >= 0; i--) c.lineTo(lerp(x0, x, i / n), y1 + (r() - .5) * 4); c.closePath(); c.fill(); c.restore(); };
// 一组文字条：S = [{id, line, from, to}]，纸条在镜头开始时一张张按上桌（12 fps），说到哪段就涂到哪段
const deskShot = (c, t, sh) => {
  deskBg(c);
  const S = sh.strips, k = 1.0, gap = 34; const items = S.map(s => ({ ...s, cc: clipCanvas(s.id) }));
  const sc = items.map(it => Math.min(960 / it.cc.w, 1.2));
  const hs = items.map((it, i) => it.cc.h * sc[i]), tot = hs.reduce((a, b) => a + b, 0) + gap * (items.length - 1);
  let y = (sh.cy || 860) - tot / 2;
  const tt = MO.step(t, 12);
  items.forEach((it, i) => { const at = sh.t0 + 0.12 + i * 0.12, q = clamp((tt - at) / 0.17); if (q <= 0) { y += hs[i] + gap; return; }
    const scale = sc[i], r = U.rng(i * 31 + 7), rot = (r() - .5) * 0.035, w = it.cc.w * scale, h = hs[i], x = W / 2 - w / 2 + (r() - .5) * 40;
    const lift = 1 + 0.08 * (1 - q);
    c.save(); c.translate(x + w / 2, y + h / 2); c.rotate(rot); c.scale(lift, lift); c.translate(-w / 2, -h / 2);
    c.shadowColor = 'rgba(40,30,15,.32)'; c.shadowBlur = 16 * lift; c.shadowOffsetY = 7 * lift;
    c.drawImage(it.cc.cv, -it.cc.pad * scale, -it.cc.pad * scale, it.cc.cv.width * scale, it.cc.cv.height * scale); c.shadowColor = 'transparent';
    if (it.line) { const a = it.from ? kw(it.line, it.from) : L[it.line].t0, b = it.to ? kw(it.line, it.to, 0, true) : L[it.line].t1;
      hlBand(c, 4, h * 0.14, w - 4, h * 0.88, MO.step(seg(t, a, b), 24), i * 5 + 3, it.col || COL.hl); }
    if (it.red && t >= it.red) { const q2 = seg(t, it.red, it.red + 0.35); c.strokeStyle = COL.red; c.lineWidth = 6; c.lineCap = 'round'; c.beginPath(); c.moveTo(6, h + 8); c.lineTo(6 + (w - 12) * q2, h + 4); c.stroke(); }
    c.restore(); y += h + gap; });
  if (sh.tape) tape(c, sh.tape.text, W / 2, (sh.cy || 860) - tot / 2 - 110, { t, at: sh.tape.at ?? sh.t0 + 0.05, size: 56, r: -0.02 });
};

// ---------- 顶部五站导航（缩小版，避开抖音顶部标签栏） ----------
const STN = ['出发', '电的路', '换乘', '光的路', '抵达'];
const drawHud = (c, t) => { if (t < D.hudIn) return;
  const w = 720, h = 60, x0 = (W - w) / 2, y0 = 196, cw = w / 5, q = pop(t, D.hudIn, 0.2);
  c.save(); c.globalAlpha = Math.min(1, q); c.translate(W / 2, y0 + h / 2); c.scale(0.9 + 0.1 * q, 0.9 + 0.1 * q); c.translate(-W / 2, -(y0 + h / 2));
  c.save(); c.translate(x0, y0); c.shadowColor = 'rgba(0,0,0,.35)'; c.shadowBlur = 8; c.shadowOffsetY = 3; c.fillStyle = '#f1ece1'; CL.tornRect(c, w, h, 91, 3); c.fill(); c.restore();
  for (let i = 0; i < 5; i++) { const cx = x0 + cw * i + cw / 2, on = i === 0;
    if (on) { c.save(); c.globalCompositeOperation = 'multiply'; c.fillStyle = COL.hl; c.fillRect(cx - cw / 2 + 8, y0 + 12, cw - 16, h - 24); c.restore(); }
    txt(c, `${i + 1} ${STN[i]}`, cx, y0 + h / 2 + 1, { size: 25, fam: 'PuHui-Heavy', col: on ? COL.ink : 'rgba(27,27,26,.35)', align: 'center' }); }
  c.restore(); };

// ---------- 关键点字幕：深色撕边条 + 奶油字，左边一小截红胶带（和黑底机制画面区分开） ----------
const SUB_Y = 1500;
const drawSubs = (c, t, sh) => { if (sh.kind === 'desk' || sh.kind === 'take' || window.NO_SUBS) return;
  const l = D.lines.find(x => x.sub && t >= x.t0 - 0.05 && t < x.t1 + 0.35); if (!l) return;
  const k = Math.min(seg(t, l.t0 - 0.05, l.t0 + 0.1), 1 - seg(t, l.t1 + 0.2, l.t1 + 0.35)); if (k <= 0) return;
  let size = 46; c.save(); c.font = `${size}px "PuHui-Heavy"`; let w = c.measureText(l.sub).width; if (w > 840) { size = Math.floor(size * 840 / w); c.font = `${size}px "PuHui-Heavy"`; w = c.measureText(l.sub).width; }
  const bw = Math.round(w + size * 1.3), bh = Math.round(size * 1.75), x = W / 2 - 30 - bw / 2;
  c.globalAlpha = k; c.save(); c.translate(x, SUB_Y - bh / 2); c.shadowColor = 'rgba(0,0,0,.5)'; c.shadowBlur = 14; c.shadowOffsetY = 4;
  c.fillStyle = '#0f0f0e'; CL.tornRect(c, bw, bh, [...l.sub].length * 7 + 11, 3); c.fill(); c.shadowColor = 'transparent';
  c.fillStyle = COL.red; c.save(); c.translate(-14, bh * 0.18); c.rotate(-0.05); CL.tornRect(c, 34, bh * 0.64, 7, 2); c.fill(); c.restore(); c.restore();
  c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillStyle = '#f3efe6'; c.fillText(l.sub, x + bw / 2, SUB_Y + size * 0.04); c.restore(); };

// ---------- 开头大字：问题从第 0 帧就在；说到哪个字，荧光笔涂到哪个字 ----------
const hookText = (c, t, rows, { y = 520, size = 112, ids = [], col = '#f6efe4', bg = COL.red, on = COL.goldHi } = {}) => {
  rows.forEach((s, i) => { c.save(); c.font = `${size}px "PuHui-Heavy"`; const w = c.measureText(s).width, x = W / 2 - w / 2, yy = y + i * size * 1.32;
    c.save(); c.translate(x - size * 0.35, yy - size * 0.72); c.rotate(i % 2 ? 0.012 : -0.015); c.shadowColor = 'rgba(0,0,0,.45)'; c.shadowBlur = 18; c.shadowOffsetY = 6;
    c.fillStyle = bg; CL.tornRect(c, w + size * 0.7, size * 1.42, 17 + i * 5, 5); c.fill(); c.restore();
    // 卡拉 OK：说到哪个字，哪个字变金色
    const l = ids[i] && L[ids[i]]; let xx = x; c.textBaseline = 'middle';
    [...s].forEach((ch, j) => { const tj = l ? (l.ch[j] ?? l.t1) : 1e9; c.fillStyle = t >= tj ? on : col; c.fillText(ch, xx, yy); xx += c.measureText(ch).width; });
    c.restore(); }); };

// ---------- 片尾：「下一条」+ 系列名 ----------
const endCard = (c, t, l) => { if (t < l.t0 - 0.1) return; const q = pop(t, l.t0 - 0.1, 0.3);
  c.save(); c.globalAlpha = Math.min(1, q); const s = l.text.replace(/^下一条：/, '');
  MD.label(c, '下一条', 150, 1330, { size: 40, bg: COL.ink, fg: '#f3efe6', t, at: l.t0 - 0.1, r: -0.03 });
  MD.label(c, s, 150, 1415, { size: 44, maxW: 860, bg: COL.cream, fg: COL.ink, t, at: l.t0, rate: 22 });
  txt(c, '一语道破 · 白话光互连', W / 2 - 30, 1540, { size: 30, fam: 'PuHui-Heavy', col: 'rgba(27,27,26,.55)', align: 'center' }); c.restore(); };

// 手机：外壳 + 屏幕，screen(g, x, y, w, h) 在屏幕里画东西（已裁切）
const phone = (c, x, y, w, h, screen, { alpha = 1 } = {}) => { c.save(); c.globalAlpha *= alpha; c.shadowColor = 'rgba(0,0,0,.6)'; c.shadowBlur = 40; c.shadowOffsetY = 16;
  c.fillStyle = '#121211'; c.beginPath(); c.roundRect(x - w / 2, y - h / 2, w, h, w * 0.12); c.fill(); c.shadowColor = 'transparent';
  c.strokeStyle = 'rgba(236,230,218,.25)'; c.lineWidth = 3; c.stroke();
  const m = w * 0.05, sx = x - w / 2 + m, sy = y - h / 2 + m * 1.6, sw = w - 2 * m, sh = h - m * 3.2;
  c.save(); c.beginPath(); c.roundRect(sx, sy, sw, sh, w * 0.07); c.clip(); screen(c, sx, sy, sw, sh); c.restore();
  c.fillStyle = '#121211'; c.beginPath(); c.roundRect(x - w * 0.12, sy + 10, w * 0.24, 22, 11); c.fill(); c.restore(); };
// 「一句话带走」：纸桌上几张打字的纸条（和口播一致），说到哪段荧光笔涂到哪段
const deskType = (c, t, sh) => {
  deskBg(c); const S = sh.type, tt = MO.step(t, 12); let y = 640;
  S.forEach((s, i) => { const big = i === 0, size = big ? 76 : 64; c.save(); c.font = `${size}px "${big ? 'PuHui-Heavy' : 'PuHui-Medium'}"`; const tw = c.measureText(s.text).width, w = tw + size * 1.1, h = size * 1.75;
    const at = sh.t0 + 0.12 + i * 0.12, q = clamp((tt - at) / 0.17); if (q <= 0) { c.restore(); y += h + 30; return; }
    const r = U.rng(i * 31 + 7), rot = (r() - .5) * 0.03, x = W / 2 - 30 - w / 2 + (r() - .5) * 30, lift = 1 + 0.08 * (1 - q);
    c.translate(x + w / 2, y + h / 2); c.rotate(rot); c.scale(lift, lift); c.translate(-w / 2, -h / 2);
    c.shadowColor = 'rgba(40,30,15,.32)'; c.shadowBlur = 16; c.shadowOffsetY = 7; c.fillStyle = big ? COL.ink : COL.paper; CL.tornRect(c, w, h, i * 17 + 5, 5); c.fill(); c.shadowColor = 'transparent';
    if (s.line && !big) { const a = s.from ? kw(s.line, s.from) : L[s.line].t0, b = s.to ? kw(s.line, s.to, 0, true) : L[s.line].t1; hlBand(c, size * 0.4, h * 0.18, w - size * 0.4, h * 0.84, MO.step(seg(t, a, b), 24), i * 5 + 3); }
    c.fillStyle = big ? '#f3efe6' : COL.ink; c.textBaseline = 'middle'; c.fillText(s.text, size * 0.55, h / 2 + 2); c.restore(); y += h + 30; });
};
window.SP = { deskType, phone, D, L, W, H, COL, kw, txt, tape, tag, pop, ease, seg, darkBg, deskBg, deskShot, hookText, endCard, hlBand, MECH: {}, STN };

SCENES.split = {
  init() { const all = [...D.lines.map(l => (l.sub || '') + l.text), ...STN, ...(window.SPLIT_GLYPHS || [])].join('').replace(/\s/g, ''); U.assertGlyphs('PuHui-Heavy', all, 'split'); },
  draw(c, lt, t) {
    const k = D.shots.findIndex(s => t >= s.t0 && t < s.t1), sh = D.shots[Math.max(0, k)];
    const paint = (g, s) => { g.save(); const f = SP.MECH[s.kind]; if (s.kind === 'desk') deskShot(g, t, s); else if (s.kind === 'take' && s.type) { deskType(g, t, s); if (SP.END) endCard(g, t, L[SP.END]); } else if (f) f(g, t, s); else { darkBg(g); txt(g, s.kind, 100, 900, { size: 60 }); } g.restore(); };
    // 换镜头：纸桌↔黑底之间用一张撕边纸从上往下盖过去（0.32 s）；黑底之间直接切（机制本身是连着的）
    const prev = D.shots[k - 1], wipe = prev && (prev.paper !== sh.paper) ? seg(t, sh.t0, sh.t0 + 0.32) : 1;
    if (wipe < 1) { paint(c, prev); const B = window.__splitBuf || (window.__splitBuf = window.__mk()), g = B.getContext('2d'); g.clearRect(0, 0, W, H); paint(g, sh);
      const yE = MO.cubicInOut(wipe) * (H + 80) - 40; c.save(); c.beginPath(); c.moveTo(0, 0); c.lineTo(W, 0); const r = U.rng(k * 13 + 1);
      for (let i = 24; i >= 0; i--) c.lineTo(W * i / 24, yE + (r() - .5) * 28); c.closePath(); c.clip(); c.drawImage(B, 0, 0); c.restore();
      c.save(); c.strokeStyle = 'rgba(0,0,0,.25)'; c.lineWidth = 6; c.beginPath(); const r2 = U.rng(k * 13 + 1); for (let i = 24; i >= 0; i--) { const yy = yE + (r2() - .5) * 28; i === 24 ? c.moveTo(W, yy) : c.lineTo(W * i / 24, yy); } c.stroke(); c.restore(); }
    else paint(c, sh);
    drawHud(c, t); drawSubs(c, t, sh);
  },
};
})();
