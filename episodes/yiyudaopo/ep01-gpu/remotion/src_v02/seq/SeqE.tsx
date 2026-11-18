import {AbsoluteFill, Sequence, useCurrentFrame} from 'remotion';
import chip from '../anchors/CHIP.json';
import {C, FONT} from '../lib/theme';
import {cue, ease, easeIO, lerp, prog, sec} from '../lib/time';
import {Note, Plate, Tag} from '../lib/ui';
import {GPU_BOX, GPU_GRID, GpuDie} from './SeqD';

// v02 E 段：GPU 版图里点亮「专门加速矩阵计算的硬件」（不再出公式）→ 版图放大、对齐真实芯片、叠化成写实俯视
// → 慢慢拉远露出 HBM →「算得快就够了吗？」→ 数据送得慢：计算单元在等 → 显存和数据搬运同样重要 → 下一个问题
const RATE = 0.6;   // 写实底片只有 10 秒，这段要 16 秒：慢放（不重渲）

export const SeqE: React.FC<{from: number}> = ({from}) => {
  const f = useCurrentFrame() + from;
  const e1 = cue('E1'), e2 = cue('E2'), e3 = cue('E3'), e4 = cue('E4'), e5 = cue('E5'), e6 = cue('E6');
  const T_CHIP = e1 + sec(3.0);
  const inK = prog(f, from, 10);
  const tc = prog(f, e1 + sec(0.9), 12);
  const d0 = chip.frames[0].die;
  const xs = d0.map((d) => d[0] * 1080), ys = d0.map((d) => d[1] * 1920);
  const target = {x: Math.min(...xs), y: Math.min(...ys), w: Math.max(...xs) - Math.min(...xs), h: Math.max(...ys) - Math.min(...ys)};
  const grow = prog(f, T_CHIP - sec(0.9), sec(0.85), easeIO);
  const xfade = prog(f, T_CHIP, sec(0.6), ease);
  const sx = lerp(1, target.w / GPU_BOX.w, grow), sy = lerp(1, target.h / GPU_BOX.h, grow);
  const tx = lerp(0, target.x - GPU_BOX.x * sx, grow), ty = lerp(0, target.y - GPU_BOX.y * sy, grow);

  const cf = Math.max(0, Math.min(chip.frames.length - 1, Math.floor((f - T_CHIP) * RATE)));
  const fr = chip.frames[cf];
  const dc = [fr.die.reduce((a, d) => a + d[0], 0) / 4 * 1080, fr.die.reduce((a, d) => a + d[1], 0) / 4 * 1920];
  const q2 = prog(f, e2, 10) * (1 - prog(f, e3 + sec(0.2), 10));
  const wait = prog(f, e3 + sec(0.6), 10) * (1 - prog(f, e4 + sec(0.3), 10));
  const hbm = prog(f, e3 + sec(0.2), 12);
  const fast = prog(f, e4, 12);                              // 数据送得上：点流变快、变密
  const q5 = prog(f, e5, 14);
  const nextK = prog(f, e6, 12);
  const pushK = 1 + 0.018 * Math.min(1.6, Math.max(0, (f - T_CHIP) / 30));

  return (
    <AbsoluteFill style={{background: C.bg}}>
      <Sequence from={T_CHIP - from} layout="none">
        <AbsoluteFill style={{opacity: xfade, transform: `scale(${pushK})`, transformOrigin: `${(xs[0] + xs[1] + xs[2] + xs[3]) / 4}px ${(ys[0] + ys[1] + ys[2] + ys[3]) / 4}px`}}>
          <Plate name="CHIP" rate={RATE} />
          <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(8,9,11,0.72) 0%, rgba(8,9,11,0.1) 28%, rgba(8,9,11,0) 68%, rgba(8,9,11,0.6) 100%)'}} />
          <svg width={1080} height={1920} style={{position: 'absolute', left: 0, top: 0}}>
            {fr.hbm.map((h, i) => {
              const hx = h[0] * 1080, hy = h[1] * 1920;
              const ex = lerp(hx, dc[0], 0.36), ey = lerp(hy, dc[1], 0.36);
              const n = fast > 0.5 ? 5 : 1;                        // 慢：一颗一颗；快：一串
              const speed = lerp(70, 18, fast);
              return (
                <g key={i} opacity={hbm}>
                  <circle cx={hx} cy={hy} r={12} fill="none" stroke={C.ink} strokeWidth={3} />
                  {Array.from({length: n}, (_, k) => {
                    const tt = ((f - e3) / speed + k / n + i * 0.17) % 1;
                    return <circle key={k} cx={lerp(hx, ex, tt)} cy={lerp(hy, ey, tt)} r={7} fill={C.ink} opacity={Math.sin(tt * Math.PI)} />;
                  })}
                </g>
              );
            })}
            {/* 计算单元在等数据：芯片中心一个慢慢转的灰环 */}
            <circle cx={dc[0]} cy={dc[1]} r={70} fill="none" stroke={C.sub} strokeWidth={8} strokeDasharray="60 380" transform={`rotate(${(f * 3) % 360} ${dc[0]} ${dc[1]})`} opacity={wait} />
            <circle cx={dc[0]} cy={dc[1]} r={70} fill="none" stroke={C.ai} strokeWidth={6} opacity={fast * 0.8} />
          </svg>
          <Tag x={dc[0]} y={dc[1] + 120} text="计算单元：等数据…" anchor="center" opacity={wait} size={46} color={C.ink} />
          {(() => {
            const top = [fr.hbm[0], fr.hbm[1], fr.hbm[2]].reduce((m, h) => (h[1] < m[1] ? h : m));
            return <Tag x={Math.max(170, top[0] * 1080)} y={top[1] * 1920 - 80} text="HBM 显存" anchor="center" opacity={hbm * (1 - q5 * 0.5)} size={46} />;
          })()}
        </AbsoluteFill>
      </Sequence>

      {/* 抽象版图（接 D 段的 GPU）：点亮矩阵单元，放大对齐真实芯片后淡出 */}
      {xfade < 1 && (
        <AbsoluteFill style={{opacity: inK * (1 - xfade)}}>
          <div style={{position: 'absolute', left: 0, top: 0, width: 1080, height: 1920, transform: `translate(${tx}px, ${ty}px) scale(${sx}, ${sy})`, transformOrigin: '0 0'}}>
            <GpuDie f={f} build={1} fire={0.3 + 0.2 * Math.sin(f * 0.5)} instr={0} label={1 - grow} />
            {Array.from({length: GPU_GRID.cols * GPU_GRID.rows}, (_, b) => {
              const c = b % GPU_GRID.cols, r = Math.floor(b / GPU_GRID.cols);
              const bw = (GPU_BOX.w - 40) / GPU_GRID.cols, bh = (GPU_BOX.h - 80) / GPU_GRID.rows;
              return <div key={b} style={{position: 'absolute', left: GPU_BOX.x + 20 + c * bw + bw - 52, top: GPU_BOX.y + 60 + r * bh + bh - 48, width: 40, height: 36, borderRadius: 4,
                background: C.ai, opacity: tc, boxShadow: `0 0 ${14 * tc}px ${C.ai}`}} />;
            })}
          </div>
          <div style={{position: 'absolute', left: 0, right: 0, top: 360, textAlign: 'center', opacity: tc * (1 - grow)}}>
            <div style={{fontFamily: FONT.title, fontSize: 92, color: C.ai, lineHeight: 1.15}}>专门加速<br />矩阵计算的硬件</div>
            <div style={{fontFamily: FONT.hei, fontWeight: 700, fontSize: 40, color: C.sub, marginTop: 16}}>（比如英伟达的「张量核心」）</div>
          </div>
        </AbsoluteFill>
      )}

      {/* 字幕之外的大字：只放一个问题，不和字幕重复太多 */}
      <div style={{position: 'absolute', left: 0, right: 0, top: 200, textAlign: 'center', fontFamily: FONT.title, fontSize: 104, color: C.ink, opacity: q2,
        textShadow: '0 4px 24px rgba(0,0,0,0.9)'}}>算得快就够了吗？</div>
      <div style={{position: 'absolute', left: 0, right: 0, top: 190, textAlign: 'center', fontFamily: FONT.title, opacity: q5, transform: `translateY(${(1 - q5) * 24}px)`,
        textShadow: '0 4px 24px rgba(0,0,0,0.9)'}}>
        <div style={{fontSize: 100, color: C.ink}}>数字放在哪？</div>
        <div style={{fontSize: 100, color: C.ai}}>怎么送到芯片上？</div>
      </div>
      <div style={{position: 'absolute', right: 64, top: 1290, fontFamily: FONT.hei, fontWeight: 700, fontSize: 38, color: C.ink, opacity: nextK,
        padding: '8px 20px', border: `2px solid ${C.ink}`, borderRadius: 12, background: 'rgba(12,13,16,0.6)'}}>下一个问题 →</div>
      <Note top={1490} opacity={xfade * 0.9}>示意：通用 AI 加速器，非特定型号；数据流向为示意</Note>
    </AbsoluteFill>
  );
};
