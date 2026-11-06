// Style 4 · 黑白漫画 + 一个亮色 — ink lines, screentone, focus lines and speed lines on paper.
// Everything is black and white except your watch time: one vermilion (the progress bar, the picked cards, the odds).
'use strict';
const MG = { paper: '#F2EEE5', ink: '#141414', red: '#FF3B1F', grey: '#BDB8AE' };
const MSANS = '"Noto Sans CJK SC"';
function mpoly(pts) { ctx.beginPath(); pts.forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)); ctx.closePath(); }
// screentone: a 45° dot grid, cached per density, fixed to the page like print
const TONES = {};
function tone(d, sp = 9) {
  const key = d + '_' + sp; if (TONES[key]) return TONES[key];
  const c = document.createElement('canvas'); c.width = c.height = sp * 2; const g = c.getContext('2d'), r = sp * .62 * Math.sqrt(d);
  g.fillStyle = MG.ink; for (const [x, y] of [[0, 0], [sp * 2, 0], [0, sp * 2], [sp * 2, sp * 2], [sp, sp]]) { g.beginPath(); g.arc(x, y, r, 0, TAU); g.fill(); }
  return (TONES[key] = ctx.createPattern(c, 'repeat'));
}
// a gradient tone drawn dot by dot (night sky)
function toneGrad(y0, y1, f, sp = 14) {
  ctx.fillStyle = MG.ink; ctx.beginPath();
  for (let j = 0, y = y0; y < y1; j++, y += sp / 2) for (let x = (j % 2) * sp / 2; x < W + sp; x += sp) { const d = f(y); if (d < .03) continue; const r = sp * .62 * Math.sqrt(Math.min(1, d)); ctx.moveTo(x + r, y); ctx.arc(x, y, r, 0, TAU); }
  ctx.fill();
}
// focus lines (集中線) toward a point; they re-draw every 2 frames like a motion comic
function focus(cx, cy, r0, n, seed, col = MG.ink, t = 0) {
  const r = mulberry32(seed + Math.floor(t * 15)); ctx.fillStyle = col; ctx.beginPath();
  for (let i = 0; i < n; i++) { const a = r() * TAU, w = .003 + r() * .011, R0 = r0 * (.82 + r() * .5), R1 = 2600; ctx.moveTo(cx + Math.cos(a) * R0, cy + Math.sin(a) * R0); ctx.lineTo(cx + Math.cos(a - w) * R1, cy + Math.sin(a - w) * R1); ctx.lineTo(cx + Math.cos(a + w) * R1, cy + Math.sin(a + w) * R1); ctx.closePath(); }
  ctx.fill();
}
// a tapered brush stroke along a polyline
function brush(pts, w0, w1, col = MG.ink) {
  const L = [], n = pts.length; ctx.fillStyle = col; ctx.beginPath();
  for (let i = 0; i < n; i++) { const a = pts[Math.max(0, i - 1)], b = pts[Math.min(n - 1, i + 1)], dx = b[0] - a[0], dy = b[1] - a[1], l = Math.hypot(dx, dy) || 1, w = lerp(w0, w1, i / (n - 1)) * Math.sin(Math.PI * Math.min(.5, .15 + i / (n - 1) * .85)) * 1.2; L.push([pts[i][0] - dy / l * w, pts[i][1] + dx / l * w, pts[i][0] + dy / l * w, pts[i][1] - dx / l * w]); }
  L.forEach((v, i) => i ? ctx.lineTo(v[0], v[1]) : ctx.moveTo(v[0], v[1])); for (let i = n - 1; i >= 0; i--) ctx.lineTo(L[i][2], L[i][3]); ctx.closePath(); ctx.fill();
}

// ---------- S0 · a manga panel: night tone at the top, focus lines on the phone, a blanket in ink
function bedroom(t) {
  ctx.fillStyle = MG.paper; ctx.fillRect(0, 0, W, H);
  const pc = P(0, 0, 0); const cx = pc ? pc[0] : W / 2, cy = pc ? pc[1] : H / 2;
  focus(cx, cy, 400, 170, 7, MG.ink, t);
  // night: solid ink at the top, dissolving into dots
  ctx.fillStyle = MG.ink; ctx.fillRect(0, 0, W, 330);
  toneGrad(330, 900, y => 1 - (y - 330) / 570);
  ctx.fillStyle = MG.paper; const r = mulberry32(4); for (let i = 0; i < 26; i++) { const x = r() * W, y = r() * 300, s = 2 + r() * 4; ctx.fillRect(x, y, s, s); }      // stars as white specks
  // the blanket: white sheet, heavy contour, folds, tone in the valleys
  const oy = CY * 26, ox = -CX * 20, edge = [];
  for (let x = -40; x <= W + 40; x += 24) edge.push([x + ox, 1420 + oy + Math.sin(x * .007 + t * .3) * 40 + Math.sin(x * .019) * 14]);
  ctx.fillStyle = MG.paper; mpoly([...edge, [W + 40, H + 40], [-40, H + 40]]); ctx.fill();
  ctx.save(); mpoly([...edge, [W + 40, H + 40], [-40, H + 40]]); ctx.clip();
  for (const [a, b, c] of [[120, 1600, 520], [560, 1560, 980], [300, 1780, 760]]) { ctx.fillStyle = tone(.28); ctx.beginPath(); ctx.moveTo(a + ox, b + oy); ctx.quadraticCurveTo((a + c) / 2 + ox, b + 120 + oy, c + ox, b + 40 + oy); ctx.quadraticCurveTo((a + c) / 2 + ox, b + 40 + oy, a + ox, b + oy); ctx.fill(); }
  ctx.restore();
  ctx.lineJoin = 'round'; ctx.lineCap = 'round'; ctx.strokeStyle = MG.ink; ctx.lineWidth = 10; ctx.beginPath(); edge.forEach((v, i) => i ? ctx.lineTo(v[0], v[1]) : ctx.moveTo(v[0], v[1])); ctx.stroke();
  for (const [a, b, c, d] of [[100, 1590, 540, 1620], [520, 1560, 1000, 1590], [260, 1770, 780, 1800], [700, 1730, 1100, 1700]]) brush([[a + ox, b + oy], [(a + c) / 2 + ox, b + 70 + oy], [c + ox, d + oy]], 2, 7);
}
function mangaCat(w, h, t) {
  ctx.fillStyle = '#FFFFFF'; ctx.fillRect(0, 0, w, h);
  ctx.fillStyle = tone(.16, 10); ctx.fillRect(0, 0, w, h * .72);      // the wall in a light tone
  ctx.fillStyle = '#FFFFFF'; ctx.fillRect(0, h * .72, w, h * .28);
  ctx.strokeStyle = MG.ink; ctx.lineWidth = 3; for (let i = 0; i < 14; i++) { const y = h * .76 + i * 26; ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y + 6); ctx.stroke(); }      // hatched floor
  ctx.lineWidth = 8; ctx.beginPath(); ctx.moveTo(0, h * .72); ctx.lineTo(w, h * .72); ctx.stroke();
  const u = (t % 2.6) / 2.6, bx = w * .62, by = h * .72, bw = w * .26, bh = h * .12, pop = u > .62 ? Math.sin(clamp((u - .62) / .12) * Math.PI) : 0;
  const bxr = [bx - bw / 2 - pop * 20, by - bh - pop * 10, bw + pop * 40, bh + pop * 10];
  ctx.fillStyle = tone(.45, 10); ctx.fillRect(...bxr); ctx.lineWidth = 8; ctx.strokeRect(...bxr);
  let cx, cy, sq = 1;
  if (u < .3) { cx = lerp(-w * .1, w * .3, u / .3); cy = by - h * .09 + Math.abs(Math.sin(u * 40)) * -8; }
  else if (u < .55) { const k = (u - .3) / .25; cx = lerp(w * .3, bx, k); cy = lerp(by - h * .09, by - h * .1, k) - Math.sin(k * Math.PI) * h * .22; }
  else if (u < .74) { cx = bx; cy = by - h * .08; sq = 1 + .25 * Math.sin((u - .55) / .19 * Math.PI); }
  else { const k = (u - .74) / .26; cx = bx + k * w * .1; cy = by - h * .09 - Math.sin(clamp(k * 1.4) * Math.PI) * h * .3; sq = .9; }
  const r = w * .11;
  if (u > .3 && u < .55) { ctx.strokeStyle = MG.ink; ctx.lineWidth = 4; for (let i = 0; i < 5; i++) { ctx.beginPath(); ctx.moveTo(cx - r * 1.4 - i * 6, cy - r * .6 + i * r * .3); ctx.lineTo(cx - r * 3.2 - i * 10, cy - r * .2 + i * r * .3); ctx.stroke(); } }      // speed lines behind the leap
  ctx.save(); ctx.translate(cx, cy); ctx.scale(sq, 1 / sq); ctx.fillStyle = MG.ink;
  ctx.beginPath(); ctx.ellipse(0, 0, r * 1.15, r, 0, 0, TAU); ctx.moveTo(-r * .7, -r * .55); ctx.lineTo(-r * .45, -r * 1.25); ctx.lineTo(-r * .1, -r * .8); ctx.moveTo(r * .1, -r * .8); ctx.lineTo(r * .45, -r * 1.25); ctx.lineTo(r * .7, -r * .55); ctx.fill();
  ctx.fillStyle = '#FFFFFF'; for (const s of [-1, 1]) { ctx.beginPath(); ctx.arc(s * r * .35, -r * .15, r * .22, 0, TAU); ctx.fill(); }
  ctx.fillStyle = MG.ink; for (const s of [-1, 1]) { ctx.beginPath(); ctx.arc(s * r * .35 + r * .05, -r * .12, r * .1, 0, TAU); ctx.fill(); }
  ctx.restore();
  if (pop > .3) { ctx.fillStyle = MG.ink; for (let i = 0; i < 7; i++) { const a = -Math.PI / 2 + (i - 3) * .32, d0 = bw * .62, d1 = bw * (1 + pop * .3); ctx.beginPath(); ctx.moveTo(bx + Math.cos(a - .05) * d0, by - bh + Math.sin(a - .05) * d0 * .7); ctx.lineTo(bx + Math.cos(a) * d1, by - bh + Math.sin(a) * d1 * .7); ctx.lineTo(bx + Math.cos(a + .05) * d0, by - bh + Math.sin(a + .05) * d0 * .7); ctx.fill(); } }
}
function mangaChrome(w, h, t, prog) {
  const ix = w - 70; ctx.strokeStyle = MG.ink; ctx.fillStyle = '#FFFFFF'; ctx.lineWidth = 6;
  ctx.save(); ctx.translate(ix, h * .52); ctx.beginPath(); ctx.moveTo(0, 14); ctx.bezierCurveTo(-34, -10, -16, -34, 0, -16); ctx.bezierCurveTo(16, -34, 34, -10, 0, 14); ctx.fill(); ctx.stroke(); ctx.restore();
  ctx.beginPath(); ctx.ellipse(ix, h * .61, 26, 22, 0, 0, TAU); ctx.fill(); ctx.stroke();
  ctx.save(); ctx.translate(ix, h * .70); ctx.beginPath(); ctx.moveTo(-22, 16); ctx.quadraticCurveTo(-18, -10, 8, -10); ctx.lineTo(8, -22); ctx.lineTo(28, 0); ctx.lineTo(8, 22); ctx.lineTo(8, 8); ctx.quadraticCurveTo(-10, 6, -22, 16); ctx.fill(); ctx.stroke(); ctx.restore();
  ctx.fillStyle = MG.ink; ctx.fillRect(0, h - 30, w, 30); ctx.fillStyle = MG.red; ctx.fillRect(0, h - 24, w * prog, 18);
}
function phoneAt(t, o = {}) {
  card(0, 0, 0, PHONE.w, PHONE.h, (w, h) => {
    ctx.fillStyle = MG.paper; rr(-.22, -.22, w + .44, h + .44, 1.2); ctx.fill();      // the white gap that keeps ink off ink
    ctx.fillStyle = MG.ink; rr(0, 0, w, h, 1.0); ctx.fill();
    ctx.fillStyle = MG.paper; ctx.beginPath(); ctx.moveTo(.35, 2.2); ctx.lineTo(.55, 1.4); ctx.lineTo(.62, 3.6); ctx.closePath(); ctx.fill();      // a gloss stroke
  });
  card(0, 0, -.01, SCREEN.w, SCREEN.h, (w, h) => { ctx.save(); rr(0, 0, w, h, .7); ctx.clip(); ctx.scale(1 / 100, 1 / 100); mangaCat(w * 100, h * 100, t); mangaChrome(w * 100, h * 100, t, o.prog ?? ((t * .09) % 1)); ctx.restore(); });
}
function hand(t, lift) {
  const p = P(2.2 + (1 - lift) * 1.5, -9.5 + lift * 5.2, -.4); if (!p) return; const s = p[2];
  ctx.save(); ctx.translate(p[0], p[1]); ctx.rotate(-.35 + lift * .15); ctx.scale(s, s);
  ctx.fillStyle = MG.paper; ctx.strokeStyle = MG.ink; ctx.lineWidth = .16; rr(-1.05, -1.3, 2.1, 9, 1.05); ctx.fill(); ctx.stroke();
  ctx.save(); rr(-1.05, -1.3, 2.1, 9, 1.05); ctx.clip(); ctx.fillStyle = tone(.3, 9); ctx.fillRect(.35, -1.4, 1, 10); ctx.restore();      // shade on one side
  ctx.lineWidth = .1; rr(-.62, -1.05, 1.24, 1.5, .55); ctx.stroke();
  ctx.lineWidth = .08; ctx.beginPath(); ctx.moveTo(-.7, 1.4); ctx.quadraticCurveTo(0, 1.7, .7, 1.4); ctx.stroke();
  ctx.restore();
}

// ---------- type: heavy sans, white with an ink outline and a hard ink shadow; the accent word in vermilion
function inkText(txt, x, y, sz, fill, o = {}) {
  ctx.font = `900 ${sz}px ${MSANS}`; ctx.textAlign = o.al ?? 'left'; ctx.textBaseline = 'alphabetic'; ctx.lineJoin = 'round';
  ctx.fillStyle = MG.ink; ctx.lineWidth = sz * .2; ctx.strokeStyle = MG.ink; ctx.strokeText(txt, x + sz * .07, y + sz * .07); ctx.fillText(txt, x + sz * .07, y + sz * .07);
  ctx.strokeText(txt, x, y); ctx.fillStyle = fill; ctx.fillText(txt, x, y);
}
STY.title = t => {
  ctx.save(); ctx.translate(72, 226); ctx.rotate(-.03); inkText('你上划之前', 0, 0, 120, MG.paper); ctx.restore();
  ctx.font = `700 32px ${MSANS}`; ctx.fillStyle = MG.paper; ctx.textAlign = 'left'; ctx.fillText('你按下去之后', 80, 296);
};
STY.hero = (t, t0, lines, x, y) => {
  lines.forEach((ln, i) => {
    const { k, show } = heroK(t, t0, i); if (k <= 0) return; const sz = ln.size ?? 120;
    const nC = ln.parts.reduce((a, p) => a + [...p[0]].length, 0), n = show(nC); let cx = 0, used = 0;
    ctx.save(); ctx.translate(x, y); ctx.rotate(-.035); ctx.scale(lerp(1.25, 1, k), lerp(1.25, 1, k));      // slams in
    for (const [s, role] of ln.parts) { const vis = [...s].slice(0, Math.max(0, n - used)).join(''); used += [...s].length; inkText(vis, cx, 0, sz, role === 'a' ? MG.red : MG.paper); ctx.font = `900 ${sz}px ${MSANS}`; cx += ctx.measureText(s).width; }
    ctx.restore();
  });
};
STY.sub = txt => {      // a narration box
  ctx.font = `700 50px ${MSANS}`; const w = ctx.measureText(txt).width;
  ctx.fillStyle = MG.ink; ctx.fillRect(W / 2 - w / 2 - 30 + 8, 1640 - 44 + 8, w + 60, 88);
  ctx.fillStyle = '#FFFFFF'; ctx.fillRect(W / 2 - w / 2 - 30, 1640 - 44, w + 60, 88); ctx.strokeStyle = MG.ink; ctx.lineWidth = 5; ctx.strokeRect(W / 2 - w / 2 - 30, 1640 - 44, w + 60, 88);
  ctx.fillStyle = MG.ink; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(txt, W / 2, 1642);
};

// ---------- the wall: a page of tiny panels; the funnel: an ink funnel with speed lines pouring in; the batch: stat cards
const DENS = [.12, .3, .5, .7];
function panelIcon(kind, cx, cy, r, col) {
  ctx.fillStyle = col; ctx.strokeStyle = col; ctx.lineWidth = r * .25; ctx.beginPath();
  if (kind === 'ball') ctx.arc(cx, cy, r, 0, TAU);
  else if (kind === 'bowl') ctx.arc(cx, cy, r, 0, Math.PI);
  else if (kind === 'hill') { ctx.moveTo(cx - r * 1.4, cy + r); ctx.lineTo(cx - r * .2, cy - r); ctx.lineTo(cx + r * .4, cy); ctx.lineTo(cx + r * .8, cy - r * .5); ctx.lineTo(cx + r * 1.4, cy + r); }
  else if (kind === 'note') { ctx.arc(cx - r * .3, cy + r * .5, r * .35, 0, TAU); ctx.rect(cx - r * .05, cy - r, r * .18, r * 1.5); }
  else if (kind === 'sun') { ctx.arc(cx, cy, r * .6, 0, TAU); }
  else if (kind === 'wave') { ctx.ellipse(cx, cy, r * 1.3, r * .35, 0, 0, TAU); }
  else if (kind === 'car') { ctx.rect(cx - r, cy - r * .2, r * 2, r * .6); ctx.rect(cx - r * .5, cy - r * .6, r, r * .5); }
  else ctx.ellipse(cx, cy, r, r * .8, 0, 0, TAU);
  ctx.fill();
}
function panel(x, y, w, h, idx, o = {}) {
  ctx.fillStyle = '#FFFFFF'; ctx.fillRect(x, y, w, h);
  const d = DENS[idx % 4], kind = THEMES[idx % THEMES.length][2];
  if (w > 10) { ctx.fillStyle = tone(d, w > 60 ? 9 : 6); ctx.fillRect(x, y + h * (o.full ? 0 : .55), w, h * (o.full ? 1 : .45)); }
  if (w > 18) panelIcon(kind, x + w / 2, y + h * .42, w * .2, d > .45 ? '#FFFFFF' : MG.ink);
  ctx.strokeStyle = o.edge ?? MG.ink; ctx.lineWidth = o.lw ?? Math.max(1.5, w * .045); ctx.strokeRect(x, y, w, h);
}
STY.wallBg = () => { ctx.fillStyle = MG.paper; ctx.fillRect(0, 0, W, H); };
STY.wallCard = (x, y, w, h, idx) => panel(x, y, w, h, idx);
STY.funnelBack = (q, k, t) => {
  const [a, b, c, d] = q;
  ctx.save(); ctx.globalAlpha = k;
  ctx.fillStyle = MG.paper; mpoly([a, b, c, d]); ctx.fill(); ctx.fillStyle = tone(.18, 8); mpoly([a, b, c, d]); ctx.fill();
  // speed lines pouring toward the mouth
  ctx.save(); mpoly([a, b, c, d]); ctx.clip(); const m = [(c[0] + d[0]) / 2, c[1] + 40], r = mulberry32(31 + Math.floor(t * 15)); ctx.fillStyle = MG.ink; ctx.beginPath();
  for (let i = 0; i < 70; i++) { const x0 = lerp(a[0], b[0], r()), y0 = a[1] - 20, ww = 3 + r() * 9; ctx.moveTo(x0 - ww, y0); ctx.lineTo(x0 + ww, y0); ctx.lineTo(lerp(x0, m[0], .55 + r() * .4), lerp(y0, m[1], .55 + r() * .4)); ctx.closePath(); }
  ctx.fill(); ctx.restore();
  ctx.restore();
};
STY.streamCard = (x, y, w, h, idx, t, u, k) => {
  ctx.save(); ctx.globalAlpha = k * (u < .1 ? u / .1 : 1); ctx.translate(x, y); ctx.rotate((hash(idx, 6) - .5) * 1.0 + u * (hash(idx, 7) - .5) * 2);
  ctx.strokeStyle = MG.ink; ctx.lineWidth = 3; for (let i = -1; i <= 1; i++) { ctx.beginPath(); ctx.moveTo(i * w * .3, -h * .6); ctx.lineTo(i * w * .3, -h * 1.3); ctx.stroke(); }
  panel(-w / 2, -h / 2, w, h, idx, { lw: 3 }); ctx.restore();
};
STY.funnelFront = (q, k, t) => {
  const [a, b, c, d] = q, rx = (b[0] - a[0]) / 2, ry = rx * .11, mx = (a[0] + b[0]) / 2;
  ctx.save(); ctx.globalAlpha = k;
  brush([[a[0] - 6, a[1]], [lerp(a[0], d[0], .5), lerp(a[1], d[1], .5)], [d[0], d[1]]], 9, 7);
  brush([[b[0] + 6, b[1]], [lerp(b[0], c[0], .5), lerp(b[1], c[1], .5)], [c[0], c[1]]], 9, 7);
  ctx.strokeStyle = MG.ink; ctx.lineWidth = 12; ctx.beginPath(); ctx.ellipse(mx, a[1], rx, ry, 0, 0, TAU); ctx.stroke();
  ctx.fillStyle = MG.ink; ctx.beginPath(); ctx.ellipse((c[0] + d[0]) / 2, c[1], (c[0] - d[0]) / 2 + 8, 14, 0, 0, TAU); ctx.fill();
  ctx.restore();
};
STY.dim = (t, k) => {
  ctx.fillStyle = `rgba(242,238,229,${.55 * k})`; ctx.fillRect(0, 0, W, H);
  if (t >= C.q - .5) { ctx.save(); ctx.globalAlpha = clamp(ev(t, C.q - .5, .5)) * .9; focus(W / 2, H * .5, 420, 120, 19, MG.ink, t); ctx.restore(); }      // focus lines on the scoreboard
};
const MROT = [-.03, .02, .035, -.035, .02, -.02];
STY.batchCard = (W1, H1, k, odds, t, back, i, u) => {
  ctx.save(); ctx.translate(W1 / 2, H1 / 2); ctx.rotate(MROT[i]); ctx.translate(-W1 / 2, -H1 / 2);
  ctx.fillStyle = MG.ink; ctx.fillRect(16, 16, W1, H1);
  ctx.fillStyle = '#FFFFFF'; ctx.fillRect(0, 0, W1, H1);
  // the picture: a panel of its own
  panel(22, 22, W1 - 44, H1 * .36, k, { full: true, lw: 6 });
  if (!back) oddsRows(t, odds).forEach((r, j) => {
    if (!r.on) return; const y0 = H1 * .52 + j * 84, bx = 118, bw = W1 - 240;
    ctx.fillStyle = MG.ink; ctx.fillRect(16, y0 - 30, 92, 60); ctx.font = `900 38px ${MSANS}`; ctx.fillStyle = '#FFFFFF'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(r.lab, 62, y0 + 1);
    ctx.fillStyle = '#FFFFFF'; ctx.fillRect(bx, y0 - 16, bw, 32); ctx.fillStyle = MG.red; ctx.fillRect(bx, y0 - 16, Math.max(5, bw * r.v * r.k), 32);
    ctx.strokeStyle = MG.ink; ctx.lineWidth = 5; ctx.strokeRect(bx, y0 - 16, bw, 32); ctx.lineWidth = 2; for (let s = 1; s < 10; s++) { ctx.beginPath(); ctx.moveTo(bx + bw * s / 10, y0 + 6); ctx.lineTo(bx + bw * s / 10, y0 + 16); ctx.stroke(); }
    ctx.save(); ctx.translate(W1 - 14, y0 + 2); ctx.transform(1, 0, -.18, 1, 0, 0); ctx.font = `900 48px ${MSANS}`; ctx.textAlign = 'right'; ctx.fillStyle = MG.ink; ctx.fillText(r.txt, 0, 0); ctx.restore();
  });
  ctx.strokeStyle = back ? MG.ink : MG.red; ctx.lineWidth = back ? 8 : 12; ctx.strokeRect(0, 0, W1, H1);
  if (back) { ctx.fillStyle = tone(.3, 7); ctx.fillRect(0, 0, W1, H1); }
  ctx.restore();
};
window.ready = Promise.all([`900 84px ${MSANS}`, `700 54px ${MSANS}`].map(f => document.fonts.load(f)));
