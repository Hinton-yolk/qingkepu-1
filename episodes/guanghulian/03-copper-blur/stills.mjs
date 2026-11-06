// node stills.mjs out_dir nosubs(0/1) t1 t2 ... —— 渲几张静帧看版面（可以不画字幕）
import { chromium } from 'playwright'; import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path'; import url from 'node:url';
const HERE = path.dirname(url.fileURLToPath(import.meta.url)), ROOT = path.join(HERE, '代码工程');
const [out, nosub, ...ts] = process.argv.slice(2); fs.mkdirSync(path.join(HERE, out), { recursive: true });
const MIME = { '.js': 'text/javascript', '.html': 'text/html', '.woff': 'font/woff' };
const srv = http.createServer((q, r) => { const p = path.join(ROOT, decodeURIComponent(q.url.split('?')[0])); if (!fs.existsSync(p)) { r.writeHead(404); r.end(); return; } r.writeHead(200, { 'content-type': MIME[path.extname(p)] || 'application/octet-stream' }); fs.createReadStream(p).pipe(r); }).listen(0);
const br = await chromium.launch(); const pg = await br.newPage({ viewport: { width: 1080, height: 1920 } }); pg.on('pageerror', e => console.log('ERR', e.message));
await pg.goto(`http://127.0.0.1:${srv.address().port}/index.html?render=1&film=${process.env.FILM||"vox"}&w=1080&h=1920`);
await pg.waitForFunction('window.__ready === true || !!window.__bootFailed', null, { timeout: 120000 }); const bf = await pg.evaluate('window.__bootFailed || null'); if (bf) { console.log(bf); process.exit(1); }
if (nosub === '1') await pg.evaluate('window.NO_SUBS = true');
for (const t of ts) { const b64 = await pg.evaluate(async t => { await window.prepare(t); window.renderFrame(t); return window.__canvas.toDataURL('image/png').split(',')[1]; }, +t); fs.writeFileSync(path.join(HERE, out, `t${(+t).toFixed(2)}.png`), Buffer.from(b64, 'base64')); }
await br.close(); srv.close();
