// Render the profile background at each platform size.
// usage: node render.mjs            -> exports/*.png (1x and @2x)
//        node render.mjs --preview  -> exports/preview-*.png (1x only)
import { createRequire } from "node:module";
import path from "node:path";
import fs from "node:fs";
import { fileURLToPath } from "node:url";

const { chromium } = createRequire(import.meta.url)("playwright");
const here = path.dirname(fileURLToPath(import.meta.url));
const outDir = path.join(here, "exports");
fs.mkdirSync(outDir, { recursive: true });

const SIZES = [
  ["douyin", 1125, 633],   // 抖音主页背景 1125×633
  ["xhs-5x4", 1000, 800],  // 小红书背景（1000×800 的说法）
  ["xhs-3x2", 1242, 828],  // 小红书背景（1242×828 的说法）
];
const preview = process.argv.includes("--preview");
const scales = preview ? [1] : [1, 2];

const browser = await chromium.launch();
for (const [name, w, h] of SIZES) {
  for (const scale of scales) {
    const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: scale });
    await page.goto(`file://${path.join(here, "scene.html")}?w=${w}&h=${h}`);
    await page.waitForFunction(() => window.ready === true);
    const file = path.join(outDir, `${preview ? "preview-" : ""}${name}${scale === 2 ? "@2x" : ""}.png`);
    await page.locator("svg").screenshot({ path: file });
    await page.close();
    console.log(file);
  }
}
await browser.close();
