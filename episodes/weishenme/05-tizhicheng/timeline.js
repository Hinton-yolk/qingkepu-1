// timeline.js — the single source of truth for picture (index.html) and sound (music/score.mjs).
// EP.05 体脂秤 — 体脂秤怎么知道你有多少脂肪？ Written from the approved script (script.md, content gate 1, 2026-11-07;
// opening shortened to 2.75 s on 2026-11-09). The 「为什么系列」 detective story in one continuous space: a glass bathroom
// scale on the floor, a person standing on it (seen from the waist down), a phone lying on the floor beside it.
//   1 phenomenon          体脂秤怎么知道，你有多少脂肪？          (a bare foot steps on; weight, then 体脂率 roll up)
//   2 wrong guess, struck  你是不是以为，它只是一台秤？ ✕           (x-ray: four load cells, nothing else)
//                          脚下那几块亮片，在给你通电               (the four pads ringed; a pulse goes into the left foot)
//   3 dig in               通电？我怎么没感觉？ → 电很弱，你根本感觉不到 (the current: up the left leg, over, down the right)
//                          它通电，是想知道什么？ → one take into the calf: a cut across it (dark)
//   4 one mechanism        肌肉里水多，电好走 → 脂肪里水少，电难走 → 脂肪越多，电越难走 (the fat thickens, the meter climbs)
//                          → 所以，体脂秤其实是一台测电阻的表
//   5 the missing step     可电阻，怎么变成体脂率？ → 它还要知道你的身高、年龄、性别 (a card) → 所以第一次用，才让你先填资料
//                          (the phone on the floor) → 那为什么每次测，数都不一样？ → 喝了水、出了汗，身体里的水就变了
//                          → 电好不好走跟着变，数字也就变了
//   6 back to the start    再踩一次 → 它不是在称脂肪，是在用电算 → tip: 每天同一时间光脚测，看趋势 (+ the pacemaker note)
// 120 BPM: 1 beat = 0.5 s = 15 frames at 30 fps, 1 bar = 2 s; 52.25 s. The strike, the name and the closing step are the
// three loudest hits; the name and the closing step each come after a half-beat stop and land on a beat.
// Moved from the script (≤ 0.5 s, onto beats): the name 21.25 → 21.0, the closing line 40.75 → 41.0.
(function (root) {
  const BPM = 120, BEAT = 60 / BPM, BAR = 4 * BEAT, FPS = 30, DUR = 52.25;
  const W = 1080, H = 1920;

  const T = {
    // 0–2.75 · 1 the phenomenon: the right foot comes down onto the glass, the display wakes, weight, then 体脂率
    landR: 0.5, wake: 0.5, magIn: 0.5, rollW: 0.625, lockW: 1.25, underline: 1.5, bfOn: 1.5, lockF: 2.0, h1Out: 2.59,
    // 2.75–7.5 · 2 the wrong guess (orange): x-ray — four load cells, "just a scale"; struck; the pads; a pulse into the foot
    myth: 2.75, q2: 2.75, xray: 2.85, scan: 3.0, scanEnd: 3.75, hush: 4.5, strike: 5.0, a2: 5.25,
    ring0: 5.375, pulse: 6.25, pulseEnd: 7.25,
    // 7.5–9.25 · 3 dig in: close on the left foot — it feels nothing
    unOrange: 7.5, q3: 7.5, close: 7.5, closeEnd: 8.4,
    // 9.25–11.75 · the current: out to the whole lower body (front), the line goes up, over and down
    a3: 9.25, pullB: 9.25, pullBEnd: 10.25, line: 10.25, lineEnd: 11.25,
    // 11.75–14.25 · one take into the calf: push in, a cut across the calf, dark, tilt to look at the cut
    q4: 11.75, dive: 11.75, cut: 12.5, cutEnd: 12.85, flood: 12.75, floodEnd: 13.0, tilt: 12.85, tiltEnd: 13.75, labels: 13.75,
    // 14.25–24 · 4 the one mechanism: muscle (water, easy), fat (dry, hard), more fat (the meter climbs) → the name
    a4: 14.25, dropsM: 14.5, a5: 16.5, dropF: 16.75, a6: 18.75, thick: 19.0, thickEnd: 20.25, meter: 19.0,
    stop1: 20.75, name: 21.0,
    // 24–39.75 · 5 the missing step: out again; a card; the phone on the floor (form, then the history); the water
    q5: 24.0, out: 24.0, outEnd: 25.25, unflood: 24.7,
    a7: 26.25, chip0: 26.25, arrow: 27.5, result: 27.75, tag: 28.0,
    a8: 29.25, pan: 29.25, panEnd: 30.25, fly: 29.5, flyEnd: 30.25, fill1: 30.5, fill2: 31.0, fill3: 31.5,
    q6: 32.25, chart: 32.25, pts: 32.5, diff: 33.75,
    a9: 34.75, back: 34.75, backEnd: 35.5, magC: 35.0, drink: 35.5, drinkEnd: 35.9, sweat: 36.25, sweatEnd: 36.75,
    a10: 37.0, magCOut: 37.0, magD: 37.25, jump1: 37.75, jump2: 38.25, jump3: 38.75, jump4: 39.25,
    // 39.75–49.25 · 6 back to the phenomenon: step on again; the closing step; a small tip on the phone's history
    q9: 39.75, magDOut: 39.75, lift: 39.75, liftEnd: 40.25, drop: 40.45, stop2: 40.75, ka: 41.0, fin: 41.0,
    magF: 41.25, calc: 41.25, calcEnd: 42.0,
    finOut: 44.0, tip: 44.0, pan2: 44.0, pan2End: 44.9, trend: 45.0, trendEnd: 46.5, pace: 45.5, tipOut: 49.1,
    // 49.25–52.25 end card
    end: 49.25, endMorph: 49.85, title1: 49.5, ep: 50.0, sting: 50.5,
  };

  const COPY = {
    h1: ["体脂秤怎么知道，", "你有多少[脂肪]？"],
    q2: ["你是不是以为，", "它只是一台[秤]？"],
    a2: ["脚下那几块亮片，", "在给你[通电]"],
    q3: ["通电？", "我怎么[没感觉]？"],
    a3: ["电很弱，", "你根本[感觉不到]"],
    q4: ["它通电，", "是想[知道]什么？"],
    a4: ["肌肉里水多，", "电[好走]"],
    a5: ["脂肪里水少，", "电[难走]"],
    a6: ["脂肪越多，", "电越[难]走"],
    name: ["所以，体脂秤其实是", "一台测[电阻]的表"],
    q5: ["可电阻，怎么变成", "[体脂率]？"],
    a7: ["它还要知道你的", "[身高、年龄、性别]"],
    a8: ["所以第一次用，", "才让你先[填资料]"],
    q6: ["那为什么每次测，", "数都[不一样]？"],
    a9: ["喝了水、出了汗，", "身体里的[水]就变了"],
    a10: ["电好不好走跟着变，", "数字也就[变]了"],
    q9: ["再踩一次"],
    fin: ["它不是在[称]脂肪，", "是在用电[算]"],
    tipTag: "小提示：", tip: ["每天同一时间", "光脚测，看[趋势]"],
    pace: "装心脏起搏器的人，别用体脂功能",
    // labels in the picture
    fat: "脂肪", muscle: "肌肉",
    // the card (a7): what the estimate needs
    cR: "电阻", cH: "身高", cW: "体重", cA: "年龄", cS: "性别", cOut: "体脂率", cEst: "估算",
    // the display and the generic app (no brand)
    bfLabel: "体脂率", kg: "kg", pct: "%",
    form: "个人资料", fH: "身高", fA: "年龄", fS: "性别", male: "男", female: "女", done: "完成",
    hist: "体脂率", morning: "早", evening: "晚",
    end: ["你每天都在用，", "但你不知道", "它[怎么工作]"], epNum: "EP.05", epName: "体脂秤",
  };
  // the readings (the only numbers in the film besides EP.05: the weight, and the body-fat % which changes value)
  const WEIGHT = 58.6, BF = 22.4, BF_JUMPS = [21.6, 23.1, 22.0, 22.7];

  const clamp01 = (x) => Math.max(0, Math.min(1, x));
  const sm = (x) => x * x * (3 - 2 * x);
  const ramp = (t, a, b) => sm(clamp01((t - a) / (b - a)));
  const S16 = BEAT / 4;

  // ---- how much fat is in the calf section: 1 = as found, rising to 2.2 on 「脂肪越多」, back to 1 after the name
  function fatK(t) { return 1 + 1.2 * ramp(t, T.thick, T.thickEnd) * (1 - ramp(t, T.q5, T.q5 + 1.0)); }
  // ---- how much water (number of droplets in the muscle) in the water beat: 4 → 7 (drink) → 2 (sweat)
  function waterN(t) { if (t < T.drink) return 4; if (t < T.sweat) return 4 + 3 * ramp(t, T.drink, T.drinkEnd); return 7 - 5 * ramp(t, T.sweat, T.sweatEnd); }

  // sound cues derived from the same times (score.mjs reads this; beatcheck.mjs checks them on the measured grid)
  const RINGS = [0, 1, 2, 3].map((i) => T.ring0 + i * S16);
  const CHIPS = [0, 1, 2, 3, 4].map((i) => T.chip0 + i * 0.25);
  const PTS = [0, 1, 2, 3, 4, 5, 6, 7].map((i) => T.pts + i * S16);
  const HITS = {
    landR: [T.landR], wake: [T.wake], rollW: [T.rollW], lockW: [T.lockW], underline: [T.underline], bfOn: [T.bfOn], lockF: [T.lockF],
    myth: [T.myth], q2: [T.q2], scan: [T.scan], hush: [T.hush], strike: [T.strike, T.strike + 0.125], a2: [T.a2], rings: RINGS, pulse: [T.pulse],
    q3: [T.q3], close: [T.close], a3: [T.a3], pullB: [T.pullB], line: [T.line],
    q4: [T.q4], dive: [T.dive], cut: [T.cut], flood: [T.flood], labels: [T.labels],
    a4: [T.a4], dropsM: [0, 1, 2, 3].map((i) => T.dropsM + i * S16), a5: [T.a5], dropF: [T.dropF], a6: [T.a6], thick: [T.thick],
    stop1: [T.stop1], name: [T.name],
    q5: [T.q5], out: [T.out], a7: [T.a7], chips: CHIPS, arrow: [T.arrow], result: [T.result], tag: [T.tag],
    a8: [T.a8], pan: [T.pan], fly: [T.fly], fill: [T.fill1, T.fill2, T.fill3],
    q6: [T.q6], pts: PTS, diff: [T.diff],
    a9: [T.a9], magC: [T.magC], drink: [0, 1, 2].map((i) => T.drink + i * S16), sweat: [0, 1, 2, 3, 4].map((i) => T.sweat + i * S16),
    a10: [T.a10], magD: [T.magD], jumps: [T.jump1, T.jump2, T.jump3, T.jump4],
    q9: [T.q9], lift: [T.lift], stop2: [T.stop2], ka: [T.ka], calc: [T.calc], calcEnd: [T.calcEnd],
    tip: [T.tip], trend: [T.trend], pace: [T.pace],
    endType: [T.title1], ep: [T.ep], sting: [T.sting],
  };

  const TL = { BPM, BEAT, BAR, FPS, DUR, W, H, T, COPY, HITS, S16, WEIGHT, BF, BF_JUMPS, fatK, waterN, ramp, RINGS, CHIPS, PTS };
  if (typeof module !== "undefined" && module.exports) module.exports = TL;
  else root.TL = TL;
})(typeof window !== "undefined" ? window : globalThis);
