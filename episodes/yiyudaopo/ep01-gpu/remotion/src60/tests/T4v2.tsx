// EP01 · T4 VISUAL RECONSTRUCTION V02（6 秒，180 帧）
// 两种不同的任务，一个共同的计算优势：
//   上半屏：小岛山坡的大特写（游戏），琥珀方块用细线连着各自的地块；下半屏：一道大字的 AI 计算，冷白方块。
//   0–1.5 s   各算一次（AI 晚 0.3 s 开始，结果同时出来）：输入到达 → 计算 → 输出（地块变亮 / 出数字）
//   1.5–3 s   相机往「方块那一层」推：背景场景放大、虚化、变暗；一个计算变成 6 个同类的独立计算，同时出结果（第 90 帧已能看出共同点）
//   3–4.5 s   再扩到每边 12 个，24 个一起算、一起出结果；之后才出一行标题「不同任务，都能并行」
//   4.5–5 s   两组排进一个大矩形（26:31，4 列 × 6 行；琥珀在上三行、冷白在下三行），宽 800 px
//   5–6 s     矩形缩放到 GPU 俯视底片第 1620 帧里芯片的屏幕位置 (220, 628)–(860, 1392)
import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {clamp, cycle, glide, lerp, linear, prog, settle} from '../lib/core';
import {PATCHES, Patch} from '../lib/island';
import {buildScene, Cam, dot, project, shadeColor, V3} from '../lib/terrain';
import {C, FONT} from '../lib/theme';
import {Dot, Tile} from '../Tile';
import CLOSE from '../anchors/CLOSE.json';

// ------------------------------------------------------------------ 时间（秒）
export const TV = {
  g0: 0.15, a0: 0.45, fill0: 0.6, out0: 1.1,                 // 第一次：游戏先、AI 后，结果同时
  approach: 1.3, appear1: 1.55, in1: 2.3, fill1: 2.55, out1: 2.95,
  appear2: 2.95, in2: 3.35, fill2: 3.55, out2: 3.95,
  headline: 4.0, headlineOut: 4.62,
  organize: 4.6, align: 5.0, end: 179 / 30,
};
// GPU 俯视底片（dl60_scenes.py CLOSE）第 1620 帧的芯片四角——终帧对齐目标
const CF = (CLOSE as unknown as {f0: number; frames: {die: [number, number][]}[]});
export const TARGET_FRAME = 1620;
const TQ = CF.frames[TARGET_FRAME - CF.f0].die;
export const TARGET = {x: TQ[0][0], y: TQ[0][1], w: TQ[1][0] - TQ[0][0], h: TQ[3][1] - TQ[0][1]};
// 4.6–5 s 的大矩形（26:31），宽 800 px
const BIG = {w: 800, h: 800 * 31 / 26};
const BIGR = {x: 540 - BIG.w / 2, y: 960 - BIG.h / 2, w: BIG.w, h: BIG.h};
const COLS = 6, ROWS = 4;               // 列不变、只上下收拢：琥珀两排 → 上两行，冷白两排 → 下两行（不交叉）
const slotLocal = (i: number): [number, number] => [((i % COLS) + 0.5) / COLS, (Math.floor(i / COLS) + 0.5) / ROWS];

// ------------------------------------------------------------------ 上半屏：小岛山坡特写
const TRI = buildScene();
const VW = 1080, VH = 800, VTOP = 220;                      // 视口在屏幕上的位置
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
// 12 个地块：近的 6 个 → 下排（A），远的 6 个 → 上排（B），各按 x 排列（连线尽量不交叉）
const NEAR = [2, 1, 6, 10, 13, 12], FAR = [0, 3, 9, 8, 7, 11];
const FIRST_G = 10;                                          // 第一个演示的地块（前坡）
const COLX = (i: number) => 120 + i * 168;
const ROW_A = 390, ROW_B = 238, GS = 120;                     // 琥珀两排
type GT = {pid: number; x: number; y: number; wave: number; order: number};
const GT_LIST: GT[] = [
  ...NEAR.map((pid, i) => ({pid, x: COLX(i), y: ROW_A, wave: pid === FIRST_G ? 0 : 1, order: 0})),
  ...FAR.map((pid, i) => ({pid, x: COLX(i), y: ROW_B, wave: 2, order: 0})),
];
// 排进大矩形的顺序：先上排（B）再下排（A），各按 x
[...GT_LIST].sort((a, b) => a.y - b.y || a.x - b.x).forEach((g, i) => { g.order = i; });

// ------------------------------------------------------------------ 下半屏：AI 计算
const IN = {x: 540, y: 1040};                                 // 共享的输入 [2, 3]
const ROW_C = 1222, ROW_D = 1372, AS = 120;
const PARAMS: [number, number][] = [[1, 6], [3, 1], [2, 2], [4, 5], [5, 1], [1, 2], [3, 3], [2, 1], [4, 1], [1, 4], [5, 2], [3, 2]];
const FIRST_A = 3;                                            // [4, 5] → 23，放在第 4 列（和琥珀那一块上下对齐）
type AT = {p: [number, number]; r: number; x: number; y: number; wave: number; order: number};
const AT_LIST: AT[] = PARAMS.map((p, i) => ({p, r: 2 * p[0] + 3 * p[1], x: COLX(i % 6), y: i < 6 ? ROW_C : ROW_D, wave: i === FIRST_A ? 0 : i < 6 ? 1 : 2, order: i}));

const appearT = (wave: number) => (wave === 0 ? -1 : wave === 1 ? TV.appear1 : TV.appear2);
const fillStarts = (wave: number) => (wave === 0 ? [TV.fill0, TV.fill2] : wave === 1 ? [TV.fill1, TV.fill2] : [TV.fill2]);

const Txt: React.FC<{x: number; y: number; size: number; o?: number; color?: string; children: React.ReactNode; w?: number; weight?: number}> = ({x, y, size, o = 1, color = '#F4F6F8', children, w = 300, weight = 700}) =>
  o <= 0.001 ? null : <div style={{position: 'absolute', left: x - w / 2, top: y - size * 0.62, width: w, textAlign: 'center', fontFamily: FONT, fontWeight: weight, fontSize: size, lineHeight: `${size * 1.24}px`, color, opacity: o, whiteSpace: 'nowrap'}}>{children}</div>;

export const T4v2: React.FC = () => {
  const f = useCurrentFrame();
  const t = f / 30;
  // 相机往方块那一层推：背景（场景）放大、虚化、变暗；4.5 s 起退场
  const ap = prog(t, TV.approach, 1.7, glide);
  // 推镜从第 0 帧就慢慢开始（0–1.3 s 约 7%），1.3 s 起加速
  const bgS = lerp(1, 1.07, prog(t, 0, 1.3, linear)) * lerp(1, 1.09, ap) * lerp(1, 1.05, prog(t, 3.0, 1.5, linear));
  const bgBlur = lerp(0, 5, ap), bgDim = lerp(1, 0.5, ap), bgOut = 1 - prog(t, TV.organize - 0.1, 0.45, glide);
  const FOC: [number, number] = [540, 640];
  const bgP = (p: [number, number]): [number, number] => [FOC[0] + (p[0] - FOC[0]) * bgS, FOC[1] + (p[1] - FOC[1]) * bgS];
  const org = prog(t, TV.organize, 0.5, glide);              // 排进大矩形
  const al = prog(t, TV.align, 0.95, settle);                // 缩放到 GPU 芯片位置
  const R = {x: lerp(BIGR.x, TARGET.x, al), y: lerp(BIGR.y, TARGET.y, al), w: lerp(BIGR.w, TARGET.w, al), h: lerp(BIGR.h, TARGET.h, al)};
  const slotXY = (i: number): [number, number] => { const [u, v] = slotLocal(i); return [R.x + u * R.w, R.y + v * R.h]; };
  const slotS = (R.w / COLS) * 0.8;
  const ctx = 1 - org;                                        // 来源的上下文（连线、参数、输入）

  // 地块光照：每个地块被「它的」方块算过以后才有明暗
  const patchLit = (pid: number) => {
    const g = GT_LIST.find((x) => x.pid === pid);
    if (!g) return 1;
    const out = g.wave === 0 ? TV.out0 : g.wave === 1 ? TV.out1 : TV.out2;
    return prog(t, out, 0.25);
  };
  // 第一个琥珀方块：开头大、在自己的地块正上方；1.5 s 起和其它方块一起排成两排
  const firstG = (g: GT): [number, number, number] => {
    const pc = bgP(pp(PATCHES[FIRST_G].c));
    const k = prog(t, TV.approach, 1.1, glide);
    return [lerp(pc[0], g.x, k), lerp(pc[1] - 190, g.y, k), lerp(160, GS, k)];
  };
  const firstA = (a: AT): [number, number, number] => {
    const k = prog(t, TV.approach, 1.1, glide);
    return [lerp(790, a.x, k), lerp(1240, a.y, k), lerp(170, AS, k)];
  };
  const gPos = (g: GT): [number, number, number] => {
    const [x0, y0, s0] = g.wave === 0 ? firstG(g) : [g.x, g.y, GS];
    if (org <= 0) return [x0, y0, s0];
    const [x1, y1] = slotXY((g.y === ROW_B ? 0 : COLS) + Math.round((g.x - 120) / 168));
    return [lerp(x0, x1, org), lerp(y0, y1, org), lerp(s0, slotS, org)];
  };
  const aPos = (a: AT): [number, number, number] => {
    const [x0, y0, s0] = a.wave === 0 ? firstA(a) : [a.x, a.y, AS];
    if (org <= 0) return [x0, y0, s0];
    const [x1, y1] = slotXY(2 * COLS + a.order);
    return [lerp(x0, x1, org), lerp(y0, y1, org), lerp(s0, slotS, org)];
  };
  // 第一次计算之前的 AI 版式：[2, 3] 和 [4, 5] 大字在左边，方块在右边；1.5 s 起 [2, 3] 上移到中间、[4, 5] 收进方块当标签
  const k1 = prog(t, TV.approach, 1.1, glide);
  const inX = lerp(300, IN.x, k1), inY = lerp(1120, IN.y, k1), inSz = lerp(108, 76, k1);
  const pX = lerp(300, firstA(AT_LIST[FIRST_A])[0], k1), pY = lerp(1330, firstA(AT_LIST[FIRST_A])[1] - 30, k1), pSz = lerp(108, 26, k1);
  const headline = prog(t, TV.headline, 0.3) * (1 - prog(t, TV.headlineOut, 0.3));

  return (
    <AbsoluteFill style={{background: 'radial-gradient(ellipse 90% 70% at 50% 48%, #1F2227 0%, #17191D 70%, #131518 100%)', overflow: 'hidden'}}>
      {/* 上半屏的场景（背景层） */}
      <div style={{position: 'absolute', left: 0, top: 0, width: 1080, height: 1920, opacity: bgOut,
        filter: `blur(${bgBlur}px) brightness(${bgDim})`, transform: `translate(${FOC[0] * (1 - bgS)}px, ${FOC[1] * (1 - bgS)}px) scale(${bgS})`, transformOrigin: '0 0',
        WebkitMaskImage: 'linear-gradient(transparent 120px, #000 260px, #000 880px, transparent 1010px)'}}>
        <svg width={VW} height={VH} style={{position: 'absolute', left: 0, top: VTOP}}>
          {PROJ.map((p) => {
            if (!p.facing && p.tri.kind !== 'water') return null;
            const pid = triPatch.get(p.tri.id);
            const L = pid === undefined ? 1 : patchLit(pid);
            const lit = shadeColor(p.tri.base, p.shade).match(/\d+/g)!.map(Number);
            const flat = [p.tri.base[0] * 0.55, p.tri.base[1] * 0.55, p.tri.base[2] * 0.57];
            const col = [0, 1, 2].map((i) => Math.round(lerp(flat[i], lit[i], clamp(L))));
            const fill = `rgb(${col[0]},${col[1]},${col[2]})`;
            return <path key={p.tri.id} d={`M${p.pts[0][0]},${p.pts[0][1]}L${p.pts[1][0]},${p.pts[1][1]}L${p.pts[2][0]},${p.pts[2][1]}Z`} fill={fill} stroke={fill} strokeWidth={0.8} />;
          })}
        </svg>
      </div>
      {/* 下半屏的上下文：问题（只留一小行） */}
      <Txt x={300} y={985} size={40} o={1 - prog(t, TV.approach, 1.0)} color={C.sub} weight={400} w={460}>「黑洞是什么？」</Txt>
      {/* 连线：琥珀方块 ↔ 自己的地块；输入 [2, 3] → 每个冷白方块 */}
      <svg width={1080} height={1920} style={{position: 'absolute', left: 0, top: 0}}>
        {GT_LIST.map((g, i) => {
          const a = g.wave === 0 ? 1 : prog(t, appearT(g.wave), 0.4);
          if (a <= 0) return null;
          const [x, y, s] = gPos(g), pc = bgP(pp(PATCHES[g.pid].c));
          return <line key={i} x1={x} y1={y + s / 2} x2={pc[0]} y2={pc[1]} stroke={C.game} strokeOpacity={0.6 * a * ctx} strokeWidth={g.wave === 0 ? 3 : 2} />;
        })}
        {AT_LIST.map((a, i) => {
          const o = a.wave === 0 ? k1 : prog(t, appearT(a.wave), 0.4);
          if (o <= 0) return null;
          const [x, y, s] = aPos(a);
          return <line key={i} x1={inX} y1={inY + 52} x2={x} y2={y - s / 2} stroke={C.ai} strokeOpacity={0.3 * o * ctx} strokeWidth={2} />;
        })}
        {/* 选中地块的琥珀描边（开头） */}
      </svg>
      {/* 输入 [2, 3]（AI 的共享输入） */}
      <div style={{position: 'absolute', left: inX - lerp(200, 150, k1), top: inY - lerp(80, 58, k1), width: lerp(400, 300, k1), height: lerp(160, 116, k1), borderRadius: 30,
        border: `3px solid rgba(${C.aiRGB},0.6)`, boxSizing: 'border-box', opacity: ctx}} />
      <Txt x={inX - lerp(80, 60, k1)} y={inY} size={inSz} o={ctx}>2</Txt>
      <Txt x={inX + lerp(80, 60, k1)} y={inY} size={inSz} o={ctx}>3</Txt>
      {/* 第一道的参数 [4, 5]：开头大字，之后收进它的方块当标签 */}
      {k1 < 1 && (
        <>
          <div style={{position: 'absolute', left: pX - lerp(200, 40, k1), top: pY - lerp(80, 18, k1), width: lerp(400, 80, k1), height: lerp(160, 36, k1), borderRadius: lerp(30, 8, k1),
            border: `3px solid rgba(${C.aiRGB},${0.6 * (1 - k1)})`, boxSizing: 'border-box'}} />
          <Txt x={pX - lerp(80, 14, k1)} y={pY} size={pSz}>4</Txt>
          <Txt x={pX + lerp(80, 14, k1)} y={pY} size={pSz}>5</Txt>
        </>
      )}
      {/* 输入到达 */}
      {[{s: TV.g0, e: TV.fill0, list: GT_LIST.filter((g) => g.wave === 0)}, {s: TV.in1, e: TV.fill1, list: GT_LIST.filter((g) => g.wave === 1)}, {s: TV.in2, e: TV.fill2, list: GT_LIST}].map(({s, e, list}, wi) =>
        t > s && t < e ? list.map((g, i) => {
          const k = prog(t, s, e - s - 0.03, glide);
          const [x, y, sz] = gPos(g), pc = bgP(pp(PATCHES[g.pid].c));
          return <Dot key={`g${wi}${i}`} x={lerp(pc[0], x, k)} y={lerp(pc[1], y + sz / 2, k)} r={g.wave === 0 && wi === 0 ? 12 : 9} kind="game" />;
        }) : null,
      )}
      {[{s: TV.a0, e: TV.fill0, list: AT_LIST.filter((a) => a.wave === 0)}, {s: TV.in1, e: TV.fill1, list: AT_LIST.filter((a) => a.wave === 1)}, {s: TV.in2, e: TV.fill2, list: AT_LIST}].map(({s, e, list}, wi) =>
        t > s && t < e ? list.map((a, i) => {
          const k = prog(t, s, e - s - 0.03, glide);
          const [x, y, sz] = aPos(a);
          if (wi === 0) {
            // 第一次：两个数分别从 [2, 3] 和 [4, 5] 飞进方块
            return (
              <React.Fragment key={`a${wi}${i}`}>
                <Dot x={lerp(inX + 120, x - sz / 2, k)} y={lerp(inY, y - 20, k)} r={12} kind="ai" />
                <Dot x={lerp(pX + 120, x - sz / 2, k)} y={lerp(pY, y + 20, k)} r={12} kind="ai" />
              </React.Fragment>
            );
          }
          return <Dot key={`a${wi}${i}`} x={lerp(inX, x, k)} y={lerp(inY + 52, y - sz / 2, k)} r={9} kind="ai" />;
        }) : null,
      )}
      {/* 输出：琥珀方块的结果落回地块（地块随之变亮） */}
      {[{s: TV.out0, list: GT_LIST.filter((g) => g.wave === 0)}, {s: TV.out1, list: GT_LIST.filter((g) => g.wave === 1)}, {s: TV.out2, list: GT_LIST.filter((g) => g.wave === 2)}].map(({s, list}, wi) =>
        t > s && t < s + 0.28 ? list.map((g, i) => {
          const k = prog(t, s, 0.25, linear);
          const [x, y, sz] = gPos(g), pc = bgP(pp(PATCHES[g.pid].c));
          return <Dot key={`o${wi}${i}`} x={lerp(x, pc[0], k)} y={lerp(y + sz / 2, pc[1], k)} r={9} kind="game" />;
        }) : null,
      )}
      {/* 琥珀方块 */}
      {GT_LIST.map((g, i) => {
        const a = g.wave === 0 ? 1 : prog(t, appearT(g.wave), 0.4, settle);
        if (a <= 0) return null;
        const [x, y, s] = gPos(g);
        const {fill, lit} = cycle(t, fillStarts(g.wave), g.wave === 0 && t < TV.approach ? TV.out0 - TV.fill0 : 0.4, 0.45);
        return <Tile key={i} x={x} y={y + (1 - a) * 30} s={s * lerp(0.7, 1, a)} kind="game" fill={fill} lit={lit} lift={0.7} opacity={a} />;
      })}
      {/* 冷白方块：上面一行小字是参数，结果在中间 */}
      {AT_LIST.map((a, i) => {
        const o = a.wave === 0 ? 1 : prog(t, appearT(a.wave), 0.4, settle);
        if (o <= 0) return null;
        const [x, y, s] = aPos(a);
        const {fill, lit} = cycle(t, fillStarts(a.wave), a.wave === 0 && t < TV.approach ? TV.out0 - TV.fill0 : 0.4, 0.45);
        const shown = t >= (a.wave === 0 ? TV.out0 : a.wave === 1 ? TV.out1 : TV.out2);
        const tag = a.wave === 0 ? k1 : 1;
        return (
          <React.Fragment key={i}>
            <Tile x={x} y={y + (1 - o) * 30} s={s * lerp(0.7, 1, o)} kind="ai" fill={fill} lit={lit} lift={0.7} opacity={o} label={shown ? String(a.r) : undefined} labelSize={s * 0.38} />
            <Txt x={x} y={y - s * 0.29} size={s * 0.25} o={o * tag * ctx * 0.85} color="#C9D1DA" weight={400} w={s}>{`${a.p[0]}, ${a.p[1]}`}</Txt>
          </React.Fragment>
        );
      })}
      {/* 大矩形 → GPU 芯片区域的轮廓 */}
      <div style={{position: 'absolute', left: R.x, top: R.y, width: R.w, height: R.h, borderRadius: 10, border: `5px solid ${C.metal}`, boxSizing: 'border-box', opacity: org}} />
      <div style={{position: 'absolute', left: R.x + 18, top: R.y + R.h / 2 - 1, width: R.w - 36, height: 2, background: `rgba(${C.neutralRGB},0.35)`, opacity: org}} />
      {/* 唯一的标题：在动画已经演完之后，短暂出现，放在两组之间的空当 */}
      <div style={{position: 'absolute', left: 60, right: 60, top: 868 + (1 - prog(t, TV.headline, 0.3)) * 16, textAlign: 'center', fontFamily: FONT, fontWeight: 700, fontSize: 64, letterSpacing: 2,
        color: C.ink, opacity: headline, textShadow: '0 2px 16px rgba(8,9,11,0.9)'}}>不同任务，都能并行</div>
    </AbsoluteFill>
  );
};
export const unusedV2 = [dot];
