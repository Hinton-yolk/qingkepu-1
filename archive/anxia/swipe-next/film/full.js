// 「你按下去之后」· 你上划之前. One mechanism: the next video is already picked and downloaded before you swipe —
// and what picked it is how long you stayed on this one.
// One continuous shot, 2.5D: in bed with the phone → through the screen: the queue of downloaded videos → the line behind them →
// your watch time becomes a signal → out over the night city → into the data centre → the wall of videos → a funnel → each card gets its odds.
// Look: night ink; the signal (amber) is the only thing that glows. Pure function of time; seeded noise only.
'use strict';
const W = 1080, H = 1920, FPS = 30;
const C = CUES.c, DUR = TL.duration;
const cv = document.getElementById('c'); cv.width = W; cv.height = H;
let ctx = cv.getContext('2d');
const UI = '"Noto Sans Mono CJK SC"', DSP = '"Noto Sans CJK SC"';
const AMB = '#FFB23E', INK = '#0A0F1E', NAVY = '#16203A', SLATE = '#2A3554', MIST = '#9AA6C4', WHITE = '#F3F5FA';
const TAU = Math.PI * 2;
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, k) => a + (b - a) * k;
const ev = (t, t0, d) => clamp((t - t0) / d);
const smooth = x => { x = clamp(x); return x * x * (3 - 2 * x); };
const ease = x => { x = clamp(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
const expoOut = x => { x = clamp(x); return x === 1 ? 1 : 1 - Math.pow(2, -10 * x); };
const expoIn = x => { x = clamp(x); return x === 0 ? 0 : Math.pow(2, 10 * x - 10); };
function mulberry32(a) { return () => { a |= 0; a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
const hash = (i, s = 1) => mulberry32(i * 7919 + s * 104729)();

// ------------------------------------------------------------------ 2.5D camera: x right, y up, z into the screen
let CX = 0, CY = 0, CZ = -10, F = 1000;
const P = (x, y, z) => { const d = z - CZ; if (d <= .01) return null; const s = F / d; return [W / 2 + (x - CX) * s, H / 2 - (y - CY) * s, s]; };
function rr(x, y, w, h, r) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); }
// a flat card facing the camera at depth z, centred on (x, y), size w × h (world units); draw(fn) gets a local 0..w, 0..h space
function card(x, y, z, w, h, fn, o = {}) {
  const p = P(x, y, z); if (!p) return null; const s = p[2];
  if (p[0] + w * s / 2 < -200 || p[0] - w * s / 2 > W + 200 || p[1] + h * s / 2 < -200 || p[1] - h * s / 2 > H + 200) return p;
  ctx.save(); ctx.translate(p[0] - w * s / 2, p[1] - h * s / 2); ctx.scale(s, s); ctx.globalAlpha = o.alpha ?? 1; fn(w, h, s); ctx.restore();
  return p;
}

// ------------------------------------------------------------------ type
const GLY = '0123456789';
function roll(str, t, t0, dur = .4) { if (t < t0) return ''; const p = (t - t0) / dur; return [...str].map((ch, i) => (p >= (i + 1) / str.length || !/[0-9]/.test(ch)) ? ch : GLY[Math.floor(mulberry32(i * 97 + Math.floor(t * 30))() * 10)]).join(''); }
function hero(t, t0, lines, x, y, o = {}) {      // big type that types in, line by line, with a short drop (no fade)
  if (t < t0 || (o.t1 && t >= o.t1)) return;
  ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic';
  lines.forEach((ln, i) => {
    const k = expoOut(ev(t, t0 + i * .15, .32)); if (k <= 0) return;
    const sz = ln.size ?? 120, yy = y + (o.lh ? i * o.lh : 0) - (1 - k) * 36;
    const nC = ln.parts.reduce((a, p) => a + [...p[0]].length, 0), show = Math.ceil(nC * clamp((t - t0 - i * .15) / .3));
    let cx = x, used = 0;
    for (const [s, col] of ln.parts) {
      ctx.font = `${ln.ui ? 700 : 900} ${sz}px ${ln.ui ? UI : DSP}`;
      const vis = [...s].slice(0, Math.max(0, show - used)).join(''); used += [...s].length;
      ctx.lineJoin = 'round'; ctx.lineWidth = sz * .16; ctx.strokeStyle = 'rgba(8,11,22,.9)'; ctx.strokeText(vis, cx, yy);
      ctx.fillStyle = col; ctx.fillText(vis, cx, yy); cx += ctx.measureText(s).width;
    }
  });
}
function subtitle(txt) { ctx.font = `700 54px ${UI}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.lineJoin = 'round'; ctx.lineWidth = 12; ctx.strokeStyle = '#070A14'; ctx.strokeText(txt, W / 2, 1640); ctx.fillStyle = '#F7F4EE'; ctx.fillText(txt, W / 2, 1640); }

// ------------------------------------------------------------------ the funny video on the screen: a round cat, a box that is far too small
function catGag(w, h, t) {
  const g = ctx.createLinearGradient(0, 0, 0, h); g.addColorStop(0, '#FFE7C2'); g.addColorStop(1, '#F6C98E'); ctx.fillStyle = g; ctx.fillRect(0, 0, w, h);
  ctx.fillStyle = '#E2A867'; ctx.fillRect(0, h * .72, w, h * .28);       // floor
  const u = (t % 2.6) / 2.6;
  // the box
  const bx = w * .62, by = h * .72, bw = w * .26, bh = h * .12, pop = u > .62 ? Math.sin(clamp((u - .62) / .12) * Math.PI) : 0;
  ctx.fillStyle = '#B9773E'; ctx.fillRect(bx - bw / 2 - pop * 20, by - bh - pop * 10, bw + pop * 40, bh + pop * 10);
  ctx.fillStyle = '#9A5F2E'; ctx.fillRect(bx - bw / 2 - pop * 20, by - bh - pop * 10, bw + pop * 40, bh * .18);
  // the cat: walks in, leaps, lands in the box, the box bursts, the cat pops out
  let cx, cy, sq = 1;
  if (u < .3) { cx = lerp(-w * .1, w * .3, u / .3); cy = by - h * .09 + Math.abs(Math.sin(u * 40)) * -8; }
  else if (u < .55) { const k = (u - .3) / .25; cx = lerp(w * .3, bx, k); cy = lerp(by - h * .09, by - h * .1, k) - Math.sin(k * Math.PI) * h * .22; }
  else if (u < .74) { cx = bx; cy = by - h * .08; sq = 1 + .25 * Math.sin((u - .55) / .19 * Math.PI); }
  else { const k = (u - .74) / .26; cx = bx + k * w * .1; cy = by - h * .09 - Math.sin(clamp(k * 1.4) * Math.PI) * h * .3; sq = .9; }
  const r = w * .11;
  ctx.save(); ctx.translate(cx, cy); ctx.scale(sq, 1 / sq);
  ctx.fillStyle = '#5C5F6E'; ctx.beginPath(); ctx.ellipse(0, 0, r * 1.15, r, 0, 0, TAU); ctx.fill();
  ctx.beginPath(); ctx.moveTo(-r * .7, -r * .55); ctx.lineTo(-r * .45, -r * 1.25); ctx.lineTo(-r * .1, -r * .8); ctx.moveTo(r * .1, -r * .8); ctx.lineTo(r * .45, -r * 1.25); ctx.lineTo(r * .7, -r * .55); ctx.fill();
  ctx.fillStyle = '#FFFFFF'; for (const s of [-1, 1]) { ctx.beginPath(); ctx.arc(s * r * .35, -r * .15, r * .2, 0, TAU); ctx.fill(); }
  ctx.fillStyle = '#1B1B22'; for (const s of [-1, 1]) { ctx.beginPath(); ctx.arc(s * r * .35 + r * .05, -r * .12, r * .09, 0, TAU); ctx.fill(); }
  ctx.strokeStyle = '#1B1B22'; ctx.lineWidth = r * .06; ctx.beginPath(); ctx.arc(0, r * .15, r * .18, .2, Math.PI - .2); ctx.stroke();
  ctx.restore();
  if (pop > .3) { ctx.strokeStyle = '#6B3E1A'; ctx.lineWidth = 6; for (let i = 0; i < 6; i++) { const a = -Math.PI / 2 + (i - 2.5) * .35; ctx.beginPath(); ctx.moveTo(bx + Math.cos(a) * bw * .7, by - bh + Math.sin(a) * bw * .5); ctx.lineTo(bx + Math.cos(a) * bw * (.9 + pop * .2), by - bh + Math.sin(a) * bw * (.7 + pop * .2)); ctx.stroke(); } }
}
// generic short-video chrome: icons on the right, progress bar
function chrome(w, h, t, prog) {
  ctx.fillStyle = 'rgba(255,255,255,.92)';
  const ix = w - 70;
  // heart
  ctx.save(); ctx.translate(ix, h * .52); ctx.beginPath(); ctx.moveTo(0, 14); ctx.bezierCurveTo(-34, -10, -16, -34, 0, -16); ctx.bezierCurveTo(16, -34, 34, -10, 0, 14); ctx.fill(); ctx.restore();
  // bubble
  ctx.beginPath(); ctx.ellipse(ix, h * .61, 26, 22, 0, 0, TAU); ctx.fill(); ctx.beginPath(); ctx.moveTo(ix - 10, h * .61 + 18); ctx.lineTo(ix - 18, h * .61 + 34); ctx.lineTo(ix + 2, h * .61 + 20); ctx.fill();
  // share arrow
  ctx.save(); ctx.translate(ix, h * .70); ctx.beginPath(); ctx.moveTo(-22, 16); ctx.quadraticCurveTo(-18, -10, 8, -10); ctx.lineTo(8, -22); ctx.lineTo(28, 0); ctx.lineTo(8, 22); ctx.lineTo(8, 8); ctx.quadraticCurveTo(-10, 6, -22, 16); ctx.fill(); ctx.restore();
  // progress
  ctx.fillStyle = 'rgba(255,255,255,.3)'; ctx.fillRect(0, h - 10, w, 10); ctx.fillStyle = '#FFFFFF'; ctx.fillRect(0, h - 10, w * prog, 10);
}
// thumbnails for the queue and the wall: a colour field and one simple, generic subject
const THEMES = [['#3B6FD8', '#7FB0FF', 'ball'], ['#D85A8A', '#FFB0C8', 'bowl'], ['#2F9E7A', '#8FE0C0', 'hill'], ['#8A5AD8', '#C9A8FF', 'note'], ['#D8843B', '#FFC98F', 'sun'], ['#3BA9C8', '#9FE6F5', 'wave'], ['#C84A4A', '#FF9F9F', 'car'], ['#5A6AD8', '#B0BAFF', 'cat']];
function thumb(w, h, k, o = {}) {
  const [a, b, kind] = THEMES[k % THEMES.length];
  const g = ctx.createLinearGradient(0, 0, w, h); g.addColorStop(0, a); g.addColorStop(1, b); ctx.fillStyle = g; rr(0, 0, w, h, w * .06); ctx.fill();
  ctx.fillStyle = 'rgba(255,255,255,.88)'; ctx.strokeStyle = 'rgba(255,255,255,.88)'; ctx.lineWidth = w * .03; const cx = w / 2, cy = h * .45, r = w * .2;
  ctx.beginPath();
  if (kind === 'ball') { ctx.arc(cx, cy, r, 0, TAU); ctx.fill(); }
  else if (kind === 'bowl') { ctx.arc(cx, cy, r, 0, Math.PI); ctx.fill(); }
  else if (kind === 'hill') { ctx.moveTo(cx - r * 1.4, cy + r); ctx.lineTo(cx - r * .2, cy - r); ctx.lineTo(cx + r * .4, cy); ctx.lineTo(cx + r * .8, cy - r * .5); ctx.lineTo(cx + r * 1.4, cy + r); ctx.fill(); }
  else if (kind === 'note') { ctx.arc(cx - r * .3, cy + r * .5, r * .35, 0, TAU); ctx.fill(); ctx.fillRect(cx - r * .05, cy - r, r * .15, r * 1.5); }
  else if (kind === 'sun') { ctx.arc(cx, cy, r * .6, 0, TAU); ctx.fill(); for (let i = 0; i < 8; i++) { const an = i / 8 * TAU; ctx.beginPath(); ctx.moveTo(cx + Math.cos(an) * r * .8, cy + Math.sin(an) * r * .8); ctx.lineTo(cx + Math.cos(an) * r * 1.2, cy + Math.sin(an) * r * 1.2); ctx.stroke(); } }
  else if (kind === 'wave') { ctx.moveTo(cx - r * 1.4, cy); for (let i = 0; i <= 20; i++) ctx.lineTo(cx - r * 1.4 + i * r * .14, cy + Math.sin(i * .9) * r * .4); ctx.stroke(); }
  else if (kind === 'car') { ctx.fillRect(cx - r, cy - r * .2, r * 2, r * .6); ctx.fillRect(cx - r * .5, cy - r * .6, r, r * .5); }
  else { ctx.ellipse(cx, cy, r, r * .8, 0, 0, TAU); ctx.fill(); }
  if (o.bar !== undefined) { ctx.fillStyle = 'rgba(8,11,22,.55)'; ctx.fillRect(w * .08, h * .88, w * .84, h * .035); ctx.fillStyle = AMB; ctx.fillRect(w * .08, h * .88, w * .84 * o.bar, h * .035); }
}

// ------------------------------------------------------------------ the amber signal: the only thing that glows
function signal(x, y, r, trail = []) {
  for (let i = 0; i < trail.length - 1; i++) { ctx.strokeStyle = `rgba(255,178,62,${(i / trail.length) * .8})`; ctx.lineWidth = r * (i / trail.length) * 1.1; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(...trail[i]); ctx.lineTo(...trail[i + 1]); ctx.stroke(); }
  const g = ctx.createRadialGradient(x, y, 0, x, y, r * 3); g.addColorStop(0, 'rgba(255,214,140,1)'); g.addColorStop(.3, 'rgba(255,178,62,.7)'); g.addColorStop(1, 'rgba(255,178,62,0)');
  ctx.fillStyle = g; ctx.fillRect(x - r * 3, y - r * 3, r * 6, r * 6); ctx.fillStyle = '#FFF4DE'; ctx.beginPath(); ctx.arc(x, y, r * .45, 0, TAU); ctx.fill();
}

// ------------------------------------------------------------------ S0 · in bed with the phone (first person)
const BOKEH = (() => { const r = mulberry32(3), a = []; for (let i = 0; i < 40; i++) a.push([r() * W, r() * H * .55, 8 + r() * 40, r() < .7 ? '255,190,120' : '150,180,255', r()]); return a; })();
const PHONE = { w: 7.2, h: 15.6 };      // world units ≈ cm; the phone sits at z = 0
const SCREEN = { w: 6.6, h: 14.4 };
function bedroom(t) {
  const g = ctx.createLinearGradient(0, 0, 0, H); g.addColorStop(0, '#0B1124'); g.addColorStop(1, '#141A2E'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  for (const [x, y, r, c, s] of BOKEH) { const dx = (CX * 6) % 1, px = x - CX * 40, py = y + CY * 30 + Math.sin(t * .3 + s * 6) * 4; ctx.fillStyle = `rgba(${c},${.08 + .1 * s})`; ctx.beginPath(); ctx.arc(px, py, r, 0, TAU); ctx.fill(); void dx; }
  // the blanket
  ctx.fillStyle = '#20283F'; ctx.beginPath(); ctx.moveTo(0, H * .78); ctx.bezierCurveTo(W * .3, H * .74, W * .6, H * .8, W, H * .76); ctx.lineTo(W, H); ctx.lineTo(0, H); ctx.fill();
  ctx.strokeStyle = 'rgba(255,255,255,.05)'; ctx.lineWidth = 3; for (let i = 0; i < 5; i++) { ctx.beginPath(); ctx.moveTo(0, H * (.82 + i * .035)); ctx.bezierCurveTo(W * .3, H * (.8 + i * .035), W * .6, H * (.84 + i * .035), W, H * (.8 + i * .035)); ctx.stroke(); }
}
function phoneAt(t, o = {}) {
  // screen light on the room
  const p = P(0, 0, 0); if (!p) return;
  const s = p[2], gl = ctx.createRadialGradient(p[0], p[1], 0, p[0], p[1], 14 * s); gl.addColorStop(0, 'rgba(255,220,170,.16)'); gl.addColorStop(1, 'rgba(255,220,170,0)'); ctx.fillStyle = gl; ctx.fillRect(p[0] - 14 * s, p[1] - 14 * s, 28 * s, 28 * s);
  card(0, 0, 0, PHONE.w, PHONE.h, (w, h) => { ctx.fillStyle = '#0D0F16'; rr(0, 0, w, h, 1.0); ctx.fill(); ctx.strokeStyle = '#3A4058'; ctx.lineWidth = .08; ctx.stroke(); });
  // the screen content is drawn at pixel resolution
  card(0, 0, -.01, SCREEN.w, SCREEN.h, (w, h, sc) => {
    ctx.save(); rr(0, 0, w, h, .7); ctx.clip(); ctx.scale(1 / 100, 1 / 100);
    catGag(w * 100, h * 100, t); chrome(w * 100, h * 100, t, o.prog ?? ((t * .09) % 1));
    if (o.watch) { ctx.font = `700 40px ${UI}`; ctx.fillStyle = 'rgba(8,11,22,.65)'; ctx.fillRect(30, 40, 300, 66); ctx.fillStyle = AMB; ctx.textBaseline = 'middle'; ctx.textAlign = 'left'; ctx.fillText(o.watch, 48, 74); }
    ctx.restore();
  });
}
function hand(t, lift) {      // your thumb comes up from the lower right and hovers, about to swipe
  const p = P(2.2 + (1 - lift) * 1.5, -9.5 + lift * 5.2, -.4); if (!p) return; const s = p[2];
  ctx.save(); ctx.translate(p[0], p[1]); ctx.rotate(-.35 + lift * .15); ctx.scale(s, s);
  const g = ctx.createLinearGradient(-1.1, 0, 1.1, 0); g.addColorStop(0, '#B07F66'); g.addColorStop(1, '#D9A88C');
  ctx.fillStyle = g; rr(-1.05, -1.3, 2.1, 9, 1.05); ctx.fill();
  ctx.fillStyle = 'rgba(255,236,224,.55)'; rr(-.62, -1.05, 1.24, 1.5, .55); ctx.fill();      // the nail
  ctx.strokeStyle = 'rgba(120,80,60,.35)'; ctx.lineWidth = .05; ctx.beginPath(); ctx.moveTo(-.8, 1.4); ctx.quadraticCurveTo(0, 1.7, .8, 1.4); ctx.stroke();
  ctx.restore();
}

// ------------------------------------------------------------------ S1 · behind the screen: the queue of downloaded videos
const QZ = [0, 12, 24, 36];
function queueScene(t) {
  const g = ctx.createLinearGradient(0, 0, 0, H); g.addColorStop(0, '#0A0F1E'); g.addColorStop(1, '#101833'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  // depth grid on the floor
  ctx.strokeStyle = 'rgba(154,166,196,.12)'; ctx.lineWidth = 2; ctx.beginPath();
  for (let z = -10; z < 120; z += 6) { const a = P(-30, -12, z), b = P(30, -12, z); if (a && b) { ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); } }
  for (let x = -30; x <= 30; x += 6) { const a = P(x, -12, -6), b = P(x, -12, 120); if (a && b) { ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); } }
  ctx.stroke();
  // the line that feeds the queue, running back into the dark
  const l0 = P(7.8, 1.5, QZ[3] + 2), l1 = P(0, 0, 400); if (l0 && l1) { ctx.strokeStyle = 'rgba(255,178,62,.6)'; ctx.lineWidth = 6; ctx.setLineDash([18, 14]); ctx.lineDashOffset = -t * 60; ctx.beginPath(); ctx.moveTo(l0[0], l0[1]); ctx.lineTo(l1[0], l1[1]); ctx.stroke(); ctx.setLineDash([]); }
  // cards, far to near
  for (let i = 3; i >= 0; i--) {
    const z = QZ[i], k = i === 0 ? 1 : ev(t, C.dl + i * .5, 1.0), bob = Math.sin(t * 1.3 + i) * .25;
    card(i === 0 ? 0 : i * 2.6, bob + i * .5, z, SCREEN.w, SCREEN.h, (w, h) => {
      if (i === 0) { ctx.save(); rr(0, 0, w, h, .7); ctx.clip(); ctx.scale(1 / 100, 1 / 100); catGag(w * 100, h * 100, t); chrome(w * 100, h * 100, t, (t * .09) % 1); ctx.restore(); }
      else { ctx.save(); ctx.scale(1 / 100, 1 / 100); thumb(w * 100, h * 100, i + 2, { bar: k }); ctx.restore(); }
      ctx.strokeStyle = i === 0 ? 'rgba(255,255,255,.4)' : (k >= 1 ? AMB : 'rgba(255,178,62,.5)'); ctx.lineWidth = .08; rr(0, 0, w, h, .7); ctx.stroke();
    });
    if (i > 0 && k >= 1 && t >= C.queue) { const p = P(i * 2.6 + SCREEN.w / 2, bob + i * .5 + SCREEN.h / 2, z); if (p) { ctx.font = `700 ${Math.max(26, 1.3 * p[2])}px ${UI}`; ctx.fillStyle = AMB; ctx.textAlign = 'left'; ctx.textBaseline = 'bottom'; ctx.fillText('已下载', p[0] + 6, p[1] - 6); } }
  }
}

// ------------------------------------------------------------------ S3 · out over the night city
const CITY = (() => { const r = mulberry32(17), b = []; for (let i = 0; i < 160; i++) b.push([(r() - .5) * 600, r() * 900 + 20, 20 + r() * 40, 30 + Math.pow(r(), 2) * 160, r()]); return b.sort((a, c) => c[1] - a[1]); })();
const DC = [40, 0, 980];      // the data centre, far away
function cityScene(t) {
  const g = ctx.createLinearGradient(0, 0, 0, H); g.addColorStop(0, '#060A16'); g.addColorStop(.6, '#0E1630'); g.addColorStop(1, '#1A2240'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  for (const [x, z, w, h, s] of CITY) {
    const a = P(x - w / 2, -120 + h, z), b = P(x + w / 2, -120, z); if (!a || !b) continue;
    ctx.fillStyle = `rgb(${18 + s * 10 | 0},${24 + s * 10 | 0},${44 + s * 14 | 0})`; ctx.fillRect(a[0], a[1], b[0] - a[0], b[1] - a[1]);
    const n = Math.floor(w / 6), m = Math.floor(h / 8);
    if (b[0] - a[0] > 6) for (let i = 0; i < n; i++) for (let j = 0; j < m; j++) { if (hash(i * 31 + j, x * 7 + z | 0) > .3) continue; const wx = lerp(a[0], b[0], (i + .3) / n), wy = lerp(b[1], a[1], (j + .3) / m); ctx.fillStyle = 'rgba(255,214,150,.65)'; ctx.fillRect(wx, wy, Math.max(1, (b[0] - a[0]) / n * .45), Math.max(1, (b[1] - a[1]) / m * .35)); }
  }
  // the data centre: a long low block with a lit roof line
  const a = P(DC[0] - 60, -120 + 50, DC[2]), b = P(DC[0] + 60, -120, DC[2]);
  if (a && b) { ctx.fillStyle = '#1C2646'; ctx.fillRect(a[0], a[1], b[0] - a[0], b[1] - a[1]); ctx.fillStyle = 'rgba(255,178,62,.6)'; ctx.fillRect(a[0], a[1], b[0] - a[0], Math.max(2, (b[1] - a[1]) * .04)); for (let i = 0; i < 12; i++) { ctx.fillStyle = (Math.floor(t * 4 + i) % 3) ? 'rgba(160,190,255,.7)' : 'rgba(255,178,62,.9)'; ctx.fillRect(lerp(a[0], b[0], (i + .5) / 12) - 2, lerp(a[1], b[1], .5), 4, 4); } }
}

// ------------------------------------------------------------------ S4 · the data centre: racks, then the wall of videos and the funnel
function dcScene(t) {
  ctx.fillStyle = '#070B16'; ctx.fillRect(0, 0, W, H);
  // floor and ceiling strips
  for (let z = 0; z < 320; z += 10) {
    const f0 = P(-8, -12, z), f1 = P(8, -12, z), f2 = P(8, -12, z + 10), f3 = P(-8, -12, z + 10);
    if (f0 && f1 && f2 && f3) { ctx.fillStyle = (z / 10) % 2 ? '#10172A' : '#0D1324'; ctx.beginPath(); ctx.moveTo(f0[0], f0[1]); ctx.lineTo(f1[0], f1[1]); ctx.lineTo(f2[0], f2[1]); ctx.lineTo(f3[0], f3[1]); ctx.fill(); }
    const c0 = P(-2, 12, z + 3), c1 = P(2, 12, z + 3), c2 = P(2, 12, z + 6), c3 = P(-2, 12, z + 6);
    if (c0 && c1 && c2 && c3) { ctx.fillStyle = 'rgba(190,210,255,.25)'; ctx.beginPath(); ctx.moveTo(c0[0], c0[1]); ctx.lineTo(c1[0], c1[1]); ctx.lineTo(c2[0], c2[1]); ctx.lineTo(c3[0], c3[1]); ctx.fill(); }
  }
  // racks on both walls, far to near, LEDs blinking
  for (let z = 310; z >= 0; z -= 10) for (const side of [-1, 1]) {
    const q = [P(side * 8, 11, z), P(side * 8, 11, z + 9), P(side * 8, -12, z + 9), P(side * 8, -12, z)]; if (q.some(v => !v)) continue;
    ctx.fillStyle = '#1A2340'; ctx.strokeStyle = '#2C3966'; ctx.lineWidth = Math.max(1, q[0][2] * .1);
    ctx.beginPath(); q.forEach((v, i) => i ? ctx.lineTo(v[0], v[1]) : ctx.moveTo(v[0], v[1])); ctx.closePath(); ctx.fill(); ctx.stroke();
    for (let j = 0; j < 14; j++) for (let k = 0; k < 3; k++) {
      const zz = z + 1.5 + k * 2.6, yy = 9.5 - j * 1.55, d = P(side * 8, yy, zz); if (!d) continue;
      const on = hash(z * 37 + j * 5 + k + (side > 0 ? 999 : 0), Math.floor(t * 4 + j * .3 + k)) > .45;
      ctx.fillStyle = on ? ((j + k) % 5 ? 'rgba(130,175,255,.95)' : 'rgba(255,178,62,.95)') : 'rgba(50,60,95,.8)';
      const r = Math.max(1.2, d[2] * .22); ctx.fillRect(d[0] - r, d[1] - r * .5, r * 2, r);
    }
  }
}
const WALL = { w: 3.0, h: 5.2, gap: .5 };
function wallScene(t) {
  ctx.fillStyle = '#080C18'; ctx.fillRect(0, 0, W, H);
  const z = 60, scroll = (t - C.dc) * 4, cw = WALL.w + WALL.gap, ch = WALL.h + WALL.gap;
  const pick = ease(ev(t, C.pick, 1.6));
  // visible range only
  const s = F / (z - CZ), halfW = W / 2 / s + cw, halfH = H / 2 / s + ch;
  for (let c = Math.floor((CX - halfW) / cw); c <= Math.ceil((CX + halfW) / cw); c++) for (let r = Math.floor((CY - halfH + scroll) / ch); r <= Math.ceil((CY + halfH + scroll) / ch); r++) {
    const x = c * cw, y = r * ch - scroll, idx = ((c * 7919 + r * 104729) >>> 0);
    const chosen = idx % 23 === 0 && Math.abs(x - CX) < 14 && Math.abs(y - CY) < 22;
    if (chosen && pick > 0) continue;
    const p = P(x, y, z); if (!p) continue; const w = WALL.w * p[2], h = WALL.h * p[2];
    ctx.globalAlpha = .45 + .35 * hash(idx, 3);
    if (w > 26) { ctx.save(); ctx.translate(p[0] - w / 2, p[1] - h / 2); ctx.scale(w / 100, w / 100); thumb(100, 100 * WALL.h / WALL.w, idx); ctx.restore(); }
    else { const th = THEMES[idx % THEMES.length]; ctx.fillStyle = th[idx % 2]; ctx.fillRect(p[0] - w / 2, p[1] - h / 2, w, h); }
    ctx.globalAlpha = 1;
  }
  // the funnel: an amber outline that sweeps down the wall and pulls a small batch toward you
  if (t >= C.pick - .3) {
    const k = ev(t, C.pick - .3, .5), fp = P(CX, CY + 6, z - 2), fq = P(CX, CY - 8, z - 2);
    if (fp && fq) { ctx.strokeStyle = AMB; ctx.lineWidth = 8; ctx.globalAlpha = k; ctx.beginPath(); ctx.moveTo(fp[0] - 9 * fp[2], fp[1]); ctx.lineTo(fp[0] + 9 * fp[2], fp[1]); ctx.lineTo(fq[0] + 1.5 * fq[2], fq[1]); ctx.lineTo(fq[0] - 1.5 * fq[2], fq[1]); ctx.closePath(); ctx.stroke(); ctx.globalAlpha = 1; }
  }
}
// the batch: six candidate cards, each gets four odds
const BATCH = [[-3.2, 4.4, 3, [23, 2, 0, 0], 40], [0, 4.4, 4, [65, 11, 4, 3], 40], [3.2, 4.4, 5, [54, 6, 1, 1], 40], [-4.45, -.4, 0, [72, 9, 2, 1], 26], [0, -.4, 1, [41, 4, 1, 0], 26], [4.45, -.4, 2, [88, 15, 3, 2], 26]];
const QL = [['看完', 'q1'], ['点赞', 'q2'], ['评论', 'q3'], ['分享', 'q4']];
function batchScene(t) {
  wallScene(t);
  ctx.fillStyle = 'rgba(8,12,24,.55)'; ctx.fillRect(0, 0, W, H);
  const pull = ease(ev(t, C.pick + .2, 1.6));
  BATCH.forEach(([bx, by, k, odds, zz], i) => {
    const z = lerp(60, zz, pull), x = lerp(bx * 2.4 + Math.sin(i) * 3, bx, pull), y = lerp(by * 2 + 4, by, pull);
    card(x + CX, y + CY, z, 4.2, 7.3, (w, h) => {
      if (zz > 30) ctx.globalAlpha = .55;
      ctx.save(); ctx.scale(1 / 100, 1 / 100); thumb(w * 100, h * 100, k); ctx.restore();
      ctx.strokeStyle = AMB; ctx.lineWidth = .06; rr(0, 0, w, h, .2); ctx.stroke();
      // the four odds (drawn at 1/100 scale so the type stays crisp)
      ctx.save(); ctx.scale(1 / 100, 1 / 100); const W1 = w * 100, H1 = h * 100;
      QL.forEach(([lab, cue], j) => {
        if (t < C[cue]) return;
        if (zz > 30) return;
        const kk = expoOut(ev(t, C[cue], .6)), v = odds[j] / 100, y0 = H1 * .44 + j * 92;
        ctx.fillStyle = 'rgba(8,11,22,.8)'; ctx.fillRect(10, y0 - 40, W1 - 20, 82);
        ctx.font = `700 44px ${UI}`; ctx.textBaseline = 'middle'; ctx.textAlign = 'left'; ctx.fillStyle = WHITE; ctx.fillText(lab, 26, y0 + 2);
        ctx.fillStyle = 'rgba(255,255,255,.18)'; ctx.fillRect(118, y0 - 12, W1 - 250, 26); ctx.fillStyle = AMB; ctx.fillRect(118, y0 - 12, (W1 - 250) * Math.max(.02, v) * kk, 26);
        ctx.textAlign = 'right'; ctx.fillStyle = WHITE; ctx.fillText(roll(String(odds[j]), t, C[cue], .5) + '%', W1 - 20, y0 + 2);
      });
      ctx.restore();
    });
  });
}

// ------------------------------------------------------------------ one shot: camera path + match-through cuts
function shot(t) {
  if (t < C.dive + .55) {      // S0: in bed → push into the screen until it fills the frame
    const p0 = ev(t, 0, C.dive), push = expoIn(ev(t, C.dive - .2, .75));
    CX = lerp(.8, 0, smooth(p0)) + .15 * Math.sin(t * .6); CY = lerp(-1.5, 0, smooth(p0)) + .1 * Math.sin(t * .8); F = 1000;
    CZ = lerp(-15.5, -12.5, ease(p0)) + push * 11.7;
    bedroom(t);
    const lift = smooth(ev(t, C.ask + .3, 1.2)) * (1 - smooth(ev(t, C.dive - .1, .3)));
    phoneAt(t, {}); hand(t, lift);
    return 'S0';
  }
  if (t < C.fly + .3) {      // S1/S2: behind the screen, the queue; then the watch-time signal leaves along the line
    const u = t - (C.dive + .55);
    CZ = lerp(-.85, -14, ease(ev(u, 0, 2.2))); CX = lerp(0, 6, smooth(ev(t, C.dl + .5, 4))) - 6 * smooth(ev(t, C.you, 1.2)); CY = lerp(0, 1.5, smooth(ev(t, C.dl, 3))) - 1.5 * smooth(ev(t, C.you, 1.2)); F = 1000;
    if (t >= C.who && t < C.you) { CZ += smooth(ev(t, C.who, 1.2)) * 20; CX += smooth(ev(t, C.who, 1.2)) * 2; }
    if (t >= C.you) CZ = lerp(CZ, -15, smooth(ev(t, C.you, 1)));
    queueScene(t);
    if (t >= C.secs - .3) {      // the watch-time counter on the current video
      const p = P(-SCREEN.w / 2 + .3, SCREEN.h / 2 - .6, -.02); const secs = 9 + Math.floor(Math.max(0, t - C.secs + .001));
      if (p) { ctx.font = `700 ${Math.round(.7 * p[2])}px ${UI}`; ctx.fillStyle = 'rgba(8,11,22,.75)'; const tw = ctx.measureText(`已看 ${secs} 秒`).width; ctx.fillRect(p[0] - 10, p[1] - .55 * p[2], tw + 20, 1.1 * p[2]); ctx.fillStyle = AMB; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.fillText(`已看 ${secs} 秒`, p[0], p[1]); }
    }
    if (t >= C.signal) {      // the signal peels off the counter and runs down the line, away from you
      const k = ev(t, C.signal, C.fly + .3 - C.signal), z = lerp(0, 300, expoIn(k)), y = lerp(SCREEN.h / 2 - .6, 0, smooth(k * 3)), x = lerp(-SCREEN.w / 2 + 1.5, 0, smooth(k * 3));
      const p = P(x, y, z); const tr = []; for (let i = 0; i < 10; i++) { const kk = Math.max(0, k - i * .015), q = P(lerp(-SCREEN.w / 2 + 1.5, 0, smooth(kk * 3)), lerp(SCREEN.h / 2 - .6, 0, smooth(kk * 3)), lerp(0, 300, expoIn(kk))); if (q) tr.unshift([q[0], q[1]]); }
      if (p) signal(p[0], p[1], Math.max(10, .9 * p[2]), tr);
    }
    return 'S1';
  }
  if (t < C.dc) {      // S3: the city at night; the signal streaks toward the data centre
    const k = ev(t, C.fly + .3, C.dc - C.fly - .3);
    CX = lerp(0, DC[0], ease(k)); CY = lerp(20, -50, ease(k)); CZ = lerp(-40, DC[2] - 120, ease(k)); F = 900;
    cityScene(t);
    const sx = lerp(0, DC[0], k), sy = lerp(40, -95, k), sz = lerp(CZ + 30, DC[2], expoIn(k * .9 + .1)); const p = P(sx, sy, sz);
    if (p) signal(p[0], p[1], 40, [[W / 2, H * .95], [p[0], p[1]]]);
    return 'S3';
  }
  if (t < C.sea) {      // S4: inside, down the corridor of racks
    const k = ev(t, C.dc, C.sea - C.dc); CX = 0; CY = 0; CZ = lerp(-20, 240, ease(k)); F = 900;
    dcScene(t); signal(W / 2, H / 2 - 40, 30, [[W / 2, H * .75], [W / 2, H / 2 - 40]]);
    return 'S4';
  }
  { // S5/S6: the wall of videos, the funnel, the batch and its odds
    const k = ev(t, C.sea, 2.5); CX = 2 * Math.sin(t * .2); CY = lerp(-30, 0, ease(k)); CZ = lerp(-30, 10, ease(k)) + 3 * smooth(ev(t, C.q, 2)); F = 1000;
    if (t < C.pick + .2) wallScene(t); else batchScene(t);
    return 'S5';
  }
}

// ------------------------------------------------------------------ the frame
const CLEAN = location.search.includes('clean');
function subtitles(t) { if (CLEAN) return; const c = CUES.subs.find(c => t >= c.t0 && t < c.t1); if (!c || t >= C.next - .2) return; subtitle(c.text); }
window.seek = function (t) {
  t = clamp(t, 0, DUR - 1 / FPS);
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over';
  const s = shot(t);
  // the title on the first frame, then the numbers each line is about
  if (t < C.dive) { ctx.fillStyle = 'rgba(8,11,22,.5)'; ctx.fillRect(0, 0, W, 360); hero(t, -1, [{ parts: [['你上划之前', WHITE]], size: 112 }, { parts: [['你按下去之后', MIST]], size: 36, ui: true }], 72, 230, { lh: 76 }); }
  if (s === 'S1') {
    if (t >= C.queue && t < C.who) hero(t, C.queue, [{ parts: [['已下载 ', WHITE], [roll('3', t, C.queue, .3), AMB], [' 条', AMB]], size: 120 }], 72, 330);
    if (t >= C.who && t < C.you) hero(t, C.who, [{ parts: [['谁挑的？', WHITE]], size: 120 }], 72, 330);
    if (t >= C.you && t < C.fly + .3) hero(t, C.you, [{ parts: [['是', WHITE], ['你', AMB], ['。', WHITE]], size: 140 }], 72, 340);
  }
  if (s === 'S3') hero(t, C.fly, [{ parts: [['飞回', WHITE], ['机房', AMB]], size: 120 }], 72, 330);
  if (s === 'S5' || s === 'S4') {
    if (t >= C.sea && t < C.pick) hero(t, C.sea, [{ parts: [['海量', WHITE]], size: 130 }], 72, 330);
    if (t >= C.pick && t < C.q) hero(t, C.pick, [{ parts: [['捞出', WHITE], ['一小批', AMB]], size: 120 }], 72, 330);
    if (t >= C.q) hero(t, C.q, [{ parts: [['算一道题', WHITE]], size: 110 }], 72, 330);
  }
  subtitles(t);
  return true;
};
window.DURATION = DUR; window.FPS = FPS;
window.ready = Promise.all([`700 54px ${UI}`, `900 84px ${DSP}`].map(f => document.fonts.load(f)));
