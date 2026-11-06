// ================================================================== the building (S04 router close-up, S05 pull-out, S09/S10)
const B = { UW: 480, UH: 400, cols: 3, floors: 8, x0: -720 };
const HOME = [1, 6];
const ATT = [1, 0.4, 0.17, 0.075, 0.033, 0.015, 0.007, 0.003, 0.001, 0, 0, 0, 0, 0];
function unitBox(c, f) { const l = B.x0 + c * B.UW; return { l, r: l + B.UW, top: -(f + 1) * B.UH, bot: -f * B.UH }; }
function routerAt(c, f) {
  if (c === HOME[0] && f === HOME[1]) return [120, -2570];
  const b = unitBox(c, f);
  return [b.l + 90 + hash(c, f, 1) * 300, b.bot - 150 - hash(c, f, 2) * 80];
}
// neighbour buildings at the edges of the wide shot
const NEIGH = [];
for (let i = 0; i < 10; i++) {
  const left = i < 5, k = i % 5;
  NEIGH.push({ x: left ? -1350 + hash(i, 7) * 260 : 1080 + hash(i, 8) * 300, y: -300 - k * 520 - hash(i, 9) * 200, ph: hash(i, 10) });
}
function litTime(c, f) { const v = CUES.lit[`${c},${f}`]; return v === undefined ? 1e9 : v; }
function routerAmp(c, f, t) {
  const tl = litTime(c, f);
  if (t < tl) return 0;
  return 1 + 1.6 * Math.exp(-(t - tl) / 0.22);
}
// each router's beacon: one visible flash per beat at its own phase (slowed down)
function beaconTimes(c, f, t, start) {
  const per = 0.6, off = (c === HOME[0] && f === HOME[1]) ? 0 : hash(c, f, 5) * per;
  const out = [];
  const n = Math.floor((t - start - off) / per);
  for (let k = Math.max(0, n - 3); k <= n; k++) out.push(start + off + k * per);
  return out;
}
function buildingSources(t, o) {
  const S = [];
  for (let c = 0; c < B.cols; c++) for (let f = 0; f < B.floors; f++) {
    const a = routerAmp(c, f, t);
    if (a <= 0) continue;
    const [x, y] = routerAt(c, f);
    S.push({ x, y: y - 90, a, c, f, ph: hash(c, f, 6) * TAU, tb: beaconTimes(c, f, t, o.beaconStart ?? C.beacons) });
  }
  return S;
}
function buildingField(t, o = {}) {
  const S = buildingSources(t, o);
  const lam = 40, v = 150, lod = o.lod ?? ringLOD(lam);
  const pulsed = o.pulsed ?? 0;           // 0 = steady lamp, 1 = beacons only
  const vb = 380, wb = o.wb ?? 16;
  const NS = NEIGH.map(n => ({ x: n.x, y: n.y }));
  return (x, y) => {
    let c = Math.floor((x - B.x0) / B.UW), f = Math.floor(-y / B.UH), out = 0;
    if (c < 0) { out += -c; c = 0; } else if (c > 2) { out += c - 2; c = 2; }
    if (f < 0) { out += 1; f = 0; } else if (f > 7) { out += 1; f = 7; }
    let val = 0;
    for (let i = 0; i < S.length; i++) {
      const s = S[i];
      const n = Math.abs(c - s.c) + Math.abs(f - s.f) + out;
      const at = ATT[n];
      if (!at) continue;
      const dx = x - s.x, dy = y - s.y, r = Math.sqrt(dx * dx + dy * dy);
      const fo = s.a * at * falloff(r, 170);
      let w = 0.3;
      if (lod > 0) w = lod * crest(r, t, lam, v, s.ph) + (1 - lod) * 0.3;
      val += fo * (1 - pulsed) * (0.32 + 0.68 * w);
      if (pulsed > 0) val += fo * pulsed * (0.18 + 2.2 * shells(r, t, s.tb, vb, wb));
    }
    // frosted walls scatter a little of the light that passes them
    const ux = (x - B.x0) % B.UW, uy = (-y) % B.UH;
    if (x > B.x0 - 12 && x < B.x0 + B.cols * B.UW + 12 && y < 12 && y > -B.floors * B.UH - 12) {
      if (ux < 10 || ux > B.UW - 10 || uy < 12 || uy > B.UH - 12) val *= 1.0 + 0.5 * (o.frost ?? 0.6);
    }
    // the neighbours across the street
    if (o.neigh) for (let i = 0; i < NS.length; i++) {
      const dx = x - NS[i].x, dy = y - NS[i].y;
      val += 0.5 * o.neigh / (1 + (dx * dx + dy * dy) / 9000);
    }
    return val;
  };
}
function unitFurniture(c, f, mode) {
  const b = unitBox(c, f), y = b.bot, k = 1000 + c * 37 + f * 101;
  const type = Math.floor(hash(c, f, 3) * 4);
  if (c === HOME[0] && f === HOME[1]) {
    sofa(b.l + 40, y, 230, mode, k); plant(b.r - 40, y, 0.8, mode, k + 9);
    ink([[b.l + 280, b.bot - 150], [b.r - 20, b.bot - 150]], 5, lineCol(mode), { key: k + 20 });
    return;
  }
  if (type === 0) { sofa(b.l + 60, y, 220, mode, k); table(b.l + 300, y, 90, 90, mode, k + 5); }
  else if (type === 1) { bed(b.l + 40, y, 260, mode, k); lampStand(b.r - 70, y, 150, mode, k + 6); }
  else if (type === 2) { fridge(b.l + 30, y, 90, 220, mode, k); table(b.l + 170, y, 220, 120, mode, k + 5); }
  else { desk(b.l + 200, y, 200, mode, k); plant(b.l + 70, y, 0.8, mode, k + 8); }
  // the router's shelf
  const [rx, ry] = routerAt(c, f);
  ink([[rx - 90, ry], [rx + 90, ry]], 4, lineCol(mode), { key: k + 30 });
}
function drawBuilding(t, o = {}) {
  const mode = 'radio', c0 = DLINE;
  // ground, trees, street
  ink([[-2600, 0], [2600, 0]], 5, c0, { key: 900 });
  for (let i = 0; i < 8; i++) {
    const x = -2300 + i * 640 + hash(i, 11) * 120;
    if (x > B.x0 - 120 && x < B.x0 + B.cols * B.UW + 120) continue;
    inkCircle(x, -170, 90 + 20 * hash(i, 12), 3, c0, { key: 910 + i });
    ink([[x, 0], [x, -90]], 4, c0, { key: 930 + i });
  }
  // neighbour buildings (outline + their routers)
  if (!o.noNeigh) for (const [x0, x1, top] of [[-2400, -1000, -2800], [1000, 2500, -3400]]) {
    ink([[x0, 0], [x0, top], [x1, top], [x1, 0]], 4, c0, { key: 950 + x0, alpha: 0.7 });
    for (let yy = -400; yy > top; yy -= 400) ink([[x0, yy], [x1, yy]], 2, c0, { key: 960 + yy, alpha: 0.45 });
  }
  // our building: units
  const bl = B.x0, br = B.x0 + B.cols * B.UW, btop = -B.floors * B.UH;
  for (let c = 0; c < B.cols; c++) for (let f = 0; f < B.floors; f++) {
    unitFurniture(c, f, mode);
    const [rx, ry] = routerAt(c, f);
    const a = routerAmp(c, f, t);
    drawRouter(rx, ry, 0.55, 'radio', a > 0 ? 1 : 0.15);
    if (hash(c, f, 4) < 0.55 && !(c === HOME[0] && f === HOME[1])) {
      const b = unitBox(c, f);
      const px = b.l + 120 + hash(c, f, 9) * 240;
      const walk = hash(c, f, 10) < 0.4;
      drawPerson(px + (walk ? Math.sin(t * 0.6 + c + f) * 40 : 0), b.bot, 230, walk ? 'walk' : 'phone', 'radio', { dir: hash(c, f, 11) < 0.5 ? 1 : -1, ph: t * 5 + f, rim: rx > px ? 1 : -1 });
    }
  }
  // frosted walls and slabs
  ctx.fillStyle = `rgba(236,228,214,${0.06 + 0.1 * (o.frost ?? 0)})`;
  for (let c = 0; c <= B.cols; c++) ctx.fillRect(bl + c * B.UW - 10, btop, 20, -btop);
  for (let f = 0; f <= B.floors; f++) ctx.fillRect(bl - 10, -f * B.UH - 12, br - bl + 20, 24);
  for (let c = 0; c <= B.cols; c++) {
    const x = bl + c * B.UW;
    ink([[x - 10, 0], [x - 10, btop]], 2, c0, { key: 970 + c, alpha: 0.8 });
    ink([[x + 10, 0], [x + 10, btop]], 2, c0, { key: 975 + c, alpha: 0.8 });
  }
  for (let f = 0; f <= B.floors; f++) {
    const y = -f * B.UH;
    ink([[bl - 10, y - 12], [br + 10, y - 12]], 2.2, c0, { key: 980 + f, alpha: 0.8 });
    ink([[bl - 10, y + 12], [br + 10, y + 12]], 2.2, c0, { key: 990 + f, alpha: 0.8 });
  }
  // roof: parapet, tank, mast
  ink([[bl - 20, btop - 12], [bl - 20, btop - 70], [br + 20, btop - 70], [br + 20, btop - 12]], 4, c0, { key: 995 });
  inkRect(-300, btop - 300, 220, 160, 4, c0, { key: 996 });
  ink([[-280, btop - 140], [-280, btop - 70]], 4, c0, { key: 997 }); ink([[-100, btop - 140], [-100, btop - 70]], 4, c0, { key: 998 });
  ink([[300, btop - 70], [300, btop - 420]], 4, c0, { key: 999 });
}
// the room around the home router, only drawn when we are close
function homeDetail(mode) {
  const b = unitBox(...HOME), c = lineCol(mode);
  inkRect(b.l + 60, b.top + 60, 150, 110, 3, c, { key: 1201 });         // window
  ink([[b.l + 135, b.top + 60], [b.l + 135, b.top + 170]], 2, c, { key: 1202 });
  ink([[60, -2570], [60, -2548], [84, -2570]], 3, c, { key: 1204 });     // shelf bracket
}
function camBuilding(t) {
  // S04 push on the router, S05 pull out through the wall to the whole block, then a slow drift
  const R = [120, -2640], M = [0, -1720];
  const s4 = SHT('S04'), s5 = SHT('S05');
  if (t < s5) { const k = expoInOut(ev(t, s4 + 0.3, Math.min(4.2, s5 - s4 - 1.2))); return [R[0] - 60 * (1 - k), R[1] + 120 * (1 - k), lerp(1.55, 3.4, k) * (1 + 0.03 * smooth((t - (s5 - 1.8)) / 1.8))]; }
  const p = expoInOut(ev(t, s5, 2.4));
  const z = Math.exp(lerp(Math.log(3.5), Math.log(0.47), p)) * (1 - 0.04 * smooth((t - (s5 + 2.4)) / 30));
  const q = smooth(p * 1.05);
  return [lerp(R[0], M[0], q), lerp(R[1], M[1], q), z];
}
function S04_05(t, o = {}) {
  darkBG();
  const [x, y, z] = o.cam ?? camBuilding(t);
  setCam(x, y, z);
  const pulsed = clamp((t - C.beacons) / 0.6);
  const frost = t > C.frost - 0.3 && t < SHT('S05') + 3.0 ? smooth(ev(t, C.frost - 0.3, 0.5)) : 0;
  field(buildingField(t, { pulsed, frost, neigh: 0.6 * smooth(ev(t, SHT('S05') + 1.4, 1.5)), wb: z > 1.5 ? 16 : 30, beaconStart: t < SHT('S05') + 2.6 ? C.beacons : SHT('S05') }), { gain: 1.15, blur: o.blur });
  if (o.blur) ctx.filter = `blur(${o.blur * 0.6}px)`;
  drawBuilding(t, { frost });
  if (z > 1.2) homeDetail('radio');
  ctx.filter = 'none';
  // the network name rides on the beacon shell
  if (t >= C.ssid && t < SHT('S05') + 1.4) {
    const [rx, ry] = routerAt(...HOME);
    const tbs = beaconTimes(...HOME, t, C.beacons).filter(b => b >= C.ssid - 0.05);
    for (const tb of tbs) {
      const r = 380 * (t - tb);
      if (r < 60 || r > 900) continue;
      const str = '702的WiFi';
      font(UI, 46 / Z, 700);
      ctx.fillStyle = HOT; ctx.globalAlpha = clamp(1 - r / 900);
      ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      for (let i = 0; i < str.length; i++) {
        const a = -Math.PI / 2 - 0.75 + i * (50 / Z) / r;
        ctx.save(); ctx.translate(rx + Math.cos(a) * r, ry - 90 + Math.sin(a) * r); ctx.rotate(a + Math.PI / 2);
        ctx.fillText(str[i], 0, -10 / Z); ctx.restore();
      }
      ctx.globalAlpha = 1;
    }
  }
  // readings
  if (t < SHT('S05') + 0.1) {
    const [rx, ry] = routerAt(...HOME);
    if (t >= C.beacons && t < SHT('S05')) {
      const [ax, ay] = toScreen(rx + 62, ry - 128);
      screenCam();
      reading('信标：每秒约 10 次', ax, ay, 120, 330, t, C.beacons, { color: DTEXT, size: 50, align: 'left' });
      if (t >= C.beacons + 0.5) text('画面已放慢 6 倍 · 示意', 132, 400, { size: 38, weight: 400, color: DTEXT, alpha: 0.85 });
      setCam(x, y, z);
    }
  }
  if (t >= C.lamp && t < C.beacons) {
    const [rx, ry] = routerAt(...HOME);
    const [ax, ay] = toScreen(rx - 82, ry - 20);
    screenCam();
    reading('发射功率 ≤ 0.1 瓦', ax, ay, 120, 1240, t, C.lamp, { color: DTEXT, size: 50, align: 'left' });
    if (t > C.lamp + 0.5) text('一盏很暗、但从不关的灯', 132, 1310, { size: 40, weight: 400, color: DTEXT });
    setCam(x, y, z);
  }
  if (t > SHT('S05') + 0.2 && t < SHT('S05') + 2.4) {
    const b = unitBox(...HOME);
    reading('墙 ≈ 毛玻璃', b.r - 10, b.top + 230, b.r - 10 - 60 / Z, b.top + 120, t, C.frost, { color: DTEXT, size: 48 });
  }
  if (t >= C.nbSide && t < 58) {
    const lab = (str, c, f, t0, side) => {
      const [rx, ry] = routerAt(c, f);
      reading(str, rx, ry - 60, rx + side * 150 / Z, ry - 200 / Z, t, t0, { color: DTEXT, size: 50 });
    };
    if (t < SHT('S09')) {
      lab('隔壁', 2, 6, C.nbSide, 1);
      lab('楼上', 1, 7, C.nbUp, -1);
      lab('楼下', 1, 5, C.nbDown, 1);
    }
  }
  grainPass(0.25);
}
