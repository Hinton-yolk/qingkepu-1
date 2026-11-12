/**
 * Remotion 命令行配置（只对 `remotion studio / still / render` 生效）。
 * 浏览器：用机器上预装的 Chromium，不让 Remotion 自己下载。
 *   查找顺序：环境变量 REMOTION_CHROME → /opt/pw-browsers/chromium（本容器里是指向 chrome 的软链接，
 *   如果它是目录就在里面找名为 chrome 的可执行文件）→ /opt/pw-browsers/chromium-星号/chrome-linux64/chrome。
 *   都找不到时不设置（在别的机器上由 Remotion 按默认方式处理），并打印提示。
 */
import { Config } from "@remotion/cli/config";
import fs from "node:fs";
import path from "node:path";

const isFile = (p: string) => {
  try {
    return fs.statSync(p).isFile();
  } catch {
    return false;
  }
};

const findIn = (dir: string, depth: number): string | null => {
  if (depth < 0) return null;
  let names: string[] = [];
  try {
    names = fs.readdirSync(dir);
  } catch {
    return null;
  }
  if (names.includes("chrome") && isFile(path.join(dir, "chrome"))) {
    return path.join(dir, "chrome");
  }
  for (const n of names) {
    const sub = path.join(dir, n);
    try {
      if (fs.statSync(sub).isDirectory()) {
        const hit = findIn(sub, depth - 1);
        if (hit) return hit;
      }
    } catch {
      // 读不了的目录跳过
    }
  }
  return null;
};

const findChrome = (): string | null => {
  const env = process.env.REMOTION_CHROME;
  if (env && isFile(env)) return env;
  const base = "/opt/pw-browsers/chromium";
  if (isFile(base)) return fs.realpathSync(base);
  const inBase = findIn(base, 3);
  if (inBase) return inBase;
  try {
    for (const n of fs.readdirSync("/opt/pw-browsers").sort().reverse()) {
      if (/^chromium-\d+$/.test(n)) {
        const hit = findIn(path.join("/opt/pw-browsers", n), 2);
        if (hit) return hit;
      }
    }
  } catch {
    // 没有这个目录
  }
  return null;
};

const chrome = findChrome();
if (chrome) {
  Config.setBrowserExecutable(chrome);
  // 预装的是完整版 Chrome（不是 headless-shell），要用新版无头模式
  Config.setChromeMode("chrome-for-testing");
} else {
  console.warn(
    "[remotion.config] 没找到预装的 Chromium；可用环境变量 REMOTION_CHROME 指定 chrome 可执行文件。",
  );
}

Config.setEntryPoint("./src/index.ts");
Config.setRspack(true);
Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);
Config.setDefaultPremountInSeconds(1);
