// ================================================================== S01 · the eye opens
const EYE_Y = 120;   // eye centre in S01 world (screen y 1080)
function charTimes(lid, sub) {
  // per-character landing times for `sub` inside line lid, from the word boundaries
  const L = TL.lines.find(l => l.id === lid);
  let acc = '', map = [];
  for (const w of L.words) {
    for (let i = 0; i < w.w.length; i++) map.push({ ch: w.w[i], t: w.t0 + (w.t1 - w.t0) * i / w.w.length });
    acc += w.w;
  }
  const out = [];
  let k = 0;
  for (const ch of sub) {
    while (k < map.length && map[k].ch !== ch) k++;
    out.push(k < map.length ? map[k].t : (out.length ? out[out.length - 1] + 0.08 : L.t0));
    k++;
  }
  return out;
}
function S01(t) {
  paperBG();
  const pp = ev(t, C.pupilPush, 0.6);
  const z = Math.exp(lerp(0, Math.log(13), expoIn(pp)));
  setCam(0, EYE_Y * smooth(pp * 1.6), z);
  const open = 1;
  // what the eye now sees: rings leave the pupil, one per beat, and cross the page
  if (open > 0.3) {
    ctx.save(); ctx.beginPath(); ctx.rect(-3000, -3000, 6000, 6000);
    { const { up, lo } = eyeLids(open); ctx.moveTo(up[0][0], up[0][1] + EYE_Y); ctx.bezierCurveTo(up[1][0], up[1][1] + EYE_Y, up[2][0], up[2][1] + EYE_Y, up[3][0], up[3][1] + EYE_Y);
      ctx.bezierCurveTo(lo[2][0], lo[2][1] + EYE_Y, lo[1][0], lo[1][1] + EYE_Y, lo[0][0], lo[0][1] + EYE_Y); ctx.closePath(); }
    ctx.clip('evenodd');
    for (let k = 0; k < 6; k++) {
      const tb = Math.floor(t / 0.6) * 0.6 - k * 0.6 + 0.3;
      if (tb > t) continue;
      const r = EYE.r + (t - tb) * 900;
      const al = clamp(1 - (t - tb) / 2.8);
      ctx.strokeStyle = ACC; ctx.globalAlpha = al * 0.22; ctx.lineWidth = 44 / Z;
      ctx.beginPath(); ctx.arc(0, EYE_Y, r, 0, TAU); ctx.stroke();
      ctx.globalAlpha = al; ctx.lineWidth = 13 / Z;
      ctx.beginPath(); ctx.arc(0, EYE_Y, r, 0, TAU); ctx.stroke();
    }
    ctx.restore(); ctx.globalAlpha = 1;
  }
  drawEye(0, EYE_Y, 1, open, t, pr => pupilRings(t, pr, 1));
  // title (in the page, above the eye): characters land on the spoken words
  const t1 = charTimes('L01', '如果眼睛'), t2 = charTimes('L01', '能看见');
  const tw = TL.lines[0].words.find(w => w.w.includes('Wi')).t0;
  const top = -600;
  writeOn('如果眼睛'.split(''), -400, top, t1.map(() => -1), t, { size: 140 });
  writeOn([...'能看见'.split(''), { ch: ' ', col: INK }, { ch: 'Wi-Fi', col: ACC }], -400, top + 175, [-1, -1, -1, -1, -1], t, { size: 140 });
  const t3 = charTimes('L01', '世界会变成什么样');
  writeOn([...'世界会变成什么样？'], -400, top + 290, [...t3, t3[t3.length - 1] + 0.1], t, { face: UI, size: 50, weight: 400 });
  // series mark, set like a printed page footer (not a corner tag)
  screenCam();
  text('如果 · 会怎样   01', W / 2, 1530, { align: 'center', size: 40, weight: 400, color: INK, alpha: 0.8 });
  setCam(0, EYE_Y * smooth(pp * 1.6), z);
  // the pupil becomes a window into the room
  if (t >= C.pupilPush) {
    const [sx, sy] = toScreen(0, EYE_Y);
    const rr = EYE.r * z;
    renderTo(OFF, () => S02(Math.max(t, SHT('S02')), true));
    ctx.save(); screenCam(); ctx.beginPath(); ctx.arc(sx, sy, rr, 0, TAU); ctx.clip();
    const k = Math.min(1, (rr * 2.3) / W);
    ctx.drawImage(OFF, sx - W * k / 2, sy - H * k / 2 + 40 * k, W * k, H * k);
    ctx.restore();
    screenCam();
    ctx.strokeStyle = INK; ctx.lineWidth = 10; ctx.beginPath(); ctx.arc(sx, sy, rr, 0, TAU); ctx.stroke();
  }
}

// ================================================================== S02 · the room, then the vision switches
const RM = { L: -500, R: 500, T: -760, F: 470 };
const RM_ROUTER = [370, -200];
const RM_PERSON = { x: -170, h: 480 };
function roomDraw(mode, t) {
  const c = lineCol(mode), radio = mode === 'radio';
  for (const [x, y, w, h] of [[-560, -820, 60, 1360], [500, -820, 60, 1360], [-560, -820, 1120, 60], [-560, 470, 1120, 80]]) {
    if (radio) { ctx.fillStyle = 'rgba(236,228,214,0.08)'; ctx.fillRect(x, y, w, h); }
    hatchRect(x, y, w, h, 0.8, 14, 2, c, radio ? 0.5 : 0.75, 50 + x);
  }
  ink([[-500, -760], [-500, 470], [500, 470], [500, -760], [-500, -760]], 4, c, { key: 51, closed: true });
  // window with the night outside
  inkRect(-380, -620, 260, 320, 4, c, { key: 52 });
  ink([[-250, -620], [-250, -300]], 3, c, { key: 53 }); ink([[-380, -460], [-120, -460]], 3, c, { key: 54 });
  if (!radio) {
    ctx.save(); ctx.beginPath(); ctx.rect(-380, -620, 260, 320); ctx.clip();
    hatch(-380, -620, 260, 320, -0.7, 12, 1.6, INK, 0.35, 55);
    ctx.fillStyle = PAPER; ctx.beginPath(); ctx.arc(-180, -560, 30, 0, TAU); ctx.fill();
    ctx.restore();
    inkCircle(-180, -560, 30, 2.5, INK, { key: 56 });
  }
  // picture frame and a clock
  inkRect(40, -640, 170, 120, 3.5, c, { key: 57 });
  ink([[55, -540], [100, -600], [130, -565], [160, -610], [195, -540]], 2.6, c, { key: 58, alpha: 0.8 });
  inkCircle(370, -560, 54, 3.5, c, { key: 59 });
  const ang = t * 0.5;
  ink([[370, -560], [370 + Math.cos(ang) * 38, -560 + Math.sin(ang) * 38]], 3, c, { raw: true, key: 591, single: true });
  ink([[370, -560], [370, -592]], 3, c, { raw: true, key: 592, single: true });
  // shelf + router
  ink([[250, -200], [500, -200]], 6, c, { key: 60 });
  ink([[300, -200], [300, -160], [340, -200]], 3, c, { key: 61 });
  drawRouter(RM_ROUTER[0], RM_ROUTER[1], 1.1, mode, 1);
  // floor lamp: on in visible light, dark to Wi-Fi eyes
  lampStand(-440, 470, 600, mode, 62);
  if (!radio) {
    for (let i = 0; i < 7; i++) {
      const a = Math.PI / 2 + (i - 3) * 0.17;
      const x0 = -440 + Math.cos(a) * 30, y0 = -126;
      ink([[x0, y0 + 10], [x0 + Math.cos(a) * 220, y0 + 10 + Math.sin(a) * 220]], 2, INK, { raw: true, key: 70 + i, single: true, alpha: 0.35 });
    }
  }
  sofa(-450, 470, 600, mode, 80);
  table(190, 470, 110, 150, mode, 84);
  ink([[222, 320], [226, 290], [256, 290], [260, 320]], 3, c, { key: 87 });
  plant(440, 470, 1.3, mode, 88);
  ink([[-400, 484], [320, 484]], 2.5, c, { key: 99, alpha: 0.5 });
  drawPerson(RM_PERSON.x, 470, RM_PERSON.h, 'sit', mode, { dir: 1, phone: true, rim: 1 });
}
function roomField(t) {
  const [rx, ry] = [RM_ROUTER[0], RM_ROUTER[1] - 90];
  const h = RM_PERSON.h, px = RM_PERSON.x, base = 470;
  const ptop = base - 0.72 * h, pbot = base - 0.28 * h, prr = 0.12 * h;
  const hand = [px + 0.2 * h, base - 0.52 * h];
  const lam = 70, v = 120, lod = ringLOD(lam);
  return (x, y) => {
    let out = (x < RM.L || x > RM.R || y < RM.T || y > RM.F) ? 0.45 : 1;
    const dx = x - rx, dy = y - ry, r = Math.sqrt(dx * dx + dy * dy);
    let a = 1.6 * falloff(r, 240) * out;
    if (blocked(rx, ry, x, y, px + 0.02 * h, ptop, pbot, prr)) a *= 0.12;
    let val = a * (0.28 + 0.72 * (lod * crest(r, t, lam, v) + (1 - lod) * 0.3));
    const hx = x - hand[0], hy = y - hand[1], hr = Math.sqrt(hx * hx + hy * hy);
    val += 0.5 * falloff(hr, 50) * (0.3 + 0.7 * crest(hr, t, lam, v, 1.3)) * out;
    return val;
  };
}
function S02(t, inPupil = false) {
  const lt = t - SHT('S02');
  const kp = smooth(ev(t, C.front1 + 0.6, SHT('S03') - C.front1 - 0.6));
  const z = 1 + 0.08 * smooth(lt / 3.6) + 0.26 * kp, camx = 210 * kp, camy = -60 - 110 * kp;
  paperBG(); setCam(camx, camy, z);
  roomDraw('paper', t);
  if (!inPupil && t >= C.front1) {
    const fx = front(t, C.front1, 0.9);
    ctx.save(); screenCam(); ctx.beginPath(); ctx.rect(0, 0, fx, H); ctx.clip();
    setCam(camx, camy, z);
    field(roomField(t), { gain: 1.25 });
    roomDraw('radio', t);
    ctx.restore();
    if (fx < W + 60) seam(fx);
  }
  if (!inPupil) grainPass(0.35);
}

// ================================================================== S03 · wavelength: a straight line that was a wave all along
function S03(t) {
  paperBG();
  const lam = 12.5, A = 3.5, zEnd = 760 / lam, z0 = 90 / 0.000055;
  const p = expoInOut(ev(t, C.zoomOut, 1.5));
  const z = Math.exp(lerp(Math.log(z0), Math.log(zEnd), p));
  const q = smooth(p);
  const cx = lerp(540, 160, q), cy = lerp(700, 447, q);       // screen position of the crest
  const S = (x, y) => [cx + x * z, cy + (y + A) * z];
  screenCam();
  // Wi-Fi wave (true geometry at every zoom)
  ctx.strokeStyle = ACC; ctx.lineWidth = 8; ctx.lineCap = 'round'; ctx.beginPath();
  for (let sx = -10; sx <= W + 10; sx += 3) {
    const x = (sx - cx) / z, y = -A * Math.cos(TAU * x / lam);
    const [, sy] = S(x, y);
    sx === -10 ? ctx.moveTo(sx, sy) : ctx.lineTo(sx, sy);
  }
  ctx.stroke();

  // visible light: a fine ink squiggle riding on the crest
  const lv = 0.000055, Av = 40 / z0;
  const rev = 0;
  if (rev > 0) {
    ctx.strokeStyle = INK; ctx.lineWidth = 4; ctx.beginPath();
    let first = true;
    const span = 450 / z0;
    for (let i = 0; i <= 600; i++) {
      const x = -span + 2 * span * i / 600;
      if (i / 600 > rev) break;
      const y = -A + Av * Math.sin(TAU * x / lv - t * 9);
      const [sx, sy] = S(x, y);
      first ? ctx.moveTo(sx, sy) : ctx.lineTo(sx, sy); first = false;
    }
    ctx.stroke();
  }
  // reading on the visible wave
  if (t >= C.squiggle + 0.6 && p < 0.05) {
    const [ax] = S(0, -A), w1 = lv * z;
    const k = expoOut(ev(t, C.squiggle + 0.6, 0.3));
    ink([[ax, 610], [ax, 596], [ax + w1 * k, 596], [ax + w1 * k, 610]], 3, INK, { raw: true, key: 120, single: true });
    text('可见光', ax + w1 / 2, 500, { size: 52, align: 'center' });
    if (k > 0.5) text('波长 < 0.001 mm', ax + w1 / 2, 572, { size: 44, weight: 700, align: 'center' });
  }
  // magnification counter while we pull out
  if (false) {
    const mag = Math.round(z / zEnd);
    const s = mag >= 1000 ? `×${Math.floor(mag / 1000)} ${String(mag % 1000).padStart(3, '0')}` : `×${mag}`;
    text('放大倍数', 540, 1060, { align: 'center', size: 44, weight: 400 });
    text(s, 540, 1140, { align: 'center', size: 72, face: UI });
  }
  // after the pull-out: the dot where visible light went, the 12 cm bracket, the phone
  if (false) {
    const [dx, dy] = S(0, -A);
    inkCircle(dx, dy, 26, 3, INK, { key: 121 });
    ink([[dx - 14, dy + 22], [dx - 50, dy + 150]], 2.5, INK, { raw: true, key: 122, single: true });
    text('可见光在这儿', dx - 110, dy + 196, { size: 42, weight: 700, align: 'left' });
  }
  if (t >= C.bracket12) {
    const k = expoOut(ev(t, C.bracket12, 0.4));
    const xa = 160, xb = 920, yb = 372, mid = 540;
    ink([[lerp(mid, xa, k), yb + 22], [lerp(mid, xa, k), yb], [lerp(mid, xb, k), yb], [lerp(mid, xb, k), yb + 22]], 4, INK, { raw: true, key: 123 });
    writeOn([...'12', ' ', ...'厘米'], 540, 330, [C.bracket12, C.bracket12 + 0.06, C.bracket12 + 0.1, C.bracket12 + 0.14, C.bracket12 + 0.2], t, { size: 120, align: 'center' });
  }
  if (t >= C.phoneIn) {
    const k = spring(t, C.phoneIn, 0.5);
    const py = lerp(1900, 1170, k), pw = 894, ph = 432;
    ctx.save(); ctx.translate(540, py);
    ctx.fillStyle = PAPER2; ctx.beginPath(); ctx.roundRect(-pw / 2, -ph / 2, pw, ph, 64); ctx.fill();
    ctx.restore();
    ink([[540 - pw / 2 + 64, py - ph / 2], [540 + pw / 2 - 64, py - ph / 2]], 5, INK, { key: 124 });
    ctx.strokeStyle = INK; ctx.lineWidth = 6; ctx.beginPath(); ctx.roundRect(540 - pw / 2, py - ph / 2, pw, ph, 64); ctx.stroke();
    ctx.lineWidth = 3; ctx.beginPath(); ctx.roundRect(540 - pw / 2 + 24, py - ph / 2 + 24, pw - 48, ph - 48, 44); ctx.stroke();
    ctx.fillStyle = INK; ctx.beginPath(); ctx.roundRect(540 + pw / 2 - 90, py - 52, 26, 104, 13); ctx.fill();
    // Wi-Fi symbol on the screen
    ctx.strokeStyle = ACC; ctx.lineCap = 'round';
    for (let i = 1; i <= 3; i++) { ctx.lineWidth = 16; ctx.beginPath(); ctx.arc(540, py + 70, 50 * i, -Math.PI * 0.75, -Math.PI * 0.25); ctx.stroke(); }
    ctx.fillStyle = ACC; ctx.beginPath(); ctx.arc(540, py + 70, 14, 0, TAU); ctx.fill();
    // the phone's length under the wave
    ink([[540 - pw / 2, py - ph / 2 - 30], [540 - pw / 2, py - ph / 2 - 44], [540 + pw / 2, py - ph / 2 - 44], [540 + pw / 2, py - ph / 2 - 30]], 2.5, INK, { raw: true, key: 125, single: true, alpha: k });
    if (t > C.phoneIn + 0.35) text('≈ 一部手机', 540, py - ph / 2 - 62, { align: 'center', size: 44, weight: 700 });
  }
  grainPass(0.35);
}
