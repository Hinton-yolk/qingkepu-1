// 「你按下去之后」· 你刚说完 — one continuous shot in cut paper.
// The dinner table → your phone lifts, the air fryer is already there → into the microphone hole: the mic is asleep,
// what listening would cost, the lab's stamp → back out: three clues (your 6 seconds, your friend's search, the same Wi-Fi)
// → into your feed: hundreds of cards, one pinned → the speech bubble is made of the clues → the switch → back to the table.
// The only gold is your own signal. Units: centimetres. Pure function of time; seeded noise only.
'use strict';
const SS = +((location.search.match(/ss=(\d)/) || [])[1] || 1);
if (SS > 1) { cv.width = W * SS; cv.height = H * SS; ctx = cv.getContext('2d'); }
function shOn(blur, dx, dy, a = .45) { ctx.shadowColor = `rgba(3,5,14,${a})`; ctx.shadowBlur = blur * SS; ctx.shadowOffsetX = dx * SS; ctx.shadowOffsetY = dy * SS; }

// ------------------------------------------------------------------ small tools
function kf(t, keys, e = ease) {
  if (t <= keys[0][0]) return keys[0].slice(1);
  for (let i = 1; i < keys.length; i++) if (t < keys[i][0]) { const a = keys[i - 1], b = keys[i], k = e((t - a[0]) / (b[0] - a[0])); return a.slice(1).map((v, j) => lerp(v, b[j + 1], k)); }
  return keys[keys.length - 1].slice(1);
}
function tag(x, y, txt, sz, o = {}) {
  ctx.font = `700 ${sz}px ${PSANS}`; const w = ctx.measureText(txt).width;
  ctx.save(); ctx.translate(x, y); ctx.rotate(o.rot ?? -.03); if (o.scale) ctx.scale(o.scale, o.scale);
  shOn(sz * .4, sz * .12, sz * .2, .45); ctx.fillStyle = o.bg ?? PP.kraft; poly(jag(rectPts(o.center ? -(w + sz * .9) / 2 : 0, -sz * .72, w + sz * .9, sz * 1.44), o.seed ?? 7, sz * .05, sz * .5)); ctx.fill(); shOff();
  ctx.fillStyle = o.fg ?? PP.ink; ctx.textAlign = o.center ? 'center' : 'left'; ctx.textBaseline = 'middle'; ctx.fillText(txt, o.center ? 0 : sz * .45, sz * .04); ctx.restore();
  return w + sz * .9;
}
function bead(x, y, r, col = 'gold') {
  shOn(r * .8, r * .25, r * .4, .5); const g = ctx.createRadialGradient(x - r * .3, y - r * .35, r * .1, x, y, r);
  if (col === 'gold') { g.addColorStop(0, PP.goldL); g.addColorStop(.5, PP.gold); g.addColorStop(1, PP.goldD); } else { g.addColorStop(0, '#FFFFFF'); g.addColorStop(.5, '#EDE3CF'); g.addColorStop(1, '#BFAE8E'); }
  ctx.fillStyle = g; ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.fill(); shOff();
}
function dashed(a, b, wd, t) { ctx.save(); ctx.setLineDash([wd * 2.2, wd * 1.6]); ctx.lineDashOffset = -t * 40; ctx.strokeStyle = PP.kraft; ctx.lineWidth = wd; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.quadraticCurveTo((a[0] + b[0]) / 2, Math.max(a[1], b[1]) + 40, b[0], b[1]); ctx.stroke(); ctx.restore(); }
// the thumb (same proportions as last episode), tip at (x, y, z)
const THUMB = (() => { const o = []; for (let i = 0; i <= 12; i++) { const a = Math.PI + i / 12 * Math.PI; o.push([Math.cos(a) * .74, .74 + Math.sin(a) * .74]); } o.push([.84, 2.4], [.95, 3.7], [1.02, 4.5], [1.06, 6.2], [1.22, 9], [1.4, 14], [1.5, 28], [-1.2, 28], [-1.1, 14], [-1.0, 9], [-.94, 6.2], [-.9, 4.5], [-.85, 3.7], [-.79, 2.4]); return o; })();
const NAIL = (() => { const o = []; for (let i = 0; i <= 10; i++) { const a = Math.PI + i / 10 * Math.PI; o.push([Math.cos(a) * .5, .66 + Math.sin(a) * .5]); } o.push([.47, 1.55], [-.47, 1.55]); return o; })();
function thumbAt(x, y, z, rot = -.35, press = 0) {
  const p = P(x, y, z); if (!p) return; const s = p[2];
  if (press > 0) { ctx.strokeStyle = `rgba(241,232,213,${.8 * (1 - press * .5)})`; ctx.lineWidth = Math.max(3, .1 * s); ctx.beginPath(); ctx.arc(p[0], p[1], (.5 + press * 1.2) * s, 0, TAU); ctx.stroke(); }
  ctx.save(); ctx.translate(p[0], p[1]); ctx.rotate(rot); ctx.scale(s, s);
  shOn(22, 9, 15, .5); ctx.fillStyle = PP.skin; poly(jag(THUMB, 51, .03, .45)); ctx.fill(); shOff();
  ctx.save(); poly(THUMB); ctx.clip(); ctx.fillStyle = 'rgba(140,82,55,.2)'; ctx.beginPath(); ctx.moveTo(.75, 1.2); ctx.quadraticCurveTo(1.0, 8, 1.5, 28); ctx.lineTo(2, 28); ctx.lineTo(2, 0); ctx.closePath(); ctx.fill(); ctx.restore();
  shOn(5, 1.5, 3, .25); ctx.fillStyle = '#EFCDB5'; poly(jag(NAIL, 52, .015, .25)); ctx.fill(); shOff();
  ctx.strokeStyle = 'rgba(140,85,58,.5)'; ctx.lineWidth = .06; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(-.5, 3.5); ctx.quadraticCurveTo(0, 3.72, .52, 3.5); ctx.moveTo(-.32, 3.78); ctx.quadraticCurveTo(0, 3.92, .34, 3.78); ctx.stroke();
  ctx.restore();
}

// ------------------------------------------------------------------ the air fryer (the thing everyone talks about), in paper
function airFryer(cx, cy, s, t, o = {}) {
  ctx.save(); ctx.translate(cx, cy); ctx.scale(s, s);
  if (o.steam !== false) { ctx.strokeStyle = 'rgba(255,248,236,.85)'; ctx.lineWidth = .035; ctx.lineCap = 'round'; for (let i = -1; i <= 1; i++) { ctx.beginPath(); for (let k = 0; k <= 10; k++) { const yy = -.72 - k * .045, xx = i * .18 + Math.sin(k * .9 + t * 4 + i) * .04; k ? ctx.lineTo(xx, yy) : ctx.moveTo(xx, yy); } ctx.stroke(); } }
  shOn(18, 6, 10, .4); ctx.fillStyle = '#2C2D36'; poly(jag([[-.42, -.62], [.42, -.62], [.5, .55], [-.5, .55]], 91, .008, .2)); ctx.fill(); shOff();
  ctx.fillStyle = '#3C3E4A'; poly(jag([[-.4, -.6], [.4, -.6], [.42, -.42], [-.42, -.42]], 92, .006, .2)); ctx.fill();
  ctx.fillStyle = PP.cream; ctx.beginPath(); ctx.arc(0, -.24, .1, 0, TAU); ctx.fill(); ctx.strokeStyle = PP.ink; ctx.lineWidth = .025; ctx.beginPath(); ctx.moveTo(0, -.24); ctx.lineTo(.06, -.31); ctx.stroke();
  ctx.fillStyle = '#383A46'; poly(jag([[-.44, -.02], [.44, -.02], [.47, .48], [-.47, .48]], 93, .006, .2)); ctx.fill();
  shOn(8, 2, 4, .4); ctx.fillStyle = PP.kraft; poly(jag([[-.16, .12], [.16, .12], [.14, .3], [-.14, .3]], 94, .006, .1)); ctx.fill(); shOff();
  if (o.fries !== false) { ctx.save(); ctx.translate(.62, .34); ctx.fillStyle = '#C0573E'; poly([[-.16, -.05], [.16, -.05], [.12, .22], [-.12, .22]]); ctx.fill(); ctx.fillStyle = '#E3B46E'; for (let i = 0; i < 5; i++) { ctx.save(); ctx.translate(-.1 + i * .05, -.05); ctx.rotate((i - 2) * .12); ctx.fillRect(-.018, -.2, .036, .22); ctx.restore(); } ctx.restore(); }
  ctx.restore();
}

// ------------------------------------------------------------------ what the phones show (drawn at 1/100: 660 × 1440)
function bgPaper(W1, H1, col) { ctx.fillStyle = col; ctx.fillRect(0, 0, W1, H1); }
function scrHome(W1, H1, t) {      // a quiet feed: what the phone shows before anything happens
  bgPaper(W1, H1, '#E9E0CC'); for (let i = 0; i < 4; i++) { ctx.save(); ctx.translate(30 + (i % 2) * 310, 160 + Math.floor(i / 2) * 520 - (t * 20) % 40); paperThumb(290, 480, i * 3 + 1, 70 + i); ctx.restore(); }
}
function scrAirAd(W1, H1, t, k = 1) {      // the air fryer slides in: 推荐
  bgPaper(W1, H1, '#E9E0CC');
  ctx.font = `700 46px ${PSANS}`; ctx.fillStyle = PP.ink; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.fillText('推荐', 40, 80); ctx.fillStyle = 'rgba(30,28,39,.4)'; ctx.fillText('关注', 170, 80);
  ctx.fillStyle = PP.ink; ctx.fillRect(40, 112, 92, 8);
  const y = lerp(H1, 160, expoOut(k));
  ctx.save(); ctx.translate(0, y);
  shOn(20, 0, 8, .4); ctx.fillStyle = '#F4C7A0'; poly(jag(rectPts(30, 0, W1 - 60, 880), 81, 3, 40)); ctx.fill(); shOff();
  airFryer(W1 / 2 - 40, 420, 430, t);
  ctx.fillStyle = PP.cream; poly(jag(rectPts(30, 880, W1 - 60, 230), 82, 3, 40)); ctx.fill();
  ctx.font = `700 64px ${PSANS}`; ctx.fillStyle = PP.ink; ctx.fillText('空气炸锅', 60, 960); ctx.font = `700 40px ${PSANS}`; ctx.fillStyle = 'rgba(30,28,39,.55)'; ctx.fillText('薯条 10 分钟就脆', 60, 1040);
  ctx.restore();
}
function scrRewind(W1, H1, t, k, secs) {      // the feed runs backwards to three days ago, stops on the air fryer, counts your seconds
  bgPaper(W1, H1, '#E9E0CC');
  const sc = (1 - expoOut(k)) * 4200;
  for (let i = -2; i < 9; i++) { const y = 140 + i * 560 + (sc % 560) - 560; const kk = (i + Math.floor(sc / 560)) * 5 + 2; ctx.save(); ctx.translate(30, y); if (i === 1 && k > .7) { shOn(20, 0, 8, .4); ctx.fillStyle = '#F7D9B6'; poly(jag(rectPts(0, 0, W1 - 60, 540), 83, 3, 40)); ctx.fill(); shOff(); airFryer((W1 - 60) / 2 - 30, 280, 300, t); } else paperThumb(W1 - 60, 540, ((kk % 8) + 8) % 8, 300 + i); ctx.restore(); }
  tag(36, 70, '3 天前', 48, { seed: 3 });
  if (secs > 0) { ctx.save(); ctx.translate(W1 - 380, 760); shOn(10, 3, 6, .4); ctx.fillStyle = '#17161E'; poly(jag(rectPts(0, 0, 350, 110), 84, 3, 20)); ctx.fill(); shOff(); ctx.font = `700 66px ${PSANS}`; ctx.fillStyle = PP.gold; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.fillText(`停留 ${secs} 秒`, 24, 57); ctx.restore(); }
}
function scrSearch(W1, H1, t, typed, done) {      // your friend's search
  bgPaper(W1, H1, '#EEE6D4');
  shOn(8, 0, 4, .3); ctx.fillStyle = '#FFFFFF'; rr(24, 60, W1 - 48, 132, 66); ctx.fill(); shOff();
  ctx.strokeStyle = PP.ink; ctx.lineWidth = 6; ctx.beginPath(); ctx.arc(95, 122, 20, 0, TAU); ctx.moveTo(110, 137); ctx.lineTo(128, 155); ctx.stroke();
  const s = '空气炸锅哪款好', n = Math.round([...s].length * typed); ctx.font = `700 64px ${PSANS}`; ctx.fillStyle = PP.ink; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.fillText([...s].slice(0, n).join('') + (done || Math.floor(t * 3) % 2 ? '' : '|'), 150, 126);
  if (done > 0) for (let i = 0; i < 4; i++) { const y = 240 + i * 290 + (1 - expoOut(clamp(done * 2 - i * .2))) * 120; ctx.save(); ctx.globalAlpha = clamp(done * 3 - i * .3); ctx.translate(30, y); ctx.fillStyle = '#FFFFFF'; poly(jag(rectPts(0, 0, W1 - 60, 260), 85 + i, 3, 30)); ctx.fill(); ctx.fillStyle = '#F4C7A0'; ctx.fillRect(20, 20, 220, 220); airFryer(130, 140, 150, t, { fries: false, steam: false }); ctx.fillStyle = 'rgba(30,28,39,.6)'; ctx.fillRect(270, 60, 300, 26); ctx.fillRect(270, 120, 220, 22); ctx.fillRect(270, 170, 260, 22); ctx.restore(); }
}
function scrPinned(W1, H1, t) { bgPaper(W1, H1, PP.night2); ctx.save(); ctx.translate(W1 / 2, H1 / 2); ctx.rotate(-.04); feedCard(-250, -330, 500, 660, -1, true, t); pushpin(0, -300, 40); ctx.restore(); }
function scrSettings(W1, H1, t, off, title = '‹  隐私设置', rows = [['个性化广告', 1], ['个性化内容推荐', 0], ['位置信息', 0], ['通讯录', 0], ['清除搜索记录', 0]]) {      // a settings page with one switch
  bgPaper(W1, H1, '#EEE6D4');
  ctx.font = `700 50px ${PSANS}`; ctx.fillStyle = PP.ink; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.fillText(title, 36, 90);
  rows.forEach(([lab, main], i) => {
    const y = 200 + i * 150; ctx.fillStyle = '#FFFFFF'; poly(jag(rectPts(24, y, W1 - 48, 130), 86 + i, 2, 30)); ctx.fill();
    ctx.font = `700 ${main ? 62 : 50}px ${PSANS}`; ctx.fillStyle = main ? PP.ink : 'rgba(30,28,39,.5)'; ctx.fillText(lab, 54, y + 66);
    if (main) { const k = smooth(off), x0 = W1 - 190, on = 1 - k; ctx.fillStyle = on > .5 ? PP.gold : '#B9B3A6'; rr(x0, y + 34, 130, 64, 32); ctx.fill(); shOn(6, 0, 3, .35); ctx.fillStyle = '#FFFFFF'; ctx.beginPath(); ctx.arc(x0 + lerp(98, 32, k), y + 66, 26, 0, TAU); ctx.fill(); shOff(); }
    else { ctx.strokeStyle = 'rgba(30,28,39,.3)'; ctx.lineWidth = 6; ctx.beginPath(); ctx.moveTo(W1 - 90, y + 50); ctx.lineTo(W1 - 70, y + 66); ctx.lineTo(W1 - 90, y + 82); ctx.stroke(); }
  });
}
function scrAdsMixed(W1, H1, t) {      // ads keep coming, just not about you
  bgPaper(W1, H1, '#E9E0CC'); const sc = (t * 260) % 600;
  for (let i = -1; i < 4; i++) { const k = (i + Math.floor(t * 260 / 600)) * 3 + 1, y = 120 + i * 600 - sc; ctx.save(); ctx.translate(30, y); paperThumb(W1 - 60, 560, k, 500 + k); ctx.restore(); tag(54, y + 60, '广告', 36, { seed: k, bg: PP.cream }); }
}

// ------------------------------------------------------------------ the dinner table world
const YOUP = [-45, 0, 0], FRP = [45, 0, 0];
const ROUTER = [60, 85, 150];
const HERO_Y = [-18, 30, -45], HERO_F = [18, 30, -45];      // where the two phones are held up
const BUB = [-28, 72, -2];
const HEAD = (() => { const o = [[-2.6, 0], [-2.5, -1.6], [-1.8, -2.8], [0, -3.4], [1.6, -3.0], [2.4, -1.8], [2.55, -.7], [3.25, .3], [2.6, .75], [2.78, 1.2], [2.55, 1.6], [2.55, 2.3], [1.6, 3.0], [1.1, 3.2], [1.1, 4.2], [-1.0, 4.2], [-1.2, 2.8], [-2.3, 1.6]]; return o; })();
const HAIR = [[-2.85, 1.0], [-2.95, -1.6], [-1.7, -3.35], [.5, -3.7], [2.2, -2.75], [2.55, -1.7], [1.4, -2.3], [-.4, -1.6], [-1.3, .1], [-2.0, 1.8]];
function person(pos, face, pal, t, o = {}) {
  card(pos[0], pos[1] + 15, pos[2], 70, 110, (w, h) => {
    ctx.translate(w / 2, 38 + (o.bob ?? 0)); ctx.scale(face, 1);
    // body
    shOn(30, 10, 16, .5); ctx.fillStyle = pal.body; poly(jag([[-14, 14], [10, 14], [18, 22], [22, 70], [-24, 70], [-20, 22]], pal.seed, .4, 6)); ctx.fill(); shOff();
    ctx.fillStyle = 'rgba(3,5,14,.18)'; poly([[-14, 14], [10, 14], [6, 20], [-12, 20]]); ctx.fill();
    // arm toward the table
    ctx.fillStyle = pal.arm; poly(jag([[6, 22], [14, 20], [30, 44], [26, 50]], pal.seed + 1, .3, 5)); ctx.fill();
    ctx.fillStyle = PP.skin; ctx.beginPath(); ctx.ellipse(29, 47, 4.2, 3.2, .5, 0, TAU); ctx.fill();
    // head (scaled from a 7-unit profile)
    ctx.save(); ctx.scale(3.4, 3.4); ctx.rotate(o.tilt ?? 0);
    shOn(16, 5, 8, .45); ctx.fillStyle = pal.skin; poly(jag(HEAD, pal.seed + 2, .05, .9)); ctx.fill(); shOff();
    ctx.fillStyle = pal.hair; poly(jag(HAIR, pal.seed + 3, .05, .8)); ctx.fill();
    ctx.fillStyle = 'rgba(140,85,58,.35)'; ctx.beginPath(); ctx.ellipse(-.4, .3, .45, .6, 0, 0, TAU); ctx.fill();
    ctx.fillStyle = PP.ink; ctx.beginPath(); ctx.ellipse(1.75, -.45, .16, .2 * (o.blink ? .15 : 1), 0, 0, TAU); ctx.fill();
    ctx.strokeStyle = 'rgba(120,60,45,.7)'; ctx.lineWidth = .14; ctx.lineCap = 'round'; ctx.beginPath(); if (o.talk) { ctx.ellipse(2.55, 1.35, .22, .12 + .14 * o.talk, 0, 0, TAU); ctx.stroke(); } else { ctx.moveTo(2.3, 1.35); ctx.lineTo(2.68, 1.32); ctx.stroke(); }
    ctx.restore();
  });
}
const PAL_YOU = { body: '#3F5C94', arm: '#36507F', skin: PP.skin, hair: '#1F1D26', seed: 11 };
const PAL_FR = { body: '#A65A42', arm: '#8F4C38', skin: '#C9926F', hair: '#3A2620', seed: 21 };
function room(t) {
  ctx.fillStyle = PP.night; ctx.fillRect(0, 0, W, H);
  // back wall paper strips (subtle)
  card(0, 60, 150, 600, 300, (w, h) => { ctx.fillStyle = '#202A4D'; ctx.fillRect(0, 0, w, h); ctx.fillStyle = 'rgba(255,255,255,.025)'; for (let i = 0; i < 20; i++) ctx.fillRect(i * 30, 0, 14, h); });
  // the window and the moon
  card(-55, 95, 150, 70, 90, (w, h) => {
    shOn(30, 10, 16, .5); ctx.fillStyle = '#121A33'; poly(jag(rectPts(0, 0, w, h), 31, .6, 12)); ctx.fill(); shOff();
    const g = ctx.createLinearGradient(0, 0, 0, h); g.addColorStop(0, '#22305C'); g.addColorStop(1, '#3A4C82'); ctx.fillStyle = g; ctx.fillRect(4, 4, w - 8, h - 8);
    shOn(10, 3, 5, .5); ctx.fillStyle = PP.cream; ctx.beginPath(); ctx.arc(w * .66, h * .3, 11, 0, TAU); ctx.fill(); shOff();
    ctx.fillStyle = '#E2D6BC'; ctx.beginPath(); ctx.arc(w * .62, h * .27, 2.4, 0, TAU); ctx.arc(w * .7, h * .34, 1.6, 0, TAU); ctx.fill();
    for (const [x, y, r] of [[12, 20, 2.6], [22, 52, 2], [50, 66, 1.8]]) { ctx.fillStyle = PP.cream; star(x, y + Math.sin(t * 1.3 + x) * .6, r); ctx.fill(); }
    ctx.fillStyle = PP.night2; ctx.fillRect(w / 2 - 1.5, 0, 3, h); ctx.fillRect(0, h * .52, w, 3);
  });
  // the router on the wall: planted in the first frame
  card(ROUTER[0], ROUTER[1], ROUTER[2], 30, 20, (w, h) => {
    ctx.strokeStyle = PP.kraftD; ctx.lineWidth = 1.4; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(6, 11); ctx.lineTo(3, 0); ctx.moveTo(24, 11); ctx.lineTo(27, 0); ctx.stroke();
    shOn(10, 3, 5, .5); ctx.fillStyle = '#E4DCCB'; poly(jag(rectPts(1, 10, 28, 9), 32, .3, 6)); ctx.fill(); shOff();
    ctx.fillStyle = (Math.floor(t * 3) % 2) ? '#8BC48A' : '#5C8F5B'; ctx.beginPath(); ctx.arc(7, 15, 1.2, 0, TAU); ctx.fill();
  });
  // the pendant lamp: cord, shade, a soft cone of light
  const sw = Math.sin(t * 1.1) * 1.6, top = P(12, 200, -5), sh = P(12 + sw, 72, -5);
  if (top && sh) { ctx.strokeStyle = '#0E1328'; ctx.lineWidth = Math.max(2, .5 * sh[2]); ctx.beginPath(); ctx.moveTo(top[0], top[1]); ctx.lineTo(sh[0], sh[1]); ctx.stroke(); }
  card(12 + sw, 66, -5, 44, 16, (w, h) => {
    ctx.fillStyle = 'rgba(255,226,170,.10)'; ctx.beginPath(); ctx.moveTo(6, h); ctx.lineTo(w - 6, h); ctx.lineTo(w + 60, h + 120); ctx.lineTo(-60, h + 120); ctx.closePath(); ctx.fill();
    shOn(16, 4, 8, .5); ctx.fillStyle = PP.kraft; poly(jag([[14, 0], [w - 14, 0], [w, h], [0, h]], 33, .3, 6)); ctx.fill(); shOff();
    ctx.fillStyle = '#FFE9B8'; ctx.beginPath(); ctx.ellipse(w / 2, h, 9, 2.5, 0, 0, TAU); ctx.fill();
  });
}
function table(t, o = {}) {
  // the top, seen a little from above
  card(0, -11, -10, 190, 14, (w, h) => {
    shOn(24, 0, -6, .45); ctx.fillStyle = '#E9DFC9'; poly(jag([[8, 0], [w - 8, 0], [w, h], [0, h]], 41, .3, 10)); ctx.fill(); shOff();
    // plates, a dish, cups, chopsticks
    for (const [x, rx] of [[w / 2 - 30, 13], [w / 2 + 30, 13]]) { shOn(6, 0, 2, .3); ctx.fillStyle = '#F7F1E4'; ctx.beginPath(); ctx.ellipse(x, h * .55, rx, 3.6, 0, 0, TAU); ctx.fill(); shOff(); ctx.strokeStyle = 'rgba(30,28,39,.15)'; ctx.lineWidth = .5; ctx.beginPath(); ctx.ellipse(x, h * .55, rx * .7, 2.4, 0, 0, TAU); ctx.stroke(); }
    shOn(8, 0, 2, .3); ctx.fillStyle = '#5C86C4'; ctx.beginPath(); ctx.ellipse(w / 2, h * .5, 18, 5, 0, 0, TAU); ctx.fill(); shOff();
    for (let i = 0; i < 9; i++) { ctx.fillStyle = i % 3 ? '#5F9E5A' : '#D9774E'; ctx.beginPath(); ctx.ellipse(w / 2 - 12 + i * 3 + Math.sin(i) * 2, h * .45 + Math.cos(i * 2) * 1.2, 2.6, 1.4, i, 0, TAU); ctx.fill(); }
    for (const x of [w / 2 - 52, w / 2 + 50]) { ctx.fillStyle = '#E4DCCB'; ctx.fillRect(x - 3, h * .2, 6, 7); ctx.fillStyle = 'rgba(30,28,39,.15)'; ctx.fillRect(x - 3, h * .2, 6, 1.4); }
    ctx.strokeStyle = PP.kraftD; ctx.lineWidth = .8; ctx.beginPath(); ctx.moveTo(w / 2 - 44, h * .82); ctx.lineTo(w / 2 - 22, h * .7); ctx.moveTo(w / 2 - 44, h * .9); ctx.lineTo(w / 2 - 21, h * .76); ctx.stroke();
  });
  // the tablecloth hanging in front
  card(0, -62, -12, 196, 100, (w, h) => {
    shOn(20, 0, -6, .4); ctx.fillStyle = '#D9C9A8'; const pts = [[0, 0], [w, 0]]; for (let x = w; x >= 0; x -= 12) pts.push([x, h - 6 + Math.sin(x * .2) * 3]); poly(pts); ctx.fill(); shOff();
    ctx.strokeStyle = 'rgba(30,28,39,.12)'; ctx.lineWidth = 1.2; for (let i = 1; i < 8; i++) { ctx.beginPath(); ctx.moveTo(i * w / 8, 4); ctx.lineTo(i * w / 8 + Math.sin(i) * 4, h - 8); ctx.stroke(); }
  });
}
function lyingPhone(x, y, z, faceUp, t) {
  card(x, y, z, 9, 3, (w, h) => { shOn(8, 1, 3, .5); ctx.fillStyle = '#15141B'; rr(0, 0, w, h, 1); ctx.fill(); shOff(); ctx.fillStyle = faceUp ? 'rgba(244,213,162,.6)' : '#24232C'; rr(.4, .3, w - .8, h - .6, .7); ctx.fill(); });
}
// a phone held up, facing you; content(W1, H1) draws the screen; flip 0..1 turns it from its back to its face
function phone(x, y, z, t, content, o = {}) {
  const sx = o.flip === undefined ? 1 : Math.abs(Math.cos(o.flip * Math.PI)), back = o.flip !== undefined && o.flip < .5;
  const p = P(x, y, z); if (!p) return;
  ctx.save(); ctx.translate(p[0], p[1]); ctx.rotate(o.rot ?? 0); ctx.scale(Math.max(.02, sx), 1); ctx.translate(-p[0], -p[1]);
  card(x, y, z, PHONE.w, PHONE.h, (w, h) => {
    shOn(30, 10, 18, .55); ctx.fillStyle = '#15141B'; rr(0, 0, w, h, .9); ctx.fill(); shOff();
    if (back) { ctx.fillStyle = '#2B2A34'; rr(.3, .3, w - .6, h - .6, .7); ctx.fill(); ctx.fillStyle = '#15141B'; rr(.6, .6, 2.2, 2.2, .5); ctx.fill(); return; }
    ctx.fillStyle = '#0B0B10'; for (let i = -2; i <= 2; i++) { ctx.beginPath(); ctx.ellipse(w / 2 + i * .32, h - .32, .09, .06, 0, 0, TAU); ctx.fill(); }      // the microphone holes
    if (o.sealed > 0) { const k = expoOut(o.sealed); ctx.save(); ctx.translate(w / 2, h - .32); ctx.rotate(-.06); ctx.scale(k, k); shOn(4, .5, 1, .4); ctx.fillStyle = PP.kraft; poly(jag(rectPts(-1.3, -.32, 2.6, .64), 160, .03, .3)); ctx.fill(); shOff(); ctx.strokeStyle = PP.ink; ctx.lineWidth = .07; ctx.beginPath(); ctx.moveTo(-.2, -.16); ctx.lineTo(.2, .16); ctx.moveTo(.2, -.16); ctx.lineTo(-.2, .16); ctx.stroke(); ctx.restore(); }      // sealed
  });
  if (!back) card(x, y + .2, z - .01, SCREEN.w, SCREEN.h, (w, h) => { ctx.save(); rr(0, 0, w, h, .6); ctx.clip(); ctx.scale(1 / 100, 1 / 100); content(w * 100, h * 100); ctx.restore(); });
  ctx.restore();
}
// the speech bubble: drawn in screen space from its world centre; tail to a world point; inner() draws the inside (local 0..w, 0..h px)
function bubble(t, c, tailTo, wcm, hcm, inner, o = {}) {
  const p = P(...c), q = P(...tailTo); if (!p || !q) return; const s = p[2], w = wcm * s, h = hcm * s;
  ctx.save(); ctx.translate(p[0], p[1]); ctx.rotate(-.03 + Math.sin(t * 1.3) * .01); ctx.scale(o.pop ?? 1, o.pop ?? 1);
  const tx = q[0] - p[0], ty = q[1] - p[1];
  shOn(26, 8, 14, .5); ctx.fillStyle = PP.cream; poly(jag([[-w / 2, -h / 2], [w / 2, -h / 2], [w / 2, h / 2], [-w * .05, h / 2], [tx * .55, ty * .55], [-w * .22, h / 2], [-w / 2, h / 2]], 61, s * .4, s * 6)); ctx.fill(); shOff();
  ctx.translate(-w / 2, -h / 2); inner(w, h, s);
  ctx.restore();
}
function sayText(w, h, s, txt, n) { ctx.font = `700 ${Math.round(5.4 * s)}px ${PSANS}`; ctx.fillStyle = PP.ink; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText([...txt].slice(0, n).join(''), w / 2, h / 2 + s * .3); }
function dots(w, h, s, t) { for (let i = 0; i < 3; i++) { ctx.fillStyle = PP.ink; ctx.beginPath(); ctx.arc(w / 2 + (i - 1) * 5 * s, h / 2 - Math.max(0, Math.sin(t * 8 - i)) * s * 1.2, 1.2 * s, 0, TAU); ctx.fill(); } }

// ------------------------------------------------------------------ the listening run (as the audience imagines it)
// z: the microphone port (0–60) → a paper membrane (70) → a tube (80–230) → a machine room (260–420) with a paper screen
const TXT = [...'最近想买个空气炸锅'];
function letterTag(p, ch, sz, i) { if (!p) return; const s = sz * p[2]; if (s < 2) return; ctx.save(); ctx.translate(p[0], p[1]); ctx.rotate((hash(i, 3) - .5) * .25); shOn(s * .3, s * .08, s * .14, .45); ctx.fillStyle = PP.gold; poly(jag(rectPts(-s * .55, -s * .6, s * 1.1, s * 1.2), 120 + i, s * .03, s * .3)); ctx.fill(); shOff(); ctx.font = `700 ${Math.round(s * .8)}px ${PSANS}`; ctx.fillStyle = PP.ink; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(ch, 0, s * .04); ctx.restore(); }
const LROW = i => [-48 + i * 12, 4, 399];
function letterPos(t, i) {
  const t0 = C.words + i * .1, a = ev(t, t0, .9);
  if (t < C.suck + .6) { const k = ease(a); return { p: [lerp(-30 + i * 7, 0, k), lerp(-40 + (i % 2) * 6, 0, k) + Math.sin(k * Math.PI) * 6, lerp(CZ + 8, 68, k)], sz: lerp(6, 1.5, k), show: t >= t0 }; }
  if (t < C.server) { const u = (i - 4) * .7 + t * 2.2; return { p: [CX + Math.cos(u) * 6, CY + Math.sin(u) * 5, CZ + 30 + i * 1.5], sz: 3.2, show: true }; }
  const k = ease(ev(t, C.server + i * .06, .8)), r = LROW(i), u = (i - 4) * .7 + t * 2.2, st = [CX + Math.cos(u) * 6, CY + Math.sin(u) * 5, CZ + 30 + i * 1.5];
  return { p: [lerp(st[0], r[0], k), lerp(st[1], r[1], k), lerp(st[2], r[2], k)], sz: lerp(3.2, 10, k), show: true };
}
function ring(z, r, col, seed) { const p = P(0, 0, z); if (!p) return; const R = r * p[2]; ctx.fillStyle = col; ctx.beginPath(); ctx.rect(0, 0, W, H); jag(Array.from({ length: 24 }, (_, i) => [p[0] + Math.cos(i / 24 * TAU) * R, p[1] + Math.sin(i / 24 * TAU) * R]), seed, R * .02, R * .3).forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)); ctx.closePath(); ctx.fill('evenodd'); }
function listenWorld(t) {
  ctx.fillStyle = '#0B0F1F'; ctx.fillRect(0, 0, W, H);
  // the machine room, far away at the end of the tube
  for (const z of [400, 360, 320, 280]) for (const sd of [-1, 1]) card(sd * 72, 0, z, 40, 120, (w, h) => {
    shOn(20, 6, 10, .5); ctx.fillStyle = '#1C2546'; poly(jag(rectPts(0, 0, w, h), (z + sd * 7) | 0, .3, 8)); ctx.fill(); shOff();
    for (let r = 0; r < 14; r++) for (let c = 0; c < 3; c++) { const on = hash(z * 3 + r * 7 + c + (sd > 0 ? 99 : 0), Math.floor(t * 4 + r * .3 + c)) > .45; ctx.fillStyle = on ? ((r + c) % 4 ? PP.cream : '#96B4EB') : '#141A30'; ctx.fillRect(6 + c * 11, 8 + r * 7.8, 6, 2.6); }
  });
  card(0, 4, 405, 150, 84, (w, h) => {      // the paper screen
    shOn(30, 8, 14, .55); ctx.fillStyle = '#F2EBDA'; poly(jag(rectPts(0, 0, w, h), 140, .5, 10)); ctx.fill(); shOff();
    ctx.fillStyle = '#2F4175'; ctx.fillRect(0, 0, w, 11); ctx.font = `700 6px ${PSANS}`; ctx.fillStyle = PP.cream; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.fillText('听到的话', 5, 5.8);
  });
  // the tube, far to near; the membrane; the port
  for (let z = 230; z >= 80; z -= 12) if (z > CZ + .5) ring(z, 22, (z / 12) % 2 ? '#26335E' : '#1E2A4E', z * 3);
  if (70 > CZ + .5) {
    const p = P(0, 0, 70); if (p) {
      const s = p[2], R = 30 * s, hole = 27 * ease(ev(t, C.suck - .1, .6)) * s;
      if (hole < R * .95) {
        ctx.strokeStyle = PP.kraftD; ctx.lineWidth = R * .1; ctx.beginPath(); ctx.arc(p[0], p[1], R * 1.05, 0, TAU); ctx.stroke();
        ctx.save(); ctx.beginPath(); ctx.arc(p[0], p[1], R, 0, TAU); if (hole > 1) jag(Array.from({ length: 14 }, (_, i) => [p[0] + Math.cos(i / 14 * TAU) * hole, p[1] + Math.sin(i / 14 * TAU) * hole]), 77, hole * .15, hole * .5).forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)); ctx.closePath(); ctx.fillStyle = PP.cream; ctx.fill('evenodd');
        ctx.clip('evenodd'); ctx.strokeStyle = 'rgba(30,28,39,.16)'; ctx.lineWidth = Math.max(1, .35 * s); for (let i = -8; i <= 8; i++) { ctx.beginPath(); ctx.moveTo(p[0] + i * R / 9, p[1] - R); ctx.lineTo(p[0] + i * R / 9, p[1] + R); ctx.stroke(); } ctx.restore();
        const aw = ev(t, C.listen - .3, .5); for (let i = 0; i < 4; i++) { const u = (t * 1.3 + i / 4) % 1; ctx.strokeStyle = `rgba(241,232,213,${(1 - u) * .7 * aw})`; ctx.lineWidth = 3 * s * (1 - u) + 2; ctx.beginPath(); ctx.arc(p[0], p[1], R * (1.12 + u * 1.3), 0, TAU); ctx.stroke(); }
      }
    }
  }
  for (let z = 60; z >= 0; z -= 10) if (z > CZ + .5) ring(z, 34, `rgb(${lerp(36, 20, z / 60) | 0},${lerp(46, 27, z / 60) | 0},${lerp(84, 52, z / 60) | 0})`, z * 7 + 1);
  // your words
  TXT.forEach((ch, i) => { const L = letterPos(t, i); if (!L.show || L.p[2] <= CZ + .5) return; letterTag(P(...L.p), ch, L.sz, i); });
  // the keyword lights up: a gold ring round 空气炸锅, its tag
  if (t >= C.hit) {
    const a = P(LROW(5)[0] - 7, LROW(5)[1] + 8, 398), b = P(LROW(8)[0] + 7, LROW(8)[1] - 8, 398), k = ease(ev(t, C.hit, .5));
    if (a && b) { const cx = (a[0] + b[0]) / 2, cy = (a[1] + b[1]) / 2, rx = (b[0] - a[0]) / 2 + 10, ry = (b[1] - a[1]) / 2 + 8; ctx.strokeStyle = PP.gold; ctx.lineWidth = Math.max(5, .9 * a[2]); ctx.lineCap = 'round'; ctx.beginPath(); ctx.ellipse(cx, cy, rx, ry, -.04, -Math.PI / 2, -Math.PI / 2 + TAU * k); ctx.stroke(); if (k >= 1) tag(cx, cy - ry - 30, '关键词：空气炸锅', Math.max(28, Math.round(4.2 * a[2])), { center: true, seed: 14 }); }
  }
  // the ad flies back, carried in front of the camera all the way out
  if (t >= C.back) {
    const k = ease(ev(t, C.back, .7)), z = lerp(396, CZ + 20, k), x = lerp(40, CX + 3, k), y = lerp(4, CY - 2, k);
    card(x, y, z, 26, 34, (w, h) => { ctx.translate(w / 2, h / 2); ctx.rotate(Math.sin(t * 3) * .05); ctx.translate(-w / 2, -h / 2); ctx.save(); ctx.scale(1 / 10, 1 / 10); feedCard(0, 0, w * 10, h * 10, -1, false, t); ctx.restore(); tag(1, 3, '广告', 2.6, { seed: 15, bg: PP.cream }); });
  }
}

// ------------------------------------------------------------------ the feed (inside your phone)
function feedCard(x, y, w, h, k, lit, t) {
  ctx.save(); ctx.translate(x, y);
  if (k < 0) { shOn(14, 4, 8, .45); ctx.fillStyle = '#F4C7A0'; poly(jag(rectPts(0, 0, w, h), 501, 3, 40)); ctx.fill(); shOff(); airFryer(w / 2 - 20, h * .46, Math.min(w, h) * .6, t); ctx.font = `700 ${Math.round(w * .09)}px ${PSANS}`; ctx.fillStyle = PP.ink; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.fillText('空气炸锅', w * .07, h * .9); if (lit) { ctx.strokeStyle = PP.gold; ctx.lineWidth = 8; poly(jag(rectPts(0, 0, w, h), 502, 2, 40)); ctx.stroke(); } }
  else { ctx.fillStyle = 'rgba(3,5,14,.4)'; ctx.fillRect(6, 10, w, h); paperThumb(w, h, k, 600 + k); }
  ctx.restore();
}
function pushpin(x, y, r) { shOn(8, 3, 6, .5); ctx.fillStyle = PP.kraftD; ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.fill(); shOff(); ctx.fillStyle = '#E2B07A'; ctx.beginPath(); ctx.arc(x - r * .25, y - r * .25, r * .45, 0, TAU); ctx.fill(); }
const FEEDC = (() => { const r = mulberry32(77), a = []; for (let i = 0; i < 60; i++) a.push({ h: 520 + r() * 300, k: (i * 5 + 3) % 8, air: i % 7 === 3 }); return a; })();
function feedWorld(t) {
  ctx.fillStyle = PP.night2; ctx.fillRect(0, 0, W, H);
  const t0 = C.feed, tp = C.pin, u = clamp((t - t0) / (tp - t0));
  const scroll = 2600 * (tp - t0) * (u - u * u / 2) + 400;      // decelerates to a stop at the pin
  const col = [[], []], cw = 500, gx = 26; let ys = [0, 160];
  FEEDC.forEach((c, i) => { const j = ys[0] <= ys[1] ? 0 : 1; col[j].push({ ...c, i, y: ys[j] }); ys[j] += c.h + 24; });
  const pinI = (() => { let best = -1, bd = 1e9; col.flat().forEach(c => { if (!c.air) return; const cy = c.y - scroll + c.h / 2 + 200, d = Math.abs(cy - H / 2); if (d < bd) { bd = d; best = c.i; } }); return best; })();
  const fall = ev(t, tp, 1.0);
  col.forEach((cs, j) => cs.forEach(c => {
    let x = gx + j * (cw + 28), y = c.y - (t < tp ? scroll : 2600 * (tp - t0) * .5 + 400) + 200, rot = 0, sc = 1;
    if (y > H + 50 || y + c.h < -50) return;
    const pinned = c.i === pinI && t >= tp;
    if (t >= tp && !pinned) { y += 2400 * fall * fall * (.6 + hash(c.i, 4) * .6); rot = fall * (hash(c.i, 5) - .5) * 1.4; }
    if (pinned) { const k = expoOut(ev(t, tp, .4)), m = ease(ev(t, tp, .6)); sc = 1 + .12 * k + .5 * ease(ev(t, tp + .4, C.rev - tp - .4)); rot = Math.sin(t * 2) * .03; x = lerp(x, W / 2 - cw / 2, m); y = lerp(y, H / 2 - c.h / 2, m); }
    ctx.save(); ctx.translate(x + cw / 2, y + c.h / 2); ctx.rotate(rot); ctx.scale(sc, sc);
    feedCard(-cw / 2, -c.h / 2, cw, c.h, c.air ? -1 : c.k, c.air, t);
    if (!c.air && !pinned) { ctx.fillStyle = 'rgba(18,24,50,.45)'; ctx.fillRect(-cw / 2, -c.h / 2, cw, c.h); }
    if (pinned) pushpin(0, -c.h / 2 + 30, 34);
    ctx.restore();
  }));
  tag(60, 480, `今天已刷 ${Math.round(lerp(281, 312, u))} 条`, 46, { seed: 8, bg: '#17161E', fg: PP.cream });
}

// ------------------------------------------------------------------ the shot
const KT = [      // the table world camera (CX, CY, CZ)
  [0, 0, 22, -125], [4.75, -3, 24, -100],
  [6.4, HERO_Y[0], HERO_Y[1], -62], [8.9, HERO_Y[0], HERO_Y[1] - 1.5, -58], [C.dive, HERO_Y[0], HERO_Y[1] - PHONE.h / 2 + .32, HERO_Y[2] - .03],
];
const KC = [      // back out of the microphone: the switch, the reversal, the clues
  [C.but, HERO_Y[0], HERO_Y[1] - PHONE.h / 2 + .6, HERO_Y[2] - 2.5], [C.but + .8, HERO_Y[0], HERO_Y[1], -61], [C.again + .8, HERO_Y[0] + .4, HERO_Y[1] + .3, -57],
  [C.clue + .9, 0, 40, -128], [C.you6 - .2, -4, 37, -112], [C.you6 + .6, HERO_Y[0], HERO_Y[1], -61], [C.six + .4, HERO_Y[0] + .5, HERO_Y[1] + .4, -59.5],
  [C.friend + .4, HERO_F[0], HERO_F[1], -61], [C.search + .9, HERO_F[0] - 1.2, HERO_F[1] + .8, -55],
  [C.table, 6, 42, -118], [C.feed - .55, 5, 41, -112], [C.feed, HERO_Y[0], HERO_Y[1] + .2, HERO_Y[2] - 6.2],
];
const KB = [
  [C.rev, HERO_Y[0], HERO_Y[1] + .2, HERO_Y[2] - 6.2], [C.rev + .8, -28, 71, -62], [C.rev2 + .3, -27.5, 70.5, -58], [C.rev2 + 1.3, -2, 50, -150], [C.tip - .1, 1, 52, -128],
  [C.tip + .8, HERO_Y[0], HERO_Y[1], -61], [C.home - .1, HERO_Y[0] + .6, HERO_Y[1] + .3, -58],
  [C.home + 1.6, 0, 22, -125], [DUR, -1.5, 23, -106],
];
function yourPhonePos(t) {      // on the table, lifted and turned to face you, held up; put back at the end
  const up = ease(ev(t, C.phone, 1.1)), down = ease(ev(t, C.home, 1.2)), k = up * (1 - down);
  return { x: lerp(-14, HERO_Y[0], k), y: lerp(-12, HERO_Y[1], k), z: lerp(-11, HERO_Y[2], k), flip: clamp(.5 + (ev(t, C.phone + .2, .7) - .5) - (t >= C.home ? ev(t, C.home + .2, .6) : 0)), k };
}
function friendPhonePos(t) {
  const up = ease(ev(t, C.friend - .5, .9)), down = ease(ev(t, C.home, 1.2)), k = up * (1 - down);
  return { x: lerp(30, HERO_F[0], k), y: lerp(14, HERO_F[1], k), z: lerp(-6, HERO_F[2], k), flip: clamp(ev(t, C.friend - .3, .6) - (t >= C.home ? ev(t, C.home + .2, .6) : 0)), k };
}
function yourScreen(t) {
  return (W1, H1) => {
    if (t < C.push) return scrHome(W1, H1, t);
    if (t < C.but) return scrAirAd(W1, H1, t, ev(t, C.push, .6));
    if (t < C.micoff) return scrAirAd(W1, H1, t, ev(t, C.but - .1, .6));
    if (t < C.again) return scrSettings(W1, H1, t, ev(t, C.off, .25), '‹  应用权限', [['麦克风', 1], ['相机', 0], ['位置信息', 0], ['通讯录', 0], ['照片', 0]]);
    if (t < C.you6) return scrAirAd(W1, H1, t, ev(t, C.again, .6));
    if (t < C.feed) { const secs = t < C.six - 1.25 ? 0 : Math.min(6, 1 + Math.floor((t - (C.six - 1.25)) / .25)); return scrRewind(W1, H1, t, ev(t, C.you6, 1.3), secs); }
    if (t < C.tip) return scrPinned(W1, H1, t);
    if (t < C.fewer) return scrSettings(W1, H1, t, ev(t, C.toggle, .25));
    if (t < C.home) return scrAdsMixed(W1, H1, t);
    return scrAirAd(W1, H1, t, 1);
  };
}
function tableWorld(t, o = {}) {
  room(t);
  const talking = t > C.say - .2 && t < C.say + 1.6 ? Math.abs(Math.sin(t * 14)) : 0;
  person(YOUP, 1, PAL_YOU, t, { talk: talking, bob: Math.sin(t * 1.4) * .6, blink: (t % 3.7) < .12 });
  person(FRP, -1, PAL_FR, t, { bob: Math.sin(t * 1.2 + 1) * .6, blink: (t % 4.3) < .12, tilt: t > C.say + .4 && t < C.say + 2 ? .06 : 0 });
  // the Wi-Fi: ripples from the router across the room
  const wk = ev(t, C.wifi, .3) * (1 - ev(t, C.feed - .4, .4));
  const rp = P(...ROUTER);
  if (wk > 0 && rp) for (let i = 0; i < 4; i++) { const u = ((t - C.wifi) * .7 + i / 4) % 1; if (t - C.wifi < i * .5) continue; ctx.strokeStyle = `rgba(241,232,213,${(1 - u) * .75 * wk})`; ctx.lineWidth = 26 * (1 - u) + 4; ctx.beginPath(); ctx.arc(rp[0], rp[1] - 20, 40 + u * 1500, Math.PI * .55, Math.PI * 1.05); ctx.stroke(); }
  table(t);
  const yp = yourPhonePos(t), fp = friendPhonePos(t);
  if (yp.k < .02) {      // face down on the table, yet it seems to be listening: a light leak that pulses, ripples when you speak
    const lp = P(-14, -12, -11);
    if (lp) { const s = lp[2], pulse = .5 + .5 * Math.sin(t * 3.2), talkK = ev(t, C.say - .3, .3) * (1 - ev(t, C.say + 1.8, .5));
      ctx.fillStyle = `rgba(255,214,140,${.35 + .3 * pulse})`; ctx.beginPath(); ctx.ellipse(lp[0], lp[1] + 1.2 * s, 4.8 * s, .7 * s, 0, 0, TAU); ctx.fill();
      for (let i = 0; i < 3; i++) { const u = (t * .9 + i / 3) % 1, a = (1 - u) * (.3 + .45 * talkK); ctx.strokeStyle = `rgba(27,36,67,${a})`; ctx.lineWidth = Math.max(3, .6 * s * (1 - u)); ctx.beginPath(); ctx.ellipse(lp[0], lp[1] - s, (7 + u * 14) * s, (3 + u * 6) * s, 0, Math.PI * 1.05, Math.PI * 1.95); ctx.stroke(); } }
    lyingPhone(-14, -12, -11, false, t);
  } else phone(yp.x, yp.y, yp.z, t, yourScreen(t), { flip: yp.flip, sealed: t < C.home ? ev(t, C.off + .15, .3) : 0 });
  if (fp.k < .02) phone(30, 14, -6, t, W1 => scrHome(W1, 1440, t), { flip: 0, rot: .1 }); else phone(fp.x, fp.y, fp.z, t, (W1, H1) => scrSearch(W1, H1, t, ev(t, C.friend + .4, C.search - C.friend - .4), ev(t, C.search, .8)), { flip: fp.flip });
  // the beads: your 6 seconds (gold), your friend's search (cream); then tied together
  const g = ev(t, C.gang, 1.0), lift = (t0) => expoOut(ev(t, t0, .7));
  const yb = [lerp(HERO_Y[0], -5, ease(g)), HERO_Y[1] + 9 + 5 * lift(C.six) + Math.sin(t * 2) * .5 + 6 * ease(g), HERO_Y[2]];
  const fb = [lerp(HERO_F[0], 5, ease(g)), HERO_F[1] + 9 + 5 * lift(C.search) + Math.sin(t * 2 + 1) * .5 + 6 * ease(g), HERO_F[2]];
  const showB = t < C.feed - .3 || (t >= C.rev && t < C.tip);
  const ybp = t >= C.six && showB ? P(...yb) : null, fbp = t >= C.search && showB ? P(...fb) : null;
  // the same Wi-Fi: a dashed thread between the phones, with its tag
  if (t >= C.table && t < C.feed - .3) { const a = P(fp.x - 3, fp.y + 8, fp.z), b = P(yp.x + 3, yp.y + 8, yp.z); if (a && b) { const k = ev(t, C.table, .5); dashed(b, [lerp(b[0], a[0], k), lerp(b[1], a[1], k)], Math.max(3, .35 * a[2]), t); if (k >= 1) tag((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + 60, '同一个 Wi-Fi', Math.max(36, Math.round(1.6 * a[2])), { center: true, seed: 9 }); } }
  if (ybp && fbp && g > 0) { thread([[ybp[0], ybp[1]], [(ybp[0] + fbp[0]) / 2, Math.max(ybp[1], fbp[1]) + 30], [fbp[0], fbp[1]]], Math.max(4, .5 * ybp[2]), t); if (g >= .8 && t < C.feed - .3) tag((ybp[0] + fbp[0]) / 2, Math.max(ybp[1], fbp[1]) + 80, '可能是一伙的', Math.max(38, Math.round(1.8 * ybp[2])), { center: true, seed: 10 }); }
  if (ybp) bead(ybp[0], ybp[1], Math.max(8, 1.4 * ybp[2]) * expoOut(ev(t, C.six, .3)));
  if (fbp) bead(fbp[0], fbp[1], Math.max(8, 1.4 * fbp[2]) * expoOut(ev(t, C.search, .3)), 'cream');
  // the speech bubble
  const youMouth = [YOUP[0] + 9, 28, 0];
  if (t < C.dive || t >= C.home) {
    const pop = t < C.dive ? 1 - expoIn(ev(t, C.phone + .1, .5)) : expoOut(ev(t, C.home + .8, .5)); 
    const txt = '最近想买个空气炸锅', n = t < C.dive ? Math.ceil(9 * clamp((t - C.say) / 1.3)) : 9;
    if (pop > .01) bubble(t, BUB, youMouth, 56, 20, (w, h, s) => { if (n <= 0) dots(w, h, s, t); else sayText(w, h, s, txt, n); }, { pop });
  }
  if (t >= C.rev && t < C.tip) {      // the same bubble, made of the three clues
    const k = expoOut(ev(t, C.rev + .4, .6));
    bubble(t, BUB, youMouth, 62, 34, (w, h, s) => {
      ctx.save(); ctx.globalAlpha = k;
      ctx.save(); ctx.translate(w * .06, h * .14); ctx.rotate(-.05); feedCard(0, 0, 15 * s, 20 * s, -1, false, t); ctx.restore();
      ctx.save(); ctx.translate(w * .08 + 13 * s, h * .1 + 17 * s); ctx.font = `700 ${Math.round(2.6 * s)}px ${PSANS}`; ctx.fillStyle = '#17161E'; ctx.fillRect(0, 0, 11 * s, 4 * s); ctx.fillStyle = PP.gold; ctx.textBaseline = 'middle'; ctx.fillText('停留 6 秒', s * .8, 2 * s); ctx.restore();
      ctx.save(); ctx.translate(w * .4, h * .22); ctx.rotate(.04); ctx.fillStyle = '#FFFFFF'; rr(0, 0, 33 * s, 6.5 * s, 3.2 * s); ctx.fill(); ctx.font = `700 ${Math.round(3 * s)}px ${PSANS}`; ctx.fillStyle = PP.ink; ctx.textBaseline = 'middle'; ctx.fillText('🔍 空气炸锅哪款好'.replace('🔍 ', ''), 2 * s, 3.3 * s); ctx.restore();
      ctx.save(); ctx.translate(w * .55, h * .48); ctx.rotate(.06); feedCard(0, 0, 13 * s, 15 * s, -1, true, t); pushpin(6.5 * s, 1.5 * s, 1.4 * s); ctx.restore();
      ctx.restore();
    });
    if (t >= C.rev2) {      // its tail splits into three threads: your phone, your friend's phone, the router
      const b = P(BUB[0] - 2, BUB[1] - 17, BUB[2]), k2 = ev(t, C.rev2, .7);
      for (const tg of [[yp.x, yp.y + 8, yp.z], [fp.x, fp.y + 8, fp.z], [ROUTER[0], ROUTER[1], ROUTER[2]]]) { const e = P(...tg); if (b && e) thread([[b[0], b[1]], [lerp(b[0], e[0], .5), lerp(b[1], e[1], .5) + 60], [lerp(b[0], e[0], k2), lerp(b[1], e[1], k2)]], 7, t); }
    }
  }
  // the law's tag beside the phone; "数量不变"
  const tagAt = HERO_Y[1] + PHONE.h / 2 + 1.1;
  if (t >= C.law && t < C.guess) { const p = P(HERO_Y[0], tagAt, HERO_Y[2] - .5); if (p) tag(p[0], p[1], '个人信息保护法 第 24 条', Math.min(46, Math.round(.75 * p[2])), { seed: 12, rot: .03, center: true, scale: expoOut(ev(t, C.law, .4)) }); }
  if (t >= C.guess && t < C.home) { const p = P(HERO_Y[0], tagAt, HERO_Y[2] - .5); if (p) tag(p[0], p[1], '数量不变 · 不再按你猜', Math.min(46, Math.round(.75 * p[2])), { seed: 13, rot: -.03, center: true, scale: expoOut(ev(t, C.guess, .4)) }); }
  // your thumb on the switch
  for (const tc of [C.off, C.toggle]) if (t > tc - .7 && t < tc + .8) { const k = ease(ev(t, tc - .7, .55)), r = expoIn(ev(t, tc + .35, .45)), tap = Math.sin(clamp((t - tc + .05) / .2) * Math.PI);
    thumbAt(HERO_Y[0] + 2.3 + r * 2, lerp(HERO_Y[1] - 14, HERO_Y[1] + 3.6, k) - r * 14, HERO_Y[2] - .5 - tap * .3, -.3); }
}
function shot(t) {
  if (t < C.dive) { [CX, CY, CZ] = t < KT[3][0] ? kf(t, KT, smooth) : kf(t, KT.slice(3), expoIn); F = 1000; CX += .3 * Math.sin(t * .6) * (1 - ev(t, KT[3][0], .5)); tableWorld(t); return 'S0'; }
  if (t < C.but) {      // the listening run: into the microphone, through the tube, the machine room, and the ad back out
    const KL = [[C.dive, -25], [C.listen + .6, 4], [C.suck, 12], [C.server, 250], [C.hit + .3, 288], [C.back + .3, 292], [C.but, -6]];
    CZ = t < KL[5][0] ? kf(t, KL)[0] : kf(t, KL.slice(5), expoIn)[0]; CX = 1.5 * Math.sin(t * .5); CY = 1.2 * Math.sin(t * .4); F = 1000;
    listenWorld(t); return 'S2';
  }
  if (t < C.feed) { [CX, CY, CZ] = t < KC[1][0] ? kf(t, KC, expoOut) : kf(t, KC); F = 1000; tableWorld(t); return t < C.clue ? 'S2b' : 'S3'; }
  if (t < C.rev) { feedWorld(t); return 'S4'; }
  [CX, CY, CZ] = kf(t, KB); F = 1000; CX += .3 * Math.sin(t * .6); tableWorld(t); return t < C.tip ? 'S5' : t < C.home ? 'S6' : 'S7';
}

// ------------------------------------------------------------------ overlays
STY.title = t => {
  ctx.save(); ctx.translate(0, Math.sin(t * .8) * 3);
  strip(-60, 110, 620, 170, 5, -.022);
  ctx.save(); ctx.translate(-60, 110); ctx.rotate(-.022); ctx.font = `700 120px ${PSERIF}`; ctx.fillStyle = PP.ink; ctx.textBaseline = 'alphabetic'; ctx.textAlign = 'left'; ctx.fillText('你刚说完', 128, 132); ctx.restore();
  ctx.save(); ctx.translate(78, 300); ctx.rotate(.025); shOn(14, 4, 8, .45); ctx.fillStyle = PP.kraft; poly(jag(rectPts(0, 0, 250, 58), 6, 3, 18)); ctx.fill(); shOff();
  ctx.font = `700 32px ${PSANS}`; ctx.fillStyle = PP.ink; ctx.textBaseline = 'middle'; ctx.fillText('你按下去之后', 26, 30); ctx.restore();
  ctx.restore();
};
window.seek = function (t) {
  t = clamp(t, 0, DUR - 1 / FPS);
  ctx.setTransform(SS, 0, 0, SS, 0, 0); ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over'; shOff(); ctx.setLineDash([]);
  const s = shot(t);
  if (COVER) { if (STY.post) STY.post(t); const y1 = COVER === '34' ? 400 : 330, y2 = COVER === '34' ? 1380 : 1770; STY.hero(t, -5, [{ parts: [['手机在', 'b'], ['偷听你', 'a'], ['吗？', 'b']], size: 118 }], 60, y1); STY.hero(t, -5, [{ parts: [['关了麦克风，', 'b'], ['它照样推', 'a']], size: 82 }], 60, y2); return true; }
  const H_ = (t0, parts, size = 110, y = 330) => STY.hero(t, t0, [{ parts, size }], 72, y);
  if (s === 'S0' && t < C.dive - .6) STY.title(t);
  if (s === 'S2' && t >= C.listen && t < C.server) H_(C.listen, [['就当它', 'b'], ['在听', 'a']], 120);
  if (s === 'S2b') { if (t >= C.but2 && t < C.again) H_(C.but2, [['可是……', 'b']], 120); if (t >= C.again) H_(C.again, [['关了，', 'b'], ['照样推', 'a']], 120); }
  if (s === 'S3' && t < C.you6) H_(C.clue, [['它', 'b'], ['不用听', 'a']], 120);
  if (s === 'S3') {
    if (t >= C.you6 && t < C.friend) H_(C.you6, [['线索 1 · ', 'b'], ['你自己', 'a']], 100);
    if (t >= C.friend) H_(C.friend, [['线索 2 · ', 'b'], ['你身边的人', 'a']], 100);
  }
  if (s === 'S4') H_(C.feed, [['线索 3 · ', 'b'], ['你的记性', 'a']], 100);
  if (s === 'S5' && t >= C.rev2) H_(C.rev2, [['不听，也', 'b'], ['早就知道', 'a']], 110);
  if (s === 'S6') { if (t < C.fewer) H_(C.tip, [['关掉', 'b'], ['个性化广告', 'a']], 100); else H_(C.fewer, [['广告不会变少', 'b']], 100); }
  if (s === 'S7' && t >= C.home + 1.2) {
    ctx.save(); ctx.translate(-(1 - expoOut(ev(t, C.home + 1.2, .5))) * 800, 0); STY.title(t); ctx.restore();
    if (t >= C.self) H_(C.self, [['它早就', 'b'], ['猜到了', 'a']], 110, 1450);
  }
  if (STY.post) STY.post(t);
  if (!CLEAN_) { const c = CUES.subs.find(c => t >= c.t0 && t < c.t1); if (c) STY.sub(c.text, t); }
  return true;
};
const COVER = (location.search.match(/cover=(\d+)/) || [])[1];
window.DURATION = DUR; window.FPS = FPS;
window.ready = Promise.all([`700 54px ${PSANS}`, `700 84px ${PSERIF}`, `900 40px ${PSERIF}`, `500 40px ${PSANS}`].map(f => document.fonts.load(f)));
