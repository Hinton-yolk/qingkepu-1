#!/usr/bin/env node
// 出单帧：npm run still -- <帧号> [更多帧号…] [--guides] [--scale=0.5]
//   1380      Remotion 帧号（从 0 起，= 秒 × fps）
//   46s       全片时间（秒）
//   b1381     Blender 的全片帧号（从 1 起，= Remotion 帧号 + 1）
// 输出到 out/stills/t<秒>_f<Remotion 帧号>.png。多个帧号一次打包、一次出完。
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const TL = JSON.parse(
  fs.readFileSync(
    path.resolve(ROOT, "..", "timeline", "timeline.json"),
    "utf8",
  ),
);
const fps = TL.meta.fps;
const total = Math.round(TL.shots.at(-1).end * fps);

const args = process.argv.slice(2);
const flags = args.filter((a) => a.startsWith("--"));
const frames = args
  .filter((a) => !a.startsWith("--"))
  .map((a) => {
    if (/^b\d+$/i.test(a)) return parseInt(a.slice(1), 10) - 1;
    if (/^[\d.]+s$/i.test(a)) return Math.round(parseFloat(a) * fps);
    if (/^\d+$/.test(a)) return parseInt(a, 10);
    console.error(`看不懂的帧号：${a}（用 1380、46s 或 b1381）`);
    process.exit(1);
  });
if (frames.length === 0) {
  console.error(
    "用法：npm run still -- <帧号> [更多帧号…] [--guides] [--scale=0.5]",
  );
  process.exit(1);
}
for (const f of frames) {
  if (f < 0 || f >= total) {
    console.error(`帧号 ${f} 超出范围 0–${total - 1}`);
    process.exit(1);
  }
}

const guides = flags.includes("--guides");
const pass = flags.filter((f) => f !== "--guides");
const outDir = path.join(ROOT, "out", "stills");
const tmpDir = path.join(outDir, "_tmp");
fs.rmSync(tmpDir, { recursive: true, force: true });
fs.mkdirSync(tmpDir, { recursive: true });

const bin = path.join(
  ROOT,
  "node_modules",
  ".bin",
  process.platform === "win32" ? "remotion.cmd" : "remotion",
);
const r = spawnSync(
  bin,
  [
    "render",
    "src/index.ts",
    "Journey",
    tmpDir,
    `--frames=${frames.join(",")}`,
    "--image-format=png",
    "--sequence",
    `--props=${JSON.stringify({ showGuides: guides })}`,
    ...pass,
  ],
  { cwd: ROOT, stdio: "inherit" },
);
if (r.status !== 0) process.exit(r.status ?? 1);

// Remotion 的序列输出按帧号命名（位数随总帧数），按数值对回去
const produced = fs.readdirSync(tmpDir).filter((n) => n.endsWith(".png"));
for (const f of frames) {
  const src = produced.find((n) => parseInt(n.replace(/\D/g, ""), 10) === f);
  if (!src) {
    console.error(`没找到第 ${f} 帧的输出`);
    process.exit(1);
  }
  const name = `t${(f / fps).toFixed(2).padStart(6, "0")}_f${String(f).padStart(4, "0")}${guides ? "_guides" : ""}.png`;
  fs.renameSync(path.join(tmpDir, src), path.join(outDir, name));
  console.log("已出：", path.relative(ROOT, path.join(outDir, name)));
}
fs.rmSync(tmpDir, { recursive: true, force: true });
