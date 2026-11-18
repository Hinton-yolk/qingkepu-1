// SHOT 02（5–17 秒）+ 之后一直留在世界左上方的「图形计算」那一组。
// 视口先贴在芯片四角上（单应），再摆正成世界里的窗口；里面是低多边形小岛。
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {clamp, cycle, glide, lerp, linear, prog, settle} from '../lib/core';
import {mapPoint, matrix3d, quadScale} from '../lib/homography';
import {focalPx, islandCam, PATCHES, patchLit, patchOutline, projectPoint, SEL, triPatch, TRIS, VPH, VPW, Patch} from '../lib/island';
import {camAt, FLY, panelQuad, panelToWorld, T, w2s} from '../lib/plan';
import {project, shadeColor} from '../lib/terrain';
import {C} from '../lib/theme';
import {Dot, Tile} from '../Tile';

export const SUN: [number, number] = [842, 118];               // 视口本地坐标
const H0 = 1.25, H1 = 1.9;                                     // 方块悬在地块上方多高（3D 单位），抬起后更高

/** 方块在视口本地坐标里的位置和边长（t 之后相机定住，位置也定住） */
export function gameTileLocal(t: number, p: Patch): [number, number, number, number, number] {
  const tt = Math.min(t, 14.7);
  const cam = islandCam(tt);
  const H = lerp(H0, H1, prog(tt, T.lift, 0.6, glide));
  const top = projectPoint(cam, [p.c[0], p.c[1] + H, p.c[2]]);
  const base = projectPoint(cam, [p.c[0], p.c[1] + 0.05, p.c[2]]);
  const s = (0.72 * focalPx(cam)) / top[2] * (p.id === SEL ? 1.25 : 1);
  return [top[0], top[1], s, base[0], base[1]];
}
/** 定住以后每个方块的世界坐标和世界尺寸（SHOT 04–05 用） */
export const GAME_WORLD = PATCHES.map((p) => {
  const [x, y, s] = gameTileLocal(14.7, p);
  const [wx, wy] = panelToWorld(x, y);
  return {id: p.id, x: wx, y: wy, s};
});
// 流进芯片的 10 块（离选中地块最近的那些；选中那块已经被镜头带走了）
export const GAME_STREAM = [...PATCHES].filter((p) => p.id !== SEL).sort((a, b) => a.order - b.order).slice(0, 10).map((p) => p.id);
FLY.start = (() => { const [x, y] = gameTileLocal(T.fly0, PATCHES[SEL]); return panelToWorld(x, y); })();
export const gameCycles = (p: Patch) => (p.id === SEL ? [T.comp1] : [T.compAll, T.act1, T.act2, T.act3]);
export const departGame = (j: number) => T.stream0 + j * 0.12;

const appear = (t: number, p: Patch) => (p.id === SEL ? prog(t, T.tile1, 0.45) : prog(t, T.tilesAll + p.order * 0.035, 0.35));

export const Game: React.FC = () => {
  const f = useCurrentFrame();
  const t = f / 30;
  if (t < T.reveal - 0.05 || t > 48.6) return null;
  const q = panelQuad(t, f);
  const z = quadScale(q, VPW);
  const cam = islandCam(t);
  const P = project(TRIS, cam, VPW, VPH);
  const sel = PATCHES[SEL];
  // 视口：贴着芯片时从中心「打开」；进去以后，14 秒起退到背景
  const open = prog(t, T.reveal, 0.65, glide);
  const recede = 1 - 0.6 * prog(t, T.lift, 1.6, glide) - 0.25 * prog(t, 40.0, 2.0, glide);
  const gone = 1 - prog(t, T.fadeOld, 1.3, glide);
  const others = 1 - 0.38 * (prog(t, T.sel + 0.3, 0.6) - prog(t, T.pull, 0.6));      // 选中时其余地块退一步
  const radius = lerp(4, 30, prog(t, T.morph, 1.0, glide));
  const outlineDraw = prog(t, T.sel, 0.95, glide);
  const outlineAll = prog(t, T.tilesAll, 0.4) * (1 - prog(t, T.lift, 0.5));
  const sunPulse = Math.exp(-Math.max(0, t - T.cue) / 0.25) * (t >= T.cue ? 1 : 0) + Math.exp(-Math.max(0, t - T.in1) / 0.25) * (t >= T.in1 ? 0.7 : 0);
  const toS = (x: number, y: number) => mapPoint(VPW, VPH, q, x, y);

  const selOutline = patchOutline(cam, sel);
  const outlinePath = (pts: [number, number][]) => 'M' + pts.map((p) => `${p[0].toFixed(1)},${p[1].toFixed(1)}`).join('L') + 'Z';
  const per = selOutline.reduce((acc, p, i) => acc + Math.hypot(p[0] - selOutline[(i + 1) % selOutline.length][0], p[1] - selOutline[(i + 1) % selOutline.length][1]), 0);

  return (
    <>
      {/* 视口 */}
      <div style={{position: 'absolute', left: 0, top: 0, width: VPW, height: VPH, transformOrigin: '0 0', transform: matrix3d(VPW, VPH, q),
        borderRadius: radius, overflow: 'hidden', opacity: recede * gone,
        WebkitMaskImage: open < 1 ? `radial-gradient(ellipse 60% 55% at 50% 50%, #000 ${open * 150 - 10}%, transparent ${open * 150 + 12}%)` : undefined}}>
        <svg width={VPW} height={VPH} style={{position: 'absolute', left: 0, top: 0}}>
          <defs>
            <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0" stopColor="#7F9DB0" /><stop offset="0.26" stopColor="#B4B6AB" /><stop offset="0.34" stopColor="#2E5568" /><stop offset="1" stopColor="#1F4253" />
            </linearGradient>
            <radialGradient id="sunG"><stop offset="0" stopColor={C.sun} stopOpacity="0.9" /><stop offset="1" stopColor={C.sun} stopOpacity="0" /></radialGradient>
          </defs>
          <rect width={VPW} height={VPH} fill="url(#sky)" />
          <circle cx={SUN[0]} cy={SUN[1]} r={90 + 40 * sunPulse} fill="url(#sunG)" opacity={0.55 + 0.4 * sunPulse} />
          <circle cx={SUN[0]} cy={SUN[1]} r={36} fill={C.sun} />
          {P.map((p) => {
            if (!p.facing && p.tri.kind !== 'water') return null;
            const pid = triPatch[p.tri.id];
            const L = pid < 0 ? 1 : patchLit(t, PATCHES[pid]);
            const dimK = pid === SEL ? 1 : others;
            const lit = shadeRGB(p.tri.base, p.shade), flat = [p.tri.base[0] * 0.36, p.tri.base[1] * 0.36, p.tri.base[2] * 0.38];
            const col = [0, 1, 2].map((k) => Math.round(lerp(flat[k], lit[k], clamp(L)) * dimK));
            const fill = `rgb(${col[0]},${col[1]},${col[2]})`;
            const d = `M${p.pts[0][0]},${p.pts[0][1]}L${p.pts[1][0]},${p.pts[1][1]}L${p.pts[2][0]},${p.pts[2][1]}Z`;
            return <path key={p.tri.id} d={d} fill={fill} stroke={fill} strokeWidth={0.8} />;
          })}
          {/* 所有地块的淡描边：它们都是「同一种地块」 */}
          {outlineAll > 0 && PATCHES.map((p) => p.id === SEL ? null : (
            <path key={p.id} d={outlinePath(patchOutline(cam, p))} fill="none" stroke={C.game} strokeOpacity={0.45 * outlineAll * prog(t, T.tilesAll + p.order * 0.035, 0.3)} strokeWidth={2.5} strokeLinejoin="round" />
          ))}
          {/* 选中的地块：琥珀描边一笔画上 */}
          <path d={outlinePath(selOutline)} fill="none" stroke={C.game} strokeWidth={5} strokeLinejoin="round"
            strokeDasharray={per} strokeDashoffset={per * (1 - outlineDraw)} opacity={1 - 0.5 * prog(t, T.lift, 0.5)} />
          {/* 方块和地块之间的细线 */}
          {PATCHES.map((p) => {
            const a = appear(t, p) * (1 - prog(t, T.lift, 0.5));
            if (a <= 0) return null;
            const [x, y, s, bx, by] = gameTileLocal(t, p);
            return <line key={p.id} x1={bx} y1={by} x2={x} y2={y + s / 2} stroke={C.game} strokeOpacity={0.55 * a} strokeWidth={2} />;
          })}
        </svg>
      </div>
      {/* 视口边：芯片的边缘变成窗口的边 */}
      <svg width={1080} height={1920} style={{position: 'absolute', left: 0, top: 0, opacity: (1 - prog(t, 6.2, 1.0)) * open}}>
        <path d={`M${q.map((p) => p.join(',')).join('L')}Z`} fill="none" stroke={C.metal} strokeWidth={2.5} strokeOpacity={0.8} />
      </svg>
      {/* 输入：从太阳飞向方块（光照方向是输入之一） */}
      {t > T.in1 && t < T.comp1 && (() => {
        const k = prog(t, T.in1, T.comp1 - T.in1, glide);
        const [x, y, s] = gameTileLocal(t, sel);
        const a = toS(SUN[0], SUN[1]), b = toS(x, y - s * 0.2);
        return <Dot x={lerp(a[0], b[0], k)} y={lerp(a[1], b[1], k) - 80 * 4 * k * (1 - k)} r={11 * z} kind="game" opacity={1 - prog(t, T.comp1 - 0.08, 0.08)} />;
      })()}
      {t > T.cue && t < T.compAll && PATCHES.filter((p) => p.id !== SEL).map((p) => {
        const k = prog(t, T.cue, T.compAll - T.cue, glide);
        const [x, y, s] = gameTileLocal(t, p);
        const a = toS(SUN[0], SUN[1]), b = toS(x, y - s * 0.2);
        return <Dot key={p.id} x={lerp(a[0], b[0], k)} y={lerp(a[1], b[1], k) - 60 * 4 * k * (1 - k)} r={7.5 * z} kind="game" opacity={prog(t, T.cue, 0.06) * (1 - prog(t, T.compAll - 0.06, 0.06))} />;
      })}
      {/* 输出：从方块落回地块，地块随之变亮 */}
      {t > T.out1 && t < T.lit1 + 0.05 && (() => {
        const k = prog(t, T.out1, T.lit1 - T.out1, linear);
        const [x, y, s, bx, by] = gameTileLocal(t, sel);
        const a = toS(x, y + s / 2), b = toS(bx, by);
        return <Dot x={lerp(a[0], b[0], k)} y={lerp(a[1], b[1], k)} r={10 * z} kind="game" />;
      })()}
      {t > T.outAll && t < T.litAll + 0.05 && PATCHES.filter((p) => p.id !== SEL).map((p) => {
        const k = prog(t, T.outAll, T.litAll - T.outAll, linear);
        const [x, y, s, bx, by] = gameTileLocal(t, p);
        const a = toS(x, y + s / 2), b = toS(bx, by);
        return <Dot key={p.id} x={lerp(a[0], b[0], k)} y={lerp(a[1], b[1], k)} r={7 * z} kind="game" />;
      })}
      {/* 方块（选中那块由 Carrier 画：它要跟着镜头走） */}
      {PATCHES.map((p) => {
        if (p.id === SEL) return null;
        const j = GAME_STREAM.indexOf(p.id);
        if (j >= 0 && t >= departGame(j)) return null;          // 已经流向芯片，由 Streams 画
        const a = appear(t, p);
        if (a <= 0) return null;
        let x: number, y: number, s: number;
        if (t < 14.7) {
          const L = gameTileLocal(t, p);
          [x, y] = toS(L[0], L[1]); s = L[2] * z;
        } else {
          const g = GAME_WORLD[p.id], c = camAt(t);
          [x, y] = w2s(c, g.x, g.y); s = g.s * c.z;
        }
        const {fill, lit} = cycle(t, gameCycles(p), 0.5);
        const fadeRest = j >= 0 ? 1 : gone;
        return <Tile key={p.id} x={x} y={y - (1 - a) * 20 * z} s={s * lerp(0.6, 1, a)} kind="game" fill={fill} lit={lit} lift={0.4 + 0.6 * prog(t, T.lift, 0.6)} opacity={a * fadeRest} />;
      })}
    </>
  );
};

function shadeRGB(base: [number, number, number], diffuse: number): number[] {
  const m = shadeColor(base, diffuse).match(/\d+/g)!.map(Number);
  return m;
}
