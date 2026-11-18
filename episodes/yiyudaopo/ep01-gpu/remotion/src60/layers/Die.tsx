// SHOT 05–06（45–57 秒）：两组方块排成两股、同一个方向往下流，落进芯片轮廓里的格子；
// 镜头接近芯片，48.5 秒起叠加层改由 Blender 底片的逐帧锚点驱动（芯片四角），真芯片在底下浮现。
// 格子只表示「芯片上同时进行的许多计算」，不是 GPU 核心（画面有注）。
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {cycle, glide, lerp, prog} from '../lib/core';
import {DIE, dieMatrix, HBM_LOCAL, SLOT, SLOT_AI, SLOT_GAME, slotXY, T, camAt, w2s, aiToWorld} from '../lib/plan';
import {PATCHES} from '../lib/island';
import {C} from '../lib/theme';
import {Tile, Kind} from '../Tile';
import {departGame, GAME_STREAM, GAME_WORLD} from './Game';
import {departAI, ROWS} from './AI';
import {AI_TILE, DOCK} from './Carrier';

const TRAVEL = 1.45;
type S = {kind: Kind; slot: number; depart: number; from: () => [number, number, number]};
const STREAM: S[] = [
  ...GAME_STREAM.map((id, j) => ({kind: 'game' as Kind, slot: SLOT_GAME[SLOT_GAME.length - 1 - j], depart: departGame(j), from: () => { const g = GAME_WORLD[id]; return [g.x, g.y, g.s] as [number, number, number]; }})),
  ...ROWS.map((r, j) => ({kind: 'ai' as Kind, slot: SLOT_AI[j], depart: departAI(j), from: () => { const [x, y] = aiToWorld(DOCK[0], r.y); return [x, y, AI_TILE * r.sc] as [number, number, number]; }})),
];
const slotWorld = (i: number): [number, number] => { const [x, y] = slotXY(i); return [DIE.cx - DIE.w / 2 + x, DIE.cy - DIE.h / 2 + y]; };
const bez = (p0: number[], p1: number[], p2: number[], p3: number[], k: number) =>
  [0, 1].map((d) => (1 - k) ** 3 * p0[d] + 3 * (1 - k) ** 2 * k * p1[d] + 3 * (1 - k) * k * k * p2[d] + k ** 3 * p3[d]) as [number, number];

/** 流动中的方块在世界里的位置和大小 */
function streamPos(s: S, t: number): [number, number, number] {
  const [x0, y0, s0] = s.from();
  const [x3, y3] = slotWorld(s.slot);
  const laneX = DIE.cx + (s.kind === 'game' ? -150 : 150), laneY = DIE.cy - DIE.h / 2 - 140;
  const k = prog(t, s.depart, TRAVEL, glide);
  const split = 0.72;
  if (k < split) {
    const u = k / split;
    const [x, y] = bez([x0, y0], [lerp(x0, laneX, 0.35), y0 + 260], [laneX, laneY - 260], [laneX, laneY], u);
    return [x, y, lerp(s0, SLOT.size, u * 0.7)];
  }
  const u = (k - split) / (1 - split);
  return [lerp(laneX, x3, u), lerp(laneY, y3, u), lerp(lerp(s0, SLOT.size, 0.7), SLOT.size, u)];
}
const slotCycles = (kind: Kind) => (kind === 'game' ? [T.g1, T.g3] : [T.g2, T.g3]);

/** 锁定后某一格方块的状态（全片 SHOT 05–06 和 T4 测试共用，保证接缝两边是同一套公式） */
export function lockedTile(slot: number, t: number) {
  const s = STREAM.find((x) => x.slot === slot)!;
  const [x, y] = slotXY(slot);
  const d = Math.hypot(x - DIE.w / 2, y - DIE.h / 2) / 500;
  const r = prog(t, T.recede + (1 - d) * 0.5, 1.5, glide);
  const {fill, lit} = cycle(t, [s.depart + TRAVEL - 0.1, ...slotCycles(s.kind)], 0.5);
  return {kind: s.kind, x, y, fill, lit: Math.max(lit, 0.35) * (1 - r), s: SLOT.size * lerp(1, 0.78, r), lift: 0.25 * (1 - r), opacity: (1 - r) * 0.94};
}
/** 芯片轮廓、HBM 轮廓、虚线格子的透明度 */
export const dieChrome = (t: number) => ({
  outline: prog(t, T.dieIn, 0.9) * (1 - prog(t, 50.6, 1.0, glide)),
  grid: prog(t, T.dieIn + 0.3, 0.8) * (1 - prog(t, 49.4, 1.0)),
  hbm: prog(t, T.dieIn + 0.4, 0.8) * (1 - prog(t, 50.4, 1.0, glide)),
});

export const Die: React.FC = () => {
  const f = useCurrentFrame();
  const t = f / 30;
  if (t < T.dieIn - 0.05) return null;
  const locked = t >= T.lock;
  const {outline, grid, hbm} = dieChrome(t);
  const cam = camAt(t);
  const tileProps = (s: S) => {
    const {fill, lit} = cycle(t, [s.depart + TRAVEL - 0.1, ...slotCycles(s.kind)], 0.5);
    return {fill, lit: Math.max(lit, 0.35)};
  };
  return (
    <>
      {/* 芯片轮廓叠加层：本地坐标 800×954 = 26×31 mm */}
      <div style={{position: 'absolute', left: 0, top: 0, width: DIE.w, height: DIE.h, transformOrigin: '0 0', transform: dieMatrix(t, f)}}>
        <div style={{position: 'absolute', inset: 0, borderRadius: 10, border: `6px solid ${C.metal}`, opacity: outline, boxSizing: 'border-box'}} />
        {HBM_LOCAL.map(([x, y, w, h], i) => (
          <div key={i} style={{position: 'absolute', left: x, top: y, width: w, height: h, borderRadius: 8, border: `4px solid ${C.metalDim}`, opacity: hbm, boxSizing: 'border-box'}} />
        ))}
        {Array.from({length: SLOT.cols * SLOT.rows}, (_, i) => {
          const [x, y] = slotXY(i);
          return <div key={i} style={{position: 'absolute', left: x - SLOT.size / 2, top: y - SLOT.size / 2, width: SLOT.size, height: SLOT.size, borderRadius: SLOT.size * 0.22,
            border: `3px dashed rgba(${C.neutralRGB},0.6)`, opacity: grid * 0.6, boxSizing: 'border-box'}} />;
        })}
        {locked && STREAM.map((s, i) => {
          const L = lockedTile(s.slot, t);
          return <Tile key={i} x={L.x} y={L.y} s={L.s} kind={L.kind} fill={L.fill} lit={L.lit} lift={L.lift} opacity={L.opacity} />;
        })}
      </div>
      {/* 流动中的方块（锁定前，世界坐标 → 屏幕） */}
      {!locked && STREAM.map((s, i) => {
        if (t < s.depart) return null;
        const [wx, wy, ws] = streamPos(s, t);
        const [x, y] = w2s(cam, wx, wy);
        const {fill, lit} = tileProps(s);
        return <Tile key={i} x={x} y={y} s={ws * cam.z} kind={s.kind} fill={fill} lit={lit} lift={0.6} />;
      })}
    </>
  );
};
export const unusedPatches = PATCHES.length;
