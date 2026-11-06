// Style 1 · 纸艺拼贴 — cut paper on a night-blue board. Everything is a paper layer with a real shadow;
// the one accent is a gold thread (your watch time): the progress bar, the thread that fishes the batch, the odds strips.
'use strict';
const PP = { night: '#1B2443', night2: '#243158', night3: '#2F4175', cream: '#F1E8D5', kraft: '#C79B6A', kraftD: '#8C6640', gold: '#E8A836', goldD: '#B97A1C', goldL: '#FFE2A0', ink: '#1E1C27', skin: '#D6A07F' };
const PSERIF = '"Noto Serif CJK SC"', PSANS = '"Noto Sans CJK SC"';
const PTH = ['#4C74C2', '#C7607C', '#3A9073', '#7A5DBB', '#CF8743', '#4A9DB5', '#BC4D4D', '#5E6CC0'];

// ---------- paper helpers
function jag(pts, seed, amp, step) {      // subdivide each edge and nudge it: a hand-cut edge (stable over time: seeded)
  const out = [], r = mulberry32(seed);
  for (let i = 0; i < pts.length; i++) {
    const [x0, y0] = pts[i], [x1, y1] = pts[(i + 1) % pts.length], L = Math.hypot(x1 - x0, y1 - y0) || 1, n = Math.max(1, Math.round(L / step)), nx = -(y1 - y0) / L, ny = (x1 - x0) / L;
    for (let k = 0; k < n; k++) { const u = k / n, j = k === 0 ? 0 : (r() - .5) * 2 * amp; out.push([x0 + (x1 - x0) * u + nx * j, y0 + (y1 - y0) * u + ny * j]); }
  }
  return out;
}
const rectPts = (x, y, w, h) => [[x, y], [x + w, y], [x + w, y + h], [x, y + h]];
function poly(pts) { ctx.beginPath(); pts.forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)); ctx.closePath(); }
function shOn(blur, dx, dy, a = .45) { ctx.shadowColor = `rgba(3,5,14,${a})`; ctx.shadowBlur = blur; ctx.shadowOffsetX = dx; ctx.shadowOffsetY = dy; }
function shOff() { ctx.shadowColor = 'transparent'; ctx.shadowBlur = 0; ctx.shadowOffsetX = 0; ctx.shadowOffsetY = 0; }
function star(x, y, r) { ctx.beginPath(); for (let i = 0; i < 10; i++) { const a = -Math.PI / 2 + i * Math.PI / 5, rr_ = i % 2 ? r * .45 : r; ctx.lineTo(x + Math.cos(a) * rr_, y + Math.sin(a) * rr_); } ctx.closePath(); }
// the gold thread: a twisted cord with its own small shadow
function thread(pts, wd, t) {
  const path = () => { ctx.beginPath(); ctx.moveTo(...pts[0]); for (let i = 1; i < pts.length - 1; i++) ctx.quadraticCurveTo(pts[i][0], pts[i][1], (pts[i][0] + pts[i + 1][0]) / 2, (pts[i][1] + pts[i + 1][1]) / 2); ctx.lineTo(...pts[pts.length - 1]); };
  ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  shOn(6, 3, 6, .5); path(); ctx.strokeStyle = PP.goldD; ctx.lineWidth = wd; ctx.stroke(); shOff();
  path(); ctx.strokeStyle = PP.gold; ctx.lineWidth = wd * .7; ctx.stroke();
  ctx.setLineDash([wd * .5, wd * 1.1]); ctx.lineDashOffset = -t * wd * 3; path(); ctx.strokeStyle = PP.goldL; ctx.lineWidth = wd * .32; ctx.stroke(); ctx.setLineDash([]);
}
// paper grain, made once
const PGRAIN = (() => {
  const c = document.createElement('canvas'); c.width = 540; c.height = 960; const g = c.getContext('2d'), im = g.createImageData(540, 960), r = mulberry32(77);
  for (let i = 0; i < im.data.length; i += 4) { const v = 128 + (r() - .5) * 60; im.data[i] = im.data[i + 1] = im.data[i + 2] = v; im.data[i + 3] = 255; }
  g.putImageData(im, 0, 0); g.globalAlpha = .35;
  for (let i = 0; i < 1400; i++) { const x = r() * 540, y = r() * 960, a = r() * TAU, l = 3 + r() * 12; g.strokeStyle = r() < .5 ? '#fff' : '#000'; g.lineWidth = .5; g.beginPath(); g.moveTo(x, y); g.lineTo(x + Math.cos(a) * l, y + Math.sin(a) * l); g.stroke(); }
  return c;
})();
const PBLOT = (() => { const c = document.createElement('canvas'); c.width = 27; c.height = 48; const g = c.getContext('2d'), im = g.createImageData(27, 48), r = mulberry32(78); for (let i = 0; i < im.data.length; i += 4) { const v = 128 + (r() - .5) * 90; im.data[i] = im.data[i + 1] = im.data[i + 2] = v; im.data[i + 3] = 255; } g.putImageData(im, 0, 0); return c; })();
STY.post = () => {
  ctx.save(); ctx.globalCompositeOperation = 'overlay'; ctx.globalAlpha = .28; ctx.drawImage(PGRAIN, 0, 0, W, H);
  ctx.globalCompositeOperation = 'soft-light'; ctx.globalAlpha = .35; ctx.imageSmoothingEnabled = true; ctx.drawImage(PBLOT, 0, 0, W, H); ctx.restore();
};

// ---------- S0 · the bedroom in paper
function bedroom(t) {
  ctx.fillStyle = PP.night; ctx.fillRect(0, 0, W, H);
  const ox = -CX * 22, oy = CY * 16 + Math.sin(t * .5) * 3;
  // the window on the back wall
  const win = jag(rectPts(560 + ox, 360 + oy, 470, 700), 11, 3, 70);
  shOn(34, 10, 18, .55); ctx.fillStyle = '#121A33'; poly(win); ctx.fill(); shOff();
  ctx.save(); poly(win); ctx.clip();
  const sky = ctx.createLinearGradient(0, 360 + oy, 0, 1060 + oy); sky.addColorStop(0, '#22305C'); sky.addColorStop(1, '#3A4C82'); ctx.fillStyle = sky; ctx.fillRect(0, 0, W, H);
  // far hills of paper
  for (const [yy, col, sd] of [[880, '#2A3A68', 3], [950, '#22305A', 4]]) { const r = mulberry32(sd), pts = [[540 + ox, 1100 + oy]]; for (let x = 540; x <= 1060; x += 26) pts.push([x + ox, yy + oy + Math.sin(x * .012 + sd) * 30 + (r() - .5) * 6]); pts.push([1060 + ox, 1100 + oy]); shOn(16, 0, -6, .4); ctx.fillStyle = col; poly(pts); ctx.fill(); shOff(); }
  // the moon and three stars
  shOn(24, 8, 12, .5); ctx.fillStyle = PP.cream; poly(jag(Array.from({ length: 18 }, (_, i) => [880 + ox * 1.1 + Math.cos(i / 18 * TAU) * 78, 520 + oy + Math.sin(i / 18 * TAU) * 78]), 12, 2.5, 30)); ctx.fill();
  ctx.fillStyle = '#E2D6BC'; ctx.beginPath(); ctx.arc(855 + ox * 1.1, 505 + oy, 16, 0, TAU); ctx.arc(905 + ox * 1.1, 548 + oy, 10, 0, TAU); ctx.fill();
  for (const [x, y, r] of [[660, 470, 18], [990, 690, 14], [720, 640, 11]]) { ctx.fillStyle = PP.cream; star(x + ox, y + oy + Math.sin(t * 1.2 + x) * 4, r); ctx.fill(); }
  shOff(); ctx.restore();
  // window frame: paper strips laid on top
  ctx.fillStyle = PP.night2; shOn(14, 4, 8, .5);
  for (const pts of [rectPts(782 + ox, 360 + oy, 22, 700), rectPts(560 + ox, 700 + oy, 470, 20)]) { poly(jag(pts, 13, 1.5, 60)); ctx.fill(); }
  shOff();
  // the pillow, cream-blue, behind the blanket
  shOn(30, 0, 14, .5); ctx.fillStyle = '#C9CFE0'; poly(jag([[-60, 1180 + oy * 1.3], [380, 1160 + oy * 1.3], [470, 1290 + oy * 1.3], [420, 1470], [-60, 1480]], 21, 5, 50)); ctx.fill(); shOff();
  ctx.strokeStyle = 'rgba(30,36,70,.25)'; ctx.lineWidth = 5; ctx.beginPath(); ctx.moveTo(40, 1230 + oy * 1.3); ctx.quadraticCurveTo(220, 1260 + oy * 1.3, 380, 1215 + oy * 1.3); ctx.stroke();
  // three layers of blanket, each a cut sheet with its own shadow on the one behind
  [[1390, '#2C3C6B', .6, 31], [1500, '#384D86', .85, 32], [1620, '#4560A0', 1.15, 33]].forEach(([y0, col, par, sd]) => {
    const r = mulberry32(sd), yy = y0 + CY * 26 * par, pts = [];
    for (let x = -40; x <= W + 40; x += 30) pts.push([x - CX * 20 * par, yy + Math.sin(x * .006 + sd + t * .35) * 34 + Math.sin(x * .017 + sd * 2) * 12 + (r() - .5) * 4]);
    pts.push([W + 40, H + 40], [-40, H + 40]);
    shOn(30, 0, -10, .55); ctx.fillStyle = col; poly(pts); ctx.fill(); shOff();
    ctx.strokeStyle = 'rgba(10,14,32,.22)'; ctx.lineWidth = 6; ctx.beginPath(); ctx.moveTo(pts[3][0], pts[3][1] + 80); ctx.quadraticCurveTo(W * .5, yy + 140 + Math.sin(sd) * 30, pts[pts.length - 6][0], pts[pts.length - 6][1] + 110); ctx.stroke();
  });
}
function paperCat(w, h, t) {
  ctx.fillStyle = '#F4D5A2'; ctx.fillRect(0, 0, w, h);
  ctx.fillStyle = '#F8E3BE'; ctx.beginPath(); ctx.arc(w * .2, h * .2, w * .16, 0, TAU); ctx.fill();      // a paper sun on the wall
  const fl = [[-10, h * .72], ...Array.from({ length: 9 }, (_, i) => [i * w / 8, h * .72 + Math.sin(i * 1.7) * 8]), [w + 10, h * .72], [w + 10, h + 10], [-10, h + 10]];
  shOn(14, 0, -6, .3); ctx.fillStyle = '#D69A5A'; poly(fl); ctx.fill(); shOff();
  const u = ((t + 1.37) % 2.6) / 2.6, bx = w * .62, by = h * .72, bw = w * .26, bh = h * .12, pop = u > .62 ? Math.sin(clamp((u - .62) / .12) * Math.PI) : 0;
  shOn(16, 6, 10, .35); ctx.fillStyle = '#A8682E'; poly(jag(rectPts(bx - bw / 2 - pop * 20, by - bh - pop * 10, bw + pop * 40, bh + pop * 10), 41, 3, 40)); ctx.fill(); shOff();
  ctx.fillStyle = '#8A5524'; ctx.fillRect(bx - bw / 2 - pop * 20, by - bh - pop * 10, bw + pop * 40, bh * .2);
  let cx, cy, sq = 1;
  if (u < .3) { cx = lerp(-w * .1, w * .3, u / .3); cy = by - h * .09 + Math.abs(Math.sin(u * 40)) * -8; }
  else if (u < .55) { const k = (u - .3) / .25; cx = lerp(w * .3, bx, k); cy = lerp(by - h * .09, by - h * .1, k) - Math.sin(k * Math.PI) * h * .22; }
  else if (u < .74) { cx = bx; cy = by - h * .08; sq = 1 + .25 * Math.sin((u - .55) / .19 * Math.PI); }
  else { const k = (u - .74) / .26; cx = bx + k * w * .1; cy = by - h * .09 - Math.sin(clamp(k * 1.4) * Math.PI) * h * .3; sq = .9; }
  const r = w * .11;
  ctx.save(); ctx.translate(cx, cy); ctx.scale(sq, 1 / sq);
  shOn(18, 8, 14, .4); ctx.fillStyle = '#5A5D6D';
  ctx.beginPath(); ctx.ellipse(0, 0, r * 1.15, r, 0, 0, TAU); ctx.moveTo(-r * .7, -r * .55); ctx.lineTo(-r * .45, -r * 1.25); ctx.lineTo(-r * .1, -r * .8); ctx.moveTo(r * .1, -r * .8); ctx.lineTo(r * .45, -r * 1.25); ctx.lineTo(r * .7, -r * .55); ctx.fill(); shOff();
  ctx.fillStyle = PP.cream; for (const s of [-1, 1]) { ctx.beginPath(); ctx.arc(s * r * .35, -r * .15, r * .2, 0, TAU); ctx.fill(); }
  ctx.fillStyle = PP.ink; for (const s of [-1, 1]) { ctx.beginPath(); ctx.arc(s * r * .35 + r * .05, -r * .12, r * .09, 0, TAU); ctx.fill(); }
  ctx.restore();
  if (pop > .3) { ctx.fillStyle = '#8A5524'; for (let i = 0; i < 6; i++) { const a = -Math.PI / 2 + (i - 2.5) * .35, d = bw * (.8 + pop * .2); ctx.beginPath(); ctx.moveTo(bx + Math.cos(a) * d, by - bh + Math.sin(a) * d * .7); ctx.lineTo(bx + Math.cos(a + .08) * (d - 30), by - bh + Math.sin(a + .08) * (d - 30) * .7); ctx.lineTo(bx + Math.cos(a - .08) * (d - 30), by - bh + Math.sin(a - .08) * (d - 30) * .7); ctx.fill(); } }
}
function paperChrome(w, h, t, prog) {
  const ix = w - 70; shOn(8, 3, 5, .35); ctx.fillStyle = PP.cream;
  ctx.save(); ctx.translate(ix, h * .52); ctx.beginPath(); ctx.moveTo(0, 14); ctx.bezierCurveTo(-34, -10, -16, -34, 0, -16); ctx.bezierCurveTo(16, -34, 34, -10, 0, 14); ctx.fill(); ctx.restore();
  ctx.beginPath(); ctx.ellipse(ix, h * .61, 26, 22, 0, 0, TAU); ctx.fill();
  ctx.save(); ctx.translate(ix, h * .70); ctx.beginPath(); ctx.moveTo(-22, 16); ctx.quadraticCurveTo(-18, -10, 8, -10); ctx.lineTo(8, -22); ctx.lineTo(28, 0); ctx.lineTo(8, 22); ctx.lineTo(8, 8); ctx.quadraticCurveTo(-10, 6, -22, 16); ctx.fill(); ctx.restore();
  shOff();
  ctx.fillStyle = 'rgba(241,232,213,.45)'; ctx.fillRect(0, h - 14, w, 6);
  thread([[0, h - 11], [w * prog * .5, h - 13], [w * prog, h - 11]], 14, t);
}
function phoneAt(t, o = {}) {
  card(0, 0, 0, PHONE.w, PHONE.h, (w, h) => { shOn(40, 18, 30, .6); ctx.fillStyle = '#15141B'; rr(0, 0, w, h, 1.0); ctx.fill(); shOff(); ctx.fillStyle = '#24232C'; rr(.1, .1, w - .2, h - .2, .92); ctx.fill(); });
  card(0, 0, -.01, SCREEN.w, SCREEN.h, (w, h) => { ctx.save(); rr(0, 0, w, h, .7); ctx.clip(); ctx.scale(1 / 100, 1 / 100); paperCat(w * 100, h * 100, t); paperChrome(w * 100, h * 100, t, o.prog ?? ((t * .09) % 1)); ctx.restore(); });
}
function hand(t, lift) {
  const p = P(2.2 + (1 - lift) * 1.5, -9.5 + lift * 5.2, -.4); if (!p) return; const s = p[2];
  ctx.save(); ctx.translate(p[0], p[1]); ctx.rotate(-.35 + lift * .15); ctx.scale(s, s);
  shOn(30, 12, 20, .55); ctx.fillStyle = PP.skin; poly(jag([[-1.05, -.3], [-.75, -1.1], [0, -1.35], [.75, -1.1], [1.05, -.3], [1.05, 7.7], [-1.05, 7.7]], 51, .04, .5)); ctx.fill(); shOff();
  shOn(6, 2, 4, .3); ctx.fillStyle = '#EDC4A8'; poly(jag([[-.6, -.4], [-.4, -1.0], [0, -1.12], [.4, -1.0], [.6, -.4], [.55, .35], [-.55, .35]], 52, .03, .3)); ctx.fill(); shOff();
  ctx.fillStyle = '#C08A6B'; poly(jag(rectPts(-1.05, 1.6, 2.1, .12), 53, .02, .3)); ctx.fill();
  ctx.restore();
}

// ---------- type: torn cream strips, ink type; the accent word gets a gold thread under it
function strip(x, y, w, h, seed, rot = 0) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot);
  shOn(24, 8, 14, .5); ctx.fillStyle = PP.cream; poly(jag(rectPts(0, 0, w, h), seed, 6, 20)); ctx.fill(); shOff();
  ctx.restore();
}
STY.title = t => {
  ctx.save(); ctx.translate(0, Math.sin(t * .8) * 3);
  strip(-60, 110, 780, 170, 5, -.022);
  ctx.save(); ctx.translate(-60, 110); ctx.rotate(-.022); ctx.font = `700 120px ${PSERIF}`; ctx.fillStyle = PP.ink; ctx.textBaseline = 'alphabetic'; ctx.textAlign = 'left'; ctx.fillText('你上划之前', 128, 132); ctx.restore();
  ctx.save(); ctx.translate(78, 300); ctx.rotate(.025); shOn(14, 4, 8, .45); ctx.fillStyle = PP.kraft; poly(jag(rectPts(0, 0, 250, 58), 6, 3, 18)); ctx.fill(); shOff();
  ctx.font = `700 32px ${PSANS}`; ctx.fillStyle = PP.ink; ctx.textBaseline = 'middle'; ctx.fillText('你按下去之后', 26, 30); ctx.restore();
  ctx.restore();
};
STY.hero = (t, t0, lines, x, y) => {
  lines.forEach((ln, i) => {
    const { k, show } = heroK(t, t0, i); if (k <= 0) return;
    const sz = ln.size ?? 120; ctx.font = `700 ${sz}px ${PSERIF}`;
    const total = ln.parts.reduce((a, p) => a + ctx.measureText(p[0]).width, 0), seed = [...ln.parts.map(p => p[0]).join('')].reduce((a, c) => a + c.charCodeAt(0), 0);
    const rot = (hash(seed, 9) - .5) * .05, xx = x - (1 - k) * 120;
    ctx.save(); ctx.translate(xx, y); ctx.rotate(rot);
    strip(-40, -sz * 1.0, total + 80, sz * 1.32, seed, 0);
    const nC = ln.parts.reduce((a, p) => a + [...p[0]].length, 0), n = show(nC); let cx = 0, used = 0;
    for (const [s, role] of ln.parts) {
      ctx.font = `700 ${sz}px ${PSERIF}`; const vis = [...s].slice(0, Math.max(0, n - used)).join(''); used += [...s].length;
      ctx.fillStyle = PP.ink; ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic'; ctx.fillText(vis, cx, 0);
      const wv = ctx.measureText(vis).width;
      if (role === 'a' && wv > 0) thread([[cx - 6, sz * .16], [cx + wv * .35, sz * .1], [cx + wv * .7, sz * .2], [cx + wv + 6, sz * .12]], 12, t);
      cx += ctx.measureText(s).width;
    }
    ctx.restore();
  });
};
STY.sub = (txt, t) => {
  ctx.font = `700 50px ${PSANS}`; const w = ctx.measureText(txt).width, seed = [...txt].reduce((a, c) => a + c.charCodeAt(0), 0);
  ctx.save(); ctx.translate(W / 2, 1640); ctx.rotate((hash(seed, 3) - .5) * .03);
  shOn(18, 6, 10, .5); ctx.fillStyle = PP.cream; poly(jag(rectPts(-w / 2 - 34, -44, w + 68, 88), seed, 4, 18)); ctx.fill(); shOff();
  ctx.fillStyle = PP.ink; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(txt, 0, 2); ctx.restore();
};

// ---------- the wall: paper scraps pinned edge to edge; the funnel: a vellum cone; the batch: index cards
function paperThumb(w, h, k, seed) {
  const kind = THEMES[k % THEMES.length][2], col = PTH[k % PTH.length];
  ctx.fillStyle = col; poly(w > 40 ? jag(rectPts(0, 0, w, h), seed, w * .012, w * .3) : rectPts(0, 0, w, h)); ctx.fill();
  if (w < 14) return;
  ctx.fillStyle = PP.cream; ctx.strokeStyle = PP.cream; ctx.lineWidth = w * .05; const cx = w / 2, cy = h * .45, r = w * .22;
  ctx.beginPath();
  if (kind === 'ball') ctx.arc(cx, cy, r, 0, TAU);
  else if (kind === 'bowl') ctx.arc(cx, cy, r, 0, Math.PI);
  else if (kind === 'hill') { ctx.moveTo(cx - r * 1.4, cy + r); ctx.lineTo(cx - r * .2, cy - r); ctx.lineTo(cx + r * .4, cy); ctx.lineTo(cx + r * .8, cy - r * .5); ctx.lineTo(cx + r * 1.4, cy + r); }
  else if (kind === 'note') { ctx.arc(cx - r * .3, cy + r * .5, r * .35, 0, TAU); ctx.rect(cx - r * .05, cy - r, r * .18, r * 1.5); }
  else if (kind === 'sun') star(cx, cy, r);
  else if (kind === 'wave') { ctx.ellipse(cx, cy, r * 1.3, r * .35, 0, 0, TAU); }
  else if (kind === 'car') { ctx.rect(cx - r, cy - r * .2, r * 2, r * .6); ctx.rect(cx - r * .5, cy - r * .6, r, r * .5); }
  else ctx.ellipse(cx, cy, r, r * .8, 0, 0, TAU);
  ctx.fill();
}
STY.wallBg = () => { ctx.fillStyle = PP.night; ctx.fillRect(0, 0, W, H); };
STY.wallCard = (x, y, w, h, idx) => {
  const rot = (hash(idx, 5) - .5) * .1;
  ctx.save(); ctx.translate(x + w / 2, y + h / 2); ctx.rotate(rot); ctx.translate(-w / 2, -h / 2);
  ctx.fillStyle = 'rgba(3,5,14,.5)'; ctx.fillRect(w * .07, w * .12, w, h);
  paperThumb(w, h, idx, idx % 997);
  ctx.fillStyle = `rgba(18,24,50,${.42 + .2 * hash(idx, 3)})`; ctx.fillRect(-2, -2, w + 4, h + 4);      // night falls on the wall
  ctx.restore();
};
STY.funnelBack = (q, k, t) => {
  const [a, b, c, d] = q;
  ctx.save(); ctx.globalAlpha = k;
  shOn(50, 24, 40, .6); ctx.fillStyle = '#5B4127'; poly([a, b, c, d]); ctx.fill(); shOff();      // the inside of the cone, in shadow
  const g = ctx.createLinearGradient(0, a[1], 0, c[1]); g.addColorStop(0, 'rgba(20,14,8,.0)'); g.addColorStop(1, 'rgba(20,14,8,.55)'); ctx.fillStyle = g; poly([a, b, c, d]); ctx.fill();
  ctx.restore();
};
STY.streamCard = (x, y, w, h, idx, t, u, k) => {
  ctx.save(); ctx.globalAlpha = k * (u < .1 ? u / .1 : 1); ctx.translate(x, y); ctx.rotate((hash(idx, 6) - .5) * 1.2 + u * 1.5 * (hash(idx, 7) - .5)); ctx.translate(-w / 2, -h / 2);
  ctx.fillStyle = 'rgba(3,5,14,.45)'; ctx.fillRect(w * .08, w * .14, w, h); paperThumb(w, h, idx, idx); ctx.restore();
};
STY.funnelFront = (q, k, t) => {
  const [a, b, c, d] = q, rx = (b[0] - a[0]) / 2, ry = rx * .12, mx = (a[0] + b[0]) / 2;
  ctx.save(); ctx.globalAlpha = k;
  // vellum: you can see the cards through it
  const g = ctx.createLinearGradient(a[0], 0, b[0], 0); g.addColorStop(0, 'rgba(241,232,213,.42)'); g.addColorStop(.35, 'rgba(241,232,213,.16)'); g.addColorStop(.75, 'rgba(241,232,213,.26)'); g.addColorStop(1, 'rgba(241,232,213,.48)');
  ctx.fillStyle = g; poly([a, b, c, d]); ctx.fill();
  // the seams of a rolled sheet
  ctx.strokeStyle = 'rgba(241,232,213,.55)'; ctx.lineWidth = 4;
  for (let i = 1; i < 5; i++) { const u = i / 5; ctx.beginPath(); ctx.moveTo(lerp(a[0], b[0], u), a[1] + ry * Math.sin(u * Math.PI)); ctx.quadraticCurveTo(lerp(a[0], b[0], u * .6 + .2), lerp(a[1], c[1], .55), lerp(d[0], c[0], u), c[1]); ctx.stroke(); }
  // rim and mouth
  ctx.lineWidth = 10; ctx.strokeStyle = PP.cream; ctx.beginPath(); ctx.ellipse(mx, a[1], rx, ry, 0, 0, TAU); ctx.stroke();
  ctx.lineWidth = 4; ctx.strokeStyle = PP.kraftD; ctx.beginPath(); ctx.ellipse(mx, a[1] + 6, rx - 8, ry - 4, 0, 0, Math.PI); ctx.stroke();
  ctx.fillStyle = PP.cream; ctx.beginPath(); ctx.ellipse((c[0] + d[0]) / 2, c[1], (c[0] - d[0]) / 2 + 6, 10, 0, 0, TAU); ctx.fill();
  // the gold thread: comes in from above, down through the cone, out of the mouth
  const m = [(c[0] + d[0]) / 2, c[1]];
  thread([[-30, a[1] - 260], [mx - rx * .3, a[1] - 120], [mx - rx * .1, a[1] + 40], [mx + rx * .12, lerp(a[1], c[1], .45)], [m[0] - 10, lerp(a[1], c[1], .8)], [m[0], m[1] + 30]], 12, t);
  ctx.restore();
};
STY.dim = (t, k) => { ctx.fillStyle = `rgba(14,19,40,${.7 * k})`; ctx.fillRect(0, 0, W, H); };
const PROT = [-.05, .02, .045, -.03, .025, -.02];
STY.batchCard = (W1, H1, k, odds, t, back, i) => {
  ctx.save(); ctx.translate(W1 / 2, H1 / 2); ctx.rotate(PROT[i] + Math.sin(t * .9 + i) * .008); ctx.translate(-W1 / 2, -H1 / 2);
  shOn(34, 12, 24, .6); ctx.fillStyle = PP.cream; poly(jag(rectPts(0, 0, W1, H1), 300 + i, 3, 50)); ctx.fill(); shOff();
  // a cut-out picture glued on
  ctx.save(); ctx.translate(26, 34); ctx.fillStyle = 'rgba(3,5,14,.25)'; ctx.fillRect(6, 8, W1 - 52, H1 * .36); paperThumb(W1 - 52, H1 * .36, k, 400 + i); ctx.restore();
  // a strip of tape
  ctx.save(); ctx.translate(W1 / 2 + (i % 2 ? 40 : -50), 16); ctx.rotate(i % 2 ? .1 : -.08); ctx.fillStyle = 'rgba(222,196,140,.7)'; poly(jag(rectPts(-80, -22, 160, 44), 500 + i, 2, 12)); ctx.fill(); ctx.restore();
  if (!back) oddsRows(t, odds).forEach((r, j) => {
    if (!r.on) return; const y0 = H1 * .52 + j * 84, bx = 112, bw = W1 - 230;
    ctx.font = `700 40px ${PSANS}`; ctx.fillStyle = PP.ink; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.fillText(r.lab, 22, y0);
    ctx.strokeStyle = 'rgba(30,28,39,.3)'; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(bx, y0 + 16); ctx.lineTo(bx + bw, y0 + 16); ctx.stroke();
    const L = Math.max(8, bw * r.v * r.k); shOn(5, 2, 3, .35); ctx.fillStyle = PP.gold; poly(jag(rectPts(bx, y0 - 12, L, 26), 600 + i * 4 + j, 2, 14)); ctx.fill(); shOff();
    ctx.font = `700 46px ${PSERIF}`; ctx.textAlign = 'right'; ctx.fillStyle = PP.ink; ctx.fillText(r.txt, W1 - 18, y0 + 2);
  });
  if (back) { ctx.fillStyle = 'rgba(16,22,46,.22)'; poly(rectPts(0, 0, W1, H1)); ctx.fill(); }
  ctx.restore();
};
window.ready = Promise.all([`700 54px ${PSANS}`, `700 84px ${PSERIF}`, `700 54px ${UI}`].map(f => document.fonts.load(f)));
