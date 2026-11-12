// 读构建前生成的清单（scripts/scan-frames.mjs）：哪些 Blender 帧存在、锚点数据。渲染时不探测文件系统。
import raw from "../generated/manifest.json";
import { W, H } from "../theme";

type AnchorRow = Record<string, [number, number, number, number]>; // [x, y, 深度 z, 是否可见]

type Manifest = {
  generatedFrom: string;
  frames: Record<string, { ext: string; frames: number[] }>;
  anchors: Record<
    string,
    { width: number; height: number; step: number; frames: Record<string, AnchorRow> }
  >;
};

export const MANIFEST = raw as unknown as Manifest;

export const hasFrames = (shotId: string) =>
  (MANIFEST.frames[shotId]?.frames.length ?? 0) > 0;

/** 该镜头里离 film（全片帧号，从 1 起）最近的已有帧；一帧都没有时返回 null */
export const nearestFrameFile = (shotId: string, film: number): string | null => {
  const entry = MANIFEST.frames[shotId];
  if (!entry || entry.frames.length === 0) return null;
  const a = entry.frames;
  let lo = 0;
  let hi = a.length - 1;
  while (lo < hi) {
    const mid = (lo + hi) >> 1;
    if (a[mid] < film) lo = mid + 1;
    else hi = mid;
  }
  const pick = lo > 0 && Math.abs(a[lo - 1] - film) <= Math.abs(a[lo] - film) ? a[lo - 1] : a[lo];
  return `frames/${shotId}/${shotId}_${String(pick).padStart(6, "0")}.${entry.ext}`;
};

export type AnchorPoint = { x: number; y: number; visible: boolean };

const sortedKeysCache: Record<string, number[]> = {};
const sortedFrames = (shotId: string) => {
  if (!sortedKeysCache[shotId]) {
    sortedKeysCache[shotId] = Object.keys(MANIFEST.anchors[shotId].frames)
      .map((k) => parseInt(k, 10))
      .sort((a, b) => a - b);
  }
  return sortedKeysCache[shotId];
};

/**
 * 取某镜头某个锚点在 film（全片帧号）的屏幕坐标。
 * names 按顺序试（第一个存在的生效）。锚点数据隔帧导出（step > 1）时在两帧之间线性插值，超出范围取最近的一帧。
 * 没有这个锚点时返回 null（调用方退到默认位置）。
 */
export const anchorAt = (
  shotId: string,
  names: (string | undefined)[],
  film: number,
): AnchorPoint | null => {
  const data = MANIFEST.anchors[shotId];
  if (!data) return null;
  const frames = sortedFrames(shotId);
  if (frames.length === 0) return null;
  const first = data.frames[String(frames[0])];
  const name = names.find((n) => n !== undefined && first[n] !== undefined);
  if (name === undefined) return null;

  let lo = frames[0];
  let hi = frames[frames.length - 1];
  if (film <= lo) hi = lo;
  else if (film >= hi) lo = hi;
  else {
    for (let i = 0; i < frames.length - 1; i++) {
      if (frames[i] <= film && film <= frames[i + 1]) {
        lo = frames[i];
        hi = frames[i + 1];
        break;
      }
    }
  }
  const a = data.frames[String(lo)][name];
  const b = data.frames[String(hi)][name] ?? a;
  if (!a) return null;
  const u = hi === lo ? 0 : (film - lo) / (hi - lo);
  const sx = W / data.width;
  const sy = H / data.height;
  return {
    x: (a[0] + (b[0] - a[0]) * u) * sx,
    y: (a[1] + (b[1] - a[1]) * u) * sy,
    visible: a[3] === 1 && b[3] === 1,
  };
};

/** 一条标注对应的锚点名候选：anchor_key（若导演写了）→ anchor 字段原文 → 标注文字原文 */
export const anchorNames = (o: { anchor_key?: string; anchor?: string; text: string }) => [
  o.anchor_key,
  o.anchor,
  o.text,
];
