// 「你上划之前」· the whole film in cut paper (loaded after common.js + paper.js).
// One continuous shot. Worlds: the bedroom (S0, S12) · behind the screen, where the queue and later the paper data centre live
// (S1, S9–S11) · the night city (S3, S8b) · the data-centre corridor (S4, S8a) · the wall of videos (S5–S7).
// The only gold is your watch time: the thread, the beads, the counter, the minus you send back.
'use strict';
const SS = +((location.search.match(/ss=(\d)/) || [])[1] || 1);
if (SS > 1) { cv.width = W * SS; cv.height = H * SS; ctx = cv.getContext('2d'); }
function shOn(blur, dx, dy, a = .45) { ctx.shadowColor = `rgba(3,5,14,${a})`; ctx.shadowBlur = blur * SS; ctx.shadowOffsetX = dx * SS; ctx.shadowOffsetY = dy * SS; }

// ------------------------------------------------------------------ small tools
const bez3 = (A, B, D, u) => [0, 1, 2].map(i => (1 - u) * (1 - u) * A[i] + 2 * (1 - u) * u * B[i] + u * u * D[i]);
function kf(t, keys, e = ease) {      // camera keyframes [[t, cx, cy, cz], …]
  if (t <= keys[0][0]) return keys[0].slice(1);
  for (let i = 1; i < keys.length; i++) if (t < keys[i][0]) { const a = keys[i - 1], b = keys[i], k = e((t - a[0]) / (b[0] - a[0])); return [lerp(a[1], b[1], k), lerp(a[2], b[2], k), lerp(a[3], b[3], k)]; }
  return keys[keys.length - 1].slice(1);
}
function tag(x, y, txt, sz, o = {}) {      // a small paper tag; ink tag + gold type for your watch time
  ctx.font = `700 ${sz}px ${PSANS}`; const w = ctx.measureText(txt).width;
  ctx.save(); ctx.translate(x, y); ctx.rotate(o.rot ?? -.03);
  shOn(sz * .4, sz * .12, sz * .2, .45); ctx.fillStyle = o.bg ?? PP.kraft; poly(jag(rectPts(0, -sz * .72, w + sz * .9, sz * 1.44), o.seed ?? 7, sz * .05, sz * .5)); ctx.fill(); shOff();
  ctx.fillStyle = o.fg ?? PP.ink; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.fillText(txt, sz * .45, sz * .04); ctx.restore();
  return w + sz * .9;
}
function bead(x, y, r) {      // the signal: a gold bead (paper has no glow; it has a shadow and a highlight)
  shOn(r * .8, r * .25, r * .4, .5); const g = ctx.createRadialGradient(x - r * .3, y - r * .35, r * .1, x, y, r); g.addColorStop(0, PP.goldL); g.addColorStop(.5, PP.gold); g.addColorStop(1, PP.goldD);
  ctx.fillStyle = g; ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.fill(); shOff();
}
function signal(x, y, r, trail = []) { if (trail.length > 1) thread(trail.length > 2 ? trail : [trail[0], [(trail[0][0] + x) / 2, (trail[0][1] + y) / 2], [x, y]], Math.max(4, r * .35), 0); bead(x, y, r * .7); }

// ------------------------------------------------------------------ the videos (what each card plays)
function paperLoop(w, h, t, k) {
  ctx.fillStyle = PTH[k % PTH.length]; ctx.fillRect(0, 0, w, h);
  ctx.fillStyle = 'rgba(255,255,255,.12)'; ctx.beginPath(); ctx.arc(w * .2, h * .2, w * .3, 0, TAU); ctx.fill();
  ctx.save(); ctx.translate(w * .1, h * .25 + Math.sin(t * 2.2 + k) * h * .02); paperThumb(w * .8, w * 1.1, k, 900 + k); ctx.restore();
}
function paperHills(w, h, t) {
  const g = ctx.createLinearGradient(0, 0, 0, h); g.addColorStop(0, '#B9D6EE'); g.addColorStop(1, '#F7DCB6'); ctx.fillStyle = g; ctx.fillRect(0, 0, w, h);
  shOn(14, 4, 8, .25); ctx.fillStyle = '#FCF1D6'; ctx.beginPath(); ctx.arc(w * .68, h * .28 + Math.sin(t * .8) * 10, w * .13, 0, TAU); ctx.fill(); shOff();
  ctx.strokeStyle = PP.ink; ctx.lineWidth = 6; ctx.lineCap = 'round';
  for (let i = 0; i < 3; i++) { const u = (t * .12 + i * .27) % 1, bx = lerp(-80, w + 80, u), by = h * (.16 + i * .05) + Math.sin(t * 2 + i) * 12, fl = Math.sin(t * 9 + i * 2) * 14; ctx.beginPath(); ctx.moveTo(bx - 28, by - fl); ctx.lineTo(bx, by); ctx.lineTo(bx + 28, by - fl); ctx.stroke(); }
  [['#86BE9F', .44, 1], ['#549D7B', .56, 2], ['#2E7859', .7, 3]].forEach(([col, y0, sd]) => {
    const r = mulberry32(sd * 13), pts = [[-20, h + 20]]; for (let i = 0; i <= 7; i++) pts.push([-20 + i * (w + 40) / 7, h * y0 + (i % 2 ? -1 : 1) * h * (.04 + r() * .05)]); pts.push([w + 20, h + 20]);
    shOn(18, 0, -8, .3); ctx.fillStyle = col; poly(jag(pts, sd, 4, 50)); ctx.fill(); shOff();
  });
}
function paperSunrise(w, h, t) {
  const g = ctx.createLinearGradient(0, 0, 0, h); g.addColorStop(0, '#F2A37A'); g.addColorStop(.6, '#F8D3A8'); ctx.fillStyle = g; ctx.fillRect(0, 0, w, h);
  const sy = h * clamp(.62 - .025 * (t - 46), .3, .62);
  shOn(20, 0, 10, .25); ctx.fillStyle = '#FFE7B0'; poly(jag(Array.from({ length: 20 }, (_, i) => [w * .5 + Math.cos(i / 20 * TAU) * w * .2, sy + Math.sin(i / 20 * TAU) * w * .2]), 77, 3, 30)); ctx.fill(); shOff();
  [['#5C86C4', .6, 1], ['#3F68A8', .7, 2], ['#2B4E88', .82, 3]].forEach(([col, y0, sd]) => {
    const pts = [[-20, h + 20]]; for (let x = -20; x <= w + 20; x += 40) pts.push([x, h * y0 + Math.sin(x * .02 + t * (1 + sd * .3) + sd) * 14]); pts.push([w + 20, h + 20]);
    shOn(14, 0, -6, .3); ctx.fillStyle = col; poly(pts); ctx.fill(); shOff();
  });
  ctx.fillStyle = 'rgba(255,240,210,.8)'; for (let i = 0; i < 8; i++) { const x = w * (.3 + .4 * hash(i, 3)) + Math.sin(t * 2 + i) * 10, y = h * (.64 + .1 * hash(i, 4)); ctx.fillRect(x, y, 40 + 20 * hash(i, 5), 6); }
}
const GREY = '#8E949D';
function paperRain(w, h, t) {
  const g = ctx.createLinearGradient(0, 0, 0, h); g.addColorStop(0, '#A9AEB6'); g.addColorStop(1, '#8B9098'); ctx.fillStyle = g; ctx.fillRect(0, 0, w, h);
  shOn(10, 0, -4, .25); ctx.fillStyle = '#727881'; poly(jag([[-20, h], [-20, h * .55], [w * .3, h * .55], [w * .3, h * .45], [w * .6, h * .45], [w * .6, h * .6], [w + 20, h * .6], [w + 20, h]], 31, 3, 40)); ctx.fill(); shOff();
  ctx.strokeStyle = 'rgba(230,234,240,.55)'; ctx.lineWidth = 4; ctx.beginPath();
  for (let i = 0; i < 46; i++) { const x = (hash(i, 1) * w * 1.2 + t * 60) % (w * 1.2) - w * .1, y = (hash(i, 2) * h + t * 900 * (.8 + .4 * hash(i, 3))) % h; ctx.moveTo(x, y); ctx.lineTo(x - 12, y + 50); }
  ctx.stroke();
}
function greyThumb(w, h, seed) {
  ctx.fillStyle = GREY; poly(w > 40 ? jag(rectPts(0, 0, w, h), seed, w * .012, w * .3) : rectPts(0, 0, w, h)); ctx.fill();
  if (w < 14) return; ctx.fillStyle = '#C9CDD3'; ctx.beginPath(); ctx.arc(w * .4, h * .42, w * .14, 0, TAU); ctx.arc(w * .58, h * .4, w * .17, 0, TAU); ctx.rect(w * .3, h * .42, w * .42, w * .14); ctx.fill();
  ctx.strokeStyle = '#C9CDD3'; ctx.lineWidth = w * .03; ctx.beginPath(); for (let i = 0; i < 4; i++) { ctx.moveTo(w * (.32 + i * .1), h * .55); ctx.lineTo(w * (.29 + i * .1), h * .63); } ctx.stroke();
}
// a video = { k: theme | 'g' (grey), c: content }
const V = { cat: { k: 7, c: 'cat' }, hills: { k: 2, c: 'hills' }, sun: { k: 4, c: 'sunrise' }, grey: { k: 'g', c: 'rain' } };
const vk = k => (k === 'g' ? V.grey : k === 2 ? V.hills : k === 4 ? V.sun : { k, c: 'loop' });
function vidContent(w, h, t, v) {
  if (v.c === 'cat') paperCat(w, h, t); else if (v.c === 'hills') paperHills(w, h, t); else if (v.c === 'sunrise') paperSunrise(w, h, t);
  else if (v.c === 'rain') paperRain(w, h, t); else paperLoop(w, h, t, v.k);
}
function vidThumb(w, h, v, seed) { if (v.k === 'g') greyThumb(w, h, seed); else paperThumb(w, h, v.k, seed); }

// ------------------------------------------------------------------ the bedroom: the phone can now play any video
function phoneAt(t, o = {}) {
  card(0, 0, 0, PHONE.w, PHONE.h, (w, h) => { shOn(40, 18, 30, .6); ctx.fillStyle = '#15141B'; rr(0, 0, w, h, 1.0); ctx.fill(); shOff(); ctx.fillStyle = '#24232C'; rr(.1, .1, w - .2, h - .2, .92); ctx.fill(); });
  card(0, 0, -.01, SCREEN.w, SCREEN.h, (w, h) => { ctx.save(); rr(0, 0, w, h, .7); ctx.clip(); ctx.scale(1 / 100, 1 / 100); vidContent(w * 100, h * 100, t, o.vid ?? V.cat); paperChrome(w * 100, h * 100, t, o.prog ?? ((t * .09) % 1)); ctx.restore(); });
}
// your thumb, drawn tip-first in centimetres: a rounded, slightly tapered thumb (≈1.5 cm at the tip, 2.2 at the base),
// a short nail, two knuckle creases; it runs on out of frame so its end is never seen
const THUMB = (() => { const o = []; for (let i = 0; i <= 12; i++) { const a = Math.PI + i / 12 * Math.PI; o.push([Math.cos(a) * .74, .74 + Math.sin(a) * .74]); }
  o.push([.84, 2.4], [.95, 3.7], [1.02, 4.5], [1.06, 6.2], [1.22, 9], [1.4, 14], [1.5, 28], [-1.2, 28], [-1.1, 14], [-1.0, 9], [-.94, 6.2], [-.9, 4.5], [-.85, 3.7], [-.79, 2.4]); return o; })();
const NAIL = (() => { const o = []; for (let i = 0; i <= 10; i++) { const a = Math.PI + i / 10 * Math.PI; o.push([Math.cos(a) * .5, .66 + Math.sin(a) * .5]); } o.push([.47, 1.55], [-.47, 1.55]); return o; })();
function thumbLocal() {
  shOn(22, 9, 15, .5); ctx.fillStyle = PP.skin; poly(jag(THUMB, 51, .03, .45)); ctx.fill(); shOff();
  ctx.save(); poly(THUMB); ctx.clip(); ctx.fillStyle = 'rgba(140,82,55,.2)'; ctx.beginPath(); ctx.moveTo(.75, 1.2); ctx.quadraticCurveTo(1.0, 8, 1.5, 28); ctx.lineTo(2, 28); ctx.lineTo(2, 0); ctx.closePath(); ctx.fill(); ctx.restore();
  shOn(5, 1.5, 3, .25); ctx.fillStyle = '#EFCDB5'; poly(jag(NAIL, 52, .015, .25)); ctx.fill(); shOff();
  ctx.fillStyle = 'rgba(255,245,235,.55)'; ctx.beginPath(); ctx.ellipse(-.12, .55, .2, .1, -.3, 0, TAU); ctx.fill();
  ctx.strokeStyle = 'rgba(140,85,58,.5)'; ctx.lineWidth = .06; ctx.lineCap = 'round';
  ctx.beginPath(); ctx.moveTo(-.5, 3.5); ctx.quadraticCurveTo(0, 3.72, .52, 3.5); ctx.moveTo(-.32, 3.78); ctx.quadraticCurveTo(0, 3.92, .34, 3.78); ctx.stroke();
}
function thumbAt(x, y, z, rot = -.35, press = 0) {      // your thumb, tip at (x, y, z)
  const p = P(x, y, z); if (!p) return; const s = p[2];
  if (press > 0) { ctx.strokeStyle = `rgba(241,232,213,${.8 * (1 - press * .5)})`; ctx.lineWidth = Math.max(3, .1 * s); ctx.beginPath(); ctx.arc(p[0], p[1], (.5 + press * 1.2) * s, 0, TAU); ctx.stroke(); }
  ctx.save(); ctx.translate(p[0], p[1]); ctx.rotate(rot); ctx.scale(s, s); thumbLocal(); ctx.restore();
}
function hand(t, lift) { const rot = -.35 + lift * .15; thumbAt(2.2 + (1 - lift) * 1.5 + 1.3 * Math.sin(rot), -9.5 + lift * 5.2 + 1.3 * Math.cos(rot), -.4, rot); }

// ------------------------------------------------------------------ behind the screen: the night, the far city, the queue, later the data centre
const SKY = (() => { const r = mulberry32(91), out = []; for (const [z, col, n, hmax] of [[150, '#212C52', 46, 34], [95, '#26335E', 34, 26]]) for (let i = 0; i < n; i++) { const x = -160 + i * 380 / n + (r() - .5) * 4, w = 380 / n * (.8 + r() * .5), h = 6 + r() * hmax; out.push({ x, z, w, h, col, s: r() }); } return out; })();
function insideBg(t) {
  ctx.fillStyle = PP.night; ctx.fillRect(0, 0, W, H);
  for (let i = 0; i < 40; i++) { const p = P(-200 + hash(i, 1) * 420, -10 + hash(i, 2) * 160, 420); if (!p) continue; ctx.fillStyle = 'rgba(241,232,213,.7)'; star(p[0], p[1] + Math.sin(t + i) * 2, 3 + hash(i, 3) * 5); ctx.fill(); }
  const m = P(60, 70, 400); if (m) { shOn(20, 6, 10, .5); ctx.fillStyle = PP.cream; ctx.beginPath(); ctx.arc(m[0], m[1], 5 * m[2], 0, TAU); ctx.fill(); shOff(); }
  for (const b of SKY) {
    const a = P(b.x, -18 + b.h, b.z), c = P(b.x + b.w, -80, b.z); if (!a || !c || c[0] < -50 || a[0] > W + 50) continue;
    ctx.fillStyle = 'rgba(3,5,14,.4)'; ctx.fillRect(a[0] + 5, a[1] + 8, c[0] - a[0], c[1] - a[1]);
    ctx.fillStyle = b.col; poly(jag(rectPts(a[0], a[1], c[0] - a[0], c[1] - a[1]), (b.x * 10) | 0, 1.5, 30)); ctx.fill();
    const n = Math.max(1, Math.floor(b.w / 1.6)), mm = Math.floor(b.h / 2.4);
    for (let i = 0; i < n; i++) for (let j = 0; j < mm; j++) { if (hash(i * 31 + j, (b.x * 10) | 0) > .25) continue; const q = P(b.x + (i + .35) * b.w / n, -18 + b.h - (j + .6) * 2.4, b.z); if (q) { ctx.fillStyle = 'rgba(244,214,150,.55)'; ctx.fillRect(q[0], q[1], .5 * q[2], .7 * q[2]); } }
  }
}
// the queue: cards at slot s (0 = the screen itself)
const SLOT = s => [s * 3.3, s * .55, s * 12];
function queueCard(x, y, z, w, h, v, t, o = {}) {
  return card(x, y, z, w, h, (W1, H1) => {
    ctx.save(); ctx.translate(W1 / 2, H1 / 2); ctx.rotate(o.rot ?? 0); ctx.translate(-W1 / 2, -H1 / 2); ctx.globalAlpha = o.a ?? 1;
    shOn(30, 12, 22, .55); ctx.fillStyle = PP.cream; poly(jag(rectPts(0, 0, W1, H1), o.seed ?? 3, .06, .9)); ctx.fill(); shOff();
    ctx.save(); ctx.translate(.25, .25); ctx.beginPath(); ctx.rect(0, 0, W1 - .5, H1 - 1.6); ctx.clip(); ctx.scale(1 / 100, 1 / 100); vidContent((W1 - .5) * 100, (H1 - 1.6) * 100, o.frame ?? 1.3, v); ctx.restore();
    if (o.bar !== undefined) { ctx.fillStyle = 'rgba(30,28,39,.18)'; ctx.fillRect(.4, H1 - 1.0, W1 - .8, .42); ctx.fillStyle = PP.kraft; poly(jag(rectPts(.4, H1 - 1.0, Math.max(.05, (W1 - .8) * o.bar), .42), 61, .03, .3)); ctx.fill(); }
    ctx.restore();
  });
}
function dashedSlot(s, a) { const [x, y, z] = SLOT(s); card(x, y, z, SCREEN.w, SCREEN.h, (w, h) => { ctx.globalAlpha = a; ctx.setLineDash([.5, .35]); ctx.strokeStyle = 'rgba(241,232,213,.55)'; ctx.lineWidth = .1; rr(0, 0, w, h, .5); ctx.stroke(); ctx.setLineDash([]); }); }
function phoneBody(t) {      // the phone seen from inside: black paper frame around the screen
  card(0, 0, .03, PHONE.w, PHONE.h, (w, h) => { shOn(40, 18, 30, .6); ctx.fillStyle = '#15141B'; rr(0, 0, w, h, 1.0); ctx.fill(); shOff(); });
}
function screenAt(t, v, o = {}) {      // the current video on the screen; o.out = outgoing video sliding away (u)
  card(0, 0, 0, SCREEN.w, SCREEN.h, (w, h) => {
    ctx.save(); rr(0, 0, w, h, .7); ctx.clip(); ctx.scale(1 / 100, 1 / 100); const W1 = w * 100, H1 = h * 100;
    vidContent(W1, H1, t, v);
    if (o.out && o.u < 1) {
      if (o.mode === 'fold') { const k = ease(o.u); ctx.save(); ctx.translate(W1 / 2, H1 / 2); ctx.rotate(k * .5); ctx.scale(1 - k, 1 - k); ctx.translate(-W1 / 2, -H1 / 2); vidContent(W1, H1, t, o.out); ctx.restore(); }
      else { ctx.save(); ctx.translate(0, -ease(o.u) * H1); vidContent(W1, H1, t, o.out); ctx.restore(); }
    }
    paperChrome(W1, H1, t, o.prog ?? ((t * .09) % 1));
    if (o.watch) { ctx.font = `700 64px ${PSANS}`; const tw = ctx.measureText(o.watch).width; shOn(10, 3, 6, .4); ctx.fillStyle = '#17161E'; poly(jag(rectPts(36, 50, tw + 56, 100), 71, 3, 20)); ctx.fill(); shOff(); ctx.fillStyle = PP.gold; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.fillText(o.watch, 64, 102); }
    if (o.menu > 0) {      // the long-press menu
      const k = expoOut(o.menu), y0 = H1 - k * 520;
      shOn(30, 0, -10, .5); ctx.fillStyle = PP.cream; poly(jag(rectPts(30, y0, W1 - 60, 470), 81, 4, 30)); ctx.fill(); shOff();
      ctx.font = `700 76px ${PSANS}`; ctx.textAlign = 'left'; ctx.textBaseline = 'middle';
      [['不感兴趣', true], ['倍速播放', false], ['清屏播放', false]].forEach(([s, hi], j) => {
        const yy = y0 + 90 + j * 140; if (hi) { ctx.strokeStyle = PP.gold; ctx.lineWidth = 12; ctx.strokeRect(54, yy - 58, W1 - 108, 116); }
        ctx.fillStyle = hi ? PP.ink : 'rgba(30,28,39,.45)'; ctx.fillText((hi ? '−  ' : '    ') + s, 90, yy);
      });
    }
    ctx.restore();
  });
}

// the queue over the film: every card's life (k, arrival, moves between slots, drop)
// arr: [t0, t1, from, s] ; from = 'line' (down the thread from far away) | 'arc' (from the data centre) | 'front' (the cards you just saw sent back)
// mv: [t0, t1, s0, s1] ; a move to s = 0 means it becomes the screen ; drop: it falls out of the queue
const QT = [
  { k: 2, arr: [34.05, 34.25, 'front', 1, 0], mv: [[C.swipe, C.swipe + .35, 1, 0]] },
  { k: 0, arr: [34.05, 34.5, 'front', 2, 1], mv: [[C.swipe + .08, C.swipe + .5, 2, 1], [41.0, 41.25, 1, 0]] },
  { k: 1, arr: [34.05, 34.75, 'front', 3, 2], mv: [[C.swipe + .15, C.swipe + .6, 3, 2], [41.0, 41.3, 2, 1], [41.5, 41.75, 1, 0]] },
  { k: 5, arr: [35.4, 36.25, 'line', 3], mv: [[41.0, 41.35, 3, 2], [41.5, 41.8, 2, 1], [42.0, 42.25, 1, 0]] },
  { k: 'g', arr: [41.05, 41.6, 'arc', 3], mv: [[41.5, 41.85, 3, 2], [42.0, 42.3, 2, 1], [44.0, 44.25, 1, 0]] },
  { k: 4, arr: [41.55, 42.1, 'arc', 3], mv: [[42.0, 42.35, 3, 2], [44.0, 44.3, 2, 1], [46.5, 46.85, 1, 0, 'fold']] },
  { k: 3, arr: [42.05, 42.6, 'arc', 3], mv: [[44.0, 44.35, 3, 2]], drop: 45.0 },
  { k: 6, arr: [44.05, 44.5, 'arc', 3], drop: 45.5 },
  { k: 'g', arr: [45.0, 45.5, 'arc', 2], mv: [[46.5, 46.9, 2, 1]], drop: 47.5 },
  { k: 'g', arr: [45.5, 46.0, 'arc', 3], mv: [[46.55, 46.95, 3, 2]], drop: 47.75 },
  { k: 0, arr: [47.75, 48.25, 'arc', 1] }, { k: 2, arr: [48.0, 48.5, 'arc', 2] }, { k: 1, arr: [48.25, 48.75, 'arc', 3] },
];
const ARC_U = [[3.7, 5, -.3], [7.6, 13, 1.5], [11.6, 7, 3.6]];      // phone → data centre (your seconds go up)
const arcL = s => [[11.6, -6, 3.6], [11, -16, 8 + s * 6], SLOT(s)];      // data centre → the queue (the picks come down)
function screenNow(t) {      // which video is on the screen, and the one leaving
  let cur = V.cat, out = null, u = 1, mode = 'slide';
  for (const q of QT) for (const m of q.mv ?? []) if (m[3] === 0 && t >= m[0]) { if (t >= m[1]) { cur = vk(q.k); out = null; } else { out = cur; cur = vk(q.k); u = (t - m[0]) / (m[1] - m[0]); mode = m[4] ?? 'slide'; } }
  return { cur, out, u, mode };
}
function drawQueue(t, o = {}) {
  const list = [];
  QT.forEach((q, n) => {
    const [a0, a1, from, s0, fi] = q.arr; if (t < a0) return; let s = s0, pos = null, sz = 1, rot = 0, alpha = 1;
    for (const m of q.mv ?? []) if (t >= m[0]) s = t >= m[1] ? m[3] : lerp(m[2], m[3], ease((t - m[0]) / (m[1] - m[0])));
    if (q.mv && q.mv.some(m => m[3] === 0 && t >= m[1])) return;      // it is the screen now
    if (s < .02) return;
    let [x, y, z] = SLOT(s);
    if (t < a1) {
      const k = ease((t - a0) / (a1 - a0));
      if (from === 'line') { const L = [7.8 + 4, 1.5 + 2, 400]; x = lerp(L[0], x, k); y = lerp(L[1], y, k); z = lerp(L[2], z, expoOut(k)); }
      else if (from === 'arc') { [x, y, z] = bez3(...arcL(s0), k); sz = lerp(.35, 1, k); rot = (1 - k) * .6; }
      else { const st = o.front?.[fi]; if (st) { x = lerp(st[0], x, k); y = lerp(st[1], y, k) + Math.sin(k * Math.PI) * 5; z = lerp(st[2], z, k); sz = lerp(.62, 1, k); rot = (1 - k) * (fi - 1) * .2; } }
    }
    if (q.drop !== undefined && t >= q.drop) { const k = ev(t, q.drop, .6); y -= 24 * k * k; rot += k * (n % 2 ? .8 : -.8); alpha = 1 - k; if (k >= 1) return; }
    const bar = from === 'line' ? ev(t, a1, .7) : 1;
    list.push({ x, y, z, v: vk(q.k), sz, rot, alpha, bar, n, landed: t >= a1 && (q.drop === undefined || t < q.drop) });
  });
  list.sort((a, b) => b.z - a.z);
  for (const c of list) {
    if ((c.z < .5) !== !!o.near) continue;
    const bob = Math.sin(t * 1.3 + c.n) * .2;
    queueCard(c.x, c.y + bob, c.z, SCREEN.w * c.sz, SCREEN.h * c.sz, c.v, t, { rot: c.rot, a: c.alpha, bar: c.bar, seed: 10 + c.n });
    if (o.tags && c.landed && c.bar >= 1) { const p = P(c.x + SCREEN.w / 2 - .2, c.y + bob + SCREEN.h / 2, c.z); if (p) tag(p[0] - 10, p[1] + 4, '已下载', Math.max(22, Math.round(.9 * p[2])), { seed: c.n }); }
  }
}

// the data centre, a pop-up paper building that stands up beside your phone
const BLD = { x: 17, y: 1, z: 4, w: 11, h: 26 };
const FEED = { x0: 12.7, x1: 21.3, y0: -7.5, y1: 6.5 };
const YOU = ['停留 12 秒', '看完了', '划走 · 1 秒', '点了赞', '停留 8 秒', '看完了', '划走 · 2 秒', '停留 15 秒'];
function youCard(W1, H1, label, t, seed) {
  shOn(16, 4, 8, .4); ctx.fillStyle = PP.night2; poly(jag(rectPts(0, 0, W1, H1), seed, 3, 40)); ctx.fill(); shOff();
  // you, in bed, phone in hand (the opening shot, in miniature)
  ctx.fillStyle = '#C9CFE0'; ctx.beginPath(); ctx.ellipse(W1 * .17, H1 * .52, W1 * .06, H1 * .16, 0, 0, TAU); ctx.fill();
  ctx.fillStyle = '#4560A0'; poly([[0, H1], [0, H1 * .62], [W1 * .1, H1 * .58], [W1 * .25, H1 * .66], [W1 * .4, H1 * .6], [W1 * .4, H1]]); ctx.fill();
  ctx.fillStyle = '#15141B'; ctx.fillRect(W1 * .27, H1 * .2, W1 * .07, H1 * .36); ctx.fillStyle = '#F4D5A2'; ctx.fillRect(W1 * .282, H1 * .23, W1 * .046, H1 * .3);
  ctx.font = `700 ${Math.round(H1 * .26)}px ${PSANS}`; ctx.fillStyle = PP.gold; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.fillText(label, W1 * .43, H1 * .52);
}
function building(t, o) {
  const up = o.up; if (up <= 0) return;
  const base = P(BLD.x, BLD.y - BLD.h / 2, BLD.z); if (!base) return;
  ctx.save(); ctx.translate(base[0], base[1]); ctx.scale(1, Math.max(.001, up)); ctx.translate(-base[0], -base[1]);      // pops up from its base, like a page opening
  card(BLD.x, BLD.y, BLD.z, BLD.w, BLD.h, (w, h) => {
    shOn(40, 16, 26, .6); ctx.fillStyle = PP.night3; poly(jag(rectPts(0, 0, w, h), 201, .08, 1.2)); ctx.fill(); shOff();
    ctx.fillStyle = PP.night2; poly(jag(rectPts(-.4, -.6, w + .8, 1.2), 202, .06, 1)); ctx.fill();      // the roof
    for (let i = 0; i < 3; i++) { ctx.fillStyle = '#3B4F86'; ctx.beginPath(); ctx.arc(2 + i * 3.4, -.9, .8, Math.PI, 0); ctx.fill(); const a = t * 6 + i; ctx.strokeStyle = PP.night2; ctx.lineWidth = .12; ctx.beginPath(); ctx.moveTo(2 + i * 3.4, -.9); ctx.lineTo(2 + i * 3.4 + Math.cos(a) * .6, -.9 - Math.abs(Math.sin(a)) * .6); ctx.stroke(); }
    // windows: a small wall of videos; grey ones spread while you stare, then flip dark after your "no"
    for (let r = 0; r < 10; r++) for (let c = 0; c < 4; c++) {
      const id = r * 4 + c, x = .9 + c * 2.45, y = 1.2 + r * 2.4; if (o.open > 0 && x > 1 && x < 9.5 && y > 5.2 && y < 19.6) continue;
      const g = o.greyN > hash(id, 8) * 40, flip = g && o.flip > hash(id, 9);
      ctx.save(); ctx.translate(x, y); ctx.fillStyle = 'rgba(3,5,14,.45)'; ctx.fillRect(.12, .18, 1.9, 1.9);
      if (flip) { ctx.fillStyle = '#141A30'; ctx.fillRect(0, 0, 1.9, 1.9); }
      else { ctx.scale(1.9 / 100, 1.9 / 100); if (g) greyThumb(100, 100, id); else paperThumb(100, 100, (id * 7) % 8, id); ctx.fillStyle = 'rgba(18,24,50,.25)'; ctx.fillRect(0, 0, 100, 100); }
      ctx.restore();
    }
  });
  // the flap folds up and the feed of YOU scrolls inside
  if (o.open > 0) {
    const fx = (FEED.x0 + FEED.x1) / 2, fy = (FEED.y0 + FEED.y1) / 2, fw = FEED.x1 - FEED.x0, fh = FEED.y1 - FEED.y0;
    card(fx, fy, BLD.z - .02, fw, fh, (w, h) => {
      ctx.fillStyle = '#10152B'; ctx.fillRect(0, 0, w, h);
      ctx.save(); ctx.beginPath(); ctx.rect(0, 0, w, h); ctx.clip();
      const step = 3.4, sc = o.feed, n0 = Math.floor(sc);
      for (let i = -1; i < 5; i++) { const n = n0 + i, y = .4 + i * step - (sc - n0) * step; const lab = o.label?.(n) ?? YOU[((n % YOU.length) + YOU.length) % YOU.length]; ctx.save(); ctx.translate(.4, y); ctx.scale(1 / 100, 1 / 100); youCard((w - .8) * 100, 300, lab, t, 300 + ((n + 50) % 9)); ctx.restore(); }
      ctx.restore();
    });
    const k = ease(o.open), top = P(fx, FEED.y1, BLD.z - .05), bot = P(fx, FEED.y0, BLD.z - .05);
    if (top && bot && k < 1) { const hgt = (bot[1] - top[1]) * (1 - k), wdt = fw * top[2]; shOn(24, 0, 12, .5); ctx.fillStyle = '#3A4F88'; poly(jag(rectPts(top[0] - wdt / 2, top[1] - hgt * .15 * k, wdt, hgt), 205, 3, 30)); ctx.fill(); shOff(); }
  }
  ctx.restore();
  const tp = P(BLD.x - BLD.w / 2 + .5, BLD.y + BLD.h / 2 + 1.6, BLD.z - .1);      // its name tag, hanging from the roof
  if (tp && up > .9) { ctx.strokeStyle = PP.cream; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(tp[0] + 30, tp[1] - 1.6 * tp[2]); ctx.lineTo(tp[0] + 30, tp[1] - 20); ctx.stroke(); tag(tp[0], tp[1], '机房', Math.round(.95 * tp[2]), { seed: 9, rot: .05 }); }
}
function arcThread(A, B, D, k, t, wd) { if (k <= 0) return; const pts = []; for (let i = 0; i <= 24 * k; i++) { const p = P(...bez3(A, B, D, i / 24)); if (p) pts.push([p[0], p[1]]); } if (pts.length > 2) thread(pts, wd, t); }

// ------------------------------------------------------------------ the city at night, in paper (S3, S8b)
function cityScene(t) {
  const g = ctx.createLinearGradient(0, 0, 0, H); g.addColorStop(0, '#141C38'); g.addColorStop(.6, PP.night); g.addColorStop(1, PP.night2); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  for (let i = 0; i < 30; i++) { ctx.fillStyle = 'rgba(241,232,213,.6)'; star(hash(i, 4) * W, hash(i, 5) * H * .4, 3 + hash(i, 6) * 4); ctx.fill(); }
  for (const [x, z, w, h, s] of CITY) {
    const a = P(x - w / 2, -120 + h, z), b = P(x + w / 2, -120, z); if (!a || !b || b[0] < -40 || a[0] > W + 40) continue;
    const bw = b[0] - a[0], bh = b[1] - a[1];
    ctx.fillStyle = 'rgba(3,5,14,.45)'; ctx.fillRect(a[0] + bw * .05, a[1] + bw * .07, bw, bh);
    ctx.fillStyle = `rgb(${30 + s * 14 | 0},${40 + s * 16 | 0},${72 + s * 24 | 0})`; poly(bw > 30 ? jag(rectPts(a[0], a[1], bw, bh), (x * 7 + z) | 0, bw * .01, bw * .25) : rectPts(a[0], a[1], bw, bh)); ctx.fill();
    const n = Math.floor(w / 6), m = Math.floor(h / 8);
    if (bw > 6) for (let i = 0; i < n; i++) for (let j = 0; j < m; j++) { if (hash(i * 31 + j, x * 7 + z | 0) > .3) continue; ctx.fillStyle = 'rgba(244,214,150,.75)'; ctx.fillRect(lerp(a[0], b[0], (i + .3) / n), lerp(b[1], a[1], (j + .3) / m), Math.max(1, bw / n * .45), Math.max(1, bh / m * .35)); }
  }
  const a = P(DC[0] - 60, -120 + 50, DC[2]), b = P(DC[0] + 60, -120, DC[2]);
  if (a && b) { const bw = b[0] - a[0], bh = b[1] - a[1]; ctx.fillStyle = 'rgba(3,5,14,.45)'; ctx.fillRect(a[0] + 6, a[1] + 8, bw, bh); ctx.fillStyle = PP.night3; ctx.fillRect(a[0], a[1], bw, bh); ctx.fillStyle = PP.kraft; ctx.fillRect(a[0], a[1], bw, Math.max(2, bh * .06)); if (bw > 60) tag(a[0] + bw * .1, a[1] - bh * .12, '机房', Math.max(16, bh * .22), { seed: 4 }); }
}
// ------------------------------------------------------------------ the data-centre corridor, in paper (S4, S8a)
function dcScene(t) {
  ctx.fillStyle = '#10162E'; ctx.fillRect(0, 0, W, H);
  for (let z = 0; z < 320; z += 10) {
    const f = [P(-8, -12, z), P(8, -12, z), P(8, -12, z + 10), P(-8, -12, z + 10)];
    if (f.every(Boolean)) { ctx.fillStyle = (z / 10) % 2 ? '#1C2546' : '#18203E'; poly(f.map(v => [v[0], v[1]])); ctx.fill(); }
    const c = [P(-2, 12, z + 3), P(2, 12, z + 3), P(2, 12, z + 6), P(-2, 12, z + 6)];
    if (c.every(Boolean)) { ctx.fillStyle = 'rgba(241,232,213,.5)'; poly(c.map(v => [v[0], v[1]])); ctx.fill(); }
  }
  for (let z = 310; z >= 0; z -= 10) for (const side of [-1, 1]) {
    const q = [P(side * 8, 11, z), P(side * 8, 11, z + 9), P(side * 8, -12, z + 9), P(side * 8, -12, z)]; if (q.some(v => !v)) continue;
    ctx.fillStyle = PP.night3; poly(q.map(v => [v[0], v[1]])); ctx.fill(); ctx.strokeStyle = 'rgba(3,5,14,.5)'; ctx.lineWidth = Math.max(1, q[0][2] * .25); ctx.stroke();
    for (let j = 0; j < 14; j++) for (let k = 0; k < 3; k++) {
      const d = P(side * 8, 9.5 - j * 1.55, z + 1.5 + k * 2.6); if (!d) continue;
      const on = hash(z * 37 + j * 5 + k + (side > 0 ? 999 : 0), Math.floor(t * 4 + j * .3 + k)) > .45;
      ctx.fillStyle = on ? ((j + k) % 4 ? 'rgba(241,232,213,.9)' : 'rgba(150,180,235,.9)') : 'rgba(20,26,50,.9)';
      const r = Math.max(1.2, d[2] * .22); ctx.fillRect(d[0] - r, d[1] - r * .5, r * 2, r);
    }
  }
}

// ------------------------------------------------------------------ the batch, ranked (S5–S7)
const RANK = { 5: 1, 3: 2, 4: 3 };      // card index → rank: 88 % first, then 72 %, then 41 %
const RX = [-4.45, 0, 4.45];
function rankedPos(i, t) {      // where front card i sits during the ranking; returns [x, y, zRel]
  const [bx, by] = BATCH[i], tx = RX[RANK[i] - 1], k = ease(ev(t, C.top + .6, .7));
  return [lerp(bx, tx, k), by + (i === 5 ? Math.sin(k * Math.PI) * 2.6 : i === 3 ? -Math.sin(k * Math.PI) * 1.2 : 0), i === 5 ? -Math.sin(k * Math.PI) * 2 : 0];
}
function batchScene(t) {
  drawWall(t);
  STY.dim(t, clamp(ev(t, C.pick + .2, 1) * .7 + ev(t, C.q, 1) * .3));
  drawFunnel(t, 1 - .5 * ev(t, C.q, 1) - .5 * ev(t, C.top, 1));
  const tops = [];
  BATCH.forEach(([bx, by, k, odds, zz], i) => {
    const u = ease(ev(t, C.pick + .2 + i * .12, 1.3)); if (u <= 0) return;
    let x = lerp(0, bx, u), y = lerp(FUN.yMouth + 1, by, u) + Math.sin(u * Math.PI) * 2.5, z = lerp(FUN.z - 1, zz, u), rot = 0;
    if (zz > 30 && t >= C.top + .2) { const kk = ev(t, C.top + .2 + i * .1, .9); y -= 30 * kk * kk; rot = kk * (i - 1) * .9; if (kk >= 1) return; }
    if (zz < 30 && t >= C.top) { const r = rankedPos(i, t); x = r[0]; y = r[1]; z = zz + r[2]; }
    const p = card(x + CX * u, y + CY * u, z, 4.2, 7.3, (w, h) => {
      ctx.save(); ctx.translate(w / 2, h / 2); ctx.rotate(rot); ctx.translate(-w / 2, -h / 2); ctx.scale(1 / 100, 1 / 100); STY.batchCard(w * 100, h * 100, k, odds, t, zz > 30, i, u);
      if (RANK[i] && t >= C.top) {      // rank sticker
        const kk = expoOut(ev(t, C.top + (RANK[i] - 1) * .25, .4)), sc = kk * (1 + .25 * Math.sin(kk * Math.PI));
        ctx.save(); ctx.translate(40, 40); ctx.scale(sc, sc); ctx.rotate(-.15); shOn(10, 3, 5, .45); ctx.fillStyle = RANK[i] === 1 ? PP.gold : PP.kraft; ctx.beginPath(); ctx.arc(0, 0, 58, 0, TAU); ctx.fill(); shOff();
        ctx.font = `700 76px ${PSERIF}`; ctx.fillStyle = PP.ink; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(String(RANK[i]), 0, 4); ctx.restore();
      }
      ctx.restore();
    });
    if (RANK[i] && p) tops[RANK[i] - 1] = P(x + CX * u, y + CY * u + 3.3, z);
  });
  // the gold thread laces through the three winners
  const lk = ev(t, C.top + 1.25, .7);
  if (lk > 0 && tops.every(Boolean) && tops.length === 3) laceThread(tops, lk, t);
}
function laceThread(tops, k, t) {
  const pts = [[-60, tops[0][1] - 80], ...tops.map(p => [p[0], p[1]]), [W + 60, tops[2][1] - 60]];
  const n = Math.max(2, Math.ceil(pts.length * k)); const cut = pts.slice(0, n);
  if (k < 1) { const a = cut[n - 2], b = pts[n - 1], f = pts.length * k - (n - 1); cut[n - 1] = [lerp(a[0], b[0], clamp(f + 1)), lerp(a[1], b[1], clamp(f + 1))]; }
  thread(cut, 12, t);
}
// the three winners, carried in front of the camera on the way back (S8)
function carried(t, dist) {
  const tops = [];
  [5, 3, 4].forEach((i, r) => {
    const [, , k, odds] = BATCH[i], x = CX + RX[r] * (dist / 10.6), y = CY - .4 - 1.5 * ev(t, C.back, .4) + Math.sin(t * 3 + r) * .25, z = CZ + dist;
    card(x, y, z, 4.2, 7.3, (w, h) => { ctx.save(); ctx.scale(1 / 100, 1 / 100); STY.batchCard(w * 100, h * 100, k, odds, t, false, i, 1); ctx.restore(); });
    tops.push(P(x, y + 3.3, z));
  });
  if (tops.every(Boolean)) laceThread(tops, 1, t);
}

// ------------------------------------------------------------------ the shot
const KIN = [      // camera behind the screen, from the cards' arrival to the push back into the screen
  [34.05, 0, 1.5, -26], [34.8, 3.5, .5, -14], [36.9, 2.4, .3, -12.5],
  [38.7, 8, 1.2, -27], [40.7, 8.4, 1.3, -25], [41.3, 3.6, -.3, -20], [42.45, 3.4, -.5, -19],
  [43.2, 15.8, 0, -21], [44.15, 16.2, .2, -19.5], [44.9, 8, 0, -22], [45.9, 7.6, -.4, -20.5], [46.45, 4.6, -.6, -16.5],
  [47.4, 9.5, .2, -20], [48.6, 8.6, 0, -21], [49.6, 6, 0, -20], [50.6, 0, 0, -.85],
];
const ARR_FRONT = [[-6.6, -1, -8.5], [0, -1, -8.5], [6.6, -1, -8.5]];
const loopPhase = t => { const d = Math.max(0, t - C.loop); return .5 * d + .45 * d * d; };
function feedScroll(t) { return Math.max(0, t - (C.rev2 + .1)) * 1.6; }
const stareSecs = t => 1 + Math.floor(Math.max(0, t - (C.tip + .25)) / .25);
function insideWorld(t, o = {}) {
  insideBg(t);
  // the gold route into the distance (fades once the data centre stands beside the phone)
  const la = 1 - ev(t, C.loop - .6, 1.2);
  if (la > 0) { const l0 = P(SLOT(3)[0], SLOT(3)[1], QZ[3] + 2), l1 = P(0, 0, 400); if (l0 && l1) { ctx.globalAlpha = la; thread([[l1[0], l1[1]], [lerp(l1[0], l0[0], .5), lerp(l1[1], l0[1], .5)], [l0[0], l0[1]]], Math.max(5, .5 * l0[2]), t); ctx.globalAlpha = 1; } }
  // the data centre and the loop
  const up = ease(ev(t, C.loop - .5, .8));
  const st = { up, open: ev(t, C.rev2, .45), feed: feedScroll(t), greyN: 40 * ev(t, C.tip + .4, 1.6), flip: ev(t, 47.5, .9),
    label: n => { const sN = Math.floor(feedScroll(C.tip + .25)) + 4; if (t >= 47.5 && n === sN + 1) return '不感兴趣 −'; if (t >= C.tip + .25 && n === sN) return `盯着看 ${Math.min(5, stareSecs(t))} 秒`; return null; } };
  if (t >= C.tip + .25) st.feed = Math.floor(feedScroll(C.tip + .25)) + ease(ev(t, C.tip + .25, .4)) + (t >= 47.5 ? ease(ev(t, 47.5, .4)) : 0);
  if (up > 0) building(t, st);
  const ak = ev(t, C.loop - .2, 1.0);
  if (ak > 0) { arcThread(...ARC_U, ak, t, 9); arcThread(...arcL(3), ak, t, 9); }
  // the queue behind the phone, the phone, the screen
  drawQueue(t, { tags: t < C.loop, front: o.front });
  phoneBody(t);
  const sn = screenNow(t);
  screenAt(t, sn.cur, { out: sn.out, u: sn.u, mode: sn.mode, watch: o.watch, menu: o.menu, prog: o.prog });
  drawQueue(t, { front: o.front, near: true });
  // beads up the upper arc (your seconds), and picks coming down the lower arc, faster and faster
  if (ak >= 1 && t < C.tip) { const ph = loopPhase(t); for (let i = 0; i < 5; i++) { const u = (ph + i / 5) % 1, p = P(...bez3(...ARC_U, u)); if (p) bead(p[0], p[1], .5 * p[2]); const q = P(...bez3(...arcL(3), (u + .1) % 1)); if (q && t < C.rev) card(...bez3(...arcL(3), (u + .1) % 1), 1.6, 2.8, (w, h) => { ctx.scale(1 / 100, 1 / 100); paperThumb(w * 100, h * 100, i * 3, i); }); } }
  if (t >= C.tip + .25 && t < 46.2) { const n = stareSecs(t); for (let j = 1; j <= Math.min(5, n); j++) { const u = ev(t, C.tip + .25 + (j - 1) * .25, .7); if (u > 0 && u < 1) { const p = P(...bez3(...ARC_U, u)); if (p) bead(p[0], p[1], (.5 + j * .08) * p[2]); } } }
  if (t >= 46.5 && t < 47.6) {      // your "no": a gold minus rides up to the data centre
    const u = ease(ev(t, 46.5, 1.0)), p = P(...bez3(...ARC_U, u)); if (p) { bead(p[0], p[1], .9 * p[2]); ctx.fillStyle = PP.ink; ctx.fillRect(p[0] - .45 * p[2], p[1] - .09 * p[2], .9 * p[2], .18 * p[2]); }
  }
}
function shot(t) {
  if (t < C.dive + .55) {      // S0: in bed → push into the screen
    const p0 = ev(t, 0, C.dive), push = expoIn(ev(t, C.dive - .2, .75));
    CX = lerp(.8, 0, smooth(p0)) + .15 * Math.sin(t * .6); CY = lerp(-1.5, 0, smooth(p0)) + .1 * Math.sin(t * .8); F = 1000;
    CZ = lerp(-15.5, -12.5, ease(p0)) + push * 11.7;
    bedroom(t);
    // 「下一条，其实已经在你手机里了」: the next card slides out from behind the phone, already downloaded
    const pk = ease(ev(t, C.next1, .6)) * (1 - ease(ev(t, C.dive - .45, .4)));
    if (pk > 0) { queueCard(lerp(0, 4.6, pk), lerp(0, .6, pk), .5, SCREEN.w, SCREEN.h, V.hills, t, { bar: 1, seed: 21, rot: pk * .04 }); const p = P(3.85, SCREEN.h / 2 + 1.0, .5); if (p && pk > .7) tag(p[0], p[1], '已下载', Math.round(.6 * p[2]), { seed: 1, rot: .04 }); }
    const lift = smooth(ev(t, C.ask + .3, 1.2)) * (1 - smooth(ev(t, C.dive - .1, .3)));
    phoneAt(t, {}); hand(t, lift);
    // 「笑出声」: paper 哈s jump out of the screen when the box bursts
    for (let i = 0; i < 3; i++) { const k = t - (C.laugh + i * .12); if (k < 0 || k > 2.3) continue; const q = P(3.2 + k * 2.4 * (1 + i * .3), 4.5 + k * 5.5 - k * k * 7.5 + i * .8, -.3); if (q) tag(q[0], q[1], '哈', Math.round(1.05 * q[2]), { seed: 40 + i, rot: k * (i % 2 ? 1.6 : -1.2) }); }
    return 'S0';
  }
  if (t < C.fly + .3) {      // S1: behind the screen, the queue; the watch-time bead leaves along the thread
    const u = t - (C.dive + .55);
    CZ = lerp(-.85, -14, expoOut(ev(u, 0, 2.0))); CX = lerp(0, 6, smooth(ev(t, C.dl + .5, 4))) - 6 * smooth(ev(t, C.you, 1.2)); CY = lerp(0, 1.5, smooth(ev(t, C.dl, 3))) - 1.5 * smooth(ev(t, C.you, 1.2)); F = 1000;
    if (t >= C.who && t < C.you) { CZ += smooth(ev(t, C.who, 1.2)) * 20; CX += smooth(ev(t, C.who, 1.2)) * 2; }
    if (t >= C.you) CZ = lerp(CZ, -15, smooth(ev(t, C.you, 1)));
    insideBg(t);
    const l0 = P(SLOT(3)[0], SLOT(3)[1], QZ[3] + 2), l1 = P(0, 0, 400); if (l0 && l1) thread([[l1[0], l1[1]], [lerp(l1[0], l0[0], .5), lerp(l1[1], l0[1], .5)], [l0[0], l0[1]]], Math.max(5, .5 * l0[2]), t);
    for (let i = 3; i >= 1; i--) { const [x, y, z] = SLOT(i), bob = Math.sin(t * 1.3 + i) * .25, kk = ev(t, C.dl + i * .5, 1.0); queueCard(x, y + bob, z, SCREEN.w, SCREEN.h, vk([2, 0, 1][i - 1]), t, { bar: kk, seed: 20 + i }); if (kk >= 1 && t >= C.queue) { const p = P(x + SCREEN.w / 2 - .2, y + bob + SCREEN.h / 2, z); if (p) tag(p[0] - 10, p[1] + 4, '已下载', Math.max(24, Math.round(.9 * p[2])), { seed: i }); } }
    phoneBody(t);
    const secs = 9 + Math.floor(Math.max(0, t - C.secs + .001));
    screenAt(t, V.cat, { watch: t >= C.secs - .3 ? `已看 ${secs} 秒` : null });
    if (t >= C.signal) {
      const k = ev(t, C.signal, C.fly + .3 - C.signal), f = kk => [lerp(-SCREEN.w / 2 + 1.5, 0, smooth(kk * 3)), lerp(SCREEN.h / 2 - .6, 0, smooth(kk * 3)), lerp(0, 300, expoIn(kk))];
      const p = P(...f(k)), tr = []; for (let i = 0; i < 10; i++) { const q = P(...f(Math.max(0, k - i * .015))); if (q) tr.unshift([q[0], q[1]]); }
      if (p) signal(p[0], p[1], Math.max(12, .9 * p[2]), tr);
    }
    return 'S1';
  }
  if (t < C.dc) {      // S3: the city; the bead streaks toward the data centre
    const k = ev(t, C.fly + .3, C.dc - C.fly - .3);
    CX = lerp(0, DC[0], ease(k)); CY = lerp(20, -50, ease(k)); CZ = lerp(-40, DC[2] - 120, ease(k)); F = 900;
    cityScene(t);
    const p = P(lerp(0, DC[0], k), lerp(40, -95, k), lerp(CZ + 30, DC[2], expoIn(k * .9 + .1)));
    if (p) signal(p[0], p[1], 44, [[W / 2, H * 1.05], [W * .45, H * .8], [p[0], p[1]]]);
    return 'S3';
  }
  if (t < C.sea) {      // S4: down the corridor
    const k = ev(t, C.dc, C.sea - C.dc); CX = 0; CY = 0; CZ = lerp(-20, 240, ease(k)); F = 900;
    dcScene(t); signal(W / 2, H / 2 - 40, 34, [[W / 2, H * 1.0], [W / 2 - 20, H * .75], [W / 2, H / 2 - 40]]);
    return 'S4';
  }
  if (t < C.back) {      // S5–S7: the wall, the funnel, the odds, the ranking
    const k = ev(t, C.sea, 2.5); CX = 2 * Math.sin(t * .2); CY = lerp(-30, 0, ease(k)); CZ = lerp(-30, 10, ease(k)) + 3 * smooth(ev(t, C.q, 2)) + 1.2 * smooth(ev(t, C.top, 2)); F = 1000;
    if (t < C.pick + .2) wallScene(t); else batchScene(t);
    return 'S5';
  }
  const dist = t => lerp(10.6, 15, ease(ev(t, C.back, .4)));
  if (t < C.back + .5) {      // S8a: back down the corridor, the winners flying with us
    const k = ev(t, C.back, .5); CX = 0; CY = 0; CZ = lerp(240, -20, ease(k)); F = 900;
    dcScene(t); carried(t, dist(t));
    return 'S8';
  }
  if (t < C.back + 1.05) {      // S8b: back over the city
    const u = 1 - ease(ev(t, C.back + .5, .55)); CX = lerp(0, DC[0], u); CY = lerp(20, -50, u); CZ = lerp(-40, DC[2] - 120, u); F = 900;
    cityScene(t); carried(t, dist(t));
    return 'S8';
  }
  if (t < C.home + .85) {      // S9–S11: behind the screen again; the queue fills, the swipe, the loop, the reversal, the "no"
    [CX, CY, CZ] = kf(t, KIN); F = 1000;
    CX += .25 * Math.sin(t * .5); CY += .15 * Math.sin(t * .7);
    const front = ARR_FRONT.map(([x, y, z]) => [x, y, z]);
    const o = { front };
    if (t >= C.tip + .25 && t < 46.4) o.watch = `已看 ${Math.min(5, stareSecs(t))} 秒`;
    if (t >= C.nope - .1 && t < 46.75) o.menu = t < 46.5 ? ev(t, C.nope - .1, .35) : 1 - ev(t, 46.5, .25);
    if (t >= 46.5) o.prog = .02 + (t - 46.5) * .09;
    insideWorld(t, o);
    // your thumb: the swipe, three flicks, the long press
    if (t > C.swipe - .5 && t < C.swipe + .9) { const k = ease(ev(t, C.swipe - .5, .45)), s = ease(ev(t, C.swipe, .35)), r = expoIn(ev(t, C.swipe + .45, .45)); thumbAt(2.2 - s * .8 + r * 3, lerp(-15, -3.5, k) + s * 7 - r * 22, -.4, -.35 + s * .2); }
    if (t > 40.6 && t < 42.5) {      // three quick flicks
      const k = ease(ev(t, 40.6, .3)), r = expoIn(ev(t, 42.1, .4)); let up = 0;
      for (const tf of [41.0, 41.5, 42.0]) { const a = ev(t, tf - .05, .22), b = ev(t, tf + .17, .2); up += ease(a) * (1 - ease(b)); }
      thumbAt(2 - up * .5 + r * 3, lerp(-15, -4.5, k) + up * 6 - r * 20, -.4, -.35 + up * .2);
    }
    if (t > C.nope - .55 && t < 47.3) {      // the long press, then a tap on 不感兴趣
      const k = ease(ev(t, C.nope - .55, .4)), dn = ease(ev(t, 46.15, .2)), tap = Math.sin(clamp((t - 46.35) / .25) * Math.PI), r = expoIn(ev(t, 46.75, .5));
      thumbAt(1.2 + r * 3, lerp(-15, -.8, k) - dn * 2.1 - r * 22, -.4 - tap * .25, -.3, t >= C.nope - .15 && t < 46.2 ? ev(t, C.nope - .15, .4) : 0);
    }
    return t < C.loop - .75 ? 'S9' : t < C.tip - .05 ? 'S10' : 'S11';
  }
  if (t < C.black) {      // S12: out through the screen into the bedroom; same framing as the first frame
    const k = ev(t, C.home + .85, 1.6);
    CX = lerp(0, .8, expoOut(k)) + .15 * Math.sin(t * .6) * k; CY = lerp(0, -1.5, expoOut(k)) + .1 * Math.sin(t * .8) * k; F = 1000;
    CZ = lerp(-.85, -15.5, expoOut(k)) + 1.0 * smooth(ev(t, C.home + 2.4, C.black - C.home - 2.4));
    bedroom(t); phoneAt(t, { vid: V.sun, prog: .02 + (t - 46.5) * .09 }); hand(t, 0);
    return 'S12';
  }
  ctx.fillStyle = '#0D0C11'; ctx.fillRect(0, 0, W, H);
  return 'S13';
}

// ------------------------------------------------------------------ overlays
window.seek = function (t) {
  t = clamp(t, 0, DUR - 1 / FPS);
  ctx.setTransform(SS, 0, 0, SS, 0, 0); ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over'; shOff(); ctx.setLineDash([]);
  const s = shot(t);
  const H_ = (t0, parts, size = 120, y = 330) => STY.hero(t, t0, [{ parts, size }], 72, y);
  if (s === 'S0' && t < C.dive) STY.title(t);
  if (s === 'S1') {
    if (t >= C.queue && t < C.who) H_(C.queue, [['已下载 ', 'b'], [roll('3', t, C.queue, .3), 'a'], [' 条', 'b']]);
    if (t >= C.who && t < C.you) H_(C.who, [['谁挑的？', 'b']]);
    if (t >= C.you) H_(C.you, [['是', 'b'], ['你', 'a'], ['。', 'b']], 140, 340);
  }
  if (s === 'S3') H_(C.fly, [['飞回', 'b'], ['机房', 'a']]);
  if (s === 'S4' || s === 'S5') {
    if (t >= C.sea && t < C.pick) H_(C.sea, [['海量', 'b']], 130);
    if (t >= C.pick && t < C.q) H_(C.pick, [['捞出', 'b'], ['一小批', 'a']]);
    if (t >= C.q && t < C.top) H_(C.q, [['算一道题', 'b']], 110);
    if (t >= C.top) H_(C.top, [['前三名', 'b']], 120);
  }
  if (s === 'S8' || (s === 'S9' && t < C.swipe)) H_(C.back, [['送回', 'b'], ['你手机', 'a']]);
  if (s === 'S9' && t >= C.swipe + .9) H_(C.swipe + .9, [['从不卡顿', 'b']]);
  if (s === 'S10') {
    if (t >= C.loop && t < C.rev) { const n = 1 + Math.floor(loopPhase(t) * 5); H_(C.loop, [['第 ', 'b'], [String(n), 'a'], [' 轮', 'b']]); }
    if (t >= C.rev && t < C.rev2) H_(C.rev, [['你在刷视频', 'b']], 110);
    if (t >= C.rev2) H_(C.rev2, [['视频也在', 'b'], ['刷你', 'a']], 110);
  }
  if (s === 'S11') {
    if (t >= C.tip && t < C.nope) H_(C.tip, [['别', 'b'], ['盯着看', 'a']]);
    if (t >= C.nope && t < C.home - .1) H_(C.nope, [['长按', 'b'], ['不感兴趣', 'a']], 110);
  }
  if (s === 'S12' && t >= C.home + 1.9) {      // the title comes back, same place; then what it meant
    ctx.save(); ctx.translate(-(1 - expoOut(ev(t, C.home + 1.9, .5))) * 800, 0); STY.title(t); ctx.restore();
    if (t >= C.self) H_(C.self, [['就是', 'b'], ['你自己', 'a']], 110, 520);
  }
  if (STY.post) STY.post(t);
  if (s === 'S13' && t >= C.next) {      // end card: black, white type, left aligned
    ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic'; ctx.fillStyle = PP.cream;
    [['你还想知道，', 0], ['按下哪个键之后的事？', .5]].forEach(([s_, d], i) => { const n = Math.ceil([...s_].length * clamp((t - C.next - d) / .5)); if (n <= 0) return; ctx.font = `700 76px ${PSERIF}`; ctx.fillText([...s_].slice(0, n).join(''), 72, 900 + i * 110); });
  }
  if (!CLEAN_) { const c = CUES.subs.find(c => t >= c.t0 && t < c.t1); if (c && t < C.next - .2) STY.sub(c.text, t); }
  if (COVER) { const y = COVER === '34' ? 1300 : 1600; STY.hero(t, -5, [{ parts: [['下一条，早就在你手机里了', 'b']], size: 70 }], 72, y); STY.hero(t, -5, [{ parts: [['挑它的，是', 'b'], ['你自己', 'a']], size: 70 }], 72, y + 125); }
  return true;
};
const COVER = (location.search.match(/cover=(\d+)/) || [])[1];
