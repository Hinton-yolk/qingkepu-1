// timeline.js — the single source of truth for picture (index.html) and sound (music/score.mjs).
// EP.04 距离传感器 (proximity sensor) — the 「为什么系列」 detective story in one continuous space: a face seen from the front,
// a phone brought up to the ear; inside, a side cut through the top of the phone (dark).
//   1 phenomenon          打电话时，屏幕怎么自己就黑了？            (it goes black before it touches; pull away, it lights up)
//   2 wrong guess, struck  你是不是以为，是脸碰到了屏幕？ ✕ 其实还没碰到，它就已经黑了
//   3 dig in               那它怎么知道，脸来了？ → the little window by the earpiece → under the glass: a lamp and an eye
//   4 one mechanism        the lamp keeps sending invisible light → a face comes close → more comes back → past the line,
//                          the screen goes dark → and sunlight? the lamp blinks, it only counts what blinks along → 距离传感器
//   5 the missing step     为什么非要把屏幕关掉？ → the cheek hangs up the call → dark, nothing counts
//   6 back to the start    再打一次，看看那束光 → the light bounces off the cheek, black; away, lit → 所以屏幕会黑……
//                          + a small tip: 打电话老被脸误触？看看贴膜有没有挡住顶部。
// 120 BPM: 1 beat = 0.5 s = 15 frames at 30 fps, 1 bar = 2 s; 59.75 s. The first black, the strike, the name and the closing
// black land on bar lines.
(function (root) {
  const BPM = 120, BEAT = 60 / BPM, BAR = 4 * BEAT, FPS = 30, DUR = 59.75;
  const W = 1080, H = 1920;

  const T = {
    // 0–5 · 1 the phenomenon: the phone comes up to the ear (ringing back), black before it touches; away: lit; back: black
    ring0: 0.0, off1: 2.0, on1: 2.875, off2: 3.25, underline: 3.0, h1Out: 4.84,
    // 5–10.5 · 2 the wrong guess: the phone pressed on the cheek (orange ground), struck; then the real gap
    myth: 5.0, contact: 5.625, q2: 5.25, hush: 7.5, strike: 8.0, a2: 8.25, gap: 8.25, gapEnd: 8.75,
    // 10.5–21.75 · 3 dig in: the phone turns to us → the window by the earpiece → under the glass → the lamp fires
    unOrange: 10.5, q3: 10.5, swing: 10.5, swingEnd: 11.6, ring: 12.0, dive1: 12.25, dive1End: 14.0, scan3: 14.0, scan3End: 14.6, a3: 14.5,
    q4: 16.75, pulse: 17.25, pulseEnd: 18.25, dive2: 19.25, dive2End: 21.75, flood: 21.4, floodEnd: 21.75, vibe: 21.75,
    // 22–38 · 4 the one mechanism (dark: a side cut through the top of the phone; the cheek comes in from the left)
    h3: 22.0, q5: 25.0, cheekIn: 26.0, cheekInEnd: 27.0, push: 27.25, a5: 29.75, dark1: 29.75,
    q6: 31.75, cheekOut: 31.75, cheekOutEnd: 32.5, sun: 32.5, sunEnd: 33.0, a6: 33.75, cheekIn2: 34.75, dark2: 35.5,
    name: 36.0, hush2: 37.5,
    // 38–45 · 5 the missing step: why switch the screen off at all? (the phone's face, the cheek pressing on it)
    climbA: 37.75, climbAEnd: 39.0, unflood: 38.05, q7: 38.0, press: 39.25, pressEnd: 40.75, a7: 40.0, touch: 41.0, ended: 41.25,
    rewind: 42.0, rewindEnd: 42.5, a8: 42.75, blackOut: 43.0, touch2: 43.75, away: 44.25, screenBack: 44.5,
    // 45–56.35 · 6 back to the start: call again, the light drawn; black / lit / black; a small tip
    climb: 45.0, climbEnd: 46.25, q9: 46.0, ring2: 46.5, lift: 46.5, off3: 48.0, on3: 48.875, off4: 50.0, quiet: 50.0,
    fin: 50.25, finOut: 52.75, tip: 52.75, tipOut: 56.35,
    // 56.5–59.75 end card
    end: 56.5, endMorph: 57.1, title1: 57.0, ep: 57.5, sting: 58.0,
  };

  const COPY = {
    h1: ["打电话时，", "屏幕怎么[自己]就黑了？"],
    q2: ["你是不是以为，", "是脸[碰到]了屏幕？"],
    a2: ["其实还没碰到，", "它就已经[黑]了"],
    q3: ["那它怎么知道，", "[脸]来了？"],
    a3: ["听筒旁边，藏着", "一盏[灯]，一只[眼]"],
    lamp: "灯", eye: "眼",
    q4: ["然后[呢]？"],
    h3: ["灯一直往外发着", "[看不见的光]"],
    q5: ["脸靠近了[呢]？"],
    push: ["脸越近，", "弹回来的光越[多]"],
    a5: ["多过这条线，", "屏幕就[黑]了"],
    meter: "弹回来的光", line: "够近了", screen: "屏幕",
    q6: ["那太阳一照[呢]？"],
    a6: ["灯一闪一闪，", "它只认[跟着闪]的光"],
    name: ["这一对小东西，", "就叫[距离传感器]。"],
    q7: ["为什么非要", "把屏幕[关掉]？"],
    a7: ["不关的话，", "脸会碰到[挂断]"],
    a8: ["屏幕一黑，", "碰哪儿都[不算数]"],
    q9: ["再打一次，", "看看那束[光]"],
    fin: ["所以屏幕会黑，", "是一束光[弹]了回来"],
    tipTag: "小提示", tip: ["打电话老被脸误触？", "看看贴膜有没有[挡住]顶部。"],
    who: "妈妈", calling: "正在呼叫…", talking: "通话中", endedTxt: "通话结束", btns: ["静音", "键盘", "免提"],
    end: ["你每天都在用，", "但你不知道", "它[怎么工作]"], epNum: "EP.04", epName: "距离传感器",
  };

  const clamp01 = (x) => Math.max(0, Math.min(1, x));
  const sm = (x) => x * x * (3 - 2 * x);
  const ramp = (t, a, b) => sm(clamp01((t - a) / (b - a)));

  // ---- the phone in the light world: screen on/off (scripted from the same times the sound uses)
  const OFF = [[T.off1, T.on1], [T.off2, 10.9], [T.blackOut, T.screenBack], [T.off3, T.on3], [T.off4, T.end + 0.2]];
  const lin = (t, a, b) => clamp01((t - a) / (b - a));
  const screenOn = (t) => OFF.reduce((k, [a, b]) => Math.min(k, 1 - lin(t, a, a + 0.08) * (1 - lin(t, b, b + 0.08))), 1);
  // the call on the screen: calling → talking (timer) → ended (the missing step) → talking again
  function callState(t) {
    if (t < 1.6) return { s: "calling" };
    if (t >= T.ended && t < T.rewindEnd) return { s: "ended", sec: Math.floor(12 + T.ended) };
    if (t >= T.ring2 && t < T.ring2 + 1.1) return { s: "calling" };
    if (t >= T.ring2) return { s: "talking", sec: Math.floor(t - (T.ring2 + 1.1)) };
    return { s: "talking", sec: Math.floor(12 + t) };
  }
  // ---- the mechanism (dark, screen px): where the cheek's surface is; how much of the lamp's own light comes back
  const GLASS_X = 720;
  function cheekX(t) {
    const s = (a, b, x0, x1) => x0 + (x1 - x0) * sm(clamp01((t - a) / (b - a)));
    if (t < T.cheekIn) return -500;
    if (t < T.push) return s(T.cheekIn, T.cheekInEnd, -500, 300);
    if (t < T.a5) return s(T.push, T.a5, 300, 456);
    if (t < T.cheekOut) return s(T.a5, T.a5 + 0.75, 456, 490);
    if (t < T.cheekIn2) return s(T.cheekOut, T.cheekOutEnd, 490, -160);
    if (t < T.dark2) return s(T.cheekIn2, T.dark2, -160, 456);
    return s(T.dark2, T.dark2 + 0.5, 456, 490);
  }
  const reading = (t) => { const d = GLASS_X - cheekX(t); return clamp01(0.03 + 1.25 * Math.exp(-(d - 120) / 150)); };   // 0.5 = the line
  const sunK = (t) => ramp(t, T.sun, T.sunEnd) * (1 - ramp(t, T.climbA, T.climbA + 0.2));
  const sunIgnoredK = (t) => ramp(t, T.a6, T.a6 + 0.5);
  const darkScreen = (t) => (t >= T.dark1 && t < T.cheekOut + 0.3) || (t >= T.dark2 && t < T.climbA + 0.5) ? 1 : 0;
  const blink = (t) => (Math.sin(2 * Math.PI * 4 * t) > -0.25 ? 1 : 0);              // the lamp: on/off, 4 times a second

  // sound cues derived from the same times (score.mjs reads this; beatcheck.mjs checks them on the measured grid)
  const HITS = {
    ring: [T.ring0, T.ring2], off: [T.off1, T.off2, T.off3, T.off4], on: [T.on1, T.on3], underline: [T.underline], myth: [T.myth], contact: [T.contact],
    strike: [T.strike, T.strike + 0.125], a2: [T.a2], plate: [T.ring], xray: [T.scan3], q4: [T.q4], pulse: [T.pulse], dive: [T.dive2],
    cheek: [T.cheekIn], push: [T.push], dark: [T.dark1, T.dark2], q6: [T.q6], sun: [T.sun], a6: [T.a6], name: [T.name], q7: [T.q7],
    touch: [T.touch], ended: [T.ended], blackOut: [T.blackOut], touch2: [T.touch2], q9: [T.q9], fin: [T.fin], tip: [T.tip],
    endType: [T.title1], ep: [T.ep], sting: [T.sting],
  };

  const TL = { BPM, BEAT, BAR, FPS, DUR, W, H, T, COPY, HITS, screenOn, callState, GLASS_X, cheekX, reading, sunK, sunIgnoredK, darkScreen, blink };
  if (typeof module !== "undefined" && module.exports) module.exports = TL;
  else root.TL = TL;
})(typeof window !== "undefined" ? window : globalThis);
