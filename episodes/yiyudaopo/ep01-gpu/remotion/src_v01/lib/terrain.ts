// B 段的「游戏画面」：一个程序生成的低多边形小岛（地形 + 树 + 水面），用真正的透视投影和
// 漫反射光照（亮度 ∝ n·l）画出来。屏幕上演示的那道「乘、乘、乘、再相加」就是这里给每个三角形算亮度的公式。
export type V3 = [number, number, number];
export type Tri = {p: [V3, V3, V3]; n: V3; base: [number, number, number]; kind: 'land' | 'water' | 'tree'; id: number};

export const LIGHT: V3 = [0.48, 0.8, 0.36]; // 单位向量：0.48² + 0.8² + 0.36² = 1
export const AMBIENT = 0.24;

const sub = (a: V3, b: V3): V3 => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const cross = (a: V3, b: V3): V3 => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const norm = (a: V3): V3 => {
  const l = Math.hypot(a[0], a[1], a[2]) || 1;
  return [a[0] / l, a[1] / l, a[2] / l];
};
export const dot = (a: V3, b: V3) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];

const hex = (h: string): [number, number, number] => [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)];
const COL = {
  water: hex('#2D5F78'), sand: hex('#C8B07A'), grass: hex('#5F8A3C'), grass2: hex('#4E7A34'),
  rock: hex('#7D766C'), snow: hex('#E6E3DC'), trunk: hex('#5A4632'), leaf: hex('#3F6E32'),
};

function height(x: number, z: number) {
  const r = Math.hypot(x, z * 1.15);
  const island = Math.max(0, 1 - Math.pow(r / 4.6, 2.2));
  const h =
    2.9 * Math.exp(-((x + 0.6) ** 2 + (z - 0.4) ** 2) / 2.2) +
    1.4 * Math.exp(-((x - 1.9) ** 2 + (z + 1.2) ** 2) / 1.3) +
    0.35 * Math.sin(x * 1.7 + 0.4) * Math.cos(z * 1.3) +
    0.18 * Math.sin(x * 3.1 - z * 2.3);
  return h * island + island * 0.55 - 0.35;
}

export function buildScene(): Tri[] {
  const tris: Tri[] = [];
  const N = 30, S = 7.5;
  const P = (i: number, j: number): V3 => {
    const x = -S + (2 * S * i) / N, z = -S + (2 * S * j) / N;
    return [x, Math.max(height(x, z), -0.05), z];
  };
  let id = 0;
  const push = (a: V3, b: V3, c: V3, kind: Tri['kind'], base?: [number, number, number]) => {
    let n = norm(cross(sub(b, a), sub(c, a)));
    if (n[1] < 0) n = [-n[0], -n[1], -n[2]];
    const hy = (a[1] + b[1] + c[1]) / 3;
    let col = base;
    if (!col) {
      if (hy < 0.0) col = COL.water;
      else if (hy < 0.22) col = COL.sand;
      else if (hy < 1.5) col = (id % 3 === 0 ? COL.grass2 : COL.grass);
      else if (hy < 2.3) col = COL.rock;
      else col = COL.snow;
      if (hy >= 0.22 && hy < 1.5 && n[1] < 0.72) col = COL.rock;
    }
    tris.push({p: [a, b, c], n, base: col, kind: hy < 0 && kind === 'land' ? 'water' : kind, id: id++});
  };
  for (let i = 0; i < N; i++)
    for (let j = 0; j < N; j++) {
      const a = P(i, j), b = P(i + 1, j), c = P(i + 1, j + 1), d = P(i, j + 1);
      if ((i + j) % 2) { push(a, b, c, 'land'); push(a, c, d, 'land'); }
      else { push(a, b, d, 'land'); push(b, c, d, 'land'); }
    }
  // 树：低多边形圆锥，放在草地上
  let seed = 11;
  const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  let trees = 0;
  for (let k = 0; k < 400 && trees < 22; k++) {
    const x = -3.4 + rnd() * 6.8, z = -3.4 + rnd() * 6.8, y = height(x, z);
    if (y < 0.35 || y > 1.35) continue;
    trees++;
    const hgt = 0.7 + rnd() * 0.5, rad = 0.26 + rnd() * 0.12, sides = 6;
    const top: V3 = [x, y + hgt + 0.18, z];
    for (let s = 0; s < sides; s++) {
      const a0 = (s / sides) * Math.PI * 2, a1 = ((s + 1) / sides) * Math.PI * 2;
      const p0: V3 = [x + Math.cos(a0) * rad, y + 0.18, z + Math.sin(a0) * rad];
      const p1: V3 = [x + Math.cos(a1) * rad, y + 0.18, z + Math.sin(a1) * rad];
      let n = norm(cross(sub(p1, p0), sub(top, p0)));
      if (dot(n, [Math.cos((a0 + a1) / 2), 0, Math.sin((a0 + a1) / 2)]) < 0) n = [-n[0], -n[1], -n[2]];
      tris.push({p: [p0, p1, top], n, base: COL.leaf, kind: 'tree', id: id++});
    }
  }
  return tris;
}

export type Cam = {az: number; el: number; dist: number; fov: number; target: V3};
export type Proj = {pts: [number, number][]; depth: number; tri: Tri; shade: number; facing: boolean};

/** 透视投影到视口（w×h 像素），返回按远近排好序（远的先画）的三角形 */
export function project(tris: Tri[], cam: Cam, w: number, h: number): Proj[] {
  const eye: V3 = [
    cam.target[0] + cam.dist * Math.cos(cam.el) * Math.sin(cam.az),
    cam.target[1] + cam.dist * Math.sin(cam.el),
    cam.target[2] + cam.dist * Math.cos(cam.el) * Math.cos(cam.az),
  ];
  const fwd = norm(sub(cam.target, eye));
  const right = norm(cross(fwd, [0, 1, 0]));
  const up = cross(right, fwd);
  const f = (0.5 * h) / Math.tan(cam.fov / 2);
  const out: Proj[] = [];
  for (const t of tris) {
    let depth = 0;
    const pts = t.p.map((p) => {
      const d = sub(p, eye);
      const z = dot(d, fwd);
      depth += z;
      return [w / 2 + (dot(d, right) * f) / z, h / 2 - (dot(d, up) * f) / z] as [number, number];
    });
    const c: V3 = [(t.p[0][0] + t.p[1][0] + t.p[2][0]) / 3, (t.p[0][1] + t.p[1][1] + t.p[2][1]) / 3, (t.p[0][2] + t.p[1][2] + t.p[2][2]) / 3];
    const facing = dot(t.n, sub(eye, c)) > 0;
    out.push({pts, depth: depth / 3, tri: t, shade: Math.max(0, dot(t.n, LIGHT)), facing});
  }
  out.sort((a, b) => b.depth - a.depth);
  return out;
}

export const shadeColor = (base: [number, number, number], diffuse: number, k = 1) => {
  const s = (AMBIENT + (1 - AMBIENT) * diffuse) * k;
  return `rgb(${Math.round(base[0] * s)},${Math.round(base[1] * s)},${Math.round(base[2] * s)})`;
};
export const area = (p: [number, number][]) => Math.abs((p[1][0] - p[0][0]) * (p[2][1] - p[0][1]) - (p[2][0] - p[0][0]) * (p[1][1] - p[0][1])) / 2;
