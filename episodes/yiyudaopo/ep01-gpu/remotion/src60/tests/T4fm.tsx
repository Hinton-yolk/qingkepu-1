// EP01 · T4 FINAL MATCH v01（6 秒，180 帧）—— 时间轴对应全片 45.0–50.97 秒：本片第 179 帧 = 全片第 1529 帧，下一帧接全片第 1530 帧（GPU 镜头）。
//   0–1.25 s  一边一个例子，时间完全一致：游戏「地块输入 → 方块计算 → 地块变亮」；AI「[2,3] 和 [4,5] → 方块计算 → 23」
//   1.3–3.1 s 相机推向方块层（场景轻微虚化，仍认得出）；每边再加两个带细节的例子，三个同时算、同时出结果
//   2.95–4.05 s 每边再来 7 个简化方块（不带小数字），10 个一起算：游戏那边 10 块地同时变亮，AI 那边 10 个方块同时出结果
//   4.05 s    一行标题「不同任务，都能并行」（动作演完之后）
//   4.45–5.0 s 数字退掉；两组交错排进全片 GPU 镜头的 4 × 5 棋盘格（琥珀 / 冷白各 10 格），位置 = Blender 底片逐帧的芯片四角
//   5.0–6.0 s 直接用全片的 Die 组件和同一段 GPU 底片：底片在格子下面浮现，第 179 帧和全片第 1529 帧是同一套代码画的
import React from 'react';
import {AbsoluteFill, OffthreadVideo, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {clamp, cycle, glide, lerp, linear, prog, settle} from '../lib/core';
import {quadScale} from '../lib/homography';
import {PATCHES} from '../lib/island';
import {DIE, dieMatrix, dieQuad, dieToScreen, HBM_LOCAL, SLOT, SLOT_AI, SLOT_GAME, slotXY} from '../lib/plan';
import {buildScene, Cam, dot, project, shadeColor, V3} from '../lib/terrain';
import {C, FONT} from '../lib/theme';
import {Dot, Kind, Tile} from '../Tile';
import {Die, dieChrome, lockedTile} from '../layers/Die';
import {Note} from '../layers/Stage';

export const FILM_F0 = 1350;                                  // 本片第 0 帧 = 全片第 1350 帧（45.0 秒）
export const E = {
  in1: 0.15, fill1: 0.55, out1: 1.0,
  approach: 1.3, appear2: 1.5, in2: 2.15, fill2: 2.45, out2: 2.85,
  appear3: 2.95, in3: 3.3, fill3: 3.55, out3: 3.85,
  headline: 4.05, headlineOut: 4.5, numOut: 4.45, ctxOut: 4.45, rearr: 4.55, chromeIn: 4.7, handoff: 5.0,
};
const HANDOFF_F = 150;

// ------------------------------------------------------------------ 上半屏：小岛山坡特写（和 v02 同一个机位）
const TRI = buildScene();
const VW = 1080, VH = 800, VTOP = 220;
const ICAM: Cam = {target: [0.3, 0.5, 0.6], dist: 11, el: 0.62, az: 0.25, fov: 0.7};
const PROJ = project(TRI, ICAM, VW, VH);
const triPatch = new Map<number, number>();
PATCHES.forEach((p) => p.tris.forEach((i) => triPatch.set(i, p.id)));
function pp(p: V3): [number, number] {
  const c = ICAM, eye: V3 = [c.target[0] + c.dist * Math.cos(c.el) * Math.sin(c.az), c.target[1] + c.dist * Math.sin(c.el), c.target[2] + c.dist * Math.cos(c.el) * Math.cos(c.az)];
  const sub = (a: V3, b: V3): V3 => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
  const n = (a: V3): V3 => { const l = Math.hypot(...a); return [a[0] / l, a[1] / l, a[2] / l]; };
  const cr = (a: V3, b: V3): V3 => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
  const fwd = n(sub(c.target, eye)), right = n(cr(fwd, [0, 1, 0])), up = cr(right, fwd), f = (0.5 * VH) / Math.tan(c.fov / 2);
  const d = sub(p, eye), z = dot(d, fwd);
  return [VW / 2 + (dot(d, right) * f) / z, VTOP + VH / 2 - (dot(d, up) * f) / z];
}

// ------------------------------------------------------------------ 两组方块
type T4Tile = {kind: Kind; detail: boolean; idx: number; x: number; y: number; s: number; pid?: number; p?: [number, number]; r?: number; wave: 1 | 2 | 3; slot: number};
const DX = [330, 540, 750];
const SX = (i: number) => 150 + i * 130;
const G_DETAIL = [6, 10, 13], G_SIMPLE = [2, 1, 0, 3, 9, 8, 12];
const A_DETAIL: [number, number][] = [[1, 6], [4, 5], [3, 1]];
const GAME: T4Tile[] = [
  ...G_DETAIL.map((pid, i) => ({kind: 'game' as Kind, detail: true, idx: i, x: DX[i], y: 440, s: 130, pid, wave: (i === 1 ? 1 : 2) as 1 | 2, slot: 0})),
  ...G_SIMPLE.map((pid, i) => ({kind: 'game' as Kind, detail: false, idx: i, x: SX(i), y: 285, s: 92, pid, wave: 3 as const, slot: 0})),
];
const AI: T4Tile[] = [
  ...A_DETAIL.map((p, i) => ({kind: 'ai' as Kind, detail: true, idx: i, x: DX[i], y: 1310, s: 130, p, r: 2 * p[0] + 3 * p[1], wave: (i === 1 ? 1 : 2) as 1 | 2, slot: 0})),
  ...Array.from({length: 7}, (_, i) => ({kind: 'ai' as Kind, detail: false, idx: i, x: SX(i), y: 1462, s: 92, wave: 3 as const, slot: 0})),
];
// 排进 4 × 5 棋盘格：按 x 排序的方块 → 按「列、再行」排序的同色格子（每列交错，琥珀往下、冷白往上，像洗牌一样插进去）
const byColRow = (slots: number[]) => [...slots].sort((a, b) => (a % SLOT.cols) - (b % SLOT.cols) || Math.floor(a / SLOT.cols) - Math.floor(b / SLOT.cols));
[...GAME].sort((a, b) => a.x - b.x || a.y - b.y).forEach((g, i) => { g.slot = byColRow(SLOT_GAME)[i]; });
[...AI].sort((a, b) => a.x - b.x || a.y - b.y).forEach((g, i) => { g.slot = byColRow(SLOT_AI)[i]; });

const appearT = (w: number) => (w === 1 ? -1 : w === 2 ? E.appear2 : E.appear3);
const fills = (w: number) => (w === 1 ? [E.fill1, E.fill2, E.fill3] : w === 2 ? [E.fill2, E.fill3] : [E.fill3]);
const outT = (w: number) => (w === 1 ? E.out1 : w === 2 ? E.out2 : E.out3);
const inT = (w: number) => (w === 1 ? E.in1 : w === 2 ? E.in2 : E.in3);

const Txt: React.FC<{x: number; y: number; size: number; o?: number; color?: string; children: React.ReactNode; w?: number; weight?: number}> = ({x, y, size, o = 1, color = '#F4F6F8', children, w = 360, weight = 700}) =>
  o <= 0.001 ? null : <div style={{position: 'absolute', left: x - w / 2, top: y - size * 0.62, width: w, textAlign: 'center', fontFamily: FONT, fontWeight: weight, fontSize: size, lineHeight: `${size * 1.24}px`, color, opacity: o, whiteSpace: 'nowrap'}}>{children}</div>;

export const T4FinalMatch: React.FC = () => {
  const f = useCurrentFrame();
  const t = f / 30;
  const tF = 45 + t, fF = FILM_F0 + f;                        // 对应的全片时间 / 帧号
  // 相机推向方块层（场景放大一点、轻微虚化，仍认得出是小岛）
  const ap = prog(t, E.approach, 1.1, glide);
  const bgS = lerp(1, 1.05, prog(t, 0, 1.3, linear)) * lerp(1, 1.06, ap) * lerp(1, 1.03, prog(t, 2.4, 2.0, linear));
  const bgBlur = lerp(0, 2.5, ap), bgDim = lerp(1, 0.72, ap), ctx = 1 - prog(t, E.ctxOut, 0.4, glide);
  const FOC: [number, number] = [540, 640];
  const bgP = (p: [number, number]): [number, number] => [FOC[0] + (p[0] - FOC[0]) * bgS, FOC[1] + (p[1] - FOC[1]) * bgS];
  const k1 = prog(t, E.approach, 1.0, glide);                  // 第一个例子归位
  const rr = prog(t, E.rearr, E.handoff - E.rearr - 0.02, glide);
  const numO = 1 - prog(t, E.numOut, 0.2);
  const labO = 1 - prog(t, 3.92, 0.15);                        // 输入和参数：计算演完后先收掉，给标题让位
  // 每块地被它的方块算过以后才有明暗
  const litOf = new Map<number, number>();
  GAME.forEach((g) => litOf.set(g.pid!, prog(t, outT(g.wave) + 0.12, 0.2)));

  // 方块当前位置：开头的第一个例子大、在自己的来源旁边；之后在各自的排上；4.55 s 起插进棋盘格
  const target = (slot: number): [number, number, number] => {
    const [lx, ly] = slotXY(slot);
    const q = dieQuad(tF, fF);
    const [x, y] = dieToScreen(tF, fF, lx, ly);
    return [x, y, SLOT.size * quadScale(q, DIE.w)];
  };
  const pos = (g: T4Tile): [number, number, number] => {
    let x = g.x, y = g.y, s = g.s;
    if (g.wave === 1) {
      const p0: [number, number, number] = g.kind === 'game' ? [bgP(pp(PATCHES[g.pid!].c))[0], bgP(pp(PATCHES[g.pid!].c))[1] - 200, 160] : [790, 1230, 170];
      x = lerp(p0[0], g.x, k1); y = lerp(p0[1], g.y, k1); s = lerp(p0[2], g.s, k1);
    }
    if (rr > 0) {
      const [tx, ty, ts] = target(g.slot);
      const side = (g.kind === 'game' ? -1 : 1) * 16 * 4 * rr * (1 - rr);
      x = lerp(x, tx, rr) + side; y = lerp(y, ty, rr); s = lerp(s, ts, rr);
    }
    return [x, y, s];
  };
  const tileState = (g: T4Tile) => {
    const c = cycle(t, fills(g.wave), g.wave === 1 && t < E.approach ? E.out1 - E.fill1 : 0.3, 0.45);
    if (rr <= 0) return {fill: c.fill, lit: c.lit, lift: 0.7, opacity: 1};
    const L = lockedTile(g.slot, tF);                          // 收拢到全片 GPU 镜头里这一格的状态
    return {fill: lerp(c.fill, L.fill, rr), lit: lerp(c.lit, L.lit, rr), lift: lerp(0.7, L.lift, rr), opacity: lerp(1, L.opacity, rr)};
  };

  // AI 第一个例子：开头 [2, 3] 和 [4, 5] 大字在左；归位后 [2, 3] 在上方中间、[4, 5] 变成第一个方块头上的参数
  const inX = lerp(300, 540, k1), inY = lerp(1150, 1095, k1), inSz = lerp(100, 78, k1);
  const pX = lerp(300, DX[1], k1), pY = lerp(1310, 1212, k1), pSz = lerp(100, 42, k1);
  const headline = prog(t, E.headline, 0.15) * (1 - prog(t, E.headlineOut, 0.15));
  // 芯片轮廓（4.7 s 起淡入，5.0 s 时等于全片那一刻的透明度，之后由全片的 Die 组件接手）
  const chromeK = prog(t, E.chromeIn, E.handoff - E.chromeIn, linear);
  const handed = f >= HANDOFF_F;

  return (
    <AbsoluteFill style={{background: 'radial-gradient(ellipse 85% 60% at 50% 46%, #1F2227 0%, #17191D 70%, #121417 100%)', overflow: 'hidden'}}>
      {/* 上半屏场景 */}
      <div style={{position: 'absolute', left: 0, top: 0, width: 1080, height: 1920, opacity: ctx,
        filter: `blur(${bgBlur}px) brightness(${bgDim})`, transform: `translate(${FOC[0] * (1 - bgS)}px, ${FOC[1] * (1 - bgS)}px) scale(${bgS})`, transformOrigin: '0 0',
        WebkitMaskImage: 'linear-gradient(transparent 140px, #000 260px, #000 900px, transparent 1030px)'}}>
        <svg width={VW} height={VH} style={{position: 'absolute', left: 0, top: VTOP}}>
          {PROJ.map((p) => {
            if (!p.facing && p.tri.kind !== 'water') return null;
            const pid = triPatch.get(p.tri.id);
            const L = pid === undefined || !litOf.has(pid) ? 1 : litOf.get(pid)!;
            const lit = shadeColor(p.tri.base, p.shade).match(/\d+/g)!.map(Number);
            const flat = [p.tri.base[0] * 0.5, p.tri.base[1] * 0.5, p.tri.base[2] * 0.52];
            const col = [0, 1, 2].map((i) => Math.round(lerp(flat[i], lit[i], clamp(L))));
            const fill = `rgb(${col[0]},${col[1]},${col[2]})`;
            return <path key={p.tri.id} d={`M${p.pts[0][0]},${p.pts[0][1]}L${p.pts[1][0]},${p.pts[1][1]}L${p.pts[2][0]},${p.pts[2][1]}Z`} fill={fill} stroke={fill} strokeWidth={0.8} />;
          })}
        </svg>
      </div>
      {/* 游戏：三个带细节的例子各有一根线连回自己的地块（其余简化方块不画线） */}
      <svg width={1080} height={1920} style={{position: 'absolute', left: 0, top: 0, opacity: ctx}}>
        {GAME.filter((g) => g.detail).map((g, i) => {
          const a = g.wave === 1 ? 1 : prog(t, appearT(g.wave), 0.35);
          if (a <= 0) return null;
          const [x, y, s] = pos(g), pc = bgP(pp(PATCHES[g.pid!].c));
          return <line key={i} x1={x} y1={y + s / 2} x2={pc[0]} y2={pc[1]} stroke={C.game} strokeOpacity={0.7 * a} strokeWidth={3} />;
        })}
      </svg>
      {/* AI：问题（一小行，交代来源）+ 共享输入 [2, 3] + 第一个例子的参数 [4, 5] */}
      <Txt x={300} y={1048} size={40} o={1 - prog(t, E.approach, 0.8)} color={C.sub} weight={400} w={480}>「黑洞是什么？」</Txt>
      <Txt x={inX} y={inY} size={inSz} o={labO}>[2, 3]</Txt>
      <Txt x={pX} y={pY} size={pSz} o={labO} color={k1 > 0.5 ? '#C9D1DA' : '#F4F6F8'}>[4, 5]</Txt>
      {AI.filter((a) => a.detail && a.wave === 2).map((a, i) => (
        <Txt key={i} x={a.x} y={1212} size={42} o={prog(t, E.appear2, 0.35) * labO} color="#C9D1DA">{`[${a.p![0]}, ${a.p![1]}]`}</Txt>
      ))}
      {/* 输入到达 */}
      {[1, 2, 3].map((w) => {
        const s0 = inT(w), e0 = w === 1 ? E.fill1 : w === 2 ? E.fill2 : E.fill3;
        if (t <= s0 || t >= e0) return null;
        const k = prog(t, s0, e0 - s0 - 0.03, glide);
        return (
          <React.Fragment key={w}>
            {GAME.filter((g) => w === 3 || g.wave === w).map((g, i) => {
              const [x, y, s] = pos(g), pc = bgP(pp(PATCHES[g.pid!].c));
              return <Dot key={`g${i}`} x={lerp(pc[0], x, k)} y={lerp(pc[1], y + s / 2, k)} r={g.detail ? 11 : 8} kind="game" />;
            })}
            {AI.filter((a) => w === 3 || a.wave === w).map((a, i) => {
              const [x, y, s] = pos(a);
              const pr = a.detail ? (a.wave === 1 ? [pX, pY] : [a.x, 1212]) : null;
              return (
                <React.Fragment key={`a${i}`}>
                  <Dot x={lerp(inX, x - s * 0.15, k)} y={lerp(inY + 30, y - s / 2, k)} r={a.detail ? 11 : 8} kind="ai" />
                  {pr && <Dot x={lerp(pr[0], x + s * 0.15, k)} y={lerp(pr[1] + 20, y - s / 2, k)} r={11} kind="ai" />}
                </React.Fragment>
              );
            })}
          </React.Fragment>
        );
      })}
      {/* 输出：琥珀方块的结果落回地块 */}
      {[1, 2, 3].map((w) => {
        const s0 = outT(w);
        if (t <= s0 || t >= s0 + 0.14) return null;
        const k = prog(t, s0, 0.12, linear);
        return GAME.filter((g) => w === 3 || g.wave === w).map((g, i) => {
          const [x, y, s] = pos(g), pc = bgP(pp(PATCHES[g.pid!].c));
          return <Dot key={`o${w}${i}`} x={lerp(x, pc[0], k)} y={lerp(y + s / 2, pc[1], k)} r={g.detail ? 11 : 8} kind="game" />;
        });
      })}
      {/* 方块（交接之前） */}
      {!handed && [...GAME, ...AI].map((g, i) => {
        const a = g.wave === 1 ? 1 : prog(t, appearT(g.wave), 0.35, settle);
        if (a <= 0) return null;
        const [x, y, s] = pos(g);
        const st = tileState(g);
        const label = g.kind === 'ai' && g.detail && t >= outT(g.wave) && numO > 0 ? String(g.r) : undefined;
        return <Tile key={i} x={x} y={y + (1 - a) * 24} s={s * lerp(0.7, 1, a)} kind={g.kind} fill={st.fill} lit={st.lit} lift={st.lift} opacity={a * st.opacity}
          label={label} labelSize={s * 0.4} style={label ? undefined : undefined} />;
      })}
      {/* 交接前的芯片轮廓（几何和透明度与全片 Die 组件相同） */}
      {!handed && chromeK > 0 && (() => {
        const ch = dieChrome(tF);
        return (
          <div style={{position: 'absolute', left: 0, top: 0, width: DIE.w, height: DIE.h, transformOrigin: '0 0', transform: dieMatrix(tF, fF), opacity: chromeK}}>
            <div style={{position: 'absolute', inset: 0, borderRadius: 10, border: `6px solid ${C.metal}`, opacity: ch.outline, boxSizing: 'border-box'}} />
            {HBM_LOCAL.map(([x, y, w, h], i) => (
              <div key={i} style={{position: 'absolute', left: x, top: y, width: w, height: h, borderRadius: 8, border: `4px solid ${C.metalDim}`, opacity: ch.hbm, boxSizing: 'border-box'}} />
            ))}
            {Array.from({length: SLOT.cols * SLOT.rows}, (_, i) => {
              const [x, y] = slotXY(i);
              return <div key={i} style={{position: 'absolute', left: x - SLOT.size / 2, top: y - SLOT.size / 2, width: SLOT.size, height: SLOT.size, borderRadius: SLOT.size * 0.22,
                border: `3px dashed rgba(${C.neutralRGB},0.6)`, opacity: ch.grid * 0.6, boxSizing: 'border-box'}} />;
            })}
          </div>
        );
      })()}
      {/* 5.0 s 起：同一段 GPU 底片在格子下面浮现 + 全片的 Die 组件（同一帧号） */}
      {handed && (
        <>
          <Sequence from={HANDOFF_F} layout="none">
            <AbsoluteFill style={{opacity: prog(f, HANDOFF_F, 26, glide)}}>
              <OffthreadVideo src={staticFile('dl60/CLOSE.mp4')} startFrom={FILM_F0 + HANDOFF_F - 1455} muted style={{width: 1080, height: 1920}} />
            </AbsoluteFill>
          </Sequence>
          <Sequence from={-FILM_F0} layout="none"><Die /></Sequence>
          <Note y={1420} o={prog(f, HANDOFF_F, 15)}>示意：方块代表计算任务，不代表核心或分区</Note>
        </>
      )}
      {/* 唯一的标题：在动作演完之后，短暂出现，放在两组之间 */}
      <div style={{position: 'absolute', left: 60, right: 60, top: 1056 + (1 - prog(t, E.headline, 0.15)) * 14, textAlign: 'center', fontFamily: FONT, fontWeight: 700, fontSize: 64, letterSpacing: 2,
        color: C.ink, opacity: headline, textShadow: '0 2px 16px rgba(8,9,11,0.9)'}}>不同任务，都能并行</div>
    </AbsoluteFill>
  );
};
