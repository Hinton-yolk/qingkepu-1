// node render.mjs --stills=1,2.5 --out=review/stills        full-res PNG stills
// node render.mjs --sheet=0.5,1,... --cols=6 --w=270 --out=review/sheet.jpg   contact sheet
// node render.mjs --video --workers=4 [--from=0 --to=90.6] --out=out/video.mp4   H.264 yuv420p CRF 16
import { createRequire } from 'module';
import { spawn, execFileSync } from 'child_process';
import fs from 'fs'; import path from 'path';
const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const A = Object.fromEntries(process.argv.slice(2).map(a => { const [k, v] = a.replace(/^--/, '').split('='); return [k, v ?? true]; }));
const ROOT = path.dirname(new URL(import.meta.url).pathname);
const URL_ = 'file://' + path.join(ROOT, 'film', 'index.html');

async function page(browser) {
  const p = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  p.on('pageerror', e => console.error('PAGE ERROR', e.message));
  p.on('console', m => { if (m.type() === 'error') console.error('console:', m.text()); });
  await p.goto(URL_);
  await p.waitForFunction(() => window.ready && window.seek);
  await p.evaluate(() => window.ready);
  return p;
}
async function grab(p, t, type = 'image/png', q = 0.92) {
  const url = await p.evaluate(([t, type, q]) => { window.seek(t); return document.getElementById('c').toDataURL(type, q); }, [t, type, q]);
  return Buffer.from(url.split(',')[1], 'base64');
}
const browser = await chromium.launch({ args: ['--disable-gpu-vsync', '--force-color-profile=srgb'] });
const t0 = Date.now();
if (A.stills) {
  const p = await page(browser); fs.mkdirSync(A.out, { recursive: true });
  for (const t of String(A.stills).split(',').map(Number)) {
    const s = Date.now(); fs.writeFileSync(path.join(A.out, `t${t.toFixed(2)}.png`), await grab(p, t)); console.log('still', t, Date.now() - s, 'ms');
  }
} else if (A.sheet) {
  const ts = String(A.sheet).split(',').map(Number), cols = +(A.cols ?? 6), w = +(A.w ?? 270), h = Math.round(w * 16 / 9);
  const tmp = fs.mkdtempSync('/tmp/claude-0/sheet-');
  const n = +(A.workers ?? 4), chunks = Array.from({ length: n }, (_, k) => ts.map((t, i) => [t, i]).filter((_, i) => i % n === k));
  await Promise.all(chunks.map(async ch => { const p = await page(browser); for (const [t, i] of ch) fs.writeFileSync(path.join(tmp, `f${String(i).padStart(4, '0')}.jpg`), await grab(p, t, 'image/jpeg', 0.9)); }));
  const rows = Math.ceil(ts.length / cols);
  const lab = A.label !== 'no';
  const vf = `scale=${w}:${h}` + (lab ? `,drawtext=fontfile=/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc:text='%{eif\\:n\\:d}':x=6:y=6:fontsize=${Math.round(w / 10)}:fontcolor=white:box=1:boxcolor=black@0.6` : '') + `,tile=${cols}x${rows}:padding=4:color=gray`;
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', '1', '-i', path.join(tmp, 'f%04d.jpg'), '-vf', vf, '-frames:v', '1', '-q:v', '3', A.out]);
  fs.rmSync(tmp, { recursive: true });
  console.log('sheet', A.out, ts.length, 'frames');
} else if (A.video) {
  const fps = 30, from = +(A.from ?? 0), dur = await (await page(browser)).evaluate(() => window.DURATION);
  const to = +(A.to ?? dur), N = Math.round((to - from) * fps), n = +(A.workers ?? 4);
  const seg = Math.ceil(N / n), tmp = A.tmp ? path.resolve(A.tmp) : path.join(ROOT, 'frames'); fs.mkdirSync(tmp, { recursive: true });
  let done = 0;
  await Promise.all(Array.from({ length: n }, async (_, k) => {
    const a = k * seg, b = Math.min(N, a + seg); if (a >= b) return;
    const p = await page(browser);
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'png', '-i', '-',
      '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-r', String(fps), path.join(tmp, `seg${k}.mp4`)]);
    for (let f = a; f < b; f++) {
      const buf = await grab(p, from + f / fps);
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (++done % 150 === 0) console.log(`${done}/${N} frames  ${((Date.now() - t0) / done).toFixed(0)} ms/frame`);
    }
    ff.stdin.end(); await new Promise(r => ff.on('close', r));
  }));
  const list = path.join(tmp, 'list.txt');
  fs.writeFileSync(list, Array.from({ length: n }, (_, k) => `file 'seg${k}.mp4'`).filter((_, k) => fs.existsSync(path.join(tmp, `seg${k}.mp4`))).join('\n'));
  const silent = path.join(tmp, 'video_silent.mp4');
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', list, '-c', 'copy', silent]);
  if (A.audio) execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', silent, '-i', A.audio, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-shortest', '-movflags', '+faststart', A.out]);
  else fs.copyFileSync(silent, A.out);
  console.log('video', A.out, N, 'frames', ((Date.now() - t0) / 1000).toFixed(1), 's');
}
await browser.close();
