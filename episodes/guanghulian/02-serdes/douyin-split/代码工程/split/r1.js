// 第 1 条（第四稿）：AI 芯片之间，最快的路只有几条？第一帧 = 光的隧道；高潮 = 子弹时间里晚到的那一位 + 整批数据碎开。
(() => {
const { clamp, lerp } = U; const { W, H, COL, T, kw, txt, tape, tag, pop, ease, seg, hookText, L } = SP;
SP.END = 'w12';
const R = (s) => U.rng(s);
const GOLD = [245, 215, 126], CORAL = [239, 125, 98];
const glowDot = (c, x, y, r, col = GOLD, a = 1) => { c.save(); c.globalCompositeOperation = 'lighter'; const g = c.createRadialGradient(x, y, 0, x, y, r * 3); g.addColorStop(0, `rgba(255,250,235,${a})`); g.addColorStop(0.3, `rgba(${col},${0.85 * a})`); g.addColorStop(1, `rgba(${col},0)`); c.fillStyle = g; c.beginPath(); c.arc(x, y, r * 3, 0, 7); c.fill(); c.restore(); };

// ---------- 光的隧道：四面墙上都是通道，光点从深处冲向镜头。keep(n) 决定哪些通道还亮着 ----------
const LANES = (() => { const a = []; for (let i = -7; i <= 7; i++) { a.push([i * 130, 600]); a.push([i * 130, -600]); } for (let j = -4; j <= 4; j++) { a.push([-950, j * 130]); a.push([950, j * 130]); } return a; })();
const tunnel = (c, t, { cx = W / 2, cy = 860, speed = 1, keep = () => 1, dim = 1 } = {}) => {
  c.fillStyle = '#040506'; c.fillRect(0, 0, W, H);
  const g = c.createRadialGradient(cx, cy, 0, cx, cy, 520); g.addColorStop(0, `rgba(245,215,126,${0.35 * dim})`); g.addColorStop(1, 'rgba(245,215,126,0)'); c.fillStyle = g; c.fillRect(0, 0, W, H);
  const f = 700, P = (x, y, z) => [cx + x * f / z, cy + y * f / z, f / z];
  c.save(); c.globalCompositeOperation = 'lighter';
  LANES.forEach(([x, y], n) => { const kq = keep(n, x, y) * dim; if (kq <= 0.01) return; const a = P(x, y, 120), b = P(x, y, 9000); c.strokeStyle = `rgba(226,181,74,${0.22 * kq})`; c.lineWidth = 2; c.beginPath(); c.moveTo(a[0], a[1]); c.lineTo(b[0], b[1]); c.stroke();
    const r = R(n + 3); for (let k = 0; k < 4; k++) { const z = 200 + ((r() * 9000 - t * 5200 * speed + k * 2200) % 9000 + 9000) % 9000; const [hx, hy, s] = P(x, y, z), [tx, ty] = P(x, y, z + 900 * speed);
      const gg = c.createLinearGradient(hx, hy, tx, ty); gg.addColorStop(0, `rgba(255,240,200,${0.95 * kq})`); gg.addColorStop(1, 'rgba(245,215,126,0)'); c.strokeStyle = gg; c.lineWidth = Math.max(1.5, 14 * s); c.lineCap = 'round'; c.beginPath(); c.moveTo(hx, hy); c.lineTo(tx, ty); c.stroke(); } });
  c.restore(); };

// ---------- 1. 隧道开场 → 只剩几条路亮着 → 打印机线 vs USB → 路少了凭什么更快？ ----------
SP.MECH.tunnel = (c, t, sh) => {
  const tFew = kw('w02', '只修几条'), t3 = L.w03.t0, tPr = kw('w03', '打印机线'), tUsb = kw('w03', 'USB'), t4 = L.w04.t0;
  const few = ease(t, tFew - 0.3, tFew + 0.6, 'c'), cmp = ease(t, t3 - 0.2, t3 + 0.3) * (1 - ease(t, t4 + 0.6, t4 + 1.2));
  // 只剩地面中间两条通道亮着，而且越跑越快
  const keep = (n, x, y) => { const hot = y > 0 && Math.abs(x) <= 130 && x !== 0; return hot ? 1 + 0.6 * few : 1 - few * 0.92; };
  tunnel(c, t, { speed: 1 + 0.8 * few, keep, dim: 1 - 0.55 * cmp });
  // 打印机线（25 针，脉冲稀）vs USB（4 根线，脉冲密）
  if (cmp > 0) { c.save(); c.globalAlpha = cmp; const yC = 760;
    const dx = 290; c.fillStyle = '#8a877f'; c.beginPath(); c.moveTo(dx - 200, yC - 70); c.lineTo(dx + 200, yC - 70); c.lineTo(dx + 175, yC + 70); c.lineTo(dx - 175, yC + 70); c.closePath(); c.fill();
    c.fillStyle = '#1b1a18'; c.beginPath(); c.moveTo(dx - 175, yC - 50); c.lineTo(dx + 175, yC - 50); c.lineTo(dx + 155, yC + 50); c.lineTo(dx - 155, yC + 50); c.closePath(); c.fill();
    for (let n = 0; n < 13; n++) glowDot(c, dx - 156 + n * 26, yC - 20, 4); for (let n = 0; n < 12; n++) glowDot(c, dx - 143 + n * 26, yC + 20, 4);
    c.fillStyle = '#4a4741'; c.fillRect(dx - 70, yC + 70, 140, 260); txt(c, '25 针', dx, yC - 130, { size: 56, fam: 'PuHui-Heavy', col: COL.cream, align: 'center' });
    for (let n = 0; n < 3; n++) glowDot(c, dx, yC + 90 + ((t * 70 + n * 90) % 240), 9, GOLD, 0.8);
    const ux = 790; c.fillStyle = '#c9c6be'; c.beginPath(); c.roundRect(ux - 70, yC - 50, 140, 110, 6); c.fill(); c.fillStyle = '#1b1a18'; c.fillRect(ux - 56, yC - 36, 112, 40);
    for (let n = 0; n < 4; n++) { c.fillStyle = COL.goldHi; c.fillRect(ux - 46 + n * 26, yC - 30, 16, 26); } c.fillStyle = '#3a3833'; c.fillRect(ux - 22, yC + 60, 44, 270);
    for (let n = 0; n < 14; n++) glowDot(c, ux, yC + 75 + ((t * 520 + n * 18) % 255), 5, GOLD, 0.9);
    txt(c, '4 根线', ux, yC - 130, { size: 56, fam: 'PuHui-Heavy', col: COL.cream, align: 'center' });
    const qa = ease(t, tPr, tPr + 0.6, 'o'), qb = ease(t, tUsb - 0.3, tUsb + 0.8, 'o'), by = 1360;
    c.fillStyle = COL.creamDim; c.fillRect(dx - 70, by - 16 * qa, 140, 16 * qa);
    if (qb > 0) { c.save(); c.globalCompositeOperation = 'lighter'; const g = c.createLinearGradient(0, by - 300 * qb, 0, by); g.addColorStop(0, 'rgba(255,240,190,.95)'); g.addColorStop(1, 'rgba(226,181,74,.5)'); c.fillStyle = g; c.shadowColor = COL.gold; c.shadowBlur = 30; c.fillRect(ux - 70, by - 300 * qb, 140, 300 * qb); c.restore(); }
    txt(c, '老打印机线 · 每秒约 2 兆字节', dx, by + 50, { size: 30, fam: 'PuHui-Heavy', col: COL.creamDim, align: 'center' }); if (qb > 0.2) txt(c, 'USB 2.0 · 每秒几十兆字节', ux, by + 50, { size: 30, fam: 'PuHui-Heavy', col: COL.goldHi, align: 'center' });
    c.restore(); }
  if (t > t4 - 0.15) tape(c, '路少了，凭什么更快？', W / 2, 400, { size: 70, t, at: t4 - 0.15, r: -0.02 });
  const up = ease(t, t3 - 0.3, t3 + 0.2, 'c');
  if (up < 1) { c.save(); c.globalAlpha = 1 - up; hookText(c, t, ['AI 芯片之间，', '最快的路只有几条？'], { y: 300, size: 84, ids: ['w01', 'w02'] }); c.restore(); }
};

// ---------- 2. 赛道：每一批都得一起到 → 一快窗口变窄 → 子弹时间：晚到的那一位 → 整批碎掉 → 路越多越难一样长 ----------
SP.MECH.race = (c, t, sh) => {
  const tMany = kw('w05', '几十条路'), tGate = kw('w05', '一起到'), tJoin = kw('w05', '拼得出'), tSlow = kw('w06', '慢的时候'), tFast = kw('w06', '一快'), tShort = kw('w06', '越来越短'),
    tLong = kw('w07', '长了一点点'), tLate = kw('w07', '晚到一步'), tAllWrong = kw('w07', '整批全错'), tAll = L.w08.t0;
  // 子弹时间：从「晚到一步」开始，画面里的时间放慢到 0.12 倍，持续到「整批全错」之后 0.4 秒
  const bA = tLate - 0.15, bB = tAllWrong + 0.4, SL = 0.12, te = t < bA ? t : t < bB ? bA + (t - bA) * SL : bA + (bB - bA) * SL + (t - bB), bt = t > bA && t < bB ? Math.min(seg(t, bA, bA + 0.3), 1 - seg(t, bB - 0.3, bB)) : 0;
  const V = 1500, N = 12, X = i => (i - (N - 1) / 2) * 110;
  const k = T.cam({ hy: lerp(520, 470, bt), camH: lerp(320, 200, bt), f: lerp(950, 1250, bt), cx: lerp(0, X(7) * 0.6, bt) });
  T.bg(c, k, { scroll: te * V });
  const nOn = Math.round(lerp(2, N, ease(t, tMany - 0.3, tMany + 0.8, 'o'))), on = i => Math.abs(i - (N - 1) / 2) < nOn / 2;
  const bendAmp = ease(t, tLong - 0.5, tLong + 0.3), allBend = ease(t, tAll - 0.2, tAll + 0.8);
  const bendOf = i => z => { const a = i === 7 ? 70 * bendAmp : 0, r = R(i * 13 + 5), b = allBend * (25 + 40 * r()) * (i === 7 ? 0 : 1); const z0 = 1300 + r() * 600;
    return (z > 1300 && z < 2100 ? a * Math.sin(Math.PI * (z - 1300) / 800) : 0) + (z > z0 && z < z0 + 700 ? b * Math.sin(Math.PI * (z - z0) / 700) : 0); };
  const extra = i => (i === 7 ? 0.24 * bendAmp : 0) + (i !== 7 ? allBend * 0.04 * (0.4 + R(i * 13 + 5)()) : 0);
  for (let i = 0; i < N; i++) T.lane(c, k, X(i), 120, 6000, { a: on(i) ? (bt > 0 && i !== 7 ? 0.55 - 0.3 * bt : 0.55) : 0.08, bend: bendOf(i), col: i === 7 && bt > 0 ? 'rgba(239,125,98,' : 'rgba(226,181,74,' });
  const pAt = s => lerp(1.5, 0.42, ease(s, tFast - 0.2, tShort + 0.3, 'c'));
  const heats = []; { let s = tMany - 0.2; while (s < sh.t1 + 3) { heats.push(s); s += pAt(s); } }
  const zGate = 430, Pnow = pAt(te), win = 0.6 * Pnow, gateQ = ease(t, tGate - 0.4, tGate + 0.2);
  if (gateQ > 0) T.gate(c, k, zGate - win * V / 2, nOn * 110 + 40, 160, win * V, { a: gateQ, flash: 0.2 * bt });
  const ARR = 5600 / V; let lastCap = null;
  heats.forEach((s, h) => { const cap = s + ARR, winH = 0.6 * pAt(s);
    for (let i = 0; i < N; i++) { if (!on(i)) continue; const late = extra(i), z = zGate + (cap + late - te) * V; if (z < zGate - (gateQ > 0 ? winH * V / 2 + 40 : 120) || z > 6000) continue;
      const bad = gateQ > 0 && late > winH / 2 && te > cap + winH / 2 - 0.05; T.bit(c, k, X(i) + bendOf(i)(z), 14, z, { len: bad && bt > 0 ? 700 : 240, bad, r: bad && bt > 0 ? 24 : 16 }); }
    if (te >= cap) lastCap = { cap, h, winH }; });
  // 门口拼出来的一批数据；整批全错时碎开飞散
  if (lastCap && gateQ > 0 && t > tGate) { const { cap, h, winH } = lastCap, q = clamp((te - cap) / 0.12), shatter = t > tAllWrong - 0.05 && t < tAll ? seg(t, tAllWrong - 0.05, tAllWrong + 1.2) : 0; let anyBad = false;
    const ids = [...Array(N).keys()].filter(on), w = Math.min(70, 900 / ids.length);
    ids.forEach((i, n) => { const late = extra(i), bad = late > winH / 2, r = R(i * 7 + 3); anyBad = anyBad || bad;
      let x = W / 2 + (n - (ids.length - 1) / 2) * (w + 8), y = 1210, rot = 0;
      if (shatter > 0) { const vx = (r() - 0.5) * 900, vy = -300 - r() * 500, s2 = shatter * 1.2; x += vx * s2; y += vy * s2 + 900 * s2 * s2; rot = (r() - 0.5) * 8 * s2; }
      c.save(); c.globalAlpha = q * (1 - seg(shatter, 0.7, 1)); c.translate(x, y); c.rotate(rot); c.fillStyle = bad || shatter > 0 ? COL.coral : 'rgba(245,215,126,.95)'; c.shadowColor = bad ? COL.coral : COL.gold; c.shadowBlur = 16; c.beginPath(); c.roundRect(-w / 2, -w / 2, w, w, 8); c.fill(); c.shadowBlur = 0;
      txt(c, bad ? '?' : String(R(h * 31 + i)() < 0.5 ? 0 : 1), 0, 2, { size: w * 0.62, fam: 'PuHui-Heavy', col: COL.ink, align: 'center' }); c.restore(); });
    if (shatter <= 0) txt(c, anyBad ? '✗ 拼错了' : '✓ 拼出一批', W / 2, 1300, { size: 44, fam: 'PuHui-Heavy', col: anyBad ? COL.coral : COL.mint, align: 'center', alpha: q }); }
  // 子弹时间的画面处理：四周压暗、红色描边、「慢动作」字样
  if (bt > 0) { c.save(); const vg = c.createRadialGradient(W / 2, 900, 300, W / 2, 900, 1200); vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, `rgba(20,0,0,${0.6 * bt})`); c.fillStyle = vg; c.fillRect(0, 0, W, H);
    c.restore(); txt(c, '慢动作', W - 70, 330, { size: 36, fam: 'PuHui-Heavy', col: COL.coral, align: 'right', alpha: bt }); }
  if (t > tAllWrong - 0.05 && t < tAllWrong + 0.35) { c.save(); c.fillStyle = `rgba(239,125,98,${0.35 * (1 - seg(t, tAllWrong - 0.05, tAllWrong + 0.35))})`; c.fillRect(0, 0, W, H); c.restore(); }
  // 标签
  if (t > tMany - 0.3 && t < tGate - 0.3) MD.label(c, `${nOn} 条路一起送`, W / 2, 330, { size: 56, align: 'center', bg: COL.cream, fg: COL.ink });
  else if (t > tGate - 0.3 && t < tSlow) tape(c, '每一批，都得一起到', W / 2, 330, { size: 58, t, at: tGate - 0.3 });
  else if (t > tSlow && t < tFast) tag(c, '慢：批和批隔得远，窗口很宽', W / 2, 330, { size: 44, t, at: tSlow });
  else if (t > tFast && t < tLong - 0.3) tape(c, '一快，窗口越来越窄', W / 2, 330, { size: 58, t, at: tFast });
  else if (t > tLong - 0.3 && t < tAll - 0.2) tape(c, t > tAllWrong - 0.1 ? '整批全错' : t > tLate - 0.2 ? '晚到一步，混进下一批' : '这条路长了一点点', W / 2, 330, { size: t > tAllWrong - 0.1 ? 80 : 56, t, at: t > tAllWrong - 0.1 ? tAllWrong - 0.1 : t > tLate - 0.2 ? tLate - 0.2 : tLong - 0.3 });
  else if (t > tAll - 0.2) tape(c, '路越多，越难条条一样长', W / 2, 330, { size: 56, t, at: tAll - 0.2 });
  if (t > tLong - 0.3 && bt < 0.5) { const [ex, ey] = T.P(k, X(7) + 40, 0, 1700); c.save(); c.strokeStyle = COL.redHi; c.lineWidth = 5; c.shadowColor = COL.redHi; c.shadowBlur = 16; c.beginPath(); c.ellipse(ex, ey, 70, 34, 0, 0, 7 * ease(t, tLong - 0.3, tLong + 0.3)); c.stroke(); c.restore(); }
};

// ---------- 3. 只修几条路、排成一列，一路提速（结尾冲进光速） ----------
SP.MECH.serial = (c, t, sh) => {
  const tFew = kw('w09', '只修几条路'), tLine = kw('w09', '排成一列'), tUp = kw('w09', '一路提速');
  const merge = ease(t, tFew - 0.3, tFew + 0.9, 'c'), sp = lerp(1500, 5200, ease(t, tUp - 0.6, tUp + 0.8, 'c'));
  const k = T.cam({ hy: 520, camH: lerp(320, 200, merge), f: 950 }); T.bg(c, k, { scroll: t * sp });
  const N = 12, X0 = i => (i - (N - 1) / 2) * 110, X = i => lerp(X0(i), i < N / 2 ? -80 : 80, merge);
  for (let i = 0; i < N; i++) { const keep = i === 0 || i === N - 1; T.lane(c, k, X(i), 120, 6000, { a: keep ? lerp(0.5, 0.95, merge) : 0.5 * (1 - merge), w: keep ? lerp(26, 44, merge) : 26 }); }
  const lq = ease(t, tLine - 0.3, tLine + 0.3);
  if (lq < 1) for (let i = 0; i < N; i++) { const z = 520 + ((t * 1500 + R(i + 3)() * 900) % 5000); T.bit(c, k, X(i), 14, z, { len: 240 }); }
  if (lq > 0) for (const lane of [0, 1]) for (let n = 0; n < 60; n++) { const z = 520 + ((t * sp + n * 120 + lane * 60) % 5500); c.save(); c.globalAlpha = lq; T.bit(c, k, lane ? 80 : -80, 14, z, { len: lerp(240, 900, (sp - 1500) / 3700) }); c.restore(); }
  if (t > tLine - 0.3) tape(c, '排成一列，一个接一个', W / 2, 330, { size: 58, t, at: tLine - 0.3 });
  if (t > tUp - 0.3) { tag(c, '不用等谁，一路提速', W / 2, 1300, { size: 50, bg: COL.goldHi, fg: COL.ink, t, at: tUp - 0.3 });
    const q = ease(t, tUp - 0.3, tUp + 0.6); c.save(); c.globalCompositeOperation = 'lighter'; for (let n = 0; n < 60; n++) { const r = R(n + Math.floor(t * 20) * 7), a = r() * Math.PI * 2, r0 = 300 + r() * 300, r1 = r0 + 300 + r() * 600;
      c.strokeStyle = `rgba(245,215,126,${0.3 * q})`; c.lineWidth = 2 + r() * 2; c.beginPath(); c.moveTo(W / 2 + Math.cos(a) * r0, 520 + Math.sin(a) * r0 * 1.6); c.lineTo(W / 2 + Math.cos(a) * r1, 520 + Math.sin(a) * r1 * 1.6); c.stroke(); } c.restore(); }
};
})();
