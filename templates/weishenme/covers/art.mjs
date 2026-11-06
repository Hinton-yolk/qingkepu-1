// art.mjs — clean frames from the films (no captions, no end card) for the covers.
//   node art.mjs <film dir> <name> t1,t2,... [keepHook]
import { createRequire } from "node:module";
import path from "node:path";
const { chromium } = createRequire(import.meta.url)("playwright");
const [dir, name, times, keepHook] = process.argv.slice(2);
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
await page.goto("file://" + path.resolve(dir, "index.html"));
await page.waitForFunction(() => window.ready === true);
await page.evaluate((keep) => {
  window.textBand = () => {}; window.endCard = () => {};
  if (!keep && typeof window.hookOverlays === "function") window.hookOverlays = () => {};
  if (typeof window.darkOverlays === "function") window.darkOverlays = () => {};
}, keepHook === "hook");
for (const t of times.split(",").map(Number)) {
  await page.evaluate((tt) => window.seek(tt), t);
  await page.locator("#c").screenshot({ path: `art/${name}-${t.toFixed(2)}.png` });
}
await browser.close();
console.log("ok", name);
