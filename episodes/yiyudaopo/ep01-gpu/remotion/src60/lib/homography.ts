// 矩形 → 任意四边形的投影变换（单应）。用来把 2D 图层精确贴到 3D 底片里芯片的四个角上。
export type P = [number, number];
export type Quad = [P, P, P, P];          // 左上、右上、右下、左下（屏幕像素）

type H = {a: number; b: number; c: number; d: number; e: number; f: number; g: number; h: number};

function unitToQuad(q: Quad): H {
  const [[x0, y0], [x1, y1], [x2, y2], [x3, y3]] = q;
  const dx1 = x1 - x2, dx2 = x3 - x2, dx3 = x0 - x1 + x2 - x3;
  const dy1 = y1 - y2, dy2 = y3 - y2, dy3 = y0 - y1 + y2 - y3;
  const den = dx1 * dy2 - dx2 * dy1;
  const g = (dx3 * dy2 - dx2 * dy3) / den;
  const h = (dx1 * dy3 - dx3 * dy1) / den;
  return {a: x1 - x0 + g * x1, b: x3 - x0 + h * x3, c: x0, d: y1 - y0 + g * y1, e: y3 - y0 + h * y3, f: y0, g, h};
}

/** CSS matrix3d：把 w×h 的 div（transform-origin 0 0）贴到四边形 q 上 */
export function matrix3d(w: number, h: number, q: Quad): string {
  const m = unitToQuad(q);
  const v = [m.a / w, m.d / w, 0, m.g / w, m.b / h, m.e / h, 0, m.h / h, 0, 0, 1, 0, m.c, m.f, 0, 1];
  return `matrix3d(${v.map((x) => x.toFixed(9)).join(',')})`;
}

/** 本地坐标 (x, y)（在 w×h 的矩形里）→ 屏幕坐标 */
export function mapPoint(w: number, h: number, q: Quad, x: number, y: number): P {
  const m = unitToQuad(q);
  const u = x / w, v = y / h;
  const z = m.g * u + m.h * v + 1;
  return [(m.a * u + m.b * v + m.c) / z, (m.d * u + m.e * v + m.f) / z];
}

export const lerpQuad = (a: Quad, b: Quad, t: number): Quad =>
  a.map((p, i) => [p[0] + (b[i][0] - p[0]) * t, p[1] + (b[i][1] - p[1]) * t]) as Quad;

export const rectQuad = (x: number, y: number, w: number, h: number): Quad => [[x, y], [x + w, y], [x + w, y + h], [x, y + h]];

/** 四边形的「局部比例」：上下边平均宽 / 本地宽 */
export const quadScale = (q: Quad, w: number) => (Math.hypot(q[1][0] - q[0][0], q[1][1] - q[0][1]) + Math.hypot(q[2][0] - q[3][0], q[2][1] - q[3][1])) / 2 / w;
