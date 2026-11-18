// 转场重建测试（T2 / T4）共用的 2.5D 空间：一张石墨「桌面」，桌上一块游戏沙盘（小岛）和一块立着的 AI 面板，
// 同一台透视相机、同一个光源方向（terrain.ts 的 LIGHT），阴影落在同一张桌面上。
// 单位：世界单位（小岛海面方板 15 × 15）。屏幕 1080 × 1920，中心 (540, 960)。
import {AMBIENT, buildScene, Cam, dot, LIGHT, project, Tri, V3} from '../lib/terrain';
import {pchip} from '../lib/core';

export const W = 1080, H = 1920;
export const FOV = 0.62;                                   // 垂直视场（弧度）
export const TABLE_Y = -0.6;                               // 桌面高度（沙盘厚 0.55）
export const BOARD = 7.5;                                  // 沙盘半边长（terrain.ts 的海面范围）
// AI 面板：立在桌上，正面朝 +z，宽高比 9:16（正对相机铺满画面时 = 1080 × 1920 的本地坐标）
export const CARD = {x: 6, z: -12, w: 11, h: 11 * 16 / 9};
export const CARD_CY = TABLE_Y + CARD.h / 2;

const sub = (a: V3, b: V3): V3 => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const norm = (a: V3): V3 => { const l = Math.hypot(a[0], a[1], a[2]) || 1; return [a[0] / l, a[1] / l, a[2] / l]; };
const cross = (a: V3, b: V3): V3 => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];

export type View = {eye: V3; fwd: V3; right: V3; up: V3; f: number};
export function view(c: Cam): View {
  const eye: V3 = [c.target[0] + c.dist * Math.cos(c.el) * Math.sin(c.az), c.target[1] + c.dist * Math.sin(c.el), c.target[2] + c.dist * Math.cos(c.el) * Math.cos(c.az)];
  const fwd = norm(sub(c.target, eye)), right = norm(cross(fwd, [0, 1, 0])), up = cross(right, fwd);
  return {eye, fwd, right, up, f: (0.5 * H) / Math.tan(c.fov / 2)};
}
/** 世界点 → 屏幕 [x, y, 深度] */
export function proj(v: View, p: V3): [number, number, number] {
  const d = sub(p, v.eye), z = dot(d, v.fwd);
  return [W / 2 + (dot(d, v.right) * v.f) / z, H / 2 - (dot(d, v.up) * v.f) / z, z];
}
/** 多边形近平面裁剪后投影（桌面这种大面要用） */
export function projPoly(v: View, pts: V3[], near = 0.5): [number, number][] {
  const cz = (p: V3) => dot(sub(p, v.eye), v.fwd);
  const out: V3[] = [];
  for (let i = 0; i < pts.length; i++) {
    const a = pts[i], b = pts[(i + 1) % pts.length], za = cz(a), zb = cz(b);
    if (za >= near) out.push(a);
    if ((za >= near) !== (zb >= near)) {
      const k = (near - za) / (zb - za);
      out.push([a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k, a[2] + (b[2] - a[2]) * k]);
    }
  }
  return out.map((p) => { const q = proj(v, p); return [q[0], q[1]]; });
}
/** 一个世界单位在某点处等于多少屏幕像素 */
export const pxPerUnit = (v: View, p: V3) => v.f / proj(v, p)[2];

// ------------------------------------------------------------------ 沙盘：小岛三角形 + 四个侧面（有厚度，像桌上的一块模型）
const BASE_SIDE: [number, number, number] = [30, 58, 74];
export const ISLAND: Tri[] = (() => {
  const tris = buildScene();
  let id = 100000;
  const quad = (a: V3, b: V3, c: V3, d: V3, n: V3) => {
    tris.push({p: [a, b, c], n, base: BASE_SIDE, kind: 'water', id: id++});
    tris.push({p: [a, c, d], n, base: BASE_SIDE, kind: 'water', id: id++});
  };
  const B = BOARD, t = -0.05, bo = TABLE_Y;
  quad([-B, t, B], [B, t, B], [B, bo, B], [-B, bo, B], [0, 0, 1]);        // 前
  quad([B, t, B], [B, t, -B], [B, bo, -B], [B, bo, B], [1, 0, 0]);         // 右
  quad([-B, t, -B], [-B, t, B], [-B, bo, B], [-B, bo, -B], [-1, 0, 0]);    // 左
  quad([B, t, -B], [-B, t, -B], [-B, bo, -B], [B, bo, -B], [0, 0, -1]);    // 后
  return tris;
})();
export const projectIsland = (c: Cam) => project(ISLAND, c, W, H);

/** 面板四角（左上、右上、右下、左下），朝 +z */
export const cardCorners = (): V3[] => [
  [CARD.x - CARD.w / 2, TABLE_Y + CARD.h, CARD.z], [CARD.x + CARD.w / 2, TABLE_Y + CARD.h, CARD.z],
  [CARD.x + CARD.w / 2, TABLE_Y, CARD.z], [CARD.x - CARD.w / 2, TABLE_Y, CARD.z],
];
/** 面板本地像素（1080 × 1920）→ 世界坐标 */
export const cardLocal = (x: number, y: number, dz = 0): V3 => [CARD.x - CARD.w / 2 + (x / W) * CARD.w, TABLE_Y + CARD.h - (y / H) * CARD.h, CARD.z + dz];
/** 面板正面受光：和小岛用同一个光（环境光 + 漫反射） */
export const CARD_LIGHT = AMBIENT + (1 - AMBIENT) * Math.max(0, dot([0, 0, 1], LIGHT));

/** 阴影：沿光的反方向把物体底面投到桌面上（平行光） */
export function shadowOnTable(pts: V3[]): V3[] {
  return pts.map((p) => { const k = (p[1] - TABLE_Y) / LIGHT[1]; return [p[0] - LIGHT[0] * k, TABLE_Y + 0.001, p[2] - LIGHT[2] * k]; });
}

/** 相机关键帧（片段秒数 → Cam），每个分量用单调三次插值 */
export function camPath(K: number[], tx: number[], ty: number[], tz: number[], dist: number[], el: number[], az: number[]) {
  const f = [tx, ty, tz, dist.map(Math.log), el, az].map((v) => pchip(K, v));
  return (t: number): Cam => ({target: [f[0](t), f[1](t), f[2](t)], dist: Math.exp(f[3](t)), el: f[4](t), az: f[5](t), fov: FOV});
}
