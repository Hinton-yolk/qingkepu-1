import {AbsoluteFill, useCurrentFrame} from 'remotion';
import macro from '../anchors/MACRO.json';
import {C, FONT} from '../lib/theme';
import {cue, lerp, prog, sec} from '../lib/time';
import {Plate} from '../lib/ui';

// v03 A 段：一个焦点、一个问题。
// 0 帧：GPU 芯片微距（芯片被一圈光框住）+ 大字问题 →「却大量使用 GPU」切到一排排 GPU 服务器 →「为什么？」回到芯片，
// 芯片的方框在 B 段长成游戏画面（同一个矩形带过去）。这一段的旁白就是大字本身，不再出字幕（Captions.tsx 里跳过 A1、A2）。
export const T_MACRO = 0;
export const MACRO_BACK = 0;            // 回到芯片时从 MACRO 底片的第几帧开始（推得更近）

/** MACRO 底片某帧里大芯片的屏幕矩形 */
export const dieRect = (mf: number) => {
  const d = macro.frames[Math.max(0, Math.min(macro.frames.length - 1, mf))].die;
  const xs = d.map((p) => p[0] * 1080), ys = d.map((p) => p[1] * 1920);
  return {x: Math.min(...xs), y: Math.min(...ys), w: Math.max(...xs) - Math.min(...xs), h: Math.max(...ys) - Math.min(...ys), poly: d.map((p) => [p[0] * 1080, p[1] * 1920])};
};

export const SeqA: React.FC<{from: number}> = ({from}) => {
  // 全集组装修正 1：去掉「芯片 → 机房 → 芯片」的快切，开头只留一个芯片镜头（慢推）
  const f = useCurrentFrame() + from;
  const a1 = cue('A1'), a2 = cue('A2');
  const t = f / 30;
  const r = dieRect(f);
  const ring = prog(f, 8, 12);
  const poly = r.poly.map((p) => p.join(',')).join(' ');
  const l2 = prog(f, a1 + sec(0.95), 8);
  const why = prog(f, a2, 8);
  return (
    <AbsoluteFill style={{background: C.bg}}>
      <Plate name="MACRO" />
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(8,9,11,0.82) 0%, rgba(8,9,11,0.25) 34%, rgba(8,9,11,0) 55%, rgba(8,9,11,0.45) 100%)'}} />
      <svg width={1080} height={1920} style={{position: 'absolute', left: 0, top: 0}}>
        <polygon points={poly} fill="none" stroke={C.ai} strokeWidth={6} strokeLinejoin="round" opacity={ring * (0.75 + 0.25 * Math.sin(t * 4))} />
      </svg>
      <div style={{position: 'absolute', left: 0, right: 0, top: 150, textAlign: 'center', fontFamily: FONT.title, textShadow: '0 4px 28px rgba(0,0,0,0.95)'}}>
        <div style={{fontSize: 116, color: C.ink, lineHeight: 1.1}}>AI 不打游戏</div>
        <div style={{fontSize: 116, color: C.ink, lineHeight: 1.1, opacity: l2, transform: `translateY(${(1 - l2) * 20}px)`}}>
          却大量使用 <span style={{color: C.ai}}>GPU</span>
        </div>
        <div style={{fontSize: 150, color: C.game, lineHeight: 1.15, marginTop: 10, opacity: why, transform: `scale(${lerp(1.25, 1, why)})`}}>为什么？</div>
      </div>
    </AbsoluteFill>
  );
};
