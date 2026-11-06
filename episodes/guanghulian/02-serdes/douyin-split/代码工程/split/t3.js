// 第 3 条（第三稿）：AI 芯片「速度翻倍」，该信几分？——先问三句：什么路、多少电、跑通没有。只讲怎么问，不点名、不荐股。
(() => {
const { clamp, lerp } = U; const { W, H, COL, T, kw, txt, tape, tag, pop, ease, seg, hookText, L } = SP;
SP.END = 'z14';
const R = (s) => U.rng(s);
const GOLD = [245, 215, 126], CORAL = [239, 125, 98], MINT = [127, 214, 180], TEAL = [155, 232, 219];
const glowDot = (c, x, y, r, col = GOLD, a = 1) => { c.save(); c.globalCompositeOperation = 'lighter'; const g = c.createRadialGradient(x, y, 0, x, y, r * 3); g.addColorStop(0, `rgba(255,250,235,${a})`); g.addColorStop(0.3, `rgba(${col},${0.85 * a})`); g.addColorStop(1, `rgba(${col},0)`); c.fillStyle = g; c.beginPath(); c.arc(x, y, r * 3, 0, 7); c.fill(); c.restore(); };
// 一段信号（屏幕空间）：blur 0 = 方方正正，1 = 糊成一片；jit = 抖动（实测）
const BITS = [1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1];
const sigPts = (x0, x1, yC, amp, blur, off, bw = 60, jit = 0, seed = 1) => { const tau = 2 + blur * bw * 0.9, a = Math.exp(-3 / tau); let y = 0; const P = []; const r = R(seed);
  for (let x = x0 - 300; x <= x1; x += 3) { const kk = Math.floor((x + off) / bw), tg = BITS[((kk % BITS.length) + BITS.length) % BITS.length] ? 1 : -1; y = blur < 0.01 ? tg : a * y + (1 - a) * tg;
    if (x >= x0) P.push([x, yC - y * amp * (1 - 0.45 * blur) + (jit ? (r() - .5) * jit : 0)]); } return P; };
const qcard = (c, n, s, x, y, t, at, { on = true, w = 860 } = {}) => { if (t < at) return; const q = Math.min(1, pop(t, at, 0.25));
  c.save(); c.translate(x, y); c.scale(0.85 + 0.15 * q, 0.85 + 0.15 * q); c.globalAlpha = q * (on ? 1 : 0.4); c.translate(-w / 2, -50);
  c.fillStyle = COL.cream; CL.tornRect(c, w, 100, n * 13 + 3, 3); c.fill();
  c.fillStyle = COL.red; c.beginPath(); c.arc(58, 50, 36, 0, 7); c.fill(); txt(c, String(n), 58, 52, { size: 46, fam: 'PuHui-Heavy', col: '#f6efe4', align: 'center' });
  txt(c, s, 116, 52, { size: 50, fam: 'PuHui-Heavy', col: COL.ink }); c.restore(); };

// ---------- 1. 新闻天天说速度翻倍 → 最高时速 300，没说什么路 → 先问三个问题 ----------
SP.MECH.news = (c, t, sh) => {
  const k = T.cam({ hy: 1480, camH: 300 }); T.bg(c, k, { scroll: t * 220, grid: 0.5 }); T.streams(c, t, { a: 0.2, seed: 9 });
  const t3 = L.z03.t0, tRoad = kw('z03', '什么路上'), t4 = L.z04.t0;
  const nq = 1 - ease(t, t3 - 0.2, t3 + 0.4, 'c');
  if (nq > 0) { c.save(); c.globalAlpha = nq; const HL = ['新一代 AI 芯片：互连速度翻倍', '传输速度再翻一倍！', '每条通道冲上 200G'];
    HL.forEach((s, i) => { const at = i === 0 ? -1 : i === 1 ? L.z01.t1 : L.z02.t0; if (t < at) return; const q = Math.min(1, pop(t, at)), y = 660 + i * 230 + 10 * Math.sin(t * 1.7 + i * 2), r = (i - 1) * 0.04 + 0.02 * Math.sin(t * 1.3 + i);
      c.save(); c.translate(W / 2, y); c.rotate(r); c.scale(q, q); c.shadowColor = 'rgba(0,0,0,.6)'; c.shadowBlur = 24; c.shadowOffsetY = 10; c.fillStyle = '#f6f2ea'; c.beginPath(); c.roundRect(-430, -95, 860, 190, 12); c.fill(); c.shadowColor = 'transparent';
      c.fillStyle = COL.red; c.fillRect(-430, -95, 14, 190); txt(c, '科技快讯', -390, -48, { size: 28, fam: 'PuHui-Heavy', col: COL.red }); txt(c, s, -390, 18, { size: 48, fam: 'PuHui-Heavy', col: COL.ink });
      c.fillStyle = 'rgba(27,27,26,.15)'; c.fillRect(-390, 60, 520, 12); c.restore(); });
    if (t > L.z02.t0) { const q = Math.min(1.1, pop(t, kw('z02', '翻倍'))); c.save(); c.translate(870, 560); c.rotate(-0.15); c.scale(q, q); c.shadowColor = COL.gold; c.shadowBlur = 40; txt(c, '×2', 0, 0, { size: 160, fam: 'PuHui-Heavy', col: COL.goldHi, align: 'center' }); c.restore(); }
    c.restore(); }
  const q3 = ease(t, t3 - 0.2, t3 + 0.3) * (1 - ease(t, t4 - 0.2, t4 + 0.3));
  if (q3 > 0) { c.save(); c.globalAlpha = q3; c.translate(W / 2, 740); const v = ease(t, t3, t3 + 1.2, 'o') * (0.97 + 0.03 * Math.sin(t * 9)), A0 = Math.PI * 0.8, A1 = Math.PI * 2.2;
    c.strokeStyle = 'rgba(236,230,218,.18)'; c.lineWidth = 18; c.beginPath(); c.arc(0, 0, 270, A0, A1); c.stroke();
    c.save(); c.globalCompositeOperation = 'lighter'; c.shadowColor = COL.gold; c.shadowBlur = 30; c.strokeStyle = COL.goldHi; c.beginPath(); c.arc(0, 0, 270, A0, A0 + (A1 - A0) * v); c.stroke(); c.restore();
    const ang = A0 + (A1 - A0) * v; c.strokeStyle = COL.redHi; c.lineWidth = 10; c.lineCap = 'round'; c.beginPath(); c.moveTo(0, 0); c.lineTo(Math.cos(ang) * 230, Math.sin(ang) * 230); c.stroke();
    txt(c, `${Math.round(300 * v)}`, 0, 120, { size: 100, fam: 'PuHui-Heavy', col: COL.cream, align: 'center' }); txt(c, '最高时速 km/h', 0, 200, { size: 34, col: COL.creamDim, align: 'center' }); c.restore();
    if (t > tRoad - 0.3) { const q = ease(t, tRoad - 0.3, tRoad + 0.3); c.save(); c.globalAlpha = q3 * q;
      c.fillStyle = '#2b2d2c'; c.fillRect(80, 1140, 420, 120); c.fillStyle = COL.cream; for (let n = 0; n < 6; n++) c.fillRect(100 + n * 70 - ((t * 200) % 70), 1196, 40, 8); txt(c, '平坦的高速', 290, 1310, { size: 40, fam: 'PuHui-Heavy', col: COL.cream, align: 'center' });
      c.fillStyle = '#5a4532'; c.beginPath(); c.moveTo(580, 1260); for (let n = 0; n <= 14; n++) c.lineTo(580 + n * 30, 1150 + 25 * Math.sin(n * 1.9 + t * 3)); c.lineTo(1000, 1260); c.closePath(); c.fill(); txt(c, '坑坑洼洼的土路', 790, 1310, { size: 40, fam: 'PuHui-Heavy', col: COL.coral, align: 'center' }); c.restore(); } }
  if (t > t4 - 0.2) { tape(c, '先问三个问题', W / 2, 520, { size: 64, t, at: t4 - 0.2 }); ['①', '②', '③'].forEach((s, i) => { const at = t4 + i * 0.2; if (t < at) return; const q = Math.min(1, pop(t, at));
    c.save(); c.translate(250 + i * 290, 900 + 14 * Math.sin(t * 3 + i * 1.5)); c.scale(q, q); c.shadowColor = COL.gold; c.shadowBlur = 24; c.fillStyle = COL.cream; c.beginPath(); c.roundRect(-110, -80, 220, 160, 16); c.fill(); c.shadowBlur = 0;
    txt(c, `${s}？`, 0, 4, { size: 72, fam: 'PuHui-Heavy', col: COL.red, align: 'center' }); c.restore(); }); }
  const up = ease(t, t3 - 0.3, t3 + 0.3, 'c');
  if (up < 1) { c.save(); c.globalAlpha = 1 - up; hookText(c, t, ['速度翻倍，', '该信几分？'], { y: 230, size: 92 });
    hookText(c, t, ['AI 芯片的新闻，', '天天在说速度翻倍。'], { y: 1520, size: 62, ids: ['z01', 'z02'], bg: '#0f0f0e' }); c.restore(); }
};

// ---------- 2. 第一问：什么路上跑出来的？同样 224G，一米铜缆 vs 几厘米 ----------
SP.MECH.road = (c, t, sh) => {
  const k = T.cam({ hy: 1500, camH: 300 }); T.bg(c, k, { scroll: t * 200, grid: 0.5 }); T.streams(c, t, { a: 0.16, seed: 11 });
  const tM = kw('z06', '一米'), tCm = kw('z06', '几厘米'), t7 = L.z07.t0, tHard = kw('z07', '越难跑');
  qcard(c, 1, '在什么路上跑出来的？', W / 2, 330, t, sh.t0 + 0.2);
  T.chip(c, 280, 620 + 8 * Math.sin(t * 2), 340, 340, { label: '224G', sub: '每条通道', t: t * 2 }); T.chip(c, 800, 620 + 8 * Math.sin(t * 2 + 1.5), 340, 340, { label: '224G', sub: '每条通道', t: t * 2 + 0.7 });
  const pm = ease(t, tM - 0.5, tM + 1.0, 'c'), pts = []; for (let i = 0; i <= 80; i++) { const u = i / 80; pts.push([280 + 170 * Math.sin(u * Math.PI * 2.5), 800 + u * 520]); }
  T.glowLine(c, pts.slice(0, Math.max(2, Math.round(80 * pm) + 1)), { col: [226, 140, 70], lw: 14 });
  if (pm > 0.9) txt(c, '约 1 米铜缆', 280, 1390, { size: 46, fam: 'PuHui-Heavy', col: COL.goldHi, align: 'center' });
  // 信号沿着铜缆跑：光点
  if (pm > 0.95) for (let n = 0; n < 6; n++) { const u = ((t - tM) * 0.35 + n / 6) % 1, p = pts[Math.round(u * 80)]; glowDot(c, p[0], p[1], 8, GOLD, 0.8 * (1 - u * 0.6)); }
  const pc = ease(t, tCm - 0.3, tCm + 0.4, 'o'); T.glowLine(c, [[800, 790], [800, 790 + 130 * pc]], { lw: 10 });
  if (pc > 0.5) txt(c, '几厘米', 800, 990, { size: 46, fam: 'PuHui-Heavy', col: COL.goldHi, align: 'center' });
  // 路越长损耗越大：两头各一个小屏，长路那头的信号糊了
  if (t > t7 - 0.3) { const q = ease(t, t7 - 0.3, t7 + 0.3), off = (t - t7) * 150; c.save(); c.globalAlpha = q;
    const scr = (x, y, w, h, blur, col, lab, labCol) => { c.fillStyle = 'rgba(8,10,11,.92)'; c.strokeStyle = 'rgba(155,232,219,.3)'; c.lineWidth = 2; c.beginPath(); c.roundRect(x, y, w, h, 12); c.fill(); c.stroke();
      c.save(); c.beginPath(); c.rect(x, y, w, h); c.clip(); T.glowLine(c, sigPts(x + 10, x + w - 10, y + h / 2, h * 0.3, blur, off), { col, lw: 5 }); c.restore(); txt(c, lab, x + w / 2, y + h + 40, { size: 36, fam: 'PuHui-Heavy', col: labCol, align: 'center' }); };
    scr(560, 1080, 470, 200, 0.05, GOLD, '几厘米后：清清楚楚', COL.goldHi); scr(50, 1080, 460, 200, 0.9, CORAL, '一米后：糊成一片', COL.coral); c.restore(); }
  if (t > tHard - 0.3) tape(c, '路越长、损耗越大，越难跑', W / 2, 470, { size: 50, t, at: tHard - 0.3 });
};

// ---------- 3. 第二问：每个比特花多少电？速度翻倍、每比特的电不降 → 耗电翻倍；几万颗芯片 ----------
SP.MECH.power = (c, t, sh) => {
  const tDbl = kw('z09', '速度翻倍'), tPow = kw('z09', '耗电'), tMany = kw('z09', '几万颗芯片'), tCost = kw('z09', '成本');
  const zo = ease(t, tMany - 0.3, tMany + 1.2, 'c');
  const k = T.cam({ hy: lerp(1500, 560, zo), camH: lerp(300, 700, zo), f: 900 }); T.bg(c, k, { scroll: t * 200, grid: 0.5 + 0.5 * zo });
  qcard(c, 2, '每传一个比特，花多少电？', W / 2, 330, t, sh.t0 + 0.2);
  // 一颗芯片：比特一颗颗穿过去，每颗带走一点电；速度翻倍以后，光点密一倍
  const rate = t > tDbl ? 2 : 1, ch = 1 - zo;
  if (ch > 0) { c.save(); c.globalAlpha = ch; T.chip(c, W / 2, 760, 420, 420, { label: '芯片', t });
    for (let n = 0; n < 24; n++) { const ph = ((t * 0.9 * rate + n / (12 * rate)) % 1); if (n >= 12 * rate) break; const x = lerp(60, W - 60, ph); glowDot(c, x, 760, 8, GOLD, 0.9); }
    // 电表：每比特的电（不变） × 速度 = 总耗电
    const bar = (x, lab, v, col, sub) => { txt(c, lab, x, 1090, { size: 38, fam: 'PuHui-Heavy', col: COL.cream, align: 'center' }); c.strokeStyle = 'rgba(236,230,218,.35)'; c.lineWidth = 3; c.strokeRect(x - 60, 1120, 120, 300);
      c.save(); c.globalCompositeOperation = 'lighter'; c.shadowColor = `rgb(${col})`; c.shadowBlur = 24; c.fillStyle = `rgba(${col},.85)`; c.fillRect(x - 52, 1412 - 284 * v, 104, 284 * v); c.restore(); if (sub) txt(c, sub, x, 1460, { size: 32, col: COL.creamDim, align: 'center' }); };
    const tot = 0.4 * lerp(1, 2, ease(t, tPow - 0.4, tPow + 0.5, 'o'));
    bar(270, '每个比特的电', 0.4, MINT, 'pJ/bit'); bar(540, '速度', 0.4 * lerp(1, 2, ease(t, tDbl - 0.3, tDbl + 0.5, 'o')), GOLD, ''); bar(810, '总耗电', tot, CORAL, '');
    if (t > tDbl - 0.3) tag(c, '速度 ×2', 540, 1040 - 0, { size: 40, bg: COL.goldHi, fg: COL.ink, t, at: tDbl - 0.3 });
    if (t > tPow - 0.3) tag(c, '耗电 ×2', 810, 1040, { size: 40, bg: COL.coral, fg: COL.ink, t, at: tPow - 0.3 });
    c.restore(); }
  // 镜头拉远：地面上几万颗芯片一起亮
  if (zo > 0) { c.save(); c.globalAlpha = zo; const S = 220;
    for (let j = 26; j >= 0; j--) for (let i = -9; i <= 9; i++) { const x = i * S, z = 1100 + j * S - ((t * 160) % S); const a = T.P(k, x - 55, 0, z - 55), b = T.P(k, x + 55, 0, z - 55), cc = T.P(k, x + 55, 0, z + 55), d = T.P(k, x - 55, 0, z + 55), fade = clamp(1 - z / 6000), on = (Math.floor(t * 8) + i * 3 + j * 7) % 5 ? 1 : 0.5;
      c.fillStyle = `rgba(239,125,98,${0.55 * fade * on})`; c.beginPath(); [a, b, cc, d].forEach((p, n) => n ? c.lineTo(p[0], p[1]) : c.moveTo(p[0], p[1])); c.closePath(); c.fill(); }
    c.restore(); if (t > tMany) tag(c, '几万颗芯片一起跑', W / 2, 1300, { size: 46, t, at: tMany }); }
  if (t > tCost - 0.3) tape(c, '每一点电，都是成本', W / 2, 480, { size: 58, t, at: tCost - 0.3 });
};

// ---------- 4. 第三问：真实芯片上跑通了吗？仿真 vs 实测 ----------
SP.MECH.real = (c, t, sh) => {
  const k = T.cam({ hy: 1500, camH: 300 }); T.bg(c, k, { scroll: t * 200, grid: 0.5 });
  const tSim = kw('z11', '仿真'), tReal = kw('z11', '测出来'), tTwo = kw('z11', '两回事');
  qcard(c, 3, '在真实芯片上跑通了吗？', W / 2, 330, t, sh.t0 + 0.2);
  const off = (t - sh.t0) * 160;
  // 左：线框芯片（纸面 / 仿真）+ 完美的信号
  c.save(); c.strokeStyle = `rgba(155,232,219,${0.55 + 0.2 * Math.sin(t * 3)})`; c.lineWidth = 3; c.setLineDash([12, 10]); c.lineDashOffset = -t * 20; c.beginPath(); c.roundRect(110, 520, 360, 360, 18); c.stroke(); c.beginPath(); c.roundRect(170, 580, 240, 240, 10); c.stroke(); c.restore();
  txt(c, '纸面 / 仿真', 290, 940, { size: 42, fam: 'PuHui-Heavy', col: COL.tealHi, align: 'center' });
  c.save(); c.beginPath(); c.rect(60, 1000, 460, 220); c.clip(); T.glowLine(c, sigPts(70, 510, 1110, 70, 0.0, off), { col: TEAL, lw: 5 }); c.restore();
  // 右：真芯片 + 测试探针 + 实测的信号（有抖动）
  const rq = ease(t, tReal - 0.8, tReal + 0.2);
  T.chip(c, 790, 700, 360, 360, { label: '真芯片', t, glow: rq });
  for (let n = 0; n < 3; n++) { const x = 700 + n * 90; c.strokeStyle = '#9a978f'; c.lineWidth = 6; c.beginPath(); c.moveTo(x, 420); c.lineTo(x + 10, 520 + 10 * Math.sin(n)); c.stroke(); glowDot(c, x + 10, 522, 5, GOLD, 0.8); }
  txt(c, '真做出来、测出来', 790, 940, { size: 42, fam: 'PuHui-Heavy', col: COL.goldHi, align: 'center' });
  c.save(); c.globalAlpha = Math.max(0.15, rq); c.beginPath(); c.rect(560, 1000, 460, 220); c.clip(); T.glowLine(c, sigPts(570, 1010, 1110, 70, 0.25, off, 60, 10, Math.floor(t * 12)), { col: GOLD, lw: 5 }); c.restore();
  if (t > tTwo - 0.3) tape(c, '仿真 ≠ 实测', W / 2, 1330, { size: 68, t, at: tTwo - 0.3, r: -0.02 });
};
})();
