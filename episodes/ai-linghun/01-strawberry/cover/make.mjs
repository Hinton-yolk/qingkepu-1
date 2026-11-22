// make.mjs — EP.01 covers: 抖音 1080×1920 and 小红书 1080×1440, laid out as HTML over film frames and screenshotted.
//   (from film/) node render.mjs --stills=7.0,20.9 --nocap --out=qa/cover_src ; then (from cover/) NODE_PATH=$(npm root -g) node make.mjs
import { createRequire } from "node:module";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
const { chromium } = createRequire(import.meta.url)("playwright");
const HERE = path.dirname(fileURLToPath(import.meta.url)), EP = path.dirname(HERE);
const SRC = path.join(EP, "film/qa/cover_src"), FONTS = path.join(EP, "assets/fonts");
const url = (p) => "file://" + p;
const HERO = url(path.join(SRC, "t7.00.png")), AIV = url(path.join(SRC, "t20.90.png"));

// one layout, two canvases. heroY: where the film frame's top sits; the strawberry row is at about y = 960 of the 1920-px frame
const COVERS = [   // row = where the strawberry row lands; the AI-view card shows the three blocks + their numbers (film 20.9 s)
  { out: "cover-douyin", W: 1080, H: 1920, heroY: 0, tag: 250, t1: 330, size: 132, card: { x: 70, y: 1110, w: 940 } },
  { out: "cover-xiaohongshu", W: 1080, H: 1440, heroY: -300, tag: 36, t1: 110, size: 124, card: { x: 90, y: 800, w: 900 } },
];
const CROP = { x: 40, y: 700, w: 1000, h: 310 };   // the blocks band in the 1080×1920 frame at 20.9 s

const html = (c) => `<!doctype html><html><head><meta charset="utf-8"><style>
@font-face { font-family: NS; src: url(${url(path.join(FONTS, "NotoSansSC-900.woff"))}); font-weight: 900; }
@font-face { font-family: NS; src: url(${url(path.join(FONTS, "NotoSansSC-700.woff"))}); font-weight: 700; }
html, body { margin: 0; width: ${c.W}px; height: ${c.H}px; overflow: hidden; background: #E7DCCB; font-family: NS, sans-serif; }
.hero { position: absolute; left: 0; top: ${c.heroY}px; width: 1080px; height: 1920px; background: url(${HERO}) center / cover; }
.tag { position: absolute; left: 50%; top: ${c.tag}px; transform: translateX(-50%); padding: 14px 34px; border-radius: 999px; background: rgba(43,39,38,.92);
  color: #F6F0E6; font-weight: 700; font-size: 40px; letter-spacing: 2px; white-space: nowrap; }
.title { position: absolute; left: 0; right: 0; top: ${c.t1}px; text-align: center; font-weight: 900; font-size: ${c.size}px; line-height: 1.12; color: #2B2726; }
.title span { display: inline-block; background: rgba(248,243,234,.94); border-radius: 26px; padding: 4px 34px 12px; box-shadow: 0 10px 30px rgba(60,40,20,.18); }
.title b { color: #E25C38; }
.card { position: absolute; left: ${c.card.x}px; top: ${c.card.y}px; width: ${c.card.w}px; height: ${Math.round(c.card.w * CROP.h / CROP.w)}px; border-radius: 28px;
  background: url(${AIV}) ${-CROP.x * c.card.w / CROP.w}px ${-CROP.y * c.card.w / CROP.w}px / ${1080 * c.card.w / CROP.w}px ${1920 * c.card.w / CROP.w}px no-repeat;
  border: 8px solid #F8F3EA; box-shadow: 0 14px 36px rgba(60,40,20,.28); }
.card i { position: absolute; left: 28px; top: -30px; white-space: nowrap; font-style: normal; font-weight: 900; font-size: 38px;
  color: #fff; background: #E25C38; border-radius: 999px; padding: 6px 24px; box-shadow: 0 6px 16px rgba(60,40,20,.2); }
</style></head><body>
<div class="hero"></div>
<div class="tag">AI 灵魂拷问 · 01</div>
<div class="title"><span>AI 为什么</span><br><span><b>数不清</b>字母？</span></div>
<div class="card"><i>AI 眼里：3 块积木</i></div>
</body></html>`;

const browser = await chromium.launch();
for (const c of COVERS) {
  const page = await browser.newPage({ viewport: { width: c.W, height: c.H }, deviceScaleFactor: 1 });
  const f = path.join(HERE, c.out + ".html"); fs.writeFileSync(f, html(c));
  await page.goto(url(f)); await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: path.join(HERE, c.out + ".png") }); console.log(c.out + ".png", c.W, "x", c.H);
  await page.close();
}
await browser.close();
