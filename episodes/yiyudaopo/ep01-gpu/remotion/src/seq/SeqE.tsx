import {AbsoluteFill, Sequence, useCurrentFrame} from 'remotion';
import chip from '../anchors/CHIP.json';
import {C, FONT} from '../lib/theme';
import {cue, ease, easeIO, lerp, prog, sec} from '../lib/time';
import {Note, Plate, Tag} from '../lib/ui';
import {GPU_BOX, GPU_GRID, GpuDie} from './SeqD';

// v03 E 段：GPU 版图点出「专门的矩阵单元」→ 放大对齐真实芯片、叠化成写实镜头
// → 叠加层只标两块：中间的「计算」区、两侧的「显存（HBM）」；数据带方向地从显存流向计算区
// → 数据来得慢：计算区变灰、在等 →「算得快还不够。数据又是怎么及时送到芯片上的？」
const RATE = 0.8;
type P = number[];
const toPx = (p: P) => [p[0] * 1080, p[1] * 1920];
const polyStr = (q: P[]) => q.map((p) => toPx(p).join(',')).join(' ');

export const SeqE: React.FC<{from: number}> = ({from}) => {
  const f = useCurrentFrame() + from;
  const e1 = cue('E1'), e3 = cue('E3');
  const e2 = cue('E1') + sec(3.6);   // 全集：E2 那句移到 F 段，这里只是标注出现的时间点
  const T_CHIP = e1 + sec(3.0);
  const inK = prog(f, from, 10);
  const tc = prog(f, e1 + sec(0.8), 12);
  const d0 = chip.frames[0].die;
  const xs = d0.map((d) => d[0] * 1080), ys = d0.map((d) => d[1] * 1920);
  const target = {x: Math.min(...xs), y: Math.min(...ys), w: Math.max(...xs) - Math.min(...xs), h: Math.max(...ys) - Math.min(...ys)};
  const grow = prog(f, T_CHIP - sec(0.9), sec(0.85), easeIO);
  const xfade = prog(f, T_CHIP, sec(0.6), ease);
  const sx = lerp(1, target.w / GPU_BOX.w, grow), sy = lerp(1, target.h / GPU_BOX.h, grow);
  const tx = lerp(0, target.x - GPU_BOX.x * sx, grow), ty = lerp(0, target.y - GPU_BOX.y * sy, grow);

  const fr = chip.frames[Math.max(0, Math.min(chip.frames.length - 1, Math.floor((f - T_CHIP) * RATE)))] as {die: P[]; hbm: P[]; hbmq: P[][]};
  const dc = [fr.die.reduce((a, d) => a + d[0], 0) / 4 * 1080, fr.die.reduce((a, d) => a + d[1], 0) / 4 * 1920];
  const computeTag = prog(f, T_CHIP + sec(0.7), 10);
  const memTag = prog(f, e2 + sec(0.1), 12);
  const waiting = 0;                                      // 「在等数据」放到 F 段讲
  const flow = prog(f, e2 + sec(0.6), 10);
  const q = prog(f, cue('E3') - 4, 14);
  const pushK = 1 + 0.018 * Math.min(1.6, Math.max(0, (f - T_CHIP) / 30));
  const t = (f - e2) / 30;

  return (
    <AbsoluteFill style={{background: C.bg}}>
      <Sequence from={T_CHIP - from} layout="none">
        <AbsoluteFill style={{opacity: xfade, transform: `scale(${pushK})`, transformOrigin: `${(xs[0] + xs[1] + xs[2] + xs[3]) / 4}px ${(ys[0] + ys[1] + ys[2] + ys[3]) / 4}px`}}>
          <Plate name="CHIP" rate={RATE} />
          <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(8,9,11,0.78) 0%, rgba(8,9,11,0.15) 30%, rgba(8,9,11,0) 66%, rgba(8,9,11,0.6) 100%)'}} />
          <svg width={1080} height={1920} style={{position: 'absolute', left: 0, top: 0}}>
            {/* 显存（HBM）：每颗一圈白框 */}
            {fr.hbmq.map((qd, i) => <polygon key={i} points={polyStr(qd)} fill="rgba(255,255,255,0.06)" stroke={C.ink} strokeWidth={4} strokeLinejoin="round" opacity={memTag * 0.9} />)}
            {/* 计算区：蓝框；等数据时变灰、虚线 */}
            <polygon points={polyStr(fr.die)} fill={`rgba(104,168,255,${0.14 * (1 - waiting)})`} stroke={waiting > 0.5 ? C.sub : C.ai} strokeWidth={7}
              strokeDasharray={waiting > 0.5 ? '22 16' : undefined} strokeLinejoin="round" opacity={computeTag} />
            {/* 数据：从每颗显存朝计算区流（带方向的小箭头），来得稀 */}
            {fr.hbm.map((h, i) => {
              const a = toPx(h), b = dc;
              const ex = lerp(a[0], b[0], 0.42), ey = lerp(a[1], b[1], 0.42);
              const ang = Math.atan2(ey - a[1], ex - a[0]) * 180 / Math.PI;
              return (
                <g key={i} opacity={flow}>
                  {[0, 1].map((k) => {
                    const u = ((t / 1.6 + k * 0.5 + i * 0.13) % 1);
                    const x = lerp(a[0], ex, u), y = lerp(a[1], ey, u);
                    return (
                      <g key={k} transform={`translate(${x},${y}) rotate(${ang})`} opacity={Math.sin(u * Math.PI)}>
                        <path d="M-30,-27 L14,0 L-30,27" fill="none" stroke="rgba(8,9,11,0.85)" strokeWidth={20} strokeLinecap="round" strokeLinejoin="round" />
                        <path d="M-30,-27 L14,0 L-30,27" fill="none" stroke={C.ink} strokeWidth={10} strokeLinecap="round" strokeLinejoin="round" />
                      </g>
                    );
                  })}
                </g>
              );
            })}
          </svg>
          <div style={{position: 'absolute', left: dc[0], top: dc[1], transform: 'translate(-50%,-50%)', opacity: computeTag, fontFamily: FONT.hei, fontWeight: 700,
            fontSize: waiting > 0.5 ? 60 : 54, color: waiting > 0.5 ? C.ink : C.ai, background: 'rgba(10,11,13,0.82)', padding: '10px 26px', borderRadius: 14,
            border: `3px solid ${waiting > 0.5 ? C.sub : C.ai}`, whiteSpace: 'nowrap'}}>{waiting > 0.5 ? '在等数据…' : '计算'}</div>
          {(() => {
            const top = [fr.hbm[0], fr.hbm[1], fr.hbm[2]].map(toPx).reduce((m, h) => (h[1] < m[1] ? h : m));
            return <Tag x={Math.max(200, top[0] - 30)} y={top[1] - 120} text="显存（HBM）" anchor="center" opacity={memTag} size={50} />;
          })()}
        </AbsoluteFill>
      </Sequence>

      {/* 抽象版图（接 D 段的 GPU 运算单元）：点出矩阵单元，放大对齐真实芯片后淡出 */}
      {xfade < 1 && (
        <AbsoluteFill style={{opacity: inK * (1 - xfade)}}>
          <div style={{position: 'absolute', left: 0, top: 0, width: 1080, height: 1920, transform: `translate(${tx}px, ${ty}px) scale(${sx}, ${sy})`, transformOrigin: '0 0'}}>
            <GpuDie f={f} build={1} fire={0.3 + 0.2 * Math.sin(f * 0.5)} instr={0} label={1 - grow} />
            {Array.from({length: GPU_GRID.cols * GPU_GRID.rows}, (_, b) => {
              const c = b % GPU_GRID.cols, r = Math.floor(b / GPU_GRID.cols);
              const bw = (GPU_BOX.w - 40) / GPU_GRID.cols, bh = (GPU_BOX.h - 80) / GPU_GRID.rows;
              return <div key={b} style={{position: 'absolute', left: GPU_BOX.x + 20 + c * bw + bw - 54, top: GPU_BOX.y + 60 + r * bh + bh - 50, width: 44, height: 40, borderRadius: 5,
                background: C.ai, opacity: tc, boxShadow: `0 0 ${16 * tc}px ${C.ai}`}} />;
            })}
          </div>
          <div style={{position: 'absolute', left: 0, right: 0, top: 380, textAlign: 'center', opacity: tc * (1 - grow), fontFamily: FONT.title, fontSize: 92, color: C.ai, lineHeight: 1.15}}>
            专门的<br />矩阵计算单元
          </div>
        </AbsoluteFill>
      )}

      {/* 结尾的问题 */}
      <div style={{position: 'absolute', left: 0, right: 0, top: 190, textAlign: 'center', fontFamily: FONT.title, opacity: q, transform: `translateY(${(1 - q) * 24}px)`,
        textShadow: '0 4px 24px rgba(0,0,0,0.95)'}}>
        <div style={{fontSize: 96, color: C.ink}}>算得快还不够。</div>
        <div style={{fontSize: 84, color: C.ai, lineHeight: 1.15}}>数据又是怎么<br />及时送到芯片上的？</div>
      </div>
      <Note top={1490} opacity={xfade * 0.9}>示意：通用 AI 加速器，非特定型号；数据流向为示意</Note>
    </AbsoluteFill>
  );
};
