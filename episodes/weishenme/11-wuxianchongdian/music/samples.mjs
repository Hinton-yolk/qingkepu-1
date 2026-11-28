// music/samples.mjs — 新一季配乐方向样曲（三段，各约 20 秒），全部代码合成，不用采样。
//   node music/samples.mjs  ->  out/sample-A.wav, sample-B.wav, sample-C.wav（48 kHz 立体声）
// 三段同一调（E 大调，系列里没用过）、同一速度（120 BPM，时间网格不变）、同一结构，只换音色和织体，方便比较：
//   0–4 秒 开头：标志动机 mi-sol-la（G#5 B5 C#6）
//   4–12 秒 讲解：vi–IV–I–V（C#m–A–E–B）
//   12.0 秒 停半拍（真静音）
//   12.25–20 秒 揭晓：IV–V–I（A–B–E），动机解决到 mi-sol-DO（G#5 B5 E6）
// A 玻璃钟琴：FM 电钢琴 + 玻璃钟 + 刷子鼓，轻、通透
// B 清透电子：玻璃拨弦 + 侧链铺底 + 次低音 + 清脆踩镲，和上一季的电子感最近
// C 马林巴拨奏：马林巴 / 卡林巴 + 拨弦 + 沙锤，暖、原声感
import { writeFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const OUT = join(dirname(fileURLToPath(import.meta.url)), "..", "out");
mkdirSync(OUT, { recursive: true });
const SR = 48000, DUR = 20.6, N = Math.ceil(SR * DUR), TAU = Math.PI * 2, BEAT = 0.5, S16 = 0.125;
const mtof = (m) => 440 * Math.pow(2, (m - 69) / 12);
let seed = 909;
const rnd = () => { seed |= 0; seed = (seed + 0x6d2b79f5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };

// ---------------------------------------------------------------- mixer
let L, R, SL, SR_, DUCK;
function reset() { L = new Float32Array(N); R = new Float32Array(N); SL = new Float32Array(N); SR_ = new Float32Array(N); DUCK = new Float32Array(N).fill(1); seed = 909; }
function put(t0, len, gen, { gain = 1, pan = 0, rev = 0.2, duck = false } = {}) {
  const i0 = Math.max(0, Math.floor(t0 * SR)), i1 = Math.min(N, Math.floor((t0 + len) * SR));
  const gl = gain * Math.cos(((pan + 1) * Math.PI) / 4), gr = gain * Math.sin(((pan + 1) * Math.PI) / 4);
  for (let i = i0; i < i1; i++) {
    let v = gen(i / SR - t0); if (!Number.isFinite(v)) continue;
    if (duck) v *= DUCK[i];
    L[i] += v * gl; R[i] += v * gr; SL[i] += v * gl * rev; SR_[i] += v * gr * rev;
  }
}
function sidechain(t, depth = 0.55, rel = 7) { const i0 = Math.floor(t * SR); for (let i = 0; i < SR * 0.4 && i0 + i < N; i++) DUCK[i0 + i] = Math.min(DUCK[i0 + i], 1 - depth * Math.exp((-i / SR) * rel)); }
function silence(t0, t1) { const i0 = Math.floor(t0 * SR), i1 = Math.floor(t1 * SR); for (let i = i0; i < i1; i++) { L[i] = R[i] = 0; } }
// Freeverb-ish: 4 combs + 2 allpasses per side
function reverb(size = 0.82, damp = 0.35, wet = 0.32) {
  const combs = [1557, 1617, 1491, 1422], aps = [556, 441];
  const proc = (inp, spread) => {
    const out = new Float32Array(N);
    for (const c of combs) { const d = c + spread, buf = new Float32Array(d); let idx = 0, fs = 0;
      for (let i = 0; i < N; i++) { const y = buf[idx]; fs = y * (1 - damp) + fs * damp; buf[idx] = inp[i] + fs * size; idx = (idx + 1) % d; out[i] += y * 0.25; } }
    for (const a of aps) { const d = a + spread, buf = new Float32Array(d); let idx = 0;
      for (let i = 0; i < N; i++) { const b = buf[idx], x = out[i]; buf[idx] = x + b * 0.5; out[i] = b - x; idx = (idx + 1) % d; } }
    return out;
  };
  const wl = proc(SL, 0), wr = proc(SR_, 23);
  for (let i = 0; i < N; i++) { L[i] += wl[i] * wet; R[i] += wr[i] * wet; }
}
function writeWav(name) {
  let pk = 1e-9; for (let i = 0; i < N; i++) pk = Math.max(pk, Math.abs(L[i]), Math.abs(R[i]));
  const g = 0.89 / pk, buf = Buffer.alloc(44 + N * 4);
  buf.write("RIFF", 0); buf.writeUInt32LE(36 + N * 4, 4); buf.write("WAVEfmt ", 8); buf.writeUInt32LE(16, 16); buf.writeUInt16LE(1, 20); buf.writeUInt16LE(2, 22);
  buf.writeUInt32LE(SR, 24); buf.writeUInt32LE(SR * 4, 28); buf.writeUInt16LE(4, 32); buf.writeUInt16LE(16, 34); buf.write("data", 36); buf.writeUInt32LE(N * 4, 40);
  for (let i = 0; i < N; i++) { buf.writeInt16LE(Math.round(Math.max(-1, Math.min(1, L[i] * g)) * 32767), 44 + i * 4); buf.writeInt16LE(Math.round(Math.max(-1, Math.min(1, R[i] * g)) * 32767), 46 + i * 4); }
  writeFileSync(join(OUT, name), buf); console.log(name, "peak", pk.toFixed(2));
}
const att = (tt, a = 0.002) => Math.min(1, tt / a);

// ---------------------------------------------------------------- instruments
function fmBell(t, m, v = 1, pan = 0, ratio = 3.5, idx = 2.2, dec = 2.6) { // glass bell
  const f = mtof(m); put(t, 3.2, (tt) => v * 0.16 * Math.sin(TAU * f * tt + idx * Math.exp(-tt * 3) * Math.sin(TAU * f * ratio * tt)) * Math.exp(-tt * dec) * att(tt), { pan, rev: 0.45 });
}
function rhodes(t, m, len, v = 1, pan = 0) { // FM electric piano: 1:1 with a bark, plus a tine at 14x
  const f = mtof(m); put(t, len + 0.5, (tt) => { const e = Math.exp(-tt * 1.6) * (tt < len ? 1 : Math.max(0, 1 - (tt - len) / 0.4));
    return v * 0.14 * e * att(tt, 0.003) * (Math.sin(TAU * f * tt + 1.4 * Math.exp(-tt * 5) * Math.sin(TAU * f * tt)) + 0.18 * Math.sin(TAU * f * 14 * tt) * Math.exp(-tt * 40)); }, { pan, rev: 0.3 });
}
function marimba(t, m, v = 1, pan = 0) { const f = mtof(m); put(t, 1.0, (tt) => v * 0.2 * (Math.sin(TAU * f * tt) + 0.35 * Math.sin(TAU * f * 4 * tt) * Math.exp(-tt * 28) + 0.12 * Math.sin(TAU * f * 9.9 * tt) * Math.exp(-tt * 60)) * Math.exp(-tt * 5.5) * att(tt, 0.0015), { pan, rev: 0.25 }); }
function kalimba(t, m, v = 1, pan = 0) { const f = mtof(m); put(t, 1.4, (tt) => v * 0.15 * (Math.sin(TAU * f * tt) + 0.25 * Math.sin(TAU * f * 5.4 * tt) * Math.exp(-tt * 20)) * Math.exp(-tt * 3.4) * att(tt, 0.001), { pan, rev: 0.35 }); }
function pluckKS(t, m, v = 1, pan = 0, bright = 0.5, len = 0.9) { // Karplus–Strong
  const p = Math.max(2, Math.round(SR / mtof(m))), buf = new Float32Array(p); for (let i = 0; i < p; i++) buf[i] = rnd() * 2 - 1; let idx = 0, last = 0;
  put(t, len, (tt) => { const y = buf[idx]; const nx = buf[(idx + 1) % p]; buf[idx] = 0.996 * (bright * y + (1 - bright) * 0.5 * (y + nx)); last = y; idx = (idx + 1) % p; return v * 0.22 * y * Math.min(1, (len - tt) / 0.05); }, { pan, rev: 0.25 });
}
function glassPluck(t, m, v = 1, pan = 0) { const f = mtof(m); put(t, 0.6, (tt) => v * 0.12 * Math.sin(TAU * f * tt + 2.5 * Math.exp(-tt * 18) * Math.sin(TAU * f * 2 * tt)) * Math.exp(-tt * 7) * att(tt, 0.001), { pan, rev: 0.35, duck: true }); }
function softPad(t, notes, len, v = 1, duck = false) {
  notes.forEach((m, k) => { const f = mtof(m), ph = [rnd(), rnd(), rnd()];
    put(t, len + 0.8, (tt) => { let s = 0; [-0.08, 0, 0.08].forEach((d, j) => { s += Math.sin(TAU * (f * Math.pow(2, d / 12) * tt + ph[j])) + 0.3 * Math.sin(TAU * (2 * f * Math.pow(2, d / 12) * tt + ph[j])); });
      return v * 0.022 * s * Math.min(1, tt / 0.4) * (tt < len ? 1 : Math.max(0, 1 - (tt - len) / 0.8)); }, { pan: (k - (notes.length - 1) / 2) * 0.4, rev: 0.6, duck }); });
}
function sub(t, m, len, v = 1, duck = false) { const f = mtof(m); put(t, len + 0.05, (tt) => v * 0.35 * Math.tanh(1.3 * Math.sin(TAU * f * tt)) * att(tt, 0.004) * (tt < len ? 1 : Math.max(0, 1 - (tt - len) / 0.05)), { rev: 0, duck }); }
function kick(t, v = 1, sc = false) { put(t, 0.45, (tt) => v * Math.sin(TAU * (48 * tt + (110 * (1 - Math.exp(-tt * 32))) / 32)) * Math.exp(-tt * 8) * att(tt), { gain: 0.8, rev: 0 }); if (sc) sidechain(t); }
function brush(t, v = 1, pan = 0.1, len = 0.18) { let lp = 0; put(t, len, (tt) => { const n = rnd() * 2 - 1; lp += 0.35 * (n - lp); return v * 0.12 * (n - lp) * Math.exp(-tt * 18) * Math.min(1, tt / 0.01); }, { pan, rev: 0.2 }); }
function hat(t, v = 1, pan = 0.25, open = false) { let hp = 0, prev = 0; put(t, open ? 0.3 : 0.05, (tt) => { const n = rnd() * 2 - 1; hp = 0.85 * (hp + n - prev); prev = n; return v * 0.11 * hp * Math.exp(-tt * (open ? 12 : 90)); }, { pan, rev: 0.08 }); }
function shaker(t, v = 1, pan = -0.3) { let hp = 0, prev = 0; put(t, 0.09, (tt) => { const n = rnd() * 2 - 1; hp = 0.7 * (hp + n - prev); prev = n; return v * 0.07 * hp * Math.sin(Math.PI * Math.min(1, tt / 0.09)); }, { pan, rev: 0.1 }); }
function snap(t, v = 1) { let bp = 0, lp = 0; put(t, 0.2, (tt) => { const n = rnd() * 2 - 1; lp += 0.4 * (n - lp); bp = n - lp; return v * 0.25 * bp * Math.exp(-tt * 30); }, { pan: -0.1, rev: 0.3 }); }

// ---------------------------------------------------------------- the shared plan (E major)
const E = 52; // E3
const CH = { E: [64, 68, 71, 75], A: [64, 69, 73, 76], B: [63, 66, 71, 73], Cs: [61, 64, 68, 71], Gs: [63, 68, 71] };
const ROOT = { E: 40, A: 45, B: 47, Cs: 49, Gs: 44 };
const HOOK = [[0.5, 80], [0.75, 83], [1.0, 85]];             // mi-sol-la  G#5 B5 C#6
const RESOLVE = [[12.25, 80], [12.5, 83], [12.75, 88]];       // mi-sol-DO  G#5 B5 E6
const explain = [["Cs", 4], ["A", 6], ["E", 8], ["B", 10]];   // vi–IV–I–V, 2 s (one bar) each
const reveal = [["A", 14], ["B", 16], ["E", 18]];
const melody = [[4, 76], [4.75, 75], [5.5, 73], [6, 73], [6.75, 76], [7.5, 78], [8, 80], [9, 78], [9.5, 76], [10, 75], [10.75, 76], [11.25, 78]];
const melody2 = [[14, 81], [14.5, 80], [15, 78], [15.5, 76], [16, 78], [16.75, 80], [17.5, 83], [18, 80], [18.5, 83], [19, 88]];

function sampleA() { // 玻璃钟琴
  reset();
  HOOK.forEach(([t, m]) => fmBell(t, m, 1.0, 0.15));
  rhodes(0.5, 52, 3.2, 0.8); rhodes(0.5, 59, 3.2, 0.6, -0.2); rhodes(0.5, 64, 3.2, 0.5, 0.2);
  for (let t = 2; t < 4; t += BEAT) fmBell(t, 88 - (t % 1 ? 5 : 0), 0.35, 0.4, 3.5, 1.4, 4);
  explain.forEach(([c, t]) => { CH[c].forEach((m, k) => rhodes(t + k * 0.03, m, 1.8, 0.55, (k - 1.5) * 0.3)); rhodes(t, ROOT[c], 1.9, 0.7);
    for (let b = 0; b < 4; b++) { brush(t + b * BEAT + 0.25, 0.6); if (b % 2) brush(t + b * BEAT, 1.0, -0.05, 0.25); } kick(t, 0.55); kick(t + 1.25, 0.35); });
  melody.forEach(([t, m]) => fmBell(t, m, 0.55, 0.2, 3.5, 1.6, 3.5));
  RESOLVE.forEach(([t, m]) => fmBell(t, m, 1.1, 0.1));
  reveal.forEach(([c, t]) => { CH[c].forEach((m, k) => rhodes(t + k * 0.02, m, 1.9, 0.6, (k - 1.5) * 0.3)); rhodes(t, ROOT[c], 1.9, 0.8);
    for (let b = 0; b < 4; b++) { kick(t + b * BEAT, b % 2 ? 0.45 : 0.7); brush(t + b * BEAT + 0.25, 0.7); if (b % 2) snap(t + b * BEAT, 0.7); } });
  melody2.forEach(([t, m]) => fmBell(t, m, 0.6, -0.15, 3.5, 1.8, 3));
  for (let t = 14; t < 20; t += S16 * 2) fmBell(t, 88 + [0, 4, 7, 4][Math.round(t * 4) % 4], 0.12, 0.5, 3.5, 1.0, 6);
  reverb(0.84, 0.3, 0.36); silence(12.0, 12.25); writeWav("sample-A.wav");
}
function sampleB() { // 清透电子
  reset();
  HOOK.forEach(([t, m]) => glassPluck(t, m, 1.3, 0.1));
  softPad(0.5, CH.E, 3.4, 0.9);
  for (let t = 2; t < 4; t += S16 * 2) glassPluck(t, [76, 80, 83, 88][Math.round((t - 2) * 4) % 4], 0.45, Math.sin(t * 3) * 0.5);
  explain.forEach(([c, t]) => { softPad(t, CH[c], 1.9, 0.8, true); sub(t, ROOT[c], 0.4, 0.8, true); sub(t + 0.75, ROOT[c], 0.3, 0.6, true); sub(t + 1.5, ROOT[c] + 12, 0.25, 0.5, true);
    for (let b = 0; b < 4; b++) { kick(t + b * BEAT, b ? 0.5 : 0.8, true); hat(t + b * BEAT + 0.25, 0.8); hat(t + b * BEAT + 0.375, 0.35, -0.25); }
    for (let s = 0; s < 16; s++) if ([0, 3, 6, 8, 11, 14].includes(s)) glassPluck(t + s * S16, CH[c][s % 4] + 12, 0.4, ((s % 3) - 1) * 0.5); });
  melody.forEach(([t, m]) => glassPluck(t, m + 12, 0.7, 0.05));
  RESOLVE.forEach(([t, m]) => glassPluck(t, m, 1.4, 0));
  reveal.forEach(([c, t]) => { softPad(t, CH[c].map(m => m + 12), 1.9, 0.7, true); sub(t, ROOT[c], 1.8, 0.9, true);
    for (let b = 0; b < 4; b++) { kick(t + b * BEAT, 0.9, true); hat(t + b * BEAT + 0.25, 1.0, 0.25, true); if (b % 2) snap(t + b * BEAT, 0.9); }
    for (let s = 0; s < 16; s++) glassPluck(t + s * S16, CH[c][(s * 3) % 4] + 12, 0.35, ((s % 4) - 1.5) * 0.4); });
  melody2.forEach(([t, m]) => glassPluck(t, m + 12, 0.8, 0));
  reverb(0.86, 0.4, 0.3); silence(12.0, 12.25); writeWav("sample-B.wav");
}
function sampleC() { // 马林巴拨奏
  reset();
  HOOK.forEach(([t, m]) => marimba(t, m, 1.2, 0.1));
  kalimba(0.5, 64, 0.7, -0.3); kalimba(0.5, 71, 0.6, 0.3);
  for (let t = 2; t < 4; t += BEAT / 2) kalimba(t, [76, 80, 83, 80][Math.round((t - 2) * 4) % 4], 0.5, 0.3);
  explain.forEach(([c, t]) => { for (let b = 0; b < 8; b++) pluckKS(t + b * 0.25, CH[c][b % 4] - 12, 0.5, ((b % 2) - 0.5) * 0.6, 0.35, 0.6);
    pluckKS(t, ROOT[c], 0.8, 0, 0.3, 1.5); for (let s = 0; s < 16; s++) shaker(t + s * S16, s % 2 ? 0.5 : 1); kick(t, 0.45); kick(t + 1, 0.35); });
  melody.forEach(([t, m]) => marimba(t, m, 0.7, -0.1));
  RESOLVE.forEach(([t, m]) => marimba(t, m, 1.3, 0));
  reveal.forEach(([c, t]) => { CH[c].forEach((m, k) => kalimba(t + k * 0.06, m, 0.55, (k - 1.5) * 0.35)); pluckKS(t, ROOT[c], 0.9, 0, 0.3, 1.8);
    for (let b = 0; b < 8; b++) pluckKS(t + b * 0.25, CH[c][(b * 3) % 4], 0.45, ((b % 2) - 0.5) * 0.7, 0.4, 0.5);
    for (let b = 0; b < 4; b++) { kick(t + b * BEAT, 0.6); if (b % 2) snap(t + b * BEAT, 0.8); } for (let s = 0; s < 16; s++) shaker(t + s * S16, s % 2 ? 0.6 : 1.1); });
  melody2.forEach(([t, m]) => marimba(t, m, 0.8, 0.1));
  reverb(0.8, 0.35, 0.28); silence(12.0, 12.25); writeWav("sample-C.wav");
}
sampleA(); sampleB(); sampleC();
