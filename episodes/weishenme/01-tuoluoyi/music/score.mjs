// music/score.mjs — the original score + every sound effect, synthesized from scratch (no samples) and locked to
// ../timeline.js, so each hit lands on its frame. 120 BPM, C major, F–G–Em–Am (IV–V–iii–vi), a 3-note hook (mi-sol-la).
//   node music/score.mjs   ->  music/score.wav (48 kHz stereo, peak-normalised; loudness is set in the mix step)
// v4 arrangement: see the arrangement header below (the 为什么系列 detective story, 20 bars, 40 s).
// No noise whooshes on transitions: tonal glides, blooms and a riser.
import { createRequire } from "node:module";
import { writeFileSync } from "node:fs";
const require = createRequire(import.meta.url);
const TL = require("../timeline.js");
const { T, DUR, omega, VIB_HZ } = TL;

const SR = 48000, N = Math.ceil(SR * (DUR + 0.6)), TAU = Math.PI * 2, BEAT = 0.5, BAR = 2, S16 = BEAT / 4;
const bus = () => [new Float32Array(N), new Float32Array(N)];
const DRUM = bus(), MUS = bus(), SFX = bus(), SEND = bus();
const duck = new Float32Array(N).fill(1);
const mtof = (m) => 440 * Math.pow(2, (m - 69) / 12);
let seed = 1234567;
const rnd = () => { seed |= 0; seed = (seed + 0x6d2b79f5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };

function put(B, t0, len, gen, { gain = 1, pan = 0, rev = 0 } = {}) {
  const i0 = Math.max(0, Math.floor(t0 * SR)), i1 = Math.min(N, Math.floor((t0 + len) * SR));
  const gl = gain * Math.cos(((pan + 1) * Math.PI) / 4), gr = gain * Math.sin(((pan + 1) * Math.PI) / 4);
  for (let i = i0; i < i1; i++) {
    const v = gen(Math.max(0, i / SR - t0), i);
    if (!Number.isFinite(v)) continue;
    B[0][i] += v * gl; B[1][i] += v * gr;
    if (rev) { SEND[0][i] += v * gl * rev; SEND[1][i] += v * gr * rev; }
  }
}
function svf() { let lp = 0, bp = 0; return (x, fc, q = 0.7) => { const f = Math.min(0.8, 2 * Math.sin((Math.PI * Math.min(fc, SR / 6)) / SR)), qq = Math.max(0.5, q); lp += f * bp; const hp = x - lp - qq * bp; bp += f * hp; return { lp, bp, hp }; }; }
function sawBL(ph, dt) { let v = 2 * ph - 1; if (ph < dt) { const x = ph / dt; v -= x + x - x * x - 1; } else if (ph > 1 - dt) { const x = (ph - 1) / dt; v -= x * x + x + x + 1; } return v; }
const env = (tt, a, d, s, len, r) => (tt < a ? tt / a : tt < a + d ? 1 - (1 - s) * ((tt - a) / d) : tt < len ? s : s * Math.max(0, 1 - (tt - len) / r));

// ------------------------------------------------------------------ drums
function kick(t, v = 1) {
  put(DRUM, t, 0.5, (tt) => v * Math.sin(TAU * (46 * tt + (120 * (1 - Math.exp(-tt * 30))) / 30)) * Math.exp(-tt * 7) * Math.min(1, tt / 0.002), { gain: 0.95 });
  put(DRUM, t, 0.012, (tt) => v * 0.35 * (rnd() * 2 - 1) * (1 - tt / 0.012), { gain: 0.6 });
  const i0 = Math.floor(t * SR); for (let i = 0; i < SR * 0.32 && i0 + i < N; i++) duck[i0 + i] = Math.min(duck[i0 + i], 1 - 0.62 * v * Math.exp((-i / SR) * 9));
}
function clap(t, v = 1) { const f = svf(); put(DRUM, t, 0.32, (tt) => { const e = tt < 0.03 ? (Math.floor(tt / 0.01) % 2 ? 0.5 : 1) * Math.exp(-(tt % 0.01) * 200) : 0.8 * Math.exp(-(tt - 0.03) * 13); return v * f(rnd() * 2 - 1, 1500, 0.9).bp * e * 2.2; }, { gain: 0.65, rev: 0.25 }); }
function snare(t, v = 1) { const f = svf(); put(DRUM, t, 0.22, (tt) => v * (f(rnd() * 2 - 1, 4200, 0.8).bp * 1.6 * Math.exp(-tt * 22) + 0.45 * Math.sin(TAU * 196 * tt) * Math.exp(-tt * 30)), { gain: 0.55, rev: 0.15 }); }
function hat(t, v = 1, open = false, pan = 0.25) { const f = svf(); put(DRUM, t, open ? 0.32 : 0.06, (tt) => v * f(rnd() * 2 - 1, 8500, 0.6).hp * Math.exp(-tt * (open ? 11 : 75)), { gain: 0.32, pan }); }
// ------------------------------------------------------------------ instruments (music bus, ducked by the kick)
function bass(t, m, len, v = 1) { const f = svf(); let ph = 0; put(MUS, t, len + 0.04, (tt) => { const fr = mtof(m); ph = (ph + fr / SR) % 1; const s = sawBL(ph, fr / SR) * 0.55 + Math.sin(TAU * ph) * 0.9; const e = Math.min(1, tt / 0.004) * (tt < len ? 1 : Math.max(0, 1 - (tt - len) / 0.04)); return v * 0.42 * Math.tanh(1.4 * f(s, 380 + 900 * Math.exp(-tt * 18), 0.8).lp) * e; }, { gain: 0.9 }); }
function stab(t, notes, len = 0.22, v = 1, bright = 1) {
  notes.forEach((m, i) => {
    const det = [-0.12, -0.05, 0, 0.05, 0.12], ph = det.map(() => rnd()), f = svf();
    put(MUS, t, len + 0.12, (tt) => { let s = 0; det.forEach((d, k) => { const fr = mtof(m + d); ph[k] = (ph[k] + fr / SR) % 1; s += sawBL(ph[k], fr / SR); }); return v * 0.05 * f(s, 1400 + 5200 * bright * Math.exp(-tt * 9), 0.8).lp * env(tt, 0.004, 0.12, 0.55, len, 0.1); }, { pan: (i - (notes.length - 1) / 2) * 0.35, rev: 0.3 });
  });
}
function lead(t, m, len, v = 1, bright = 1) {
  const ph = [rnd(), rnd()], f = svf();
  put(MUS, t, len + 0.18, (tt) => {
    const vib = tt > 0.12 ? 0.12 * Math.sin(TAU * 5.5 * tt) * Math.min(1, (tt - 0.12) * 4) : 0;
    let s = 0; [-0.07, 0.07].forEach((d, k) => { const fr = mtof(m + d + vib); ph[k] = (ph[k] + fr / SR) % 1; s += sawBL(ph[k], fr / SR); });
    s += 0.6 * Math.sin(TAU * ph[0] * 2);
    return v * 0.11 * f(s, 900 + 4200 * bright * Math.exp(-tt * 7), 1.1).lp * env(tt, 0.005, 0.18, 0.62, len, 0.14);
  }, { pan: 0.05, rev: 0.32 });
}
function mallet(t, m, v = 1, pan = 0) { put(MUS, t, 0.9, (tt) => v * 0.2 * (Math.sin(TAU * mtof(m) * tt) + 0.3 * Math.sin(TAU * mtof(m) * 3.9 * tt) * Math.exp(-tt * 30)) * Math.exp(-tt * 6) * Math.min(1, tt / 0.002), { pan, rev: 0.3 }); }
function pluck(t, m, v = 1, pan = 0) { put(MUS, t, 0.35, (tt) => v * 0.13 * (Math.sin(TAU * mtof(m) * tt) + 0.4 * Math.sin(TAU * mtof(m) * 2 * tt) * Math.exp(-tt * 14) + 0.2 * Math.sin(TAU * mtof(m) * 3.01 * tt) * Math.exp(-tt * 22)) * Math.exp(-tt * 11) * Math.min(1, tt / 0.002), { pan, rev: 0.22 }); }
function pad(t, notes, len, v = 1, cut = 1100) {
  notes.forEach((m, i) => { const ph = [rnd(), rnd(), rnd()], f = svf(); put(MUS, t, len + 0.6, (tt) => { let s = 0; [-0.1, 0, 0.1].forEach((d, k) => { const fr = mtof(m + d); ph[k] = (ph[k] + fr / SR) % 1; s += sawBL(ph[k], fr / SR); }); return v * 0.028 * f(s, cut, 0.7).lp * Math.min(1, tt / 0.35) * (tt < len ? 1 : Math.max(0, 1 - (tt - len) / 0.6)); }, { pan: (i - 1.5) * 0.4, rev: 0.55 }); });
}
// ------------------------------------------------------------------ effects (sfx bus, not ducked)
function blip(t, m, v = 1, pan = 0) { put(SFX, t, 0.16, (tt) => v * 0.3 * Math.sin(TAU * mtof(m) * tt) * Math.exp(-tt * 26) * Math.min(1, tt / 0.001), { pan, rev: 0.35 }); }
function tick(t, v = 1, pan = 0, f0 = 2900) { put(SFX, t, 0.03, (tt) => v * 0.32 * Math.sin(TAU * f0 * tt) * Math.exp(-tt * 190), { pan }); }
function click(t, v = 1) { put(SFX, t, 0.025, (tt) => v * 0.5 * ((rnd() * 2 - 1) * 0.6 + Math.sin(TAU * 3200 * tt)) * Math.exp(-tt * 260)); }
function thunk(t, v = 1, f0 = 150) { put(SFX, t, 0.35, (tt) => v * 0.7 * Math.sin(TAU * (f0 * tt + (f0 * 0.8 * (1 - Math.exp(-tt * 25))) / 25)) * Math.exp(-tt * 14), {}); click(t, v * 0.5); }
function glide(t, len, m0, m1, v = 1, pan = 0) { let ph = 0; put(SFX, t, len + 0.12, (tt) => { const q = Math.min(1, tt / len), fr = mtof(m0 + (m1 - m0) * q * q * (3 - 2 * q)); ph = (ph + fr / SR) % 1; return v * 0.09 * (1 - 4 * Math.abs(ph - 0.5)) * Math.sin(Math.PI * Math.min(1, tt / (len + 0.12))); }, { pan, rev: 0.45 }); }
function bloom(t, notes, v = 1) { notes.forEach((m, i) => put(SFX, t + i * 0.03, 1.6, (tt) => v * 0.06 * (Math.sin(TAU * mtof(m) * tt) + 0.3 * Math.sin(TAU * mtof(m) * 2.01 * tt)) * Math.min(1, tt / 0.06) * Math.exp(-tt * 2.6), { pan: (i - 1) * 0.4, rev: 0.6 })); }
function impact(t, v = 1) {
  kick(t, v); const f = svf();
  put(SFX, t, 1.4, (tt) => v * 0.55 * f(rnd() * 2 - 1, 1600 * Math.exp(-tt * 2.2) + 120, 0.7).lp * Math.exp(-tt * 3.4), { rev: 0.5 });
  put(SFX, t, 1.6, (tt) => v * 0.55 * Math.sin(TAU * (36 * tt + (34 * (1 - Math.exp(-tt * 7))) / 7)) * Math.exp(-tt * 2.1), {});
}
function softImpact(t, v = 1) { kick(t, v); put(SFX, t, 1.1, (tt) => v * 0.4 * Math.sin(TAU * (40 * tt + (22 * (1 - Math.exp(-tt * 8))) / 8)) * Math.exp(-tt * 2.8), {}); }
function buzz(t, len, v = 1) { let ph = 0; const f = svf(); put(SFX, t, len, (tt) => { ph = (ph + 92 / SR) % 1; return v * 0.3 * f(sawBL(ph, 92 / SR), 1100, 0.8).lp * Math.min(1, tt / 0.005) * Math.exp(-tt * 6); }, {}); }
function snapSfx(t, v = 1) { click(t, v); put(SFX, t, 0.09, (tt) => v * 0.45 * Math.sin(TAU * 1900 * tt) * Math.exp(-tt * 70), { rev: 0.2 }); thunk(t + 0.002, 0.45 * v, 210); }
function riser(t, len, v = 1) { const f = svf(); let ph = 0; put(SFX, t, len, (tt) => { const q = tt / len, fr = mtof(48 + 24 * q * q); ph = (ph + fr / SR) % 1; return v * 0.08 * Math.pow(q, 2.2) * f(sawBL(ph, fr / SR), 300 + 5000 * q * q, 1.2).lp; }, { rev: 0.4 }); }
function scanSfx(t, len, v = 1) { put(SFX, t, len, (tt) => { const q = tt / len; return v * 0.07 * Math.sin(TAU * (500 * tt + 700 * tt * q)) * (0.6 + 0.4 * Math.sin(TAU * 28 * tt)) * Math.sin(Math.PI * q); }, { pan: -0.2, rev: 0.3 }); }
function whirr(t0, t1, v = 1) {                              // the toy top spinning: a hum with a wobble, cut dead by the strike
  put(SFX, t0, t1 - t0, (tt) => { const e = Math.min(1, tt / 0.25) * Math.min(1, (t1 - t0 - tt) / 0.01); return v * 0.06 * e * (Math.sin(TAU * 330 * tt) + 0.5 * Math.sin(TAU * 662 * tt)) * (0.7 + 0.3 * Math.sin(TAU * 9 * tt)); }, { pan: 0.1, rev: 0.25 });
}

// ------------------------------------------------------------------ arrangement (44.5 s; chords per 2 s bar, sections by time)
// The detective story: hook → the guess (thin, suspicious; the toy top's hum alone right before the strike)
// → struck (one of the loudest hits) → digging in → inside → the mechanism (an arp that pans with the mass) → the name lands
// → breath → the second sensor (half-time, mallets) → climb out → the same turn again, building → the answer (the hook
// motif finally resolves: mi-sol-DO instead of mi-sol-la) → end card. Every question gets the same rising two-note cue.
// Sections start where the picture says (timeline.js), not necessarily on a bar line; chords change on bar lines.
const CH = { F: [53, 57, 60, 65], G: [55, 59, 62, 67], Em: [52, 55, 59, 64], Am: [57, 60, 64, 69], C: [48, 52, 55, 60] };
const ROOT = { F: 29, G: 31, Em: 28, Am: 33, C: 36 };
const BARS = ["F", "G", "Am", "F", "Em", "Am", "F", "G", "Em", "Am", "F", "G", "Em", "Am", "F", "Em", "Am", "F", "G", "C", "F", "C", "C"];
const SECS = [[0, "hook"], [T.myth, "myth"], [T.strike, "ans"], [T.unOrange, "board"], [T.lid, "inside"], [T.h3, "mech"], [T.name, "name"],
  [T.q7, "split"], [T.climb, "build"], [T.turn2, "turn"], [T.snap2, "payoff"], [T.snap2 + BAR, "end"]];
const secAt = (t) => { let s = SECS[0][1]; for (const [t0, n] of SECS) if (t >= t0 - 1e-6) s = n; return s; };
const MEL = {
  F: [[0, 76, 2], [2, 79, 2], [4, 81, 3], [7, 84, 3], [10, 81, 2], [12, 79, 4]],
  G: [[0, 79, 2], [2, 81, 2], [4, 83, 3], [7, 86, 3], [10, 83, 2], [12, 81, 4]],
  Em: [[0, 76, 2], [2, 79, 2], [4, 81, 3], [7, 83, 3], [10, 79, 2], [12, 76, 4]],
  Am: [[0, 81, 3], [3, 79, 3], [6, 76, 2], [8, 74, 2], [10, 76, 6]],
  C: [[0, 76, 2], [2, 79, 2], [4, 84, 5], [10, 86, 2], [12, 84, 4]],      // the answer: mi-sol-DO
};
const silent = (t) => (t >= T.hush && t < T.strike);               // real silence before the strike (only the toy top hums)
const breath = (t) => (t >= T.hush2 && t < T.q7);                  // drums out before the missing step
function playLead(b, v, bright, oct = 0, until = Infinity) { MEL[BARS[b]].forEach(([s, m, d]) => { const t = b * BAR + s * S16; if (!silent(t) && t < until) lead(t, m + oct, d * S16 * 0.92, v, bright); }); }
function playMallet(b, v, from, until) { MEL[BARS[b]].forEach(([s, m], i) => { const t = b * BAR + s * S16; if (i < 4 && t >= from && t < until) mallet(t, m - 12, v, -0.3 + (i % 3) * 0.3); }); }
const NB = Math.ceil(DUR / BAR);

for (let b = 0; b < NB; b++) {
  const t0 = b * BAR, ch = BARS[b], root = ROOT[ch];
  for (let q = 0; q < 4; q++) {
    const t = t0 + q * BEAT; if (t >= DUR) break;
    const sec = secAt(t);
    if (silent(t)) continue;
    const br = breath(t);
    const full = sec === "hook" || sec === "mech" || sec === "name" || sec === "payoff" || sec === "board" || sec === "turn";
    if ((full || sec === "inside" || sec === "build") && !br) kick(t, sec === "inside" ? 0.75 : sec === "board" ? 0.85 : sec === "build" ? 0.8 : q === 0 ? 1 : 0.9);
    if (sec === "myth" && q === 2) kick(t, 0.6);
    if (sec === "ans" && (q === 0 || q === 2) && t > T.strike + 0.01) kick(t, 0.75);
    if (sec === "split" && (q === 0 || q === 2) && Math.abs(t - T.split) > 1e-6) kick(t, q === 0 ? 0.95 : 0.6);
    if (sec === "end" && Math.abs(t - (T.snap2 + BAR)) < 1e-6) kick(t, 0.8);
    if (full && !br && (q === 1 || q === 3)) clap(t, sec === "board" ? 0.6 : 0.8);
    if (sec === "split" && q === 2) snare(t, 0.7);
    if ((full || sec === "split" || sec === "myth" || sec === "ans") && !br) {
      const sixteen = sec === "mech" || sec === "payoff" || sec === "name" || sec === "turn";
      for (let e = 0; e < (sixteen ? 4 : 2); e++) { const th = t + e * (sixteen ? S16 : BEAT / 2); if (!silent(th)) hat(th, (e % 2 ? 0.9 : 0.45) * (sec === "myth" ? 0.6 : 1), sec !== "mech" && sec !== "name" && e === (sixteen ? 2 : 1) && q === 3); }
    }
    if ((full || sec === "inside" || sec === "ans") && !br) { bass(t, root + 12, BEAT * 0.42, 0.9); if (!silent(t + BEAT / 2)) bass(t + BEAT / 2, root + 24, BEAT * 0.38, 0.7); }
    if (sec === "myth") { [0, 0.75].forEach((o) => { if (!silent(t + o * BEAT)) bass(t + o * BEAT, root + 12, BEAT * 0.22, 0.75); }); }
    if (sec === "split" && (q === 0 || q === 2)) [[0, 0], [0.75, 7], [1.0, 12], [1.5, 7]].forEach(([o, iv]) => { if (t + o * BEAT < T.climb) bass(t + o * BEAT, root + 12 + iv, BEAT * 0.3, 0.8); });
    if ((sec === "hook" || sec === "payoff") && !silent(t + BEAT / 2)) stab(t + BEAT / 2, CH[ch].map((m) => m + 12), 0.2, sec === "hook" ? 0.8 : 1, sec === "payoff" ? 1.2 : 1);
  }
  // pads: one per section piece inside the bar
  const cuts = [t0, ...SECS.map(([x]) => x).filter((x) => x > t0 + 1e-6 && x < t0 + BAR - 1e-6), t0 + BAR];
  for (let k = 0; k + 1 < cuts.length; k++) {
    const a = cuts[k], z = Math.min(cuts[k + 1], DUR), sec = secAt(a), notes = CH[ch].map((m) => m + 12), len = z - a - 0.05;
    if (len < 0.2 || b === NB - 1) continue;                             // the last half bar is the tail of the final chord
    if (sec === "myth") { const e = Math.min(z, T.hush) - a - 0.02; if (e > 0.2) pad(a, notes, e, 0.55, 800); }
    if (sec === "ans") { const s0 = Math.max(a, T.a2); if (z - s0 > 0.25) pad(s0, notes, z - s0 - 0.05, 0.8, 1100); }
    if (sec === "board") pad(a, notes, len, 0.6, 1300);
    if (sec === "inside") pad(a, notes, len, 1, 700);
    if (sec === "mech" || sec === "name") pad(a, notes, len, 0.8, 1200);
    if (sec === "split" || sec === "build" || sec === "turn") pad(a, notes, len, 0.75, sec === "turn" ? 1500 : 1000);
    if (sec === "payoff") pad(a, notes, len, 0.9, 1800);
    if (sec === "end") pad(a, notes, b === NB - 2 ? 1.6 : len, 1, 1500);
  }
  if (secAt(t0) === "hook") playLead(b, 0.9, 1);
  if (b === 5) playLead(b, 0.55, 0.4);                                   // a soft hint of the hook while the chip is found
  if (secAt(t0 + BAR - 0.01) === "split" || secAt(t0) === "split") playMallet(b, 1, T.q7, T.climb);
  if (secAt(t0) === "payoff") playLead(b, 1, 1.4, 12);
  if (b === NB - 2) MEL.C.slice(0, 3).forEach(([s, m, d], i) => lead(t0 + s * S16, m, (i === 2 ? 10 : d) * S16 * 0.92, 0.85, 0.9));
}
// the guess: a small "la-do-mi?" motif under the question
[[0, 69], [2, 72], [4, 76], [8, 74]].forEach(([s, m], i) => pluck(T.q2 + 0.25 + s * S16, m + 12, 0.8, -0.2 + 0.15 * i));
// the vibration, heard: a 16th arp that pans with the proof mass (x ∝ cos 2π·t)
for (let t = T.vibe; t < T.climb - 1e-6; t += S16) {
  const ch = BARS[Math.floor(t / BAR)], notes = CH[ch].map((m) => m + 24), k = Math.round(t / S16);
  const v = (t < T.split ? 0.7 : 0.4) * Math.min(1, (t - T.vibe) / 0.5) * (breath(t) ? 0.75 : 1);
  pluck(t, notes[k % 4] + (k % 8 >= 4 ? 12 : 0), v, 0.75 * Math.cos(TAU * VIB_HZ * t));
}
// the sideways pushes while the phone turns: a blip on each 8th off-beat where the push peaks, louder when faster
for (let t = Math.ceil((T.turnA - 0.25) / 0.5) * 0.5 + 0.25; t < T.turnEnd; t += 0.5) { const w = omega(t); if (w > 0.04) { const up = Math.round((t - 0.25) / 0.5) % 2 === 0; blip(t, up ? 93 : 86, 0.45 + 0.55 * w, up ? 0.4 : -0.4); } }

// ------------------------------------------------------------------ sound effects on picture events
const ask = (t) => { blip(t, 81, 0.55, -0.15); blip(t + 0.125, 86, 0.6, 0.15); };      // every question: the same rising 4th
[T.q2, T.q3, T.q4, T.q5, T.q6, T.q7, T.q8].forEach(ask);
tick(T.rotEnd, 0.9); snapSfx(T.snap1, 1); stab(T.snap1, [72, 76, 79, 84], 0.3, 0.9, 1.2);
blip(T.underline, 88, 0.8); blip(T.underline + 0.125, 93, 0.6);
// the guess: the ground turns orange, a toy top is scanned in and hums; half a second of real silence; struck
softImpact(T.myth, 0.3); scanSfx(T.scan1, T.scan1End - T.scan1, 0.9);
whirr(T.scan1 + 0.2, T.strike, 1.15);
impact(T.strike, 1.4); stab(T.strike, [53, 60, 65, 69, 72], 0.7, 1.1, 1.3);
buzz(T.strike, 0.3, 1); thunk(T.strike, 0.8, 120); thunk(T.strike + 0.125, 0.8, 110); buzz(T.strike + 0.125, 0.25, 0.8);
[[0, 76], [1, 74], [2, 72]].forEach(([i, m]) => pluck(T.a2 + 0.25 + i * 0.25, m, 0.7, 0.1 * i));
// digging in
scanSfx(T.scan2, T.scan2End - T.scan2, 1); blip(T.ring, 84, 0.9); blip(T.ring + 0.08, 91, 0.7);
glide(T.dive1, T.dive1End - T.dive1, 60, 79, 1.1);
put(SFX, T.rice, 0.2, (tt) => 0.4 * Math.sin(TAU * (700 - 400 * tt) * tt) * Math.exp(-tt * 20), {}); for (let i = 0; i < 4; i++) tick(T.dims + i * 0.06, 0.6, 0.3, 3400);
glide(T.push2, T.push2End - T.push2, 67, 72, 0.6, 0);
thunk(T.lid, 0.9, 260); click(T.lid + 0.01, 0.8); glide(T.lid + 0.05, 0.45, 67, 79, 0.7, 0.3);
glide(T.dive2, T.dive2End - T.dive2, 55, 84, 1.0, 0.1); bloom(T.vibe, [76, 81, 88], 0.8);
// the mechanism
glide(T.close, 0.6, 64, 76, 0.7, 0); glide(T.turnA, 0.6, 72, 79, 0.7, -0.3); glide(T.turnB, 0.5, 76, 88, 0.8, 0.3);
// the noun lands as the answer
impact(T.name, 1.3); stab(T.name, [57, 64, 69, 72, 76], 0.6, 1, 1.2); bloom(T.name + 0.25, [81, 88, 93], 0.7);
// the missing step: the second sensor
softImpact(T.split, 0.35); stab(T.split, [57, 64, 69, 72], 0.5, 0.45, 0.8);
blip(T.sayL, 84, 0.8); blip(T.sayL + 0.125, 91, 0.6);
thunk(T.accDrop + 0.18, 0.9, 170); thunk(T.accDrop + 0.45, 0.3, 170);
blip(T.sayR, 86, 0.8); blip(T.sayR + 0.125, 93, 0.6);
// back out, the same turn again, both sensors speak, the screen turns
glide(T.climb, T.climbEnd - T.climb, 84, 60, 0.7);
riser(T.q8 + 0.25, T.snap2 - T.q8 - 0.25, 1.1);
glide(T.turn2, T.turn2End - T.turn2, 72, 79, 0.6, -0.2);
blip(T.say2G, 84, 0.8); blip(T.say2G + 0.125, 91, 0.6);
blip(T.say2A, 86, 0.8); blip(T.say2A + 0.125, 93, 0.6); thunk(T.say2A + 0.25, 0.7, 170);
for (let i = 0; i < 8; i++) snare(T.snap2 - 1.0 + i * 0.125, 0.25 + i * 0.07);
impact(T.snap2, 1.2); snapSfx(T.snap2, 1);
{ let k = 0; TL.COPY.end.forEach((s, li) => { const n = s.replace(/[\[\]]/g, "").length; for (let j = 0; j < n; j++) tick(T.title1 + li * 0.3 + j * 0.045, 0.45, -0.2 + 0.05 * (k++ % 8), 2600 + (j % 3) * 300); }); }
blip(T.ep, 84, 0.6);
impact(T.sting, 0.8); stab(T.sting, [60, 64, 67, 72, 76], 1.6, 1, 1); bloom(T.sting, [84, 88, 91, 96], 1.2);

// ------------------------------------------------------------------ mix: duck the music by the kick, reverb send, glue
function verb(inp, spread) {
  const sc = SR / 44100;
  const combs = [1116, 1188, 1277, 1356, 1422, 1491].map((d) => ({ b: new Float32Array(Math.round((d + spread) * sc)), i: 0, s: 0 }));
  const aps = [556, 441, 341].map((d) => ({ b: new Float32Array(Math.round((d + spread) * sc)), i: 0 }));
  const o = new Float32Array(N);
  for (let n = 0; n < N; n++) {
    const x = inp[n] * 0.02; let y = 0;
    for (const c of combs) { const v = c.b[c.i]; c.s = v * 0.7 + c.s * 0.3; c.b[c.i] = x + c.s * 0.82; c.i = (c.i + 1) % c.b.length; y += v; }
    for (const a of aps) { const v = a.b[a.i]; a.b[a.i] = y + v * 0.5; a.i = (a.i + 1) % a.b.length; y = v - y; }
    o[n] = y;
  }
  return o;
}
const wl = verb(SEND[0], 0), wr = verb(SEND[1], 23);
const L = new Float32Array(N), R = new Float32Array(N); let peak = 0;
for (let n = 0; n < N; n++) {
  const gate = silent(n / SR) ? 0 : 1;                       // the hush: music, drums and reverb cut; the toy top's dry hum stays
  let l = (DRUM[0][n] + MUS[0][n] * duck[n] * 0.9 + wl[n] * 3.2) * gate + SFX[0][n];
  let r = (DRUM[1][n] + MUS[1][n] * duck[n] * 0.9 + wr[n] * 3.2) * gate + SFX[1][n];
  l = Math.tanh(l * 1.15) / 1.15; r = Math.tanh(r * 1.15) / 1.15;
  L[n] = l; R[n] = r; peak = Math.max(peak, Math.abs(l), Math.abs(r));
}
const g = 0.89 / peak, endFade = (DUR - 0.9) * SR, NN = Math.floor(DUR * SR);
const buf = Buffer.alloc(44 + NN * 4);
buf.write("RIFF", 0); buf.writeUInt32LE(36 + NN * 4, 4); buf.write("WAVE", 8); buf.write("fmt ", 12); buf.writeUInt32LE(16, 16); buf.writeUInt16LE(1, 20); buf.writeUInt16LE(2, 22);
buf.writeUInt32LE(SR, 24); buf.writeUInt32LE(SR * 4, 28); buf.writeUInt16LE(4, 32); buf.writeUInt16LE(16, 34); buf.write("data", 36); buf.writeUInt32LE(NN * 4, 40);
for (let n = 0; n < NN; n++) {
  const f = Math.min(1, n / (0.004 * SR)) * (n > endFade ? Math.max(0, 1 - (n - endFade) / (0.9 * SR)) : 1);
  buf.writeInt16LE(Math.round(Math.max(-1, Math.min(1, L[n] * g * f)) * 32767), 44 + n * 4);
  buf.writeInt16LE(Math.round(Math.max(-1, Math.min(1, R[n] * g * f)) * 32767), 46 + n * 4);
}
writeFileSync(new URL("./score.wav", import.meta.url), buf);
console.log(`score.wav: ${DUR} s @ ${SR} Hz, mix peak ${peak.toFixed(2)} -> normalised`);
