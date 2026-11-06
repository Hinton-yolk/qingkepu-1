// ================================================================== v2 scenes
const SHT = id => CUES.shots.find(s => s[0] === id)[1];

// ------------------------------------------------------------------ S06 · one continuous pan: weakened by a wall, absorbed by a body, reflected by metal
const PR = { floor: 420, ceil: -780, A: [-650, 150], B: [1720, 150], w1: [-260, -220], w2: [735, 765], M: [1050, 1210, 30] };
function prPerson(t) {
  const x = lerp(170, 330, ev(t, SHT('S06'), 6));
  return { x, h: 540, ph: x / 50 };
}
function camProps(t) {
  const xs = [[SHT('S06'), -430], [C.body - 0.35, 250], [C.metal - 0.35, 1180]];
  let x = xs[0][1];
  for (let i = 1; i < xs.length; i++) x = lerp(x, xs[i][1], expoInOut(ev(t, xs[i][0], 0.8)));
  return [x, -140, 0.92 + 0.03 * smooth(ev(t, SHT('S06'), 6))];
}
function S06v2(t) {
  darkBG();
  const [cx, cy, z] = camProps(t);
  setCam(cx, cy, z);
  const P = prPerson(t);
  const ptop = PR.floor - 0.95 * P.h, pbot = PR.floor - 0.1 * P.h, prr = 0.11 * P.h;
  const [ml, mr, mtop] = PR.M, mbot = PR.floor;
  const lam = 90, v = 75, kk = TAU / lam, w = TAU * v / lam;
  const ax = PR.A[0], ay = PR.A[1] - 90, bx = PR.B[0], by = PR.B[1] - 90;
  field((x, y) => {
    if (y > PR.floor || y < PR.ceil) return 0.05;
    let val = 0;
    // router A (left): through the first wall, past the person
    {
      let att = 1;
      if (x > PR.w1[0]) att *= 0.38;
      if (x > PR.w2[0]) att *= 0.38;
      if (blocked(ax, ay, x, y, P.x, ptop, pbot, prr)) att *= 0.08;
      if (x > ml && ax < ml) { const yc = ay + (y - ay) * (ml - ax) / (x - ax); if (yc > mtop && yc < mbot) att = 0; }
      const dx = x - ax, dy = y - ay, r = Math.sqrt(dx * dx + dy * dy);
      const a = 1.9 * falloff(r, 420) * att;
      const E = a * Math.cos(kk * r - w * t);
      val += 0.35 * a * a + 0.85 * (E > 0 ? E * E : 0);
    }
    // router B (right): the metal box mirrors it
    {
      let att = 1;
      if (x < PR.w2[1]) att *= 0.38;
      if (x < PR.w1[1]) att *= 0.38;
      let shade = 1;
      if (x < mr) { const yc = by + (y - by) * (mr - bx) / (x - bx); if (yc > mtop && yc < mbot) shade = 0; }
      if (x > ml && x < mr && y > mtop) return 0;
      const dx = x - bx, dy = y - by, r = Math.sqrt(dx * dx + dy * dy);
      const a = 1.9 * falloff(r, 420) * att * shade;
      let I = a * a, E = a * Math.cos(kk * r - w * t);
      if (x > mr) {
        const ix = 2 * mr - bx, yc = by + (y - by) * (mr - ix) / (x - ix);
        if (yc > mtop && yc < mbot) {
          const ddx = x - ix, rr = Math.sqrt(ddx * ddx + dy * dy), ar = 1.9 * falloff(rr, 420) * 0.95;
          I += ar * ar; E += ar * Math.cos(kk * rr - w * t + Math.PI);
        }
      }
      val += 0.35 * I + 0.85 * (E > 0 ? E * E : 0);
    }
    return val;
  }, { gain: 1.2 });
  const c = DLINE;
  ink([[-1400, PR.floor], [2400, PR.floor]], 4, c, { key: 3000 });
  ink([[-1400, PR.ceil], [2400, PR.ceil]], 4, c, { key: 3001 });
  // walls: frosted bands
  for (const [x0, x1] of [PR.w1, PR.w2]) {
    ctx.fillStyle = 'rgba(236,228,214,0.12)'; ctx.fillRect(x0, PR.ceil, x1 - x0, PR.floor - PR.ceil);
    hatchRect(x0, PR.ceil, x1 - x0, PR.floor - PR.ceil, 0.8, 12, 2, c, 0.6, 3002 + x0);
    ink([[x0, PR.ceil], [x0, PR.floor]], 2.5, c, { key: 3010 + x0 }); ink([[x1, PR.ceil], [x1, PR.floor]], 2.5, c, { key: 3020 + x1 });
  }
  // router A on a side table, router B on a shelf
  table(PR.A[0] - 110, PR.floor, 220, PR.floor - PR.A[1], 'radio', 3030);
  drawRouter(PR.A[0], PR.A[1], 1, 'radio', 1);
  ink([[PR.B[0] - 140, PR.B[1]], [PR.B[0] + 140, PR.B[1]]], 5, c, { key: 3040 });
  drawRouter(PR.B[0], PR.B[1], 1, 'radio', 1);
  plant(-980, PR.floor, 1.4, 'radio', 3050);
  inkRect(-60, -560, 220, 300, 3, c, { key: 3060 });            // a window between the walls
  // the person
  drawPerson(P.x, PR.floor, P.h, 'walk', 'radio', { dir: 1, ph: P.ph, rim: 1 });
  // the metal box: dark inside, its right face a bright mirror
  ctx.fillStyle = '#000'; ctx.fillRect(ml, mtop, mr - ml, mbot - mtop);
  ink([[ml, mtop], [ml, mbot]], 3, c, { raw: true, key: 3070 }); ink([[ml, mtop], [mr, mtop]], 3, c, { raw: true, key: 3071 });
  ctx.globalCompositeOperation = 'lighter';
  ink([[mr, mtop], [mr, mbot]], 16, ACC, { raw: true, key: 3072, single: true, alpha: 0.5 });
  ink([[mr, mtop], [mr, mbot]], 6, HOT, { raw: true, key: 3073, single: true });
  const g = ev(t, C.metal, 0.8);
  if (g > 0 && g < 1) {
    const gy = lerp(mtop - 40, mbot + 40, g);
    const gr = ctx.createRadialGradient(mr, gy, 0, mr, gy, 110);
    gr.addColorStop(0, 'rgba(255,240,225,1)'); gr.addColorStop(1, 'rgba(255,106,26,0)');
    ctx.fillStyle = gr; ctx.fillRect(mr - 110, gy - 110, 220, 220);
  }
  ctx.globalCompositeOperation = 'source-over';
  ink([[ml + 20, mtop + 130], [mr - 20, mtop + 130]], 2.5, c, { raw: true, key: 3074 });
  // three readings, one per effect, on the words that name them
  reading('墙：削弱', PR.w1[0], -420, PR.w1[0] - 90, -560, t, C.wall, { color: DTEXT, size: 54, align: 'right' });
  reading('人体：吸收', P.x + 10, PR.floor - 0.72 * P.h, P.x + 170, PR.floor - 1.0 * P.h - 40, t, C.body, { color: DTEXT, size: 54, align: 'left' });
  reading('金属：反射', mr, mtop + 60, mr + 120, mtop - 150, t, C.metal, { color: DTEXT, size: 54, align: 'left' });
  grainPass(0.25);
}

// ------------------------------------------------------------------ S14 · the real world is not tidy: a whole city soaked in a messy field
const CITY = [];
(() => {
  const r = mulberry32(2026);
  let x = -9800;
  while (x < 9800) {
    const w = 700 + r() * 1300, h = 1400 + r() * 4800;
    if (x + w > -1100 && x < 1100) { x = 1100; continue; }      // leave room for our block in the middle
    CITY.push({ x, w, h, n: 3 + Math.floor(r() * 4), seed: Math.floor(r() * 1e6) });
    x += w + 120 + r() * 400;
  }
})();
const CITY_SRC = [];
for (const b of CITY) { const r = mulberry32(b.seed); for (let i = 0; i < b.n; i++) CITY_SRC.push({ x: b.x + 80 + r() * (b.w - 160), y: -150 - r() * (b.h - 300), ph: r() * TAU, k: 0.85 + r() * 0.3, f: 0.35 + r() * 0.5 }); }
function camCity(t) {
  const s = SHT('S14');
  const p = expoInOut(ev(t, C.soak, 2.4));
  const z0 = CAM_WIDE[2] * 0.92 * (1 - 0.06 * smooth(ev(t, s, C.soak - s)));
  const z = Math.exp(lerp(Math.log(z0), Math.log(0.075), p)) * (1 + 0.07 * smooth(ev(t, C.soak + 2.4, 3.2)));
  return [0, lerp(-1720, -5900, smooth(p)), z];
}
function S14city(t) {
  darkBG();
  const [cx, cy, z] = camCity(t);
  setCam(cx, cy, z);
  const own = buildingSources(t, { beaconStart: 25.8 }).map((s, i) => ({ x: s.x, y: s.y, ph: s.ph, k: 1, f: 0.35 + hash(i, 91) * 0.5 }));
  const src = own.concat(CITY_SRC);
  const m = smooth(ev(t, C.messy, 1.4));                     // tidy rings -> real, messy field
  const lam = Math.max(40, 52 / z), kk = TAU / lam;
  const r0 = lerp(170, 900, smooth(ev(t, C.soak, 2.4)));
  const n = src.length;
  field((x, y) => {
    if (y > 0) return 0.06;
    let inc = 0, tidy = 0, E = 0;
    for (let i = 0; i < n; i++) {
      const s = src[i], dx = x - s.x, dy = y - s.y, r = Math.sqrt(dx * dx + dy * dy);
      const a = falloff(r, r0);
      if (a < 0.02) continue;
      const a2 = a * a;
      inc += a2;
      if (m < 1) tidy += a2 * crest(r, t, 40, 150, s.ph);
      if (m > 0) {
        const wt = TAU * s.f * t;
        E += a * Math.cos(kk * s.k * r - wt + s.ph);
        const ry = -y - s.y, rr = Math.sqrt(dx * dx + ry * ry);   // a reflection off the ground
        E -= 0.6 * falloff(rr, r0) * Math.cos(kk * s.k * rr - wt + s.ph);
      }
    }
    const messy = 0.3 * inc + 0.55 * E * E;
    return (1 - m) * (0.3 * inc + 0.7 * tidy) + m * messy;
  }, { gain: 1.25 });
  // the skyline
  for (const b of CITY) {
    ctx.fillStyle = 'rgba(14,13,12,0.42)'; ctx.fillRect(b.x, -b.h, b.w, b.h);
    ink([[b.x, 0], [b.x, -b.h], [b.x + b.w, -b.h], [b.x + b.w, 0]], 3, DLINE, { key: 3100 + b.seed % 997 });
    if (z > 0.06) for (let yy = -400; yy > -b.h; yy -= 400) ink([[b.x, yy], [b.x + b.w, yy]], 1.6, DLINE, { key: 3200 + yy + b.seed % 97, alpha: 0.5, single: true });
  }
  drawBuilding(t, { noNeigh: true });
  ink([[-12000, 0], [12000, 0]], 4, DLINE, { key: 3300 });
  grainPass(0.25);
}

// ------------------------------------------------------------------ S15 · back to the eye (loops to frame 0)
function S15end(t) {
  const s = SHT('S15');
  const fp = ev(t, s, 0.9);
  paperBG();
  const mm = smooth(ev(t, s + 1.0, 1.6));
  const z = lerp(EYE_S, 1, mm);
  const sy = lerp(EYE_SCREEN[1], 1080, mm);
  setCam(0, 0, 1);
  ctx.setTransform(z, 0, 0, z, 540, sy);
  Z = z;
  const open = 1 - smooth(ev(t, C.blink, 0.3));
  drawEye(0, 0, 1, Math.max(0, open), t, pr => {
    ctx.fillStyle = '#16120E'; ctx.beginPath(); ctx.arc(0, 0, pr, 0, TAU); ctx.fill();
    pupilRings(t, pr, 0.8);
  });
  screenCam();
  const ct = charTimes('L16', '下一个如果');
  writeOn([...'下一个「如果」'], 140, 360, [ct[0], ct[1], ct[2], ct[2], ct[3], ct[4], ct[4] + 0.1], t, { size: 120 });
  const tq = charTimes('L16', '你想看什么');
  writeOn([...'你想看什么？'], 140, 520, [...tq, tq[tq.length - 1] + 0.12], t, { size: 120 });
  const L16 = TL.lines.find(l => l.id === 'L16');
  if (t > L16.t1 + 0.3) text('如果 · 会怎样   01', W / 2, 1530, { align: 'center', size: 40, weight: 400, color: INK, alpha: 0.8 });
  if (fp < 1) {          // the vision front closes the Wi-Fi eyes, right to left
    const fx = lerp(W + 60, -60, ease(fp));
    ctx.save(); ctx.beginPath(); ctx.rect(0, 0, fx, H); ctx.clip();
    S14city(t);
    ctx.restore();
    seam(fx);
  }
  grainPass(0.35);
}
