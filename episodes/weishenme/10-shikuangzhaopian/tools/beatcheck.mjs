// beats.json: the measured beat grid of audio/mix.wav (hyperframes beats) + every picture hit checked against it.
import { createRequire } from "node:module"; import fs from "node:fs";
const require = createRequire(import.meta.url); const TL = require("../timeline.js");
const m = JSON.parse(fs.readFileSync("qa/hf-beats.json", "utf8"));
const beats = m.beatTimes;
// Robust grid: start from the score's tempo, keep the measured beats within ±30 ms of it (a sparse section can make the
// detector slip onto off-beats), then least-squares fit period + offset on those inliers.
let period = 60 / TL.BPM, offset = 0;
const resid = (b) => b - offset - Math.round((b - offset) / period) * period;
{ const r0 = beats.map((b) => b - Math.round(b / period) * period).sort((x, y) => x - y); offset = r0[Math.floor(r0.length / 2)]; }
let inl = beats;
for (let it = 0; it < 3; it++) {
  inl = beats.filter((b) => Math.abs(resid(b)) < 0.03);
  const n = inl.map((b) => Math.round((b - offset) / period)), N = n.length, sx = n.reduce((a, x) => a + x, 0), sy = inl.reduce((a, x) => a + x, 0);
  const sxx = n.reduce((a, x) => a + x * x, 0), sxy = n.reduce((a, x, i) => a + x * inl[i], 0);
  period = (N * sxy - sx * sy) / (N * sxx - sx * sx); offset = (sy - period * sx) / N; offset -= Math.floor(offset / period) * period;
}
const bpm = +(60 / period).toFixed(3), inlierShare = +(inl.length / beats.length).toFixed(3);
const grid16 = (t) => Math.round((t - offset) / (period / 4)) * (period / 4) + offset;
const hits = [];
for (const [name, list] of Object.entries(TL.HITS)) for (const h of list) { const t = Array.isArray(h) ? h[0] : h; const g = grid16(t); hits.push({ name, t, nearest16th: +g.toFixed(3), errMs: +((t - g) * 1000).toFixed(1), frames: +(((t - g) * 30)).toFixed(2) }); }
const worst = hits.reduce((a, h) => Math.max(a, Math.abs(h.frames)), 0);
fs.writeFileSync("beats.json", JSON.stringify({ source: m.file, measuredBy: "npx hyperframes beats", detectorBpm: m.bpm, bpm, period, inlierShare, offsetSec: +offset.toFixed(4), beats, hits, worstHitErrorFrames: worst }, null, 1));
console.log(`detector ${m.bpm} BPM; fitted ${bpm} BPM on ${inl.length}/${beats.length} beats; grid offset ${(offset * 1000).toFixed(1)} ms, worst hit error ${worst} frames`);
hits.filter((h) => Math.abs(h.frames) > 0.5).forEach((h) => console.log("  off-grid:", h.name, h.t, "->", h.nearest16th));
