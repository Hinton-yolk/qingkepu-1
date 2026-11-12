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

/** 角注占内容区最下面一条；图表面板的下沿留在它上面 */
export const NOTE_BAND = 88;
export const PANEL_BOTTOM = SAFE.bottom - NOTE_BAND;

/** 字号（1080 宽）。参照 Style Bible 现稿的层级，待用户确认后再统一调。 */
export const SIZE = {
  hookMain: 112,
  hookLead: 80,
  labelHead: 40,
  labelBody: 31,
  term: 44,
  panelLabel: 29,
  panelSmall: 24,
  note: 27,
  subtitle: 48,
  station: 28,
};

/** 文字压在 3D 画面上时的暗色晕边（不是辉光：只为在亮画面上也读得清） */
export const TEXT_SHADOW = [
  `0 0 3px ${rgba(TL.colors.ink, 1)}`,
  `0 0 8px ${rgba(TL.colors.ink, 0.95)}`,
  `0 0 18px ${rgba(TL.colors.ink, 0.75)}`,
  `0 2px 4px ${rgba(TL.colors.ink, 0.9)}`,
].join(", ");

export const CLAMP = {
  extrapolateLeft: "clamp",
  extrapolateRight: "clamp",
} as const;
