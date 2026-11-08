// Render the avatar with and without glasses, plus a round-crop preview sheet.
// usage: node render.mjs
import { createRequire } from "node:module";
import path from "node:path";
import fs from "node:fs";
import { fileURLToPath } from "node:url";

const { chromium } = createRequire(import.meta.url)("playwright");
const here = path.dirname(fileURLToPath(import.meta.url));
const outDir = path.join(here, "exports");
fs.mkdirSync(outDir, { recursive: true });

const browser = await chromium.launch();
for (const glasses of [0, 1]) {
  const page = await browser.newPage({ viewport: { width: 1080, height: 1080 } });
  await page.goto(`file://${path.join(here, "avatar.html")}?size=1080&glasses=${glasses}`);
  await page.waitForFunction(() => window.ready === true);
  const file = path.join(outDir, `avatar${glasses ? "-glasses" : ""}.png`);
  await page.locator("svg").screenshot({ path: file });
  await page.close();
  console.log(file);
}

// preview: both versions as round crops at profile sizes (large and feed-sized)
const page = await browser.newPage({ viewport: { width: 760, height: 420 } });
const img = n => "data:image/png;base64," + fs.readFileSync(path.join(outDir, n)).toString("base64");
await page.setContent(`<body style="margin:0;background:#F1ECE2;display:flex;gap:28px;align-items:center;padding:30px;font:14px sans-serif">
  ${["avatar.png", "avatar-glasses.png"].map(n => `<div style="display:flex;flex-direction:column;gap:18px;align-items:center">
    <img src="${img(n)}" style="width:300px;height:300px;border-radius:50%">
    <img src="${img(n)}" style="width:44px;height:44px;border-radius:50%"></div>`).join("")}
</body>`);
await page.screenshot({ path: path.join(outDir, "preview-round.png") });
await browser.close();
console.log(path.join(outDir, "preview-round.png"));
