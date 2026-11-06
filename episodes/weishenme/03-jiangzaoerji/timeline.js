// timeline.js — the single source of truth for picture (index.html) and sound (music/score.mjs).
// EP.02 降噪耳机 v3 — written from the approved plain-language version (白话.md). The 「为什么系列」 detective story in one
// continuous space: a cross-section of a head with an earbud in it, the subway to the left.
//   1 phenomenon          按一下，噪音怎么就没了？                          (the rumble really disappears from the soundtrack)
//   2 wrong guess, struck  你是不是以为，它只是堵得更严？ ✕ 其实它在往耳朵里加声音。
//   3 dig in               加声音，怎么会更安静？ → a microphone behind the hole → 然后呢？ → mic → chip → speaker → into the canal
//   4 one mechanism        noise pushes the air → add the reversed wave (噪音往里进，它就往外推…) → cancelled → a little late
//                          → not cancelled → 这一招，就叫主动降噪。
//   5 the missing step     要是耳塞没戴紧呢？ → noise leaks in → 这头还有一个麦克风，专门听还剩多少「还剩一点！」→ into the chip
//                          → 没消干净，芯片就再补一点 → chip → speaker → flat again (one wider canal view: chip, speaker, mic, canal)
//   7 back to the start    再按一次，发生了什么？ → tap: the outer mic, then the inner mic, report to the chip; the meter under the
//                          cut-away drops 100 % → 0 %, the rumble really goes quiet → 所以你一按，噪音就被它抵消了。
//                          + a small tip under the last line: 戴久了耳朵发胀？其实气压没变……调低降噪，或摘下来歇会儿。
// 120 BPM: 1 beat = 0.5 s = 15 frames at 30 fps, 1 bar = 2 s; 59.75 s. Strike, name and the quiet land on bar lines.
(function (root) {
  const BPM = 120, BEAT = 60 / BPM, BAR = 4 * BEAT, FPS = 30, DUR = 59.75;
  const W = 1080, H = 1920;

  const T = {
    // 0–5 · 1 the phenomenon: two seconds of rumble first, then the tap
    hand: 1.25, tap1: 2.0, underline: 3.0, h1Out: 4.84,
    // 5–10.5 · 2 the wrong guess: the canal stuffed with a plug, struck
    myth: 5.0, push1End: 5.7, scan1: 5.0, scan1End: 5.6, q2: 5.25, hush: 7.5, strike: 8.0, a2: 8.25,
    // 10.5–22 · 3 dig in: the inside of the earbud → the outer microphone → follow the signal → into the ear canal
    unOrange: 10.5, scan2: 10.5, scan2End: 11.1, q3: 10.5, ring: 11.5, dive1: 12.0, dive1End: 14.0,
    seed: 14.0, a3: 14.0, q4: 16.5, follow: 16.75, followEnd: 17.5, pulse: 17.5, pulseEnd: 18.5, chipLbl: 17.85, spkLbl: 18.35,
    dive2: 19.75, dive2End: 22.0, flood: 20.25, floodEnd: 20.5, vibe: 21.25,
    // 22–38.5 · 4 the one mechanism, slowly: inside the ear canal
    h3: 22.0,                                                         // 噪音让空气一推一拉
    close: 25.0, closeEnd: 25.6, q5: 25.0, antiOn: 26.0, antiEnd: 27.0, push: 27.25, a5: 29.75,   // 反过来的波 → 进/推、退/拉 → 抵消
    q6: 31.75, lagOn: 33.0, lagMax: 33.5, a6: 33.75, lagOff: 35.0, lagZero: 35.5,                 // 慢了一点 → 抵消不掉
    name: 36.0, hush2: 37.5,                                          // 这一招，就叫主动降噪。
    // 38–45 · 5 the missing step, shown as a loop: a loose ear tip leaks → the inner microphone hears what is left
    //          → its "还剩一点！" flies into the chip → the chip drives the speaker → the canal goes flat again
    q7: 38.0, panR: 38.25, panREnd: 39.0, leak: 39.0, leakEnd: 39.75, a7: 40.0, sayR: 40.75,
    a8: 42.25, bubR: 42.5, sig: 42.5, sigEnd: 42.875, fix: 42.875, fixEnd: 43.625, panC: 45.0, panCEnd: 45.5,
    // 45–56.35 · 6 back to the phenomenon: climb out, noise on again, tap; the outer mic, then the inner mic, tell the chip;
    //          the meter under the cut-away drops 100 % → 0 % and the rumble really goes quiet; a small tip
    climb: 45.0, climbEnd: 46.25, unflood: 45.6, cover: 45.85, q9: 46.0,
    hand2: 46.5, tap2: 47.25, say2L: 47.375, bubL: 48.5, say2R: 48.75, bubOut: 49.75, quiet: 50.0,
    fin: 50.25, finOut: 52.75, tip: 52.75, tipOut: 56.35,
    // 56.5–59.75 end card
    end: 56.5, endMorph: 57.1, title1: 57.0, ep: 57.5, sting: 58.0,
  };

  const COPY = {
    h1: ["按一下，", "噪音怎么就[没了]？"],
    q2: ["你是不是以为，", "它只是[堵]得更严？"],
    a2: ["其实它在", "往耳朵里[加]声音。"],
    q3: ["加声音，", "怎么会[更安静]？"],
    a3: ["小孔后面，", "藏着一个[麦克风]"],
    q4: ["然后[呢]？"],
    chip: "芯片", spk: "扬声器",
    h3: ["噪音让空气", "[一推一拉]"], slow: "慢放",
    lbDrum: "鼓膜",
    q5: ["[如果]再加一个", "[反]过来的波呢？"],
    push: ["噪音往里进，它就往外[推]；", "噪音往外退，它就往里[拉]"],
    a5: ["正好[抵消]！"],
    q6: ["要是反得", "[慢]了一点呢？"],
    a6: ["慢一点，", "就抵消[不干净]"],
    meter: "听到的噪音",
    name: ["这一招，", "就叫[主动降噪]。"],
    q7: ["要是耳塞", "[没戴紧]呢？"],
    a7: ["这头还有一个麦克风，", "专门听[还剩多少]"], sayR: "还剩一点！",
    a8: ["没消干净，", "芯片就再[补]一点"],
    nameL: "外侧麦克风", nameR: "内侧麦克风", sayL: "轰隆声来了",
    q9: ["再按一次，", "发生了[什么]？"],
    fin: ["所以你一按，", "噪音就被它[抵消]了。"],
    tipTag: "小提示", tip: ["戴久了[耳朵发胀]？", "其实气压没变，是大脑的误会。", "调低降噪，或摘下来[歇会儿]。"],
    end: ["你每天都在用，", "但你不知道", "它[怎么工作]"], epNum: "EP.03", epName: "降噪耳机",
  };

  const clamp01 = (x) => Math.max(0, Math.min(1, x));
  const sm = (x) => x * x * (3 - 2 * x);
  const ramp = (t, a, b) => sm(clamp01((t - a) / (b - a)));

  // ---- the mechanism (inside the canal): how strong the reversed wave is, and how late (in cycles of the slowed wave)
  const LAG_MAX = 0.1;                                       // a tenth of a cycle late: 62 % of the noise is left
  const antiK = (t) => ramp(t, T.antiOn, T.antiEnd);
  const lag = (t) => LAG_MAX * (ramp(t, T.lagOn, T.lagMax) - ramp(t, T.lagOff, T.lagZero));
  const residual = (t) => { const k = antiK(t), p = 2 * Math.PI * lag(t); return Math.sqrt(1 + k * k - 2 * k * Math.cos(p)); };
  // ---- the missing step: a loose ear tip lets a little noise leak in; the inner microphone hears it, the chip fixes it
  const leakK = (t) => ramp(t, T.leak, T.leakEnd) * (1 - ramp(t, T.panC, T.panCEnd));      // the gap (closes again after)
  const fixK = (t) => ramp(t, T.fix, T.fixEnd);
  const leftover = (t) => 0.3 * ramp(t, T.leak, T.leakEnd) * (1 - fixK(t));
  // (v4: the adaptive section is gone; the noise level stays constant)
  const envK = () => 1, envF = () => 1;
  // everything the eardrum still gets, relative to the plain noise (mechanism + leak + adaptive lag)
  const residualAll = (t) => residual(t) * envK(t) + leftover(t) + Math.abs(envK(t) - envF(t)) * antiK(t);
  // ---- the real world (hook, closing): how much of the noise the earbud is cancelling right now
  function cancelReal(t) {
    if (t < T.unflood) return ramp(t, T.tap1, T.tap1 + 0.2);
    // after the climb it is off again until the second tap; then in two steps: the outer microphone's report reaches the
    // chip (most of it is cancelled), then the inner microphone's (the rest)
    return 0.88 * ramp(t, T.bubL - 0.125, T.bubL + 0.375) + 0.12 * ramp(t, T.bubOut - 0.1, T.bubOut + 0.2);
  }
  // ---- what the score's rumble layer does (0..1 of full level) and whether the world sounds "plugged"
  function rumbleLevel(t) {
    if (t < T.myth) return 1 - 0.95 * cancelReal(t);
    if (t < T.strike) return 0.3;                           // the wrong picture: plugged, muffled
    if (t < T.vibe) return 0.05;
    if (t < T.climb) return 0.05 + 0.6 * Math.min(1.4, residualAll(t)) * ramp(t, T.vibe, T.vibe + 0.5);
    if (t < T.climbEnd) return 0.05 + 0.75 * ramp(t, T.unflood, T.climbEnd);
    if (t < T.finOut) return 0.8 * (1 - 0.97 * cancelReal(t));   // the closing: a touch quieter than the opening
    return 0.8 * 0.03;
  }
  const muffled = (t) => (t < T.tap1 ? 1 : 0) + (t >= T.myth + 0.2 && t < T.strike ? 1 : 0) + (t >= T.climbEnd ? 1 - cancelReal(t) : 0);

  // sound cues derived from the same times (score.mjs reads this; beatcheck.mjs checks them on the measured grid)
  const HITS = {
    tap: [T.tap1, T.tap2], underline: [T.underline], myth: [T.myth], strike: [T.strike, T.strike + 0.125], a2: [T.a2],
    scan: [T.scan2], ring: [T.ring], seed: [T.seed], q4: [T.q4], pulse: [T.pulse], spk: [T.pulseEnd],
    anti: [T.antiOn], push: [T.push], lag: [T.lagOn, T.lagOff], name: [T.name], q7: [T.q7], leak: [T.leak], a7: [T.a7], say: [T.sayR], toChip: [T.bubR], fix: [T.fix],
    q9: [T.q9], say2: [T.say2L, T.say2R], toChip2: [T.bubL, T.bubOut], quiet: [T.quiet], fin: [T.fin], tip: [T.tip], endType: [T.title1], ep: [T.ep], sting: [T.sting],
  };

  const TL = { BPM, BEAT, BAR, FPS, DUR, W, H, T, COPY, HITS, LAG_MAX, antiK, lag, residual, leakK, fixK, leftover, envK, envF, residualAll, cancelReal, rumbleLevel, muffled };
  if (typeof module !== "undefined" && module.exports) module.exports = TL;
  else root.TL = TL;
})(typeof window !== "undefined" ? window : globalThis);
