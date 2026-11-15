// 颜色、字体、安全区。颜色只取 timeline.json 的 colors；这里不新增任何色相，只做透明度变化。
import { TL } from "./timeline";

/** 字体名常量：预览用系统里的文泉驿正黑；以后换成系列字体（思源黑体等）只改这一处。 */
export const FONT_FAMILY =
  '"WenQuanYi Zen Hei", "Noto Sans SC", "Source Han Sans SC", "Microsoft YaHei", sans-serif';

export const C = {
  electric: TL.colors.electric, // 金 = 电
  light: TL.colors.light, // 青 = 光
  alert: TL.colors.alert, // 珊瑚 = 出错 / 强调
  ink: TL.colors.ink, // 深色底
  cream: TL.colors.cream, // 奶油色字
};

/** #RRGGBB + 透明度 → rgba() */
export const rgba = (hex: string, a: number) => {
  const h = hex.replace("#", "");
  const n = parseInt(h.length === 3 ? h.replace(/(.)/g, "$1$1") : h, 16);
  return `rgba(${(n >> 16) & 255}, ${(n >> 8) & 255}, ${n & 255}, ${a})`;
};

export const W = TL.meta.width;
export const H = TL.meta.height;

const sz = TL.meta.safe_zone;
const SIDE = 60; // 左右各留 60 px

export const SAFE = {
  left: SIDE,
  right: W - SIDE,
  width: W - SIDE * 2,
  top: sz.content_top, // 标签、波形等内容区上沿
  bottom: sz.content_bottom, // 内容区下沿
  stationY: sz.station_bar_y, // 五站条
  subtitleY: sz.subtitle_y, // 字幕
};

/** 角注占内容区最下面一条；图表面板的下沿留在它上面（角注叠得更高时面板再往上让，见 lib/shotLayout） */
export const NOTE_BAND = 88;
export const PANEL_BOTTOM = SAFE.bottom - NOTE_BAND;

/**
 * 字号（1080 宽）。预演是 540 宽，所以压在画面上的字都按「缩一半还读得出」定：
 *   五站条 ≥ 34；贴物体的标签主行 ≥ 34、副行 ≥ 28；角注 ≥ 26；路线上的「电 / 光」44。
 * 层级参照 Style Bible 现稿，待用户确认后再统一调。
 */
export const SIZE = {
  hookMain: 112,
  hookLead: 68,
  labelHead: 38,
  labelBody: 30,
  term: 42,
  labelHeadMin: 34, // 太长要缩字时的下限；再放不下就折两行
  labelBodyMin: 28,
  pathChar: 44,
  panelLabel: 29,
  panelSmall: 24,
  note: 28,
  subtitle: 48,
  station: 36,
};

/** 深色衬底的不透明度：压在亮画面（机房地面、铜色芯片）上也要读得清 */
export const BACKING = {
  chip: 0.8, // 标签、路线上的字
  note: 0.72, // 角注
  subtitle: 0.72, // 字幕条
  station: 0.7, // 五站条
  hook: 0.56, // 开头大字后面的暗垫
};

/** 文字压在 3D 画面上时的暗色晕边（不是辉光：只为在亮画面上也读得清） */
export const TEXT_SHADOW = [
  `0 0 3px ${rgba(TL.colors.ink, 1)}`,
  `0 0 8px ${rgba(TL.colors.ink, 0.95)}`,
  `0 0 18px ${rgba(TL.colors.ink, 0.75)}`,
  `0 2px 4px ${rgba(TL.colors.ink, 0.9)}`,
].join(", ");

/** 已经有衬底的字用的轻晕边 */
export const TEXT_SHADOW_SOFT = `0 1px 3px ${rgba(TL.colors.ink, 0.9)}`;

/** 深色描边（8 个方向的硬阴影）：大字压在亮地面上用。px = 描边宽度 */
export const outlineShadow = (px: number, alpha = 0.95) => {
  const c = rgba(TL.colors.ink, alpha);
  const d = Math.round(px * 0.7071 * 10) / 10;
  return [
    `${px}px 0 0 ${c}`,
    `-${px}px 0 0 ${c}`,
    `0 ${px}px 0 ${c}`,
    `0 -${px}px 0 ${c}`,
    `${d}px ${d}px 0 ${c}`,
    `-${d}px ${d}px 0 ${c}`,
    `${d}px -${d}px 0 ${c}`,
    `-${d}px -${d}px 0 ${c}`,
  ].join(", ");
};

export const CLAMP = {
  extrapolateLeft: "clamp",
  extrapolateRight: "clamp",
} as const;
