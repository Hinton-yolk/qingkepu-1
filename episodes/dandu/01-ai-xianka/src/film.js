'use strict';
// AI 为什么非要用显卡？ 60 秒竖屏动画。render(t) 是纯函数：给定秒数画一帧。
const W = 1080, H = 1920, DUR = 60;
const cv = document.getElementById('c');
const ctx = cv.getContext('2d');

const C = {
  cpu: '#FF9A3C', cpuL: '#FFC98A', gpu: '#3DF5B0', gpuL: '#B8FFE4', gpuD: '#1A5546',
  num: '#8FE3FF', hi: '#FFD84A', pink: '#FF5C8A', blue: '#4D8DFF', white: '#F4F6FF',
  mute: '#A6ACD3', cache: '#6F86C9', ink: '#0B0E22',
};
const FT = '"Smiley Sans"', FB = '"Noto Sans CJK SC"', FM = '"DejaVu Sans Mono"';

// ---------- utils ----------
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, u) => a + (b - a) * u;
const seg = (t, a, b) => clamp((t - a) / (b - a));
const eo = u => 1 - Math.pow(1 - u, 3);
const ei = u => u * u * u;
const eio = u => (u < 0.5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2);
const back = u => { const c1 = 1.9, c3 = c1 + 1; return 1 + c3 * Math.pow(u - 1, 3) + c1 * Math.pow(u - 1, 2); };
const win = (t, a, b, fi = 0.25, fo = 0.25) => seg(t, a, a + fi) * (1 - seg(t, b - fo, b));
function rnd(i) { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); }
function rr(x, y, w, h, r) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); }
function hexA(hex, a) {
  const n = parseInt(hex.slice(1), 16);
  return `rgba(${n >> 16},${(n >> 8) & 255},${n & 255},${a})`;
}
function mix(h1, h2, u) {
  const a = parseInt(h1.slice(1), 16), b = parseInt(h2.slice(1), 16);
  const r = Math.round(lerp(a >> 16, b >> 16, u)), g = Math.round(lerp((a >> 8) & 255, (b >> 8) & 255, u)), bl = Math.round(lerp(a & 255, b & 255, u));
  return '#' + ((1 << 24) | (r << 16) | (g << 8) | bl).toString(16).slice(1);
}
function glowDot(x, y, r, col, a = 1) {
  const g = ctx.createRadialGradient(x, y, 0, x, y, r);
  g.addColorStop(0, hexA(col, a)); g.addColorStop(0.35, hexA(col, a * 0.45)); g.addColorStop(1, hexA(col, 0));
  ctx.fillStyle = g; ctx.fillRect(x - r, y - r, 2 * r, 2 * r);
}
function fmtInt(n) { return Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ','); }

// ---------- 数据 ----------
const VEC = [0.21, -1.3, 0.87, 0.05, -0.42, 1.1, -0.66, 0.38];
const WM = []; for (let r = 0; r < 5; r++) { WM.push([]); for (let c = 0; c < 8; c++) WM[r].push(Math.round((rnd(r * 8 + c + 50) * 2 - 1) * 10) / 10); }
const OUT = [2.7, 1.4, 0.6, -0.3, -1.2];
const CAND = [['光', 62], ['亮', 18], ['财', 9], ['呆', 3], ['…', 8]];
const AI_TXT = '你今天也闪闪发光';
function wColor(w) {
  const base = '#1A1F3A';
  return mix(base, w >= 0 ? '#3BA9FF' : '#FF5C8A', 0.3 + 0.7 * Math.abs(w));
}

// 格子海纹理：1024×1024，每个像素 = 一道乘法；中间 8×5 和数字表一致
const TEX = document.createElement('canvas'); TEX.width = TEX.height = 1024;
(function buildTex() {
  const g = TEX.getContext('2d'); const id = g.createImageData(1024, 1024); const d = id.data;
  const pos = [59, 169, 255], neg = [255, 92, 138], base = [26, 31, 58];
  for (let y = 0; y < 1024; y++) for (let x = 0; x < 1024; x++) {
    let w;
    const gx = x - 508, gy = y - 510;
    if (gx >= 0 && gx < 8 && gy >= 0 && gy < 5) w = WM[gy][gx];
    else { const h = Math.sin(x * 12.9898 + y * 78.233) * 43758.5453; w = (h - Math.floor(h)) * 2 - 1; }
    const tgt = w >= 0 ? pos : neg, u = 0.3 + 0.7 * Math.abs(w), i = (y * 1024 + x) * 4;
    d[i] = base[0] + (tgt[0] - base[0]) * u; d[i + 1] = base[1] + (tgt[1] - base[1]) * u; d[i + 2] = base[2] + (tgt[2] - base[2]) * u; d[i + 3] = 255;
  }
  g.putImageData(id, 0, 0);
})();

// ---------- 背景 ----------
function bg(t) {
  const g = ctx.createLinearGradient(0, 0, 0, H);
  g.addColorStop(0, '#0C0F26'); g.addColorStop(0.5, '#141034'); g.addColorStop(1, '#090B1C');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  const blobs = [[0.18, 0.22, '#5A46FF', 0.26, 560], [0.88, 0.52, '#28C8AA', 0.14, 620], [0.25, 0.86, '#FF7850', 0.11, 560]];
  blobs.forEach((b, i) => {
    const x = W * b[0] + Math.sin(t * 0.31 + i * 2.1) * 90, y = H * b[1] + Math.cos(t * 0.27 + i) * 100;
    const rg = ctx.createRadialGradient(x, y, 0, x, y, b[4]);
    rg.addColorStop(0, hexA(b[2], b[3])); rg.addColorStop(1, hexA(b[2], 0));
    ctx.fillStyle = rg; ctx.fillRect(0, 0, W, H);
  });
  ctx.fillStyle = 'rgba(150,160,255,0.09)';
  const sp = 54, oy = (t * 16) % sp;
  for (let y = -sp + oy; y < H; y += sp) for (let x = 27; x < W; x += sp) ctx.fillRect(x - 1.5, y - 1.5, 3, 3);
  for (let i = 0; i < 46; i++) {
    const x = (rnd(i) * W + t * (6 + rnd(i + 9) * 18)) % W;
    const y = ((rnd(i + 3) * H - t * (14 + rnd(i + 5) * 26)) % H + H) % H;
    const a = 0.25 + 0.35 * Math.sin(t * 1.3 + i);
    ctx.fillStyle = `rgba(200,210,255,${a * 0.5})`; ctx.fillRect(x, y, 2.2, 2.2);
  }
  const v = ctx.createRadialGradient(W / 2, H / 2, H * 0.3, W / 2, H / 2, H * 0.75);
  v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(0,0,8,0.55)');
  ctx.fillStyle = v; ctx.fillRect(0, 0, W, H);
}

// ---------- 文字 ----------
function parseRich(s) { return s.split(/(\{[^}]*\})/).filter(Boolean).map(p => p[0] === '{' ? { t: p.slice(1, -1), h: 1 } : { t: p, h: 0 }); }
function richLine(str, x, y, size, font, col, hcol, weight = 700) {
  ctx.font = `${weight} ${size}px ${font}`;
  const parts = parseRich(str); let tw = 0; parts.forEach(p => { p.w = ctx.measureText(p.t).width; tw += p.w; });
  let cx = x - tw / 2; ctx.textAlign = 'left'; ctx.textBaseline = 'middle';
  parts.forEach(p => { ctx.fillStyle = p.h ? hcol : col; ctx.fillText(p.t, cx, y); cx += p.w; });
  return tw;
}
function measureRich(str, size, font, weight = 700) {
  ctx.font = `${weight} ${size}px ${font}`; return parseRich(str).reduce((s, p) => s + ctx.measureText(p.t).width, 0);
}

const CAPS = [
  [0.0, 2.6, 'AI 说话，其实在做{乘法}'],
  [3.1, 5.4, '它先把字，变成{一串数字}'],
  [5.4, 8.3, '再和一张数字表\n{乘一乘、加起来}'],
  [8.3, 10.3, '算出下一个字：{光}'],
  [10.4, 13.1, '说一个字，要做约 {70 亿次}'],
  [13.2, 15.6, '交给 CPU：几位{数学教授}', '类比'],
  [15.6, 18.3, '什么难题都会，可{人太少}'],
  [18.3, 20.9, '题太多，只能{排长队}'],
  [21.4, 24.0, '换成 GPU：{上万个小学生}', '类比'],
  [24.0, 26.3, '只会口算，但{一起动手}'],
  [26.4, 28.2, 'CPU：大半用来{“想”和“记”}'],
  [28.2, 30.0, 'GPU：更多用来{“算”}'],
  [30.0, 33.4, '能一起算，是因为\n这些乘法{谁也不用等谁}'],
  [33.4, 37.1, '要是一步等一步，\n{人再多也没用}'],
  [37.2, 40.2, '其实，显卡本来是\n{打游戏}用的'],
  [40.2, 43.4, '4K 屏上 800 多万个像素\n{各算各的}颜色'],
  [43.6, 45.7, '2012 年，有人用两块游戏显卡'],
  [45.7, 48.0, '训练出的 AI，认图{一战成名}'],
  [50.6, 53.6, '教授再聪明，人也太少'],
  [53.6, 57.0, '上万个小学生{一起开工}\n才是 AI 要的'],
];
const NOTES = [
  [3.6, 8.2, '示意：实际每个字会变成几千个数，这里只画 8 个'],
  [8.3, 10.3, '示意：实际要一层接一层算几十层，这里只画一层'],
  [10.6, 13.1, '估算：按 70 亿参数的模型\n每说一个字（token）约 70 亿次乘加'],
  [15.7, 20.9, '慢放示意：真实 CPU 一秒能算上千亿次乘加\n同样的活，显卡快几十到上百倍（两段同样慢放）'],
  [21.6, 24.0, 'RTX 4090 有 16384 个 CUDA 核心，全画了（排布示意）'],
  [24.0, 26.3, 'GPU 的“核”比 CPU 的核简单得多（同样慢放）'],
  [26.4, 30.0, '示意：面积比例不精确'],
  [33.4, 37.1, '一步接一步的活，CPU 更拿手\nAI 也要一层等一层，但每层里的乘法能同时算'],
  [40.2, 43.4, '4K 屏 3840×2160 ≈ 829 万像素，每一帧都要算'],
  [43.6, 48.0, 'AlexNet：2012 年 ImageNet 图像识别比赛冠军\n猫图为示意'],
];
const CAP_Y = 1480, CAP_SIZE = 60, CAP_LH = 80;
function captionTop(t) {
  for (const c of CAPS) if (t >= c[0] && t < c[1]) { const n = c[2].split('\n').length; return CAP_Y - (n * CAP_LH) / 2 - 26; }
  return CAP_Y - 66;
}
function drawCaptions(t) {
  for (const c of CAPS) {
    const [t0, t1, txt, tag] = c; if (t < t0 - 0.01 || t > t1) continue;
    const ui = t0 < 0.05 ? 1 : eo(seg(t, t0, t0 + 0.2)), uo = seg(t, t1 - 0.14, t1);
    const a = ui * (1 - uo); if (a <= 0) continue;
    const lines = txt.split('\n');
    let mw = 0; lines.forEach(l => { mw = Math.max(mw, measureRich(l, CAP_SIZE, FB, 900)); });
    const tagW = tag ? 96 : 0;
    const bw = mw + 64 + tagW, bh = lines.length * CAP_LH + 36;
    ctx.save(); ctx.globalAlpha = a;
    const s = lerp(0.92, 1, ui); ctx.translate(W / 2, CAP_Y + (1 - ui) * 16); ctx.scale(s, s);
    ctx.fillStyle = 'rgba(8,9,26,0.72)'; rr(-bw / 2, -bh / 2, bw, bh, 30); ctx.fill();
    ctx.strokeStyle = 'rgba(255,255,255,0.10)'; ctx.lineWidth = 2; ctx.stroke();
    lines.forEach((l, i) => {
      const y = -((lines.length - 1) * CAP_LH) / 2 + i * CAP_LH;
      ctx.shadowColor = 'rgba(0,0,0,0.6)'; ctx.shadowBlur = 8;
      richLine(l, -tagW / 2, y, CAP_SIZE, FB, C.white, C.hi, 900);
      ctx.shadowBlur = 0;
    });
    if (tag) {
      const x = bw / 2 - tagW - 10, y = -24;
      ctx.strokeStyle = C.cpuL; ctx.lineWidth = 2.5; rr(x, y, 80, 48, 12); ctx.stroke();
      ctx.fillStyle = C.cpuL; ctx.font = `700 28px ${FB}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(tag, x + 40, y + 25);
    }
    ctx.restore();
  }
}
function drawNotes(t) {
  for (const n of NOTES) {
    const [t0, t1, txt] = n; if (t < t0 || t > t1) continue;
    const a = win(t, t0, t1, 0.25, 0.15); const lines = txt.split('\n');
    const top = captionTop(t) - 22;
    ctx.save(); ctx.globalAlpha = a; ctx.font = `500 32px ${FB}`; ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
    lines.forEach((l, i) => {
      const y = top - (lines.length - 1 - i) * 44;
      const w = ctx.measureText(l).width;
      ctx.fillStyle = 'rgba(8,9,26,0.7)'; rr(W / 2 - w / 2 - 14, y - 33, w + 28, 44, 10); ctx.fill();
      ctx.fillStyle = '#C9CDEB'; ctx.fillText(l, W / 2, y);
    });
    ctx.restore();
  }
}
function bigTitle(lines, y0, a, opt = {}) {
  if (a <= 0) return;
  ctx.save(); ctx.globalAlpha = a; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  const size = opt.size || 140, lh = opt.lh || 150;
  lines.forEach((l, i) => {
    const y = y0 + i * lh;
    ctx.save(); ctx.translate(W / 2, y); const sc = opt.scale ? opt.scale[i] || 1 : 1; ctx.scale(sc, sc);
    ctx.shadowColor = 'rgba(80,60,255,0.55)'; ctx.shadowBlur = 40;
    richLine(l, 0, 0, size, FT, C.white, C.hi, 400);
    ctx.shadowBlur = 0; ctx.restore();
  });
  ctx.restore();
}

// ---------- 手机 ----------
const PH = { w: 500, h: 640, sw: 472, sh: 612, tx: -136, ty: -14, cw: 38 };
function slotLocal(n) { return { x: PH.tx + n * PH.cw + PH.cw / 2, y: PH.ty }; }
function drawPhone(cx, cy, s, n, t, opt = {}) {
  ctx.save(); ctx.translate(cx, cy); ctx.scale(s, s);
  const { w, h, sw, sh } = PH;
  ctx.fillStyle = 'rgba(0,0,0,0.4)'; rr(-w / 2 + 16, -h / 2 + 26, w, h, 64); ctx.fill();
  const bgr = ctx.createLinearGradient(-w / 2, -h / 2, w / 2, h / 2); bgr.addColorStop(0, '#4A5075'); bgr.addColorStop(1, '#1A1D2E');
  ctx.fillStyle = bgr; rr(-w / 2, -h / 2, w, h, 62); ctx.fill();
  const sg = ctx.createLinearGradient(0, -sh / 2, 0, sh / 2); sg.addColorStop(0, '#FAFBFF'); sg.addColorStop(1, '#E9EDF8');
  ctx.fillStyle = sg; rr(-sw / 2, -sh / 2, sw, sh, 50); ctx.fill();
  ctx.fillStyle = '#0E0F18'; rr(-58, -sh / 2 + 16, 116, 32, 16); ctx.fill();
  ctx.fillStyle = '#1B1E2E'; ctx.font = `700 30px ${FB}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText('AI 助手', 0, -sh / 2 + 92);
  ctx.fillStyle = 'rgba(30,35,60,0.08)'; ctx.fillRect(-sw / 2, -sh / 2 + 124, sw, 2);
  // user bubble
  ctx.font = `500 32px ${FB}`; const ut = '用一句话夸夸我'; const uw = ctx.measureText(ut).width + 48;
  ctx.fillStyle = '#4D7CFF'; rr(212 - uw, -150, uw, 64, 26); ctx.fill();
  ctx.fillStyle = '#fff'; ctx.textAlign = 'left'; ctx.fillText(ut, 212 - uw + 24, -117);
  // avatar
  const ag = ctx.createLinearGradient(-220, -40, -172, 8); ag.addColorStop(0, '#7B5CFF'); ag.addColorStop(1, '#3DF5B0');
  ctx.fillStyle = ag; ctx.beginPath(); ctx.arc(-196, -14, 24, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = '#fff'; ctx.font = `700 26px ${FB}`; ctx.textAlign = 'center'; ctx.fillText('✦', -196, -13);
  // AI bubble
  const shown = Math.min(n, AI_TXT.length), slot = shown < AI_TXT.length && opt.slot !== false;
  const bwid = 48 + (shown + (slot ? 1 : 0)) * PH.cw;
  ctx.fillStyle = '#FFFFFF'; rr(-160, -54, bwid, 80, 26); ctx.fill();
  ctx.strokeStyle = 'rgba(30,35,60,0.10)'; ctx.lineWidth = 2; ctx.stroke();
  ctx.font = `500 ${PH.cw}px ${FB}`; ctx.textAlign = 'center';
  for (let i = 0; i < shown; i++) {
    const isLast = opt.goldLast && i === AI_TXT.length - 1;
    ctx.fillStyle = isLast ? '#E0A400' : '#1B1E2E';
    ctx.fillText(AI_TXT[i], PH.tx + i * PH.cw + PH.cw / 2, PH.ty);
  }
  if (slot) {
    const p = slotLocal(shown); const pulse = 0.5 + 0.5 * Math.sin(t * 10);
    ctx.fillStyle = hexA(C.hi, 0.25 + 0.25 * pulse); rr(p.x - 17, p.y - 22, 34, 44, 8); ctx.fill();
    ctx.strokeStyle = hexA('#E0A400', 0.9); ctx.lineWidth = 3; ctx.stroke();
    if (Math.floor(t * 3) % 2 === 0) { ctx.fillStyle = '#1B1E2E'; ctx.fillRect(p.x - 2, p.y - 16, 4, 32); }
  }
  // input bar
  ctx.fillStyle = '#DDE2F0'; rr(-206, 226, 360, 58, 29); ctx.fill();
  ctx.fillStyle = '#8A90AE'; ctx.font = `400 26px ${FB}`; ctx.textAlign = 'left'; ctx.fillText('发消息…', -178, 256);
  ctx.fillStyle = '#4D7CFF'; ctx.beginPath(); ctx.arc(196, 255, 29, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.moveTo(184, 268); ctx.lineTo(210, 255); ctx.lineTo(184, 242); ctx.lineTo(189, 255); ctx.fill();
  ctx.restore();
}

// ---------- 显卡 ----------
function drawFan(x, y, r, a, light) {
  ctx.save(); ctx.translate(x, y);
  ctx.fillStyle = '#0D0F1A'; ctx.beginPath(); ctx.arc(0, 0, r, 0, Math.PI * 2); ctx.fill();
  ctx.strokeStyle = hexA(C.gpu, 0.35 + 0.4 * light); ctx.lineWidth = 3; ctx.beginPath(); ctx.arc(0, 0, r - 3, 0, Math.PI * 2); ctx.stroke();
  const blur = ctx.createRadialGradient(0, 0, r * 0.2, 0, 0, r * 0.95);
  blur.addColorStop(0, 'rgba(120,130,170,0.25)'); blur.addColorStop(1, 'rgba(120,130,170,0.05)');
  ctx.fillStyle = blur; ctx.beginPath(); ctx.arc(0, 0, r * 0.95, 0, Math.PI * 2); ctx.fill();
  ctx.rotate(a);
  for (let k = 0; k < 9; k++) {
    ctx.save(); ctx.rotate((k * Math.PI * 2) / 9);
    ctx.fillStyle = 'rgba(120,128,165,0.75)';
    ctx.beginPath(); ctx.moveTo(r * 0.22, -4); ctx.quadraticCurveTo(r * 0.6, -r * 0.32, r * 0.9, -r * 0.12);
    ctx.quadraticCurveTo(r * 0.62, r * 0.02, r * 0.22, 8); ctx.closePath(); ctx.fill();
    ctx.restore();
  }
  ctx.fillStyle = '#222538'; ctx.beginPath(); ctx.arc(0, 0, r * 0.24, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = hexA(C.gpu, 0.5 + 0.5 * light); ctx.beginPath(); ctx.arc(0, 0, r * 0.08, 0, Math.PI * 2); ctx.fill();
  ctx.restore();
}
function drawCard(cx, cy, s, t, opt = {}) {
  const w = 760, h = 190, light = opt.light || 0, al = opt.alpha == null ? 1 : opt.alpha;
  if (al <= 0) return;
  ctx.save(); ctx.globalAlpha = al; ctx.translate(cx, cy); ctx.scale(s, s);
  // bracket
  const bk = ctx.createLinearGradient(-w / 2 - 30, 0, -w / 2, 0); bk.addColorStop(0, '#9AA1B5'); bk.addColorStop(1, '#D5DAE6');
  ctx.fillStyle = bk; ctx.fillRect(-w / 2 - 28, -h / 2 - 6, 26, h + 40);
  ctx.fillStyle = '#2A2E40'; for (let i = 0; i < 3; i++) ctx.fillRect(-w / 2 - 22, -h / 2 + 16 + i * 52, 14, 34);
  // PCB + gold fingers
  ctx.fillStyle = '#143428'; ctx.fillRect(-w / 2 + 6, h / 2 - 10, w - 40, 30);
  ctx.fillStyle = '#E3B341'; for (let i = 0; i < 34; i++) ctx.fillRect(-150 + i * 9, h / 2 + 10, 6, 14);
  // shroud
  const sa = opt.shroud == null ? 1 : opt.shroud;
  ctx.globalAlpha = al * sa;
  const sg = ctx.createLinearGradient(0, -h / 2, 0, h / 2); sg.addColorStop(0, '#41465F'); sg.addColorStop(0.5, '#2A2E43'); sg.addColorStop(1, '#1B1E2D');
  ctx.fillStyle = sg; rr(-w / 2, -h / 2, w, h, 26); ctx.fill();
  ctx.strokeStyle = 'rgba(255,255,255,0.12)'; ctx.lineWidth = 2; ctx.stroke();
  ctx.strokeStyle = 'rgba(255,255,255,0.06)'; ctx.lineWidth = 6;
  for (let i = 0; i < 6; i++) { ctx.beginPath(); ctx.moveTo(-w / 2 + 20 + i * 140, h / 2 - 8); ctx.lineTo(-w / 2 + 80 + i * 140, -h / 2 + 8); ctx.stroke(); }
  [-250, 0, 250].forEach((x, i) => drawFan(x, 6, 80, t * (9 + i * 0.7) + i, light));
  // LED strip
  ctx.fillStyle = hexA(C.gpu, 0.45 + 0.55 * light); rr(-w / 2 + 40, -h / 2 + 7, w - 80, 7, 4); ctx.fill();
  ctx.restore();
  if (light > 0.02) { ctx.save(); ctx.globalAlpha = al * light * sa; glowDot(cx, cy - (h / 2 - 10) * s, 420 * s, C.gpu, 0.35); ctx.restore(); }
}

// ---------- CPU ----------
// 本地坐标：die 480×480，中心 0,0。cores 4 列 × 2 行
function cpuCoreRect(i) { const c = i % 4, r = Math.floor(i / 4); return { x: -229 + c * 118, y: r === 0 ? -225 : 55, w: 104, h: 170 }; }
function drawCPUDie(cx, cy, s, t, opt = {}) {
  const func = opt.func || 0; // 0 写实，1 按用途上色
  const fl = opt.flash || [];
  ctx.save(); ctx.translate(cx, cy); ctx.scale(s, s);
  ctx.fillStyle = '#181B2C'; rr(-240, -240, 480, 480, 14); ctx.fill();
  ctx.strokeStyle = 'rgba(255,255,255,0.1)'; ctx.lineWidth = 2; ctx.stroke();
  const ctrl = mix('#5C4630', C.cpu, func), cache = mix('#3A4262', C.cache, func), alu = mix('#2D5A4C', C.gpu, func);
  // L3
  ctx.fillStyle = cache; rr(-229, -40, 458, 80, 8); ctx.fill();
  ctx.strokeStyle = 'rgba(255,255,255,0.10)'; ctx.lineWidth = 1.5;
  for (let i = 1; i < 16; i++) { ctx.beginPath(); ctx.moveTo(-229 + i * 28.6, -40); ctx.lineTo(-229 + i * 28.6, 40); ctx.stroke(); }
  for (let i = 0; i < 8; i++) {
    const r = cpuCoreRect(i);
    ctx.fillStyle = '#222639'; rr(r.x, r.y, r.w, r.h, 8); ctx.fill();
    ctx.fillStyle = ctrl; rr(r.x + 6, r.y + 6, r.w - 12, r.h * 0.46, 5); ctx.fill();
    // 控制区里的细线
    ctx.strokeStyle = 'rgba(255,230,190,0.18)'; ctx.lineWidth = 1.5;
    for (let k = 0; k < 6; k++) { const yy = r.y + 14 + k * 11; ctx.beginPath(); ctx.moveTo(r.x + 12, yy); ctx.lineTo(r.x + 12 + (r.w - 24) * (0.4 + 0.6 * rnd(i * 9 + k)), yy); ctx.stroke(); }
    ctx.fillStyle = cache; rr(r.x + 6, r.y + 12 + r.h * 0.46, r.w - 12, r.h * 0.24, 5); ctx.fill();
    ctx.fillStyle = alu; rr(r.x + 6, r.y + 18 + r.h * 0.70, (r.w - 12) * 0.48, r.h * 0.22, 5); ctx.fill();
    ctx.fillStyle = cache; rr(r.x + 10 + (r.w - 12) * 0.48, r.y + 18 + r.h * 0.70, (r.w - 12) * 0.52 - 4, r.h * 0.22, 5); ctx.fill();
    const f = fl[i] || 0;
    if (f > 0) { ctx.fillStyle = hexA(C.cpuL, 0.55 * f); rr(r.x, r.y, r.w, r.h, 8); ctx.fill(); }
  }
  ctx.restore();
}
function drawCap(x, y, s, a) {
  if (a <= 0) return;
  ctx.save(); ctx.globalAlpha = a; ctx.translate(x, y); ctx.scale(s, s);
  ctx.fillStyle = '#2A1C10'; ctx.beginPath(); ctx.moveTo(-26, 6); ctx.lineTo(-26, 20); ctx.quadraticCurveTo(0, 32, 26, 20); ctx.lineTo(26, 6); ctx.fill();
  ctx.fillStyle = C.cpuL; ctx.beginPath(); ctx.moveTo(0, -18); ctx.lineTo(44, 0); ctx.lineTo(0, 18); ctx.lineTo(-44, 0); ctx.closePath(); ctx.fill();
  ctx.strokeStyle = C.hi; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(34, 8); ctx.lineTo(34, 30); ctx.stroke();
  ctx.fillStyle = C.hi; ctx.beginPath(); ctx.arc(34, 32, 5, 0, Math.PI * 2); ctx.fill();
  ctx.restore();
}
function drawCPUChip(cx, cy, s, t, opt) {
  ctx.save(); ctx.translate(cx, cy); ctx.scale(s, s);
  ctx.fillStyle = 'rgba(0,0,0,0.4)'; rr(-280 + 14, -280 + 20, 560, 560, 26); ctx.fill();
  ctx.fillStyle = '#163A2D'; rr(-280, -280, 560, 560, 26); ctx.fill();
  ctx.fillStyle = '#D9A640';
  for (let i = 0; i < 22; i++) { const p = -252 + i * 24; ctx.fillRect(p, -272, 10, 10); ctx.fillRect(p, 262, 10, 10); ctx.fillRect(-272, p, 10, 10); ctx.fillRect(262, p, 10, 10); }
  ctx.restore();
  drawCPUDie(cx, cy, s, t, opt);
  // 顶盖
  const lift = opt.lift || 0, la = 1 - seg(lift, 0.4, 1);
  if (la > 0) {
    ctx.save(); ctx.globalAlpha = la; ctx.translate(cx, cy - lift * 160 * s); ctx.scale(s, s);
    const g = ctx.createLinearGradient(-260, -260, 260, 260); g.addColorStop(0, '#E8ECF3'); g.addColorStop(0.5, '#AEB4C4'); g.addColorStop(1, '#D3D8E3');
    ctx.fillStyle = g; rr(-262, -262, 524, 524, 30); ctx.fill();
    ctx.strokeStyle = 'rgba(255,255,255,0.6)'; ctx.lineWidth = 3; ctx.stroke();
    ctx.fillStyle = 'rgba(40,46,70,0.75)'; ctx.font = `400 150px ${FT}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText('CPU', 0, 0);
    const sh = (t * 0.6) % 1; const sx = lerp(-400, 400, sh);
    const sg = ctx.createLinearGradient(sx - 80, -260, sx + 80, 260); sg.addColorStop(0, 'rgba(255,255,255,0)'); sg.addColorStop(0.5, 'rgba(255,255,255,0.35)'); sg.addColorStop(1, 'rgba(255,255,255,0)');
    ctx.fillStyle = sg; rr(-262, -262, 524, 524, 30); ctx.fill();
    ctx.restore();
  }
}

// ---------- GPU 芯片：128 SM × 128 核 = 16384 ----------
function gpuLayout(cx, cy, size) {
  const m = size * 0.03, l2 = size * 0.045, g = size * 0.006;
  const aw = size - 2 * m, smW = (aw - 7 * g) / 8;
  const ah = size - 2 * m - l2 - 2 * g, smH = (ah - 14 * g) / 16;
  return { x0: cx - size / 2, y0: cy - size / 2, m, l2, g, smW, smH, size };
}
function smRect(L, sc, sr) {
  const x = L.x0 + L.m + sc * (L.smW + L.g);
  let y = L.y0 + L.m + sr * (L.smH + L.g); if (sr >= 8) y += L.l2 + L.g;
  return { x, y };
}
const LV = 6;
function drawGPUDie(cx, cy, size, light, opt = {}) {
  const L = gpuLayout(cx, cy, size), func = opt.func || 0, al = opt.alpha == null ? 1 : opt.alpha;
  if (al <= 0) return;
  ctx.save(); ctx.globalAlpha = al;
  ctx.fillStyle = '#141828'; rr(L.x0, L.y0, size, size, size * 0.02); ctx.fill();
  ctx.strokeStyle = 'rgba(255,255,255,0.12)'; ctx.lineWidth = 2; ctx.stroke();
  // L2
  const ly = L.y0 + L.m + 8 * (L.smH + L.g) - L.g + L.g;
  ctx.fillStyle = mix('#323A5A', C.cache, func); ctx.fillRect(L.x0 + L.m, ly, size - 2 * L.m, L.l2);
  const paths = []; for (let k = 0; k < LV; k++) paths.push(new Path2D());
  const strips = new Path2D(), strips2 = new Path2D(), smBg = new Path2D();
  const coreW = L.smW * 0.86, stripW = L.smW * 0.14, cw = coreW / 16, ch = L.smH / 8, gx = Math.max(0.6, cw * 0.2), gy = Math.max(0.6, ch * 0.2);
  for (let sr = 0; sr < 16; sr++) for (let sc = 0; sc < 8; sc++) {
    const p = smRect(L, sc, sr);
    strips.rect(p.x, p.y, stripW - 1, L.smH * 0.5 - 0.5);
    smBg.rect(p.x + stripW, p.y, coreW - 1, L.smH - 0.5);
    strips2.rect(p.x, p.y + L.smH * 0.5, stripW - 1, L.smH * 0.5);
    for (let j = 0; j < 8; j++) for (let i = 0; i < 16; i++) {
      const gi = sc * 16 + i, gj = sr * 8 + j; // 全局 128×128
      const v = light(gi, gj, p.x + stripW + i * cw + cw / 2, p.y + j * ch + ch / 2);
      const k = clamp(Math.floor(v * LV), 0, LV - 1);
      paths[k].rect(p.x + stripW + i * cw, p.y + j * ch, cw - gx, ch - gy);
    }
  }
  ctx.fillStyle = hexA('#1FAE7E', 0.12 + 0.4 * func); ctx.fill(smBg);
  ctx.fillStyle = mix('#4A3A2A', C.cpu, func); ctx.fill(strips);
  ctx.fillStyle = mix('#2C3350', C.cache, func); ctx.fill(strips2);
  for (let k = 0; k < LV; k++) { ctx.fillStyle = mix(mix('#1C4A3E', '#1FAE7E', func), C.gpuL, k / (LV - 1)); ctx.fill(paths[k]); }
  ctx.restore();
}

// ---------- 题堆 ----------
const PILE = { top: 140, bot: 400 };
const PILE_COL = []; for (let i = 0; i < 54 * 14; i++) { const w = rnd(i * 1.37 + 9) * 2 - 1; PILE_COL.push(w); }
function drawPile(t, frac, a = 1, label = true) {
  if (frac <= 0.001 || a <= 0) return;
  const h = (PILE.bot - PILE.top) * frac, top = PILE.bot - h;
  ctx.save(); ctx.globalAlpha = a;
  ctx.beginPath(); ctx.moveTo(0, PILE.bot + 4);
  for (let x = 0; x <= W; x += 20) ctx.lineTo(x, top + Math.sin(x * 0.03 + t * 3) * 8 * frac + Math.sin(x * 0.11 - t * 5) * 4);
  ctx.lineTo(W, PILE.bot + 4); ctx.closePath(); ctx.clip();
  for (let j = 0; j < 14; j++) for (let i = 0; i < 54; i++) {
    const w = PILE_COL[j * 54 + i]; const y = PILE.bot - 20 - j * 20 + Math.sin(t * 2 + i * 0.5 + j) * 1.5, x = 3 + i * 20;
    const sh = Math.max(0, Math.sin(t * 2.5 + i * 0.7 - j * 1.1 + w * 6));
    ctx.fillStyle = mix(wColor(w), '#FFFFFF', sh * sh * 0.35); ctx.fillRect(x, y, 16, 16);
  }
  ctx.restore();
  if (label && frac > 0.35) {
    ctx.save(); ctx.globalAlpha = a * clamp((frac - 0.35) * 3);
    ctx.fillStyle = 'rgba(8,9,26,0.85)'; rr(W / 2 - 210, 236, 420, 76, 38); ctx.fill();
    ctx.strokeStyle = hexA(C.hi, 0.7); ctx.lineWidth = 2.5; ctx.stroke();
    richLine('{70 亿}道乘加题', W / 2, 275, 44, FB, C.white, C.hi, 900);
    ctx.restore();
  }
}
function pilePoint(i) { return { x: 60 + rnd(i * 3.1) * 960, y: PILE.top + 60 + rnd(i * 7.7) * 180 }; }

// ---------- 场景 A：开头 0–3 ----------
const A_CH = [[-0.12, 4], [0.4, 5], [0.8, 6], [1.2, 7]]; // 在这个时刻显示到第 n 个字
function aCount(t) { let n = 3; for (const [tt, k] of A_CH) if (t >= tt) n = k; return n; }
function sceneA(t) {
  if (t > 3.2) return;
  const PCX = 540, PCY = 830, CCY = 1285;
  const z = seg(t, 2.25, 3.0), zu = ei(z);
  const n = aCount(t); const sl = slotLocal(Math.min(n, 7)); const F = { x: PCX + sl.x, y: PCY + sl.y };
  ctx.save();
  if (z > 0) { const s = 1 + zu * 16; ctx.translate(lerp(F.x, 540, zu), lerp(F.y, 900, zu)); ctx.scale(s, s); ctx.translate(-F.x, -F.y); }
  bigTitle(['AI 为什么', '非要用{显卡}？'], 225, 1, { scale: [1 + 0.015 * Math.sin(t * 4), 1 + 0.015 * Math.sin(t * 4 + 1)] });
  // 每个字蹦出前，显卡发光，光沿线走到手机
  let light = 0;
  for (const [tt] of A_CH) { const d = t - (tt - 0.28); if (d > 0 && d < 0.7) light = Math.max(light, Math.sin(Math.PI * clamp(d / 0.7))); }
  // 线
  ctx.save(); ctx.strokeStyle = hexA(C.gpu, 0.25 + 0.5 * light); ctx.lineWidth = 6; ctx.setLineDash([14, 10]); ctx.lineDashOffset = -t * 80;
  ctx.beginPath(); ctx.moveTo(540, 1190); ctx.lineTo(540, 1150); ctx.stroke(); ctx.restore();
  drawCard(540, CCY, 1, t, { light });
  // 光圈往上扩散
  for (const [tt] of A_CH) {
    const d = t - (tt - 0.3); if (d < 0 || d > 0.6) continue;
    const u = d / 0.6; ctx.save(); ctx.globalAlpha = (1 - u) * 0.8; ctx.strokeStyle = C.gpu; ctx.lineWidth = 6 * (1 - u) + 1;
    ctx.beginPath(); ctx.ellipse(540, 1190 - u * 80, 380 * (0.6 + u * 0.5), 30 + u * 40, 0, 0, Math.PI * 2); ctx.stroke(); ctx.restore();
  }
  drawPhone(PCX, PCY, 1, n, t);
  // 字上迸出 ×
  for (const [tt, k] of A_CH) {
    const d = t - tt; if (d < 0 || d > 0.8) continue;
    const p = slotLocal(k - 1); const ox = PCX + p.x, oy = PCY + p.y;
    for (let i = 0; i < 12; i++) {
      const ang = rnd(k * 31 + i) * Math.PI * 2, sp = 160 + rnd(k * 17 + i) * 220, u = d / 0.8;
      const x = ox + Math.cos(ang) * sp * d, y = oy + Math.sin(ang) * sp * d - 40 * d;
      ctx.save(); ctx.globalAlpha = (1 - u) * 0.95; ctx.fillStyle = i % 2 ? C.num : C.pink;
      ctx.font = `700 ${26 + 10 * rnd(i + k)}px ${FM}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      ctx.fillText(i % 3 === 0 ? '+' : '×', x, y); ctx.restore();
    }
  }
  ctx.restore();
  if (z > 0) { ctx.fillStyle = hexA('#0C0F26', clamp((z - 0.55) / 0.45)); ctx.fillRect(0, 0, W, H); }
}

// ---------- 场景 B：字 → 数字 → 乘加 → 下一个字 3–10.4 ----------
const GX = 80, GY = 740, CELL = 96, OUTX = 950, TY = 380, VY = 615;
function colX(c) { return GX + c * CELL + CELL / 2; }
function rowY(r) { return GY + r * CELL + CELL / 2; }
function tileX(i) { return 89 + i * 114; }
function drawTiles(t, a) {
  if (a <= 0) return;
  const won = t >= 9.85;
  for (let i = 0; i < 8; i++) {
    const ui = eo(seg(t, 3.0 + i * 0.04, 3.4 + i * 0.04)); const x = tileX(i), y = TY + (1 - ui) * -50;
    ctx.save(); ctx.globalAlpha = a * ui;
    if (i < 7) {
      ctx.fillStyle = '#F4F6FF'; rr(x, y - 55, 104, 110, 18); ctx.fill();
      ctx.fillStyle = '#1B1E2E'; ctx.font = `700 64px ${FB}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(AI_TXT[i], x + 52, y + 2);
    } else {
      const p = 0.5 + 0.5 * Math.sin(t * 8);
      ctx.fillStyle = won ? C.hi : hexA(C.hi, 0.14 + 0.12 * p); rr(x, y - 55, 104, 110, 18); ctx.fill();
      ctx.strokeStyle = C.hi; ctx.lineWidth = 4; ctx.stroke();
      ctx.fillStyle = won ? '#1B1E2E' : C.hi; ctx.font = `700 64px ${FB}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      if (won) { const s = back(seg(t, 9.85, 10.15)); ctx.translate(x + 52, y + 2); ctx.scale(s, s); ctx.fillText('光', 0, 0); }
      else ctx.fillText('?', x + 52, y + 2);
    }
    ctx.restore();
  }
}
function scramble(v, t, tEnd, seed) {
  if (t >= tEnd) return v.toFixed(1);
  const r = (rnd(seed + Math.floor(t * 30)) * 2.6 - 1.3); return r.toFixed(1);
}
function sceneB(t) {
  if (t < 2.9 || t > 10.7) return;
  const aAll = seg(t, 2.9, 3.15);
  ctx.save(); ctx.globalAlpha = aAll;
  drawTiles(t, 1 - seg(t, 10.2, 10.6));
  // 汇聚线
  const lu = seg(t, 3.45, 4.1), la = (1 - seg(t, 4.6, 5.2)) * lu;
  if (la > 0) {
    ctx.save(); ctx.globalAlpha = aAll * la; ctx.lineWidth = 3;
    for (let i = 0; i < 7; i++) for (let c = 0; c < 8; c += 1) {
      if ((i + c) % 3) continue;
      const x0 = tileX(i) + 52, y0 = TY + 58, x1 = colX(c), y1 = VY - 40;
      const g = ctx.createLinearGradient(x0, y0, x1, y1); g.addColorStop(0, hexA(C.white, 0.0)); g.addColorStop(1, hexA(C.num, 0.6));
      ctx.strokeStyle = g; ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(lerp(x0, x1, lu), lerp(y0, y1, lu)); ctx.stroke();
    }
    ctx.restore();
  }
  // 字 → 数字：持续的光点流
  const st = seg(t, 3.6, 3.9) * (1 - seg(t, 5.3, 5.7));
  if (st > 0) {
    for (let i = 0; i < 40; i++) {
      const ph = (t * 1.3 + rnd(i * 2.7)) % 1, ti = i % 7, c = Math.floor(rnd(i * 5.3) * 8);
      const x = lerp(tileX(ti) + 52, colX(c), ph), y = lerp(TY + 58, VY - 40, ph);
      ctx.save(); ctx.globalAlpha = aAll * st * Math.sin(Math.PI * ph); glowDot(x, y, 16, C.num, 0.9); ctx.restore();
    }
  }
  // 候选阶段：表格淡出
  const fadeGrid = 1 - seg(t, 8.3, 8.6) + seg(t, 9.9, 10.3);
  const gA = clamp(fadeGrid);
  // 向量
  for (let c = 0; c < 8; c++) {
    const t0 = 3.8 + c * 0.08, ui = back(seg(t, t0, t0 + 0.3)); if (ui <= 0) continue;
    const x = colX(c), y = VY + Math.sin(t * 3.2 + c * 0.8) * 6 * seg(t, 4.3, 4.8);
    ctx.save(); ctx.globalAlpha = aAll * clamp(ui) * gA; ctx.translate(x, y); ctx.scale(ui, ui);
    ctx.fillStyle = '#10233A'; rr(-44, -36, 88, 72, 14); ctx.fill(); ctx.strokeStyle = C.num; ctx.lineWidth = 3; ctx.stroke();
    ctx.fillStyle = C.num; ctx.font = `700 30px ${FM}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText(scramble(VEC[c], t, t0 + 0.45, c * 13), 0, 1); ctx.restore();
  }
  // 数字表
  for (let r = 0; r < 5; r++) for (let c = 0; c < 8; c++) {
    const t0 = 5.4 + (r * 8 + c) * 0.012, ui = eo(seg(t, t0, t0 + 0.3)); if (ui <= 0) continue;
    const x = GX + c * CELL, y = GY + r * CELL;
    ctx.save(); ctx.globalAlpha = aAll * ui * gA;
    ctx.fillStyle = wColor(WM[r][c]); rr(x + 3, y + 3, CELL - 6, CELL - 6, 10); ctx.fill();
    // 乘
    const mt = 6.0 + r * 0.2, mf = seg(t, mt, mt + 0.12) * (1 - seg(t, mt + 0.25, mt + 0.5));
    if (mf > 0) { ctx.fillStyle = hexA('#FFFFFF', 0.6 * mf); rr(x + 3, y + 3, CELL - 6, CELL - 6, 10); ctx.fill(); }
    ctx.fillStyle = 'rgba(255,255,255,0.85)'; ctx.font = `700 24px ${FM}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    const done = t > mt + 0.12;
    if (!done) ctx.fillText(WM[r][c].toFixed(1), x + CELL / 2, y + CELL / 2);
    else {
      const st = 7.1 + r * 0.16, su = eio(seg(t, st, st + 0.45));
      if (su < 1) { ctx.fillStyle = C.hi; ctx.font = `700 34px ${FM}`; ctx.fillText('×', x + CELL / 2, y + CELL / 2); }
    }
    ctx.restore();
  }
  // 乘积滑到右边求和
  for (let r = 0; r < 5; r++) {
    const st = 7.1 + r * 0.16, su = eio(seg(t, st, st + 0.45)); if (su <= 0) continue;
    ctx.save(); ctx.globalAlpha = aAll * gA;
    for (let c = 0; c < 8; c++) {
      if (su >= 1) break;
      const x = lerp(colX(c), OUTX, su), y = rowY(r);
      glowDot(x, y, 22, C.hi, 0.9);
      if (c < 7) { ctx.fillStyle = hexA(C.hi, 1 - su); ctx.font = `700 26px ${FM}`; ctx.textAlign = 'center'; ctx.fillText('+', lerp(colX(c) + CELL / 2, OUTX, su), y); }
    }
    ctx.restore();
  }
  // 输出 → 候选
  for (let r = 0; r < 5; r++) {
    const st = 7.1 + r * 0.16 + 0.42, ui = back(seg(t, st, st + 0.25)); if (ui <= 0) continue;
    const cu = eio(seg(t, 8.3 + r * 0.05, 8.75 + r * 0.05));
    const out = 1 - seg(t, 9.9, 10.3);
    const x = lerp(OUTX, 200, cu), y = lerp(rowY(r), 730 + r * 125, cu);
    ctx.save(); ctx.globalAlpha = aAll * clamp(ui) * out; ctx.translate(x, y); ctx.scale(clamp(ui, 0, 1.2), clamp(ui, 0, 1.2));
    const win_ = r === 0 && t > 9.0;
    ctx.fillStyle = win_ ? C.hi : '#2A2340'; rr(-58, -40, 116, 80, 16); ctx.fill();
    ctx.strokeStyle = C.hi; ctx.lineWidth = 3; ctx.stroke();
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    if (cu < 0.5) { ctx.globalAlpha *= 1 - cu * 2; ctx.fillStyle = C.hi; ctx.font = `700 30px ${FM}`; ctx.fillText(OUT[r].toFixed(1), 0, 2); }
    else {
      ctx.globalAlpha *= (cu - 0.5) * 2;
      const flyAway = r === 0 && t > 9.3;
      if (!flyAway) { ctx.fillStyle = win_ ? '#1B1E2E' : C.white; ctx.font = `700 54px ${FB}`; ctx.fillText(CAND[r][0], 0, 2); }
    }
    ctx.restore();
    // 概率条
    if (cu > 0.6) {
      const bu = eo(seg(t, 8.7 + r * 0.06, 9.2 + r * 0.06));
      ctx.save(); ctx.globalAlpha = aAll * out; const bx = 290, by = 730 + r * 125, bw = 660 * CAND[r][1] / 62 * bu;
      ctx.fillStyle = 'rgba(255,255,255,0.06)'; rr(bx, by - 24, 660, 48, 24); ctx.fill();
      ctx.fillStyle = r === 0 ? C.hi : hexA(C.num, 0.7); rr(bx, by - 24, Math.max(bw, 1), 48, 24); ctx.fill();
      ctx.fillStyle = r === 0 ? '#1B1E2E' : C.white; ctx.font = `700 30px ${FM}`; ctx.textAlign = 'left'; ctx.textBaseline = 'middle';
      if (bw > 110) ctx.fillText(Math.round(CAND[r][1] * bu) + '%', bx + 18, by + 1);
      else { ctx.fillStyle = C.white; ctx.fillText(Math.round(CAND[r][1] * bu) + '%', bx + bw + 14, by + 1); }
      ctx.restore();
    }
  }
  // 光 飞进空位
  const fu = seg(t, 9.3, 9.85);
  if (fu > 0 && fu < 1) {
    const e = eio(fu), x0 = 200, y0 = 730, x1 = tileX(7) + 52, y1 = TY + 2;
    const x = lerp(x0, x1, e), y = lerp(y0, y1, e) - Math.sin(Math.PI * e) * 120;
    glowDot(x, y, 90, C.hi, 0.6);
    ctx.save(); ctx.fillStyle = C.hi; ctx.font = `700 ${lerp(54, 64, e)}px ${FB}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText('光', x, y); ctx.restore();
  }
  if (t > 9.85 && t < 10.5) { const u = seg(t, 9.85, 10.5); ctx.save(); ctx.globalAlpha = 1 - u; ctx.strokeStyle = C.hi; ctx.lineWidth = 5; ctx.beginPath(); ctx.arc(tileX(7) + 52, TY, 60 + u * 120, 0, Math.PI * 2); ctx.stroke(); ctx.restore(); }
  ctx.restore();
}

// ---------- 格子海 10.3–13.3 ----------
function sceneMosaic(t) {
  if (t < 10.3 || t > 13.4) return;
  const u = eio(seg(t, 10.4, 12.3)), s = CELL * Math.pow(4 / CELL, u);
  const px = lerp(GX + 4 * CELL, 540, u), py = lerp(GY + 2.5 * CELL, 960, u);
  const cu = eio(seg(t, 12.35, 13.2));
  const clipTop = lerp(0, PILE.top, cu), clipBot = lerp(H, PILE.bot, cu);
  const a = seg(t, 10.3, 10.45) * (1 - seg(t, 12.7, 13.2));
  ctx.save(); ctx.globalAlpha = a;
  ctx.beginPath(); ctx.rect(0, clipTop, W, clipBot - clipTop); ctx.clip();
  ctx.imageSmoothingEnabled = false;
  ctx.drawImage(TEX, px - 512 * s, py - 512.5 * s, 1024 * s, 1024 * s);
  // 网格线（格子大时）
  if (s > 12) {
    ctx.strokeStyle = `rgba(12,15,38,${clamp((s - 12) / 30) * 0.9})`; ctx.lineWidth = Math.min(6, s * 0.07);
    const x0 = px - 512 * s, y0 = py - 512.5 * s; const i0 = Math.floor(-x0 / s), j0 = Math.floor(-y0 / s);
    ctx.beginPath();
    for (let i = i0; x0 + i * s < W; i++) { ctx.moveTo(x0 + i * s, 0); ctx.lineTo(x0 + i * s, H); }
    for (let j = j0; y0 + j * s < H; j++) { ctx.moveTo(0, y0 + j * s); ctx.lineTo(W, y0 + j * s); }
    ctx.stroke();
  }
  ctx.fillStyle = `rgba(10,12,30,${0.35 * u})`; ctx.fillRect(0, 0, W, H);
  // 中心那一小格（原来的数字表）亮框
  const hl = 1 - seg(t, 11.6, 12.2);
  if (hl > 0) { ctx.strokeStyle = hexA(C.hi, hl); ctx.lineWidth = 4; ctx.strokeRect(px - 4 * s, py - 2.5 * s, 8 * s, 5 * s); }
  ctx.restore();
  // 计数
  const ca = seg(t, 10.8, 11.0) * (1 - seg(t, 12.45, 12.9));
  if (ca > 0) {
    const cu2 = eo(seg(t, 10.8, 12.2)), v = 7e9 * cu2;
    let txt; if (v < 1e4) txt = fmtInt(v); else if (v < 1e8) txt = Math.floor(v / 1e4) + ' 万'; else txt = (v / 1e8).toFixed(v >= 6.995e9 ? 0 : 1) + ' 亿';
    ctx.save(); ctx.globalAlpha = ca;
    const rg = ctx.createRadialGradient(540, 930, 0, 540, 930, 520); rg.addColorStop(0, 'rgba(8,9,26,0.85)'); rg.addColorStop(1, 'rgba(8,9,26,0)');
    ctx.fillStyle = rg; ctx.fillRect(0, 400, W, 1060);
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.shadowColor = hexA(C.hi, 0.6); ctx.shadowBlur = 40;
    ctx.fillStyle = C.hi; ctx.font = `400 210px ${FT}`; ctx.fillText(txt, 540, 900);
    ctx.shadowBlur = 0; ctx.fillStyle = C.white; ctx.font = `900 54px ${FB}`; ctx.fillText('次「乘一下，加起来」', 540, 1050);
    ctx.restore();
  }
  if (t > 12.5) drawPile(t, 1, seg(t, 12.6, 13.2), true);
}

// ---------- 场景 C：CPU 13.2–21.5 ----------
const CPU_C = { x: 540, y: 880 };
function cpuTasks(t) { // 每核每 0.3 秒一道
  const list = []; const t0 = 15.4;
  if (t < t0) return { list, done: 0 };
  let done = 0;
  for (let c = 0; c < 8; c++) {
    const kmax = Math.floor((t - t0 - c * 0.0375) / 0.3);
    for (let k = Math.max(0, kmax - 1); k <= kmax; k++) {
      const ts = t0 + k * 0.3 + c * 0.0375; const d = t - ts; if (d < 0) continue;
      list.push({ c, k, d });
    }
    done += Math.max(0, kmax);
  }
  return { list, done };
}
function sceneC(t) {
  if (t < 13.1 || t > 21.6) return;
  const ox = -1300 * ei(seg(t, 21.0, 21.5));
  ctx.save(); ctx.translate(ox, 0);
  drawPile(t, 1, 1, true);
  const ui = back(seg(t, 13.2, 13.9)), s = 1 * clamp(ui, 0, 1.1);
  const lift = eio(seg(t, 14.0, 14.7));
  const tk = cpuTasks(t); const flash = new Array(8).fill(0);
  tk.list.forEach(o => { if (o.d > 0.22 && o.d < 0.4) flash[o.c] = Math.max(flash[o.c], 1 - (o.d - 0.22) / 0.18); });
  ctx.save(); ctx.globalAlpha = seg(t, 13.2, 13.45);
  drawCPUChip(CPU_C.x, CPU_C.y + (1 - clamp(ui)) * 300, s, t, { lift, flash });
  ctx.restore();
  if (lift > 0.8) {
    for (let i = 0; i < 8; i++) {
      const r = cpuCoreRect(i); const ca = back(seg(t, 14.6 + i * 0.05, 14.95 + i * 0.05));
      drawCap(CPU_C.x + r.x + r.w / 2, CPU_C.y + r.y + 46 - flash[i] * 8, clamp(ca, 0, 1.2) * 0.9, clamp(ca));
    }
  }
  // 题飞进核
  tk.list.forEach(o => {
    if (o.d > 0.22) return;
    const p = pilePoint(o.c * 100 + o.k), r = cpuCoreRect(o.c); const e = eio(o.d / 0.22);
    const x = lerp(p.x, CPU_C.x + r.x + r.w / 2, e), y = lerp(p.y, CPU_C.y + r.y + r.h / 2, e);
    ctx.fillStyle = hexA(C.hi, 0.95); rr(x - 9, y - 9, 18, 18, 4); ctx.fill(); glowDot(x, y, 26, C.hi, 0.5);
  });
  // 进度（和 GPU 段同样慢放：GPU 2 秒算完，CPU 这 5.3 秒只算了 4%，约慢 60 倍）
  const ca = seg(t, 15.4, 15.7);
  if (ca > 0) {
    const pr = 0.04 * seg(t, 15.4, 20.7);
    ctx.save(); ctx.globalAlpha = ca; ctx.textBaseline = 'middle';
    ctx.fillStyle = 'rgba(8,9,26,0.7)'; rr(100, 1172, 880, 116, 24); ctx.fill();
    ctx.font = `700 32px ${FB}`; ctx.fillStyle = C.mute; ctx.textAlign = 'left'; ctx.fillText('已算', 136, 1208);
    ctx.font = `700 42px ${FM}`; ctx.fillStyle = C.cpuL; ctx.fillText((7e9 * pr / 1e8).toFixed(1), 214, 1210);
    ctx.font = `700 32px ${FB}`; ctx.fillStyle = C.mute; ctx.fillText('亿 / 70 亿', 214 + ctx.measureText('0').width * 0 + 96, 1208);
    ctx.textAlign = 'right'; ctx.font = `700 40px ${FM}`; ctx.fillStyle = C.white; ctx.fillText((pr * 100).toFixed(1) + '%', 944, 1210);
    ctx.fillStyle = 'rgba(255,255,255,0.08)'; rr(136, 1246, 808, 22, 11); ctx.fill();
    ctx.fillStyle = C.cpu; rr(136, 1246, Math.max(4, 808 * pr), 22, 11); ctx.fill();
    ctx.restore();
  }
  ctx.restore();
}

// ---------- 场景 D：GPU 21–30 ----------
const GPU_C = { x: 540, y: 900 };
function sceneD(t) {
  if (t < 20.95 || t > 30.6) return;
  const inU = eo(seg(t, 21.0, 21.55)), ox = (1 - inU) * 1300;
  // 甩镜速度线
  const wv = Math.sin(Math.PI * seg(t, 20.95, 21.6));
  if (wv > 0) {
    ctx.save(); ctx.globalAlpha = wv * 0.6;
    for (let i = 0; i < 26; i++) { const y = 200 + rnd(i) * 1300, x = rnd(i + 7) * W, l = 200 + rnd(i + 3) * 500; ctx.fillStyle = i % 3 ? 'rgba(180,200,255,0.5)' : hexA(C.gpu, 0.6); ctx.fillRect(x - l / 2, y, l, 3 + rnd(i) * 4); }
    ctx.restore();
  }
  // 题堆
  const pf = 1 - eio(seg(t, 24.05, 26.0));
  if (t < 26.6) drawPile(t, pf, 1, true);
  // 推进：显卡 → 芯片
  const k = eio(seg(t, 21.65, 22.55)), dsz0 = 150, dsz = lerp(dsz0, 860, k);
  // 对照阶段：芯片缩到下半
  const cmp = eio(seg(t, 26.4, 27.0)), cmpOut = 1 - seg(t, 29.9, 30.4);
  const gsz = lerp(dsz, 420, cmp) * (1 + 0.02 * cmp * Math.sin(t * 3 + 1)), gcx = lerp(GPU_C.x + ox, 640, cmp), gcy = lerp(GPU_C.y, 1080, cmp) + cmp * Math.sin(t * 2.2 + 1.5) * 10;
  const powerT = 22.45;
  const light = (gi, gj, x, y) => {
    const d = Math.hypot(x - gcx, y - gcy) / gsz * 860;
    let v = clamp(((t - powerT) * 1500 - d) / 160);
    const tw = 0.5 + 0.5 * Math.sin(t * 7 + gi * 0.37 + gj * 0.51);
    let b = v * (0.32 + 0.18 * tw);
    if (t > 24.0 && t < 26.4) { // 一起算：整片同时闪
      const ph = ((t - 24.0) % 0.3) / 0.3; const p = Math.exp(-ph * 5);
      b = Math.max(b, p * (0.7 + 0.3 * rnd(gi * 131 + gj * 7 + Math.floor((t - 24) / 0.3))));
    }
    if (t >= 28.2 && cmp > 0) b = Math.max(b, 0.45 + 0.35 * Math.sin(t * 6 + (gi + gj) * 0.08));
    return b;
  };
  if (k < 1 || true) {
    const dieA = seg(t, 21.3, 21.6) * cmpOut * (cmp > 0 && t < 28.2 ? lerp(1, 0.45, seg(t, 26.6, 26.9)) : 1);
    drawGPUDie(gcx, gcy, gsz, light, { alpha: dieA, func: eio(seg(t, 26.6, 27.1)) });
    if (t > 24.0 && t < 26.4) {
      const p = Math.exp(-(((t - 24.0) % 0.3) / 0.3) * 4);
      ctx.save(); ctx.globalCompositeOperation = 'lighter'; glowDot(gcx, gcy, gsz * 0.8, C.gpu, 0.45 * p); ctx.restore();
    }
    if (t > 22.45 && t < 23.6) { const u = seg(t, 22.45, 23.6); ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.globalAlpha = 1 - u; ctx.strokeStyle = C.gpuL; ctx.lineWidth = 8; ctx.beginPath(); ctx.arc(gcx, gcy, (t - 22.45) * 1500 * gsz / 860, 0, Math.PI * 2); ctx.stroke(); ctx.restore(); }
  }
  const cardS = 1.12 * dsz / dsz0;
  drawCard(GPU_C.x + ox, GPU_C.y, cardS, t, { alpha: 1 - seg(t, 21.9, 22.45), shroud: lerp(1, 0.35, seg(t, 21.55, 21.85)), light: 0.6 });
  // 题雨
  if (t > 24.0 && t < 26.3) {
    for (let i = 0; i < 180; i++) {
      const ph = ((t - 24.0) * 1.8 + rnd(i * 3.3)) % 1; const x = 90 + rnd(i) * 900;
      const y = lerp(PILE.bot - 60, 470 + rnd(i * 5.1) * 860, ph * ph);
      ctx.fillStyle = hexA(C.hi, 0.85 * (1 - ph)); ctx.fillRect(x - 6, y - 6, 12, 12);
    }
  }
  // 算完
  const dn = seg(t, 25.95, 26.15) * (1 - seg(t, 26.4, 26.7));
  if (dn > 0) {
    ctx.save(); ctx.globalAlpha = dn; const s = back(seg(t, 25.95, 26.25)); ctx.translate(540, 280); ctx.scale(s, s);
    ctx.fillStyle = 'rgba(8,9,26,0.85)'; rr(-280, -50, 560, 100, 50); ctx.fill(); ctx.strokeStyle = C.gpu; ctx.lineWidth = 3; ctx.stroke();
    richLine('✓ {70 亿}道，算完了', 0, 2, 50, FB, C.gpuL, C.hi, 900); ctx.restore();
  }
  // 核心数标签
  const la = seg(t, 22.9, 23.2) * (1 - seg(t, 23.9, 24.1));
  if (la > 0) {
    ctx.save(); ctx.globalAlpha = la; ctx.fillStyle = 'rgba(8,9,26,0.82)'; rr(300, 845, 480, 110, 30); ctx.fill(); ctx.strokeStyle = C.gpu; ctx.lineWidth = 3; ctx.stroke();
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillStyle = C.gpuL; ctx.font = `400 84px ${FT}`; ctx.fillText('16384 个', 540, 902); ctx.restore();
  }
  // 对照：CPU 芯片在上
  if (cmp > 0) {
    const ca = cmp * cmpOut * (t < 28.2 ? 1 : lerp(1, 0.45, seg(t, 28.2, 28.5)));
    const cy0 = 600 - (1 - cmp) * 120 + Math.sin(t * 2.2) * 10;
    ctx.save(); ctx.globalAlpha = ca; drawCPUDie(640, cy0, 420 / 480 * (1 + 0.02 * Math.sin(t * 3)), t, { func: eio(seg(t, 26.6, 27.1)) }); ctx.restore();
    // 扫光：先扫 CPU，再扫 GPU
    const hy = t < 28.2 ? cy0 : gcy, sw = ((t - (t < 28.2 ? 26.6 : 28.2)) / 0.9) % 1;
    ctx.save(); ctx.beginPath(); ctx.rect(430, hy - 210, 420, 420); ctx.clip(); ctx.globalCompositeOperation = 'lighter';
    const gx = lerp(330, 950, sw), gg = ctx.createLinearGradient(gx - 90, 0, gx + 90, 0);
    gg.addColorStop(0, 'rgba(255,255,255,0)'); gg.addColorStop(0.5, `rgba(255,255,255,${0.35 * cmp * cmpOut})`); gg.addColorStop(1, 'rgba(255,255,255,0)');
    ctx.fillStyle = gg; ctx.fillRect(430, hy - 210, 420, 420); ctx.restore();
    ctx.save(); ctx.globalAlpha = cmp * cmpOut; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.font = `400 92px ${FT}`;
    ctx.fillStyle = C.cpu; ctx.fillText('CPU', 210, 600); ctx.fillStyle = C.gpu; ctx.fillText('GPU', 210, 1080);
    // 图例
    const items = [[C.cpu, '想（调度）'], [C.cache, '记（缓存）'], [C.gpu, '算']];
    let x = 120; ctx.font = `700 34px ${FB}`; ctx.textAlign = 'left';
    items.forEach(([col, lab], i) => {
      const act = t < 28.2 ? (i < 2) : (i === 2); const al = act ? 1 : 0.4;
      ctx.globalAlpha = cmp * cmpOut * al; ctx.fillStyle = col; rr(x, 1318, 38, 38, 8); ctx.fill();
      ctx.fillStyle = C.white; ctx.fillText(lab, x + 52, 1338); x += 52 + ctx.measureText(lab).width + 56;
    });
    ctx.restore();
  }
}

// ---------- 场景 E：谁也不用等谁 30–37.2 ----------
const E_GX = 196, E_GY = 320, E_CELL = 86; // 8×5 题
const K_X0 = 197, K_Y0 = 800, K_S = 70, K_G = 18; // 8×5 核
function kRect(c, r) { return { x: K_X0 + c * (K_S + K_G), y: K_Y0 + r * (K_S + K_G) }; }
function sceneE(t) {
  if (t < 29.9 || t > 37.9) return;
  const a = seg(t, 30.0, 30.4);
  const gA = a * (1 - seg(t, 33.2, 33.6));
  const tf = seg(t, 37.15, 37.7); // 转场进显示器
  // 题格
  if (gA > 0) {
    for (let r = 0; r < 5; r++) for (let c = 0; c < 8; c++) {
      const x = E_GX + c * E_CELL, y = E_GY + r * E_CELL; const ui = eo(seg(t, 30.0 + (r + c) * 0.02, 30.3 + (r + c) * 0.02));
      ctx.save(); ctx.globalAlpha = gA * ui; ctx.fillStyle = wColor(WM[r][c]); rr(x + 3, y + 3, E_CELL - 6, E_CELL - 6, 10); ctx.fill();
      ctx.fillStyle = C.hi; ctx.font = `700 32px ${FM}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText('×', x + E_CELL / 2, y + E_CELL / 2); ctx.restore();
    }
    // 连线：两波，同时出发同时到
    [[30.6, 31.4], [32.1, 32.9]].forEach(([s0, s1]) => {
      const u = eio(seg(t, s0, s1)), fade = 1 - seg(t, s1 + 0.1, s1 + 0.4); if (u <= 0 || fade <= 0) return;
      for (let r = 0; r < 5; r++) for (let c = 0; c < 8; c++) {
        const x0 = E_GX + c * E_CELL + E_CELL / 2, y0 = E_GY + r * E_CELL + E_CELL / 2; const k = kRect(c, r), x1 = k.x + K_S / 2, y1 = k.y + K_S / 2;
        ctx.save(); ctx.globalAlpha = gA * fade * 0.55; ctx.strokeStyle = C.gpu; ctx.lineWidth = 2;
        ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(lerp(x0, x1, u), lerp(y0, y1, u)); ctx.stroke(); ctx.restore();
        if (u < 1) { ctx.save(); ctx.globalAlpha = gA * fade; ctx.fillStyle = C.hi; const x = lerp(x0, x1, u), y = lerp(y0, y1, u); rr(x - 7, y - 7, 14, 14, 3); ctx.fill(); ctx.restore(); }
      }
    });
  }
  // 链
  const chA = seg(t, 33.4, 33.8) * (1 - seg(t, 36.9, 37.2));
  const stepT = k => 33.6 + k * 0.6;
  if (chA > 0) {
    for (let k = 0; k < 6; k++) {
      const x = 90 + k * 156, y = 460; const act = t >= stepT(k), now = act && t < stepT(k + 1);
      ctx.save(); ctx.globalAlpha = chA;
      ctx.fillStyle = act ? (now ? C.hi : hexA(C.hi, 0.35)) : '#262A44'; rr(x, y, 120, 120, 22); ctx.fill();
      ctx.strokeStyle = hexA(C.hi, act ? 1 : 0.3); ctx.lineWidth = 3; ctx.stroke();
      ctx.fillStyle = act ? '#1B1E2E' : C.mute; ctx.font = `400 64px ${FT}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(String(k + 1), x + 60, y + 62);
      ctx.font = `700 26px ${FB}`; ctx.fillStyle = C.mute; ctx.fillText('第' + (k + 1) + '步', x + 60, y - 32);
      if (k < 5) {
        const au = seg(t, stepT(k) + 0.25, stepT(k + 1)); ctx.strokeStyle = hexA(C.hi, 0.25 + 0.75 * au); ctx.lineWidth = 5;
        ctx.beginPath(); ctx.moveTo(x + 124, y + 60); ctx.lineTo(x + 152, y + 60); ctx.stroke();
      }
      if (now) { const pu = seg(t, stepT(k), stepT(k) + 0.35); ctx.globalAlpha = chA * (1 - pu); ctx.strokeStyle = C.hi; ctx.lineWidth = 4; rr(x - pu * 20, y - pu * 20, 120 + pu * 40, 120 + pu * 40, 26); ctx.stroke(); }
      ctx.restore();
    }
    // 接力棒：在两步之间移动
    if (t >= 33.6 && t < 36.6) {
      const k = Math.floor((t - 33.6) / 0.6), u = eio(((t - 33.6) % 0.6) / 0.6);
      const x = 90 + k * 156 + 60 + u * 156 * (k < 5 ? 1 : 0), y = 460 + 60 - Math.sin(Math.PI * u) * 70 * (k < 5 ? 1 : 0);
      glowDot(x, y, 46, C.hi, 0.9);
    }
    // 等待中的小沙漏
    ctx.save(); ctx.globalAlpha = chA; ctx.font = `700 30px ${FB}`; ctx.fillStyle = C.mute; ctx.textAlign = 'center';
    ctx.fillText('后面的每一步，都要等前一步的结果', 540, 660); ctx.restore();
  }
  // 核阵
  const kA = a * (1 - tf);
  if (kA > 0) {
    for (let r = 0; r < 5; r++) for (let c = 0; c < 8; c++) {
      const kr = kRect(c, r); let b = 0.15, idle = false;
      [[31.4], [32.9]].forEach(([s1]) => { const d = t - s1; if (d >= 0 && d < 0.6) b = Math.max(b, 1 - d / 0.6 * 0.6); });
      if (t >= 33.4) {
        const idx = r * 8 + c; const cur = Math.floor((t - 33.6) / 0.6);
        b = 0.12 + 0.12 * Math.sin(t * 4.5 + (r + c) * 0.3); idle = true;
        if (t >= 33.6 && idx === cur && cur < 6) { b = 1; idle = false; }
      }
      const ui = eo(seg(t, 30.1 + (r + c) * 0.015, 30.4 + (r + c) * 0.015));
      ctx.save(); ctx.globalAlpha = kA * ui;
      ctx.fillStyle = mix('#173C33', C.gpuL, b); rr(kr.x, kr.y, K_S, K_S, 12); ctx.fill();
      ctx.strokeStyle = hexA(C.gpu, 0.5); ctx.lineWidth = 2; ctx.stroke();
      if (idle && t > 33.7) {
        const zz = (t * 0.8 + rnd(r * 8 + c)) % 1;
        ctx.globalAlpha = kA * (1 - zz) * 0.8; ctx.fillStyle = C.mute; ctx.font = `700 ${22 + zz * 10}px ${FB}`; ctx.textAlign = 'center';
        ctx.fillText('z', kr.x + K_S * 0.7 + zz * 14, kr.y + K_S * 0.3 - zz * 30);
      }
      ctx.restore();
    }
  }
}

// ---------- 场景 F：游戏 & 2012 37.2–48.2 ----------
const MON = { x: 70, y: 330, w: 940, h: 540 };
const GAME = document.createElement('canvas'); GAME.width = 480; GAME.height = 276; const gctx = GAME.getContext('2d');
const SMALL = document.createElement('canvas'); const sctx = SMALL.getContext('2d');
function drawGame(t) {
  const g = gctx, w = 480, h = 276, hz = 150;
  const sky = g.createLinearGradient(0, 0, 0, hz); sky.addColorStop(0, '#1B0B3A'); sky.addColorStop(0.55, '#7A1F6E'); sky.addColorStop(1, '#FF7A4A');
  g.fillStyle = sky; g.fillRect(0, 0, w, hz);
  for (let i = 0; i < 40; i++) { g.fillStyle = `rgba(255,255,255,${0.3 + 0.5 * rnd(i + 2)})`; g.fillRect(rnd(i) * w, rnd(i + 9) * hz * 0.6, 1.5, 1.5); }
  // 太阳
  g.save(); g.beginPath(); g.arc(240, 120, 62, 0, Math.PI * 2); g.clip();
  const sg = g.createLinearGradient(0, 58, 0, 182); sg.addColorStop(0, '#FFE45A'); sg.addColorStop(1, '#FF3D7F'); g.fillStyle = sg; g.fillRect(170, 50, 140, 140);
  g.fillStyle = '#7A1F6E'; for (let i = 0; i < 6; i++) { const yy = 120 + i * 9 + ((t * 10) % 9); g.fillRect(170, yy, 140, 2 + i * 0.6); }
  g.restore();
  // 山
  g.fillStyle = '#2A0F45'; g.beginPath(); g.moveTo(0, hz);
  for (let x = 0; x <= w; x += 8) g.lineTo(x, hz - 30 - 26 * Math.abs(Math.sin(x * 0.021 + 1.3)) - 12 * Math.sin(x * 0.07)); g.lineTo(w, hz); g.fill();
  g.fillStyle = '#160828'; g.beginPath(); g.moveTo(0, hz);
  for (let x = 0; x <= w; x += 6) g.lineTo(x, hz - 8 - 18 * Math.abs(Math.sin(x * 0.033 + 0.4))); g.lineTo(w, hz); g.fill();
  // 地面网格
  g.fillStyle = '#0E0620'; g.fillRect(0, hz, w, h - hz);
  g.strokeStyle = '#FF3DBA'; g.lineWidth = 1.2;
  for (let i = -12; i <= 12; i++) { g.beginPath(); g.moveTo(240 + i * 8, hz); g.lineTo(240 + i * 70, h); g.stroke(); }
  for (let i = 0; i < 10; i++) { const p = ((i + (t * 1.4) % 1) / 10); const y = hz + (h - hz) * p * p; g.globalAlpha = p; g.beginPath(); g.moveTo(0, y); g.lineTo(w, y); g.stroke(); }
  g.globalAlpha = 1;
  // 小飞船
  const sx = 240 + Math.sin(t * 1.5) * 60, sy = 222;
  g.fillStyle = '#3DF5B0'; g.beginPath(); g.moveTo(sx, sy - 16); g.lineTo(sx + 26, sy + 10); g.lineTo(sx, sy + 4); g.lineTo(sx - 26, sy + 10); g.closePath(); g.fill();
  g.fillStyle = '#FFD84A'; g.fillRect(sx - 4, sy + 6, 8, 6 + 4 * Math.sin(t * 30));
}
function drawMonitorFrame(x, y, w, h, a) {
  ctx.save(); ctx.globalAlpha = a;
  ctx.fillStyle = '#1E2236'; rr(x - 18, y - 18, w + 36, h + 36, 24); ctx.fill();
  ctx.strokeStyle = 'rgba(255,255,255,0.15)'; ctx.lineWidth = 2; ctx.stroke();
  ctx.fillStyle = '#2A2F48'; ctx.fillRect(x + w / 2 - 40, y + h + 18, 80, 60); rr(x + w / 2 - 170, y + h + 74, 340, 22, 11); ctx.fill();
  ctx.restore();
}
function sceneF(t) {
  if (t < 37.1 || t > 48.6) return;
  const tu = eio(seg(t, 37.15, 37.75));
  const out = 1 - seg(t, 43.2, 43.7);
  // 核阵 → 屏幕
  const kx = K_X0, ky = K_Y0, kw = 8 * K_S + 7 * K_G, kh = 5 * K_S + 4 * K_G;
  const rx = lerp(kx, MON.x, tu), ry = lerp(ky, MON.y, tu), rw = lerp(kw, MON.w, tu), rh = lerp(kh, MON.h, tu);
  drawMonitorFrame(rx, ry, rw, rh, seg(t, 37.5, 37.9) * out);
  drawGame(t);
  ctx.save(); ctx.globalAlpha = out;
  ctx.beginPath(); ctx.roundRect(rx, ry, rw, rh, 10); ctx.clip();
  ctx.fillStyle = '#0B0D1C'; ctx.fillRect(rx, ry, rw, rh);
  if (t < 38.3) {
    // 所有像素几乎同时亮起
    const cols = 48, rows = 28; SMALL.width = cols; SMALL.height = rows; sctx.imageSmoothingEnabled = true; sctx.drawImage(GAME, 0, 0, cols, rows);
    const d = sctx.getImageData(0, 0, cols, rows).data; const pw = rw / cols, ph = rh / rows;
    for (let j = 0; j < rows; j++) for (let i = 0; i < cols; i++) {
      const st = 37.62 + rnd(i * 57 + j * 13) * 0.22; const u = back(seg(t, st, st + 0.2)); const k = (j * cols + i) * 4;
      const green = 1 - seg(t, st, st + 0.15);
      if (u <= 0) { ctx.fillStyle = '#173C33'; ctx.fillRect(rx + i * pw + 1, ry + j * ph + 1, pw - 2, ph - 2); continue; }
      ctx.fillStyle = green > 0.5 ? C.gpuL : `rgb(${d[k]},${d[k + 1]},${d[k + 2]})`;
      const s = clamp(u, 0, 1.25); ctx.fillRect(rx + i * pw + pw / 2 - (pw / 2) * s, ry + j * ph + ph / 2 - (ph / 2) * s, pw * s, ph * s);
    }
  } else {
    const res = Math.round(lerp(48, 480, eio(seg(t, 38.3, 39.2)))); const rh2 = Math.round(res * 276 / 480);
    SMALL.width = res; SMALL.height = rh2; sctx.imageSmoothingEnabled = true; sctx.drawImage(GAME, 0, 0, res, rh2);
    ctx.imageSmoothingEnabled = res >= 470; ctx.drawImage(SMALL, rx, ry, rw, rh);
  }
  ctx.restore();
  // 放大镜
  const ma = seg(t, 40.2, 40.6) * out;
  if (ma > 0) {
    const sx = 760, sy = 470, mx = 540, my = 1110, mr = 200 * eo(seg(t, 40.2, 40.6));
    ctx.save(); ctx.globalAlpha = ma;
    ctx.strokeStyle = C.white; ctx.lineWidth = 3; ctx.strokeRect(sx - 30, sy - 30, 60, 60);
    ctx.beginPath(); ctx.moveTo(sx, sy + 30); ctx.lineTo(mx, my - mr); ctx.stroke();
    ctx.beginPath(); ctx.arc(mx, my, mr, 0, Math.PI * 2); ctx.save(); ctx.clip();
    ctx.fillStyle = '#0B0D1C'; ctx.fillRect(mx - mr, my - mr, 2 * mr, 2 * mr);
    // 采样 9×9 像素
    const gx = (sx - MON.x) / MON.w * 480, gy = (sy - MON.y) / MON.h * 276;
    SMALL.width = 9; SMALL.height = 9; sctx.imageSmoothingEnabled = true; sctx.drawImage(GAME, gx - 14, gy - 14, 28, 28, 0, 0, 9, 9);
    const d = sctx.getImageData(0, 0, 9, 9).data; const ps = 46;
    for (let j = 0; j < 9; j++) for (let i = 0; i < 9; i++) {
      const k = (j * 9 + i) * 4; const x = mx - 4.5 * ps + i * ps, y = my - 4.5 * ps + j * ps;
      ctx.fillStyle = `rgb(${d[k]},${d[k + 1]},${d[k + 2]})`; ctx.fillRect(x + 2, y + 2, ps - 4, ps - 4);
      const fl = 0.5 + 0.5 * Math.sin(t * 9 + i * 1.7 + j * 2.3);
      ctx.fillStyle = `rgba(255,255,255,${0.35 + 0.55 * fl})`; ctx.font = `700 24px ${FM}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText('×', x + ps / 2, y + ps / 2 + 1);
    }
    ctx.restore();
    ctx.strokeStyle = C.white; ctx.lineWidth = 6; ctx.beginPath(); ctx.arc(mx, my, mr, 0, Math.PI * 2); ctx.stroke();
    ctx.fillStyle = 'rgba(8,9,26,0.85)'; rr(mx + 60, my - mr - 10, 360, 56, 28); ctx.fill();
    ctx.fillStyle = C.gpuL; ctx.font = `700 28px ${FB}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText('每个像素都是一道独立的题', mx + 240, my - mr + 18);
    ctx.restore();
  }
  // 2012
  const ya = seg(t, 43.6, 44.0) * (1 - seg(t, 48.0, 48.4));
  if (ya > 0) {
    ctx.save(); ctx.globalAlpha = ya;
    const ys = back(seg(t, 43.6, 44.0)); ctx.save(); ctx.translate(540, 300); ctx.scale(ys, ys);
    ctx.fillStyle = C.hi; ctx.font = `400 170px ${FT}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.shadowColor = hexA(C.hi, 0.5); ctx.shadowBlur = 40; ctx.fillText('2012', 0, 0); ctx.restore();
    [0, 1].forEach(i => {
      const u = eo(seg(t, 43.9 + i * 0.15, 44.4 + i * 0.15)); const x = 290 + i * 500, y = 540 + (1 - u) * 60;
      ctx.save(); ctx.globalAlpha = ya * u; drawBlower(x, y, 1, t); ctx.restore();
      ctx.save(); ctx.globalAlpha = ya * u; ctx.fillStyle = C.mute; ctx.font = `700 32px ${FB}`; ctx.textAlign = 'center'; ctx.fillText('游戏显卡 GTX 580', x, y + 108); ctx.restore();
    });
    // 两条箭头汇到照片
    const au = eio(seg(t, 44.5, 45.1));
    if (au > 0) {
      ctx.save(); ctx.strokeStyle = C.gpu; ctx.lineWidth = 6; ctx.setLineDash([16, 12]); ctx.lineDashOffset = -t * 60;
      [[290, 670, 250, 740], [790, 670, 560, 730]].forEach(([x0, y0, cx_, cy_]) => {
        const x1 = 300, y1 = 790; ctx.beginPath();
        const N = 24; for (let k = 0; k <= N * au; k++) { const u = k / N, x = (1 - u) * (1 - u) * x0 + 2 * u * (1 - u) * cx_ + u * u * x1, y = (1 - u) * (1 - u) * y0 + 2 * u * (1 - u) * cy_ + u * u * y1; k ? ctx.lineTo(x, y) : ctx.moveTo(x, y); }
        ctx.stroke();
      });
      ctx.restore();
    }
    // 照片
    const pu = back(seg(t, 45.0, 45.45));
    if (pu > 0) { ctx.save(); ctx.translate(280, 1010); const sc = 1.2 * clamp(pu, 0, 1.2); ctx.scale(sc, sc); drawCatPhoto(t); ctx.restore(); }
    // 猫 ✓
    const cu = back(seg(t, 46.3, 46.6));
    if (cu > 0) { ctx.save(); ctx.translate(440, 820); ctx.scale(cu, cu); ctx.fillStyle = C.gpu; rr(-90, -40, 180, 80, 40); ctx.fill(); ctx.fillStyle = '#0B1A14'; ctx.font = `900 46px ${FB}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText('猫 ✓', 0, 2); ctx.restore(); }
    // 错误率
    const bu = seg(t, 46.6, 47.5);
    if (bu > 0) {
      ctx.save(); ctx.globalAlpha = ya * seg(t, 46.6, 46.8); ctx.textBaseline = 'middle'; ctx.textAlign = 'left';
      ctx.fillStyle = C.white; ctx.font = `900 40px ${FB}`; ctx.fillText('前 5 错误率', 530, 880);
      ctx.fillStyle = C.mute; ctx.font = `400 28px ${FB}`; ctx.fillText('猜 5 次内猜中算对 · 越低越好', 530, 930);
      const rows = [['第二名', 26.2, '#7B819F'], ['AlexNet', 15.3, C.gpu]];
      rows.forEach(([lab, v, col], i) => {
        const y = 1040 + i * 125, e = eo(seg(bu, i * 0.3, 0.7 + i * 0.3)); const bw = 250 * v / 26.2 * e;
        ctx.fillStyle = i ? C.gpuL : C.mute; ctx.font = `700 32px ${FB}`; ctx.fillText(lab, 530, y - 40);
        ctx.fillStyle = col; rr(530, y - 18, Math.max(bw, 1), 44, 22); ctx.fill();
        ctx.fillStyle = C.white; ctx.font = `700 34px ${FM}`; ctx.fillText((v * e).toFixed(1) + '%', 544 + bw, y + 5);
      });
      ctx.restore();
    }
    ctx.restore();
  }
}
function drawBlower(x, y, s, t) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  ctx.fillStyle = '#8C93A8'; ctx.fillRect(-222, -52, 16, 104);
  ctx.fillStyle = '#143428'; ctx.fillRect(-205, 40, 400, 18); ctx.fillStyle = '#E3B341'; for (let i = 0; i < 18; i++) ctx.fillRect(-120 + i * 8, 56, 5, 8);
  const g = ctx.createLinearGradient(0, -55, 0, 50); g.addColorStop(0, '#3A3F57'); g.addColorStop(1, '#1C1F2E');
  ctx.fillStyle = g; rr(-205, -55, 410, 100, 14); ctx.fill(); ctx.strokeStyle = 'rgba(255,255,255,0.15)'; ctx.lineWidth = 2; ctx.stroke();
  ctx.strokeStyle = 'rgba(255,255,255,0.08)'; ctx.lineWidth = 4; for (let i = 0; i < 8; i++) { ctx.beginPath(); ctx.moveTo(-190 + i * 30, 35); ctx.lineTo(-170 + i * 30, -40); ctx.stroke(); }
  drawFan(130, -4, 42, t * 10, 0.3);
  ctx.restore();
}
function drawCatPhoto(t) {
  ctx.fillStyle = '#F4F6FF'; rr(-180, -170, 360, 340, 14); ctx.fill();
  const g = ctx.createLinearGradient(0, -150, 0, 150); g.addColorStop(0, '#BFE3FF'); g.addColorStop(1, '#FFE2C2'); ctx.fillStyle = g; ctx.fillRect(-160, -150, 320, 300);
  ctx.save(); ctx.translate(0, 30 + Math.sin(t * 2) * 3);
  ctx.fillStyle = '#F2A65A';
  ctx.beginPath(); ctx.moveTo(-95, -40); ctx.lineTo(-80, -135); ctx.lineTo(-25, -85); ctx.fill();
  ctx.beginPath(); ctx.moveTo(95, -40); ctx.lineTo(80, -135); ctx.lineTo(25, -85); ctx.fill();
  ctx.beginPath(); ctx.ellipse(0, -20, 110, 90, 0, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = '#D9843A'; for (let i = -1; i <= 1; i++) ctx.fillRect(i * 22 - 6, -105, 12, 30);
  const blink = (t % 3) > 2.85 ? 0.15 : 1;
  ctx.fillStyle = '#2A1C10'; ctx.beginPath(); ctx.ellipse(-40, -25, 12, 16 * blink, 0, 0, Math.PI * 2); ctx.fill(); ctx.beginPath(); ctx.ellipse(40, -25, 12, 16 * blink, 0, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = '#FF7A8A'; ctx.beginPath(); ctx.moveTo(-10, 5); ctx.lineTo(10, 5); ctx.lineTo(0, 16); ctx.fill();
  ctx.strokeStyle = '#2A1C10'; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(0, 16); ctx.quadraticCurveTo(-12, 30, -24, 22); ctx.moveTo(0, 16); ctx.quadraticCurveTo(12, 30, 24, 22); ctx.stroke();
  ctx.lineWidth = 2; [-1, 1].forEach(sd => { for (let k = 0; k < 3; k++) { ctx.beginPath(); ctx.moveTo(sd * 50, 8 + k * 9); ctx.lineTo(sd * 120, -4 + k * 14); ctx.stroke(); } });
  ctx.restore();
  // 识别框
  ctx.strokeStyle = C.gpu; ctx.lineWidth = 5; ctx.setLineDash([18, 10]); ctx.lineDashOffset = -t * 40; ctx.strokeRect(-130, -125, 260, 240); ctx.setLineDash([]);
}

// ---------- 场景 G：回到手机 48–57 ----------
function sceneG(t) {
  if (t < 47.9 || t > 57.4) return;
  const a = seg(t, 48.0, 48.5) * (1 - seg(t, 56.9, 57.2));
  // 背景大芯片
  ctx.save(); ctx.globalAlpha = a * 0.11;
  drawGPUDie(540, 900, 1500, (gi, gj) => 0.1 + 0.9 * Math.pow(Math.max(0, Math.sin(t * 3 - (gi + gj) * 0.05)), 3), {});
  ctx.restore();
  const pu = eo(seg(t, 48.0, 48.6));
  const land = t >= 49.0;
  ctx.save(); ctx.globalAlpha = a;
  drawPhone(540, 940 + (1 - pu) * 200, 1.05, land ? 8 : 7, t, { slot: !land, goldLast: true });
  ctx.restore();
  // 光 从上方落下
  const fu = seg(t, 48.5, 49.0);
  const sl = slotLocal(7), tx = 540 + sl.x * 1.05, ty = 940 + sl.y * 1.05;
  if (fu > 0 && fu < 1) {
    const e = ei(fu), x = lerp(540, tx, e), y = lerp(560, ty, e);
    glowDot(x, y, 120, C.hi, 0.7); ctx.fillStyle = C.hi; ctx.font = `700 ${lerp(120, 40, e)}px ${FB}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText('光', x, y);
  }
  if (t > 49.0 && t < 50.2) {
    const u = seg(t, 49.0, 50.2); ctx.save(); ctx.globalAlpha = a * (1 - u);
    for (let i = 0; i < 14; i++) { const ang = i / 14 * Math.PI * 2, r = 30 + u * 220; ctx.fillStyle = i % 2 ? C.hi : C.gpu; ctx.beginPath(); ctx.arc(tx + Math.cos(ang) * r, ty + Math.sin(ang) * r, 6 * (1 - u) + 2, 0, Math.PI * 2); ctx.fill(); }
    ctx.restore();
  }
  // 标题：问题 → 答案
  const q = seg(t, 48.0, 48.4) * (1 - seg(t, 50.2, 50.5));
  bigTitle(['AI 为什么', '非要用{显卡}？'], 225, q * a);
  const ans1 = seg(t, 50.4, 50.8) * a, ans2 = back(seg(t, 52.8, 53.2));
  if (ans1 > 0) {
    bigTitle(['AI 要的不是天才'], 225, ans1, { size: 120 });
    if (ans2 > 0) bigTitle(['而是{人多}'], 375, a * clamp(ans2), { size: 130, scale: [clamp(ans2, 0, 1.3)] });
  }
}

// ---------- 片尾 57–60 ----------
function sceneEnd(t) {
  if (t < 56.9) return;
  const a = seg(t, 57.0, 57.4);
  ctx.save(); ctx.globalAlpha = a;
  for (let j = 0; j < 14; j++) for (let i = 0; i < 24; i++) {
    const x = 60 + i * 40, y = 1150 + j * 40; const b = 0.5 + 0.5 * Math.sin(t * 4 - i * 0.4 + j * 0.7 + rnd(i * 14 + j) * 3);
    ctx.fillStyle = mix('#173C33', C.gpuL, b * 0.7); ctx.globalAlpha = a * (1 - j / 14) * 0.9; rr(x, y, 30, 30, 6); ctx.fill();
  }
  ctx.globalAlpha = a; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.shadowColor = hexA(C.gpu, 0.5); ctx.shadowBlur = 50;
  ctx.fillStyle = C.white; ctx.font = `400 150px ${FT}`; ctx.fillText('芯片与光', 540, 620);
  ctx.shadowBlur = 0;
  ctx.fillStyle = C.mute; ctx.font = `700 40px ${FB}`; ctx.fillText('剑桥材料学博士 · 半导体', 540, 760);
  ctx.fillStyle = C.white; ctx.font = `900 46px ${FB}`; ctx.fillText('你还想知道芯片的什么？', 540, 940);
  ctx.fillStyle = C.hi; ctx.fillText('评论区告诉我', 540, 1015);
  ctx.restore();
}

function render(t) {
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.imageSmoothingEnabled = true;
  bg(t);
  sceneA(t); sceneB(t); sceneMosaic(t); sceneC(t); sceneD(t); sceneE(t); sceneF(t); sceneG(t); sceneEnd(t);
  drawNotes(t); drawCaptions(t);
}
window.render = render; window.DUR = DUR;
window.ready = Promise.all([document.fonts.load(`400 100px ${FT}`), document.fonts.load(`700 60px ${FB}`), document.fonts.load(`900 60px ${FB}`), document.fonts.load(`700 30px ${FM}`)]).then(() => { render(0); return true; });
