// music/samples2.mjs — 新一季配乐方向样曲第二轮（用户 11-27：「配乐要大改，现在听着跟之前的还是很接近」）
//   node music/samples2.mjs  ->  out/sample-D.wav, sample-E.wav, sample-F.wav
// 第一轮只换了音色，骨架（120 BPM、十六分音符律动、mi-sol-la 动机、流行进行）没变。这一轮全部换掉：
// D Lo-fi 爵士：84 BPM，摇摆十六分，电钢琴九和弦（D 大调 Gmaj9–F#m7–Em9–A13），闷鼓 + 黑胶底噪，低音提琴式拨弦
// E 极简钢琴：100 BPM，降 A 大调，毡片钢琴八分音符琶音（Steve Reich / Nils Frahm 那一路），暖铺底，鼓只在揭晓时进
// F 波萨诺瓦：132 BPM（二拍子感），F 大调 ii–V–I（Gm9–C13–Fmaj9–Dm9），尼龙吉他扫弦、边击、沙锤、低音 1–5
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

// ---------------------------------------------------------------- D Lo-fi 爵士 (84 BPM, D major, swung 16ths)
function sampleD() {
  const BPM = 84, B = 60 / BPM, S = B / 4, sw = (i) => i * S + (i % 2 ? S * 0.28 : 0); // swing
  const bars = 7.2, stopAt = 4 * 4 * B; reset(bars * 4 * B + 1.2);
  // chords: Gmaj9  F#m7  Em9  A13  |  Gmaj9  A13  Dmaj9
  const prog = [[[55, 59, 62, 66, 69], 43], [[54, 57, 61, 64], 42], [[52, 55, 59, 62, 66], 40], [[55, 59, 61, 66], 45], [[55, 59, 62, 66, 69], 43], [[55, 59, 61, 66], 45], [[54, 57, 61, 64, 66], 38]];
  crackle();
  prog.forEach(([ch, root], bar) => {
    const t0 = bar * 4 * B; if (bar === 4) revealD(t0 + B * 0.5); if (bar >= 4) return;
    ch.forEach((m, k) => rhodes(t0 + sw(0) + k * 0.018, m, B * 1.6, 0.6, (k - 2) * 0.25)); ch.forEach((m, k) => rhodes(t0 + sw(10), m, B * 0.9, 0.35, (k - 2) * 0.25));
    if (bar > 0) { uprightBass(t0, root, B * 1.4); uprightBass(t0 + sw(6), root + 7, B * 0.5, 0.7); uprightBass(t0 + 3 * B, root + 12, B * 0.7, 0.6);
      [0, 10].forEach(i => lofiKick(t0 + sw(i), 0.9)); [4, 12].forEach(i => lofiSnare(t0 + sw(i), 0.8)); for (let i = 0; i < 16; i += 2) softHat(t0 + sw(i), i % 4 ? 0.6 : 1); }
  });
  // motif: a lazy falling three-note line on a small bell — A5 F#5 D5 … E5
  [[0.5, 81], [0.75, 78], [1.25, 74], [2.25, 76]].forEach(([b, m]) => bell(b * B, m, 0.9, 0.2));
  function revealD(t0) { // after the half-beat stop: motif resolves up — A5 F#5 A5 D6
    [[0, 81], [0.25, 78], [0.75, 81], [1.25, 86]].forEach(([b, m]) => bell(t0 + b * B, m, 1.0, 0.1));
    [[prog[4], 0], [prog[5], 1], [prog[6], 2]].forEach(([[ch, root], k]) => { const tt = t0 + k * 4 * B;
      ch.forEach((m, j) => rhodes(tt + sw(0) + j * 0.015, m, B * 1.8, 0.7, (j - 2) * 0.25)); uprightBass(tt, root, B * 1.5, 1.0); uprightBass(tt + 2 * B, root + 7, B * 1.2, 0.8);
      [0, 6, 10].forEach(i => lofiKick(tt + sw(i), 1.0)); [4, 12].forEach(i => lofiSnare(tt + sw(i), 1.0)); for (let i = 0; i < 16; i++) softHat(tt + sw(i), i % 2 ? 0.5 : 1); });
  }
  reverb(0.8, 0.45, 0.25); lowpassAll(7000); silence(stopAt, stopAt + B * 0.5); writeWav("sample-D.wav");
}
// ---------------------------------------------------------------- E 极简钢琴 (100 BPM, A-flat major, 8th-note arpeggios)
function sampleE() {
  const BPM = 100, B = 60 / BPM, E8 = B / 2; reset(9 * 4 * B / 1.0 * 0.5 + 9 + 1.5);
  // Ab  Fm  Db(add9)  Eb(sus4→3) … reveal: Db  Eb  Ab(add9)
  const prog = [[[56, 63, 68, 72], [44]], [[53, 60, 65, 68], [41]], [[49, 56, 61, 63, 65], [37]], [[51, 58, 63, 68], [39]]];
  const rev = [[[49, 56, 61, 65, 68], [37]], [[51, 58, 63, 67, 70], [39]], [[56, 63, 68, 70, 72, 75], [44]]];
  const arp = (t0, ch, bars, v) => { const pat = [0, 2, 1, 3, 2, 1, 3, 2]; for (let i = 0; i < bars * 8; i++) feltPiano(t0 + i * E8, ch[pat[i % 8] % ch.length] + 12, v * (i % 2 ? 0.7 : 1), ((i % 4) - 1.5) * 0.25, 2.8); };
  let t = 0;
  // opening: motif alone, then arpeggio starts — C6 Eb6 Ab6 … G6
  [[0, 84], [0.5, 87], [1, 92], [2, 91]].forEach(([b, m]) => feltPiano(b * B, m, 1.1, 0.1, 1.4));
  pad(0, [56, 63, 68], 4 * B, 0.8); feltPiano(0, 44, 0.9, 0, 0.8); t = 4 * B;
  prog.forEach(([ch, [root]]) => { arp(t, ch, 1, 0.75); pad(t, ch, 4 * B, 0.8); feltPiano(t, root, 0.9, 0, 0.7); t += 4 * B; });
  const stop = t; t += B * 0.5;
  [[0, 84], [0.5, 87], [1, 92], [1.5, 96]].forEach(([b, m]) => feltPiano(t + b * B, m, 1.2, 0.05, 1.2)); // resolves up to C7
  rev.forEach(([ch, [root]], k) => { arp(t, ch, 1, 0.9); pad(t, ch.map(m => m + 12), 4 * B, 0.9); feltPiano(t, root, 1.0, 0, 0.6); feltPiano(t, root - 12, 0.7, 0, 0.5);
    for (let b = 0; b < 4; b++) { kick(t + b * B, b % 2 ? 0.35 : 0.6); shaker(t + b * B + E8, 0.8); } t += 4 * B; });
  reverb(0.88, 0.3, 0.38); silence(stop, stop + B * 0.5); writeWav("sample-E.wav");
}
// ---------------------------------------------------------------- F 波萨诺瓦 (132 BPM, F major, ii–V–I)
function sampleF() {
  const BPM = 132, B = 60 / BPM, S8 = B / 2; reset(11 * 4 * B + 1.5);
  const ch = { Gm9: [55, 58, 62, 65, 69], C13: [52, 58, 62, 64, 69], F9: [53, 57, 60, 64, 67], Dm9: [50, 57, 60, 64, 65], Bb: [58, 62, 65, 69], Am7: [57, 60, 64, 67] };
  const rt = { Gm9: 43, C13: 36, F9: 41, Dm9: 38, Bb: 46, Am7: 45 };
  const explain = ["Gm9", "C13", "F9", "Dm9", "Gm9", "C13"], reveal = ["Bb", "C13", "F9", "F9"];
  const comp = [0, 3, 6, 10, 13]; // bossa comping in 8ths over 2 bars (16 eighths): 1, 2&, 4, 2-of-bar2&, 3&...
  const clave = [0, 3, 6, 10, 12];
  const bar2 = (t0, a, b, v = 0.7) => { comp.forEach(e => { const c = e < 8 ? a : b; strum(t0 + e * S8, ch[c].map(m => m - 0), v, e % 2 === 0, 0.5); });
    [a, b].forEach((c, k) => { const tb = t0 + k * 4 * B; uprightBass(tb, rt[c], B * 1.4, 0.9); uprightBass(tb + 1.5 * B, rt[c] + 7, B * 0.4, 0.6); uprightBass(tb + 2 * B, rt[c] + 7, B * 1.4, 0.8); uprightBass(tb + 3.5 * B, rt[c], B * 0.4, 0.6); });
    clave.forEach(e => rimClick(t0 + e * S8, 0.8)); for (let i = 0; i < 16; i++) shaker(t0 + i * S8, i % 2 ? 0.5 : 0.9); for (let k = 0; k < 4; k++) lofiKick(t0 + k * 2 * B, 0.4); };
  // opening: guitar motif alone — A4 C5 F5 E5 (sweet major-7 colour)
  [[0, 69], [0.5, 72], [1, 77], [2, 76]].forEach(([b, m]) => guitar(b * B, m, 1.1, 0.15, 1.5)); strum(0, ch.F9, 0.5, true, 2.5);
  let t = 4 * B; for (let i = 0; i < explain.length; i += 2) { bar2(t, explain[i], explain[i + 1]); t += 8 * B; }
  // melody over the explanation
  [[4, 77], [5, 76], [5.5, 74], [6.5, 72], [8, 74], [9, 72], [9.5, 70], [10.5, 69], [12, 72], [13, 74], [14, 76]].forEach(([b, m]) => guitar(b * B, m + 12, 0.8, 0.3, 0.8));
  const stop = t; t += B * 0.5;
  [[0, 69], [0.5, 72], [1, 77], [1.5, 81]].forEach(([b, m]) => guitar(t + b * B, m, 1.2, 0.1, 1.6)); // resolves up to A5
  for (let i = 0; i < reveal.length; i += 2) { bar2(t, reveal[i], reveal[i + 1], 0.85); t += 8 * B; }
  reverb(0.78, 0.4, 0.22); silence(stop, stop + B * 0.5); writeWav("sample-F.wav");
}
sampleD(); sampleE(); sampleF();
