import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {C, FONT} from '../lib/theme';
import {cue, ease, easeIO, lerp, prog, sec} from '../lib/time';
import {Drift, Kicker, Note} from '../lib/ui';

// C 段：「黑洞是什么？」→ 切成几段 → 每段换成一长串数字 → 一个看得懂的例子 2×4 + 3×5 = 23（两次乘法分开演，
// 再相加，留停顿）→ 真实模型里一次几千对 → 很多行排整齐 = 矩阵乘法 → 每个字要做几十亿到上千亿次
const TOKENS = ['黑洞', '是', '什么', '？'];
// 示意数字（不是任何真实模型的向量）
const VEC = [
  [0.12, -0.83, 0.45, 0.07, -0.31, 0.92, -0.18, 0.66],
  [-0.54, 0.21, 0.08, -0.77, 0.39, -0.02, 0.58, -0.25],
  [0.33, 0.71, -0.46, 0.15, -0.64, 0.27, 0.04, -0.89],
  [-0.09, -0.36, 0.81, -0.52, 0.11, 0.48, -0.73, 0.2],
];
const sgn = (v: number) => (v < 0 ? '−' : '') + Math.abs(v).toFixed(2);
// 例子之后那一长排：前两对就是 2,4 和 3,5
const XS = [2, 3, 1, 4, 0, 2, 5, 1, 3, 2, 4, 1, 0, 3, 2, 1];
const WS = [4, 5, 2, 1, 3, 0, 1, 4, 2, 3, 1, 5, 2, 0, 1, 3];

const Big: React.FC<{v: string; color: string; x: number; y: number; o?: number; size?: number; glow?: number}> = ({v, color, x, y, o = 1, size = 132, glow = 0}) => (
  <div style={{position: 'absolute', left: x, top: y, transform: 'translate(-50%,-50%)', fontFamily: FONT.num, fontWeight: 700, fontSize: size, color, opacity: o,
    textShadow: glow ? `0 0 ${30 * glow}px ${color}` : undefined, lineHeight: 1}}>{v}</div>
);

export const SeqC: React.FC<{from: number}> = ({from}) => {
  const f = useCurrentFrame() + from;
  const inK = prog(f, from, 10);
  const slideIn = prog(f, from, 14, easeIO);

  // ---- C1：问题气泡 → 切成几段
  const c1 = cue('C1');
  const split = prog(f, c1 + sec(1.25), 16, easeIO);
  const arrive = prog(f, from + 4, sec(1.1), ease);   // 问题气泡落进来（就是 A 段手机里那句问题）
  // ---- C2：每段下面长出一列数字
  const c2 = cue('C2');
  const colIn = (i: number) => prog(f, c2 + sec(0.15) + i * 4, 14);
  // ---- C3：数字列退到上面，中间出现 × 和 +
  const c3 = cue('C3');
  const tokUp = prog(f, c3 + sec(0.2), 16, easeIO);
  const xSym = prog(f, c3 + sec(1.9), 8), pSym = prog(f, c3 + sec(2.5), 8);
  const symOut = prog(f, cue('C4') - 6, 8);
  const tokOut = prog(f, cue('C4') - 8, 10);
  // ---- C4–C6：2×4 + 3×5 = 23
  const c4 = cue('C4'), c5 = cue('C5'), c6 = cue('C6');
  const stageIn = prog(f, cue('C4') - 6, 12);
  const col1 = prog(f, c4 + sec(0.45), 8), prod1 = prog(f, c4 + sec(1.05), 9);
  const col2 = prog(f, c5 + sec(0.05), 8), prod2 = prog(f, c5 + sec(0.75), 9);
  const plus = prog(f, c6 + sec(0.1), 8), eq = prog(f, c6 + sec(0.95), 10);
  const glow23 = prog(f, c6 + sec(1.0), 6) * (1 - prog(f, c6 + sec(2.0), 14));
  // ---- C7：缩进一长排（几千对），乘积一路算过去，加成一个输出
  const c7 = cue('C7'), c8 = cue('C8'), c9 = cue('C9');
  const shrink = prog(f, c7 + sec(0.1), 18, easeIO);
  const rowIn = (j: number) => prog(f, c7 + sec(0.5) + j * 2, 8);
  const ripple = (j: number) => prog(f, c7 + sec(1.3) + j * 2.2, 6);
  const outCell = prog(f, c7 + sec(2.5), 10);
  // ---- C8：很多行参数排整齐 → 矩阵；每一行各出一个输出，同时算
  const rowsIn = (r: number) => prog(f, c8 + sec(0.1) + r * 2, 8);
  const allFire = prog(f, c8 + sec(1.0), 6) * (1 - prog(f, c8 + sec(1.7), 10));
  const prodOut = prog(f, c8, 8);
  // ---- C9：缩成很多层里的一块 + 数量级
  const stackK = prog(f, c9 + sec(0.1), 18, easeIO);
  const bigNum = prog(f, c9 + sec(0.9), 12);
  const outro = prog(f, cue('D1') - sec(0.45), 10);

  const PITCH = 50, CELL = 44, X0 = 90, YX = 560, YW = 620;
  const teachX = [340, 680], teachY = {x: 600, w: 790, p: 1010};
  const gridScale = lerp(1, 0.42, stackK);

  return (
    <AbsoluteFill style={{background: C.bg, transform: `translateX(${(1 - slideIn) * 1080}px)`, opacity: 1 - outro * 0.0}}>
      <Kicker text="AI 模型" color={C.ai} opacity={inK} />
      <Drift from={from} amp={1.35}>

      {/* C1–C3：问题和切出来的几段 */}
      {tokOut < 1 && (
        <div style={{position: 'absolute', left: 0, right: 0, top: lerp(640, 300, tokUp) - (1 - arrive) * 260, opacity: (1 - tokOut) * arrive, transform: `scale(${lerp(0.8, 1, arrive)})`}}>
          <div style={{display: 'flex', justifyContent: 'center', gap: lerp(0, 34, split)}}>
            {TOKENS.map((t, i) => (
              <div key={i} style={{position: 'relative', fontFamily: FONT.hei, fontSize: lerp(78, 66, tokUp), color: C.ink, background: split > 0.05 ? C.bg2 : '#2B3038',
                border: `3px solid ${split > 0.05 ? C.ai : 'transparent'}`, borderColor: `rgba(104,168,255,${split})`,
                padding: '18px 26px', borderRadius: i === 0 ? '30px 10px 10px 30px' : i === TOKENS.length - 1 ? '10px 30px 30px 10px' : 10,
                ...(split < 0.05 ? {borderRadius: i === 0 ? '40px 0 0 40px' : i === TOKENS.length - 1 ? '0 40px 40px 0' : 0, marginLeft: -1} : {})}}>
                {t}
                {/* 下面那一列数字 */}
                <div style={{position: 'absolute', left: 0, right: 0, top: '115%', textAlign: 'center', opacity: colIn(i) * (1 - tokUp * 0.6)}}>
                  {VEC[i].map((v, k) => (
                    <div key={k} style={{fontFamily: FONT.num, fontSize: 34, lineHeight: 1.42, color: v < 0 ? '#9DB6D8' : C.ai,
                      transform: `translateY(${(1 - prog(f, c2 + sec(0.15) + i * 4 + k * 1.5, 8)) * -20}px)`, opacity: prog(f, c2 + sec(0.15) + i * 4 + k * 1.5, 8)}}>{sgn(v)}</div>
                  ))}
                  <div style={{color: C.dim, fontSize: 34, fontFamily: FONT.num}}>⋮</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      <Note top={1490} opacity={(prog(f, c1 + sec(1.6), 10) * (1 - prog(f, c2 + sec(0.6), 8))) * 0.9}>示意：怎么切因模型而异</Note>
      <Note top={1490} opacity={(prog(f, c2 + sec(0.8), 10) * (1 - tokOut)) * 0.9}>示意数字：真实模型里每段有几千个数</Note>
      {/* C3 的 × 和 + */}
      {symOut < 1 && (
        <div style={{position: 'absolute', left: 0, right: 0, top: 1030, display: 'flex', justifyContent: 'center', gap: 160, opacity: 1 - symOut}}>
          <div style={{fontFamily: FONT.num, fontSize: 220, color: C.ink, opacity: xSym, transform: `scale(${lerp(0.6, 1, xSym)})`}}>×</div>
          <div style={{fontFamily: FONT.num, fontSize: 220, color: C.ink, opacity: pSym, transform: `scale(${lerp(0.6, 1, pSym)})`}}>+</div>
        </div>
      )}

      {/* C4–C6 教学：两对数，竖着相乘，再相加（和 B 段算亮度同一个版式） */}
      {stageIn > 0 && shrink < 1 && (
        <AbsoluteFill style={{opacity: stageIn * (1 - shrink)}}>
          <div style={{position: 'absolute', left: 0, right: 0, top: 360, textAlign: 'center', fontFamily: FONT.hei, fontSize: 36, color: C.sub}}>举个最简单的例子</div>
          <div style={{position: 'absolute', left: 70, top: teachY.x - 22, fontFamily: FONT.hei, fontWeight: 700, fontSize: 38, color: C.ai}}>输入</div>
          <div style={{position: 'absolute', left: 70, top: teachY.w - 22, fontFamily: FONT.hei, fontWeight: 700, fontSize: 38, color: C.sub}}>参数</div>
          {/* 当前这一对的高亮框 */}
          {[col1 * (1 - col2), col2 * (1 - plus)].map((o, i) => (
            <div key={i} style={{position: 'absolute', left: teachX[i] - 110, top: teachY.x - 100, width: 220, height: 300, borderRadius: 24, border: `3px solid ${C.op}`, opacity: o * 0.8}} />
          ))}
          <Big v="2" color={C.ai} x={teachX[0]} y={teachY.x} />
          <Big v="3" color={C.ai} x={teachX[1]} y={teachY.x} />
          <Big v="4" color={C.ink} x={teachX[0]} y={teachY.w} />
          <Big v="5" color={C.ink} x={teachX[1]} y={teachY.w} />
          <Big v="×" color={C.sub} x={teachX[0]} y={(teachY.x + teachY.w) / 2} size={70} o={col1} />
          <Big v="×" color={C.sub} x={teachX[1]} y={(teachY.x + teachY.w) / 2} size={70} o={col2} />
          <div style={{position: 'absolute', left: 230, width: 560, top: 890, height: 4, background: C.line}} />
          <Big v="8" color={C.game === '' ? C.ink : C.op} x={teachX[0]} y={lerp(teachY.w, teachY.p, prod1)} o={prod1} glow={prod1 * (1 - col2)} />
          <Big v="15" color={C.op} x={teachX[1]} y={lerp(teachY.w, teachY.p, prod2)} o={prod2} glow={prod2 * (1 - plus)} />
          <Big v="+" color={C.ink} x={(teachX[0] + teachX[1]) / 2} y={teachY.p} size={100} o={plus} />
          <Big v="=" color={C.ink} x={860} y={teachY.p} size={100} o={eq} />
          <Big v="23" color={C.ai} x={980} y={teachY.p} size={132} o={eq} glow={glow23 * 1.4} />
          {/* 写到这一步为止的算式 */}
          <div style={{position: 'absolute', left: 0, right: 0, top: 1190, textAlign: 'center', fontFamily: FONT.num, fontSize: 56, color: C.sub, opacity: prog(f, c4 + sec(1.2), 10)}}>
            <span style={{color: C.ink}}>2×4</span>
            <span style={{opacity: col2}}> + </span>
            <span style={{opacity: col2, color: C.ink}}>3×5</span>
            <span style={{opacity: eq}}> = </span>
            <span style={{opacity: eq, color: C.ai}}>23</span>
          </div>
        </AbsoluteFill>
      )}

      {/* C7–C9：一长排 → 矩阵 → 很多层 */}
      {shrink > 0 && (
        <AbsoluteFill style={{transform: `translate(${-stackK * 0}px, ${-stackK * 190}px) scale(${gridScale})`, transformOrigin: '540px 560px'}}>
          {/* 层叠（C9）：后面再画几层同样的块 */}
          {Array.from({length: 8}, (_, k) => (
            <div key={k} style={{position: 'absolute', left: X0 - 16 + (k + 1) * 46 * stackK, top: YX - 70 - (k + 1) * 64 * stackK, width: 16 * PITCH + 150, height: 11 * 56 + 150,
              borderRadius: 18, border: `2px solid ${C.aiDim}`, background: 'rgba(20,24,32,0.85)', opacity: stackK * (1 - k * 0.09), zIndex: -k - 1}} />
          ))}
          <div style={{position: 'absolute', left: X0 - 16, top: YX - 70, width: 16 * PITCH + 150, height: 11 * 56 + 150, borderRadius: 18, border: `2px solid ${C.ai}`, background: C.bg, opacity: stackK}} />
          <div style={{position: 'absolute', left: X0, top: YX - 60, fontFamily: FONT.hei, fontWeight: 700, fontSize: 32, color: C.ai, opacity: shrink * (1 - stackK)}}>输入（一长串）</div>
          {XS.map((v, j) => (
            <div key={'x' + j} style={{position: 'absolute', left: X0 + j * PITCH, top: YX, width: CELL, height: CELL, borderRadius: 8, background: 'rgba(104,168,255,0.16)',
              border: `2px solid ${C.ai}`, color: C.ai, fontFamily: FONT.num, fontWeight: 700, fontSize: 26, display: 'flex', alignItems: 'center', justifyContent: 'center',
              opacity: j < 2 ? shrink : rowIn(j) * (j > 13 ? 1 - (j - 13) * 0.3 : 1)}}>{v}</div>
          ))}
          {Array.from({length: 11}, (_, r) => (
            <div key={'r' + r}>
              {WS.map((w0, j) => {
                const w = r === 0 ? w0 : (w0 * (r + 3) + j * 7 + r) % 6;
                const o = r === 0 ? (j < 2 ? shrink : rowIn(j)) : rowsIn(r);
                const fire = r === 0 ? Math.max(ripple(j) * (1 - prodOut), allFire) : allFire;
                return (
                  <div key={j} style={{position: 'absolute', left: X0 + j * PITCH, top: YW + r * 56, width: CELL, height: CELL, borderRadius: 8,
                    background: fire > 0.1 ? `rgba(255,255,255,${0.08 + 0.2 * fire})` : C.bg2, border: `2px solid ${fire > 0.4 ? C.op : C.line}`,
                    color: C.ink, fontFamily: FONT.num, fontSize: 24, display: 'flex', alignItems: 'center', justifyContent: 'center', opacity: o * (j > 13 ? 1 - (j - 13) * 0.3 : 1)}}>{w}</div>
                );
              })}
              {/* 每行的输出 */}
              <div style={{position: 'absolute', left: X0 + 16 * PITCH + 34, top: YW + r * 56, width: 60, height: CELL, borderRadius: 8,
                background: r === 0 ? `rgba(104,168,255,${0.25 * outCell + 0.4 * allFire})` : `rgba(104,168,255,${0.4 * allFire + 0.15 * prog(f, c8 + sec(1.0), 6)})`,
                border: `2px solid ${C.ai}`, opacity: r === 0 ? outCell : rowsIn(r) * prog(f, c8 + sec(0.9), 6)}} />
            </div>
          ))}
          {/* 第一行的乘积（C7） */}
          {XS.map((v, j) => (
            <div key={'p' + j} style={{position: 'absolute', left: X0 + j * PITCH, top: YW + 62, width: CELL, textAlign: 'center', fontFamily: FONT.num, fontSize: 22, color: C.op,
              opacity: ripple(j) * (1 - prodOut) * (j > 13 ? 1 - (j - 13) * 0.3 : 1)}}>{v * WS[j]}</div>
          ))}
          <div style={{position: 'absolute', left: X0 + 16 * PITCH - 40, top: YX + 4, fontFamily: FONT.num, fontSize: 34, color: C.dim, opacity: rowIn(14)}}>…</div>
          <div style={{position: 'absolute', left: X0 + 16 * PITCH + 20, top: YW - 52, fontFamily: FONT.hei, fontSize: 28, color: C.ai, opacity: outCell * (1 - stackK)}}>输出</div>
          <div style={{position: 'absolute', left: X0, top: YW + 11 * 56 + 6, fontFamily: FONT.hei, fontWeight: 700, fontSize: 32, color: C.sub, opacity: prog(f, c8 + sec(0.5), 10) * (1 - stackK)}}>参数矩阵</div>
        </AbsoluteFill>
      )}
      {/* C7 说明：几千对 → 一个数 */}
      <div style={{position: 'absolute', left: 0, right: 0, top: 1250, textAlign: 'center', fontFamily: FONT.hei, fontSize: 46, fontWeight: 700, color: C.ink,
        opacity: prog(f, c7 + sec(2.2), 10) * (1 - prog(f, c8 - 4, 8))}}>
        几千到几万对数，各自相乘，加成 <span style={{color: C.ai}}>1 个</span>输出
      </div>
      <div style={{position: 'absolute', left: 0, right: 0, top: 1300, textAlign: 'center', fontFamily: FONT.hei, fontSize: 50, fontWeight: 700, color: C.ink,
        opacity: prog(f, c8 + sec(0.9), 10) * (1 - stackK)}}>
        每一行各算各的，<span style={{color: C.ai}}>同时</span>出结果
      </div>
      <div style={{position: 'absolute', left: 0, right: 0, top: 900, textAlign: 'center', fontFamily: FONT.hei, color: C.ink, opacity: bigNum}}>
        <div style={{fontSize: 44, color: C.sub}}>每吐出一个字</div>
        <div style={{fontFamily: FONT.title, fontSize: 112, color: C.ai, lineHeight: 1.15}}>几十亿～上千亿次</div>
        <div style={{fontSize: 44, color: C.sub}}>乘加</div>
        <div style={{fontFamily: FONT.num, fontSize: 40, color: C.ink, marginTop: 22, opacity: prog(f, c9 + sec(1.2), 8)}}>
          {Math.round(7e9 * prog(f, c9 + sec(1.0), sec(1.7), (x) => x)).toLocaleString('en-US')}
        </div>
        <div style={{fontSize: 28, color: C.sub, opacity: prog(f, c9 + sec(1.2), 8)}}>以 70 亿参数的模型为例，生成一个字</div>
      </div>
      </Drift>
      <Note top={1490} opacity={stageIn * (1 - shrink) * 0.9}>示意：只取两对整数举例；真实模型每次有几千对</Note>
      <Note top={1490} opacity={bigNum * 0.9}>粗略量级：约等于模型参数个数（几十亿到上千亿个）</Note>
    </AbsoluteFill>
  );
};
