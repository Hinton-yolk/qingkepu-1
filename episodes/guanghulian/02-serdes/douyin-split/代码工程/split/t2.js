// 第 2 条（第三稿）：没人给节拍，接收端怎么数清连续五个 1？——从每次跳变里对表、锁住节拍、在正中间清点；数据先打乱。
(() => {
const { clamp, lerp } = U; const { W, H, COL, T, kw, txt, tape, tag, pop, ease, seg, hookText, L } = SP;
SP.END = 'y14';
const R = (s) => U.rng(s);
const glowDot = (c, x, y, r, col = [245, 215, 126], a = 1) => { c.save(); c.globalCompositeOperation = 'lighter'; const g = c.createRadialGradient(x, y, 0, x, y, r * 3); g.addColorStop(0, `rgba(255,250,235,${a})`); g.addColorStop(0.3, `rgba(${col},${0.85 * a})`); g.addColorStop(1, `rgba(${col},0)`); c.fillStyle = g; c.beginPath(); c.arc(x, y, r * 3, 0, 7); c.fill(); c.restore(); };
const MINT = [127, 214, 180], CORAL = [239, 125, 98], GOLD = [245, 215, 126];
const wavePts = (bits, x0, bw, yH, yL, xa = -50, xb = W + 50) => { const P = []; bits.forEach((b, i) => { const a = x0 + i * bw, e = a + bw; if (e < xa || a > xb) return; const y = b ? yH : yL; P.push([Math.max(a, xa), y], [Math.min(e, xb), y]); }); return P; };
const metronome = (c, x, y, s, t) => { c.save(); c.translate(x, y); c.fillStyle = '#3a3833'; c.beginPath(); c.moveTo(-s * 0.5, s * 0.6); c.lineTo(s * 0.5, s * 0.6); c.lineTo(s * 0.22, -s * 0.6); c.lineTo(-s * 0.22, -s * 0.6); c.closePath(); c.fill();
  c.strokeStyle = COL.cream; c.lineWidth = 6; c.lineCap = 'round'; const a = 0.45 * Math.sin(t * Math.PI * 2 * 1.2); c.beginPath(); c.moveTo(0, s * 0.45); c.lineTo(Math.sin(a) * s * 0.9, s * 0.45 - Math.cos(a) * s * 0.9); c.stroke(); c.restore(); };

// ---------- 1. 你刷的每条视频都是 0 和 1 → 线上没有分开的 0 和 1 → 四个还是五个？→ 没人告诉它节拍 ----------
SP.MECH.video = (c, t, sh) => {
  const k = T.cam({ hy: 1500, camH: 300 }); T.bg(c, k, { scroll: t * 200, grid: 0.5 }); T.streams(c, t, { a: 0.2, seed: 7 });
  const t2 = L.y02.t0, t3 = L.y03.t0, tLine = kw('y03', '一条直线'), t4 = L.y04.t0, t5n = kw('y04', '五个'), tErr = kw('y04', '数错'), t5 = L.y05.t0, tNo = kw('y05', '没人告诉'), tQ = kw('y05', '怎么数清');
  const dig = ease(t, t2, t2 + 1.0), away = ease(t, t3 - 0.2, t3 + 0.6, 'c');
  const vid = (g, x, y, w, h, gl = false) => { const sky = g.createLinearGradient(0, y, 0, y + h); sky.addColorStop(0, '#f2c27a'); sky.addColorStop(0.55, '#e98a5c'); sky.addColorStop(1, '#5c3a52'); g.fillStyle = sky; g.fillRect(x, y, w, h);
    g.fillStyle = '#fff2c9'; g.beginPath(); g.arc(x + w * 0.62 + Math.sin(t * 1.1) * 20, y + h * 0.42 + Math.sin(t * 0.8) * 16, w * 0.12, 0, 7); g.fill();
    g.fillStyle = '#3b2a3c'; g.beginPath(); g.moveTo(x, y + h * 0.7); for (let n = 0; n <= 12; n++) g.lineTo(x + w * n / 12, y + h * (0.62 + 0.08 * Math.sin(n * 1.7 + 1))); g.lineTo(x + w, y + h); g.lineTo(x, y + h); g.fill();
    g.fillStyle = '#241a27'; g.beginPath(); g.moveTo(x, y + h * 0.82); for (let n = 0; n <= 12; n++) g.lineTo(x + w * n / 12, y + h * (0.78 + 0.05 * Math.sin(n * 2.3))); g.lineTo(x + w, y + h); g.lineTo(x, y + h); g.fill();
    if (gl) { const r = R(Math.floor(t * 12)); for (let n = 0; n < 9; n++) { g.fillStyle = ['#2bd0c0', '#e04f8a', '#7a7a7a', '#f2e14a'][n % 4]; g.fillRect(x + r() * w, y + r() * h, 30 + r() * w * 0.4, 10 + r() * 40); } }
    g.fillStyle = 'rgba(255,255,255,.85)'; g.fillRect(x + 30, y + h - 40, (w - 60) * ((t * 0.05) % 1), 6); g.fillStyle = 'rgba(255,255,255,.3)'; g.fillRect(x + 30, y + h - 40, w - 60, 6); };
  if (away < 1) { c.save(); c.globalAlpha = 1 - away; c.translate(0, 12 * Math.sin(t * 2.2)); c.translate(W / 2, 900); c.rotate(0.015 * Math.sin(t * 1.4)); c.translate(-W / 2, -900); SP.phone(c, W / 2, 900, 600, 1060, (g, x, y, w, h) => { vid(g, x, y, w, h);
      if (dig > 0) { const r = R(3); g.save(); g.globalAlpha = dig; g.fillStyle = 'rgba(8,10,11,.86)'; g.fillRect(x, y, w, h); g.font = '34px "PuHui-Heavy"'; g.textAlign = 'center';
        for (let n = 0; n < 15; n++) for (let j = 0; j < 26; j++) { const b = r() < 0.5 ? '0' : '1'; g.fillStyle = (j + n + Math.floor(t * 8)) % 9 === 0 ? '#fff6d6' : 'rgba(245,215,126,.6)'; g.fillText(b, x + 20 + n * 36, y + 40 + ((j * 38 + t * 260) % (h + 40))); } g.restore(); } }); c.restore(); }
  if (away > 0) { c.save(); c.globalAlpha = away; const FIVE = [0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0], bw = 98, x0 = 2 - ((t - t3) * 14) % 6, yH = 640, yL = 860;
    T.glowLine(c, wavePts(FIVE, x0, bw, yH, yL), { lw: 8 });
    const a = x0 + 3 * bw, b = x0 + 8 * bw;
    if (t > tLine - 0.3 && t < t5 - 0.3) { const q = ease(t, tLine - 0.3, tLine + 0.2); c.save(); c.globalAlpha *= q; c.strokeStyle = COL.redHi; c.lineWidth = 5; c.setLineDash([12, 10]); c.lineDashOffset = -t * 30; c.beginPath(); c.roundRect(a, yH - 44, b - a, 88, 14); c.stroke(); c.restore();
      tag(c, '一条直线', (a + b) / 2, yH - 110, { size: 44, t, at: tLine - 0.3 }); }
    const rul = (y, n, col, at, lab) => { if (t < at) return; const q = ease(t, at, at + 0.4), step = (b - a) / n; c.save(); c.globalAlpha *= q;
      for (let m = 0; m <= n; m++) T.glowLine(c, [[a + m * step, y], [a + m * step, y + 44]], { col, lw: 4 });
      for (let m = 0; m < n; m++) txt(c, String(m + 1), a + (m + 0.5) * step, y + 84, { size: 50, fam: 'PuHui-Heavy', col: `rgb(${col})`, align: 'center' });
      txt(c, lab, 70, y + 30, { size: 44, fam: 'PuHui-Heavy', col: `rgb(${col})` }); c.restore(); };
    rul(1000, 4, CORAL, t4 - 0.2, '4？'); rul(1150, 5, MINT, t5n - 0.2, '5？');
    if (t > tErr - 0.1 && t < t5 + 0.3) { const q = Math.min(1, pop(t, tErr - 0.1)); c.save(); c.translate(810, 440); c.scale(q, q); c.fillStyle = '#121211'; c.beginPath(); c.roundRect(-150, -100, 300, 200, 18); c.fill();
      c.beginPath(); c.roundRect(-138, -88, 276, 176, 12); c.clip(); vid(c, -138, -88, 276, 176, true); c.restore(); tag(c, '数错一个，数据就错了', 360, 440, { size: 40, bg: COL.coral, fg: COL.ink, t, at: tErr }); }
    c.restore(); }
  if (t > t5 - 0.2) { const q = ease(t, t5 - 0.2, t5 + 0.3); c.save(); c.globalAlpha = q; c.fillStyle = 'rgba(8,10,11,.9)'; c.beginPath(); c.roundRect(110, 300, 860, 230, 20); c.fill(); c.strokeStyle = 'rgba(226,181,74,.4)'; c.lineWidth = 2; c.stroke();
    txt(c, `每秒 ${Math.round(lerp(0, 1000, ease(t, t5, t5 + 1.2, 'o')))} 亿+ 次`, W / 2, 390, { size: 76, fam: 'PuHui-Heavy', col: COL.goldHi, align: 'center' }); txt(c, 'AI 芯片之间，每条通道', W / 2, 480, { size: 38, fam: 'PuHui-Heavy', col: COL.cream, align: 'center' }); c.restore();
    if (t > tNo - 0.2) { metronome(c, 920, 1330, 80, t); const q2 = ease(t, tNo, tNo + 0.3); c.save(); c.globalAlpha = q2; c.strokeStyle = COL.redHi; c.lineWidth = 10; c.lineCap = 'round'; c.beginPath(); c.moveTo(850, 1250); c.lineTo(990, 1410); c.moveTo(990, 1250); c.lineTo(850, 1410); c.stroke(); c.restore(); }
    if (t > tQ - 0.2) tape(c, '它怎么数清？', W / 2 - 60, 1330, { size: 70, t, at: tQ - 0.2, r: -0.02 }); }
  const up = ease(t, t3 - 0.3, t3 + 0.3, 'c');
  if (up < 1) { c.save(); c.globalAlpha = 1 - up; hookText(c, t, ['数错一个 0 和 1，', '会怎样？'], { y: 220, size: 68 });
    hookText(c, t, ['你刷的每条视频，', '都是一串 0 和 1。'], { y: 1520, size: 62, ids: ['y01', 'y02'], bg: '#0f0f0e' }); c.restore(); }
};

// ---------- 2. 节拍：跳变处对表、早了往后拨晚了往前拨、锁住；在正中间清点五个 ----------
// 信号从右往左流过「接收端」（x = 540 的竖光）。接收端自己的节拍 = 一排薄荷色光柱，和比特中心差 e（像素）；每有一个跳变经过接收端，e 就被拨回去一半。
const RX = 540, BW = 120, VV = 170, yH = 660, yL = 880;
const makeBits = (n, run, seed) => { const r = R(seed), B = []; for (let i = 0; i < n; i++) B.push(r() < 0.5 ? 1 : 0); for (let i = 1; i < run; i++) if (B[i] === B[i - 1] && r() < 0.6) B[i] = 1 - B[i]; B[run - 1] = 0; for (let i = 0; i < 5; i++) B[run + i] = 1; B[run + 5] = 0; return B; };
SP.MECH.beat = (c, t, sh) => {
  const k = T.cam({ hy: 1450, camH: 300 }); T.bg(c, k, { scroll: t * VV, grid: 0.5 });
  const tBeat = kw('y06', '节拍'), tLen = kw('y06', '多长'), tEdge = kw('y07', '跳变'), tFix = kw('y07', '对一次表'), tLock = kw('y08', '锁住'), tCount = kw('y09', '一个一个'), tFive = kw('y09', '五个');
  const RUN = 40, B = makeBits(70, RUN, 7), tS = sh.t0, X0 = RX + VV * (tCount - tS) - RUN * BW, x0 = X0 - VV * (t - tS);
  // 跳变经过接收端的时刻 → 拨表（从 tFix 开始），误差交替正负、每次减半
  let e = 56 * Math.sin(t * 2.3) + 20 * Math.sin(t * 4.1), lockQ = 0, last = null, nFix = 0;
  if (t > tFix - 0.2) { e = 60; for (let i = 1; i < B.length; i++) if (B[i] !== B[i - 1]) { const tc = tS + (X0 + i * BW - RX) / VV; if (tc < tFix - 0.2 || tc > t) continue; nFix++; e = 60 * Math.pow(-0.45, nFix); last = tc; } lockQ = clamp(1 - Math.abs(e) / 8); }
  T.glowLine(c, wavePts(B, x0, BW, yH, yL), { lw: 8 });
  // 跳变闪光
  if (t > tEdge - 0.3) for (let i = 1; i < B.length; i++) if (B[i] !== B[i - 1]) { const x = x0 + i * BW; if (x < -40 || x > W + 40) continue; const near = 1 - clamp(Math.abs(x - RX) / 200); glowDot(c, x, (yH + yL) / 2, 10 + 10 * near, GOLD, 0.35 + 0.6 * near); }
  // 接收端
  c.save(); c.globalCompositeOperation = 'lighter'; const g = c.createLinearGradient(0, 520, 0, 1040); g.addColorStop(0, 'rgba(155,232,219,0)'); g.addColorStop(0.5, 'rgba(155,232,219,.5)'); g.addColorStop(1, 'rgba(155,232,219,0)'); c.fillStyle = g; c.fillRect(RX - 3, 520, 6, 520); c.restore();
  txt(c, '接收端', RX, 1080, { size: 36, fam: 'PuHui-Heavy', col: COL.tealHi, align: 'center' });
  // 节拍光柱
  const showT = ease(t, tBeat - 0.4, tBeat + 0.2);
  if (showT > 0) { const col = lockQ > 0.9 ? MINT : t > tFix - 0.2 ? [200, 220, 210] : CORAL;
    for (let m = -6; m < 16; m++) { const x = x0 + (Math.floor((RX - x0) / BW) + m - 4 + 0.5) * BW + e; if (x < 20 || x > W - 20) continue; c.save(); c.globalAlpha = showT; T.glowLine(c, [[x, yL + 70], [x, yL + 140]], { col, lw: 5 }); c.restore(); }
    if (t < tLen + 0.8 && t > tLen - 0.4) { const xa = x0 + Math.floor((RX - x0) / BW) * BW; c.save(); c.strokeStyle = COL.cream; c.lineWidth = 4; c.beginPath(); c.moveTo(xa, 1210); c.lineTo(xa + BW, 1210); c.stroke(); c.restore(); txt(c, '一个比特这么长', xa + BW / 2, 1260, { size: 36, fam: 'PuHui-Heavy', col: COL.cream, align: 'center' }); } }
  // 拨表：每次跳变经过时，接收端旁边一个小箭头（往后 / 往前）
  if (last != null && t - last < 0.5 && lockQ < 0.95) { const back = nFix % 2 === 1; txt(c, back ? '← 往前拨' : '往后拨 →', RX, 560, { size: 40, fam: 'PuHui-Heavy', col: COL.goldHi, align: 'center', alpha: 1 - (t - last) / 0.5 }); }
  if (t > tLock - 0.3 && lockQ > 0.9) tag(c, '节拍锁住了', RX, 470, { size: 48, bg: COL.mint, fg: COL.ink, t, at: tLock - 0.3 });
  // 正中间看一眼：五个 1 经过接收端，一个一个点亮
  if (t > tCount - 0.5) { for (let i = 0; i < 5; i++) { const xc = x0 + (RUN + i + 0.5) * BW, tc = tS + (X0 + (RUN + i + 0.5) * BW - RX) / VV; if (t < tc) continue; glowDot(c, xc, yH, 14, MINT);
      txt(c, String(i + 1), xc, yH - 80, { size: 64, fam: 'PuHui-Heavy', col: COL.mint, align: 'center' }); } }
  if (t > tFive - 0.2) tape(c, '五个，不是四个', W / 2, 360, { size: 64, t, at: tFive - 0.2 });
  else if (t > tFix - 0.3) tape(c, '每次跳变，对一次表', W / 2, 360, { size: 58, t, at: tFix - 0.3 });
  else if (t > tBeat - 0.3) tape(c, '每个比特多长 = 节拍', W / 2, 360, { size: 58, t, at: tBeat - 0.3 });
};

// ---------- 3. 一长串 1 没有跳变 → 节拍跑偏；先打乱、收到再还原 ----------
SP.MECH.scramble = (c, t, sh) => {
  const k = T.cam({ hy: 1450, camH: 300 }); T.bg(c, k, { scroll: t * VV, grid: 0.5 });
  const tLong = kw('y10', '一长串'), tNo = kw('y10', '没有跳变'), tDrift = kw('y10', '跑偏'), tMix = kw('y11', '打乱'), tOft = kw('y11', '够勤'), tBack = kw('y11', '还原');
  const mix = ease(t, tMix - 0.2, tMix + 0.6, 'c'), x0 = 40 - VV * (t - sh.t0);
  const RAW = Array(40).fill(1), r = R(11), MIX = RAW.map((_, i) => (i % 2 ? 0 : 1) ^ (r() < 0.35 ? 1 : 0));
  const B = mix < 0.5 ? RAW.map((v, i) => (i < 2 ? i % 2 : v)) : MIX;
  T.glowLine(c, wavePts(B, x0 % (BW * 2) - BW * 2, BW, yH, yL), { lw: 8, col: mix < 0.5 ? GOLD : GOLD });
  // 接收端
  c.save(); c.globalCompositeOperation = 'lighter'; const g = c.createLinearGradient(0, 520, 0, 1040); g.addColorStop(0, 'rgba(155,232,219,0)'); g.addColorStop(0.5, 'rgba(155,232,219,.5)'); g.addColorStop(1, 'rgba(155,232,219,0)'); c.fillStyle = g; c.fillRect(RX - 3, 520, 6, 520); c.restore();
  // 节拍光柱：没有跳变时慢慢漂走（变珊瑚色）；打乱以后重新锁住
  const drift = mix < 0.5 ? 8 + 26 * clamp((t - tNo) / 3) * (t > tNo ? 1 : 0) + 8 * Math.sin(t * 2) : lerp(40, 0, ease(t, tMix + 0.3, tOft + 0.5));
  const bad = Math.abs(drift) > 22, xb = (x0 % BW) - BW;
  for (let m = 0; m < 12; m++) { const x = xb + (m + 0.5) * BW + drift * (1 + m * 0.08); if (x < 20 || x > W - 20) continue; T.glowLine(c, [[x, yL + 70], [x, yL + 140]], { col: bad ? CORAL : MINT, lw: 5 }); }
  if (t > tNo - 0.2 && mix < 0.5) tape(c, '没有跳变，节拍会跑偏', W / 2, 360, { size: 58, bg: COL.red, t, at: tNo - 0.2 });
  // 发出去之前：一排 1 像老虎机一样打乱；收到以后：再还原回一排 1
  const row = (y, lab, digits, q) => { c.save(); c.globalAlpha = q; txt(c, lab, 70, y - 70, { size: 38, fam: 'PuHui-Heavy', col: COL.cream });
    digits.forEach((d, i) => { const x = 110 + i * 86; c.fillStyle = 'rgba(8,10,11,.9)'; c.strokeStyle = 'rgba(226,181,74,.5)'; c.lineWidth = 2; c.beginPath(); c.roundRect(x - 36, y - 40, 72, 80, 10); c.fill(); c.stroke();
      txt(c, String(d), x, y + 2, { size: 52, fam: 'PuHui-Heavy', col: COL.goldHi, align: 'center' }); }); c.restore(); };
  if (t > tMix - 0.4) { const q = ease(t, tMix - 0.4, tMix); const spin = t < tMix + 0.9, dg = Array(11).fill(0).map((_, i) => spin ? (Math.floor(t * 24 + i * 3) % 2) : MIX[i]);
    row(360, '发出去之前：打乱', t < tMix ? Array(11).fill(1) : dg, q); }
  if (t > tBack - 0.4) { const q = ease(t, tBack - 0.4, tBack); const spin = t < tBack + 0.9, dg = Array(11).fill(0).map((_, i) => spin ? (Math.floor(t * 24 + i * 5) % 2) : 1);
    row(1230, '收到以后：还原', dg, q); if (t > tBack + 1.0) txt(c, '✓', 1010, 1232, { size: 64, fam: 'PuHui-Heavy', col: COL.mint, align: 'center' }); }
  if (t > tOft - 0.2 && t < tBack - 0.4) tag(c, '跳变够多，节拍重新锁住', W / 2, 1230, { size: 44, bg: COL.mint, fg: COL.ink, t, at: tOft - 0.2 });
};
})();
