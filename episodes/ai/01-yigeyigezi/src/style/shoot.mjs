import { createRequire } from 'node:module'; const require = createRequire(import.meta.url);
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
import fs from 'node:fs'; import path from 'node:path'; import { fileURLToPath } from 'node:url';
const here = path.dirname(fileURLToPath(import.meta.url)); const out = process.argv[2]; fs.mkdirSync(out, { recursive: true });
const b = await chromium.launch(); const page = await b.newPage({ viewport: { width: 1080, height: 1920 } });
page.on('pageerror', e => console.error('ERR', e.message));
for (const th of (process.argv[3] || 'A,B,C').split(',')) for (const sh of [1, 2, 3]) {
  await page.goto('file://' + path.join(here, 'style.html') + `?theme=${th}&shot=${sh}`); await page.evaluate(() => window.ready);
  const b64 = await page.evaluate(() => document.getElementById('c').toDataURL('image/png').split(',')[1]);
  fs.writeFileSync(path.join(out, `${th}${sh}.png`), Buffer.from(b64, 'base64'));
}
await b.close();
