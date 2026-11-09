// node render_iso.mjs stills t1 t2 …  → stills/t*.png ；node render_iso.mjs frames FPS DUR → frames/%05d.png
import { chromium } from 'playwright'; import fs from 'node:fs'; import path from 'node:path'; import url from 'node:url';
const HERE = path.dirname(url.fileURLToPath(import.meta.url)); const [mode, ...rest] = process.argv.slice(2);
const br = await chromium.launch(); const pg = await br.newPage({ viewport: { width: 1080, height: 1920 } }); pg.on('pageerror', e => console.log('ERR', e.message));
await pg.goto('file://' + path.join(HERE, 'iso.html')); await pg.evaluate(() => window.ready());
const shot = async t => Buffer.from(await pg.evaluate(t => { window.seek(t); return document.getElementById('c').toDataURL('image/png').split(',')[1]; }, t), 'base64');
if (mode === 'stills') { fs.mkdirSync(path.join(HERE, 'stills'), { recursive: true }); for (const t of rest) fs.writeFileSync(path.join(HERE, 'stills', `t${(+t).toFixed(2)}.png`), await shot(+t)); }
else { const fps = +rest[0], dur = +rest[1], dir = path.join(HERE, 'frames'); fs.mkdirSync(dir, { recursive: true }); const n = Math.round(fps * dur);
  for (let i = 0; i < n; i++) fs.writeFileSync(path.join(dir, String(i).padStart(5, '0') + '.png'), await shot(i / fps)); }
await br.close();
