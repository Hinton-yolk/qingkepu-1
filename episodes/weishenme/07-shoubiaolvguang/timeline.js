// timeline.js — the single source of truth for picture (index.html) and sound (music/score.mjs).
// EP.07 手表绿光 — 手表背面的绿光，在看什么？ script v2 (script.md 「逐句脚本 v2（定稿）」, 2026-11-14).
// One forearm (world units: mm; x along the arm towards the hand, y across it, z up), a watch on the wrist.
//   0      手表背面的绿光，在看什么？    (fingertips hold the watch back-up over the wrist; 2.0 it rolls over and lands)
//   2.75   它又没摸你的脉，怎么知道你的心跳？ (♥ 80 on the face, a beat every 0.75 s)
//   5.25   它在用光，看你的血          (the camera turns to the side and goes into the gap under the watch → the section, dark)
//   7.5–14.5 为什么是绿光？ → 血吃掉绿光 → 光眼睛接住 (green photons on banana paths; the ones that reach a vessel die there)
//   14.5–26 它怎么数心跳？ → 血多一点 → 弹回来的光呢？ → 暗一下就是一次心跳 → 按一分钟算 → 80
//   26–39.5 可你一跑起来呢？ (out, side view, the arm swings) → 光乱了 → 哪下是甩手？ → 加速度计 → 减掉甩手 → 120
//   39.5–44 那戒指那么小？ (the hand opens, a ring; its section: green light into the finger)
//   44–52.5 the watch off, back up (green), on again + 它不是在摸你的脉… (closing) → 小提示 (strap, towards the elbow)
// 120 BPM: 1 beat = 0.5 s = 15 frames at 30 fps, 1 bar = 2 s; 56.25 s. Hearts: 80 / min (0.75 s) at rest, 120 / min (0.5 s) running.
(function (root) {
  const BPM = 120, BEAT = 60 / BPM, BAR = 4 * BEAT, FPS = 30, DUR = 56.25;
  const W = 1080, H = 1920;

  const T = {
    // 0–5.25 · the phenomenon: the back of the watch, green; it rolls over and lands; the face: ♥ 80
    underline: 1.5, flip: 2.0, flipEnd: 2.5, land: 2.5, release: 2.5, releaseEnd: 3.3, h1Out: 2.59,
    q2: 2.75, scrOn: 2.75, beat0: 3.0,
    // 5.25–9.5 · one take in: the camera turns to the side, goes into the gap under the watch, the section (dark)
    a1: 5.25, pitch: 5.25, pitchEnd: 6.5, gap: 5.75, gapEnd: 6.75, flood: 6.25, floodEnd: 7.25, ledLab: 7.25,
    q3: 7.5, push1: 7.25, push1End: 9.5,
    // 9.5–14.5 · blood eats green light; what comes back is caught by the light eye
    a3: 9.5, photons: 9.5, eat: 9.75, pd: 12.0, pdOn: 12.25,
    // 14.5–26 · how does it count? the trace; the vessel swells; the answer; the ticks; 80
    q4: 14.5, curve: 14.5, curveEnd: 15.25, b1: 16.25, pulseOn: 16.25,
    q5: 18.5, ans5: 19.0, b2: 21.0, ticks: 21.0, rate: 23.25, gather: 23.25, gatherEnd: 23.75, num80: 23.75, term: 24.25,
    // 26–39.5 · running: out to the arm; it swings; the trace goes wild; the accelerometer; subtract; 120
    q6: 26.0, unflood: 26.0, unfloodEnd: 26.4, pullOut: 26.0, pullOutEnd: 27.5, run: 26.5,
    r1: 28.0, q7: 30.5, qmark: 30.75,
    acc: 32.75, mag: 32.75, magEnd: 33.15, chipOn: 33.0, swing: 33.25, swingEnd: 34.0,
    acc2: 34.75, align: 34.75, alignEnd: 36.5, sub: 37.0, subEnd: 37.75, num120: 37.75,
    // 39.5–44 · the ring
    q8: 39.5, stop: 39.5, stopEnd: 40.5, slide: 39.75, slideEnd: 41.0, open: 40.0, openEnd: 40.9, ringMark: 40.75, ringGlow: 41.25,
    ringA: 41.75, rmag: 41.75, rmagEnd: 42.15, curveSlide: 42.0, curveSlideEnd: 42.75,
    // 44–53.5 · back to the start; the closing line; the tip
    // v3 (2026-11-14, audience #3 adopted): the question 「现在知道，它在看什么了吗？」 is cut; the closing line comes straight after the ring
    q9: 44.0, back: 44.0, backEnd: 44.75, grab: 44.25, lift: 44.5, flip2: 44.75, flip2End: 45.25,
    stop2: 45.25, fin: 45.75, flip3: 45.75, flip3End: 46.25, ka: 46.25, finOut: 48.5,
    tip: 48.5, wide: 48.5, wideEnd: 49.5, tighten: 49.75, move: 50.25, moveEnd: 51.0, tipOut: 52.35,
    // 52.5–56.25 end card
    end: 52.5, endMorph: 53.1, title1: 53.25, ep: 54.0, sting: 54.5,
  };

  const COPY = {
    h1: ["手表背面的绿光，", "在[看]什么？"],
    q2: ["它又没摸你的脉，", "怎么知道你的[心跳]？"],
    a1: ["它在用光，", "[看]你的血"],
    q3: ["为什么是[绿光]？"],
    a3: ["血是红的，因为它", "把绿光[吃掉]了"],
    pd: ["没被吃掉的光，", "弹回来被[光眼睛]接住"],
    q4: ["它怎么[数]心跳？"],
    b1: ["心脏一跳，", "血就[多]一点"],
    q5: ["血一多，", "弹回来的[光]呢？"],
    b2: ["暗一下，", "就是[一次心跳]"],
    rate: ["按一分钟算有几下，", "就是你的[心率]"],
    q6: ["可你一跑起来呢？"],
    r1: ["手一甩，表在晃，", "血也晃，光就[乱]了"],
    q7: ["哪下是心跳，", "哪下是[甩手]？"],
    acc: ["表里还有个[加速度计]"],
    acc2: ["它告诉手表：", "这几下是[甩手]"],
    sub: ["减掉甩手，", "剩下的才是[心跳]"],
    q8: ["那戒指那么小，", "怎么测[心跳]？"],
    ringA: ["同一招：", "把灯搬到了[手指]上"],
    fin: ["它不是在[摸]你的脉，", "是在用光[看]你的血"],
    tipTag: "小提示：", tip: ["表带贴紧，", "戴在腕骨[靠手肘]那边"],
    // small text (terms and notes only as small text)
    led: "每秒闪几百次", caught: "接住的光", note: "示意", pdName: "光电二极管", term: "这种测法叫光电容积描记",
    rowLight: "光", rowSwing: "甩手", elbow: "手肘", bone: "腕骨", tattoo: "有些纹身会挡光，可能测不准",
    end: ["你每天都在用，", "但你不知道", "它[怎么工作]"], epNum: "EP.07", epName: "手表绿光",
  };
  const HR_REST = 80, HR_RUN = 120;                     // the only two numbers in the film (plus 每秒闪几百次)
  const P_REST = 60 / HR_REST, P_RUN = 60 / HR_RUN;     // 0.75 s, 0.5 s: three and two 16ths of the 120 BPM grid
  const S16 = BEAT / 4;

  // ---- the heart: beat times (the watch face, the vessel, the trace and the sound all use these)
  const BEATS = [];
  for (let t = T.beat0; t < T.flip2 - 0.01; t += P_REST) if (t < T.run || t >= T.stopEnd + 0.25) BEATS.push(+t.toFixed(4));
  for (let t = T.run + 0.5; t < T.stopEnd; t += P_RUN) BEATS.push(+t.toFixed(4));
  for (let t = T.ka + 0.25; t < T.end; t += P_REST) BEATS.push(+t.toFixed(4));
  BEATS.sort((a, b) => a - b);
  // the beats heard as a soft thump: where the picture shows the heart (the face, the vessel, the trace)
  const THUMPS = BEATS.filter((t) => (t >= T.beat0 && t < T.a1) || (t >= T.pulseOn && t < T.q6) || (t >= T.num120 && t < T.q8) || (t >= T.ka && t < T.tip));
  // ---- the swing of the running arm: one swing a second (two beats), from T.run to T.stopEnd
  const SWINGS = []; for (let t = T.run + 0.5; t < T.stop; t += 1.0) SWINGS.push(t);

  const HITS = {
    underline: [T.underline], flip: [T.flip], land: [T.land], scrOn: [T.scrOn],
    a1: [T.a1], pitch: [T.pitch], flood: [T.flood], ledLab: [T.ledLab],
    q3: [T.q3], a3: [T.a3], eat: [T.eat], pd: [T.pd], pdOn: [T.pdOn],
    q4: [T.q4], curve: [T.curve], b1: [T.b1], q5: [T.q5], ans5: [T.ans5], b2: [T.b2], rate: [T.rate], num80: [T.num80],
    q6: [T.q6], unflood: [T.unflood], run: [T.run], r1: [T.r1], q7: [T.q7], qmark: [T.qmark],
    acc: [T.acc], mag: [T.mag], chipOn: [T.chipOn], acc2: [T.acc2], sub: [T.sub], num120: [T.num120],
    q8: [T.q8], stop: [T.stop], ringGlow: [T.ringGlow], ringA: [T.ringA], rmag: [T.rmag],
    grab: [T.grab], flip2: [T.flip2], stop2: [T.stop2], fin: [T.fin], ka: [T.ka],
    tip: [T.tip], tighten: [T.tighten], move: [T.move],
    endType: [T.title1], ep: [T.ep], sting: [T.sting],
    thumps: THUMPS, swings: SWINGS,
  };

  const TL = { BPM, BEAT, BAR, FPS, DUR, W, H, T, COPY, HITS, S16, HR_REST, HR_RUN, P_REST, P_RUN, BEATS, THUMPS, SWINGS };
  if (typeof module !== "undefined" && module.exports) module.exports = TL;
  else root.TL = TL;
})(typeof window !== "undefined" ? window : globalThis);
