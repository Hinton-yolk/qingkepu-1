// 第 2 条（第四稿）：没人给节拍，接收端怎么数清连续五个 1？——从每次跳变里对表、锁住节拍、在正中间清点；数据先打乱。
(() => {
const { clamp, lerp } = U; const { W, H, COL, T, kw, txt, tape, tag, pop, ease, seg, hookText, L } = SP;
SP.END = 'v13';
const R = (s) => U.rng(s);
const glowDot = (c, x, y, r, col = [245, 215, 126], a = 1) => { c.save(); c.globalCompositeOperation = 'lighter'; const g = c.createRadialGradient(x, y, 0, x, y, r * 3); g.addColorStop(0, `rgba(255,250,235,${a})`); g.addColorStop(0.3, `rgba(${col},${0.85 * a})`); g.addColorStop(1, `rgba(${col},0)`); c.fillStyle = g; c.beginPath(); c.arc(x, y, r * 3, 0, 7); c.fill(); c.restore(); };
const MINT = [127, 214, 180], CORAL = [239, 125, 98], GOLD = [245, 215, 126];
const wavePts = (bits, x0, bw, yH, yL, xa = -50, xb = W + 50) => { const P = []; bits.forEach((b, i) => { const a = x0 + i * bw, e = a + bw; if (e < xa || a > xb) return; const y = b ? yH : yL; P.push([Math.max(a, xa), y], [Math.min(e, xb), y]); }); return P; };
const metronome = (c, x, y, s, t) => { c.save(); c.translate(x, y); c.fillStyle = '#3a3833'; c.beginPath(); c.moveTo(-s * 0.5, s * 0.6); c.lineTo(s * 0.5, s * 0.6); c.lineTo(s * 0.22, -s * 0.6); c.lineTo(-s * 0.22, -s * 0.6); c.closePath(); c.fill();
  c.strokeStyle = COL.cream; c.lineWidth = 6; c.lineCap = 'round'; const a = 0.45 * Math.sin(t * Math.PI * 2 * 1.2); c.beginPath(); c.moveTo(0, s * 0.45); c.lineTo(Math.sin(a) * s * 0.9, s * 0.45 - Math.cos(a) * s * 0.9); c.stroke(); c.restore(); };

// ---------- 1. 第一帧：一条巨大的发光信号从深处斜着冲到眼前 → 都是 0 和 1 → 连续五个 1 是一条直线：4 还是 5？→ 没人打拍子 ----------
SP.MECH.ribbon = (c, t, sh) => {
  const t2 = L.v02.t0, t3 = L.v03.t0, tLine = kw('v03', '一条直线'), t4n = kw('v03', '四个'), t5n = kw('v03', '五个'), tErr = kw('v04', '数错'), tBig = kw('v04', '上千亿'), tNo = kw('v04', '没人');
  const k = T.cam({ hy: 760, camH: 250, f: lerp(900, 1080, ease(t, 0, sh.t1, 's')), cx: 60 * Math.sin(t * 0.4) }); T.bg(c, k, { scroll: t * 300, grid: 0.7 }); T.streams(c, t, { a: 0.14, seed: 7 });
  const B = [0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 1, 0, 1], n = B.length, at = u => [lerp(-560, 900, u), lerp(330, 2600, u)];
  const err = t > tErr - 0.05 && t < tErr + 0.5, pts = [];
  B.forEach((b, i) => { for (const u of [i / n, (i + 1) / n]) { const [x, z] = at(u); pts.push(T.P(k, x, b ? 520 : 120, z)); } });
  T.glowLine(c, pts, { lw: 11, col: err ? CORAL : GOLD });
  // 信号上流动的光点
  for (let m = 0; m < 6; m++) { const u = ((t * 0.12 + m / 6) % 1), i = Math.floor(u * n), [x, z] = at(u), p = T.P(k, x, B[i] ? 520 : 120, z); glowDot(c, p[0], p[1], 10 * p[2], GOLD, 0.9); }
  // 每一位上方浮着 0 / 1
  if (t > t2 - 0.2) B.forEach((b, i) => { const [x, z] = at((i + 0.5) / n), p = T.P(k, x, 700, z), q = ease(t, t2 - 0.2 + i * 0.04, t2 + 0.2 + i * 0.04); if (q <= 0) return; txt(c, String(b), p[0], p[1] - 10 * Math.sin(t * 3 + i), { size: Math.max(22, 110 * p[2]), fam: 'PuHui-Heavy', col: 'rgba(245,215,126,.9)', align: 'center', alpha: q * (1 - ease(t, tLine - 0.2, tLine + 0.4)) }); });
  // 那一段平平的高电平：红色虚线框住；4？5？轮流亮
  if (t > tLine - 0.3) { const [xa, za] = at(3 / n), [xb, zb] = at(8 / n), A = T.P(k, xa, 600, za), Bp = T.P(k, xb, 600, zb), q = ease(t, tLine - 0.3, tLine + 0.2);
    c.save(); c.globalAlpha = q; c.strokeStyle = COL.redHi; c.lineWidth = 6; c.setLineDash([14, 10]); c.lineDashOffset = -t * 40; c.beginPath(); c.moveTo(A[0], A[1]); c.lineTo(Bp[0], Bp[1]); c.stroke(); c.restore(); }
  const f4 = t > t4n - 0.2 ? 0.5 + 0.5 * Math.sin(t * 6) : 0, f5 = t > t5n - 0.2 ? 0.5 - 0.5 * Math.sin(t * 6) : 0;
  if (t > t4n - 0.2) txt(c, '4？', 300, 1330, { size: 130 + 20 * f4, fam: 'PuHui-Heavy', col: COL.coral, align: 'center', alpha: 0.5 + 0.5 * f4 });
  if (t > t5n - 0.2) txt(c, '5？', 760, 1330, { size: 130 + 20 * f5, fam: 'PuHui-Heavy', col: COL.mint, align: 'center', alpha: 0.5 + 0.5 * f5 });
  if (err) { c.save(); c.fillStyle = `rgba(239,125,98,${0.25 * (1 - seg(t, tErr - 0.05, tErr + 0.5))})`; c.fillRect(0, 0, W, H); const r = R(Math.floor(t * 20)); for (let m = 0; m < 10; m++) { c.fillStyle = ['rgba(43,208,192,.5)', 'rgba(224,79,138,.5)', 'rgba(242,225,74,.4)'][m % 3]; c.fillRect(r() * W, 300 + r() * 1100, 80 + r() * 400, 8 + r() * 30); } c.restore(); }
  if (t > tBig - 0.3) { const q = ease(t, tBig - 0.3, tBig + 0.2); c.save(); c.globalAlpha = q; c.fillStyle = 'rgba(8,10,11,.9)'; c.beginPath(); c.roundRect(110, 1180 - 0, 860, 210, 20); c.fill(); c.strokeStyle = 'rgba(226,181,74,.4)'; c.lineWidth = 2; c.stroke();
    txt(c, `每秒 ${Math.round(lerp(0, 1000, ease(t, tBig - 0.2, tBig + 1.0, 'o')))} 亿+ 个`, W / 2, 1260, { size: 76, fam: 'PuHui-Heavy', col: COL.goldHi, align: 'center' }); txt(c, 'AI 芯片之间，每条通道', W / 2, 1345, { size: 36, fam: 'PuHui-Heavy', col: COL.cream, align: 'center' }); c.restore(); }
  if (t > tNo - 0.2) tape(c, '没人给它打拍子', W / 2, 470, { size: 70, t, at: tNo - 0.2, r: -0.02 });
  const up = ease(t, t3 - 0.3, t3 + 0.3, 'c');
  if (up < 1) { c.save(); c.globalAlpha = 1 - up; hookText(c, t, ['这一段，', '是几个 1？'], { y: 260, size: 96 });
    hookText(c, t, ['你刷的每条视频，', '都是一串 0 和 1。'], { y: 1520, size: 62, ids: ['v01', 'v02'], bg: '#0f0f0e' }); c.restore(); }
};

// ---------- 2. 节拍：跳变处对表、早了往后拨晚了往前拨、锁住；在正中间清点五个 ----------
// 信号从右往左流过「接收端」（x = 540 的竖光）。接收端自己的节拍 = 一排薄荷色光柱，和比特中心差 e（像素）；每有一个跳变经过接收端，e 就被拨回去一半。
const RX = 540, BW = 120, VV = 240, yH = 660, yL = 880;
const makeBits = (n, run, seed) => { const r = R(seed), B = []; for (let i = 0; i < n; i++) B.push(r() < 0.5 ? 1 : 0); for (let i = 1; i < run; i++) if (B[i] === B[i - 1] && r() < 0.6) B[i] = 1 - B[i]; B[run - 1] = 0; for (let i = 0; i < 5; i++) B[run + i] = 1; B[run + 5] = 0; return B; };
SP.MECH.beat = (c, t, sh) => {
  const k = T.cam({ hy: 1450, camH: 300 }); T.bg(c, k, { scroll: t * VV, grid: 0.5 });
  const tBeat = kw('v05', '节拍'), tLen = kw('v05', '多长'), tEdge = kw('v06', '跳变'), tFix = kw('v06', '对一次表'), tLock = kw('v07', '锁住'), tCount = kw('v08', '正中间'), tFive = kw('v08', '五个');
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
  if (t > tLock - 0.1 && t < tFive - 0.2) tape(c, '咔——锁住了', W / 2, 470, { size: 76, bg: COL.mint, fg: COL.ink, t, at: tLock - 0.1, r: -0.02 });
  // 正中间看一眼：五个 1 经过接收端，一个一个点亮
  if (t > tCount - 0.5) { for (let i = 0; i < 5; i++) { const xc = x0 + (RUN + i + 0.5) * BW, tc = tS + (X0 + (RUN + i + 0.5) * BW - RX) / VV; if (t < tc) continue; glowDot(c, xc, yH, 14, MINT);
      txt(c, String(i + 1), xc, yH - 80, { size: 64, fam: 'PuHui-Heavy', col: COL.mint, align: 'center' }); } }
  const t5th = tS + (X0 + (RUN + 4.5) * BW - RX) / VV;
  if (t > t5th) tape(c, '五个，不是四个', W / 2, 360, { size: 64, t, at: t5th });
  else if (t > tFix - 0.3 && t < tLock - 0.1) tape(c, '每次跳变，对一次表', W / 2, 360, { size: 58, t, at: tFix - 0.3 });
  else if (t > tBeat - 0.3 && t < tFix - 0.3) tape(c, '每一位多长 = 节拍', W / 2, 360, { size: 58, t, at: tBeat - 0.3 });
};

// ---------- 3. 一长串 1 没有跳变 → 节拍跑偏；先打乱、收到再还原 ----------
SP.MECH.scramble = (c, t, sh) => {
  const k = T.cam({ hy: 1450, camH: 300 }); T.bg(c, k, { scroll: t * VV, grid: 0.5 });
  const tLong = kw('v09', '一长串'), tNo = kw('v09', '没有跳变'), tDrift = kw('v09', '跑偏'), tMix = kw('v10', '打乱'), tOft = tMix + 0.9, tBack = kw('v10', '还原');
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
