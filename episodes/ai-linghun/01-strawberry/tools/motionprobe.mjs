// motionprobe.mjs — quick motion estimate without a full render: renders frame pairs (t, t+1/30) at sample times and
// prints the same metric as tools/motion_check.py (mean abs grey difference on a 135x240 copy; still if < 0.15).
//   node tools/motionprobe.mjs [--every=0.5] [--from=0] [--to=DUR]
import { createRequire } from "node:module"; import path from "node:path"; import { fileURLToPath } from "node:url";
const HERE = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const { chromium } = createRequire(import.meta.url)("playwright");
const TL = createRequire(import.meta.url)(path.join(HERE, "timeline.js"));
const arg = (k, d) => { const a = process.argv.find((x) => x.startsWith(`--${k}=`)); return a ? parseFloat(a.split("=")[1]) : d; };
const every = arg("every", 0.5), from = arg("from", 0), to = arg("to", TL.END_CARD);
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
await p.goto("file://" + path.join(HERE, "index.html")); await p.waitForFunction(() => window.ready === true);
const res = await p.evaluate(({ from, to, every }) => {
  const c = document.getElementById("c"), mk = (w, h) => { const e = document.createElement("canvas"); e.width = w; e.height = h; const g = e.getContext("2d", { willReadFrequently: true }); g.imageSmoothingQuality = "high"; return [e, g]; };
  const [s1, g1] = mk(540, 960), [s2c, g2] = mk(270, 480), [s, x] = mk(135, 240);
  const grab = (t) => { window.seek(t); g1.drawImage(c, 0, 0, 540, 960); g2.drawImage(s1, 0, 0, 270, 480); x.drawImage(s2c, 0, 0, 135, 240); const d = x.getImageData(0, 0, 135, 240).data; const g = new Float32Array(135 * 240); for (let i = 0; i < g.length; i++) g[i] = 0.299 * d[4 * i] + 0.587 * d[4 * i + 1] + 0.114 * d[4 * i + 2]; return g; };
  const out = [];
  for (let t = from; t < to; t += every) { const A = grab(t), B = grab(t + 1 / 30); let s2 = 0; for (let i = 0; i < A.length; i++) s2 += Math.abs(Math.round(A[i]) - Math.round(B[i])); out.push([t, s2 / A.length]); }
  return out;
}, { from, to, every });
await b.close();
const still = res.filter((r) => r[1] < 0.15);
console.log(res.map(([t, d]) => `${t.toFixed(1)}:${d.toFixed(2)}${d < 0.15 ? "*" : ""}`).join("  "));
console.log(`samples ${res.length}, still ${(100 * still.length / res.length).toFixed(0)}% (need < 15%), median ${res.map((r) => r[1]).sort((a, b) => a - b)[res.length >> 1].toFixed(2)}`);
