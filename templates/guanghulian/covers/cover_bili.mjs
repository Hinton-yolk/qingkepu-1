// node cover_bili.mjs <spec.json> —— B站横屏封面：用片子自己的引擎（横屏版 ep1b）画背景，右边是片中的机制卡片，左边压三行标题标签。
// 画布 1920×1080（16:9 版直接用）；B站投稿要 4:3，从中间裁 1440×1080 再缩到 1200×900。很多地方按 16:9 显示 4:3 封面（上下会被裁），
// 所以标题和卡片都放在 x 240–1680、y 135–945 这一块里（4:3 的中间 16:9）。
import { chromium } from 'playwright'; import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const spec = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const ROOT = spec.root;
const MIME = { '.js': 'text/javascript', '.html': 'text/html', '.woff': 'font/woff', '.json': 'application/json', '.png': 'image/png' };
const srv = http.createServer((q, r) => { const p = path.join(ROOT, decodeURIComponent(q.url.split('?')[0])); if (!fs.existsSync(p)) { r.writeHead(404); r.end(); return; }
  r.writeHead(200, { 'content-type': MIME[path.extname(p)] || 'application/octet-stream' }); fs.createReadStream(p).pipe(r); }).listen(0);
const br = await chromium.launch(); const pg = await br.newPage({ viewport: { width: 1920, height: 1080 } }); pg.on('pageerror', e => console.log('ERR', e.message));
await pg.goto(`http://127.0.0.1:${srv.address().port}/index.html?render=1&film=${spec.film}&w=1920&h=1080`);
await pg.waitForFunction('window.__ready === true || !!window.__bootFailed', null, { timeout: 120000 });
const bf = await pg.evaluate('window.__bootFailed || null'); if (bf) { console.log(bf); process.exit(1); }
const b64 = await pg.evaluate(async (S) => {
  window.NO_HUD = true; window.SHOW_SUBS = false; window.CAM_OVERRIDE = S.cam; await window.prepare(S.t); window.renderFrame(S.t);
  const c = window.__canvas.getContext('2d'), W = 1920, H = 1080;
  // 左半边铺一层桌面色，把后面的纸条压淡（往右渐隐到卡片前）
  const off = document.createElement('canvas'); off.width = S.washTo + 160; off.height = H; const og = off.getContext('2d');
  og.fillStyle = og.createPattern(CL.paperTile('desk', '#e4ddcf', { amt: 12, grain: 10, fibers: 320, seed: 5 }), 'repeat'); og.fillRect(0, 0, off.width, H);
  const g = og.createLinearGradient(0, 0, off.width, 0); g.addColorStop(0, 'rgba(0,0,0,1)'); g.addColorStop(S.washTo / off.width, 'rgba(0,0,0,1)'); g.addColorStop(1, 'rgba(0,0,0,0)');
  og.globalCompositeOperation = 'destination-in'; og.fillStyle = g; og.fillRect(0, 0, off.width, H); c.drawImage(off, 0, 0);
  // 上下两条也铺桌面色，把卡片上下露出来的纸条压掉（4:3 封面上下这两条是看得见的）
  for (const [y0, y1, up] of [[0, S.topWash, true], [S.botWash, H, false]]) {
    const o2 = document.createElement('canvas'); o2.width = W; o2.height = y1 - y0; const q = o2.getContext('2d');
    q.fillStyle = q.createPattern(CL.paperTile('desk', '#e4ddcf', { amt: 12, grain: 10, fibers: 320, seed: 5 }), 'repeat'); q.fillRect(0, 0, W, o2.height);
    const gg = q.createLinearGradient(0, 0, 0, o2.height); gg.addColorStop(up ? 0.7 : 0, up ? 'rgba(0,0,0,1)' : 'rgba(0,0,0,0)'); gg.addColorStop(up ? 1 : 0.3, up ? 'rgba(0,0,0,0)' : 'rgba(0,0,0,1)');
    q.globalCompositeOperation = 'destination-in'; q.fillStyle = gg; q.fillRect(0, 0, W, o2.height); c.drawImage(o2, 0, y0); }
  const X = S.x;
  MD.label(c, S.tag, X, S.tagY, { size: 40, fam: 'PuHui-Heavy', align: 'left', bg: '#b8433f', fg: '#f6efe4', r: -0.02 });
  S.lines.forEach((L, i) => {
    const y = S.lineY[i], cream = !!L.kw;
    MD.label(c, L.text, X, y, { size: S.size, fam: 'PuHui-Black', align: 'left', bg: cream ? '#f3efe5' : undefined, fg: cream ? '#1b1b1a' : undefined, r: L.r || 0 });
    if (!cream) return;
    // 关键词上扫一道荧光笔（和片子里的划重点一样，multiply 压在字下）
    c.save(); c.translate(X, y); c.rotate(L.r || 0); c.font = `${S.size}px "PuHui-Black"`;
    const padX = S.size * 0.42, k0 = L.text.indexOf(L.kw), x0 = padX + c.measureText(L.text.slice(0, k0)).width, kw = c.measureText(L.kw).width, s = S.size;
    c.globalCompositeOperation = 'multiply'; c.fillStyle = 'rgba(222,208,20,.9)'; c.beginPath(); c.moveTo(x0 - 6, -s * 0.52);
    for (let k = 0; k <= 12; k++) c.lineTo(x0 - 6 + (kw + 12) * k / 12, -s * 0.52 + Math.sin(k * 1.7) * 3);
    for (let k = 12; k >= 0; k--) c.lineTo(x0 - 6 + (kw + 12) * k / 12, s * 0.5 + Math.sin(k * 2.3) * 3);
    c.closePath(); c.fill(); c.restore(); });
  MD.label(c, S.sub, X, S.subY, { size: 42, fam: 'PuHui-Heavy', align: 'left', r: -0.01 });
  return window.__canvas.toDataURL('image/png').split(',')[1];
}, spec);
fs.writeFileSync(spec.out, Buffer.from(b64, 'base64')); await br.close(); srv.close(); console.log('wrote', spec.out);
