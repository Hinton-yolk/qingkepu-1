// timeline.js — the single source of truth for picture (index.html) and sound (music/score.mjs).
// EP.10 实况照片 — 你还没按快门，它怎么就拍上了？ script v3 (script.md 「逐句脚本 v3」, user 11-23: 「没问题 继续吧」).
//   0      烟花快散了才按，怎么还拍到它炸开？   (two hands hold the phone sideways; the shutter after the burst; the photo plays)
//   2.75   你是不是以为，一按它才开始录？        (orange; a film strip grows only to the right of 按下; 4.0 ✕)
//   4.75   其实你按之前，它早就在拍了。          (the strip grows to the left too)
//   6.75   那它从什么时候开始拍的？              (one take into the phone: the screen in front, the lens + chip behind, dark)
//   9.5–20.75  the viewfinder moves before you press; the chip shoots it; a pile; the ring keeps only the latest
//   20.75–31.25 the press: the 1.5 s before are kept, the 1.5 s after too, one sharp photo at the press → 实况照片
//   31.25  烟花快散了才按，炸开那一下哪来的？      (back to the first shot; a window into the phone shows the ring)
//   33.5   按快门，不是让它开始拍，是让它别扔掉。
//   36.5   小提示 (change the cover frame)
//   41.0   end card
// 120 BPM: 1 beat = 0.5 s = 15 frames at 30 fps, 1 bar = 2 s.
(function (root) {
  const BPM = 120, BEAT = 60 / BPM, BAR = 4 * BEAT, FPS = 30, DUR = 44.75;
  const W = 1080, H = 1920;

  const T = {
    // 0–2.75 · the phenomenon (the firework burst at −0.25; the shutter 1 s after the burst)
    h1: 0, tap0: 0.75, thumbFly: 1.25, open0: 1.5, underline: 2.0,
    // 2.75–6.75 · the guess (orange), struck; the flip
    q2: 2.75, myth: 2.75, stripR: 3.0, hush: 3.5, strike: 4.0,
    a2: 4.75, unOrange: 4.75, stripL: 4.9,
    // 6.75–9.5 · one take in
    q3: 6.75, dive: 6.75, xray: 6.9, darkA: 7.1, darkB: 8.1, lay: 8.0, diveEnd: 9.5,
    // 9.5–20.75 · the viewfinder, the chip, the pile, the ring
    h4: 9.5, vfOn: 9.5,
    a4: 11.75, chipOn: 11.25, flow: 11.75,
    q5: 14.0, pile: 14.0, pileEnd: 16.0,
    a5: 16.0, ringForm: 16.0, ringFormEnd: 17.0, write0: 17.0,
    a6: 18.5, term: 18.5,
    // 20.75–31.25 · the press
    q7: 20.75, pull: 20.75, pullEnd: 21.35, tap: 21.0,
    a7: 22.75, copyB: 23.0,
    q8: 24.75, liveBox: 24.75, copyA: 25.25,
    a8: 26.75, key: 26.75, soften: 27.5,
    stop1: 28.25, a9: 28.75, collapse: 28.75, collapseEnd: 29.25,
    // 31.25–36.5 · back to the first shot
    q10: 31.25, iris: 31.25, irisEnd: 31.85, tapC: 32.0,
    stop2: 33.0, fin: 33.5,
    // 36.5–41 · the tip
    tip: 36.5, tipIn: 36.5, tipInEnd: 37.1, tip2: 38.5, slide: 38.75, slideEnd: 39.25,
    // 41–44.75 · end card
    end: 41.0, endMorph: 41.6, title1: 41.75, ep: 42.5, sting: 43.0,
  };

  // the fireworks. Outside (film time): the opening burst at −0.25, the closing one at 31.0 (the shutter 1 s after each).
  // Inside (sky time τ, see tau()): bursts at 10.0 (the viewfinder), 14.5 (the pile), 18.0 (the ring), 20.0 (pressed at 21.0).
  const BURST_OUT = [-0.25, 31.0];
  const BURST_IN = [10.0, 14.5, 18.0, 20.0];
  // inside, the press is shown 4× slowed (示意): τ runs at ¼ speed from the tap until 27.5
  const SLOW = { a: 21.0, b: 27.5, k: 0.25 };
  function tau(t) {
    if (t < SLOW.a) return t;
    if (t < SLOW.b) return SLOW.a + (t - SLOW.a) * SLOW.k;
    return SLOW.a + (SLOW.b - SLOW.a) * SLOW.k + (t - SLOW.b);
  }
  // the ring: 12 slots, one written every ¼ s of sky time from T.write0 (write index n = 0 at τ = 17.0)
  const RING = { n: 12, dt: 0.25, t0: 17.0 };
  const ringF = (t) => (t < T.write0 ? 0 : (tau(t) - RING.t0) / RING.dt);
  const PRESS_N = 16;                      // τ = 21.0: the write index at the press
  const BEFORE = [10, 11, 12, 13, 14, 15]; // τ 19.5 … 20.75
  const AFTER = [16, 17, 18, 19, 20, 21];  // τ 21.0 … 22.25
  const COPYB_T = BEFORE.map((_, i) => T.copyB + i * 0.25);
  const COPYA_T = AFTER.map((_, i) => T.copyA + i * 0.25);

  const COPY = {
    h1: ["烟花快散了才按，", "怎么还拍到它[炸开]？"],
    q2: ["你是不是以为，", "一按它才开始[录]？"],
    a2: ["其实你按之前，", "它[早就]在拍了。"],
    q3: ["那它从什么时候", "开始[拍]的？"],
    h4: ["你还没按，", "取景框就已经在[动]了"],
    a4: ["取景框里的画面，", "就是它[刚拍]的"],
    q5: ["它还一张张留着，", "不会被[塞满]吗？"],
    a5: ["它只留最近一小段，", "旧的被新的[盖掉]"],
    a6: ["没按快门的，", "转一圈就[没了]"],
    q7: ["那你一按快门，", "它做了[什么]？"],
    a7: ["前面这1.5秒，", "从这一圈里[留下]"],
    q8: ["那按下之后呢？", "接着拍的也[留下]"],
    a8: ["按下那一刻，", "还拍了一张[清楚的]"],
    a9: ["拼在一起，", "就是[实况照片]。"],
    q10: ["烟花快散了才按，", "炸开那一下[哪来]的？"],
    fin: ["按快门，", "不是让它开始拍，", "是让它[别扔掉]。"],
    tip1: ["没拍到最亮那一下？", "先别[删]"],
    tip2: ["点编辑，", "换一帧当[封面]"],
    // small text (terms and notes only as small text)
    press: "按下", rec: "开始录", before: "按之前", chip: "感光芯片", fps: "一秒很多张", ring: "这一圈 · 示意", term: "学名：环形缓冲区",
    pre: "前 1.5 秒", post: "后 1.5 秒", names: "叫法、时长各家不同", tipTag: "小提示", iphone: "以 iPhone 为例 · 可能没原图清楚", live: "实况",
    end: ["你每天都在用，", "但你不知道", "它[怎么工作]"], epNum: "EP.10", epName: "实况照片",
  };
  const S16 = BEAT / 4;

  const HITS = {
    tap0: [T.tap0], open0: [T.open0], underline: [T.underline],
    myth: [T.myth], stripR: [T.stripR], strike: [T.strike], a2: [T.a2], stripL: [T.stripL + 0.1],
    q3: [T.q3], h4: [T.h4], chipOn: [T.chipOn], a4: [T.a4], q5: [T.q5], a5: [T.a5], write0: [T.write0], a6: [T.a6],
    q7: [T.q7], tap: [T.tap], a7: [T.a7], copyB: COPYB_T, q8: [T.q8], liveBox: [T.liveBox], copyA: COPYA_T,
    a8: [T.a8], key: [T.key], a9: [T.a9],
    q10: [T.q10], tapC: [T.tapC], fin: [T.fin],
    tip: [T.tip], tip2: [T.tip2], slideEnd: [T.slideEnd],
    endType: [T.title1], ep: [T.ep], sting: [T.sting],
  };

  const TL = { BPM, BEAT, BAR, FPS, DUR, W, H, T, COPY, HITS, S16, BURST_OUT, BURST_IN, SLOW, tau, RING, ringF, PRESS_N, BEFORE, AFTER, COPYB_T, COPYA_T };
  if (typeof module !== "undefined" && module.exports) module.exports = TL;
  else root.TL = TL;
})(typeof window !== "undefined" ? window : globalThis);
