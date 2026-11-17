import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {C, FONT} from '../lib/theme';
import {cue, ease, easeIO, lerp, prog, sec} from '../lib/time';
import {Drift, Kicker, Note} from '../lib/ui';

// v02 C 段：问题 → 切段换数字 → 输入 [2,3]
// → 第 1 行参数 [4,5]：2×4 + 3×5 = 23（快）→ 第 2 行参数 [1,6]：2×1 + 3×6 = 20（同一个输入，各自的连线）
// → 很多行一起展开（不放小数字）→ 「矩阵 × 向量」简化示意
const TOKENS = ['黑洞', '是', '什么？'];
const VEC = [[0.12, -0.83, 0.45], [-0.54, 0.21, 0.08], [0.33, 0.71, -0.46]];   // 示意数字
const sgn = (v: number) => (v < 0 ? '−' : '') + Math.abs(v).toFixed(2);

const Chip: React.FC<{x: number; y: number; v: string; color: string; o?: number; size?: number; glow?: number; fill?: string}> = ({x, y, v, color, o = 1, size = 150, glow = 0, fill}) => (
  <div style={{position: 'absolute', left: x - size / 2, top: y - size / 2, width: size, height: size, borderRadius: size * 0.16, opacity: o,
    border: `4px solid ${color}`, background: fill ?? 'rgba(20,22,27,0.9)', display: 'flex', alignItems: 'center', justifyContent: 'center',
    fontFamily: FONT.num, fontWeight: 700, fontSize: size * 0.6, color, boxShadow: glow ? `0 0 ${40 * glow}px ${color}` : undefined}}>{v}</div>
);

export const SeqC: React.FC<{from: number}> = ({from}) => {
  const f = useCurrentFrame() + from;
  const slideIn = prog(f, from, 14, easeIO);
  const c1 = cue('C1'), c2 = cue('C2'), c3 = cue('C3'), c4 = cue('C4'), c5 = cue('C5'), c6 = cue('C6'), c7 = cue('C7');
  // C1–C2：问题 → 切段 → 每段几个数字
  const arrive = prog(f, from + 4, sec(0.8), ease);
  const split = prog(f, c2 + sec(0.2), 12, easeIO);
  const nums = (i: number) => prog(f, c2 + sec(0.9) + i * 4, 10);
  const tokOut = prog(f, c3, sec(0.9), easeIO);
  // C3：输入 [2,3]
  const inIn = prog(f, c3 + sec(0.15), sec(1.1), easeIO);   // 数字从上面那几列「收拢」成输入 [2, 3]
  const inPulse = inIn * (1 - prog(f, c4, 8)) * (0.5 + 0.5 * Math.sin((f - c3) * 0.35));
  // C4：第 1 行
  const r1 = prog(f, c4 - 2, 10);
  const p1a = prog(f, c4 + sec(0.55), 6), p1b = prog(f, c4 + sec(1.3), 6), o1 = prog(f, c4 + sec(2.15), 8);
  // C5：第 2 行（同一个输入，各自的连线）
  const r2 = prog(f, c5 + sec(0.1), 10);
  const link2 = prog(f, c5 + sec(0.9), 14, easeIO);
  const p2a = prog(f, c5 + sec(1.5), 6), p2b = prog(f, c5 + sec(1.85), 6), o2 = prog(f, c5 + sec(2.6), 8);
  const dim1 = r2 * (1 - o2) * 0.55;                         // 算第 2 行时，第 1 行退后
  // C6：很多行一起展开
  const zoom = prog(f, c6, 16, easeIO);
  const rowsIn = (r: number) => prog(f, c6 + sec(0.5) + r * 2, 8);
  const fire = prog(f, c6 + sec(2.0), 4) * (1 - prog(f, c6 + sec(2.8), 12));
  const fired = prog(f, c6 + sec(2.0), 4);
  // C7：标注
  const lab = prog(f, c7, 12);

  const IX = [340, 540], IY = 520, R1Y = 860, R2Y = 1110, OX = 915;
  // C6 网格的几何（第 1、2 行就是上面两行，缩小到这里）
  const G = {x0: 170, y0: 600, pitch: 78, cell: 66, cols: 6, rows: 9, iy: 500, ox: 790};
  const gx = (j: number) => G.x0 + j * G.pitch, gy = (r: number) => G.y0 + r * G.pitch;

  // 教学舞台缩到网格前两行的位置
  const stageT = `translate(${-zoom * 60}px, ${-zoom * 120}px) scale(${lerp(1, 0.6, zoom)})`;

  return (
    <AbsoluteFill style={{background: C.bg, transform: `translateX(${(1 - slideIn) * 1080}px)`}}>
      <Kicker text="AI 模型" color={C.ai} opacity={slideIn} />
      <Drift from={from} amp={1.1} push={0.0012}>
        {/* C1–C2 问题和切段 */}
        {tokOut < 1 && (
          <div style={{position: 'absolute', left: 0, right: 0, top: 420 - (1 - arrive) * 240 + tokOut * 60, opacity: arrive * (1 - tokOut), display: 'flex', justifyContent: 'center', gap: lerp(0, 40, split) * (1 - tokOut), transform: `scale(${1 - 0.4 * tokOut})`}}>
            {TOKENS.map((t, i) => (
              <div key={i} style={{position: 'relative', fontFamily: FONT.hei, fontSize: 92, color: C.ink, padding: '20px 34px', background: split > 0.05 ? C.bg2 : '#2B3038',
                border: `4px solid rgba(104,168,255,${split})`, borderRadius: split > 0.05 ? 18 : i === 0 ? '46px 0 0 46px' : i === 2 ? '0 46px 46px 0' : 0}}>
                {t}
                <div style={{position: 'absolute', left: 0, right: 0, top: '118%', textAlign: 'center'}}>
                  {VEC[i].map((v, k) => (
                    <div key={k} style={{fontFamily: FONT.num, fontSize: 54, lineHeight: 1.35, color: C.ai, opacity: prog(f, c2 + sec(0.9) + i * 4 + k * 3, 8) * nums(i)}}>{sgn(v)}</div>
                  ))}
                  <div style={{fontFamily: FONT.num, fontSize: 54, color: C.dim, opacity: nums(i)}}>⋮</div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* C3–C5 教学舞台 */}
        {inIn > 0 && (
          <AbsoluteFill style={{transform: stageT, transformOrigin: '30% 30%', opacity: 1 - zoom}}>
            <div style={{position: 'absolute', left: 70, top: IY - 26, fontFamily: FONT.hei, fontWeight: 700, fontSize: 44, color: C.ai, opacity: inIn * (1 - zoom)}}>输入</div>
            <div style={{transform: `translateY(${(1 - inIn) * 160}px) scale(${lerp(0.55, 1, inIn)})`, transformOrigin: '460px 520px'}}>
              <Chip x={IX[0]} y={IY} v="2" color={C.ai} o={inIn} glow={inPulse} />
              <Chip x={IX[1]} y={IY} v="3" color={C.ai} o={inIn} glow={inPulse} />
            </div>
            <svg width={1080} height={1400} style={{position: 'absolute', left: 0, top: 0}}>
              {/* 第 1 行的连线：直下 */}
              {[0, 1].map((j) => <line key={j} x1={IX[j]} y1={IY + 78} x2={IX[j]} y2={IY + 78 + (R1Y - 78 - IY - 78) * r1} stroke={C.ai} strokeWidth={6}
                opacity={(1 - dim1) * (1 - zoom)} />)}
              {/* 第 2 行的连线：从同一个输入绕到外侧落下（另一条连接） */}
              <path d={`M${IX[0] - 60},${IY + 78} C ${IX[0] - 150},${IY + 260} ${IX[0] - 150},${R2Y - 200} ${IX[0] - 30},${R2Y - 78}`} fill="none" stroke={C.ai}
                strokeWidth={6} strokeDasharray="16 12" pathLength={1} strokeDashoffset={0} opacity={link2 * (1 - zoom)} />
              <path d={`M${IX[1] + 60},${IY + 78} C ${IX[1] + 120},${IY + 260} ${IX[1] + 120},${R2Y - 200} ${IX[1] + 30},${R2Y - 78}`} fill="none" stroke={C.ai}
                strokeWidth={6} strokeDasharray="16 12" opacity={link2 * (1 - zoom)} />
              {/* 箭头到输出 */}
              {[[R1Y, o1], [R2Y, o2]].map(([y, o], k) => <line key={k} x1={IX[1] + 90} y1={y} x2={IX[1] + 90 + (OX - 95 - IX[1] - 90) * o} y2={y} stroke={C.ink} strokeWidth={5} opacity={(1 - zoom) * (k === 0 ? 1 - dim1 : 1)} />)}
            </svg>
            {/* 第 1 行 */}
            <div style={{opacity: 1 - dim1}}>
              <div style={{position: 'absolute', left: 50, top: R1Y - 26, fontFamily: FONT.hei, fontWeight: 700, fontSize: 40, color: C.sub, opacity: r1 * (1 - zoom)}}>参数 ①</div>
              <Chip x={IX[0]} y={R1Y} v="4" color={C.ink} o={r1} glow={p1a * (1 - p1b)} />
              <Chip x={IX[1]} y={R1Y} v="5" color={C.ink} o={r1} glow={p1b * (1 - o1)} />
              <div style={{position: 'absolute', left: IX[1] + 135, width: OX - 95 - IX[1] - 135, top: R1Y - 82, textAlign: 'center', fontFamily: FONT.num, fontSize: 40, color: C.game,
                opacity: (1 - zoom)}}>
                <span style={{opacity: p1a}}>8</span><span style={{opacity: p1b}}> + 15</span>
              </div>
              <Chip x={OX} y={R1Y} v="23" color={C.ai} o={o1} size={170} glow={o1 * (1 - o2) * 0.8} fill="rgba(104,168,255,0.16)" />
            </div>
            {/* 第 2 行 */}
            <div style={{position: 'absolute', left: 50, top: R2Y - 26, fontFamily: FONT.hei, fontWeight: 700, fontSize: 40, color: C.sub, opacity: r2 * (1 - zoom)}}>参数 ②</div>
            <Chip x={IX[0]} y={R2Y} v="1" color={C.ink} o={r2} glow={p2a * (1 - p2b)} />
            <Chip x={IX[1]} y={R2Y} v="6" color={C.ink} o={r2} glow={p2b * (1 - o2)} />
            <div style={{position: 'absolute', left: IX[1] + 135, width: OX - 95 - IX[1] - 135, top: R2Y - 82, textAlign: 'center', fontFamily: FONT.num, fontSize: 40, color: C.game, opacity: 1 - zoom}}>
              <span style={{opacity: p2a}}>2</span><span style={{opacity: p2b}}> + 18</span>
            </div>
            <Chip x={OX} y={R2Y} v="20" color={C.ai} o={o2} size={170} glow={o2 * 0.8 * (1 - zoom)} fill="rgba(104,168,255,0.16)" />
          </AbsoluteFill>
        )}

        {/* C6–C7：很多行一起展开（除前两行外不放数字） */}
        {zoom > 0 && (
          <AbsoluteFill>
            {/* 输入向量延长 */}
            {Array.from({length: G.cols}, (_, j) => (
              <div key={'i' + j} style={{position: 'absolute', left: gx(j) - G.cell / 2, top: G.iy - G.cell / 2, width: G.cell, height: G.cell, borderRadius: 10,
                border: `3px solid ${C.ai}`, background: 'rgba(104,168,255,0.12)', opacity: prog(f, c6 + sec(0.2) + j * 2, 8),
                display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: FONT.num, fontWeight: 700, fontSize: 38, color: C.ai}}>{j < 2 ? ['2', '3'][j] : ''}</div>
            ))}
            {Array.from({length: G.rows}, (_, r) => (
              <div key={'r' + r}>
                {Array.from({length: G.cols}, (_, j) => (
                  <div key={j} style={{position: 'absolute', left: gx(j) - G.cell / 2, top: gy(r) - G.cell / 2, width: G.cell, height: G.cell, borderRadius: 10,
                    border: `3px solid ${fire > 0.3 ? C.op : '#5C6370'}`, background: fire > 0.1 ? `rgba(255,255,255,${0.15 * fire})` : C.bg2,
                    opacity: r < 2 ? prog(f, c6 + sec(0.2) + j * 2, 8) : rowsIn(r),
                    display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: FONT.num, fontWeight: 700, fontSize: 38, color: C.ink}}>{r < 2 && j < 2 ? [['4', '5'], ['1', '6']][r][j] : ''}</div>
                ))}
                <div style={{position: 'absolute', left: G.ox - 45, top: gy(r) - G.cell / 2, width: 90, height: G.cell, borderRadius: 10, border: `3px solid ${C.ai}`,
                  background: `rgba(104,168,255,${0.12 + 0.5 * fire + 0.15 * fired})`, opacity: r < 2 ? prog(f, c6 + sec(0.3), 8) : rowsIn(r), boxShadow: fire > 0.2 ? `0 0 ${24 * fire}px ${C.ai}` : undefined,
                  display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: FONT.num, fontWeight: 700, fontSize: 38, color: C.ai}}>{r < 2 ? ['23', '20'][r] : ''}</div>
              </div>
            ))}
            <div style={{position: 'absolute', left: gx(G.cols - 1) + 46, top: G.iy - 26, fontFamily: FONT.num, fontSize: 44, color: C.dim, opacity: zoom}}>…</div>
            {/* C7 标注 */}
            <div style={{position: 'absolute', left: gx(0) - 40, top: G.iy - 96, fontFamily: FONT.hei, fontWeight: 700, fontSize: 38, color: C.ai, opacity: lab}}>输入向量（同一个）</div>
            <div style={{position: 'absolute', left: G.ox - 70, top: G.y0 - 100, fontFamily: FONT.hei, fontWeight: 700, fontSize: 38, color: C.ai, opacity: lab}}>输出</div>
            <div style={{position: 'absolute', left: 40, top: gy(G.rows - 1) + 60, right: 40, fontFamily: FONT.hei, fontWeight: 700, fontSize: 40, color: C.sub, opacity: lab}}>
              每一行参数 × 同一个输入 → 一个输出
            </div>
            <div style={{position: 'absolute', left: 0, right: 0, top: 262, textAlign: 'center', fontFamily: FONT.title, fontSize: 88, color: C.ink, opacity: lab}}>矩阵 × 向量</div>
          </AbsoluteFill>
        )}
      </Drift>
      <Note top={1490} opacity={prog(f, c2 + sec(0.9), 10) * (1 - inIn) * 0.9}>示意数字：真实模型里每段有几千个数</Note>
      <Note top={1490} opacity={inIn * (1 - lab) * 0.9}>示意：用两对简单整数举例</Note>
      <Note top={1490} opacity={lab * 0.9}>简化示意：神经网络里的矩阵计算，不是语言模型的完整过程</Note>
    </AbsoluteFill>
  );
};
