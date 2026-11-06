// ================================================================== v3 scenes: the title's four questions
// 0 hook (H1) · ① why can't we see it (S03 wave, P1 photon & molecule) · ② what not seeing means (D1 DNA, M1 microwave)
// ③ what we would see (S06v3 room, B1 blur → S11 500 m → S12/S13 FAST) · ④ what seeing means (R1 breathing) · end (E1)

// a section kicker: types on at the top-left, stays while its section lasts
function kicker(str, t, t0, o = {}) {
  if (t < t0) return;
  screenCam();
  const n = Math.floor(clamp((t - t0) * 28, 0, str.length));
  const col = o.color ?? INK;
  ctx.fillStyle = ACC; ctx.fillRect(72, 214, 44 * expoOut(ev(t, t0, .3)), 6);
  text(str.slice(0, n), 72, 290, { size: 50, color: col, weight: 700 });
}
const K1 = '① 为什么看不见？', K2 = '② 看不见，意味着什么？', K3 = '③ 要是看得见，会看到什么？', K4 = '④ 看见了，又意味着什么？';

// ------------------------------------------------------------------ H1 · the hook: your room, then the same room to Wi-Fi eyes
function H1(t) {
  paperBG();
  const zIn = expoInOut(ev(t, C.hkYou - .2, 1.0));
  const camx = lerp(0, RM_PERSON.x + 60, zIn), camy = lerp(-150, 180, zIn), z = lerp(0.92, 1.55, zIn) * (1 + .03 * smooth(t / 4));
  setCam(camx, camy, z);
  roomDraw('paper', t);
  if (t >= C.flip) {
    const fx = front(t, C.flip, 0.55);
    ctx.save(); screenCam(); ctx.beginPath(); ctx.rect(0, 0, fx, H); ctx.clip();
    setCam(camx, camy, z);
    field(roomField(t), { gain: 1.25 });
    roomDraw('radio', t);
    // the walls: what was solid is now a pale frosted glass
    const g = smooth(ev(t, C.hkWall, .5));
    if (g > 0) {
      ctx.globalCompositeOperation = 'lighter';
      for (const [x, y, w, h] of [[-560, -820, 60, 1360], [500, -820, 60, 1360]]) { ctx.fillStyle = `rgba(255,217,184,${.22 * g})`; ctx.fillRect(x, y, w, h); }
      ctx.globalCompositeOperation = 'source-over';
      reading('墙：透明', 530, -300, 300, -360, t, C.hkWall, { color: DTEXT, size: 46, align: 'right' });
    }
    reading('你：黑的', RM_PERSON.x + 40, 470 - .62 * RM_PERSON.h, RM_PERSON.x - 150, 470 - RM_PERSON.h - 30, t, C.hkYou + .25, { color: DTEXT, size: 46, align: 'right' });
    ctx.restore();
    if (fx < W + 60) seam(fx);
  }
  grainPass(0.3);
}

// ------------------------------------------------------------------ S03v3 · the reused wave zoom + the ratio
function S03v3(t) {
  S03(t);
  screenCam();
  if (t < C.bracket12 - .25) kicker(K1, t, SHT('S03') + .1);
  if (t >= C.ratio) {
    writeOn(['×', ' ', '2', '5', ' ', '万', ' ', '倍'], 540, 1180, [0, .04, .08, .12, .14, .18, .2, .24].map(x => C.ratio + x), t, { size: 130, align: 'center', color: ACC });
    if (t > C.ratio + .4) text('12.5 厘米 ÷ 0.0005 毫米', 540, 1260, { align: 'center', size: 40, weight: 400, color: FIG });
  }
}

// ------------------------------------------------------------------ P1 · photons as pushes: visible light flips the molecule, Wi-Fi can't
const MOL_BENT = [[-150, 40], [-100, 0], [-50, 40], [0, 0], [40, -45], [90, -20], [130, -65], [180, -40]];
const MOL_STR = [[-150, 40], [-100, 0], [-50, 40], [0, 0], [50, 40], [100, 0], [150, 40], [200, 0]];
function molecule(x, y, k, key, col = INK, s = 1.25) {
  const P = MOL_BENT.map((p, i) => [x + lerp(p[0], MOL_STR[i][0], k) * s, y + lerp(p[1], MOL_STR[i][1], k) * s]);
  ink(P, 6, col, { raw: true, key });
  for (const [px, py] of P) { ctx.fillStyle = col; ctx.beginPath(); ctx.arc(px, py, 8, 0, TAU); ctx.fill(); }
  // the ring at the start of the chain
  inkCircle(x - 205 * s, y + 20 * s, 45 * s, 5, col, { key: key + 1, n: 6 });
}
function packet(x, y, lam, amp, len, col, lw, t, ph = 0) {      // a short wave train: the photon
  ctx.strokeStyle = col; ctx.lineWidth = lw; ctx.lineCap = 'round'; ctx.beginPath();
  for (let i = 0; i <= 160; i++) {
    const u = -len / 2 + len * i / 160, env = Math.exp(-Math.pow(u / (len * .32), 2));
    const yy = y + amp * env * Math.sin(TAU * u / lam - t * 10 + ph);
    i ? ctx.lineTo(x + u, yy) : ctx.moveTo(x + u, yy);
  }
  ctx.stroke();
}
function P1(t) {
  paperBG(); screenCam();
  kicker(K1, t, -1);
  const dim = 1 - .88 * smooth(ev(t, C.punch, .4));
  ctx.globalAlpha = dim;
  // lane A: visible light
  const yA = 700, yB = 1140, mx = 640;
  const tL = SHT('P1') + .1;
  if (t >= tL) {
    text('可见光的光子', 72, yA - 170, { size: 44 }); text('≈ 2 eV', 72, yA - 116, { size: 40, weight: 400, color: FIG });
    text('Wi-Fi 的光子', 72, yB - 170, { size: 44, color: ACC }); text('≈ 0.00001 eV', 72, yB - 116, { size: 40, weight: 400, color: FIG });
  }
  // molecules arrive with 「感光分子」
  const mk = spring(t, C.mol, .5);
  if (t >= C.mol) {
    ctx.save(); ctx.globalAlpha = dim * clamp(mk);
    const flip = expoOut(ev(t, C.flip2, .25));
    molecule(mx, yA + 20, flip, 6100);
    const jig = t >= C.noMove - .3 ? Math.sin((t - C.noMove) * 40) * 3 * Math.exp(-(t - C.noMove + .3) * 4) : 0;
    molecule(mx + jig, yB + 20, 0, 6110);
    ctx.restore(); ctx.globalAlpha = dim;
    reading('感光分子（视黄醛）', mx + 120, yA - 40, mx + 60, yA - 120, t, C.mol + .2, { size: 38 });
  }
  // the visible photon: a tight, strong train that hits and flips
  if (t >= tL && t < C.flip2 + .6) {
    const hx = lerp(-120, mx - 260, expoIn(ev(t, C.push, C.flip2 - C.push)));
    const x = t < C.push ? lerp(-200, 220, smooth(ev(t, tL, .8))) : hx;
    if (t < C.flip2) packet(x, yA + 40, 22, 34, 220, INK, 6, t);
  }
  if (t >= C.flip2) {
    const k = ev(t, C.flip2, .5);
    text('咔', mx + 230, yA - 60, { size: 110 * (0.8 + .2 * backOut(k)), face: DISPLAY, color: INK, alpha: dim * (1 - smooth(ev(t, C.flip2 + 1.2, .3))) });
    const sx = lerp(mx + 260, 1040, expoOut(ev(t, C.flip2 + .15, .6)));
    ink([[mx + 260, yA + 20], [sx, yA + 20]], 4, INK, { raw: true, key: 6120, single: true, alpha: dim });
    if (t > C.flip2 + .6) text('→ 大脑：看见了', 1010, yA + 90, { size: 38, align: 'right', alpha: dim });
  }
  // the Wi-Fi photon: long and lazy; it arrives and nothing happens
  if (t >= tL) {
    const x = t < C.wifiPush ? lerp(-500, -240, smooth(ev(t, tL, 1))) : lerp(-240, mx - 300, expoOut(ev(t, C.wifiPush, .8)));
    packet(x, yB + 40, 260, 26, 560, ACC, 7, t * .25, 1);
  }
  if (t >= C.noMove) {
    const k = expoOut(ev(t, C.noMove, .3));
    text('推不动', mx - 40, yB + 200, { size: 96 * (0.7 + .3 * k), face: DISPLAY, color: ACC, alpha: dim, align: 'center' });
  }
  ctx.globalAlpha = 1;
  // ── V04 punch: not too dim — too light
  if (t >= C.punch) {
    writeOn([...'不是太暗，'], 72, 820, [0, .05, .1, .15, .2].map(x => C.punch + x), t, { size: 150 });
    writeOn([{ ch: '是' }, { ch: '太', col: ACC }, { ch: '轻', col: ACC }, { ch: '。' }], 72, 1010, [0, .05, .1, .15].map(x => C.punch2 + x), t, { size: 150 });
  }
  grainPass(0.3);
}

// ------------------------------------------------------------------ D1 · too light to flip a molecule, too light to break DNA: non-ionizing; at most a little heat
function helix(cx, y0, y1, t, k) {
  const n = 120, amp = 120, per = 340;
  const S = s => [cx + amp * Math.sin(TAU * s / per + t * .6), lerp(y0, y1, s / (y1 - y0))];
  const yEnd = lerp(y0, y1, k);
  for (const ph of [0, Math.PI]) {
    ctx.strokeStyle = INK; ctx.lineWidth = 7; ctx.lineCap = 'round'; ctx.beginPath();
    for (let i = 0; i <= n; i++) {
      const y = lerp(y0, y1, i / n); if (y > yEnd) break;
      const x = cx + amp * Math.sin(TAU * (y - y0) / per + t * .6 + ph);
      i ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
    }
    ctx.stroke();
  }
  for (let y = y0 + 20; y < yEnd; y += 42) {
    const a = TAU * (y - y0) / per + t * .6, x1 = cx + amp * Math.sin(a), x2 = cx + amp * Math.sin(a + Math.PI);
    ink([[x1, y], [x2, y]], 3.5, INK, { raw: true, key: 6200 + y, single: true, alpha: .8 });
  }
}
function D1(t) {
  paperBG(); screenCam();
  kicker(K2, t, SHT('D1') + .1);
  const k = expoOut(ev(t, SHT('D1') + .2, 1.2));
  const hx = 360;
  helix(hx, 420, 1300, t, k);
  if (t >= C.bond) reading('化学键 ≈ 几 eV', hx + 60, 820, hx + 260, 760, t, C.bond, { size: 40 });
  // Wi-Fi photons come in from the right and bounce off, the helix untouched
  if (t >= C.dna) {
    for (let i = 0; i < 3; i++) {
      const t0 = C.dna + i * .55, a = ev(t, t0, 1.3);
      if (a <= 0 || a >= 1) continue;
      const yy = 560 + i * 260, hitAt = .5;
      const x = a < hitAt ? lerp(1180, hx + 150, a / hitAt) : lerp(hx + 150, 1180, (a - hitAt) / (1 - hitAt));
      const yb = a < hitAt ? yy : yy - (a - hitAt) * 300;
      packet(x, yb, 120, 18, 300, ACC, 6, t * .3, i);
    }
  }
  if (t >= C.ion) {
    writeOn([...'非电离辐射'], 560, 560, [0, .05, .1, .15, .2].map(x => C.ion + x), t, { size: 96, color: ACC });
    if (t > C.ion + .4) text('能量太低，打不断化学键', 562, 630, { size: 38, weight: 400, color: FIG });
  }
  // a thermometer: just a little warmer
  if (t >= C.heat - .3) {
    const tx = 780, ty0 = 1260, ty1 = 820, q = spring(t, C.heat - .3, .4);
    ctx.save(); ctx.globalAlpha = clamp(q);
    inkRect(tx - 26, ty1, 52, ty0 - ty1, 4, INK, { key: 6300 }); inkCircle(tx, ty0 + 40, 48, 4, INK, { key: 6301 });
    const lv = lerp(ty0 - 60, ty0 - 150, expoOut(ev(t, C.heat, 1.2)));
    ctx.fillStyle = ACC; ctx.fillRect(tx - 16, lv, 32, ty0 + 20 - lv); ctx.beginPath(); ctx.arc(tx, ty0 + 40, 38, 0, TAU); ctx.fill();
    for (let i = 0; i < 8; i++) ink([[tx + 26, ty1 + 40 + i * 50], [tx + 46, ty1 + 40 + i * 50]], 2.5, INK, { raw: true, key: 6310 + i, single: true });
    text('微微发热', tx + 70, lv + 14, { size: 44, color: ACC });
    ctx.restore();
  }
  grainPass(0.3);
}

// ------------------------------------------------------------------ M1 · the microwave is on the same band: switch it on and the video stalls
function M1(t) {
  paperBG(); screenCam();
  kicker(K2, t, -1);
  const on = t >= C.ovenOn, lt = t - C.ovenOn;
  // the oven
  const ox = 90, oy = 470, ow = 640, oh = 400;
  ctx.fillStyle = PAPER2; ctx.fillRect(ox, oy, ow, oh);
  inkRect(ox, oy, ow, oh, 6, INK, { key: 6400 });
  inkRect(ox + 40, oy + 50, 420, 300, 4, INK, { key: 6401 });
  ctx.save(); ctx.beginPath(); ctx.rect(ox + 40, oy + 50, 420, 300); ctx.clip();
  if (on) { const g = ctx.createRadialGradient(ox + 250, oy + 200, 10, ox + 250, oy + 200, 260); g.addColorStop(0, `rgba(255,170,90,${.8})`); g.addColorStop(1, 'rgba(255,106,26,.15)'); ctx.fillStyle = g; ctx.fillRect(ox + 40, oy + 50, 420, 300); }
  for (let y = oy + 60; y < oy + 350; y += 16) for (let x = ox + 50; x < ox + 460; x += 16) { ctx.fillStyle = 'rgba(27,25,22,.35)'; ctx.fillRect(x, y, 5, 5); }
  ctx.restore();
  inkRect(ox + 500, oy + 60, 100, 70, 3, INK, { key: 6402 });
  text(on ? `0:${String(Math.max(0, 30 - Math.floor(lt))).padStart(2, '0')}` : '0:30', ox + 550, oy + 108, { size: 34, align: 'center', face: UI });
  inkCircle(ox + 550, oy + 220, 40, 3, INK, { key: 6403 });
  text('微波炉', ox, oy - 30, { size: 44 });
  // the band: both on the same line
  if (t >= C.band) {
    const k = expoOut(ev(t, C.band, .5)), y = 1000, x0 = 120, x1 = 960;
    ink([[x0, y], [lerp(x0, x1, k), y]], 4, INK, { raw: true, key: 6410 });
    for (const [f, lab, col, dy] of [[2.40, 'Wi-Fi 2.4 GHz', ACC, -26], [2.45, '微波炉 2.45 GHz', INK, 64]]) {
      const x = lerp(x0, x1, (f - 2.3) / .25);
      if (k > .5) { ink([[x, y - 18], [x, y + 18]], 4, col, { raw: true, key: 6411 + f * 10 }); text(lab, x, y + dy, { size: 38, align: 'center', color: col }); }
    }
    if (k > .8) text('几乎同一个频段', 540, 1150, { size: 44, align: 'center', color: FIG, weight: 400 });
  }
  // waves leaking toward the phone while it runs
  const px = 860, py = 760;
  if (on) {
    for (let i = 0; i < 4; i++) {
      const r = ((lt * 240 + i * 90) % 360);
      ctx.strokeStyle = `rgba(255,106,26,${.6 * (1 - r / 360)})`; ctx.lineWidth = 6;
      ctx.beginPath(); ctx.arc(ox + ow, oy + 200, r, -.6, .6); ctx.stroke();
    }
  }
  // the phone with a video; with 「会卡」 it stalls and spins
  ctx.fillStyle = PAPER2; ctx.beginPath(); ctx.roundRect(px - 90, py - 170, 180, 340, 24); ctx.fill();
  ctx.strokeStyle = INK; ctx.lineWidth = 5; ctx.beginPath(); ctx.roundRect(px - 90, py - 170, 180, 340, 24); ctx.stroke();
  ctx.fillStyle = '#2a2622'; ctx.fillRect(px - 72, py - 120, 144, 110);
  const playing = t < C.lag;
  const prog = playing ? (t * .08) % 1 : (C.lag * .08) % 1;
  ctx.fillStyle = ACC; ctx.fillRect(px - 72, py, 144 * prog, 6);
  if (!playing) {
    ctx.strokeStyle = PAPER2; ctx.lineWidth = 6; ctx.beginPath(); ctx.arc(px, py - 65, 26, t * 7, t * 7 + 4.2); ctx.stroke();
    text('缓冲中…', px, py + 60, { size: 30, align: 'center' });
  } else {
    ctx.fillStyle = PAPER2; ctx.beginPath(); ctx.moveTo(px - 14, py - 85); ctx.lineTo(px + 18, py - 65); ctx.lineTo(px - 14, py - 45); ctx.fill();
  }
  // Wi-Fi bars: full, then knocked down
  const bars = playing ? 3 : 1;
  for (let i = 1; i <= 3; i++) { ctx.strokeStyle = i <= bars ? ACC : 'rgba(27,25,22,.2)'; ctx.lineWidth = 7; ctx.beginPath(); ctx.arc(px, py + 150, 16 * i, -Math.PI * .75, -Math.PI * .25); ctx.stroke(); }
  grainPass(0.3);
}

// ------------------------------------------------------------------ S06v3 · the room to Wi-Fi eyes: lamp, glass door, mirror, a dark you
function camProps3(t) {
  const xs = [[SHT('S06'), -560, .95], [C.door - .3, -260, .95], [C.metal - .35, 1150, .95], [C.body - .3, 330, .62]];
  let x = xs[0][1], z = xs[0][2];
  for (let i = 1; i < xs.length; i++) { const p = expoInOut(ev(t, xs[i][0], .75)); x = lerp(x, xs[i][1], p); z = lerp(z, xs[i][2], p); }
  return [x, -140, z];
}
function S06v3(t) {
  darkBG();
  const [cx, cy, z] = camProps3(t);
  setCam(cx, cy, z);
  const P = { x: lerp(200, 300, ev(t, SHT('S06'), 6)), h: 540 }; P.ph = P.x / 50;
  const ptop = PR.floor - 0.95 * P.h, pbot = PR.floor - 0.1 * P.h, prr = 0.11 * P.h;
  const [ml, mr, mtop] = PR.M, mbot = PR.floor;
  const lam = 90, v = 75, kk = TAU / lam, w = TAU * v / lam;
  const ax = PR.A[0], ay = PR.A[1] - 90, bx = PR.B[0], by = PR.B[1] - 90;
  field((x, y) => {
    if (y > PR.floor || y < PR.ceil) return 0.05;
    let val = 0;
    { // router A: through the wooden door (barely dimmed) and the concrete wall, past you
      let att = 1;
      if (x > PR.w1[0]) att *= 0.85;
      if (x > PR.w2[0]) att *= 0.38;
      if (blocked(ax, ay, x, y, P.x, ptop, pbot, prr)) att *= 0.08;
      if (x > ml && ax < ml) { const yc = ay + (y - ay) * (ml - ax) / (x - ax); if (yc > mtop && yc < mbot) att = 0; }
      const dx = x - ax, dy = y - ay, r = Math.sqrt(dx * dx + dy * dy), a = 1.9 * falloff(r, 420) * att, E = a * Math.cos(kk * r - w * t);
      val += 0.35 * a * a + 0.85 * (E > 0 ? E * E : 0);
    }
    { // router B: mirrored by the metal box
      let att = 1;
      if (x < PR.w2[1]) att *= 0.38;
      if (x < PR.w1[1]) att *= 0.85;
      let shade = 1;
      if (x < mr) { const yc = by + (y - by) * (mr - bx) / (x - bx); if (yc > mtop && yc < mbot) shade = 0; }
      if (x > ml && x < mr && y > mtop) return 0;
      const dx = x - bx, dy = y - by, r = Math.sqrt(dx * dx + dy * dy), a = 1.9 * falloff(r, 420) * att * shade;
      let I = a * a, E = a * Math.cos(kk * r - w * t);
      if (x > mr) {
        const ix = 2 * mr - bx, yc = by + (y - by) * (mr - ix) / (x - ix);
        if (yc > mtop && yc < mbot) { const rr = Math.hypot(x - ix, dy), ar = 1.9 * falloff(rr, 420) * .95; I += ar * ar; E += ar * Math.cos(kk * rr - w * t + Math.PI); }
      }
      val += 0.35 * I + 0.85 * (E > 0 ? E * E : 0);
    }
    return val;
  }, { gain: 1.2 });
  const c = DLINE;
  ink([[-1400, PR.floor], [2400, PR.floor]], 4, c, { key: 3000 }); ink([[-1400, PR.ceil], [2400, PR.ceil]], 4, c, { key: 3001 });
  // a wooden door (almost clear) and a concrete wall (frosted)
  { const [x0, x1] = PR.w1; ctx.fillStyle = 'rgba(236,228,214,0.05)'; ctx.fillRect(x0, PR.floor - 560, x1 - x0, 560);
    ink([[x0, PR.floor], [x0, PR.floor - 560], [x1, PR.floor - 560], [x1, PR.floor]], 2.5, c, { key: 3005, alpha: .7 });
    ink([[x0, PR.floor - 560], [x0, PR.ceil]], 2.5, c, { key: 3006 }); ink([[x1, PR.floor - 560], [x1, PR.ceil]], 2.5, c, { key: 3007 });
    ctx.fillStyle = 'rgba(236,228,214,0.12)'; ctx.fillRect(x0, PR.ceil, x1 - x0, PR.floor - 560 - PR.ceil); }
  { const [x0, x1] = PR.w2; ctx.fillStyle = 'rgba(236,228,214,0.12)'; ctx.fillRect(x0, PR.ceil, x1 - x0, PR.floor - PR.ceil);
    hatchRect(x0, PR.ceil, x1 - x0, PR.floor - PR.ceil, 0.8, 12, 2, c, 0.6, 3002 + x0); }
  table(PR.A[0] - 110, PR.floor, 220, PR.floor - PR.A[1], 'radio', 3030);
  drawRouter(PR.A[0], PR.A[1], 1, 'radio', 1);
  ink([[PR.B[0] - 140, PR.B[1]], [PR.B[0] + 140, PR.B[1]]], 5, c, { key: 3040 });
  drawRouter(PR.B[0], PR.B[1], 1, 'radio', 1);
  plant(-980, PR.floor, 1.4, 'radio', 3050);
  drawPerson(P.x, PR.floor, P.h, 'walk', 'radio', { dir: 1, ph: P.ph, rim: 1 });
  ctx.fillStyle = '#000'; ctx.fillRect(ml, mtop, mr - ml, mbot - mtop);
  ink([[ml, mtop], [ml, mbot]], 3, c, { raw: true, key: 3070 }); ink([[ml, mtop], [mr, mtop]], 3, c, { raw: true, key: 3071 });
  ctx.globalCompositeOperation = 'lighter';
  ink([[mr, mtop], [mr, mbot]], 16, ACC, { raw: true, key: 3072, single: true, alpha: 0.5 }); ink([[mr, mtop], [mr, mbot]], 6, HOT, { raw: true, key: 3073, single: true });
  ctx.globalCompositeOperation = 'source-over';
  reading('路由器：一盏灯', PR.A[0], PR.A[1] - 60, PR.A[0] + 60, PR.A[1] - 330, t, C.router, { color: DTEXT, size: 54, align: 'left' });
  reading('木门：几乎透明', PR.w1[0] + 10, -120, PR.w1[0] + 90, -480, t, C.door, { color: DTEXT, size: 54, align: 'left' });
  reading('金属：镜子', mr, mtop + 60, mr + 120, mtop - 150, t, C.metal, { color: DTEXT, size: 54, align: 'left' });
  reading('你：一团黑影', P.x + 10, PR.floor - .72 * P.h, P.x + 200, PR.floor - P.h - 80, t, C.body + .2, { color: DTEXT, size: 70, align: 'left' });
  screenCam(); kicker(K3, t, SHT('S06') + .1, { color: DTEXT });
  grainPass(0.25);
}

// ------------------------------------------------------------------ B1 · but it is all a blur
function B1(t) {
  renderTo(OFF, () => S06v3(t));
  screenCam();
  drawBlurred(OFF, 5.5 * smooth(ev(t, C.blur, .9)));
  grainPass(0.25);
}

// ------------------------------------------------------------------ S13v3 · the reused quiet zone + a phone that glares
function S13v3(t) {
  S13(t);
  if (t >= C.glare) {
    screenCam();
    const k = expoOut(ev(t, C.glare, .5));
    const g = ctx.createRadialGradient(780, 560, 0, 780, 560, 420 * k);
    g.addColorStop(0, 'rgba(255,240,225,.95)'); g.addColorStop(.25, 'rgba(255,170,90,.6)'); g.addColorStop(1, 'rgba(255,106,26,0)');
    ctx.globalCompositeOperation = 'lighter'; ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); ctx.globalCompositeOperation = 'source-over';
    text('一部手机', 780, 560 + 30, { size: 40, align: 'center', color: DARK, weight: 700 });
    text('（比喻：手机信号会干扰天眼）', 540, 1300, { size: 34, align: 'center', color: DTEXT, weight: 400 });
  }
}

// ------------------------------------------------------------------ R1 · the other way round: you reflect Wi-Fi, so Wi-Fi can see you breathe
const BR = { rx: -330, ry: 120, wall: [-70, -10], px: 300, floor: 420, h: 520 };
function R1(t) {
  darkBG();
  setCam(0, -60, 1.0);
  const per = 3.6, chest = .5 + .5 * Math.sin(TAU * (t - C.refl) / per);
  const lam = 80, v = 70, kk = TAU / lam, w = TAU * v / lam;
  const sx = BR.rx, sy = BR.ry - 80, qx = BR.px + 40, qy = BR.floor - .62 * BR.h;
  const echoOn = smooth(ev(t, C.refl, .6));
  field((x, y) => {
    if (y > BR.floor || y < -760) return .04;
    let val = 0;
    let att = 1; if ((x - BR.wall[0]) * (sx - BR.wall[0]) < 0) att *= .55;
    const r = Math.hypot(x - sx, y - sy), a = 1.7 * falloff(r, 380) * att, E = a * Math.cos(kk * r - w * t);
    val += .3 * a * a + .8 * (E > 0 ? E * E : 0);
    // the echo off your chest: it starts where you are, its phase moves with each breath
    if (echoOn > 0) {
      let at2 = 1; if ((x - BR.wall[0]) * (qx - BR.wall[0]) < 0) at2 *= .55;
      const rr = Math.hypot(x - qx, y - qy), ar = 1.2 * falloff(rr, 300) * at2 * echoOn * (x < qx ? 1 : .3);
      const Er = ar * Math.cos(kk * rr - w * t + 2.2 * chest);
      val += .8 * (Er > 0 ? Er * Er : 0);
    }
    return val;
  }, { gain: 1.2 });
  const c = DLINE;
  ink([[-900, BR.floor], [900, BR.floor]], 4, c, { key: 6500 });
  ctx.fillStyle = 'rgba(236,228,214,0.12)'; ctx.fillRect(BR.wall[0], -760, BR.wall[1] - BR.wall[0], BR.floor + 760);
  hatchRect(BR.wall[0], -760, BR.wall[1] - BR.wall[0], BR.floor + 760, .8, 12, 2, c, .6, 6501);
  table(BR.rx - 110, BR.floor, 220, BR.floor - BR.ry, 'radio', 6502);
  drawRouter(BR.rx, BR.ry, 1, 'radio', 1);
  // you, behind the wall, breathing
  ctx.save(); ctx.translate(BR.px, BR.floor); ctx.scale(1 + .025 * chest, 1); ctx.translate(-BR.px, -BR.floor);
  drawPerson(BR.px, BR.floor, BR.h, 'walk', 'radio', { dir: -1, ph: 0, rim: 1 });
  ctx.restore();
  // the router's eye opens: it sees you
  if (t >= C.see) {
    const op = expoOut(ev(t, C.see, .5));
    drawEye(BR.rx, BR.ry - 230, .32, op, t, null, { noGlint: true });
  }
  reading('墙', BR.wall[1], -560, BR.wall[1] + 70, -640, t, C.wall, { color: DTEXT, size: 46 });
  // the breathing trace, read from the echo
  screenCam(); kicker(K4, t, SHT('R1') + .1, { color: DTEXT });
  if (t >= C.echo) {
    const x0 = 120, x1 = 960, y = 1260, k = clamp((t - C.echo) / 2.6);
    ctx.fillStyle = 'rgba(14,13,12,.75)'; ctx.fillRect(x0 - 30, y - 120, x1 - x0 + 60, 200);
    ctx.strokeStyle = HOT; ctx.lineWidth = 6; ctx.lineCap = 'round'; ctx.beginPath();
    for (let i = 0; i <= 200 * k; i++) {
      const u = i / 200, tt = C.echo + u * 2.6 * 2;
      const yy = y - 50 * Math.sin(TAU * (tt - C.refl) / per) - 6 * Math.sin(tt * 23);
      i ? ctx.lineTo(lerp(x0, x1, u), yy) : ctx.moveTo(lerp(x0, x1, u), yy);
    }
    ctx.stroke();
    if (t >= C.breath) text('呼吸', x0, y - 82, { size: 44, color: HOT });
    text('反射信号的变化', x1, y - 82, { size: 32, color: DTEXT, align: 'right', weight: 400 });
  }
  grainPass(0.25);
}

// ------------------------------------------------------------------ E1 · Wi-Fi can see you: the router's eye, the end card
function E1(t) {
  darkBG();
  setCam(0, 0, 1 + .1 * smooth(ev(t, SHT('E1'), 4)));
  const lam = 80, v = 70;
  field((x, y) => { const r = Math.hypot(x, y - 260); return 1.8 * falloff(r, 300) * (.3 + .7 * crest(r, t, lam, v)); }, { gain: 1.1 });
  drawRouter(0, 330, 1.6, 'radio', 1);
  const op = 1 - smooth(ev(t, C.blink, .15)) + smooth(ev(t, C.blink + .2, .2));
  drawEye(0, 80, .7, Math.min(1, expoOut(ev(t, SHT('E1'), .6)) * op), t, null, { noGlint: false });
  screenCam();
  if (t >= C.endCard) {
    text('如果……会怎样 · 01', 72, 300, { size: 40, color: DTEXT, weight: 400 });
    writeOn([...'如果你的眼睛'], 72, 430, [0, .04, .08, .12, .16, .2].map(x => C.endCard + x), t, { size: 96, color: DTEXT });
    writeOn([...'能看见 ', { ch: 'Wi-Fi', col: ACC }], 72, 550, [.3, .34, .38, .42, .46].map(x => C.endCard + x), t, { size: 96, color: DTEXT });
  }
  grainPass(0.25);
}
