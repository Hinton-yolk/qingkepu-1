// music/score.mjs — the original score + every sound effect, synthesized from scratch (no samples) and locked to
// ../timeline.js, so each hit lands on its frame.
//   node music/score.mjs   ->  music/score-C.wav (48 kHz stereo, peak-normalised; loudness is set in the mix step)
// EP.04 触摸屏 — same sound as the series (the same synths, drums, 120 BPM straight 16ths, the question cue, the hook
// mi-sol-la → mi-sol-DO), a new piece:
//   · D major. The ringtone IS the hook: mi-sol-la-sol-mi-sol (F#5 A5 B5 A5 F#5 A5) in 16ths, once a second while the phone
//     vibrates; the vibration motor buzzes on D3 (146.8 Hz). Answering the call (咔) resolves it: mi-sol-DO (F#5 A5 D6).
//   · Progression: opening IV–V (G–A) and a deceptive vi (Bm) on the guess; the explanation climbs the circle
//     vi–ii–V–iii–IV–V (Bm–Em–A–F#m–G–A) and only lands on I (D) on the name. (EP.01/03: IV–V–iii–vi in C;
//     EP.02: vi–IV–I–V in G; EP.04 v1: IV–I–V–vi in A.)
//   · Three textures: opening = the ringtone + a light kick/hat pulse and a held sub; explanation = pulsing 8th stabs, an
//     8th bass ostinato and a 16th "current" shimmer (muffled, low-passed, while the glove is on); reveal = four on the
//     floor, off-beat open hats, octave bass and the lead. Half-beat stop before the name and before the 咔.
//   · The three loudest hits: the ✕, the name, the 咔. 0.5 s of true silence before the ✕.
import { createRequire } from "node:module";
import { writeFileSync } from "node:fs";
const require = createRequire(import.meta.url);
const TL = require("../timeline.js");
const { T, DUR, HITS, buzzK, buzzVis } = TL;

const SR = 48000, N = Math.ceil(SR * (DUR + 0.6)), TAU = Math.PI * 2, BEAT = 0.5, BAR = 2, S16 = BEAT / 4;
const bus = () => [new Float32Array(N), new Float32Array(N)];
const DRUM = bus(), MUS = bus(), SFX = bus(), SEND = bus(), MUF = bus();
const duck = new Float32Array(N).fill(1);
const mtof = (m) => 440 * Math.pow(2, (m - 69) / 12);
let seed = 4040404;
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

// ------------------------------------------------------------------ the harmony: one chord per bar (a few change mid-bar)
const CH = { D: [50, 54, 57, 62], G: [50, 55, 59, 62], A: [49, 52, 57, 61], Bm: [50, 54, 59, 62], Em: [52, 55, 59, 64], Fsm: [49, 54, 57, 61] };
const ROOT = { D: 26, G: 31, A: 33, Bm: 35, Em: 28, Fsm: 30 };
// [start, chord]
const PROG = [[0, "G"], [2, "A"], [4, "Bm"], [6, "Em"], [7, "A"], [8, "Bm"], [10, "G"], [12, "Bm"], [14, "Em"], [16, "A"], [18, "Fsm"],
  [20, "G"], [21, "A"], [22, "D"], [24, "Bm"], [26, "Em"], [28, "A"], [30, "Bm"], [32, "G"], [34, "A"], [36, "Fsm"], [38, "G"], [40, "A"],
  [T.ka, "D"], [42, "G"], [44, "Em"], [46, "A"], [48, "D"]];
const chordAt = (t) => { let c = PROG[0][1]; for (const [a, ch] of PROG) if (t >= a - 1e-6) c = ch; return c; };
const SECS = [[0, "hook"], [T.myth, "myth"], [T.strike, "ans"], [T.q3, "dig"], [T.dive, "dive"], [T.arcsOn, "grid"], [T.stop1, "stop"], [T.name, "name"],
  [T.q6, "glove"], [T.q7, "climb"], [T.wake, "saus"], [T.a8, "touch"], [T.q9, "call"], [T.stop2, "stop"], [T.ka, "payoff"], [T.tip, "tip"], [T.end, "end"]];
const secAt = (t) => { let s = SECS[0][1]; for (const [t0, n] of SECS) if (t >= t0 - 1e-6) s = n; return s; };
const silent = (t) => (t >= T.hush && t < T.strike) || (t >= T.stop1 && t < T.name) || (t >= T.stop2 && t < T.ka);

// ------------------------------------------------------------------ arrangement
const ARP = [0, 1, 2, 3, 2, 1, 2, 3];
for (let t = 0; t < DUR - 1e-6; t += BEAT) {
  const q = Math.round(t / BEAT) % 4, sec = secAt(t), ch = chordAt(t + 1e-4), root = ROOT[ch], notes = CH[ch];
  if (silent(t)) continue;
  const muff = sec === "glove";
  const MB = muff ? MUF : MUS;
  // drums
  if (sec === "hook" || sec === "call") { if (q === 0 || q === 2) kick(t, q === 0 ? 0.8 : 0.6); if (q === 1 || q === 3) clap(t, 0.4); for (let e = 0; e < 2; e++) hat(t + e * BEAT / 2, e ? 0.5 : 0.3); }
  if (sec === "myth" && q === 0) kick(t, 0.6);
  if (sec === "myth") hat(t + BEAT / 2, 0.35);
  if (sec === "ans" && t >= T.a2 - 1e-6) { if (q === 0 || q === 2) kick(t, 0.7); hat(t + BEAT / 2, 0.45); }
  if (sec === "dig" && q === 0) kick(t, 0.45);
  if (sec === "grid" || sec === "touch") { if (q === 0 || q === 2) kick(t, 0.7); if (q === 3) rim(t + BEAT / 2, 0.5); for (let e = 0; e < 4; e++) hat(t + e * S16, e === 2 ? 0.42 : 0.18); }
  if (sec === "glove") { if (q === 0) kick(t, 0.6); for (let e = 0; e < 4; e++) hat(t + e * S16, e === 2 ? 0.3 : 0.12); }
  if (sec === "climb" && q === 0) kick(t, 0.5);
  if (sec === "name" || sec === "payoff") { kick(t, q === 0 ? 1 : 0.85); if (q === 1 || q === 3) clap(t, 0.75); for (let e = 0; e < 4; e++) { if (e === 2) hat(t + e * S16, 0.75, true, 0.2); else hat(t + e * S16, e % 2 ? 0.4 : 0.22); } }
  if (sec === "saus") { if (q === 0 || q === 2) kick(t, 0.75); if (q === 1 || q === 3) clap(t, 0.55); hat(t + BEAT / 2, 0.6, true, 0.2); hat(t, 0.25); }
  if (sec === "tip") { if (q === 0) kick(t, 0.55); hat(t + BEAT / 2, 0.35); }
  if (sec === "end" && Math.abs(t - T.sting) < 1e-6) kick(t, 0.7);
  // bass
  if (sec === "hook" || sec === "call") { if (q === 0) bass(t, root + 12, BEAT * 3.6, 0.55); }
  if (sec === "myth") { [0, 0.5].forEach((o) => { if (!silent(t + o * BEAT)) bass(t + o * BEAT, root + 12, BEAT * 0.2, 0.7); }); }
  if (sec === "ans" && t >= T.a2 - 1e-6) { bass(t, root + 12, BEAT * 0.2, 0.7); bass(t + BEAT / 2, root + 24, BEAT * 0.35, 0.8); }
  if (sec === "dig" && q === 0) bass(t, root + 12, BEAT * 3.6, 0.45);
  if (sec === "grid" || sec === "touch" || sec === "glove") {                       // the 8th ostinato: root, root, fifth, octave
    const pat = [0, 0, 7, 12]; for (let e = 0; e < 2; e++) { const k = (q * 2 + e) % 4, tt = t + e * BEAT / 2; if (!silent(tt)) bass(tt, root + 12 + pat[k], BEAT * 0.3, muff ? 0.55 : 0.75, MB); }
  }
  if (sec === "name" || sec === "payoff" || sec === "saus") { bass(t, root + 12, BEAT * 0.18, 0.75); bass(t + BEAT / 2, root + 24, BEAT * 0.4, 0.9); }
  if ((sec === "climb" || sec === "tip") && q === 0) bass(t, root + 12, BEAT * 3.6, 0.45);
  if (sec === "end" && q === 0 && t >= T.sting - 1e-6) bass(t, root + 12, BEAT * 3, 0.6);
  // the explanation's pulsing 8th stabs (low-passed under the glove)
  if (sec === "grid" || sec === "touch" || sec === "glove") for (let e = 0; e < 2; e++) { const tt = t + e * BEAT / 2; if (!silent(tt)) stab(tt, notes.map((m) => m + 12), 0.16, e ? 0.55 : 0.75, muff ? 0.05 : 0.45, MB); }
  // the "current": a 16th shimmer, two octaves up (off under the glove)
  if (sec === "grid" || sec === "touch") { const nn = notes.map((m) => m + 24); for (let e = 0; e < 4; e++) { const tt = t + e * S16; if (!silent(tt)) pluck(tt, nn[ARP[(q * 4 + e) % 8]], e === 0 ? 0.42 : 0.3, e % 2 ? 0.35 : -0.35); } }
  // reveal: off-beat bright stabs and a 16th arp
  if (sec === "name" || sec === "payoff") { stab(t + BEAT / 2, notes.map((m) => m + 12), 0.2, 0.8, 1.2); const nn = notes.map((m) => m + 24); for (let e = 0; e < 4; e++) pluck(t + e * S16, nn[ARP[(q * 4 + e) % 8]], e === 0 ? 0.5 : 0.36, e % 2 ? 0.3 : -0.3); }
  if (sec === "saus" || sec === "tip" || sec === "climb") { const nn = notes.map((m) => m + 24); for (let e = 0; e < 2; e++) pluck(t + e * BEAT / 2, nn[(q * 2 + e) % 4], sec === "saus" ? 0.45 : 0.33, e ? 0.3 : -0.3); }
}
// pads, by chord span and section
{
  const cuts = [...new Set([...PROG.map(([a]) => a), ...SECS.map(([a]) => a), T.hush, T.strike, T.a2, DUR])].sort((a, b) => a - b);
  for (let k = 0; k + 1 < cuts.length; k++) {
    const a = cuts[k], z = Math.min(cuts[k + 1], DUR), sec = secAt(a + 1e-4), notes = CH[chordAt(a + 1e-4)].map((m) => m + 12), len = z - a - 0.04;
    if (len < 0.2 || silent(a + 1e-4)) continue;
    const V = { hook: [0.45, 1300], myth: [0.6, 750], ans: [0.6, 1100], dig: [0.7, 900], dive: [1.0, 700], grid: [0.6, 1000], name: [0.8, 1600], glove: [0.55, 600],
      climb: [0.7, 1000], saus: [0.55, 1500], touch: [0.6, 1100], call: [0.45, 1200], payoff: [0.85, 1800], tip: [0.75, 1300], end: [1.0, 1500] }[sec];
    if (V) pad(a, notes, len, V[0], V[1]);
  }
}
// ---- melodies grown from the motif (F#–A–B = mi-sol-la; the answer F#–A–D = mi-sol-DO)
const play = (t0, notes, v = 0.9, br = 1) => notes.forEach(([s, m, d]) => lead(t0 + s * S16, m, d * S16 * 0.92, v, br));
play(T.name, [[0, 78, 2], [2, 81, 2], [4, 86, 6], [10, 85, 2], [12, 83, 2], [14, 81, 4]], 0.95, 1.1);           // the name: mi-sol-DO, then down
play(T.name + BAR, [[0, 83, 2], [2, 81, 2], [4, 78, 4]], 0.75, 0.9);
play(T.ka, [[0, 78, 2], [2, 81, 2], [4, 86, 8], [12, 88, 2], [14, 86, 2]], 0.95, 1.1);                          // the 咔: the ringtone answered
play(T.ka + 1.5, [[0, 83, 2], [2, 86, 2], [4, 88, 4], [8, 86, 2], [10, 83, 2], [12, 81, 4]], 0.85, 1.0);
play(T.ka + 3.5, [[0, 78, 2], [2, 81, 2], [4, 83, 4], [8, 81, 6]], 0.7, 0.9);
// the sausage: a playful mallet line over Bm–G–A
[[0, 83], [2, 86], [3, 90], [4, 88], [6, 86], [8, 83], [10, 81], [12, 83]].forEach(([s, m]) => mallet(T.wake + 0.5 + s * S16, m, 0.85, 0.1));
[[0, 83], [2, 86], [4, 91], [6, 90], [8, 86], [12, 88]].forEach(([s, m]) => mallet(32 + s * S16, m, 0.75, -0.1));
// the tip: a soft mallet answer (Em – A – D)
[[0, 79], [2, 83], [4, 88], [6, 86], [8, 83]].forEach(([s, m]) => mallet(T.tip + 0.75 + s * S16, m, 0.6, 0.15));
[[0, 81], [2, 85], [4, 88], [6, 85], [10, 81]].forEach(([s, m]) => mallet(46 + s * S16, m, 0.55, -0.15));
// the last word: mi-sol-DO, the DO on the sting
[[0, 78, 2], [2, 81, 2], [4, 86, 12]].forEach(([s, m, d]) => lead(T.sting - 0.5 + s * S16, m, d * S16 * 0.92, 0.85, 0.9));
// the guess: a small falling "la–sol–mi?" under the question
[[0, 83], [2, 81], [4, 78], [8, 81]].forEach(([s, m], i) => pluck(T.q2 + 0.5 + s * S16, m, 0.8, -0.2 + 0.15 * i));

// ------------------------------------------------------------------ the phone: ringtone (the motif) and vibration motor (D3)
const RING = [78, 81, 83, 81, 78, 81];                              // mi sol la sol mi sol
function ringLevel(t) {
  if (t < T.myth) return 1;
  if (t < T.hush) return 0.5;
  if (t < T.a2) return 0;
  if (t < T.q3) return 0.45;
  if (t < T.dive + 0.5) return 0.3 * (1 - (t - T.q3) / (T.dive + 0.5 - T.q3));
  if (t >= T.ring2 && t < T.stop2) return 0.95;
  return 0;
}
for (let c = 0; c < DUR; c += 1) RING.forEach((m, i) => { const t = c + i * S16; if (buzzK(t + 0.001) > 0 && ringLevel(t) > 0.01 && !silent(t)) ringNote(t, m, ringLevel(t), i % 2 ? 0.2 : 0.05); });
const VIB = bus();
{
  let ph = 0; const lp = svf();
  for (let n = 0; n < Math.floor(DUR * SR); n++) {
    const t = n / SR, b = buzzVis(t); if (b <= 0 || silent(t)) { lp(0, 600); continue; }
    const lev = t < T.myth ? 1 : t < T.a2 ? 0.7 : t < T.dive ? 0.45 * (1 - (t - T.a2) / (T.dive - T.a2)) : t >= T.ring2 ? 0.9 : 0;
    ph = (ph + 146.83 / SR) % 1;
    const s = 0.6 * Math.sin(TAU * ph) + 0.3 * Math.sin(TAU * 2 * ph) + 0.15 * sawBL(ph, 146.83 / SR);
    const v = 0.22 * b * lev * lp(s, 600, 0.8).lp * (0.75 + 0.25 * Math.sin(TAU * 31 * t));
    VIB[0][n] = v; VIB[1][n] = v * 0.9;
  }
}

// ------------------------------------------------------------------ sound effects on picture events
const ask = (t) => { blip(t, 81, 0.55, -0.15); blip(t + 0.125, 86, 0.6, 0.15); };      // every question: the same rising 4th (A5 → D6)
[T.q2, T.q3, T.q4, T.q6, T.q7, T.q9].forEach(ask);
// 1 the phenomenon: the gloved swipes (muffled, nothing answers), the underline, the hard press
[T.sw1, T.sw2].forEach((t) => { tap(t, 0.7, 110); glide(t + 0.05, 0.5, 64, 62, 0.25, 0.2); });
blip(T.underline, 88, 0.8); blip(T.underline + 0.125, 93, 0.6);
thunk(T.press1, 0.55, 100); creak(T.press1 + 0.05, 0.7);
// 2 the guess: pressed harder, the glass creaks; silence; struck; a bare finger grazes and the knob follows at once
softImpact(T.myth, 0.3);
[T.press2, T.press2 + 0.5, T.press2 + 1.0].forEach((t, i) => { thunk(t, 0.45 + 0.1 * i, 95 - 8 * i); creak(t + 0.03, 0.6 + 0.2 * i); });
impact(T.strike, 1.4); stab(T.strike, [52, 59, 64, 67, 71], 0.7, 1.1, 1.3);
buzz(T.strike, 0.3, 1); thunk(T.strike, 0.8, 120); thunk(T.strike + 0.125, 0.8, 110); buzz(T.strike + 0.125, 0.25, 0.8);
tick(T.graze, 0.9, 0, 3400); blip(T.graze, 86, 0.7); glide(T.graze, T.grazeEnd - T.graze, 74, 86, 0.6, 0.2); glide(T.grazeEnd, 0.3, 86, 74, 0.35, -0.2);
// 3 dig in: the finger lifts; through the glass; the grid lights up row by row
tick(T.lift, 0.5, 0.1, 2600);
glide(T.dive, 1.0, 55, 81, 1.1, 0.1); riser(T.dive - 0.25, 1.0, 0.7);
bloom(T.arcsOn, [83, 86, 90], 0.75);
for (let j = 0; j < 11; j++) tick(T.arcsOn + j * 0.05, 0.25, -0.4 + 0.08 * j, 2200 + 90 * j);
// 4 the mechanism: the finger comes close, the field is drawn away (falling), the scan, the lock, the name
glide(T.fIn, T.fNear - T.fIn, 62, 74, 0.35, -0.2);
glide(T.steal, T.stealEnd - T.steal, 90, 78, 0.7, 0.25); bloom(T.a4, [78, 81, 85], 0.45);
HITS.scan.forEach((t, i) => tick(t, 0.6, -0.5 + 0.14 * i, 2000 + 160 * i));
blip(T.lock1, 86, 1.0); blip(T.lock1 + 0.08, 93, 0.75); bloom(T.lock1 + 0.05, [86, 90, 93], 0.6);
impact(T.name, 1.3); stab(T.name, [50, 57, 62, 66, 69], 0.6, 1, 1.2); bloom(T.name + 0.25, [86, 90, 93], 0.7);
// 5 the glove: the fabric goes on, the scan finds nothing
for (let i = 0; i < 4; i++) mallet(T.wrap + i * S16, [62, 59, 57, 54][i], 0.45, -0.2 + 0.12 * i);
tap(T.fDownEnd, 0.6, 95);
HITS.scan2.forEach((t, i) => tick(t, 0.5, -0.5 + 0.14 * i, 2000 + 160 * i));
[T.miss].forEach((m) => { blip(m, 81, 0.6, 0.1); blip(m + 0.25, 78, 0.5, -0.1); thunk(m + 0.25, 0.25, 90); });
// the camera swings between the side cut and the view from above: soft tonal glides (no noise)
HITS.swing.forEach((t, i) => glide(t, 0.5, i % 2 ? 79 : 74, i % 2 ? 74 : 79, 0.35, i % 2 ? -0.2 : 0.2));
// back out: a sausage wakes the screen; the touch glove's yarn
glide(T.climb, T.climbEnd - T.climb, 79, 67, 0.6, 0);
tap(T.saus, 0.85, 85); thunk(T.saus, 0.25, 70);
blip(T.inset, 84, 0.5, -0.3); blip(T.inset + 0.08, 88, 0.4, -0.3);
blip(T.sLock, 86, 0.8); blip(T.sLock + 0.08, 93, 0.6);
bloom(T.wake, [74, 78, 81, 86], 0.9); [[0, 86], [1, 90], [2, 93]].forEach(([i, m]) => blip(T.wake + i * S16, m, 0.55, -0.2 + 0.2 * i));
tick(T.sLabel, 0.5, 0.2, 2600);
tap(T.unlock, 0.55, 90); glide(T.unlock, T.unlockEnd - T.unlock, 74, 86, 0.6, -0.1); bloom(T.unlockEnd, [81, 86, 90], 0.4);
tap(T.iconTap, 0.6, 95); blip(T.iconTap, 90, 0.6, 0.15);
tap(T.tg, 0.6, 110); bloom(T.tg + 0.25, [81, 85, 88], 0.35);
glide(T.dive2, T.top2 - T.dive2 + 0.2, 60, 79, 0.8, 0.1);
for (let i = 0; i < 6; i++) blip(T.yarn + i * S16, [81, 85, 88, 93, 97, 100][i], 0.45 - 0.04 * i, -0.3 + 0.12 * i);   // glints climbing the yarn
blip(T.lock2, 86, 0.85); blip(T.lock2 + 0.08, 93, 0.65); bloom(T.lock2 + 0.05, [86, 90, 93], 0.5);
// 6 the same call: it rings; the touch glove swipes; half a beat of nothing; 咔
glide(T.climb2, T.climb2End - T.climb2, 67, 79, 0.5, 0); riser(T.ring2 + 0.25, T.stop2 - T.ring2 - 0.25, 0.5);
tick(T.sw3, 0.8, 0, 3400); glide(T.sw3, T.stop2 - T.sw3, 74, 81, 0.55, 0.2);
snapSfx(T.ka, 1.2); impact(T.ka, 1.35); stab(T.ka, [50, 57, 62, 66, 69], 0.5, 1, 1.25); bloom(T.ka + 0.05, [86, 90, 93, 98], 0.6);
bloom(T.tip, [79, 83, 86], 0.45);
tap(T.toggle, 0.5, 110); click(T.toggle, 0.9); blip(T.toggle, 86, 0.7); blip(T.toggle + 0.08, 90, 0.5);
{ let k = 0; TL.COPY.end.forEach((s, li) => { const n = s.replace(/[\[\]]/g, "").length; for (let j = 0; j < n; j++) tick(T.title1 + li * 0.3 + j * 0.045, 0.45, -0.2 + 0.05 * (k++ % 8), 2600 + (j % 3) * 300); }); }
blip(T.ep, 86, 0.6);
impact(T.sting, 0.55); stab(T.sting, [50, 57, 62, 66, 69], 1.6, 0.8, 0.9); bloom(T.sting, [86, 90, 93, 98], 1.0);

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
// the glove: its music bus goes through a low-pass (the sound is "insulated" while the glove is on)
{ const fL = svf(), fR = svf(); for (let n = 0; n < N; n++) { MUF[0][n] = fL(MUF[0][n], 700, 0.7).lp; MUF[1][n] = fR(MUF[1][n], 700, 0.7).lp; } }
const L = new Float32Array(N), R = new Float32Array(N); let peak = 0;
for (let n = 0; n < N; n++) {
  const t = n / SR, gate = silent(t) ? 0 : 1;                 // the stops: everything cuts (true silence)
  let l = (DRUM[0][n] + (MUS[0][n] + MUF[0][n] * 1.5) * duck[n] * 0.9 + wl[n] * 3.2 + SFX[0][n] + VIB[0][n]) * gate;
  let r = (DRUM[1][n] + (MUS[1][n] + MUF[1][n] * 1.5) * duck[n] * 0.9 + wr[n] * 3.2 + SFX[1][n] + VIB[1][n]) * gate;
  l = Math.tanh(l * 1.15) / 1.15; r = Math.tanh(r * 1.15) / 1.15;
  L[n] = l; R[n] = r; peak = Math.max(peak, Math.abs(l), Math.abs(r));
}
// soften the gate edges (2 ms) so the stops do not click
for (const [a, b] of [[T.hush, T.strike], [T.stop1, T.name], [T.stop2, T.ka]]) {
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
// the loudest moments (10 ms peak within 120 ms of each hit), to check the ✕ / name / 咔 are on top
{ const pk = (t) => { let m = 0; for (let n = Math.floor(t * SR); n < Math.floor((t + 0.12) * SR); n++) m = Math.max(m, Math.abs(L[n]), Math.abs(R[n])); return (20 * Math.log10(m * g + 1e-9)).toFixed(1); };
  const rms = (a, b) => { let e = 0; for (let n = Math.floor(a * SR); n < Math.floor(b * SR); n++) e += L[n] * L[n]; return (10 * Math.log10(e * g * g / ((b - a) * SR) + 1e-12)).toFixed(1); };
  console.log(`peaks dBFS: strike ${pk(T.strike)}, name ${pk(T.name)}, 咔 ${pk(T.ka)}, lock ${pk(T.lock1)}, wake ${pk(T.wake)}, sting ${pk(T.sting)}, myth ${pk(T.myth)}`);
  console.log(`rms dB: hook ${rms(0.1, 4)}, myth ${rms(4.3, 6)}, hush ${rms(T.hush + 0.01, T.strike - 0.01)}, grid ${rms(12, 19)}, name ${rms(22, 24)}, glove ${rms(24.5, 29)}, saus ${rms(31.5, 34.5)}, payoff ${rms(40.5, 44)}, tip ${rms(44.5, 48.5)}`); }
console.log(`score-${STYLE}.wav: ${DUR} s @ ${SR} Hz, mix peak ${peak.toFixed(2)} -> normalised`);
