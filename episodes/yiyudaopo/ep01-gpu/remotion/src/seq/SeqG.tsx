import {AbsoluteFill, Sequence, useCurrentFrame} from 'remotion';
import srv from '../anchors/SERVER.json';
import {C, FONT} from '../lib/theme';
import {cue, ease, easeIO, lerp, prog, sec} from '../lib/time';
import {Note, Plate, Tag} from '../lib/ui';

// G 段（一块 GPU 不够）：写实镜头从一块 GPU 封装慢慢拉远 → 模组 → 一台服务器里的 8 块加速器（Blender 灰模级底片，本机渲）
// 叠加层：一块 GPU 的两个上限（显存、算力）→ 模型太大装不下 → 任务太多排长队 →「怎么办？」
// → 拉远看到 8 块 → 模型拆成几份放到几块上（分担不同部分）、一大批任务分给另外几块（一起处理更大的任务）。
type P = number[];
const SLOW = 0.32;                         // 讲「上限」时，底片几乎停在一块 GPU 上

export const SeqG: React.FC<{from: number}> = ({from}) => {
  const f = useCurrentFrame() + from;
  const g1 = cue('G1'), g2 = cue('G2'), g3 = cue('G3'), g4 = cue('G4'), g5 = cue('G5'), g6 = cue('G6'), g7 = cue('G7'), g8 = cue('G8');
  const END = cue('H1') - sec(0.35);
  const split = g5;                                                   // 从这里开始快速拉远
  const srcSplit = Math.round((split - from) * SLOW);
  const rate2 = (srv.frames.length - 1 - srcSplit) / Math.max(1, END + 12 - split);
  const srcF = f < split ? (f - from) * SLOW : srcSplit + (f - split) * rate2;
  const fr = srv.frames[Math.max(0, Math.min(srv.frames.length - 1, Math.floor(srcF)))] as {die: P[]; mods: P[]};
  const mods = fr.mods.map((m) => [m[0] * 1080, m[1] * 1920]);
  const inK = prog(f, from, 12);
  // 叠加层时间
  const bars = prog(f, g1 + sec(0.4), 12) * (1 - prog(f, g5, 10));
  const model = prog(f, g2 + sec(0.2), 16, easeIO);
  const over = prog(f, g2 + sec(1.4), 10);
  const queue = prog(f, g3 + sec(0.2), 18, easeIO);
  const how = prog(f, g4, 6) * (1 - prog(f, g5, 8));
  const rings = (i: number) => prog(f, g5 + sec(0.6) + i * 2, 8);
  const share = prog(f, g6 + sec(0.3), 20, easeIO);
  const shareB = prog(f, g6 + sec(2.4), 20, easeIO);
  const count = prog(f, g7, 10);
  const srvTag = prog(f, g8 + sec(0.3), 10);
  const BX = 700, BY0 = 560, BH = 460;                                // 两根「上限」柱
  const slice = (i: number) => ({x: lerp(300 + i * 70, mods[i][0], share), y: lerp(330, mods[i][1], share)});
  const batch = (i: number) => ({x: lerp(120 + i * 60, mods[4 + i][0], shareB), y: lerp(1290, mods[4 + i][1], shareB)});

  return (
    <AbsoluteFill style={{background: C.bg, transform: `scale(${1.03 + 0.004 * (f - from) / 30}) translate(${10 * Math.sin((f - from) / 30 * 0.8)}px, ${8 * Math.cos((f - from) / 30 * 0.8)}px)`, transformOrigin: '50% 50%'}}>
      <AbsoluteFill style={{opacity: inK}}>
        <Sequence from={0} durationInFrames={split - from} layout="none">
          <Plate name="SERVER" rate={SLOW} />
        </Sequence>
        <Sequence from={split - from} layout="none">
          <Plate name="SERVER" rate={rate2} startFrom={srcSplit} />
        </Sequence>
      </AbsoluteFill>
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(8,9,11,0.75) 0%, rgba(8,9,11,0.12) 30%, rgba(8,9,11,0) 66%, rgba(8,9,11,0.6) 100%)'}} />

      {/* 一块 GPU 的两个上限 */}
      {bars > 0 && (
        <AbsoluteFill style={{opacity: bars}}>
          {[['显存', C.ai, 0.88], ['算力', C.game, 0.9]].map(([lab, col, v], k) => (
            <div key={k}>
              <div style={{position: 'absolute', left: BX + k * 90, top: BY0, width: 64, height: BH, borderRadius: 12, border: `4px solid ${C.ink}`, background: 'rgba(12,13,16,0.75)'}}>
                <div style={{position: 'absolute', left: 4, right: 4, bottom: 4, height: (BH - 8) * (v as number), borderRadius: 8, background: col as string, opacity: 0.85}} />
              </div>
              <div style={{position: 'absolute', left: BX + k * 90 + 32, top: BY0 + BH + 14, transform: 'translateX(-50%)', fontFamily: FONT.hei, fontWeight: 700, fontSize: 38, color: C.ink,
                textShadow: '0 2px 8px rgba(0,0,0,0.9)'}}>{lab}</div>
            </div>
          ))}
          <div style={{position: 'absolute', left: BX - 20, top: BY0 - 6, width: 200, height: 6, background: C.warn}} />
          <div style={{position: 'absolute', left: BX - 10, top: BY0 - 58, fontFamily: FONT.hei, fontWeight: 700, fontSize: 38, color: C.warn, textShadow: '0 2px 8px rgba(0,0,0,0.9)'}}>上限</div>
          {/* 模型太大：一大摞参数落进显存柱，多出来的那截在上限之上 */}
          {model > 0 && Array.from({length: 9}, (_, k) => {
            const yy = lerp(-200 - k * 60, BY0 + BH - 30 - k * 62, model);
            const outside = BY0 + BH - 30 - k * 62 < BY0;
            return <div key={k} style={{position: 'absolute', left: BX + 4, top: yy, width: 56, height: 50, borderRadius: 8,
              background: outside && over > 0.5 ? C.warn : C.ai, border: `3px solid ${C.ink}`, opacity: 0.95}} />;
          })}
          <div style={{position: 'absolute', left: BX - 250, top: BY0 - 150, fontFamily: FONT.hei, fontWeight: 700, fontSize: 44, color: C.warn, opacity: over,
            textShadow: '0 2px 10px rgba(0,0,0,0.95)'}}>模型太大，装不下</div>
          {/* 任务太多：长长一队 */}
          {queue > 0 && Array.from({length: 13}, (_, k) => (
            <div key={k} style={{position: 'absolute', left: lerp(-760, 60, queue) + k * 58 + ((f - g3) % 20) * 2.9 * (queue >= 1 ? 1 : 0), top: 1270, width: 48, height: 48, borderRadius: 8, background: 'rgba(240,160,64,0.6)',
              border: `3px solid ${C.game}`}} />
          ))}
          <div style={{position: 'absolute', left: 60, top: 1205, fontFamily: FONT.hei, fontWeight: 700, fontSize: 42, color: C.game, opacity: prog(f, g3 + sec(1.2), 10),
            textShadow: '0 2px 10px rgba(0,0,0,0.95)'}}>算的活太多，排很长的队</div>
        </AbsoluteFill>
      )}
      <div style={{position: 'absolute', left: 0, right: 0, top: 820, textAlign: 'center', fontFamily: FONT.title, fontSize: 150, color: C.ink, opacity: how,
        textShadow: '0 4px 30px rgba(0,0,0,0.95)'}}>怎么办？</div>

      {/* 多块 GPU：每块一个圈；模型拆开放在 0–3 号，一批任务分给 4–7 号 */}
      {f >= g5 && (
        <svg width={1080} height={1920} style={{position: 'absolute', left: 0, top: 0}}>
          {mods.map((m, i) => (
            <circle key={i} cx={m[0]} cy={m[1]} r={lerp(70, 44, prog(f, g5, sec(4)))} fill="none" stroke={i < 4 ? C.ai : C.game} strokeWidth={6} opacity={rings(i) * (1 - srvTag * 0.6)} />
          ))}
        </svg>
      )}
      {share > 0 && share < 1 && Array.from({length: 4}, (_, i) => {
        const p = slice(i);
        return <div key={'s' + i} style={{position: 'absolute', left: p.x - 28, top: p.y - 22, width: 56, height: 44, borderRadius: 8, background: C.ai, border: `3px solid ${C.ink}`}} />;
      })}
      {shareB > 0 && shareB < 1 && Array.from({length: 4}, (_, i) => {
        const p = batch(i);
        return <div key={'b' + i} style={{position: 'absolute', left: p.x - 24, top: p.y - 24, width: 48, height: 48, borderRadius: 8, background: 'rgba(240,160,64,0.8)', border: `3px solid ${C.game}`}} />;
      })}
      <div style={{position: 'absolute', left: 60, top: 200, fontFamily: FONT.hei, fontWeight: 700, fontSize: 42, color: C.ai, opacity: share * (1 - count), textShadow: '0 2px 10px rgba(0,0,0,0.95)'}}>
        ■ 模型拆开，每块放一部分
      </div>
      <div style={{position: 'absolute', left: 60, top: 262, fontFamily: FONT.hei, fontWeight: 700, fontSize: 42, color: C.game, opacity: shareB * (1 - count), textShadow: '0 2px 10px rgba(0,0,0,0.95)'}}>
        ■ 任务分开，每块算一批
      </div>
      <div style={{position: 'absolute', left: 0, right: 0, top: 190, textAlign: 'center', fontFamily: FONT.title, fontSize: 120, color: C.ink, opacity: count * (1 - srvTag),
        textShadow: '0 4px 24px rgba(0,0,0,0.95)'}}>1 → 8</div>
      <Tag x={540} y={300} text="一台服务器里的 8 块加速器" anchor="center" size={48} opacity={srvTag} />
      <Note top={1490} box opacity={prog(f, g5 + sec(0.5), 10)}>示意：拿掉了散热器；不是每次提问都要很多 GPU</Note>
    </AbsoluteFill>
  );
};
