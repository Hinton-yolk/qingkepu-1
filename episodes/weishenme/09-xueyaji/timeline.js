// timeline.js — the single source of truth for picture (index.html) and sound (music/score.mjs).
// EP.09 血压计 — 血压每次量的都不一样，该信哪一次？ script v2.1 (script.md, user 11-18: 「确认脚本，字幕改动都同意」).
//   0      血压每次量的都不一样，该信哪一次？  (the arm on a table, a cuff; 138, then — measured again — 126)
//   2.75   你是不是以为，是血压计量错了？      (orange; 5.0 ✕)
//   5.25   很多时候，它没错
//   6.75   先看看，它是怎么量的                 (one take in: the cuff → a side cut through the arm, dark)
//   9.5–28.75  the mechanism: air in the cuff; squeeze; deflate (the sensor); a beat squeezes through; 顶; the hill; 算出来
//   31.5–46    why each time differs: one half-minute window on a line that keeps moving; the first is often higher;
//              the arm's height (below the heart: higher; above: lower)
//   46     该信哪一次？一次都别单信。 (back to the first shot)
//   48–56.25   the tips (a checklist card builds up)
//   56.25  end card
// 120 BPM: 1 beat = 0.5 s = 15 frames at 30 fps, 1 bar = 2 s.
(function (root) {
  const BPM = 120, BEAT = 60 / BPM, BAR = 4 * BEAT, FPS = 30, DUR = 59.75;
  const W = 1080, H = 1920;

  const T = {
    // 0–2.75 · two readings
    r1: 0.25, inflate2: 0.5, underline: 1.5, r2: 2.0,
    // 2.75–6.75 · the wrong guess (orange), struck; the flip
    q2: 2.75, myth: 2.75, qmarks: 3.25, hush: 4.5, strike: 5.0, a2: 5.25, unOrange: 5.25,
    // 6.75–9.5 · one take in
    q3: 6.75, dive: 6.75, xray: 7.25, diveEnd: 9.5,
    // 9.5–28.75 · the mechanism
    air: 9.5, stetho: 9.6,
    squeeze: 12.0, squeezeEnd: 13.25, stop: 12.9,
    deflate: 14.0, sensor: 14.0, sensorEnd: 14.75, release: 14.75,
    beat1: 16.0,
    q5: 18.25, panDown: 18.25,
    push: 20.0,
    more: 22.0,
    less: 24.25, hill: 24.9,
    q6: 26.75, big: 26.75, bigEnd: 27.5, peak: 27.75,
    a6: 28.75, mkHi: 28.9, mkLo: 29.2, hold: 29.5,
    // 31.5–46 · why each time differs
    q7: 31.5, line: 31.5, a7: 33.5, win1: 34.5,
    a8: 35.25, a9: 37.25, sat: 37.4, win2: 37.9,
    q10: 39.5, side: 39.5, sideIn: 40.0,
    a10: 41.5, lower: 41.5, col: 42.25, up: 42.9,
    a11: 44.0, raise: 44.0, gapC: 44.75, down: 45.4,
    // 46–48 · back to the first shot
    fin: 46.0, iris: 45.75, irisEnd: 46.25, avg: 46.75,
    // 48–56.25 · the tips
    tip1: 48.0, timer: 48.2, timerEnd: 49.4, align: 49.4, card1: 50.0,
    tip2: 50.5, m1: 50.6, m1End: 51.2, wait: 51.25, m2: 51.75, m2End: 52.25, card2: 52.4,
    tip3: 52.75, week: 52.9, weekEnd: 53.9, wline: 54.0, card3: 54.6, cardHold: 55.25,
    // 56.25–59.75 · end card
    end: 56.25, endMorph: 56.85, title1: 57.0, ep: 57.75, sting: 58.25,
  };

  // the heart beats during the measurement (picture: a squeeze-through, a spike; sound: a soft thump)
  const BEATS = []; for (let t = T.beat1; t < 26.6; t += 0.8) BEATS.push(+t.toFixed(3));

  const COPY = {
    h1: ["血压每次量的", "都不一样，", "该信[哪一次]？"],
    q2: ["你是不是以为，", "是血压计[量错]了？"],
    a2: ["很多时候，", "它没[错]"],
    q3: ["先看看，", "它是怎么[量]的"],
    h4: ["它没有听诊器，", "靠袖带里的[空气]"],
    a4: ["袖带鼓起来，", "把血管[压扁]"],
    a5: ["然后，", "一点一点[放气]"],
    b5: ["心脏一跳，", "血就[挤过去]一下"],
    q5: ["这一下，", "机器怎么[知道]？"],
    a5b: ["血管一鼓，", "把袖带[顶]一下"],
    m5: ["越往下放气，", "顶得越[厉害]"],
    l5: ["过了最厉害那一下，", "又越来越[弱]"],
    q6: ["那高压低压，", "从哪[来]？"],
    a6: ["高压和低压，", "是[算]出来的"],
    q7: ["那为什么，", "每次都[不一样]？"],
    a7: ["它只量了", "那[半分钟]"],
    a8: ["可你的血压，", "一直在[变]"],
    a9: ["刚坐下、一紧张，", "第一次往往[偏高]"],
    q10: ["还有，胳膊", "放得多[高]？"],
    a10: ["胳膊比心脏低，", "读数就[偏高]"],
    a11: ["抬得比心脏高，", "又会[偏低]"],
    fin: ["该信哪一次？", "一次都别[单信]。"],
    t1: ["坐好歇[5分钟]，", "胳膊和心脏[一样高]"],
    t2: ["隔一分钟再量，", "两次[取平均]"],
    t3: ["每天早晚各量，", "看一周的[平均]"],
    // small text (terms and notes only as small text)
    again: "隔一会儿，再量一次", first: "第一次", second: "第二次", note: "示意",
    air: "空气", artery: "动脉", bone: "骨头", noflow: "血过不去", sensor: "压力传感器", cuffP: "袖带的压力",
    hi: "高压", lo: "低压", rule: "从“顶”由弱到强、再变弱算出来 · 这叫示波法", algo: "示意 · 各家算法不同",
    bp: "你的血压", one: "一次测量", sat: "刚坐下", heart: "心脏的高度", more: "多压一截", less: "少压一截",
    up: "读数 ↑", down: "读数 ↓", avg: "取平均", pad: "桌子低就垫高", gap: "隔一分钟", week: "一周的平均", am: "早", pm: "晚",
    c1: "歇 5 分钟 · 胳膊和心脏一样高", c1b: "（桌子低就垫高）", c2: "隔一分钟，量两次，取平均", c3: "早晚各量，看一周的平均",
    end: ["你每天都在用，", "但你不知道", "它[怎么工作]"], epNum: "EP.09", epName: "血压计",
  };
  const S16 = BEAT / 4;

  const HITS = {
    r1: [T.r1], inflate2: [T.inflate2], underline: [T.underline], r2: [T.r2],
    myth: [T.myth], qmarks: [T.qmarks], strike: [T.strike], a2: [T.a2],
    dive: [T.dive], air: [T.air], squeeze: [T.squeeze], sensor: [T.sensor], release: [T.release],
    beats: BEATS, q5: [T.q5], push: [T.push], hill: [T.hill],
    q6: [T.q6], a6: [T.a6], mk: [T.mkHi, T.mkLo],
    q7: [T.q7], a7: [T.a7], win: [T.win1, T.win2], q10: [T.q10], col: [T.col], gapC: [T.gapC],
    fin: [T.fin], avg: [T.avg], tip: [T.tip1, T.tip2, T.tip3], cuffs: [T.m1, T.m2], card: [T.card1, T.card2, T.card3],
    endType: [T.title1], ep: [T.ep], sting: [T.sting],
  };

  const TL = { BPM, BEAT, BAR, FPS, DUR, W, H, T, COPY, HITS, S16, BEATS };
  if (typeof module !== "undefined" && module.exports) module.exports = TL;
  else root.TL = TL;
})(typeof window !== "undefined" ? window : globalThis);
