// 波形用的信号：确定性的伪随机比特、带边沿的方波、低通（模拟走线把边沿拖圆）。
// 不用 Math.random()：同一帧每次渲染结果必须一样。

/** PRBS7（x^7 + x^6 + 1），固定种子。周期 127，0 / 1 接近各半，最长连 7 个相同的比特。 */
export const prbs7 = (seed = 0x5a): number[] => {
  let s = seed & 0x7f || 1;
  const out: number[] = [];
  for (let i = 0; i < 127; i++) {
    const bit = ((s >> 6) ^ (s >> 5)) & 1;
    s = ((s << 1) | bit) & 0x7f;
    out.push(bit);
  }
  return out;
};

export const BITS = prbs7();

/** 取第 n 个比特（周期延拓，n 可以是负数） */
export const bitAt = (n: number, bits: number[] = BITS) =>
  bits[((n % bits.length) + bits.length) % bits.length];

const smooth = (x: number) => {
  const s = Math.min(1, Math.max(0, x));
  return s * s * (3 - 2 * s);
};

/**
 * 发送端波形：t 的单位是「一个比特的时长」（UI）。第 n 个比特占 [n, n+1)。
 * edge = 边沿占多少 UI（0.08 ≈ 方正）。返回 0–1。
 */
export const nrz = (t: number, edge: number, bits: number[] = BITS) => {
  const n = Math.floor(t + 0.5); // 最近的比特边界：n−1 和 n 之间
  const a = bitAt(n - 1, bits);
  const b = bitAt(n, bits);
  if (a === b) return a;
  return a + (b - a) * smooth((t - n) / edge + 0.5);
};

/**
 * 从 t0 起取 count 个采样点（每 UI spu 个点）。
 * tau > 0 时经过两级一阶低通（各 tau 个 UI），先预热 12 个 UI 让滤波器进入稳态。
 */
export const sampleWave = (opts: {
  t0: number;
  ui: number;
  spu: number;
  tau: number;
  edge?: number;
  bits?: number[];
}): number[] => {
  const { t0, ui, spu, tau, edge = 0.08, bits = BITS } = opts;
  const n = Math.round(ui * spu) + 1;
  const dt = 1 / spu;
  const out = new Array<number>(n);
  if (tau <= 1e-4) {
    for (let i = 0; i < n; i++) out[i] = nrz(t0 + i * dt, edge, bits);
    return out;
  }
  const a = 1 - Math.exp(-dt / tau);
  const warm = 12 * spu;
  let y1 = nrz(t0 - warm * dt, edge, bits);
  let y2 = y1;
  for (let i = -warm; i < n; i++) {
    const x = nrz(t0 + i * dt, edge, bits);
    y1 += (x - y1) * a;
    y2 += (y1 - y2) * a;
    if (i >= 0) out[i] = y2;
  }
  return out;
};

/**
 * 低通之后，「眼睛」张得最大的判决时刻比比特中心晚多少（UI）。
 * 小 tau 时约等于群时延 2·tau；tau 大了之后按数值扫描的结果拟合（tau 0.3–0.6 时约 0.34 + 0.6·tau）。
 */
export const eyeDelay = (tau: number) => Math.min(2 * tau, 0.34 + 0.6 * tau);

/** 「到达时」最糊的程度：两级低通各 0.57 UI，最坏情况的眼高约剩 13%（快要分不清，但还没完全合上） */
export const TAU_MAX = 0.57;

/** 在采样数组里取 t 时刻的值（线性插值）。数组从 t0 起，每 UI spu 个点。 */
export const valueAt = (
  values: number[],
  t0: number,
  spu: number,
  t: number,
) => {
  const f = (t - t0) * spu;
  const i = Math.max(0, Math.min(values.length - 2, Math.floor(f)));
  const u = Math.max(0, Math.min(1, f - i));
  return values[i] + (values[i + 1] - values[i]) * u;
};

/** 采样点 → SVG 折线路径。v: 0–1；y0 是 v = 0 的位置，y1 是 v = 1 的位置。 */
export const toPath = (
  values: number[],
  x0: number,
  x1: number,
  y0: number,
  y1: number,
) => {
  const n = values.length;
  let d = "";
  for (let i = 0; i < n; i++) {
    const x = x0 + ((x1 - x0) * i) / (n - 1);
    const y = y0 + (y1 - y0) * values[i];
    d += (i === 0 ? "M" : "L") + x.toFixed(1) + " " + y.toFixed(1);
  }
  return d;
};
