// timeline.js — the single source of truth for picture (index.html) and sound (music/score.mjs).
// v4/v5: the 「为什么系列」 micro detective story, in one continuous space — a new question every 4–6 s, each one
// answered on screen before the next is asked:
//   1 phenomenon (no noun)      手机怎么知道你把它横过来了？
//   2 wrong guess, struck        你是不是以为里面藏了个小陀螺？ ✕ 其实里面什么都不转。
//   3 dig in                     那它到底怎么测旋转？ → scan → board → chip (smaller than rice) → 它自己不转，怎么知道你在转？ → lid → MEMS
//   4 one mechanism (slow)       一小块硅一直左右振动 → 这时手机转一下呢？ → 它就会向侧面"偏" → 为什么一偏就知道转多快？ → 转得越快偏得越多
//                                → the noun arrives as part of the answer: 这块会"偏"的硅，就叫陀螺仪。
//   5 the missing step           但只知道"转了"，够吗？ → split: 陀螺仪「我在转」| 加速度计「下面在哪」
//   6 back to the phenomenon     climb out → 手机到底怎么判断横屏？ → the phone turns again, both sensors speak live → 所以，你一横手机，它就知道了。
// v5: the same story, paced for reading — every key picture holds ≥ 1.5 s after it lands, every caption stays up
// ≥ 0.1 s per glyph + 0.5 s. 120 BPM: 1 beat = 0.5 s = 15 frames at 30 fps, 1 bar = 2 s; 44.5 s.
(function (root) {
  const BPM = 120, BEAT = 60 / BPM, BAR = 4 * BEAT, FPS = 30, DUR = 44.5;
  const W = 1080, H = 1920;

  const T = {
    // 0–4 · 1 the phenomenon
    rotEnd: 0.75, snap1: 1.0, underline: 2.0, h1Out: 3.84,
    // 4–8.5 · 2 the wrong guess: a toy spinning top inside the phone, struck
    myth: 4.0, push1End: 4.6, scan1: 4.0, scan1End: 4.5, q2: 4.25, hush: 6.0, strike: 6.5, a2: 6.75,
    // 8.5–17.25 · 3 dig in: the real board → the chip → open it, look, then go in
    unOrange: 8.5, scan2: 8.5, scan2End: 9.0, q3: 8.5, ring: 9.0, dive1: 9.5, dive1End: 11.0,
    rice: 11.0, dims: 11.25, a3: 11.0, q4: 13.0, push2: 14.0, push2End: 14.5,
    lid: 14.5, lidEnd: 15.1, flood: 15.5, floodEnd: 15.9, dive2: 15.25, dive2End: 17.25, vibe: 17.0,
    // 17.25–29 · 4 the one mechanism, deliberately slow: one proof mass
    h3: 17.25, tag1: 17.75,                                           // 一小块硅，一直在左右振动
    close: 19.25, closeEnd: 19.85, q5: 19.25, turnA: 20.0, a5: 21.0, tag2: 21.5,   // 这时，手机转一下呢？ → 它就会向侧面"偏"
    q6: 22.75, turnB: 24.0, punch: 24.0, a6: 24.5,                   // 为什么一偏就知道转多快？ → 转得越快，偏得越多
    name: 26.75, tagN: 27.25, glyphOut: 26.75, hush2: 28.5, turnEnd: 28.75,        // 这块会"偏"的硅，就叫陀螺仪。
    // 29–33.5 · 5 the missing step: the second sensor
    q7: 29.0, split: 30.5, splitEnd: 31.1, accDrop: 30.9, sayL: 31.0, sayR: 31.75,
    // 33.5–40.75 · 6 back to the phenomenon: climb out, the phone turns again, both sensors speak, the screen turns
    climb: 33.5, climbEnd: 34.75, unflood: 34.0, cover: 34.5, q8: 34.5,
    turn2: 36.25, turn2End: 37.5, say2G: 36.25, say2A: 36.75, snap2: 38.0, bubOut: 38.75, fin: 38.5, finOut: 40.75,
    // 40.75–44.5 end card
    end: 40.75, endMorph: 41.35, title1: 41.25, ep: 42.0, sting: 42.5,
  };

  const COPY = {
    h1: ["手机怎么知道", "你把它[横过来]了？"],
    q2: ["你是不是以为", "里面藏了个小[陀螺]？"],
    a2: ["其实里面", "什么都[不转]。"],
    q3: ["那它到底", "怎么测[旋转]？"],
    a3: ["答案藏在一颗", "比米粒还小的[芯片]里"],
    rice: "一粒米", mm3: "3 × 2.5 mm",
    q4: ["它自己不转，", "怎么知道你在[转]？"],
    h3: ["一小块硅，", "一直在[左右]振动"], tag1: "每秒上万次 · 慢放演示",
    q5: ["这时，", "手机[转]一下呢？"],
    a5: ["它就会", "向侧面[“偏”]！"], tag2: "这叫科里奥利效应",
    q6: ["为什么一偏，", "就知道转多[快]？"],
    a6: ["转得越快，", "偏得越[多]。"],
    name: ["这块会“偏”的硅，", "就叫[陀螺仪]。"], tagN: "名叫“陀螺”，却一圈都不转",
    rateUnit: "°/秒",
    q7: ["但只知道“转了”，", "[够吗]？"],
    nameL: "陀螺仪", nameR: "加速度计", tells: "告诉手机：", sayL: "我在转", sayR: "下面在哪", grav: "重力",
    q8: ["手机到底", "怎么判断[横屏]？"],
    fin: ["所以，你一横手机，", "它就[知道]了。"],
    deg: "90°",
    end: ["你每天都在用，", "但你不知道", "它[怎么工作]"], epNum: "EP.01", epName: "陀螺仪",
  };

  // the mass is driven at 1 Hz in the slow-motion demo: one swing per beat (right on one beat, left on the next)
  const VIB_HZ = 1;
  // how fast the phone turns (deg/s): a steady slow turn, then a steady fast one (trapezoids)
  const R1 = 30, R2 = 75, RAMP = 0.35;
  const clamp01 = (x) => Math.max(0, Math.min(1, x));
  const sm = (x) => x * x * (3 - 2 * x);
  function rate(t) {
    const up1 = sm(clamp01((t - T.turnA) / RAMP)), up2 = sm(clamp01((t - T.turnB) / RAMP)), down = 1 - sm(clamp01((t - (T.turnEnd - RAMP)) / RAMP));
    return (R1 * up1 + (R2 - R1) * up2) * down;
  }
  function turn(t) {                                      // integral of rate (numeric, pure)
    let s = 0; const n = 200, a = T.turnA, b = Math.max(a, Math.min(t, T.turnEnd)), h = (b - a) / n;
    for (let i = 0; i < n; i++) s += rate(a + (i + 0.5) * h) * h; return s;
  }
  const RATE_MAX = R2;
  const omega = (t) => rate(t) / RATE_MAX;                 // 0..1

  // sound cues derived from the same times (score.mjs reads this; beatcheck.mjs checks them on the measured grid)
  const HITS = {
    tick: [T.rotEnd], snap: [T.snap1, T.snap2], underline: [T.underline],
    myth: [T.myth], strike: [T.strike, T.strike + 0.125], a2: [T.a2],
    scan: [T.scan2], ring: [T.ring], rice: [T.rice, T.dims], q4: [T.q4], lid: [T.lid],
    close: [T.close], turn: [T.turnA, T.turnB], name: [T.name], q7: [T.q7], split: [T.split], say: [T.sayL, T.sayR],
    q8: [T.q8], turn2: [T.turn2], say2: [T.say2G, T.say2A], fin: [T.fin], endType: [T.title1], ep: [T.ep], sting: [T.sting],
  };

  const TL = { BPM, BEAT, BAR, FPS, DUR, W, H, T, COPY, HITS, VIB_HZ, turn, rate, omega, RATE_MAX, R1, R2 };
  if (typeof module !== "undefined" && module.exports) module.exports = TL;
  else root.TL = TL;
})(typeof window !== "undefined" ? window : globalThis);
