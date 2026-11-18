'use strict';
// 风格样张：三套配色 × 三个镜头。用法：style.html?theme=A&shot=1
const W = 1080, H = 1920;
const cv = document.getElementById('c'); const ctx = cv.getContext('2d');
const Q = new URLSearchParams(location.search);
const THEMES = {
  // A 钴蓝海报：中明度饱和底，奶油色实体，柠檬黄 / 番茄红点睛，无辉光
  A: { name: '钴蓝海报', bg0: '#3349D6', bg1: '#2536B4', ground: '#2A3DC4', ink: '#0E1240', text: '#F5EEE2', face: '#F5EEE2', top: '#FFFBF3', side: '#C9BCA6',
       key: '#FFD23F', warn: '#FF5A3C', pos: '#8EC9FF', neg: '#FF9BB0', shadow: 'rgba(10,14,60,0.35)', cap: '#0E1240', capText: '#F5EEE2', serif: true },
  // B 奶油墨绿：浅暖底，深墨绿墨色，柿子橙 / 芥末黄
  B: { name: '奶油墨绿', bg0: '#F3EAD7', bg1: '#E9DDC3', ground: '#E6D8BC', ink: '#13392F', text: '#13392F', face: '#FFFDF7', top: '#FFFFFF', side: '#D9CBB0',
       key: '#E8A92B', warn: '#EE6433', pos: '#2F8C7A', neg: '#C9709E', shadow: 'rgba(19,57,47,0.22)', cap: '#13392F', capText: '#FFF8EC', serif: true },
  // C 墨绿哑光：深色但不霓虹、不发光；奶油实体，珊瑚 / 芥末
  C: { name: '墨绿哑光', bg0: '#16423A', bg1: '#0F2E28', ground: '#133B33', ink: '#0B231E', text: '#F3EAD8', face: '#F3EAD8', top: '#FFF8EA', side: '#B9AA8E',
       key: '#F2C14E', warn: '#FF7A50', pos: '#7CC6B0', neg: '#E89AA8', shadow: 'rgba(0,0,0,0.35)', cap: '#0B231E', capText: '#F3EAD8', serif: true },
};
const T = THEMES[Q.get('theme') || 'A'];
const SHOT = +(Q.get('shot') || 1);
const FT = '"Noto Serif CJK SC"', FB = '"Noto Sans CJK SC"', FM = '"DejaVu Sans Mono"', FS = '"Smiley Sans"';

function rnd(i) { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); }
function hexA(hex, a) { const n = parseInt(hex.slice(1), 16); return `rgba(${n >> 16},${(n >> 8) & 255},${n & 255},${a})`; }
function mix(h1, h2, u) { const a = parseInt(h1.slice(1), 16), b = parseInt(h2.slice(1), 16); const l = (p, q) => Math.round(p + (q - p) * u); return '#' + ((1 << 24) | (l(a >> 16, b >> 16) << 16) | (l((a >> 8) & 255, (b >> 8) & 255) << 8) | l(a & 255, b & 255)).toString(16).slice(1); }
function poly(pts, fill, stroke) { ctx.beginPath(); pts.forEach((p, i) => (i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1]))); ctx.closePath(); if (fill) { ctx.fillStyle = fill; ctx.fill(); } if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = 2; ctx.stroke(); } }

// ---------- 斜二测投影（正面不变形，字可读；深度往右上） ----------
let CAM = { ox: 0, oy: 0, s: 80, a: 35 * Math.PI / 180, k: 0.55 };
function P(x, y, z) { return [CAM.ox + x * CAM.s + y * CAM.s * CAM.k * Math.cos(CAM.a), CAM.oy - z * CAM.s - y * CAM.s * CAM.k * Math.sin(CAM.a)]; }
function box(x, y, z, w, d, h, c = {}) {
  const f = c.face || T.face, tp = c.top || T.top, sd = c.side || T.side;
  // 硬阴影：投在地面（z=0），往右下偏
  if (c.shadow !== false) {
    const sx = 0.35, sy = -0.25; const g = (X, Y) => P(X + sx * (z + h), Y + sy * (z + h), 0);
    ctx.save(); ctx.globalAlpha *= 1; poly([P(x, y, 0), P(x + w, y, 0), g(x + w, y + d), g(x + w, y), g(x, y)].slice(0, 0), null); ctx.restore();
    poly([P(x, y, 0), g(x, y), g(x + w, y), g(x + w, y + d), P(x + w, y + d, 0), P(x + w, y, 0)], T.shadow);
  }
  poly([P(x + w, y, z), P(x + w, y + d, z), P(x + w, y + d, z + h), P(x + w, y, z + h)], sd);               // 右侧
  poly([P(x, y, z + h), P(x + w, y, z + h), P(x + w, y + d, z + h), P(x, y + d, z + h)], tp);              // 顶
  poly([P(x, y, z), P(x + w, y, z), P(x + w, y, z + h), P(x, y, z + h)], f);                               // 正面
  if (c.edge) { ctx.strokeStyle = c.edge; ctx.lineWidth = 2; poly([P(x, y, z), P(x + w, y, z), P(x + w, y, z + h), P(x, y, z + h)], null, c.edge); }
}
// 字块：正面写字
function tok(x, y, z, ch, st = 'n', sc = 1) {
  const w = 1 * sc, h = 1.15 * sc, d = 0.55 * sc;
  let c = {};
  if (st === 'slot') c = { face: hexA(T.key, 0.25), top: hexA(T.key, 0.35), side: hexA(T.key, 0.2), shadow: false };
  if (st === 'key') c = { face: T.key, top: mix(T.key, '#FFFFFF', 0.4), side: mix(T.key, '#000000', 0.25) };
  box(x, y, z, w, d, h, c);
  if (st === 'slot') { ctx.setLineDash([10, 8]); poly([P(x, y, z), P(x + w, y, z), P(x + w, y, z + h), P(x, y, z + h)], null, T.key); ctx.setLineDash([]); }
  const p = P(x + w / 2, y, z + h / 2);
  ctx.fillStyle = st === 'slot' ? T.key : '#1B1B22'; ctx.font = `700 ${Math.round(CAM.s * 0.62 * sc)}px ${FB}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText(ch, p[0], p[1] + 2);
}
// 参数板：一块薄板，顶面铺粉蓝格子（这里用主题里的 pos / neg）
function slab(x, y, z, w, d, seed, lit = 0) {
  box(x, y, z, w, d, 0.22, { face: mix(T.ink, T.bg1, 0.3), top: mix(T.ink, T.bg1, 0.15), side: mix(T.ink, '#000000', 0.2) });
  const cols = 10, rows = 6, cw = w / cols, cd = d / rows;
  for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
    const v = rnd(seed * 31 + r * 13 + c * 7) * 2 - 1; const col = mix(mix(T.ink, '#000000', 0.1), v >= 0 ? T.pos : T.neg, 0.35 + 0.65 * Math.abs(v));
    const X = x + c * cw + 0.06, Y = y + r * cd + 0.06, Z = z + 0.221;
    poly([P(X, Y, Z), P(X + cw - 0.12, Y, Z), P(X + cw - 0.12, Y + cd - 0.12, Z), P(X, Y + cd - 0.12, Z)], lit ? mix(col, '#FFFFFF', lit * 0.5) : col);
  }
}
function bead(x, y, z, r, col) { // 实心小珠（代替辉光点）
  const p = P(x, y, z);
  ctx.fillStyle = T.shadow; ctx.beginPath(); ctx.ellipse(P(x + 0.3 * z, y - 0.2 * z, 0)[0], P(x + 0.3 * z, y - 0.2 * z, 0)[1], r * 1.1, r * 0.45, 0, 0, Math.PI * 2); ctx.fill();
  const g = ctx.createRadialGradient(p[0] - r * 0.35, p[1] - r * 0.35, r * 0.1, p[0], p[1], r);
  g.addColorStop(0, mix(col, '#FFFFFF', 0.6)); g.addColorStop(1, col); ctx.fillStyle = g; ctx.beginPath(); ctx.arc(p[0], p[1], r, 0, Math.PI * 2); ctx.fill();
}

// ---------- 底色 + 颗粒 ----------
const GRAIN = document.createElement('canvas'); GRAIN.width = GRAIN.height = 256;
(function () { const g = GRAIN.getContext('2d'); const id = g.createImageData(256, 256); for (let i = 0; i < id.data.length; i += 4) { const v = rnd(i * 0.37) * 255; id.data[i] = id.data[i + 1] = id.data[i + 2] = v; id.data[i + 3] = 22; } g.putImageData(id, 0, 0); })();
function background() {
  const g = ctx.createLinearGradient(0, 0, W * 0.3, H); g.addColorStop(0, T.bg0); g.addColorStop(1, T.bg1);
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  const v = ctx.createRadialGradient(W * 0.5, H * 0.45, H * 0.2, W * 0.5, H * 0.5, H * 0.75); v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(0,0,0,0.18)');
  ctx.fillStyle = v; ctx.fillRect(0, 0, W, H);
}
function grain() { ctx.save(); ctx.globalCompositeOperation = 'overlay'; ctx.fillStyle = ctx.createPattern(GRAIN, 'repeat'); ctx.fillRect(0, 0, W, H); ctx.restore(); }
function ground(y0) { // 一块地面，往远处变淡
  const g = ctx.createLinearGradient(0, y0 - 500, 0, y0 + 300); g.addColorStop(0, hexA(T.ground, 0)); g.addColorStop(1, T.ground);
  ctx.fillStyle = g; ctx.fillRect(0, y0 - 500, W, 800);
}
// 景深：前景虚化的块
function blurred(px, fn) { ctx.save(); ctx.filter = `blur(${px}px)`; fn(); ctx.restore(); }

// ---------- 文字 ----------
function title(lines, y0, size, lh) {
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  lines.forEach((l, i) => {
    const parts = l.split(/(\{[^}]*\})/).filter(Boolean); ctx.font = `900 ${size}px ${FT}`;
    let tw = 0; parts.forEach(p => { tw += ctx.measureText(p.replace(/[{}]/g, '')).width; }); let x = W / 2 - tw / 2;
    parts.forEach(p => { const hi = p[0] === '{'; const s = p.replace(/[{}]/g, ''); ctx.fillStyle = hi ? T.key : T.text; ctx.textAlign = 'left'; ctx.fillText(s, x, y0 + i * lh); x += ctx.measureText(s).width; });
  });
}
function caption(lines) {
  ctx.font = `900 60px ${FB}`; const lh = 80; let mw = 0; lines.forEach(l => { mw = Math.max(mw, ctx.measureText(l.replace(/[{}]/g, '')).width); });
  const bw = mw + 64, bh = lines.length * lh + 36, y = 1480;
  ctx.fillStyle = hexA(T.cap, 0.9); ctx.beginPath(); ctx.roundRect(W / 2 - bw / 2, y - bh / 2, bw, bh, 14); ctx.fill();
  // 左侧色条：系列标识
  ctx.fillStyle = T.key; ctx.fillRect(W / 2 - bw / 2, y - bh / 2, 10, bh);
  lines.forEach((l, i) => {
    const parts = l.split(/(\{[^}]*\})/).filter(Boolean); let tw = 0; parts.forEach(p => { tw += ctx.measureText(p.replace(/[{}]/g, '')).width; });
    let x = W / 2 - tw / 2; const yy = y - ((lines.length - 1) * lh) / 2 + i * lh;
    parts.forEach(p => { const hi = p[0] === '{'; const s = p.replace(/[{}]/g, ''); ctx.fillStyle = hi ? T.key : T.capText; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.fillText(s, x, yy); x += ctx.measureText(s).width; });
  });
}
function label(txt, x, y, size = 30) { ctx.font = `700 ${size}px ${FB}`; ctx.fillStyle = hexA(T.text, 0.8); ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(txt, x, y); }

// ---------- 镜头 1：开头（手机斜放，下一个字从屏幕的空位里「蹦」出来，变成字块飞向镜头） ----------
function shot1() {
  background(); ground(1300);
  CAM = { ox: 760, oy: 820, s: 70, a: 35 * Math.PI / 180, k: 0.55 };
  blurred(8, () => { tok(1.6, 5, 0, '想', 'n'); tok(-8.4, 7, 0.2, '末', 'n'); });
  const px = 250, py = 560, pw = 540, ph = 700, sk = 60;
  // 阴影 + 机身厚度 + 机身
  ctx.fillStyle = T.shadow; ctx.beginPath(); ctx.moveTo(px + 40, py + ph + 14); ctx.lineTo(px + pw + 30, py + ph - 20); ctx.lineTo(px + pw + 150, py + ph + 60); ctx.lineTo(px + 120, py + ph + 100); ctx.fill();
  ctx.fillStyle = mix(T.ink, '#000000', 0.25); ctx.beginPath(); ctx.moveTo(px + pw, py + sk); ctx.lineTo(px + pw + 26, py + sk + 14); ctx.lineTo(px + pw + 26, py + ph + 10); ctx.lineTo(px + pw, py + ph - 4); ctx.fill();
  ctx.fillStyle = T.ink; ctx.beginPath(); ctx.moveTo(px, py); ctx.lineTo(px + pw, py + sk); ctx.lineTo(px + pw, py + ph - 4); ctx.lineTo(px, py + ph + 30); ctx.closePath(); ctx.fill();
  ctx.save(); ctx.translate(px, py); ctx.transform(1, sk / pw, 0, 1, 0, 0);
  ctx.fillStyle = '#FBF8F1'; ctx.beginPath(); ctx.roundRect(20, 22, pw - 40, ph - 30, 34); ctx.fill();
  ctx.fillStyle = '#1B1B22'; ctx.font = `700 30px ${FB}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText('AI 助手', pw / 2, 80);
  ctx.fillStyle = 'rgba(0,0,0,0.08)'; ctx.fillRect(20, 112, pw - 40, 2);
  ctx.fillStyle = '#4D7CFF'; ctx.beginPath(); ctx.roundRect(170, 160, 330, 70, 26); ctx.fill(); ctx.fillStyle = '#fff'; ctx.font = `500 34px ${FB}`; ctx.textAlign = 'left'; ctx.fillText('帮我写一句周末计划', 192, 196);
  ctx.fillStyle = '#FFFFFF'; ctx.beginPath(); ctx.roundRect(46, 280, 340, 96, 30); ctx.fill(); ctx.strokeStyle = 'rgba(0,0,0,0.08)'; ctx.lineWidth = 2; ctx.stroke();
  ctx.fillStyle = '#1B1B22'; ctx.font = `500 50px ${FB}`; ctx.fillText('周末我想', 70, 329);
  ctx.strokeStyle = T.key; ctx.lineWidth = 4; ctx.setLineDash([8, 6]); ctx.strokeRect(276, 300, 52, 58); ctx.setLineDash([]);
  ctx.fillStyle = '#DDE2EE'; ctx.beginPath(); ctx.roundRect(46, ph - 120, pw - 92, 60, 30); ctx.fill();
  ctx.restore();
  const sx = px + 302, sy = py + 329 + 302 * sk / pw;  // 空位在屏幕上的位置
  // 飞出的轨迹
  ctx.strokeStyle = hexA(T.key, 0.9); ctx.lineWidth = 6; ctx.lineCap = 'round'; ctx.setLineDash([2, 16]);
  ctx.beginPath(); ctx.moveTo(sx, sy); ctx.quadraticCurveTo(sx + 40, sy - 160, sx + 150, sy - 210); ctx.stroke(); ctx.setLineDash([]);
  CAM = { ox: sx + 120, oy: sy - 170, s: 150, a: 35 * Math.PI / 180, k: 0.55 };
  tok(0, 0, 0, '去', 'key', 1);
  CAM = { ox: 40, oy: 1720, s: 220, a: 35 * Math.PI / 180, k: 0.55 };
  blurred(16, () => tok(0, 0, 0, '周', 'n'));
  title(['AI 为什么', '{一个字一个字}往外蹦？'], 230, 96, 128);
  caption(['它不是在打字给你看']);
  grain();
}

// ---------- 镜头 2：模型（一摞参数板，字块排在桌上，新字化成小珠滚进模型） ----------
function shot2() {
  background(); ground(1300);
  CAM = { ox: 100, oy: 1200, s: 80, a: 35 * Math.PI / 180, k: 0.6 };
  // 远处：模型的一摞板
  for (let k = 0; k < 5; k++) slab(2.2, 3.2, 1.0 + k * 0.9, 6, 4, k, k === 2 ? 0.9 : 0);
  // 板间的支柱
  [[2.2, 3.2], [8.0, 3.2]].forEach(([x, y]) => box(x, y, 0, 0.18, 0.18, 4.8, { face: mix(T.ink, T.bg1, 0.2), top: T.ink, side: mix(T.ink, '#000', 0.3) }));
  // 近处：一排字块
  const s = '周末我想去';
  for (let i = 0; i < 5; i++) tok(0.2 + i * 1.15, 0, 0, s[i], 'n');
  tok(0.2 + 5 * 1.15, 0, 0, '?', 'slot');
  // 存档书签：旧字顶上的小旗
  for (let i = 0; i < 4; i++) { const p = P(0.2 + i * 1.15 + 0.8, 0.3, 1.15); ctx.fillStyle = T.pos; ctx.beginPath(); ctx.moveTo(p[0], p[1]); ctx.lineTo(p[0], p[1] - 34); ctx.lineTo(p[0] + 22, p[1] - 26); ctx.lineTo(p[0], p[1] - 18); ctx.fill(); }
  // 新字化成小珠，沿弧线滚进模型
  ctx.strokeStyle = hexA(T.key, 0.7); ctx.lineWidth = 5; ctx.setLineDash([12, 10]);
  ctx.beginPath(); const a0 = P(4.8 + 0.5, 0.3, 1.3), a1 = P(5.2, 4.2, 3.0); ctx.moveTo(a0[0], a0[1]); ctx.quadraticCurveTo(a0[0] + 120, a0[1] - 380, a1[0], a1[1]); ctx.stroke(); ctx.setLineDash([]);
  bead(5.6, 1.4, 2.4, 22, T.key);
  // 标签（贴在物体旁边）
  const lp = P(5.2, 3.2, 5.6); label('模型：一层一层', lp[0], lp[1] - 20, 32);
  const kp = P(5.4, 0, 1.6); ctx.fillStyle = T.key; ctx.font = `700 30px ${FB}`; ctx.textAlign = 'center'; ctx.fillText('只送新字', kp[0], kp[1] - 30);
  // 前景虚化
  CAM = { ox: 860, oy: 1700, s: 190, a: 35 * Math.PI / 180, k: 0.6 };
  blurred(16, () => tok(0, 0, 0, '末', 'n'));
  caption(['每写一个字，', '都要把模型{从头到尾}过一遍']);
  grain();
}

// ---------- 镜头 3：分叉（一条轨道在「去」后面分成两条，像铁路道岔） ----------
function shot3() {
  background(); ground(1350);
  CAM = { ox: 40, oy: 1090, s: 62, a: 42 * Math.PI / 180, k: 1.25 };
  const band = (pts, col) => { ctx.fillStyle = col; ctx.beginPath(); pts.forEach((p, i) => { const q = P(p[0], p[1], 0); i ? ctx.lineTo(q[0], q[1]) : ctx.moveTo(q[0], q[1]); }); ctx.closePath(); ctx.fill(); };
  const tr = hexA(T.ink, 0.3);
  band([[0, -0.2], [5.6, -0.2], [5.6, 0.8], [0, 0.8]], tr);
  band([[5.4, -0.2], [6.8, -2.6], [12.6, -2.6], [12.6, -1.6], [7.3, -1.6], [6.0, 0.8]], tr);
  band([[5.4, -0.2], [6.8, 2.4], [12.6, 2.4], [12.6, 3.4], [7.3, 3.4], [6.0, 0.8]], tr);
  // 远的先画
  const dn = '睡个懒觉'; for (let i = 0; i < dn.length; i++) tok(7.1 + i * 1.08, 2.5, 0, dn[i], i === 0 ? 'key' : 'n', 0.95);
  const s = '周末我想去'; for (let i = 0; i < 5; i++) tok(0.1 + i * 1.08, 0, 0, s[i], 'n', 0.95);
  const up = '海边看日落'; for (let i = 0; i < up.length; i++) tok(7.1 + i * 1.08, -2.5, 0, up[i], i === 0 ? 'key' : 'n', 0.95);
  const sp = P(5.9, 0.3, 2.0); ctx.fillStyle = T.key; ctx.beginPath(); ctx.arc(sp[0], sp[1], 40, 0, Math.PI * 2); ctx.fill(); ctx.fillStyle = T.ink; ctx.font = `900 48px ${FB}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText('?', sp[0], sp[1] + 2);
  const p1 = P(9.4, -2.5, 0), p2 = P(9.4, 2.5, 1.2);
  label('→ 周末我想去海边看日落', 600, p1[1] + 70, 30); label('→ 周末我想去睡个懒觉', 640, p2[1] - 50, 30);
  caption(['这里选了「海」，', '后面是「边看日落」']);
  grain();
}

function render() { ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.filter = 'none'; [shot1, shot2, shot3][SHOT - 1](); }
window.ready = Promise.all([document.fonts.load(`900 100px ${FT}`), document.fonts.load(`700 60px ${FB}`), document.fonts.load(`900 60px ${FB}`)]).then(() => { render(); return true; });
