// node cover.mjs <spec.json> —— 用片子自己的引擎画封面：背景是片中某一刻的桌面（指定相机、不画进度条），上面压标题标签。
// 输出 1080×1920（抖音）；小红书 3:4 由 make_covers.py 从中间裁 1080×1440（y 240–1680），所以标题和主体都放在这个范围里。
import { chromium } from 'playwright'; import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const spec = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const ROOT = spec.root;
const MIME = { '.js': 'text/javascript', '.html': 'text/html', '.woff': 'font/woff', '.json': 'application/json', '.png': 'image/png' };
const srv = http.createServer((q, r) => { const p = path.join(ROOT, decodeURIComponent(q.url.split('?')[0])); if (!fs.existsSync(p)) { r.writeHead(404); r.end(); return; }
  r.writeHead(200, { 'content-type': MIME[path.extname(p)] || 'application/octet-stream' }); fs.createReadStream(p).pipe(r); }).listen(0);
const br = await chromium.launch(); const pg = await br.newPage({ viewport: { width: 1080, height: 1920 } }); pg.on('pageerror', e => console.log('ERR', e.message));
await pg.goto(`http://127.0.0.1:${srv.address().port}/index.html?render=1&film=${spec.film}&w=1080&h=1920`);
await pg.waitForFunction('window.__ready === true || !!window.__bootFailed', null, { timeout: 120000 });
const bf = await pg.evaluate('window.__bootFailed || null'); if (bf) { console.log(bf); process.exit(1); }
const b64 = await pg.evaluate(async (S) => {
  window.NO_HUD = true; window.CAM_OVERRIDE = S.cam; await window.prepare(S.t); window.renderFrame(S.t);
  const c = window.__canvas.getContext('2d'), W = 1080;
  // 标题区：铺一层桌面色，把后面的纸条压淡（往下渐隐）
  const off = document.createElement('canvas'); off.width = W; off.height = S.washTo + 90; const og = off.getContext('2d');
  og.fillStyle = og.createPattern(CL.paperTile('desk', '#e4ddcf', { amt: 12, grain: 10, fibers: 320, seed: 5 }), 'repeat'); og.fillRect(0, 0, W, off.height);
  const g = og.createLinearGradient(0, 0, 0, off.height); g.addColorStop(0, 'rgba(0,0,0,1)'); g.addColorStop(S.washTo / off.height, 'rgba(0,0,0,1)'); g.addColorStop(1, 'rgba(0,0,0,0)');
  og.globalCompositeOperation = 'destination-in'; og.fillStyle = g; og.fillRect(0, 0, W, off.height); c.drawImage(off, 0, 0);
  MD.label(c, S.tag, 540, S.tagY, { size: 44, fam: 'PuHui-Heavy', align: 'center', bg: '#b8433f', fg: '#f6efe4', r: -0.02 });
  MD.label(c, S.l1, 540, S.l1Y, { size: S.size, fam: 'PuHui-Black', align: 'center', r: -0.015 });
  // 第二行：米白纸条＋荧光笔扫过关键词（和片子里的划重点一样，multiply 压在字下）
  const S2 = S.size2 || S.size;   // 第二行可以比第一行小（第二行字多时）
  MD.label(c, S.l2, 540, S.l2Y, { size: S2, fam: 'PuHui-Black', align: 'center', bg: '#f3efe5', fg: '#1b1b1a', r: 0.012 });
  c.save(); c.translate(540, S.l2Y); c.rotate(0.012); c.font = `${S2}px "PuHui-Black"`;
  const tw = c.measureText(S.l2).width, padX = S2 * 0.42, w = Math.round(tw + padX * 2), i = S.l2.indexOf(S.kw);
  const x0 = -w / 2 + padX + c.measureText(S.l2.slice(0, i)).width, kw = c.measureText(S.kw).width;
  c.globalCompositeOperation = 'multiply'; c.fillStyle = 'rgba(222,208,20,.9)'; c.beginPath(); c.moveTo(x0 - 6, -S2 * 0.52);
  for (let k = 0; k <= 12; k++) c.lineTo(x0 - 6 + (kw + 12) * k / 12, -S2 * 0.52 + Math.sin(k * 1.7) * 3);
  for (let k = 12; k >= 0; k--) c.lineTo(x0 - 6 + (kw + 12) * k / 12, S2 * 0.5 + Math.sin(k * 2.3) * 3);
  c.closePath(); c.fill(); c.restore();
  MD.label(c, S.sub, 540, S.subY, { size: 52, fam: 'PuHui-Heavy', align: 'center', r: -0.01 });
  return window.__canvas.toDataURL('image/png').split(',')[1];
}, spec);
fs.writeFileSync(spec.out, Buffer.from(b64, 'base64')); await br.close(); srv.close(); console.log('wrote', spec.out);
