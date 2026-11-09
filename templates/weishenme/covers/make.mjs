// make.mjs — lay out the four covers (抖音 1080×1920, 小红书 1080×1440) as HTML and screenshot them.
import { createRequire } from "node:module";
import fs from "node:fs";
import path from "node:path";
const { chromium } = createRequire(import.meta.url)("playwright");
const HERE = path.dirname(new URL(import.meta.url).pathname);
const A = JSON.parse(fs.readFileSync(path.join(HERE, "art/anchors.json"), "utf8"));
const SMILEY = "file://" + path.join(HERE, "../assets/fonts/SmileySans-Oblique.ttf");
const NOTO = "file:///usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc";
const SERIES = "你每天都在用，但你不知道它怎么工作";

const COVERS = [
  { out: "ep01-douyin", W: 1080, H: 1920, ep: "EP.01", title: ["手机怎么知道", "你把它<b>横过来</b>了？"],
    hero: "ep01-hero-dy", heroDy: 40, anchor: A["ep01-hero-dy"], inset: { img: "ep01-inset", cx: 540, cy: 1060, src: 400, x: 830, y: 1440, r: 210 },
    arc: { cx: 470, cy: 1190, r: 520, a0: -86, a1: -126 }, ser: 300, t1: 452, t2: 602, size: 132, wash: 700 },
  { out: "ep01-xiaohongshu", W: 1080, H: 1440, ep: "EP.01", title: ["手机怎么知道", "你把它<b>横过来</b>了？"],
    hero: "ep01-hero-xhs", heroDy: 30, anchor: A["ep01-hero-xhs"], inset: { img: "ep01-inset", cx: 540, cy: 1060, src: 400, x: 845, y: 1150, r: 185 },
    arc: { cx: 470, cy: 910, r: 450, a0: -86, a1: -126 }, ser: 108, t1: 252, t2: 398, size: 128, wash: 470 },
  { out: "ep02-douyin", W: 1080, H: 1920, ep: "EP.02", title: ["热了两分钟，", "中间还是<b>凉</b>的？"],
    hero: "ep02-hero-dy", heroDy: 0, anchor: A["ep02-hero-dy"], inset: { img: "ep02-inset", cx: 540, cy: 1255, src: 440, x: 820, y: 1440, r: 200 },
    ser: 300, t1: 452, t2: 602, size: 132, wash: 760 },
  { out: "ep02-xiaohongshu", W: 1080, H: 1440, ep: "EP.02", title: ["热了两分钟，", "中间还是<b>凉</b>的？"],
    hero: "ep02-hero-xhs", heroDy: 0, anchor: A["ep02-hero-xhs"], inset: { img: "ep02-inset", cx: 540, cy: 1255, src: 440, x: 830, y: 1215, r: 180 },
    ser: 108, t1: 252, t2: 398, size: 128, wash: 470 },
  { out: "ep03-douyin", W: 1080, H: 1920, ep: "EP.03", title: ["按一下，", "噪音怎么就<b>没了</b>？"],
    hero: "ep03-hero-dy", heroDy: 0, anchor: A["ep03-hero-dy"], inset: { img: "ep03-inset", cx: 560, cy: 1000, src: 430, x: 850, y: 1490, r: 190 },
    ser: 300, t1: 452, t2: 602, size: 132, wash: 800 },
  { out: "ep03-xiaohongshu", W: 1080, H: 1440, ep: "EP.03", title: ["按一下，", "噪音怎么就<b>没了</b>？"],
    hero: "ep03-hero-xhs", heroDy: 0, anchor: A["ep03-hero-xhs"], inset: { img: "ep03-inset", cx: 560, cy: 1000, src: 430, x: 830, y: 1215, r: 175 },
    ser: 108, t1: 252, t2: 398, size: 128, wash: 540 },
  { out: "ep04-douyin", W: 1080, H: 1920, ep: "EP.04", title: ["戴着手套，", "为什么点不动<b>屏幕</b>？"],
    hero: "ep04-hero-dy", heroDy: 0, anchor: A["ep04-hero-dy"], inset: { img: "ep04-inset", cx: 375, cy: 1125, src: 330, x: 880, y: 960, r: 180 },
    ser: 300, t1: 452, t2: 602, size: 124, wash: 760 },
  { out: "ep04-xiaohongshu", W: 1080, H: 1440, ep: "EP.04", title: ["戴着手套，", "为什么点不动<b>屏幕</b>？"],
    hero: "ep04-hero-xhs", heroDy: 0, anchor: A["ep04-hero-xhs"], inset: { img: "ep04-inset", cx: 375, cy: 1125, src: 330, x: 875, y: 770, r: 165 },
    ser: 108, t1: 252, t2: 398, size: 120, wash: 480 },
  { out: "ep05-douyin", W: 1080, H: 1920, ep: "EP.05", title: ["体脂秤怎么知道，", "你有多少<b>脂肪</b>？"],
    hero: "ep05-hero-dy", heroDy: 0, anchor: A["ep05-hero-dy"], inset: { img: "ep05-inset", cx: 540, cy: 1070, src: 430, x: 830, y: 1010, r: 210 },
    ser: 300, t1: 452, t2: 602, size: 124, wash: 760 },
  { out: "ep05-xiaohongshu", W: 1080, H: 1440, ep: "EP.05", title: ["体脂秤怎么知道，", "你有多少<b>脂肪</b>？"],
    hero: "ep05-hero-xhs", heroDy: 0, anchor: A["ep05-hero-xhs"], inset: { img: "ep05-inset", cx: 540, cy: 1070, src: 430, x: 860, y: 720, r: 175 },
    ser: 108, t1: 252, t2: 398, size: 120, wash: 480 },
];
const ONLY = process.argv[2];                                   // node make.mjs ep04 → only those covers

function html(c) {
  const i = c.inset, k = i.r / i.src;                                   // the inset shows a circle of radius src (px) from the inset frame
  const ax = c.anchor[0], ay = c.anchor[1] + c.heroDy;
  const dx = i.x - ax, dy = i.y - ay, L = Math.hypot(dx, dy), ex = i.x - dx / L * (i.r + 6), ey = i.y - dy / L * (i.r + 6);
  let arc = "";
  if (c.arc) {
    const r = c.arc.r, rad = (d) => d * Math.PI / 180, cx = c.arc.cx, cy = c.arc.cy + 0;
    const p0 = [cx + r * Math.cos(rad(c.arc.a0)), cy + r * Math.sin(rad(c.arc.a0))], p1 = [cx + r * Math.cos(rad(c.arc.a1)), cy + r * Math.sin(rad(c.arc.a1))];
    const t = [Math.sin(rad(c.arc.a1)), -Math.cos(rad(c.arc.a1))];      // direction of travel (counter-clockwise)
    const h = [p1[0] + t[0] * 34, p1[1] + t[1] * 34], n = [-t[1], t[0]];
    arc = `<path d="M ${p0[0]} ${p0[1]} A ${r} ${r} 0 0 0 ${p1[0]} ${p1[1]}" fill="none" stroke="#FF4A1C" stroke-width="7" stroke-dasharray="20 14"/>
      <path d="M ${h[0]} ${h[1]} L ${p1[0] + n[0] * 17} ${p1[1] + n[1] * 17} L ${p1[0] - n[0] * 17} ${p1[1] - n[1] * 17} Z" fill="#FF4A1C"/>`;
  }
  return `<!doctype html><html><head><meta charset="utf-8"><style>
  @font-face { font-family: "Smiley"; src: url("${SMILEY}"); }
  @font-face { font-family: "NotoSC"; src: url("${NOTO}"); }
  html, body { margin: 0; background: #ECEBE6; }
  #cv { position: relative; width: ${c.W}px; height: ${c.H}px; overflow: hidden; background: #ECEBE6; }
  .hero { position: absolute; left: 0; top: ${c.heroDy}px; width: 1080px; height: 1920px; background: url("art/${c.hero}.png") no-repeat; }
  .wash { position: absolute; left: 0; top: 0; width: 100%; height: ${c.wash}px; background: linear-gradient(#ECEBE6 0%, #ECEBE6 70%, rgba(236,235,230,0) 100%); }
  .ser { position: absolute; left: 76px; top: ${c.ser - 40}px; font: 400 38px "NotoSC"; color: rgba(20,20,20,0.62); letter-spacing: 1px; }
  .ser i { font-style: normal; color: #FF4A1C; font-weight: 700; margin-left: 14px; }
  .t { position: absolute; left: 72px; font: ${c.size}px "Smiley"; color: #141414; white-space: nowrap; line-height: 1; }
  .t b { font-weight: normal; color: #FF4A1C; }
  .inset { position: absolute; left: ${i.x - i.r}px; top: ${i.y - i.r}px; width: ${2 * i.r}px; height: ${2 * i.r}px; border-radius: 50%;
    background: #17191C url("art/${i.img}.png") no-repeat; background-size: ${1080 * k}px ${1920 * k}px; background-position: ${-(i.cx - i.src) * k}px ${-(i.cy - i.src) * k}px;
    box-shadow: 0 0 0 10px #141414, 0 24px 50px rgba(20,20,20,0.28); }
  svg { position: absolute; left: 0; top: 0; }
  </style></head><body><div id="cv">
  <div class="hero"></div>
  <svg width="${c.W}" height="${c.H}">${arc}
    <line x1="${ax}" y1="${ay}" x2="${ex}" y2="${ey}" stroke="#141414" stroke-width="6" stroke-linecap="round"/>
    <circle cx="${ax}" cy="${ay}" r="16" fill="none" stroke="#FF4A1C" stroke-width="7"/></svg>
  <div class="wash"></div>
  <div class="ser">${SERIES}<i>${c.ep}</i></div>
  <div class="t" style="top:${c.t1 - c.size * 0.86}px">${c.title[0]}</div>
  <div class="t" style="top:${c.t2 - c.size * 0.86}px">${c.title[1]}</div>
  <div class="inset"></div>
  </div></body></html>`;
}

const browser = await chromium.launch();
for (const c of COVERS.filter((c) => !ONLY || c.out.startsWith(ONLY))) {
  const f = path.join(HERE, `${c.out}.html`); fs.writeFileSync(f, html(c));
  const page = await browser.newPage({ viewport: { width: c.W, height: c.H } });
  await page.goto("file://" + f); await page.evaluate(() => document.fonts.ready); await page.waitForTimeout(300);
  await page.locator("#cv").screenshot({ path: path.join(HERE, "out", `${c.out}.png`) });
  await page.close();
}
await browser.close();
console.log("covers ->", COVERS.filter((c) => !ONLY || c.out.startsWith(ONLY)).map((c) => c.out).join(", "));
