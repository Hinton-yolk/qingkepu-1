// timeline.js — the single source of truth for picture (index.html) and sound (music/score.mjs).
// EP.06 人脸解锁 — 化了妆、戴了口罩，手机为什么还认得你？ (script.md v2.1, content gate 1 passed 2026-11-11).
//   0      化了妆，手机为什么还认得你？      (lipstick, the last stroke; the phone comes up; a glance; the lock opens)
//   2.75   它不只在看你，还在量你             (the camera goes to the top of the phone; 以 iPhone 面容 ID 为例)
//   5.25   拿什么量？钻进屏幕顶上看看 → in, one take (dark): the dot projector and the infrared camera beside it
//   7.75   成千上万个光点 → 10.25 为了什么？ → 12 量高低 (lines of equal height sweep over the face)
//   14.25  怎么看出高低？ → top view: the same beam on the reference wall and on the nose tip → 18.75 three beams
//   20.75  把每个点挪了多少拼起来 → 22.75 高低起伏 (the depth map; an infrared photo; both go to the stored you)
//   25.25  化了妆呢？ → 26.75 颜色变，高低几乎没变 (depth map still, IR photo 略变) → 29.25 修容 → 31.75 高度没变
//   34     戴了口罩呢？ → 36.5 只看眼睛周围 → 39 够认出你吗？ → 41 独有的
//   43     闭环 (light again): makeup and a mask, a glance, the lock opens → 46 / 48 小提示 (two beats) → 50.5 end card
// 120 BPM: 1 beat = 0.5 s = 15 frames at 30 fps. Every cue is on the 0.25 s grid, at the script's times.
(function (root) {
  const BPM = 120, BEAT = 60 / BPM, BAR = 4 * BEAT, FPS = 30, DUR = 54.0;
  const W = 1080, H = 1920;

  const T = {
    // 0–2.75 · the phenomenon: the last stroke of lipstick, the phone comes up, a glance, the lock opens
    stroke: 0, strokeEnd: 0.75, lipOut: 0.5, lipOutEnd: 0.95, rise: 0.75, riseEnd: 1.25, scan: 1.25, ka0: 1.5, underline: 2, h1Out: 2.59,
    // 2.75–5.25 · it measures you: to the top of the phone
    a2: 2.75, toTop: 2.75, toTopEnd: 4.0, note: 3.0, noteOut: 7.5, glow: 4.25,
    // 5.25–7.75 · one take in (dark): the projector and the infrared camera
    q3: 5.25, dive: 5.25, flood: 5.75, floodEnd: 6.25, diveEnd: 6.5, parts: 6.5,
    // 7.75–14.25 · the dots; what for; to measure the heights
    a3: 7.75, turn: 7.75, turnEnd: 8.5, fire: 8.25, fireEnd: 9.25,
    q4: 10.25, a4: 12, iso: 12.25, isoEnd: 13.75,
    // 14.25–20.75 · how: the top view; the same beam (wall / nose); three beams
    q5: 14.25, top: 14.25, topEnd: 15.0, beam: 15.25, a5: 16.25, wall: 16.25, nose: 16.75, shift: 17.25,
    a6: 18.75, b1: 19.0, b2: 19.5, b3: 20.0,
    // 20.75–25.25 · put together: the depth map; the infrared photo; both compared with the stored you
    q6: 20.75, back: 20.75, backEnd: 21.5, grow: 21.25, growEnd: 22.5, stop1: 22.5, a7: 22.75, irPhoto: 23.25, compare: 24.0, compareEnd: 24.75, match1: 24.75,
    // 25.25–34 · makeup: colour changes, the heights hardly; the contour
    q8: 25.25, lips: 25.25, lipsEnd: 25.75, blush: 25.75, blushEnd: 26.25, shadow: 26.25, shadowEnd: 26.75,
    a8: 26.75, cards: 26.75, cardsEnd: 27.25, irTag: 27.75,
    q9: 29.25, contour: 29.5, contourEnd: 30.5, a9: 31.75, prof: 31.75, profEnd: 32.5,
    // 34–43 · the mask; only the eyes; enough?; unique
    q10: 34, mask: 34.25, maskEnd: 35.0, toDepth: 35.0, toDepthEnd: 35.75, a10: 36.5, ring: 36.5, ringEnd: 37.25,
    q11: 39, swing: 39, swingEnd: 41, a11: 41, match2: 41.5,
    // 43–46 · back to the start (light): makeup, a mask, a glance, the lock opens (loudest hit, after a half-beat stop)
    fin: 43, out: 43, outEnd: 43.75, stop: 43.75, ka: 44, finOut: 45.9,
    // 46–50.4 · the tip, two beats: not recognised → the passcode → close enough, next time easier
    tip: 46, miss: 46.25, keys: 46.75, keysEnd: 47.75, open2: 48.0, tip2: 48.0, tipOut: 50.4,
    // 50.5–54 end card
    end: 50.5, endMorph: 51.1, title1: 51.25, ep: 52.0, sting: 52.5,
  };

  const COPY = {
    h1: ["[化了妆]，手机", "为什么还[认得]你？"],
    a2: ["它不只在看你，", "还在[量]你"],
    note: "以 iPhone 面容 ID 为例", irNote: "红外光，肉眼看不见",
    q3: ["拿什么量？钻进", "屏幕[顶上]看看"],
    a3: ["它往你脸上打出", "成千上万个[光点]"],
    q4: ["打这么多点，", "是为了[什么]？"],
    a4: ["为了量出你脸的", "[高低]"],
    q5: ["点打在脸上，", "怎么看出[高低]？"],
    a5: ["旁边的镜头斜着看，", "同一个点会[挪位置]"],
    a6: ["鼻尖离手机更近，", "挪得就[更多]"],
    q6: ["把每个点挪了多少", "[拼起来]"],
    a7: ["就是你脸的", "[高低起伏]"],
    q8: ["那[化了妆]呢？"],
    a8: ["妆主要改[颜色]，", "脸的高低几乎[没变]"],
    q9: ["修容让鼻梁看着更高，", "它会[量错]吗？"],
    a9: ["不会：鼻梁的高度", "[没变]"],
    q10: ["那[戴了口罩]，", "半张脸都挡住了呢？"],
    a10: ["它就只看你", "[眼睛]周围"],
    q11: ["只看眼睛周围，", "[够]认出你吗？"],
    a11: ["眼周的高低和样子，", "也是你[独有]的"],
    fin: ["妆会变，口罩会挡，", "但你脸的[形状]还在"],
    tipTag: "小提示：", tip: ["[浓妆]没认出？", "马上输一次[密码]"], tip2: ["这次和存下的够接近，", "下次更[容易]认出"],
    // labels in the picture (short; technical words only as small text)
    proj: "点阵投影器", ircam: "红外镜头", demo: "示意", dots: "红外光点 · 人眼看不见",
    wallL: "参考面", topv: "俯视", noseL: "鼻尖", cheekL: "脸颊", sideL: "脸侧", angle: "角度已放大 · 示意", imgL: "镜头里",
    depth: "深度图", ir: "红外照片", stored: "存着的你", slight: "略变", same: "没变", before: "修容前", after: "修容后",
    setting: "需在设置里打开", setting2: "「戴口罩使用面容 ID」", hiL: "高低", lookL: "样子", lockMiss: "未识别", pass: "输入密码",
    end: ["你每天都在用，", "但你不知道", "它[怎么工作]"], epNum: "EP.06", epName: "人脸解锁",
  };

  const clamp01 = (x) => Math.max(0, Math.min(1, x));
  const S16 = BEAT / 4;
  const HITS = {
    stroke: [T.stroke], rise: [T.rise], scan: [T.scan], ka0: [T.ka0], underline: [T.underline],
    a2: [T.a2], toTop: [T.toTop], glow: [T.glow],
    q3: [T.q3], dive: [T.dive], flood: [T.flood], parts: [T.parts, T.parts + 0.25],
    a3: [T.a3], fire: [0, 1, 2, 3].map((i) => T.fire + i * S16 * 2),
    q4: [T.q4], a4: [T.a4], iso: [T.iso],
    q5: [T.q5], top: [T.top], beam: [T.beam], a5: [T.a5], wall: [T.wall], nose: [T.nose], shift: [T.shift],
    a6: [T.a6], beams: [T.b1, T.b2, T.b3],
    q6: [T.q6], grow: [T.grow], stop1: [T.stop1], a7: [T.a7], irPhoto: [T.irPhoto], compare: [T.compare], match1: [T.match1],
    q8: [T.q8], makeup: [T.lips, T.blush, T.shadow], a8: [T.a8], cards: [T.cards], irTag: [T.irTag],
    q9: [T.q9], contour: [T.contour, T.contour + 0.5], a9: [T.a9], prof: [T.prof],
    q10: [T.q10], mask: [T.mask], toDepth: [T.toDepth], a10: [T.a10], ring: [T.ring],
    q11: [T.q11], a11: [T.a11], match2: [T.match2],
    fin: [T.fin], out: [T.out], stop: [T.stop], ka: [T.ka],
    tip: [T.tip], miss: [T.miss], keys: [0, 1, 2, 3, 4, 5].map((i) => T.keys + i * S16), open2: [T.open2],
    endType: [T.title1], ep: [T.ep], sting: [T.sting],
  };

  const TL = { BPM, BEAT, BAR, FPS, DUR, W, H, T, COPY, HITS, S16, clamp01 };
  if (typeof module !== "undefined" && module.exports) module.exports = TL;
  else root.TL = TL;
})(typeof window !== "undefined" ? window : globalThis);
