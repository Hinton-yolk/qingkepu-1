// TEST B — T4：两种计算 → 共同点（6 秒，180 帧）
// 和 T2 同一张桌面：左前方游戏沙盘，右后方 AI 面板（停在 SHOT 04 的状态：23、20 两行）。
//   0–1.5  两边同框、都占大面积
//   1.5–3  各选一个方块，拉到画面中间（连线连回各自的来源），同步演「输入 → 计算 → 输出」
//   3–4.5  两边各自冒出更多同类计算，一起算；相机只退一点；第 115 帧出唯一一行标题
//   4.5–6  两股方块飞向桌面前方的一块「芯片格板」（26:31，4 × 5 格，左两列琥珀、右两列冷白），相机升到正上方
//          最后一帧：格板在屏幕上是一个正的矩形（宽约 700 px），可以直接对上 GPU 俯视镜头
import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {cycle, glide, lerp, linear, prog, settle} from '../lib/core';
import {PATCHES, SEL, Patch} from '../lib/island';
import {V3} from '../lib/terrain';
import {C, FONT} from '../lib/theme';
import {Dot, Tile, Kind} from '../Tile';
import {ringPath, Stage3D} from './Stage3D';
import {camPath, cardLocal, H, proj, projPoly, pxPerUnit, TABLE_Y, view, View, W} from './world3d';

export const K4 = {
  pick: 1.5, inA: 2.05, op: 2.45, out: 2.95, done: 3.3,
  expand: 3.05, all: 3.6, headline: 115 / 30, slabIn: 4.35, stream0: 4.5, final: 6.0,
};
// 芯片格板：躺在桌面上、沙盘正前方；长边沿 z（俯视时竖着），26:31
export const SLAB = {cx: 2.4, cz: 13.6, w: 8.6, h: 8.6 * 31 / 26, y: TABLE_Y + 0.06, cols: 4, rows: 5};
const D_TOP = (SLAB.w * (0.5 * 1920 / Math.tan(0.31))) / 700;      // 最后一帧格板宽约 700 px
export const cam4 = camPath(
  [0, 1.5, 3.0, 4.5, 6.0],
  [3.4, 3.3, 3.25, 3.2, SLAB.cx],
  [4.5, 4.5, 4.55, 4.6, SLAB.y],
  [-3.0, -2.6, -2.4, -2.2, SLAB.cz],
  [44, 42.5, 43.5, 45, D_TOP],
  [0.30, 0.305, 0.31, 0.31, 1.52],
  [0.25, 0.24, 0.235, 0.23, 0.0],
);
const slotWorld = (i: number): V3 => {
  const c = i % SLAB.cols, r = Math.floor(i / SLAB.cols);
  return [SLAB.cx - SLAB.w / 2 + (c + 0.5) * (SLAB.w / SLAB.cols), SLAB.y + 0.01, SLAB.cz - SLAB.h / 2 + (r + 0.5) * (SLAB.h / SLAB.rows)];
};
const SLOT_SIZE = 1.4;                                                   // 世界单位
const GAME_SLOTS = [0, 1, 4, 5, 8, 9, 12, 13, 16, 17], AI_SLOTS = [2, 3, 6, 7, 10, 11, 14, 15, 18, 19];

// AI 面板：SHOT 04 的布局（本地 1080 × 1920）
const X1 = 330, X2 = 530, VC = 430, TX = 830;
const ROWS = [
  {y: 830, sc: 1, p: [4, 5], r: 23}, {y: 1010, sc: 1, p: [1, 6], r: 20},
  {y: 1160, sc: 0.8, p: [3, 1], r: 9}, {y: 1290, sc: 0.8, p: [2, 2], r: 10}, {y: 1420, sc: 0.8, p: [5, 1], r: 13},
  ...[0, 1, 2, 3, 4].map((k) => ({y: 1530 + k * 86, sc: 0.62, p: null as null | number[], r: 0})),
];
const rowEnter = (i: number) => (i < 2 ? -1 : K4.expand + (i - 2) * 0.09);
// 被选出来的两个方块在世界里的「中间位置」（由 t = 2.25 时的相机反投影得到：屏幕 (380, 900) 和 (700, 900)，深度 30）
function unproject(v: View, sx: number, sy: number, depth: number): V3 {
  const dx = (sx - W / 2) / v.f, dy = -(sy - H / 2) / v.f;
  return [0, 1, 2].map((k) => v.eye[k] + depth * (v.fwd[k] + dx * v.right[k] + dy * v.up[k])) as V3;
}
const vMid = view(cam4(2.25));
const MID_G = unproject(vMid, 360, 930, 30), MID_A = unproject(vMid, 720, 930, 30);

const Txt: React.FC<{x: number; y: number; size: number; o?: number; color?: string; children: React.ReactNode; w?: number}> = ({x, y, size, o = 1, color = '#F4F6F8', children, w = 160}) =>
  o <= 0.001 ? null : <div style={{position: 'absolute', left: x - w / 2, top: y - size * 0.62, width: w, textAlign: 'center', fontFamily: FONT, fontWeight: 700, fontSize: size, lineHeight: `${size * 1.24}px`, color, opacity: o, whiteSpace: 'nowrap'}}>{children}</div>;

const aiCycles = (i: number) => (i === 0 ? [K4.op, K4.all] : [K4.all]);
const CardContent: React.FC<{t: number}> = ({t}) => (
  <>
    <div style={{position: 'absolute', left: VC - 175, top: 640 - 70, width: 350, height: 140, borderRadius: 30, border: `3px solid rgba(${C.aiRGB},0.6)`, boxSizing: 'border-box'}} />
    <Txt x={X1} y={640} size={104}>2</Txt><Txt x={X2} y={640} size={104}>3</Txt>
    {[X1, X2].map((x) => <div key={x} style={{position: 'absolute', left: x - 1.5, top: 712, width: 3, height: (t < K4.expand ? 1010 : 1420 + 455 * prog(t, K4.expand + 0.3, 0.8)) - 712 * (1) + 0, background: `rgba(${C.aiRGB},0.22)`}} />)}
    {ROWS.map((row, i) => {
      const a = i < 2 ? 1 : prog(t, rowEnter(i), 0.5, settle);
      if (a <= 0) return null;
      const sc = row.sc, rise = (1 - a) * 70;
      const {fill, lit} = cycle(t, aiCycles(i), 0.5);
      const away = i === 0 ? prog(t, K4.pick, 0.6) : t >= departAI(i) ? 1 : 0;     // 这一行的方块被拿走（拉到中间 / 流向格板）
      return (
        <React.Fragment key={i}>
          <div style={{position: 'absolute', left: VC - 175 * sc, top: row.y + rise - 70 * sc, width: 350 * sc, height: 140 * sc, borderRadius: 30 * sc, border: `${2.5}px solid rgba(${C.aiRGB},${row.p ? 0.55 : 0.3})`, boxSizing: 'border-box', opacity: a}} />
          {row.p ? (<><Txt x={X1} y={row.y + rise} size={104 * sc} o={a}>{row.p[0]}</Txt><Txt x={X2} y={row.y + rise} size={104 * sc} o={a}>{row.p[1]}</Txt></>) : (
            <><div style={{position: 'absolute', left: X1 - 40, top: row.y + rise - 6, width: 80, height: 12, borderRadius: 6, background: `rgba(${C.aiRGB},0.3)`, opacity: a}} />
              <div style={{position: 'absolute', left: X2 - 40, top: row.y + rise - 6, width: 80, height: 12, borderRadius: 6, background: `rgba(${C.aiRGB},0.3)`, opacity: a}} /></>
          )}
          <Txt x={680} y={row.y + rise} size={56 * sc} o={a * 0.55} color={C.sub} w={100}>→</Txt>
          {/* 方块离开后，原位留一个空位（来源一直看得见） */}
          <Tile x={TX} y={row.y + rise} s={150 * sc} kind="neutral" empty={1} opacity={a * away * 0.8} />
          <Tile x={TX} y={row.y + rise} s={150 * sc} kind="ai" fill={fill} lit={lit} lift={0.5} opacity={a * (1 - away)}
            label={row.p && (i < 2 || t > K4.all + 0.45) ? String(row.r) : undefined} labelSize={64 * sc} />
        </React.Fragment>
      );
    })}
  </>
);

// 流向格板的方块：每个都有出发时间、来源位置（世界）、目标格
type Mover = {kind: Kind; slot: number; depart: number; from: (t: number) => [V3, number]};
function departAI(i: number) { return K4.stream0 + 0.035 + i * 0.07; }
function departGame(j: number) { return K4.stream0 + j * 0.07; }
const TRAVEL = 0.85;
const MID_S = 1.7;

export const T4Test: React.FC = () => {
  const f = useCurrentFrame();
  const t = f / 30;
  const cam = cam4(t);
  const v = view(cam);
  const sel = PATCHES[SEL];
  // 游戏这一边：起初 5 块地上有方块，3 秒后所有地块都有
  const byOrder = [...PATCHES].sort((a, b) => a.order - b.order);
  const initial = new Set(byOrder.slice(0, 6).map((p) => p.id));
  const streamGame = [sel.id, ...byOrder.filter((p) => p.id !== sel.id).slice(0, 9).map((p) => p.id)];
  const tileAppear = (p: Patch) => (initial.has(p.id) ? 1 : prog(t, K4.expand + p.order * 0.03, 0.35));
  const patchLit = (p: Patch) => (p.id === SEL ? 1 - prog(t, 1.65, 0.25) + prog(t, K4.done, 0.25) : 1);
  const hover = (p: Patch): V3 => [p.c[0], p.c[1] + 1.4, p.c[2]];
  const gameCyc = (p: Patch) => (p.id === SEL ? [K4.op, K4.all] : [K4.all]);

  // 选中的两块：从来源拉到中间
  const pk = prog(t, K4.pick, 0.9, glide);
  const gSrc = hover(sel), aSrc = cardLocal(TX, ROWS[0].y, 0.3);
  const gPos: V3 = [lerp(gSrc[0], MID_G[0], pk), lerp(gSrc[1], MID_G[1], pk) + 3 * 4 * pk * (1 - pk) * 0.3, lerp(gSrc[2], MID_G[2], pk)];
  const aPos: V3 = [lerp(aSrc[0], MID_A[0], pk), lerp(aSrc[1], MID_A[1], pk), lerp(aSrc[2], MID_A[2], pk)];

  const movers: Mover[] = [
    ...streamGame.map((id, j) => ({kind: 'game' as Kind, slot: GAME_SLOTS[j], depart: departGame(j),
      from: (): [V3, number] => (id === SEL ? [gPos, MID_S] : [hover(PATCHES[id]), 0.66])})),
    ...ROWS.map((r, i) => ({kind: 'ai' as Kind, slot: AI_SLOTS[i], depart: departAI(i),
      from: (): [V3, number] => (i === 0 ? [aPos, MID_S] : [cardLocal(TX, r.y, 0.1), (150 * r.sc / 1080) * 11])})),
  ];
  const moverPos = (m: Mover): [V3, number] => {
    const [a, sa] = m.from(t);
    const k = prog(t, m.depart, TRAVEL, glide);
    if (k <= 0) return [a, sa];
    const b = slotWorld(m.slot);
    const arcH = 3 * 4 * k * (1 - k);
    return [[lerp(a[0], b[0], k), lerp(a[1], b[1], k) + arcH, lerp(a[2], b[2], k)], lerp(sa, SLOT_SIZE, k)];
  };

  // 芯片格板
  const slabIn = prog(t, K4.slabIn, 0.6, glide);
  const sc = (x: number, z: number): V3 => [x, SLAB.y, z];
  const slab = projPoly(v, [sc(SLAB.cx - SLAB.w / 2, SLAB.cz - SLAB.h / 2), sc(SLAB.cx + SLAB.w / 2, SLAB.cz - SLAB.h / 2), sc(SLAB.cx + SLAB.w / 2, SLAB.cz + SLAB.h / 2), sc(SLAB.cx - SLAB.w / 2, SLAB.cz + SLAB.h / 2)]);
  const slabPath = slab.length ? 'M' + slab.map((p) => p.join(',')).join('L') + 'Z' : '';
  const slotPaths = Array.from({length: 20}, (_, i) => {
    const c = slotWorld(i), h = SLOT_SIZE / 2;
    const q = projPoly(v, [[c[0] - h, c[1], c[2] - h], [c[0] + h, c[1], c[2] - h], [c[0] + h, c[1], c[2] + h], [c[0] - h, c[1], c[2] + h]]);
    return q.length ? 'M' + q.map((p) => p.join(',')).join('L') + 'Z' : '';
  });
  const slabEl = (
    <svg width={W} height={H} style={{position: 'absolute', left: 0, top: 0, opacity: slabIn}}>
      <path d={slabPath} fill="#202329" stroke={C.metal} strokeWidth={4} strokeLinejoin="round" />
      {slotPaths.map((d, i) => <path key={i} d={d} fill="none" stroke={`rgba(${C.neutralRGB},0.55)`} strokeWidth={2} strokeDasharray="7 6" />)}
    </svg>
  );

  const link = (a: V3, b: V3, color: string, o: number) => { const p = proj(v, a), q = proj(v, b); return <line x1={p[0]} y1={p[1]} x2={q[0]} y2={q[1]} stroke={color} strokeOpacity={o} strokeWidth={3} />; };
  const gP = proj(v, gPos), aP = proj(v, aPos);
  const gS = MID_S * pxPerUnit(v, gPos), aS = MID_S * pxPerUnit(v, aPos);
  const cg = cycle(t, [K4.op, K4.all], 0.5), ca = cycle(t, [K4.op, K4.all], 0.5);
  const linkO = prog(t, K4.pick, 0.3) * (1 - prog(t, K4.stream0, 0.4));
  const patchBase = proj(v, [sel.c[0], sel.c[1] + 0.05, sel.c[2]]);
  const rowSrc = proj(v, cardLocal(TX, ROWS[0].y, 0.05));
  const inSrc = proj(v, cardLocal(VC, 640, 0.05));
  const fade = 1 - prog(t, 5.2, 0.7);                  // 来源（沙盘、面板）在相机升起时退到背景

  return (
    <AbsoluteFill style={{background: '#17191D', overflow: 'hidden'}}>
      <Stage3D cam={cam} lit={patchLit} dim={(p) => (p && p.id === SEL ? 1 : 0.95)} card={<CardContent t={t} />} islandOpacity={fade} cardOpacity={fade} extraTable={slabEl} />
      <svg width={W} height={H} style={{position: 'absolute', left: 0, top: 0}}>
        <path d={ringPath(v, sel)} fill="none" stroke={C.game} strokeWidth={4} strokeLinejoin="round" opacity={fade} />
        {/* 连线：中间的两块一直连回各自的来源 */}
        {linkO > 0 && <line x1={patchBase[0]} y1={patchBase[1]} x2={gP[0]} y2={gP[1] + gS * 0.5} stroke={C.game} strokeOpacity={0.8 * linkO} strokeWidth={3} />}
        {linkO > 0 && <line x1={rowSrc[0]} y1={rowSrc[1]} x2={aP[0]} y2={aP[1]} stroke={C.ai} strokeOpacity={0.7 * linkO} strokeWidth={3} strokeDasharray="2 0" />}
        {PATCHES.map((p) => {
          if (p.id === SEL || tileAppear(p) <= 0) return null;
          const m = movers.find((mm) => mm.kind === 'game' && streamGame[GAME_SLOTS.indexOf(mm.slot)] === p.id);
          if (m && t >= m.depart) return null;
          const top = proj(v, hover(p)), base = proj(v, [p.c[0], p.c[1] + 0.05, p.c[2]]);
          return <line key={p.id} x1={base[0]} y1={base[1]} x2={top[0]} y2={top[1]} stroke={C.game} strokeOpacity={0.4 * tileAppear(p) * fade} strokeWidth={1.5} />;
        })}
      </svg>
      {/* 游戏地块上的方块（还没出发的） */}
      {PATCHES.map((p) => {
        if (p.id === SEL) return null;
        const a = tileAppear(p);
        if (a <= 0) return null;
        const j = streamGame.indexOf(p.id);
        if (j >= 0 && t >= departGame(j)) return null;
        const q = proj(v, hover(p)), u = pxPerUnit(v, hover(p));
        const {fill, lit} = cycle(t, gameCyc(p), 0.5);
        return <Tile key={p.id} x={q[0]} y={q[1] - (1 - a) * 20} s={0.66 * u * lerp(0.6, 1, a)} kind="game" fill={fill} lit={Math.max(lit, 0.4)} lift={0.5} opacity={a * (j >= 0 ? 1 : fade)} />;
      })}
      {/* 输入 → 计算 → 输出（两边同步） */}
      {t > K4.inA && t < K4.op && (() => {
        const k = prog(t, K4.inA, K4.op - K4.inA - 0.03, glide);
        return (<>
          <Dot x={lerp(patchBase[0], gP[0], k)} y={lerp(patchBase[1], gP[1] + gS * 0.5, k)} r={11} kind="game" />
          <Dot x={lerp(inSrc[0] - 30, aP[0], k)} y={lerp(inSrc[1], aP[1], k)} r={10} kind="ai" />
          <Dot x={lerp(inSrc[0] + 30, aP[0], k)} y={lerp(inSrc[1], aP[1], k)} r={10} kind="ai" />
        </>);
      })()}
      {t > K4.out && t < K4.done && (() => {
        const k = prog(t, K4.out, K4.done - K4.out, linear);
        return (<>
          <Dot x={lerp(gP[0], patchBase[0], k)} y={lerp(gP[1] + gS * 0.5, patchBase[1], k)} r={11} kind="game" />
          <Dot x={lerp(aP[0], rowSrc[0], k)} y={lerp(aP[1], rowSrc[1], k)} r={10} kind="ai" />
        </>);
      })()}
      {/* 流动的方块 + 中间那两块 */}
      {movers.map((m, i) => {
        const isMid = (m.kind === 'game' && streamGame[GAME_SLOTS.indexOf(m.slot)] === SEL) || (m.kind === 'ai' && AI_SLOTS.indexOf(m.slot) === 0);
        if (!isMid && t < m.depart) return null;
        if (isMid && t < K4.pick) return null;
        const [pos, su] = moverPos(m);
        const q = proj(v, pos), u = pxPerUnit(v, pos);
        const c = isMid ? (m.kind === 'game' ? cg : ca) : cycle(t, [K4.all, m.depart + TRAVEL - 0.1], 0.5);
        const label = m.kind === 'ai' && isMid && t >= K4.out ? '23' : undefined;
        return <Tile key={i} x={q[0]} y={q[1]} s={su * u} kind={m.kind} fill={c.fill} lit={Math.max(c.lit, 0.35)} lift={0.8} label={label} labelSize={su * u * 0.42} />;
      })}
      {/* 唯一的标题，第 115 帧出现；底下一道很淡的暗带，相机升起时面板上的数字从标题下面滑过也不会撞字 */}
      <div style={{position: 'absolute', left: 0, right: 0, top: 120, height: 260, opacity: prog(t, K4.headline, 0.4),
        background: 'linear-gradient(rgba(16,17,20,0) 0%, rgba(16,17,20,0.78) 30%, rgba(16,17,20,0.78) 70%, rgba(16,17,20,0) 100%)'}} />
      <div style={{position: 'absolute', left: 60, right: 60, top: 186 + (1 - prog(t, K4.headline, 0.4)) * 20, textAlign: 'center', fontFamily: FONT, fontWeight: 700, fontSize: 74, letterSpacing: 2,
        color: C.ink, opacity: prog(t, K4.headline, 0.4), textShadow: '0 2px 18px rgba(8,9,11,0.9), 0 1px 3px rgba(8,9,11,0.9)'}}>共同点：大量计算可以并行</div>
    </AbsoluteFill>
  );
};
export const T4_FINAL = {slab: SLAB, D_TOP};
export const unusedT4 = settle;
