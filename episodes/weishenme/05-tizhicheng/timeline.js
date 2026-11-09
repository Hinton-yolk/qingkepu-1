// timeline.js — the single source of truth for picture (index.html) and sound (music/score.mjs).
// EP.05 体脂秤 — 体脂秤怎么知道你有多少脂肪？ Written from the approved script (script.md, content gate 1, 2026-11-07;
// opening shortened to 2.75 s on 2026-11-09). The 「为什么系列」 detective story in one continuous space: a glass bathroom
// scale on the floor, a person standing on it (seen from the waist down), a phone lying on the floor beside it.
//   1 phenomenon          体脂秤怎么知道，你有多少脂肪？          (a bare foot steps on; weight, then 体脂率 roll up)
//   2 wrong guess, struck  你是不是以为，脚下这几块亮片只是装饰？ ✕  (the four pads glint like trim)
//                          其实，它们正在给你通电                   (the four pads ringed; a pulse goes into the left foot)
//   3 dig in               通电？我怎么没感觉？ → 电很弱，你根本感觉不到 (the current: up the left leg, over, down the right)
//                          它通电，是想知道什么？ (ride one pulse round) → 它在测：电穿过你，有多难走 (a big dial: the principle)
//   4 one mechanism        可电难不难走，跟脂肪有什么关系？ → one take into the calf: a cut across it (dark)
//                          肌肉里水多，电好走 | 脂肪里水少，电难走 (two samples pulled out of the cut, each with its own meter)
//                          所以电越难走，脂肪就越多 (two calves, thin and thick fat) → 所以，体脂秤其实是一台测电阻的表
//   5 the missing step     可电阻，怎么变成体脂率？ → 它还要知道你的身高、年龄、性别 (a card) → 所以第一次用，才让你先填资料
//                          (the phone on the floor) → 那为什么每次测，数都不一样？ → 喝了水、出了汗，身体里的水就变了
//                          → 电好不好走跟着变，数字也就变了
//   6 back to the start    再踩一次 → 它不是在称脂肪，是在用电算 → tip: 每天同一时间光脚测，看趋势 (+ the pacemaker note)
// 120 BPM: 1 beat = 0.5 s = 15 frames at 30 fps, 1 bar = 2 s; 56.25 s. The strike, the name and the closing step are the
// three loudest hits; the name and the closing step each come after a half-beat stop and land on a beat.
// v2 (2026-11-09): the first half re-cut per script.md 「前半段改稿 v2」; the second half is the first cut moved 4.0 s (2 bars)
// later, so its cues keep their beats (the script table says 27.75 for 可电阻…; it lands at 28.0).
(function (root) {
  const BPM = 120, BEAT = 60 / BPM, BAR = 4 * BEAT, FPS = 30, DUR = 56.25;
  const W = 1080, H = 1920;

  const T = {
    // 0–2.75 · 1 the phenomenon: the right foot comes down onto the glass, the display wakes, weight, then 体脂率
    landR: 0.5, wake: 0.5, magIn: 0.5, rollW: 0.625, lockW: 1.25, underline: 1.5, bfOn: 1.5, lockF: 2.0, h1Out: 2.59,
    // 2.75–7.5 · 2 the wrong guess (orange): the four shiny pads, glinting like trim — "just decoration?"; struck; they carry a current
    myth: 2.75, q2: 2.75, xray: 2.85, glint: 3.0, hush: 4.5, strike: 5.0, a2: 5.25, ring0: 5.375, pulse: 6.25, pulseEnd: 7.25,
    // 7.5–9.25 · close on the left foot — it feels nothing
    unOrange: 7.5, q3: 7.5, close: 7.5, closeEnd: 8.4,
    // 9.25–11.75 · the current: out to the whole lower body (front), the line goes up, over and down
    a3: 9.25, pullB: 9.25, pullBEnd: 10.25, line: 10.25, lineEnd: 11.25,
    // 11.75–16.25 · what is it measuring? the camera rides one pulse round the loop; then the principle: a big dial beside the body
    q4: 11.75, follow: 11.75, followEnd: 13.5, pr: 13.75, prWide: 13.5, prWideEnd: 14.25, dial: 13.75, swing: 14.25, swingEnd: 15.0,
    // 16.25–18.5 · and fat? one take into the calf: push in, a cut across, dark, tilt to look at the cut; 脂肪 / 肌肉
    fq: 16.25, dive: 16.25, cut: 16.5, cutEnd: 16.85, flood: 16.75, floodEnd: 17.0, tilt: 16.85, tiltEnd: 17.5, labels: 17.25,
    // 18.5–25 · the comparison: two samples out of the cut — muscle (easy), fat (hard); then two calves, thin and thick fat → the name
    a4: 18.5, blocks: 17.75, blocksEnd: 18.25, dropsM: 18.5, a5: 20.5, fatGo: 20.5, a6: 22.5, twin: 22.5, twinEnd: 23.1, thick: 23.25, thickEnd: 24.25,
    stop1: 24.75, name: 25.0,
    // 28–43.75 · 5 the missing step (everything from here on is the first cut, 4.0 s = 2 bars later)
    q5: 28.0, out: 28.0, outEnd: 29.25, unflood: 28.7,
    a7: 30.25, chip0: 30.25, arrow: 31.5, result: 31.75, tag: 32.0,
    a8: 33.25, pan: 33.25, panEnd: 34.25, fly: 33.5, flyEnd: 34.25, fill1: 34.5, fill2: 35.0, fill3: 35.5,
    q6: 36.25, chart: 36.25, pts: 36.5, diff: 37.75,
    a9: 38.75, back: 38.75, backEnd: 39.5, magC: 39.0, drink: 39.5, drinkEnd: 39.9, sweat: 40.25, sweatEnd: 40.75,
    a10: 41.0, magCOut: 41.0, magD: 41.25, jump1: 41.75, jump2: 42.25, jump3: 42.75, jump4: 43.25,
    // 43.75–53.25 · 6 back to the phenomenon: step on again; the closing step; a small tip on the phone's history
    q9: 43.75, magDOut: 43.75, lift: 43.75, liftEnd: 44.25, drop: 44.45, stop2: 44.75, ka: 45.0, fin: 45.0,
    magF: 45.25, calc: 45.25, calcEnd: 46.0,
    finOut: 48.0, tip: 48.0, pan2: 48.0, pan2End: 48.9, trend: 49.0, trendEnd: 50.5, pace: 49.5, tipOut: 53.1,
    // 53.25–56.25 end card
    end: 53.25, endMorph: 53.85, title1: 53.5, ep: 54.0, sting: 54.5,
  };

  const COPY = {
    h1: ["体脂秤怎么知道，", "你有多少[脂肪]？"],
    q2: ["你是不是以为，", "脚下这几块", "亮片只是[装饰]？"],          // script: 「你是不是以为，脚下这几块」/「亮片只是[装饰]？」 — three lines at 96 px (the series rule)
    a2: ["其实，它们正在", "给你[通电]"],
    q3: ["通电？", "我怎么[没感觉]？"],
    a3: ["电很弱，", "你根本[感觉不到]"],
    q4: ["它通电，", "是想[知道]什么？"],
    pr: ["它在测：电穿过你，", "有多[难走]"],
    fq: ["可电难不难走，", "跟[脂肪]有什么关系？"],
    a4: ["肌肉里水多，", "电[好走]"],
    a5: ["脂肪里水少，", "电[难走]"],
    a6: ["所以电越难走，", "脂肪就越[多]"],
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
    fat: "脂肪", muscle: "肌肉", ohm: "电阻", fatLow: "脂肪少", fatHigh: "脂肪多",
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
  function fatK(t) { return 1 + 1.2 * ramp(t, T.thick, T.thickEnd); }            // the right-hand calf of the pair
  // ---- how much water (number of droplets in the muscle) in the water beat: 4 → 7 (drink) → 2 (sweat)
  function waterN(t) { if (t < T.drink) return 4; if (t < T.sweat) return 4 + 3 * ramp(t, T.drink, T.drinkEnd); return 7 - 5 * ramp(t, T.sweat, T.sweatEnd); }

  // sound cues derived from the same times (score.mjs reads this; beatcheck.mjs checks them on the measured grid)
  const RINGS = [0, 1, 2, 3].map((i) => T.ring0 + i * S16);
  const CHIPS = [0, 1, 2, 3, 4].map((i) => T.chip0 + i * 0.25);
  const PTS = [0, 1, 2, 3, 4, 5, 6, 7].map((i) => T.pts + i * S16);
  const HITS = {
    landR: [T.landR], wake: [T.wake], rollW: [T.rollW], lockW: [T.lockW], underline: [T.underline], bfOn: [T.bfOn], lockF: [T.lockF],
    myth: [T.myth], q2: [T.q2], glint: [0, 1, 2, 3].map((i) => T.glint + i * 0.25), hush: [T.hush], strike: [T.strike, T.strike + 0.125], a2: [T.a2], rings: RINGS, pulse: [T.pulse],
    q3: [T.q3], close: [T.close], a3: [T.a3], pullB: [T.pullB], line: [T.line],
    q4: [T.q4], follow: [T.follow], pr: [T.pr], dial: [T.dial], swing: [T.swing],
    fq: [T.fq], dive: [T.dive], cut: [T.cut], flood: [T.flood], labels: [T.labels],
    a4: [T.a4], blocks: [T.blocks], dropsM: [0, 1, 2, 3, 4, 5].map((i) => T.dropsM + i * S16), a5: [T.a5], fatSteps: [0, 1, 2, 3, 4, 5, 6].map((i) => T.fatGo + 0.25 + i * 0.25),
    a6: [T.a6], twin: [T.twin], thick: [T.thick], stop1: [T.stop1], name: [T.name],
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
