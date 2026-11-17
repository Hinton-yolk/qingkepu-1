import {AbsoluteFill, Sequence, useCurrentFrame} from 'remotion';
import chip from '../anchors/CHIP.json';
import {C, FONT} from '../lib/theme';
import {cue, ease, easeIO, lerp, prog, sec} from '../lib/time';
import {Note, Plate, Tag} from '../lib/ui';
import {GPU_BOX, GPU_GRID, GpuDie} from './SeqD';

// E 段：抽象的 GPU 版图里点出「专门算矩阵乘法的单元」→ 版图放大、对齐到 Blender 俯视镜头里真实大芯片的位置，
// 叠化成写实画面 → 相机拉远、倾斜，露出两侧的 HBM 堆叠 → 数据从 HBM 送进芯片（示意）→ 下一个问题：数字放在哪、怎么送
export const SeqE: React.FC<{from: number}> = ({from}) => {
  const f = useCurrentFrame() + from;
  const e1 = cue('E1'), e2 = cue('E2'), e3 = cue('E3');
  const T_CHIP = e1 + sec(2.55);                  // 写实镜头从这一帧开始（第 1 帧是俯视、静止）
  const inK = prog(f, from, 10);
  const tc = prog(f, e1 + sec(1.0), 12);          // 矩阵单元高亮
  // 版图 → 真实芯片的位置（CHIP 镜头第 1 帧大芯片四角的投影）
  const d0 = chip.frames[0].die;
  const xs = d0.map((d) => d[0] * 1080), ys = d0.map((d) => d[1] * 1920);
  const target = {x: Math.min(...xs), y: Math.min(...ys), w: Math.max(...xs) - Math.min(...xs), h: Math.max(...ys) - Math.min(...ys)};
  const grow = prog(f, T_CHIP - sec(1.0), sec(0.9), easeIO);
  const xfade = prog(f, T_CHIP, sec(0.6), ease);
  const sx = lerp(1, target.w / GPU_BOX.w, grow), sy = lerp(1, target.h / GPU_BOX.h, grow);
  const tx = lerp(0, target.x - GPU_BOX.x * sx, grow), ty = lerp(0, target.y - GPU_BOX.y * sy, grow);

  const cf = Math.max(0, Math.min(chip.frames.length - 1, f - T_CHIP));
  const fr = chip.frames[cf];
  const hbmTag = prog(f, e2 + sec(0.2), 12);
  const flow = prog(f, e2 + sec(0.8), 10);
  const q = prog(f, e3 + sec(0.1), 14);
  const nextK = prog(f, e3 + sec(1.6), 12);
  // 芯片中心
  const dc = [fr.die.reduce((a, d) => a + d[0], 0) / 4 * 1080, fr.die.reduce((a, d) => a + d[1], 0) / 4 * 1920];

  return (
    <AbsoluteFill style={{background: C.bg}}>
      {/* 写实：俯视 → 拉远 */}
      <Sequence from={T_CHIP - from} layout="none">
        {/* 写实镜头开头 1.5 秒俯视静止：在合成里加一点慢推（从 1.0 开始，对齐不受影响） */}
        <AbsoluteFill style={{opacity: xfade, transform: `scale(${1 + 0.018 * Math.min(1.6, Math.max(0, (f - T_CHIP) / 30))})`,
          transformOrigin: `${(xs[0] + xs[1] + xs[2] + xs[3]) / 4}px ${(ys[0] + ys[1] + ys[2] + ys[3]) / 4}px`}}>
          <Plate name="CHIP" />
          <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(8,9,11,0.65) 0%, rgba(8,9,11,0) 26%, rgba(8,9,11,0) 70%, rgba(8,9,11,0.6) 100%)'}} />
          {/* HBM：标签 + 送数据的点（从每颗 HBM 中心流向芯片边缘，示意） */}
          {hbmTag > 0 && (
            <svg width={1080} height={1920} style={{position: 'absolute', left: 0, top: 0}}>
              {fr.hbm.map((h, i) => {
                const hx = h[0] * 1080, hy = h[1] * 1920;
                const ex = lerp(hx, dc[0], 0.36), ey = lerp(hy, dc[1], 0.36);   // 停在芯片边缘（数据经中介层布线进芯片边上的接口）
                return (
                  <g key={i} opacity={hbmTag}>
                    <circle cx={hx} cy={hy} r={10} fill="none" stroke={C.ink} strokeWidth={3} />
                    {flow > 0 && Array.from({length: 4}, (_, k) => {
                      const t = ((f - e2) / 22 + k / 4 + i * 0.13) % 1;
                      return <circle key={k} cx={lerp(hx, ex, t)} cy={lerp(hy, ey, t)} r={6} fill={C.ink} opacity={flow * Math.sin(t * Math.PI)} />;
                    })}
                  </g>
                );
              })}
            </svg>
          )}
          {hbmTag > 0 && (() => {
            // 左边一列 HBM（0–2）里最上面那颗的上方，不压在 GPU 芯片上
            const top = [fr.hbm[0], fr.hbm[1], fr.hbm[2]].reduce((m, h) => (h[1] < m[1] ? h : m));
            return <Tag x={Math.max(150, top[0] * 1080)} y={top[1] * 1920 - 80} text="HBM 显存" anchor="center" opacity={hbmTag} size={44} />;
          })()}
          {hbmTag > 0 && <Tag x={dc[0]} y={dc[1] - 40} text="GPU" anchor="center" opacity={hbmTag * (1 - q * 0.6)} size={44} />}
        </AbsoluteFill>
      </Sequence>

      {/* 抽象版图（接 D 段），放大对齐到真实芯片后淡出 */}
      {xfade < 1 && (
        <AbsoluteFill style={{opacity: inK * (1 - xfade)}}>
          <div style={{position: 'absolute', left: 0, top: 0, width: 1080, height: 1920, transform: `translate(${tx}px, ${ty}px) scale(${sx}, ${sy})`, transformOrigin: '0 0'}}>
            <GpuDie f={f} build={1} fire={0.35 + 0.2 * Math.sin(f * 0.5)} instr={0} label={1 - grow} />
            {/* 每个块里一小块「矩阵乘法单元」 */}
            {Array.from({length: GPU_GRID.cols * GPU_GRID.rows}, (_, b) => {
              const c = b % GPU_GRID.cols, r = Math.floor(b / GPU_GRID.cols);
              const bw = (GPU_BOX.w - 40) / GPU_GRID.cols, bh = (GPU_BOX.h - 80) / GPU_GRID.rows;
              return (
                <div key={b} style={{position: 'absolute', left: GPU_BOX.x + 20 + c * bw + bw - 50, top: GPU_BOX.y + 60 + r * bh + bh - 46, width: 38, height: 34, borderRadius: 4,
                  background: C.ai, opacity: tc, boxShadow: `0 0 ${12 * tc}px ${C.ai}`}} />
              );
            })}
          </div>
          <div style={{position: 'absolute', left: 0, right: 0, top: 380, textAlign: 'center', opacity: tc * (1 - grow)}}>
            <div style={{fontFamily: FONT.hei, fontWeight: 700, fontSize: 52, color: C.ai}}>专门算矩阵乘法的单元</div>
            <div style={{fontFamily: FONT.hei, fontSize: 34, color: C.sub, marginTop: 14}}>一次算一小块矩阵的乘加（如英伟达的「张量核心」）</div>
          </div>
          <div style={{position: 'absolute', left: 0, right: 0, top: 560, textAlign: 'center', fontFamily: FONT.num, fontSize: 52, color: C.ink, opacity: tc * (1 - grow)}}>
            D = A × B + C
            <div style={{fontFamily: FONT.hei, fontSize: 30, color: C.sub, marginTop: 10}}>A、B、C、D 都是小矩阵（如 4×4）</div>
          </div>
        </AbsoluteFill>
      )}

      {/* 结尾的问题 */}
      <div style={{position: 'absolute', left: 0, right: 0, top: 200, textAlign: 'center', fontFamily: FONT.title, opacity: q, transform: `translateY(${(1 - q) * 24}px)`,
        textShadow: '0 4px 24px rgba(0,0,0,0.85)'}}>
        <div style={{fontSize: 100, color: C.ink}}>算得再快</div>
        <div style={{fontSize: 100, color: C.ai}}>数字怎么及时送到？</div>
      </div>
      <div style={{position: 'absolute', right: 64, top: 1300, fontFamily: FONT.hei, fontWeight: 700, fontSize: 34, color: C.ink, opacity: nextK,
        padding: '8px 18px', border: `2px solid ${C.ink}`, borderRadius: 10, background: 'rgba(12,13,16,0.6)'}}>下一段：显存与数据搬运 →</div>
      <Note top={1490} opacity={prog(f, T_CHIP + sec(0.6), 10) * 0.9}>示意：通用 AI 加速器，非特定型号；数据流向为示意</Note>
    </AbsoluteFill>
  );
};
