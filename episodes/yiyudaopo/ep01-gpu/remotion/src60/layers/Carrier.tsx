// 被选中的那一块：SHOT 02 里算出第一块地形的光照 → 14–17 秒被镜头跟着横移，路上琥珀色的内容留在身后，
// 只剩一个空的「计算方块」外形 → 停在 AI 区等着 → 27 秒 AI 的算式收进这个外形，变成冷白色的 AI 方块。
// 它是贯穿全片的「同一种东西」：一次计算。图形数据没有变成语言模型数据——内容先倒空了。
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {cycle, glide, lerp, prog} from '../lib/core';
import {mapPoint, quadScale} from '../lib/homography';
import {PATCHES, SEL, VPH, VPW} from '../lib/island';
import {camAt, carrierWorld, DOCK_LOCAL, panelQuad, T, w2s} from '../lib/plan';
import {Tile} from '../Tile';
import {gameTileLocal} from './Game';

export const DOCK = DOCK_LOCAL;      // AI 局部坐标：第一行结果方块的位置
export const AI_TILE = 150;

export const Carrier: React.FC = () => {
  const f = useCurrentFrame();
  const t = f / 30;
  if (t < T.tile1 || t >= 28.2) return null;
  const p = PATCHES[SEL];
  const {fill, lit} = cycle(t, [T.comp1], T.out1 - T.comp1, 0.55);
  const appear = prog(t, T.tile1, 0.45);
  if (t < T.fly0) {
    const q = panelQuad(t, f), z = quadScale(q, VPW);
    const [lx, ly, s] = gameTileLocal(t, p);
    const [x, y] = mapPoint(VPW, VPH, q, lx, ly);
    return <Tile x={x} y={y - (1 - appear) * 30} s={s * z * (0.6 + 0.4 * appear)} kind="game" fill={fill} lit={lit} lift={0.4 + 0.6 * prog(t, T.lift, 0.6)} opacity={appear} />;
  }
  // 飞行：世界坐标里从地块上方到 AI 区的停靠位
  const s0 = gameTileLocal(T.fly0, p)[2];
  const [wx, wy] = carrierWorld(t);
  const c = camAt(t);
  const [x, y] = w2s(c, wx, wy);
  const s = lerp(s0, AI_TILE, prog(t, T.fly0 + 0.4, 2.0, glide)) * c.z;
  const drain = prog(t, 15.0, 1.3);                      // 琥珀色的内容倒空，只剩外形
  const wait = 1 - 0.65 * prog(t, T.fly1, 0.7);          // 到位以后退成淡淡的空位
  const become = prog(t, T.contract + 0.55, 0.35);       // AI 的算式收进来
  const aiLit = cycle(t, [T.contract + 0.5], 0.5);
  return (
    <>
      <Tile x={x} y={y} s={s} kind="game" lit={lit * (1 - drain)} lift={1} opacity={1 - drain} />
      <Tile x={x} y={y} s={s} kind="neutral" empty={1} lift={0.6} opacity={drain * wait * (1 - become)} />
      <Tile x={x} y={y} s={s} kind="ai" fill={aiLit.fill} lit={aiLit.lit} lift={0.6} opacity={become} label={t >= T.contract + 0.9 ? '23' : undefined} labelSize={64 * c.z} />
    </>
  );
};
