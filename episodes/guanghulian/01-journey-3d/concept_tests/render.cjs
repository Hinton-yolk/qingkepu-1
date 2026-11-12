// 把概念测试的网页逐帧渲成 PNG。用法：
//   node render.cjs <网页> <输出目录> <秒数> '<传给 renderFrame 的 JSON>' [--times 1.0,3.2]
// 网页里要有 window.renderFrame(t, opts)。逻辑尺寸 540×960，按 2 倍像素渲，再由 ffmpeg 缩回 540×960。
// --times 只渲指定的几个时刻（看静帧用），文件名是 still_<秒>.png。
const { chromium } = require('playwright');
const fs = require('node:fs');
const path = require('node:path');

(async () => {
const [page_, outDir, secs, optJson, flag, timesArg] = process.argv.slice(2);
const FPS = 30;
const opts = JSON.parse(optJson || '{}');
fs.mkdirSync(outDir, { recursive: true });
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 540, height: 960 }, deviceScaleFactor: 2 });
await page.goto('file://' + path.resolve(page_));
await page.evaluate(() => document.fonts.ready);
const shot = async (t, file) => {
  await page.evaluate(([t, o]) => window.renderFrame(t, o), [t, opts]);
  await page.locator('#c').screenshot({ path: file });
};
if (flag === '--times') {
  for (const t of timesArg.split(',').map(Number)) await shot(t, path.join(outDir, `still_${t.toFixed(2)}.png`));
} else {
  const n = Math.round(Number(secs) * FPS);
  for (let i = 0; i < n; i++) await shot(i / FPS, path.join(outDir, `f_${String(i).padStart(5, '0')}.png`));
  console.log(`${n} 帧 → ${outDir}`);
}
await browser.close();
})();
