// node cover.mjs -> out/cover_9x16.png, out/cover_3x4.png (built from the film's own frame)
import { createRequire } from 'module'; import fs from 'fs'; import path from 'path'; import { execFileSync } from 'child_process';
const require = createRequire(import.meta.url); const { chromium } = require('playwright');
const ROOT = path.dirname(new URL(import.meta.url).pathname);
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
p.on('pageerror', e => console.error(e.message));
await p.goto('file://' + path.join(ROOT, 'film', 'index.html')); await p.evaluate(() => window.ready);
const url = await p.evaluate(() => {
  seek(CUES.shots.find(s => s[0] === 'S09')[1] + 0.5);
  screenCam();
  const g = ctx.createLinearGradient(0, 0, 0, 980);
  g.addColorStop(0, 'rgba(14,13,12,0.97)'); g.addColorStop(0.55, 'rgba(14,13,12,0.85)'); g.addColorStop(1, 'rgba(14,13,12,0)');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, 980);
  // cover text: left aligned, two faces, one accent
  text('如果眼睛能看见', 90, 420, { face: DISPLAY, size: 120, color: '#F7F2E8' });
  text('Wi-Fi', 86, 610, { face: DISPLAY, size: 210, color: ACC });
  text('整栋楼都在发光', 96, 710, { size: 54, color: '#F7F2E8' });
  text('如果 · 会怎样  01', 96, 270, { size: 40, weight: 400, color: '#F7F2E8', alpha: 0.8 });
  return document.getElementById('c').toDataURL('image/png');
});
fs.writeFileSync(path.join(ROOT, 'out', 'cover_9x16.png'), Buffer.from(url.split(',')[1], 'base64'));
await b.close();
execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', path.join(ROOT, 'out', 'cover_9x16.png'), '-vf', 'crop=1080:1440:0:120', path.join(ROOT, 'out', 'cover_3x4.png')]);
console.log('covers written');
