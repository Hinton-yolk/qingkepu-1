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

/** 图表面板的位置。bottom 默认在角注带上面；同时在场的角注叠得更高时由 lib/shotLayout 往上让 */
export const panelRect = (h: number, bottom: number = PANEL_BOTTOM) => ({
  x: SAFE.left,
  y: bottom - h,
  w: SAFE.width,
  h,
});

/**
 * 时序图里并行线画几条（3D 里示意画 32 条；手机上 8 条才看得清，待导演定）。
 * 条数会写进图里并行那一行标题后面的小字（strings.ts 的 timingLanes），免得和 3D 画面对不上。
 */
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
 * 标注在 anchors JSON 里找不到对应锚点时的默认位置（屏幕坐标）。按镜头里「贴物体的标签」出现的先后顺序取用，
 * 用完后循环。两个槽一左一右、一高一低。退回默认位置的标签只有衬底和字，不画引线（它没有指着任何东西）。
 */
export const DEFAULT_SLOTS: LabelSlot[] = [
  { x: 250, y: 800, side: "right", vert: "up" },
  { x: 830, y: 690, side: "left", vert: "down" },
];

/** 个别镜头单独指定（顺序 = 该镜头里贴物体标签的先后）。现在没有哪个镜头需要。 */
export const SHOT_SLOTS: Record<string, LabelSlot[]> = {};

/** 标签和锚点之间留多远（标签停在锚点旁边，不挡住它） */
export const LABEL_GAP = {
  dx: 40, // 斜向摆放：横向间距
  dy: 36, // 斜向摆放：纵向间距
  v: 52, // 正上 / 正下
  h: 60, // 正左 / 正右
  clear: 20, // 标签边框离锚点至少这么远
};

/** 同一时刻最多几个贴物体的标签（多出来的、开始得晚的不画；scan 时会提示） */
export const MAX_LABELS = 3;

/**
 * 锚点出画以后标签怎么办：
 *   刚出画（离画面边不到 LABEL_NEAR_MARGIN）：标签留着，停在离锚点最近的画面内位置，不画引线；
 *   出得更远、或转到相机背后：停在最后的位置，用 LABEL_LOST_FADE 帧淡出，不跟着乱飞。
 */
export const LABEL_NEAR_MARGIN = 120;
export const LABEL_LOST_FADE = 8;

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

// ---------- 开头大字 ----------
/**
 * hook_title 占的区域（屏幕坐标）。大字固定在这里；它在场时，标签和路线上的字都让开这一块。
 * 位置：走廊地面上、角注带上面；左右各收进 140 px，让出两侧机柜上的 GPU 锚点。
 */
export const HOOK_BOX = { x: 140, y: 984, w: W - 280, h: 240 };

// ---------- 路线（path_trace） ----------
/**
 * 路线图：沿 anchors JSON 里的取样点画一条 2D 折线。
 *   锚点名  path_<段>_<两位以上的序号>，序号沿 A → B 递增。
 *           段名以 e 开头 = 电（金），以 o 开头 = 光（青）；先后顺序见 sectionOrder，表里没有的段按名字排在后面。
 *   例：path_e1_00 … path_e1_07，path_o_00 … path_o_23，path_e2_00 … path_e2_05
 */
export const PATH_TRACE = {
  sectionOrder: ["e1", "o", "e2"],
  drawSeconds: 2.7, // 标注开始后多久从 A 端画到 B 端
  lineWidth: 6,
  outlineWidth: 11, // 深色描边（垫在彩线下面）
  dash: [16, 16], // 虚线：这是把被机柜挡住的段补全的「路线图」，不是 3D 里的实物
  charGap: 54, // 「电 / 光」离线多远
};

/** 路线文案里的字 → 信号色（「电 → 光 → 电」；旧写法「金（电）→ 青（光）」也认） */
export const SIGNAL_WORDS: Record<string, "electric" | "light"> = {
  电: "electric",
  金: "electric",
  光: "light",
  青: "light",
};
