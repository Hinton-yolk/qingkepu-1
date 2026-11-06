// Shared staging for the style tests (loaded after full.js when ?style=… is set).
// Same camera, same timing; only the drawing changes. Each style file fills STY and overrides bedroom / phoneAt / hand.
// New staging used by every style: a big funnel standing in front of the wall, cards streaming down into it,
// and the batch coming out of its mouth one card after another.
'use strict';
const STY = {};
const FUN = { z: 56, yTop: 17, yMouth: -15, wTop: 24, wMouth: 2.6 };
const funHalf = y => lerp(FUN.wMouth, FUN.wTop, clamp((y - FUN.yMouth) / (FUN.yTop - FUN.yMouth)));
function funnelPts() { return [P(-FUN.wTop, FUN.yTop, FUN.z), P(FUN.wTop, FUN.yTop, FUN.z), P(FUN.wMouth, FUN.yMouth, FUN.z), P(-FUN.wMouth, FUN.yMouth, FUN.z)]; }

function drawWall(t) {
  STY.wallBg(t);
  const z = 60, scroll = (t - C.dc) * 4, cw = WALL.w + WALL.gap, ch = WALL.h + WALL.gap;
  const s = F / (z - CZ), halfW = W / 2 / s + cw, halfH = H / 2 / s + ch;
  for (let c = Math.floor((CX - halfW) / cw); c <= Math.ceil((CX + halfW) / cw); c++) for (let r = Math.floor((CY - halfH + scroll) / ch); r <= Math.ceil((CY + halfH + scroll) / ch); r++) {
    const x = c * cw, y = r * ch - scroll, idx = ((c * 7919 + r * 104729) >>> 0);
    const p = P(x, y, z); if (!p) continue; const w = WALL.w * p[2], h = WALL.h * p[2];
    STY.wallCard(p[0] - w / 2, p[1] - h / 2, w, h, idx, t);
  }
}
function drawFunnel(t, a) {
  const k = ev(t, C.pick - .3, .6) * a; if (k <= 0) return;
  const pts = funnelPts(); if (pts.some(v => !v)) return;
  STY.funnelBack(pts, k, t);
  if (STY.streamCard) for (let i = 0; i < 14; i++) {      // cards sliding down the funnel toward the mouth
    const u = ((t - C.pick) * .5 + hash(i, 41)) % 1; if (u < 0) continue;
    const y = lerp(FUN.yTop + 1, FUN.yMouth + 1.5, u), x = (hash(i, 42) * 2 - 1) * funHalf(y) * .8;
    const p = P(x, y, FUN.z + .5); if (!p) continue;
    const sc = lerp(1, .4, u), w = WALL.w * sc * p[2], h = WALL.h * sc * p[2];
    STY.streamCard(p[0], p[1], w, h, i * 13 + 5, t, u, k);
  }
  STY.funnelFront(pts, k, t);
}
function wallScene(t) { drawWall(t); drawFunnel(t, 1); }
function batchScene(t) {
  drawWall(t);
  STY.dim(t, clamp(ev(t, C.pick + .2, 1) * .7 + ev(t, C.q, 1) * .3));
  drawFunnel(t, 1 - .5 * ev(t, C.q, 1));
  BATCH.forEach(([bx, by, k, odds, zz], i) => {
    const u = ease(ev(t, C.pick + .2 + i * .12, 1.3)); if (u <= 0) return;
    const x = lerp(0, bx, u), y = lerp(FUN.yMouth + 1, by, u) + Math.sin(u * Math.PI) * 2.5, z = lerp(FUN.z - 1, zz, u);
    card(x + CX * u, y + CY * u, z, 4.2, 7.3, (w, h) => {
      ctx.save(); ctx.scale(1 / 100, 1 / 100); STY.batchCard(w * 100, h * 100, k, odds, t, zz > 30, i, u); ctx.restore();
    });
  });
}
// odds row helper shared by every style: which rows are visible and how far each bar has grown
function oddsRows(t, odds) { return QL.map(([lab, cue], j) => ({ lab, on: t >= C[cue], k: expoOut(ev(t, C[cue], .6)), v: odds[j] / 100, txt: roll(String(odds[j]), t, C[cue], .5) + '%' })); }

// the frame: same overlays as full.js, drawn by the style
const CLEAN_ = location.search.includes('clean');
window.seek = function (t) {
  t = clamp(t, 0, DUR - 1 / FPS);
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over'; ctx.shadowColor = 'transparent'; ctx.setLineDash([]);
  const s = shot(t);
  if (STY.post) STY.post(t);
  if (t < C.dive) STY.title(t);
  if (s === 'S1') {
    if (t >= C.queue && t < C.who) STY.hero(t, C.queue, [{ parts: [['已下载 ', 'b'], [roll('3', t, C.queue, .3), 'a'], [' 条', 'a']], size: 120 }], 72, 330);
    if (t >= C.who && t < C.you) STY.hero(t, C.who, [{ parts: [['谁挑的？', 'b']], size: 120 }], 72, 330);
    if (t >= C.you && t < C.fly + .3) STY.hero(t, C.you, [{ parts: [['是', 'b'], ['你', 'a'], ['。', 'b']], size: 140 }], 72, 340);
  }
  if (s === 'S3') STY.hero(t, C.fly, [{ parts: [['飞回', 'b'], ['机房', 'a']], size: 120 }], 72, 330);
  if (s === 'S5' || s === 'S4') {
    if (t >= C.sea && t < C.pick) STY.hero(t, C.sea, [{ parts: [['海量', 'b']], size: 130 }], 72, 330);
    if (t >= C.pick && t < C.q) STY.hero(t, C.pick, [{ parts: [['捞出', 'b'], ['一小批', 'a']], size: 120 }], 72, 330);
    if (t >= C.q) STY.hero(t, C.q, [{ parts: [['算一道题', 'b']], size: 110 }], 72, 330);
  }
  if (!CLEAN_) { const c = CUES.subs.find(c => t >= c.t0 && t < c.t1); if (c && t < C.next - .2) STY.sub(c.text, t); }
  return true;
};
// how many characters of a hero line are typed by now, and the drop
function heroK(t, t0, i) { return { k: expoOut(ev(t, t0 + i * .15, .32)), show: c => Math.ceil(c * clamp((t - t0 - i * .15) / .3)) }; }
