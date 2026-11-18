// TEST A — T2：游戏计算 → AI 计算（6 秒，180 帧）
// 同一张桌面：左前方是游戏沙盘（小岛），右后方立着 AI 面板。相机一直往右、往面板方向走（Follow → Approach），
// 中间 2.5–4 秒两边各有一个计算方块，用同样的「输入 → 计算 → 输出」同时演一遍——这是两段之间的桥。
// 游戏的数据留在游戏里（输出回到地块），AI 的数据从问题来（输入来自问题的示意数字），两者不互相变成对方。
import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {clamp, cycle, glide, lerp, linear, prog, settle} from '../lib/core';
import {PATCHES, SEL} from '../lib/island';
import {C, FONT} from '../lib/theme';
import {Dot, Tile} from '../Tile';
import {ringPath, Stage3D} from './Stage3D';
import {CARD, CARD_CY, cardLocal, camPath, proj, pxPerUnit, view, W} from './world3d';

const S = (f: number) => f / 30;
// 关键时间（秒，片段内）
export const K2 = {
  selDraw: 0.15, dimOthers: 1.0, type0: 1.25, split: 2.0, nums: 2.15, drain: 2.1,
  inA: 2.55, comp: 2.95, out: 3.55, litDone: 3.9,
  select: 4.0, recede: 4.3, center: 4.65, label: 5.35,
};
const D_FRONT = (CARD.w * (0.5 * 1920 / Math.tan(0.31))) / (1080 * 1.03);   // 正对面板、面板宽 = 屏宽 × 1.03
export const cam2 = camPath(
  [0, 1.0, 2.5, 4.0, 6.0],
  [0.6, 0.75, 3.9, 4.15, CARD.x],
  [0.6, 0.7, 5.0, 5.15, CARD_CY],
  [1.0, 0.8, -4.0, -4.3, CARD.z],
  [28, 27.4, 55, 54.0, D_FRONT],
  [0.62, 0.61, 0.30, 0.295, 0.0],
  [0.55, 0.53, 0.25, 0.245, 0.0],
);

// AI 面板本地布局（和全片 SHOT 03 同一套坐标：面板正对铺满时就是屏幕坐标）
const Q = '黑洞是什么？', CH = 84;
const charX = (i: number) => 540 - (Q.length * CH) / 2 + CH / 2 + i * CH;
const SEGS = [
  {from: [0, 1], x: 215, v: [2, 3]}, {from: [2], x: 425, v: [1, 4]}, {from: [3, 4], x: 655, v: [5, 2]}, {from: [5], x: 865, v: [6, 1]},
];
export const AI_DOCK: [number, number] = [830, 830];
const Txt: React.FC<{x: number; y: number; size: number; o?: number; color?: string; children: React.ReactNode; w?: number; weight?: number}> = ({x, y, size, o = 1, color = '#F4F6F8', children, w = 160, weight = 700}) =>
  o <= 0.001 ? null : (
    <div style={{position: 'absolute', left: x - w / 2, top: y - size * 0.62, width: w, textAlign: 'center', fontFamily: FONT, fontWeight: weight, fontSize: size, lineHeight: `${size * 1.24}px`, color, opacity: o, whiteSpace: 'nowrap'}}>{children}</div>
  );

const CardContent: React.FC<{t: number}> = ({t}) => {
  const split = prog(t, K2.split, 0.6, glide);
  const sel = prog(t, K2.select, 0.35);
  const rec = prog(t, K2.recede, 0.45);
  const cen = prog(t, K2.center, 1.0, glide);
  const box = prog(t, 0.8, 0.4) * (1 - prog(t, K2.split, 0.35));
  const {fill, lit} = cycle(t, [K2.comp], K2.out - K2.comp, 0.5);
  const afterDemo = prog(t, 4.3, 0.8);                       // 演示完退成空位（之后 23 会收进这里）
  return (
    <>
      {/* 提问框 */}
      <div style={{position: 'absolute', left: 170, top: 358, width: 740, height: 144, borderRadius: 40, border: `3px solid rgba(${C.aiRGB},0.55)`, background: 'rgba(220,228,236,0.05)', opacity: box, boxSizing: 'border-box'}}>
        <div style={{position: 'absolute', left: 26, top: 44, width: 52, height: 52, borderRadius: 26, background: `rgba(${C.aiRGB},0.9)`, color: C.bg, fontFamily: FONT, fontWeight: 700, fontSize: 24, lineHeight: '52px', textAlign: 'center'}}>AI</div>
      </div>
      {Q.split('').map((ch, i) => {
        const s = SEGS.findIndex((g) => g.from.includes(i)), g = SEGS[s];
        const off = g.from.length === 2 ? (g.from.indexOf(i) - 0.5) * CH : 0;
        let x = lerp(charX(i), g.x + off, split), y = lerp(430, 470, split);
        let o = prog(t, K2.type0 + i * 0.09, 0.1);
        if (s === 0) { x = lerp(x, 430 + off, cen); y = lerp(y, 500, cen); } else o *= 1 - rec;
        return <Txt key={i} x={x} y={y} size={CH} o={o} w={120}>{ch}</Txt>;
      })}
      {/* 每段下面一小列示意数字 */}
      {SEGS.map((g, k) => {
        const a = prog(t, K2.nums + k * 0.1, 0.4);
        const first = k === 0;
        const o = first ? a : a * (1 - rec);
        const x1 = first ? lerp(g.x, 330, cen) : g.x, x2 = first ? lerp(g.x, 530, cen) : g.x;
        const y1 = first ? lerp(595, 640, cen) : 595 + rec * 30, y2 = first ? lerp(685, 640, cen) : 685 + rec * 30;
        const sz = first ? lerp(64, 104, cen) : 64;
        const bx = first ? lerp(g.x, 430, cen) : g.x, bw = first ? lerp(110, 350, cen) : 110, bh = first ? lerp(190, 140, cen) : 190;
        const glow = first ? sel * (1 - 0.6 * cen) : 0;
        return (
          <React.Fragment key={k}>
            <div style={{position: 'absolute', left: bx - bw / 2, top: (first ? lerp(640, 640, cen) : 640 + rec * 30) - bh / 2 - (1 - a) * 50, width: bw, height: bh, borderRadius: 30,
              border: `${first ? lerp(2, 4, sel) : 2}px solid rgba(${C.aiRGB},${0.5 + 0.4 * glow})`, opacity: o * 0.85, boxSizing: 'border-box',
              boxShadow: glow ? `0 0 ${24 * glow}px rgba(${C.aiRGB},${0.35 * glow})` : undefined}} />
            <Txt x={x1} y={y1 - (1 - a) * 50} size={sz} o={o}>{g.v[0]}</Txt>
            <Txt x={x2} y={y2 - (1 - a) * 50} size={sz} o={o}>{g.v[1]}</Txt>
          </React.Fragment>
        );
      })}
      <div style={{position: 'absolute', left: 33, top: 616, width: 200, textAlign: 'right', fontFamily: FONT, fontSize: 36, color: C.sub, opacity: prog(t, K2.label, 0.4)}}>示例输入</div>
      {/* AI 的计算方块（位置 = 全片里第一行结果方块的位置） */}
      <Tile x={AI_DOCK[0]} y={AI_DOCK[1]} s={150} kind="ai" fill={fill} lit={lit * (1 - afterDemo)} lift={0.6} opacity={prog(t, 1.9, 0.4) * (1 - 0.65 * afterDemo)} empty={afterDemo} />
      {/* 输入：问题变来的数字流进方块 */}
      {t > K2.inA && t < K2.comp && SEGS.map((g, k) => {
        const kk = prog(t, K2.inA + k * 0.04, K2.comp - K2.inA - 0.12, glide);
        return <Dot key={k} x={lerp(g.x, AI_DOCK[0] - 40, kk)} y={lerp(745, AI_DOCK[1], kk) - 60 * 4 * kk * (1 - kk)} r={10} kind="ai" opacity={1 - prog(t, K2.comp - 0.06, 0.06)} />;
      })}
      {/* 输出：落进下面的结果位 */}
      <div style={{position: 'absolute', left: AI_DOCK[0] - 50, top: 1060 - 50, width: 100, height: 100, borderRadius: 22, boxSizing: 'border-box',
        border: `3px solid rgba(${C.aiRGB},${0.35 + 0.5 * prog(t, K2.litDone, 0.2)})`, background: `rgba(${C.aiRGB},${0.3 * prog(t, K2.litDone, 0.2)})`,
        opacity: prog(t, 2.3, 0.4) * (1 - prog(t, 4.4, 0.5))}} />
      {t > K2.out && t < K2.litDone + 0.05 && <Dot x={AI_DOCK[0]} y={lerp(AI_DOCK[1] + 75, 1060, prog(t, K2.out, K2.litDone - K2.out, linear))} r={11} kind="ai" />}
    </>
  );
};

export const T2Test: React.FC = () => {
  const f = useCurrentFrame();
  const t = S(f);
  const cam = cam2(t);
  const v = view(cam);
  const sel = PATCHES[SEL];
  const others = 1 - 0.55 * prog(t, K2.dimOthers, 0.6);
  const patchLit = (p: typeof sel) => (p.id === SEL ? 1 - prog(t, K2.drain, 0.3) + prog(t, K2.litDone, 0.25) : 1);
  const dim = (p: typeof sel | null) => (p && p.id === SEL ? 1 : lerp(1, 0.72, prog(t, K2.dimOthers, 0.6)));
  const tileAt = (p: typeof sel, h: number): [number, number, number, number, number] => {
    const top = proj(v, [p.c[0], p.c[1] + h, p.c[2]]), base = proj(v, [p.c[0], p.c[1] + 0.05, p.c[2]]);
    return [top[0], top[1], pxPerUnit(v, [p.c[0], p.c[1] + h, p.c[2]]), base[0], base[1]];
  };
  const {fill, lit} = cycle(t, [K2.comp], K2.out - K2.comp, 0.55);
  const selPop = prog(t, K2.selDraw, 0.5);
  const [sx, sy, su, bx, by] = tileAt(sel, 2.3);
  return (
    <AbsoluteFill style={{background: '#17191D', overflow: 'hidden'}}>
      <Stage3D cam={cam} lit={patchLit} dim={dim} card={<CardContent t={t} />} />
      <svg width={W} height={1920} style={{position: 'absolute', left: 0, top: 0}}>
        {/* 选中地块的琥珀描边 + 方块和地块之间的连线 */}
        <path d={ringPath(v, sel)} fill="none" stroke={C.game} strokeWidth={4} strokeLinejoin="round" opacity={selPop} />
        {PATCHES.map((p) => {
          if (p.id === SEL) return null;
          const [x, y, u, b1, b2] = tileAt(p, 1.4);
          return <line key={p.id} x1={b1} y1={b2} x2={x} y2={y + 0.33 * u} stroke={C.game} strokeOpacity={0.35 * others} strokeWidth={1.5} />;
        })}
        <line x1={bx} y1={by} x2={sx} y2={sy + 0.6 * su * selPop} stroke={C.game} strokeOpacity={0.85} strokeWidth={3} />
      </svg>
      {/* 其余地块上的方块：一直钉在各自的地块上，退一步 */}
      {PATCHES.map((p) => {
        if (p.id === SEL) return null;
        const [x, y, u] = tileAt(p, 1.4);
        return <Tile key={p.id} x={x} y={y} s={0.66 * u} kind="game" lit={0.45} lift={0.5} opacity={0.95 * others} />;
      })}
      {/* 选中的那块 */}
      <Tile x={sx} y={sy} s={1.2 * su * lerp(0.7, 1, selPop)} kind="game" fill={fill} lit={Math.max(lit, 0.5 * selPop)} lift={1} />
      {/* 输入：地块的朝向（法线）沿连线上来；输出：落回地块，地块变亮 */}
      {t > K2.inA && t < K2.comp && <Dot x={lerp(bx, sx, prog(t, K2.inA, K2.comp - K2.inA - 0.05, glide))} y={lerp(by, sy + 0.6 * su, prog(t, K2.inA, K2.comp - K2.inA - 0.05, glide))} r={0.16 * su} kind="game" />}
      {t > K2.out && t < K2.litDone + 0.05 && <Dot x={lerp(sx, bx, prog(t, K2.out, K2.litDone - K2.out, linear))} y={lerp(sy + 0.6 * su, by, prog(t, K2.out, K2.litDone - K2.out, linear))} r={0.16 * su} kind="game" />}
    </AbsoluteFill>
  );
};
export const unusedT2 = [clamp, settle, cardLocal];
