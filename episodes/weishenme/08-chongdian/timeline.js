// timeline.js — the single source of truth for picture (index.html) and sound (music/score.mjs).
// EP.08 充电 — 手机天天充，会充坏电池吗？ script v4 (script.md 「逐句脚本 v4」, user 11-16: 「确认定稿」).
//   0      手机天天充，会充坏电池吗？        (a hand plugs the cable in, ⚡37% → 38%; unplug, plug again)
//   2.75   你是不是以为，充一次，就少一次命？  (orange; a row of little batteries, one struck per plug-in; 5.0 ✕)
//   5.25   它不数你插了几次                   (quick plug / unplug: no battery is struck any more)
//   7.25   那它数的是什么？                   (one take in: the phone → the battery → between two electrode sheets, dark)
//   10.5–24.25 lithium moves: 去哪？ 用电呢？ 用掉一整条电量才算一次；两次各用一半 → 还是一次
//   24.25–38.5 ageing: the SEI film thickens, some lithium is stuck, it never comes back; the capacity shrinks;
//                 什么时候老得更快？ 又满又热 (side by side)
//   38.5–49.75 night: it holds at 80%, fills before you wake; a phone without the feature: full, no more current; a limit
//   49.75  想充就充，别让它又满又热          (back to the first shot)
//   52.75  小提示 (gaming while charging in a thick case: the thermometer; pause, case off, it cools)
//   55.75  end card
// 120 BPM: 1 beat = 0.5 s = 15 frames at 30 fps, 1 bar = 2 s.
(function (root) {
  const BPM = 120, BEAT = 60 / BPM, BAR = 4 * BEAT, FPS = 30, DUR = 59.5;
  const W = 1080, H = 1920;

  const T = {
    // 0–2.75 · the phenomenon: plug in, 37% → 38%; unplug, plug again
    plug1: 0.25, pct: 0.5, tick38: 1.25, underline: 1.5, unplug1: 1.75, plug2: 2.25,
    // 2.75–7.25 · the wrong guess (orange), struck; the flip
    q2: 2.75, myth: 2.75, row: 3.0, unplug2: 3.25, plug3: 3.5, unplug3: 4.0, plug4: 4.25, hush: 4.5, strike: 5.0,
    a2: 5.25, unOrange: 5.25, fast: 5.5, fastEnd: 7.0,
    // 7.25–10.5 · one take in
    q3: 7.25, dive: 7.25, xray: 7.6, cells: 8.35, diveEnd: 10.25,
    // 10.5–24.25 · lithium moves
    h1: 10.5, spot: 10.75, tagCath: 11.9, tagAnode: 12.3,
    q4: 13.0, barOn: 13.25, chg1: 13.55, chg1End: 15.0,
    q5: 15.5, dis1: 15.75, dis1End: 17.25,
    a6: 17.75, ringOn: 17.85, chgR: 18.3, chgREnd: 18.75, disR: 18.85, disREnd: 19.85,
    q7: 20.0, clear: 20.0, chgH: 20.25, chgHEnd: 20.75,
    a7: 21.5, half1: 21.75, half1End: 22.5, back1: 22.55, back1End: 22.95, half2: 23.0, half2End: 23.7, term: 23.25,
    // 24.25–38.5 · ageing
    q8: 24.25, chgA: 24.35, chgAEnd: 25.0, zoomA: 24.25, zoomAEnd: 25.5, film: 25.25,
    a8: 26.5, thick: 26.6, thickEnd: 27.5, stick: 27.75, stickEnd: 28.6,
    q9: 29.5, dis9: 29.75, dis9End: 31.55,
    a10: 31.75, zoomOut: 30.0, zoomOutEnd: 30.8, chgS: 32.45, chgSEnd: 32.95, shrink: 33.0, shrinkEnd: 33.6,   // pull back while they go home (the stuck ones are seen staying); fill it up again, then the outline shrinks
    q11: 34.0, split: 34.25, splitEnd: 35.0,
    a12: 36.0, cmpL: 36.15, cmpR: 36.9, full: 36.9, fullEnd: 37.4, heat: 37.45, heatEnd: 38.25,
    // 38.5–49.75 · night
    q13: 38.5, pull: 38.5, pullEnd: 39.9,
    a13: 40.75, hold80: 41.25, dawn: 42.0, fill100: 42.35, fill100End: 42.75, grab: 42.6, liftEnd: 43.2,
    q14: 43.25, phone2: 43.25, phone2End: 43.7,   // a whip pan to another bedside (another phone, still night)
    a14: 45.0, flowStop: 45.5,
    a15: 47.5, toggle: 47.6, toggleEnd: 47.85, limit: 47.95, limitEnd: 48.45,   // the next charge: up from low, it stops at 80% (held ≥ 1 s before the circle reaches it)
    // 49.75–52.75 · back to the first shot
    stop2: 49.25, fin: 49.75, irisOut: 49.25, irisOutEnd: 49.85, plugF: 50.35, ka: 50.5,   // the circle opens in the half-beat stop: the closing line lands on light
    // 52.75–55.75 · the tip
    tip: 52.75, tipIn: 52.75, tipInEnd: 53.25, hot: 53.25, hotEnd: 53.9, pause: 54.0, caseOff: 54.4, caseOffEnd: 54.9, cool: 54.9, coolEnd: 55.6,
    // 55.75–59.5 · end card
    end: 55.75, endMorph: 56.35, title1: 56.5, ep: 57.25, sting: 57.75,
  };

  const COPY = {
    h1: ["手机天天充，", "会[充坏]电池吗？"],
    q2: ["你是不是以为，", "充一次，就[少一次]命？"],
    a2: ["它不数你[插了几次]"],
    q3: ["那它数的是[什么]？"],
    h4: ["电池里，有一群", "会搬家的[锂]"],
    q4: ["充电时，", "它们去[哪]？"],
    q5: ["那用电[呢]？"],
    a6: ["用掉[一整条]电量，", "才算一次"],
    q7: ["两次，各用[一半]呢？"],
    a7: ["加起来，", "还是[一次]"],
    q8: ["那电池，", "到底是[怎么老]的？"],
    a8: ["锂挤在这一边时，", "总有一些被[粘]住"],
    q9: ["被粘住的锂，", "还能[搬回去]吗？"],
    a10: ["就这样一点点老，", "电池就[不耐用]了"],
    q11: ["什么时候，", "老得[更快]？"],
    a12: ["又[满]，", "又[热]的时候"],
    q13: ["那夜里插着", "充[一整晚]呢？"],
    a13: ["不少手机会", "先停在[80%]"],
    q14: ["手机没有", "这个[功能]呢？"],
    a14: ["充满就不再", "往里充了，", "只是[一直满]着"],   // 3 lines at 96 px (SERIES.md: too long → 3 lines)
    a15: ["有的手机，", "还能在设置里", "限到[80%]"],
    fin: ["想充就充，", "别让它[又满又热]"],
    tipTag: "小提示：", tip: ["边充边打游戏、", "闷着充，", "最容易[发烫]"],
    // small text (terms and notes only as small text)
    cath: "正极", anode: "负极 · 石墨", bar: "现在的电量", ring: "循环", term: "这叫一次充电循环", sei: "SEI 膜", note: "示意",
    cmpL: "不满、不热", cmpR: "满 + 热", hot: "热", opt: "优化电池充电 · 学会你的作息后", dawn: "快起床时再充满",
    limit: "充电上限", pause: "暂停", next: "下一次充电",
    used: "累计用掉的电", half1: "第一次用掉一半", half2: "第二次用掉一半", elec: "电子", stuck: "被粘住，搬不回去", less: "满格也少一截",
    night: "夜里", wake: "起床", faster: "膜长得更快", full: "一直满着", stopped: "充满后不再往里充", gap: "空出来的位置", optTag: "起床前充满", limTag: "一直停在 80%，不再充满", li: "锂",
    end: ["你每天都在用，", "但你不知道", "它[怎么工作]"], epNum: "EP.08", epName: "充电",
  };
  const S16 = BEAT / 4;

  // the plug-ins of the opening and the guess (picture: the plug goes home; sound: a click)
  const PLUGS = [T.plug1, T.plug2, T.plug3, T.plug4];
  const UNPLUGS = [T.unplug1, T.unplug2, T.unplug3];
  // the quick plug / unplug after the flip: on every beat from T.fast to T.fastEnd (in on the beat, out half a beat later)
  const FAST = []; for (let t = T.fast; t < T.fastEnd - 0.01; t += BEAT) FAST.push(+t.toFixed(3));

  const HITS = {
    plug: PLUGS, unplug: UNPLUGS, pct: [T.pct], tick38: [T.tick38], underline: [T.underline],
    myth: [T.myth], row: [T.row], strike: [T.strike], a2: [T.a2], fast: FAST,
    q3: [T.q3], xray: [T.xray], cells: [T.cells], h1: [T.h1], spot: [T.spot],
    q4: [T.q4], barOn: [T.barOn], chg1: [T.chg1], q5: [T.q5], dis1: [T.dis1],
    a6: [T.a6], ringOn: [T.ringOn], ka1: [T.disREnd], q7: [T.q7], a7: [T.a7], ka2: [T.half2End],
    q8: [T.q8], film: [T.film], a8: [T.a8], stick: [T.stick], q9: [T.q9], a10: [T.a10], shrink: [T.shrink],
    q11: [T.q11], a12: [T.a12], heat: [T.heat],
    q13: [T.q13], a13: [T.a13], hold80: [T.hold80], fill100: [T.fill100End], q14: [T.q14], a14: [T.a14], flowStop: [T.flowStop],
    a15: [T.a15], toggle: [T.toggle], fin: [T.fin], ka: [T.ka],
    tip: [T.tip], pause: [T.pause], caseOff: [T.caseOff],
    endType: [T.title1], ep: [T.ep], sting: [T.sting],
  };

  const TL = { BPM, BEAT, BAR, FPS, DUR, W, H, T, COPY, HITS, S16, PLUGS, UNPLUGS, FAST };
  if (typeof module !== "undefined" && module.exports) module.exports = TL;
  else root.TL = TL;
})(typeof window !== "undefined" ? window : globalThis);
