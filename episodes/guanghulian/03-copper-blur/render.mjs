// node render.mjs [start] [end] [workers] [outdir] —— 用 skill 引擎的页面逐帧渲（window.renderFrame(t)，纯时间函数），多页面并行、帧按编号存盘、可断点续渲
import { chromium } from 'playwright';
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path'; import url from 'node:url';
const HERE = path.dirname(url.fileURLToPath(import.meta.url)), ROOT = path.join(HERE, '代码工程');
const [a = 0, b = 79, nw = 4, out = 'frames'] = process.argv.slice(2); const FPS = +process.env.FPS || 30;
const MIME = { '.js': 'text/javascript', '.html': 'text/html', '.woff': 'font/woff', '.json': 'application/json', '.png': 'image/png' };
const srv = http.createServer((q, r) => { const p = path.join(ROOT, decodeURIComponent(q.url.split('?')[0])); if (!p.startsWith(ROOT) || !fs.existsSync(p)) { r.writeHead(404); r.end(); return; }
  r.writeHead(200, { 'content-type': MIME[path.extname(p)] || 'application/octet-stream' }); fs.createReadStream(p).pipe(r); }).listen(0);
const port = srv.address().port, dir = path.join(HERE, out); fs.mkdirSync(dir, { recursive: true });
const todo = []; for (let f = Math.round(+a * FPS); f < Math.round(+b * FPS); f++) { const p = path.join(dir, String(f).padStart(5, '0') + '.png'); if (!fs.existsSync(p)) todo.push([f, p]); }
const br = await chromium.launch();
await Promise.all([...Array(+nw)].map(async (_, w) => {
  const pg = await br.newPage({ viewport: { width: 1080, height: 1920 } }); pg.on('pageerror', e => console.log('ERR', e.message));
  await pg.goto(`http://127.0.0.1:${port}/index.html?render=1&film=${process.env.FILM||"vox"}&w=1080&h=1920`);
  await pg.waitForFunction('window.__ready === true || !!window.__bootFailed', null, { timeout: 120000 });
  const bf = await pg.evaluate('window.__bootFailed || null'); if (bf) throw new Error(bf);
  for (let i = w; i < todo.length; i += +nw) { const [f, p] = todo[i];
    // 相机快的帧：180° 快门内取几次相机位置平均（只动相机，画面里的元素时间不变）
    const b64 = await pg.evaluate(async ([t, FPS]) => { await window.prepare(t);
      const SH = 0.5 / FPS, sp = window.CAM_SPEED ? window.CAM_SPEED(t) * SH * 30 : 0, n = sp < 3 ? 1 : Math.min(16, 2 + Math.ceil(sp / 6));
      if (n === 1) { window.CAM_DT = 0; window.renderFrame(t); return window.__canvas.toDataURL('image/png').split(',')[1]; }
      const cv = window.__canvas, acc = window.__acc || (window.__acc = Object.assign(document.createElement('canvas'), { width: cv.width, height: cv.height })), g = acc.getContext('2d');
      for (let i = 0; i < n; i++) { window.CAM_DT = (i / (n - 1) - 0.5) * SH; window.renderFrame(t); g.globalAlpha = 1 / (i + 1); g.drawImage(cv, 0, 0); }
      window.CAM_DT = 0; g.globalAlpha = 1; return acc.toDataURL('image/png').split(',')[1]; }, [f / FPS, FPS]);
    fs.writeFileSync(p + '.tmp', Buffer.from(b64, 'base64')); fs.renameSync(p + '.tmp', p); }
}));
await br.close(); srv.close(); console.log('rendered', todo.length);
