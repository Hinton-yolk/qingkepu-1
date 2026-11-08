// Render the avatar and a round-crop preview sheet.
// usage: node render.mjs [path/to/reference-photo.jpg]
// With a reference photo it also writes exports/compare.png (photo beside the avatar) for checking likeness;
// the reference photo itself is never written into the repo.
import { createRequire } from "node:module";
import path from "node:path";
import fs from "node:fs";
import { fileURLToPath } from "node:url";

const { chromium } = createRequire(import.meta.url)("playwright");
const here = path.dirname(fileURLToPath(import.meta.url));
const outDir = path.join(here, "exports");
fs.mkdirSync(outDir, { recursive: true });
const ref = process.argv[2];

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1080 } });
await page.goto(`file://${path.join(here, "avatar.html")}?size=1080`);
await page.waitForFunction(() => window.ready === true);
const file = path.join(outDir, "avatar.png");
await page.locator("svg").screenshot({ path: file });
await page.close();
console.log(file);

const img = p => "data:image/" + (p.endsWith(".png") ? "png" : "jpeg") + ";base64," + fs.readFileSync(p).toString("base64");
const sheet = await browser.newPage({ viewport: { width: 420, height: 400 } });
await sheet.setContent(`<body style="margin:0;background:#E9E2D4;display:flex;gap:28px;align-items:center;padding:30px">
  <img src="${img(file)}" style="width:300px;height:300px;border-radius:50%">
  <img src="${img(file)}" style="width:44px;height:44px;border-radius:50%"></body>`);
await sheet.screenshot({ path: path.join(outDir, "preview-round.png") });
await sheet.close();

if (ref) {
  const cmp = await browser.newPage({ viewport: { width: 1000, height: 500 } });
  await cmp.setContent(`<body style="margin:0;display:flex"><img src="${img(ref)}" style="width:500px;height:500px;object-fit:cover">
    <img src="${img(file)}" style="width:500px;height:500px"></body>`);
  const out = process.env.COMPARE_OUT || path.join(outDir, "compare.png");
  await cmp.screenshot({ path: out });
  await cmp.close();
  console.log(out);
}
await browser.close();
