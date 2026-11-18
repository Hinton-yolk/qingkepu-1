// 背景（石墨 + 跟着世界相机走的淡点阵）、两段 Blender 底片、屏幕上的字
import React from 'react';
import {AbsoluteFill, OffthreadVideo, Sequence, staticFile, useCurrentFrame} from 'remotion';
import plates from '../plates.json';
import {glide, launch, lerp, prog, settle, win} from '../lib/core';
import {camAt, CLOSE_F0, T} from '../lib/plan';
import {C, FONT} from '../lib/theme';

export const Background: React.FC = () => {
  const f = useCurrentFrame();
  const t = f / 30;
  const c = camAt(t);
  const sp = 72 * c.z;
  const ox = 540 - c.cx * c.z, oy = 960 - c.cy * c.z;
  return (
    <AbsoluteFill style={{background: `radial-gradient(ellipse 85% 60% at 50% 46%, ${C.bgLift} 0%, ${C.bg} 70%, #121417 100%)`}}>
      <AbsoluteFill style={{backgroundImage: `radial-gradient(circle, ${C.dot} ${Math.max(1, 2.2 * c.z)}px, transparent ${Math.max(1.5, 2.8 * c.z)}px)`,
        backgroundSize: `${sp}px ${sp}px`, backgroundPosition: `${ox}px ${oy}px`}} />
    </AbsoluteFill>
  );
};

const Plate: React.FC<{name: 'OPEN' | 'CLOSE'}> = ({name}) =>
  (plates as Record<string, boolean>)[name] ? (
    <OffthreadVideo src={staticFile(`dl60/${name}.mp4`)} muted style={{width: 1080, height: 1920}} />
  ) : (
    <AbsoluteFill style={{background: 'repeating-linear-gradient(45deg,#1b1d21 0 40px,#202227 40px 80px)', color: C.sub, fontFamily: FONT, fontSize: 40, textAlign: 'center', paddingTop: 900}}>
      占位 · Blender {name}
    </AbsoluteFill>
  );

export const Plates: React.FC = () => {
  const f = useCurrentFrame();
  const t = f / 30;
  // OPEN：芯片方框里长出视口时，四周的电路板退进石墨底色
  const openO = 1 - prog(t, 4.95, 0.8, glide);
  const closeO = prog(t, T.plateIn, T.plateFull - T.plateIn, glide);
  return (
    <>
      {openO > 0 && (
        <Sequence from={0} durationInFrames={166} layout="none">
          <AbsoluteFill style={{opacity: openO}}><Plate name="OPEN" /></AbsoluteFill>
        </Sequence>
      )}
      <Sequence from={CLOSE_F0} layout="none">
        <AbsoluteFill style={{opacity: closeO}}><Plate name="CLOSE" /></AbsoluteFill>
      </Sequence>
    </>
  );
};

// ------------------------------------------------------------------ 屏幕上的字（全部在中间安全区：左右 ≥ 72 px，避开下方字幕区和右侧按钮）
const Line: React.FC<{y: number; size: number; o: number; dy?: number; color?: string; weight?: number; children: React.ReactNode; spacing?: number}> = ({
  y, size, o, dy = 0, color = C.ink, weight = 700, children, spacing = 2,
}) =>
  o <= 0.001 ? null : (
    <div style={{position: 'absolute', left: 60, right: 60, top: y - size * 0.62 + dy, textAlign: 'center', fontFamily: FONT, fontWeight: weight, fontSize: size,
      lineHeight: `${size * 1.24}px`, letterSpacing: spacing, color, opacity: o, whiteSpace: 'nowrap',
      textShadow: '0 2px 18px rgba(8,9,11,0.85), 0 1px 3px rgba(8,9,11,0.9)'}}>{children}</div>
  );
const Note: React.FC<{y: number; o: number; children: React.ReactNode}> = ({y, o, children}) =>
  o <= 0.001 ? null : (
    <div style={{position: 'absolute', left: 72, top: y, fontFamily: FONT, fontSize: 38, color: '#C3C8CE', opacity: o, letterSpacing: 1,
      background: 'rgba(16,17,20,0.6)', padding: '4px 14px', borderRadius: 10}}>{children}</div>
  );

export const Texts: React.FC = () => {
  const f = useCurrentFrame();
  const t = f / 30;
  // SHOT 01：第一行先出，第二行出来时第一行往上让位、退成次要（同一个位置，不分两处）
  const l1 = prog(t, T.q1, 0.35), l2 = prog(t, T.q2, 0.4);
  const out = prog(t, T.qOut, 0.45, launch);
  const make = prog(t, T.q2, 0.45, glide);
  // 片尾
  const aQ = prog(t, T.ansQ, 0.45), aA = prog(t, T.ansA, 0.5), sig = prog(t, T.sig, 0.6);
  return (
    <>
      <Line y={lerp(400, 318, make)} size={lerp(108, 78, make)} o={l1 * (1 - out) * lerp(1, 0.82, make)} dy={(1 - l1) * 26 - out * 40} color={lerp(0, 1, make) > 0.5 ? C.sub : C.ink}>AI 不打游戏</Line>
      <Line y={438} size={104} o={l2 * (1 - out)} dy={(1 - l2) * 26 - out * 40}>为什么还要用 GPU？</Line>

      <Line y={262} size={74} o={win(t, 10.0, 0.4, 15.7, 0.4)} dy={(1 - prog(t, 10.0, 0.4)) * 20}>相似的计算，可以一起做</Line>
      <Line y={262} size={70} o={win(t, 17.8, 0.4, 20.3, 0.4)} dy={(1 - prog(t, 17.8, 0.4)) * 20}>AI 也要进行大量数值计算</Line>
      <Line y={262} size={74} o={win(t, 36.0, 0.4, 41.2, 0.5)} dy={(1 - prog(t, 36.0, 0.4)) * 20}>同一种运算，许多组结果</Line>
      <Line y={262} size={74} o={win(t, T.reveal5, 0.45, 49.3, 0.6)} dy={(1 - prog(t, T.reveal5, 0.45)) * 20}>共同点：大量计算可以并行</Line>

      <Note y={318} o={win(t, 8.7, 0.4, 13.8, 0.4)}>示意：每个地块按同一规则算明暗</Note>
      <Note y={1330} o={win(t, 18.7, 0.4, 29.4, 0.4)}>示意：真实模型的数字多得多，且多为小数</Note>
      <Note y={1420} o={win(t, 48.0, 0.5, 55.6, 0.5)}>示意：方块代表计算任务，不代表核心或分区</Note>

      <Line y={300} size={62} o={aQ} dy={(1 - aQ) * 18} color={C.sub} weight={700}>GPU 为什么适合 AI？</Line>
      <Line y={418} size={92} o={aA} dy={(1 - aA) * 22}>因为大量计算，</Line>
      <Line y={532} size={92} o={prog(t, T.ansA + 0.25, 0.5)} dy={(1 - prog(t, T.ansA + 0.25, 0.5)) * 22}>可以高效并行。</Line>
      <Line y={1470} size={38} o={sig * 0.9} color={C.ink} weight={400} spacing={16}>一语道破</Line>
      {/* 只在最后几帧落黑 */}
      <AbsoluteFill style={{background: '#000', opacity: prog(t, T.black, 1.8 / 30 * 8, settle)}} />
    </>
  );
};
