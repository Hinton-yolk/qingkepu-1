import timing from '../timing.json';
import {interpolate, Easing} from 'remotion';

export const FPS = 30;
export const T = timing as unknown as {
  version: string; engine: string; total: number;
  lines: {id: string; seq: string; text: string; start: number; end: number; file: string}[];
  seqs: Record<string, [number, number]>;
};
export const TOTAL_FRAMES = Math.ceil((T.total + 0.12) * FPS);
const byId = Object.fromEntries(T.lines.map((l) => [l.id, l]));
/** 某句旁白开始 / 结束的帧（全片帧号） */
export const cue = (id: string, at: 'start' | 'end' = 'start') => Math.round(byId[id][at] * FPS);
export const sec = (s: number) => Math.round(s * FPS);
export const ease = Easing.bezier(0.33, 0, 0.15, 1);       // 出手快、落位慢
export const easeIO = Easing.bezier(0.6, 0, 0.3, 1);
/** frame 在 [a, a+d] 之间从 0 到 1（夹住、缓动） */
export const prog = (frame: number, a: number, d: number, e = ease) =>
  interpolate(frame, [a, a + Math.max(1, d)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: e});
export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
/** 片段边界：A 从 0 开始；之后每段从这段第一句前 0.35 秒开始，到下一段开始为止 */
export const SEQ_START: Record<string, number> = {
  A: 0,
  B: cue('B1') - sec(0.35),
  C: cue('C1') - sec(0.35),
  D: cue('D1') - sec(0.3),
  E: cue('E1') - sec(0.45),
  F: cue('F1') - sec(0.35),
  G: cue('G1') - sec(0.35),
  H: cue('H1') - sec(0.35),
};
export const SEQ_END: Record<string, number> = {A: SEQ_START.B, B: SEQ_START.C, C: SEQ_START.D, D: SEQ_START.E, E: SEQ_START.F, F: SEQ_START.G, G: SEQ_START.H, H: TOTAL_FRAMES};
