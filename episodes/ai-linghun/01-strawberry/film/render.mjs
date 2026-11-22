// render.mjs — EP.01 film (three.js draft). Serves ../ over http (ES modules + importmap need http, not file://),
// drives index.html's window.seek(t) in headless Chromium (WebGL via SwiftShader), frame by frame.
//   node render.mjs                          all frames -> out/frames, then encode
//   node render.mjs --stills=0,1,6.9 [--out=qa/stills]
//   node render.mjs --sheet [--every=0.5] [--tag=r1]
//   node render.mjs --strip=11.3,12.3 [--n=12]
//   node render.mjs --cues                    sound cues -> ../music/cues.json
//   node render.mjs --export-stills=0.6,6.7   Blender test stills: blender/stills/<frame>/{scene.glb,anim.json}
//   node render.mjs --export-seg=0,8,screen  Blender hybrid segment: blender/seg/<f0>_<f1>/ (every moving object, per frame)
//   node render.mjs --start=42 --end=48.2 --noencode   re-render a range in place;  node render.mjs --encode --out=…   encode only
import { createRequire } from "node:module";
import { execFileSync } from "node:child_process";
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url)), ROOT = path.dirname(HERE);
const { chromium } = createRequire(import.meta.url)("playwright");
const arg = (k, d) => { const a = process.argv.find((x) => x === `--${k}` || x.startsWith(`--${k}=`)); if (!a) return d; return a.includes("=") ? a.split("=").slice(1).join("=") : true; };
const TL = createRequire(import.meta.url)("../timeline.js");
const FPS = TL.FPS, DUR = parseFloat(arg("end", String(TL.DUR))), T0 = parseFloat(arg("start", "0")), NF = Math.round(FPS * DUR);
const QS0 = arg("overlay") ? "?overlay=1" : arg("bg") ? `?bg=${arg("bg")}` : arg("nocap") ? "?nocap=1" : "";
const QS = arg("qs") ? (QS0 ? QS0 + "&" : "?") + arg("qs") : QS0;   // --qs=cs=B : extra page parameters   // --nocap: cover art (no captions)
const WORKERS = parseInt(arg("workers", "4"));

const TYPES = { ".html": "text/html", ".js": "text/javascript", ".mjs": "text/javascript", ".woff": "font/woff", ".png": "image/png", ".json": "application/json" };
function serve() {
  return new Promise((res) => {
    const srv = http.createServer((q, s) => {
      const f = path.join(ROOT, decodeURIComponent(q.url.split("?")[0]));
      if (!f.startsWith(ROOT) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { s.writeHead(404); s.end(); return; }
      s.writeHead(200, { "content-type": TYPES[path.extname(f)] || "application/octet-stream" }); fs.createReadStream(f).pipe(s);
    }).listen(0, "127.0.0.1", () => res(srv));
  });
}
async function openPage(browser, port) {
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  const errs = [];
  page.on("pageerror", (e) => errs.push(String(e)));
  page.on("console", (m) => { if (m.type() === "error") errs.push(m.text()); });
  await page.goto(`http://127.0.0.1:${port}/film/index.html${QS}`);
  await page.waitForFunction(() => window.ready === true, null, { timeout: 60000 });
  if (errs.length) throw new Error("page errors:\n" + errs.join("\n"));
  page._errs = errs;
  return page;
}
async function shot(page, t, file) {
  await page.evaluate((tt) => window.seek(tt), t);
  if (page._errs.length) throw new Error(`error at t=${t}: ` + page._errs.join("\n"));
  await page.locator("#c").screenshot({ path: file, type: "png", omitBackground: !!arg("overlay") });   // --overlay: labels + captions on transparent
}
async function renderTimes(list, workers = WORKERS) {
  const srv = await serve(), port = srv.address().port;
  const browser = await chromium.launch(launchOpts());
  const pages = await Promise.all(Array.from({ length: Math.min(workers, list.length) }, () => openPage(browser, port)));
  if (arg("gpuinfo")) console.log("GPU:", await pages[0].evaluate(() => { const g = document.createElement("canvas").getContext("webgl2"), x = g && g.getExtension("WEBGL_debug_renderer_info"); return g ? (x ? g.getParameter(x.UNMASKED_RENDERER_WEBGL) : g.getParameter(g.RENDERER)) : "no webgl2"; }));
  let next = 0, done = 0; const t0 = Date.now();
  await Promise.all(pages.map(async (p) => {
    while (next < list.length) {
      const job = list[next++];
      await shot(p, job.t, job.file);
      if (++done % 60 === 0) process.stdout.write(`  ${done}/${list.length} frames, ${((Date.now() - t0) / done).toFixed(0)} ms/frame\n`);
    }
  }));
  await browser.close(); srv.close();
  return (Date.now() - t0) / 1000;
}
// on a GPU machine (tools/runpod_chromium.py) the WebGL backend comes from the environment: CHROME_ARGS (JSON array of flags), CHROME_CHANNEL
function launchOpts() {
  const o = { args: ["--disable-gpu-vsync", "--font-render-hinting=none", "--ignore-gpu-blocklist", ...JSON.parse(process.env.CHROME_ARGS || "[]")] };
  if (process.env.CHROME_CHANNEL) o.channel = process.env.CHROME_CHANNEL;
  return o;
}
const ff = (args) => execFileSync("ffmpeg", ["-v", "error", "-y", ...args], { stdio: "inherit" });

async function main() {
  fs.mkdirSync(path.join(HERE, "qa"), { recursive: true });
  if (arg("export-seg")) {   // --export-seg=a,b[,screen] : frames [a·30, b·30) for the Blender hybrid -> blender/seg/<f0>_<f1>/{scene.glb, anim.json, screen/}
    const [ta, tb, scr] = String(arg("export-seg")).split(","), fa = Math.round(+ta * FPS), fb = Math.round(+tb * FPS);
    const dir = path.join(HERE, "blender/seg", `${String(fa).padStart(5, "0")}_${String(fb).padStart(5, "0")}`); fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true });
    const srv = await serve(), port = srv.address().port;
    const browser = await chromium.launch(launchOpts()); const page = await openPage(browser, port);
    const b64 = await page.evaluate((t) => window.exportSegGLB(t), fa / FPS); fs.writeFileSync(path.join(dir, "scene.glb"), Buffer.from(b64, "base64"));
    const frames = [];
    for (let f = fa; f < fb; f++) {
      const fr = await page.evaluate(([t, ws]) => window.exportFrameAll(t, ws), [f / FPS, scr === "screen"]);
      if (fr.screen) { fs.mkdirSync(path.join(dir, "screen"), { recursive: true }); fs.writeFileSync(path.join(dir, "screen", `screen_${String(f).padStart(5, "0")}.png`), Buffer.from(fr.screen.split(",")[1], "base64")); delete fr.screen; }
      frames.push(fr);
    }
    const J = (v) => JSON.stringify(v), f0 = frames[0];
    const dyn = Object.keys(f0.all).filter((n) => frames.some((fr) => J(fr.all[n]) !== J(f0.all[n])));
    const dynM = Object.keys(f0.mats).filter((n) => frames.some((fr) => J(fr.mats[n]) !== J(f0.mats[n])));
    const stat = Object.fromEntries(Object.entries(f0.all).map(([n, v]) => [n, v[0]]));
    for (const fr of frames) { fr.nodes = Object.fromEntries(dyn.map((n) => [n, fr.all[n]])); fr.mats = Object.fromEntries(dynM.map((n) => [n, fr.mats[n]])); delete fr.all; }
    fs.writeFileSync(path.join(dir, "anim.json"), JSON.stringify({ fps: FPS, f0: fa, f1: fb - 1, W: 1080, H: 1920, static: stat, frames }));
    console.log(`segment ${fa}–${fb - 1}: ${Object.keys(stat).length} meshes, ${dyn.length} moving, ${dynM.length} recoloured; scene.glb ${(fs.statSync(path.join(dir, "scene.glb")).size / 1e6).toFixed(1)} MB, anim.json ${(fs.statSync(path.join(dir, "anim.json")).size / 1e6).toFixed(1)} MB`);
    await browser.close(); srv.close(); return;
  }
  if (arg("export-stills")) {   // --export-stills=0.6,6.7,… : blender/stills/<frame>/scene.glb (only what is visible at t, colours as at t) + anim.json (that frame)
    const srv = await serve(), port = srv.address().port;
    const browser = await chromium.launch(launchOpts()); const page = await openPage(browser, port);
    for (const t of String(arg("export-stills")).split(",").map(Number)) {
      const f = Math.round(t * FPS), dir = path.join(HERE, "blender/stills", String(f).padStart(5, "0")); fs.mkdirSync(dir, { recursive: true });
      const b64 = await page.evaluate(([tt]) => window.exportGLB(tt, true), [f / FPS]); fs.writeFileSync(path.join(dir, "scene.glb"), Buffer.from(b64, "base64"));
      const fr = await page.evaluate((tt) => window.exportFrame(tt), f / FPS);
      fs.writeFileSync(path.join(dir, "anim.json"), JSON.stringify({ fps: FPS, f0: f, f1: f, W: 1080, H: 1920, frames: [fr] }));
      console.log(`still ${f} (${(f / FPS).toFixed(2)} s): scene.glb ${(fs.statSync(path.join(dir, "scene.glb")).size / 1e6).toFixed(1)} MB`);
    }
    await browser.close(); srv.close(); return;
  }
  if (arg("export")) {     // --export --start=18.4 --end=22.4 : blender/scene.glb (state at --start) + blender/anim.json (every frame)
    const srv = await serve(), port = srv.address().port;
    const browser = await chromium.launch({ args: ["--ignore-gpu-blocklist"] }); const page = await openPage(browser, port);
    const dir = path.join(HERE, "blender"); fs.mkdirSync(dir, { recursive: true });
    const b64 = await page.evaluate((t) => window.exportGLB(t), T0); fs.writeFileSync(path.join(dir, "scene.glb"), Buffer.from(b64, "base64"));
    const f0 = Math.round(T0 * FPS), f1 = Math.round(DUR * FPS), frames = [];
    for (let f = f0; f <= f1; f++) frames.push(await page.evaluate((t) => window.exportFrame(t), f / FPS));
    fs.writeFileSync(path.join(dir, "anim.json"), JSON.stringify({ fps: FPS, f0, f1, W: 1080, H: 1920, frames }));
    console.log(`export: scene.glb ${(fs.statSync(path.join(dir, "scene.glb")).size / 1e6).toFixed(1)} MB, frames ${f0}–${f1}`);
    await browser.close(); srv.close(); return;
  }
  if (arg("cues")) {      // --cues : the page's sound cues (window.CUES) -> ../music/cues.json, for music/sfx.py
    const srv = await serve(), port = srv.address().port;
    const browser = await chromium.launch(launchOpts()); const page = await openPage(browser, port);
    const c = await page.evaluate(() => window.CUES.slice().sort((p, q) => p.t - q.t));
    fs.mkdirSync(path.join(ROOT, "music"), { recursive: true }); fs.writeFileSync(path.join(ROOT, "music/cues.json"), JSON.stringify({ dur: TL.DUR, end_card: TL.END_CARD, cues: c }, null, 1));
    console.log(`cues: ${c.length} -> music/cues.json`); await browser.close(); srv.close(); return;
  }
  if (arg("stills")) {
    const out = path.join(HERE, arg("out", "qa/stills")); fs.mkdirSync(out, { recursive: true });
    const ts = String(arg("stills")).split(",").map(Number);
    await renderTimes(ts.map((t) => ({ t, file: path.join(out, `t${t.toFixed(2)}.png`) })));
    console.log("stills ->", out); return;
  }
  if (arg("sheet")) {
    const every = parseFloat(arg("every", "0.5")), tag = arg("tag", "r");
    const dir = path.join(HERE, "qa/sheet-" + tag); fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true });
    const ts = []; for (let i = 0; i * every < DUR - 1e-9; i++) ts.push(+(i * every + parseFloat(arg("offset", "0"))).toFixed(3));
    const sec = await renderTimes(ts.map((t, i) => ({ t, file: path.join(dir, String(i).padStart(3, "0") + ".png") })));
    const cols = parseInt(arg("cols", "8")), rows = Math.ceil(ts.length / cols);
    ff(["-framerate", "1", "-i", path.join(dir, "%03d.png"), "-vf", `scale=270:480,tile=${cols}x${rows}:padding=6:color=white`, "-frames:v", "1", "-q:v", "3", path.join(HERE, `qa/sheet-${tag}.jpg`)]);
    console.log(`sheet: ${ts.length} frames in ${sec.toFixed(1)} s -> qa/sheet-${tag}.jpg`); return;
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
  const frames = path.join(HERE, arg("frames", "out/frames"));
  if (!arg("encode")) {
    if (!arg("resume") && !T0) fs.rmSync(frames, { recursive: true, force: true }); fs.mkdirSync(frames, { recursive: true });
    // --resume: keep frames already rendered (a frame file is written whole by the screenshot, so a present file is complete)
    const list = Array.from({ length: NF }, (_, i) => ({ t: i / FPS, file: path.join(frames, String(i).padStart(5, "0") + ".png") })).filter((f) => f.t >= T0 - 1e-9).filter((f) => !arg("resume") || !fs.existsSync(f.file) || fs.statSync(f.file).size < 1000);
    const sec = await renderTimes(list);
    console.log(`rendered ${list.length} frames in ${sec.toFixed(1)} s`);
    if (arg("noencode")) return;   // patch a range of out/frames, encode later with --encode
  }
  const audio = path.join(HERE, arg("audio", "audio/mix.wav"));
  const out = path.join(HERE, arg("out", "out/ai01-strawberry-film.mp4"));
  const args = ["-framerate", String(FPS), "-i", path.join(frames, "%05d.png")];
  if (fs.existsSync(audio)) args.push("-i", audio);
  args.push("-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p", "-profile:v", "high", "-r", String(FPS), "-movflags", "+faststart");
  if (fs.existsSync(audio)) args.push("-c:a", "aac", "-aac_coder", "fast", "-b:a", "256k", "-ar", "48000", "-shortest");   // fast: the default twoloop coder overshot to +1.5 dBTP on the ACE-Step music
  args.push(out);
  ff(args);
  console.log("encoded ->", out, `(${DUR} s)`);
}
main().catch((e) => { console.error(e); process.exit(1); });
