// common.mjs — shared bits for the EP.01 style frames (same moment in every style).
export const W = 1080, H = 1920;
export const COPY = {
  head: "AI 怎么[读]字？",
  cap: "要先把它切成一块一块的“积木”",
  tool: "分词器（示意）",
  aiSees: "AI 看到的（示意）",
  src: "切法和编号：GPT-4 分词器实测",
  pieces: [["str", "#496"], ["aw", "#675"], ["berry", "#15717"]],
};
export const F = (w, s) => `${w} ${s}px NS, "Noto Sans CJK SC", sans-serif`;
export const FI = (w, s) => `${w} ${s}px IN, NS, "Noto Sans CJK SC", sans-serif`;
export async function fonts() {
  await Promise.all([F(500, 40), F(700, 40), F(900, 40)].map((f) => document.fonts.load(f, "字")).concat([document.fonts.load(FI(800, 40), "a"), document.fonts.load(`900 40px "Noto Sans CJK SC"`, "关")]));
}
export function rr(c, x, y, w, h, r) { c.beginPath(); c.roundRect(x, y, w, h, r); }
export function tw(c, s, font) { c.save(); c.font = font; const w = c.measureText(s).width; c.restore(); return w; }
export function txt(c, s, x, y, o = {}) {
  c.save(); c.font = o.font || F(700, 40); c.fillStyle = o.color || "#1C1B22"; c.textAlign = o.align || "center"; c.textBaseline = "middle";
  c.globalAlpha *= o.alpha ?? 1; c.fillText(s, x, y); c.restore();
}
// [word] in the highlight colour
export function rich(c, s, x, y, font, color, hl, align = "center") {
  const parts = []; s.replace(/\[([^\]]+)\]|([^\[]+)/g, (m, h, n) => parts.push(h ? [h, hl] : [n, color]));
  c.save(); c.font = font; c.textBaseline = "middle"; c.textAlign = "left";
  const total = parts.reduce((w, p) => w + c.measureText(p[0]).width, 0);
  let cx = align === "center" ? x - total / 2 : x;
  for (const [str, col] of parts) { c.fillStyle = col; c.fillText(str, cx, y); cx += c.measureText(str).width; }
  c.restore(); return total;
}
export function mulberry(seed) { return function () { seed |= 0; seed = (seed + 0x6d2b79f5) | 0; let x = Math.imul(seed ^ (seed >>> 15), 1 | seed); x = (x + Math.imul(x ^ (x >>> 7), 61 | x)) ^ x; return ((x ^ (x >>> 14)) >>> 0) / 4294967296; }; }
