// node stills.mjs <url> <outprefix> <t1,t2,...>   (waits for window.ready, calls window.seek(t), saves the canvas)
import { createRequire } from 'module'; const require = createRequire(import.meta.url);
const { chromium } = require('playwright'); import fs from 'fs';
const [url, out, ts] = process.argv.slice(2);
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
p.on('pageerror', e => console.error('PAGE ERROR', e.message)); p.on('console', m => { if (m.type() === 'error') console.error('console:', m.text()); });
await p.goto(url); await p.waitForFunction(() => window.ready && window.seek, null, { timeout: 120000 }); await p.evaluate(() => window.ready);
for (const t of ts.split(',').map(Number)) {
  const s = Date.now(); const d = await p.evaluate(async t => { await window.seek(t); return document.getElementById('c').toDataURL('image/png'); }, t);
  fs.writeFileSync(`${out}_${t}.png`, Buffer.from(d.split(',')[1], 'base64')); console.log('still', t, Date.now() - s, 'ms');
}
await b.close();
