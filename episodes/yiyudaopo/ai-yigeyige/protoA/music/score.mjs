// music/score.mjs — score + sound effects, synthesized (no samples), locked to ../timeline.js.
//   node music/score.mjs  ->  music/score.wav (48 kHz stereo, peak-normalised; loudness is set by tools/master.sh)
// D major, 100 BPM (8th = 0.3 s). Textures: hook = ticking plucks over Bm–G (suspense); compare = same plucks over G–A,
// cut to true silence 0.33 s before the empty reveal; written = warm D pad; slow replay = half-time plucks Em–G → D on the zip;
// rhythm = 8th plucks + soft kick D–A–Bm–G; teaser = Asus4, unresolved.
import { createRequire } from "node:module";
import { writeFileSync } from "node:fs";
const TL = createRequire(import.meta.url)("../timeline.js");
const { T, DUR, HITS } = TL;
const SR = 48000, N = Math.ceil(SR * (DUR + 0.8)), TAU = Math.PI * 2;
const L = new Float32Array(N), R = new Float32Array(N);
const mtof = (m) => 440 * Math.pow(2, (m - 69) / 12);
let seed = 424242; const rnd = () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; };
function put(t0, len, gen, { gain = 1, pan = 0 } = {}) {
  const i0 = Math.max(0, Math.floor(t0 * SR)), i1 = Math.min(N, Math.floor((t0 + len) * SR));
  const gl = gain * Math.cos(((pan + 1) * Math.PI) / 4), gr = gain * Math.sin(((pan + 1) * Math.PI) / 4);
  for (let i = i0; i < i1; i++) { const v = gen(i / SR - t0); if (Number.isFinite(v)) { L[i] += v * gl; R[i] += v * gr; } }
}
function lp() { let y = 0; return (x, fc) => { const a = 1 - Math.exp(-TAU * fc / SR); y += a * (x - y); return y; }; }

// ---------------------------------------------------------------- instruments
function pluck(t, m, v = 1, pan = 0) {
  const f = mtof(m);
  put(t, 0.9, (u) => v * 0.16 * (Math.sin(TAU * f * u) + 0.35 * Math.sin(TAU * 2 * f * u) * Math.exp(-u * 12) + 0.12 * Math.sin(TAU * 3 * f * u) * Math.exp(-u * 20)) * Math.exp(-u * 5.5) * Math.min(1, u / 0.003), { pan });
}
function pad(t, len, notes, v = 1) {
  notes.forEach((m, k) => {
    const f = mtof(m), F = lp();
    put(t, len + 0.6, (u) => {
      const e = Math.min(1, u / 0.35) * (u < len ? 1 : Math.max(0, 1 - (u - len) / 0.6));
      const s = Math.sin(TAU * f * u) + 0.5 * Math.sin(TAU * f * 1.003 * u + 1) + 0.25 * Math.sin(TAU * 2 * f * u);
      return v * 0.045 * F(s, 1800) * e;
    }, { pan: (k - 1) * 0.3 });
  });
}
function kick(t, v = 1) { put(t, 0.35, (u) => v * 0.5 * Math.sin(TAU * (48 * u + 70 * (1 - Math.exp(-u * 28)) / 28)) * Math.exp(-u * 9)); }
function bass(t, m, len, v = 1) { const f = mtof(m); put(t, len + 0.05, (u) => v * 0.2 * Math.sin(TAU * f * u) * Math.min(1, u / 0.01) * (u < len ? 1 : Math.max(0, 1 - (u - len) / 0.05))); }

const CH = { D: [62, 66, 69, 73], Bm: [59, 62, 66, 69], G: [55, 59, 62, 66], A: [57, 61, 64, 69], Em: [55, 59, 62, 64], Asus: [57, 62, 64, 69] };
const ROOT = { D: 38, Bm: 35, G: 31, A: 33, Em: 28, Asus: 33 };
function arp(t0, t1, chords, step, v = 1) {      // chords: [[time, name], ...]
  let k = 0;
  for (let t = t0; t < t1 - 1e-6; t += step, k++) {
    const name = chords.filter(([at]) => at <= t + 1e-6).pop()[1], c = CH[name];
    pluck(t, c[[0, 2, 1, 3, 2, 1][k % 6]] + 12, v * (k % 2 ? 0.7 : 1), (k % 2 ? 0.25 : -0.25));
  }
}
// hook + compare (stops before the empty reveal)
arp(0, 8.45, [[0, "Bm"], [2.4, "G"], [4.2, "G"], [6.0, "A"]], 0.3, 0.9);
pad(0, 2.4, CH.Bm, 0.8); pad(2.4, 1.8, CH.G, 0.8); pad(4.2, 1.8, CH.G, 0.7); pad(6.0, 2.45, CH.A, 0.7);
// written: warm D
pad(9.25, 2.1, CH.D, 1.0); bass(9.25, ROOT.D, 2.0, 0.8);
// slow replay: half-time
arp(12.2, 15.9, [[12.2, "Em"], [14.0, "G"]], 0.6, 0.75);
pad(12.2, 1.8, CH.Em, 0.8); pad(14.0, 1.9, CH.G, 0.8);
pad(15.95, 2.2, CH.D, 1.1); bass(15.95, ROOT.D, 2.1, 0.9);
[74, 78, 81, 86].forEach((m, i) => pluck(15.95 + i * 0.07, m, 0.8, 0.2));      // the zip lands on D
// rhythm
arp(17.50, 22.80, [[17.50, "D"], [18.70, "A"], [19.90, "Bm"], [21.10, "G"]], 0.3, 0.85);
for (let t = 17.50; t < 22.80; t += 0.6) kick(t, 0.7);
[[17.50, "D"], [18.70, "A"], [19.90, "Bm"], [21.10, "G"]].forEach(([t, c]) => { pad(t, 1.2, CH[c], 0.7); bass(t, ROOT[c], 1.1, 0.8); });
// teaser: unresolved
pad(22.90, 3.0, CH.Asus, 1.0); bass(22.90, ROOT.Asus, 2.8, 0.6);
pluck(23.10, 81, 0.7); pluck(23.28, 83, 0.7); pluck(24.60, 76, 0.5);

// ---------------------------------------------------------------- sound effects
const noise = (t, len, fc, v, pan = 0, shape = (u) => Math.exp(-u * 30)) => { const F = lp(); put(t, len, (u) => v * F(rnd() * 2 - 1, typeof fc === "function" ? fc(u) : fc) * shape(u), { pan }); };
const tone = (t, len, f, v, decay = 20, pan = 0) => put(t, len, (u) => v * Math.sin(TAU * (typeof f === "function" ? f(u) : f) * u) * Math.exp(-u * decay) * Math.min(1, u / 0.002), { pan });
const SFX = {
  tick: (t, k = 0) => { noise(t, 0.04, 5000, 0.35, -0.1, (u) => Math.exp(-u * 120)); tone(t, 0.06, 1900 + 120 * k, 0.08, 60); },
  click: (t) => { tone(t, 0.05, 3200, 0.25, 90, 0.3); noise(t, 0.03, 7000, 0.4, 0.3, (u) => Math.exp(-u * 150)); },
  stretch: (t, len) => { const F = lp(); put(t, len, (u) => 0.22 * F(rnd() * 2 - 1, 300 + 1400 * (u / len)) * Math.sin(Math.PI * u / len), { pan: 0.3 }); tone(t, len, (u) => 140 + 90 * u / len, 0.05, 0.5); },
  tug: (t) => { tone(t, 0.12, 180, 0.18, 25, 0.3); noise(t, 0.08, 900, 0.2, 0.3); },
  hmm: () => {},
  boing: (t) => put(t, 0.6, (u) => 0.22 * Math.sin(TAU * (220 * u + 60 * Math.sin(TAU * 7 * u) / (TAU * 7) * 1)) * Math.exp(-u * 6) * (1 + 0.5 * Math.sin(TAU * 7 * u)), { pan: 0.1 }),
  whoosh: (t) => noise(t, 0.45, (u) => 400 + 3000 * Math.sin(Math.PI * u / 0.45), 0.35, 0, (u) => Math.sin(Math.PI * u / 0.45)),
  lift: (t) => noise(t, 0.4, (u) => 800 + 2500 * u, 0.3, 0.1, (u) => Math.sin(Math.PI * u / 0.4)),
  found: (t) => { [81, 88].forEach((m, i) => tone(t + i * 0.06, 0.9, mtof(m), 0.12, 6, 0.2)); },
  drop: (t) => { tone(t, 0.1, 150, 0.2, 30); noise(t, 0.06, 1200, 0.2); },
  hollow: (t) => { tone(t, 0.5, 95, 0.32, 9); tone(t, 0.4, 190, 0.08, 12); },
  pen: (t, len) => { for (let u = 0; u < len; u += 0.045) noise(t + u, 0.05, 3500 + 1500 * rnd(), 0.18 + 0.1 * rnd(), -0.15, (x) => Math.exp(-x * 60)); },
  rewind: (t, len) => { const F = lp(); put(t, len, (u) => 0.25 * F(rnd() * 2 - 1, 3000 - 2400 * u / len) * Math.sin(Math.PI * u / len) + 0.06 * Math.sin(TAU * (900 - 600 * u / len) * u), {}); },
  sweep: (t, len) => noise(t, len, (u) => 600 + 2600 * u / len, 0.22, -0.2, (u) => Math.sin(Math.PI * u / len)),
  rise: (t) => [0, 0.07, 0.14].forEach((d, i) => tone(t + d, 0.25, mtof(76 + i * 3), 0.07, 14, (i - 1) * 0.5)),
  hop: (t, k = 0) => tone(t, 0.09, mtof(83 + (k % 3) * 2), 0.11, 40, 0.2),
  pick: (t) => { tone(t, 0.5, mtof(88), 0.12, 8, 0.2); tone(t, 0.5, mtof(95), 0.05, 10, 0.2); },
  land: (t, v = 1) => { tone(t, 0.18, 120, 0.3 * v, 22); noise(t, 0.05, 2500, 0.25 * v, 0, (u) => Math.exp(-u * 80)); },
  zip: (t, v = 1) => put(t, 0.3, (u) => 0.13 * v * Math.sin(TAU * (500 * u + 2400 * u * u / 0.6)) * Math.sin(Math.PI * u / 0.3), { pan: 0.15 }),
  thread: (t) => noise(t, 0.5, (u) => 1500 + 3000 * u, 0.14, 0.2, (u) => Math.sin(Math.PI * u / 0.5)),
  slot: (t) => { tone(t, 0.25, 600, 0.12, 18); tone(t, 0.25, 900, 0.06, 18); },
  question: (t) => { tone(t, 0.6, mtof(81), 0.08, 5); tone(t + 0.15, 0.6, mtof(83), 0.07, 5); },
};
HITS.forEach(([t, kind, arg]) => SFX[kind](t, arg));

// ---------------------------------------------------------------- soft room reverb (feedback combs) + write
function reverb(X) {
  const out = new Float32Array(N), D = [1557, 1617, 1491, 1422].map((d) => Math.round(d * SR / 44100));
  D.forEach((d) => { const buf = new Float32Array(d); let j = 0; for (let i = 0; i < N; i++) { const y = buf[j]; buf[j] = X[i] + y * 0.78; out[i] += y * 0.06; j = (j + 1) % d; } });
  return out;
}
const rl = reverb(L), rr = reverb(R);
let peak = 0; for (let i = 0; i < N; i++) { L[i] += rl[i]; R[i] += rr[i]; peak = Math.max(peak, Math.abs(L[i]), Math.abs(R[i])); }
const g = 0.89 / peak, buf = Buffer.alloc(44 + N * 4);
buf.write("RIFF", 0); buf.writeUInt32LE(36 + N * 4, 4); buf.write("WAVEfmt ", 8); buf.writeUInt32LE(16, 16); buf.writeUInt16LE(1, 20); buf.writeUInt16LE(2, 22);
buf.writeUInt32LE(SR, 24); buf.writeUInt32LE(SR * 4, 28); buf.writeUInt16LE(4, 32); buf.writeUInt16LE(16, 34); buf.write("data", 36); buf.writeUInt32LE(N * 4, 40);
for (let i = 0; i < N; i++) { buf.writeInt16LE(Math.round(Math.max(-1, Math.min(1, L[i] * g)) * 32767), 44 + i * 4); buf.writeInt16LE(Math.round(Math.max(-1, Math.min(1, R[i] * g)) * 32767), 46 + i * 4); }
writeFileSync(new URL("./score.wav", import.meta.url), buf);
console.log("music/score.wav", DUR, "s");
