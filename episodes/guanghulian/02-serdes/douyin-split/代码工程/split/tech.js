// 科技感画面工具：透视地面 + 发光信号光尾 + 金属芯片。坐标：地面 y=0，相机在 (0, camH, 0) 看向 +z；z 越大越远。
(() => {
const { clamp, lerp } = U; const { W, H, COL } = SP;
const T = {};
// 相机：f 焦距，hy 地平线高度，camH 相机高度，cx 横向偏移
T.cam = (o = {}) => ({ f: 900, hy: 620, camH: 260, cx: 0, ...o });
T.P = (k, x, y, z) => { const zz = Math.max(1, z); return [W / 2 + (x - k.cx) * k.f / zz, k.hy + (k.camH - y) * k.f / zz, k.f / zz]; };
// 深色背景 + 透视网格地面（青色细线，往远处变暗），网格以 scroll 速度往镜头流
T.bg = (c, k, { scroll = 0, grid = 1, tint = 'rgba(63,181,165,' } = {}) => {
  const g = c.createLinearGradient(0, 0, 0, H); g.addColorStop(0, '#07090b'); g.addColorStop(k.hy / H, '#0d1416'); g.addColorStop(1, '#050606'); c.fillStyle = g; c.fillRect(0, 0, W, H);
  // 地平线上的一抹光
  const hz = c.createRadialGradient(W / 2, k.hy, 10, W / 2, k.hy, 700); hz.addColorStop(0, 'rgba(226,181,74,.18)'); hz.addColorStop(1, 'rgba(226,181,74,0)'); c.fillStyle = hz; c.fillRect(0, 0, W, H);
  if (grid <= 0) return; c.save(); c.lineWidth = 1.5;
  for (let i = -14; i <= 14; i++) { const x = i * 120, a = T.P(k, x, 0, 60), b = T.P(k, x, 0, 6000); c.strokeStyle = tint + (0.16 * grid) + ')'; c.beginPath(); c.moveTo(a[0], a[1]); c.lineTo(b[0], b[1]); c.stroke(); }
  const step = 160, off = ((scroll % step) + step) % step;
  for (let n = 0; n < 40; n++) { const z = 80 + n * step - off; if (z < 60) continue; const a = T.P(k, -1700, 0, z), b = T.P(k, 1700, 0, z), al = 0.18 * grid * clamp(1 - z / 5000); c.strokeStyle = tint + al + ')'; c.beginPath(); c.moveTo(a[0], a[1]); c.lineTo(b[0], b[1]); c.stroke(); }
  c.restore();
  const vg = c.createRadialGradient(W / 2, H * 0.48, 380, W / 2, H / 2, 1250); vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,.55)'); c.fillStyle = vg; c.fillRect(0, 0, W, H); };
// 一条地面上的发光通道（从 z0 到 z1，x 处，宽 w）
T.lane = (c, k, x, z0, z1, { w = 26, col = 'rgba(226,181,74,', a = 0.5, bend = null } = {}) => { const N = 40; c.save(); c.globalCompositeOperation = 'lighter';
  for (const [lw, al] of [[3.2, 0.12], [1, a]]) { c.beginPath(); for (let i = 0; i <= N; i++) { const z = lerp(z0, z1, i / N), xx = x + (bend ? bend(z) : 0), [sx, sy, s] = T.P(k, xx, 0, z); i ? c.lineTo(sx, sy) : c.moveTo(sx, sy); }
    c.strokeStyle = col + al + ')'; c.lineWidth = Math.max(1.5, w * lw * k.f / ((z0 + z1) / 2) * 0.5); c.stroke(); } c.restore(); };
// 发光的比特：一颗亮核 + 往后拖的光尾（len 为 z 方向长度）
T.bit = (c, k, x, y, z, { len = 220, col = [245, 215, 126], r = 16, bad = false } = {}) => { const C = bad ? [239, 125, 98] : col; const [hx, hy, s] = T.P(k, x, y, z), [tx, ty] = T.P(k, x, y, z + len);
  c.save(); c.globalCompositeOperation = 'lighter'; const g = c.createLinearGradient(hx, hy, tx, ty); g.addColorStop(0, `rgba(${C},.85)`); g.addColorStop(1, `rgba(${C},0)`);
  c.strokeStyle = g; c.lineCap = 'round'; c.lineWidth = Math.max(2, r * s * 1.3); c.beginPath(); c.moveTo(hx, hy); c.lineTo(tx, ty); c.stroke();
  const rr = Math.max(2, r * s); const hg = c.createRadialGradient(hx, hy, 0, hx, hy, rr * 3); hg.addColorStop(0, 'rgba(255,250,235,1)'); hg.addColorStop(0.25, `rgba(${C},.9)`); hg.addColorStop(1, `rgba(${C},0)`);
  c.fillStyle = hg; c.beginPath(); c.arc(hx, hy, rr * 3, 0, 7); c.fill(); c.restore(); return [hx, hy, s]; };
// 立起来的发光门（时间窗口）：在 z 处、宽 wd、高 ht、厚 dz
T.gate = (c, k, z, wd, ht, dz, { col = [127, 214, 180], a = 1, flash = 0 } = {}) => { const q = (x, y, zz) => T.P(k, x, y, zz);
  c.save(); c.globalCompositeOperation = 'lighter'; const p = [q(-wd / 2, 0, z), q(wd / 2, 0, z), q(wd / 2, 0, z + dz), q(-wd / 2, 0, z + dz)];
  c.fillStyle = `rgba(${col},${0.16 * a + 0.3 * flash})`; c.beginPath(); p.forEach((v, i) => i ? c.lineTo(v[0], v[1]) : c.moveTo(v[0], v[1])); c.closePath(); c.fill();
  for (const zz of [z, z + dz]) { const a0 = q(-wd / 2, 0, zz), a1 = q(-wd / 2, ht, zz), b1 = q(wd / 2, ht, zz), b0 = q(wd / 2, 0, zz); c.strokeStyle = `rgba(${col},${0.7 * a})`; c.lineWidth = 3; c.shadowColor = `rgb(${col})`; c.shadowBlur = 18;
    c.beginPath(); c.moveTo(a0[0], a0[1]); c.lineTo(a1[0], a1[1]); c.lineTo(b1[0], b1[1]); c.lineTo(b0[0], b0[1]); c.stroke(); }
  c.restore(); };
// 金属芯片（正面看）：基板 + 金属顶盖 + 扫过的高光 + 刻字
T.chip = (c, x, y, w, h, { label = '', t = 0, glow = 0, sub = '' } = {}) => { c.save(); c.shadowColor = glow ? 'rgba(245,215,126,.6)' : 'rgba(0,0,0,.7)'; c.shadowBlur = glow ? 40 * glow : 40; c.shadowOffsetY = glow ? 0 : 14;
  c.fillStyle = '#1f2a1d'; c.beginPath(); c.roundRect(x - w / 2, y - h / 2, w, h, 14); c.fill(); c.shadowColor = 'transparent';
  for (let i = 0; i < 18; i++) { c.fillStyle = 'rgba(226,181,74,.55)'; c.fillRect(x - w / 2 + 14 + i * (w - 28) / 18, y + h / 2 - 10, (w - 28) / 18 - 6, 6); }
  const m = Math.min(w, h) * 0.14, lx = x - w / 2 + m, ly = y - h / 2 + m, lw = w - 2 * m, lh = h - 2 * m;
  const g = c.createLinearGradient(lx, ly, lx + lw, ly + lh); g.addColorStop(0, '#d6d3cb'); g.addColorStop(0.45, '#8f8c85'); g.addColorStop(0.55, '#a7a49c'); g.addColorStop(1, '#6f6d68'); c.fillStyle = g; c.beginPath(); c.roundRect(lx, ly, lw, lh, 10); c.fill();
  c.save(); c.beginPath(); c.roundRect(lx, ly, lw, lh, 10); c.clip(); const sx = lx - lw + ((t * 0.35) % 1.6) * lw * 1.6; const hg = c.createLinearGradient(sx, ly, sx + lw * 0.5, ly + lh); hg.addColorStop(0, 'rgba(255,255,255,0)'); hg.addColorStop(0.5, 'rgba(255,255,255,.35)'); hg.addColorStop(1, 'rgba(255,255,255,0)'); c.fillStyle = hg; c.fillRect(lx, ly, lw, lh); c.restore();
  if (label) { c.font = `${Math.round(lh * 0.26)}px "PuHui-Heavy"`; c.fillStyle = 'rgba(30,29,27,.78)'; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText(label, x, y - (sub ? lh * 0.06 : 0)); }
  if (sub) { c.font = `${Math.round(lh * 0.1)}px "PuHui-Heavy"`; c.fillStyle = 'rgba(30,29,27,.65)'; c.textAlign = 'center'; c.fillText(sub, x, y + lh * 0.24); }
  c.restore(); };
// 屏幕空间的发光线（波形、走线）：pts 数组
T.glowLine = (c, pts, { col = [245, 215, 126], lw = 6, a = 1 } = {}) => { c.save(); c.globalCompositeOperation = 'lighter'; c.lineJoin = 'round'; c.lineCap = 'round';
  for (const [w, al] of [[lw * 5, 0.08], [lw * 2.2, 0.22], [lw, 0.95]]) { c.strokeStyle = `rgba(${col},${al * a})`; c.lineWidth = w; c.beginPath(); pts.forEach((p, i) => i ? c.lineTo(p[0], p[1]) : c.moveTo(p[0], p[1])); c.stroke(); }
  c.restore(); };
// 背景里缓缓流动的数据流（竖向的一串串小光点），只在画面比较静的段落加一点，不做粒子爆炸
T.streams = (c, t, { a = 0.22, n = 22, col = [245, 215, 126], seed = 3 } = {}) => { const r = U.rng(seed); c.save(); c.globalCompositeOperation = 'lighter';
  for (let i = 0; i < n; i++) { const x = (i + 0.3 + r() * 0.4) * W / n, sp = 120 + r() * 260, len = 4 + Math.floor(r() * 6), ph = r() * H, al = a * (0.4 + r() * 0.6);
    for (let k = 0; k < len; k++) { const y = ((t * sp + ph + k * 34) % (H + 300)) - 150; c.fillStyle = `rgba(${col},${al * (1 - k / len)})`; c.fillRect(x - 2, y, 4, 18); } }
  c.restore(); };
SP.T = T;
})();
