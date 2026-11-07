// 第 3 条（第四稿）：AI 芯片「速度翻倍」，该信几分？——先问三句：什么路、多少电、跑通没有。只讲怎么问，不点名、不荐股。
(() => {
const { clamp, lerp } = U; const { W, H, COL, T, kw, txt, tape, tag, pop, ease, seg, hookText, L } = SP;
SP.END = 'u13';
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

// ---------- 1. 第一帧：一大片芯片上空立着发光的「×2」→ 最高时速 300 没说什么路 → 先问三个问题 ----------
SP.MECH.x2 = (c, t, sh) => {
  const t3 = L.u03.t0, tRoad = kw('u03', '什么路上'), t4 = L.u04.t0;
  const k = T.cam({ hy: 760, camH: 650, f: lerp(880, 1000, ease(t, 0, 9, 's')), cx: 80 * Math.sin(t * 0.35) }); T.bg(c, k, { grid: 0.8, scroll: t * 300 }); const S = 200;
  for (let j = 28; j >= 0; j--) for (let i = -10; i <= 10; i++) { const x = i * S, z = 600 + j * S - ((t * 300) % S); if (z < 420) continue; const pp = [[-60, -60], [60, -60], [60, 60], [-60, 60]].map(([dx, dz]) => T.P(k, x + dx, 0, z + dz)), fade = clamp(1 - z / 6000), on = (R(i * 31 + j)() + t * 0.6 + j * 0.05) % 1 < 0.55;
    c.fillStyle = on ? `rgba(245,215,126,${0.5 * fade})` : `rgba(60,58,52,${fade})`; c.beginPath(); pp.forEach((p, n) => n ? c.lineTo(p[0], p[1]) : c.moveTo(p[0], p[1])); c.closePath(); c.fill(); }
  const tSlam = kw('u02', '翻倍'), away = t > 0.9 && t < tSlam - 0.05 ? ease(t, 0.9, 1.2) : 0, slam = t >= tSlam - 0.05 ? 1 + 0.6 * (1 - ease(t, tSlam - 0.05, tSlam + 0.25, 'o')) : 1;
  // 新闻卡：1 秒以后一张接一张快速划过
  if (t > 0.9 && t < tSlam + 0.3) ['新一代 AI 芯片：互连速度翻倍', '传输速度再翻一倍！', '每条通道冲上 200G'].forEach((h_, i) => { const at = 0.95 + i * 0.42, q = ease(t, at, at + 0.22, 'o'), out = ease(t, tSlam - 0.15, tSlam + 0.15); if (t < at) return;
    c.save(); c.globalAlpha = 1 - out; c.translate(lerp(W + 500, W / 2 + (i - 1) * 30, q), 720 + i * 210); c.rotate((i - 1) * 0.05); c.shadowColor = 'rgba(0,0,0,.6)'; c.shadowBlur = 24; c.fillStyle = '#f6f2ea'; c.beginPath(); c.roundRect(-430, -90, 860, 180, 12); c.fill(); c.shadowColor = 'transparent';
    c.fillStyle = COL.red; c.fillRect(-430, -90, 14, 180); txt(c, '科技快讯', -390, -44, { size: 28, fam: 'PuHui-Heavy', col: COL.red }); txt(c, h_, -390, 20, { size: 46, fam: 'PuHui-Heavy', col: COL.ink }); c.restore(); });
  const xq = (1 - ease(t, t3 - 0.3, t3 + 0.3, 'c')) * (1 - away);
  if (xq > 0) { const pulse = slam * (1 + 0.04 * Math.sin(t * 3)); c.save(); c.globalAlpha = xq; c.translate(W / 2, 900); c.scale(pulse, pulse); c.rotate(0.03 * Math.sin(t * 0.9));
    for (let d = 14; d > 0; d--) txt(c, '×2', d * 1.2, d * 1.5, { size: 420, fam: 'PuHui-Heavy', col: 'rgba(120,90,30,.9)', align: 'center' }); c.shadowColor = COL.gold; c.shadowBlur = 60; txt(c, '×2', 0, 0, { size: 420, fam: 'PuHui-Heavy', col: '#fff2c4', align: 'center' }); c.restore(); }
  // 最高时速 300：表盘在芯片地面上方亮起来；下面两条路
  const q3 = ease(t, t3 - 0.2, t3 + 0.3) * (1 - ease(t, t4 - 0.2, t4 + 0.3));
  if (q3 > 0) { c.save(); c.globalAlpha = q3; c.fillStyle = 'rgba(4,5,6,.55)'; c.fillRect(0, 0, W, H); c.translate(W / 2, 760); const v = ease(t, t3, t3 + 1.2, 'o') * (0.97 + 0.03 * Math.sin(t * 9)), A0 = Math.PI * 0.8, A1 = Math.PI * 2.2;
    c.strokeStyle = 'rgba(236,230,218,.18)'; c.lineWidth = 18; c.beginPath(); c.arc(0, 0, 270, A0, A1); c.stroke();
    c.save(); c.globalCompositeOperation = 'lighter'; c.shadowColor = COL.gold; c.shadowBlur = 30; c.strokeStyle = COL.goldHi; c.beginPath(); c.arc(0, 0, 270, A0, A0 + (A1 - A0) * v); c.stroke(); c.restore();
    const ang = A0 + (A1 - A0) * v; c.strokeStyle = COL.redHi; c.lineWidth = 10; c.lineCap = 'round'; c.beginPath(); c.moveTo(0, 0); c.lineTo(Math.cos(ang) * 230, Math.sin(ang) * 230); c.stroke();
    txt(c, `${Math.round(300 * v)}`, 0, 120, { size: 100, fam: 'PuHui-Heavy', col: COL.cream, align: 'center' }); txt(c, '最高时速 km/h', 0, 200, { size: 34, col: COL.creamDim, align: 'center' }); c.restore();
    if (t > tRoad - 0.3) { const q = ease(t, tRoad - 0.3, tRoad + 0.3); c.save(); c.globalAlpha = q3 * q;
      c.fillStyle = '#2b2d2c'; c.fillRect(80, 1140, 420, 120); c.fillStyle = COL.cream; for (let n = 0; n < 6; n++) c.fillRect(100 + n * 70 - ((t * 200) % 70), 1196, 40, 8); txt(c, '平坦的高速', 290, 1310, { size: 40, fam: 'PuHui-Heavy', col: COL.cream, align: 'center' });
      c.fillStyle = '#5a4532'; c.beginPath(); c.moveTo(580, 1260); for (let n = 0; n <= 14; n++) c.lineTo(580 + n * 30, 1150 + 25 * Math.sin(n * 1.9 + t * 3)); c.lineTo(1000, 1260); c.closePath(); c.fill(); txt(c, '坑坑洼洼的土路', 790, 1310, { size: 40, fam: 'PuHui-Heavy', col: COL.coral, align: 'center' }); c.restore(); } }
  // 先问三个问题：三张卡片砸下来
  if (t > t4 - 0.2) { c.save(); c.fillStyle = 'rgba(4,5,6,.55)'; c.fillRect(0, 0, W, H); c.restore(); tape(c, '先问三个问题', W / 2, 560, { size: 66, t, at: t4 - 0.2 });
    ['①', '②', '③'].forEach((s_, i) => { const at = t4 + 0.2 + i * 0.22; if (t < at) return; const q = Math.min(1, pop(t, at, 0.18)), drop = (1 - q) * -300;
      c.save(); c.translate(250 + i * 290, 900 + drop + 12 * Math.sin(t * 3 + i * 1.5)); c.shadowColor = COL.gold; c.shadowBlur = 30; c.fillStyle = COL.cream; c.beginPath(); c.roundRect(-110, -80, 220, 160, 16); c.fill(); c.shadowBlur = 0;
      txt(c, `${s_}？`, 0, 4, { size: 72, fam: 'PuHui-Heavy', col: COL.red, align: 'center' }); c.restore(); }); }
  const up = ease(t, t3 - 0.3, t3 + 0.3, 'c');
  if (up < 1) { c.save(); c.globalAlpha = 1 - up; hookText(c, t, ['AI 芯片速度翻倍，', '该信几分？'], { y: 260, size: 88 });
    hookText(c, t, ['AI 芯片的新闻，', '天天在说速度翻倍。'], { y: 1290, size: 56, ids: ['u01', 'u02'], bg: '#0f0f0e' }); c.restore(); }
};

// ---------- 2. 第一问：什么路上跑出来的？同样 224G，一米铜缆 vs 几厘米 ----------
SP.MECH.road = (c, t, sh) => {
  const k = T.cam({ hy: 1500, camH: 300 }); T.bg(c, k, { scroll: t * 200, grid: 0.5 }); T.streams(c, t, { a: 0.16, seed: 11 });
  const tM = kw('u06', '一米'), tCm = kw('u06', '几厘米'), t7 = tCm + 0.7, tHard = tCm + 1.0;
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
  if (t > tHard - 0.3) tape(c, '路况不同，难度差很多', W / 2, 470, { size: 50, t, at: tHard - 0.3 });
};

// ---------- 3. 第二问：每个比特花多少电？速度翻倍、每比特的电不降 → 耗电翻倍；几万颗芯片 ----------
SP.MECH.power = (c, t, sh) => {
  const tDbl = kw('u08', '速度翻倍'), tPow = kw('u08', '电费'), tMany = kw('u08', '几万颗芯片'), tCost = kw('u08', '真金白银');
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
    bar(270, '每个比特的电', 0.4, MINT, 'pJ/bit'); bar(540, '速度', 0.4 * lerp(1, 2, ease(t, tDbl - 0.3, tDbl + 0.5, 'o')), GOLD, ''); bar(810, '电费', tot, CORAL, '');
    if (t > tDbl - 0.3) tag(c, '速度 ×2', 540, 1040 - 0, { size: 40, bg: COL.goldHi, fg: COL.ink, t, at: tDbl - 0.3 });
    if (t > tPow - 0.3) tag(c, '电费 ×2', 810, 1040, { size: 40, bg: COL.coral, fg: COL.ink, t, at: tPow - 0.3 });
    c.restore(); }
  // 镜头拉远：地面上几万颗芯片一起亮
  if (zo > 0) { c.save(); c.globalAlpha = zo; const S = 220;
    for (let j = 26; j >= 0; j--) for (let i = -9; i <= 9; i++) { const x = i * S, z = 1100 + j * S - ((t * 160) % S); const a = T.P(k, x - 55, 0, z - 55), b = T.P(k, x + 55, 0, z - 55), cc = T.P(k, x + 55, 0, z + 55), d = T.P(k, x - 55, 0, z + 55), fade = clamp(1 - z / 6000), on = (Math.floor(t * 8) + i * 3 + j * 7) % 5 ? 1 : 0.5;
      c.fillStyle = `rgba(239,125,98,${0.55 * fade * on})`; c.beginPath(); [a, b, cc, d].forEach((p, n) => n ? c.lineTo(p[0], p[1]) : c.moveTo(p[0], p[1])); c.closePath(); c.fill(); }
    c.restore(); if (t > tMany) tag(c, '几万颗芯片一起跑', W / 2, 1300, { size: 46, t, at: tMany }); }
  if (t > tCost - 0.3) tape(c, '这就是真金白银', W / 2, 480, { size: 58, t, at: tCost - 0.3 });
};

// ---------- 4. 第三问：PPT 上的速度，还是真芯片测出来的？——PPT 裂开碎掉，真芯片亮起来 ----------
SP.MECH.ppt = (c, t, sh) => {
  const k = T.cam({ hy: 1500, camH: 300 }); T.bg(c, k, { grid: 0.5, scroll: t * 200 }); T.streams(c, t, { a: 0.12, seed: 13 });
  const tP = kw('u09', 'PPT'), tReal = kw('u09', '真芯片'), tOk = kw('u10', '才算数');
  qcard(c, 3, '是 PPT 上的，还是测出来的？', W / 2, 330, t, sh.t0 + 0.2);
  // PPT：一张发布会幻灯片，说到「真芯片」时裂开、碎成几块往下掉
  const crack = ease(t, tReal - 0.25, tReal), fall = clamp((t - tReal) / 1.4);
  const PCS = [[[-230, -160], [20, -160], [-60, 10], [-230, -40]], [[20, -160], [230, -160], [230, 0], [120, 40], [20, -80]], [[-230, -40], [-60, 10], [60, 160], [-230, 160]], [[-60, 10], [20, -80], [120, 40], [230, 0], [230, 160], [60, 160]]];
  const slide = (g) => { g.fillStyle = '#f6f2ea'; g.fillRect(-230, -160, 460, 320); g.fillStyle = COL.red; g.fillRect(-230, -160, 460, 50); txt(g, '新品发布', -200, -134, { size: 30, fam: 'PuHui-Heavy', col: '#fff' }); txt(g, '224G!!', 0, 20, { size: 110, fam: 'PuHui-Heavy', col: COL.ink, align: 'center' }); txt(g, '业界领先', 0, 110, { size: 34, fam: 'PuHui-Heavy', col: 'rgba(27,27,26,.5)', align: 'center' }); };
  const sx = 300, sy = 780 + 8 * Math.sin(t * 2);
  if (fall < 1) PCS.forEach((poly, i) => { const r = R(i + 21), dx = (r() - 0.5) * 300 * fall, dy = 900 * fall * fall + (r() - 0.3) * 120 * fall, rot = (r() - 0.5) * 2 * fall;
    c.save(); c.globalAlpha = 1 - seg(fall, 0.6, 1); c.translate(sx + dx, sy + dy); c.rotate(-0.05 + rot); c.beginPath(); poly.forEach((p, n) => n ? c.lineTo(p[0], p[1]) : c.moveTo(p[0], p[1])); c.closePath(); c.clip(); slide(c); c.restore(); });
  if (crack > 0 && fall <= 0) { c.save(); c.translate(sx, sy); c.rotate(-0.05); c.strokeStyle = '#040506'; c.lineWidth = 6; c.beginPath(); c.moveTo(-230, -40); c.lineTo(-230 + 170 * crack, -40 + 50 * crack); c.moveTo(20, -160); c.lineTo(20 - 80 * crack, -160 + 170 * crack); c.moveTo(20, -80); c.lineTo(20 + 100 * crack, -80 + 120 * crack); c.stroke(); c.restore(); }
  if (t > tP - 0.3) txt(c, 'PPT 上的速度', sx, 1020, { size: 44, fam: 'PuHui-Heavy', col: COL.creamDim, align: 'center', alpha: 1 - fall });
  // 真芯片：探针扎下去，测出来的信号在跳
  const rq = ease(t, tReal - 0.3, tReal + 0.4);
  T.chip(c, 790, 760, 330, 330, { label: '真芯片', t: t * 1.5, glow: rq });
  for (let n = 0; n < 3; n++) { const yy = lerp(380, 470, rq); c.strokeStyle = '#9a978f'; c.lineWidth = 6; c.beginPath(); c.moveTo(710 + n * 80, yy - 120); c.lineTo(720 + n * 80, yy + 110); c.stroke(); if (rq > 0.8) glowDot(c, 720 + n * 80, yy + 112, 5, GOLD, 0.9); }
  if (rq > 0) { c.save(); c.globalAlpha = rq; c.beginPath(); c.rect(600, 1000, 400, 180); c.clip(); T.glowLine(c, sigPts(605, 995, 1090, 60, 0.22, (t - tReal) * 200, 50, 8, Math.floor(t * 12)), { col: GOLD, lw: 5 }); c.restore();
    txt(c, '真芯片测出来的', 790, 1230, { size: 44, fam: 'PuHui-Heavy', col: COL.goldHi, align: 'center', alpha: rq }); }
  if (t > tOk - 0.6) tape(c, '做出来、测出来，才算数', W / 2, 1370, { size: 60, t, at: tOk - 0.6, r: -0.02 });
};

})();
