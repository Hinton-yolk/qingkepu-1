// music/variants.mjs — three alternative full-length scores for EP.11, each with a real arc that follows the picture (user 11-28: 「结合视频再出几个不同的配乐，现在听起来有点平淡」).
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

// ---------------------------------------------------------------- extra instruments
function crash(t, v = 1) { let hp = 0, pv = 0; put(t, 2.2, (tt) => { const n = rnd() * 2 - 1; hp = 0.92 * (hp + n - pv); pv = n; return v * 0.14 * hp * Math.exp(-tt * 1.8) * att(tt, 0.002); }, { pan: 0.15, rev: 0.4 }); }
function riser(t0, t1, v = 1) { let lp = 0; const d = t1 - t0; put(t0, d, (tt) => { const u = tt / d, n = rnd() * 2 - 1; lp += (0.02 + 0.5 * u * u) * (n - lp); return v * 0.16 * lp * u * u; }, { rev: 0.5 }); put(t0, d, (tt) => { const u = tt / d; return v * 0.05 * Math.sin(TAU * (200 * tt + 500 * tt * u)) * u * u; }, { rev: 0.4 }); }
function drone(t0, t1, m, v = 1) { const f = mtof(m); put(t0, t1 - t0, (tt) => v * 0.08 * (Math.sin(TAU * f * tt) + 0.4 * Math.sin(TAU * 2.003 * f * tt)) * Math.min(1, tt / 0.6) * Math.min(1, (t1 - t0 - tt) / 0.4), { rev: 0.5 }); }
function timp(t, m, v = 1) { const f = mtof(m); put(t, 1.6, (tt) => v * 0.45 * Math.sin(TAU * f * tt * (1 + 0.08 * Math.exp(-tt * 12))) * Math.exp(-tt * 2.4) * att(tt, 0.003) + v * 0.08 * (rnd() * 2 - 1) * Math.exp(-tt * 40), { rev: 0.35 }); }
function pizz(t, m, v = 1, pan = 0) { uke(t, m, 0.9 * v, pan, 0.35); }
function logDrum(t, m, v = 1, pan = 0) { const f = mtof(m); put(t, 0.5, (tt) => v * 0.32 * Math.sin(TAU * f * tt * (1 + 0.25 * Math.exp(-tt * 30))) * Math.exp(-tt * 9) * att(tt, 0.002), { pan, rev: 0.15 }); }
function marimba(t, m, v = 1, pan = 0) { const f = mtof(m); put(t, 1.0, (tt) => v * 0.2 * (Math.sin(TAU * f * tt) + 0.35 * Math.sin(TAU * f * 4 * tt) * Math.exp(-tt * 28)) * Math.exp(-tt * 5.5) * att(tt, 0.0015), { pan, rev: 0.25 }); }
function tom(t, m, v = 1) { const f = mtof(m); put(t, 0.5, (tt) => v * 0.4 * Math.sin(TAU * f * tt * (1 + 0.5 * Math.exp(-tt * 20))) * Math.exp(-tt * 7) * att(tt, 0.002), { rev: 0.2 }); }
function strings(t, notes, len, v = 1, trem = 0) { notes.forEach((m, k) => { const f = mtof(m), ph = [rnd(), rnd(), rnd()];
  put(t, len + 0.8, (tt) => { let s = 0; [-0.07, 0, 0.07].forEach((d, j) => { s += Math.sin(TAU * (f * Math.pow(2, d / 12) * tt + ph[j])) + 0.35 * Math.sin(TAU * (2 * f * Math.pow(2, d / 12) * tt + ph[j])) + 0.15 * Math.sin(TAU * (3 * f * tt + ph[j])); });
    const tr = trem ? 0.65 + 0.35 * Math.sin(TAU * 7 * tt) : 1; return v * 0.02 * s * tr * Math.min(1, tt / 0.5) * rel(tt, len, 0.8); }, { pan: (k - (notes.length - 1) / 2) * 0.4, rev: 0.55 }); }); }
function tapeStop(t, v = 1) { put(t, 0.7, (tt) => v * 0.22 * Math.sin(TAU * (330 * tt - 220 * tt * tt)) * Math.max(0, 1 - tt / 0.7), { rev: 0.2 }); put(t, 0.5, (tt) => v * 0.3 * Math.sin(TAU * (60 * tt - 40 * tt * tt)) * Math.max(0, 1 - tt / 0.5), { rev: 0 }); }
function heartbeat(t, v = 1) { kick(t, 0.55 * v); kick(t + 0.22, 0.38 * v); }
function roll(t0, t1, hit, v0 = 0.3, v1 = 1) { const n = Math.round((t1 - t0) / (E8 / 2)); for (let i = 0; i < n; i++) hit(t0 + i * E8 / 2, lerp(v0, v1, i / n)); }
const lerp = (a, b, k) => a + (b - a) * k;
// ---------------------------------------------------------------- shared
const B = 60 / TL.BPM, S = B / 4;
const tr = (ch, k) => ch.map((m) => m + k);
const CH = { D: [62, 66, 69], G: [62, 67, 71], A: [61, 64, 69], Bm: [62, 66, 71], Em: [59, 64, 67], Fsm: [61, 66, 69], Gm: [62, 67, 70], E: [64, 68, 71], Asus: [62, 64, 69] };
const ROOT = { D: 38, G: 43, A: 45, Bm: 47, Em: 40, Fsm: 42, Gm: 43, E: 40, Asus: 45 };
const MOTIF = [[0, 81], [0.5, 86], [0.75, 90], [1.5, 88]], RESOLVE = [[0, 81], [0.5, 86], [0.75, 90], [1.25, 93]];
const MEL = [[0, 78], [0.75, 81], [1.5, 83], [2.5, 81], [4, 81], [4.75, 85], [5.5, 88], [6.5, 85], [8, 86], [8.75, 83], [9.5, 81], [10.5, 78], [12, 81], [12.75, 85], [13.5, 88], [14.5, 85]];
const each = (t0, t1, step, fn) => { let i = 0; for (let t = t0; t < t1 - 1e-6; t += step, i++) fn(t, i); };
const chordAt = (prog, t0, t) => prog[Math.floor((t - t0) / (4 * B)) % prog.length];
function sfx() {
  HITS.land.forEach((t) => thunk(t)); HITS.closing.forEach((t) => thunk(t)); HITS.bolt.forEach((t) => chime(t)); chime(T.land2 + 0.02, 0.9);
  HITS.question.forEach((t) => qmark(t)); HITS.snap.forEach((t) => magSnap(t)); HITS.ringOff.forEach((t) => metal(t)); click(T.nudge, 0.8, 1500);
  [T.magIn1 + 0.15, T.magOut1 + 0.15].forEach((t, i) => glock(t, i ? 90 : 93, 0.7, 0.25)); each(T.shake + E8, T.labOut, 2 * E8, (t, i) => glock(t, i % 2 ? 90 : 93, 0.55, 0.25));
}
function finish(name) { reverb(0.78, 0.4, 0.22); HITS.stop.forEach((t) => silence(t, t + E8)); writeWav(name); }

// ================================================================ A · 钢鼓 · 加强版 (same palette, a real arc, modulates up for the ending)
function varA() {
  reset(DUR + 1.2);
  const groove = (t0, t1, prog, lvl, k = 0) => each(t0, t1, 4 * B, (t, i) => { const c = tr(CH[prog[i % prog.length]], k), r = ROOT[prog[i % prog.length]] + k;
    [2, 6, 10, 14].forEach((j) => ukeStrum(t + j * S, c, 0.5 * (lvl ? 1 : 0.7), true));
    if (lvl >= 1) { popBass(t, r, 3 * S, 0.9); popBass(t + 3 * S, r + 7, 2 * S, 0.7); popBass(t + 8 * S, r + 12, 2 * S, 0.7); popBass(t + 11 * S, r + 10, S, 0.5); popBass(t + 12 * S, r + 7, 3 * S, 0.8); each(t, t + 4 * B, S, (u, j) => shaker(u, j % 2 ? 0.45 : 0.9)); }
    if (lvl >= 2) { [0, 6, 8, 11].forEach((j) => lofiKick(t + j * S, 0.65)); [4, 12].forEach((j) => snareBright(t + j * S, 0.6)); [3, 7, 10, 14, 15].forEach((j, n) => conga(t + j * S, n % 2 === 1, 0.75)); }
    if (lvl >= 3) each(t, t + 4 * B, S, (u, j) => softHat(u, j % 2 ? 0.6 : 1.2)); });
  const mel = (list, t0, v, k = 0) => list.forEach(([b, m]) => { steelpan(t0 + b * B, m + k, v); steelpan(t0 + b * B + 0.07, m + k, 0.28 * v, -0.3); });
  // hook: alone, light
  mel(MOTIF, 0, 1.1); groove(0, T.q1, ["D"], 0);
  // into the coils: bass in, a riser into the lab
  groove(T.q1, T.labIn, ["G", "A"], 1); riser(T.labIn - 1.6, T.labIn, 0.9); crash(T.labIn, 0.7);
  // the lab: half-time, a thump each time the magnet goes in or out
  each(T.labIn, T.backPad, 4 * B, (t) => { lofiKick(t, 0.8); clap(t + 2 * B, 0.6); });
  each(T.labIn, T.backPad, E8, (t, i) => { const c = CH[["Bm", "G", "A", "A"][Math.floor(i / 8) % 4]]; steelpan(t, c[i % 3] + 12, 0.3, ((i % 4) - 1.5) * 0.3); });
  [T.magIn1, T.magOut1].forEach((t) => { popBass(t, 35, 0.3, 1.1); tom(t, 45, 0.5); });
  // back on the pad: the full groove; a snare roll into the half-beat stop
  groove(T.backPad, T.name - E8, ["G", "A", "Bm", "A"], 2); mel(MEL, T.backPad + 4 * B, 0.6);
  roll(T.name - E8 - 4 * B, T.name - E8, (t, v) => snareBright(t, v), 0.15, 0.9); riser(T.name - E8 - 2 * B, T.name - E8, 0.7);
  // the reveal: crash, everything, hats doubled
  mel(RESOLVE, T.name, 1.25); slamHit(T.name); crash(T.name, 1); groove(T.name, T.q4, ["G", "A", "D", "D"], 3);
  // leakage: a minor turn, thinner
  groove(T.q4, T.magnet, ["Bm", "G", "Em", "Fsm"], 1); each(T.slide, T.slideEnd, E8, (t, i) => steelpan(t, 86 - i, 0.35, 0.3));
  // magnets: snap + crash, major again
  crash(T.snap, 0.8); timp(T.snap, 38, 0.7); groove(T.magnet, T.heatQ, ["G", "D"], 2);
  // heat: a heartbeat under a warm pad that swells into the thermal view
  each(T.heatQ, T.metal, 4 * B, (t) => { heartbeat(t); heartbeat(t + 2 * B, 0.8); }); pad(T.heatQ, [50, 57, 62, 66], T.metal - T.heatQ, 1.1);
  riser(T.thermal - 1.2, T.thermal, 0.6); each(T.thermal, T.metal, E8, (t, i) => steelpan(t, [74, 78, 81, 86][i % 4], 0.28, 0.2));
  // metal: suspense — low drone, ticking, whirling arps; a low hit when the field is blocked; the pad gives up: tape-stop
  drone(T.metal, T.stop + 0.4, 38, 1.2); each(T.metal, T.stop, E8, (t, i) => { rimClick(t, i % 2 ? 0.4 : 0.8); if (t > T.eddy) glock(t, [81, 85, 88, 85][i % 4], 0.25, ((i % 4) - 1.5) * 0.4); });
  timp(T.block, 35, 1); crash(T.block, 0.5); riser(T.metalHot - 1, T.metalHot, 0.5); tapeStop(T.stop, 1.1);
  // closing: up a whole step (E major), the full band; tip lighter; end card motif
  mel(RESOLVE, T.a14, 1.3, 2); slamHit(T.a14); crash(T.a14, 1); groove(T.a14, T.tip, ["G", "A", "D"], 3, 2);
  groove(T.tip, T.end, ["G", "A", "D", "D"], 1, 2); mel(MOTIF.slice(0, 3), T.ep - 2 * E8, 0.9, 2); groove(T.end, DUR, ["D"], 0, 2);
  steelpan(T.sting, 90, 1.2, 0); glock(T.sting, 102, 0.6);
  sfx(); finish("var-A.wav");
}
// ================================================================ B · 律动打击乐 (log drums, congas, marimba; stronger rhythm)
function varB() {
  reset(DUR + 1.2);
  const K = -2;   // C major colour (a tone down) for a warmer drum sound
  const perc = (t0, t1, lvl) => each(t0, t1, 4 * B, (t) => {
    [0, 3, 6, 10, 12].forEach((j, n) => conga(t + j * S, n % 2 === 1, 0.8)); each(t, t + 4 * B, S, (u, j) => shaker(u, j % 4 === 2 ? 1 : 0.5));
    if (lvl >= 1) { [0, 7, 10].forEach((j) => kick(t + j * S, 0.6)); [4, 12].forEach((j) => clap(t + j * S, 0.7)); }
    if (lvl >= 2) { [2, 5, 9, 14].forEach((j, n) => logDrum(t + j * S, [43, 47, 50, 45][n] + K, 0.8, n % 2 ? 0.3 : -0.3)); each(t, t + 4 * B, S, (u, j) => softHat(u, j % 2 ? 0.5 : 1)); } });
  const mar = (t0, t1, prog, v = 0.45) => each(t0, t1, S * 2, (t, i) => { const c = tr(CH[chordAt(prog, t0, t)], K); marimba(t, c[[0, 1, 2, 1, 2, 0, 1, 2][i % 8]] + 12, v * (i % 2 ? 0.7 : 1), ((i % 4) - 1.5) * 0.3); });
  const bass = (t0, t1, prog) => each(t0, t1, 4 * B, (t, i) => { const r = ROOT[prog[i % prog.length]] + K; logDrum(t, r, 1.1); logDrum(t + 1.5 * B, r + 7, 0.8); logDrum(t + 3 * B, r + 12, 0.7); });
  const lead = (list, t0, v = 0.8) => list.forEach(([b, m]) => whistle(t0 + b * B, m + K - 12, B * 0.7, v));
  lead(MOTIF, 0, 0.9); perc(0, T.q1, 0);
  perc(T.q1, T.labIn, 1); mar(T.q1, T.labIn, ["G", "A"]); riser(T.labIn - 1.4, T.labIn, 0.7);
  perc(T.labIn, T.backPad, 0); mar(T.labIn, T.backPad, ["Bm", "G", "A", "A"], 0.35); [T.magIn1, T.magOut1].forEach((t) => { logDrum(t, 31, 1.2); tom(t, 50, 0.6); });
  perc(T.backPad, T.name - E8, 2); mar(T.backPad, T.name - E8, ["G", "A", "Bm", "A"]); bass(T.backPad, T.name - E8, ["G", "A", "Bm", "A"]);
  roll(T.name - E8 - 2 * B, T.name - E8, (t, v) => tom(t, 45 + Math.round(v * 12), v), 0.3, 1);
  lead(RESOLVE, T.name, 1); timp(T.name, 38 + K, 1); crash(T.name, 0.9); perc(T.name, T.q4, 2); mar(T.name, T.q4, ["G", "A", "D", "D"], 0.55); bass(T.name, T.q4, ["G", "A", "D", "D"]);
  perc(T.q4, T.magnet, 1); mar(T.q4, T.magnet, ["Bm", "G", "Em", "Fsm"], 0.4); bass(T.q4, T.magnet, ["Bm", "G", "Em", "Fsm"]);
  timp(T.snap, 38 + K, 0.9); crash(T.snap, 0.6); perc(T.magnet, T.heatQ, 2); mar(T.magnet, T.heatQ, ["G", "D"], 0.5);
  // heat: toms build from sparse to a roll as the picture turns thermal
  each(T.heatQ, T.thermal, B, (t, i) => tom(t, 40 + (i % 4) * 3, 0.4 + i * 0.05)); roll(T.thermal - 2 * B, T.thermal, (t, v) => tom(t, 52, v), 0.3, 1); crash(T.thermal, 0.6);
  perc(T.thermal, T.metal, 1); mar(T.thermal, T.metal, ["Em", "A"], 0.45);
  // metal: a talking-drum wobble over a drone; block = big low drum; stop = everything drops out
  drone(T.metal, T.stop + 0.4, 36 + K, 1.2); each(T.metal, T.stop, 2 * E8, (t, i) => { logDrum(t, 45 + (i % 3) * 2 + K, 0.7, 0.3); shaker(t + E8, 0.7); });
  logDrum(T.block, 26, 1.4); timp(T.block, 33, 0.9); tapeStop(T.stop, 1);
  lead(RESOLVE, T.a14, 1.1); timp(T.a14, 38 + K, 1); crash(T.a14, 1); perc(T.a14, T.tip, 2); mar(T.a14, T.tip, ["G", "A", "D"], 0.6); bass(T.a14, T.tip, ["G", "A", "D"]);
  perc(T.tip, T.end, 1); mar(T.tip, T.end, ["G", "A", "D", "D"], 0.4); lead(MOTIF.slice(0, 3), T.ep - 2 * E8, 0.8); perc(T.end, DUR, 0);
  marimba(T.sting, 88 + K, 1.2, 0);
  sfx(); finish("var-B.wav");
}
// ================================================================ C · 轻电影感 (pizzicato strings, glockenspiel, string swells, timpani)
function varC() {
  reset(DUR + 1.2);
  const pz = (t0, t1, prog, v = 0.7, every = 1) => each(t0, t1, E8, (t, i) => { if (i % every) return; const c = CH[chordAt(prog, t0, t)]; pizz(t, c[[0, 2, 1, 2][i % 4]] - 12, v * (i % 2 ? 0.75 : 1), ((i % 2) - 0.5) * 0.5); if (i % 4 === 0) pizz(t, ROOT[chordAt(prog, t0, t)] + 12, 0.8 * v, 0); });
  const sw = (t0, t1, prog, v = 1, trem = 0) => each(t0, t1, 4 * B, (t, i) => strings(t, CH[prog[i % prog.length]].map((m) => m - 12), 4 * B, v, trem));
  const gl = (list, t0, v = 0.8, k = 0) => list.forEach(([b, m]) => glock(t0 + b * B, m + k, v, 0.1));
  gl(MOTIF, 0, 1); pz(0, T.q1, ["D"], 0.5, 2);
  pz(T.q1, T.labIn, ["G", "A"], 0.7); sw(T.q1, T.labIn, ["G", "A"], 0.6); riser(T.labIn - 1.5, T.labIn, 0.5); timp(T.labIn, 38, 0.7);
  pz(T.labIn, T.backPad, ["Bm", "G", "A", "A"], 0.55, 2); [T.magIn1, T.magOut1].forEach((t) => timp(t, 33, 0.8));
  pz(T.backPad, T.name - E8, ["G", "A", "Bm", "A"], 0.85); sw(T.backPad, T.name - E8, ["G", "A", "Bm", "A"], 0.9); gl(MEL, T.backPad + 4 * B, 0.55);
  roll(T.name - E8 - 4 * B, T.name - E8, (t, v) => timp(t, 38, v * 0.6), 0.1, 1);
  gl(RESOLVE, T.name, 1.2); timp(T.name, 26, 1.2); crash(T.name, 0.8); sw(T.name, T.q4, ["G", "A", "D", "D"], 1.4); pz(T.name, T.q4, ["G", "A", "D", "D"], 1);
  each(T.name, T.q4, 4 * B, (t) => { kick(t, 0.5); kick(t + 2 * B, 0.4); });
  pz(T.q4, T.magnet, ["Bm", "G", "Em", "Fsm"], 0.7); sw(T.q4, T.magnet, ["Bm", "G", "Em", "Fsm"], 0.8);
  timp(T.snap, 38, 1); crash(T.snap, 0.6); sw(T.magnet, T.heatQ, ["G", "D"], 1.1); pz(T.magnet, T.heatQ, ["G", "D"], 0.9);
  // heat: tremolo strings rising, heartbeat timpani, swell into the thermal view
  sw(T.heatQ, T.metal, ["Em", "A", "Bm", "A"], 1.2, 1); each(T.heatQ, T.metal, 2 * B, (t) => timp(t, 31, 0.5)); riser(T.thermal - 1.2, T.thermal, 0.5); crash(T.thermal, 0.5);
  // metal: suspense — low tremolo, sparse pizz; block = timpani; stop = cut
  drone(T.metal, T.stop + 0.4, 38, 1); sw(T.metal, T.stop, ["Bm", "Gm"], 0.9, 1); pz(T.metal, T.stop, ["Bm", "Gm"], 0.5, 2); each(T.eddy, T.stop, E8, (t, i) => glock(t, [81, 85, 88, 85][i % 4], 0.2, ((i % 4) - 1.5) * 0.4));
  timp(T.block, 26, 1.3); tapeStop(T.stop, 0.9);
  // closing: up a whole step, full strings + glock
  gl(RESOLVE, T.a14, 1.3, 2); timp(T.a14, 28, 1.2); crash(T.a14, 1); sw(T.a14, T.tip, ["G", "A", "D"].map((c) => c), 1.5); pz(T.a14, T.tip, ["G", "A", "D"], 1.1);
  each(T.a14, T.tip, 4 * B, (t) => { kick(t, 0.55); kick(t + 2 * B, 0.45); });
  pz(T.tip, T.end, ["G", "A", "D", "D"], 0.6, 2); sw(T.tip, T.end, ["G", "A", "D", "D"], 0.7); gl(MOTIF.slice(0, 3), T.ep - 2 * E8, 0.9);
  glock(T.sting, 93, 1.2); strings(T.sting, [50, 57, 62, 66], 1.2, 1);
  sfx(); finish("var-C.wav");
}
varA(); varB(); varC();
