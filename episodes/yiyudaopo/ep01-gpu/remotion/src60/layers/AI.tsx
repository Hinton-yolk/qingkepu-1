// SHOT 03–04（17–42 秒）：AI 区。所有坐标是「AI 局部坐标」= 相机 z=1 对准 AI 区时的屏幕像素；
// 外面套一层世界相机的变换，所以镜头拉远时这些东西和左上方的图形计算在同一个空间里。
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {clamp, cycle, glide, launch, lerp, linear, pchip, prog, settle} from '../lib/core';
import {AI0, camAt, T, worldTransform} from '../lib/plan';
import {C, FONT} from '../lib/theme';
import {Dot, Tile} from '../Tile';
import {AI_TILE, DOCK} from './Carrier';

const Q = '黑洞是什么？';
const CH = 84;                                  // 问题字号
const charX = (i: number) => 540 - (Q.length * CH) / 2 + CH / 2 + i * CH;
const SEGS = [
  {txt: '黑洞', from: [0, 1], x: 215, v: [2, 3]},
  {txt: '是', from: [2], x: 425, v: [1, 4]},
  {txt: '什么', from: [3, 4], x: 655, v: [5, 2]},
  {txt: '？', from: [5], x: 865, v: [3, 1]},
];
// 行：参数向量 → 结果方块。前两行是讲解的主角，后面三行小一号，再往后五行只有形状（拉远时才看得到）
export const ROWS = [
  {y: 830, sc: 1, p: [4, 5], r: 23, enter: T.params, cyc: [T.contract + 0.5, 33.6, 38.2, T.act1, T.act2, T.act3]},
  {y: 1010, sc: 1, p: [1, 6], r: 20, enter: T.row2, cyc: [31.95, 33.6, 38.2, T.act1, T.act2, T.act3]},
  {y: 1160, sc: 0.8, p: [3, 1], r: 9, enter: T.rows, cyc: [38.2, T.act1, T.act2, T.act3]},
  {y: 1290, sc: 0.8, p: [2, 2], r: 10, enter: T.rows + 0.25, cyc: [38.2, T.act1, T.act2, T.act3]},
  {y: 1420, sc: 0.8, p: [5, 1], r: 13, enter: T.rows + 0.5, cyc: [38.2, T.act1, T.act2, T.act3]},
  ...[0, 1, 2, 3, 4].map((k) => ({y: 1545 + k * 110, sc: 0.72, p: null as null | number[], r: 0, enter: 39.5 + k * 0.12, cyc: [T.act1, T.act2, T.act3]})),
];
// 先走最下面的行（离芯片最近），后面的不会从已经落位的方块上面穿过
export const departAI = (row: number) => T.stream0 + 0.06 + (9 - row) * 0.12;
const X1 = 330, X2 = 530, VC = 430, TX = DOCK[0], NS = 104;
// 注意力光区：一块很淡的柔光，跟着「此刻正在算的地方」走（问题 → 选中的数 → 算式 → 结果 → 各行）
const FK = [16.4, 17.6, 18.6, 20.0, 20.9, 21.6, 22.3, 23.2, 24.2, 25.4, 26.3, 27.4, 28.6, 30.6, 32.4, 33.8, 36.4, 38.4, 40.0];
const FX = pchip(FK, [540, 540, 560, 230, 330, 380, 470, 430, 330, 480, 430, 700, 760, 430, 650, 600, 560, 600, 560]);
const FY = pchip(FK, [430, 470, 640, 640, 640, 590, 700, 830, 1000, 1010, 1180, 900, 840, 1080, 1010, 920, 1150, 1100, 1100]);

const Txt: React.FC<{x: number; y: number; size: number; children: React.ReactNode; o?: number; color?: string; w?: number}> = ({x, y, size, children, o = 1, color = C.ai, w = 700}) =>
  o <= 0.001 ? null : (
    <div style={{position: 'absolute', left: x - w / 2, top: y - size * 0.62, width: w, textAlign: 'center', fontFamily: FONT, fontWeight: 700, fontSize: size,
      lineHeight: `${size * 1.24}px`, color, opacity: o, whiteSpace: 'nowrap'}}>{children}</div>
  );
const Box: React.FC<{x: number; y: number; w: number; h: number; o: number; bw?: number; r?: number; glow?: number}> = ({x, y, w, h, o, bw = 3, r = 26, glow = 0}) =>
  o <= 0.001 ? null : (
    <div style={{position: 'absolute', left: x - w / 2, top: y - h / 2, width: w, height: h, borderRadius: r, border: `${bw}px solid rgba(${C.aiRGB},${0.5 + 0.4 * glow})`,
      opacity: o, boxSizing: 'border-box', boxShadow: glow ? `0 0 ${24 * glow}px rgba(${C.aiRGB},${0.35 * glow})` : undefined}} />
  );
const Label: React.FC<{x: number; y: number; text: string; o: number}> = ({x, y, text, o}) =>
  o <= 0.001 ? null : (
    <div style={{position: 'absolute', left: x - 200, top: y - 24, width: 200, textAlign: 'right', fontFamily: FONT, fontWeight: 400, fontSize: 36, color: C.sub, opacity: o}}>{text}</div>
  );

export const AI: React.FC = () => {
  const f = useCurrentFrame();
  const t = f / 30;
  if (t < 14.8 || t > 48.6) return null;
  const cam = camAt(t);
  const old = 1 - prog(t, T.fadeOld, 1.3, glide);                       // SHOT 05：讲解用的数字退场，只留方块
  // ---------------- 问题
  const box = prog(t, 15.5, 0.5) * (1 - prog(t, T.split, 0.4));
  const split = prog(t, T.split, 0.8, glide);
  const selK = prog(t, T.select, 0.4);
  const cen = prog(t, T.center, 1.2, glide);
  const othersOut = prog(t, T.select + 0.25, 0.5);
  const contract = prog(t, T.contract, 1.0, glide);
  const nb = prog(t, T.contract, 0.6);                                   // 标签、来路退场
  // 输入行（[2, 3]）的位置：SHOT 03 居中大字 → 27 秒起靠左，给结果方块让位
  const inX1 = X1, inX2 = X2, inSize = NS;
  const rowC = VC, rowW = 350, rowH = 140;
  const seg0 = SEGS[0];
  // 胶囊 → 输入行（外框在两种形状之间过渡）
  const capX = lerp(seg0.x, rowC, cen), capY = lerp(640, 640, cen), capW = lerp(110, rowW, cen), capH = lerp(190, rowH, cen);
  const nums = prog(t, T.nums, 0.5);
  // 算式
  const f1 = prog(t, T.f1, 0.5, glide), f2 = prog(t, T.f2, 0.5, glide);
  const prod = prog(t, T.prod, 0.35), sum = prog(t, T.sum, 0.5, glide), res = prog(t, T.sum + 0.25, 0.35);
  const fly23 = prog(t, T.contract, 0.9, glide);
  const guides = prog(t, 29.9, 0.6) * old;
  const lastRow = t < T.rows ? 1010 : t < 39.4 ? 1420 : 1985;
  const guideEnd = lerp(t < T.rows ? 1010 : 1420, lastRow, t < T.rows ? 1 : t < 39.4 ? prog(t, T.rows, 0.9) : prog(t, 39.4, 1.0));

  return (
    <div style={{position: 'absolute', left: 0, top: 0, width: 1080, height: 1920, transformOrigin: '0 0', transform: worldTransform(cam)}}>
      <div style={{position: 'absolute', left: AI0.x - 540, top: AI0.y - 960, width: 1080, height: 1920}}>
        <div style={{position: 'absolute', left: FX(t) - 520, top: FY(t) - 520, width: 1040, height: 1040, borderRadius: 520,
          background: 'radial-gradient(circle, rgba(220,228,236,0.085) 0%, rgba(220,228,236,0.035) 40%, rgba(220,228,236,0) 70%)', opacity: prog(t, 16.0, 0.8) * (1 - prog(t, 40.5, 1.5))}} />
        {/* 提问框 */}
        <div style={{position: 'absolute', left: 540 - 370, top: 430 - 72, width: 740, height: 144, borderRadius: 40, border: `3px solid rgba(${C.aiRGB},0.55)`,
          background: 'rgba(220,228,236,0.05)', opacity: box, boxSizing: 'border-box'}}>
          <div style={{position: 'absolute', left: 26, top: 44, width: 52, height: 52, borderRadius: 26, background: `rgba(${C.aiRGB},0.9)`, color: C.bg,
            fontFamily: FONT, fontWeight: 700, fontSize: 24, lineHeight: '52px', textAlign: 'center'}}>AI</div>
        </div>
        {/* 问题的字 → 分成几段 */}
        {Q.split('').map((ch, i) => {
          const seg = SEGS.findIndex((s) => s.from.includes(i));
          const sg = SEGS[seg];
          const typed = prog(t, T.type0 + i * 0.1, 0.12);
          const offset = sg.from.length === 2 ? (sg.from.indexOf(i) - 0.5) * CH : 0;
          let x = lerp(charX(i), sg.x + offset, split), y = lerp(430, 470, split);
          let o = typed;
          if (seg === 0) { x = lerp(x, VC + offset, cen); y = lerp(y, 500, cen); o *= 1 - prog(t, T.params - 0.3, 0.6); }
          else o *= 1 - othersOut;
          return <Txt key={i} x={x} y={y} size={CH} o={o} color="#F4F6F8" w={120}>{ch}</Txt>;
        })}
        {t > T.type0 && t < T.split && Math.floor(t * 2.5) % 2 === 0 && (
          <div style={{position: 'absolute', left: charX(Math.min(5, Math.floor((t - T.type0) / 0.1))) + CH / 2 + 6, top: 400, width: 4, height: 62, background: C.ai, opacity: 0.8}} />
        )}
        {/* 每段下面的一小列数字（示意，不是某个模型的真实编码） */}
        {SEGS.map((sg, k) => {
          const a = prog(t, T.nums + k * 0.35, 0.45);
          if (k === 0) return null;
          const o = a * (1 - othersOut);
          return (
            <React.Fragment key={k}>
              <div style={{position: 'absolute', left: sg.x - 1.5, top: 508, width: 3, height: 34 * a, background: `rgba(${C.aiRGB},0.4)`, opacity: o}} />
              <Box x={sg.x} y={640 + othersOut * 30 - (1 - a) * 60} w={110} h={190} o={o * 0.8} bw={2} r={30} />
              <Txt x={sg.x} y={595 + othersOut * 30 - (1 - a) * 60} size={64} o={o * 0.85} w={110}>{sg.v[0]}</Txt>
              <Txt x={sg.x} y={685 + othersOut * 30 - (1 - a) * 60} size={64} o={o * 0.85} w={110}>{sg.v[1]}</Txt>
            </React.Fragment>
          );
        })}
        {/* 第一段的数字：被选出来做例子 → 变成横着的输入行 [2, 3] */}
        {(() => {
          const a = prog(t, T.nums, 0.45);
          const x1 = lerp(seg0.x, inX1, cen), y1 = lerp(595, 640, cen) - (1 - a) * 60, x2 = lerp(seg0.x, inX2, cen), y2 = lerp(685, 640, cen) - (1 - a) * 60;
          const sz = lerp(64, inSize, cen);
          return (
            <>
              <div style={{position: 'absolute', left: seg0.x - 1.5, top: 508, width: 3, height: 34 * a, background: `rgba(${C.aiRGB},0.4)`, opacity: a * (1 - cen)}} />
              <Box x={capX} y={capY - (1 - a) * 60} w={capW} h={capH} o={a * old} bw={lerp(2, 4, selK)} r={lerp(30, 32, cen)} glow={selK * (1 - 0.6 * cen)} />
              <Txt x={x1} y={y1} size={sz} o={a * old} w={160}>2</Txt>
              <Txt x={x2} y={y2} size={sz} o={a * old} w={160}>3</Txt>
              <Label x={lerp(seg0.x + 200, rowC - rowW / 2 - 22, cen)} y={lerp(790, 640, cen)} text="示例输入" o={prog(t, T.center + 1.05, 0.4) * (1 - nb)} />
            </>
          );
        })()}
        {/* 竖向的「同一列」引导线：示意 2 和 4、3 和 5 配成一对 */}
        <div style={{position: 'absolute', left: X1 - 1.5, top: 705, width: 3, height: 225, background: `rgba(${C.aiRGB},0.5)`, opacity: prog(t, T.f1, 0.2) * (1 - prog(t, T.f1 + 0.9, 0.4))}} />
        <div style={{position: 'absolute', left: X2 - 1.5, top: 705, width: 3, height: 225, background: `rgba(${C.aiRGB},0.5)`, opacity: prog(t, T.f2, 0.2) * (1 - prog(t, T.f2 + 0.9, 0.4))}} />
        {/* 共享的输入：两条竖线把 [2, 3] 接到每一行 */}
        {[X1, X2].map((x) => (
          <div key={x} style={{position: 'absolute', left: x - 1.5, top: 705, width: 3, height: Math.max(0, guideEnd - 705), opacity: guides,
            background: `linear-gradient(rgba(${C.aiRGB},0.32), rgba(${C.aiRGB},0.16))`}} />
        ))}
        {/* 各行：参数向量 → 结果方块 */}
        {ROWS.map((row, i) => {
          const a = prog(t, row.enter, 1.05, settle);
          if (a <= 0) return null;
          const sc = row.sc;
          const slide = (1 - a) * 520;
          const cx = VC, w = 350 * sc, h = 140 * sc, px1 = X1, px2 = X2, size = NS * sc;
          const tileOn = i === 0 ? 1 : prog(t, row.enter + 0.5, 0.5);
          const {fill, lit} = cycle(t, row.cyc, 0.5);
          const showRes = i === 0 ? 1 : t >= row.cyc[0] + 0.45 ? 1 : 0;
          const j = i;                                           // 流向芯片的顺序
          const departed = t >= departAI(j);
          return (
            <React.Fragment key={i}>
              <Box x={cx + slide} y={row.y} w={w} h={h} o={a * old * (row.p ? 1 : 0.6)} bw={2.5 * Math.max(sc, 0.8)} r={30 * sc} />
              {row.p ? (
                <>
                  <Txt x={px1 + slide} y={row.y} size={size} o={a * old} w={160}>{row.p[0]}</Txt>
                  <Txt x={px2 + slide} y={row.y} size={size} o={a * old} w={160}>{row.p[1]}</Txt>
                </>
              ) : (
                <>
                  <div style={{position: 'absolute', left: X1 - 40 + slide, top: row.y - 7, width: 80, height: 14, borderRadius: 7, background: `rgba(${C.aiRGB},0.35)`, opacity: a * old}} />
                  <div style={{position: 'absolute', left: X2 - 40 + slide, top: row.y - 7, width: 80, height: 14, borderRadius: 7, background: `rgba(${C.aiRGB},0.35)`, opacity: a * old}} />
                </>
              )}
              <Txt x={680 + slide} y={row.y} size={56 * sc} o={(i === 0 ? prog(t, T.contract + 0.6, 0.4) : a) * old * 0.55} color={C.sub} w={100}>→</Txt>
              {i === 0 && t >= 28.2 && !departed && (
                <Tile x={TX} y={row.y} s={AI_TILE} kind="ai" fill={fill} lit={lit} lift={0.6} label="23" labelSize={64} />
              )}
              {i > 0 && !departed && (
                <>
                  <Tile x={TX + slide} y={row.y} s={AI_TILE * sc} kind="neutral" empty={1} opacity={tileOn * (1 - prog(t, row.cyc[0] - 0.1, 0.25))} />
                  <Tile x={TX + slide} y={row.y} s={AI_TILE * sc} kind="ai" fill={fill} lit={lit} lift={0.6} opacity={prog(t, row.cyc[0] - 0.1, 0.25)}
                    label={row.p && showRes ? String(row.r) : undefined} labelSize={64 * sc} />
                </>
              )}
            </React.Fragment>
          );
        })}
        <Label x={rowC - rowW / 2 - 22} y={830} text="示例参数" o={prog(t, T.params + 0.4, 0.4) * (1 - nb)} />
        {/* 第一道算式：2×4 + 3×5 = 23 */}
        {t > T.f1 && t < T.contract + 1.0 && (() => {
          const o1 = 1 - prod;
          return (
            <>
              <Txt x={lerp(X1, 250, f1) - 110 * 4 * f1 * (1 - f1)} y={lerp(640, 1010, f1)} size={lerp(NS, 84, f1)} o={o1} w={160}>2</Txt>
              <Txt x={lerp(X1, 350, f1)} y={lerp(830, 1010, f1)} size={lerp(NS, 84, f1)} o={o1} w={160}>4</Txt>
              <Txt x={300} y={1010} size={70} o={prog(t, T.f1 + 0.3, 0.2) * o1} color={C.sub} w={80}>×</Txt>
              {t > T.f2 && (
                <>
                  <Txt x={lerp(X2, 510, f2) + 110 * 4 * f2 * (1 - f2)} y={lerp(640, 1010, f2)} size={lerp(NS, 84, f2)} o={o1} w={160}>3</Txt>
                  <Txt x={lerp(X2, 610, f2)} y={lerp(830, 1010, f2)} size={lerp(NS, 84, f2)} o={o1} w={160}>5</Txt>
                  <Txt x={560} y={1010} size={70} o={prog(t, T.f2 + 0.3, 0.2) * o1} color={C.sub} w={80}>×</Txt>
                </>
              )}
              <Txt x={VC} y={1010} size={78} o={prog(t, T.f2 + 0.3, 0.2) * (1 - sum)} color={C.sub} w={80}>+</Txt>
              <Txt x={lerp(X1, VC, sum)} y={lerp(1010, 1190, sum)} size={lerp(60, 104, prod) * (1 - 0.3 * sum)} o={prod * (1 - prog(t, T.sum + 0.3, 0.2))} w={200}>8</Txt>
              <Txt x={lerp(X2, VC, sum)} y={lerp(1010, 1190, sum)} size={lerp(60, 104, prod) * (1 - 0.3 * sum)} o={prod * (1 - prog(t, T.sum + 0.3, 0.2))} w={200}>15</Txt>
              <Txt x={lerp(VC, TX, fly23)} y={lerp(1190, DOCK[1], fly23)} size={lerp(150 * (0.7 + 0.3 * res), 64, fly23)} o={res * (1 - prog(t, T.contract + 0.85, 0.12))} color="#FFFFFF" w={300}>23</Txt>
            </>
          );
        })()}
        {/* 第二道算式（同样的动作，紧凑版）：2×1 + 3×6 = 20 */}
        {t > T.op2 && t < 32.5 && (() => {
          const k = prog(t, T.op2, 0.5, glide);
          const pr = prog(t, 31.25, 0.3), sm = prog(t, 31.7, 0.35, glide), fl = prog(t, 31.95, 0.45, launch);
          const y = 1110;
          return (
            <>
              <Txt x={lerp(X1, 250, k) - 90 * 4 * k * (1 - k)} y={lerp(640, y, k)} size={lerp(NS, 68, k)} o={1 - pr} w={120}>2</Txt>
              <Txt x={lerp(X1, 350, k)} y={lerp(1010, y, k)} size={lerp(NS, 68, k)} o={1 - pr} w={120}>1</Txt>
              <Txt x={300} y={y} size={56} o={prog(t, T.op2 + 0.3, 0.2) * (1 - pr)} color={C.sub} w={60}>×</Txt>
              <Txt x={VC} y={y} size={60} o={prog(t, T.op2 + 0.3, 0.2) * (1 - sm)} color={C.sub} w={60}>+</Txt>
              <Txt x={lerp(X2, 510, k) + 90 * 4 * k * (1 - k)} y={lerp(640, y, k)} size={lerp(NS, 68, k)} o={1 - pr} w={120}>3</Txt>
              <Txt x={lerp(X2, 610, k)} y={lerp(1010, y, k)} size={lerp(NS, 68, k)} o={1 - pr} w={120}>6</Txt>
              <Txt x={560} y={y} size={56} o={prog(t, T.op2 + 0.3, 0.2) * (1 - pr)} color={C.sub} w={60}>×</Txt>
              <Txt x={lerp(X1, VC, sm)} y={y} size={76} o={pr * (1 - prog(t, 31.75, 0.15))} w={100}>2</Txt>
              <Txt x={lerp(X2, VC, sm)} y={y} size={76} o={pr * (1 - prog(t, 31.75, 0.15))} w={100}>18</Txt>
              <Txt x={lerp(VC, TX, fl)} y={lerp(y, 1010, fl)} size={lerp(84, 64, fl)} o={prog(t, 31.85, 0.2) * (1 - prog(t, 32.35, 0.1))} color="#FFFFFF" w={140}>20</Txt>
            </>
          );
        })()}
        {/* 输入同时流向每一行：两颗小点沿竖线下来，到了这一行再流进结果方块 */}
        {[{s: T.both, rows: [0, 1]}, {s: T.all, rows: [0, 1, 2, 3, 4]}].map(({s, rows}, gi) =>
          t > s && t < s + 0.65 ? rows.map((ri) => {
            const row = ROWS[ri];
            const kd = prog(t, s, 0.4, glide), kr = prog(t, s + 0.4, 0.2, linear);
            const r = 9 * row.sc;
            return (
              <React.Fragment key={`${gi}-${ri}`}>
                {kr <= 0 && <Dot x={X1} y={lerp(700, row.y, kd)} r={r} kind="ai" />}
                {kr <= 0 && <Dot x={X2} y={lerp(700, row.y, kd)} r={r} kind="ai" />}
                {kr > 0 && <Dot x={lerp(610, TX - AI_TILE * row.sc / 2, kr)} y={row.y} r={r * 1.2} kind="ai" opacity={1 - prog(t, s + 0.6, 0.05)} />}
              </React.Fragment>
            );
          }) : null,
        )}
      </div>
    </div>
  );
};
export const clampUnused = clamp;
