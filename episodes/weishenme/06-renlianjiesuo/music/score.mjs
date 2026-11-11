// music/score.mjs — the original score + every sound effect, synthesized from scratch (no samples) and locked to
// ../timeline.js, so each hit lands on its frame.
//   node music/score.mjs   ->  music/score-C.wav (48 kHz stereo, peak-normalised; loudness is set in the mix step)
// EP.06 人脸解锁 — the series' sound (the same synths and drum kit, 120 BPM straight 16ths, the question cue, the hook
// mi-sol-la → mi-sol-DO), a new piece:
//   · B-flat major (new). The hook is the phone's scan: mi-sol-la (D6 F6 G6) as sparkles; on the closing unlock it resolves
//     mi-sol-DO (D6 F6 Bb6). Every question: the rising fourth F6 → Bb6.
//   · Progressions (new): opening I–vi–ii–V; the measuring walks I–iii–IV–iv (Bb–Dm–Eb–Ebm, a minor iv for colour);
//     the reveal IV–V–vi–I; the makeup half ii–V–I–vi; the closing IV–V → I.
//   · Three textures: opening = plucks, a light pulse; explanation = 8th stabs, 8th bass, a 16th "dot" shimmer (from the
//     moment the dots fly); reveal = four on the floor, off-beat open hats, octave bass, the lead. The makeup half adds
//     mallets; the mask part thins to plucks. Half-beat stops before the reveal (22.5) and before the closing unlock (43.75).
//   · The three loudest hits: 2.75 量你, 22.75 高低起伏, 44.0 the closing unlock.
import { createRequire } from "node:module";
import { writeFileSync } from "node:fs";
const require = createRequire(import.meta.url);
const TL = require("../timeline.js");
const { T, DUR, HITS, S16 } = TL;

const SR = 48000, N = Math.ceil(SR * (DUR + 0.6)), TAU = Math.PI * 2, BEAT = 0.5, BAR = 2;
const bus = () => [new Float32Array(N), new Float32Array(N)];
const DRUM = bus(), MUS = bus(), SFX = bus(), SEND = bus();
const duck = new Float32Array(N).fill(1);
const mtof = (m) => 440 * Math.pow(2, (m - 69) / 12);
let seed = 5050505;
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

function beep(t, m, len = 0.11, v = 1, pan = 0) { put(SFX, t, len + 0.02, (tt) => v * 0.2 * (Math.sin(TAU * mtof(m) * tt) + 0.18 * Math.sin(TAU * mtof(m) * 3 * tt)) * Math.min(1, tt / 0.003) * (tt < len ? 1 : Math.max(0, 1 - (tt - len) / 0.02)), { pan, rev: 0.12 }); }
function plink(t, m, v = 1, pan = 0) { put(SFX, t, 0.5, (tt) => { const f = mtof(m) * (1 + 0.5 * Math.exp(-tt * 60)); return v * 0.2 * Math.sin(TAU * f * tt) * Math.exp(-tt * 9) * Math.min(1, tt / 0.002); }, { pan, rev: 0.4 }); }

// ------------------------------------------------------------------ the phone's sounds
function unlockClick(t, v = 1) { click(t, 0.6 * v); put(SFX, t, 0.08, (tt) => v * 0.35 * Math.sin(TAU * 2400 * tt) * Math.exp(-tt * 80), { rev: 0.15 }); put(SFX, t + 0.05, 0.1, (tt) => v * 0.28 * Math.sin(TAU * 3200 * tt) * Math.exp(-tt * 70), { rev: 0.2 }); }
function key(t, v = 1, pan = 0) { put(SFX, t, 0.05, (tt) => v * 0.3 * (Math.sin(TAU * 1500 * tt) + 0.5 * (rnd() * 2 - 1)) * Math.exp(-tt * 140), { pan }); }
function sparkle(t, m, v = 1, pan = 0) { put(SFX, t, 0.18, (tt) => v * 0.12 * Math.sin(TAU * mtof(m) * tt) * Math.exp(-tt * 30) * Math.min(1, tt / 0.001), { pan, rev: 0.45 }); }

// ------------------------------------------------------------------ the harmony: B-flat major (new for the series)
//   opening: I–vi–ii–V (Bb–Gm–Cm7–F); the measuring: the line I–iii–IV–iv (Bb–Dm–Eb–Ebm), a minor iv for the colour;
//   the reveal: IV–V–vi–I (Eb–F–Gm–Bb); the makeup / mask half: ii–V–I–vi with mallets; the closing: IV–V–I.
const CH = { Bb: [53, 58, 62, 65], Gm: [55, 58, 62, 67], Cm7: [51, 55, 58, 63], F: [53, 57, 60, 65], Dm: [53, 57, 62, 65], Eb: [51, 55, 58, 63], Ebm: [51, 54, 58, 63],
  Fsus: [53, 58, 60, 65], Cm: [51, 55, 60, 63], BbD: [50, 53, 58, 62] };
const ROOT = { Bb: 22, Gm: 19, Cm7: 24, F: 17, Dm: 26, Eb: 15, Ebm: 15, Fsus: 17, Cm: 24, BbD: 26 };
const PROG = [[0, "Bb"], [0.75, "Gm"], [1.5, "Cm7"], [2.25, "F"], [T.a2, "Bb"], [4, "Gm"], [T.q3, "Fsus"], [6, "F"],
  [T.a3, "Bb"], [8.75, "Dm"], [9.75, "Eb"], [10.75, "Ebm"], [11.75, "Bb"], [12.75, "Dm"], [13.75, "Eb"], [14.75, "Ebm"],
  [15.75, "Bb"], [16.75, "Dm"], [17.75, "Eb"], [18.75, "Ebm"], [19.75, "Cm"], [20.75, "Eb"], [21.75, "F"],
  [T.a7, "Eb"], [23.75, "F"], [24.25, "Gm"], [24.75, "Bb"],
  [T.q8, "Cm7"], [26.25, "F"], [27.25, "Bb"], [28.25, "Gm"], [29.25, "Cm7"], [30.25, "F"], [T.a9, "Bb"], [32.75, "Gm"],
  [T.q10, "Eb"], [35, "Bb"], [36, "Cm7"], [37, "F"], [38, "Eb"], [39, "Bb"], [40, "Cm7"], [41, "F"], [42, "Gm"], [T.fin, "Eb"], [43.5, "F"],
  [T.ka, "Bb"], [45, "Gm"], [T.tip, "Eb"], [47, "F"], [48, "Bb"], [49, "Gm"], [T.end, "Eb"], [T.sting, "Bb"]];
const chordAt = (t) => { let c = PROG[0][1]; for (const [a, ch] of PROG) if (t >= a - 1e-6) c = ch; return c; };
const SECS = [[0, "hook"], [T.a2, "ans"], [T.q3, "dive"], [T.a3, "path"], [T.q5, "mech"], [T.q6, "build"], [T.stop1, "stop"], [T.a7, "name"],
  [T.q8, "card"], [T.a9, "card2"], [T.q10, "mask"], [T.fin, "build2"], [T.stop, "stop"], [T.ka, "payoff"], [T.tip, "tip"], [T.end, "end"]];
const secAt = (t) => { let s = SECS[0][1]; for (const [t0, n] of SECS) if (t >= t0 - 1e-6) s = n; return s; };
const silent = (t) => (t >= T.stop1 && t < T.a7) || (t >= T.stop && t < T.ka);
const MUF = bus();

// ------------------------------------------------------------------ arrangement
const ARP = [0, 1, 2, 3, 2, 1, 2, 3];
for (let t = 0; t < DUR - 1e-6; t += BEAT) {
  const q = Math.round(t / BEAT) % 4, sec = secAt(t), ch = chordAt(t + 1e-4), root = ROOT[ch], notes = CH[ch];
  if (silent(t)) continue;
  // drums
  if (sec === "hook") { if (q === 0 || q === 2) kick(t, q === 0 ? 0.7 : 0.5); hat(t + BEAT / 2, 0.4); if (t > 0.9) hat(t, 0.2); }
  if (sec === "ans") { if (q === 0 || q === 2) kick(t, 0.7); hat(t + BEAT / 2, 0.45); }
  if (sec === "dive") { const k = Math.max(0, Math.min(1, (t - T.dive) / (T.diveEnd - T.dive))); for (let e = 0; e < 4; e++) hat(t + e * S16, 0.12 + 0.35 * k * (e === 2 ? 1.3 : 1)); if (Math.abs(t - T.flood) < 0.01) kick(t, 0.6); }
  if (sec === "path" || sec === "mech") { if (q === 0 || q === 2) kick(t, 0.7); if (q === 3) rim(t + BEAT / 2, 0.5); for (let e = 0; e < 4; e++) hat(t + e * S16, e === 2 ? 0.42 : 0.18); }
  if (sec === "build" || sec === "build2") { if (q === 0 || q === 2) kick(t, 0.65); for (let e = 0; e < 4; e++) { const tt = t + e * S16, a0 = sec === "build" ? T.q6 : T.fin, a1 = sec === "build" ? T.stop1 : T.stop; if (!silent(tt)) { const k = (tt - a0) / (a1 - a0); hat(tt, 0.15 + 0.3 * k); snare(tt, 0.06 + 0.3 * k * k); } } }
  if (sec === "name" || sec === "payoff") { const after = (sec === "name" ? t - T.a7 : t - T.ka) >= 0.5 ? 0.78 : 1; kick(t, (q === 0 ? 1 : 0.85) * after); if (q === 1 || q === 3) clap(t, 0.75 * after); for (let e = 0; e < 4; e++) { if (e === 2) hat(t + e * S16, 0.75, true, 0.2); else hat(t + e * S16, e % 2 ? 0.4 : 0.22); } }
  if (sec === "card" || sec === "card2") { if (q === 0) kick(t, 0.6); if (q === 2) rim(t, 0.45); hat(t + BEAT / 2, 0.32); hat(t, 0.15); }
  if (sec === "mask") { if (q === 0) kick(t, 0.5); hat(t + BEAT / 2, 0.28); if (q === 2) rim(t, 0.3); }
  if (sec === "tip") { if (q === 0) kick(t, 0.5); hat(t + BEAT / 2, 0.3); }
  // bass
  if (sec === "hook") bass(t, root + 12, BEAT * 0.8, 0.55);
  if (sec === "ans") { bass(t, root + 12, BEAT * 0.2, 0.7); bass(t + BEAT / 2, root + 24, BEAT * 0.35, 0.8); }
  if (sec === "dive" && q === 0) bass(t, root + 12, BEAT * 3.6, 0.45);
  if (sec === "path" || sec === "mech") { const pat = [0, 0, 12, 0]; for (let e = 0; e < 2; e++) { const k = (q * 2 + e) % 4, tt = t + e * BEAT / 2; bass(tt, ROOT[chordAt(tt + 1e-4)] + 12 + pat[k], BEAT * 0.3, 0.78); } }
  if (sec === "build" || sec === "build2") bass(t, root + 12, BEAT * 0.3, 0.7);
  if (sec === "name" || sec === "payoff") { bass(t, root + 12, BEAT * 0.18, 0.75); bass(t + BEAT / 2, root + 24, BEAT * 0.4, 0.9); }
  if ((sec === "card" || sec === "card2") && (q === 0 || q === 2)) bass(t, root + 12, BEAT * 1.7, 0.55);
  if ((sec === "mask" || sec === "tip") && q === 0) bass(t, root + 12, BEAT * 3.6, 0.45);
  if (sec === "end" && Math.abs(t - T.sting) < 1e-6) bass(t, 22 + 12, BEAT * 3, 0.6);
  // the measuring: 8th stabs, and a 16th "dot" shimmer two octaves up (the dots)
  if (sec === "path" || sec === "mech") { for (let e = 0; e < 2; e++) { const tt = t + e * BEAT / 2; stab(tt, CH[chordAt(tt + 1e-4)].map((m) => m + 12), 0.16, e ? 0.55 : 0.75, 0.45); }
    const nn = notes.map((m) => m + 24); for (let e = 0; e < 4; e++) { const tt = t + e * S16; if (tt < T.fire) continue; pluck(tt, nn[ARP[(q * 4 + e) % 8]], e === 0 ? 0.42 : 0.3, e % 2 ? 0.35 : -0.35); } }
  // the opening: 8th plucks under the question
  if (sec === "hook") { const nn = notes.map((m) => m + 12); for (let e = 0; e < 2; e++) pluck(t + e * BEAT / 2, nn[(q * 2 + e + 1) % 4], 0.28, e ? 0.3 : -0.3); }
  // reveal: off-beat bright stabs and a 16th arp
  if (sec === "name" || sec === "payoff") { stab(t + BEAT / 2, notes.map((m) => m + 12), 0.2, 0.8, 1.2); const nn = notes.map((m) => m + 24); for (let e = 0; e < 4; e++) pluck(t + e * S16, nn[ARP[(q * 4 + e) % 8]], e === 0 ? 0.5 : 0.36, e % 2 ? 0.3 : -0.3); }
  // the makeup half: mallet arpeggios (a new colour); the mask: sparser plucks
  if (sec === "card" || sec === "card2") { const nn = notes.map((m) => m + 12); for (let e = 0; e < 2; e++) mallet(t + e * BEAT / 2, nn[ARP[(q * 2 + e) % 8]] + (e ? 12 : 0), 0.42, e ? 0.25 : -0.25); }
  if (sec === "mask" || sec === "tip") { const nn = notes.map((m) => m + 24); for (let e = 0; e < 2; e++) pluck(t + e * BEAT / 2, nn[(q * 2 + e) % 4], 0.3, e ? 0.3 : -0.3); }
}
// pads, by chord span and section
{
  const cuts = [...new Set([...PROG.map(([a]) => a), ...SECS.map(([a]) => a), DUR])].sort((a, b) => a - b);
  for (let k = 0; k + 1 < cuts.length; k++) {
    const a = cuts[k], z = Math.min(cuts[k + 1], DUR), sec = secAt(a + 1e-4), notes = CH[chordAt(a + 1e-4)].map((m) => m + 12), len = z - a - 0.04;
    if (len < 0.2 || silent(a + 1e-4)) continue;
    const V = { hook: [0.5, 1300], ans: [0.6, 1100], dive: [1.0, 700], path: [0.6, 1000], mech: [0.55, 1000], build: [0.7, 1400], name: [0.8, 1600],
      card: [0.55, 1300], card2: [0.6, 1400], mask: [0.9, 1100], build2: [0.7, 1400], payoff: [0.85, 1800], tip: [0.75, 1300], end: [1.0, 1500] }[sec];
    if (V) pad(a, notes, len, V[0], V[1]);
  }
}
// ---- melodies grown from the motif: mi-sol-la (D–F–G); the answer mi-sol-DO (D–F–Bb)
const play = (t0, notes, v = 0.9, br = 1) => notes.forEach(([s, m, d]) => lead(t0 + s * S16, m, d * S16 * 0.92, v, br));
[[0, 86], [1, 89], [2, 91]].forEach(([i, m]) => sparkle(T.scan + i * S16, m, 0.9, 0.15));                       // the hook, as the scan
play(T.a7, [[0, 86, 2], [2, 89, 2], [4, 94, 6], [10, 93, 2], [12, 91, 2], [14, 89, 2]], 0.95, 1.1);              // the reveal: mi-sol-DO, then down
play(T.a7 + 1.0, [[0, 89, 2], [2, 86, 2], [4, 82, 4]], 0.8, 1.0);
play(T.ka, [[0, 86, 2], [2, 89, 2], [4, 94, 8], [12, 96, 2], [14, 94, 2]], 0.95, 1.1);                         // the closing unlock
play(T.ka + 1.0, [[0, 93, 2], [2, 89, 2], [4, 86, 4], [8, 89, 6]], 0.85, 1.0);
[[0, 86], [2, 89], [4, 94], [6, 93], [8, 89]].forEach(([s, m]) => mallet(T.tip + 0.5 + s * S16, m, 0.6, 0.15));
[[0, 86], [2, 89], [4, 94, 12]].forEach(([s, m, d]) => lead(T.sting - 0.5 + s * S16, m, (d || 2) * S16 * 0.92, 0.85, 0.9));   // the last word: mi-sol-DO

// ------------------------------------------------------------------ sound effects on picture events
const ask = (t) => { blip(t, 89, 0.55, -0.15); blip(t + 0.125, 94, 0.6, 0.15); };      // every question: the same rising 4th (F6 → Bb6)
[T.q3, T.q4, T.q5, T.q6, T.q8, T.q9, T.q10, T.q11].forEach(ask);
// 1 the phenomenon: the lipstick's soft stroke; the phone comes up; the scan (the hook); the lock opens
glide(T.stroke + 0.05, 0.6, 74, 79, 0.35, -0.2); glide(T.rise, T.riseEnd - T.rise, 67, 79, 0.45, 0.3);
unlockClick(T.ka0, 0.9); blip(T.underline, 89, 0.7); blip(T.underline + 0.125, 94, 0.5);
// 2 the fact (one of the three loudest hits): it measures you
impact(T.a2, 1.4); stab(T.a2, [46, 53, 58, 62, 65], 0.6, 1.05, 1.3); glide(T.toTop, T.toTopEnd - T.toTop, 72, 84, 0.4, 0.2);
for (let i = 0; i < 4; i++) sparkle(T.glow + i * 0.25, 94 + (i % 2) * 3, 0.5, 0.2);
// the dive: a riser; the dark; the two parts light up
riser(T.dive, T.flood - T.dive + 0.1, 0.75); glide(T.dive, 1.0, 60, 77, 0.6, 0.1); bloom(T.flood, [70, 74, 77], 0.6);
HITS.parts.forEach((t, i) => { blip(t, [86, 82][i], 0.5, i ? -0.3 : 0.3); tick(t, 0.3, 0, 3000); });
// the dots: a spray of tiny sparkles (seeded), as they fly
{ let s = 0; for (let i = 0; i < 40; i++) { s = (s * 9301 + 49297) % 233280; const r = s / 233280; sparkle(T.fire + 0.02 * i + 0.01 * r, [86, 89, 91, 94, 98][i % 5], 0.35 + 0.2 * r, (r - 0.5) * 0.8); } }
glide(T.iso, T.isoEnd - T.iso, 70, 86, 0.45, 0);                                      // the lines of equal height sweep
// the top view: the beam, the wall point, the nose point, the shift; three beams
glide(T.beam, 0.4, 82, 94, 0.4, 0.3); tick(T.wall, 0.5, -0.2, 3000); tick(T.nose, 0.5, 0.2, 3400); glide(T.shift, 0.4, 86, 79, 0.45, -0.3);
HITS.beams.forEach((t, i) => { blip(t, [94, 89, 86][i], 0.55, -0.2 + 0.2 * i); });
// the depth map grows; the reveal (after a half-beat stop); the IR photo; the compare; the tick
riser(T.q6 + 0.25, T.stop1 - T.q6 - 0.25, 0.5);
impact(T.a7, 1.7); stab(T.a7, [51, 58, 63, 67, 70], 0.8, 1.15, 1.25); bloom(T.a7 + 0.25, [94, 98, 101], 0.7);
tick(T.irPhoto, 0.35, 0.3, 2800); glide(T.compare, 0.6, 79, 72, 0.2, 0); blip(T.match1, 94, 0.35, 0); blip(T.match1 + 0.125, 98, 0.3, 0);
// the makeup: three soft brush strokes; the cards; 略变; the contour; the profile line: the same
HITS.makeup.forEach((t, i) => glide(t, 0.4, 79 + 3 * i, 84 + 3 * i, 0.3, -0.3 + 0.3 * i));
tick(T.cards, 0.45, 0.3, 2800); tick(T.cards + 0.25, 0.4, 0.35, 3000); blip(T.irTag, 86, 0.45, 0.3);
HITS.contour.forEach((t) => glide(t, 0.4, 77, 82, 0.28, -0.2));
bloom(T.a9, [82, 86, 89], 0.35); glide(T.prof, T.profEnd - T.prof, 82, 89, 0.45, 0.3);
// the mask goes on; to the data; the eye ring; the swing; the match
glide(T.mask, T.maskEnd - T.mask, 67, 79, 0.45, 0); bloom(T.toDepth, [74, 77, 82], 0.4);
blip(T.ring, 94, 0.55, 0.2); blip(T.ring + 0.125, 98, 0.45, 0.2); glide(T.swing, 1.0, 82, 86, 0.25, -0.3); glide(T.swing + 1.0, 1.0, 86, 82, 0.25, 0.3);
blip(T.match2, 94, 0.6, -0.2); blip(T.match2 + 0.125, 98, 0.5, -0.2);
// back to the start: half a beat of nothing; the lock opens (loudest hit): the hook resolves (mi-sol-DO)
riser(T.fin + 0.25, T.stop - T.fin - 0.25, 0.45);
unlockClick(T.ka, 1.2); impact(T.ka, 1.35); stab(T.ka, [46, 53, 58, 62, 65], 0.5, 1, 1.25);
[[0, 86], [1, 89], [2, 94]].forEach(([i, m]) => sparkle(T.ka + i * S16, m, 0.9, 0.1));
// the tip: not recognised (a low double buzz); the passcode keys; it opens
bloom(T.tip, [70, 74, 77], 0.4); buzz(T.miss, 0.12, 0.45); buzz(T.miss + 0.16, 0.12, 0.4);
HITS.keys.forEach((t, i) => key(t, 0.7, -0.2 + 0.08 * i)); unlockClick(T.open2, 0.8);
{ let k = 0; TL.COPY.end.forEach((s, li) => { const n = s.replace(/[\[\]]/g, "").length; for (let j = 0; j < n; j++) tick(T.title1 + li * 0.3 + j * 0.045, 0.45, -0.2 + 0.05 * (k++ % 8), 2600 + (j % 3) * 300); }); }
blip(T.ep, 94, 0.6);
impact(T.sting, 0.55); stab(T.sting, [46, 53, 58, 62, 65], 1.6, 0.8, 0.9); bloom(T.sting, [94, 98, 101, 106], 1.0);

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
for (const [a] of [[T.stop1], [T.stop]]) {          // soften the gate edges so the stops do not click
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
// the loudest moments (10 ms peak within 120 ms of each hit): the ✕ / the name / the closing step must be on top
{ const pk = (t) => { let m = 0; for (let n = Math.floor(t * SR); n < Math.floor((t + 0.12) * SR); n++) m = Math.max(m, Math.abs(L[n]), Math.abs(R[n])); return +(20 * Math.log10(m * g + 1e-9)).toFixed(1); };
  const rms = (a, b) => { let e = 0; for (let n = Math.floor(a * SR); n < Math.floor(b * SR); n++) e += L[n] * L[n]; return (10 * Math.log10(e * g * g / ((b - a) * SR) + 1e-12)).toFixed(1); };
  const top3 = { current: pk(T.a2), name: pk(T.a7), close: pk(T.ka) };
  let others = -99, at = 0; for (let t = 0; t < DUR - 0.2; t += 0.125) { if ([T.a2, T.a7, T.ka].some((h) => Math.abs(t - h) < 0.3)) continue; const p = pk(t); if (p > others) { others = p; at = t; } }
  console.log(`peaks dBFS: 量你 ${top3.current}, name ${top3.name}, closing step ${top3.close}; loudest other ${others} at ${at.toFixed(2)} s; sting ${pk(T.sting)}`);
  console.log(`rms dB: hook ${rms(0.1, 2.7)}, fact ${rms(2.8, 5.2)}, measure ${rms(T.a3, T.q6)}, reveal ${rms(T.a7 + 0.2, T.q8 - 0.2)}, makeup ${rms(T.q8, T.q10)}, mask ${rms(T.q10, T.fin)}, payoff ${rms(T.ka + 0.2, T.tip - 0.2)}, tip ${rms(T.tip + 0.5, T.tipOut)}`); }
console.log(`score-${STYLE}.wav: ${DUR} s @ ${SR} Hz, mix peak ${peak.toFixed(2)} -> normalised`);
