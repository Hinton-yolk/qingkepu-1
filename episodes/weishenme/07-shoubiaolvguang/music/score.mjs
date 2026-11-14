// music/score.mjs — the original score + every sound effect, synthesized from scratch (no samples) and locked to
// ../timeline.js, so each hit lands on its frame.
//   node music/score.mjs   ->  music/score-C.wav (48 kHz stereo, peak-normalised; loudness is set in the mix step)
// EP.07 手表绿光 — same sound as the series (the same synths and drum kit, 120 BPM straight 16ths, the question cue, the hook
// mi-sol-la → mi-sol-DO), a new piece:
//   · A major (new for the series). The watch's own wake-up chime is the hook: mi-sol-la (C#7 E7 F#7) when the face lights;
//     on the closing landing it resolves: mi-sol-DO (C#7 E7 A7).
//   · The heart is in the music: a soft lub-dub on every beat the picture shows — 80 / min (every three 16ths, a 3-against-4
//     against the groove) at rest; running, 120 / min, the heart IS the beat (four on the floor = the heart).
//   · Progression (new): opening vi–IV–Vsus–V (F#m–D–Esus–E); the explanation I–IV–vi–V (A–D–F#m–E), a chord a second;
//     the reveals land on I; the run: vi–IV–I–V (F#m–D–A–E) with ii (Bm) before the accelerometer.
//     (EP.01/03: IV–V–iii–vi in C; EP.02: vi–IV–I–V in G; EP.04 in D; EP.05: I–V6–vi–iii6–IV… in F.)
//   · Three textures: opening = chime, light pulse, 8th plucks; explanation = the heart thump + soft 8th stabs + a 16th
//     "photon" shimmer; reveal = four on the floor, off-beat open hats, octave bass, the lead. Half-beat stops before 心率,
//     before 减掉甩手 and before the closing line. The three loudest hits: 5.25 用光看血, 23.25 心率, 45.75 the closing line.
import { createRequire } from "node:module";
import { writeFileSync } from "node:fs";
const require = createRequire(import.meta.url);
const TL = require("../timeline.js");
const { T, DUR, HITS, S16, BEATS, THUMPS, SWINGS } = TL;

const SR = 48000, N = Math.ceil(SR * (DUR + 0.6)), TAU = Math.PI * 2, BEAT = 0.5, BAR = 2;
const bus = () => [new Float32Array(N), new Float32Array(N)];
const DRUM = bus(), MUS = bus(), SFX = bus(), SEND = bus(), MUF = bus();
const duck = new Float32Array(N).fill(1);
const mtof = (m) => 440 * Math.pow(2, (m - 69) / 12);
let seed = 6060606;
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

// ------------------------------------------------------------------ drums (the series kit)
function kick(t, v = 1) {
  put(DRUM, t, 0.5, (tt) => v * Math.sin(TAU * (46 * tt + (120 * (1 - Math.exp(-tt * 30))) / 30)) * Math.exp(-tt * 7) * Math.min(1, tt / 0.002), { gain: 0.95 });
  put(DRUM, t, 0.012, (tt) => v * 0.35 * (rnd() * 2 - 1) * (1 - tt / 0.012), { gain: 0.6 });
  const i0 = Math.floor(t * SR); for (let i = 0; i < SR * 0.32 && i0 + i < N; i++) duck[i0 + i] = Math.min(duck[i0 + i], 1 - 0.62 * v * Math.exp((-i / SR) * 9));
}
function clap(t, v = 1) { const f = svf(); put(DRUM, t, 0.32, (tt) => { const e = tt < 0.03 ? (Math.floor(tt / 0.01) % 2 ? 0.5 : 1) * Math.exp(-(tt % 0.01) * 200) : 0.8 * Math.exp(-(tt - 0.03) * 13); return v * f(rnd() * 2 - 1, 1500, 0.9).bp * e * 2.2; }, { gain: 0.65, rev: 0.25 }); }
function snare(t, v = 1) { const f = svf(); put(DRUM, t, 0.22, (tt) => v * (f(rnd() * 2 - 1, 4200, 0.8).bp * 1.6 * Math.exp(-tt * 22) + 0.45 * Math.sin(TAU * 196 * tt) * Math.exp(-tt * 30)), { gain: 0.55, rev: 0.15 }); }
function hat(t, v = 1, open = false, pan = 0.25) { const f = svf(); put(DRUM, t, open ? 0.32 : 0.06, (tt) => v * f(rnd() * 2 - 1, 8500, 0.6).hp * Math.exp(-tt * (open ? 11 : 75)), { gain: 0.32, pan }); }
function rim(t, v = 1) { put(DRUM, t, 0.05, (tt) => v * 0.4 * (Math.sin(TAU * 1700 * tt) + 0.6 * Math.sin(TAU * 830 * tt)) * Math.exp(-tt * 90), { pan: -0.2, rev: 0.15 }); }
// ------------------------------------------------------------------ instruments (music bus, ducked by the kick)
function bass(t, m, len, v = 1, B = MUS) { const f = svf(); let ph = 0; put(B, t, len + 0.04, (tt) => { const fr = mtof(m); ph = (ph + fr / SR) % 1; const s = sawBL(ph, fr / SR) * 0.55 + Math.sin(TAU * ph) * 0.9; const e = Math.min(1, tt / 0.004) * (tt < len ? 1 : Math.max(0, 1 - (tt - len) / 0.04)); return v * 0.42 * Math.tanh(1.4 * f(s, 380 + 900 * Math.exp(-tt * 18), 0.8).lp) * e; }, { gain: 0.9 }); }
function stab(t, notes, len = 0.22, v = 1, bright = 1, B = MUS) {
  notes.forEach((m, i) => {
    const det = [-0.12, -0.05, 0, 0.05, 0.12], ph = det.map(() => rnd()), f = svf();
    put(B, t, len + 0.12, (tt) => { let s = 0; det.forEach((d, k) => { const fr = mtof(m + d); ph[k] = (ph[k] + fr / SR) % 1; s += sawBL(ph[k], fr / SR); }); return v * 0.05 * f(s, 900 + 5200 * bright * Math.exp(-tt * 9), 0.8).lp * env(tt, 0.004, 0.12, 0.55, len, 0.1); }, { pan: (i - (notes.length - 1) / 2) * 0.35, rev: 0.3 });
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
function mallet(t, m, v = 1, pan = 0, B = MUS) { put(B, t, 0.9, (tt) => v * 0.2 * (Math.sin(TAU * mtof(m) * tt) + 0.3 * Math.sin(TAU * mtof(m) * 3.9 * tt) * Math.exp(-tt * 30)) * Math.exp(-tt * 6) * Math.min(1, tt / 0.002), { pan, rev: 0.3 }); }
function pluck(t, m, v = 1, pan = 0, B = MUS) { put(B, t, 0.35, (tt) => v * 0.13 * (Math.sin(TAU * mtof(m) * tt) + 0.4 * Math.sin(TAU * mtof(m) * 2 * tt) * Math.exp(-tt * 14) + 0.2 * Math.sin(TAU * mtof(m) * 3.01 * tt) * Math.exp(-tt * 22)) * Math.exp(-tt * 11) * Math.min(1, tt / 0.002), { pan, rev: 0.22 }); }
function pad(t, notes, len, v = 1, cut = 1100) {
  notes.forEach((m, i) => { const ph = [rnd(), rnd(), rnd()], f = svf(); put(MUS, t, len + 0.6, (tt) => { let s = 0; [-0.1, 0, 0.1].forEach((d, k) => { const fr = mtof(m + d); ph[k] = (ph[k] + fr / SR) % 1; s += sawBL(ph[k], fr / SR); }); return v * 0.028 * f(s, cut, 0.7).lp * Math.min(1, tt / 0.35) * (tt < len ? 1 : Math.max(0, 1 - (tt - len) / 0.6)); }, { pan: (i - 1.5) * 0.4, rev: 0.55 }); });
}
// the phone's ringtone: a bright two-partial "marimba" — the hook motif, as a ringtone
function ringNote(t, m, v = 1, pan = 0.12) { put(SFX, t, 0.3, (tt) => v * 0.16 * (Math.sin(TAU * mtof(m) * tt) + 0.45 * Math.sin(TAU * mtof(m) * 2 * tt) * Math.exp(-tt * 18) + 0.25 * Math.sin(TAU * mtof(m) * 4.02 * tt) * Math.exp(-tt * 40)) * Math.exp(-tt * 9) * Math.min(1, tt / 0.0015), { pan, rev: 0.18 }); }
// ------------------------------------------------------------------ effects (sfx bus, not ducked)
function blip(t, m, v = 1, pan = 0) { put(SFX, t, 0.16, (tt) => v * 0.3 * Math.sin(TAU * mtof(m) * tt) * Math.exp(-tt * 26) * Math.min(1, tt / 0.001), { pan, rev: 0.35 }); }
function tick(t, v = 1, pan = 0, f0 = 2900) { put(SFX, t, 0.03, (tt) => v * 0.32 * Math.sin(TAU * f0 * tt) * Math.exp(-tt * 190), { pan }); }
function click(t, v = 1) { put(SFX, t, 0.025, (tt) => v * 0.5 * ((rnd() * 2 - 1) * 0.6 + Math.sin(TAU * 3200 * tt)) * Math.exp(-tt * 260)); }
function thunk(t, v = 1, f0 = 150) { put(SFX, t, 0.35, (tt) => v * 0.7 * Math.sin(TAU * (f0 * tt + (f0 * 0.8 * (1 - Math.exp(-tt * 25))) / 25)) * Math.exp(-tt * 14), {}); click(t, v * 0.5); }
function tap(t, v = 1, f0 = 120) { put(SFX, t, 0.12, (tt) => v * 0.55 * Math.sin(TAU * (f0 * tt + (f0 * 0.6 * (1 - Math.exp(-tt * 40))) / 40)) * Math.exp(-tt * 38), {}); }   // a soft, muffled tap (no click)
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
function riser(t, len, v = 1) { const f = svf(); let ph = 0; put(SFX, t, len, (tt) => { const q = tt / len, fr = mtof(50 + 24 * q * q); ph = (ph + fr / SR) % 1; return v * 0.08 * Math.pow(q, 2.2) * f(sawBL(ph, fr / SR), 300 + 5000 * q * q, 1.2).lp; }, { rev: 0.4 }); }
function creak(t, v = 1) { put(SFX, t, 0.22, (tt) => { const q = tt / 0.22; return v * 0.12 * Math.sin(TAU * (420 * tt - 300 * tt * q)) * (0.6 + 0.4 * Math.sin(TAU * 55 * tt)) * Math.sin(Math.PI * q); }, { pan: -0.1, rev: 0.2 }); }

// the scale: a short electronic beep (sine + a little 3rd harmonic), and the footstep on glass
function beep(t, m, len = 0.11, v = 1, pan = 0) { put(SFX, t, len + 0.02, (tt) => v * 0.2 * (Math.sin(TAU * mtof(m) * tt) + 0.18 * Math.sin(TAU * mtof(m) * 3 * tt)) * Math.min(1, tt / 0.003) * (tt < len ? 1 : Math.max(0, 1 - (tt - len) / 0.02)), { pan, rev: 0.12 }); }
function step(t, v = 1) { tap(t, 0.9 * v, 82); thunk(t, 0.35 * v, 64); put(SFX, t + 0.004, 0.12, (tt) => v * 0.16 * (Math.sin(TAU * 1180 * tt) + 0.5 * Math.sin(TAU * 2630 * tt)) * Math.exp(-tt * 42), { pan: -0.1, rev: 0.25 }); }
function plink(t, m, v = 1, pan = 0) { put(SFX, t, 0.5, (tt) => { const f = mtof(m) * (1 + 0.5 * Math.exp(-tt * 60)); return v * 0.2 * Math.sin(TAU * f * tt) * Math.exp(-tt * 9) * Math.min(1, tt / 0.002); }, { pan, rev: 0.4 }); }


// the heart: a soft, low lub-dub (sine thumps), and a swish for each swing of the arm
function heart(t, v = 1) {
  put(SFX, t, 0.25, (tt) => v * 0.55 * Math.sin(TAU * (52 * tt + (40 * (1 - Math.exp(-tt * 30))) / 30)) * Math.exp(-tt * 16) * Math.min(1, tt / 0.004), {});
  put(SFX, t + 0.13, 0.2, (tt) => v * 0.32 * Math.sin(TAU * (64 * tt + (36 * (1 - Math.exp(-tt * 34))) / 34)) * Math.exp(-tt * 20) * Math.min(1, tt / 0.004), {});
}
function swish(t, len = 0.32, v = 1, pan = 0) { const f = svf(); put(SFX, t, len, (tt) => { const q = tt / len; return v * 0.22 * f(rnd() * 2 - 1, 500 + 2600 * Math.sin(Math.PI * q), 1.4).bp * Math.sin(Math.PI * q); }, { pan, rev: 0.15 }); }

// ------------------------------------------------------------------ the harmony (A major)
const CH = { A: [52, 57, 61, 64], D: [54, 57, 62, 66], E: [52, 56, 59, 64], Fsm: [54, 57, 61, 66], Bm: [54, 59, 62, 66], Csm: [52, 56, 61, 64], Esus: [52, 57, 59, 64] };
const ROOT = { A: 33, D: 26, E: 28, Fsm: 30, Bm: 23, Csm: 25, Esus: 28 };
const PROG = [[0, "Fsm"], [1, "D"], [2, "Esus"], [2.5, "E"], [T.q2, "A"], [4, "D"], [T.a1, "A"],
  [T.flood, "Fsm"], [7, "D"], [8, "A"], [9, "E"], [10, "Fsm"], [11, "D"], [12, "Bm"], [13, "E"],
  [T.q4, "A"], [14.5, "D"], [15.5, "Fsm"], [16.5, "E"], [17.5, "A"], [18.5, "D"], [19.5, "Fsm"], [20.5, "D"], [21.25, "E"],
  [T.rate, "A"], [23, "Csm"], [24, "D"], [T.q6, "E"],
  [26, "Fsm"], [27, "D"], [28, "A"], [29, "E"], [30, "Fsm"], [31, "D"], [32, "Bm"], [33, "E"], [34, "Fsm"], [35, "E"],
  [T.sub, "A"], [37, "D"], [38, "E"],
  [T.q8, "Fsm"], [39.5, "D"], [40.5, "A"], [41.5, "E"], [42.25, "D"],
  [T.q9, "Bm"], [T.flip2, "Esus"], [T.fin, "A"], [T.fin + 0.75, "Csm"], [T.fin + 1.75, "D"], [T.fin + 2.25, "E"],
  [T.tip, "A"], [T.tip + 1, "Fsm"], [T.tip + 2, "D"], [T.tip + 3, "E"], [T.end, "A"]];
const chordAt = (t) => { let c = PROG[0][1]; for (const [a, ch] of PROG) if (t >= a - 1e-6) c = ch; return c; };
const SECS = [[0, "hook"], [T.a1, "ans"], [T.flood, "dive"], [T.q3, "dig"], [T.q4, "mech"], [T.rate, "name"], [T.q6, "out"], [T.r1, "run"],
  [T.acc, "acc"], [T.sub, "name"], [T.q8, "ring"], [T.q9, "build"], [T.fin, "payoff"], [T.tip, "tip"], [T.end, "end"]];
const secAt = (t) => { let s = SECS[0][1]; for (const [t0, n] of SECS) if (t >= t0 - 1e-6) s = n; return s; };
const STOPS = [[T.rate - 0.5, T.rate], [T.sub - 0.5, T.sub], [T.stop2, T.fin]];
const silent = (t) => STOPS.some(([a, b]) => t >= a && t < b);

// ------------------------------------------------------------------ arrangement
const ARP = [0, 1, 2, 3, 2, 1, 2, 3];
for (let t = 0; t < DUR - 1e-6; t += BEAT) {
  const q = Math.round(t / BEAT) % 4, sec = secAt(t), ch = chordAt(t + 1e-4), root = ROOT[ch], notes = CH[ch];
  if (silent(t)) continue;
  // drums (where the heart is heard, the kick steps back: the heart is the pulse)
  if (sec === "hook") { if (q === 0) kick(t, 0.55); hat(t + BEAT / 2, 0.35); if (t > 0.9) hat(t, 0.16); }
  if (sec === "ans") { if (q === 0 || q === 2) kick(t, 0.7); hat(t + BEAT / 2, 0.45); }
  if (sec === "dive") { const k = Math.min(1, (t - T.flood) / 0.8); for (let e = 0; e < 4; e++) hat(t + e * S16, 0.1 + 0.2 * k * (e === 2 ? 1.3 : 1)); }
  if (sec === "dig") { if (q === 0) kick(t, 0.4); if (q === 3) rim(t + BEAT / 2, 0.35); for (let e = 0; e < 4; e++) hat(t + e * S16, e === 2 ? 0.3 : 0.12); }
  if (sec === "mech") { if (q === 3) rim(t + BEAT / 2, 0.4); for (let e = 0; e < 4; e++) hat(t + e * S16, e === 2 ? 0.34 : 0.13); }
  if (sec === "name" || sec === "payoff") { kick(t, q === 0 ? 1 : 0.85); if (q === 1 || q === 3) clap(t, 0.75); for (let e = 0; e < 4; e++) { if (e === 2) hat(t + e * S16, 0.75, true, 0.2); else hat(t + e * S16, e % 2 ? 0.4 : 0.22); } }
  if (sec === "out") { if (q === 0) kick(t, 0.55); hat(t + BEAT / 2, 0.3); }
  if (sec === "run" || sec === "acc") { if (q === 1 || q === 3) snare(t, sec === "run" ? 0.55 : 0.4); for (let e = 0; e < 4; e++) hat(t + e * S16, e === 2 ? 0.45 : 0.18); }
  if (sec === "ring") { if (q === 0) kick(t, 0.45); hat(t + BEAT / 2, 0.28); }
  if (sec === "build") { if (q === 0 || q === 2) kick(t, 0.6); for (let e = 0; e < 4; e++) { const tt = t + e * S16; if (!silent(tt)) { hat(tt, 0.15 + 0.2 * (tt - T.q9)); snare(tt, 0.06 + 0.2 * (tt - T.q9)); } } }
  if (sec === "tip") { if (q === 0) kick(t, 0.45); hat(t + BEAT / 2, 0.28); }
  // bass
  if (sec === "hook" && (q === 0 || q === 2)) bass(t, root + 12, BEAT * 1.7, 0.55);
  if (sec === "ans") { bass(t, root + 12, BEAT * 0.2, 0.7); bass(t + BEAT / 2, root + 24, BEAT * 0.35, 0.8); }
  if ((sec === "dive" || sec === "dig") && q === 0) bass(t, root + 12, BEAT * 3.6, 0.45);
  if (sec === "mech") for (let e = 0; e < 2; e++) { const tt = t + e * BEAT / 2; if (!silent(tt)) bass(tt, ROOT[chordAt(tt + 1e-4)] + 12 + (e ? 12 : 0), BEAT * 0.3, 0.62); }
  if (sec === "name" || sec === "payoff") { bass(t, root + 12, BEAT * 0.18, 0.75); bass(t + BEAT / 2, root + 24, BEAT * 0.4, 0.9); }
  if (sec === "out" && (q === 0 || q === 2)) bass(t, root + 12, BEAT * 1.7, 0.55);
  if (sec === "run" || sec === "acc") { const pat = [0, 12, 0, 12]; for (let e = 0; e < 2; e++) { const tt = t + e * BEAT / 2; bass(tt, ROOT[chordAt(tt + 1e-4)] + 12 + pat[(q * 2 + e) % 4], BEAT * 0.3, sec === "run" ? 0.8 : 0.65); } }
  if ((sec === "ring" || sec === "tip") && q === 0) bass(t, root + 12, BEAT * 3.6, 0.45);
  if (sec === "build") bass(t, root + 12, BEAT * 0.3, 0.7);
  if (sec === "end" && Math.abs(t - T.sting) < 1e-6) bass(t, 33 + 12, BEAT * 3, 0.6);
  // the opening: 8th plucks
  if (sec === "hook") { const nn = notes.map((m) => m + 12); for (let e = 0; e < 2; e++) pluck(t + e * BEAT / 2, nn[(q * 2 + e + 1) % 4], 0.28, e ? 0.3 : -0.3); }
  // the explanation: soft 8th stabs and a 16th "photon" shimmer (the light going in and out)
  if (sec === "dig" || sec === "mech") {
    for (let e = 0; e < 2; e++) { const tt = t + e * BEAT / 2; if (!silent(tt)) stab(tt, CH[chordAt(tt + 1e-4)].map((m) => m + 12), 0.15, e ? 0.45 : 0.62, 0.35); }
    if (t >= T.photons - 1e-6) { const nn = notes.map((m) => m + 24); for (let e = 0; e < 4; e++) { const tt = t + e * S16; if (silent(tt)) continue; pluck(tt, nn[ARP[(q * 4 + e) % 8]], e === 0 ? 0.36 : 0.24, e % 2 ? 0.35 : -0.35); } }
  }
  // running: driving 8th stabs; the accelerometer: mallets answer the swing
  if (sec === "run") for (let e = 0; e < 2; e++) stab(t + e * BEAT / 2, notes.map((m) => m + 12), 0.14, e ? 0.5 : 0.7, 0.6);
  if (sec === "acc") { const nn = notes.map((m) => m + 12); for (let e = 0; e < 2; e++) { const tt = t + e * BEAT / 2; if (!silent(tt)) mallet(tt, nn[ARP[(q * 2 + e) % 8]] + (e ? 12 : 0), 0.4, e ? 0.25 : -0.25); } }
  // reveal: off-beat bright stabs and a 16th arp
  if (sec === "name" || sec === "payoff") { stab(t + BEAT / 2, notes.map((m) => m + 12), 0.2, 0.8, 1.2); const nn = notes.map((m) => m + 24); for (let e = 0; e < 4; e++) pluck(t + e * S16, nn[ARP[(q * 4 + e) % 8]], e === 0 ? 0.5 : 0.36, e % 2 ? 0.3 : -0.3); }
  // the ring and the tip: mallet arpeggios, quieter
  if (sec === "ring" || sec === "tip" || sec === "out") { const nn = notes.map((m) => m + 12); for (let e = 0; e < 2; e++) mallet(t + e * BEAT / 2, nn[ARP[(q * 2 + e) % 8]] + (e ? 12 : 0), sec === "out" ? 0.3 : 0.38, e ? 0.25 : -0.25); }
}
// pads, by chord span and section
{
  const cuts = [...new Set([...PROG.map(([a]) => a), ...SECS.map(([a]) => a), ...STOPS.flat(), DUR])].sort((a, b) => a - b);
  for (let k = 0; k + 1 < cuts.length; k++) {
    const a = cuts[k], z = Math.min(cuts[k + 1], DUR), sec = secAt(a + 1e-4), notes = CH[chordAt(a + 1e-4)].map((m) => m + 12), len = z - a - 0.04;
    if (len < 0.2 || silent(a + 1e-4)) continue;
    const V = { hook: [0.5, 1300], ans: [0.6, 1100], dive: [1.0, 700], dig: [0.75, 900], mech: [0.6, 1000], name: [0.8, 1600], out: [0.7, 1000],
      run: [0.5, 1400], acc: [0.6, 1200], ring: [0.8, 1300], build: [0.7, 1400], payoff: [0.85, 1800], tip: [0.75, 1300], end: [1.0, 1500] }[sec];
    if (V) pad(a, notes, len, V[0], V[1]);
  }
}
// ---- melodies grown from the motif (C#–E–F# = mi-sol-la; the answer C#–E–A = mi-sol-DO)
const play = (t0, notes, v = 0.9, br = 1) => notes.forEach(([s, m, d]) => lead(t0 + s * S16, m, d * S16 * 0.92, v, br));
play(T.rate, [[0, 85, 2], [2, 88, 2], [4, 93, 6], [10, 92, 2], [12, 90, 2], [14, 88, 2]], 0.95, 1.1);         // 心率: mi-sol-DO, then down
play(T.rate + 1.0, [[0, 88, 2], [2, 85, 2], [4, 81, 4]], 0.8, 1.0);
play(T.rate + 2.0, [[0, 90, 2], [2, 88, 2], [4, 86, 4], [8, 85, 2], [10, 83, 2]], 0.7, 0.9);
play(T.sub, [[0, 85, 2], [2, 88, 2], [4, 90, 4], [8, 88, 2], [10, 85, 2], [12, 88, 4]], 0.85, 1.0);             // 减掉甩手: mi-sol-la, open
play(T.sub + 1.0, [[0, 86, 2], [2, 85, 2], [4, 83, 4], [8, 81, 6]], 0.75, 0.9);
play(T.fin, [[0, 85, 2], [2, 88, 2], [4, 93, 8], [12, 95, 2], [14, 93, 2]], 0.95, 1.1);                           // the closing line
play(T.fin + 1.0, [[0, 92, 2], [2, 88, 2], [4, 85, 4], [8, 88, 6]], 0.85, 1.0);
play(T.fin + 2.0, [[0, 90, 2], [2, 93, 2], [4, 90, 4], [8, 88, 2], [10, 85, 2]], 0.75, 0.9);
[[0, 85], [2, 88], [4, 93], [6, 92], [8, 88]].forEach(([s, m]) => mallet(T.tip + 0.5 + s * S16, m, 0.55, 0.15));
[[0, 86], [2, 90], [4, 93], [6, 90], [10, 88]].forEach(([s, m]) => mallet(T.tip + 2 + s * S16, m, 0.5, -0.15));
[[0, 81, 2], [2, 85, 2], [4, 93, 12]].forEach(([s, m, d]) => lead(T.sting - 0.5 + s * S16, m, d * S16 * 0.92, 0.85, 0.9));

// ------------------------------------------------------------------ sound effects on picture events
const ask = (t) => { blip(t, 88, 0.55, -0.15); blip(t + 0.125, 93, 0.6, 0.15); };       // every question: the same rising 4th (E6 → A6)
[T.q3, T.q4, T.q5, T.q6, T.q7, T.q8].forEach(ask);
// the heart, wherever the picture shows it
THUMPS.forEach((t) => heart(t, t >= T.run && t < T.stopEnd ? 0.8 : 1));
// 1 the phenomenon: the green glows (a faint shimmer); the underline; the watch rolls over and lands; the face wakes (mi-sol-la)
bloom(0.02, [97, 100, 105], 0.25);
blip(T.underline, 93, 0.7); blip(T.underline + 0.125, 97, 0.5);
glide(T.flip, T.flipEnd - T.flip, 72, 84, 0.45, 0.1); tap(T.land, 0.8, 95); click(T.land, 0.35);
[[0, 97], [1, 100], [2, 102]].forEach(([i, m]) => beep(T.scrOn + i * S16, m, 0.09, 0.7, 0.1));
// 2 into the light (one of the three loudest hits): the turn to the side, the gap, the dark
impact(T.a1, 1.4); stab(T.a1, [57, 64, 69, 73, 76], 0.6, 1.05, 1.3);
riser(T.pitch + 0.25, T.flood - T.pitch, 0.7); glide(T.gap, 0.9, 62, 79, 0.55, 0.1);
bloom(T.flood, [69, 73, 76], 0.6); tick(T.ledLab, 0.45, -0.3, 3200);
// 3 the light: photons go in; the deep ones are eaten (falling); the light eye catches the rest
for (let i = 0; i < 6; i++) plink(T.photons + i * 0.25, [93, 97, 100, 97, 93, 100][i], 0.35, -0.4 + 0.16 * i);
glide(T.eat, 0.6, 81, 69, 0.5, -0.2); glide(T.eat + 1.0, 0.6, 81, 69, 0.4, 0.2);
blip(T.pdOn, 93, 0.55, 0.35); blip(T.pdOn + 0.08, 97, 0.45, 0.35);
// 4 the trace; the dim answer; the ticks; 心率 (after a half-beat stop)
glide(T.curve, T.curveEnd - T.curve, 69, 81, 0.45, 0);
glide(T.ans5, 0.5, 84, 76, 0.45, 0.1);
BEATS.filter((b) => b >= T.ticks - 0.3 && b < T.gather).forEach((b) => tick(b + 0.125, 0.45, 0.2, 3000));
glide(T.gather, T.gatherEnd - T.gather, 76, 88, 0.5, 0.3);
impact(T.rate, 1.3); stab(T.rate, [57, 64, 69, 73, 76], 0.6, 1, 1.2); bloom(T.num80, [93, 97, 100], 0.6);
// 5 running: out of the skin; the swings; the trace goes wild; ?; the accelerometer; matching; subtract; 120
glide(T.pullOut, T.pullOutEnd - T.pullOut, 79, 67, 0.55, 0);
SWINGS.forEach((t, i) => swish(t - 0.16, 0.34, 0.55, i % 2 ? 0.3 : -0.3));
glide(T.r1 + 0.25, 0.4, 76, 88, 0.35, 0.2); glide(T.r1 + 0.75, 0.4, 88, 72, 0.35, -0.2);
blip(T.qmark, 87, 0.5, 0.3); blip(T.qmark + 0.08, 86, 0.45, 0.3);
blip(T.mag, 88, 0.5, 0.35); blip(T.mag + 0.08, 92, 0.4, 0.35); tick(T.chipOn, 0.5, 0.35, 3400);
glide(T.swing, T.swingEnd - T.swing, 69, 81, 0.4, -0.2);
for (let i = 0; i < 6; i++) tick(T.align + 0.3 * i, 0.4, -0.3 + 0.12 * i, 2800 + 150 * i);
impact(T.sub, 0.7); glide(T.sub + 0.1, 0.6, 84, 72, 0.4, 0); bloom(T.num120, [93, 97, 100], 0.55);
// 6 the ring: the hand opens; the ring's light; its section
glide(T.slide, T.slideEnd - T.slide, 72, 79, 0.4, 0.2);
bloom(T.ringGlow, [88, 93, 97], 0.45); blip(T.rmag, 88, 0.5, 0.2); blip(T.rmag + 0.08, 93, 0.4, 0.2);
// 7 back to the start: the camera back; fingers; lift; it rolls over (green); half a beat of nothing; the closing line; it lands
glide(T.back, T.backEnd - T.back, 79, 69, 0.45, -0.2); click(T.grab, 0.4);
glide(T.lift, 0.25, 74, 81, 0.35, 0); glide(T.flip2, T.flip2End - T.flip2, 76, 88, 0.4, 0.1); bloom(T.flip2End, [97, 100, 105], 0.3);
riser(T.flip2End, T.stop2 - T.flip2End, 0.4);
impact(T.fin, 1.35); stab(T.fin, [57, 64, 69, 73, 76], 0.5, 1, 1.25);
tap(T.ka, 0.9, 95); [[0, 97], [1, 100], [2, 105]].forEach(([i, m]) => beep(T.ka + i * S16, m, i === 2 ? 0.3 : 0.09, 0.85, 0.1));
// 8 the tip: the strap one notch; the watch slides towards the elbow
bloom(T.tip, [81, 85, 88], 0.45); click(T.tighten, 0.6); click(T.tighten + 0.125, 0.5); tap(T.tighten, 0.4, 140);
glide(T.move, T.moveEnd - T.move, 79, 72, 0.4, -0.3);
{ let k = 0; TL.COPY.end.forEach((s, li) => { const n = s.replace(/[\[\]]/g, "").length; for (let j = 0; j < n; j++) tick(T.title1 + li * 0.3 + j * 0.045, 0.45, -0.2 + 0.05 * (k++ % 8), 2600 + (j % 3) * 300); }); }
blip(T.ep, 93, 0.6);
impact(T.sting, 0.55); stab(T.sting, [57, 64, 69, 73, 76], 1.6, 0.8, 0.9); bloom(T.sting, [93, 97, 100, 105], 1.0);

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
  const t = n / SR, gate = silent(t) ? 0 : 1;                 // the stops: everything cuts (true silence)
  let l = (DRUM[0][n] + (MUS[0][n] + MUF[0][n] * 1.5) * duck[n] * 0.9 + wl[n] * 3.2 + SFX[0][n]) * gate;
  let r = (DRUM[1][n] + (MUS[1][n] + MUF[1][n] * 1.5) * duck[n] * 0.9 + wr[n] * 3.2 + SFX[1][n]) * gate;
  l = Math.tanh(l * 1.15) / 1.15; r = Math.tanh(r * 1.15) / 1.15;
  L[n] = l; R[n] = r; peak = Math.max(peak, Math.abs(l), Math.abs(r));
}
for (const [a] of STOPS) {          // soften the gate edges so the stops do not click
  const i0 = Math.floor(a * SR), w = Math.floor(0.004 * SR);
  for (let k = 0; k < w; k++) { const g = k / w; L[i0 - w + k] *= 1 - g; R[i0 - w + k] *= 1 - g; }
}
const STYLE = process.env.STYLE || "C";
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
// the loudest moments (10 ms peak within 120 ms of each hit)
{ const pk = (t) => { let m = 0; for (let n = Math.floor(t * SR); n < Math.floor((t + 0.12) * SR); n++) m = Math.max(m, Math.abs(L[n]), Math.abs(R[n])); return +(20 * Math.log10(m * g + 1e-9)).toFixed(1); };
  const top = [T.a1, T.rate, T.fin];
  let others = -99, at = 0; for (let t = 0; t < DUR - 0.2; t += 0.125) { if (top.some((h) => Math.abs(t - h) < 0.3)) continue; const p = pk(t); if (p > others) { others = p; at = t; } }
  console.log(`peaks dBFS: 用光看血 ${pk(T.a1)}, 心率 ${pk(T.rate)}, closing ${pk(T.fin)}; loudest other ${others} at ${at.toFixed(2)} s; sting ${pk(T.sting)}`); }
console.log(`score-${STYLE}.wav: ${DUR} s @ ${SR} Hz, mix peak ${peak.toFixed(2)} -> normalised`);
