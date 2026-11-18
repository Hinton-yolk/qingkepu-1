// render.mjs — drives index.html's window.seek(t) in headless Chromium, frame by frame.
//   node render.mjs                          all frames -> out/frames, then encode (H.264 yuv420p CRF 16) with audio/mix.wav
//   node render.mjs --stills=0,1,6.9 [--out=qa/stills]   full-res PNG stills
//   node render.mjs --sheet [--every=0.5] [--tag=r1]     one frame per beat -> qa/sheet-<tag>.jpg + phone-width sheet
//   node render.mjs --strip=11.3,12.3 [--n=12]           a strip of consecutive frames around a cut
//   node render.mjs --encode                             encode existing frames only
//   node render.mjs --from=57.4                          re-render the frames from 57.4 s on into out/frames, then encode
import { createRequire } from "node:module";
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const { chromium } = createRequire(import.meta.url)("playwright");   // resolved via NODE_PATH (pre-installed)
const arg = (k, d) => { const a = process.argv.find((x) => x === `--${k}` || x.startsWith(`--${k}=`)); if (!a) return d; return a.includes("=") ? a.split("=").slice(1).join("=") : true; };
const URL_ = "file://" + path.join(HERE, "index.html");
const TLm = createRequire(import.meta.url)("./timeline.js");
const FPS = TLm.FPS, DUR = TLm.DUR, NF = Math.round(FPS * DUR);
const WORKERS = parseInt(arg("workers", "4"));

async function openPage(browser) {
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  const errs = [];
  page.on("pageerror", (e) => errs.push(String(e)));
  page.on("console", (m) => { if (m.type() === "error") errs.push(m.text()); });
  await page.goto(URL_);
  await page.waitForFunction(() => window.ready === true, null, { timeout: 30000 });
  if (errs.length) throw new Error("page errors:\n" + errs.join("\n"));
  page._errs = errs;
  return page;
}
async function shot(page, t, file) {
  await page.evaluate((tt) => window.seek(tt), t);
  if (page._errs.length) throw new Error(`error at t=${t}: ` + page._errs.join("\n"));
  await page.locator("#c").screenshot({ path: file, type: "png" });
}
async function renderTimes(list, workers = WORKERS) {      // list: [{t, file}]
  const browser = await chromium.launch({ args: ["--disable-gpu-vsync", "--font-render-hinting=none"] });
  const pages = await Promise.all(Array.from({ length: Math.min(workers, list.length) }, () => openPage(browser)));
  let next = 0, done = 0; const t0 = Date.now();
  await Promise.all(pages.map(async (p) => {
    while (next < list.length) {
      const job = list[next++];
      await shot(p, job.t, job.file);
      if (++done % 60 === 0) process.stdout.write(`  ${done}/${list.length} frames, ${((Date.now() - t0) / done).toFixed(0)} ms/frame\n`);
    }
  }));
  await browser.close();
  return (Date.now() - t0) / 1000;
}
const ff = (args) => execFileSync("ffmpeg", ["-v", "error", "-y", ...args], { stdio: "inherit" });

async function main() {
  if (arg("stills")) {
    const out = path.join(HERE, arg("out", "qa/stills")); fs.mkdirSync(out, { recursive: true });
    const ts = String(arg("stills")).split(",").map(Number);
    await renderTimes(ts.map((t) => ({ t, file: path.join(out, `t${t.toFixed(2)}.png`) })));
    console.log("stills ->", out); return;
  }
  if (arg("sheet")) {
    const every = parseFloat(arg("every", "0.5")), tag = arg("tag", "r");
    const dir = path.join(HERE, "qa/sheet-" + tag); fs.mkdirSync(dir, { recursive: true });
    const ts = []; for (let i = 0; i * every < DUR - 1e-9; i++) ts.push(+(i * every + (parseFloat(arg("offset", "0")))).toFixed(3));
    const sec = await renderTimes(ts.map((t, i) => ({ t, file: path.join(dir, String(i).padStart(3, "0") + ".png") })));
    const cols = parseInt(arg("cols", "12")), rows = Math.ceil(ts.length / cols);
    // label each cell with its time (drawtext may be missing: use a tiny overlay via ffmpeg's built-in font if available)
    ff(["-framerate", "1", "-i", path.join(dir, "%03d.png"), "-vf", `scale=270:480,tile=${cols}x${rows}:padding=6:color=white`, "-frames:v", "1", "-q:v", "3", path.join(HERE, `qa/sheet-${tag}.jpg`)]);
    ff(["-framerate", "1", "-i", path.join(dir, "%03d.png"), "-vf", `scale=360:640,tile=${cols}x${rows}:padding=4:color=white`, "-frames:v", "1", "-q:v", "4", path.join(HERE, `qa/phone-${tag}.jpg`)]);
    console.log(`sheet: ${ts.length} frames in ${sec.toFixed(1)} s -> qa/sheet-${tag}.jpg, qa/phone-${tag}.jpg`); return;
  }
  if (arg("strip")) {
    const [a, b] = String(arg("strip")).split(",").map(Number), n = parseInt(arg("n", "12"));
    const dir = path.join(HERE, "qa/strip"); fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true });
    const ts = Array.from({ length: n }, (_, i) => a + (b - a) * (i / (n - 1)));
    await renderTimes(ts.map((t, i) => ({ t, file: path.join(dir, String(i).padStart(3, "0") + ".png") })));
    const name = arg("name", `strip-${a}-${b}`);
    ff(["-framerate", "1", "-i", path.join(dir, "%03d.png"), "-vf", `scale=240:427,tile=${Math.min(n, 12)}x${Math.ceil(n / 12)}:padding=4:color=white`, "-frames:v", "1", "-q:v", "3", path.join(HERE, `qa/${name}.jpg`)]);
    console.log("strip ->", `qa/${name}.jpg`); return;
  }
  const frames = path.join(HERE, "out/frames");
  if (!arg("encode")) {
    const from = parseFloat(arg("from", "0"));                       // --from=57.4: re-render only the frames from there on
    if (!from) fs.rmSync(frames, { recursive: true, force: true });
    fs.mkdirSync(frames, { recursive: true });
    const list = Array.from({ length: NF }, (_, i) => ({ t: i / FPS, file: path.join(frames, String(i).padStart(5, "0") + ".png") })).filter((f) => f.t >= from - 1e-9);
    const sec = await renderTimes(list);
    console.log(`rendered ${NF} frames in ${sec.toFixed(1)} s`);
  }
  const audio = path.join(HERE, arg("audio", "audio/mix.wav"));
  const out = path.join(HERE, arg("out", "out/ep09-xueyaji.mp4"));
  const args = ["-framerate", String(FPS), "-i", path.join(frames, "%05d.png")];
  if (fs.existsSync(audio)) args.push("-i", audio);
  args.push("-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p", "-profile:v", "high", "-r", String(FPS), "-movflags", "+faststart");
  if (fs.existsSync(audio)) args.push("-c:a", "aac", "-aac_coder", "fast", "-b:a", "256k", "-ar", "48000", "-shortest");
  args.push(out);
  ff(args);
  console.log("encoded ->", out);
}
main().catch((e) => { console.error(e); process.exit(1); });
