// ================================================================== v3 timeline, transitions, subtitles, seek(t)
const C = CUES.c;
const DUR = TL.duration;
const SCENE = {
  H1: t => H1(t), S03: t => S03v3(t), P1: t => P1(t), D1: t => D1(t), M1: t => M1(t), S06: t => S06v3(t),
  B1: t => B1(t), S11: t => S11(t), S12: t => S12(t), S13: t => S13v3(t), R1: t => R1(t), E1: t => E1(t),
};
const SHOTS = CUES.shots.map(([id, t0]) => [id, t0, SCENE[id]]);
const at = id => SHOTS.find(s => s[0] === id)[1];
// transitions straddle a boundary: [into shot, start, duration, type, params]
const TRANS = [
  ['S03', at('S03') - 0.45, 0.45, 'zoomIris', { cx: 540 + (RM_PERSON.x + 40 - (RM_PERSON.x + 60)) * 1.55, cy: 960, k: 6 }],
  ['S06', at('S06') - 0.3, 0.6, 'front', {}],
  ['S11', at('S11') - 0.45, 0.45, 'zoomIris', { cx: 540, cy: 960, k: 6 }],
];
function shotIndex(t) { let i = 0; while (i + 1 < SHOTS.length && t >= SHOTS[i + 1][1] - 1e-9) i++; return i; }
function drawTransition(tr, t) {
  const i = SHOTS.findIndex(s => s[0] === tr[0]);
  const prev = SHOTS[i - 1][2], next = SHOTS[i][2];
  const p = clamp((t - tr[1]) / tr[2]), o = tr[4];
  if (tr[3] === 'zoomIris') {
    renderTo(OFF, () => prev(t));
    screenCam();
    const k = lerp(1, o.k, expoIn(p));
    ctx.drawImage(OFF, o.cx - o.cx * k, o.cy - o.cy * k, W * k, H * k);
    const r = lerp(0, 1.25 * H, expoIn(p));
    ctx.save(); ctx.beginPath(); ctx.arc(o.cx, o.cy, r, 0, TAU); ctx.clip();
    next(t);
    ctx.restore();
  } else if (tr[3] === 'front') {
    prev(t);
    const fx = lerp(-60, W + 60, ease(p));
    ctx.save(); screenCam(); ctx.beginPath(); ctx.rect(0, 0, fx, H); ctx.clip();
    next(t);
    ctx.restore();
    seam(fx);
  }
}

// ---------------------------------------------------------------- subtitles (UI face), from the layout's cue list
function subtitles(t) {
  const c = CUES.subs.find(c => t >= c.t0 && t < c.t1);
  if (!c) return;
  screenCam();
  font(UI, 58, 700);
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.lineJoin = 'round';
  ctx.lineWidth = 12; ctx.strokeStyle = '#141210'; ctx.strokeText(c.text, W / 2, 1520);
  ctx.fillStyle = '#F7F2E8'; ctx.fillText(c.text, W / 2, 1520);
}

// ---------------------------------------------------------------- seek
window.seek = function (t) {
  t = clamp(t, 0, DUR - 1 / FPS);
  BT = boil(t);
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over'; ctx.filter = 'none';
  const tr = TRANS.find(tr => t >= tr[1] && t < tr[1] + tr[2]);
  if (tr) drawTransition(tr, t);
  else SHOTS[shotIndex(t)][2](t);
  subtitles(t);
  return true;
};
window.DURATION = DUR;
window.FPS = FPS;
window.ready = document.fonts.ready.then(() => Promise.all(['700 58px "Noto Sans Mono CJK SC"', '700 120px "Noto Serif CJK SC"'].map(f => document.fonts.load(f))));
