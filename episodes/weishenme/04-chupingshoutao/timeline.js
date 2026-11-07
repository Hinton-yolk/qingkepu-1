// timeline.js — the single source of truth for picture (index.html) and sound (music/score.mjs).
// EP.04 触摸屏 — 戴着手套，为什么点不动屏幕？ Written from the approved script (script.md, content gate 1, 2026-11-07).
// The 「为什么系列」 detective story in one continuous space: a phone ringing, a knitted glove that cannot answer it.
//   1 phenomenon          戴着手套，为什么点不动屏幕？            (the gloved finger swipes 接听 twice, presses hard: nothing)
//   2 wrong guess, struck  你是不是以为，是手套太厚，按不到？ ✕ 其实，屏幕根本不管你按没按 (a bare finger grazes: it follows)
//   3 dig in               那它到底在感觉什么？ → push to the touch point → one take through the cover glass (dark)
//                          → the camera tilts: two layers of thin lines, field arcs at every crossing → 玻璃下面，藏着一张通着电的网
//   4 one mechanism        手指一靠近，会怎样？ → the arcs bend into the finger, those cells dim → 它会引走一点点电
//                          → the scan line, row by row, finds the dim cell, the ring locks → 这种屏幕，就叫电容屏。
//   5 the missing step     那戴上手套呢？ → the arcs stop at the fabric, nothing dims, the scan finds nothing
//                          → 这么说，只要导电，什么都能点？ → a sausage wakes the screen (2010, Korea) → a touch glove's yarns
//   6 back to the start    再接一次电话 → the touch glove swipes, 咔 → 戴手套点不动，是因为电过不去 → tip: 手套模式
// 120 BPM: 1 beat = 0.5 s = 15 frames at 30 fps, 1 bar = 2 s; 51.75 s. The strike, the name and the 咔 are the three
// loudest hits; the name and the 咔 each come after a half-beat stop; the sting lands on a bar line.
(function (root) {
  const BPM = 120, BEAT = 60 / BPM, BAR = 4 * BEAT, FPS = 30, DUR = 51.75;
  const W = 1080, H = 1920;

  const T = {
    // 0–4.25 · 1 the phenomenon: the call rings; the gloved finger swipes 接听 twice and presses hard — nothing moves
    sw1: 0.0, sw1End: 0.75, ret1End: 1.5, sw2: 1.5, sw2End: 2.0, underline: 2.0, ret2End: 2.75,
    press1: 3.0, press1End: 3.75, h1Out: 4.09,
    // 4.25–8.75 · 2 the wrong guess (orange): pressed harder, the glass dents; struck; a bare finger grazes and it follows
    myth: 4.25, q2: 4.25, push1: 4.25, push1End: 4.85, press2: 4.75, hush: 6.0, strike: 6.5, a2: 6.75,
    bareIn: 6.75, graze: 7.25, grazeEnd: 7.75, rest: 8.25,
    // 8.75–14.75 · 3 dig in: push in on the touch point, the finger lifts, one take through the glass, tilt
    unOrange: 8.75, q3: 8.75, lift: 10.0, liftEnd: 10.5, dive: 10.75, flood: 11.25, floodEnd: 11.5, tilt: 11.5, tiltEnd: 12.75,
    arcsOn: 11.75, a3: 11.75,
    // 14.75–24.25 · 4 the one mechanism: a finger (section) comes close; the arcs bend into it; the scan finds the cell
    q4: 14.75, fIn: 14.75, fNear: 16.5, steal: 15.75, stealEnd: 17.25, a4: 16.75,
    a5: 19.25, scan1: 19.75, lock1: 20.5, stop1: 21.75, name: 22.0,
    // 24.25–29.25 · 5 the missing step: a glove on the same finger — the arcs stop at the fabric, the scan finds nothing
    q6: 24.25, fUp: 24.25, fUpEnd: 24.75, wrap: 24.75, wrapEnd: 25.5, fDown: 25.5, fDownEnd: 26.25, a6: 26.25,
    scan2: 27.0, miss: 27.75,
    // 29.25–38.75 · back out: a sausage wakes the screen; a touch glove: conductive yarn
    q7: 29.25, fOut: 29.0, climb: 29.25, climbEnd: 30.5, unflood: 29.6,
    sausIn: 30.25, saus: 30.75, sLock: 31.25, wake: 31.5, a7: 31.5, sLabel: 32.0, sausOut: 34.5,
    a8: 35.0, tgIn: 34.75, tg: 35.25, dive2: 35.5, dive2End: 36.25, yarn: 36.5, lock2: 37.0,
    // 38.75–48.75 · 6 back to the phenomenon: the same call; the touch glove swipes; 咔; a small tip
    q9: 38.75, climb2: 38.75, climb2End: 39.75, unflood2: 38.95, ring2: 39.0, hand2: 39.25, sw3: 40.0, stop2: 40.25, ka: 40.5,
    fin: 41.25, finOut: 44.25, tip: 44.25, toggle: 45.25, tipOut: 48.6,
    // 48.75–51.75 end card
    end: 48.75, endMorph: 49.35, title1: 49.0, ep: 49.5, sting: 50.0,
  };

  const COPY = {
    h1: ["戴着手套，", "为什么点不动[屏幕]？"],
    q2: ["你是不是以为，", "是手套太厚，[按]不到？"],
    a2: ["其实，屏幕根本", "不管你[按]没按"],
    q3: ["那它到底", "在感觉[什么]？"],
    a3: ["玻璃下面，藏着一张", "通着电的[网]"],
    q4: ["手指一靠近，", "会[怎样]？"],
    a4: ["它会[引走]", "一点点电"],
    a5: ["哪一格的电[少]了，", "就是你点的位置"],
    name: ["这种屏幕，", "就叫[电容]屏。"],
    q6: ["那戴上[手套]呢？"],
    a6: ["手套不导电，", "电就[引不走]"],
    q7: ["这么说，只要[导电]，", "什么都能点？"],
    a7: ["对，一根[香肠]", "也能点亮屏幕"],
    sLabel: "2010 年冬天，韩国真有人这么用",
    a8: ["触屏手套，就是在指尖", "织进了[导电线]"],
    q9: ["再接一次[电话]"],
    fin: ["戴手套点不动，", "是因为电[过不去]"],
    tipTag: "小提示：", tip: ["有的手机设置里，", "有个[手套模式]"],
    // phone UI (generic, no brand, no digits)
    caller: "妈妈", incoming: "来电", slide: "滑动接听", inCall: "通话中", settings: "设置", gloveMode: "手套模式", gloveSub: "戴手套时提高触控灵敏度",
    rowA: "显示", rowB: "声音", rowC: "触控", rowD: "电池",
    end: ["你每天都在用，", "但你不知道", "它[怎么工作]"], epNum: "EP.04", epName: "触摸屏",
  };

  const clamp01 = (x) => Math.max(0, Math.min(1, x));
  const sm = (x) => x * x * (3 - 2 * x);
  const ramp = (t, a, b) => sm(clamp01((t - a) / (b - a)));

  // ---- is the phone ringing (screen = incoming call, vibrating, ringtone)?
  const ringing = (t) => (t < T.dive + 0.6) || (t >= T.ring2 && t < T.ka);
  // the vibration motor: bursts of 0.75 s on, 0.25 s off (every 1 s, starting on the beat)
  function buzzK(t) {
    if (!ringing(t)) return 0;
    const t0 = t < T.ring2 ? 0 : T.ring2, u = (t - t0) % 1;
    return u < 0.75 ? Math.min(1, u / 0.03) * Math.min(1, (0.75 - u) / 0.04) : 0;
  }
  // ---- how much a finger near the glass steals from the cells (0..1) in the dark interior
  function stealK(t) {
    if (t < T.fUp) return ramp(t, T.steal, T.stealEnd);
    if (t < T.yarn - 0.3) return 1 - ramp(t, T.fUp, T.fUpEnd);       // (the glove: nothing is stolen)
    return ramp(t, T.yarn, T.yarn + 0.6);                              // the touch glove: through the yarn
  }
  const S16 = BEAT / 4;
  // the scan line: steps one row per 16th, back (row -6) to front (row +1); returns the row index (float) or null
  const ROWS = [-6, -5, -4, -3, -2, -1, 0, 1];
  function scanRow(t) {
    for (const s0 of [T.scan1, T.scan2, T.lock2 - 0.75]) {
      const k = (t - s0) / S16;
      if (k >= 0 && k < ROWS.length) return { row: ROWS[Math.floor(k)], u: k - Math.floor(k), s0 };
    }
    return null;
  }

  // sound cues derived from the same times (score.mjs reads this; beatcheck.mjs checks them on the measured grid)
  const HITS = {
    swipe: [T.sw1, T.sw2], underline: [T.underline], press: [T.press1, T.press2, T.press2 + 0.5, T.press2 + 1.0],
    myth: [T.myth], strike: [T.strike, T.strike + 0.125], graze: [T.graze], q3: [T.q3], lift: [T.lift], dive: [T.dive],
    arcs: [T.arcsOn], q4: [T.q4], steal: [T.steal], a4: [T.a4],
    scan: ROWS.map((_, i) => T.scan1 + i * S16), lock: [T.lock1], name: [T.name],
    q6: [T.q6], wrap: [T.wrap], scan2: ROWS.map((_, i) => T.scan2 + i * S16), miss: [T.miss],
    q7: [T.q7], saus: [T.saus], sLock: [T.sLock], wake: [T.wake],
    tg: [T.tg], dive2: [T.dive2], yarn: [T.yarn], lock2: [T.lock2],
    q9: [T.q9], ring2: [T.ring2], sw3: [T.sw3], ka: [T.ka], fin: [T.fin], tip: [T.tip], toggle: [T.toggle],
    endType: [T.title1], ep: [T.ep], sting: [T.sting],
  };

  const TL = { BPM, BEAT, BAR, FPS, DUR, W, H, T, COPY, HITS, S16, ROWS, ringing, buzzK, stealK, scanRow, ramp };
  if (typeof module !== "undefined" && module.exports) module.exports = TL;
  else root.TL = TL;
})(typeof window !== "undefined" ? window : globalThis);
