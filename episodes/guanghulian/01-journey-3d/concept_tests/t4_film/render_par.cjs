// 并行渲染的单个工作进程。用法：
//   node render_par.cjs <网页> <输出目录> '<opts JSON>' <总帧数> <工作序号> <工作总数> [--caps-only]
// 第 i 帧属于工作序号 i % 工作总数。逻辑尺寸 540×960，按 1 倍像素渲（画布本身就是 540×960）。
// --caps-only：只渲「字幕条正在显示」的帧（window.t4CapActive(t) 为真），其余帧由 build.sh 从无字幕底帧复制。
const { chromium } = require('playwright');
const fs = require('node:fs');
const path = require('node:path');
(async () => {
  const [page_, outDir, optJson, nS, wS, kS, flag] = process.argv.slice(2);
  const N = +nS, w = +wS, k = +kS, FPS = 30, opts = JSON.parse(optJson || '{}');
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 540, height: 960 }, deviceScaleFactor: 1 });
  await page.goto('file://' + path.resolve(page_));
  await page.evaluate(() => document.fonts.ready);
  let n = 0;
  for (let i = w; i < N; i += k) {
    const t = i / FPS;
    if (flag === '--caps-only' && !(await page.evaluate(t => window.t4CapActive(t), t))) continue;
    await page.evaluate(([t, o]) => window.renderFrame(t, o), [t, opts]);
    await page.locator('#c').screenshot({ path: path.join(outDir, `f_${String(i).padStart(5, '0')}.png`) });
    n++;
  }
  console.log(`worker ${w}: ${n} 帧`);
  await browser.close();
})();
