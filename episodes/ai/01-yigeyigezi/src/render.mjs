// 用法：
//   node render.mjs stills <outdir> 0,1.5,3.2 ...   出指定时刻的静帧（png）
//   node render.mjs film <out.mp4> [fps=30] [workers=3]   出整片（无声）
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
let chromium; try { ({ chromium } = require('playwright')); } catch { ({ chromium } = require('/opt/node22/lib/node_modules/playwright')); }
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const url = 'file://' + path.join(here, 'film.html');
const [mode, out, a3, a4] = process.argv.slice(2);

async function openPage(browser) {
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  page.on('pageerror', e => console.error('PAGE ERROR', e.message));
  await page.goto(url);
  await page.evaluate(() => window.ready);
  return page;
}
async function frameJpeg(page, t, type = 'image/jpeg') {
  const b64 = await page.evaluate(([t, type]) => { window.render(t); return document.getElementById('c').toDataURL(type, 0.95).split(',')[1]; }, [t, type]);
  return Buffer.from(b64, 'base64');
}

const browser = await chromium.launch({ args: ['--disable-gpu-vsync'] });
if (mode === 'stills') {
  fs.mkdirSync(out, { recursive: true });
  const page = await openPage(browser);
  for (const s of a3.split(',')) {
    const t = parseFloat(s);
    fs.writeFileSync(path.join(out, `t${t.toFixed(2).padStart(5, '0')}.png`), await frameJpeg(page, t, 'image/png'));
  }
} else if (mode === 'film') {
  const fps = parseInt(a3 || '30'), workers = parseInt(a4 || '3');
  const page0 = await openPage(browser); const dur = await page0.evaluate(() => window.DUR); await page0.close(); const n = Math.round(dur * fps);
  const tmp = path.join(path.dirname(out), 'frames_' + path.basename(out, '.mp4'));
  fs.mkdirSync(tmp, { recursive: true });
  const t0 = Date.now();
  await Promise.all([...Array(workers).keys()].map(async w => {
    const page = await openPage(browser);
    for (let i = w; i < n; i += workers) {
      fs.writeFileSync(path.join(tmp, `f${String(i).padStart(5, '0')}.jpg`), await frameJpeg(page, i / fps));
      if (w === 0 && i % (fps * 5) === 0) console.log(`frame ${i}/${n}  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
    }
  }));
  await new Promise((res, rej) => {
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', String(fps), '-i', path.join(tmp, 'f%05d.jpg'),
      '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], { stdio: 'inherit' });
    ff.on('close', c => (c === 0 ? res() : rej(new Error('ffmpeg ' + c))));
  });
  fs.rmSync(tmp, { recursive: true, force: true });
  console.log('done', out, ((Date.now() - t0) / 1000).toFixed(0) + 's');
}
await browser.close();
