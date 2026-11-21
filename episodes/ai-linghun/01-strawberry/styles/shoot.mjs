// shoot.mjs — style frames for EP.01 (one 1080×1920 still per style, same moment: strawberry just cut into str / aw / berry).
//   node shoot.mjs [s1-paper s2-clay ...]     -> out/<name>.png, plus out/compare.jpg
import { createRequire } from "node:module";
import { execFileSync } from "node:child_process";
import http from "node:http"; import fs from "node:fs"; import path from "node:path"; import { fileURLToPath } from "node:url";
const HERE = path.dirname(fileURLToPath(import.meta.url)), ROOT = path.dirname(HERE);
const { chromium } = createRequire(import.meta.url)("playwright");
const TYPES = { ".html": "text/html", ".js": "text/javascript", ".mjs": "text/javascript", ".woff": "font/woff", ".json": "application/json", ".png": "image/png" };
const srv = http.createServer((q, s) => {
  const f = path.join(ROOT, decodeURIComponent(q.url.split("?")[0]));
  if (!f.startsWith(ROOT) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { s.writeHead(404); s.end(); return; }
  s.writeHead(200, { "content-type": TYPES[path.extname(f)] || "application/octet-stream" }); fs.createReadStream(f).pipe(s);
}).listen(0, "127.0.0.1");
await new Promise((r) => srv.on("listening", r));
const all = ["s3-pixel", "s4-glass", "s1-paper", "s2-clay"];
const names = process.argv.slice(2).length ? process.argv.slice(2) : all;
fs.mkdirSync(path.join(HERE, "out"), { recursive: true });
const browser = await chromium.launch({ args: ["--font-render-hinting=none", "--ignore-gpu-blocklist"] });
for (const n of names) {
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  const errs = []; page.on("pageerror", (e) => errs.push(String(e))); page.on("console", (m) => { if (m.type() === "error") errs.push(m.text()); });
  await page.goto(`http://127.0.0.1:${srv.address().port}/styles/${n}.html`);
  try { await page.waitForFunction(() => window.ready === true, null, { timeout: 90000 }); } catch (e) { console.log(n, "not ready", errs); }
  if (errs.length) console.log(n, "errors:", errs.join("\n"));
  await page.locator("#c").screenshot({ path: path.join(HERE, "out", n + ".png") });
  console.log("shot", n); await page.close();
}
await browser.close(); srv.close();
const have = all.filter((n) => fs.existsSync(path.join(HERE, "out", n + ".png")));
if (have.length > 1) execFileSync("ffmpeg", ["-v", "error", "-y", ...have.flatMap((n) => ["-i", path.join(HERE, "out", n + ".png")]), "-filter_complex", `${have.map((_, i) => `[${i}]`).join("")}hstack=${have.length},scale=${540 * have.length}:-1`, "-q:v", "3", path.join(HERE, "out", "compare.jpg")]);
