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
  ["../../../episodes/weishenme/04-chupingshoutao", "ep04-inset", 26.9, null, null],  // the glove: the charges stop at the fabric
  ["../../../episodes/weishenme/05-tizhicheng", "ep05-hero-dy", 2.4, "key([0, -20, 120], [540, 1230], 2.2, 50)", "CALF"],
  ["../../../episodes/weishenme/05-tizhicheng", "ep05-hero-xhs", 2.4, "key([0, -20, 120], [540, 930], 1.9, 50)", "CALF"],
  ["../../../episodes/weishenme/05-tizhicheng", "ep05-inset", 17.6, null, null],   // the calf cut the anchor points at: fat ring outside, muscle inside
  ["../../../episodes/weishenme/06-renlianjiesuo", "ep06-hero", 1.9, null, null],     // her profile, lipstick on, the phone unlocking (no drift); anchor set in make.mjs
  ["../../../episodes/weishenme/06-renlianjiesuo", "ep06-mask", 44.6, null, null],     // the closing: the mask on (for the second, small inset)
  ["../../../episodes/weishenme/06-renlianjiesuo", "ep06-inset", 13.0, null, null],   // the dots and the lines of equal height on the face
  ["../../../episodes/weishenme/07-shoubiaolvguang", "ep07-hero", 0.6, null, null],   // fingertips hold the watch back-up over the wrist: the green lights
  ["../../../episodes/weishenme/07-shoubiaolvguang", "ep07-inset", 10.0, null, null],  // the section (v7.2 timing): green light into the skin, the blood eats it
  ["../../../episodes/weishenme/08-chongdian", "ep08-hero", 0.6, null, null],          // the hand plugs the cable into the phone, ⚡37%
  ["../../../episodes/weishenme/08-chongdian", "ep08-inset", 23.6, null, null],        // the two bars: 现在的电量 | 累计用掉的电 (two halves = one)
  ["../../../episodes/weishenme/09-xueyaji", "ep09-hero", 2.5, null, null],            // INTERNAL time (frame(t)): the arm in the cuff, 第一次 138 | 第二次 126
  ["../../../episodes/weishenme/09-xueyaji", "ep09-inset", 30.9, null, null],          // internal 30.9 = film 28.9: the hill, 高压 / 低压 (about here)
];
const ONLY = process.argv[2];                                   // node shots.mjs ep04 → only the jobs whose name starts with ep04
const browser = await chromium.launch();
const anchors = fs.existsSync("art/anchors.json") ? JSON.parse(fs.readFileSync("art/anchors.json", "utf8")) : {};   // merge, keep the other episodes
for (const [dir, name, t, camExpr, anchor] of JOBS.filter((j) => !ONLY || j[1].startsWith(ONLY))) {
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.goto("file://" + path.resolve(dir, "index.html"));
  await page.waitForFunction(() => window.ready === true);
  const a = await page.evaluate(({ t, camExpr, anchor, name }) => {
    window.textBand = () => {}; window.endCard = () => {};
    if (typeof window.hookOverlays === "function") window.hookOverlays = () => {};
    if (typeof window.darkOverlays === "function") window.darkOverlays = () => {};
    if (typeof window.microOverlays === "function") window.microOverlays = () => {};
    for (const f of ["displayMag", "calfMag"]) if (typeof window[f] === "function") window[f] = () => {};   // EP.05: no in-film magnifiers on the cover art
    if (name.startsWith("ep05") && typeof window.overlays === "function") window.overlays = () => {};   // EP.05 inset: no label leaders cut off by the circle
    if (typeof window.driftZ === "function") window.driftZ = () => ({ s: 1, tx: 0, ty: 0 });   // EP.06: no drift on the cover art
    if (typeof window.tag === "function" && name.startsWith("ep06")) window.tag = () => {};          // EP.06: no small tags on the cover art
    if (name === "ep07-inset") { for (const f of ["overlays", "spotlight", "drawCard"]) if (typeof window[f] === "function") window[f] = () => {}; }   // EP.07 inset: the light and the vessel only (no frames, tags or card)
    if (name === "ep08-inset") { window.pill = () => {}; window.label = () => {}; }   // EP.08 inset: the two bars only (no small text cut by the circle)
    if (name === "ep09-hero") { window.againNote = () => {}; const K = key([540, 1000], [560, 980], 0.86); window.roomK = () => K; }   // EP.09: no small note; a wider shot (the film's own camera is very close)
    if (name === "ep09-inset") { window.label = () => {}; }                            // EP.09 inset: the hill and its two tags (the 示意 line would be cut)
    if (camExpr) { const K = eval(camExpr); window.cam = () => K; }
    if (camExpr && typeof window.sweeping === "function" && typeof window.drawPhone === "function") {
      // EP.01: the phone half seen through — the board above an orange scan line, the screen below it
      window.layers = () => [[-80, -6, "real"], [-6, 80, "screen"]]; window.sweeping = () => true;
    }
    if (typeof window.frame === "function") frame(t); else window.seek(t);   // one sharp frame, no motion blur
    if (!anchor) return null;
    if (typeof window.toS !== "function") window.toS = (K, p) => proj(K, p[0], p[1], p[2] || 0);   // EP.04 on: the camera is proj()
    const p = toS(cam(t), eval(anchor)); return [Math.round(p[0]), Math.round(p[1])];
  }, { t, camExpr, anchor, name });
  await page.locator("#c").screenshot({ path: `art/${name}.png` });
  anchors[name] = a; await page.close();
}
await browser.close();
fs.writeFileSync("art/anchors.json", JSON.stringify(anchors, null, 1));
console.log(anchors);
