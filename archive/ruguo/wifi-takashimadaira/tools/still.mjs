// node tools/still.mjs "<query>" <outdir> <prefix> t1 t2 …  — final-quality stills without the 30 s screenshot timeout
import fs from 'fs'; import path from 'path';
const { openDemo, closeServer } = await import(path.join(process.env.LIB || '/root/lemo-opuscar', 'core/render/page.mjs'));
const [q, out, pre, ...ts] = process.argv.slice(2); fs.mkdirSync(out, { recursive: true });
const { browser, page } = await openDemo(path.dirname(path.dirname(new URL(import.meta.url).pathname)), { w: 1080, h: 1920, q });
for (const t of ts) { await page.evaluate(t => window.seek(t), +t); fs.writeFileSync(path.join(out, `${pre}${t}.png`), await page.screenshot({ type: 'png', timeout: 0 })); console.log(pre + t); }
await browser.close(); closeServer();
