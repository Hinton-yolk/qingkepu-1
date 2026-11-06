// ================================================================== timeline, transitions, subtitles, seek(t)
const C = CUES.c;
const DUR = TL.duration;
const SCENE = {
  S01: t => S01(t), S02: t => S02(t), S03: t => S03(t), S04: t => S04_05(t), S05: t => S04_05(t),
  S06: t => S06v2(t), S09: t => S09(t), S10: t => S10(t), S11: t => S11(t), S12: t => S12(t),
  S13: t => S13(t), S14: t => S14city(t), S15: t => S15end(t),
};
const SHOTS = CUES.shots.map(([id, t0]) => [id, t0, SCENE[id]]);
// transitions straddle a boundary: [into shot, start, duration, type, params]
const TRANS = [
  ['S03', SHOTS.find(s => s[0] === 'S03')[1] - 0.45, 0.45, 'zoomIris', { cx: 540, cy: 700, k: 6 }],
  ['S04', SHOTS.find(s => s[0] === 'S04')[1] - 0.3, 0.6, 'front', {}],
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

// ---------------------------------------------------------------- subtitles (UI face), phone-safe, chunked at punctuation
const SUB_OFF = new Set([TL.lines[0].id, TL.lines[TL.lines.length - 1].id]);   // these lines are already set as display type in the picture
const CHUNKS = [];
(() => {
  for (const L of TL.lines) {
    if (SUB_OFF.has(L.id)) continue;
    // char -> time map
    const chars = [];
    for (const w of L.words) for (let i = 0; i < w.w.length; i++) chars.push({ ch: w.w[i], t: w.t0 + (w.t1 - w.t0) * i / w.w.length });
    let k = 0, cur = '', t0 = null;
    const flush = (tEnd) => { if (cur.trim()) CHUNKS.push({ text: cur.trim(), t0, t1: tEnd }); cur = ''; t0 = null; };
    for (const ch of L.text) {
      if ('，。：；？、！'.includes(ch)) {
        // close chunk at the time of the next spoken char
        const nt = k < chars.length ? chars[k].t : L.t1;
        flush(nt);
        continue;
      }
      if (ch === ' ') { cur += ' '; continue; }
      let tt = null;
      if (k < chars.length && chars[k].ch === ch) { tt = chars[k].t; k++; }
      else { const j = chars.findIndex((c, idx) => idx >= k && c.ch === ch); if (j >= 0) { tt = chars[j].t; k = j + 1; } }
      if (t0 === null) t0 = tt ?? (CHUNKS.length ? CHUNKS[CHUNKS.length - 1].t1 : L.t0);
      cur += ch;
    }
    flush(L.t1 + 0.35);
  }
  // join very short chunks with their neighbour, cap at 15 chars per chunk
  for (let i = 0; i < CHUNKS.length - 1; i++) {
    const a = CHUNKS[i], b = CHUNKS[i + 1];
    if (a.text.length + b.text.length <= 13 && b.t0 - a.t1 < 0.25 && a.text.length < 6) { a.text += ' ' + b.text; a.t1 = b.t1; CHUNKS.splice(i + 1, 1); i--; }
  }
  for (let i = 0; i < CHUNKS.length - 1; i++) CHUNKS[i].t1 = Math.min(CHUNKS[i].t1, CHUNKS[i + 1].t0);
})();
function subtitles(t) {
  const c = CHUNKS.find(c => t >= c.t0 - 0.05 && t < c.t1);
  if (!c) return;
  screenCam();
  font(UI, 58, 700);
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.lineJoin = 'round';
  ctx.lineWidth = 12; ctx.strokeStyle = '#141210'; ctx.strokeText(c.text, W / 2, 1450);
  ctx.fillStyle = '#F7F2E8'; ctx.fillText(c.text, W / 2, 1450);
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
window.ready = document.fonts.load(`700 120px ${DISPLAY}`).then(() => document.fonts.load(`700 40px ${UI}`)).then(() => document.fonts.load(`400 40px ${UI}`)).then(() => true);
