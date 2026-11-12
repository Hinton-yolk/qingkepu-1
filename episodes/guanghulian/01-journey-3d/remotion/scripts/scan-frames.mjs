#!/usr/bin/env node
// 构建前扫描：public/frames 里有哪些 Blender 帧、有哪些锚点文件，写成 src/generated/manifest.json。
// 渲染时不做文件系统探测，只读这份清单。npm run studio / still / draft / render / typecheck 之前会自动运行。
//
// 约定：
//   图像序列  public/frames/<镜头号>/<镜头号>_<全片帧号 6 位>.png      （也认 .jpg / .jpeg / .webp）
//   锚点      public/anchors/anchors_<镜头号>.json   或   public/frames/<镜头号>/anchors_<镜头号>.json
//   全片帧号 = round(秒 × fps) + 1（和 blender/common.py 的 F() 一致）
//   音频（可选）  public/audio/narration.* 或 public/audio/<旁白 id>.*，以及 public/audio/music.*
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "..");
const TL = JSON.parse(
  fs.readFileSync(
    path.resolve(ROOT, "..", "timeline", "timeline.json"),
    "utf8",
  ),
);
const fps = TL.meta.fps;
const FRAMES_DIR = path.join(ROOT, "public", "frames");
const ANCHORS_DIR = path.join(ROOT, "public", "anchors");
const OUT = path.join(ROOT, "src", "generated", "manifest.json");

const AUDIO_DIR = path.join(ROOT, "public", "audio");

const manifest = {
  generatedFrom: TL.meta.version,
  frames: {},
  anchors: {},
  audio: { narration: null, music: null, lines: {} },
};
const report = [];

for (const shot of TL.shots) {
  const id = shot.id;
  const f0 = Math.round(shot.start * fps) + 1;
  const f1 = Math.round(shot.end * fps);
  const dir = path.join(FRAMES_DIR, id);
  const byExt = {};
  if (fs.existsSync(dir)) {
    const re = new RegExp(`^${id}_(\\d{6})\\.(png|jpg|jpeg|webp)$`, "i");
    for (const name of fs.readdirSync(dir)) {
      const m = re.exec(name);
      if (!m) continue;
      (byExt[m[2]] ??= []).push(parseInt(m[1], 10));
    }
  }
  const exts = Object.keys(byExt).sort(
    (a, b) => byExt[b].length - byExt[a].length,
  );
  if (exts.length > 0) {
    const ext = exts[0];
    const all = byExt[ext].sort((a, b) => a - b);
    const inside = all.filter((f) => f >= f0 && f <= f1);
    if (exts.length > 1) {
      console.warn(
        `提示：${id} 有多种图像格式（${exts.join("、")}），只用数量最多的 .${ext}`,
      );
    }
    if (inside.length !== all.length) {
      console.warn(
        `提示：${id} 有 ${all.length - inside.length} 帧不在镜头范围 ${f0}–${f1} 内，已忽略`,
      );
    }
    if (inside.length > 0) manifest.frames[id] = { ext, frames: inside };
    report.push(`${id}  ${inside.length}/${f1 - f0 + 1} 帧`);
  } else {
    report.push(
      `${id}  ${shot.blender ? "无帧 → 占位卡" : "无 Blender 画面（纯 Remotion）"}`,
    );
  }

  for (const p of [
    path.join(ANCHORS_DIR, `anchors_${id}.json`),
    path.join(dir, `anchors_${id}.json`),
  ]) {
    if (!fs.existsSync(p)) continue;
    try {
      const a = JSON.parse(fs.readFileSync(p, "utf8"));
      if (!a.frames || typeof a.frames !== "object")
        throw new Error("缺 frames");
      manifest.anchors[id] = {
        width: a.width ?? TL.meta.width,
        height: a.height ?? TL.meta.height,
        step: a.step ?? 1,
        frames: a.frames,
      };
      const keys = new Set();
      for (const row of Object.values(a.frames))
        for (const k of Object.keys(row)) keys.add(k);
      report[report.length - 1] += `；锚点 ${[...keys].join("、")}`;
      break;
    } catch (e) {
      console.warn(`提示：锚点文件读不了，已跳过：${p}（${e.message}）`);
    }
  }
}

// 音频（可选）：public/audio/narration.*（整条旁白，从 0 秒起）或 public/audio/<旁白 id>.*（逐句，按 narration[].start 摆放）；
// public/audio/music.*（音乐，从 0 秒起）。认 wav / mp3 / m4a / aac / ogg。
if (fs.existsSync(AUDIO_DIR)) {
  const files = fs
    .readdirSync(AUDIO_DIR)
    .filter((n) => /\.(wav|mp3|m4a|aac|ogg)$/i.test(n));
  const find = (stem) => files.find((n) => n.replace(/\.[^.]+$/, "") === stem);
  const full = find("narration");
  const music = find("music");
  if (full) manifest.audio.narration = `audio/${full}`;
  if (music) manifest.audio.music = `audio/${music}`;
  for (const n of TL.narration) {
    const f = find(n.id);
    if (f) manifest.audio.lines[n.id] = `audio/${f}`;
  }
  const nLines = Object.keys(manifest.audio.lines).length;
  report.push(
    `音频  旁白：${full ? "整条 " + full : nLines > 0 ? `逐句 ${nLines}/${TL.narration.length}` : "无"}；音乐：${music ?? "无"}`,
  );
} else {
  report.push("音频  无（没有 public/audio 目录）");
}

fs.mkdirSync(path.dirname(OUT), { recursive: true });
fs.writeFileSync(OUT, JSON.stringify(manifest));
console.log(
  `[scan-frames] 时间轴 ${TL.meta.version}，${Math.round(TL.shots.at(-1).end * fps)} 帧`,
);
for (const line of report) console.log("  " + line);
console.log(`[scan-frames] 已写 ${path.relative(ROOT, OUT)}`);
