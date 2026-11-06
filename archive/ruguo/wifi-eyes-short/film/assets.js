// ------------------------------------------------------------------ drawn props (ink style, two modes)
// mode 'paper' = what you normally see; mode 'radio' = Wi-Fi vision (dark, only Wi-Fi is light)
function withScale(s, fn) { ctx.save(); ctx.scale(s, s); const z0 = Z; Z = Z * s; fn(); Z = z0; ctx.restore(); }
function bez(p0, p1, p2, p3, u) {
  const v = 1 - u;
  return [v * v * v * p0[0] + 3 * v * v * u * p1[0] + 3 * v * u * u * p2[0] + u * u * u * p3[0],
          v * v * v * p0[1] + 3 * v * v * u * p1[1] + 3 * v * u * u * p2[1] + u * u * u * p3[1]];
}
const lineCol = m => m === 'radio' ? DLINE : INK;

// ---------------------------------------------------------------- the eye
const EYE = { EW: 470, UH: 340, LH: 250, R: 225, r: 98 };
function eyeLids(open) {
  const { EW, UH, LH } = EYE;
  const up = [[-EW, 0], [-EW * 0.45, lerp(55, -UH, open)], [EW * 0.5, lerp(55, -UH, open)], [EW, -8]];
  const lo = [[-EW, 0], [-EW * 0.4, lerp(55, LH, open)], [EW * 0.45, lerp(55, LH, open)], [EW, -8]];
  return { up, lo };
}
function eyeClip(open) {
  const { up, lo } = eyeLids(open);
  ctx.beginPath(); ctx.moveTo(...up[0]); ctx.bezierCurveTo(...up[1], ...up[2], ...up[3]);
  ctx.bezierCurveTo(...lo[2], ...lo[1], ...lo[0]); ctx.closePath();
}
// pupilFn(r) draws inside the pupil (already clipped, origin at pupil centre)
function drawEye(cx, cy, s, open, t, pupilFn, o = {}) {
  ctx.save(); ctx.translate(cx, cy);
  withScale(s, () => {
    const { EW, R, r } = EYE;
    const { up, lo } = eyeLids(open);
    const pr = r * (o.dilate ?? 1);
    if (open > 0.02) {
      ctx.save(); eyeClip(open); ctx.clip();
      ctx.fillStyle = PAPER2; ctx.fillRect(-EW, -400, EW * 2, 800);
      // iris
      ctx.fillStyle = '#D8CEBD'; ctx.beginPath(); ctx.arc(0, 0, R, 0, TAU); ctx.fill();
      for (let i = 0; i < 120; i++) {
        const a = i / 120 * TAU + hash(i, 1) * 0.04;
        const r0 = pr + 4 + hash(i, 2) * 14, r1 = R - 8 - hash(i, 4) * 40;
        ink([[Math.cos(a) * r0, Math.sin(a) * r0], [Math.cos(a + 0.03) * r1, Math.sin(a + 0.03) * r1]], 2.2, INK, { raw: true, key: 400 + i, single: true, alpha: 0.6 });
      }
      inkCircle(0, 0, pr + 42, 2, INK, { alpha: 0.5, key: 31 });
      inkCircle(0, 0, R - 4, 10, INK, { key: 32 });
      // pupil
      ctx.fillStyle = INK; ctx.beginPath(); ctx.arc(0, 0, pr, 0, TAU); ctx.fill();
      if (pupilFn) { ctx.save(); ctx.beginPath(); ctx.arc(0, 0, pr, 0, TAU); ctx.clip(); pupilFn(pr); ctx.restore(); }
      if (!o.noGlint) {
        ctx.fillStyle = PAPER2;
        ctx.beginPath(); ctx.ellipse(-pr * 0.5, -pr * 0.55, pr * 0.26, pr * 0.22, -0.5, 0, TAU); ctx.fill();
        ctx.beginPath(); ctx.arc(pr * 0.42, pr * 0.4, pr * 0.09, 0, TAU); ctx.fill();
      }
      // shadow of the upper lid
      ctx.save();
      ctx.beginPath(); ctx.moveTo(...up[0]); ctx.bezierCurveTo(...up[1], ...up[2], ...up[3]);
      ctx.lineTo(up[3][0], up[3][1] + 60);
      ctx.bezierCurveTo(up[2][0], up[2][1] + 70, up[1][0], up[1][1] + 70, up[0][0], up[0][1] + 60);
      ctx.closePath(); ctx.clip();
      hatch(-EW, -420, EW * 2, 540, -0.6, 11, 2, INK, 0.55, 33);
      ctx.restore();
      ctx.restore();
    }
    // lids
    const upP = [], loP = [];
    for (let i = 0; i <= 40; i++) { upP.push(bez(...up, i / 40)); loP.push(bez(...lo, i / 40)); }
    ink(upP, 9, INK, { raw: true, key: 34 });
    ink(loP, open > 0.05 ? 4 : 0.01, INK, { raw: true, key: 35 });
    if (open > 0.25) {
      const cr = [];
      for (let i = 0; i <= 30; i++) { const [x, y] = bez(...up, 0.08 + i / 30 * 0.8); cr.push([x * 1.02, y - 62 * open - 10]); }
      ink(cr, 3, INK, { raw: true, key: 36, alpha: 0.8 });
    }
    // lashes
    for (let i = 0; i < 24; i++) {
      const u = 0.1 + i / 23 * 0.84;
      const [x, y] = bez(...up, u);
      const [x2, y2] = bez(...up, Math.min(1, u + 0.01));
      let nx = (y2 - y), ny = -(x2 - x); const nl = Math.hypot(nx, ny); nx /= nl; ny /= nl;
      if (ny > 0) { nx = -nx; ny = -ny; }
      const L = (48 + 28 * Math.sin(u * Math.PI)) * (0.55 + 0.45 * open);
      const sweep = (u - 0.35) * 0.9;
      const tip = [x + (nx + sweep) * L, y + ny * L];
      const mid = [x + (nx + sweep * 0.3) * L * 0.55, y + ny * L * 0.6];
      ink([[x, y], mid, tip], 3.6, INK, { raw: true, key: 500 + i, single: true });
    }
    if (open > 0.3) for (let i = 0; i < 10; i++) {
      const u = 0.2 + i / 9 * 0.62;
      const [x, y] = bez(...lo, u);
      ink([[x, y], [x + (u - 0.45) * 30, y + 26]], 2.4, INK, { raw: true, key: 600 + i, single: true, alpha: 0.8 });
    }
  });
  ctx.restore();
}
// orange reflection inside the pupil: a tiny router throwing rings
function pupilRings(t, pr, k = 1) {
  ctx.globalCompositeOperation = 'lighter';
  const ox = pr * 0.18, oy = pr * 0.12;
  for (let i = 0; i < 6; i++) {
    const r = ((t * 0.9 + i / 6) % 1) * pr * 1.3;
    ctx.strokeStyle = ACC; ctx.globalAlpha = (1 - r / (pr * 1.3)) * 0.9 * k;
    ctx.lineWidth = pr * 0.06;
    ctx.beginPath(); ctx.arc(ox, oy, r, 0, TAU); ctx.stroke();
  }
  const g = ctx.createRadialGradient(ox, oy, 0, ox, oy, pr * 0.35);
  g.addColorStop(0, `rgba(255,217,184,${0.95 * k})`); g.addColorStop(1, 'rgba(255,106,26,0)');
  ctx.globalAlpha = 1; ctx.fillStyle = g; ctx.beginPath(); ctx.arc(ox, oy, pr * 0.35, 0, TAU); ctx.fill();
  ctx.globalCompositeOperation = 'source-over';
}

// ---------------------------------------------------------------- router (base centre at x,y)
function drawRouter(x, y, s, mode, hot = 1) {
  const c = lineCol(mode);
  ctx.save(); ctx.translate(x, y);
  withScale(s, () => {
    // antennas
    for (const sx of [-1, 1]) {
      const p = [[sx * 52, -36], [sx * 62, -128]];
      if (mode === 'radio') {
        ctx.globalCompositeOperation = 'lighter';
        ink(p, 12, ACC, { raw: true, key: 40 + sx, single: true, alpha: 0.35 * hot });
        ink(p, 5, HOT, { raw: true, key: 42 + sx, single: true, alpha: hot });
        ctx.globalCompositeOperation = 'source-over';
      } else ink(p, 7, c, { raw: true, key: 44 + sx });
    }
    ctx.fillStyle = mode === 'radio' ? '#17140F' : PAPER2;
    ctx.beginPath(); ctx.roundRect(-82, -40, 164, 40, 12); ctx.fill();
    if (mode !== 'radio') { ctx.save(); ctx.beginPath(); ctx.roundRect(-82, -40, 164, 40, 12); ctx.clip(); hatch(-82, -40, 164, 40, 0.9, 9, 1.6, INK, 0.5, 45); ctx.restore(); }
    ink([[-82, -28], [-82, -6], [-70, 0], [70, 0], [82, -6], [82, -28], [70, -40], [-70, -40], [-82, -28]], 4, c, { key: 46 });
    for (let i = 0; i < 4; i++) {
      ctx.fillStyle = mode === 'radio' ? HOT : INK;
      ctx.globalAlpha = mode === 'radio' ? hot : 1;
      ctx.beginPath(); ctx.arc(-36 + i * 24, -18, 4.5, 0, TAU); ctx.fill();
    }
    ctx.globalAlpha = 1;
  });
  ctx.restore();
}

// ---------------------------------------------------------------- people (feet at x,y; h = height)
function personShape(h, pose, ph, dir) {
  // returns stroke list [[pts], width] and head
  const S = [];
  const P = (x, y) => [x * dir, y];
  let head, hip, sh;
  if (pose === 'sit') {
    hip = [0, -0.28 * h]; sh = [0.01 * h, -0.6 * h]; head = P(0.04 * h, -0.69 * h);
    S.push([[P(...hip), P(...sh)], 0.2 * h]);
    S.push([[P(...hip), P(0.24 * h, -0.29 * h), P(0.25 * h, -0.02 * h)], 0.1 * h]);
    S.push([[P(0.03 * h, -0.57 * h), P(0.1 * h, -0.42 * h), P(0.2 * h, -0.5 * h)], 0.07 * h]);
  } else {
    const sw = pose === 'walk' ? Math.sin(ph) : 0;
    hip = [0, -0.5 * h]; sh = [0, -0.8 * h]; head = P(0.01 * h, -0.915 * h);
    S.push([[P(...hip), P(...sh)], 0.21 * h]);
    for (const k of [1, -1]) {
      const a = 0.42 * sw * k;
      const knee = [hip[0] + Math.sin(a) * 0.25 * h, hip[1] + Math.cos(a) * 0.25 * h];
      const bend = pose === 'walk' ? Math.max(0, -Math.sin(ph) * k) * 0.35 : 0;
      const foot = [knee[0] + Math.sin(a - bend) * 0.25 * h, Math.min(0, knee[1] + Math.cos(a - bend) * 0.25 * h)];
      S.push([[P(...hip), P(...knee), P(...foot)], 0.1 * h]);
    }
    if (pose === 'phone') {
      S.push([[P(0.06 * h, -0.78 * h), P(0.1 * h, -0.62 * h), P(0.18 * h, -0.7 * h)], 0.07 * h]);
      S.push([[P(-0.06 * h, -0.78 * h), P(0.02 * h, -0.62 * h), P(0.15 * h, -0.69 * h)], 0.07 * h]);
    } else for (const k of [1, -1]) {
      const a = -0.45 * sw * k;
      const el = [Math.sin(a) * 0.17 * h, -0.78 * h + Math.cos(a) * 0.17 * h];
      const hd = [el[0] + Math.sin(a * 1.3) * 0.16 * h, el[1] + Math.cos(a * 1.3) * 0.16 * h];
      S.push([[P(0, -0.78 * h), P(...el), P(...hd)], 0.075 * h]);
    }
  }
  return { S, head, hr: 0.068 * h };
}
function drawPerson(x, y, h, pose, mode, o = {}) {
  const dir = o.dir ?? 1, ph = o.ph ?? 0;
  const { S, head, hr } = personShape(h, pose, ph, dir);
  ctx.save(); ctx.translate(x, y);
  const paint = (col, dx, alpha) => {
    ctx.strokeStyle = col; ctx.fillStyle = col; ctx.globalAlpha = alpha; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    for (const [pts, w] of S) {
      ctx.lineWidth = w; ctx.beginPath();
      pts.forEach(([px, py], i) => i ? ctx.lineTo(px + dx, py) : ctx.moveTo(px + dx, py));
      ctx.stroke();
    }
    ctx.beginPath(); ctx.arc(head[0] + dx, head[1], hr, 0, TAU); ctx.fill();
  };
  if (mode === 'radio') {
    ctx.globalCompositeOperation = 'lighter';
    paint(ACC, (o.rim ?? -1) * h * 0.012, 0.75);
    ctx.globalCompositeOperation = 'source-over';
    paint('#030303', 0, 1);
  } else paint(o.col ?? FIG, 0, 1);
  if (o.phone) {   // phone in hand
    const hx = (pose === 'sit' ? 0.2 : 0.17) * h * dir, hy = (pose === 'sit' ? -0.52 : -0.72) * h;
    ctx.globalAlpha = 1;
    ctx.fillStyle = mode === 'radio' ? HOT : PAPER2;
    ctx.save(); ctx.translate(hx, hy); ctx.rotate(-0.5 * dir);
    ctx.fillRect(-0.018 * h, -0.04 * h, 0.036 * h, 0.07 * h);
    ctx.restore();
  }
  ctx.globalAlpha = 1;
  ctx.restore();
}
// distance from point to segment (used for body shadows in the field)
function segDist2(px, py, ax, ay, bx, by) {
  const dx = bx - ax, dy = by - ay, l = dx * dx + dy * dy;
  let u = l ? ((px - ax) * dx + (py - ay) * dy) / l : 0; u = u < 0 ? 0 : u > 1 ? 1 : u;
  const ex = ax + u * dx - px, ey = ay + u * dy - py;
  return ex * ex + ey * ey;
}
// does segment S(s->p) pass through a vertical capsule (cx, top..bot, radius rr)?
function blocked(sx, sy, px, py, cx, top, bot, rr) {
  // sample the capsule axis against the ray: closest approach between two segments (approx, 5 samples)
  let best = 1e18;
  for (let k = 0; k <= 4; k++) {
    const cy = top + (bot - top) * k / 4;
    const d = segDist2(cx, cy, sx, sy, px, py);
    if (d < best) best = d;
  }
  return best < rr * rr;
}

// ---------------------------------------------------------------- furniture (outline icons, floor at y)
function sofa(x, y, w, mode, key = 1) {
  const c = lineCol(mode), h = w * 0.42;
  ink([[x, y], [x, y - h], [x + w * 0.1, y - h], [x + w * 0.1, y - h * 0.5], [x + w * 0.9, y - h * 0.5], [x + w * 0.9, y - h], [x + w, y - h], [x + w, y]], 3.5, c, { key });
  ink([[x + w * 0.1, y - h * 0.5], [x + w * 0.1, y - h * 0.95], [x + w * 0.9, y - h * 0.95], [x + w * 0.9, y - h * 0.5]], 3, c, { key: key + 1 });
  ink([[x + w * 0.1, y - h * 0.22], [x + w * 0.9, y - h * 0.22]], 2.5, c, { key: key + 2, alpha: 0.7 });
}
function table(x, y, w, h, mode, key = 5) {
  const c = lineCol(mode);
  ink([[x, y - h], [x + w, y - h]], 4, c, { key });
  ink([[x + w * 0.12, y - h], [x + w * 0.12, y]], 3, c, { key: key + 1 });
  ink([[x + w * 0.88, y - h], [x + w * 0.88, y]], 3, c, { key: key + 2 });
}
function bed(x, y, w, mode, key = 9) {
  const c = lineCol(mode), h = w * 0.3;
  ink([[x, y], [x, y - h * 1.6], [x + w * 0.06, y - h * 1.6], [x + w * 0.06, y - h * 0.6], [x + w, y - h * 0.6], [x + w, y]], 3.2, c, { key });
  ink([[x + w * 0.08, y - h * 0.6], [x + w * 0.08, y - h], [x + w * 0.3, y - h], [x + w * 0.3, y - h * 0.6]], 2.6, c, { key: key + 1 });
  ink([[x + w * 0.3, y - h * 0.75], [x + w * 0.98, y - h * 0.8]], 2.4, c, { key: key + 2, alpha: 0.7 });
}
function plant(x, y, s, mode, key = 13) {
  const c = lineCol(mode);
  ink([[x - 22 * s, y - 50 * s], [x - 16 * s, y], [x + 16 * s, y], [x + 22 * s, y - 50 * s], [x - 22 * s, y - 50 * s]], 3, c, { key, closed: true });
  for (let i = 0; i < 7; i++) {
    const a = -Math.PI / 2 + (i - 3) * 0.32;
    const L = (70 + 40 * hash(i, key)) * s;
    ink([[x, y - 50 * s], [x + Math.cos(a) * L * 0.5, y - 50 * s + Math.sin(a) * L * 0.6], [x + Math.cos(a) * L, y - 50 * s + Math.sin(a) * L]], 2.6, c, { raw: true, key: key + i + 1, single: true });
  }
}
function lampStand(x, y, h, mode, key = 21) {
  const c = lineCol(mode);
  ink([[x - 30, y], [x + 30, y]], 4, c, { key });
  ink([[x, y], [x, y - h]], 3.5, c, { key: key + 1 });
  ink([[x - 40, y - h + 4], [x - 24, y - h - 60], [x + 24, y - h - 60], [x + 40, y - h + 4], [x - 40, y - h + 4]], 3.5, c, { key: key + 2, closed: true });
}
function fridge(x, y, w, h, mode, key = 25) {
  const c = lineCol(mode);
  inkRect(x, y - h, w, h, 3.5, c, { key });
  ink([[x, y - h * 0.62], [x + w, y - h * 0.62]], 3, c, { key: key + 1 });
  ink([[x + w * 0.12, y - h * 0.8], [x + w * 0.12, y - h * 0.7]], 4, c, { key: key + 2 });
}
function desk(x, y, w, mode, key = 27) {
  table(x, y, w, w * 0.45, mode, key);
  const c = lineCol(mode);
  inkRect(x + w * 0.3, y - w * 0.45 - w * 0.32, w * 0.36, w * 0.26, 3, c, { key: key + 3 });
  ink([[x + w * 0.48, y - w * 0.45 - w * 0.06], [x + w * 0.48, y - w * 0.45]], 3, c, { key: key + 4 });
}
