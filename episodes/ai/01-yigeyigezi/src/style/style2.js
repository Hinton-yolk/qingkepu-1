'use strict';
// 风格样张第二轮：四种画面语言 × 三个镜头。用法：style2.html?theme=D&shot=1
const W = 1080, H = 1920;
const cv = document.getElementById('c'); const ctx = cv.getContext('2d');
const Q = new URLSearchParams(location.search);
const THEMES = {
  // D 技术线稿：方格绘图纸 + 墨蓝线稿 + 排线阴影 + 尺寸标注，红铅笔点睛
  D: { mode: 'line', name: '技术线稿', paper: '#F6F3EA', grid: '#C9D3E6', ink: '#1F3A7A', key: '#E5432E', pos: '#1F3A7A', neg: '#E5432E', text: '#1F3A7A', title: '"Noto Serif CJK SC"' },
  // E 双色孔版：米白纸 + 荧光粉 + 联邦蓝两种油墨，网点、套色错位
  E: { mode: 'riso', name: '双色孔版', paper: '#F3EEE3', a: '#FF4FA3', b: '#1E5BC6', text: '#1E5BC6', key: '#FF4FA3', title: '"Smiley Sans"' },
  // F 木头积木：浅橡木桌面 + 木块字 + 柔和真实阴影 + 浅景深，像微缩实拍
  F: { mode: 'wood', name: '木头积木', desk0: '#D8B98C', desk1: '#C49D6C', maple: '#F0D9AE', mapleD: '#D7B985', mapleS: '#B8935F', ink: '#3A2416', key: '#C8392B', blue: '#2F5DA8', text: '#3A2416', pos: '#2F5DA8', neg: '#C8392B', title: '"Noto Serif CJK SC"' },
  // G 瑞士网格：白底黑块，超大无衬线字，唯一强调色群青，细网格线
  G: { mode: 'swiss', name: '瑞士网格', paper: '#F4F3EF', ink: '#111111', key: '#2340FF', pos: '#111111', neg: '#2340FF', text: '#111111', title: '"Noto Sans CJK SC"' },
};
const T = THEMES[Q.get('theme') || 'D'];
const SHOT = +(Q.get('shot') || 1);
const FB = '"Noto Sans CJK SC"', FM = '"DejaVu Sans Mono"';

function rnd(i) { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); }
function hexA(hex, a) { const n = parseInt(hex.slice(1), 16); return `rgba(${n >> 16},${(n >> 8) & 255},${n & 255},${a})`; }
function mix(h1, h2, u) { const a = parseInt(h1.slice(1), 16), b = parseInt(h2.slice(1), 16); const l = (p, q) => Math.round(p + (q - p) * u); return '#' + ((1 << 24) | (l(a >> 16, b >> 16) << 16) | (l((a >> 8) & 255, (b >> 8) & 255) << 8) | l(a & 255, b & 255)).toString(16).slice(1); }
function path(pts) { ctx.beginPath(); pts.forEach((p, i) => (i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1]))); ctx.closePath(); }

// ---------- 网点（孔版用） ----------
const DOTS = {};
function dots(col, dens) { // dens 0..1
  const key = col + dens; if (DOTS[key]) return DOTS[key];
  const c = document.createElement('canvas'); c.width = c.height = 12; const g = c.getContext('2d');
  g.fillStyle = col; g.beginPath(); g.arc(6, 6, 1 + dens * 5.5, 0, Math.PI * 2); g.fill();
  return (DOTS[key] = ctx.createPattern(c, 'repeat'));
}
function hatch(pts, col, gap = 9, ang = 1) { // 排线
  ctx.save(); path(pts); ctx.clip(); ctx.strokeStyle = col; ctx.lineWidth = 1.6;
  const xs = pts.map(p => p[0]), ys = pts.map(p => p[1]); const x0 = Math.min(...xs) - 200, x1 = Math.max(...xs) + 200, y0 = Math.min(...ys), y1 = Math.max(...ys);
  ctx.beginPath(); for (let x = x0; x < x1; x += gap) { ctx.moveTo(x, y1); ctx.lineTo(x + (y1 - y0) * ang, y0); } ctx.stroke(); ctx.restore();
}
function woodGrain(pts, base, seed, dark) {
  ctx.save(); path(pts); ctx.clip(); ctx.fillStyle = base; ctx.fill();
  const xs = pts.map(p => p[0]), ys = pts.map(p => p[1]); const x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = Math.min(...ys), y1 = Math.max(...ys);
  ctx.strokeStyle = hexA(dark, 0.18); ctx.lineWidth = 1.4;
  for (let k = 0; k < 14; k++) { const yy = y0 + (y1 - y0) * (k + rnd(seed + k)) / 14; ctx.beginPath(); ctx.moveTo(x0, yy); for (let x = x0; x <= x1; x += 8) ctx.lineTo(x, yy + Math.sin(x * 0.03 + seed + k) * 3 + Math.sin(x * 0.11 + k) * 1.2); ctx.stroke(); }
  ctx.restore();
}

// ---------- 投影 ----------
let CAM = { ox: 0, oy: 0, s: 80, a: 35 * Math.PI / 180, k: 0.55 };
function P(x, y, z) { return [CAM.ox + x * CAM.s + y * CAM.s * CAM.k * Math.cos(CAM.a), CAM.oy - z * CAM.s - y * CAM.s * CAM.k * Math.sin(CAM.a)]; }
function faces(x, y, z, w, d, h) {
  return {
    side: [P(x + w, y, z), P(x + w, y + d, z), P(x + w, y + d, z + h), P(x + w, y, z + h)],
    top: [P(x, y, z + h), P(x + w, y, z + h), P(x + w, y + d, z + h), P(x, y + d, z + h)],
    front: [P(x, y, z), P(x + w, y, z), P(x + w, y, z + h), P(x, y, z + h)],
    shadow: (() => { const g = (X, Y) => P(X + 0.35 * (z + h), Y - 0.25 * (z + h), 0); return [P(x, y, 0), g(x, y), g(x + w, y), g(x + w, y + d), P(x + w, y + d, 0), P(x + w, y, 0)]; })(),
  };
}
function box(x, y, z, w, d, h, role = 'n', seed = 0) {
  const F = faces(x, y, z, w, d, h);
  if (T.mode === 'line') {
    hatch(F.shadow, hexA(T.ink, 0.35), 10);
    path(F.side); ctx.fillStyle = T.paper; ctx.fill(); hatch(F.side, hexA(T.ink, 0.55), 7);
    path(F.top); ctx.fillStyle = mix(T.paper, '#FFFFFF', 0.6); ctx.fill();
    path(F.front); ctx.fillStyle = role === 'key' ? hexA(T.key, 0.14) : T.paper; ctx.fill();
    ctx.strokeStyle = role === 'key' ? T.key : T.ink; ctx.lineWidth = 2.6; ctx.lineJoin = 'round';
    [F.side, F.top, F.front].forEach(f => { path(f); ctx.stroke(); });
  } else if (T.mode === 'riso') {
    ctx.save(); ctx.globalCompositeOperation = 'multiply';
    path(F.shadow); ctx.fillStyle = dots(T.b, 0.35); ctx.fill();
    const ink = role === 'key' ? T.a : T.b;
    path(F.side); ctx.fillStyle = dots(ink, 0.8); ctx.fill();
    path(F.top); ctx.fillStyle = dots(ink, 0.25); ctx.fill();
    ctx.globalCompositeOperation = 'source-over'; path(F.front); ctx.fillStyle = '#FFFFFF'; ctx.fill();
    ctx.globalCompositeOperation = 'multiply'; if (role === 'key') { path(F.front); ctx.fillStyle = hexA(T.a, 0.85); ctx.fill(); }
    ctx.translate(3, -2); ctx.strokeStyle = hexA(T.a, 0.8); ctx.lineWidth = 2.2; path(F.front); ctx.stroke();
    ctx.translate(-3, 2); ctx.strokeStyle = T.b; ctx.lineWidth = 2.4; [F.side, F.top, F.front].forEach(f => { path(f); ctx.stroke(); });
    ctx.restore();
  } else if (T.mode === 'wood') {
    ctx.save(); ctx.filter = 'blur(10px)'; path(F.shadow); ctx.fillStyle = 'rgba(60,35,15,0.35)'; ctx.fill(); ctx.restore();
    woodGrain(F.side, T.mapleS, seed + 3, T.ink); woodGrain(F.top, mix(T.maple, '#FFFFFF', 0.25), seed + 7, T.ink);
    woodGrain(F.front, role === 'key' ? mix(T.key, T.maple, 0.15) : T.maple, seed, T.ink);
    ctx.strokeStyle = 'rgba(255,245,225,0.55)'; ctx.lineWidth = 2; path(F.top); ctx.stroke();
    ctx.strokeStyle = 'rgba(70,40,15,0.25)'; ctx.lineWidth = 1.5; path(F.front); ctx.stroke();
  } else { // swiss
    path(F.side); ctx.fillStyle = role === 'key' ? mix(T.key, '#000000', 0.35) : '#2A2A2A'; ctx.fill();
    path(F.top); ctx.fillStyle = role === 'key' ? mix(T.key, '#FFFFFF', 0.25) : '#4A4A4A'; ctx.fill();
    path(F.front); ctx.fillStyle = role === 'key' ? T.key : T.ink; ctx.fill();
  }
  return F;
}
function tok(x, y, z, ch, st = 'n', sc = 1) {
  const w = sc, h = 1.15 * sc, d = 0.55 * sc;
  if (st === 'slot') {
    const F = faces(x, y, z, w, d, h); ctx.save(); ctx.setLineDash([10, 8]); ctx.lineWidth = 3; ctx.strokeStyle = T.key; [F.front, F.top, F.side].forEach(f => { path(f); ctx.stroke(); }); ctx.restore();
  } else box(x, y, z, w, d, h, st === 'key' ? 'key' : 'n', (ch.charCodeAt(0) % 50));
  const p = P(x + w / 2, y, z + h / 2);
  let col = T.ink;
  if (T.mode === 'line') col = st === 'key' || st === 'slot' ? T.key : T.ink;
  if (T.mode === 'riso') col = st === 'key' ? '#FFFFFF' : (st === 'slot' ? T.a : T.b);
  if (T.mode === 'wood') col = st === 'slot' ? T.key : (st === 'key' ? '#FFF6E6' : ((ch.charCodeAt(0) % 2) ? T.key : T.blue));
  if (T.mode === 'swiss') col = st === 'slot' ? T.key : '#FFFFFF';
  ctx.fillStyle = col; ctx.font = `${T.mode === 'swiss' ? 900 : 700} ${Math.round(CAM.s * 0.62 * sc)}px ${FB}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText(st === 'slot' ? '?' : ch, p[0], p[1] + 2);
}
function slab(x, y, z, w, d, seed, lit = 0) {
  box(x, y, z, w, d, 0.22, 'n', seed * 11);
  const cols = 10, rows = 6, cw = w / cols, cd = d / rows, Z = z + 0.221;
  for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
    const v = rnd(seed * 31 + r * 13 + c * 7) * 2 - 1, m = Math.abs(v);
    const X = x + c * cw, Y = y + r * cd;
    if (T.mode === 'wood') { // 彩色木钉
      const p = P(X + cw / 2, Y + cd / 2, Z); ctx.fillStyle = v >= 0 ? T.pos : T.neg; ctx.globalAlpha = 0.35 + 0.65 * m;
      ctx.beginPath(); ctx.ellipse(p[0], p[1], CAM.s * cw * 0.32, CAM.s * cw * 0.2, 0, 0, Math.PI * 2); ctx.fill(); ctx.globalAlpha = 1; continue;
    }
    const q = [P(X + 0.07, Y + 0.07, Z), P(X + cw - 0.07, Y + 0.07, Z), P(X + cw - 0.07, Y + cd - 0.07, Z), P(X + 0.07, Y + cd - 0.07, Z)];
    if (T.mode === 'line') { path(q); if (v < 0) hatch(q, hexA(T.key, 0.4 + 0.5 * m), 5, -1); else { ctx.fillStyle = hexA(T.ink, 0.12 + 0.5 * m); ctx.fill(); } }
    else if (T.mode === 'riso') { ctx.save(); ctx.globalCompositeOperation = 'multiply'; path(q); ctx.fillStyle = dots(v >= 0 ? T.b : T.a, 0.2 + 0.8 * m); ctx.fill(); ctx.restore(); }
    else { path(q); ctx.fillStyle = v >= 0 ? hexA('#FFFFFF', 0.2 + 0.8 * m) : hexA(T.key, 0.35 + 0.65 * m); ctx.fill(); }
  }
}
function bead(x, y, z, r) {
  const p = P(x, y, z);
  if (T.mode === 'line') { ctx.strokeStyle = T.key; ctx.lineWidth = 3; ctx.fillStyle = hexA(T.key, 0.15); ctx.beginPath(); ctx.arc(p[0], p[1], r, 0, Math.PI * 2); ctx.fill(); ctx.stroke(); return; }
  if (T.mode === 'riso') { ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.fillStyle = T.a; ctx.beginPath(); ctx.arc(p[0] + 3, p[1] - 2, r, 0, Math.PI * 2); ctx.fill(); ctx.restore(); return; }
  if (T.mode === 'swiss') { ctx.fillStyle = T.key; ctx.beginPath(); ctx.arc(p[0], p[1], r, 0, Math.PI * 2); ctx.fill(); return; }
  const g = ctx.createRadialGradient(p[0] - r * 0.35, p[1] - r * 0.35, r * 0.1, p[0], p[1], r); g.addColorStop(0, '#FF9A8A'); g.addColorStop(1, T.key);
  ctx.save(); ctx.filter = 'blur(6px)'; ctx.fillStyle = 'rgba(60,35,15,0.35)'; ctx.beginPath(); ctx.ellipse(p[0] + 20, p[1] + 50, r, r * 0.4, 0, 0, Math.PI * 2); ctx.fill(); ctx.restore();
  ctx.fillStyle = g; ctx.beginPath(); ctx.arc(p[0], p[1], r, 0, Math.PI * 2); ctx.fill();
}

// ---------- 底 ----------
function background() {
  if (T.mode === 'line') {
    ctx.fillStyle = T.paper; ctx.fillRect(0, 0, W, H);
    for (let x = 0; x < W; x += 30) { ctx.fillStyle = hexA(T.grid, x % 150 ? 0.45 : 0.9); ctx.fillRect(x, 0, x % 150 ? 1 : 2, H); }
    for (let y = 0; y < H; y += 30) { ctx.fillStyle = hexA(T.grid, y % 150 ? 0.45 : 0.9); ctx.fillRect(0, y, W, y % 150 ? 1 : 2); }
    ctx.fillStyle = hexA(T.ink, 0.7); ctx.font = `400 22px ${FM}`; ctx.textAlign = 'left'; ctx.fillText('FIG.01  ·  逐字生成  ·  SCALE 示意', 60, 1820);
  } else if (T.mode === 'riso') {
    ctx.fillStyle = T.paper; ctx.fillRect(0, 0, W, H);
    for (let i = 0; i < 2500; i++) { ctx.fillStyle = hexA(i % 2 ? T.a : T.b, 0.08); ctx.fillRect(rnd(i) * W, rnd(i + 7) * H, 2, 2); }
  } else if (T.mode === 'wood') {
    const g = ctx.createLinearGradient(0, 0, 0, H); g.addColorStop(0, mix(T.desk0, '#FFFFFF', 0.15)); g.addColorStop(1, T.desk1); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    ctx.strokeStyle = 'rgba(90,55,25,0.12)'; ctx.lineWidth = 2;
    for (let k = 0; k < 60; k++) { const y = k * 34 + rnd(k) * 20; ctx.beginPath(); ctx.moveTo(0, y); for (let x = 0; x <= W; x += 20) ctx.lineTo(x, y + Math.sin(x * 0.006 + k) * 8); ctx.stroke(); }
    for (let k = 1; k < 4; k++) { ctx.fillStyle = 'rgba(70,40,15,0.18)'; ctx.fillRect(0, k * 520 - 2, W, 3); }
    const v = ctx.createRadialGradient(W * 0.5, H * 0.45, H * 0.2, W * 0.5, H * 0.5, H * 0.8); v.addColorStop(0, 'rgba(255,240,210,0.15)'); v.addColorStop(1, 'rgba(40,20,5,0.35)'); ctx.fillStyle = v; ctx.fillRect(0, 0, W, H);
  } else {
    ctx.fillStyle = T.paper; ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = 'rgba(17,17,17,0.12)'; for (let x = 60; x < W; x += 160) ctx.fillRect(x, 0, 1, H);
    ctx.fillStyle = 'rgba(17,17,17,0.05)'; ctx.font = `900 520px ${FB}`; ctx.textAlign = 'right'; ctx.fillText('01', W - 20, 1780);
  }
}
function blurred(px, fn) { ctx.save(); ctx.filter = `blur(${px}px)`; fn(); ctx.restore(); }

// ---------- 字 ----------
function rich(l, x, y, size, font, weight, col, key, align = 'center') {
  const parts = l.split(/(\{[^}]*\})/).filter(Boolean); ctx.font = `${weight} ${size}px ${font}`;
  let tw = 0; parts.forEach(p => { tw += ctx.measureText(p.replace(/[{}]/g, '')).width; });
  let cx = align === 'center' ? x - tw / 2 : x; ctx.textAlign = 'left'; ctx.textBaseline = 'middle';
  parts.forEach(p => { const hi = p[0] === '{'; const s = p.replace(/[{}]/g, ''); ctx.fillStyle = hi ? key : col; ctx.fillText(s, cx, y); cx += ctx.measureText(s).width; });
  return tw;
}
function title(lines) {
  if (T.mode === 'swiss') { rich(lines[0], 60, 200, 120, FB, 900, T.ink, T.key, 'left'); rich(lines[1], 60, 335, 104, FB, 900, T.ink, T.key, 'left'); ctx.fillStyle = T.ink; ctx.fillRect(60, 420, 960, 8); return; }
  if (T.mode === 'riso') {
    ctx.save(); ctx.globalCompositeOperation = 'multiply';
    lines.forEach((l, i) => { ctx.save(); ctx.translate(4, -3); rich(l.replace(/[{}]/g, ''), W / 2, 220 + i * 130, i ? 104 : 116, T.title, 400, hexA(T.a, 0.7), hexA(T.a, 0.7)); ctx.restore(); rich(l, W / 2, 220 + i * 130, i ? 104 : 116, T.title, 400, T.b, T.a); });
    ctx.restore(); return;
  }
  lines.forEach((l, i) => rich(l, W / 2, 230 + i * 128, 96, T.title, 900, T.text, T.key));
}
function caption(lines) {
  const lh = 80, y = 1480; ctx.font = `900 60px ${FB}`; let mw = 0; lines.forEach(l => { mw = Math.max(mw, ctx.measureText(l.replace(/[{}]/g, '')).width); });
  const bw = mw + 64, bh = lines.length * lh + 36; let col = T.text, key = T.key;
  if (T.mode === 'line') { ctx.fillStyle = '#FFFFFF'; ctx.fillRect(W / 2 - bw / 2, y - bh / 2, bw, bh); ctx.strokeStyle = T.ink; ctx.lineWidth = 3; ctx.strokeRect(W / 2 - bw / 2, y - bh / 2, bw, bh); ctx.fillStyle = T.ink; ctx.font = `400 20px ${FM}`; ctx.textAlign = 'left'; ctx.fillText('NOTE', W / 2 - bw / 2 + 8, y - bh / 2 - 14); }
  if (T.mode === 'riso') { ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.fillStyle = T.b; ctx.fillRect(W / 2 - bw / 2, y - bh / 2, bw, bh); ctx.restore(); col = '#FFFFFF'; key = '#FFC2E0'; }
  if (T.mode === 'wood') { ctx.save(); ctx.filter = 'blur(8px)'; ctx.fillStyle = 'rgba(50,25,5,0.35)'; ctx.fillRect(W / 2 - bw / 2 + 10, y - bh / 2 + 14, bw, bh); ctx.restore(); ctx.fillStyle = '#FBF4E6'; ctx.beginPath(); ctx.roundRect(W / 2 - bw / 2, y - bh / 2, bw, bh, 8); ctx.fill(); }
  if (T.mode === 'swiss') { ctx.fillStyle = T.ink; ctx.fillRect(60, y - bh / 2, Math.max(bw, 620), bh); col = '#FFFFFF'; key = '#8FA0FF'; }
  lines.forEach((l, i) => { const yy = y - ((lines.length - 1) * lh) / 2 + i * lh; if (T.mode === 'swiss') rich(l, 92, yy, 60, FB, 900, col, key, 'left'); else rich(l, W / 2, yy, 60, FB, 900, col, key); });
}
function label(txt, x, y, size = 30) { ctx.font = `700 ${size}px ${T.mode === 'line' ? FM + ',' + FB : FB}`; ctx.fillStyle = T.mode === 'riso' ? T.b : T.text; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(txt, x, y); }
function dim(x0, y0, x1, y1, txt) { // 尺寸标注（线稿专用）
  if (T.mode !== 'line') return; ctx.strokeStyle = T.key; ctx.fillStyle = T.key; ctx.lineWidth = 2;
  ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x1, y1); ctx.stroke();
  [[x0, y0, x1, y1], [x1, y1, x0, y0]].forEach(([a, b, c, d]) => { const an = Math.atan2(d - b, c - a); ctx.beginPath(); ctx.moveTo(a, b); ctx.lineTo(a + 14 * Math.cos(an + 0.4), b + 14 * Math.sin(an + 0.4)); ctx.lineTo(a + 14 * Math.cos(an - 0.4), b + 14 * Math.sin(an - 0.4)); ctx.fill(); });
  ctx.font = `400 24px ${FM},${FB}`; ctx.textAlign = 'center'; ctx.fillText(txt, (x0 + x1) / 2, (y0 + y1) / 2 - 18);
}

// ---------- 手机 ----------
function phone(px, py, pw, ph, sk) {
  ctx.save();
  const body = [[px, py], [px + pw, py + sk], [px + pw, py + ph - 4], [px, py + ph + 30]];
  if (T.mode === 'wood') { ctx.save(); ctx.filter = 'blur(14px)'; ctx.fillStyle = 'rgba(50,25,5,0.4)'; path([[px + 40, py + ph + 10], [px + pw + 40, py + ph - 10], [px + pw + 150, py + ph + 70], [px + 110, py + ph + 100]]); ctx.fill(); ctx.restore(); }
  if (T.mode === 'line') hatch([[px + 40, py + ph + 14], [px + pw + 30, py + ph - 20], [px + pw + 150, py + ph + 60], [px + 120, py + ph + 100]], hexA(T.ink, 0.35), 10);
  path(body);
  ctx.fillStyle = T.mode === 'line' ? T.paper : T.mode === 'riso' ? hexA(T.b, 0.9) : T.mode === 'swiss' ? T.ink : '#2B2B30'; ctx.fill();
  if (T.mode === 'line') { ctx.strokeStyle = T.ink; ctx.lineWidth = 3; ctx.stroke(); }
  ctx.translate(px, py); ctx.transform(1, sk / pw, 0, 1, 0, 0);
  ctx.fillStyle = T.mode === 'riso' ? T.paper : '#FBFAF6'; ctx.beginPath(); ctx.roundRect(20, 22, pw - 40, ph - 30, 34); ctx.fill();
  if (T.mode === 'line') { ctx.strokeStyle = T.ink; ctx.lineWidth = 2; ctx.stroke(); }
  const blue = T.mode === 'riso' ? T.b : T.mode === 'swiss' ? T.ink : T.mode === 'line' ? T.ink : '#4D7CFF';
  ctx.fillStyle = '#1B1B22'; ctx.font = `700 30px ${FB}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText('AI 助手', pw / 2, 80);
  ctx.fillStyle = blue; ctx.beginPath(); ctx.roundRect(170, 160, 330, 70, 26); ctx.fill(); ctx.fillStyle = '#fff'; ctx.font = `500 34px ${FB}`; ctx.textAlign = 'left'; ctx.fillText('帮我写一句周末计划', 192, 196);
  ctx.fillStyle = '#FFFFFF'; ctx.beginPath(); ctx.roundRect(46, 280, 340, 96, 30); ctx.fill(); ctx.strokeStyle = 'rgba(0,0,0,0.2)'; ctx.lineWidth = 2; ctx.stroke();
  ctx.fillStyle = '#1B1B22'; ctx.font = `500 50px ${FB}`; ctx.fillText('周末我想', 70, 329);
  ctx.strokeStyle = T.key; ctx.lineWidth = 4; ctx.setLineDash([8, 6]); ctx.strokeRect(276, 300, 52, 58); ctx.setLineDash([]);
  ctx.fillStyle = 'rgba(0,0,0,0.07)'; ctx.beginPath(); ctx.roundRect(46, ph - 120, pw - 92, 60, 30); ctx.fill();
  ctx.restore();
  return [px + 302, py + 329 + 302 * sk / pw];
}

// ---------- 三个镜头（构图和第一轮一样，方便对比） ----------
function shot1() {
  background();
  CAM = { ox: 760, oy: 820, s: 70, a: 35 * Math.PI / 180, k: 0.55 };
  if (T.mode !== 'line' && T.mode !== 'swiss') blurred(8, () => { tok(1.6, 5, 0, '想'); tok(-8.4, 7, 0.2, '末'); });
  const [sx, sy] = phone(250, 560, 540, 700, 60);
  ctx.strokeStyle = T.key; ctx.lineWidth = 6; ctx.lineCap = 'round'; ctx.setLineDash([2, 16]);
  ctx.beginPath(); ctx.moveTo(sx, sy); ctx.quadraticCurveTo(sx + 40, sy - 160, sx + 150, sy - 210); ctx.stroke(); ctx.setLineDash([]);
  CAM = { ox: sx + 120, oy: sy - 170, s: 150, a: 35 * Math.PI / 180, k: 0.55 };
  tok(0, 0, 0, '去', 'key', 1);
  if (T.mode === 'wood') { CAM = { ox: 40, oy: 1720, s: 220, a: 35 * Math.PI / 180, k: 0.55 }; blurred(16, () => tok(0, 0, 0, '周')); }
  if (T.mode === 'line') dim(250, 1330, 790, 1300, '下一个字：还没写');
  title(['AI 为什么', '{一个字一个字}往外蹦？']);
  caption(['它不是在打字给你看']);
}
function shot2() {
  background();
  CAM = { ox: 100, oy: 1200, s: 80, a: 35 * Math.PI / 180, k: 0.6 };
  for (let k = 0; k < 5; k++) slab(2.2, 3.2, 1.0 + k * 0.9, 6, 4, k, k === 2 ? 0.9 : 0);
  [[2.2, 3.2], [8.0, 3.2]].forEach(([x, y]) => box(x, y, 0, 0.18, 0.18, 4.8, 'n', 5));
  const s = '周末我想去'; for (let i = 0; i < 5; i++) tok(0.2 + i * 1.15, 0, 0, s[i]);
  tok(0.2 + 5 * 1.15, 0, 0, '?', 'slot');
  ctx.strokeStyle = T.mode === 'riso' ? T.a : T.key; ctx.lineWidth = 5; ctx.setLineDash([12, 10]);
  ctx.beginPath(); const a0 = P(5.3, 0.3, 1.3), a1 = P(5.2, 4.2, 3.0); ctx.moveTo(a0[0], a0[1]); ctx.quadraticCurveTo(a0[0] + 120, a0[1] - 380, a1[0], a1[1]); ctx.stroke(); ctx.setLineDash([]);
  bead(5.6, 1.4, 2.4, 22);
  const lp = P(5.2, 3.2, 5.6); label('模型：一层一层', lp[0], lp[1] - 20, 32);
  if (T.mode === 'line') { const q0 = P(8.4, 3.2, 1.0), q1 = P(8.4, 3.2, 4.8); dim(q0[0] + 30, q0[1], q1[0] + 30, q1[1], '×几十层'); }
  if (T.mode === 'wood') { CAM = { ox: 860, oy: 1700, s: 190, a: 35 * Math.PI / 180, k: 0.6 }; blurred(16, () => tok(0, 0, 0, '末')); }
  caption(['每写一个字，', '都要把模型{从头到尾}过一遍']);
}
function shot3() {
  background();
  CAM = { ox: 40, oy: 1090, s: 62, a: 42 * Math.PI / 180, k: 1.25 };
  const band = pts => { path(pts.map(p => P(p[0], p[1], 0))); };
  const tracks = [[[0, -0.2], [5.6, -0.2], [5.6, 0.8], [0, 0.8]], [[5.4, -0.2], [6.8, -2.6], [12.6, -2.6], [12.6, -1.6], [7.3, -1.6], [6.0, 0.8]], [[5.4, -0.2], [6.8, 2.4], [12.6, 2.4], [12.6, 3.4], [7.3, 3.4], [6.0, 0.8]]];
  tracks.forEach(tr => {
    band(tr);
    if (T.mode === 'line') { ctx.strokeStyle = T.ink; ctx.lineWidth = 2; ctx.setLineDash([12, 8]); ctx.stroke(); ctx.setLineDash([]); }
    else if (T.mode === 'riso') { ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.fillStyle = dots(T.b, 0.15); ctx.fill(); ctx.restore(); }
    else if (T.mode === 'wood') { ctx.fillStyle = 'rgba(90,55,25,0.22)'; ctx.fill(); }
    else { ctx.fillStyle = 'rgba(17,17,17,0.1)'; ctx.fill(); }
  });
  const dn = '睡个懒觉'; for (let i = 0; i < dn.length; i++) tok(7.1 + i * 1.08, 2.5, 0, dn[i], i === 0 ? 'key' : 'n', 0.95);
  const s = '周末我想去'; for (let i = 0; i < 5; i++) tok(0.1 + i * 1.08, 0, 0, s[i], 'n', 0.95);
  const up = '海边看日落'; for (let i = 0; i < up.length; i++) tok(7.1 + i * 1.08, -2.5, 0, up[i], i === 0 ? 'key' : 'n', 0.95);
  const sp = P(5.9, 0.3, 2.0); ctx.fillStyle = T.mode === 'riso' ? T.a : T.key; ctx.beginPath(); ctx.arc(sp[0], sp[1], 40, 0, Math.PI * 2); ctx.fill(); ctx.fillStyle = '#FFFFFF'; ctx.font = `900 48px ${FB}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText('?', sp[0], sp[1] + 2);
  const p1 = P(9.4, -2.5, 0), p2 = P(9.4, 2.5, 1.2);
  label('→ 周末我想去海边看日落', 600, p1[1] + 70, 30); label('→ 周末我想去睡个懒觉', 640, p2[1] - 50, 30);
  caption(['这里选了「海」，', '后面是「边看日落」']);
}
function render() { ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.filter = 'none'; [shot1, shot2, shot3][SHOT - 1](); }
window.ready = Promise.all([document.fonts.load(`900 100px "Noto Serif CJK SC"`), document.fonts.load(`400 100px "Smiley Sans"`), document.fonts.load(`700 60px ${FB}`), document.fonts.load(`900 60px ${FB}`)]).then(() => { render(); return true; });
