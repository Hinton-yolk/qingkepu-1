// shots.mjs — re-render frames from the films with a custom camera (no captions), and report anchor points.
import { createRequire } from "node:module";
import path from "node:path";
import fs from "node:fs";
const { chromium } = createRequire(import.meta.url)("playwright");
const JOBS = [
  // film, out name, t, camera (null = the film's own), anchor point in world coords for the leader line
  ["../../../episodes/weishenme/01-tuoluoyi", "ep01-hero-dy", 0.5, "key([0, 0], [470, 1150], 0.98, -36)", "CHIP"],
  ["../../../episodes/weishenme/01-tuoluoyi", "ep01-hero-xhs", 0.5, "key([0, 0], [470, 880], 0.84, -36)", "CHIP"],
  ["../../../episodes/weishenme/01-tuoluoyi", "ep01-inset", 24.6, null, null],
  ["../../../episodes/weishenme/02-weibolu", "ep02-hero-dy", 1.4, "key([-5, 0], [540, 1170], 1.12)", "bowlW(bowlAt(1.4), [0, -25])"],
  ["../../../episodes/weishenme/02-weibolu", "ep02-hero-xhs", 1.4, "key([-5, 0], [540, 930], 1.12)", "bowlW(bowlAt(1.4), [0, -25])"],
  ["../../../episodes/weishenme/02-weibolu", "ep02-inset", 4.2, null, null],
  ["../../../episodes/weishenme/03-jiangzaoerji", "ep03-hero-dy", 3.6, "key([9, -10], [560, 1180], 0.92)", "[13, 0]"],
  ["../../../episodes/weishenme/03-jiangzaoerji", "ep03-hero-xhs", 3.6, "key([9, -10], [560, 900], 0.8)", "[13, 0]"],
  ["../../../episodes/weishenme/03-jiangzaoerji", "ep03-inset", 28.6, null, null],
  ["../../../episodes/weishenme/04-chupingshoutao", "ep04-hero-dy", 1.6, "key([0, 4], [460, 1150], 1.15)", "P"],
  ["../../../episodes/weishenme/04-chupingshoutao", "ep04-hero-xhs", 1.6, "key([0, 4], [470, 900], 0.98)", "P"],
  ["../../../episodes/weishenme/04-chupingshoutao", "ep04-inset", 26.9, null, null]   // the glove: the charges stop at the fabric,
];
const ONLY = process.argv[2];                                   // node shots.mjs ep04 → only the jobs whose name starts with ep04
const browser = await chromium.launch();
const anchors = fs.existsSync("art/anchors.json") ? JSON.parse(fs.readFileSync("art/anchors.json", "utf8")) : {};   // merge, keep the other episodes
for (const [dir, name, t, camExpr, anchor] of JOBS.filter((j) => !ONLY || j[1].startsWith(ONLY))) {
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.goto("file://" + path.resolve(dir, "index.html"));
  await page.waitForFunction(() => window.ready === true);
  const a = await page.evaluate(({ t, camExpr, anchor }) => {
    window.textBand = () => {}; window.endCard = () => {};
    if (typeof window.hookOverlays === "function") window.hookOverlays = () => {};
    if (typeof window.darkOverlays === "function") window.darkOverlays = () => {};
    if (typeof window.microOverlays === "function") window.microOverlays = () => {};
    if (camExpr) { const K = eval(camExpr); window.cam = () => K; }
    if (camExpr && typeof window.sweeping === "function" && typeof window.drawPhone === "function") {
      // EP.01: the phone half seen through — the board above an orange scan line, the screen below it
      window.layers = () => [[-80, -6, "real"], [-6, 80, "screen"]]; window.sweeping = () => true;
    }
    if (typeof window.frame === "function") frame(t); else window.seek(t);   // one sharp frame, no motion blur
    if (!anchor) return null;
    if (typeof window.toS !== "function") window.toS = (K, p) => proj(K, p[0], p[1], p[2] || 0);   // EP.04 on: the camera is proj()
    const p = toS(cam(t), eval(anchor)); return [Math.round(p[0]), Math.round(p[1])];
  }, { t, camExpr, anchor });
  await page.locator("#c").screenshot({ path: `art/${name}.png` });
  anchors[name] = a; await page.close();
}
await browser.close();
fs.writeFileSync("art/anchors.json", JSON.stringify(anchors, null, 1));
console.log(anchors);
