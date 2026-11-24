// music/score.mjs — the original score + every sound effect, synthesized from scratch (no samples) and locked to
// ../timeline.js, so each hit lands on its frame.
//   node music/score.mjs   ->  music/score-C.wav (48 kHz stereo, peak-normalised; loudness is set in the mix step)
// EP.10 实况照片 — same sound as the series (the same synths and drum kit, 120 BPM straight 16ths, the question cue, the hook
// mi-sol-la → mi-sol-DO), a new piece:
//   · A-flat major (new for the series: EP.01/03 C, EP.02 G, EP.04 D, EP.05 F, EP.06 B-flat, EP.07 A, EP.08 E-flat, EP.09 E).
//     The hook is the photo's chime: mi-sol-la (C6 E♭6 F6) when the photo opens; on the closing line it resolves: mi-sol-DO.
//   · Progressions (new): opening I–V–vi–IV (A♭–E♭–Fm–D♭); the explanation IV–I–V–vi (D♭–A♭–E♭–Fm) with ii (B♭m) before
//     questions and a minor iv (D♭m) under 转一圈就没了; the press in a darker colour (B♭m–E♭–Cm–Fm–D♭–E♭); reveals on I.
//   · Three textures: opening = shutter + 8th plucks; explanation = soft 8th stabs, a 16th shimmer while frames flow, one pluck
//     per frame written into the ring; reveal = four on the floor, off-beat open hats, octave bass, the lead. Tip = mallets.
//     True silence 0.5 s before ✕; half-beat stops before 实况照片 and before the closing line.
//     The three loudest hits: 4.0 ✕, 28.75 实况照片 (the name), 33.5 the closing line.
import { createRequire } from "node:module";
import { writeFileSync } from "node:fs";
const require = createRequire(import.meta.url);
const TL = require("../timeline.js");
const { T, DUR, HITS, S16 } = TL;

const SR = 48000, N = Math.ceil(SR * (DUR + 0.6)), TAU = Math.PI * 2, BEAT = 0.5, BAR = 2;
const bus = () => [new Float32Array(N), new Float32Array(N)];
const DRUM = bus(), MUS = bus(), SFX = bus(), SEND = bus(), MUF = bus();
const duck = new Float32Array(N).fill(1);
const mtof = (m) => 440 * Math.pow(2, (m - 69) / 12);
let seed = 10101010;
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


// the camera shutter: a mechanical-sounding double click (synthesised); the firework: a soft low boom and a few crackles
function shutter(t, v = 1) { click(t, 0.8 * v); put(SFX, t, 0.05, (tt) => v * 0.28 * Math.sin(TAU * 2400 * tt) * Math.exp(-tt * 120), { rev: 0.12 }); click(t + 0.055, 0.55 * v); tap(t + 0.055, 0.35 * v, 170); }
function boom(t, v = 1) {
  put(SFX, t, 0.9, (tt) => v * 0.5 * Math.sin(TAU * (48 * tt + (30 * (1 - Math.exp(-tt * 9))) / 9)) * Math.exp(-tt * 4.5) * Math.min(1, tt / 0.004), { rev: 0.35 });
  [0.18, 0.27, 0.33, 0.46, 0.52, 0.61, 0.74].forEach((d, i) => tick(t + d, 0.16 * v * (1 - i * 0.1), (i % 2 ? 0.3 : -0.3), 3600 + 400 * (i % 3)));
}

// ------------------------------------------------------------------ the harmony (A-flat major)
const CH = { Ab: [51, 56, 60, 63], Db: [53, 56, 61, 65], Eb: [51, 55, 58, 63], Fm: [53, 56, 60, 65], Cm: [51, 55, 60, 63], Bbm: [53, 58, 61, 65], Ebsus: [51, 56, 58, 63], Dbm: [52, 56, 61, 64] };
const ROOT = { Ab: 32, Db: 25, Eb: 27, Fm: 29, Cm: 24, Bbm: 34, Ebsus: 27, Dbm: 25 };
const PROG = [[0, "Ab"], [0.75, "Eb"], [1.5, "Fm"], [2.25, "Db"],                  // the opening: I–V–vi–IV
  [T.q2, "Fm"], [3.25, "Db"], [T.strike, "Fm"], [T.a2, "Ab"], [5.75, "Eb"],
  [T.q3, "Fm"], [7.75, "Db"], [8.5, "Bbm"], [9.0, "Eb"]];
{ const cyc = ["Db", "Ab", "Eb", "Fm"]; let i = 0; for (let t = T.h4; t < T.q7 - 1e-6; t += 1) { let c = cyc[i++ % 4]; if (Math.abs(t - 13.5) < 0.01 || Math.abs(t - 20.5) < 0.01) c = "Bbm"; PROG.push([t, c]); } }   // the explanation: IV–I–V–vi, ii before the questions
PROG.push([T.a6, "Db"], [19.0, "Dbm"], [19.5, "Ab"], [20.0, "Eb"]);                // 转一圈就没了: a minor iv
PROG.push([T.q7, "Bbm"], [21.75, "Eb"], [T.a7, "Cm"], [23.75, "Fm"], [T.q8, "Db"], [25.75, "Eb"], [T.a8, "Cm"], [27.25, "Fm"], [27.75, "Ebsus"],
  [T.a9, "Ab"], [29.75, "Eb"], [30.25, "Fm"], [30.75, "Db"],
  [T.q10, "Db"], [32.0, "Ab"], [32.5, "Ebsus"],
  [T.fin, "Ab"], [34.5, "Cm"], [35.25, "Db"], [35.75, "Eb"]);
{ const cyc = ["Db", "Ab", "Bbm", "Eb"]; let i = 0; for (let t = T.tip; t < T.end - 1e-6; t += 1) PROG.push([t, cyc[i++ % 4]]); }
PROG.push([T.end, "Ab"]);
PROG.sort((a, b) => a[0] - b[0]);
const chordAt = (t) => { let c = PROG[0][1]; for (const [a, ch] of PROG) if (t >= a - 1e-6) c = ch; return c; };
const SECS = [[0, "hook"], [T.q2, "myth"], [T.a2, "ans"], [T.q3, "dive"], [T.h4, "mech"], [T.q7, "press"], [T.a9, "name"], [T.q10, "back"], [T.fin, "payoff"], [T.tip, "tip"], [T.end, "end"]];
const secAt = (t) => { let s = SECS[0][1]; for (const [t0, n] of SECS) if (t >= t0 - 1e-6) s = n; return s; };
const STOPS = [[T.hush, T.strike], [T.stop1, T.a9], [T.stop2, T.fin]];
const silent = (t) => STOPS.some(([a, b]) => t >= a && t < b);
// the ring writes a frame every ¼ s of sky time (inside: 4×slow during the press): one pluck per write
const writes = []; { for (let n = 0; ; n++) { const t = TL.writeT(n); if (t >= T.collapse) break; if (t >= T.write0) writes.push(t); } }   // v3: the ring stops for the overwrite (timeline.js RING.hold)
const flowing = (t) => t >= T.flow && t < T.ringForm;

// ------------------------------------------------------------------ arrangement
const ARP = [0, 1, 2, 3, 2, 1, 2, 3];
for (let t = 0; t < DUR - 1e-6; t += BEAT) {
  const q = Math.round(t / BEAT) % 4, sec = secAt(t), ch = chordAt(t + 1e-4), root = ROOT[ch], notes = CH[ch];
  if (silent(t)) continue;
  if (sec === "hook") { if (q === 0) kick(t, 0.55); hat(t + BEAT / 2, 0.35); if (t > 0.9) hat(t, 0.16); }
  if (sec === "myth") { if (q === 0) kick(t, 0.5); if (q === 2) rim(t, 0.35); hat(t + BEAT / 2, 0.25); }
  if (sec === "ans") { if (q === 0 || q === 2) kick(t, 0.7); hat(t + BEAT / 2, 0.45); }
  if (sec === "dive") { const k = Math.min(1, (t - T.q3) / 2.5); for (let e = 0; e < 4; e++) hat(t + e * S16, 0.08 + 0.25 * k * (e === 2 ? 1.3 : 1)); if (q === 0) kick(t, 0.35 + 0.3 * k); }
  if (sec === "mech") { if (q === 0) kick(t, 0.45); if (q === 3) rim(t + BEAT / 2, 0.4); for (let e = 0; e < 4; e++) { const tt = t + e * S16; if (!silent(tt)) hat(tt, e === 2 ? 0.32 : 0.12); } }
  if (sec === "press") { if (q === 0 || q === 2) kick(t, 0.5); if (q === 1 || q === 3) snare(t, 0.28); hat(t + BEAT / 2, 0.3); }
  if (sec === "name" || sec === "payoff") { kick(t, q === 0 ? 1 : 0.85); if (q === 1 || q === 3) clap(t, 0.75); for (let e = 0; e < 4; e++) { if (e === 2) hat(t + e * S16, 0.75, true, 0.2); else hat(t + e * S16, e % 2 ? 0.4 : 0.22); } }
  if (sec === "back") { if (q === 0) kick(t, 0.5); hat(t + BEAT / 2, 0.3); }
  if (sec === "tip") { if (q === 0) kick(t, 0.45); hat(t + BEAT / 2, 0.28); }
  // bass
  if ((sec === "hook" || sec === "myth" || sec === "back") && (q === 0 || q === 2)) bass(t, root + 12, BEAT * 1.7, 0.55);
  if (sec === "ans") { bass(t, root + 12, BEAT * 0.2, 0.7); bass(t + BEAT / 2, root + 24, BEAT * 0.35, 0.8); }
  if (sec === "dive" && q === 0) bass(t, root + 12, BEAT * 3.6, 0.45);
  if (sec === "mech" || sec === "press") for (let e = 0; e < 2; e++) { const tt = t + e * BEAT / 2; if (!silent(tt)) bass(tt, ROOT[chordAt(tt + 1e-4)] + 12 + (e ? 12 : 0), BEAT * 0.3, sec === "press" ? 0.65 : 0.6); }
  if (sec === "name" || sec === "payoff") { bass(t, root + 12, BEAT * 0.18, 0.75); bass(t + BEAT / 2, root + 24, BEAT * 0.4, 0.9); }
  if (sec === "tip" && q === 0) bass(t, root + 12, BEAT * 3.6, 0.45);
  if (sec === "end" && Math.abs(t - T.sting) < 1e-6) bass(t, 32 + 12, BEAT * 3, 0.6);
  // the opening, the guess and the way back: 8th plucks
  if (sec === "hook" || sec === "myth" || sec === "back") { const nn = notes.map((m) => m + 12); for (let e = 0; e < 2; e++) { const tt = t + e * BEAT / 2; if (!silent(tt)) pluck(tt, nn[(q * 2 + e + 1) % 4], sec === "myth" ? 0.22 : 0.28, e ? 0.3 : -0.3); } }
  // the explanation and the press: soft 8th stabs (darker for the press)
  if (sec === "mech" || sec === "press") for (let e = 0; e < 2; e++) { const tt = t + e * BEAT / 2; if (!silent(tt)) stab(tt, CH[chordAt(tt + 1e-4)].map((m) => m + 12), 0.15, e ? 0.45 : 0.62, sec === "press" ? 0.28 : 0.35); }
  // while frames flow up into the screen: a 16th shimmer
  if (sec === "mech") { const nn = notes.map((m) => m + 24); for (let e = 0; e < 4; e++) { const tt = t + e * S16; if (silent(tt) || !flowing(tt)) continue; pluck(tt, nn[ARP[(q * 4 + e) % 8]], e === 0 ? 0.3 : 0.2, e % 2 ? 0.35 : -0.35); } }
  // reveal: off-beat bright stabs and a 16th arp
  if (sec === "name" || sec === "payoff") { stab(t + BEAT / 2, notes.map((m) => m + 12), 0.2, 0.8, 1.2); const nn = notes.map((m) => m + 24); for (let e = 0; e < 4; e++) pluck(t + e * S16, nn[ARP[(q * 4 + e) % 8]], e === 0 ? 0.5 : 0.36, e % 2 ? 0.3 : -0.3); }
  // the tip: mallet arpeggios
  if (sec === "tip") { const nn = notes.map((m) => m + 12); for (let e = 0; e < 2; e++) { const tt = t + e * BEAT / 2; if (!silent(tt)) mallet(tt, nn[ARP[(q * 2 + e) % 8]] + (e ? 12 : 0), 0.4, e ? 0.25 : -0.25); } }
}
// one pluck per frame written into the ring (it goes round: the pitch walks round the chord)
writes.forEach((t, i) => { if (silent(t)) return; const nn = CH[chordAt(t + 1e-4)].map((m) => m + 24); pluck(t, nn[i % 4], 0.3, (i % 2 ? 0.3 : -0.3)); });
// pads, by chord span and section
{
  const cuts = [...new Set([...PROG.map(([a]) => a), ...SECS.map(([a]) => a), ...STOPS.flat(), DUR])].sort((a, b) => a - b);
  for (let k = 0; k + 1 < cuts.length; k++) {
    const a = cuts[k], z = Math.min(cuts[k + 1], DUR), sec = secAt(a + 1e-4), notes = CH[chordAt(a + 1e-4)].map((m) => m + 12), len = z - a - 0.04;
    if (len < 0.2 || silent(a + 1e-4)) continue;
    const V = { hook: [0.5, 1300], myth: [0.7, 900], ans: [0.6, 1100], dive: [1.0, 700], mech: [0.65, 1000], press: [0.75, 900], name: [0.8, 1600],
      back: [0.7, 1100], payoff: [0.85, 1800], tip: [0.75, 1300], end: [1.0, 1500] }[sec];
    if (V) pad(a, notes, len, V[0], V[1]);
  }
}
// ---- melodies grown from the motif (C–E♭–F = mi-sol-la; the answer C–E♭–A♭ = mi-sol-DO)
const play = (t0, notes, v = 0.9, br = 1) => notes.forEach(([s, m, d]) => lead(t0 + s * S16, m, d * S16 * 0.92, v, br));
[[0, 84], [1, 87], [2, 89]].forEach(([i, m]) => ringNote(T.open0 + i * S16, m, 0.9));                             // the photo opens: mi-sol-la
play(T.a9, [[0, 72, 2], [2, 75, 2], [4, 80, 6], [10, 79, 2], [12, 77, 2], [14, 75, 2]], 0.95, 1.1);            // 实况照片: mi-sol-DO, then down
play(T.a9 + 1.0, [[0, 77, 2], [2, 75, 2], [4, 72, 4]], 0.8, 1.0);
play(T.a9 + 2.0, [[0, 73, 2], [2, 72, 2], [4, 70, 4], [8, 72, 4]], 0.7, 0.9);
play(T.fin, [[0, 72, 2], [2, 75, 2], [4, 80, 8], [12, 82, 2], [14, 80, 2]], 0.95, 1.1);                            // the closing line
play(T.fin + 1.0, [[0, 79, 2], [2, 75, 2], [4, 72, 4], [8, 75, 6]], 0.85, 1.0);
play(T.fin + 2.0, [[0, 77, 2], [2, 80, 2], [4, 77, 4], [8, 75, 2], [10, 72, 2]], 0.75, 0.9);
[[0, 84, 2], [2, 87, 2], [4, 92, 12]].forEach(([s, m, d]) => ringNote(T.fin + 0.25 + s * S16, m, 0.7));            // the chime resolves: mi-sol-DO
[[0, 72], [2, 75], [4, 77], [6, 75], [8, 72]].forEach(([s, m]) => mallet(T.tip + 0.5 + s * S16, m, 0.55, 0.15));
[[0, 73], [2, 77], [4, 80], [6, 77], [10, 75]].forEach(([s, m]) => mallet(T.tip + 2 + s * S16, m, 0.5, -0.15));
[[0, 68, 2], [2, 72, 2], [4, 80, 12]].forEach(([s, m, d]) => lead(T.sting - 0.5 + s * S16, m, d * S16 * 0.92, 0.85, 0.9));

// ------------------------------------------------------------------ sound effects on picture events
const ask = (t) => { blip(t, 75, 0.55, -0.15); blip(t + 0.125, 80, 0.6, 0.15); };       // every question: the same rising 4th (E♭5 → A♭5)
[T.q3, T.q5, T.q7, T.q10].forEach(ask);
// 1 the opening: the shutter after the burst; the photo opens and plays (its burst)
shutter(T.tap0, 1); boom(T.underline, 0.55);
blip(T.underline, 80, 0.5); blip(T.underline + 0.125, 84, 0.4);
// 2 the guess: frames grow to the right; true silence; ✕ (one of the three loudest); the flip: frames to the left too
for (let i = 0; i < 6; i++) tick(T.stripR + i * 0.15, 0.35, 0.3, 2800 + i * 120);
impact(T.strike, 1.4); stab(T.strike, [53, 60, 65, 68, 72], 0.6, 1.05, 1.3);
softImpact(T.a2, 0.6); for (let i = 0; i < 6; i++) tick(T.stripL + i * 0.12, 0.35, -0.3, 2800 + i * 120);
// 3 the dive
riser(T.q3 + 0.25, T.diveEnd - T.q3 - 0.25, 0.7); glide(T.xray, 0.5, 70, 79, 0.4, 0.1); glide(T.lay, 1.2, 72, 87, 0.45, -0.1);
// 4 the viewfinder on; its burst; the chip; the pile; the ring
glide(T.vfOn, 0.3, 75, 82, 0.35, 0.2); boom(7.5, 0.3); boom(10.0, 0.4);
blip(T.chipOn, 84, 0.5, -0.3); blip(T.chipOn + 0.08, 87, 0.4, -0.3);
boom(12.75, 0.3); boom(14.85, 0.3); riser(T.pile, T.pileEnd - T.pile, 0.45);
blip(15.12, 87, 0.45, 0.3); tick(15.65, 0.55, 0.3, 2300);   // v3: the bright frame leaves the chip, lands on the pile
glide(T.ringForm, 0.9, 82, 75, 0.4, 0); bloom(T.ringFormEnd, [75, 80, 84], 0.45); boom(18.0, 0.28);
creak(TL.RING.hold.in1 - 0.05, 0.5); tick(TL.RING.hold.in1, 0.5, 0, 2000);   // v3: the new frame covers the old one at the head
// 5 the press: the shutter; each copy a rising tick; 实况 boxed; the sharp photo
shutter(T.tap, 0.8); boom(19.8, 0.3);
TL.COPYB_T.forEach((t, i) => tick(t, 0.45, -0.3, 2600 + i * 180));
blip(T.liveBox, 84, 0.45, 0.3);
TL.COPYA_T.forEach((t, i) => tick(t, 0.45, 0.3, 2600 + i * 180));
snapSfx(T.key, 0.85);
// 6 实况照片 (after the half-beat stop; one of the three loudest); its burst
impact(T.a9, 1.35); stab(T.a9, [51, 56, 60, 63, 68], 0.6, 1, 1.2); boom(29.75, 0.45);
// 7 back to the first shot; the shutter; the closing line (one of the three loudest) with the screen's 咔
swish(T.iris, 0.5, 0.6, 0); shutter(T.tapC, 0.9);
impact(T.fin, 1.35); stab(T.fin, [51, 56, 60, 63, 68], 0.5, 1, 1.25); click(T.fin, 0.8); boom(34.0, 0.45);
// 8 the tip: the edit view; the selector slides; set as cover
glide(T.tipIn, T.tipInEnd - T.tipIn, 72, 79, 0.4, 0.2);
glide(T.slide, T.slideEnd - T.slide, 79, 72, 0.35, -0.2); snapSfx(T.slideEnd, 0.6); blip(T.slideEnd + 0.125, 84, 0.45);
{ let k = 0; TL.COPY.end.forEach((s, li) => { const n = s.replace(/[\[\]]/g, "").length; for (let j = 0; j < n; j++) tick(T.title1 + li * 0.3 + j * 0.045, 0.45, -0.2 + 0.05 * (k++ % 8), 2600 + (j % 3) * 300); }); }
blip(T.ep, 80, 0.6);
impact(T.sting, 0.55); stab(T.sting, [51, 56, 60, 63, 68], 1.6, 0.8, 0.9); bloom(T.sting, [80, 84, 87, 92], 1.0);

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
  const top = [T.strike, T.a9, T.fin];
  let others = -99, at = 0; for (let t = 0; t < DUR - 0.2; t += 0.125) { if (top.some((h) => Math.abs(t - h) < 0.3)) continue; const p = pk(t); if (p > others) { others = p; at = t; } }
  console.log(`peaks dBFS: ✕ ${pk(T.strike)}, 实况照片 ${pk(T.a9)}, closing ${pk(T.fin)}; loudest other ${others} at ${at.toFixed(2)} s; sting ${pk(T.sting)}`); }
console.log(`score-${STYLE}.wav: ${DUR} s @ ${SR} Hz, mix peak ${peak.toFixed(2)} -> normalised`);
