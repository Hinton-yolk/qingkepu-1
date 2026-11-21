// timeline.js — single source of truth for picture (index.html) and sound (music/score.mjs).
// 一语道破 ·《AI 为什么一个字一个字往外蹦？》方案 A「把光标后面打开」— opening prototype (≈27 s).
//
//   0      后面的答案，已经写好了吗？   the answer is streaming; tweezers pinch the cursor and pull it right:
//                                     the bubble stretches, but behind the cursor there is only blank paper; it snaps back
//   4.2    掀开比一比                   a second card appears: "假如早写好" (the full sentence printed, under a cover).
//                                     Lift its cover: the text is there. Play it: the cover slides, text is *uncovered*.
//                                     Lift the real card's cover: blank. Then 「火锅」 is *written* at the cursor tip.
//   9.9    后面没藏着，是现写的          the "pre-written" card leaves
//   11.4   那下一块，从哪来？            rewind 「火锅」, slow replay: the amber "前文" band covers everything so far,
//                                     a few candidates rise from it, one is picked, it drops into the slot —
//   15.9   ★ the band zips forward and swallows 「火锅」: 刚写出的，立刻算进前文
//   18.2   normal speed: ， 加 一份 — land + zip, land + zip, land + zip (the rule, by rhythm)
//   20.0   the next candidates are all hot-pot things (毛肚 肥牛 虾滑) — a thread runs from 「火锅」 to them
//   23.6   two empty slots open after the cursor: 后面几块，能一起算吗？  (→ the climax of the full episode)
// 30 fps.  Beat grid 100 BPM (0.6 s) only for the music; picture events are placed by eye.
(function (root) {
  const FPS = 30, DUR = 26.2, W = 1080, H = 1920;

  const T = {
    // hook
    pop2: 0.40,
    twIn: 0.85, twAt: 1.30, pinch: 1.38, pull: 1.52, pullEnd: 2.70, tug1: 2.82, tug2: 3.12, empty: 2.85, release: 3.45, back: 4.15,
    // compare
    cmpIn: 4.25, cmpInEnd: 4.95, cap2: 4.4,
    gGo: 5.0, gGrab: 5.45, gLift: 5.55, gLiftEnd: 6.05, gDrop: 6.35, gDropEnd: 6.65, gPlay: 6.75, gPlayEnd: 7.65,
    rGo: 7.75, rGrab: 8.15, rLift: 8.25, rLiftEnd: 8.75, rHollow: 8.78, twOut: 9.0,
    write: 9.25, writeEnd: 9.85,
    cap3: 9.9, ghostOut: 10.2, ghostOutEnd: 10.9, zoomIn: 10.2, zoomInEnd: 11.3,
    // slow replay
    cap4: 11.4, rewind: 11.5, rewindEnd: 12.0, slowTag: 11.5,
    band: 12.0, bandEnd: 12.8,
    cand: 13.1, candEnd: 13.7,
    hop: [13.95, 14.25, 14.55, 14.80, 15.05], pick: 15.05,
    fly: 15.25, flyEnd: 15.65,
    zip: 15.95, zipEnd: 16.55, cap5: 16.35,
    slowOff: 17.20,
    // rhythm
    r1: 17.50, z1: 17.70, r2: 18.00, z2: 18.20, r3: 18.50, z3: 18.70,
    cand2: 19.10, cand2End: 19.60, thread: 19.65, threadEnd: 20.15, cap6: 19.90,
    hop2: [20.55, 20.85, 21.15], pick2: 21.15,
    fly2: 21.35, fly2End: 21.75, zip4: 22.00, zip4End: 22.45,
    // teaser
    cap7: 22.90, slots: 23.10, slotsEnd: 23.70, push: 23.20, pushEnd: 24.20, endHold: 24.60,
  };

  // the answer, split into display blocks (a demonstration split — not a real tokenizer's output)
  const BLOCKS = [
    { s: "今晚", i: 0 }, { s: "吃", i: 2 }, { s: "火锅", i: 3 }, { s: "，", i: 5 },
    { s: "加", i: 6 }, { s: "一份", i: 7 }, { s: "毛肚", i: 9 },
  ];
  const CAND1 = ["面条", "火锅", "烧烤"], PICK1 = 1;
  const CAND2 = ["肥牛", "毛肚", "虾滑"], PICK2 = 1;

  const COPY = {
    q1a: "后面的答案", q1b: "已经写好了吗？", q1c: "……拉开是空的？",
    c2: "掀开比一比",
    c3: "后面没藏着，是现写的",
    c4: "那下一块，从哪来？",
    c5a: "刚写出的", c5b: "立刻算进「前文」",
    c6a: "有了「火锅」", c6b: "才冒出「毛肚」",
    q7a: "后面几块", q7b: "能一起算吗？",
    user: "今晚吃什么？",
    tagGhost: "假如早写好", tagReal: "AI 的回答", band: "前文", slow: "慢放", note: "分块、候选均为示意",
  };

  // sound cues: [time, kind, arg]
  const HITS = [
    [0.0, "tick", 0], [T.pop2, "tick", 1],
    [T.empty, "hmm"], [T.pinch, "click"], [T.pull, "stretch", T.pullEnd - T.pull], [T.tug1, "tug"], [T.tug2, "tug"], [T.release, "boing"],
    [T.cmpIn, "whoosh"], [T.gLift, "lift"], [T.gLiftEnd, "found"], [T.gDrop, "drop"],
    [T.gPlay, "tick", 3], [T.gPlay + 0.3, "tick", 4], [T.gPlay + 0.6, "tick", 5],
    [T.rLift, "lift"], [T.rHollow, "hollow"], [T.write, "pen", T.writeEnd - T.write],
    [T.ghostOut, "whoosh"], [T.rewind, "rewind", T.rewindEnd - T.rewind],
    [T.band, "sweep", T.bandEnd - T.band], [T.cand, "rise"],
    ...T.hop.map((h, k) => [h, "hop", k]), [T.pick, "pick"], [T.flyEnd, "land"], [T.zip, "zip"],
    [T.r1, "land", 0.5], [T.z1, "zip", 0.5], [T.r2, "land", 0.5], [T.z2, "zip", 0.5], [T.r3, "land", 0.5], [T.z3, "zip", 0.5],
    [T.cand2, "rise"], [T.thread, "thread"], ...T.hop2.map((h, k) => [h, "hop", k + 1]), [T.pick2, "pick"],
    [T.fly2End, "land"], [T.zip4, "zip"], [T.slots, "slot"], [T.slots + 0.18, "slot"], [T.cap7, "question"],
  ];

  const TL = { FPS, DUR, W, H, T, BLOCKS, CAND1, PICK1, CAND2, PICK2, COPY, HITS };
  if (typeof module !== "undefined" && module.exports) module.exports = TL; else root.TL = TL;
})(typeof window !== "undefined" ? window : globalThis);
