// timeline.js — the single source of truth for picture (index.html) and sound (music/score.mjs).
// EP.09 无线充电 · 第二季第一集（半透明玻璃画风、字幕版式 A、钢鼓热带配乐 104 BPM）。脚本：script.md 逐句脚本 v3.1（定稿）。
// Every cue is written in script seconds and snapped to the 104 BPM eighth-note grid (≈ 0.2885 s) by q().
//   1 phenomenon   0     没插线，电怎么进手机的？（手把手机放上充电板，⚡）
//   2 surprise     2.75  没有一根线，连着它们
//   3 dig in       4.75  那电，怎么过去？ → 两边各藏着一圈铜线
//   4 mechanism    8.75  电流来回跑 → 磁跟着翻 → 穿过手机这圈 → 电也动起来 → 电没走过去，过去的是磁 → 理顺充进电池
//   5 missing step 24.75 为什么要放正 → 磁挤在正上方 → 放歪 → 磁少了、板子使劲发烫 → 磁铁；板子怎么知道是手机 → 问 / 回话 / 钥匙不回 / 还在说
//   6 closing      47.5  所以没插线，靠的是磁 + 小提示 → 片尾卡
(function (root) {
  const BPM = 104, BEAT = 60 / BPM, E8 = BEAT / 2, S16 = BEAT / 4, BAR = 4 * BEAT, FPS = 30;
  const W = 1080, H = 1920;
  const q = (s) => Math.round(s / E8) * E8;
  const S = {
    // 1 · 0–2.75
    h1: 0, drop: 0, land: 0.75, bolt: 0.75, under1: 1.5,
    // 2 · 2.75–4.75 镜头压低到侧面，两层外壳贴在一起，剖开一角
    a1: 2.75, low: 2.75, lowEnd: 4.0, cut: 3.5,
    // 3 · 4.75–8.75 推进去，外壳变透，露出两圈线圈
    q1: 4.75, push: 4.75, pushEnd: 8.5, a2: 6.75, litTx: 6.75, litRx: 7.75,
    // 4 · 8.75–24.75
    a3: 8.75, cur: 8.75,
    a4: 11.0, field: 11.0,
    q2: 13.25, through: 13.25,
    a5: 15.5, rxCur: 15.5,
    name: 17.75,
    q3: 20.75, toChip: 20.75,
    a6: 22.5, chip: 22.5, batt: 23.25,
    // 5 · 24.75–47.5
    q4: 24.75, pull: 24.75, pullEnd: 26.25,
    a7: 26.75, dense: 26.75,
    q5: 28.75, split: 28.75, splitEnd: 29.75,
    a8: 30.25, litL: 30.25, litR: 31.25,
    a9: 32.25, warm: 32.25, slow: 33.25,
    a10: 34.25, magnet: 34.25, ringTx: 34.5, ringRx: 35.0, snap: 35.75,
    q6: 36.75, pair: 36.75, pairEnd: 37.75,
    a11: 39.0, ping: 39.0,
    a12: 40.75, replyL: 40.75,
    a13: 42.75, silentR: 42.75,
    q7: 45.0, talk: 45.0, bub1: 45.75, bub2: 46.5,
    // 6 · 47.5–54.25
    a14: 47.5, back: 47.5, drop2: 47.75, land2: 48.5,
    tip: 50.25, ringOff: 51.25, nudge: 52.5,
    end: 54.25, endMorph: 54.85, title1: 54.75, ep: 55.75, sting: 56.75,
  };
  const T = {}; for (const k in S) T[k] = +q(S[k]).toFixed(4);
  const DUR = +(T.sting + 1.25).toFixed(4);

  // subtitles: [cue, lines, style, endCue]
  const COPY = {
    h1: ["没插线，", "电怎么[进]手机的？"],
    a1: ["没有一根线，", "[连]着它们"],
    q1: ["那电，", "怎么[过]去？"],
    a2: ["两边各藏着", "一圈[铜线]"],
    a3: ["板子这圈，电流", "来回[跑]"],
    a4: ["电流一来回，", "周围的[磁]也跟着翻"],
    q2: ["磁穿过外壳，", "手机这圈会[怎样]？"],
    a5: ["它里面的电，", "也跟着[动]起来了"],
    name: ["电没走过去，", "过去的是[磁]"],
    q3: ["来回跑的电，", "能直接[充]吗？"],
    a6: ["手机先把它理顺，", "再充进[电池]"],
    q4: ["那为什么，", "一定要放[正]？"],
    a7: ["磁都挤在线圈", "[正上方]"],
    q5: ["放[歪]一点呢？"],
    a8: ["穿过手机这圈的", "磁就[少]了"],
    a9: ["板子得更[使劲]，", "还容易[发烫]"],
    a10: ["有的手机和充电器，", "各有一圈[磁铁]"],
    q6: ["板子怎么知道，", "上面是[手机]？"],
    a11: ["板子先[问]一声"],
    a12: ["手机就用这圈线", "[回话]"],
    a13: ["钥匙不会回话，", "板子就[不送电]"],
    q7: ["充电时，手机", "还在[说]吗？"],
    a14: ["所以没插线，", "靠的是[磁]"],
    tip: ["充得慢、发烫？", "摘掉厚壳和[金属]指环，", "再放[正]一点"],
    // small labels
    tx: "发射线圈", rx: "接收线圈", freq: "每秒来回十几万到几十万次 · 慢放示意", color: "颜色为示意",
    induct: "这叫电磁感应", acdc: "交流 → 直流", aligned: "放正", tilted: "放歪", qi2: "Qi2 磁吸",
    load: "负载调制 · 示意", more: "多一点", less: "少一点", tipTag: "小提示", hand: "（手为占位，等参考图）",
    phone: "手机", key: "钥匙", reads: "板子读到的",
    end: ["你每天都在用，", "但你不知道", "它[怎么工作]"], epNum: "EP.09", epName: "无线充电",
  };
  const ORDER = ["h1", "a1", "q1", "a2", "a3", "a4", "q2", "a5", "name", "q3", "a6", "q4", "a7", "q5", "a8", "a9", "a10", "q6", "a11", "a12", "a13", "q7", "a14", "tip"];
  const STYLE = { name: "slam", a14: "slam" };
  const SUBS = ORDER.map((k, i) => ({ key: k, t0: T[k], t1: i + 1 < ORDER.length ? T[ORDER[i + 1]] : T.end, lines: COPY[k], style: STYLE[k] || "blur" }));

  // sound cues (music/score.mjs)
  const QUESTIONS = ["h1", "q1", "q2", "q3", "q4", "q5", "q6", "q7"].map((k) => T[k]);
  const HITS = {
    land: [T.land], bolt: [T.bolt], question: QUESTIONS.slice(1), name: [T.name], snap: [T.snap],
    ping: [T.ping], reply: [T.replyL, T.replyL + 2 * E8, T.replyL + 4 * E8], bubbles: [T.bub1, T.bub2],
    closing: [T.land2], ringOff: [T.ringOff], sting: [T.sting], stop: [T.name - E8, T.a14 - E8],
  };
  const TL = { BPM, BEAT, E8, S16, BAR, FPS, DUR, W, H, T, COPY, SUBS, HITS, QUESTIONS };
  if (typeof module !== "undefined" && module.exports) module.exports = TL;
  else root.TL = TL;
})(typeof window !== "undefined" ? window : globalThis);
