// timeline.js — the single source of truth for picture (index.html) and sound (music/score.mjs).
// EP.05 体脂秤 — 体脂秤怎么知道你有多少脂肪？ v3 (script.md 「改稿 v3」, 2026-11-09). One continuous space: a glass bathroom
// scale on the floor, a person standing on it (seen from the waist down), a phone lying on the floor beside it.
//   0      体脂秤怎么知道，你有多少脂肪？             (a bare foot steps on; weight, then 体脂率 roll up)
//   2.75   脚下这几块亮片，正在给你通电              (no wrong guess: the four pads ringed; a pulse goes into the left foot)
//   5–9.25 通电？我怎么没感觉？ → 电很弱，你根本感觉不到 (the current: up one leg, over, down the other)
//   9.25   它通电，是想知道什么？ → 它在测：电穿过你，有多难走 (a big dial: 好走 … 难走)
//   13.75  可电难不难走，跟脂肪有什么关系？ → into the calf → two samples (肌肉 / 脂肪) → two calves (脂肪少 / 脂肪多)
//   22.0   所以，体脂秤其实是一台测电阻的表          (the dial again, now named 电阻)
//   25.25  可为什么每次测，数都不一样？ → 水 → 数字也就变了 → 脂肪多，还是水少，它分得清吗？ → back into the calf:
//          它默认你身体里的水都是正常的 (正常含水) → 水一少，就会被算成脂肪多
//   39     还要加上你的身高、年龄、性别 (秤称 / 你填 → 估算) → 填资料 → 再踩一次 → 它不是在称脂肪，是在用电估算
//   48.75  小提示 … 看趋势 → 51.5 装了心脏起搏器的人，别用体脂功能 (its own caption beat) → 54.25 end card
// 120 BPM: 1 beat = 0.5 s = 15 frames at 30 fps, 1 bar = 2 s; 56.5 s (v3.1: 可为什么每次测 tightened to 24.5). The three loudest hits: 2.75 通电, 22.5 电阻, 45.75 the
// closing step (the last two after a half-beat stop). Every cue is on the 0.25 s grid, at the script's times.
(function (root) {
  const BPM = 120, BEAT = 60 / BPM, BAR = 4 * BEAT, FPS = 30, DUR = 56.5;
  const W = 1080, H = 1920;

  const T = {
    // 0–2.75 · the phenomenon: the right foot comes down onto the glass, the display wakes, weight, then 体脂率
    landR: 0.5, wake: 0.5, magIn: 0.5, rollW: 0.625, lockW: 1.25, underline: 1.5, bfOn: 1.5, lockF: 2, h1Out: 2.59,
    // 2.75–5 · the fact (one of the three loudest hits): the four pads are ringed; a pulse goes into the left foot
    a2: 2.75, xray: 2.75, ring0: 2.875, pulse: 3.5, pulseEnd: 4.5,
    // 5–6.75 · close on the left foot — it feels nothing
    q3: 5, close: 5, closeEnd: 5.9,
    // 6.75–9.25 · the current: out to the whole lower body (front), the line goes up, over and down
    a3: 6.75, pullB: 6.75, pullBEnd: 7.75, line: 7.75, lineEnd: 8.75,
    // 9.25–13.75 · what is it measuring? ride one pulse round the loop; the principle: a big dial (好走 … 难走)
    q4: 9.25, follow: 9.25, followEnd: 11, pr: 11.25, prWide: 11, prWideEnd: 11.75, dial: 11.25, swing: 11.75, swingEnd: 12.5,
    // 13.75–16 · and fat? one take into the calf; 脂肪 / 肌肉; the two samples come out of the cut
    fq: 13.75, dive: 13.75, cut: 14, cutEnd: 14.35, flood: 14.25, floodEnd: 14.5, tilt: 14.35, tiltEnd: 15, labels: 14.75,
    blocks: 15.25, blocksEnd: 15.75,
    // 16–25.25 · the comparison: muscle (easy), fat (hard); two calves, thin and thick fat → the name (loudest hit)
    a4: 16, dropsM: 16, a5: 18, fatGo: 18, a6: 19.75, twin: 19.75, twinEnd: 20.35, thick: 20.5, thickEnd: 21.5,
    twinLabOut: 21.5, stop1: 21.75, name: 22,
    // 25.25–32.25 · why is it different every time? out to the person on the scale: 早 / 晚; the water; the number jumps
    q6: 24.5, out: 24.5, outEnd: 25.5, unflood: 24.95, magE: 25.25, eve: 26,
    a9: 26.75, magC: 26.75, drink: 27.25, drinkEnd: 27.65, sweat: 28, sweatEnd: 28.5,
    a10: 29, magCOut: 29, magD: 29.25, jump1: 29.75, jump2: 30.25, jump3: 30.75, jump4: 31.25,
    // 32.25–39 · fat or just less water — can it tell? back into the calf: a dial with a 正常含水 mark; less water reads as more fat
    q7: 31.5, magDOut: 31.5, dive2: 31.5, cut2: 32, cut2End: 32.35, flood2: 32.25, flood2End: 32.5, tilt2: 32.35, tilt2End: 33, dial2: 33,
    n1: 34, mark: 34.25, n2: 36.25, dry: 36.25, dryEnd: 37,
    // 39–44.5 · the estimate: a card (秤称 / 你填); the phone on the floor: the form
    a7: 38.25, out2: 38.25, out2End: 39.25, unflood2: 38.7, chip0: 39, arrow: 40.25, result: 40.5, tag: 40.75,
    a8: 41, pan: 41, panEnd: 41.85, fly: 41.25, flyEnd: 41.85, fill1: 42, fill2: 42.5, fill3: 43,
    // 44.5–51.5 · back to the start: step on again; the closing step (loudest hit); the tip on the phone's history
    q9: 43.75, magDOut2: 43.75, lift: 43.75, liftEnd: 44.25, drop: 44.45, stop2: 44.75, ka: 45, fin: 45,
    magF: 45.25, calc: 45.25, calcEnd: 46,
    finOut: 48, tip: 48, chart: 48, pan2: 48, pan2End: 48.9, trend: 49, trendEnd: 50.5, tipOut: 50.6,
    // 51.5–54.25 · the safety line, its own caption beat, over the empty scale
    pace: 50.75, back3: 50.75, back3End: 51.55, paceOut: 53.35,
    // 54.25–57.25 end card (typing starts after the badge has landed)
    end: 53.5, endMorph: 54.1, title1: 54.25, ep: 55, sting: 55.5,
  };

  const COPY = {
    h1: ["体脂秤怎么知道，", "你有多少[脂肪]？"],
    a2: ["脚下这几块亮片，", "正在给你[通电]"],
    q3: ["通电？", "我怎么[没感觉]？"],
    a3: ["电很弱，", "你根本[感觉不到]"],
    q4: ["它通电，", "是想[知道]什么？"],
    pr: ["它在测：电穿过你，", "有多[难走]"],
    fq: ["可电难不难走，", "跟[脂肪]有什么关系？"],
    a4: ["肌肉里水多，", "电[好走]"],
    a5: ["脂肪里水少，", "电[难走]"],
    a6: ["所以电越难走，", "脂肪一般就越[多]"],
    name: ["所以，体脂秤其实是", "一台测[电阻]的表"],
    q6: ["可为什么每次测，", "数都[不一样]？"],
    a9: ["喝了水、出了汗，", "身体里的[水]就变了"],
    a10: ["电好不好走跟着变，", "数字也就[变]了"],
    q7: ["脂肪多，还是水少，", "它[分得清]吗？"],
    n1: ["它先按[正常含水量]", "来算"],
    n2: ["水一少，", "就会被算成[脂肪多]"],
    a7: ["还要加上你的", "[身高、年龄、性别]"],
    a8: ["所以第一次用，", "才让你先[填资料]"],
    q9: ["再踩一次"],
    fin: ["它不是在[称]脂肪，", "是在用电[估算]"],
    tipTag: "小提示：", tip: ["每天同一时间", "光脚测，看[趋势]"],
    pace: ["装了心脏起搏器的人，", "别用[体脂功能]"],
    // labels in the picture (short; technical words only as small text)
    fat: "脂肪", muscle: "肌肉", ohm: "电阻", fatLow: "脂肪少", fatHigh: "脂肪多", easy: "好走", hard: "难走", normal: "正常含水",
    am: "早", pm: "晚",
    // the card: what the estimate needs
    cR: "电阻", cH: "身高", cW: "体重", cA: "年龄", cS: "性别", cOut: "体脂率", cEst: "估算", cScale: "秤称", cYou: "你填",
    // the display and the generic app (no brand)
    bfLabel: "体脂率", kg: "kg", pct: "%",
    form: "个人资料", fH: "身高", fA: "年龄", fS: "性别", male: "男", female: "女", done: "完成",
    hist: "体脂率", morning: "早", evening: "晚",
    end: ["你每天都在用，", "但你不知道", "它[怎么工作]"], epNum: "EP.05", epName: "体脂秤",
  };
  // the readings (the only numbers in the film besides EP.05: the weight, and the body-fat % which changes value)
  const WEIGHT = 58.6, BF = 22.4, BF_EVE = 20.9, BF_JUMPS = [21.6, 23.1, 22.0, 22.7], BF_DRY = 26.8;

  const clamp01 = (x) => Math.max(0, Math.min(1, x));
  const sm = (x) => x * x * (3 - 2 * x);
  const ramp = (t, a, b) => sm(clamp01((t - a) / (b - a)));
  const S16 = BEAT / 4;

  // ---- how much fat is in the calf section: 1 = as found, rising to 2.2 on 「脂肪越多」, back to 1 after the name
  function fatK(t) { return 1; }
  // ---- how much water (number of droplets in the muscle) in the water beat: 4 → 7 (drink) → 2 (sweat)
  function waterN(t) { if (t < T.drink) return 4; if (t < T.sweat) return 4 + 3 * ramp(t, T.drink, T.drinkEnd); return 7 - 5 * ramp(t, T.sweat, T.sweatEnd); }
  function waterDry(t) { return 4 - 3 * ramp(t, T.dry, T.dryEnd); }       // the second dive: normal water, then less

  // sound cues derived from the same times (score.mjs reads this; beatcheck.mjs checks them on the measured grid)
  const RINGS = [0, 1, 2, 3].map((i) => T.ring0 + i * S16);
  const CHIPS = [0, 1, 2, 3, 4].map((i) => T.chip0 + i * 0.25);
  
  const HITS = {
    landR: [T.landR], wake: [T.wake], rollW: [T.rollW], lockW: [T.lockW], underline: [T.underline], bfOn: [T.bfOn], lockF: [T.lockF],
    a2: [T.a2], rings: RINGS, pulse: [T.pulse],
    q3: [T.q3], close: [T.close], a3: [T.a3], pullB: [T.pullB], line: [T.line],
    q4: [T.q4], follow: [T.follow], pr: [T.pr], dial: [T.dial], swing: [T.swing],
    fq: [T.fq], dive: [T.dive], cut: [T.cut], flood: [T.flood], labels: [T.labels], blocks: [T.blocks],
    a4: [T.a4], dropsM: [0, 1, 2, 3, 4, 5].map((i) => T.dropsM + i * S16), a5: [T.a5], fatSteps: [0, 1, 2, 3, 4, 5].map((i) => T.fatGo + 0.25 + i * 0.25),
    a6: [T.a6], twin: [T.twin], thick: [T.thick], stop1: [T.stop1], name: [T.name],
    q6: [T.q6], out: [T.out], magE: [T.magE], eve: [T.eve],
    a9: [T.a9], magC: [T.magC], drink: [0, 1, 2].map((i) => T.drink + i * S16), sweat: [0, 1, 2, 3, 4].map((i) => T.sweat + i * S16),
    a10: [T.a10], magD: [T.magD], jumps: [T.jump1, T.jump2, T.jump3, T.jump4],
    q7: [T.q7], dive2: [T.dive2], cut2: [T.cut2], flood2: [T.flood2], dial2: [T.dial2], n1: [T.n1], mark: [T.mark], n2: [T.n2], dryDrops: [0, 1, 2].map((i) => T.dry + i * 0.25),
    a7: [T.a7], out2: [T.out2], chips: CHIPS, arrow: [T.arrow], result: [T.result], tag: [T.tag],
    a8: [T.a8], pan: [T.pan], fly: [T.fly], fill: [T.fill1, T.fill2, T.fill3],
    q9: [T.q9], lift: [T.lift], stop2: [T.stop2], ka: [T.ka], calc: [T.calc], calcEnd: [T.calcEnd],
    tip: [T.tip], trend: [T.trend], pace: [T.pace],
    endType: [T.title1], ep: [T.ep], sting: [T.sting],
  };

  const TL = { BPM, BEAT, BAR, FPS, DUR, W, H, T, COPY, HITS, S16, WEIGHT, BF, BF_JUMPS, fatK, waterN, ramp, RINGS, CHIPS, waterDry, BF_EVE, BF_DRY };
  if (typeof module !== "undefined" && module.exports) module.exports = TL;
  else root.TL = TL;
})(typeof window !== "undefined" ? window : globalThis);
