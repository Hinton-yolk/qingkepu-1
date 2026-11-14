// 用 Playwright 打开 t4.html，把 window.t4Events() 写成 JSON。用法：node dump_events.cjs <输出.json>
const { chromium } = require('playwright');
const fs = require('node:fs');
const path = require('node:path');
(async () => {
  const out = process.argv[2];
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 540, height: 960 } });
  await page.goto('file://' + path.resolve(__dirname, 't4.html'));
  await page.evaluate(() => document.fonts.ready);
  const ev = await page.evaluate(() => window.t4Events());
  fs.writeFileSync(out, JSON.stringify(ev));
  console.log(`${ev.length} 个事件 → ${out}`);
  await browser.close();
})();
