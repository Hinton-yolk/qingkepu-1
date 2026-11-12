// 按镜头给的版式配置：只有「放哪里、画哪种」，没有时间和文案。
// 时间、文字、颜色都从 timeline.json 来；这里的键是镜头号，时间轴里没有的镜头号不会被用到。
import { PANEL_BOTTOM, SAFE, W } from "./theme";

// ---------- 图表面板（波形 / 时序图 / 读数） ----------
export type WaveformVariant = "degrade" | "restore" | "eo";

/**
 * waveform 在各镜头画哪一种：
 *   degrade  同一段比特，出发方正 → 到达圆钝，眼图由开到合（电的路）
 *   restore  左糊右清两条（DSP 两侧）
 *   eo       上金（电信号）下青（光强）对齐
 * 没写的镜头按 degrade。
 */
export const WAVEFORM_VARIANT: Record<string, WaveformVariant> = {
  S04: "degrade",
  S05: "restore",
  S06: "eo",
};

export const PANEL_HEIGHT = {
  degrade: 428,
  restore: 250,
  eo: 330,
  timing_diagram: 428,
  gauge: 340,
} as const;

export const panelRect = (h: number) => ({
  x: SAFE.left,
  y: PANEL_BOTTOM - h,
  w: SAFE.width,
  h,
});

/** 时序图里并行线画几条（3D 里示意画 32 条；手机上 8 条才看得清，导演可改） */
export const TIMING_LANES = 8;
/** 时序图一共演示几拍（几组数据） */
export const TIMING_WORDS = 4;

/** 耦合读数：高斯模场半径 w（µm）。来源：FACTS.md F11（模场直径 9.2 µm 的一半） */
export const MODE_FIELD_RADIUS_UM = 4.6;
/** 文案里解析不出偏移量时的后备值（µm） */
export const GAUGE_OFFSETS_FALLBACK_UM = [2, 5];

// ---------- 贴物体的短标签（label / term / scale / alert） ----------
export type LabelSlot = {
  x: number;
  y: number;
  side: "left" | "right"; // 文字往锚点的哪一侧伸
  vert: "up" | "down"; // 文字在锚点的上方还是下方
};

/**
 * 没有 anchors JSON 时的默认锚点位置（屏幕坐标）。按镜头里「贴物体的标签」出现的先后顺序取用，
 * 用完后循环。两个槽一左一右、一高一低，同时出现两条标签也不会叠在一起。
 */
export const DEFAULT_SLOTS: LabelSlot[] = [
  { x: 250, y: 712, side: "right", vert: "up" },
  { x: 830, y: 680, side: "left", vert: "down" },
];

/** 个别镜头单独指定（顺序 = 该镜头里贴物体标签的先后）。有 anchors JSON 后这些都不再使用。 */
export const SHOT_SLOTS: Record<string, LabelSlot[]> = {
  S01: [{ x: W / 2 - 120, y: 860, side: "right", vert: "up" }],
};

/** 标签引线：从锚点斜着引出多远 */
export const LEADER = { dx: 64, dy: 72 };

/**
 * scale 类标注在分镜里写的是「3D 立体字（Blender 内）」。
 * 该镜头已有 Blender 帧时，Remotion 不再重复画；只有占位卡时才画出来顶位置。
 */
export const SCALE_ONLY_WHEN_PLACEHOLDER = true;

// ---------- 五站条 ----------
/** 每一站用哪种信号色：电 = 金，光 = 青，换乘 = 金到青。键是 stations[].id */
export const STATION_SIGNAL: Record<string, "electric" | "light" | "both"> = {
  st1: "electric",
  st2: "electric",
  st3: "both",
  st4: "light",
  st5: "both",
};

/** path_trace 没有锚点时，几个站名沿一条浅弧线排开的默认位置 */
export const pathTraceDefault = (i: number, n: number) => {
  const u = n <= 1 ? 0.5 : i / (n - 1);
  return {
    x: SAFE.left + 90 + u * (SAFE.width - 180),
    y: 760 - 70 * Math.sin(Math.PI * u),
  };
};
