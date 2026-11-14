// 读构建前生成的清单（scripts/scan-frames.mjs）：哪些 Blender 帧存在、锚点数据。渲染时不探测文件系统。
import raw from "../generated/manifest.json";
import { W, H } from "../theme";

type AnchorRow = Record<string, [number, number, number, number]>; // [x, y, 深度 z, 是否可见]

type Manifest = {
  generatedFrom: string;
  frames: Record<string, { ext: string; frames: number[] }>;
  anchors: Record<
    string,
    {
      width: number;
      height: number;
      step: number;
      frames: Record<string, AnchorRow>;
    }
  >;
  audio: {
    narration: string | null; // 整条旁白
    music: string | null;
    lines: Record<string, string>; // 逐句旁白：旁白 id → 文件
  };
};

export const MANIFEST = raw as unknown as Manifest;

export const hasFrames = (shotId: string) =>
  (MANIFEST.frames[shotId]?.frames.length ?? 0) > 0;

/** 该镜头里离 film（全片帧号，从 1 起）最近的已有帧；一帧都没有时返回 null */
export const nearestFrameFile = (
  shotId: string,
  film: number,
): string | null => {
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
  const pick =
    lo > 0 && Math.abs(a[lo - 1] - film) <= Math.abs(a[lo] - film)
      ? a[lo - 1]
      : a[lo];
  return `frames/${shotId}/${shotId}_${String(pick).padStart(6, "0")}.${entry.ext}`;
};

// ---------- 锚点 ----------

/**
 * 一个锚点在某一帧的屏幕位置（1080×1920，左上原点）。
 *   z      相机前方的深度；z ≤ 0 表示在相机背后，这时 x / y 没有意义
 *   front  z > 0
 *   inFrame  在相机前面，而且落在画面内
 */
export type AnchorSample = {
  x: number;
  y: number;
  z: number;
  front: boolean;
  inFrame: boolean;
};

const sortedKeysCache: Record<string, number[]> = {};
const sortedFrames = (shotId: string) => {
  if (!sortedKeysCache[shotId]) {
    sortedKeysCache[shotId] = Object.keys(MANIFEST.anchors[shotId].frames)
      .map((k) => parseInt(k, 10))
      .sort((a, b) => a - b);
  }
  return sortedKeysCache[shotId];
};

const namesCache: Record<string, string[]> = {};
/** 该镜头的 anchors JSON 里有哪些锚点名（没有锚点文件时是空数组） */
export const anchorNameList = (shotId: string): string[] => {
  if (!namesCache[shotId]) {
    const data = MANIFEST.anchors[shotId];
    const set = new Set<string>();
    if (data) {
      // Blender 每一帧都写全部锚点；取首、中、尾三帧的并集就够了，不必扫所有帧
      const fr = sortedFrames(shotId);
      for (const f of [fr[0], fr[fr.length >> 1], fr[fr.length - 1]]) {
        if (f === undefined) continue;
        for (const k of Object.keys(data.frames[String(f)])) set.add(k);
      }
    }
    namesCache[shotId] = [...set];
  }
  return namesCache[shotId];
};

/**
 * 取某镜头某个锚点在 film（全片帧号）的屏幕坐标和深度。没有这个锚点时返回 null。
 * 锚点数据隔帧导出（step > 1）时在两帧之间线性插值；两帧里有一帧在相机背后时不插值，取离得近的那一帧。
 * 超出数据范围取最近的一帧。
 */
export const anchorSample = (
  shotId: string,
  name: string,
  film: number,
): AnchorSample | null => {
  const data = MANIFEST.anchors[shotId];
  if (!data) return null;
  const frames = sortedFrames(shotId);
  if (frames.length === 0) return null;

  // 二分找 film 落在哪两帧之间
  let i = 0;
  let j = frames.length - 1;
  if (film <= frames[0]) j = 0;
  else if (film >= frames[j]) i = j;
  else {
    while (j - i > 1) {
      const mid = (i + j) >> 1;
      if (frames[mid] <= film) i = mid;
      else j = mid;
    }
  }
  const lo = frames[i];
  const hi = frames[j];
  const a = data.frames[String(lo)][name];
  const b = data.frames[String(hi)][name] ?? a;
  if (!a) return null;
  const u = hi === lo ? 0 : (film - lo) / (hi - lo);
  let x: number;
  let y: number;
  let z: number;
  if (hi === lo || a[2] <= 0 || b[2] <= 0) {
    [x, y, z] = u < 0.5 ? a : b;
  } else {
    x = a[0] + (b[0] - a[0]) * u;
    y = a[1] + (b[1] - a[1]) * u;
    z = a[2] + (b[2] - a[2]) * u;
  }
  x *= W / data.width;
  y *= H / data.height;
  const front = z > 0;
  return {
    x,
    y,
    z,
    front,
    inFrame: front && x >= 0 && x <= W && y >= 0 && y <= H,
  };
};

// \s 也包含全角空格
const norm = (s: string) => s.toLowerCase().replace(/\s+/g, "");

/**
 * 一条标注用 anchors JSON 里的哪个锚点。规则（先到先得）：
 *   1. 标注的 anchor_key 字段（时间轴里可选，专门用来指定锚点名）
 *   2. 标注的 anchor 字段原文（例如 "gpu_a"、"大芯片"、"串化电路旁"）
 *   3. 标注的 text 原文
 *   以上先按原文精确比；都没有，再按「不分大小写、去掉空格」各比一遍。
 * 找不到返回 null，调用方退回默认位置。
 * 如果写了 anchor_key 却没找到，同样返回 null（不再去试 anchor / text，免得指到别的东西上）。
 */
export const resolveAnchorName = (
  shotId: string,
  o: { anchor_key?: string; anchor?: string; text: string },
): string | null => {
  const names = anchorNameList(shotId);
  if (names.length === 0) return null;
  const cands = (o.anchor_key ? [o.anchor_key] : [o.anchor, o.text]).filter(
    (c): c is string => typeof c === "string" && c.length > 0,
  );
  for (const c of cands) if (names.includes(c)) return c;
  for (const c of cands) {
    const hit = names.find((n) => norm(n) === norm(c));
    if (hit) return hit;
  }
  return null;
};
