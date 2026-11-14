// timeline.js — the single source of truth for picture (index.html) and sound (music/score.mjs).
// EP.03 微波炉 v1 — written from the approved plain-language version (白话.md). The 「为什么系列」 detective story in one
// continuous space: a microwave oven seen from the front (a little from above), a bowl of leftover rice inside, drawn as a section.
//   1 phenomenon          热了两分钟，中间怎么还是凉的？                (the hum stops on the ding; the section: hot rim, cold middle)
//   2 wrong guess, struck  你是不是以为，它是从里往外热的？ ✕ 其实它先热的，是外面一层。
//   3 dig in               为什么，只热外面？ → the little plate on the side wall → the tube behind the control panel → 然后呢？
//                          → follow the microwave out, bouncing off the metal walls, into the rice → into its outer layer (dark)
//   4 one mechanism        water molecules (+/−) → the field flips, they twist along → twisting fast, bumping, hot
//                          → why only the outside? the wave is eaten on the way in → 微波炉热的，其实是水。
//   5 the missing step     要是转盘不转呢？ → bounced waves stack into hot spots → the turntable walks every bit of rice through them
//   6 back to the start    再按一次，发生了什么？ → the outer water: 我在扭！ the middle: 还没轮到我… → ding → 所以中间凉……
//                          + a small tip in the same place: 热剩饭，中间扒个坑，叮完焖一分钟，热会自己走到中间。
// 120 BPM: 1 beat = 0.5 s = 15 frames at 30 fps, 1 bar = 2 s; 59.75 s. Both dings, the strike and the name land on bar lines.
(function (root) {
  const BPM = 120, BEAT = 60 / BPM, BAR = 4 * BEAT, FPS = 30, DUR = 59.75;
  const W = 1080, H = 1920;

  const T = {
    // 0–5 · 1 the phenomenon: two seconds of the oven running, the ding, push in on the bowl
    ding1: 2.0, push0: 2.0, push0End: 3.0, underline: 3.0, h1Out: 4.84,
    // 5–10.5 · 2 the wrong guess: the section swept into "hottest in the middle", struck
    myth: 5.0, scan1: 5.0, scan1End: 5.6, q2: 5.25, hush: 7.5, strike: 8.0, a2: 8.25,
    // 10.5–22 · 3 dig in: back to the cavity → the little plate → the tube behind the panel → follow the microwave into the rice
    unOrange: 10.5, scan2: 10.5, scan2End: 11.1, q3: 10.5, back1: 10.75, back1End: 12.0, ring: 12.25,
    dive1: 12.75, dive1End: 14.25, scan3: 14.0, scan3End: 14.6, a3: 14.5,
    q4: 16.75, follow: 17.0, followEnd: 17.75, pulse: 17.75, pulseEnd: 19.0,
    dive2: 19.25, dive2End: 21.75, flood: 21.4, floodEnd: 21.75, vibe: 21.75,        // one take: oven → bowl → rice → one grain → inside it
    // 22–38 · 4 the one mechanism, slowly: water molecules in the rice's outer layer
    h3: 22.0,                                                         // 饭里的水分子，一头正，一头负
    q5: 25.0, pullOut: 25.0, pullOutEnd: 25.75, fieldOn: 26.0, fieldOnEnd: 27.0, push: 27.25,   // 微波一来 → 跟着扭
    heat: 29.5, heatEnd: 30.5, a5: 30.0,                               // 挤来撞去，就热了
    q6: 31.75, depth: 32.0, depthEnd: 32.6, front: 32.646, frontEnd: 34.792, a6: 33.25,   // 只热外面？每碰到水分子，就被吃掉一点
    // (the front crosses one column of molecules every 0.25 s: 32.75, 33.0, … 34.5 — on the grid, so each bite can be heard)
    name: 36.0, hush2: 37.5,                                           // 微波炉热的，其实是水。
    // 38–45 · 5 the missing step: the turntable (back in the cavity, light)
    climbA: 37.75, climbAEnd: 39.0, unflood: 38.05,
    q7: 38.0, lightA: 38.6, spots: 39.25, spotsEnd: 40.0, a7: 40.0, side: 40.25, sideEnd: 41.5,
    a8: 42.75, spin: 42.75, spinUp: 43.25, even: 43.25, evenEnd: 44.5,
    // 45–56.35 · 6 back to the phenomenon: pull out, a fresh cold bowl, press start; in the section the microwaves go in and
    //            die within the outer layer, which turns orange; the middle stays grey; ding; a small tip
    climb: 45.0, climbEnd: 46.25, q9: 46.0,
    hand2: 46.5, tap2: 47.25, waveIn: 47.625, waveInEnd: 49.875, ding2: 50.0, quiet: 50.0,
    fin: 50.25, finOut: 52.75, tip: 52.75, tipOut: 56.35,
    // 56.5–59.75 end card
    end: 56.5, endMorph: 57.1, title1: 57.0, ep: 57.5, sting: 58.0,
  };

  const COPY = {
    h1: ["热了两分钟，", "中间怎么还是[凉]的？"],
    q2: ["你是不是以为，", "它是[从里往外]热的？"],
    a2: ["其实它先热的，", "是[外面]一层。"],
    q3: ["为什么，", "只热[外面]？"],
    a3: ["小方片后面，", "藏着发[微波]的管子"],
    q4: ["然后[呢]？"],
    h3: ["饭里的水分子，", "一头[正]，一头[负]"],
    q5: ["微波一来[呢]？"],
    push: ["电场每秒来回翻 24.5 亿次，", "它就跟着来回[扭]"],
    slow: "慢放", field: "电场",
    a5: ["扭得飞快，挤来撞去，", "就[热]了"],
    q6: ["那为什么，", "只热[外面]？"],
    depth: "两三厘米", mid: "中间",
    a6: ["微波每碰到水分子，", "就被[吃掉]一点"],
    name: ["微波炉热的，", "其实是[水]。"],
    q7: ["为什么需要", "转盘[转动]呢？"],
    a7: ["因为微波来回反弹", "不均匀，", "会叠出一块块[热点]"],
    a8: ["转盘一转，", "每块饭都轮流[路过]热点"],
    q9: ["再热一次，", "看看微波去了[哪儿]"],
    fin: ["所以中间凉：", "微波只热得到[外面]的水"],
    tipTag: "小提示", tip: ["热剩饭，中间[扒个坑]，", "叮完[焖一分钟]，", "热会自己走到中间。"],
    start: "开始",
    end: ["你每天都在用，", "但你不知道", "它[怎么工作]"], epNum: "EP.02", epName: "微波炉",
  };

  const clamp01 = (x) => Math.max(0, Math.min(1, x));
  const sm = (x) => x * x * (3 - 2 * x);
  const ramp = (t, a, b) => sm(clamp01((t - a) / (b - a)));

  // ---- the oven: is it running (light, hum), and the turntable angle (pure function of t: integrated piecewise)
  const running = (t) => (t < T.ding1) || (t >= T.lightA && t < T.climb) || (t >= T.tap2 + 0.05 && t < T.ding2);
  const OMEGA = (2 * Math.PI) / 6;                                   // one turn in 6 s (a little quicker than life)
  function turn(t) {                                                 // bowl angle on the plate; π/2 = at the front
    const F = Math.PI / 2;
    if (t < T.ding1) return F + OMEGA * (t - T.ding1);              // stops at the front on the first ding
    if (t < T.climbA) return F;                                      // parked at the front while we look inside
    if (t < T.spin) return F + 2.1;                                  // the missing step: stopped, off to one side
    if (t < T.climb + 0.6) {                                         // spins up over 0.5 s, then turns
      const u = t - T.spin, a = T.spinUp - T.spin;
      const d = u < a ? OMEGA * u * u / (2 * a) : OMEGA * (a / 2 + (u - a));
      return F + 2.1 + d;
    }
    if (t < T.tap2) return F + Math.PI / 2;                          // (hidden by the pull-out) a fresh bowl, parked
    if (t < T.ding2) return F + OMEGA * (t - T.ding2);               // stops at the front on the second ding
    return F;
  }
  // ---- the rice (drawn as a section): how hot the outer layer is, how big the cold middle is, a one-sided heating
  function rim(t) {
    if (t < T.ding1) return 0.55 + 0.45 * ramp(t, 0, T.ding1);
    if (t < T.climbA) return 1;
    if (t < T.climb) return 0.85 * ramp(t, T.even, T.evenEnd);       // the missing step: a fresh bowl; even only once it turns
    if (t < T.tap2) return 0;                                        // the closing: cold again
    return ramp(t, T.waveIn + 0.2, T.ding2);
  }
  const sideHeat = (t) => (t >= T.climbA && t < T.climb ? ramp(t, T.side, T.sideEnd) * (1 - 0.6 * ramp(t, T.even, T.evenEnd)) : 0);
  const core = (t) => 0.6 - 0.48 * ramp(t, T.tip + 0.3, T.tipOut - 0.2);     // the cold middle shrinks while it rests (焖)
  // ---- the molecules (dark): one close-up, the field, the heat, the depth view
  const oneK = (t) => 1 - ramp(t, T.pullOut, T.pullOutEnd);
  const fieldK = (t) => ramp(t, T.fieldOn, T.fieldOnEnd);
  const FIELD_HZ = 1.0;                                               // slowed: flips on every beat
  const field = (t) => Math.sin(2 * Math.PI * FIELD_HZ * (t - T.fieldOn));
  const heatK = (t) => ramp(t, T.heat, T.heatEnd);
  const depthK = (t) => ramp(t, T.depth, T.depthEnd);
  const frontK = (t) => clamp01((t - T.front) / (T.frontEnd - T.front));   // the microwave's front, crossing the rice (linear)
  const spotsK = (t) => (t >= T.climbA && t < T.climb + 0.6 ? ramp(t, T.spots, T.spotsEnd) * (1 - ramp(t, T.climb, T.climb + 0.6)) : 0);
  // ---- what the score's hum does (0..1) — the magnetron only hums while the oven runs
  function humLevel(t) {
    if (t < T.ding1) return 1;
    if (t >= T.lightA && t < T.climb) return 0.55 * ramp(t, T.lightA, T.lightA + 0.3) * (1 - ramp(t, T.climb - 0.4, T.climb));
    if (t >= T.tap2 && t < T.ding2) return ramp(t, T.tap2, T.tap2 + 0.1);
    return 0;
  }

  // sound cues derived from the same times (score.mjs reads this; beatcheck.mjs checks them on the measured grid)
  const HITS = {
    ding: [T.ding1, T.ding2], underline: [T.underline], myth: [T.myth], strike: [T.strike, T.strike + 0.125], a2: [T.a2],
    scan: [T.scan2], ring: [T.ring], xray: [T.scan3], q4: [T.q4], pulse: [T.pulse], dive: [T.dive2],
    field: [T.fieldOn], push: [T.push], heat: [T.a5], depth: [T.front + 0.104], name: [T.name], q7: [T.q7], spots: [T.spots], spin: [T.spin],
    q9: [T.q9], tap: [T.tap2], waveIn: [T.waveIn], fin: [T.fin], tip: [T.tip], endType: [T.title1], ep: [T.ep], sting: [T.sting],
  };

  const TL = { BPM, BEAT, BAR, FPS, DUR, W, H, T, COPY, HITS, OMEGA, running, turn, rim, sideHeat, core, oneK, fieldK, FIELD_HZ, field, heatK, depthK, frontK, spotsK, humLevel };
  if (typeof module !== "undefined" && module.exports) module.exports = TL;
  else root.TL = TL;
})(typeof window !== "undefined" ? window : globalThis);
