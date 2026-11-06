// node render.mjs [--draft] [--fps 24] [--workers 3] [--from s] [--to s] [--sheet] [--encode-only]
// The page is a pure function of time (window.render(t) = window.seek(t)); each worker opens its own browser and writes
// JPEG frames to frames/<tag>/f_00000.jpg. Existing frames are skipped, so an interrupted render resumes where it stopped.
// --sheet: one frame per beat (2 fps at 120 BPM) in draft quality -> review/beat_sheet.jpg
// otherwise: frames -> H.264 yuv420p CRF 16 with audio/mix.wav and a light grain -> out/如果眼睛能看见WiFi_高岛平团地.mp4
import fs from 'fs'; import path from 'path'; import { execFileSync } from 'child_process';
import { fileURLToPath } from 'url';
const HERE = path.dirname(fileURLToPath(import.meta.url));
const LIB = process.env.LIB || '/root/lemo-opuscar';
const { openDemo, closeServer } = await import(path.join(LIB, 'core/render/page.mjs'));
const args = process.argv.slice(2), has = k => args.includes(k), opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const SHEET = has('--sheet'), DRAFT = has('--draft') || SHEET;
const FPS = SHEET ? 2 : +opt('--fps', 24), WK = +opt('--workers', 3);
const Q = DRAFT ? 'draft' : opt('--q', 'pr=1&ssaa=2');
const TL = JSON.parse(fs.readFileSync(path.join(HERE, 'timeline.json'), 'utf8'));
const DUR = TL.dur, from = +opt('--from', 0), to = Math.min(DUR, +opt('--to', DUR));
const tag = SHEET ? 'beats' : DRAFT ? `draft${FPS}` : `final${FPS}`;
const dir = path.join(HERE, 'frames', tag); fs.mkdirSync(dir, { recursive: true });
const name = f => path.join(dir, `f_${String(f).padStart(5, '0')}.jpg`);
const TOTAL = Math.round(DUR * FPS), f0 = Math.round(from * FPS), f1 = Math.min(TOTAL, Math.round(to * FPS));
const todo = []; for (let f = f0; f < f1; f++) if (!fs.existsSync(name(f))) todo.push(f);
const t0 = Date.now();
if (!has('--encode-only') && todo.length) {
  console.log(`${tag}: ${todo.length} of ${f1 - f0} frames to render, ${WK} workers, q=${Q}`);
  let next = 0, done = 0;
  await Promise.all([...Array(Math.min(WK, todo.length))].map(async (_, w) => {
    const { browser, page } = await openDemo(HERE, { w: 1080, h: 1920, q: Q });
    while (next < todo.length) {
      const f = todo[next++];
      await page.evaluate(t => window.seek(t), f / FPS);
      const buf = await page.screenshot({ type: 'jpeg', quality: 95, timeout: 0 });
      fs.writeFileSync(name(f) + '.tmp', buf); fs.renameSync(name(f) + '.tmp', name(f));
      if (++done % 24 === 0 || done === todo.length) {
        const el = (Date.now() - t0) / 1000;
        console.log(`  ${done}/${todo.length}  ${el.toFixed(0)} s  (${(el / done).toFixed(2)} s/frame, ~${((todo.length - done) * el / done / 60).toFixed(0)} min left)`);
      }
    }
    await browser.close();
  }));
  closeServer();
}
if (SHEET) {
  execFileSync('python3', [path.join(HERE, 'tools/sheet_frames.py'), dir, path.join(HERE, 'review/beat_sheet.jpg'), String(FPS)], { stdio: 'inherit' });
  process.exit(0);
}
if (DRAFT && !has('--encode')) process.exit(0);
const missing = []; for (let f = 0; f < TOTAL; f++) if (!fs.existsSync(name(f))) missing.push(f);
if (missing.length) { console.log(`${missing.length} frames still missing (first ${missing[0]}): not encoding yet`); process.exit(0); }
const out = path.join(HERE, 'out', DRAFT ? '草稿.mp4' : '如果眼睛能看见WiFi_高岛平团地.mp4'); fs.mkdirSync(path.dirname(out), { recursive: true });
execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', String(FPS), '-i', path.join(dir, 'f_%05d.jpg'), '-i', path.join(HERE, 'audio/mix.wav'),
  '-vf', 'noise=alls=2:allf=t', '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-r', String(FPS),
  '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-movflags', '+faststart', '-shortest', out], { stdio: 'inherit' });
console.log('wrote', out, `${((Date.now() - t0) / 1000).toFixed(0)} s`);
process.exit(0);
