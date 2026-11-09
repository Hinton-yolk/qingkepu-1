import { chromium } from 'playwright'; import fs from 'node:fs'; import path from 'node:path'; import url from 'node:url';
const HERE = path.dirname(url.fileURLToPath(import.meta.url)); const br = await chromium.launch(); const pg = await br.newPage({ viewport: { width: 1080, height: 1920 } });
pg.on('pageerror', e => console.log('ERR', e.message)); await pg.goto('file://' + path.join(HERE, 'covers.html'));
for (const k of ['Au', 'Ad', 'Bu', 'Bd', 'Cu', 'Cd']) { const b = await pg.evaluate(k => window.draw(k), k); fs.writeFileSync(path.join(HERE, `${k}.png`), Buffer.from(b, 'base64')); }
await br.close();
