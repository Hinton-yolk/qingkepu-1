// music/score.mjs — the original score + every sound effect, synthesized from scratch (no samples) and locked to
// ../timeline.js, so each hit lands on its frame. 120 BPM, C major, F–G–Em–Am (IV–V–iii–vi), a 3-note hook (mi-sol-la).
//   node music/score.mjs   ->  music/score.wav (48 kHz stereo, peak-normalised; loudness is set in the mix step)
// EP.03 微波炉 on the series template: same motif, same question cue, plus the oven's own sounds — the hum (only while it
// runs; level from timeline.js humLevel) and the ding, once at the start and once at the end, both on bar lines.
// No noise whooshes on transitions: tonal glides, blooms.
import { createRequire } from "node:module";
import { writeFileSync } from "node:fs";
const require = createRequire(import.meta.url);
const TL = require("../timeline.js");
const { T, DUR, humLevel, fieldK, heatK } = TL;

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

// ------------------------------------------------------------------ arrangement (59.75 s; chords per 2 s bar, sections by time)
// v3: the series' own sound (the same synths, straight 16ths, 120 BPM, the same drums and lead), a new piece inside it:
// G major (the oven's ding, G6, is the answer's DO), vi–IV–I–V instead of IV–V–iii–vi, a new melody grown from the same
// motif, off-beat open hats and an off-beat bass, a 16th pluck arpeggio in place of the off-beat chord stabs.
// Under the oven's hum (tuned to G) every chord holds a G. The marks stay: mi-sol-la → mi-sol-DO, the question cue,
// the strike and the name, the sting on DO.
const STYLE = process.env.STYLE || "C";                       // (C is the approved one)
const CH = { Em: [52, 55, 59, 64], C: [48, 52, 55, 60], G: [50, 55, 59, 62], D: [50, 54, 57, 62], Am: [45, 48, 52, 57], Bm: [47, 50, 54, 59] };
const ROOT = { Em: 28, C: 24, G: 31, D: 26, Am: 33, Bm: 35 };
// 30 bars: hook Em C G | guess D | struck Em | digging in C G D Em C | the rice Am | molecules Em C G D Em C D | the name C
// | turntable Em C G D | climb out Em | press start C | the answer G (50) | the tip Em C | end G G
const BARS = ["Em", "C", "G", "D", "Em", "C", "G", "D", "Em", "C", "Am", "Em", "C", "G", "D", "Em", "C", "D", "C",
  "Em", "C", "G", "D", "Em", "C", "G", "Em", "C", "G", "G"];
const SECS = [[0, "hook"], [T.myth, "myth"], [T.strike, "ans"], [T.unOrange, "board"], [T.dive2, "inside"], [T.h3, "mech"], [T.name, "name"],
  [T.q7, "missing"], [T.climb, "build"], [T.tap2, "turn"], [T.ding2, "payoff"], [T.ding2 + BAR, "outro"], [T.end, "end"]];
const secAt = (t) => { let s = SECS[0][1]; for (const [t0, n] of SECS) if (t >= t0 - 1e-6) s = n; return s; };
// the motif in G: mi-sol-la = B D E (a question over Em), the answer mi-sol-DO = B D G
const MEL = {
  Em: [[0, 71, 2], [2, 74, 2], [4, 76, 4], [10, 74, 2], [12, 71, 4]],
  C: [[0, 72, 2], [2, 76, 2], [4, 79, 3], [7, 76, 3], [10, 74, 2], [12, 72, 4]],
  G: [[0, 71, 2], [2, 74, 2], [4, 79, 5], [10, 81, 2], [12, 79, 4]],      // the answer: mi-sol-DO
  D: [[0, 74, 2], [2, 78, 2], [4, 81, 3], [7, 78, 3], [10, 76, 2], [12, 74, 4]],
  Am: [[0, 76, 3], [3, 74, 3], [6, 72, 2], [8, 71, 2], [10, 72, 6]],
  Bm: [[0, 74, 2], [2, 78, 2], [4, 76, 4], [10, 74, 2], [12, 71, 4]],
};
const silent = (t) => (t >= T.hush && t < T.strike);               // real silence before the strike
const breath = (t) => (t >= T.hush2 && t < T.q7);                  // drums out before the missing step
function playLead(b, v, bright, oct = 0, until = Infinity) { MEL[BARS[b]].forEach(([s, m, d]) => { const t = b * BAR + s * S16; if (!silent(t) && t < until) lead(t, m + oct, d * S16 * 0.92, v, bright); }); }
function playMallet(b, v, from, until) { MEL[BARS[b]].forEach(([s, m], i) => { const t = b * BAR + s * S16; if (i < 4 && t >= from && t < until) mallet(t, m - 12, v, -0.3 + (i % 3) * 0.3); }); }
const ARP = [0, 1, 2, 3, 2, 1, 2, 3];                              // chord-tone order for the 16th pluck arpeggio
const NB = Math.ceil(DUR / BAR);

for (let b = 0; b < NB; b++) {
  const t0 = b * BAR, ch = BARS[b], root = ROOT[ch];
  for (let q = 0; q < 4; q++) {
    const t = t0 + q * BEAT; if (t >= DUR) break;
    const sec = secAt(t);
    if (silent(t)) continue;
    if (t < T.ding1 - 1e-6) continue;                                     // the beat drops in on the ding
    const br = breath(t);
    const full = sec === "hook" || sec === "name" || sec === "payoff" || sec === "board";
    if ((full || sec === "inside") && !br && (sec !== "payoff" || q === 0 || q === 2)) kick(t, sec === "inside" ? 0.75 : sec === "board" ? 0.85 : sec === "payoff" ? 0.75 : q === 0 ? 1 : 0.9);
    if (sec === "mech" && !br && (q === 0 || q === 2)) kick(t, 0.5);
    if (sec === "outro" && q === 0) kick(t, 0.6);
    if (sec === "myth" && q === 2) kick(t, 0.6);
    if (sec === "ans" && (q === 0 || q === 2) && t > T.strike + 0.01) kick(t, 0.75);
    if (sec === "missing" && (q === 0 || q === 2)) kick(t, q === 0 ? 0.8 : 0.5);
    if (sec === "end" && Math.abs(t - (T.ding2 + BAR)) < 1e-6) kick(t, 0.8);
    if (full && !br && (q === 1 || q === 3)) clap(t, sec === "board" ? 0.6 : 0.75);
    if (sec === "missing" && q === 2) snare(t, 0.7);
    // hats: soft closed 16ths, an open hat on every off-beat 8th (new for this episode)
    if ((full || sec === "missing" || sec === "ans" || sec === "outro") && !br) {
      for (let e = 0; e < 4; e++) { const th = t + e * S16; if (silent(th)) continue; if (e === 2) hat(th, sec === "outro" ? 0.5 : 0.75, true, 0.2); else hat(th, e % 2 ? 0.4 : 0.22, false, 0.25); }
    }
    if (sec === "myth") hat(t + BEAT / 2, 0.45, false, 0.25);
    // bass: a short root on the beat, the octave on the off-beat (a pumping, off-beat bass)
    if ((full || sec === "inside" || sec === "ans") && !br) { bass(t, root + 12, BEAT * 0.18, 0.75); if (!silent(t + BEAT / 2)) bass(t + BEAT / 2, root + 24, BEAT * 0.4, 0.9); }
    if ((sec === "mech" || sec === "outro") && !br && q === 0) bass(t, root + 12, BEAT * 1.6, 0.45);
    if (sec === "myth") { [0, 0.75].forEach((o) => { if (!silent(t + o * BEAT)) bass(t + o * BEAT, root + 12, BEAT * 0.22, 0.75); }); }
    if (sec === "missing" && (q === 0 || q === 2)) [[0, 0], [0.75, 7], [1.0, 12], [1.5, 7]].forEach(([o, iv]) => { if (t + o * BEAT < T.climb) bass(t + o * BEAT, root + 12 + iv, BEAT * 0.3, 0.6); });
    // a 16th pluck arpeggio, two octaves up, where the groove is full
    if ((sec === "hook" || sec === "payoff" || sec === "board" || sec === "name") && !br) {
      const notes = CH[ch].map((m) => m + 24);
      for (let e = 0; e < 4; e++) { const th = t + e * S16; if (!silent(th)) pluck(th, notes[ARP[(q * 4 + e) % 8]], (e === 0 ? 0.55 : 0.4) * (sec === "board" ? 0.75 : 1), e % 2 ? 0.3 : -0.3); }
    }
  }
  const cuts = [t0, ...SECS.map(([x]) => x).filter((x) => x > t0 + 1e-6 && x < t0 + BAR - 1e-6), t0 + BAR];
  for (let k = 0; k + 1 < cuts.length; k++) {
    const a = cuts[k], z = Math.min(cuts[k + 1], DUR), sec = secAt(a), notes = CH[ch].map((m) => m + 12), len = z - a - 0.05;
    if (len < 0.2) continue;
    if (sec === "hook") pad(a, notes, len, a < T.ding1 ? 0.35 : 0.5, 1400);
    if (sec === "myth") { const e = Math.min(z, T.hush) - a - 0.02; if (e > 0.2) pad(a, notes, e, 0.55, 800); }
    if (sec === "ans") { const s0 = Math.max(a, T.a2); if (z - s0 > 0.25) pad(s0, notes, z - s0 - 0.05, 0.8, 1100); }
    if (sec === "board") pad(a, notes, len, 0.6, 1300);
    if (sec === "inside") pad(a, notes, len, 1, 700);
    if (sec === "mech" || sec === "name") pad(a, notes, len, 0.85, 1100);
    if (sec === "outro") pad(a, notes, len, 0.7, 1300);
    if (sec === "missing") pad(a, notes, len, 0.75, 1000);
    if (sec === "build") pad(a, notes, len, 0.45, 900);
    if (sec === "turn") pad(a, notes, len, 0.5, 1200);
    if (sec === "payoff") pad(a, notes, len, 0.9, 1800);
    if (sec === "end") pad(a, notes, len, 1, 1500);
  }
  if (secAt(t0) === "hook") playLead(b, b === 0 ? 0.6 : 0.9, 1);
  if (b === 7) playLead(b, 0.55, 0.4);                                   // a soft hint of the hook at the tube
  if (secAt(t0 + BAR - 0.01) === "missing" || secAt(t0) === "missing") playMallet(b, 0.8, T.q7, T.climb);
  if (secAt(t0) === "outro") playMallet(b, 0.6, T.ding2 + BAR, T.end);
  if (secAt(t0) === "payoff") playLead(b, 0.95, 1.1);
}
// the last word: mi-sol-DO, the DO on the sting
[[0, 71, 2], [2, 74, 2], [4, 79, 10]].forEach(([s, m, d]) => lead(T.sting - 0.5 + s * S16, m, d * S16 * 0.92, 0.85, 0.9));
// the guess: a small "la-do-mi?" motif under the question (E G B A in G)
[[0, 76], [2, 79], [4, 83], [8, 81]].forEach(([s, m], i) => pluck(T.q2 + 0.25 + s * S16, m, 0.8, -0.2 + 0.15 * i));
// inside the rice: a quiet 8th arp
for (let t = T.vibe; t < T.climbA - 1e-6; t += BEAT / 2) {
  const ch = BARS[Math.floor(t / BAR)], notes = CH[ch].map((m) => m + 24), k = Math.round(t / (BEAT / 2));
  if (breath(t)) continue;
  pluck(t, notes[k % 4], 0.36 * Math.min(1, (t - T.vibe) / 0.5), k % 2 ? 0.25 : -0.25);
}

// ------------------------------------------------------------------ the oven: its hum (own bus; level from the picture) and its ding
const HUM = bus();
{
  const lpA = svf(), lpB = svf(); let ph1 = 0, ph2 = 0, ph3 = 0, br = 0;
  const N0 = Math.floor(DUR * SR);
  for (let n = 0; n < N0; n++) {
    const t = n / SR, lev = humLevel(t);
    if (lev < 1e-4) { lpA(0, 900, 0.7); lpB(0, 300, 0.7); continue; }
    ph1 = (ph1 + 98 / SR) % 1; ph2 = (ph2 + 196 / SR) % 1; ph3 = (ph3 + 294 / SR) % 1;   // tuned to G
    br = 0.97 * br + 0.05 * (rnd() * 2 - 1);                              // the fan: soft air
    const buzz = 0.5 * Math.sin(TAU * ph1) + 0.32 * Math.sin(TAU * ph2) + 0.12 * Math.sin(TAU * ph3) + 0.18 * Math.tanh(3 * Math.sin(TAU * ph1));
    const air = lpA(br, 900, 0.7).lp * 2.2;
    const v = 0.3 * lev * (buzz + air) * (0.92 + 0.08 * Math.sin(TAU * 0.5 * t));
    HUM[0][n] = v * 0.97; HUM[1][n] = v;
  }
}
function ding(t, v = 1) {                                                  // a small struck bell: inharmonic partials, long ring
  [[1, 1.0, 1.3], [2.32, 0.42, 0.7], [4.25, 0.22, 0.35], [6.63, 0.1, 0.18]].forEach(([r, a, d]) =>
    put(SFX, t, 2.2, (tt) => v * 0.22 * a * Math.sin(TAU * 1568 * r * tt) * Math.exp(-tt / d) * Math.min(1, tt / 0.0015), { pan: 0.15, rev: 0.35 }));
  click(t, 0.35 * v);
}
function beep(t, v = 1) { put(SFX, t, 0.12, (tt) => v * 0.16 * Math.sin(TAU * 2093 * tt) * Math.min(1, tt / 0.003) * Math.min(1, (0.12 - tt) / 0.01), { pan: 0.2 }); }

// ------------------------------------------------------------------ sound effects on picture events
const ask = (t) => { blip(t, 81, 0.55, -0.15); blip(t + 0.125, 86, 0.6, 0.15); };      // every question: the same rising 4th
[T.q2, T.q3, T.q4, T.q5, T.q6, T.q7, T.q9].forEach(ask);
ding(T.ding1, 1); ding(T.ding2, 1);
blip(T.underline, 88, 0.8); blip(T.underline + 0.125, 93, 0.6);
// the guess: orange, the section swept into "hottest in the middle"; struck
softImpact(T.myth, 0.3); scanSfx(T.scan1, T.scan1End - T.scan1, 0.9); thunk(T.scan1End, 0.6, 95);
impact(T.strike, 1.4); stab(T.strike, [52, 59, 64, 67, 71], 0.7, 1.1, 1.3);
buzz(T.strike, 0.3, 1); thunk(T.strike, 0.8, 120); thunk(T.strike + 0.125, 0.8, 110); buzz(T.strike + 0.125, 0.25, 0.8);
[[0, 76], [1, 74], [2, 71]].forEach(([i, m]) => pluck(T.a2 + 0.25 + i * 0.25, m, 0.7, 0.1 * i));
// digging in
scanSfx(T.scan2, T.scan2End - T.scan2, 1); glide(T.back1, T.back1End - T.back1, 79, 67, 0.5, 0);
blip(T.ring, 84, 0.9); blip(T.ring + 0.08, 91, 0.7);
glide(T.dive1, T.dive1End - T.dive1, 60, 79, 1.1); scanSfx(T.scan3, T.scan3End - T.scan3, 0.9); tick(T.a3, 0.6, 0.2, 2400);
glide(T.follow, T.followEnd - T.follow, 72, 67, 0.5, 0);
glide(T.pulse, T.pulseEnd - T.pulse, 76, 88, 0.8, 0.3); bloom(T.pulseEnd, [79, 84, 88], 0.5); thunk(T.pulseEnd, 0.35, 180);
glide(T.dive2, T.dive2End - T.dive2, 55, 79, 1.0, 0.1); bloom(T.vibe, [76, 81, 88], 0.7);
// the mechanism: the field comes on (a rising glide), every flip a soft tick, the heat a warm chord; the wave dies (falling)
glide(T.fieldOn, T.fieldOnEnd - T.fieldOn, 72, 84, 0.8, 0);
for (let t = T.fieldOn; t < T.climbA - 1e-6; t += BEAT) { const k = fieldK(t + 0.01); if (k > 0.05) blip(t, Math.round((t - T.fieldOn) / BEAT) % 2 ? 86 : 91, 0.32 * k, Math.round((t - T.fieldOn) / BEAT) % 2 ? -0.3 : 0.3); }
for (let i = 0; i < 4; i++) blip(T.push + i * 0.5, i % 2 ? 74 : 79, 0.4, i % 2 ? -0.3 : 0.3);
bloom(T.a5, [71, 76, 79, 83], 0.75);
// the depth demo: every column the microwave passes takes a bite — one note per column, each softer and lower than the last
for (let c = 0; c < 8; c++) { const tc = T.front + 0.104 + 0.25 * c, g = Math.pow(0.55, c); if (g > 0.04) { blip(tc, [83, 79, 76, 74, 71, 67, 64, 62][c], 0.9 * g + 0.05, -0.4 + 0.1 * c); } }
impact(T.name, 1.3); stab(T.name, [48, 55, 60, 64, 71], 0.6, 1, 1.2); bloom(T.name + 0.25, [79, 83, 88], 0.7);
// the missing step: hot spots appear, one side heats, the turntable spins up
bloom(T.spots, [76, 83, 88], 0.55); blip(T.side, 84, 0.5);
glide(T.spin, T.spinUp - T.spin + 0.3, 67, 79, 0.7, 0.2); bloom(T.evenEnd, [74, 78, 81], 0.5);
// back out; press start (the oven's beep); the water speaks; the ding
glide(T.climb, T.climbEnd - T.climb, 84, 60, 0.7);
click(T.tap2, 0.6); beep(T.tap2 + 0.02, 0.9);
glide(T.waveIn, T.waveInEnd - T.waveIn, 72, 84, 0.45, 0);              // the microwaves going in (soft, under the hum)
stab(T.ding2, [55, 59, 62, 67, 71], 0.3, 0.8, 1.0); bloom(T.ding2 + 0.05, [79, 83, 86, 91], 0.5);
bloom(T.tip, [76, 79, 83], 0.45);                                     // the small tip: a soft chime
{ let k = 0; TL.COPY.end.forEach((s, li) => { const n = s.replace(/[\[\]]/g, "").length; for (let j = 0; j < n; j++) tick(T.title1 + li * 0.3 + j * 0.045, 0.45, -0.2 + 0.05 * (k++ % 8), 2600 + (j % 3) * 300); }); }
blip(T.ep, 84, 0.6);
impact(T.sting, 0.8); stab(T.sting, [55, 59, 62, 67, 71], 1.6, 1, 1); bloom(T.sting, [79, 83, 86, 91], 1.2);

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
const mfL = svf(), mfR = svf(); let cut = 20000;
for (let n = 0; n < N; n++) {
  const t = n / SR, gate = silent(t) ? 0 : 1;                 // the hush: music, drums and reverb cut; the hum stays
  const m = 0, target = 20000;
  cut += (target - cut) * 0.002;                             // ~10 ms glide
  let ml = DRUM[0][n] + MUS[0][n] * duck[n] * 0.9 + wl[n] * 3.2, mr = DRUM[1][n] + MUS[1][n] * duck[n] * 0.9 + wr[n] * 3.2;
  if (cut < 17000) { const a = mfL(ml, cut, 0.7).lp, b = mfR(mr, cut, 0.7).lp, w = Math.min(1, (17000 - cut) / 3000); ml = ml + (a - ml) * w; mr = mr + (b - mr) * w; } else { mfL(ml, 17000, 0.7); mfR(mr, 17000, 0.7); }
  let l = ml * gate + SFX[0][n] + HUM[0][n];
  let r = mr * gate + SFX[1][n] + HUM[1][n];
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
writeFileSync(new URL(`./score-${STYLE}.wav`, import.meta.url), buf);
{ const win = 0.25 * SR, rows = [];
  for (const [nm, a, b] of [["hook (oven on)", 0.1, T.ding1 - 0.1], ["after the ding", T.ding1 + 0.4, T.h1Out], ["hush", T.hush, T.strike], ["mechanism", T.push, T.name], ["turntable", T.spots, T.climb], ["closing (oven on)", T.tap2 + 0.2, T.ding2 - 0.1], ["after the ding", T.ding2 + 0.3, T.finOut]]) {
    let er = 0, em = 0; for (let n = Math.floor(a * SR); n < Math.floor(b * SR); n++) { er += HUM[0][n] ** 2; const m = L[n] - HUM[0][n] * 1; em += m * m; }
    rows.push(`${nm}: hum ${(10 * Math.log10(er / ((b - a) * SR) + 1e-12)).toFixed(1)} dB, rest ${(10 * Math.log10(em / ((b - a) * SR) + 1e-12)).toFixed(1)} dB`); }
  console.log(rows.join("\n")); }
console.log(`score-${STYLE}.wav: ${DUR} s @ ${SR} Hz, mix peak ${peak.toFixed(2)} -> normalised`);
