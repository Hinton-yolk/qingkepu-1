'use strict';
// AI 为什么非要用显卡？ 60 秒竖屏动画。render(t) 是纯函数：给定秒数画一帧。
const W = 1080, H = 1920, DUR = 78;
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

function wColor(w) {
  const base = '#1A1F3A';
  return mix(base, w >= 0 ? '#3BA9FF' : '#FF5C8A', 0.3 + 0.7 * Math.abs(w));
}

// 格子海纹理：1024×1024，每个像素 = 一道乘法；中间 8×5 和数字表一致
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
const AI_TXT = '周末我想去海边看日落';
const PH = { w: 500, h: 640, sw: 472, sh: 612, tx: -136, ty: -14, cw: 34 };
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
  ctx.font = `500 32px ${FB}`; const ut = '帮我写一句周末计划'; const uw = ctx.measureText(ut).width + 48;
  ctx.fillStyle = '#4D7CFF'; rr(212 - uw, -150, uw, 64, 26); ctx.fill();
  ctx.fillStyle = '#fff'; ctx.textAlign = 'left'; ctx.fillText(ut, 212 - uw + 24, -117);
  // avatar
  const ag = ctx.createLinearGradient(-220, -40, -172, 8); ag.addColorStop(0, '#7B5CFF'); ag.addColorStop(1, '#3DF5B0');
  ctx.fillStyle = ag; ctx.beginPath(); ctx.arc(-196, -14, 24, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = '#fff'; ctx.font = `700 26px ${FB}`; ctx.textAlign = 'center'; ctx.fillText('✦', -196, -13);
  // AI bubble
  const shown = Math.min(n, AI_TXT.length), slot = shown < AI_TXT.length && opt.slot !== false;
  const bwid = 48 + Math.max(shown + (slot ? 1 : 0), opt.ghost > 0 ? AI_TXT.length : 0) * PH.cw;
  ctx.fillStyle = '#FFFFFF'; rr(-160, -54, bwid, 80, 26); ctx.fill();
  ctx.strokeStyle = 'rgba(30,35,60,0.10)'; ctx.lineWidth = 2; ctx.stroke();
  ctx.font = `500 ${PH.cw}px ${FB}`; ctx.textAlign = 'center';
  for (let i = 0; i < shown; i++) {
    const isLast = opt.goldLast && i === AI_TXT.length - 1;
    ctx.fillStyle = isLast ? '#E0A400' : '#1B1E2E';
    ctx.fillText(AI_TXT[i], PH.tx + i * PH.cw + PH.cw / 2, PH.ty);
  }
  if (opt.ghost > 0) { ctx.fillStyle = `rgba(27,30,46,${0.25 * opt.ghost})`; for (let i = shown + 1; i < AI_TXT.length; i++) ctx.fillText(AI_TXT[i], PH.tx + i * PH.cw + PH.cw / 2, PH.ty); }
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

// ================= EP.01 场景 =================
const CAPS = [
  [0.0, 2.2, '它不是在打字给你看'],
  [2.2, 5.4, '你以为它早就写好了整段，\n故意一个字一个字放给你看？'],
  [5.4, 8.2, '不是。\n它真的只能{一个字一个字}地写'],
  [8.2, 11.2, '每写一个字，\n都要把模型{从头到尾}过一遍'],
  [11.2, 14.0, '还要回头看一遍\n{前面所有的字}'],
  [14.0, 17.0, '给每个可能的下一个字\n{打个分}'],
  [17.0, 19.8, '{抽}一个，接上，再来一遍'],
  [19.8, 22.6, '为什么不能\n{几个字一起写}？'],
  [22.6, 25.4, '这里选了「海」，\n后面是「边看日落」'],
  [25.4, 28.2, '选了「睡」，\n后面就成了「个懒觉」'],
  [28.2, 31.4, '前一个字没定，\n后面的字{没法写}'],
  [31.4, 34.8, '显卡再多核，\n也只能{一个字接一个字}'],
  [34.8, 38.2, '可 AI {学说话}的时候，\n一整段能同时算', '类比'],
  [38.2, 41.6, '因为整段话是{现成的}：\n不用等它自己选下一个字'],
  [41.6, 44.4, '那就先造一段\n{「现成的」话}'],
  [44.4, 47.4, '让一个小模型\n先{抢答}几个字', '类比'],
  [47.4, 50.6, '大模型{一次全部批改}', '类比'],
  [50.6, 54.0, '批改 4 个字，\n和写 1 个字{差不多快}'],
  [54.0, 57.6, '因为最慢的不是算，\n是把参数{从显存搬过来}'],
  [57.6, 60.8, '搬一趟，\n就能{顺便批好几个字}'],
  [60.8, 64.4, '对得上的全收下，\n从第一个对不上的{接着来}'],
  [64.4, 67.8, '一步就出好几个字，\n快 {2–3 倍}'],
  [67.8, 71.0, '一个字一个字蹦，是因为\n{下一个字要等上一个}'],
  [71.6, 75.0, '用这个办法，它可以\n{几个字几个字}地蹦了'],
];
const NOTES = [
  [5.6, 8.2, '有的 App 会再匀速显示，但模型确实是一个个生成的'],
  [8.4, 11.2, '动辄几百亿个参数\n混合专家模型每个字只用其中一部分，但每一层都要过'],
  [11.4, 14.0, '前面的字算过的结果存着，不重算；但每次都要再看一遍\n句子越长，线越多'],
  [14.2, 17.0, '分数为示意'],
  [17.2, 19.8, '通常按分数抽签（也可以设成总选第一名）'],
  [31.6, 34.8, '每层里的乘加是并行算的；同一句话里，字和字之间只能排队\n实际服务会把很多人的请求拼在一起算'],
  [35.0, 38.2, '学说话 = 训练'],
  [38.4, 41.6, '训练时拿现成的文章让它逐字猜，猜完一起对答案'],
  [44.6, 47.4, '小模型参数少得多，写得快，但没那么准'],
  [47.6, 50.6, '这种方法叫投机解码（speculative decoding）'],
  [50.8, 54.0, '单条对话时'],
  [54.2, 57.6, '一个字一个字写的时候，显卡大多在等参数搬过来'],
  [61.0, 64.4, '对不上的字后面的草稿，是接着它猜的，一起作废'],
  [64.6, 67.8, '论文实测，单条对话，因模型而异\n数学上保证和大模型自己逐字写的一样（标准做法）'],
  [68.0, 71.0, '示意：用了投机解码后的效果'],
];

// ---------- 字块 ----------
const TK = { w: 72, h: 84, step: 80 };
// st: 'n' 普通 | 'slot' 黄色描边 ? | 'gray' 灰色 ? | 'draft' 草稿（虚线框）| 'ok' 绿勾 | 'no' 作废 | 'hi' 黄色高亮 | 'new' 新字（发光）
function token(x, y, ch, st = 'n', a = 1, s = 1, t = 0) {
  if (a <= 0) return;
  const w = TK.w, h = TK.h;
  ctx.save(); ctx.globalAlpha *= a; ctx.translate(x + w / 2, y + h / 2); ctx.scale(s, s);
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.font = `700 50px ${FB}`;
  if (st === 'slot') {
    const p = 0.5 + 0.5 * Math.sin(t * 8);
    ctx.fillStyle = hexA(C.hi, 0.12 + 0.12 * p); rr(-w / 2, -h / 2, w, h, 14); ctx.fill();
    ctx.strokeStyle = C.hi; ctx.lineWidth = 4; ctx.stroke(); ctx.fillStyle = C.hi; ctx.fillText(ch || '?', 0, 2);
  } else if (st === 'gray') {
    ctx.fillStyle = '#262A44'; rr(-w / 2, -h / 2, w, h, 14); ctx.fill(); ctx.fillStyle = '#5A6080'; ctx.fillText('?', 0, 2);
  } else if (st === 'draft') {
    ctx.fillStyle = 'rgba(244,246,255,0.14)'; rr(-w / 2, -h / 2, w, h, 14); ctx.fill();
    ctx.setLineDash([10, 7]); ctx.strokeStyle = C.white; ctx.lineWidth = 3; ctx.stroke(); ctx.setLineDash([]);
    ctx.fillStyle = C.white; ctx.fillText(ch, 0, 2);
  } else if (st === 'no') {
    ctx.fillStyle = 'rgba(244,246,255,0.08)'; rr(-w / 2, -h / 2, w, h, 14); ctx.fill();
    ctx.fillStyle = 'rgba(244,246,255,0.3)'; ctx.fillText(ch, 0, 2);
    ctx.strokeStyle = C.white; ctx.lineWidth = 5; ctx.beginPath(); ctx.moveTo(-22, -22); ctx.lineTo(22, 22); ctx.moveTo(22, -22); ctx.lineTo(-22, 22); ctx.stroke();
  } else {
    const hi = st === 'hi';
    ctx.fillStyle = hi ? C.hi : '#F4F6FF'; rr(-w / 2, -h / 2, w, h, 14); ctx.fill();
    ctx.fillStyle = '#1B1E2E'; ctx.fillText(ch, 0, 2);
    if (st === 'new') { ctx.strokeStyle = C.hi; ctx.lineWidth = 5; rr(-w / 2 - 4, -h / 2 - 4, w + 8, h + 8, 16); ctx.stroke(); }
    if (st === 'ok') { ctx.fillStyle = C.gpu; ctx.beginPath(); ctx.arc(w / 2 - 6, -h / 2 + 6, 17, 0, Math.PI * 2); ctx.fill(); ctx.strokeStyle = '#0B1A14'; ctx.lineWidth = 4; ctx.beginPath(); ctx.moveTo(w / 2 - 14, -h / 2 + 6); ctx.lineTo(w / 2 - 8, -h / 2 + 12); ctx.lineTo(w / 2 + 2, -h / 2); ctx.stroke(); }
  }
  ctx.restore();
}
function bookmark(x, y, a) { // 存档标记
  if (a <= 0) return; ctx.save(); ctx.globalAlpha *= a; ctx.fillStyle = C.num;
  ctx.beginPath(); ctx.moveTo(x + TK.w - 22, y - 6); ctx.lineTo(x + TK.w - 6, y - 6); ctx.lineTo(x + TK.w - 6, y + 18); ctx.lineTo(x + TK.w - 14, y + 11); ctx.lineTo(x + TK.w - 22, y + 18); ctx.closePath(); ctx.fill(); ctx.restore();
}
function rowX(n, cx = 540) { return cx - (n * TK.step - (TK.step - TK.w)) / 2; }

// ---------- 模型：一摞粉蓝格子 ----------
function stack(cx, cy, s, t, opt = {}) {
  const layers = opt.layers || 4, scan = opt.scan == null ? -1 : opt.scan, a = opt.alpha == null ? 1 : opt.alpha;
  if (a <= 0) return;
  const cols = 10, rows = 6, cs = 34 * s, gw = cols * cs, gh = rows * cs;
  ctx.save(); ctx.globalAlpha *= a;
  for (let k = layers - 1; k >= 0; k--) {
    const ox = cx - gw / 2 + k * 26 * s, oy = cy - gh / 2 - k * 30 * s;
    const lit = scan >= 0 ? clamp(1 - Math.abs(scan * layers - (layers - 1 - k) - 0.5) * 1.2) : 0;
    ctx.fillStyle = 'rgba(8,9,26,0.85)'; rr(ox - 8 * s, oy - 8 * s, gw + 16 * s, gh + 16 * s, 10 * s); ctx.fill();
    ctx.strokeStyle = hexA(C.white, 0.15 + 0.6 * lit); ctx.lineWidth = 2; ctx.stroke();
    for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
      const w = rnd(k * 97 + r * 13 + c * 7) * 2 - 1;
      ctx.fillStyle = mix(wColor(w), '#FFFFFF', lit * 0.45 + 0.08 * Math.max(0, Math.sin(t * 2 + r + c * 0.6 + k)));
      ctx.fillRect(ox + c * cs + 2, oy + r * cs + 2, cs - 4, cs - 4);
    }
  }
  ctx.restore();
}

// ---------- 场景 0：开头手机 0–8.2 ----------
const A_T = [-0.6, -0.25, 0.1, 0.45, 0.8];   // 第 0 帧已经蹦出「周末」，正在往外蹦   // 周 末 我 想 去 出现的时刻
function nShown(t) { let n = 0; A_T.forEach(x => { if (t >= x) n++; }); return n; }
function scene0(t) {
  if (t > 8.6) return;
  const PCX = 540, PCY = 900, PS = 1.22;
  const z = seg(t, 7.2, 8.2), zu = ei(z);
  const n = nShown(t); const sl = slotLocal(5); const F = { x: PCX + sl.x * PS, y: PCY + sl.y * PS };
  ctx.save();
  if (z > 0) { const s = 1 + zu * 14; ctx.translate(lerp(F.x, 540, zu), lerp(F.y, 360 + TK.h / 2, zu)); ctx.scale(s, s); ctx.translate(-F.x, -F.y); }
  const ta = 1 - seg(t, 2.2, 2.6);
  bigTitle(['AI 为什么'], 200, ta, { size: 120 });
  bigTitle(['{一个字一个字}往外蹦？'], 330, ta, { size: 96 });
  // 字上的闪光
  const g = seg(t, 2.4, 2.8) * (1 - seg(t, 5.4, 5.8));
  drawPhone(PCX, PCY, PS, n, t, { slot: true, ghost: g });
  A_T.forEach((x, k) => { const d = t - x; if (d < 0 || d > 0.4) return; const p = slotLocal(k); glowDot(PCX + p.x * PS, PCY + p.y * PS, 70, C.hi, 0.7 * (1 - d / 0.4)); });
  // ✕
  const xu = back(seg(t, 5.0, 5.3)), xa = seg(t, 5.0, 5.1) * (1 - seg(t, 5.6, 6.0));
  if (xa > 0) {
    ctx.save(); ctx.globalAlpha = xa; ctx.translate(PCX + 30, PCY - 15); ctx.scale(xu, xu);
    ctx.strokeStyle = C.white; ctx.lineWidth = 26; ctx.lineCap = 'round';
    ctx.shadowColor = 'rgba(0,0,0,0.5)'; ctx.shadowBlur = 20;
    ctx.beginPath(); ctx.moveTo(-120, -120); ctx.lineTo(120, 120); ctx.moveTo(120, -120); ctx.lineTo(-120, 120); ctx.stroke();
    ctx.restore();
  }
  // ✕ 碎片
  if (t > 5.6 && t < 6.6) {
    const u = seg(t, 5.6, 6.6);
    for (let i = 0; i < 18; i++) { const ang = rnd(i) * 6.28, r = u * (160 + rnd(i + 3) * 200); ctx.fillStyle = hexA(C.white, 1 - u); ctx.fillRect(PCX + 30 + Math.cos(ang) * r, PCY - 15 + Math.sin(ang) * r, 14, 6); }
  }
  ctx.restore();
  if (z > 0) { ctx.fillStyle = hexA('#0C0F26', clamp((z - 0.5) / 0.5)); ctx.fillRect(0, 0, W, H); }
}

// ---------- 场景 1：接龙 8.2–19.8 ----------
const CTX5 = '周末我想去';
const CAND = [['海', 41], ['睡', 18], ['爬', 12], ['吃', 9], ['…', 20]];
const S1 = { y: 300, step: 100, s: 1.22 };
function scene1(t) {
  if (t < 7.9 || t > 20.3) return;
  const a = seg(t, 8.0, 8.3) * (1 - seg(t, 19.8, 20.2));
  ctx.save(); ctx.globalAlpha = a;
  const landed = t >= 19.1;
  const n = landed ? 7 : 6, ST = S1.step, x0 = 540 - (n * ST - (ST - TK.w)) / 2;
  for (let i = 0; i < 5; i++) {
    const isNew = i === 4 && t < 11.2;
    token(x0 + i * ST, S1.y, CTX5[i], isNew ? 'new' : 'n', 1, S1.s, t);
    bookmark(x0 + i * ST + 8, S1.y - 6, seg(t, 10.6, 11.0) * (i < 4 || t > 11.2 ? 1 : 0));
  }
  if (landed) { token(x0 + 5 * ST, S1.y, '海', 'new', 1, S1.s * back(seg(t, 19.1, 19.4)), t); token(x0 + 6 * ST, S1.y, '?', 'slot', 1, S1.s, t); }
  else token(x0 + 5 * ST, S1.y, '?', 'slot', 1, S1.s, t);
  // 一摞格子 = 模型
  const SX = 540, SY = 720;
  const scan = t >= 8.6 && t < 10.8 ? ((t - 8.6) / 1.1) % 1 : -1;
  stack(SX, SY, 1.4, t, { scan });
  ctx.save(); ctx.fillStyle = C.mute; ctx.font = `700 30px ${FB}`; ctx.textAlign = 'center'; ctx.fillText('模型（一层一层）', SX, SY + 200); ctx.restore();
  // 新字送进模型
  if (t > 8.4 && t < 10.8) {
    const u = ((t - 8.4) / 1.2) % 1; const sx = x0 + 4 * ST + TK.w / 2, sy = S1.y + TK.h;
    const x = lerp(sx, SX, eio(u)), y = lerp(sy, SY - 60, eio(u));
    glowDot(x, y, 40, C.hi, 0.9 * Math.sin(Math.PI * u));
  }
  // 回看细线
  const la = seg(t, 11.2, 11.6) * (1 - seg(t, 13.8, 14.2));
  if (la > 0) {
    const sx = x0 + 5 * ST + TK.w / 2, sy = S1.y - 14;
    for (let i = 0; i < 5; i++) {
      const ex = x0 + i * ST + TK.w / 2, u = eo(seg(t, 11.3 + i * 0.08, 11.9 + i * 0.08));
      const h = 60 + (5 - i) * 26;
      ctx.save(); ctx.globalAlpha = a * la; ctx.strokeStyle = hexA(C.num, 0.85); ctx.lineWidth = 3;
      ctx.beginPath(); ctx.moveTo(sx, sy);
      const N = 20; for (let k = 1; k <= N * u; k++) { const v = k / N; ctx.lineTo(lerp(sx, ex, v), sy - Math.sin(Math.PI * v) * h); }
      ctx.stroke(); ctx.restore();
      if (u >= 1) glowDot(ex, sy, 26, C.num, 0.5 + 0.3 * Math.sin(t * 6 + i));
    }
  }
  // 候选排行条
  const ca = seg(t, 14.0, 14.4) * (1 - seg(t, 16.9, 17.3));
  const BY = 990;
  if (ca > 0) {
    CAND.forEach(([ch, p], r) => {
      const y = BY + r * 70, bu = eo(seg(t, 14.2 + r * 0.08, 14.9 + r * 0.08)), bw = 520 * p / 41 * bu;
      ctx.save(); ctx.globalAlpha = a * ca;
      ctx.fillStyle = r === 0 ? C.hi : '#F4F6FF'; rr(170, y, 52, 52, 10); ctx.fill();
      ctx.fillStyle = '#1B1E2E'; ctx.font = `700 34px ${FB}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(ch, 196, y + 27);
      ctx.fillStyle = 'rgba(255,255,255,0.06)'; rr(240, y + 8, 520, 36, 18); ctx.fill();
      ctx.fillStyle = r === 0 ? C.hi : hexA(C.num, 0.7); rr(240, y + 8, Math.max(2, bw), 36, 18); ctx.fill();
      ctx.fillStyle = C.white; ctx.font = `700 30px ${FM}`; ctx.textAlign = 'left'; ctx.fillText(Math.round(p * bu) + '%', 254 + bw, y + 27);
      ctx.restore();
    });
  }
  // 抽签转盘
  const wa = seg(t, 17.0, 17.3) * (1 - seg(t, 19.5, 19.8));
  if (wa > 0) {
    const cx = 540, cy = 1165, R = 175;
    const spin = t < 18.6 ? (t - 17.0) * 9 * (1 - seg(t, 17.0, 18.6) * 0.6) : 0;
    const stopA = -Math.PI / 2 - (41 / 100) * Math.PI;   // 停在「海」扇区中间
    const ang = t < 18.6 ? stopA + 6.28 * 3 * (1 - eo(seg(t, 17.0, 18.6))) : stopA;
    ctx.save(); ctx.globalAlpha = a * wa; ctx.translate(cx, cy);
    let st = ang; const cols = [C.hi, C.num, C.blue, C.pink, '#4A5075'];
    CAND.forEach(([ch, p], i) => {
      const e = st + p / 100 * 6.283; ctx.fillStyle = cols[i]; ctx.beginPath(); ctx.moveTo(0, 0); ctx.arc(0, 0, R, st, e); ctx.closePath(); ctx.fill();
      ctx.strokeStyle = '#0C0F26'; ctx.lineWidth = 4; ctx.stroke();
      const m = (st + e) / 2; ctx.fillStyle = '#1B1E2E'; ctx.font = `700 40px ${FB}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(ch, Math.cos(m) * R * 0.66, Math.sin(m) * R * 0.66);
      st = e;
    });
    ctx.restore();
    ctx.save(); ctx.globalAlpha = a * wa; ctx.fillStyle = C.white; ctx.beginPath(); ctx.moveTo(cx, cy - R - 6); ctx.lineTo(cx - 20, cy - R - 44); ctx.lineTo(cx + 20, cy - R - 44); ctx.fill(); ctx.restore();
  }
  // 海 飞进空位
  const fu = seg(t, 18.6, 19.1);
  if (fu > 0 && fu < 1) {
    const e = eio(fu), x = lerp(540, x0 + 5 * ST + TK.w / 2, e), y = lerp(1165 - 175, S1.y + TK.h / 2, e);
    glowDot(x, y, 70, C.hi, 0.7); ctx.fillStyle = C.hi; ctx.font = `700 56px ${FB}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText('海', x, y);
  }
  ctx.restore();
}

// ---------- 场景 2：分叉 19.8–34.8 ----------
function scene2(t) {
  if (t < 19.6 || t > 35.2) return;
  const a = seg(t, 19.8, 20.2) * (1 - seg(t, 34.6, 35.0));
  ctx.save(); ctx.globalAlpha = a;
  const split = eio(seg(t, 21.0, 22.0)) * (1 - eio(seg(t, 28.2, 28.9)));
  const by = 820, x0 = 140;
  for (let i = 0; i < 5; i++) token(x0 + i * TK.step, by, CTX5[i], 'n', 1, 1, t);
  const fx = x0 + 5 * TK.step;
  // 分叉线
  if (split > 0) {
    ctx.save(); ctx.globalAlpha *= split; ctx.strokeStyle = hexA(C.hi, 0.7); ctx.lineWidth = 5;
    ctx.beginPath(); ctx.moveTo(fx - 4, by + TK.h / 2); ctx.bezierCurveTo(fx + 30, by + TK.h / 2, fx + 20, by - 150 + TK.h / 2, fx + 50, by - 150 + TK.h / 2);
    ctx.moveTo(fx - 4, by + TK.h / 2); ctx.bezierCurveTo(fx + 30, by + TK.h / 2, fx + 20, by + 150 + TK.h / 2, fx + 50, by + 150 + TK.h / 2); ctx.stroke(); ctx.restore();
    const up = '海边看日落', dn = '睡个懒觉';
    for (let i = 0; i < up.length; i++) { const u = back(seg(t, 22.7 + i * 0.25, 23.0 + i * 0.25)); token(fx + 50 + i * 76, by - 150, up[i], i === 0 ? 'hi' : 'n', split * clamp(u), clamp(u, 0, 1.2), t); }
    for (let i = 0; i < dn.length; i++) { const u = back(seg(t, 25.5 + i * 0.25, 25.8 + i * 0.25)); token(fx + 50 + i * 76, by + 150, dn[i], i === 0 ? 'hi' : 'n', split * clamp(u), clamp(u, 0, 1.2), t); }
    if (t < 22.7) { token(fx + 50, by - 150, '?', 'slot', split, 1, t); }
    if (t < 25.5) { token(fx + 50, by + 150, '?', 'slot', split, 1, t); }
  }
  // 一句：黄 ? + 灰 ?
  const one = seg(t, 28.6, 29.0);
  if (one > 0) {
    token(fx, by, '?', 'slot', one, 1, t);
    for (let i = 1; i < 5; i++) token(fx + i * TK.step, by, '?', 'gray', one * seg(t, 28.8 + i * 0.1, 29.1 + i * 0.1), 1, t);
  }
  // 显卡：一格一格往前推
  const ga = seg(t, 31.4, 31.9);
  if (ga > 0) {
    const step = Math.floor((t - 31.6) / 0.55), ph = ((t - 31.6) % 0.55) / 0.55;
    ctx.save(); ctx.globalAlpha *= ga;
    drawGPUDie(540, 430, 460, (gi, gj) => 0.25 + 0.5 * Math.exp(-ph * 4) * (0.6 + 0.4 * rnd(gi * 7 + gj * 13 + step)), {});
    ctx.restore();
    // 当前位置高亮
    if (t > 31.6) {
      const k = clamp(step, 0, 4); const x = fx + k * TK.step;
      ctx.save(); ctx.globalAlpha *= ga; ctx.strokeStyle = C.gpu; ctx.lineWidth = 5; rr(x - 8, by - 8, TK.w + 16, TK.h + 16, 18); ctx.stroke();
      ctx.strokeStyle = hexA(C.gpu, 0.5); ctx.setLineDash([8, 8]); ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(540, 660); ctx.lineTo(x + TK.w / 2, by - 10); ctx.stroke(); ctx.restore();
    }
  }
  ctx.restore();
}

// ---------- 场景 3：学说话 34.8–41.6 ----------
const FULL = '周末我想去海边看日落';
function scene3(t) {
  if (t < 34.6 || t > 42.0) return;
  const a = seg(t, 34.8, 35.3) * (1 - seg(t, 41.4, 41.8));
  ctx.save(); ctx.globalAlpha = a;
  ctx.fillStyle = '#EDE9DE'; rr(70, 500, 900, 600, 24); ctx.fill();
  ctx.fillStyle = '#6A6458'; ctx.font = `700 30px ${FB}`; ctx.textAlign = 'left'; ctx.fillText('现成的文章', 110, 560);
  const x0 = rowX(10);
  const allOk = t >= 39.4;
  for (let i = 0; i < 10; i++) {
    const u = eo(seg(t, 35.1 + i * 0.05, 35.5 + i * 0.05));
    token(x0 + i * TK.step, 650, FULL[i], allOk && i > 0 ? 'ok' : 'n', u, 1, t);
    if (i < 9) {
      const nu = seg(t, 38.4, 38.8);
      ctx.save(); ctx.globalAlpha *= nu; ctx.fillStyle = '#6A6458'; ctx.font = `700 26px ${FB}`; ctx.textAlign = 'center';
      ctx.fillText('↓', x0 + i * TK.step + TK.w / 2, 780); ctx.fillStyle = '#3A3630'; ctx.font = `700 34px ${FB}`; ctx.fillText(FULL[i + 1], x0 + i * TK.step + TK.w / 2, 830); ctx.restore();
    }
  }
  // 一起对答案：扫光
  if (t > 39.0 && t < 40.2) { const u = seg(t, 39.0, 40.2); ctx.save(); ctx.globalAlpha *= Math.sin(Math.PI * u); ctx.fillStyle = hexA(C.gpu, 0.35); rr(90, 630, 860, 230, 20); ctx.fill(); ctx.restore(); }
  ctx.save(); ctx.globalAlpha *= seg(t, 38.6, 39.0); ctx.fillStyle = '#2B6E58'; ctx.font = `900 40px ${FB}`; ctx.textAlign = 'center'; ctx.fillText('每个位置同时猜、同时对答案', 520, 1010); ctx.restore();
  ctx.restore();
}

// ---------- 场景 4：抢答 + 批改 41.6–50.6 ----------
const DRAFT = '海边吃饭';
function scene4(t) {
  if (t < 41.4 || t > 50.9) return;
  const a = seg(t, 41.6, 42.0) * (1 - seg(t, 50.4, 50.8));
  ctx.save(); ctx.globalAlpha = a;
  const by = 520, x0 = rowX(9);
  for (let i = 0; i < 5; i++) token(x0 + i * TK.step, by, CTX5[i], 'n', 1, 1, t);
  // 「海」退回
  if (t < 42.4) { const u = eio(seg(t, 41.6, 42.4)); token(x0 + 5 * TK.step, by - u * 120, '海', 'n', 1 - u, 1, t); }
  for (let i = 0; i < 4; i++) {
    const x = x0 + (5 + i) * TK.step, dt = 44.6 + i * 0.45;
    if (t < dt) token(x, by, '?', i === 0 ? 'slot' : 'gray', seg(t, 42.2, 42.6), 1, t);
    else token(x, by, DRAFT[i], 'draft', 1, back(seg(t, dt, dt + 0.2)), t);
  }
  // 小模型
  const sa = seg(t, 44.2, 44.6);
  if (sa > 0) {
    stack(300, 900, 0.6, t, { layers: 2, scan: t > 44.6 && t < 46.6 ? ((t - 44.6) / 0.45) % 1 : -1, alpha: sa * (t > 47.2 ? 0.4 : 1) });
    ctx.save(); ctx.globalAlpha *= sa; ctx.fillStyle = C.mute; ctx.font = `700 30px ${FB}`; ctx.textAlign = 'center'; ctx.fillText('小模型：抢答', 300, 1050); ctx.restore();
    for (let i = 0; i < 4; i++) {
      const dt = 44.6 + i * 0.45, u = seg(t, dt - 0.3, dt); if (u <= 0 || u >= 1) continue;
      const x = lerp(300, x0 + (5 + i) * TK.step + TK.w / 2, eio(u)), y = lerp(840, by + TK.h, eio(u));
      glowDot(x, y, 30, C.white, 0.9);
    }
  }
  // 大模型一次批改
  const ba = seg(t, 47.2, 47.6);
  if (ba > 0) {
    stack(700, 1000, 1.05, t, { alpha: ba, scan: t > 47.8 && t < 49.6 ? seg(t, 47.8, 49.0) : -1 });
    ctx.save(); ctx.globalAlpha *= ba; ctx.fillStyle = C.mute; ctx.font = `700 30px ${FB}`; ctx.textAlign = 'center'; ctx.fillText('大模型：一次批改', 700, 1190); ctx.restore();
    const su = seg(t, 48.2, 49.2);
    if (su > 0 && su < 1) {
      ctx.save(); ctx.globalCompositeOperation = 'lighter';
      const x = lerp(x0 + 5 * TK.step - 40, x0 + 9 * TK.step + 40, su);
      const g = ctx.createLinearGradient(x - 60, 0, x + 60, 0); g.addColorStop(0, 'rgba(255,255,255,0)'); g.addColorStop(0.5, 'rgba(255,255,255,0.7)'); g.addColorStop(1, 'rgba(255,255,255,0)');
      ctx.fillStyle = g; ctx.fillRect(x - 60, by - 20, 120, TK.h + 40); ctx.restore();
    }
    // 四条线同时从大模型连到四个字
    const lu = eo(seg(t, 48.0, 48.6));
    for (let i = 0; i < 4; i++) {
      const ex = x0 + (5 + i) * TK.step + TK.w / 2;
      ctx.save(); ctx.globalAlpha *= ba * 0.6; ctx.strokeStyle = C.white; ctx.lineWidth = 3;
      ctx.beginPath(); ctx.moveTo(700, 860); ctx.lineTo(lerp(700, ex, lu), lerp(860, by + TK.h + 6, lu)); ctx.stroke(); ctx.restore();
    }
  }
  ctx.restore();
}

// ---------- 场景 5：为什么批改快：搬一趟 50.6–60.8 ----------
function scene5(t) {
  if (t < 50.4 || t > 61.1) return;
  const a = seg(t, 50.6, 51.0) * (1 - seg(t, 60.6, 61.0));
  ctx.save(); ctx.globalAlpha = a;
  // 两个计时条
  const ta = 1 - seg(t, 53.8, 54.2);
  if (ta > 0) {
    ctx.save(); ctx.globalAlpha *= ta;
    const rows = [['写 1 个字', 1, 600], ['批改 4 个字', 4, 640]];
    rows.forEach(([lab, k, L], r) => {
      const y = 640 + r * 280, u = eo(seg(t, 51.0 + r * 0.15, 52.6 + r * 0.15));
      ctx.fillStyle = C.white; ctx.font = `900 44px ${FB}`; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.fillText(lab, 120, y);
      for (let i = 0; i < k; i++) token(560 + i * 70, y - 42, '字', r ? 'draft' : 'n', 1, 0.8, t);
      ctx.fillStyle = 'rgba(255,255,255,0.08)'; rr(120, y + 60, 800, 40, 20); ctx.fill();
      ctx.fillStyle = r ? C.gpu : C.num; rr(120, y + 60, Math.max(4, L * u), 40, 20); ctx.fill();
      ctx.fillStyle = C.mute; ctx.font = `700 28px ${FB}`; ctx.fillText('用时', 120, y + 130);
    });
    ctx.restore();
  }
  // 显存传送带
  const ca = seg(t, 54.0, 54.4);
  if (ca > 0) {
    ctx.save(); ctx.globalAlpha *= ca; ctx.translate(0, 90);
    // 显存
    ctx.fillStyle = 'rgba(8,9,26,0.85)'; rr(60, 430, 300, 420, 20); ctx.fill(); ctx.strokeStyle = hexA(C.cache, 0.9); ctx.lineWidth = 3; ctx.stroke();
    for (let r = 0; r < 10; r++) for (let c = 0; c < 6; c++) { ctx.fillStyle = wColor(rnd(r * 6 + c + 300) * 2 - 1); ctx.fillRect(84 + c * 44, 470 + r * 36, 38, 30); }
    ctx.fillStyle = C.white; ctx.font = `900 40px ${FB}`; ctx.textAlign = 'center'; ctx.fillText('显存', 210, 900);
    ctx.fillStyle = C.mute; ctx.font = `500 28px ${FB}`; ctx.fillText('几百亿个参数', 210, 945);
    // 传送带
    ctx.fillStyle = '#20243A'; rr(370, 615, 290, 50, 12); ctx.fill();
    for (let i = 0; i < 8; i++) { const x = 370 + ((t * 120 + i * 40) % 290); ctx.fillStyle = 'rgba(255,255,255,0.12)'; ctx.fillRect(x, 615, 4, 50); }
    // 搬运中的参数块：一拍一块
    const arrive = [];
    for (let i = 0; i < 12; i++) {
      const st = 54.2 + i * 0.5, u = seg(t, st, st + 0.5); if (u <= 0) continue;
      if (u < 1) { ctx.fillStyle = wColor(rnd(i + 900) * 2 - 1); ctx.fillRect(lerp(380, 640, u), 622, 36, 36); }
      else arrive.push(t - st - 0.5);
    }
    // 计算核心：大多暗着等，参数到了才亮一下
    const lastArr = arrive.length ? Math.min(...arrive) : 9;
    const flash = Math.exp(-lastArr * 6);
    drawGPUDie(840, 640, 320, (gi, gj) => 0.08 + 0.85 * flash * (0.6 + 0.4 * rnd(gi * 3 + gj * 5)), {});
    ctx.fillStyle = C.white; ctx.font = `900 40px ${FB}`; ctx.textAlign = 'center'; ctx.fillText('计算核心', 840, 900);
    ctx.fillStyle = C.mute; ctx.font = `500 28px ${FB}`; ctx.fillText('大多在等', 840, 945);
    ctx.restore();
  }
  // 搬一趟，四个位置一起用
  const fa = seg(t, 57.6, 58.0);
  if (fa > 0) {
    const x0 = rowX(4), y = 1170;
    for (let i = 0; i < 4; i++) {
      token(x0 + i * TK.step, y, DRAFT[i], 'draft', fa, 1, t);
      const pu = (t - 58.2) % 1.0; const lit = t > 58.2 ? Math.exp(-pu * 3) : 0;
      ctx.save(); ctx.globalAlpha *= fa * lit; ctx.strokeStyle = C.gpu; ctx.lineWidth = 5; rr(x0 + i * TK.step - 6, y - 6, TK.w + 12, TK.h + 12, 16); ctx.stroke(); ctx.restore();
      ctx.save(); ctx.globalAlpha *= fa * 0.5; ctx.strokeStyle = C.gpu; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(840, 900); ctx.lineTo(x0 + i * TK.step + TK.w / 2, y - 8); ctx.stroke(); ctx.restore();
    }
  }
  ctx.restore();
}

// ---------- 场景 6：收下 / 作废，2–3 倍 60.8–67.8 ----------
function scene6(t) {
  if (t < 60.6 || t > 68.1) return;
  const a = seg(t, 60.8, 61.2) * (1 - seg(t, 67.6, 68.0));
  ctx.save(); ctx.globalAlpha = a;
  const ra = 1 - seg(t, 64.2, 64.6);
  if (ra > 0) {
    ctx.save(); ctx.globalAlpha *= ra;
    const by = 720, x0 = rowX(9);
    for (let i = 0; i < 5; i++) token(x0 + i * TK.step, by, CTX5[i], 'n', 1, 1, t);
    const st = [61.3, 61.7, 62.2, 62.7];
    for (let i = 0; i < 4; i++) {
      const x = x0 + (5 + i) * TK.step;
      if (t < st[i]) { token(x, by, DRAFT[i], 'draft', 1, 1, t); continue; }
      if (i < 2) token(x, by, DRAFT[i], 'ok', 1, back(seg(t, st[i], st[i] + 0.2)), t);
      else token(x, by, DRAFT[i], 'no', 1, 1, t);
    }
    // 大模型自己的「看」
    const ku = back(seg(t, 62.4, 62.8));
    if (ku > 0) { token(x0 + 7 * TK.step, by + 140, '看', 'hi', clamp(ku), clamp(ku, 0, 1.2), t); ctx.save(); ctx.fillStyle = C.mute; ctx.font = `700 28px ${FB}`; ctx.textAlign = 'center'; ctx.fillText('大模型自己的字', x0 + 7 * TK.step + TK.w / 2, by + 270); ctx.restore(); }
    // 「饭」作废的原因
    const ea = seg(t, 62.9, 63.3);
    if (ea > 0) { ctx.save(); ctx.globalAlpha *= ea; ctx.strokeStyle = hexA(C.mute, 0.8); ctx.lineWidth = 3; ctx.setLineDash([8, 6]); ctx.beginPath(); ctx.moveTo(x0 + 7 * TK.step + TK.w / 2, by - 10); ctx.quadraticCurveTo(x0 + 7.5 * TK.step + TK.w / 2, by - 90, x0 + 8 * TK.step + TK.w / 2, by - 10); ctx.stroke(); ctx.fillStyle = C.mute; ctx.font = `700 26px ${FB}`; ctx.textAlign = 'center'; ctx.fillText('接着「吃」猜的', x0 + 7.5 * TK.step + TK.w / 2, by - 100); ctx.restore(); }
    ctx.restore();
  }
  // 2–3 倍
  const ba = seg(t, 64.4, 64.8);
  if (ba > 0) {
    ctx.save(); ctx.globalAlpha *= ba;
    ctx.fillStyle = C.mute; ctx.font = `700 34px ${FB}`; ctx.textAlign = 'left'; ctx.textBaseline = 'middle';
    ctx.fillText('原来：一步 1 个字', 110, 560); ctx.fillText('现在：一步好几个字', 110, 740);
    const k1 = Math.floor(((t - 64.6) % 1.2) / 1.2 * 1) + 1;
    token(520, 518, '字', 'n', 1, 0.8, t);
    for (let i = 0; i < 3; i++) token(560 + i * 74, 698, '字', 'n', seg(t, 64.9 + i * 0.12, 65.1 + i * 0.12), 0.8, t);
    const s = back(seg(t, 65.4, 65.8));
    ctx.save(); ctx.translate(540, 1030); ctx.scale(s, s); ctx.fillStyle = C.hi; ctx.font = `400 230px ${FT}`; ctx.textAlign = 'center'; ctx.shadowColor = hexA(C.hi, 0.5); ctx.shadowBlur = 50; ctx.fillText('2–3 倍', 0, 0); ctx.restore();
    ctx.restore();
  }
  ctx.restore();
}

// ---------- 场景 7：回到开头 67.8–75；片尾 75–78 ----------
const CHUNKS = [[68.3, 5], [69.0, 8], [69.6, 10]];
function scene7(t) {
  if (t < 67.6 || t > 75.3) return;
  const a = seg(t, 67.8, 68.2) * (1 - seg(t, 74.8, 75.2));
  ctx.save(); ctx.globalAlpha = a;
  const pa = 1 - seg(t, 70.8, 71.2);
  if (pa > 0) {
    ctx.save(); ctx.globalAlpha *= pa;
    let n = 0; CHUNKS.forEach(([tt, k]) => { if (t >= tt) n = k; });
    drawPhone(540, 860, 1.15, n, t, { slot: n < 10 });
    ctx.strokeStyle = hexA(C.mute, 0.9); ctx.setLineDash([14, 10]); ctx.lineWidth = 3; rr(225, 450, 630, 820, 40); ctx.stroke(); ctx.setLineDash([]);
    ctx.fillStyle = 'rgba(8,9,26,0.85)'; rr(245, 428, 110, 44, 22); ctx.fill(); ctx.fillStyle = C.mute; ctx.font = `700 26px ${FB}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText('示意', 300, 450);
    ctx.restore();
  }
  const ea = seg(t, 71.0, 71.4);
  if (ea > 0) {
    bigTitle(['写，要{一个字一个字}写；'], 640, a * ea, { size: 92 });
    bigTitle(['批改，可以{一起批}'], 800, a * seg(t, 71.5, 71.9), { size: 92, scale: [back(seg(t, 71.5, 71.9))] });
  }
  ctx.restore();
}
function sceneEnd(t) {
  if (t < 74.9) return;
  const a = seg(t, 75.0, 75.4);
  ctx.save(); ctx.globalAlpha = a; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  for (let j = 0; j < 12; j++) for (let i = 0; i < 24; i++) {
    const b = 0.5 + 0.5 * Math.sin(t * 4 - i * 0.4 + j * 0.7 + rnd(i * 14 + j) * 3);
    ctx.globalAlpha = a * (1 - j / 12) * 0.9; ctx.fillStyle = mix('#173C33', C.gpuL, b * 0.7); rr(60 + i * 40, 1150 + j * 40, 30, 30, 6); ctx.fill();
  }
  ctx.globalAlpha = a; ctx.shadowColor = hexA(C.gpu, 0.5); ctx.shadowBlur = 50;
  ctx.fillStyle = C.hi; ctx.font = `400 120px ${FT}`; ctx.fillText('EP.01', 540, 470);
  ctx.fillStyle = C.white; ctx.font = `400 96px ${FT}`; ctx.fillText('一个字一个字往外蹦', 540, 610);
  ctx.shadowBlur = 0; ctx.fillStyle = C.mute; ctx.font = `700 38px ${FB}`; ctx.fillText('〔系列名待定〕 · 芯片与光 · 剑桥材料学博士', 540, 730);
  ctx.fillStyle = C.white; ctx.font = `900 46px ${FB}`; ctx.fillText('你还想知道 AI 的什么？', 540, 900);
  ctx.fillStyle = C.hi; ctx.fillText('评论区告诉我', 540, 975);
  ctx.restore();
}

function render(t) {
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.imageSmoothingEnabled = true;
  bg(t);
  scene0(t); scene1(t); scene2(t); scene3(t); scene4(t); scene5(t); scene6(t); scene7(t); sceneEnd(t);
  drawNotes(t); drawCaptions(t);
}
window.render = render; window.DUR = DUR;
window.ready = Promise.all([document.fonts.load(`400 100px ${FT}`), document.fonts.load(`700 60px ${FB}`), document.fonts.load(`900 60px ${FB}`), document.fonts.load(`500 30px ${FB}`), document.fonts.load(`700 30px ${FM}`)]).then(() => { render(0); return true; });
