// music/samples3.mjs — 配乐第三轮：三段「轻快」的（用户 11-27：「配乐再换三个轻快的」）
//   node music/samples3.mjs  ->  out/sample-G.wav, sample-H.wav, sample-I.wav
// G 尤克里里：112 BPM，G 大调，尤克里里扫弦 + 钟琴 + 拍手 + 口哨旋律（vlog 那种开心）
// H 轻放克：108 BPM，降 B 大调，切音吉他 + 克拉维 + 跳跳的贝斯 + 碎拍鼓（不是四拍底鼓）
// I 钢鼓热带：104 BPM，D 大调，钢鼓旋律 + 反拍吉他切音 + 康加 + 沙锤（海边那种松快）
// 结构同前：开头（新动机）→ 讲解 → 停半拍（真静音）→ 揭晓（动机解决），约 20 秒。
// 每段都是：开头（新动机）→ 讲解 → 停半拍（真静音）→ 揭晓（动机解决），约 20 秒。
import { writeFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const OUT = join(dirname(fileURLToPath(import.meta.url)), "..", "out");
mkdirSync(OUT, { recursive: true });
const SR = 48000, TAU = Math.PI * 2;
const mtof = (m) => 440 * Math.pow(2, (m - 69) / 12);
let seed = 4242, N, L, R, SL, SRv;
const rnd = () => { seed |= 0; seed = (seed + 0x6d2b79f5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
function reset(dur) { N = Math.ceil(SR * dur); L = new Float32Array(N); R = new Float32Array(N); SL = new Float32Array(N); SRv = new Float32Array(N); seed = 4242; }
function put(t0, len, gen, { gain = 1, pan = 0, rev = 0.2 } = {}) {
  const i0 = Math.max(0, Math.floor(t0 * SR)), i1 = Math.min(N, Math.floor((t0 + len) * SR));
  const gl = gain * Math.cos(((pan + 1) * Math.PI) / 4), gr = gain * Math.sin(((pan + 1) * Math.PI) / 4);
  for (let i = i0; i < i1; i++) { const v = gen(i / SR - t0); if (!Number.isFinite(v)) continue; L[i] += v * gl; R[i] += v * gr; SL[i] += v * gl * rev; SRv[i] += v * gr * rev; }
}
function reverb(size, damp, wet) {
  const combs = [1557, 1617, 1491, 1422, 1277, 1356], aps = [556, 441, 341];
  const proc = (inp, sp) => { const out = new Float32Array(N);
    for (const c of combs) { const d = c + sp, b = new Float32Array(d); let k = 0, fs = 0; for (let i = 0; i < N; i++) { const y = b[k]; fs = y * (1 - damp) + fs * damp; b[k] = inp[i] + fs * size; k = (k + 1) % d; out[i] += y / combs.length; } }
    for (const a of aps) { const d = a + sp, b = new Float32Array(d); let k = 0; for (let i = 0; i < N; i++) { const bb = b[k], x = out[i]; b[k] = x + bb * 0.5; out[i] = bb - x; k = (k + 1) % d; } }
    return out; };
  const wl = proc(SL, 0), wr = proc(SRv, 23); for (let i = 0; i < N; i++) { L[i] += wl[i] * wet; R[i] += wr[i] * wet; }
}
function lowpassAll(fc) { const a = 1 - Math.exp(-TAU * fc / SR); let l = 0, r = 0; for (let i = 0; i < N; i++) { l += a * (L[i] - l); r += a * (R[i] - r); L[i] = l; R[i] = r; } }
function silence(t0, t1) { for (let i = Math.floor(t0 * SR); i < Math.min(N, Math.floor(t1 * SR)); i++) L[i] = R[i] = 0; }
function writeWav(name) {
  let pk = 1e-9; for (let i = 0; i < N; i++) pk = Math.max(pk, Math.abs(L[i]), Math.abs(R[i]));
  const g = 0.89 / pk, buf = Buffer.alloc(44 + N * 4);
  buf.write("RIFF", 0); buf.writeUInt32LE(36 + N * 4, 4); buf.write("WAVEfmt ", 8); buf.writeUInt32LE(16, 16); buf.writeUInt16LE(1, 20); buf.writeUInt16LE(2, 22);
  buf.writeUInt32LE(SR, 24); buf.writeUInt32LE(SR * 4, 28); buf.writeUInt16LE(4, 32); buf.writeUInt16LE(16, 34); buf.write("data", 36); buf.writeUInt32LE(N * 4, 40);
  for (let i = 0; i < N; i++) { buf.writeInt16LE(Math.round(Math.max(-1, Math.min(1, L[i] * g)) * 32767), 44 + i * 4); buf.writeInt16LE(Math.round(Math.max(-1, Math.min(1, R[i] * g)) * 32767), 46 + i * 4); }
  writeFileSync(join(OUT, name), buf); console.log(name, (N / SR).toFixed(1) + " s");
}
const att = (tt, a = 0.002) => Math.min(1, tt / a);
const rel = (tt, len, r) => (tt < len ? 1 : Math.max(0, 1 - (tt - len) / r));

// ---------------------------------------------------------------- instruments
function rhodes(t, m, len, v = 1, pan = 0) { const f = mtof(m);
  put(t, len + 0.6, (tt) => v * 0.13 * att(tt, 0.004) * Math.exp(-tt * 1.1) * rel(tt, len, 0.5) * (Math.sin(TAU * f * tt + 1.1 * Math.exp(-tt * 4) * Math.sin(TAU * f * tt)) * (1 + 0.15 * Math.sin(TAU * 4.8 * tt)) + 0.15 * Math.sin(TAU * f * 14 * tt) * Math.exp(-tt * 45)), { pan, rev: 0.25 }); }
function feltPiano(t, m, v = 1, pan = 0, dec = 2.2) { const f = mtof(m), dt = 0.0015 * f;
  put(t, 3.0, (tt) => { const e = att(tt, 0.006) * Math.exp(-tt * dec); let s = Math.sin(TAU * f * tt) + 0.5 * Math.sin(TAU * (f + dt) * tt) + 0.35 * Math.sin(TAU * 2 * f * tt) * Math.exp(-tt * 3) + 0.12 * Math.sin(TAU * 3 * f * tt) * Math.exp(-tt * 6);
    const thump = (rnd() * 2 - 1) * Math.exp(-tt * 120) * 0.15; return v * 0.12 * (s * e + thump); }, { pan, rev: 0.45 }); }
function pad(t, notes, len, v = 1) { notes.forEach((m, k) => { const f = mtof(m), ph = [rnd(), rnd()];
  put(t, len + 1.2, (tt) => v * 0.02 * (Math.sin(TAU * (f * tt + ph[0])) + Math.sin(TAU * (f * 1.003 * tt + ph[1])) + 0.25 * Math.sin(TAU * 2 * f * tt)) * Math.min(1, tt / 0.8) * rel(tt, len, 1.2), { pan: (k - (notes.length - 1) / 2) * 0.35, rev: 0.6 }); }); }
function uprightBass(t, m, len, v = 1) { const f = mtof(m); put(t, len + 0.1, (tt) => v * 0.17 * (Math.sin(TAU * f * tt) + 0.3 * Math.sin(TAU * 2 * f * tt) * Math.exp(-tt * 8)) * att(tt, 0.006) * Math.exp(-tt * 2.2) * rel(tt, len, 0.08), { rev: 0.05 }); }
function guitar(t, m, v = 1, pan = 0, len = 1.2) { // Karplus–Strong nylon
  const p = Math.max(2, Math.round(SR / mtof(m))), b = new Float32Array(p); let lp = 0; for (let i = 0; i < p; i++) { lp += 0.5 * ((rnd() * 2 - 1) - lp); b[i] = lp; } let k = 0;
  put(t, len, (tt) => { const y = b[k], nx = b[(k + 1) % p]; b[k] = 0.4985 * (y + nx); k = (k + 1) % p; return v * 0.3 * y * Math.min(1, (len - tt) / 0.06); }, { pan, rev: 0.22 }); }
function strum(t, notes, v = 1, down = true, len = 0.9) { (down ? notes : notes.slice().reverse()).forEach((m, k) => guitar(t + k * 0.012, m, v * (0.8 + 0.2 * rnd()), (k / notes.length - 0.5) * 0.5, len)); }
function bell(t, m, v = 1, pan = 0) { const f = mtof(m); put(t, 2.5, (tt) => v * 0.1 * Math.sin(TAU * f * tt + 1.6 * Math.exp(-tt * 4) * Math.sin(TAU * f * 3.01 * tt)) * Math.exp(-tt * 2.4) * att(tt), { pan, rev: 0.5 }); }
function lofiKick(t, v = 1) { put(t, 0.4, (tt) => v * 0.55 * Math.sin(TAU * (50 * tt + 70 * (1 - Math.exp(-tt * 25)) / 25)) * Math.exp(-tt * 9) * att(tt, 0.003), { rev: 0 }); }
function lofiSnare(t, v = 1) { let lp = 0; put(t, 0.25, (tt) => { const n = rnd() * 2 - 1; lp += 0.25 * (n - lp); return v * (0.5 * lp * Math.exp(-tt * 16) + 0.25 * Math.sin(TAU * 185 * tt) * Math.exp(-tt * 28)); }, { pan: -0.05, rev: 0.2 }); }
function softHat(t, v = 1, pan = 0.3) { let hp = 0, pv = 0; put(t, 0.06, (tt) => { const n = rnd() * 2 - 1; hp = 0.8 * (hp + n - pv); pv = n; return v * 0.06 * hp * Math.exp(-tt * 70); }, { pan, rev: 0.05 }); }
function rimClick(t, v = 1) { put(t, 0.05, (tt) => v * 0.35 * (Math.sin(TAU * 1650 * tt) + 0.5 * Math.sin(TAU * 820 * tt)) * Math.exp(-tt * 110), { pan: 0.25, rev: 0.12 }); }
function shaker(t, v = 1, pan = -0.35) { let hp = 0, pv = 0; put(t, 0.08, (tt) => { const n = rnd() * 2 - 1; hp = 0.7 * (hp + n - pv); pv = n; return v * 0.06 * hp * Math.sin(Math.PI * Math.min(1, tt / 0.08)); }, { pan, rev: 0.08 }); }
function crackle() { for (let t = 0; t < N / SR; t += 0.03 + rnd() * 0.25) put(t, 0.004, (tt) => (rnd() * 2 - 1) * 0.08 * (1 - tt / 0.004), { pan: rnd() - 0.5, rev: 0 });
  let lp = 0; put(0, N / SR, () => { lp += 0.02 * ((rnd() * 2 - 1) - lp); return lp * 0.05; }, { rev: 0 }); }
function kick(t, v = 1) { put(t, 0.45, (tt) => v * 0.7 * Math.sin(TAU * (52 * tt + 90 * (1 - Math.exp(-tt * 30)) / 30)) * Math.exp(-tt * 7) * att(tt), { rev: 0 }); }

// ---------------------------------------------------------------- new instruments
function uke(t, m, v = 1, pan = 0, len = 0.7) { // bright, short Karplus–Strong
  const p = Math.max(2, Math.round(SR / mtof(m))), b = new Float32Array(p); for (let i = 0; i < p; i++) b[i] = rnd() * 2 - 1; let k = 0;
  put(t, len, (tt) => { const y = b[k], nx = b[(k + 1) % p]; b[k] = 0.497 * (y + nx); k = (k + 1) % p; return v * 0.2 * y * Math.min(1, (len - tt) / 0.04); }, { pan, rev: 0.18 }); }
function ukeStrum(t, notes, v = 1, down = true) { (down ? notes : notes.slice().reverse()).forEach((m, k) => uke(t + k * 0.009, m, v * (0.85 + 0.15 * rnd()), (k - 1.5) * 0.2)); }
function glock(t, m, v = 1, pan = 0.2) { const f = mtof(m); put(t, 1.6, (tt) => v * 0.1 * (Math.sin(TAU * f * tt) + 0.25 * Math.sin(TAU * f * 2.76 * tt) * Math.exp(-tt * 8) + 0.1 * Math.sin(TAU * f * 5.4 * tt) * Math.exp(-tt * 20)) * Math.exp(-tt * 2.6) * att(tt, 0.001), { pan, rev: 0.35 }); }
function clap(t, v = 1) { let lp = 0; put(t, 0.25, (tt) => { const n = rnd() * 2 - 1; lp += 0.5 * (n - lp); const e = tt < 0.025 ? (Math.floor(tt / 0.008) % 2 ? 0.4 : 1) : Math.exp(-(tt - 0.025) * 18); return v * 0.3 * (n - lp) * e; }, { pan: 0.05, rev: 0.25 }); }
function whistle(t, m, len, v = 1) { const f = mtof(m); let ph = 0;
  put(t, len + 0.1, (tt) => { const vib = 1 + 0.006 * Math.sin(TAU * 5.5 * tt) * Math.min(1, tt * 4); ph += f * vib / SR; return v * 0.12 * (Math.sin(TAU * ph) + 0.04 * (rnd() * 2 - 1)) * Math.min(1, tt / 0.03) * rel(tt, len, 0.08); }, { pan: -0.1, rev: 0.3 }); }
function clav(t, m, len = 0.12, v = 1, pan = 0.25) { const f = mtof(m); let ph = 0, lp = 0;
  put(t, len + 0.03, (tt) => { ph = (ph + f / SR) % 1; const s = ph < 0.25 ? 1 : -0.33; lp += (0.25 + 0.5 * Math.exp(-tt * 30)) * (s - lp); return v * 0.16 * lp * att(tt, 0.001) * rel(tt, len, 0.02); }, { pan, rev: 0.12 }); }
function mute(t, m, v = 1, pan = -0.3) { uke(t, m, v * 0.8, pan, 0.09); }
function popBass(t, m, len, v = 1) { const f = mtof(m); put(t, len + 0.05, (tt) => v * 0.2 * (Math.sin(TAU * f * tt) + 0.5 * Math.sin(TAU * 2 * f * tt) * Math.exp(-tt * 14) + 0.25 * Math.sin(TAU * 3 * f * tt) * Math.exp(-tt * 25)) * att(tt, 0.002) * Math.exp(-tt * 3) * rel(tt, len, 0.04), { rev: 0.03 }); }
function snareBright(t, v = 1) { let hp = 0, pv = 0; put(t, 0.2, (tt) => { const n = rnd() * 2 - 1; hp = 0.6 * (hp + n - pv); pv = n; return v * (0.35 * hp * Math.exp(-tt * 20) + 0.25 * Math.sin(TAU * 210 * tt) * Math.exp(-tt * 30)); }, { rev: 0.18 }); }
function steelpan(t, m, v = 1, pan = 0.1) { const f = mtof(m); put(t, 1.4, (tt) => v * 0.12 * (Math.sin(TAU * f * tt) + 0.6 * Math.sin(TAU * 2.005 * f * tt) * Math.exp(-tt * 5) + 0.3 * Math.sin(TAU * 3.98 * f * tt) * Math.exp(-tt * 9)) * Math.exp(-tt * 3.2) * Math.min(1, tt / 0.004), { pan, rev: 0.3 }); }
function conga(t, hi = false, v = 1) { const f0 = hi ? 330 : 220; put(t, 0.25, (tt) => v * 0.3 * Math.sin(TAU * f0 * tt * (1 + 0.3 * Math.exp(-tt * 40))) * Math.exp(-tt * (hi ? 18 : 12)) * att(tt, 0.001), { pan: hi ? 0.35 : -0.25, rev: 0.12 }); }
const tri = (tt) => 0;

// ---------------------------------------------------------------- G 尤克里里 (112 BPM, G major)
function sampleG() {
  const B = 60 / 112, S = B / 2; reset(4 * B * 10 + 1.5);
  const C = { G: [67, 62, 59, 55], C: [67, 64, 60, 55], D: [69, 66, 62, 57], Em: [67, 64, 59, 55], Am: [69, 64, 60, 57] }; // re-entrant-ish voicings
  const R = { G: 43, C: 48, D: 50, Em: 52, Am: 45 };
  const pattern = [[0, 1], [2, 1], [3, 0], [5, 0], [6, 1], [7, 0]]; // D . D U . U D U
  const bar = (t0, c, v = 0.8, full = true) => { pattern.forEach(([e, d]) => ukeStrum(t0 + e * S, C[c], v * (d ? 1 : 0.75), !!d));
    if (full) { popBass(t0, R[c], B * 0.9, 0.9); popBass(t0 + 2 * B, R[c] + 7, B * 0.9, 0.8); lofiKick(t0, 0.9); lofiKick(t0 + 2.5 * B, 0.7); clap(t0 + B, 0.8); clap(t0 + 3 * B, 0.8); for (let i = 0; i < 8; i++) shaker(t0 + i * S, i % 2 ? 0.6 : 1); } };
  // opening motif on glockenspiel: D6 G6 B6 A6
  [[0, 86], [0.5, 91], [1, 95], [1.5, 93]].forEach(([b, m]) => glock(b * B, m, 1.1)); bar(0, "G", 0.8, false); bar(4 * B, "G", 0.85, true);
  let t = 8 * B; ["G", "Em", "C", "D"].forEach(c => { bar(t, c); t += 4 * B; });
  [[8, 79, 1], [9, 81, 0.5], [9.5, 83, 1.5], [12, 83, 1], [13, 84, 0.5], [13.5, 86, 1.5], [16, 84, 1], [17, 83, 0.5], [17.5, 81, 1.5], [20, 81, 1], [21, 79, 0.5], [21.5, 78, 1.5]].forEach(([b, m, l]) => whistle(b * B, m, l * B * 0.9, 0.9));
  const stop = t; t += S;
  [[0, 86], [0.5, 91], [1, 95], [1.5, 98]].forEach(([b, m]) => glock(t + b * B, m, 1.2)); // resolves up to D7
  ["C", "D", "G", "G"].forEach((c, k) => { bar(t, c, 0.95); if (k < 2) [[0, 88], [1, 86], [2, 83], [3, 86]].forEach(([b, m]) => glock(t + b * B, m, 0.5, -0.2)); t += 4 * B; });
  [[0, 79], [1, 83], [2, 86], [3, 91]].forEach(([b, m]) => whistle(t - 8 * B + b * B, m, B * 0.8, 0.9));
  reverb(0.75, 0.4, 0.2); silence(stop, stop + S); writeWav("sample-G.wav");
}
// ---------------------------------------------------------------- H 轻放克 (108 BPM, B-flat major)
function sampleH() {
  const B = 60 / 108, S = B / 4; reset(4 * B * 9 + 1.5);
  const CH = { Bb: [62, 65, 69, 72], Eb: [63, 67, 70, 74], Cm: [60, 63, 67, 70], F: [60, 65, 69, 72], Gm: [62, 65, 70, 74] };
  const R = { Bb: 46, Eb: 39, Cm: 48, F: 41, Gm: 43 };
  const bassline = [[0, 0, 1.5], [3, 12, 0.5], [6, 0, 1], [8, 7, 1], [10, 10, 0.5], [11, 12, 1], [14, 7, 1]]; // 16th positions, interval, length(16ths)
  const groove = (t0, c, v = 1, drums = true) => {
    [2, 6, 10, 13].forEach(i => clav(t0 + i * S, CH[c][i % 4], 0.1, 0.9 * v));
    [1, 4, 7, 9, 12, 15].forEach(i => mute(t0 + i * S, CH[c][(i + 1) % 4] - 12, 0.7 * v));
    bassline.forEach(([i, iv, l]) => popBass(t0 + i * S, R[c] + iv, l * S, v));
    if (drums) { [0, 7, 10].forEach(i => lofiKick(t0 + i * S, 0.8)); [4, 12].forEach(i => snareBright(t0 + i * S, 0.9)); for (let i = 0; i < 16; i++) softHat(t0 + i * S, i % 2 ? 0.5 : 1.2, 0.3); clap(t0 + 12 * S, 0.5); } };
  // opening motif (clav, bluesy): F5 Ab5 Bb5 … D6
  [[0, 77], [0.5, 80], [0.75, 82], [1.5, 86]].forEach(([b, m]) => clav(b * B, m, 0.18, 1.3, 0)); groove(0, "Bb", 0.6, false); groove(4 * B, "Bb", 0.8, true);
  let t = 8 * B; ["Eb", "Cm", "F", "F"].forEach(c => { groove(t, c); t += 4 * B; });
  const stop = t; t += 2 * S;
  [[0, 77], [0.5, 80], [0.75, 82], [1.25, 89]].forEach(([b, m]) => clav(t + b * B, m, 0.2, 1.4, 0)); // up to F6
  ["Eb", "F", "Bb"].forEach(c => { groove(t, c, 1.05); CH[c].forEach((m, k) => glock(t, m + 12, 0.35, (k - 1.5) * 0.3)); t += 4 * B; });
  reverb(0.7, 0.45, 0.16); silence(stop, stop + 2 * S); writeWav("sample-H.wav");
}
// ---------------------------------------------------------------- I 钢鼓热带 (104 BPM, D major)
function sampleI() {
  const B = 60 / 104, S = B / 4; reset(4 * B * 9 + 1.5);
  const CH = { D: [62, 66, 69], G: [62, 67, 71], A: [61, 64, 69], Bm: [62, 66, 71], Em: [59, 64, 67] };
  const R = { D: 38, G: 43, A: 45, Bm: 47, Em: 40 };
  const bar = (t0, c, v = 1, full = true) => {
    [2, 6, 10, 14].forEach(i => ukeStrum(t0 + i * S, CH[c].map(m => m + 0), 0.55 * v, true)); // off-beat skank
    if (full) { popBass(t0, R[c], 3 * S, 0.9 * v); popBass(t0 + 3 * S, R[c] + 7, 2 * S, 0.7 * v); popBass(t0 + 8 * B / 4, R[c] + 12, 2 * S, 0.7 * v); popBass(t0 + 12 * S, R[c] + 7, 3 * S, 0.8 * v);
      [0, 6, 8].forEach(i => lofiKick(t0 + i * S, 0.6)); [3, 7, 11, 14, 15].forEach((i, k) => conga(t0 + i * S, k % 2 === 1, 0.8)); for (let i = 0; i < 16; i++) shaker(t0 + i * S, i % 2 ? 0.5 : 1); rimClick(t0 + 4 * S, 0.6); rimClick(t0 + 12 * S, 0.6); } };
  // opening motif on steel pan: A5 D6 F#6 E6
  [[0, 81], [0.5, 86], [0.75, 90], [1.5, 88]].forEach(([b, m]) => steelpan(b * B, m, 1.1)); bar(0, "D", 0.7, false); bar(4 * B, "D", 0.85);
  let t = 8 * B; ["G", "A", "Bm", "A"].forEach(c => { bar(t, c); t += 4 * B; });
  [[8, 78], [8.75, 81], [9.5, 83], [10.5, 81], [12, 81], [12.75, 85], [13.5, 88], [14.5, 85], [16, 86], [16.75, 83], [17.5, 81], [18.5, 78], [20, 81], [20.75, 85], [21.5, 88], [22.5, 85]].forEach(([b, m]) => { steelpan(b * B, m, 0.75); steelpan(b * B + 0.07, m, 0.3, -0.3); });
  const stop = t; t += 2 * S;
  [[0, 81], [0.5, 86], [0.75, 90], [1.25, 93]].forEach(([b, m]) => steelpan(t + b * B, m, 1.2)); // up to A6
  ["G", "A", "D"].forEach(c => { bar(t, c, 1.05); t += 4 * B; });
  reverb(0.76, 0.4, 0.2); silence(stop, stop + 2 * S); writeWav("sample-I.wav");
}
sampleG(); sampleH(); sampleI();
