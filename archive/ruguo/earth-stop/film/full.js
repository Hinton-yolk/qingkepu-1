// 如果……会怎样 02 · 如果地球突然停止自转. One core rule: inertia does not stop with the ground.
// Opening: title first frame → the scene (dusk balcony, a sip of pour-over) → the question → 「好，让我们把现实修改一下！」 → 啪 (自转 1× → 0×).
// Sudden stop: the arrows were always there → the ground stops, nothing else does → cup, dripper, plant, table, you → the street → the air → the oceans.
// Reversal: stop it gently → the sun rises in the west, 1 day = 1 year → the planet is fat because it spins → the sea moves (our map) → spin restored, the world turns on → black.
// Pure function of time; seeded noise only.
'use strict';
const C = CUES.c, DUR = TL.duration, FPS = 30;
const ease = x => { x = clamp(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
function keys(K_, t) {      // [t, x, y, z, k] world camera keys
  let i = 0; while (i < K_.length - 2 && t > K_[i + 1][0]) i++;
  const a = K_[i], b = K_[i + 1], p = ease(ev(t, a[0], b[0] - a[0]));
  cam(lerp(a[1], b[1], p), lerp(a[2], b[2], p), lerp(a[3], b[3], p), lerp(a[4], b[4], p) * (1 + .004 * Math.sin(t * .9)));
}
const BAL_CAM = [1.6, 0.6, 1.2];
const N_ = [-Math.SQRT1_2, -Math.SQRT1_2];      // world "north" on screen = straight up (away from us)

// ------------------------------------------------------------------ shared furniture
function steamAt(t, cx, cy, a = 1) {
  const s = K / 100;
  ctx.save(); ctx.strokeStyle = `rgba(255,250,240,${.7 * a})`; ctx.lineWidth = 3.5 * s; ctx.lineCap = 'round';
  for (let i = 0; i < 3; i++) { ctx.beginPath(); for (let k = 0; k <= 20; k++) { const u = k / 20, yy = cy - 16 * s - u * 90 * s, xx = cx + (i - 1) * 8 * s + Math.sin(u * 5 + t * 2.2 + i * 2) * 8 * s * u; k ? ctx.lineTo(xx, yy) : ctx.moveTo(xx, yy); } ctx.globalAlpha = .75 - i * .15; ctx.stroke(); }
  ctx.restore();
}
function panelAt(t, t0, tf, name, from, to) {      // the series panel: rises at t0, flips at tf, leaves after tf + .9
  if (t < t0 || t > tf + 1.4) return;
  const k = expoOut(ev(t, t0, .4)) * (1 - smooth(ev(t, tf + .9, .3)));
  if (k < .01) return;
  ctx.save(); ctx.translate(0, lerp(560, 0, k));
  panel(name, from, to, t >= tf - .15);
  ctx.restore();
}
function flash(t, t0, a = .5) { const k = 1 - ev(t, t0, .35); if (t >= t0 && k > 0) { ctx.fillStyle = `rgba(255,244,232,${a * k * k})`; ctx.fillRect(0, 0, W, H); } }
// hero type: the number the line is about, big; lands with a short drop (no fade)
function hero(t, t0, lines, x, y, o = {}) {
  if (t < t0 || (o.t1 && t >= o.t1)) return;
  ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic';
  lines.forEach((ln, i) => {
    const k = expoOut(ev(t, t0 + i * .15, .32)); if (k <= 0) return;
    const sz = ln.size ?? o.size ?? 140, yy = y + (o.lh ? i * o.lh : 0) - (1 - k) * 46;
    let cx = x;
    for (const [s, col] of ln.parts) {
      ctx.font = `${ln.ui ? 700 : 900} ${sz}px ${ln.ui ? UI : DSP}`;
      if (o.halo) { ctx.lineJoin = 'round'; ctx.lineWidth = sz * .14; ctx.strokeStyle = o.halo; ctx.strokeText(s, cx, yy); }
      ctx.fillStyle = col; ctx.fillText(s, cx, yy); cx += ctx.measureText(s).width;
    }
  });
}
const WHITE = '#F4F8FC';

// ------------------------------------------------------------------ A · the balcony at dusk (human view), the wish
const CAM_A = [[0, ...BAL_CAM, 88], [C.coffee - .4, ...BAL_CAM, 92], [C.coffee + .8, 2.6, 1.9, .9, 200], [C.ask, 2.6, 1.9, .9, 206], [C.stopq + .5, ...BAL_CAM, 94], [C.pak, ...BAL_CAM, 104], [C.turn, 1.9, .4, 1.1, 112]];
const sunPos = t => [250, 500 + Math.min(t, C.pak) * 8];      // sinks behind the skyline until 啪, then stops dead
const BIRDS = [[0, 420, .9], [.5, 470, 1.1], [.9, 440, .8]];
function cupPath(t) {      // the cup: in the hand → a sip → back to the chest → set down on the table (p = 1 means on the table)
  const c = C.coffee;
  if (t < c + .1) return { m: 0, p: 0 };
  if (t < c + .7) return { m: ease(ev(t, c + .1, .6)), p: 0 };
  if (t < c + 1.5) return { m: 1, p: 0 };
  if (t < c + 2.0) return { m: 1 - ease(ev(t, c + 1.5, .5)), p: 0 };
  return { m: 0, p: ease(ev(t, c + 2.3, .8)) };
}
function cupScreen(cx, cy) {      // the human cup drawn at a screen point (base centre)
  const r = .09 * K * 1.22, hgt = .12 * K;
  ctx.fillStyle = '#F4EEE6'; ctx.fillRect(cx - r, cy - hgt, 2 * r, hgt); ctx.beginPath(); ctx.ellipse(cx, cy, r, r * .58, 0, 0, Math.PI); ctx.fill();
  ctx.fillStyle = '#5A3A2A'; ctx.beginPath(); ctx.ellipse(cx, cy - hgt, r, r * .58, 0, 0, TAU); ctx.fill();
  ctx.strokeStyle = '#F4EEE6'; ctx.lineWidth = r * .32; ctx.beginPath(); ctx.arc(cx + r * 1.15, cy - hgt * .5, r * .42, -1.3, 1.3); ctx.stroke();
}
function sceneA(t) {
  keys(CAM_A, t); OY = 200;
  const tf = Math.min(t, C.pak);
  SHANG = -.38 + tf * .03; LIT_T = tf * 1.25;
  duskBG();
  const cp = t < C.pak ? cupPath(t) : { m: 0, p: 1 };
  balcony('human', { sunAt: sunPos(t), shadowLen: 2.4 + tf * .12, cup: cp.p >= 1 });
  // the arm + the cup in hand
  const k = K / 80, [bx, by] = iso(2.25, 2.35, .45), hand = [bx + 46 * k, by - 66 * k], mouth = [bx + 30 * k, by - 104 * k], table = iso(...CUPW);
  let cxy = cp.p > 0 ? [lerp(hand[0], table[0], cp.p), lerp(hand[1], table[1], cp.p)] : [lerp(hand[0], mouth[0], cp.m), lerp(hand[1], mouth[1], cp.m)];
  const sh = [bx + 8 * k, by - 84 * k], reach = cp.p >= 1 ? [bx + 44 * k, by - 50 * k] : [cxy[0] - 10 * k, cxy[1] - 6 * k];
  const el = [lerp(sh[0], reach[0], .5) + 4 * k, lerp(sh[1], reach[1], .5) + 22 * k];
  ctx.strokeStyle = '#2E7A78'; ctx.lineWidth = 12 * k; ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.beginPath(); ctx.moveTo(...sh); ctx.lineTo(...el); ctx.lineTo(...reach); ctx.stroke();
  if (cp.p < 1) cupScreen(cxy[0], cxy[1]); else cxy = table;
  steamAt(t, cxy[0], cxy[1] - .1 * K, t < C.pak ? 1 : .8);
  // birds cross the sky on the question
  if (t >= C.stopq && t < C.pak + 1) for (const [d, y, s] of BIRDS) { const u = t - C.stopq - d; if (u < 0) continue; const x = -40 + u * 150 * s, f = Math.sin(t * 14 + d * 5) * 9; ctx.strokeStyle = 'rgba(70,45,50,.75)'; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(x - 14, y - f); ctx.lineTo(x, y); ctx.lineTo(x + 14, y - f); ctx.stroke(); }
  const wish = smooth(ev(t, C.pak + .2, .8)) * (1 - smooth(ev(t, C.turn, .6)));
  if (wish > 0) { ctx.save(); ctx.globalCompositeOperation = 'soft-light'; ctx.fillStyle = `rgba(255,150,60,${.6 * wish})`; ctx.fillRect(0, 0, W, H); ctx.restore(); }
  if (t >= C.frozen && t < C.turn) {      // the sun is pinned; the clock keeps running
    const [sx, sy] = sunPos(t), kk = expoOut(ev(t, C.frozen, .4));
    ctx.strokeStyle = INK; ctx.lineWidth = 3; ctx.setLineDash([10, 8]); ctx.beginPath(); ctx.arc(sx, sy, lerp(200, 92, kk), 0, TAU); ctx.stroke(); ctx.setLineDash([]);
    if (kk > .6) plateText('太阳位置  不再变化', sx + 120, sy - 90, {});
    if (t >= C.endless) {
      const m = Math.floor(18 * 60 + 42 + (t - C.endless) * 95), hh = Math.floor(m / 60) % 24, mm = m % 60;
      hero(t, C.endless, [{ parts: [['时钟 ', INK]], size: 44, ui: true }, { parts: [[`${String(hh).padStart(2, '0')}:${String(mm).padStart(2, '0')}`, INK]], size: 120 }], 600, sy + 70, { lh: 120 });
    }
  }
  if (t < C.pak + .25) display([[['如果地球，', INK]], [['突然停止', INK], ['自转', ACC], ['？', INK]]], 72, 300, { size: 92, lh: 120 });
  panelAt(t, C.panel, C.pak, '地球自转', '1×', '0×');
  flash(t, C.pak, .45);
}

// ------------------------------------------------------------------ B · blueprint: everything has always been running east; then the ground stops
const CAM_B = [[C.turn, 1.9, .4, 1.1, 112], [C.run, ...BAL_CAM, 100], [C.together, ...BAL_CAM, 96], [C.groundStop, ...BAL_CAM, 98], [C.cup - .1, 2.9, 1.7, .7, 150], [C.you - .3, 2.9, 1.7, .7, 154], [C.you + .1, 2.6, 2.0, .7, 140], [C.cars, 2.6, 2.0, .7, 130]];
function miniGlobe(t, t0, t1) {      // where Beijing is: a small globe with its parallel
  if (t < t0 || t >= t1) return;
  const k = expoOut(ev(t, t0, .5)), P = ortho(105, 30, 170 * k, 540, 470);
  ctx.fillStyle = 'rgba(16,40,90,.96)'; ctx.beginPath(); ctx.arc(P.cx, P.cy, P.R, 0, TAU); ctx.fill();
  graticule(P, 'rgba(220,235,250,.15)'); coast(P, 'rgba(220,235,250,.8)', 1.4);
  ctx.strokeStyle = ACC; ctx.lineWidth = 3; ctx.beginPath(); let pen = false;
  for (let lo = -180; lo <= 180; lo += 2) { const [x, y, c] = P.f(lo, 39.9); if (c > 0) { pen ? ctx.lineTo(x, y) : ctx.moveTo(x, y); pen = true; } else pen = false; } ctx.stroke();
  const [bx, by] = P.f(116.4, 39.9); ctx.fillStyle = '#FFF'; ctx.beginPath(); ctx.arc(bx, by, 7, 0, TAU); ctx.fill();
  if (k > .7) plateText(roll('北京 · 北纬 39.9°', t, t0 + .3, .5), 540, 690, { size: 38 });
}
function speedBars(t, t0, t1) {
  if (t < t0 || t >= t1) return;
  const bx = 72, by = 600, bw = 936, k = expoOut(ev(t, t0, .6));
  ctx.font = `700 40px ${UI}`; ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic';
  ctx.fillStyle = 'rgba(220,235,250,.85)'; ctx.fillText('声速    1235 km/h', bx, by - 16); ctx.fillStyle = 'rgba(220,235,250,.4)'; ctx.fillRect(bx, by, bw * 1235 / 1500 * k, 34);
  ctx.fillStyle = ACC; ctx.fillText('北京地面 1285 km/h', bx, by + 100); ctx.fillRect(bx, by + 116, bw * 1285 / 1500 * k, 34);
  if (k > .9) { ctx.strokeStyle = WHITE; ctx.lineWidth = 3; ctx.setLineDash([8, 6]); ctx.beginPath(); ctx.moveTo(bx + bw * 1235 / 1500, by - 60); ctx.lineTo(bx + bw * 1235 / 1500, by + 170); ctx.stroke(); ctx.setLineDash([]); }
}
function airLines(t, t0, speed = 1, y0 = 800, n = 6, alpha = .55, gap = 44) {
  if (t < t0) return;
  const k = expoOut(ev(t, t0, .5));
  ctx.save(); ctx.strokeStyle = `rgba(220,235,250,${alpha * k})`; ctx.lineWidth = 2; ctx.setLineDash([120, 60]);
  for (let i = 0; i < n; i++) { const y = y0 + i * gap; ctx.lineDashOffset = -((t - t0) * 600 * speed + i * 57); ctx.beginPath(); ctx.moveTo(40, y); ctx.bezierCurveTo(300, y - 10, 700, y + 10, 1040, y); ctx.stroke(); }
  ctx.restore();
}
// the order things leave the balcony (screen offsets; slowed down for the eye)
const FLING = { cup: C.cup, dripper: C.cup + .25, plant: C.cup + .5, table: C.cup + .75, person: C.you, chair: C.you + .25 };
function flingOff(t, t0, mass = 1) { if (t < t0) return null; const u = t - t0; return [(u * 700 + u * u * 1600) / mass, -u * 90 / mass + u * u * 40, u * 3.2 / mass]; }
function sceneB(t) {
  keys(CAM_B, t); OY = 180;
  let sx = 0, sy = 0;
  if (t >= C.groundStop && t < C.groundStop + .45) { const j = 1 - ev(t, C.groundStop, .45); sx = 22 * j * Math.sin(t * 90); sy = 14 * j * Math.cos(t * 77); }
  ctx.save(); ctx.translate(sx, sy);
  sheetBG();
  const off = {}; for (const [k_, t0] of Object.entries(FLING)) off[k_] = flingOff(t, t0, k_ === 'table' ? 1.3 : k_ === 'person' ? 1.7 : 1);
  const { head } = balcony('line', { off });
  const [fx, fy] = iso(3.2, 2.2, 0);
  // the ground arrow: grows at 「你其实一直在跑」, dies at 「地面停了」
  if (t >= C.run) {
    const stopped = t >= C.groundStop, k = expoOut(ev(t, C.run, .5));
    if (!stopped) floorArrow({ fill: `rgba(255,106,26,${.22 * k})`, stroke: ACC });
    else floorArrow({ fill: null, stroke: 'rgba(220,235,250,.35)', dash: [10, 8] });
    if (t >= C.speed && t < C.together && !stopped) plateText('地面  →  东', fx - 470, fy + 70, { accent: true, size: 44 });
    if (t >= C.together && !stopped) plateText('地面  1285 km/h  →', fx - 470, fy + 70, { accent: true, size: 44 });
    if (stopped && t < C.cars) plateText('地面  0 km/h', fx - 470, fy + 70, { accent: true, size: 44 });
  }
  miniGlobe(t, C.beijing, C.speed);
  hero(t, C.speed, [{ parts: [['北京的地面，每小时往东', WHITE]], size: 44, ui: true }, { parts: [[roll('1285', t, C.speed, .7), ACC], [' km/h', ACC]], size: 160 }], 72, 330, { lh: 160, t1: C.together });
  speedBars(t, C.sound, C.together);
  // L06: every thing gets the same arrow, and relative to the ground nothing moves
  if (t >= C.together && t < C.cup) {
    const [hx, hy] = head;
    vArrow(hx + 40, hy - 10, 190, { col: t >= C.youNot ? ACC : LINE }); plateText('你  1285 km/h', hx - 300, hy - 90, { accent: t >= C.youNot });
    if (t >= C.together + .4) { const [cx, cy] = iso(...CUPW); vArrow(cx + 30, cy - 30, 150, { lw: 4 }); plateText('杯子  1285 km/h', cx + 40, cy - 100, { size: 36 }); }
    if (t >= C.together + .8) { airLines(t, C.together + .8, .25, 720, 6, .45); if (t < C.groundStop) plateText('空气  1285 km/h', 640, 660, { size: 36 }); }
    if (t >= C.noFeel && t < C.now) hero(t, C.noFeel, [{ parts: [['相对你脚下：', WHITE]], size: 44, ui: true }, { parts: [['0 km/h', WHITE]], size: 140 }], 72, 330, { lh: 150 });
    if (t >= C.groundStop) hero(t, C.groundStop, [{ parts: [['地面  ', WHITE], ['0', ACC]], size: 130 }, { parts: [['你  ', WHITE], ['1285', ACC]], size: 130 }], 72, 330, { lh: 150 });
  }
  if (t >= C.groundStop && t < C.groundStop + .3) { ctx.fillStyle = `rgba(255,106,26,${.25 * (1 - ev(t, C.groundStop, .3))})`; ctx.fillRect(0, 0, W, H); }
  // L08: one by one, everything that isn't bolted down leaves, east
  if (t >= C.cup) {
    hero(t, C.cup, [{ parts: [['杯子', ACC], ['  →', WHITE]], size: 120 }], 72, 330, { t1: C.you });
    hero(t, C.you, [{ parts: [['你', ACC], ['  →', WHITE]], size: 120 }], 72, 330);
    ctx.font = `400 30px ${UI}`; ctx.fillStyle = 'rgba(220,235,250,.75)'; ctx.textAlign = 'left'; ctx.fillText('画面已慢放：真实情况发生在一瞬间', 76, 400);
  }
  ctx.restore();
}

// ------------------------------------------------------------------ C · the street outside: cars, trees; then the wind
const Q0 = [3.2 + 18 * Math.SQRT1_2, 2.2 + 18 * Math.SQRT1_2];      // the street runs east–west in front of the building
const GZ = -24;
const SW = (s, n) => [Q0[0] + s * EAST[0] + n * N_[0], Q0[1] + s * EAST[1] + n * N_[1]];
const isoS = (s, n, z) => { const [x, y] = SW(s, n); return iso(x, y, z); };
const FAR = (() => { const r = mulberry32(21), b = []; for (let s = -84; s <= 84; s += 12) { if (Math.abs(s) < 10) continue; const [x, y] = SW(s + (r() - .5) * 3, 17 + r() * 3), w = 7 + r() * 2, h = 8 + Math.pow(r(), 1.5) * 20; b.push({ box: [x - w / 2, x + w / 2, y - w / 2, y + w / 2, GZ, GZ + h], s, wins: [] }); } return b.sort((a, c) => (a.box[0] + a.box[2]) - (c.box[0] + c.box[2])); })();
FAR.forEach((B, i) => { const r = mulberry32(100 + i), [x0, x1, y0, y1, z0, z1] = B.box; for (let z = z0 + 2; z < z1 - 1.5; z += 2.6) { for (let u = .15; u < .9; u += .28) { B.wins.push(['x', lerp(y0, y1, u), z, r()]); B.wins.push(['y', lerp(x0, x1, u), z, r()]); } } });
const CARS = (() => { const r = mulberry32(23), a = []; for (let i = 0; i < 16; i++) a.push([-80 + i * 10.5 + r() * 4, r() < .5 ? -3.4 : 3.4, r()]); return a; })();
const TREES = (() => { const r = mulberry32(29), a = []; for (let s = -84; s <= 84; s += 9) { a.push([s + r() * 2, -9, r()]); a.push([s + 4 + r() * 2, 9, r()]); } return a.sort((p, q) => q[1] - p[1]); })();
const CAM_C = [[C.cars, 2.6, 2.0, .7, 130], [C.cars + 1.3, ...SW(6, 0), GZ + 7, 23], [C.air, ...SW(6, 0), GZ + 7, 21], [C.sea, ...SW(6, 0), GZ + 7, 19]];
function carShape(s, n, hot) {      // a prism along the street: top + the face toward us
  const L = 2.3, Wd = .95, h = 1.5, P = (a, b, z) => isoS(s + a, n + b, GZ + z);
  const fill = hot ? 'rgba(255,106,26,.9)' : 'rgba(16,40,90,1)';
  poly([P(-L, -Wd, 0), P(L, -Wd, 0), P(L, -Wd, h * .65), P(-L, -Wd, h * .65)], fill, LINE, 1.6);
  poly([P(-L, -Wd, h * .65), P(L, -Wd, h * .65), P(L, Wd, h * .65), P(-L, Wd, h * .65)], hot ? 'rgba(255,160,110,.9)' : 'rgba(26,56,110,1)', LINE, 1.6);
  poly([P(-L * .55, -Wd * .8, h * .65), P(L * .45, -Wd * .8, h * .65), P(L * .3, -Wd * .8, h), P(-L * .4, -Wd * .8, h)], hot ? 'rgba(255,200,170,.9)' : 'rgba(26,56,110,1)', LINE, 1.4);
}
const sOff = (t, t0, seed, m = 1) => t < t0 ? 0 : ((t - t0) * 14 + (t - t0) ** 2 * 26) * (.75 + .5 * seed) / m;      // metres east (slowed down)
function sceneC(t) {
  keys(CAM_C, t); OY = 180; sheetBG(false);
  LIT_T = 1e9;
  const front = t >= C.air ? lerp(-300, W + 300, ev(t, C.air, 1.3)) : -1e9;      // the wind front, screen x
  // ground, road, kerbs
  poly([isoS(-120, -40, GZ), isoS(120, -40, GZ), isoS(120, 40, GZ), isoS(-120, 40, GZ)], 'rgba(14,34,78,.95)');
  poly([isoS(-120, -7, GZ), isoS(120, -7, GZ), isoS(120, 7, GZ), isoS(-120, 7, GZ)], 'rgba(10,26,62,1)', 'rgba(220,235,250,.35)', 1.5);
  ctx.strokeStyle = 'rgba(220,235,250,.4)'; ctx.lineWidth = 2; ctx.setLineDash([22, 18]); ctx.beginPath(); ctx.moveTo(...isoS(-120, 0, GZ)); ctx.lineTo(...isoS(120, 0, GZ)); ctx.stroke(); ctx.setLineDash([]);
  // far side: buildings (our tower among them), their windows blow out when the wind front passes
  for (const B of FAR) {
    box(...B.box, '', 'line');
    const [x0, x1, y0, y1] = B.box;
    for (const [f, u, z, r] of B.wins) {
      const q = f === 'x' ? [iso(x1, u - .5, z), iso(x1, u + .5, z), iso(x1, u + .5, z + 1.1), iso(x1, u - .5, z + 1.1)] : [iso(u - .5, y1, z), iso(u + .5, y1, z), iso(u + .5, y1, z + 1.1), iso(u - .5, y1, z + 1.1)];
      const cx = q[0][0], tb = t >= C.air && cx < front ? C.air + 1.3 * ((cx + 300) / (W + 600)) + r * .6 : 1e9;
      if (t < tb) { poly(q, null, 'rgba(220,235,250,.5)', 1.2); continue; }
      const u2 = t - tb, dx = u2 * 600 + u2 * u2 * 900, dy = u2 * 60 + u2 * u2 * 200;
      if (cx + dx > W + 40) continue;
      ctx.save(); ctx.translate(dx, dy); ctx.translate(cx, q[0][1]); ctx.rotate(u2 * (2 + r * 4)); ctx.translate(-cx, -q[0][1]); poly(q, 'rgba(255,106,26,.35)', ACC, 1.6); ctx.restore();
    }
  }
  box(-1, 6.4, -8, -.2, GZ, 9, '', 'line'); box(-.3, 6.7, -.3, 4.7, GZ, -.3, '', 'line');
  balcony('line', { sky: false, plant: false, bare: true });
  { const [px, py] = iso(3.2, 2.2, 0); if (t < C.cars + .25) plateText('你家阳台', px + 40, py - 60, { size: 34 }); }
  // trees on both kerbs; crowns tear off east (far kerb first, then cars, then the near kerb in front)
  const tree = (s, n, seed) => {
    const [bx, by] = isoS(s, n, GZ), d = sOff(t, C.loose + seed * .5, seed, 1.4), [cx, cy] = isoS(s + d, n, GZ + 3.4);
    ctx.strokeStyle = LINE; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(bx, by); ctx.lineTo(bx, by - (d > 0 ? 1.4 : 2.4) * K); ctx.stroke();
    if (d > 0) { ctx.strokeStyle = 'rgba(255,106,26,.6)'; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(Math.max(bx, cx - 300), cy); ctx.lineTo(cx, cy); ctx.stroke(); }
    if (cx < W + 60) { ctx.fillStyle = d > 0 ? 'rgba(255,106,26,.35)' : 'rgba(16,40,90,1)'; ctx.strokeStyle = d > 0 ? ACC : LINE; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(cx, cy, 1.4 * K, 0, TAU); ctx.fill(); ctx.stroke(); }
  };
  for (const [s, n, seed] of TREES) if (n > 0) tree(s, n, seed);
  for (const [s, n, seed] of CARS) {
    const d = sOff(t, C.cars + seed * .45, seed), [ax, ay] = isoS(s, n, GZ + .8), [bx, by] = isoS(s + d, n, GZ + .8);
    if (d > 0) { ctx.strokeStyle = 'rgba(255,106,26,.7)'; ctx.lineWidth = 3; for (const o of [-6, 0, 6]) { ctx.beginPath(); ctx.moveTo(Math.max(ax, bx - 420), by + o); ctx.lineTo(bx - 2.3 * K, by + o); ctx.stroke(); } }
    if (bx - 3 * K < W) carShape(s + d, n, d > 0);
  }
  for (const [s, n, seed] of TREES) if (n < 0) tree(s, n, seed);
  // the wind: a front sweeps left → right, everything behind it streams
  if (t >= C.air) {
    ctx.save(); ctx.beginPath(); ctx.rect(0, 0, Math.max(0, front), H); ctx.clip();
    airLines(t, C.air, 2.6, 260, 30, .55, 44);
    ctx.restore();
    if (front < W + 200) { const g = ctx.createLinearGradient(front - 160, 0, front, 0); g.addColorStop(0, 'rgba(220,235,250,0)'); g.addColorStop(1, 'rgba(220,235,250,.35)'); ctx.fillStyle = g; ctx.fillRect(front - 160, 0, 160, H); ctx.fillStyle = WHITE; ctx.fillRect(front - 2, 0, 3, H); }
  }
  // type
  if (t >= C.cars && t < C.air) {
    hero(t, C.cars, [{ parts: [['街上的车', ACC], ['  →', WHITE]], size: 110 }], 72, 330, { t1: C.loose, halo: 'rgba(8,18,44,.9)' });
    hero(t, C.loose, [{ parts: [['没绑牢的一切', ACC]], size: 110 }, { parts: [['→ 东  1285 km/h', WHITE]], size: 64, ui: true }], 72, 330, { lh: 110, halo: 'rgba(8,18,44,.9)' });
    ctx.font = `400 30px ${UI}`; ctx.fillStyle = 'rgba(220,235,250,.75)'; ctx.textAlign = 'left'; ctx.fillText('画面已慢放', 76, 500);
  }
  if (t >= C.wind) hero(t, C.wind, [{ parts: [['风速', WHITE]], size: 44, ui: true }, { parts: [[roll('1285', t, C.wind, .6), ACC], [' km/h', ACC]], size: 150 }], 72, 330, { lh: 150, halo: 'rgba(8,18,44,.9)' });
  if (t >= C.record) {
    const bx = 72, by = 1250, bw = 936, k1 = expoOut(ev(t, C.record, .6)), k2 = expoOut(ev(t, C.x3, .7));
    ctx.fillStyle = 'rgba(6,12,28,.9)'; ctx.fillRect(bx - 24, by - 90, bw + 48, 300);
    ctx.font = `700 38px ${UI}`; ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic';
    ctx.fillStyle = 'rgba(220,235,250,.9)'; ctx.fillText('有记录最强阵风  408 km/h', bx, by - 30); ctx.fillStyle = 'rgba(220,235,250,.55)'; ctx.fillRect(bx, by - 10, bw * 408 / 1320 * k1, 40);
    if (t >= C.x3) { ctx.fillStyle = ACC; ctx.fillText('现在  1285 km/h', bx, by + 90); ctx.fillRect(bx, by + 110, bw * 1285 / 1320 * k2, 40); hero(t, C.x3, [{ parts: [['×3.1', ACC]], size: 150 }], 700, by + 80, { halo: 'rgba(6,12,28,1)' }); }
    ctx.font = `400 26px ${UI}`; ctx.fillStyle = 'rgba(220,235,250,.6)'; ctx.fillText('1996 年，澳大利亚 Barrow Island（WMO）', bx, by + 190);
  }
}

// ------------------------------------------------------------------ D · the planet: the sea is dragged off China's coast, piles on Korea/Japan, slams the Americas
const COAST_CN = (() => { const a = []; for (let la = 21; la <= 40; la += .5) { let lo = null; for (let l = 108; l < 126; l += .5) if (zAt(la, l) >= 0 && zAt(la, l + .5) < 0 && zAt(la, l + 1) < 0) { lo = l + .5; } if (lo !== null) { let far = null; for (let l = lo + 1.5; l < 146; l += .5) if (zAt(la, l) >= 0 && zAt(la, l + .5) >= 0) { far = l; break; } a.push([la, lo, far]); } } return a; })();
function lineOn(P, pts, col, lw, dash) { ctx.strokeStyle = col; ctx.lineWidth = lw; ctx.setLineDash(dash || []); ctx.beginPath(); let pen = false; for (const [lo, la] of pts) { const q = P.f(lo, la); if (q[2] > 0) { pen ? ctx.lineTo(q[0], q[1]) : ctx.moveTo(q[0], q[1]); pen = true; } else pen = false; } ctx.stroke(); ctx.setLineDash([]); }
function sceneD(t) {
  sheetBG(false);
  const z = ease(ev(t, C.sea, .9)), rot = ease(ev(t, C.slam - .1, 1.1)), rew = ease(ev(t, C.gentle, .8));
  const R = lerp(2600, 460, z), lo0 = lerp(128, 235, rot) + 300 * rew, la0 = lerp(28, 20, rot);
  let P = ortho(lo0, la0, R, 540, 880);
  const [bx, by] = P.f(116.4, 39.9);
  P = ortho(lo0, la0, R, 540 + (540 - bx) * (1 - z), 880 + (880 - by) * (1 - z));
  ctx.fillStyle = 'rgba(16,40,90,.95)'; ctx.beginPath(); ctx.arc(P.cx, P.cy, P.R, 0, TAU); ctx.fill();
  graticule(P, 'rgba(220,235,250,.16)'); coast(P, LINE, 2);
  const grow = expoOut(ev(t, C.sea + .5, .8)) * (1 - rew);
  if (grow > 0) for (const la of [-60, -40, -20, 0, 20, 40, 60]) latArrow(P, la, lo0 - 75, 46 * Math.cos(la * D2R) * grow + .5, la === 0 ? ACC : 'rgba(255,106,26,.75)', la === 0 ? 7 : 5);
  if (t >= C.ocean && rew < 1) {      // all water keeps drifting east
    const r = mulberry32(51); ctx.strokeStyle = `rgba(220,235,250,${.6 * (1 - rew)})`; ctx.lineWidth = 2; ctx.beginPath();
    for (let i = 0; i < 300; i++) { const la = (r() - .5) * 130, lo = r() * 360 - 180 + (t - C.ocean) * 14 * Math.cos(la * D2R); if (zAt(la, lo) >= 0) continue; const a = P.f(lo, la), b = P.f(lo + 5 * Math.cos(la * D2R), la); if (a[2] > .05 && b[2] > .05) { ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); } }
    ctx.stroke();
    // off China's coast the water is pulled away east; on the far side (Korea, Japan, Ryukyu) it piles up
    const k = expoOut(ev(t, C.ocean, 1.0)) * (1 - rew), d = 3.5 * k;
    ctx.save(); ctx.beginPath(); ctx.arc(P.cx, P.cy, P.R, 0, TAU); ctx.clip();
    for (const [la, lo] of COAST_CN) { const a = P.f(lo, la), b = P.f(lo + d, la); if (a[2] > 0) { ctx.strokeStyle = `rgba(255,106,26,${.55 * k})`; ctx.lineWidth = 6; ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.stroke(); } }
    lineOn(P, COAST_CN.map(([la, lo]) => [lo + d, la]), `rgba(255,106,26,${k})`, 3, [10, 8]);
    lineOn(P, COAST_CN.filter(c => c[2] !== null).map(([la, , far]) => [far - .5, la]), `rgba(255,236,220,${.95 * k})`, 7 + 3 * Math.sin(t * 12));
    ctx.restore();
    if (k > .6 && rot < .3) { const q = P.f(118, 28); plateText('海水被拽离中国海岸', q[0] - 440, q[1] + 120, { accent: true, size: 38 }); const w = P.f(133, 37); plateText('堆向朝鲜半岛、日本', w[0] - 40, w[1] - 110, { size: 38 }); }
  }
  if (t >= C.slam && rew < 1) {      // …and the Pacific hits the west coast of the Americas
    const k = expoOut(ev(t, C.slam + 1.0, .3)) * (1 - rew);
    ctx.save(); ctx.beginPath(); ctx.arc(P.cx, P.cy, P.R, 0, TAU); ctx.clip();
    ctx.strokeStyle = `rgba(255,236,220,${.95 * k})`; ctx.lineWidth = 9 + 6 * Math.sin((t - C.slam) * 12); ctx.lineCap = 'round'; ctx.beginPath(); let pen = false;
    for (let la = 58; la >= -50; la -= 1) { let lo = -180; for (let l = -135; l < -30; l += .5) if (zAt(la, l) >= 0 && zAt(la, l + .5) >= 0 && zAt(la, l + 1) >= 0 && zAt(la, l + 1.5) >= 0) { lo = l; break; } const q = P.f(lo - 2, la); if (q[2] > 0 && lo > -170) { pen ? ctx.lineTo(q[0], q[1]) : ctx.moveTo(q[0], q[1]); pen = true; } else pen = false; }
    ctx.stroke(); ctx.restore();
    if (k > .6 && rew < .2) { const q = P.f(-112, 26); plateText('拍上美洲西岸', q[0] - 420, q[1] - 40, { accent: true, size: 38 }); }
  }
  if (z > .95 && rew < .2) hero(t, C.sea + .9, [{ parts: [['赤道 ', WHITE], ['1674', ACC], [' km/h', ACC]], size: 96 }, { parts: [['越往两极越慢，两极是 0', WHITE]], size: 38, ui: true }], 72, 260, { lh: 80 });
}

// ------------------------------------------------------------------ E · gently: the sun now rises in the west; 1 day = 1 year; dusk lasts a week; night half a year
const CAM_E = [[C.gentle + .8, ...BAL_CAM, 104], [C.noFly, ...BAL_CAM, 100], [C.noFly + 1.2, 2.2, 1.2, .2, 58], [C.realSea, 2.2, 1.2, .2, 56]];
const HZ = 1060;
function skyPath(p, cw) {      // p 0..1 across the sky; cw = east→west (old, higher) else west→east (new)
  const u = cw ? 1 - p : p, x = lerp(110, 970, u), y = HZ - Math.sin(u * Math.PI) * (cw ? 520 : 420); return [x, y];
}
const STARS = (() => { const r = mulberry32(61), a = []; for (let i = 0; i < 160; i++) a.push([r() * W, r() * HZ, r()]); return a; })();
function sunP(t) {      // where the sun is on the new path
  if (t < C.slow) return .03;
  if (t < C.dusk) return lerp(.03, .14, smooth(ev(t, C.slow, 2.6)));
  if (t < C.dusk + .9) return lerp(.14, .985, ease(ev(t, C.dusk, .9)));      // half a year, fast-forwarded
  return lerp(.985, 1.02, smooth(ev(t, C.dusk + .9, 2.4)));
}
function sceneE(t) {
  keys(CAM_E, t); OY = lerp(200, 380, ease(ev(t, C.noFly, 1.2)));
  const night = smooth(ev(t, C.night + .2, 1.2));
  SHANG = -.38 + C.pak * .03; LIT_T = C.pak * 1.25 + night * 20;
  duskBG();
  const sky = t >= C.noFly;
  const sp = sky ? skyPath(sunP(t), false) : sunPos(C.pak);
  if (night > 0) { ctx.fillStyle = `rgba(14,20,48,${.92 * night})`; ctx.fillRect(0, 0, W, H); for (const [x, y, s] of STARS) { ctx.fillStyle = `rgba(255,255,255,${night * (.3 + .6 * s)})`; ctx.fillRect(x, y, 2 + s * 2, 2 + s * 2); } }
  balcony('human', { sunAt: night > .5 ? [-999, -999] : sp, shadowLen: 2.4 + C.pak * .12, shadows: night < .5 });
  if (night > 0) { ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.fillStyle = `rgba(60,70,120,${.75 * night})`; ctx.fillRect(0, HZ, W, H - HZ); ctx.restore(); }
  steamAt(t, ...iso(...CUPW), 1 - night);
  panelAt(t, C.panel2, C.pak2, '刹车时间', '1 秒', '几十年');
  flash(t, C.pak2, .3);
  if (!sky) return;
  const ink = night > .5 ? LINE : INK, k0 = expoOut(ev(t, C.noFly, .6));
  ctx.strokeStyle = ink; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(60, HZ); ctx.lineTo(60 + 960 * k0, HZ); ctx.stroke();
  ctx.font = `700 44px ${UI}`; ctx.fillStyle = ink; ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic'; ctx.fillText('西', 70, HZ + 60); ctx.textAlign = 'right'; ctx.fillText('东', 1010, HZ + 60);
  const head = (pts, col, alpha = 1) => { const [x0, y0] = pts[0], [x1, y1] = pts[1], a = Math.atan2(y1 - y0, x1 - x0); ctx.fillStyle = col; ctx.globalAlpha = alpha; ctx.beginPath(); ctx.moveTo(x1 + Math.cos(a) * 18, y1 + Math.sin(a) * 18); ctx.lineTo(x1 + Math.cos(a + 2.5) * 22, y1 + Math.sin(a + 2.5) * 22); ctx.lineTo(x1 + Math.cos(a - 2.5) * 22, y1 + Math.sin(a - 2.5) * 22); ctx.fill(); ctx.globalAlpha = 1; };
  if (t >= C.sunMove) {      // the old path: one day, east → west
    const k = ev(t, C.sunMove, .8);
    ctx.strokeStyle = ink; ctx.lineWidth = 2.5; ctx.globalAlpha = .55; ctx.setLineDash([10, 10]); ctx.beginPath(); for (let i = 0; i <= 60 * k; i++) { const [x, y] = skyPath(i / 60, true); i ? ctx.lineTo(x, y) : ctx.moveTo(x, y); } ctx.stroke(); ctx.setLineDash([]); ctx.globalAlpha = 1;
    if (k >= 1) { head([skyPath(.58, true), skyPath(.62, true)], ink, .7); if (t < C.dusk) { const [x, y] = skyPath(.2, true); plateText('原来：东升西落，1 天', x - 60, y - 90, { size: 34 }); } }
  }
  if (t >= C.slow) {      // the new path: west → east
    const k = ev(t, C.slow, .8);
    ctx.strokeStyle = ACC; ctx.lineWidth = 5; ctx.beginPath(); for (let i = 0; i <= 60 * k; i++) { const [x, y] = skyPath(i / 60, false); i ? ctx.lineTo(x, y) : ctx.moveTo(x, y); } ctx.stroke();
    if (k >= 1) head([skyPath(.38, false), skyPath(.42, false)], ACC);
    if (k >= 1 && t < C.dusk) { const [x, y] = skyPath(.5, false); plateText('现在：约半年才走完', x - 220, y + 60, { accent: true, size: 34 }); }
  }
  if (night < .6) {      // the sun, with a short trail while it climbs out of the west
    const p = sunP(t), [sx, sy] = skyPath(p, false);
    if (t >= C.slow) { ctx.strokeStyle = 'rgba(255,154,85,.5)'; ctx.lineWidth = 10; ctx.beginPath(); for (let i = 0; i <= 12; i++) { const [x, y] = skyPath(Math.max(.0, p - i * .008), false); i ? ctx.lineTo(x, y) : ctx.moveTo(x, y); } ctx.stroke(); }
    ctx.fillStyle = '#FF9A55'; ctx.beginPath(); ctx.arc(sx, Math.min(sy, HZ - 4), 32, 0, TAU); ctx.fill(); ctx.strokeStyle = ink; ctx.lineWidth = 2.5; ctx.beginPath(); ctx.arc(sx, Math.min(sy, HZ - 4), 46, 0, TAU); ctx.stroke();
  }
  const tc = night > .5 ? WHITE : INK;
  if (t < C.dusk) {
    hero(t, C.year, [{ parts: [['1 天 = ', tc], ['1 年', ACC]], size: 150 }], 72, 290);
    hero(t, C.slow, [{ parts: [['太阳改从', tc], ['西边', ACC], ['升起', tc]], size: 76 }], 72, 410);
  } else {
    const d = Math.min(7, 1 + Math.floor(Math.max(0, t - C.dusk - .9) * 2.6));
    if (t < C.night + .2) hero(t, C.dusk + .9, [{ parts: [['黄昏 ', tc], ['第 ' + d + ' 天', ACC]], size: 120 }], 72, 330);
    else hero(t, C.night + .2, [{ parts: [['黑夜 ', WHITE], ['约 ' + roll('182', t, C.night + .2, .7) + ' 天', ACC]], size: 120 }], 72, 330);
  }
}

// ------------------------------------------------------------------ F · the section: spinning, it is fat at the waist and the sea piles there; stop → the sea runs to the poles
const SPIN0 = 2.2;
function spinPhase(t) {
  const t0 = C.realSea, ts = C.stopSpin, D = 1.4;
  if (t < ts) return SPIN0 * (t - t0);
  const u = Math.min(t - ts, D); return SPIN0 * (ts - t0) + SPIN0 * (u - u * u / (2 * D));
}
function sceneF(t) {
  sheetBG(false);
  const cx = 540, cy = 900, fat = ease(ev(t, C.fling, 1.6)), a = lerp(300, 350, fat), b = lerp(300, 262, fat);
  const spinning = t < C.stopSpin + 1.2, pile = ease(ev(t, C.fling + .4, 1.8)), flow = ease(ev(t, C.flow, 1.1));
  const th = phi => 7 + 34 * lerp(pile * Math.cos(phi) ** 2, Math.sin(phi) ** 2 * 1.5, flow);
  // the sea
  ctx.fillStyle = 'rgba(80,140,220,.65)'; ctx.beginPath();
  for (let i = 0; i <= 240; i++) { const q = i / 240 * TAU, c = Math.cos(q), s = Math.sin(q), e = th(Math.asin(clamp(s, -1, 1))); const x = cx + (a + e) * c, y = cy - (b + e) * s; i ? ctx.lineTo(x, y) : ctx.moveTo(x, y); }
  ctx.closePath(); ctx.fill();
  // the rock, with meridians that turn while it spins
  ctx.fillStyle = 'rgba(16,40,90,1)'; ctx.strokeStyle = LINE; ctx.lineWidth = 3; ctx.beginPath(); ctx.ellipse(cx, cy, a, b, 0, 0, TAU); ctx.fill(); ctx.stroke();
  const ph = spinPhase(t);
  for (let i = 0; i < 6; i++) {
    const lon = ph + i * Math.PI / 6, rx = Math.abs(a * Math.sin(lon)), front = Math.cos(lon) > 0;
    ctx.strokeStyle = front ? 'rgba(220,235,250,.55)' : 'rgba(220,235,250,.14)'; ctx.lineWidth = front ? 2 : 1.2;
    ctx.beginPath(); ctx.ellipse(cx, cy, Math.max(.5, rx), b, 0, Math.sin(lon) > 0 ? -Math.PI / 2 : Math.PI / 2, Math.sin(lon) > 0 ? Math.PI / 2 : Math.PI * 1.5); ctx.stroke();
  }
  ctx.strokeStyle = 'rgba(220,235,250,.25)'; ctx.lineWidth = 1.2; for (const la of [-60, -30, 0, 30, 60]) { const y = cy - b * Math.sin(la * D2R), hw = a * Math.cos(la * D2R); ctx.beginPath(); ctx.moveTo(cx - hw, y); ctx.lineTo(cx + hw, y); ctx.stroke(); }
  if (fat > 0) { ctx.strokeStyle = 'rgba(220,235,250,.45)'; ctx.setLineDash([12, 10]); ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(cx, cy, 300, 0, TAU); ctx.stroke(); ctx.setLineDash([]); }
  // axis + spin indicator
  ctx.strokeStyle = LINE; ctx.lineWidth = 2; ctx.setLineDash([16, 10]); ctx.beginPath(); ctx.moveTo(cx, cy - b - 160); ctx.lineTo(cx, cy + b + 130); ctx.stroke(); ctx.setLineDash([]);
  ctx.strokeStyle = spinning ? ACC : 'rgba(220,235,250,.5)'; ctx.lineWidth = 5; ctx.beginPath(); ctx.ellipse(cx, cy - b - 120, 80, 20, 0, .15, Math.PI - .15); ctx.stroke();
  for (let i = 0; i < 6; i++) { const u = ph * .9 + i * TAU / 6; if (Math.sin(u) <= 0) continue; ctx.fillStyle = spinning ? ACC : 'rgba(220,235,250,.5)'; ctx.beginPath(); ctx.arc(cx + Math.cos(u) * 80, cy - b - 120 + Math.sin(u) * 20, 6, 0, TAU); ctx.fill(); }
  plateText(spinning ? '自转 1×' : '自转 0×', cx + 110, cy - b - 150, { accent: !spinning, size: 36 });
  // 甩
  if (t >= C.fling && flow < .4) {
    const k = expoOut(ev(t, C.fling, .5)) * (spinning ? 1 : 1 - ev(t, C.stopSpin, .6));
    for (const s of [-1, 1]) { ctx.save(); ctx.translate(cx + s * (a + 52), cy); ctx.scale(s, 1); ctx.globalAlpha = k; vArrow(0, 0, 110 + 12 * Math.sin(t * 8), { col: ACC, lw: 7 }); ctx.restore(); }
    ctx.globalAlpha = k; ctx.font = `900 72px ${DSP}`; ctx.fillStyle = ACC; ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic'; ctx.fillText('甩', cx + a + 112, cy - 44); ctx.fillText('甩', cx - a - 112, cy - 44); ctx.globalAlpha = 1;
  }
  if (t >= C.fat) {      // the dimension: 21 km
    const k = expoOut(ev(t, C.fat, .5));
    ctx.globalAlpha = k; ctx.strokeStyle = WHITE; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(cx + 300, cy + 80); ctx.lineTo(cx + a, cy + 80); ctx.moveTo(cx + 300, cy + 62); ctx.lineTo(cx + 300, cy + 98); ctx.moveTo(cx + a, cy + 62); ctx.lineTo(cx + a, cy + 98); ctx.stroke(); ctx.globalAlpha = 1;
    hero(t, C.fat, [{ parts: [['赤道比两极离地心远', WHITE]], size: 42, ui: true }, { parts: [['21 km', ACC]], size: 150 }], 72, 1330, { lh: 150 });
    ctx.font = `400 28px ${UI}`; ctx.fillStyle = 'rgba(220,235,250,.7)'; ctx.textAlign = 'left'; ctx.fillText('示意：形状已放大（真实扁率 1/298）', 76, 1520);
  }
  if (t >= C.pile && t < C.stopSpin) hero(t, C.pile, [{ parts: [['海水堆在', WHITE], ['赤道', ACC]], size: 90 }], 72, 300);
  if (t >= C.stopSpin && t < C.flow) hero(t, C.stopSpin, [{ parts: [['自转 ', WHITE], ['0×', ACC]], size: 110 }], 72, 300);
  if (t >= C.flow) {      // poleward arrows along the surface
    const k = expoOut(ev(t, C.flow, .5));
    ctx.strokeStyle = ACC; ctx.fillStyle = ACC; ctx.lineWidth = 6;
    for (const sx of [-1, 1]) for (const sy of [-1, 1]) {
      ctx.beginPath(); for (let i = 0; i <= 20; i++) { const q = lerp(.12, .12 + 1.05 * k, i / 20), x = cx + sx * (a + 80) * Math.cos(q), y = cy - sy * (b + 80) * Math.sin(q); i ? ctx.lineTo(x, y) : ctx.moveTo(x, y); } ctx.stroke();
      const q = .12 + 1.05 * k, x = cx + sx * (a + 80) * Math.cos(q), y = cy - sy * (b + 80) * Math.sin(q); ctx.beginPath(); ctx.arc(x, y, 10, 0, TAU); ctx.fill();
    }
    hero(t, C.flow, [{ parts: [['海水 → ', WHITE], ['两极', ACC]], size: 110 }], 72, 300);
  }
}

// ------------------------------------------------------------------ G · our map: East Asia, the sea moves
const MAPC = { sea: [22, 52, 112], land: [196, 212, 232], flood: [64, 118, 196], bed: [235, 124, 52], depth: true };
function sceneG(t) {
  sheetBG(false);
  const p = smooth(ev(t, C.map + .2, 2.4)), P = ortho(112, 32, 460, 540, 880);
  globeRaster(P, p, MAPC);
  graticule(P, 'rgba(220,235,250,.16)'); coast(P, 'rgba(244,248,252,.85)', 1.8);
  if (t >= C.harbin) { const hb = P.f(126.6, 45.75); bracket(hb[0], hb[1], 44, 44, '哈尔滨', { dx: 70, dy: -110, size: 38 }); }
  if (t >= C.scs) { const nh = P.f(114, 14); bracket(nh[0], nh[1], 120, 120, '南海', { dx: 110, dy: 130, size: 38, accent: true }); }
  if (t < C.harbin) hero(t, C.map + .3, [{ parts: [['北边，', WHITE], ['被淹', 'rgb(120,170,235)']], size: 110 }], 72, 300);
  else if (t < C.scs) hero(t, C.harbin, [{ parts: [['哈尔滨', WHITE]], size: 64 }, { parts: [['水下约 1 公里', 'rgb(120,170,235)']], size: 96 }], 72, 230, { lh: 100 });
  else hero(t, C.scs, [{ parts: [['南海', WHITE]], size: 64 }, { parts: [['大半露出海底', ACC]], size: 96 }], 72, 230, { lh: 100 });
  if (t >= C.map + .8) {
    const lx = 72, ly = 1420;
    for (const [i, [c, s]] of [['rgb(64,118,196)', '被淹的陆地'], ['rgb(235,124,52)', '露出的海底']].entries()) { ctx.fillStyle = c; ctx.fillRect(lx + i * 420, ly - 20, 40, 40); ctx.font = `700 34px ${UI}`; ctx.fillStyle = WHITE; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.fillText(s, lx + 56 + i * 420, ly + 2); }
    ctx.font = `400 28px ${UI}`; ctx.fillStyle = 'rgba(220,235,250,.7)'; ctx.textBaseline = 'alphabetic'; ctx.fillText('估算：岩石形状暂时不变，海面沿新的等势面；NOAA ETOPO1', 76, 1490);
  }
}

// ------------------------------------------------------------------ H · the whole new world, then the spin comes back and the sea goes home
function sceneH(t) {
  sheetBG(false);
  const turn = ease(ev(t, C.thought, 3)), back = smooth(ev(t, C.always + 1.2, 1.6));
  const lo0 = 112 - 150 * turn - 120 * ease(ev(t, C.always + 1, 4)), R = lerp(460, 430, turn);
  const P = ortho(lo0, lerp(32, 18, turn), R, 540, 880);
  globeRaster(P, 1 - back, MAPC);
  graticule(P, 'rgba(220,235,250,.16)');
  coast(P, t >= C.coast ? `rgba(255,${lerp(106, 248, ev(t, C.coast + .6, 1)) | 0},${lerp(26, 252, ev(t, C.coast + .6, 1)) | 0},1)` : 'rgba(244,248,252,.85)', t >= C.coast ? 3 : 1.8);
  panelAt(t, C.always - .6, C.always + .6, '地球自转', '0×', '1×');
  flash(t, C.always + .6, .3);
}

function endScene(t) {
  ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);
  if (t < C.next) return;
  display([[['下一个「如果」，', '#F4F4F2']], [['你想看什么？', ACC]]], 72, 860, { size: 96, lh: 128 });
  ctx.font = `400 32px ${UI}`; ctx.fillStyle = 'rgba(244,244,242,.6)'; ctx.textAlign = 'left'; ctx.fillText('如果……会怎样 · 02', 76, 1130);
}

// ------------------------------------------------------------------ the whole frame
const OFF = document.createElement('canvas'); OFF.width = W; OFF.height = H;
function sweep(t, t0, dur, from, to) {      // a scan line sweeps left → right: `to` behind it, `from` ahead of it
  const x = lerp(-60, W + 60, ease(ev(t, t0, dur)));
  to(t);
  const g = OFF.getContext('2d'); g.setTransform(1, 0, 0, 1, 0, 0);
  const r = ctx; ctx = g; from(t); ctx = r;
  ctx.save(); ctx.beginPath(); ctx.rect(x, 0, W - x, H); ctx.clip(); ctx.drawImage(OFF, 0, 0); ctx.restore();
  ctx.fillStyle = HOT; ctx.fillRect(x - 2, 0, 4, H);
}
const CLEAN = location.search.includes('clean');
function subtitles(t) {
  if (CLEAN) return;
  const c = CUES.subs.find(c => t >= c.t0 && t < c.t1); if (!c || t >= C.next - .2) return;
  subtitle(c.text);
}
function mood(t) {      // warm life → golden wish → darker unease → calm → cold reversal
  const uneasy = smooth(ev(t, C.turn, 1.5)) * (1 - smooth(ev(t, C.gentle, .8)));
  if (uneasy > 0) { ctx.fillStyle = `rgba(40,4,30,${.14 * uneasy})`; ctx.fillRect(0, 0, W, H); }
}
window.seek = function (t) {
  t = clamp(t, 0, DUR - 1 / FPS);
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over'; OY = 0; LIT_T = 1e9;
  if (t < C.turn) sceneA(t);
  else if (t < C.turn + .9) sweep(t, C.turn, .9, sceneA, sceneB);
  else if (t < C.sea) { if (t < C.cars) sceneB(t); else sceneC(t); }
  else if (t < C.gentle + .8) sceneD(t);
  else if (t < C.realSea) sceneE(t);
  else if (t < C.realSea + .8) sweep(t, C.realSea, .8, sceneE, sceneF);
  else if (t < C.map) sceneF(t);
  else if (t < C.thought) sceneG(t);
  else if (t < C.black) sceneH(t);
  else endScene(t);
  if (t < C.black) mood(t);
  subtitles(t);
  return true;
};
window.DURATION = DUR; window.FPS = FPS;
window.ready = Promise.all([`700 54px ${UI}`, `900 84px ${DSP}`].map(f => document.fonts.load(f)));
