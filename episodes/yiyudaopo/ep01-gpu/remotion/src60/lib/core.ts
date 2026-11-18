// 时间、缓动、插值：整部片子共用（一语道破 EP01 DIRECTOR-LOCKED 60s）
import {Easing, interpolate} from 'remotion';

export const FPS = 30;
export const TOTAL = 1800;                        // 帧 0000–1799
export const S = (sec: number) => Math.round(sec * FPS);
export const clamp = (x: number, a = 0, b = 1) => Math.max(a, Math.min(b, x));
export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

// 三种缓动，按动作的意思选，不是每个动作都 ease-in-out：
export const settle = Easing.bezier(0.2, 0.7, 0.2, 1);     // 落位：出手快、慢慢停（物体到位、字出现）
export const glide = Easing.bezier(0.45, 0, 0.25, 1);      // 镜头：起步和停下都柔（推拉摇）
export const launch = Easing.bezier(0.55, 0, 0.9, 0.6);    // 出发：慢起、越走越快（被吸走、离场）
export const linear = (t: number) => t;

/** t 秒（片子时间）在 [a, a+d] 内 0→1 */
export const prog = (t: number, a: number, d: number, e: (x: number) => number = settle) =>
  interpolate(t, [a, a + Math.max(1e-3, d)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: e});
/** 出现 a→a+d，消失 b→b+d2 */
export const win = (t: number, a: number, d: number, b: number, d2: number) => prog(t, a, d) * (1 - prog(t, b, d2, glide));

/** 单调三次 Hermite（和 Blender 端 dl60_scenes.py 的 pchip 完全同一个公式，两边的相机曲线才能接上） */
export function pchip(xs: number[], ys: number[]) {
  const n = xs.length;
  const h = xs.slice(0, -1).map((x, i) => xs[i + 1] - x);
  const d = h.map((hi, i) => (ys[i + 1] - ys[i]) / hi);
  const m = new Array(n).fill(0);
  m[0] = d[0]; m[n - 1] = d[n - 2];
  for (let i = 1; i < n - 1; i++) {
    if (d[i - 1] * d[i] <= 0) m[i] = 0;
    else {
      const w1 = 2 * h[i] + h[i - 1], w2 = h[i] + 2 * h[i - 1];
      m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i]);
    }
  }
  return (x: number) => {
    if (x <= xs[0]) return ys[0];
    if (x >= xs[n - 1]) return ys[n - 1];
    let i = 0;
    while (i < n - 2 && xs[i + 1] <= x) i++;
    const t = (x - xs[i]) / h[i], t2 = t * t, t3 = t2 * t;
    return (2 * t3 - 3 * t2 + 1) * ys[i] + (t3 - 2 * t2 + t) * h[i] * m[i] + (-2 * t3 + 3 * t2) * ys[i + 1] + (t3 - t2) * h[i] * m[i + 1];
  };
}

/** 两点之间的弧线（出发点、到达点、往上鼓多少），给「输入 / 输出」小点和飞行的方块用 */
export const arc = (a: [number, number], b: [number, number], k: number, bulge = 0): [number, number] => [
  lerp(a[0], b[0], k),
  lerp(a[1], b[1], k) - bulge * 4 * k * (1 - k),
];

/** 方块的计算循环：starts 里每个时刻开始一次「灌满（dur 秒）→ 亮一下 → 回到常亮」 */
export function cycle(t: number, starts: number[], dur: number, rest = 0.45): {fill: number; lit: number} {
  let s = -1, prev = false;
  for (const a of starts) { if (a <= t) { if (s >= 0) prev = true; s = a; } }
  if (s < 0) return {fill: 0, lit: 0};
  if (t < s + dur) return {fill: (t - s) / dur, lit: prev ? rest : 0};
  return {fill: 0, lit: rest + (1 - rest) * Math.exp(-(t - s - dur) / 0.7)};
}
