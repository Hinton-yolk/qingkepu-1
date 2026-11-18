import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {C, FONT} from '../lib/theme';
import {cue, ease, easeIO, lerp, prog, sec} from '../lib/time';
import {Drift, Kicker, Note} from '../lib/ui';

// v03 C 段：一个连续的舞台，元素变形、移动，不换「幻灯片」。
// 问题 → 一串数字 → 收拢成输入 [2,3] → 输入的「复制」落到第 1 行参数 [4,5]，积 8、15 飞出合成 23
// → 再绕到第 2 行 [1,6]，积 2、18 合成 20 → 镜头拉远，又来 3 行，输入沿两条竖线同时送到每一行，所有输出一起亮。
const Chip: React.FC<{x: number; y: number; v: string; color: string; o?: number; size?: number; glow?: number; fill?: string; fs?: number}> = ({x, y, v, color, o = 1, size = 150, glow = 0, fill, fs}) => (
  <div style={{position: 'absolute', left: x - size / 2, top: y - size / 2, width: size, height: size, borderRadius: size * 0.18, opacity: o,
    border: `5px solid ${color}`, background: fill ?? 'rgba(20,22,27,0.92)', display: 'flex', alignItems: 'center', justifyContent: 'center',
    fontFamily: FONT.num, fontWeight: 700, fontSize: fs ?? size * 0.58, color, boxShadow: glow > 0.05 ? `0 0 ${46 * glow}px ${color}` : undefined}}>{v}</div>
);
const bez = (a: number[], b: number[], c: number[], d: number[], t: number) => {
  const u = 1 - t;
  return [0, 1].map((k) => u * u * u * a[k] + 3 * u * u * t * b[k] + 3 * u * t * t * c[k] + t * t * t * d[k]);
};

export const SeqC: React.FC<{from: number}> = ({from}) => {
  const f = useCurrentFrame() + from;
  const slideIn = prog(f, from, 14, easeIO);
  const c1 = cue('C1'), c2 = cue('C2'), c3 = cue('C3'), c4 = cue('C4'), c5 = cue('C5');
  const IX = [370, 570], IY = 420, R1Y = 760, R2Y = 1040, OX = 860, EXTRA = [1260, 1480, 1700];
  // 问题 → 一串数字 → 输入
  const bub = prog(f, from + 4, 14, ease);
  const toNums = prog(f, c2 + sec(0.2), 12);
  const gather = prog(f, c2 + sec(1.0), 26, easeIO);
  const NUMS = ['2', '3', '1', '4', '0', '2'];
  // 第 1 行
  const r1 = prog(f, c3 - 8, 10);
  const g1a = prog(f, c3 + sec(0.3), 9, easeIO), g1b = prog(f, c3 + sec(1.05), 9, easeIO);   // 输入的复制落到 4、5
  const p1a = prog(f, c3 + sec(0.6), 8), p1b = prog(f, c3 + sec(1.35), 8);               // 8、15 出现
  const fuse1 = prog(f, c3 + sec(1.95), 12, easeIO);                                      // 合成 23
  // 第 2 行
  const r2 = prog(f, c4 + sec(0.05), 10);
  const g2 = prog(f, c4 + sec(0.9), 16, easeIO);
  const p2a = prog(f, c4 + sec(1.5), 8), p2b = prog(f, c4 + sec(1.8), 8);
  const fuse2 = prog(f, c4 + sec(2.55), 12, easeIO);
  // 拉远 + 更多行 + 一起算
  const pull = prog(f, c5, 22, easeIO);
  const more = (k: number) => prog(f, c5 + sec(0.5) + k * 5, 10);
  const bus = prog(f, c5 + sec(1.6), 10);
  const fireT = c5 + sec(2.0);
  const fire = prog(f, fireT, 4) * (1 - prog(f, fireT + 8, 14));
  const fired = prog(f, fireT, 4);
  const S = lerp(1, 0.74, pull);
  // 拉远后整体居中：内容中心 x≈615 放到画面中线，输入行停在 y≈330
  const stage = `translate(${lerp(0, 540 - 615 * 0.74, pull)}px, ${lerp(0, 330 - IY * 0.74, pull)}px) scale(${S})`;

  const outChip = (y: number, v: string, fuse: number, pa: number, pb: number, va: string, vb: string, row: number) => {
    // 积先出现在行和输出之间（上下两个小块），再飞进输出合成一个数
    const midX = (IX[1] + OX) / 2 + 20;
    const pa0 = [midX, y - 62], pb0 = [midX, y + 62];
    return (
      <>
        <Chip x={lerp(pa0[0], OX, fuse)} y={lerp(pa0[1], y, fuse)} v={va} color={C.game} size={100} o={pa * (1 - fuse)} glow={pa * (1 - fuse) * 0.6} />
        <Chip x={lerp(pb0[0], OX, fuse)} y={lerp(pb0[1], y, fuse)} v={vb} color={C.game} size={100} o={pb * (1 - fuse)} glow={pb * (1 - fuse) * 0.6} />
        <Chip x={OX} y={y} v={v} color={C.ai} size={150} o={fuse} glow={Math.max(fuse * (1 - prog(f, (row === 1 ? c3 : c4) + sec(3.0), 16)), fire) * 0.9} fill="rgba(104,168,255,0.18)" />
      </>
    );
  };

  return (
    <AbsoluteFill style={{background: C.bg, transform: `translateX(${(1 - slideIn) * 1080}px)`}}>
      <Kicker text="AI 模型" color={C.ai} opacity={slideIn} />
      <Drift from={from} amp={0.7} push={0.0012}>
        {/* 问题气泡 → 一串数字 */}
        <div style={{position: 'absolute', left: 0, right: 0, top: 500 + 14 * Math.sin((f - from) * 0.12), textAlign: 'center', opacity: bub * (1 - toNums), transform: `scale(${lerp(0.85, 1, bub) + 0.04 * Math.sin((f - from) * 0.09)})`}}>
          <span style={{fontFamily: FONT.hei, fontSize: 96, color: C.ink, background: '#2B3038', padding: '26px 52px', borderRadius: '56px 56px 14px 56px'}}>黑洞是什么？</span>
        </div>
        {toNums > 0 && gather < 1 && NUMS.map((v, i) => {
          const x0 = 540 + (i - 2.5) * 150, y0 = 560;
          const keep = i < 2;
          const x = keep ? lerp(x0, IX[i], gather) : x0 + gather * 400;
          const y = keep ? lerp(y0, IY, gather) : y0;
          const pop = prog(f, c2 + sec(0.15) + i * 3, 8, ease);   // 一个个落下来
          return <Chip key={i} x={x} y={y - (1 - pop) * 70} v={v} color={C.ai} size={lerp(120, 150, keep ? gather : 0)} o={pop * (keep ? 1 : 1 - gather)} />;
        })}

        {/* 教学舞台（C5 时整体拉远） */}
        <AbsoluteFill style={{transform: stage, transformOrigin: '0 0'}}>
          <div style={{position: 'absolute', left: 60, top: IY - 30, fontFamily: FONT.hei, fontWeight: 700, fontSize: 46, color: C.ai, opacity: gather * (1 - pull)}}>输入</div>
          {/* C5：两条竖线把输入同时送到每一行 */}
          <svg width={1080} height={1900} style={{position: 'absolute', left: 0, top: 0}}>
            {[0, 1].map((j) => (
              <g key={j} opacity={bus}>
                <line x1={IX[j]} y1={IY + 80} x2={IX[j]} y2={EXTRA[2] - 80} stroke={C.ai} strokeWidth={8} opacity={0.35} />
                {fire > 0 && <line x1={IX[j]} y1={IY + 80} x2={IX[j]} y2={lerp(IY + 80, EXTRA[2] - 80, prog(f, fireT - 6, 8))} stroke={C.ai} strokeWidth={12} />}
              </g>
            ))}
            {/* 第 2 行的连线：从同一个输入绕到外侧落下 */}
            <path d={`M${IX[0] - 60},${IY + 80} C ${IX[0] - 200},${IY + 300} ${IX[0] - 200},${R2Y - 250} ${IX[0] - 40},${R2Y - 80}`} fill="none" stroke={C.ai} strokeWidth={6} strokeDasharray="18 12" opacity={r2 * (1 - bus)} />
            <path d={`M${IX[1] + 60},${IY + 80} C ${IX[1] + 150},${IY + 300} ${IX[1] + 150},${R2Y - 250} ${IX[1] + 40},${R2Y - 80}`} fill="none" stroke={C.ai} strokeWidth={6} strokeDasharray="18 12" opacity={r2 * (1 - bus)} />
            {/* 第 1 行的连线：直下 */}
            {[0, 1].map((j) => <line key={j} x1={IX[j]} y1={IY + 80} x2={IX[j]} y2={R1Y - 80} stroke={C.ai} strokeWidth={6} opacity={r1 * (1 - bus)} />)}
          </svg>
          <Chip x={IX[0]} y={IY} v="2" color={C.ai} o={gather >= 1 ? 1 : 0} glow={(f < c3 ? 0.45 + 0.45 * Math.sin(f * 0.3) : 0) + prog(f, c4, 6) * (1 - prog(f, c4 + 12, 10)) + fire * 0.5} />
          <Chip x={IX[1]} y={IY} v="3" color={C.ai} o={gather >= 1 ? 1 : 0} glow={(f < c3 ? 0.45 + 0.45 * Math.sin(f * 0.3 + 1) : 0) + prog(f, c4, 6) * (1 - prog(f, c4 + 12, 10)) + fire * 0.5} />
          {/* 输入的复制：落到第 1 行 */}
          <Chip x={IX[0]} y={lerp(IY, R1Y, g1a)} v="2" color={C.ai} size={110} o={g1a > 0 && g1a < 1 ? 1 : 0} />
          <Chip x={IX[1]} y={lerp(IY, R1Y, g1b)} v="3" color={C.ai} size={110} o={g1b > 0 && g1b < 1 ? 1 : 0} />
          {/* 输入的复制：绕到第 2 行 */}
          {g2 > 0 && g2 < 1 && (() => {
            const pa = bez([IX[0] - 60, IY + 80], [IX[0] - 200, IY + 300], [IX[0] - 200, R2Y - 250], [IX[0], R2Y], g2);
            const pb = bez([IX[1] + 60, IY + 80], [IX[1] + 150, IY + 300], [IX[1] + 150, R2Y - 250], [IX[1], R2Y], g2);
            return <><Chip x={pa[0]} y={pa[1]} v="2" color={C.ai} size={110} /><Chip x={pb[0]} y={pb[1]} v="3" color={C.ai} size={110} /></>;
          })()}
          {/* 行标签：这些是模型里的参数（不是从问题变来的） */}
          <div style={{position: 'absolute', left: 40, top: R1Y - 28, fontFamily: FONT.hei, fontWeight: 700, fontSize: 44, color: C.sub, opacity: r1 * (1 - pull)}}>参数</div>
          <div style={{position: 'absolute', left: 40, top: R2Y - 28, fontFamily: FONT.hei, fontWeight: 700, fontSize: 44, color: C.sub, opacity: r2 * (1 - pull)}}>参数</div>
          <div style={{position: 'absolute', left: IX[0] - 75, top: R1Y + 92, fontFamily: FONT.hei, fontSize: 32, color: C.sub, opacity: r1 * (1 - r2)}}>模型里的数字</div>
          {/* 第 1 行 */}
          <Chip x={IX[0]} y={R1Y} v="4" color={C.ink} o={r1} glow={g1a >= 1 ? 0.5 * (1 - fuse1) : 0} />
          <Chip x={IX[1]} y={R1Y} v="5" color={C.ink} o={r1} glow={g1b >= 1 ? 0.5 * (1 - fuse1) : 0} />
          {outChip(R1Y, '23', fuse1, p1a, p1b, '8', '15', 1)}
          {/* 第 2 行 */}
          <Chip x={IX[0]} y={R2Y} v="1" color={C.ink} o={r2} glow={g2 >= 1 ? 0.5 * (1 - fuse2) : 0} />
          <Chip x={IX[1]} y={R2Y} v="6" color={C.ink} o={r2} glow={g2 >= 1 ? 0.5 * (1 - fuse2) : 0} />
          {outChip(R2Y, '20', fuse2, p2a, p2b, '2', '18', 2)}
          {/* 更多行：不放数字 */}
          {EXTRA.map((y, k) => (
            <div key={k} style={{opacity: more(k), transform: `translateY(${(1 - more(k)) * 60}px)`}}>
              <Chip x={IX[0]} y={y} v="" color={C.sub} />
              <Chip x={IX[1]} y={y} v="" color={C.sub} />
              <Chip x={OX} y={y} v="" color={C.ai} fill={`rgba(104,168,255,${0.12 + 0.45 * fired})`} glow={fire * 0.9} />
            </div>
          ))}
        </AbsoluteFill>
      </Drift>
      <Note top={1490} opacity={toNums * (1 - gather) * 0.9}>示意数字</Note>
      <Note top={1490} opacity={prog(f, c4, 10) * 0.9}>简化示意：每一行参数 × 同一个输入 → 一个输出</Note>
    </AbsoluteFill>
  );
};
