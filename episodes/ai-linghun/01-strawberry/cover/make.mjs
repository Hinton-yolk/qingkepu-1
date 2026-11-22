// make.mjs — EP.01 covers: 抖音 1080×1920 and 小红书 1080×1440, laid out as HTML over film frames and screenshotted.
//   (from film/) node render.mjs --stills=6.8 --bg=hyb --qs=nocap=1 --out=qa/cover_src   (Blender frame 204 under the same grade, no captions); then (from cover/) NODE_PATH=$(npm root -g) node make.mjs
import { createRequire } from "node:module";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
const { chromium } = createRequire(import.meta.url)("playwright");
const HERE = path.dirname(fileURLToPath(import.meta.url)), EP = path.dirname(HERE);
const SRC = path.join(EP, "film/qa/cover_src"), FONTS = path.join(EP, "assets/fonts");
const url = (p) => "file://" + p;
const HERO = url(path.join(SRC, "t6.80.png"));   // 6.8 s: one stroke through "AI：2 个" (at 7.0 the full ✗ hides the 2)   // the card below is drawn in HTML (audience: the #496… numbers read as part numbers)

// one layout, two canvases. heroY: where the film frame's top sits; the strawberry row is at about y = 960 of the 1920-px frame
const COVERS = [   // the strawberry row lands at about y = 960 + heroY; the card below shows how the AI cuts the word (str / aw / berry, GPT-4 tokenizer)
  { out: "cover-douyin", W: 1080, H: 1920, heroY: 0, tag: 236, t1: 352, size: 132, card: { x: 60, y: 1150, w: 960 } },
  { out: "cover-xiaohongshu", W: 1080, H: 1440, heroY: -262, tag: 26, t1: 126, size: 120, card: { x: 80, y: 880, w: 920 } },
];

const html = (c) => `<!doctype html><html><head><meta charset="utf-8"><style>
@font-face { font-family: NS; src: url(${url(path.join(FONTS, "NotoSansSC-900.woff"))}); font-weight: 900; }
@font-face { font-family: NS; src: url(${url(path.join(FONTS, "NotoSansSC-700.woff"))}); font-weight: 700; }
@font-face { font-family: IN; src: url(${url(path.join(FONTS, "Inter-var.woff"))}); font-weight: 100 900; }
html, body { margin: 0; width: ${c.W}px; height: ${c.H}px; overflow: hidden; background: #E7DCCB; font-family: NS, sans-serif; }
.hero { position: absolute; left: 0; top: ${c.heroY}px; width: 1080px; height: 1920px; background: url(${HERO}) center / cover; }
.tag { position: absolute; left: 50%; top: ${c.tag}px; transform: translateX(-50%); padding: 14px 34px; border-radius: 999px; background: rgba(43,39,38,.92);
  color: #F6F0E6; font-weight: 700; font-size: 40px; letter-spacing: 2px; white-space: nowrap; }
.title { position: absolute; left: 0; right: 0; top: ${c.t1}px; text-align: center; font-weight: 900; font-size: ${c.size}px; line-height: 1.12; color: #2B2726; }
.title span { display: inline-block; background: rgba(248,243,234,.94); border-radius: 26px; padding: 4px 34px 12px; box-shadow: 0 10px 30px rgba(60,40,20,.18); }
.title b { color: #E25C38; }
.card { position: absolute; left: ${c.card.x}px; top: ${c.card.y}px; width: ${c.card.w}px; padding: 56px 0 50px; border-radius: 28px; display: flex; justify-content: center; gap: 22px;
  background: linear-gradient(#EFE6D8, #E2D6C3); border: 8px solid #F8F3EA; box-shadow: 0 14px 36px rgba(60,40,20,.28); }
.card i { position: absolute; left: 28px; top: -30px; white-space: nowrap; font-style: normal; font-weight: 900; font-size: 38px;
  color: #fff; background: #E25C38; border-radius: 999px; padding: 6px 24px; box-shadow: 0 6px 16px rgba(60,40,20,.2); }
.blk { position: relative; padding-bottom: 18px; }
.blk::after { content: ""; position: absolute; left: -10px; right: -10px; bottom: 0; height: 30px; border-radius: 10px; background: #2B2726; }
.blk b { position: relative; z-index: 1; display: block; padding: 10px 26px 14px; border-radius: 16px; background: linear-gradient(#FBF7F0, #EAE1D2); box-shadow: 0 6px 0 #CFC3AF, 0 10px 18px rgba(60,40,20,.25);
  font-family: IN, NS, sans-serif; font-weight: 800; font-size: 72px; letter-spacing: 10px; color: #2B2726; }
.card u { position: absolute; right: 26px; bottom: 8px; text-decoration: none; font-weight: 700; font-size: 26px; color: rgba(43,39,38,.62); }
</style></head><body>
<div class="hero"></div>
<div class="tag">AI 灵魂拷问 · 01</div>
<div class="title"><span>AI 为什么</span><br><span><b>数不清</b>字母？</span></div>
<div class="card"><i>AI 眼里：3 块积木</i><div class="blk"><b>str</b></div><div class="blk"><b>aw</b></div><div class="blk"><b>berry</b></div><u>GPT-4 分词器实测</u></div>
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
