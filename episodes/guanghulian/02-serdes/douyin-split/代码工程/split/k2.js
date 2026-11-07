// 第 2 条（第五稿 · 翻译）：没人给节拍，接收端怎么数清连续五个 1？——从每次跳变里对表、锁住节拍、在正中间清点；数据先打乱。
(() => {
const { clamp, lerp } = U; const { W, H, COL, T, kw, txt, tape, tag, pop, ease, seg, hookText, L } = SP;
SP.END = 'q12';
const R = (s) => U.rng(s);
const glowDot = (c, x, y, r, col = [245, 215, 126], a = 1) => { c.save(); c.globalCompositeOperation = 'lighter'; const g = c.createRadialGradient(x, y, 0, x, y, r * 3); g.addColorStop(0, `rgba(255,250,235,${a})`); g.addColorStop(0.3, `rgba(${col},${0.85 * a})`); g.addColorStop(1, `rgba(${col},0)`); c.fillStyle = g; c.beginPath(); c.arc(x, y, r * 3, 0, 7); c.fill(); c.restore(); };
const MINT = [127, 214, 180], CORAL = [239, 125, 98], GOLD = [245, 215, 126];
const wavePts = (bits, x0, bw, yH, yL, xa = -50, xb = W + 50) => { const P = []; bits.forEach((b, i) => { const a = x0 + i * bw, e = a + bw; if (e < xa || a > xb) return; const y = b ? yH : yL; P.push([Math.max(a, xa), y], [Math.min(e, xb), y]); }); return P; };
const metronome = (c, x, y, s, t) => { c.save(); c.translate(x, y); c.fillStyle = '#3a3833'; c.beginPath(); c.moveTo(-s * 0.5, s * 0.6); c.lineTo(s * 0.5, s * 0.6); c.lineTo(s * 0.22, -s * 0.6); c.lineTo(-s * 0.22, -s * 0.6); c.closePath(); c.fill();
  c.strokeStyle = COL.cream; c.lineWidth = 6; c.lineCap = 'round'; const a = 0.45 * Math.sin(t * Math.PI * 2 * 1.2); c.beginPath(); c.moveTo(0, s * 0.45); c.lineTo(Math.sin(a) * s * 0.9, s * 0.45 - Math.cos(a) * s * 0.9); c.stroke(); c.restore(); };

const chatBg = (g, x, y, w, h) => { g.fillStyle = '#ededed'; g.fillRect(x, y, w, h); g.fillStyle = '#f7f7f7'; g.fillRect(x, y, w, 110); txt(g, '小林', x + w / 2, y + 70, { size: 34, fam: 'PuHui-Heavy', col: '#222', align: 'center' }); };
const GARB = '仐晚丂炏耂土斾见乛亍冂兦凵卄夨孒屮巛幵廾彐';
// ---------- 1. 第一帧：「今晚七点，老地方见」发出去，对面收到一串乱码 → 化成一条信号：连着五个 1 是一条直线，4 还是 5？→ 没人打拍子 ----------
SP.MECH.chat = (c, t, sh) => {
  const k = T.cam({ hy: 1500, camH: 300 }); T.bg(c, k, { grid: 0.5, scroll: t * 200 }); T.streams(c, t, { a: 0.14, seed: 4 });
  const tMess = kw('q02', '全乱了'), tBig = kw('q03', '上千亿'), tLine = kw('q03', '一条直线'), t4 = kw('q03', '四个'), t5 = kw('q03', '五个'), tNo = kw('q04', '打拍子'), tQ = kw('q04', '怎么数清');
  const dis = sh.kind === 'chat2' ? ease(t, sh.t0, sh.t0 + 0.8, 'c') : 0;
  if (dis < 1) { c.save(); c.globalAlpha = 1 - dis; c.translate(W / 2, 840 + 10 * Math.sin(t * 2)); c.scale(1 - 0.2 * dis, 1 - 0.2 * dis); c.rotate(0.012 * Math.sin(t * 1.3));
    SP.phone(c, 0, 0, 640, 1060, (g, x, y, w, h) => { chatBg(g, x, y, w, h);
      g.font = '42px "PuHui-Medium"'; const s1 = '今晚七点，老地方见', tw = g.measureText(s1).width; g.fillStyle = '#95ec69'; g.beginPath(); g.roundRect(x + w - tw - 84, y + 200, tw + 46, 88, 16); g.fill(); txt(g, s1, x + w - tw - 61, y + 246, { size: 42, col: '#1b1b1a' });
      const shake = t > tMess - 0.1 && t < tMess + 0.6 ? 8 * Math.sin(t * 60) : 0, r = R(Math.floor(t * (t > tMess - 0.1 ? 14 : 3)));
      let s2 = ''; for (let i = 0; i < 9; i++) s2 += i === 4 ? '，' : GARB[Math.floor(r() * GARB.length)];
      g.fillStyle = '#ffffff'; g.beginPath(); g.roundRect(x + 40 + shake, y + 340, tw + 46, 88, 16); g.fill(); txt(g, s2, x + 63 + shake, y + 386, { size: 42, col: '#1b1b1a' });
      if (dis > 0) { const r2 = R(9); g.save(); g.globalAlpha = dis; g.font = '30px "PuHui-Heavy"'; g.fillStyle = 'rgba(245,215,126,.8)'; for (let n = 0; n < 60; n++) g.fillText(r2() < 0.5 ? '0' : '1', x + 40 + r2() * (w - 80) + (t - tBig) * 400 * r2(), y + 200 + r2() * 300); g.restore(); } });
    c.restore();
    if (dis < 0.2) { c.save(); c.strokeStyle = COL.redHi; c.lineWidth = 5; c.beginPath(); c.moveTo(640, 1080); c.lineTo(400, 720); c.stroke(); c.restore(); tag(c, '少数一个 1', 700, 1110, { size: 56, bg: COL.coral, fg: COL.ink, r: -0.03 }); }
    hookText(c, t, ['少数一个 1，', '这句话就全乱了。'], { y: 1430, size: 54, ids: ['q01', 'q02'], bg: '#0f0f0e' }); }
  if (dis > 0) { c.save(); c.globalAlpha = dis; const FIVE = [0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0], bw = 98, x0 = 2 - ((t - tBig) * 14) % 6, yH = 640, yL = 860;
    T.glowLine(c, wavePts(FIVE, x0, bw, yH, yL), { lw: 8 });
    tag(c, `每秒 ${Math.round(lerp(0, 1000, ease(t, tBig - 0.2, tBig + 1.0, 'o')))} 亿+ 个 0 和 1`, W / 2, 480, { size: 46, bg: COL.goldHi, fg: COL.ink });
    const a = x0 + 3 * bw, b = x0 + 8 * bw;
    if (t > tLine - 0.3) { const q = ease(t, tLine - 0.3, tLine + 0.2); c.save(); c.globalAlpha *= q; c.strokeStyle = COL.redHi; c.lineWidth = 5; c.setLineDash([12, 10]); c.lineDashOffset = -t * 30; c.beginPath(); c.roundRect(a, yH - 44, b - a, 88, 14); c.stroke(); c.restore();
      tag(c, '五个 1 = 一条直线', (a + b) / 2, yH - 100, { size: 42, t, at: tLine - 0.3 }); }
    const rul = (y, n, col, at, lab) => { if (t < at) return; const q = ease(t, at, at + 0.4), step = (b - a) / n; c.save(); c.globalAlpha *= q;
      for (let m = 0; m <= n; m++) T.glowLine(c, [[a + m * step, y], [a + m * step, y + 44]], { col, lw: 4 });
      for (let m = 0; m < n; m++) txt(c, String(m + 1), a + (m + 0.5) * step, y + 84, { size: 50, fam: 'PuHui-Heavy', col: `rgb(${col})`, align: 'center' });
      txt(c, lab, 70, y + 30, { size: 44, fam: 'PuHui-Heavy', col: `rgb(${col})` }); c.restore(); };
    rul(980, 4, CORAL, t4 - 0.2, '4？'); rul(1120, 5, MINT, t5 - 0.2, '5？');
    if (t > tNo - 0.3) { metronome(c, 920, 1320, 80, t); const q2 = ease(t, tNo, tNo + 0.3); c.save(); c.globalAlpha *= q2; c.strokeStyle = COL.redHi; c.lineWidth = 10; c.lineCap = 'round'; c.beginPath(); c.moveTo(850, 1240); c.lineTo(990, 1400); c.moveTo(990, 1240); c.lineTo(850, 1400); c.stroke(); c.restore();
      tag(c, '没人打拍子', 700, 1320, { size: 44, bg: COL.coral, fg: COL.ink, t, at: tNo - 0.3 }); }
    if (t > tQ - 0.2) txt(c, '？', (a + b) / 2, yH - 230, { size: 160 * Math.min(1, pop(t, tQ - 0.2)), fam: 'PuHui-Heavy', col: COL.goldHi, align: 'center' });
    c.restore(); }
};

SP.MECH.chat2 = (c, t, sh) => SP.MECH.chat(c, t, sh);
// ---------- 2. 就像跟着一首歌拍手：一首歌的声波，鼓点处是亮的尖峰；一双手在每个鼓点上拍一下 ----------
SP.MECH.clap = (c, t, sh) => {
  const k = T.cam({ hy: 1500, camH: 300 }); T.bg(c, k, { grid: 0.5, scroll: t * 200 });
  const tSong = kw('q05', '一首歌'), tNo = kw('q05', '没人'), tDrum = kw('q05', '鼓点'), tOn = kw('q05', '跟上');
  const BT = 0.5, PX = 220, off = (t - sh.t0) * PX;   // 每 0.5 s 一个鼓点，声波从右往左流
  // 声波：一根根竖条；鼓点处是高高的亮尖峰
  for (let x = -20; x < W + 20; x += 10) { const u = (x + off) / PX, dr = Math.abs(u - Math.round(u)), hi = Math.exp(-dr * dr * 120), r = R(Math.floor(x + off) & 1023)();
    const hgt = 30 + 60 * r * (0.6 + 0.4 * Math.sin(u * 1.7)) + 260 * hi; c.fillStyle = hi > 0.5 ? `rgba(245,215,126,${0.6 + 0.4 * hi})` : 'rgba(155,232,219,.35)'; c.fillRect(x, 760 - hgt / 2, 6, hgt); }
  // 听的位置（中间的竖线）+ 一双手：鼓点经过这条线时拍一下
  const RXc = W / 2; c.save(); c.globalCompositeOperation = 'lighter'; c.fillStyle = 'rgba(155,232,219,.35)'; c.fillRect(RXc - 2, 560, 4, 400); c.restore();
  const ph = ((RXc + off) / PX) % 1, gap = Math.min(ph, 1 - ph), closed = t > tOn - 1.5 ? clamp(1 - gap * 8) : clamp(1 - Math.abs(ph - 0.35) * 8);
  const hand = (side) => { c.save(); c.translate(RXc + side * lerp(150, 34, closed), 1180); c.rotate(side * -0.25); c.fillStyle = '#e8c4a0'; c.beginPath(); c.roundRect(-55, -120, 110, 230, 50); c.fill();
    for (let f = 0; f < 4; f++) { c.beginPath(); c.roundRect(-52 + f * 27, -200, 24, 100, 12); c.fill(); } c.restore(); };
  hand(-1); hand(1);
  if (closed > 0.85) { c.save(); c.globalCompositeOperation = 'lighter'; c.strokeStyle = `rgba(245,215,126,${closed - 0.6})`; c.lineWidth = 6; for (const r of [70, 110]) { c.beginPath(); c.arc(RXc, 1080, r * (2 - closed), -2.6, -0.5); c.stroke(); } c.restore(); }
  if (t > tSong - 0.3) tag(c, '一首歌', 200, 560, { size: 44, t, at: tSong - 0.3 });
  if (t > tDrum - 0.3) tag(c, '鼓点', RXc + 170, 560, { size: 44, bg: COL.goldHi, fg: COL.ink, t, at: tDrum - 0.3 });
  if (t > tNo - 0.3) { metronome(c, 900, 1420, 60, t); c.save(); c.strokeStyle = COL.redHi; c.lineWidth = 8; c.lineCap = 'round'; c.beginPath(); c.moveTo(850, 1360); c.lineTo(950, 1480); c.moveTo(950, 1360); c.lineTo(850, 1480); c.stroke(); c.restore(); }
  if (t > tOn - 0.3) tag(c, '听着鼓点，就跟上了', RXc, 1420, { size: 46, bg: COL.mint, fg: COL.ink, t, at: tOn - 0.3 });
};

// ---------- 2. 节拍：跳变处对表、早了往后拨晚了往前拨、锁住；在正中间清点五个 ----------
// 信号从右往左流过「接收端」（x = 540 的竖光）。接收端自己的节拍 = 一排薄荷色光柱，和比特中心差 e（像素）；每有一个跳变经过接收端，e 就被拨回去一半。
const RX = 540, BW = 120, VV = 240, yH = 660, yL = 880;
const makeBits = (n, run, seed) => { const r = R(seed), B = []; for (let i = 0; i < n; i++) B.push(r() < 0.5 ? 1 : 0); for (let i = 1; i < run; i++) if (B[i] === B[i - 1] && r() < 0.6) B[i] = 1 - B[i]; B[run - 1] = 0; for (let i = 0; i < 5; i++) B[run + i] = 1; B[run + 5] = 0; return B; };
SP.MECH.beat = (c, t, sh) => {
  const k = T.cam({ hy: 1450, camH: 300 }); T.bg(c, k, { scroll: t * VV, grid: 0.5 });
  const tBeat = kw('q06', '鼓点'), tLen = -9, tEdge = kw('q06', '跳一下'), tFix = kw('q06', '校准'), tLock = kw('q06', '踩准'), tCount = kw('q07', '每一拍'), tFive = kw('q07', '五个');
  const RUN = 40, B = makeBits(70, RUN, 7), tS = sh.t0, X0 = RX + VV * (tCount - 0.4 - tS) - RUN * BW - BW / 2, x0 = X0 - VV * (t - tS);
  // 跳变经过接收端的时刻 → 拨表（从 tFix 开始），误差交替正负、每次减半
  let e = 56 * Math.sin(t * 2.3) + 20 * Math.sin(t * 4.1), lockQ = 0, last = null, nFix = 0;
  if (t > tFix - 0.2) { e = 60; for (let i = 1; i < B.length; i++) if (B[i] !== B[i - 1]) { const tc = tS + (X0 + i * BW - RX) / VV; if (tc < tFix - 0.2 || tc > t) continue; nFix++; e = 60 * Math.pow(-0.75, nFix); last = tc; } const snap = ease(t, tLock - 0.12, tLock + 0.06); e *= 1 - snap; lockQ = snap; }
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
  if (t > tLock - 0.1 && t < tLock + 1.2) { const p = seg(t, tLock - 0.1, tLock + 1.2); c.save(); c.globalCompositeOperation = 'lighter';
    for (const [d, a] of [[0, 0.7], [0.15, 0.45], [0.3, 0.25]]) { const pp = clamp((p - d) / (1 - d)); if (pp <= 0) continue; c.strokeStyle = `rgba(155,232,219,${a * (1 - pp)})`; c.lineWidth = 10 * (1 - pp) + 2; c.beginPath(); c.ellipse(RX, (yH + yL) / 2, 80 + pp * 900, 40 + pp * 450, 0, 0, 7); c.stroke(); }
    c.fillStyle = `rgba(127,214,180,${0.22 * (1 - seg(t, tLock - 0.1, tLock + 0.35))})`; c.fillRect(0, 0, W, H); c.restore(); }
  if (t > tLock - 0.1 && t < tFive - 0.2) tag(c, '咔——踩准了', RX, 470, { size: 66, bg: COL.mint, fg: COL.ink, t, at: tLock - 0.1, r: -0.02 });
  // 正中间看一眼：五个 1 经过接收端，一个一个点亮
  if (t > tCount - 0.5) { for (let i = 0; i < 5; i++) { const xc = x0 + (RUN + i + 0.5) * BW, tc = tS + (X0 + (RUN + i + 0.5) * BW - RX) / VV; if (t < tc) continue; glowDot(c, xc, yH, 14, MINT);
      txt(c, String(i + 1), xc, yH - 80, { size: 64, fam: 'PuHui-Heavy', col: COL.mint, align: 'center' }); } }
  const t5th = tS + (X0 + (RUN + 4.5) * BW - RX) / VV;
  if (t > t5th) tag(c, '五个，不是四个', RX, 470, { size: 60, bg: COL.mint, fg: COL.ink, t, at: t5th });
  else if (t > tFix - 0.3 && t < tLock - 0.1) tag(c, '跟着鼓点校准', RX + 160, 1180, { size: 48, bg: COL.goldHi, fg: COL.ink, t, at: tFix - 0.3 });
  else if (t > tBeat - 0.3 && t < tFix - 0.3) tag(c, '每跳一下 = 一个鼓点', W / 2, 520, { size: 48, bg: COL.goldHi, fg: COL.ink, t, at: tBeat - 0.3 });
};

// ---------- 3. 一长串 1 没有跳变 → 节拍跑偏；先打乱、收到再还原 ----------
SP.MECH.scramble = (c, t, sh) => {
  const k = T.cam({ hy: 1450, camH: 300 }); T.bg(c, k, { scroll: t * VV, grid: 0.5 });
  const tLong = kw('q08', '一长串'), tNo = kw('q08', '没有鼓点'), tDrift = kw('q08', '跑偏'), tMix = kw('q09', '打乱'), tOft = kw('q09', '鼓点'), tBack = kw('q09', '还原');
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
  if (t > tLong - 0.2 && mix < 0.5) tag(c, t > tNo - 0.2 ? '长音：没有鼓点，拍子跑偏' : '一长串 1 = 一个长音', W / 2, 560, { size: 46, bg: COL.coral, fg: COL.ink, t, at: t > tNo - 0.2 ? tNo - 0.2 : tLong - 0.2 });
  // 发出去之前：一排 1 像老虎机一样打乱；收到以后：再还原回一排 1
  const row = (y, lab, digits, q) => { c.save(); c.globalAlpha = q; txt(c, lab, 70, y - 70, { size: 38, fam: 'PuHui-Heavy', col: COL.cream });
    digits.forEach((d, i) => { const x = 110 + i * 86; c.fillStyle = 'rgba(8,10,11,.9)'; c.strokeStyle = 'rgba(226,181,74,.5)'; c.lineWidth = 2; c.beginPath(); c.roundRect(x - 36, y - 40, 72, 80, 10); c.fill(); c.stroke();
      txt(c, String(d), x, y + 2, { size: 52, fam: 'PuHui-Heavy', col: COL.goldHi, align: 'center' }); }); c.restore(); };
  if (t > tMix - 0.4) { const q = ease(t, tMix - 0.4, tMix); const spin = t < tMix + 0.9, dg = Array(11).fill(0).map((_, i) => spin ? (Math.floor(t * 24 + i * 3) % 2) : MIX[i]);
    row(360, '发出去之前：打乱', t < tMix ? Array(11).fill(1) : dg, q); }
  if (t > tBack - 0.4) { const q = ease(t, tBack - 0.4, tBack); const spin = t < tBack + 0.45, dg = Array(11).fill(0).map((_, i) => spin ? (Math.floor(t * 24 + i * 5) % 2) : 1);
    row(1230, '收到以后：还原', dg, q); }
  if (t > tBack + 0.4) { const q = Math.min(1, pop(t, tBack + 0.4)); c.save(); c.translate(W / 2, 1460); c.scale(q, q); c.fillStyle = '#ffffff'; c.beginPath(); c.roundRect(-330, -55, 660, 110, 18); c.fill(); txt(c, '今晚七点，老地方见', 0, 2, { size: 46, fam: 'PuHui-Medium', col: '#1b1b1a', align: 'center' }); c.restore(); tag(c, '✓ 一字不差', W / 2 + 300, 1380, { size: 40, bg: COL.mint, fg: COL.ink }); }
  if (t > tOft - 0.2 && t < tBack - 0.4) tag(c, '鼓点一直都在，重新踩准', W / 2, 1230, { size: 44, bg: COL.mint, fg: COL.ink, t, at: tOft - 0.2 });
};
})();
