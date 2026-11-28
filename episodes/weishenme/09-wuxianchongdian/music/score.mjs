// music/score.mjs — EP.09 的整片配乐 + 音效，全部代码合成，读 ../timeline.js，让每个音落在画面动作上。
//   node music/score.mjs  ->  out/score.wav（再 sh tools/master.sh out/score.wav audio/mix.wav → -14 LUFS）
// 第二季配乐：钢鼓热带（用户 11-27 选样曲 I），104 BPM，D 大调。
//   开头（0–4.6）：钢鼓动机 sol-do-mi-re（A5 D6 F#6 E6，没解决）+ 轻反拍切音，没有鼓
//   讲解（4.6–17.9）：G–A–Bm–A，反拍切音 + 贝斯 + 康加 + 沙锤，钢鼓旋律；问题处一个上行四度两音（钟琴）
//   停半拍 → 揭晓（17.9 名词）：动机解决 sol-do-mi-sol（A5 D6 F#6 A6），全编制 G–A–D
//   第 5 段（20.8–36.6）：Em–A–D–Bm，织体加满；36.6–47.6「说话」段收成钢鼓琶音 + 沙锤（让 ping / 回话 的音效听得见）
//   停半拍 → 闭环（47.6）：动机再解决，全编制；小提示放轻；片尾卡：动机 + 最后的问号音
import { createRequire } from "node:module";
const TL = createRequire(import.meta.url)("../timeline.js");
const { T, HITS, DUR, E8 } = TL;
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

// ---------------------------------------------------------------- sound effects
function thunk(t, v = 1) { put(t, 0.3, (tt) => v * 0.5 * Math.sin(TAU * (90 * tt + 60 * (1 - Math.exp(-tt * 30)) / 30)) * Math.exp(-tt * 16) * att(tt, 0.002), { rev: 0.05 }); glock(t + 0.01, 98, 0.35, 0.1); }   // phone lands on glass
function chime(t, v = 1) { [86, 93].forEach((m, i) => glock(t + i * 0.06, m, 0.8 * v, 0.15)); }                       // ⚡ charging
function qmark(t) { glock(t, 81, 0.55, -0.2); glock(t + E8 / 2, 86, 0.6, -0.2); }                                     // every question: a rising fourth
function click(t, v = 1, f0 = 2400) { put(t, 0.04, (tt) => v * 0.3 * Math.sin(TAU * f0 * tt) * Math.exp(-tt * 160), { pan: 0.1, rev: 0.05 }); }
function magSnap(t) { click(t, 1.2, 1800); thunk(t, 0.6); }
function ping(t) { put(t, 0.5, (tt) => 0.18 * Math.sin(TAU * 1320 * tt) * Math.exp(-tt * 7) * att(tt, 0.004), { pan: 0, rev: 0.4 }); }
function pop(t) { put(t, 0.12, (tt) => 0.25 * Math.sin(TAU * (500 + 900 * tt * 8) * tt) * Math.exp(-tt * 30), { pan: -0.2, rev: 0.2 }); }
function metal(t) { [3100, 4270, 5650].forEach((f, i) => put(t, 0.6, (tt) => 0.06 * Math.sin(TAU * f * tt) * Math.exp(-tt * (6 + i * 3)), { pan: 0.2, rev: 0.3 })); }
function slamHit(t) { lofiKick(t, 1.0); clap(t, 0.9); put(t, 0.8, (tt) => 0.12 * Math.sin(TAU * mtof(38) * tt) * Math.exp(-tt * 3), { rev: 0.1 }); }

// ---------------------------------------------------------------- the score
reset(DUR + 1.2);
const B = 60 / TL.BPM, S = B / 4;
const CH = { D: [62, 66, 69], G: [62, 67, 71], A: [61, 64, 69], Bm: [62, 66, 71], Em: [59, 64, 67] };
const ROOT = { D: 38, G: 43, A: 45, Bm: 47, Em: 40 };
function bar(t0, c, lvl) {          // lvl 0: skank only · 1: + bass, shaker · 2: + kick, congas, rims
  [2, 6, 10, 14].forEach((i) => ukeStrum(t0 + i * S, CH[c], 0.5, true));
  if (lvl >= 1) { popBass(t0, ROOT[c], 3 * S, 0.85); popBass(t0 + 3 * S, ROOT[c] + 7, 2 * S, 0.65); popBass(t0 + 8 * S, ROOT[c] + 12, 2 * S, 0.65); popBass(t0 + 12 * S, ROOT[c] + 7, 3 * S, 0.75);
    for (let i = 0; i < 16; i++) shaker(t0 + i * S, i % 2 ? 0.45 : 0.9); }
  if (lvl >= 2) { [0, 6, 8].forEach((i) => lofiKick(t0 + i * S, 0.6)); [3, 7, 11, 14, 15].forEach((i, k) => conga(t0 + i * S, k % 2 === 1, 0.7)); rimClick(t0 + 4 * S, 0.55); rimClick(t0 + 12 * S, 0.55); }
}
function bars(t0, t1, prog, lvl) { let i = 0; for (let t = t0; t < t1 - 0.01; t += 4 * B, i++) bar(t, prog[i % prog.length], typeof lvl === "function" ? lvl(i, t) : lvl); }
const panMel = (list, t0, v = 0.7) => list.forEach(([b, m]) => { steelpan(t0 + b * B, m, v); steelpan(t0 + b * B + 0.07, m, 0.28 * v, -0.3); });
const MOTIF = [[0, 81], [0.5, 86], [0.75, 90], [1.5, 88]], RESOLVE = [[0, 81], [0.5, 86], [0.75, 90], [1.25, 93]];
const MEL = [[0, 78], [0.75, 81], [1.5, 83], [2.5, 81], [4, 81], [4.75, 85], [5.5, 88], [6.5, 85], [8, 86], [8.75, 83], [9.5, 81], [10.5, 78], [12, 81], [12.75, 85], [13.5, 88], [14.5, 85]];

// 1 · opening
panMel(MOTIF, 0.0, 1.1); bar(0, "D", 0); bar(4 * B, "D", 1);
// 2–3 · into the coils (q1 → the lab)
bars(T.q1, T.labIn, ["G", "A"], (i) => (i < 1 ? 1 : 2));
// the lab: lighter — pan arpeggios + shaker; a bright plink each time a lamp lights
const arps = (t0, t1, prog, v = 0.32) => { for (let t = t0; t < t1 - 0.01; t += E8) { const k = Math.round((t - t0) / E8), c = prog[Math.floor(k / 8) % prog.length]; steelpan(t, CH[c][k % 3] + 12, v, ((k % 4) - 1.5) * 0.3); shaker(t, 0.55); } };
arps(T.labIn, T.backPad, ["Bm", "G", "A", "A"]); bars(T.labIn, T.backPad, ["Bm", "G", "A", "A"], 0);
const plink = (t, m) => { glock(t, m, 0.7, 0.25); steelpan(t, m - 12, 0.4, 0.25); };
plink(T.magIn1 + 0.15, 93); plink(T.magOut1 + 0.15, 90);
for (let t = T.shake + E8; t < T.labOut; t += 2 * E8) plink(t, Math.round((t - T.shake) / (2 * E8)) % 2 ? 90 : 93);
// back on the pad: the full band up to the half-beat stop before the name
bars(T.backPad, T.name - E8, ["G", "A", "Bm", "A"], 2);
panMel(MEL, T.backPad + 4 * B, 0.6);
// name: resolve; the AC → DC part keeps the full band
panMel(RESOLVE, T.name, 1.2); slamHit(T.name);
bars(T.name, T.q4, ["G", "A", "D", "D"], 2);
// 5a · alignment + heat (a darker colour while it's hot), magnets
bars(T.q4, T.metal, ["Em", "A", "D", "Bm"], 2);
panMel(MEL.map(([b, m]) => [b, m - 2]), T.q4, 0.55);
// 5b · metal: lighter while it heats; the pad gives up at T.stop (a falling tone), then only pads until the closing
arps(T.metal, T.stop, ["Em", "C" in CH ? "C" : "G", "A", "Bm"], 0.3); bars(T.metal, T.stop, ["Em", "G", "A", "Bm"], 1);
put(T.stop, 1.2, (tt) => 0.16 * Math.sin(TAU * (520 * tt - 180 * tt * tt)) * Math.exp(-tt * 2.5) * att(tt, 0.01), { rev: 0.4 });
for (let t = T.stop + E8; t < T.a14 - E8 - 0.01; t += 2 * E8) steelpan(t, CH.Bm[Math.round((t - T.stop) / (2 * E8)) % 3] + 12, 0.22, 0);
// closing: resolve + full band, tip lighter, end card motif + the question-mark note
panMel(RESOLVE, T.a14, 1.2); slamHit(T.a14);
bars(T.a14, T.tip, ["G", "A", "D"], 2);
bars(T.tip, T.end, ["G", "A", "D", "D"], 1);
panMel(MOTIF.slice(0, 3), T.ep - 2 * E8, 0.9); bar(T.end, "D", 0); bar(T.end + 4 * B, "D", 0);
steelpan(T.sting, 88, 1.2, 0); glock(T.sting, 100, 0.6);
// effects
HITS.land.forEach((t) => thunk(t)); HITS.closing.forEach((t) => thunk(t)); HITS.bolt.forEach((t) => chime(t)); chime(T.land2 + 0.02, 0.9);
HITS.question.forEach((t) => qmark(t)); HITS.snap.forEach((t) => magSnap(t)); HITS.ringOff.forEach((t) => metal(t)); click(T.nudge, 0.8, 1500);
reverb(0.76, 0.4, 0.2);
// half-beat stops: true silence
HITS.stop.forEach((t) => silence(t, t + E8));
writeWav("score.wav");
