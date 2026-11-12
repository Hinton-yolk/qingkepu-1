// 唯一的时间来源：../timeline/timeline.json（相对路径导入，改了 JSON 重新渲染 / 刷新预览就生效）。
// 这里只做类型和「秒 → 帧」的换算，不保存任何镜头时间或文案。
import raw from "../../timeline/timeline.json";

export type OverlayType =
  | "hook_title"
  | "path_trace"
  | "label"
  | "term"
  | "scale"
  | "alert"
  | "note"
  | "waveform"
  | "timing_diagram"
  | "gauge"
  | "end_card";

export type Overlay = {
  t: number; // 全片时间（秒）
  dur: number; // 持续（秒）
  type: OverlayType | string;
  text: string;
  anchor?: string; // 导演写的锚点说明；也用作 anchors JSON 的锚点名（见 lib/anchors.ts）
  anchor_key?: string; // 可选：明确指定 anchors JSON 里的锚点名
};

export type Shot = {
  id: string;
  name: string;
  start: number;
  end: number;
  station: string | null;
  scale: string;
  blender: string | null;
  status: string;
  camera: string;
  transition_out: string;
  purpose: string;
  overlays: Overlay[];
};

export type Station = { id: string; name: string; tech: string };

export type Narration = {
  id: string;
  shot: string;
  start: number;
  end: number;
  text: string;
  slow?: boolean;
};

export type Timeline = {
  meta: {
    title: string;
    series: string;
    fps: number;
    width: number;
    height: number;
    version: string;
    status: string;
    safe_zone: {
      station_bar_y: number;
      subtitle_y: number;
      content_top: number;
      content_bottom: number;
    };
  };
  stations: Station[];
  colors: {
    electric: string;
    light: string;
    alert: string;
    ink: string;
    cream: string;
  };
  shots: Shot[];
  narration: Narration[];
};

export const TL = raw as unknown as Timeline;

export const FPS = TL.meta.fps;

/** 全片时间（秒）→ Remotion 帧号（从 0 起）。Blender 的全片帧号 = 这个值 + 1。 */
export const toFrame = (sec: number) => Math.round(sec * FPS);

/** 一段时长（秒）→ 帧数，至少 1 帧 */
export const durFrames = (t: number, dur: number) =>
  Math.max(1, toFrame(t + dur) - toFrame(t));

export const TOTAL_FRAMES = toFrame(TL.shots[TL.shots.length - 1].end);

export const shotFrames = (shot: Shot) => ({
  from: toFrame(shot.start),
  duration: Math.max(1, toFrame(shot.end) - toFrame(shot.start)),
});

export const stationById = (id: string | null) =>
  TL.stations.find((s) => s.id === id) ?? null;
