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
    h1: 0, drop: 0, land: 0.75, bolt: 0.75,
    a1: 2.75, low: 2.75, lowEnd: 4.0, cut: 3.5,
    q1: 4.75, push: 4.75, pushEnd: 8.0, a2: 6.75, litTx: 6.75, litRx: 7.5,
    exp1: 8.75, labIn: 8.75, magIn1: 9.25, magStop: 9.75, magOut1: 10.5,
    exp2: 11.25, shake: 11.25, labOut: 13.25,
    q2: 13.5, backPad: 13.5, backPadEnd: 14.75,
    a3: 15.5, cur: 15.5,
    a4: 18.0, through: 18.0, rxCur: 18.5,
    name: 20.5,
    // 5a · 放正：漏磁
    q4: 23.25, pull: 23.25, pullEnd: 24.5,
    q5: 25.25, slide: 25.75, slideEnd: 27.25,
    a7: 27.5, leak: 27.5,
    a10: 30.0, magnet: 30.0, ringTx: 30.25, ringRx: 30.75, snap: 31.5,
    // 5b · 无线为什么更容易热
    q8: 32.5, heatQ: 32.5,
    a15: 34.75, loss: 34.75,
    a16: 37.0, thermal: 37.25,
    // 5c · 金属：挡住磁
    q6: 39.25, metal: 39.25, metalIn: 39.75,
    a11: 41.0, eddy: 41.25, block: 41.5,
    a12: 43.5, metalHot: 43.5,
    a13: 45.75, stop: 46.5,
    // 6 · 闭环 + 小提示
    a14: 48.25, back: 48.25, drop2: 48.5, land2: 49.25,
    tip: 51.0, ringOff: 52.0, nudge: 53.25,
    end: 55.0, endMorph: 55.6, title1: 55.5, ep: 56.5, sting: 57.5,
  };
  const T = {}; for (const k in S) T[k] = +q(S[k]).toFixed(4);
  const DUR = +(T.sting + 1.25).toFixed(4);

  // subtitles: [cue, lines, style, endCue]
  const COPY = {
    h1: ["没插线，", "电怎么[进]手机的？"],
    a1: ["没有一根线，", "[连]着它们"],
    q1: ["那电，", "怎么[过]去？"],
    a2: ["两边各藏着", "一圈[铜线]"],
    exp1: ["磁铁插进线圈，", "灯就[亮]一下"],
    exp2: ["磁一[变]，", "线圈里就有电"],
    q2: ["但充电板里，", "没有会动的[磁铁]？"],
    a3: ["充电板让电流", "来回[换向]，", "磁也跟着来回变"],
    a4: ["手机这圈被磁穿过，", "电就[跑]起来了"],
    name: ["底下的磁一变，", "手机线圈里就有了[电]"],
    q4: ["那为什么，", "一定要放[正]？"],
    q5: ["把手机往旁边", "[挪]一挪呢？"],
    a7: ["磁从旁边[漏]走了，", "手机接到的就少"],
    a10: ["有的手机和充电器，", "各有一圈[磁铁]"],
    q8: ["那无线充电，", "为什么更容易[热]？"],
    a15: ["隔空传过去，", "总会[损失]一些"],
    a16: ["损失的变成了[热]，", "就贴在电池背后"],
    q6: ["中间夹块[金属]呢？"],
    a11: ["金属里感应出电，", "反过来把磁[挡住]"],
    a12: ["挡下来的，", "在金属里变成[热]"],
    a13: ["板子发现有金属，", "就降速、甚至[停充]"],
    a14: ["所以没插线，", "靠的是[磁]"],
    tip: ["充得慢、发烫？", "摘掉厚壳和[金属]指环，", "再放[正]一点"],
    tx: "发射线圈", rx: "接收线圈", freq: "每秒来回十几万到几十万次 · 慢放示意", color: "颜色为示意", gapNote: "间距放大 · 示意",
    induct: "这叫电磁感应", leakNote: "漏磁", lossNote: "线圈电阻 · 漏磁", thermalNote: "热成像 · 示意", qi2: "Qi2 磁吸 · 帮你对准",
    eddyNote: "涡流", fod: "异物检测", battNote: "电池", tipTag: "小提示",
    end: ["你每天都在用，", "但你不知道", "它[怎么工作]"], epNum: "EP.09", epName: "无线充电",
  };
  const ORDER = ["h1", "a1", "q1", "a2", "exp1", "exp2", "q2", "a3", "a4", "name", "q4", "q5", "a7", "a10", "q8", "a15", "a16", "q6", "a11", "a12", "a13", "a14", "tip"];
  const STYLE = { name: "slam", a14: "slam" };
  const SUBS = ORDER.map((k, i) => ({ key: k, t0: T[k], t1: i + 1 < ORDER.length ? T[ORDER[i + 1]] : T.end, lines: COPY[k], style: STYLE[k] || "blur" }));

  // sound cues (music/score.mjs)
  const QUESTIONS = ["h1", "q1", "q2", "q4", "q5", "q8", "q6"].map((k) => T[k]);
  const HITS = {
    land: [T.land], bolt: [T.bolt], question: QUESTIONS.slice(1), name: [T.name], snap: [T.snap],
    ledFlash: [T.magIn1, T.magOut1], closing: [T.land2], ringOff: [T.ringOff], stopCharge: [T.stop], sting: [T.sting],
    stop: [T.name - E8, T.a14 - E8],
  };
  const TL = { BPM, BEAT, E8, S16, BAR, FPS, DUR, W, H, T, COPY, SUBS, HITS, QUESTIONS };
  if (typeof module !== "undefined" && module.exports) module.exports = TL;
  else root.TL = TL;
})(typeof window !== "undefined" ? window : globalThis);
