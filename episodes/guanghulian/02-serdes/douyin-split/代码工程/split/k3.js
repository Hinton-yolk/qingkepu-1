// 第 3 条（第五稿 · 翻译）：AI 芯片「速度翻倍」，该信几分？——先问三句：什么路、多少电、跑通没有。只讲怎么问，不点名、不荐股。
(() => {
const { clamp, lerp } = U; const { W, H, COL, T, kw, txt, tape, tag, pop, ease, seg, hookText, L } = SP;
SP.END = 'k10';
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

const chatBg = (g, x, y, w, h) => { g.fillStyle = '#ededed'; g.fillRect(x, y, w, h); };
// 小问题卡（贴在画面左上角的东西旁边，不是顶部标题条）
const qtag = (c, n, s, x, y, t, at) => { if (t < at) return; const q = Math.min(1, pop(t, at, 0.2)); c.save(); c.translate(x, y); c.scale(q, q); c.fillStyle = COL.red; c.beginPath(); c.arc(0, 0, 36, 0, 7); c.fill(); txt(c, String(n), 0, 2, { size: 44, fam: 'PuHui-Heavy', col: '#f6efe4', align: 'center' }); c.restore(); tag(c, s, x + 60, y, { size: 44, align: 'left', t, at }); };

// ---------- 1. 第一帧：发布会大屏「速度 ×2」，台下手机实测只有一半 → 新闻也天天说翻倍 → 先问三句 ----------
SP.MECH.launch = (c, t, sh) => {
  const k = T.cam({ hy: 1500, camH: 300 }); T.bg(c, k, { grid: 0.4, scroll: t * 150 }); T.streams(c, t, { a: 0.12, seed: 6 });
  const tHalf = kw('k02', '打对折'), tNews = 1e9, tAsk = 1e9;
  // 大屏 + 扫来扫去的追光
  c.save(); c.fillStyle = '#0d0f12'; c.fillRect(90, 330, 900, 520); c.strokeStyle = 'rgba(155,232,219,.25)'; c.lineWidth = 3; c.strokeRect(90, 330, 900, 520);
  const g = c.createRadialGradient(540, 590, 50, 540, 590, 600); g.addColorStop(0, 'rgba(245,215,126,.35)'); g.addColorStop(1, 'rgba(245,215,126,0)'); c.fillStyle = g; c.fillRect(90, 330, 900, 520);
  const pz = 1 + 0.03 * Math.sin(t * 3); c.translate(540, 570); c.scale(pz, pz); c.shadowColor = COL.gold; c.shadowBlur = 50; txt(c, '速度 ×2', 0, 0, { size: 190, fam: 'PuHui-Heavy', col: '#fff2c4', align: 'center' }); c.restore();
  txt(c, '新一代 AI 芯片发布会', 540, 780, { size: 40, fam: 'PuHui-Heavy', col: COL.creamDim, align: 'center' });
  for (const [x0, ph] of [[200, 0], [880, 1.7]]) { const a = Math.sin(t * 1.3 + ph) * 0.35; c.save(); c.globalCompositeOperation = 'lighter'; c.translate(x0, 1500); c.rotate(a); const gg = c.createLinearGradient(0, 0, 0, -1200); gg.addColorStop(0, 'rgba(255,240,200,.18)'); gg.addColorStop(1, 'rgba(255,240,200,0)'); c.fillStyle = gg; c.beginPath(); c.moveTo(-30, 0); c.lineTo(30, 0); c.lineTo(220, -1200); c.lineTo(-220, -1200); c.closePath(); c.fill(); c.restore(); }
  for (let n = 0; n < 9; n++) { c.fillStyle = '#050607'; c.beginPath(); c.arc(80 + n * 115, 1560 + (n % 2) * 20, 60, Math.PI, 0); c.fill(); }      // 台下观众的后脑勺
  // 台下一部手机：实测进度条，说到「打对折」那一刻停在一半
  const fill = 0.5 + 0.03 * Math.sin(t * 5);                    // 第一帧就是对比：大屏 ×2，手里实测只有一半
  SP.phone(c, 780, 1180, 280, 480, (g2, x, y, w, h) => { g2.fillStyle = '#10141a'; g2.fillRect(x, y, w, h); txt(g2, '到手实测', x + w / 2, y + 80, { size: 30, fam: 'PuHui-Heavy', col: COL.cream, align: 'center' });
    g2.fillStyle = 'rgba(236,230,218,.2)'; g2.fillRect(x + 30, y + 150, w - 60, 30); g2.fillStyle = fill <= 0.55 ? COL.coral : COL.goldHi; g2.fillRect(x + 30, y + 150, (w - 60) * fill, 30);
    txt(g2, '×1', x + w / 2, y + 280, { size: 80, fam: 'PuHui-Heavy', col: fill <= 0.55 ? COL.coral : COL.goldHi, align: 'center' }); });
  tag(c, '到手：打对折？', 380, 1180 + 6 * Math.sin(t * 3), { size: 54, bg: COL.coral, fg: COL.ink, r: -0.03 });
  // 新闻卡：一张接一张划过大屏
  if (t > tNews - 0.2) { c.save(); c.fillStyle = `rgba(4,5,6,${0.55 * ease(t, tNews - 0.2, tNews + 0.2)})`; c.fillRect(0, 0, W, H); c.restore();
    ['新一代 AI 芯片：互连速度翻倍', '传输速度再翻一倍！', '每条通道冲上 200G'].forEach((h_, i) => { const at = tNews - 0.1 + i * 0.35, q = ease(t, at, at + 0.22, 'o'), out = ease(t, tAsk - 0.2, tAsk + 0.1); if (t < at) return;
      c.save(); c.globalAlpha = 1 - out; c.translate(lerp(W + 500, W / 2 + (i - 1) * 30, q) + 12 * Math.sin(t * 2 + i), 560 + i * 200 + 8 * Math.sin(t * 2.6 + i)); c.rotate((i - 1) * 0.05); c.shadowColor = 'rgba(0,0,0,.6)'; c.shadowBlur = 24; c.fillStyle = '#f6f2ea'; c.beginPath(); c.roundRect(-430, -85, 860, 170, 12); c.fill(); c.shadowColor = 'transparent';
      c.fillStyle = COL.red; c.fillRect(-430, -85, 14, 170); txt(c, '科技快讯', -390, -40, { size: 28, fam: 'PuHui-Heavy', col: COL.red }); txt(c, h_, -390, 22, { size: 46, fam: 'PuHui-Heavy', col: COL.ink }); c.restore(); }); }
  if (t > tAsk - 0.2) ['什么路？', '费不费电？', '实测了吗？'].forEach((s_, i) => { const at = tAsk - 0.1 + i * 0.22; if (t < at) return; const q = Math.min(1, pop(t, at, 0.18));
    c.save(); c.translate(W / 2, 640 + i * 190 + (1 - q) * -200); c.shadowColor = COL.gold; c.shadowBlur = 24; c.fillStyle = COL.cream; c.beginPath(); c.roundRect(-330, -70, 660, 140, 16); c.fill(); c.shadowBlur = 0;
    c.fillStyle = COL.red; c.beginPath(); c.arc(-250, 0, 40, 0, 7); c.fill(); txt(c, String(i + 1), -250, 2, { size: 48, fam: 'PuHui-Heavy', col: '#fff', align: 'center' }); txt(c, s_, -180, 2, { size: 60, fam: 'PuHui-Heavy', col: COL.ink }); c.restore(); });
  hookText(c, t, ['发布会上的速度翻倍，', '到手可能打对折。'], { y: 1430, size: 54, ids: ['k01', 'k02'], bg: '#0f0f0e' });
};

// 快递路线图镜头里：说到「先问哪三句」时，三张问题卡砸下来
SP.ROUTE_EXTRA = (c, t, sh) => { const tAsk = kw('k03', '三句'); if (t < tAsk - 0.2) return; c.save(); c.fillStyle = `rgba(4,5,6,${0.6 * ease(t, tAsk - 0.2, tAsk + 0.1)})`; c.fillRect(0, 0, W, H); c.restore();
  ['什么路？', '费不费电？', '实测了吗？'].forEach((s_, i) => { const at = tAsk - 0.1 + i * 0.22; if (t < at) return; const q = Math.min(1, pop(t, at, 0.18));
    c.save(); c.translate(W / 2, 640 + i * 190 + (1 - q) * -200 + 8 * Math.sin(t * 3 + i)); c.shadowColor = COL.gold; c.shadowBlur = 24; c.fillStyle = COL.cream; c.beginPath(); c.roundRect(-330, -70, 660, 140, 16); c.fill(); c.shadowBlur = 0;
    c.fillStyle = COL.red; c.beginPath(); c.arc(-250, 0, 40, 0, 7); c.fill(); txt(c, String(i + 1), -250, 2, { size: 48, fam: 'PuHui-Heavy', col: '#fff', align: 'center' }); txt(c, s_, -180, 2, { size: 60, fam: 'PuHui-Heavy', col: COL.ink }); c.restore(); }); };
// ---------- 2. 第一句：什么路？——千兆宽带到卧室只剩一半（户型图：路由器一圈圈的信号，穿过两堵墙变弱） ----------
SP.MECH.wifi = (c, t, sh) => {
  const k = T.cam({ hy: 1500, camH: 300 }); T.bg(c, k, { grid: 0.4, scroll: t * 150 });
  const tBand = kw('k04', '千兆宽带'), tRoom = kw('k04', '卧室'), tHalf = kw('k04', '一半'); T.streams(c, t, { a: 0.16, seed: 10 });
  qtag(c, 1, '在什么路上跑的？', 120, 330, t, sh.t0 + 0.2);
  const x0 = 110, y0 = 470, w = 860, h = 860; c.save(); c.fillStyle = 'rgba(236,230,218,.06)'; c.fillRect(x0, y0, w, h); c.strokeStyle = COL.cream; c.lineWidth = 10; c.strokeRect(x0, y0, w, h);
  c.beginPath(); c.moveTo(x0 + w * 0.45, y0); c.lineTo(x0 + w * 0.45, y0 + h * 0.38); c.moveTo(x0 + w * 0.45, y0 + h * 0.55); c.lineTo(x0 + w * 0.45, y0 + h); c.moveTo(x0 + w * 0.45, y0 + h * 0.6); c.lineTo(x0 + w, y0 + h * 0.6); c.stroke(); c.restore();
  txt(c, '客厅', x0 + 60, y0 + 60, { size: 36, fam: 'PuHui-Heavy', col: COL.creamDim }); txt(c, '卧室', x0 + w * 0.5 + 40, y0 + h * 0.66, { size: 36, fam: 'PuHui-Heavy', col: COL.creamDim });
  const rx = x0 + 180, ry = y0 + 260; c.fillStyle = '#e8e4da'; c.beginPath(); c.roundRect(rx - 60, ry - 26, 120, 52, 10); c.fill(); for (const d of [-30, 30]) { c.fillStyle = '#e8e4da'; c.fillRect(rx + d - 4, ry - 80, 8, 56); }
  // 一圈圈往外扩的信号；穿墙以后变淡
  for (let n = 0; n < 5; n++) { const r = ((t * 260 + n * 160) % 800); c.save(); c.globalCompositeOperation = 'lighter'; c.strokeStyle = `rgba(155,232,219,${0.5 * (1 - r / 800) * (r > 420 ? 0.4 : 1)})`; c.lineWidth = 6; c.beginPath(); c.arc(rx, ry, r, 0, 7); c.stroke(); c.restore(); }
  if (t > tBand - 0.3) tag(c, '1000M', rx + 40, ry + 110, { size: 56, bg: COL.goldHi, fg: COL.ink, t, at: tBand - 0.3 });
  const px = x0 + w * 0.78, py = y0 + h * 0.82; if (t > tRoom - 0.3) { SP.phone(c, px, py, 120, 210, (g, x, y, ww, hh) => { g.fillStyle = '#10141a'; g.fillRect(x, y, ww, hh); for (let b = 0; b < 4; b++) { g.fillStyle = b < 2 ? COL.coral : 'rgba(236,230,218,.2)'; g.fillRect(x + 20 + b * 22, y + hh - 50 - b * 20, 16, 20 + b * 20); } });
    if (t > tHalf - 0.3) tag(c, '只剩 500M', px - 30, py - 170, { size: 52, bg: COL.coral, fg: COL.ink, t, at: tHalf - 0.3, r: -0.03 }); }
};

// ---------- 3. 第二句：费不费电？——手机跑分越高越烫手掉电；几万颗芯片一起跑，电费哗哗涨 ----------
SP.MECH.hot = (c, t, sh) => {
  const tPh = kw('k06', '手机'), tScore = kw('k06', '跑分'), tHot = kw('k06', '烫手'), tMany = kw('k06', '几万颗芯片'), tBill = kw('k06', '电费');
  const zo = ease(t, tMany - 0.3, tMany + 1.0, 'c');
  const k = T.cam({ hy: lerp(1500, 560, zo), camH: lerp(300, 700, zo), f: 900 }); T.bg(c, k, { grid: 0.4 + 0.6 * zo, scroll: t * 200 }); T.streams(c, t, { a: 0.2 * (1 - zo), seed: 8 });
  qtag(c, 2, '费不费电？', 120, 330, t, sh.t0 + 0.2);
  const ph = 1 - zo;
  if (ph > 0) { c.save(); c.globalAlpha = ph; const heat = ease(t, tScore, tHot + 0.6), sh2 = heat > 0.6 ? 4 * Math.sin(t * 50) * (heat - 0.6) : 0;
    SP.phone(c, 420 + sh2, 900 + 12 * Math.sin(t * 2.2), 460, 820, (g, x, y, w, h) => { const bg = g.createLinearGradient(0, y, 0, y + h); bg.addColorStop(0, `rgb(${lerp(16, 120, heat)},${lerp(20, 30, heat)},26)`); bg.addColorStop(1, '#0a0b0c'); g.fillStyle = bg; g.fillRect(x, y, w, h);
      txt(g, '跑分', x + w / 2, y + 120, { size: 40, fam: 'PuHui-Heavy', col: COL.cream, align: 'center' }); const sc = Math.round(lerp(0, 2345678, ease(t, tScore - 0.3, tHot + 0.5, 'o'))) + Math.floor((t - sh.t0) * 4321);
      txt(g, sc.toLocaleString('en-US'), x + w / 2, y + 230, { size: 66, fam: 'PuHui-Heavy', col: COL.goldHi, align: 'center' });
      const bat = lerp(0.95, 0.12, ease(t, tScore, tHot + 1.5)); g.strokeStyle = COL.cream; g.lineWidth = 4; g.strokeRect(x + 120, y + 560, 220, 90); g.fillStyle = bat < 0.3 ? COL.coral : COL.mint; g.fillRect(x + 128, y + 568, 204 * bat, 74); txt(g, `${Math.round(bat * 100)}%`, x + w / 2, y + 700, { size: 40, fam: 'PuHui-Heavy', col: COL.cream, align: 'center' }); });
    // 温度计
    c.save(); c.translate(860, 900); c.strokeStyle = COL.cream; c.lineWidth = 5; c.beginPath(); c.roundRect(-26, -300, 52, 380, 26); c.stroke(); c.fillStyle = COL.coral; c.beginPath(); c.arc(0, 110, 50, 0, 7); c.fill(); c.fillRect(-16, 90 - 360 * heat, 32, 360 * heat); c.restore();
    if (t > tHot - 0.3) tag(c, '烫手', 860, 520, { size: 56, bg: COL.coral, fg: COL.ink, t, at: tHot - 0.3 });
    c.restore(); }
  if (zo > 0) { c.save(); c.globalAlpha = zo; const S = 220;
    for (let j = 26; j >= 0; j--) for (let i = -9; i <= 9; i++) { const x = i * S, z = 1100 + j * S - ((t * 160) % S); const a = T.P(k, x - 55, 0, z - 55), b = T.P(k, x + 55, 0, z - 55), cc = T.P(k, x + 55, 0, z + 55), d = T.P(k, x - 55, 0, z + 55), fade = clamp(1 - z / 6000), on = (Math.floor(t * 8) + i * 3 + j * 7) % 5 ? 1 : 0.5;
      c.fillStyle = `rgba(239,125,98,${0.55 * fade * on})`; c.beginPath(); [a, b, cc, d].forEach((p, n) => n ? c.lineTo(p[0], p[1]) : c.moveTo(p[0], p[1])); c.closePath(); c.fill(); }
    c.restore();
    if (t > tBill - 0.4) { const v = Math.round(lerp(0, 9876543, ease(t, tBill - 0.4, sh.t1, 's'))); c.save(); c.fillStyle = 'rgba(8,10,11,.9)'; c.beginPath(); c.roundRect(190, 1180, 700, 170, 20); c.fill(); c.restore();
      txt(c, '电费', 260, 1265, { size: 44, fam: 'PuHui-Heavy', col: COL.cream }); txt(c, `¥ ${v.toLocaleString('en-US')}`, 850, 1268, { size: 72, fam: 'PuHui-Heavy', col: COL.coral, align: 'right' }); }
    if (t > tMany - 0.2) tag(c, '几万颗芯片一起跑', W / 2, 1100, { size: 46, t, at: tMany - 0.2 }); }
};

// ---------- 4. 第三句：实测了吗？——发布会 PPT「续航 2 天」碎掉，到手手机只撑 1 天；芯片也要真机测出来 ----------
SP.MECH.ppt = (c, t, sh) => {
  const k = T.cam({ hy: 1500, camH: 300 }); T.bg(c, k, { grid: 0.5, scroll: t * 200 }); T.streams(c, t, { a: 0.2, seed: 13 });
  const tLaunch = kw('k07', '发布会'), tHand = kw('k07', '到手'), tTwo = kw('k07', '两回事');
  qtag(c, 3, '真机测过没有？', 120, 330, t, sh.t0 + 0.2);
  const crack = ease(t, tHand - 0.25, tHand), fall = clamp((t - tHand) / 1.3);
  const PCS = [[[-230, -160], [20, -160], [-60, 10], [-230, -40]], [[20, -160], [230, -160], [230, 0], [120, 40], [20, -80]], [[-230, -40], [-60, 10], [60, 160], [-230, 160]], [[-60, 10], [20, -80], [120, 40], [230, 0], [230, 160], [60, 160]]];
  const slide = (g) => { g.fillStyle = '#f6f2ea'; g.fillRect(-230, -160, 460, 320); g.fillStyle = COL.red; g.fillRect(-230, -160, 460, 50); txt(g, '新品发布', -200, -134, { size: 30, fam: 'PuHui-Heavy', col: '#fff' }); txt(g, '续航 2 天', 0, 30, { size: 92, fam: 'PuHui-Heavy', col: COL.ink, align: 'center' }); };
  const sx = 300, sy = 760 + 8 * Math.sin(t * 2), sq = ease(t, sh.t0, sh.t0 + 0.4);
  if (fall < 1) PCS.forEach((poly, i) => { const r = R(i + 21), dx = (r() - 0.5) * 300 * fall, dy = 900 * fall * fall + (r() - 0.3) * 120 * fall, rot = (r() - 0.5) * 2 * fall;
    c.save(); c.globalAlpha = sq * (1 - seg(fall, 0.6, 1)); c.translate(sx + dx + 10 * Math.sin(t * 1.7), sy + dy); c.rotate(-0.05 + rot + 0.03 * Math.sin(t * 1.3)); c.beginPath(); poly.forEach((p, n) => n ? c.lineTo(p[0], p[1]) : c.moveTo(p[0], p[1])); c.closePath(); c.clip(); slide(c); c.restore(); });
  if (crack > 0 && fall <= 0) { c.save(); c.translate(sx, sy); c.rotate(-0.05); c.strokeStyle = '#040506'; c.lineWidth = 6; c.beginPath(); c.moveTo(-230, -40); c.lineTo(-230 + 170 * crack, -40 + 50 * crack); c.moveTo(20, -160); c.lineTo(20 - 80 * crack, -160 + 170 * crack); c.stroke(); c.restore(); }
  if (sq > 0.5 && fall < 0.5) tag(c, '发布会上', sx, 980, { size: 42 });
  const rq = ease(t, tHand - 0.3, tHand + 0.4);
  if (rq > 0) { c.save(); c.globalAlpha = rq; SP.phone(c, 790, 780 + 14 * Math.sin(t * 2.4), 300, 520, (g, x, y, w, h) => { g.fillStyle = '#10141a'; g.fillRect(x, y, w, h); txt(g, '实际续航', x + w / 2, y + 90, { size: 32, fam: 'PuHui-Heavy', col: COL.cream, align: 'center' });
      const bat = lerp(0.8, 0.15, ease(t, tHand, tTwo)); g.strokeStyle = COL.cream; g.lineWidth = 4; g.strokeRect(x + 50, y + 170, 200, 80); g.fillStyle = bat < 0.3 ? COL.coral : COL.goldHi; g.fillRect(x + 58, y + 178, 184 * bat, 64);
      txt(g, '1 天', x + w / 2, y + 360, { size: 90, fam: 'PuHui-Heavy', col: COL.coral, align: 'center' }); }); c.restore(); tag(c, '到手', 790, 1100, { size: 42, bg: COL.coral, fg: COL.ink }); }
  if (t > tTwo - 0.3) { for (let n = 0; n < 4; n++) { const r = ((t - tTwo) * 300 + n * 90) % 360; c.save(); c.globalCompositeOperation = 'lighter'; c.strokeStyle = `rgba(127,214,180,${0.5 * (1 - r / 360)})`; c.lineWidth = 5; c.beginPath(); c.arc(W / 2, 1310, 110 + r, 0, 7); c.stroke(); c.restore(); } T.chip(c, W / 2, 1310 + 8 * Math.sin(t * 3), 220, 220, { label: '芯片', t: t * 1.5, glow: 1 }); for (let n = 0; n < 3; n++) { c.strokeStyle = '#9a978f'; c.lineWidth = 5; c.beginPath(); c.moveTo(470 + n * 70, 1130); c.lineTo(480 + n * 70, 1220); c.stroke(); glowDot(c, 480 + n * 70, 1222, 4, GOLD, 0.9); }
    tag(c, '芯片也一样：测出来才算数', W / 2, 1480 - 40, { size: 42, bg: COL.mint, fg: COL.ink, t, at: tTwo - 0.3 }); }
};

// ---------- 2. 第一问：什么路上跑出来的？同样 224G，一米铜缆 vs 几厘米 ----------
SP.MECH.cable = (c, t, sh) => {
  const k = T.cam({ hy: 1500, camH: 300 }); T.bg(c, k, { scroll: t * 200, grid: 0.5 }); T.streams(c, t, { a: 0.16, seed: 11 });
  const tM = kw('k05', '一米'), tCm = kw('k05', '几厘米'), t7 = tCm + 0.5, tHard = 1e9;
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

})();
