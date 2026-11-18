// 桌面空间的渲染：背景 → 桌面（光池 + 阴影）→ 沙盘和面板（按远近排序）。方块、连线等由各测试在上层画。
import React from 'react';
import {Cam, shadeColor, V3} from '../lib/terrain';
import {PATCHES, triPatch, Patch} from '../lib/island';
import {lerp, clamp} from '../lib/core';
import {matrix3d, Quad} from '../lib/homography';
import {C} from '../lib/theme';
import {BOARD, CARD, CARD_LIGHT, cardCorners, H, proj, projectIsland, projPoly, shadowOnTable, TABLE_Y, view, View, W} from './world3d';
import {ISLAND} from './world3d';


const path = (pts: [number, number][]) => (pts.length ? 'M' + pts.map((p) => `${p[0].toFixed(1)},${p[1].toFixed(1)}`).join('L') + 'Z' : '');

// 地块边界：沿地形起伏的一圈世界坐标点（缓存）
const ringCache = new Map<number, V3[]>();
export function patchRing(p: Patch): V3[] {
  const hit = ringCache.get(p.id);
  if (hit) return hit;
  const CELL = 1.5, x0 = -4.5 + p.ix * CELL, z0 = -4.5 + p.iz * CELL, M = 6;
  const h = (x: number, z: number) => {
    let best = 0, bd = 1e9;
    for (const i of p.tris) for (const v of ISLAND[i].p) { const dd = (v[0] - x) ** 2 + (v[2] - z) ** 2; if (dd < bd) { bd = dd; best = v[1]; } }
    return Math.max(best, 0) + 0.05;
  };
  const xz: [number, number][] = [];
  for (let k = 0; k < M; k++) xz.push([x0 + (CELL * k) / M, z0]);
  for (let k = 0; k < M; k++) xz.push([x0 + CELL, z0 + (CELL * k) / M]);
  for (let k = 0; k < M; k++) xz.push([x0 + CELL - (CELL * k) / M, z0 + CELL]);
  for (let k = 0; k < M; k++) xz.push([x0, z0 + CELL - (CELL * k) / M]);
  const out = xz.map(([x, z]) => [x, h(x, z), z] as V3);
  ringCache.set(p.id, out);
  return out;
}
export const ringPath = (v: View, p: Patch) => path(patchRing(p).map((q) => { const s = proj(v, q); return [s[0], s[1]] as [number, number]; }));

export const Stage3D: React.FC<{
  cam: Cam;
  lit: (p: Patch) => number;            // 地块光照状态：1 算过（有明暗）/ 0 没算（平涂暗）
  dim?: (p: Patch | null) => number;    // 亮度系数（选中时其余地块退一步）
  islandOpacity?: number;
  card: React.ReactNode;                // 面板内容：本地 1080 × 1920
  cardOpacity?: number;
  extraTable?: React.ReactNode;         // 桌面上的东西（例如 T4 的芯片格板），画在沙盘和面板之前
}> = ({cam, lit, dim = () => 1, islandOpacity = 1, card, cardOpacity = 1, extraTable}) => {
  const v = view(cam);
  const P = projectIsland(cam);
  // 桌面
  const table = projPoly(v, [[-60, TABLE_Y, -60], [80, TABLE_Y, -60], [80, TABLE_Y, 60], [-60, TABLE_Y, 60]]);
  const pool = (cx: number, cz: number, r: number) => projPoly(v, Array.from({length: 40}, (_, i) => [cx + r * Math.cos((i / 40) * 2 * Math.PI), TABLE_Y + 0.002, cz + r * Math.sin((i / 40) * 2 * Math.PI)] as V3));
  const boardShadow = projPoly(v, shadowOnTable([[-BOARD, -0.05, -BOARD], [BOARD, -0.05, -BOARD], [BOARD, -0.05, BOARD], [-BOARD, -0.05, BOARD]]));
  const cc = cardCorners();
  const cardShadow = projPoly(v, [cc[3], cc[2], ...shadowOnTable([cc[1], cc[0]])]);
  const q = cc.map((p) => { const s = proj(v, p); return [s[0], s[1]] as [number, number]; }) as Quad;
  const side = projPoly(v, [cc[1], [cc[1][0], cc[1][1], cc[1][2] - 0.22], [cc[2][0], cc[2][1], cc[2][2] - 0.22], cc[2]]);
  const top = projPoly(v, [cc[0], cc[1], [cc[1][0], cc[1][1], cc[1][2] - 0.22], [cc[0][0], cc[0][1], cc[0][2] - 0.22]]);
  const cardDepth = proj(v, [CARD.x, TABLE_Y + CARD.h / 2, CARD.z])[2];
  const islandDepth = proj(v, [0, 0, 0])[2];
  const cardFirst = cardDepth > islandDepth;

  const islandSvg = (
    <svg key="isl" width={W} height={H} style={{position: 'absolute', left: 0, top: 0, opacity: islandOpacity}}>
      {P.map((p) => {
        if (!p.facing) return null;
        const pid = p.tri.id < 100000 ? triPatch[p.tri.id] : -1;
        const pt = pid >= 0 ? PATCHES[pid] : null;
        const L = pt ? clamp(lit(pt)) : 1;
        const k = dim(pt);
        const litC = shadeColor(p.tri.base, p.shade).match(/\d+/g)!.map(Number);
        const flat = [p.tri.base[0] * 0.36, p.tri.base[1] * 0.36, p.tri.base[2] * 0.38];
        const col = [0, 1, 2].map((i) => Math.round(lerp(flat[i], litC[i], L) * k));
        const fill = `rgb(${col[0]},${col[1]},${col[2]})`;
        return <path key={p.tri.id} d={`M${p.pts[0][0]},${p.pts[0][1]}L${p.pts[1][0]},${p.pts[1][1]}L${p.pts[2][0]},${p.pts[2][1]}Z`} fill={fill} stroke={fill} strokeWidth={0.8} />;
      })}
    </svg>
  );
  const shade = Math.round(255 * CARD_LIGHT);
  const cardEl = (
    <React.Fragment key="card">
      <svg width={W} height={H} style={{position: 'absolute', left: 0, top: 0, opacity: cardOpacity}}>
        <path d={path(side)} fill="#0E0F12" />
        <path d={path(top)} fill="#2A2E35" />
      </svg>
      <div style={{position: 'absolute', left: 0, top: 0, width: W, height: H, transformOrigin: '0 0', transform: matrix3d(W, H, q), opacity: cardOpacity,
        borderRadius: 36, overflow: 'hidden', background: `linear-gradient(200deg, rgb(${shade * 0.17 + 18},${shade * 0.17 + 20},${shade * 0.17 + 24}) 0%, #17191D 70%)`,
        boxShadow: `inset 0 0 0 3px rgba(154,161,170,0.35)`}}>
        {card}
      </div>
    </React.Fragment>
  );
  return (
    <>
      <div style={{position: 'absolute', inset: 0, background: 'linear-gradient(#121417 0%, #1A1D21 45%, #1F2227 100%)'}} />
      <svg width={W} height={H} style={{position: 'absolute', left: 0, top: 0}}>
        <defs>
          <radialGradient id="pool"><stop offset="0" stopColor="#2A2E35" /><stop offset="1" stopColor="#1A1C20" stopOpacity="0" /></radialGradient>
          <filter id="soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="14" /></filter>
        </defs>
        <path d={path(table)} fill="#1A1C20" />
        <path d={path(pool(0, 0, 16))} fill="url(#pool)" />
        <path d={path(pool(CARD.x, CARD.z + 2, 9))} fill="url(#pool)" />
        <path d={path(boardShadow)} fill="rgba(0,0,0,0.3)" filter="url(#soft)" />
        <path d={path(cardShadow)} fill="rgba(0,0,0,0.38)" filter="url(#soft)" />
      </svg>
      {extraTable}
      {cardFirst ? [cardEl, islandSvg] : [islandSvg, cardEl]}
    </>
  );
};
export const metalLine = C.metal;
