// 「你按下去之后」· 你把验证码念出去之后 — new series look: cream paper, one hero (your phone), big type, one accent (orange-red).
// The six digits are the heartbeat: they lift out of the SMS, jitter on the orange sheet, get tied to a transfer slip, fly to the other phone.
// Pure function of time; seeded noise only. Units: cm in the 2.5D camera.
'use strict';
const SS = +((location.search.match(/ss=(\d)/) || [])[1] || 1);
if (SS > 1) { cv.width = W * SS; cv.height = H * SS; ctx = cv.getContext('2d'); }
const K = { bg: '#F1EADB', bg2: '#E8DFCC', ink: '#1E1C27', acc: '#E8552D', accD: '#B93E1E', cream: '#FBF6EA', kraft: '#C79B6A', grey: '#6E6A73', greyL: '#B9B4AC' };
const SERIF = '"Noto Serif CJK SC"', SANS = '"Noto Sans CJK SC"';
// ---------- paper helpers
function jag(pts, seed, amp, step) { const out = [], r = mulberry32(seed); for (let i = 0; i < pts.length; i++) { const [x0, y0] = pts[i], [x1, y1] = pts[(i + 1) % pts.length], L = Math.hypot(x1 - x0, y1 - y0) || 1, n = Math.max(1, Math.round(L / step)), nx = -(y1 - y0) / L, ny = (x1 - x0) / L; for (let k = 0; k < n; k++) { const u = k / n, j = k === 0 ? 0 : (r() - .5) * 2 * amp; out.push([x0 + (x1 - x0) * u + nx * j, y0 + (y1 - y0) * u + ny * j]); } } return out; }
const rectPts = (x, y, w, h) => [[x, y], [x + w, y], [x + w, y + h], [x, y + h]];
function poly(pts) { ctx.beginPath(); pts.forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)); ctx.closePath(); }
function shOn(blur, dx, dy, a = .25) { ctx.shadowColor = `rgba(60,40,20,${a})`; ctx.shadowBlur = blur * SS; ctx.shadowOffsetX = dx * SS; ctx.shadowOffsetY = dy * SS; }
function shOff() { ctx.shadowColor = 'transparent'; ctx.shadowBlur = 0; ctx.shadowOffsetX = 0; ctx.shadowOffsetY = 0; }
const GRAIN = (() => { const c = document.createElement('canvas'); c.width = 540; c.height = 960; const g = c.getContext('2d'), im = g.createImageData(540, 960), r = mulberry32(5); for (let i = 0; i < im.data.length; i += 4) { const v = 128 + (r() - .5) * 46; im.data[i] = im.data[i + 1] = im.data[i + 2] = v; im.data[i + 3] = 255; } g.putImageData(im, 0, 0); return c; })();
function grain() { ctx.save(); ctx.globalCompositeOperation = 'overlay'; ctx.globalAlpha = .22; ctx.drawImage(GRAIN, 0, 0, W, H); ctx.restore(); }

// ---------- big type: one sentence per screen, typed in; keyword in the accent with a cut-paper underline
function bigType(t, t0, t1, lines, o = {}) {
  if (t < t0 || t >= t1) return;
  const out = ev(t, t1 - .25, .25), x = 70, y0 = o.y ?? 250, lh = o.lh ?? 128, sz = o.size ?? 104;
  let typed = o.instant ? 999 : (t - t0) / .045; ctx.save(); ctx.translate(-out * 60, 0); ctx.globalAlpha = 1 - out;
  lines.forEach((parts, i) => {
    let cx = x; const y = y0 + i * lh;
    for (const [s, role] of parts) {
      ctx.font = `700 ${sz}px ${SERIF}`; ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic';
      const ch = [...s], n = Math.max(0, Math.min(ch.length, Math.floor(typed))); typed -= ch.length;
      const vis = ch.slice(0, n).join(''), w = ctx.measureText(vis).width, full = ctx.measureText(s).width;
      if (role === 'a' && n > 0) { ctx.fillStyle = o.under ?? K.acc; poly(jag(rectPts(cx - 6, y + 14, w + 12, 16), 9 + i, 3, 20)); ctx.fill(); }
      ctx.fillStyle = role === 'a' ? (o.accText ?? K.acc) : (o.ink ?? K.ink); ctx.fillText(vis, cx, y); cx += full;
    }
  });
  ctx.restore();
}

// ---------- the phones
function phoneBody(cx, cy, s, o = {}) {      // cx, cy screen px; s px per cm
  const w = 7.4 * s, h = 15.6 * s;
  ctx.save(); ctx.translate(cx, cy); ctx.rotate(o.rot ?? 0);
  shOn(30, 10, 22, .3); ctx.fillStyle = o.body ?? K.ink; ctx.beginPath(); ctx.roundRect(-w / 2, -h / 2, w, h, 1.0 * s); ctx.fill(); shOff();
  ctx.fillStyle = o.screen ?? K.cream; ctx.beginPath(); ctx.roundRect(-w / 2 + .32 * s, -h / 2 + .32 * s, w - .64 * s, h - .64 * s, .75 * s); ctx.fill();
  ctx.save(); ctx.beginPath(); ctx.roundRect(-w / 2 + .32 * s, -h / 2 + .32 * s, w - .64 * s, h - .64 * s, .75 * s); ctx.clip();
  if (o.content) o.content(-w / 2 + .32 * s, -h / 2 + .32 * s, w - .64 * s, h - .64 * s, s);
  ctx.restore();
  ctx.fillStyle = 'rgba(30,28,39,.85)'; ctx.beginPath(); ctx.roundRect(-1.1 * s, -h / 2 + .55 * s, 2.2 * s, .5 * s, .25 * s); ctx.fill();      // the notch
  ctx.restore();
}
const CODE = [...'836592'];
function smsCard(x, y, w, s, t, o = {}) {      // the verification SMS, as a notification card
  const h = 4.2 * s; shOn(14, 0, 6, .18); ctx.fillStyle = '#FFFFFF'; ctx.beginPath(); ctx.roundRect(x, y, w, h, .5 * s); ctx.fill(); shOff();
  ctx.fillStyle = K.acc; ctx.beginPath(); ctx.roundRect(x + .4 * s, y + .4 * s, .9 * s, .9 * s, .2 * s); ctx.fill();
  ctx.font = `700 ${.5 * s}px ${SANS}`; ctx.fillStyle = K.ink; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.fillText('短信 · 现在', x + 1.6 * s, y + .85 * s);
  ctx.font = `500 ${.48 * s}px ${SANS}`; ctx.fillStyle = 'rgba(30,28,39,.75)';
  ctx.fillText('【XX银行】您正在进行', x + .45 * s, y + 1.9 * s);
  ctx.fillStyle = o.hiUse ? K.acc : 'rgba(30,28,39,.75)'; ctx.font = `700 ${.48 * s}px ${SANS}`; const pre = ctx.measureText('【XX银行】您正在进行').width; ctx.fillText('转账', x + .45 * s + pre, y + 1.9 * s);
  ctx.fillStyle = 'rgba(30,28,39,.75)'; ctx.font = `500 ${.48 * s}px ${SANS}`; ctx.fillText('操作，验证码：', x + .45 * s + pre + ctx.measureText('转账').width + .02 * s, y + 1.9 * s);
  // the digits sit here until they lift off
  CODE.forEach((d, i) => { if (o.lifted?.[i]) return; ctx.font = `900 ${1.15 * s}px ${SERIF}`; ctx.fillStyle = K.acc; ctx.textAlign = 'center'; ctx.fillText(d, x + (1.0 + i * .95) * s, y + 3.1 * s); });
  ctx.font = `500 ${.4 * s}px ${SANS}`; ctx.fillStyle = 'rgba(30,28,39,.55)'; ctx.textAlign = 'left'; ctx.fillText('5 分钟内有效，切勿告知他人。', x + 6.5 * s, y + 3.1 * s);
}
// a digit tile (cut paper)
function tile(x, y, s, d, i, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(o.rot ?? 0); const w = 1.25 * s, h = 1.6 * s;
  shOn(10, 3, 7, .3); ctx.fillStyle = o.bg ?? K.acc; poly(jag(rectPts(-w / 2, -h / 2, w, h), 30 + i, s * .03, s * .3)); ctx.fill(); shOff();
  ctx.font = `900 ${1.15 * s}px ${SERIF}`; ctx.fillStyle = o.fg ?? K.cream; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(d, 0, s * .06); ctx.restore();
}
// the thumb (as last episode)
const THUMB = (() => { const o = []; for (let i = 0; i <= 12; i++) { const a = Math.PI + i / 12 * Math.PI; o.push([Math.cos(a) * .74, .74 + Math.sin(a) * .74]); } o.push([.84, 2.4], [.95, 3.7], [1.02, 4.5], [1.06, 6.2], [1.22, 9], [1.4, 14], [1.5, 28], [-1.2, 28], [-1.1, 14], [-1.0, 9], [-.94, 6.2], [-.9, 4.5], [-.85, 3.7], [-.79, 2.4]); return o; })();
function thumb(x, y, s, rot) { ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s); shOn(16, 6, 10, .3); ctx.fillStyle = '#D6A07F'; poly(jag(THUMB, 51, .03, .45)); ctx.fill(); shOff(); ctx.fillStyle = '#EFCDB5'; ctx.beginPath(); ctx.ellipse(0, .9, .48, .62, 0, 0, TAU); ctx.fill(); ctx.restore(); }

// ---------- the shot
function frame(t) {
  ctx.fillStyle = K.bg; ctx.fillRect(0, 0, W, H);
  // camera: one hero phone, a slow steady push; pulls back a little when the second phone arrives
  const pull = ease(ev(t, C.phone2 - .2, 1.0));
  const s = lerp(90 + 2.5 * t, 58, pull), cx = lerp(540, 320, pull), cy = lerp(1250, 1250, pull);
  // the other phone, sliding in from the right
  const p2 = ease(ev(t, C.phone2, .8)), ox = lerp(1500, 800, p2), oy = 1260;
  if (p2 > 0) {
    phoneBody(ox, oy, s * .95, { body: '#55515A', rot: .05, content: (x, y, w, h, ss) => {
      ctx.fillStyle = '#F3F1EC'; ctx.fillRect(x, y, w, h);
      ctx.font = `700 ${.7 * ss}px ${SANS}`; ctx.fillStyle = K.ink; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText('转账', x + w / 2, y + 1.6 * ss);
      ctx.font = `900 ${1.3 * ss}px ${SERIF}`; ctx.fillText('¥5,000', x + w / 2, y + 4.2 * ss);
      ctx.fillStyle = 'rgba(30,28,39,.15)'; ctx.fillRect(x + .6 * ss, y + 5.6 * ss, w - 1.2 * ss, .08 * ss);
      ctx.font = `500 ${.45 * ss}px ${SANS}`; ctx.fillStyle = 'rgba(30,28,39,.6)'; ctx.fillText('验证码  _ _ _ _ _ _', x + w / 2, y + 6.6 * ss);
      const pressed = t >= C.tap && t < C.tap + .25; ctx.fillStyle = pressed ? K.accD : K.acc; ctx.beginPath(); ctx.roundRect(x + .8 * ss, y + h - 3.0 * ss, w - 1.6 * ss, 1.3 * ss, .65 * ss); ctx.fill();
      ctx.font = `700 ${.6 * ss}px ${SANS}`; ctx.fillStyle = K.cream; ctx.fillText('确认转账', x + w / 2, y + h - 2.35 * ss);
    } });
    if (t > C.tap - .7) { const k = ease(ev(t, C.tap - .7, .55)), tap = Math.sin(clamp((t - C.tap + .05) / .25) * Math.PI); thumb(ox + 2.6 * s * .95, lerp(1920 + 200, oy + 5.6 * s * .95, k) + tap * 6, s * .95 * (1 - tap * .03), -.4); }
  }
  // your phone with the SMS
  const lifted = CODE.map((_, i) => t >= C.fly + i * .18);
  phoneBody(cx, cy, s, { content: (x, y, w, h, ss) => {
    ctx.fillStyle = '#EDE6D6'; ctx.fillRect(x, y, w, h);
    ctx.font = `700 ${1.5 * ss}px ${SANS}`; ctx.fillStyle = 'rgba(30,28,39,.8)'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText('21:36', x + w / 2, y + 3.1 * ss);
    smsCard(x + .35 * ss, y + 5.2 * ss, w - .7 * ss, ss, t, { lifted, hiUse: false });
  } });
  // the six digits: lift off, hover in a row, jitter on the orange sheet, then settle and get tied to a transfer slip
  const flood = ease(ev(t, C.flood, .45)) * (1 - ease(ev(t, C.x + .3, .5)));
  if (flood > 0) {      // the orange sheet comes up from the bottom and covers the frame
    const top = lerp(H + 40, -60, ease(ev(t, C.flood, .45))) + (t > C.x + .3 ? lerp(0, H + 100, ease(ev(t, C.x + .3, .5))) : 0);
    const pts = [[-20, top]]; for (let x = 0; x <= W + 20; x += 40) pts.push([x, top + Math.sin(x * .03) * 8 + (hash(x, 3) - .5) * 10]); pts.push([W + 20, H + 200], [-20, H + 200]);
    shOn(30, 0, -12, .35); ctx.fillStyle = K.acc; poly(pts); ctx.fill(); shOff();
  }
  const rowY = lerp(470, 560, pull), rowX = i => lerp(cx, 540, flood) + (i - 2.5) * 1.55 * s * lerp(1, 1.1, flood);
  CODE.forEach((d, i) => {
    const t0 = C.fly + i * .18; if (t < t0) return;
    const k = expoOut(ev(t, t0, .6));
    const from = [cx + (-3.25 + 1.0 + i * .95 + .35) * s, cy + (-7.8 + .32 + 5.2 + 3.1) * s];
    let x = lerp(from[0], rowX(i), k), y = lerp(from[1], rowY, k) - Math.sin(k * Math.PI) * 60 + Math.sin(t * 2.4 + i) * 6, rot = (1 - k) * .4 + Math.sin(t * 1.7 + i) * .03, dd = d;
    if (flood > .5) { dd = String(Math.floor(hash(i * 13 + Math.floor(t * 12), 7) * 10)); x += (hash(i, Math.floor(t * 10)) - .5) * 30; y += (hash(i + 9, Math.floor(t * 10)) - .5) * 40; rot = (hash(i + 3, Math.floor(t * 10)) - .5) * .5; }
    tile(x, y, s * 1.05, dd, i, flood > .5 ? { rot, bg: K.cream, fg: K.acc } : { rot });
  });
  // the cross: two ink brush strokes over "随机"
  if (t >= C.x && t < C.x + 1.0) { const a = ease(ev(t, C.x, .15)), b = ease(ev(t, C.x + .12, .15)), fade = 1 - ev(t, C.x + .6, .4); ctx.save(); ctx.globalAlpha = fade; ctx.strokeStyle = K.ink; ctx.lineCap = 'round'; ctx.lineWidth = 34;
    ctx.beginPath(); ctx.moveTo(150, 380); ctx.lineTo(lerp(150, 930, a), lerp(380, 820, a)); ctx.stroke(); if (b > 0) { ctx.beginPath(); ctx.moveTo(930, 380); ctx.lineTo(lerp(930, 150, b), lerp(380, 820, b)); ctx.stroke(); } ctx.restore(); }
  // the transfer slip hanging from the digits; its thread runs to the other phone's button
  const sl = expoOut(ev(t, C.slip, .6));
  if (sl > 0) {
    const ax = rowX(2.5), ay = rowY + 1.1 * s, sx = ax + Math.sin(t * 2) * 12, sy = ay + lerp(0, 4.2 * s, sl);
    ctx.strokeStyle = K.ink; ctx.lineWidth = 4; ctx.beginPath(); ctx.moveTo(ax, ay); ctx.lineTo(sx, sy - 1.0 * s); ctx.stroke();
    ctx.save(); ctx.translate(sx, sy); ctx.rotate(Math.sin(t * 2) * .05); shOn(14, 4, 8, .3); ctx.fillStyle = K.kraft; poly(jag(rectPts(-3.2 * s, -1.0 * s, 6.4 * s, 2.0 * s), 70, s * .04, s * .4)); ctx.fill(); shOff();
    ctx.font = `700 ${.95 * s}px ${SERIF}`; ctx.fillStyle = K.ink; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText('转账 ¥5,000', 0, .05 * s); ctx.restore();
    if (p2 > .6) { const bx = ox, by = oy + (15.6 / 2 - 3.0 + .65) * s * .95, k2 = ease(ev(t, C.phone2 + .5, .7)); ctx.strokeStyle = K.ink; ctx.setLineDash([12, 10]); ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(sx + 3.2 * s, sy); ctx.lineTo(lerp(sx + 3.2 * s, bx, k2), lerp(sy, by, k2)); ctx.stroke(); ctx.setLineDash([]); }
  }
  grain();
  // the big type
  const onOrange = flood > .5;
  bigType(t, 0, C.flood, [[['一个验证码，', 'b']], [['凭什么能', 'b'], ['转走你的钱', 'a'], ['？', 'b']]], { y: 230, instant: true });
  bigType(t, C.flood + .1, C.x + .6, [[['你以为：', 'b']], [['它只是 6 个', 'b'], ['随机', 'a'], ['数字', 'b']]], { y: 230, ink: K.cream, accText: K.ink, under: K.cream });
  bigType(t, C.x + .6, C.phone2, [[['其实：', 'b']], [['它绑着一件', 'b'], ['具体的事', 'a']]], { y: 230 });
  bigType(t, C.phone2 + .2, DUR + 1, [[['有人在另一台手机上，', 'b']], [['点了', 'b'], ['「转账」', 'a']]], { y: 230, size: 92, lh: 116 });
  void onOrange;
}
window.seek = function (t) {
  t = clamp(t, 0, DUR - 1 / FPS);
  ctx.setTransform(SS, 0, 0, SS, 0, 0); ctx.globalAlpha = 1; shOff(); ctx.setLineDash([]);
  frame(t); return true;
};
window.DURATION = DUR; window.FPS = FPS;
window.ready = Promise.all([`700 104px ${SERIF}`, `900 80px ${SERIF}`, `700 40px ${SANS}`, `500 30px ${SANS}`].map(f => document.fonts.load(f)));
