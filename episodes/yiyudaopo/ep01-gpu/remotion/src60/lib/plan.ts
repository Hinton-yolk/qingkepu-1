// 导演锁定版 60 秒的「世界」：所有 2D 元素放在同一张世界平面上，一台虚拟相机在上面推、跟、拉。
// 片子从头到尾就是这台相机的一条连续路径 + 首尾两段 Blender 底片（同一块芯片）。
import {clamp, glide, lerp, pchip, prog} from './core';
import {mapPoint, matrix3d, Quad, rectQuad} from './homography';
import OPEN from '../anchors/OPEN.json';
import CLOSE from '../anchors/CLOSE.json';

// ------------------------------------------------------------------ 关键时间（秒）
export const T = {
  // SHOT 01
  q1: 0.35, q2: 1.5, qOut: 4.05,
  reveal: 4.35,                 // 芯片方框里开始长出游戏视口
  morph: 4.65,                  // 视口从贴在芯片上 → 摆正成正面的窗口（1.0 秒）
  // SHOT 02
  sel: 6.3, drain1: 7.4, tile1: 8.05, in1: 8.6, comp1: 9.15, out1: 9.85, lit1: 10.2,
  pull: 10.8, drainAll: 11.25, tilesAll: 11.35, cue: 12.2, compAll: 12.6, outAll: 13.1, litAll: 13.4,
  lift: 14.0, fly0: 14.3, fly1: 16.9, pan0: 14.5, pan1: 17.1,
  // SHOT 03
  type0: 16.15, split: 17.4, nums: 18.15, select: 20.0, center: 20.8, params: 22.35,
  f1: 23.55, f2: 24.0, prod: 25.15, sum: 26.05, contract: 27.0, row2: 28.8,
  // SHOT 04
  op2: 30.4, both: 33.0, rows: 36.2, all: 37.6, pullAI: 39.0,
  // SHOT 05
  act1: 42.3, act2: 43.25, act3: 44.4, reveal5: 44.0, fadeOld: 45.2, dieIn: 45.3, stream0: 45.6, lock: 48.5,
  plateIn: 48.5, plateFull: 50.3,
  // SHOT 06
  g1: 51.3, g2: 52.1, g3: 52.9, recede: 54.0, ansQ: 56.6, ansA: 57.2, sig: 58.5, black: 59.72,
};

// ------------------------------------------------------------------ 世界里的三个区域（世界坐标，单位 = 相机 z=1 时的屏幕像素）
export const PANEL = {cx: 540, cy: 960, w: 960, h: 1144};          // 游戏视口（宽高比 = 芯片 26:31）
export const AI0 = {x: 1700, y: 1550};                               // AI 区：相机 z=1 对准这里时，屏幕坐标 = AI 局部坐标
export const aiToWorld = (x: number, y: number): [number, number] => [AI0.x + x - 540, AI0.y + y - 960];
export const panelToWorld = (x: number, y: number): [number, number] => [PANEL.cx - PANEL.w / 2 + x, PANEL.cy - PANEL.h / 2 + y];
export const DIE = {cx: 1100, cy: 3020, w: 800, h: 954};              // 芯片「计算区」叠加层（26 × 31 mm，1 mm = 30.77 px）
export const MM = DIE.w / 26;

// ------------------------------------------------------------------ Blender 底片的逐帧锚点
type AF = {f: number; die: Quad; hbm: Quad[]; subs: Quad};
const OF = (OPEN as unknown as {frames: AF[]}).frames;
const CF = (CLOSE as unknown as {frames: AF[]}).frames;
export const OPEN_F0 = 0, OPEN_F1 = OF.length - 1;
export const CLOSE_F0 = (CLOSE as unknown as {f0: number}).f0;
export const openAnchor = (f: number) => OF[Math.max(0, Math.min(OF.length - 1, f))];
export const closeAnchor = (f: number) => CF[Math.max(0, Math.min(CF.length - 1, f - CLOSE_F0))];

// CLOSE 镜头屏幕上的芯片宽度（像素）：和 dl60_scenes.py 的 DIEW_K / DIEW_V 一字不差
const DIEW_K = [45.0, 48.5, 51.0, 52.2, 54.0, 57.0, 60.0];
const DIEW_V = [250.0, 430.0, 610.0, 628.0, 640.0, 440.0, 425.0];
const dieWlog = pchip(DIEW_K, DIEW_V.map(Math.log));
export const dieWidth = (t: number) => Math.exp(dieWlog(t));

// ------------------------------------------------------------------ 虚拟相机（世界 → 屏幕）
const zLock = dieWidth(T.lock) / DIE.w;
const cyLock = DIE.cy - (1010 - 960) / zLock;                          // CLOSE 起点：芯片中心在屏幕 y = 1010
const zK = [4.3, 6.8, 14.5, 17.1, 18.6, 39.0, 42.0, 45.0, 46.2, 48.5, 49.2];
const zV = [0.905, 1.0, 1.0, 1.0, 1.012, 1.11, 0.47, 0.43, 0.375, zLock, dieWidth(49.2) / DIE.w];
const zf = pchip(zK, zV.map(Math.log));
// 17–39 秒：镜头随着算式往下长、慢慢靠近（Approach），不是原地不动，也不是随机晃
const cK = [16.9, 26.0, 39.0, 42.0, 45.0, 46.2, 48.5];
const cxf = pchip(cK, [AI0.x, AI0.x - 25, AI0.x - 10, 1100, 1100, 1150, DIE.cx]);
const cyf = pchip(cK, [AI0.y, AI0.y + 20, AI0.y + 110, 1450, 1460, 2050, cyLock]);
// SHOT 02 → 03：镜头「跟着」被选中的方块横移。方块先留在屏幕上差不多的位置（世界从它身后滑走），
// 最后一秒多才滑到 AI 区的停靠位，镜头同时落定。FLY.start 由 Game.tsx 在载入时填上（方块起飞时的世界坐标）。
export const FLY = {start: [540, 960] as [number, number]};
export const DOCK_LOCAL: [number, number] = [830, 830];
export const carrierWorld = (t: number): [number, number] => {
  const a = FLY.start, b = aiToWorld(DOCK_LOCAL[0], DOCK_LOCAL[1]);
  const k = prog(t, T.fly0, T.fly1 - T.fly0, glide);
  return [lerp(a[0], b[0], k), lerp(a[1], b[1], k) - 140 * 4 * k * (1 - k)];
};
export type Cam = {cx: number; cy: number; z: number};
export const camAt = (t: number): Cam => {
  if (t <= T.fly0) return {cx: 540, cy: 960, z: Math.exp(zf(t))};
  if (t < T.fly1) {
    const p = carrierWorld(t), m = prog(t, 15.6, T.fly1 - 15.6, glide);
    const off0 = [FLY.start[0] - 540, FLY.start[1] - 960], off1 = [DOCK_LOCAL[0] - 540, DOCK_LOCAL[1] - 960];
    return {cx: p[0] - lerp(off0[0], off1[0], m), cy: p[1] - lerp(off0[1], off1[1], m), z: Math.exp(zf(t))};
  }
  return {cx: cxf(t), cy: cyf(t), z: Math.exp(zf(t))};
};
export const w2s = (c: Cam, x: number, y: number): [number, number] => [540 + (x - c.cx) * c.z, 960 + (y - c.cy) * c.z];
export const worldTransform = (c: Cam) => `translate(${540 - c.cx * c.z}px, ${960 - c.cy * c.z}px) scale(${c.z})`;

// ------------------------------------------------------------------ 游戏视口在屏幕上的四边形
// 4.35 秒起贴在芯片四角（单应），4.65–5.65 秒摆正成世界里的正面窗口
export const panelQuad = (t: number, f: number): Quad => {
  const c = camAt(t);
  const [x0, y0] = w2s(c, PANEL.cx - PANEL.w / 2, PANEL.cy - PANEL.h / 2);
  const rect = rectQuad(x0, y0, PANEL.w * c.z, PANEL.h * c.z);
  const m = prog(t, T.morph, 1.0, glide);
  if (m >= 1) return rect;
  const a = openAnchor(f).die;
  return a.map((p, i) => [lerp(p[0], rect[i][0], m), lerp(p[1], rect[i][1], m)]) as Quad;
};

// ------------------------------------------------------------------ 芯片叠加层在屏幕上的四边形
export const dieQuad = (t: number, f: number): Quad => {
  if (f >= CLOSE_F0) return closeAnchor(f).die;
  const c = camAt(t);
  const [x0, y0] = w2s(c, DIE.cx - DIE.w / 2, DIE.cy - DIE.h / 2);
  return rectQuad(x0, y0, DIE.w * c.z, DIE.h * c.z);
};
export const dieMatrix = (t: number, f: number) => matrix3d(DIE.w, DIE.h, dieQuad(t, f));
export const dieToScreen = (t: number, f: number, x: number, y: number) => mapPoint(DIE.w, DIE.h, dieQuad(t, f), x, y);

// 芯片叠加层上的格子：4 列 × 5 行，琥珀（图形）和冷白（AI）交错，表示两类计算任务都在这块芯片上跑（示意，不是核心）
export const SLOT = {cols: 4, rows: 5, cell: DIE.w / 4, size: 128};
export const slotXY = (i: number): [number, number] => {
  const c = i % SLOT.cols, r = Math.floor(i / SLOT.cols);
  const ch = DIE.h / SLOT.rows;
  return [(c + 0.5) * SLOT.cell, (r + 0.5) * ch];
};
export const slotKind = (i: number): 'game' | 'ai' => ((i % SLOT.cols) + Math.floor(i / SLOT.cols)) % 2 === 0 ? 'game' : 'ai';
export const SLOT_GAME = Array.from({length: SLOT.cols * SLOT.rows}, (_, i) => i).filter((i) => slotKind(i) === 'game');
export const SLOT_AI = Array.from({length: SLOT.cols * SLOT.rows}, (_, i) => i).filter((i) => slotKind(i) === 'ai');

// HBM 在叠加层本地坐标里的位置（和 Blender 模型同尺寸：HBM 11 × 10 mm，离芯片边 0.8 mm）
export const HBM_LOCAL = (() => {
  const out: [number, number, number, number][] = [];
  for (const sx of [-1, 1])
    for (const sy of [-1, 0, 1]) {
      const cx = DIE.w / 2 + sx * (13 + 0.8 + 5.5) * MM, cy = DIE.h / 2 + sy * (10 + 0.6) * MM;
      out.push([cx - 5.5 * MM, cy - 5 * MM, 11 * MM, 10 * MM]);
    }
  return out;
})();

export const ease01 = (x: number) => clamp(x);
