// runpod_chromium_probe.mjs — runs ON the RunPod pod (tools/runpod_chromium.py puts it at /w/scene/_probe.mjs).
// Tries several ways of giving headless Chromium the GPU, renders the same 12 stills with each, and writes the fastest one
// that works to /w/chosen.env (CHROME_ARGS / CHROME_CHANNEL / WORKERS). Two stills of each are kept for a visual check.
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const FILM = process.argv[2] || "/w/scene/film";
const VK = ["--use-angle=vulkan", "--enable-features=Vulkan", "--disable-vulkan-surface", "--enable-gpu"];
const EGL = ["--use-gl=angle", "--use-angle=gl-egl", "--enable-gpu"];
const CFGS = [
  ["shell-swiftshader", "", []],
  ["shell-vulkan", "", VK],
  ["shell-gl-egl", "", EGL],
  ["full-vulkan", "chromium", VK],
  ["full-gl-egl", "chromium", EGL],
  ["shell-egl", "", ["--use-gl=egl", "--enable-gpu"]],
];
const STILLS = "5,10,20,30,40,50,60,70,80,85,88,90";
const res = [];
fs.mkdirSync("/w/out/probe", { recursive: true });
for (const [name, ch, args] of CFGS) {
  const env = { ...process.env, CHROME_ARGS: JSON.stringify(args), CHROME_CHANNEL: ch };
  const t0 = Date.now();
  const r = spawnSync("node", ["render.mjs", "--gpuinfo", `--stills=${STILLS}`, `--out=qa/probe-${name}`, "--workers=2"],
    { cwd: FILM, env, timeout: 240000, encoding: "utf8" });
  const sec = (Date.now() - t0) / 1000, ok = r.status === 0;
  const gpu = ((r.stdout || "").match(/GPU: (.*)/) || [])[1] || "?";
  res.push({ name, ch, args, ok, sec, gpu, err: ok ? "" : String(r.stderr || r.error || "").slice(-600) });
  console.log(`probe ${name}: ${ok ? "ok" : "FAILED"} ${sec.toFixed(1)} s  ${gpu}`);
  if (ok) for (const t of ["10.00", "80.00"]) {
    const f = path.join(FILM, `qa/probe-${name}/t${t}.png`), tmp = `/w/probe_${name}_t${t}.png`;
    if (fs.existsSync(f)) { fs.copyFileSync(f, tmp); fs.renameSync(tmp, `/w/out/probe/${name}-t${t}.png`); }
  }
}
const best = res.filter((r) => r.ok).sort((a, b) => a.sec - b.sec)[0];
fs.writeFileSync("/w/out/probe.json", JSON.stringify({ cpus: os.cpus().length, best: best && best.name, res }, null, 1));
if (!best) { console.log("no working config"); process.exit(1); }
const workers = Math.max(4, Math.min(12, os.cpus().length));
fs.writeFileSync("/w/chosen.env", `export CHROME_ARGS='${JSON.stringify(best.args)}' CHROME_CHANNEL='${best.ch}' WORKERS=${workers}\n`);
console.log(`chosen: ${best.name} (${best.gpu}), ${workers} workers`);
