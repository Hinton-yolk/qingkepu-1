// 第 1 条（第五稿 · 翻译）：照片切成几十条一起送 → 一快，一条晚到半步、拼进下一张 → 照片错位 → 排成一队就不会乱。
// 字只做标注，贴在画面正在演示的东西旁边；画面动作卡在口播的字上。
(() => {
const { clamp, lerp } = U; const { W, H, COL, T, kw, txt, tag, pop, ease, seg, hookText, L } = SP;
SP.END = 'p12';
const R = (s) => U.rng(s);
const GOLD = [245, 215, 126], CORAL = [239, 125, 98];
const glowDot = (c, x, y, r, col = GOLD, a = 1) => { c.save(); c.globalCompositeOperation = 'lighter'; const g = c.createRadialGradient(x, y, 0, x, y, r * 3); g.addColorStop(0, `rgba(255,250,235,${a})`); g.addColorStop(0.3, `rgba(${col},${0.85 * a})`); g.addColorStop(1, `rgba(${col},0)`); c.fillStyle = g; c.beginPath(); c.arc(x, y, r * 3, 0, 7); c.fill(); c.restore(); };
// 两张「照片」：v=0 夕阳，v=1 蓝天草地。一条一条拼起来时，混进另一张的那一条一眼就看得出
const photo = (g, x, y, w, h, v = 0) => { const sky = g.createLinearGradient(0, y, 0, y + h);
  if (v) { sky.addColorStop(0, '#7fc8f0'); sky.addColorStop(1, '#2f6f9a'); } else { sky.addColorStop(0, '#f2c27a'); sky.addColorStop(0.55, '#e98a5c'); sky.addColorStop(1, '#5c3a52'); }
  g.fillStyle = sky; g.fillRect(x, y, w, h); g.fillStyle = v ? '#ffffff' : '#fff2c9'; g.beginPath(); g.arc(x + w * 0.62, y + h * 0.36, w * 0.11, 0, 7); g.fill();
  g.fillStyle = v ? '#2e5b3a' : '#3b2a3c'; g.beginPath(); g.moveTo(x, y + h * 0.66); for (let n = 0; n <= 12; n++) g.lineTo(x + w * n / 12, y + h * (0.58 + 0.08 * Math.sin(n * 1.7 + 1))); g.lineTo(x + w, y + h); g.lineTo(x, y + h); g.fill();
  g.fillStyle = v ? '#1f4029' : '#241a27'; g.fillRect(x, y + h * 0.82, w, h * 0.18); };
const NS = 12;                                                          // 照片切成 12 条
const stripCol = (i, v) => v ? ['#7fc8f0', '#76bfe7', '#6db5dd', '#64abd3', '#5ba1c9', '#5297bf', '#4a8db5', '#3f7e9f', '#2e5b3a', '#2a5536', '#1f4029', '#1f4029'][i] : ['#f2c27a', '#f0b672', '#eea96a', '#ec9c62', '#ea905b', '#e2865b', '#c06f58', '#9c5a56', '#3b2a3c', '#352638', '#241a27', '#241a27'][i];
// 一张拼起来的照片：rows[i] = 第 i 条用哪一张（0/1），null = 还没到
const assembled = (c, x, y, w, h, rows, { bad = -1, frame = true } = {}) => { if (frame) { c.save(); c.shadowColor = 'rgba(0,0,0,.6)'; c.shadowBlur = 30; c.fillStyle = '#f6f2ea'; c.fillRect(x - 14, y - 14, w + 28, h + 28); c.restore(); }
  c.fillStyle = '#1b1a18'; c.fillRect(x, y, w, h);
  rows.forEach((v, i) => { if (v == null) return; const sy = y + h * i / NS, sh = h / NS + 0.5; c.save(); c.beginPath(); c.rect(x, sy, w, sh); c.clip(); photo(c, x + (i === bad ? 34 : 0), y, w, h, v); c.restore(); }); };
const chatBg = (g, x, y, w, h) => { g.fillStyle = '#ededed'; g.fillRect(x, y, w, h); g.fillStyle = '#f7f7f7'; g.fillRect(x, y, w, 110); txt(g, '小林', x + w / 2, y + 70, { size: 34, fam: 'PuHui-Heavy', col: '#222', align: 'center' }); };

// ---------- 1. 第一帧：手机里刚发出去的照片，中间一条错了位 → 照片飞进芯片 ----------
SP.MECH.photo = (c, t, sh) => {
  const k = T.cam({ hy: 1500, camH: 300 }); T.bg(c, k, { grid: 0.5, scroll: t * 200 }); T.streams(c, t, { a: 0.14 });
  const tGo = kw('p02', '芯片'), go = ease(t, tGo - 0.5, tGo + 0.7, 'c');
  const rows = Array(NS).fill(0); rows[6] = 1;
  // 手机：从正中往左上缩小；照片从手机里飞出，落进右下的芯片
  c.save(); c.globalAlpha = 1 - go * 0.6; const s = lerp(1, 0.55, go); c.translate(lerp(W / 2, 300, go), lerp(860, 560, go) + 10 * Math.sin(t * 2)); c.scale(s, s); c.rotate(0.012 * Math.sin(t * 1.3));
  SP.phone(c, 0, 0, 620, 1080, (g, x, y, w, h) => { chatBg(g, x, y, w, h); if (go < 0.3) assembled(g, x + w - 450, y + 180, 400, 520, rows, { bad: 6, frame: false });
    g.fillStyle = '#95ec69'; g.beginPath(); g.roundRect(x + w - 240, y + 740, 190, 66, 16); g.fill(); txt(g, '已发送', x + w - 145, y + 774, { size: 30, fam: 'PuHui-Heavy', col: '#1b1b1a', align: 'center' }); });
  c.restore();
  if (go < 0.15) { const lx = W / 2 + 70, ly = 860 - 540 + 180 + 520 * 6.5 / NS; c.save(); c.strokeStyle = COL.redHi; c.lineWidth = 5; c.beginPath(); c.moveTo(170, ly + 150); c.lineTo(lx - 150, ly); c.stroke(); c.restore();
    tag(c, '晚到半步的一条', 300, ly + 180, { size: 48, bg: COL.coral, fg: COL.ink, r: -0.03 }); }
  if (go > 0) { const p = clamp((t - tGo + 0.3) / 1.0), px = lerp(300, 760, MO.cubicInOut(p)), py = lerp(560, 1050, MO.cubicInOut(p)) - 200 * Math.sin(Math.PI * p), sc = lerp(0.5, 0.25, p);
    T.chip(c, 760, 1100, 360, 360, { label: '芯片', t: t * 1.5, glow: seg(t, tGo + 0.3, tGo + 0.7) });
    if (p < 1) { c.save(); c.translate(px, py); c.rotate(0.3 * p); c.scale(sc, sc); assembled(c, -200, -260, 400, 520, Array(NS).fill(0)); c.restore(); } }
  if (!SP.D.novoice) hookText(c, t, ['你发出去的每张照片，', '在芯片之间都要跑一趟。'], { y: 1420, size: 52, ids: ['p01', 'p02'], bg: '#0f0f0e' });
};

// ---------- 2. 照片切成 12 条、各走一条路 → 慢：拼得严丝合缝 → 一快：一张紧跟一张、一条晚到半步拼进下一张 → 照片错位 → 转账错一位 → 路越多越难一样长 ----------
SP.MECH.strips = (c, t, sh) => {
  const tCut = kw('p03', '切成'), tSend = kw('p03', '一起送'), tSlow = L.p04.t0, tOk = kw('p04', '严丝合缝'), tFast = kw('p05', '一快'), tTight = kw('p05', '紧跟着'), tLong = kw('p05', '长了一点点'), tLate = kw('p05', '晚到半步'), tInto = kw('p05', '拼进'),
    tLook = L.p06.t0, tMoney = L.p07.t0, tFlip = kw('p07', '错一位'), tAll = L.p08.t0;
  // 子弹时间：「晚到半步」→「拼进了下一张」之后 0.5 秒，画面里的时间放慢到 0.15 倍
  const bA = tLate - 0.1, bB = tInto + 0.6, SL = 0.15, te = t < bA ? t : t < bB ? bA + (t - bA) * SL : bA + (bB - bA) * SL + (t - bB), bt = t > bA && t < bB ? Math.min(seg(t, bA, bA + 0.3), 1 - seg(t, bB - 0.3, bB)) : 0;
  const V = 1500, X = i => (i - (NS - 1) / 2) * 100, ZG = 430;
  const k = T.cam({ hy: lerp(470, 430, bt), camH: lerp(300, 200, bt), f: lerp(900, 1150, bt), cx: lerp(0, X(7) * 0.5, bt) });
  T.bg(c, k, { scroll: te * V });
  const bendAmp = ease(t, tLong - 0.4, tLong + 0.3), allBend = ease(t, tAll - 0.2, tAll + 0.8);
  const bendOf = i => z => { const r = R(i * 13 + 5), z0 = 1300 + r() * 600, a = i === 7 ? 80 * bendAmp : allBend * (25 + 40 * r());
    return i === 7 ? (z > 1300 && z < 2100 ? a * Math.sin(Math.PI * (z - 1300) / 800) : 0) : (z > z0 && z < z0 + 700 ? a * Math.sin(Math.PI * (z - z0) / 700) : 0); };
  const late = i => (i === 7 ? 0.62 * bendAmp : 0) + (i !== 7 ? allBend * 0.55 * (R(i * 13 + 5)() > 0.55 ? 1 : 0) : 0);   // 晚到的秒数
  const laneOn = ease(t, tSend - 0.6, tSend + 0.2);
  for (let i = 0; i < NS; i++) T.lane(c, k, X(i), 120, 6000, { a: 0.5 * laneOn, bend: bendOf(i), col: i === 7 && bt > 0 ? 'rgba(239,125,98,' : 'rgba(226,181,74,' });
  // 一张一张照片：慢的时候间隔 2.0 s，说到「一快」那一刻立刻变成 0.55 s
  const pAt = s => s < tFast ? 2.0 : 0.55;
  // 按「到达时刻」排：说到「一快」的那一刻起，到达就一张紧跟一张（画面立刻变密，不用等路上的照片跑完）
  const ARR = 0; const heats = []; { let s = tSend + 0.9; while (s < sh.t1 + 4) { heats.push(s); s += pAt(s); } }
  // 远处：说到「切成」时，一张照片在路的尽头切成 12 条
  const cutQ = ease(t, tCut - 0.3, tCut + 0.4) * (1 - ease(t, tSend, tSend + 0.6));
  if (cutQ > 0) { const [ox, oy] = T.P(k, 0, 300, 3800); c.save(); c.globalAlpha = cutQ; for (let i = 0; i < NS; i++) { const gap = 10 * cutQ; c.save(); c.beginPath(); c.rect(ox - 200, oy - 260 + i * (520 / NS) + i * gap - 60, 400, 520 / NS); c.clip(); photo(c, ox - 200, oy - 260 + i * gap - 60, 400, 520, 0); c.restore(); } c.restore();
    tag(c, '切成 12 条', ox + 230, oy - 120, { size: 40, t, at: tCut - 0.3 }); }
  // 每一张照片的 12 条：各自沿着自己的路飞过来（颜色就是那一条的颜色）
  heats.forEach((s0, h) => { const cap = s0 + ARR, v = h % 2;
    for (let i = 0; i < NS; i++) { const z = ZG + (cap + late(i) - te) * V; if (z < ZG - 60 || z > 6000) continue; const [hx, hy, sc] = T.P(k, X(i) + bendOf(i)(z), 20, z);
      const ww = 90 * sc, hh = 34 * sc, badNow = late(i) > 0.27 && bt > 0;
      c.save(); c.globalCompositeOperation = 'source-over'; c.fillStyle = stripCol(i, v); c.shadowColor = badNow ? COL.coral : 'rgba(245,215,126,.8)'; c.shadowBlur = 18 * sc + (badNow ? 30 : 0); c.fillRect(hx - ww / 2, hy - hh / 2, ww, hh); c.restore();
      if (badNow) { c.save(); c.strokeStyle = COL.coral; c.lineWidth = 4; c.strokeRect(hx - ww / 2 - 6, hy - hh / 2 - 6, ww + 12, hh + 12); c.restore(); } } });
  // 对面拼出来的照片：第 i 条如果晚到超过半张的间隔，用的就是上一张的那一条（拼进了下一张）
  let cur = -1; heats.forEach((s0, h) => { if (te >= s0 + ARR) cur = h; });
  const showA = cur >= 0 && t > tSend + 1, look = ease(t, tLook - 0.3, tLook + 0.4, 'c') * (1 - ease(t, tMoney - 0.3, tMoney + 0.1));
  if (showA) { const P = pAt(heats[cur]), rows = []; let bad = -1;
    for (let i = 0; i < NS; i++) { const lt = late(i); if (lt > P / 2) { const hp = cur - 1; rows.push(hp >= 0 ? hp % 2 : null); if (hp >= 0 && hp % 2 !== cur % 2) bad = i; } else rows.push(te >= heats[cur] + ARR + lt ? cur % 2 : (cur > 0 ? (cur - 1) % 2 : null)); }
    const bx = lerp(340, 140, look), by = lerp(1040, 560, look), bw = lerp(400, 800, look), bh = lerp(300, 600, look);
    assembled(c, bx, by, bw, bh, rows);
    const okNow = bad < 0 && rows.every(r => r != null);
    if (look < 0.5) { if (okNow && t > tOk - 0.6 && t < tFast) tag(c, '✓ 拼得严丝合缝', W / 2, by + bh + 70, { size: 42, bg: COL.mint, fg: COL.ink }); if (bad >= 0 && t > tInto - 0.2) tag(c, '上一张的一条，拼进来了', W / 2, by + bh + 70, { size: 42, bg: COL.coral, fg: COL.ink }); }
    if (look > 0.5 && bad >= 0) { c.save(); c.strokeStyle = COL.redHi; c.lineWidth = 6; c.strokeRect(bx - 20, by + bh * bad / NS - 8, bw + 60, bh / NS + 16); c.restore(); tag(c, '错位的一条', bx + bw / 2, by + bh + 80, { size: 50, bg: COL.coral, fg: COL.ink, r: -0.02 }); } }
  // 标注：贴在发生事情的地方
  if (t > tFast - 0.1 && t < tLong - 0.2) { const [tx, ty] = T.P(k, 0, 300, 2400); tag(c, '一快：一张紧跟一张', tx, ty, { size: 44, bg: COL.goldHi, fg: COL.ink, t, at: tFast - 0.1 }); }
  if (t > tLong - 0.3 && t < tLook - 0.3) { const [ex, ey] = T.P(k, X(7) + 40, 0, 1700); c.save(); c.strokeStyle = COL.redHi; c.lineWidth = 5; c.shadowColor = COL.redHi; c.shadowBlur = 16; c.beginPath(); c.ellipse(ex, ey, 80, 38, 0, 0, 7 * ease(t, tLong - 0.3, tLong + 0.3)); c.stroke(); c.restore();
    tag(c, t > tLate - 0.1 ? '晚到半步' : '这条长了一点点', ex + 40, ey - 90, { size: 44, bg: COL.coral, fg: COL.ink, t, at: t > tLate - 0.1 ? tLate - 0.1 : tLong - 0.3 }); }
  if (bt > 0) { c.save(); const vg = c.createRadialGradient(W / 2, 900, 300, W / 2, 900, 1200); vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, `rgba(20,0,0,${0.55 * bt})`); c.fillStyle = vg; c.fillRect(0, 0, W, H); c.restore(); }
  // 转账：一位变了，金额就变了（示意）
  const mq = ease(t, tMoney - 0.3, tMoney + 0.2) * (1 - ease(t, tAll - 0.3, tAll));
  if (mq > 0) { c.save(); c.fillStyle = `rgba(4,5,6,${0.75 * mq})`; c.fillRect(0, 0, W, H); c.globalAlpha = mq; c.translate(W / 2, 880);
    SP.phone(c, 0, 0, 560, 900, (g, x, y, w, h) => { chatBg(g, x, y, w, h); const flip = t > tFlip;
      const card = (yy, amt, col, lab) => { g.fillStyle = col; g.beginPath(); g.roundRect(x + 40, yy, w - 80, 200, 18); g.fill(); txt(g, lab, x + 70, yy + 50, { size: 30, fam: 'PuHui-Heavy', col: '#fff' }); txt(g, amt, x + 70, yy + 130, { size: 76, fam: 'PuHui-Heavy', col: '#fff' }); };
      card(y + 180, '¥ 520.00', '#f0a043', '发出：转账'); card(y + 440, flip ? '¥ 528.00' : '¥ 520.00', flip ? '#c8503f' : '#f0a043', '收到：转账'); }); c.restore();
    if (t > tFlip) tag(c, '错一位（示意）', W / 2 + 60, 1330, { size: 44, bg: COL.coral, fg: COL.ink, t, at: tFlip }); }
  if (t > tAll - 0.2) { const [tx, ty] = T.P(k, 0, 300, 2600); tag(c, '路越多，越难条条一样长', tx, ty, { size: 44, bg: COL.coral, fg: COL.ink, t, at: tAll - 0.2 }); }
};

// ---------- 3. 只修几条路，照片化成一串像素排成一队，越跑越快；到了对面一个一个拼回去，完整无缺 ----------
SP.MECH.serial = (c, t, sh) => {
  const tFew = kw('p09', '只修几条路'), tLine = kw('p09', '排成一队'), tUp = kw('p09', '越跑越快');
  const merge = ease(t, tFew - 0.3, tFew + 0.8, 'c'), sp = lerp(1500, 5200, ease(t, tUp - 0.5, tUp + 0.6, 'c'));
  const k = T.cam({ hy: 470, camH: lerp(300, 200, merge), f: 950 }); T.bg(c, k, { scroll: t * sp });
  const X0 = i => (i - (NS - 1) / 2) * 100, X = i => lerp(X0(i), i < NS / 2 ? -70 : 70, merge);
  for (let i = 0; i < NS; i++) { const keep = i === 0 || i === NS - 1; T.lane(c, k, X(i), 120, 6000, { a: keep ? lerp(0.5, 0.95, merge) : 0.5 * (1 - merge), w: keep ? lerp(26, 44, merge) : 26 }); }
  const lq = ease(t, tLine - 0.3, tLine + 0.3);
  // 一串像素：颜色按照片从上到下排，排成一队往前冲
  if (lq > 0) for (const lane of [0, 1]) for (let n = 0; n < 70; n++) { const z = 520 + ((t * sp + n * 100 + lane * 50) % 5500), row = Math.floor(((n + lane * 35) % 70) / 70 * NS), [hx, hy, s] = T.P(k, lane ? 70 : -70, 18, z);
    c.save(); c.globalAlpha = lq; c.fillStyle = stripCol(row, 0); c.shadowColor = 'rgba(245,215,126,.8)'; c.shadowBlur = 14 * s; c.fillRect(hx - 14 * s, hy - 14 * s - 30 * s * (sp / 5200), 28 * s, 28 * s + 60 * s * (sp / 5200)); c.restore(); }
  // 对面：像素一个个落位，照片从上到下拼出来，完整无缺
  const fill = ease(t, tLine + 0.2, sh.t1 - 0.3), rows = Array(NS).fill(null).map((_, i) => (i / NS < fill ? 0 : null));
  assembled(c, 340, 1000, 400, 300, rows);
  if (fill > 0.98) tag(c, '✓ 一个不乱', W / 2, 1380, { size: 46, bg: COL.mint, fg: COL.ink, t, at: tLine + 0.2 + (sh.t1 - 0.3 - tLine - 0.2) * 0.98 });
  if (t > tLine - 0.3) { const [tx, ty] = T.P(k, 0, 300, 2400); tag(c, '排成一队', tx, ty, { size: 48, bg: COL.goldHi, fg: COL.ink, t, at: tLine - 0.3 }); }
  if (t > tUp - 0.3) { const q = ease(t, tUp - 0.3, tUp + 0.6); c.save(); c.globalCompositeOperation = 'lighter'; for (let n = 0; n < 60; n++) { const r = R(n + Math.floor(t * 20) * 7), a = r() * Math.PI * 2, r0 = 300 + r() * 300, r1 = r0 + 300 + r() * 600;
      c.strokeStyle = `rgba(245,215,126,${0.3 * q})`; c.lineWidth = 2 + r() * 2; c.beginPath(); c.moveTo(W / 2 + Math.cos(a) * r0, 470 + Math.sin(a) * r0 * 1.6); c.lineTo(W / 2 + Math.cos(a) * r1, 470 + Math.sin(a) * r1 * 1.6); c.stroke(); } c.restore(); }
};
})();
