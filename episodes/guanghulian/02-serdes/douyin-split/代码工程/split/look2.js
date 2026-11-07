// 第四稿样帧：每条的第一帧 + 高潮瞬间（t = 0..5 对应 6 张）
(() => { const { clamp, lerp } = U; const { W, H, COL, T, txt, tape, tag, hookText } = SP; const R = s => U.rng(s);
const glow = (c, x, y, r, col, a = 1) => { c.save(); c.globalCompositeOperation = 'lighter'; const g = c.createRadialGradient(x, y, 0, x, y, r); g.addColorStop(0, `rgba(255,250,235,${a})`); g.addColorStop(0.25, `rgba(${col},${0.8 * a})`); g.addColorStop(1, `rgba(${col},0)`); c.fillStyle = g; c.beginPath(); c.arc(x, y, r, 0, 7); c.fill(); c.restore(); };
// 光的隧道：四面墙上都是通道，光点从深处冲向镜头（中心消失点）
const tunnel = (c, t, { cx = W / 2, cy = 820, speed = 1, hot = -1, slow = 1 } = {}) => {
  c.fillStyle = '#040506'; c.fillRect(0, 0, W, H);
  const g = c.createRadialGradient(cx, cy, 0, cx, cy, 500); g.addColorStop(0, 'rgba(245,215,126,.35)'); g.addColorStop(1, 'rgba(245,215,126,0)'); c.fillStyle = g; c.fillRect(0, 0, W, H);
  const f = 700, P = (x, y, z) => [cx + x * f / z, cy + y * f / z, f / z];
  const lanes = []; for (let i = -7; i <= 7; i++) { lanes.push([i * 130, 600]); lanes.push([i * 130, -600]); } for (let j = -4; j <= 4; j++) { lanes.push([-950, j * 130]); lanes.push([950, j * 130]); }
  c.save(); c.globalCompositeOperation = 'lighter';
  lanes.forEach(([x, y], n) => { const a = P(x, y, 120), b = P(x, y, 9000); c.strokeStyle = 'rgba(226,181,74,.22)'; c.lineWidth = 2; c.beginPath(); c.moveTo(a[0], a[1]); c.lineTo(b[0], b[1]); c.stroke();
    const r = R(n + 3); for (let k = 0; k < 4; k++) { const z = 200 + ((r() * 9000 - t * 5200 * speed * slow + k * 2200) % 9000 + 9000) % 9000; const [hx, hy, s] = P(x, y, z), [tx, ty] = P(x, y, z + 900 * speed);
      const gg = c.createLinearGradient(hx, hy, tx, ty); gg.addColorStop(0, 'rgba(255,240,200,.95)'); gg.addColorStop(1, 'rgba(245,215,126,0)'); c.strokeStyle = gg; c.lineWidth = Math.max(1.5, 14 * s); c.lineCap = 'round'; c.beginPath(); c.moveTo(hx, hy); c.lineTo(tx, ty); c.stroke(); } });
  c.restore(); };
SCENES.look = { draw(c, lt, t) { const f = Math.floor(t);
  if (f === 0) { // 第 1 条第一帧：在光的隧道里飞
    tunnel(c, 0.37); hookText(c, 0, ['AI 芯片之间，', '最快的路只有几条？'], { y: 300, size: 84 });
  } else if (f === 1) { // 第 1 条高潮：子弹时间——晚到的那一位被冻结、拉出红色光尾，拼好的一排数据碎开
    const k = T.cam({ hy: 520, camH: 240, f: 1100 }); T.bg(c, k, { scroll: 0 }); const N = 12, X = i => (i - 5.5) * 110;
    for (let i = 0; i < N; i++) T.lane(c, k, X(i), 120, 6000, { a: 0.5, bend: i === 7 ? (z => z > 900 && z < 1700 ? 80 * Math.sin(Math.PI * (z - 900) / 800) : 0) : null });
    T.gate(c, k, 360, N * 110 + 40, 170, 120, { a: 1, flash: 0.15 });
    for (let i = 0; i < N; i++) if (i !== 7) T.bit(c, k, X(i), 14, 420, { len: 160 }); T.bit(c, k, X(7) + 30, 14, 760, { len: 520, bad: true, r: 26 });
    const [lx, ly] = T.P(k, X(7) + 30, 14, 760); c.save(); c.strokeStyle = 'rgba(239,125,98,.9)'; c.lineWidth = 4; c.setLineDash([10, 8]); c.beginPath(); c.arc(lx, ly, 90, 0, 7); c.stroke(); c.restore();
    for (let i = 0; i < N; i++) { const r = R(i + 1), bad = i === 7, x = W / 2 + (i - 5.5) * 78 + (r() - .5) * 60, y = 1240 + (r() - .5) * 90, rot = (r() - .5) * 0.9; c.save(); c.translate(x, y); c.rotate(rot); c.fillStyle = bad ? COL.coral : 'rgba(245,215,126,.95)'; c.shadowColor = bad ? COL.coral : COL.gold; c.shadowBlur = 20; c.fillRect(-32, -32, 64, 64); c.restore(); }
    c.save(); c.fillStyle = 'rgba(239,125,98,.12)'; c.fillRect(0, 0, W, H); c.restore(); tape(c, '晚到一步 → 整批全错', W / 2, 330, { size: 64 }); txt(c, '慢动作', 930, 450, { size: 34, fam: 'PuHui-Heavy', col: COL.coral, align: 'right' });
  } else if (f === 2) { // 第 2 条第一帧：一条巨大的发光信号从右边深处斜着冲到左边眼前，中间一段平平的高电平
    const k = T.cam({ hy: 760, camH: 250, f: 900 }); T.bg(c, k, { scroll: 0, grid: 0.7 });
    const B = [0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 1, 0, 1], n = B.length, at = u => [lerp(-560, 900, u), lerp(330, 2600, u)], pts = [];
    B.forEach((b, i) => { for (const u of [i / n, (i + 1) / n]) { const [x, z] = at(u); pts.push(T.P(k, x, b ? 520 : 120, z)); } }); T.glowLine(c, pts, { lw: 11 });
    const [xa, za] = at(3 / n), [xb, zb] = at(8 / n), A = T.P(k, xa, 600, za), Bp = T.P(k, xb, 600, zb);
    c.save(); c.strokeStyle = COL.redHi; c.lineWidth = 6; c.setLineDash([14, 10]); c.beginPath(); c.moveTo(A[0], A[1]); c.lineTo(Bp[0], Bp[1]); c.stroke(); c.restore();
    hookText(c, 0, ['这一段，', '是几个 1？'], { y: 260, size: 96 }); txt(c, '4？', 300, 1330, { size: 130, fam: 'PuHui-Heavy', col: COL.coral, align: 'center' }); txt(c, '5？', 760, 1330, { size: 130, fam: 'PuHui-Heavy', col: COL.mint, align: 'center' });
  } else if (f === 3) { // 第 2 条高潮：几十根乱晃的节拍光柱「咔」一下全部对齐，一圈冲击波
    const k = T.cam({ hy: 1500, camH: 300 }); T.bg(c, k, { grid: 0.4 }); const B = [0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0], bw = 98, pts = []; B.forEach((b, i) => pts.push([2 + i * bw, b ? 640 : 860], [2 + (i + 1) * bw, b ? 640 : 860])); T.glowLine(c, pts, { lw: 8 });
    for (let i = 0; i < 11; i++) { const x = 2 + (i + 0.5) * bw; T.glowLine(c, [[x, 560], [x, 960]], { col: [127, 214, 180], lw: 6 }); }
    c.save(); c.globalCompositeOperation = 'lighter'; for (const [r, a] of [[260, 0.5], [420, 0.3], [600, 0.15]]) { c.strokeStyle = `rgba(155,232,219,${a})`; c.lineWidth = 8; c.beginPath(); c.ellipse(W / 2, 760, r * 1.4, r * 0.7, 0, 0, 7); c.stroke(); } c.restore();
    tape(c, '咔——锁住了', W / 2, 360, { size: 72, bg: COL.mint, fg: COL.ink }); ['1', '2', '3', '4', '5'].forEach((s, i) => txt(c, s, 2 + (i + 3.5) * bw, 560, { size: 70, fam: 'PuHui-Heavy', col: COL.mint, align: 'center' }));
  } else if (f === 4) { // 第 3 条第一帧：一大片芯片上空，立着一个发光的「×2」
    const k = T.cam({ hy: 760, camH: 650, f: 900 }); T.bg(c, k, { grid: 0.8 }); const S = 200;
    for (let j = 26; j >= 0; j--) for (let i = -10; i <= 10; i++) { const x = i * S, z = 600 + j * S; const pp = [[-60, -60], [60, -60], [60, 60], [-60, 60]].map(([dx, dz]) => T.P(k, x + dx, 0, z + dz)), fade = clamp(1 - z / 6000), on = R(i * 31 + j)() < 0.6;
      c.fillStyle = on ? `rgba(245,215,126,${0.5 * fade})` : `rgba(60,58,52,${fade})`; c.beginPath(); pp.forEach((p, n) => n ? c.lineTo(p[0], p[1]) : c.moveTo(p[0], p[1])); c.closePath(); c.fill(); }
    c.save(); c.translate(W / 2, 880); for (let d = 14; d > 0; d--) txt(c, '×2', d * 1.2, d * 1.5, { size: 420, fam: 'PuHui-Heavy', col: `rgba(120,90,30,${0.9})`, align: 'center' }); c.shadowColor = COL.gold; c.shadowBlur = 60; txt(c, '×2', 0, 0, { size: 420, fam: 'PuHui-Heavy', col: '#fff2c4', align: 'center' }); c.restore();
    hookText(c, 0, ['速度翻倍，', '该信几分？'], { y: 270, size: 96 });
  } else { // 第 3 条高潮：PPT 上的「224G」碎掉，旁边真芯片上测出来的信号
    const k = T.cam({ hy: 1500, camH: 300 }); T.bg(c, k, { grid: 0.4 });
    c.save(); c.translate(300, 760); c.rotate(-0.05); c.fillStyle = '#f6f2ea'; c.fillRect(-230, -160, 460, 320); c.fillStyle = COL.red; c.fillRect(-230, -160, 460, 50); txt(c, '新品发布', -200, -134, { size: 30, fam: 'PuHui-Heavy', col: '#fff' }); txt(c, '224G!!', 0, 20, { size: 110, fam: 'PuHui-Heavy', col: COL.ink, align: 'center' });
    c.strokeStyle = '#040506'; c.lineWidth = 5; c.beginPath(); c.moveTo(-230, -40); c.lineTo(-60, 10); c.lineTo(20, -80); c.lineTo(120, 40); c.lineTo(230, 0); c.moveTo(20, -80); c.lineTo(60, 160); c.stroke(); c.restore(); txt(c, 'PPT 上的速度', 300, 1000, { size: 44, fam: 'PuHui-Heavy', col: COL.creamDim, align: 'center' });
    T.chip(c, 790, 740, 330, 330, { label: '真芯片', t: 1, glow: 1 }); for (let n = 0; n < 3; n++) { c.strokeStyle = '#9a978f'; c.lineWidth = 6; c.beginPath(); c.moveTo(710 + n * 80, 470); c.lineTo(720 + n * 80, 580); c.stroke(); }
    const pts = []; const r = R(4); for (let x = 600; x <= 1000; x += 4) { const b = Math.floor((x - 600) / 50) % 3 ? 1 : 0; pts.push([x, 1000 - b * 90 + (r() - .5) * 10]); } T.glowLine(c, pts, { lw: 5 }); txt(c, '真芯片测出来的', 790, 1080, { size: 44, fam: 'PuHui-Heavy', col: COL.goldHi, align: 'center' });
    tape(c, '测出来，才算数', W / 2, 360, { size: 72 });
  } } };
})();
