// ================================================================== S06 · people are walking shadows
const P6 = { router: [-430, 230], floor: 380 };
function people6(t) {
  const u = ev(t, 35.4, 6.6);
  const wx = lerp(-260, 420, u);
  return [
    { x: wx, h: 540, pose: 'walk', ph: wx / 52, dir: 1 },
    { x: 560, h: 520, pose: 'sit', dir: -1 },
  ];
}
function cam6(t) {
  const P = people6(t)[0];
  const k = expoInOut(ev(t, C.person2 - 0.15, 1.1));
  return [lerp(P.x * 0.55 - 10, 70, k), lerp(-40, 0, k), lerp(1.12, 0.8, k)];
}
function S06(t) {
  darkBG();
  const [cx, cy, z] = cam6(t);
  setCam(cx, cy, z);
  const [rx, ry] = [P6.router[0], P6.router[1] - 90];
  const ppl = people6(t).map(p => {
    const top = p.pose === 'sit' ? P6.floor - 0.72 * p.h : P6.floor - 0.95 * p.h;
    const bot = p.pose === 'sit' ? P6.floor - 0.3 * p.h : P6.floor - 0.1 * p.h;
    return { cx: p.x + (p.pose === 'sit' ? 0.02 * p.h * p.dir : 0), top, bot, rr: 0.11 * p.h };
  });
  const lam = 80, v = 130, lod = ringLOD(lam);
  field((x, y) => {
    const out = (x < -1000 || x > 1000 || y < -760 || y > P6.floor) ? 0.4 : 1;
    const dx = x - rx, dy = y - ry, r = Math.sqrt(dx * dx + dy * dy);
    let a = 1.9 * falloff(r, 330) * out;
    for (const p of ppl) if (blocked(rx, ry, x, y, p.cx, p.top, p.bot, p.rr)) { a *= 0.1; break; }
    return a * (0.28 + 0.72 * (lod * crest(r, t, lam, v) + (1 - lod) * 0.3));
  }, { gain: 1.2 });
  // room
  const c = DLINE;
  ink([[-1000, P6.floor], [1000, P6.floor]], 4, c, { key: 1300 });
  ink([[-1000, -760], [1000, -760]], 4, c, { key: 1301 });
  inkRect(-180, -560, 320, 330, 3, c, { key: 1302 });
  ink([[-20, -560], [-20, -230]], 2.5, c, { key: 1303 });
  inkRect(-520, P6.floor - 150, 200, 150, 3, c, { key: 1304 });
  drawRouter(P6.router[0], P6.router[1], 1, 'radio', 1);
  ink([[540, P6.floor - 160], [700, P6.floor - 160]], 4, c, { key: 1305 });
  ink([[555, P6.floor - 160], [555, P6.floor]], 3, c, { key: 1306 }); ink([[685, P6.floor - 160], [685, P6.floor]], 3, c, { key: 1307 });
  plant(880, P6.floor, 1.4, 'radio', 1308);
  for (const p of people6(t)) drawPerson(p.x, P6.floor, p.h, p.pose, 'radio', { dir: p.dir, ph: p.ph, rim: p.x > P6.router[0] ? -1 : 1 });
  const w = people6(t)[0];
  reading('人体 ≈ 60% 是水', w.x - 10, P6.floor - 0.7 * w.h, w.x - 10 - 120 / Z, P6.floor - 0.98 * w.h - 60 / Z, t, snapW('L09', '水'), { color: DTEXT, size: 44 });
  grainPass(0.25);
}
function snapW(lid, sub) { const L = TL.lines.find(l => l.id === lid); const w = L.words.find(w => w.w.includes(sub)); return w ? Math.round(w.t0 / 0.3) * 0.3 : L.t0; }

// ================================================================== S07 · metal is a mirror: the elevator
const E7 = { cl: -170, cr: 170, h: 420, rx: 470 };
function carTop(t) { return lerp(-1100, 700, ease(ev(t, 42.0, 6.0))); }
function S07(t) {
  darkBG();
  const top = carTop(t), bot = top + E7.h;
  setCam(0, top + E7.h / 2 + 20, lerp(1.25, 1.0, ease(ev(t, 42, 6))));
  // one router per hallway, two floors apart; only the ones near the car matter
  const mid = top + E7.h / 2, srcs = [];
  for (let k = -4; k <= 4; k++) {
    const yl = k * 1400 - 150, yr = k * 1400 + 550;
    if (Math.abs(yl - mid) < 1100) srcs.push([-E7.rx, yl]);
    if (Math.abs(yr - mid) < 1100) srcs.push([E7.rx, yr]);
  }
  const lam = 130, v = 150, kk = TAU / lam, w = TAU * v / lam;
  field((x, y) => {
    if (x > E7.cl && x < E7.cr && y > top && y < bot) return 0;           // inside the box: dark
    let val = 0;
    for (const [sx, sy] of srcs) {
      const dy0 = y - sy;
      const left = sx < 0, face = left ? E7.cl : E7.cr;
      const behind = left ? x > face : x < face;
      let shade = 1;
      if (behind) {   // shadow of the car
        const yc = sy + (y - sy) * (face - sx) / (x - sx);
        if (yc > top - 10 && yc < bot + 10) shade = 0;
      }
      const dx = x - sx, r = Math.sqrt(dx * dx + dy0 * dy0);
      const a = 1.25 * falloff(r, 300) * shade;
      let I = a * a, E = a * Math.cos(kk * r - w * t);
      if (!behind) {    // reflection: image source across the face
        const ix = 2 * face - sx;
        const yc = sy + (y - sy) * (face - ix) / (x - ix);
        if (yc > top && yc < bot) {
          const ddx = x - ix, rr = Math.sqrt(ddx * ddx + dy0 * dy0);
          const ar = 1.25 * falloff(rr, 300) * 0.95;
          I += ar * ar; E += ar * Math.cos(kk * rr - w * t + Math.PI);
        }
      }
      val += 0.45 * I + 0.8 * (E > 0 ? E * E : 0);
    }
    return val;
  }, { gain: 1.25 });
  const c = DLINE;
  // shaft and floors
  ink([[-260, -3000], [-260, 3000]], 3, c, { key: 1400 }); ink([[260, -3000], [260, 3000]], 3, c, { key: 1401 });
  for (let k = -5; k <= 5; k++) {
    const y = k * 350;
    ink([[-1200, y], [-260, y]], 3, c, { key: 1402 + k, alpha: 0.7 }); ink([[260, y], [1200, y]], 3, c, { key: 1420 + k, alpha: 0.7 });
  }
  for (const [sx, sy] of srcs) drawRouter(sx, sy + 70, 0.7, 'radio', 1);
  // cables
  ink([[-60, top], [-60, top - 3000]], 2.5, c, { key: 1440, raw: true }); ink([[60, top], [60, top - 3000]], 2.5, c, { key: 1441, raw: true });
  // the mirror box
  ctx.fillStyle = '#000'; ctx.fillRect(E7.cl, top, E7.cr - E7.cl, E7.h);
  ctx.globalCompositeOperation = 'lighter';
  for (const [x0] of [[E7.cl], [E7.cr]]) {
    ink([[x0, top], [x0, bot]], 14, ACC, { raw: true, key: 1450 + x0, single: true, alpha: 0.5 });
    ink([[x0, top], [x0, bot]], 5, HOT, { raw: true, key: 1460 + x0, single: true });
  }
  ink([[E7.cl, top], [E7.cr, top]], 4, HOT, { raw: true, key: 1470, single: true, alpha: 0.8 });
  ink([[E7.cl, bot], [E7.cr, bot]], 4, HOT, { raw: true, key: 1471, single: true, alpha: 0.8 });
  // glint sliding down the faces on "镜子"
  const g = ev(t, C.mirror, 0.9);
  if (g > 0 && g < 1) {
    const gy = lerp(top - 40, bot + 40, g);
    for (const x0 of [E7.cl, E7.cr]) {
      const gr = ctx.createRadialGradient(x0, gy, 0, x0, gy, 90);
      gr.addColorStop(0, 'rgba(255,240,225,1)'); gr.addColorStop(1, 'rgba(255,106,26,0)');
      ctx.fillStyle = gr; ctx.fillRect(x0 - 90, gy - 90, 180, 180);
    }
  }
  ctx.globalCompositeOperation = 'source-over';
  // inside: a person you can barely see, phone with no bars
  ctx.save(); ctx.beginPath(); ctx.rect(E7.cl, top, E7.cr - E7.cl, E7.h); ctx.clip();
  const { S: shp, head, hr } = personShape(340, 'phone', 0, 1);
  ctx.translate(-10, bot - 6); ctx.strokeStyle = '#2A2622'; ctx.lineCap = 'round';
  for (const [pts, wd] of shp) { ctx.lineWidth = wd; ctx.beginPath(); pts.forEach(([px, py], i) => i ? ctx.lineTo(px, py) : ctx.moveTo(px, py)); ctx.stroke(); }
  ctx.fillStyle = '#2A2622'; ctx.beginPath(); ctx.arc(head[0], head[1], hr, 0, TAU); ctx.fill();
  ctx.fillStyle = '#4A443C'; ctx.fillRect(0.15 * 340 - 7, -0.72 * 340 - 13, 14, 24);
  ctx.restore();
  if (t >= C.nosig) reading('无信号', 46, bot - 250, 300, bot - 360, t, C.nosig, { color: DTEXT, size: 54 });
  if (t >= C.dark - 0.3) reading('里面：一片漆黑', E7.cl + 60, top + 70, -170, top - 110, t, C.dark - 0.3, { color: DTEXT, size: 50, align: 'left' });
  grainPass(0.25);
}

// ================================================================== S08 · the microwave door
const MW = { x: -480, y: -380, w: 960, h: 600, door: [-450, -350, 620, 540], win: [-405, -300, 520, 440] };
function microwave(mode, t) {
  const c = lineCol(mode), radio = mode === 'radio';
  const [wx, wy, ww, wh] = MW.win;
  if (!radio) {
    // what you see through the door: a bowl of rice, steam
    ctx.save(); ctx.beginPath(); ctx.roundRect(wx, wy, ww, wh, 26); ctx.clip();
    ctx.fillStyle = '#D9D0C0'; ctx.fillRect(wx, wy, ww, wh);
    const bx = wx + ww / 2, by = wy + wh - 70;
    ink([[bx - 170, by - 110], [bx - 140, by - 20], [bx - 90, by + 20], [bx + 90, by + 20], [bx + 140, by - 20], [bx + 170, by - 110]], 5, INK, { key: 1500 });
    ink(ellPts(bx, by - 110, 170, 26, 40), 4, INK, { key: 1501, raw: true });
    for (let i = 0; i < 70; i++) {
      const a = hash(i, 1) * TAU, rr = Math.sqrt(hash(i, 2));
      const gx = bx + Math.cos(a) * rr * 150, gy = by - 128 + Math.sin(a) * rr * 30 - (1 - rr) * 40;
      ctx.strokeStyle = INK; ctx.lineWidth = 3; ctx.beginPath(); ctx.ellipse(gx, gy, 9, 5, a, 0, TAU); ctx.stroke();
    }
    for (let k = 0; k < 3; k++) {
      const sx = bx - 70 + k * 70, P = [];
      for (let j = 0; j <= 12; j++) P.push([sx + Math.sin(j * 0.7 + t * 2 + k) * 16, by - 200 - j * 14]);
      ink(P, 3, INK, { raw: true, key: 1510 + k, alpha: 0.6 });
    }
    hatchRect(wx, by + 24, ww, 60, 0.6, 12, 2, INK, 0.5, 1520);
    // the mesh: a perforated metal sheet in front
    ctx.fillStyle = 'rgba(27,25,22,0.32)';
    for (let yy = wy + 10; yy < wy + wh; yy += 22) for (let xx = wx + 10; xx < wx + ww; xx += 22) { ctx.beginPath(); ctx.arc(xx, yy, 5.5, 0, TAU); ctx.fill(); }
    ctx.restore();
  } else {
    // to Wi-Fi eyes the door is a solid mirror
    ctx.save(); ctx.beginPath(); ctx.roundRect(wx, wy, ww, wh, 26); ctx.clip();
    const g = ctx.createLinearGradient(wx, wy, wx + ww, wy + wh);
    g.addColorStop(0, '#FF8A3D'); g.addColorStop(0.5, '#FFD9B8'); g.addColorStop(1, '#FF6A1A');
    ctx.fillStyle = g; ctx.fillRect(wx, wy, ww, wh);
    ctx.globalAlpha = 0.25; ctx.strokeStyle = '#FFF4EA'; ctx.lineWidth = 26;
    for (let k = 0; k < 4; k++) { const x0 = wx - 200 + k * 230 + ((t * 60) % 230); ctx.beginPath(); ctx.moveTo(x0, wy + wh); ctx.lineTo(x0 + 300, wy); ctx.stroke(); }
    ctx.globalAlpha = 1;
    const gl = ev(t, C.mirror2, 0.7);
    if (gl > 0 && gl < 1) { ctx.fillStyle = 'rgba(255,255,255,0.55)'; const x0 = lerp(wx - 200, wx + ww + 200, gl); ctx.beginPath(); ctx.moveTo(x0, wy); ctx.lineTo(x0 + 90, wy); ctx.lineTo(x0 - 110, wy + wh); ctx.lineTo(x0 - 200, wy + wh); ctx.fill(); }
    ctx.restore();
  }
  ctx.strokeStyle = c; ctx.lineWidth = 5; ctx.beginPath(); ctx.roundRect(wx, wy, ww, wh, 26); ctx.stroke();
  // body, door, panel
  ctx.lineWidth = 7; ctx.beginPath(); ctx.roundRect(MW.x, MW.y, MW.w, MW.h, 30); ctx.stroke();
  const [dx, dy, dw, dh] = MW.door;
  ctx.lineWidth = 4; ctx.beginPath(); ctx.roundRect(dx, dy, dw, dh, 20); ctx.stroke();
  ink([[dx + dw - 30, dy + 120], [dx + dw - 30, dy + dh - 120]], 9, c, { key: 1530 });
  inkRect(250, -310, 170, 80, 4, c, { key: 1531 });
  const left = Math.max(0, Math.ceil(30 - Math.max(0, t - 48.0) * 30 / 9.6));
  text(t >= C.ding ? '0:00' : `0:${String(left).padStart(2, '0')}`, 335, -252, { align: 'center', size: 50, color: radio ? DTEXT : INK });
  inkCircle(335, -110, 52, 4, c, { key: 1532 });
  ink([[335, -110], [360, -150]], 4, c, { key: 1533 });
  for (let k = 0; k < 3; k++) inkRect(270, -10 + k * 62, 130, 40, 3, c, { key: 1534 + k });
  ink([[MW.x + 60, MW.y + MW.h], [MW.x + 60, MW.y + MW.h + 26]], 6, c, { key: 1540 }); ink([[MW.x + MW.w - 60, MW.y + MW.h], [MW.x + MW.w - 60, MW.y + MW.h + 26]], 6, c, { key: 1541 });
  ink([[-900, MW.y + MW.h + 28], [900, MW.y + MW.h + 28]], 5, c, { key: 1542 });
}
// the loupe: a side cut through the door's mesh
const LP = { x: 0, y: -900, r: 250, ax: -150, ay: -60 };
function loupe(mode, t) {
  const radio = mode === 'radio', c = lineCol(mode);
  const k = expoOut(ev(t, C.holes, 0.45));
  if (k <= 0) return;
  const r = LP.r * k;
  ink([[LP.ax, LP.ay], [LP.x - r * 0.7, LP.y + r * 0.7]], 2, c, { raw: true, key: 1600, single: true });
  ink([[LP.ax, LP.ay], [LP.x + r * 0.7, LP.y + r * 0.7]], 2, c, { raw: true, key: 1601, single: true });
  inkCircle(LP.ax, LP.ay, 34, 3, c, { key: 1602 });
  ctx.save(); ctx.beginPath(); ctx.arc(LP.x, LP.y, r, 0, TAU);
  ctx.fillStyle = radio ? '#120F0C' : PAPER2; ctx.fill(); ctx.clip();
  // the sheet, cut: a vertical line of metal with small gaps
  const gap = 18, pitch = 64;
  for (let yy = LP.y - 300; yy < LP.y + 300; yy += pitch) {
    ctx.fillStyle = radio ? HOT : INK;
    ctx.fillRect(LP.x - 9, yy + gap / 2, 18, pitch - gap);
  }
  if (!radio) {
    // light: short waves pass straight through the gaps
    const p = ev(t, C.lightThru, 1.8);
    for (let yy = LP.y - 300 + pitch / 2; yy < LP.y + 300; yy += pitch) {
      const P = [];
      for (let x = LP.x - 240; x < LP.x - 240 + 480 * Math.min(1, 0.4 + p); x += 4) P.push([x, yy - pitch / 2 + 9 + Math.sin((x - t * 200) * 0.35) * 5]);
      if (P.length > 1) ink(P, 2.6, INK, { raw: true, key: 1610 + yy, single: true });
    }
  } else {
    // Wi-Fi: one wave far bigger than the holes, sent back
    const lam = 240, x0 = LP.x - 9;
    ctx.globalCompositeOperation = 'lighter';
    for (let j = 0; j < 6; j++) {
      const ph = ((t * 160) / lam + j / 6) % 1;
      const xin = LP.x - 260 + ph * 260;                // incoming front
      ctx.strokeStyle = ACC; ctx.globalAlpha = 0.9 * (1 - ph * 0.3); ctx.lineWidth = 10;
      ctx.beginPath(); ctx.moveTo(xin, LP.y - 260); ctx.lineTo(xin, LP.y + 260); ctx.stroke();
      const xout = x0 - ph * 260;                        // reflected front
      ctx.globalAlpha = 0.55 * (1 - ph); ctx.beginPath(); ctx.moveTo(xout, LP.y - 260); ctx.lineTo(xout, LP.y + 260); ctx.stroke();
    }
    ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over';
    ctx.fillStyle = '#120F0C'; ctx.fillRect(LP.x + 9, LP.y - 300, 300, 600);   // nothing gets through
    text('穿不过去', LP.x + 130, LP.y + 14, { align: 'center', size: 46, color: DTEXT });
  }
  ctx.restore();
  inkCircle(LP.x, LP.y, r, 6, c, { key: 1620 });
  if (!radio) text('孔只有 1–2 mm，光能穿过', LP.x, LP.y + r + 66, { align: 'center', size: 46 });
  if (radio) { ctx.fillStyle = DARK; ctx.fillRect(LP.x - 400, LP.y + r + 18, 800, 70); text('波长 12 cm ≫ 孔 1–2 mm', LP.x, LP.y + r + 66, { align: 'center', size: 46, color: DTEXT }); }
}
function S08(t) {
  const k8 = expoInOut(ev(t, C.holes - 0.45, 0.9));
  const z = lerp(1.06, 0.92, k8) + 0.04 * smooth(ev(t, 50.6, 7.5));
  const cam = () => setCam(0, lerp(-80, -310, k8), z);
  paperBG(); cam();
  microwave('paper', t); loupe('paper', t);
  if (t >= C.front2) {
    const fx = front(t, C.front2, 0.9);
    ctx.save(); screenCam(); ctx.beginPath(); ctx.rect(0, 0, fx, H); ctx.clip();
    cam();
    field((x, y) => {
      const dx = x + 1400, dy = y + 200, r = Math.sqrt(dx * dx + dy * dy);
      return 1.1 * falloff(r, 900) * (0.3 + 0.7 * crest(r, t, 110, 140));
    });
    microwave('radio', t); loupe('radio', t);
    ctx.restore();
    if (fx < W + 60) seam(fx);
  }
  if (t >= C.ding) {
    cam();
    writeOn(['叮', '！'], 335, -470, [C.ding, C.ding + 0.08], t, { size: 130, color: t >= C.front2 ? DTEXT : INK, align: 'center' });
  }
  grainPass(0.3);
}

// ================================================================== S09 · bad news: hold the most beautiful frame
const CAM_WIDE = [0, -1720, 0.47 * (1 - 0.04 * smooth((35.4 - 29.1) / 30))];
const camHold = t => [CAM_WIDE[0], CAM_WIDE[1], CAM_WIDE[2] * (1 + 0.06 * smooth(ev(t, SHT('S09'), 6.0)))];
function S09(t) { S04_05(t, { cam: camHold(t) }); }

// ================================================================== S10 · too blurry → it was all inside a small eye
const EYE_SCREEN = [540, 980], EYE_S = 1.12;
function S10(t) {
  const lv = 5 * smooth(ev(t, C.blur, 2.4));
  renderTo(OFF, () => S04_05(t, { cam: camHold(t) }));
  if (t < C.pullEye) { screenCam(); drawBlurred(OFF, lv); grainPass(0.25); return; }
  paperBG();
  const p = expoInOut(ev(t, C.pullEye, 1.2));
  const rp = Math.exp(lerp(Math.log(1250), Math.log(EYE.r * EYE_S), p));
  const s = rp / EYE.r;
  setCam(0, 0, 1);
  ctx.setTransform(1, 0, 0, 1, EYE_SCREEN[0], EYE_SCREEN[1]);
  const haze = smooth(ev(t, C.haze, 0.8));
  drawEye(0, 0, s, 1, t, pr => {
    ctx.save();
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.beginPath(); ctx.arc(EYE_SCREEN[0], EYE_SCREEN[1], rp, 0, TAU); ctx.clip();
    const kk = (rp * 2.6) / W;
    drawBlurred(OFF, 5 + 1.5 * haze, EYE_SCREEN[0] - W * kk / 2, EYE_SCREEN[1] - H * kk / 2, W * kk, H * kk);
    ctx.restore();
  }, { noGlint: s > 3 });
  grainPass(0.3);
}

// ================================================================== S11 · the pupil you would need: half a kilometre
function fmtLen(m) {
  if (m < 0.01) return `${(m * 1000).toFixed(0)} mm`;
  if (m < 1) return `${(m * 100).toFixed(m < 0.1 ? 1 : 0)} cm`;
  if (m < 10) return `${m.toFixed(1)} m`;
  return `${Math.round(m)} m`;
}
function S11(t) {
  paperBG();
  // the pupil grows in four steps on the beat grid: coin, person, building, valley
  const STOPS = [0.0031, 0.05, 3.5, 60, 500], T0 = C.steps;
  let ld = Math.log10(STOPS[0]);
  for (let i = 0; i < 4; i++) ld = lerp(ld, Math.log10(STOPS[i + 1]), expoInOut(ev(t, T0[i], 0.32)));
  const d = Math.pow(10, ld), p = (ld - Math.log10(0.0031)) / (Math.log10(500) - Math.log10(0.0031));
  const Wm = d * lerp(1080 / 220, 2.1, smooth(ev(t, T0[0], 0.32)));
  const z = 1080 / Wm;
  const q = smooth(ev(t, T0[0], 0.32));
  const ox = lerp(540, 690, q), oy = lerp(980, 1010, q);     // where the pupil centre sits on screen
  setCam((540 - ox) / z, (960 - oy) / z, z);
  const mm = 0.0031 / 2 / EYE.r;      // the eye at true size: pupil 3.1 mm
  // things for scale, left of the pupil, all at true size
  const objs = [
    { name: '硬币 2.5 cm', x: -0.044, s: 0.025, draw: (x, s) => { inkCircle(x, 0, s / 2, 4, INK, { key: 1700 }); inkCircle(x, 0, s * 0.38, 2, INK, { key: 1701 }); } },
    { name: '人 1.7 m', x: -3.06, s: 1.7, draw: (x, s) => drawPerson(x, s / 2, s, 'stand', 'paper', { col: INK }) },
    { name: '楼 30 m', x: -52, s: 30, draw: (x, s) => { inkRect(x - 7, -s / 2, 14, s, 4, INK, { key: 1702 }); for (let k = 1; k < 10; k++) ink([[x - 7, -s / 2 + k * 3], [x + 7, -s / 2 + k * 3]], 2, INK, { key: 1703 + k, alpha: 0.7 }); } },
  ];
  // ground and hills arrive with the last decade
  const hill = smooth(ev(Math.log10(d), 1.6, 0.8));
  if (hill > 0) {
    const gy = 250;
    ink([[-2000, gy], [lerp(-200, 2000, hill), gy]], 4, INK, { key: 1720 });
    for (const [hx, hh, hw, key] of [[-430, 260, 300, 1721], [-200, 190, 200, 1722], [430, 300, 330, 1723], [640, 220, 260, 1724]]) {
      const P = [[hx - hw, gy], [hx - hw * 0.45, gy - hh * 0.8], [hx - hw * 0.15, gy - hh], [hx + hw * 0.2, gy - hh * 0.95], [hx + hw * 0.55, gy - hh * 0.6], [hx + hw, gy]];
      ctx.save(); ctx.beginPath(); P.forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)); ctx.closePath(); ctx.fillStyle = PAPER; ctx.fill(); ctx.clip();
      hatch(hx - hw, gy - hh, hw * 2, hh, 0.9, 16, 2, INK, 0.45, key); ctx.restore();
      ink(P, 4, INK, { key });
    }
  }
  // the pupil: a black disk growing out of the eye
  if (p < 0.25) drawEye(0, 0, mm, 1, t, null, { noGlint: true });
  ctx.fillStyle = INK; ctx.beginPath(); ctx.arc(0, 0, d / 2, 0, TAU); ctx.fill();
  ctx.save(); ctx.beginPath(); ctx.arc(0, 0, d / 2, 0, TAU); ctx.clip(); ctx.scale(d / 2 / EYE.r, d / 2 / EYE.r); pupilRings(t, EYE.r, 0.9); ctx.restore();
  for (const o of objs) {
    const hpx = o.s * z;
    if (hpx < 8 || hpx > 4000) continue;
    ctx.save(); ctx.beginPath(); ctx.rect(-1e6, -1e6, 2e6, 2e6); ctx.arc(0, 0, d / 2, 0, TAU, true); ctx.clip('evenodd');
    o.draw(o.x, o.s);
    ctx.restore();
    if (hpx > 90 && hpx < 1400 && Math.abs(o.x) > d / 2 + o.s / 2) {
      const [lx, ly] = toScreen(o.x, -o.s / 2);
      ctx.save(); screenCam(); text(o.name, lx, ly - 22, { align: 'center', size: 44 }); ctx.restore();
      setCam((540 - ox) / z, (960 - oy) / z, z);
    }
  }
  // counter + the answer
  screenCam();
  if (t < C.halfkm) {
    if (t >= C.note) { text('要看得和现在一样清楚', 540, 290, { align: 'center', size: 52 }); text('瞳孔得多大？', 540, 370, { align: 'center', size: 52 }); }
  } else {
    writeOn(['≈', ' ', '5', '0', '0', ' ', 'm'], 540, 400, [0, 0.03, 0.06, 0.09, 0.12, 0.15, 0.18].map(x => C.halfkm + x), t, { size: 170, align: 'center' });
    if (t > C.halfkm + 0.3) {
      text('≈ 半公里', 540, 490, { align: 'center', size: 50 });
      text('按衍射极限 θ≈1.22λ/D 估算', 540, 580, { align: 'center', size: 36, weight: 400 });
      text('要达到人眼约 1′ 的清晰度', 540, 630, { align: 'center', size: 36, weight: 400 });
    }
  }
  grainPass(0.35);
}

// ================================================================== S12 · FAST: humanity built that eye
function S12(t) {
  darkBG();
  const lt = t - C.hit;
  const z = 1 + 0.1 * smooth(ev(t, C.hit + 0.5, 7.5));
  setCam(0, 0, z);
  const k = expoOut(ev(t, C.hit, 0.55));
  const dcx = lerp(150, 0, k), dcy = lerp(50, 250, k), rx = lerp(257, 505, k), ry = lerp(257, 185, k);
  // sky: the radio glow of the galaxy and a few pulsars
  field((x, y) => {
    const band = Math.exp(-Math.pow((y + 0.55 * x + 380) / 260, 2)) * 0.45;
    let v = band * (0.8 + 0.2 * Math.sin(x * 0.01 + y * 0.013));
    for (let i = 0; i < 6; i++) {
      const px = -460 + hash(i, 71) * 920, py = -880 + hash(i, 72) * 520;
      const per = 0.3 + hash(i, 73) * 0.9;
      const pulse = Math.exp(-Math.pow(((t + hash(i, 74)) % per) / 0.05, 2));
      const dx = x - px, dy = y - py;
      v += (0.25 + 1.2 * pulse) / (1 + (dx * dx + dy * dy) / 260);
    }
    // focused energy at the feed
    const fx = x - dcx, fy = y - (dcy - 420);
    v += 2.2 * k / (1 + (fx * fx + fy * fy) / 1500);
    if (y > dcy - 40) v *= 0.4;
    return v;
  }, { gain: 1.1 });
  const c = DLINE;
  // back hills
  for (let i = 0; i < 9; i++) {
    const hx = -620 + i * 160 + hash(i, 80) * 60, hh = 160 + hash(i, 81) * 140, hw = 140 + hash(i, 82) * 60;
    const base = dcy + 20;
    const P = [[hx - hw, base], [hx - hw * 0.3, base - hh * 0.9], [hx, base - hh], [hx + hw * 0.35, base - hh * 0.85], [hx + hw, base]];
    ctx.save(); ctx.beginPath(); P.forEach(([x, y], j) => j ? ctx.lineTo(x, y) : ctx.moveTo(x, y)); ctx.closePath(); ctx.fillStyle = DARK; ctx.fill(); ctx.restore();
    ink(P, 3, c, { key: 1800 + i });
  }
  // incoming wavefronts, then focusing to the feed
  ctx.globalCompositeOperation = 'lighter';
  for (let j = 0; j < 7; j++) {
    const ph = ((lt * 0.55) + j / 7) % 1;
    const y = lerp(-950, dcy - 20, ph);
    const half = rx * 0.92;
    ctx.strokeStyle = ACC; ctx.lineWidth = 5 / Z;
    const r = lerp(rx * 0.9, 6, ph);
    ctx.globalAlpha = 0.6 * k * (1 - ph);
    ctx.beginPath(); ctx.arc(dcx, dcy - 420, r * 0.6, 0.15 * Math.PI, 0.85 * Math.PI); ctx.stroke();
  }
  ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over';
  // the dish
  ctx.fillStyle = '#16120E'; ctx.beginPath(); ctx.ellipse(dcx, dcy, rx, ry, 0, 0, TAU); ctx.fill();
  ctx.save(); ctx.beginPath(); ctx.ellipse(dcx, dcy, rx, ry, 0, 0, TAU); ctx.clip();
  for (let i = 1; i <= 6; i++) ink(ellPts(dcx, dcy + ry * 0.12 * i / 6 * 2, rx * i / 6.2, ry * i / 6.2, 60), 2, c, { raw: true, key: 1820 + i, alpha: 0.8 });
  for (let i = 0; i < 28; i++) { const a = i / 28 * TAU; ink([[dcx, dcy + ry * 0.25], [dcx + Math.cos(a) * rx, dcy + Math.sin(a) * ry]], 1.6, c, { raw: true, key: 1830 + i, alpha: 0.6, single: true }); }
  const g = ctx.createRadialGradient(dcx, dcy + ry * 0.3, 10, dcx, dcy, rx);
  g.addColorStop(0, 'rgba(255,106,26,0.35)'); g.addColorStop(1, 'rgba(255,106,26,0)');
  ctx.fillStyle = g; ctx.fillRect(dcx - rx, dcy - ry, rx * 2, ry * 2);
  const sw = ev(t, C.panels, 1.8);
  if (sw > 0) {
    ctx.globalCompositeOperation = 'lighter';
    for (let i = 1; i <= 14; i++) {
      const f = i / 14, on = clamp((sw * 1.25 - f) * 5);
      if (on <= 0) continue;
      ctx.strokeStyle = HOT; ctx.globalAlpha = 0.5 * on * (sw < 1 ? 1 : 0.55); ctx.lineWidth = 2.5;
      ctx.beginPath(); ctx.ellipse(dcx, dcy + ry * 0.25 * (1 - f), rx * f, ry * f, 0, 0, TAU); ctx.stroke();
    }
    ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over';
  }
  ctx.restore();
  ctx.globalCompositeOperation = 'lighter';
  ink(ellPts(dcx, dcy, rx, ry, 90), 12, ACC, { raw: true, key: 1860, single: true, alpha: 0.5 });
  ink(ellPts(dcx, dcy, rx, ry, 90), 4.5, HOT, { raw: true, key: 1861, single: true });
  ctx.globalCompositeOperation = 'source-over';
  // towers, cables, the feed cabin
  const cab = [dcx, dcy - 420];
  if (k > 0.3) {
    for (let i = 0; i < 6; i++) {
      const a = i / 6 * TAU + 0.3;
      const bx = dcx + Math.cos(a) * rx * 1.05, by = dcy + Math.sin(a) * ry * 1.05;
      const tt = by - 470;
      ink([[bx - 8, by], [bx, tt], [bx + 8, by]], 4, DTEXT, { raw: true, key: 1870 + i, alpha: 0.75 });
      for (let j = 1; j < 6; j++) { const yy = lerp(by, tt, j / 6); ink([[bx - 8 * (1 - j / 6), yy], [bx + 8 * (1 - j / 6), yy - 30]], 1.5, DTEXT, { raw: true, key: 1900 + i * 10 + j, single: true, alpha: 0.5 }); }
      ink([[bx, tt], cab], 2, DTEXT, { raw: true, key: 1880 + i, single: true, alpha: 0.55 });
    }
    ctx.fillStyle = '#16120E'; ctx.beginPath(); ctx.moveTo(cab[0] - 30, cab[1] - 14); ctx.lineTo(cab[0] + 30, cab[1] - 14); ctx.lineTo(cab[0] + 20, cab[1] + 18); ctx.lineTo(cab[0] - 20, cab[1] + 18); ctx.closePath(); ctx.fill();
    ctx.strokeStyle = HOT; ctx.lineWidth = 3; ctx.stroke();
  }
  // front hills overlapping the rim
  for (const [hx, hh, hw, key] of [[-560, 230, 260, 1890], [580, 260, 280, 1891], [-300, 120, 200, 1892], [330, 140, 230, 1893]]) {
    const base = dcy + ry + 260;
    const P = [[hx - hw, base], [hx - hw * 0.3, base - hh * 0.85 - 120], [hx, base - hh - 120], [hx + hw * 0.4, base - hh * 0.8 - 120], [hx + hw, base]];
    ctx.save(); ctx.beginPath(); P.forEach(([x, y], j) => j ? ctx.lineTo(x, y) : ctx.moveTo(x, y)); ctx.closePath(); ctx.fillStyle = DARK; ctx.fill(); ctx.clip();
    hatch(hx - hw, base - hh - 140, hw * 2, hh + 140, 0.9, 16, 2, c, 0.6, key); ctx.restore();
    ink(P, 3.5, c, { key });
  }
  // type
  if (t >= C.tianyan) {
    writeOn('中国天眼'.split(''), 0, -640, [0, .06, .12, .18].map(x => C.tianyan + x), t, { size: 140, color: DTEXT, align: 'center' });
    if (t > C.tianyan + 0.5) text('FAST · 贵州平塘', 0, -555, { align: 'center', size: 44, weight: 400, color: DTEXT, alpha: 0.9 });
  }
  if (t >= C.aperture) {
    const q = expoOut(ev(t, C.aperture, 0.5));
    const y = dcy;
    ink([[dcx - rx * q, y - 10], [dcx - rx * q, y + 10]], 3, DTEXT, { raw: true, key: 1895, single: true });
    ink([[dcx + rx * q, y - 10], [dcx + rx * q, y + 10]], 3, DTEXT, { raw: true, key: 1896, single: true });
    ink([[dcx - rx * q, y], [dcx + rx * q, y]], 2.5, DTEXT, { raw: true, key: 1897, single: true });
    text('口径 500 m', dcx, y - 26, { align: 'center', size: 48, color: DTEXT, alpha: q > 0.6 ? 1 : 0, stroke: 8 });
  }
  if (t >= C.radio) {
    reading('射电望远镜：收听宇宙的无线电', cab[0] - 30, cab[1], -440, -470, t, C.radio, { color: DTEXT, size: 44, align: 'left' });
  }
  grainPass(0.25);
}

// ================================================================== S13 · the quiet zone: five kilometres without Wi-Fi
const QZ = { cx: 540, cy: 980, R: 400, dish: 110 };
const VILL = [];
(() => {
  const r = mulberry32(77);
  let n = 0;
  while (VILL.length < 11 && n < 500) {
    n++;
    const x = 60 + r() * 960, y = 280 + r() * 1360;
    const d = Math.hypot(x - QZ.cx, y - QZ.cy);
    if (d < QZ.R + 70) continue;
    if (VILL.some(v => Math.hypot(v.x - x, v.y - y) < 170)) continue;
    VILL.push({ x, y, n: 3 + Math.floor(r() * 4), s: r() });
  }
})();
const INSIDE = [[380, 820], [700, 760], [460, 1190], [690, 1150], [300, 1010], [810, 1070], [560, 690]];
function S13(t) {
  darkBG(); screenCam();
  const z = 1.0 + 0.12 * smooth(ev(t, SHT('S13') + 1.6, 4.4));
  setCam(540, 980, z);
  const ring = expoOut(ev(t, C.ring5, 1.1)) * QZ.R;
  const offT = CUES.phonesOff;
  field((x, y) => {
    let v = 0;
    for (let i = 0; i < VILL.length; i++) {
      const V = VILL[i], dx = x - V.x, dy = y - V.y, r = Math.sqrt(dx * dx + dy * dy);
      const tb = Math.floor((t + V.s) / 0.6) * 0.6 - V.s;
      v += 1.2 * (0.6 + 0.8 * Math.exp(-(t - tb) / 0.12)) / (1 + r * r / 1600) + 0.18 * crest(r, t, 60, 60) / (1 + r / 60);
    }
    for (let i = 0; i < INSIDE.length; i++) {
      if (t >= offT[i]) continue;
      const dx = x - INSIDE[i][0], dy = y - INSIDE[i][1];
      v += 1.0 / (1 + (dx * dx + dy * dy) / 700);
    }
    return v;
  }, { gain: 1 });
  // karst terrain as contour rings
  const r = mulberry32(5);
  for (let i = 0; i < 46; i++) {
    const hx = r() * 1200 - 60, hy = 160 + r() * 1650, s = 40 + r() * 70;
    if (Math.hypot(hx - QZ.cx, hy - QZ.cy) < QZ.dish + s) continue;
    for (let k = 1; k <= 3; k++) {
      const P = [];
      for (let j = 0; j <= 24; j++) { const a = j / 24 * TAU; const rr = s * k / 3 * (0.85 + 0.25 * Math.sin(a * 3 + i)); P.push([hx + Math.cos(a) * rr, hy + Math.sin(a) * rr * 0.9]); }
      ink(P, 1.6, DLINE, { raw: true, key: 2000 + i * 4 + k, single: true, alpha: 0.6 });
    }
  }
  // villages: little houses
  for (const [i, V] of VILL.entries()) for (let k = 0; k < V.n; k++) {
    const hx = V.x + (hash(i, k, 1) - 0.5) * 90, hy = V.y + (hash(i, k, 2) - 0.5) * 70;
    inkRect(hx - 9, hy - 7, 18, 14, 2, DLINE, { key: 2300 + i * 10 + k, single: true });
  }
  // the dish from above (it is an eye)
  ctx.fillStyle = '#16120E'; ctx.beginPath(); ctx.arc(QZ.cx, QZ.cy, QZ.dish, 0, TAU); ctx.fill();
  for (let i = 0; i < 24; i++) { const a = i / 24 * TAU; ink([[QZ.cx, QZ.cy], [QZ.cx + Math.cos(a) * QZ.dish, QZ.cy + Math.sin(a) * QZ.dish]], 1.4, DLINE, { raw: true, key: 2400 + i, single: true }); }
  for (let k = 1; k <= 3; k++) inkCircle(QZ.cx, QZ.cy, QZ.dish * k / 3.2, 1.4, DLINE, { key: 2430 + k, single: true });
  ctx.globalCompositeOperation = 'lighter';
  inkCircle(QZ.cx, QZ.cy, QZ.dish, 5, HOT, { key: 2440, single: true });
  ctx.globalCompositeOperation = 'source-over';
  for (let i = 0; i < 6; i++) { const a = i / 6 * TAU + 0.3; ctx.fillStyle = DTEXT; ctx.beginPath(); ctx.arc(QZ.cx + Math.cos(a) * QZ.dish * 1.12, QZ.cy + Math.sin(a) * QZ.dish * 1.12, 6, 0, TAU); ctx.fill(); }
  // the 5 km ring
  if (ring > 0) {
    ctx.setLineDash([22, 16]); ctx.strokeStyle = DTEXT; ctx.lineWidth = 4;
    ctx.beginPath(); ctx.arc(QZ.cx, QZ.cy, ring, 0, TAU); ctx.stroke(); ctx.setLineDash([]);
    if (t > C.ring5 + 0.6) text('电磁波宁静区 · 核心区', QZ.cx, QZ.cy - ring - 34, { align: 'center', size: 46, color: DTEXT, stroke: 8 });
    if (t >= C.km5) {
      const q = expoOut(ev(t, C.km5, 0.4));
      ink([[QZ.cx + QZ.dish, QZ.cy], [QZ.cx + QZ.dish + (ring - QZ.dish) * q, QZ.cy]], 3, DTEXT, { raw: true, key: 2450, single: true });
      if (q > 0.6) text('半径 5 km', QZ.cx + (QZ.dish + ring) / 2, QZ.cy - 24, { align: 'center', size: 54, color: DTEXT, stroke: 9 });
    }
  }
  // phones switching off inside, one per 16th
  for (let i = 0; i < INSIDE.length; i++) {
    const [x, y] = INSIDE[i];
    const off = t >= offT[i];
    ctx.fillStyle = off ? '#000' : '#2A1A10'; ctx.strokeStyle = off ? DLINE : HOT; ctx.lineWidth = 4;
    ctx.beginPath(); ctx.roundRect(x - 16, y - 28, 32, 56, 6); ctx.fill(); ctx.stroke();
    if (!off) { ctx.fillStyle = HOT; ctx.fillRect(x - 10, y - 20, 20, 36); }
    if (off && t < offT[i] + 0.3) { ctx.strokeStyle = DTEXT; ctx.lineWidth = 5; ctx.beginPath(); ctx.moveTo(x - 24, y - 34); ctx.lineTo(x + 24, y + 34); ctx.stroke(); }
  }
  grainPass(0.25);
}

// ================================================================== S14 · back to the eye (loops to frame 0)
function S14(t) {
  const fp = ev(t, 84.6, 0.9);
  // the paper eye
  paperBG();
  const m = smooth(ev(t, 85.6, 1.6));
  const z = lerp(EYE_S, 1, m);
  const sy = lerp(EYE_SCREEN[1], 1080, m);
  setCam(0, 0, 1);
  ctx.setTransform(z, 0, 0, z, 540, sy);
  Z = z;
  const close = smooth(ev(t, C.blink, 0.3));
  const open = 1 - close;
  drawEye(0, 0, 1, Math.max(0.0, open), t, pr => {
    // the dish seen from above, reflected in the pupil
    ctx.fillStyle = '#16120E'; ctx.beginPath(); ctx.arc(0, 0, pr, 0, TAU); ctx.fill();
    pupilRings(t, pr, 0.8);
  });
  const top = -560 / 1;
  screenCam();
  writeOn([...'下一个「如果」'], 140, 360, charTimes('L19', '下一个如果').reduce((a, v, i) => { a.push(v); if (i === 2) a.push(v); if (i === 4) a.push(v + 0.1); return a; }, []).slice(0, 7), t, { size: 120 });
  const tq = charTimes('L19', '你想看什么');
  writeOn([...'你想看什么？'], 140, 520, [...tq, tq[tq.length - 1] + 0.12], t, { size: 120 });
  if (t > 87.4) text('如果 · 会怎样   01', W / 2, 1530, { align: 'center', size: 40, weight: 400, color: INK, alpha: 0.8 });
  // the vision front closing: radio world on the left until it passes
  if (fp < 1) {
    const fx = lerp(W + 60, -60, ease(fp));
    ctx.save(); ctx.beginPath(); ctx.rect(0, 0, fx, H); ctx.clip();
    S13(t);
    ctx.restore();
    seam(fx);
  }
  grainPass(0.35);
}
