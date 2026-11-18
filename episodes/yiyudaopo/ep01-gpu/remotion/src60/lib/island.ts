// SHOT 02 的游戏场景：复用 Pilot 的低多边形小岛（terrain.ts），把地形按 1.5 × 1.5 的方格分成「地块」。
// 每个地块的亮度用同一条规则算（漫反射，亮度 ∝ n·l）——画面上只演「算 → 变亮」，不显示公式。
import {clamp, lerp, pchip} from './core';
import {buildScene, Cam, V3, dot} from './terrain';
import {PANEL, T} from './plan';

export const TRIS = buildScene();
export const VPW = PANEL.w, VPH = PANEL.h;
const CELL = 1.5, ORIGIN = -4.5, N = 6;

export type Patch = {id: number; ix: number; iz: number; c: V3; tris: number[]; ring: number; order: number};
const cellOf = (x: number, z: number) => {
  const ix = Math.floor((x - ORIGIN) / CELL), iz = Math.floor((z - ORIGIN) / CELL);
  return ix >= 0 && ix < N && iz >= 0 && iz < N ? [ix, iz] : null;
};
export const triPatch: number[] = new Array(TRIS.length).fill(-1);
export const PATCHES: Patch[] = (() => {
  const acc = new Map<number, {sum: V3; n: number; tris: number[]}>();
  TRIS.forEach((t, i) => {
    const cx = (t.p[0][0] + t.p[1][0] + t.p[2][0]) / 3, cy = (t.p[0][1] + t.p[1][1] + t.p[2][1]) / 3, cz = (t.p[0][2] + t.p[1][2] + t.p[2][2]) / 3;
    if (t.kind === 'water') return;
    const c = cellOf(cx, cz);
    if (!c) return;
    const k = c[0] * N + c[1];
    const a = acc.get(k) ?? {sum: [0, 0, 0] as V3, n: 0, tris: []};
    a.tris.push(i);
    if (t.kind === 'land') { a.sum = [a.sum[0] + cx, a.sum[1] + cy, a.sum[2] + cz]; a.n++; }
    acc.set(k, a);
  });
  const out: Patch[] = [];
  acc.forEach((a, k) => {
    if (a.n < 10) return;
    const c: V3 = [a.sum[0] / a.n, a.sum[1] / a.n, a.sum[2] / a.n];
    if (c[1] < 0.12) return;
    out.push({id: out.length, ix: Math.floor(k / N), iz: k % N, c, tris: a.tris, ring: 0, order: 0});
  });
  return out;
})();
// 被选中的地块：岛的前坡、画面中下部，草地
export const SEL = PATCHES.reduce((best, p) => (Math.hypot(p.c[0] - 0.6, p.c[2] - 1.9) < Math.hypot(best.c[0] - 0.6, best.c[2] - 1.9) ? p : best), PATCHES[0]).id;
PATCHES.forEach((p) => { p.ring = Math.hypot(p.ix - PATCHES[SEL].ix, p.iz - PATCHES[SEL].iz); });
[...PATCHES].sort((a, b) => a.ring - b.ring).forEach((p, i) => { p.order = i; });
PATCHES.forEach((p) => p.tris.forEach((i) => { triPatch[i] = p.id; }));

// ------------------------------------------------------------------ 岛上的相机：5–8 秒全景 → 8–11 秒推向选中的地块 → 11–14 秒拉回、露出所有地块 → 之后定住
const K = [5.0, 8.0, 9.7, 11.0, 12.5, 14.0];
const distf = pchip(K, [13.6, 13.2, 9.6, 9.4, 13.4, 13.7]);
const elf = pchip(K, [0.50, 0.52, 0.58, 0.58, 0.54, 0.54]);
const tk = pchip(K, [0, 0, 1, 1, 0, 0]);
export const islandCam = (t: number): Cam => {
  const tt = clamp(t, 4.0, 14.2);
  const s = tk(tt), pc = PATCHES[SEL].c;
  return {az: 0.24 + 0.17 * clamp((tt - 4.0) / 10.2), el: elf(tt), dist: distf(tt), fov: 0.70,
    target: [lerp(0.15, pc[0], s), lerp(0.45, pc[1], s), lerp(0, pc[2], s)]};
};

/** 投影一个 3D 点到视口本地像素，返回 [x, y, 深度] */
export function projectPoint(cam: Cam, p: V3): [number, number, number] {
  const eye: V3 = [cam.target[0] + cam.dist * Math.cos(cam.el) * Math.sin(cam.az), cam.target[1] + cam.dist * Math.sin(cam.el), cam.target[2] + cam.dist * Math.cos(cam.el) * Math.cos(cam.az)];
  const sub = (a: V3, b: V3): V3 => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
  const norm = (a: V3): V3 => { const l = Math.hypot(...a) || 1; return [a[0] / l, a[1] / l, a[2] / l]; };
  const cross = (a: V3, b: V3): V3 => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
  const fwd = norm(sub(cam.target, eye)), right = norm(cross(fwd, [0, 1, 0])), up = cross(right, fwd);
  const f = (0.5 * VPH) / Math.tan(cam.fov / 2);
  const d = sub(p, eye), z = dot(d, fwd);
  return [VPW / 2 + (dot(d, right) * f) / z, VPH / 2 - (dot(d, up) * f) / z, z];
}
export const focalPx = (cam: Cam) => (0.5 * VPH) / Math.tan(cam.fov / 2);

/** 地块边界沿地形起伏的一圈点（给琥珀色描边） */
export function patchOutline(cam: Cam, p: Patch): [number, number][] {
  const x0 = ORIGIN + p.ix * CELL, z0 = ORIGIN + p.iz * CELL, pts: [number, number][] = [];
  const h = (x: number, z: number) => {
    // 取最近三角形顶点的高度（足够贴地）
    let best = 0, bd = 1e9;
    for (const i of p.tris) for (const v of TRIS[i].p) { const dd = (v[0] - x) ** 2 + (v[2] - z) ** 2; if (dd < bd) { bd = dd; best = v[1]; } }
    return Math.max(best, 0) + 0.04;
  };
  const ring: [number, number][] = [];
  const M = 6;
  for (let k = 0; k < M; k++) ring.push([x0 + (CELL * k) / M, z0]);
  for (let k = 0; k < M; k++) ring.push([x0 + CELL, z0 + (CELL * k) / M]);
  for (let k = 0; k < M; k++) ring.push([x0 + CELL - (CELL * k) / M, z0 + CELL]);
  for (let k = 0; k < M; k++) ring.push([x0, z0 + CELL - (CELL * k) / M]);
  for (const [x, z] of ring) { const q = projectPoint(cam, [x, h(x, z), z]); pts.push([q[0], q[1]]); }
  return pts;
}

// 时间线上的地块状态：1 = 算过光照（有明暗），0 = 还没算（平涂、暗）
export const patchLit = (t: number, p: Patch) => {
  const k = (a: number, d: number) => clamp((t - a) / d);
  if (p.id === SEL) return 1 - k(T.drain1, 0.4) + k(T.lit1, 0.3);
  return 1 - k(T.drainAll + p.ring * 0.04, 0.35) + k(T.litAll, 0.3);
};
