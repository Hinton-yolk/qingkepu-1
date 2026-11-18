import {AbsoluteFill, Sequence, useCurrentFrame} from 'remotion';
import macro from '../anchors/MACRO.json';
import {C, FONT} from '../lib/theme';
import {cue, ease, easeIO, lerp, prog, sec} from '../lib/time';
import {Plate} from '../lib/ui';

// v03 A 段：一个焦点、一个问题。
// 0 帧：GPU 芯片微距（芯片被一圈光框住）+ 大字问题 →「却大量使用 GPU」切到一排排 GPU 服务器 →「为什么？」回到芯片，
// 芯片的方框在 B 段长成游戏画面（同一个矩形带过去）。这一段的旁白就是大字本身，不再出字幕（Captions.tsx 里跳过 A1、A2）。
export const T_MACRO = 0;
export const MACRO_BACK = 92;            // 回到芯片时从 MACRO 底片的第几帧开始（推得更近）

/** MACRO 底片某帧里大芯片的屏幕矩形 */
export const dieRect = (mf: number) => {
  const d = macro.frames[Math.max(0, Math.min(macro.frames.length - 1, mf))].die;
  const xs = d.map((p) => p[0] * 1080), ys = d.map((p) => p[1] * 1920);
  return {x: Math.min(...xs), y: Math.min(...ys), w: Math.max(...xs) - Math.min(...xs), h: Math.max(...ys) - Math.min(...ys), poly: d.map((p) => [p[0] * 1080, p[1] * 1920])};
};

export const SeqA: React.FC<{from: number}> = ({from}) => {
  const f = useCurrentFrame() + from;
  const a1 = cue('A1'), a2 = cue('A2');
  const T_DC = a1 + sec(1.25);                 // 「却大量使用 GPU」
  const T_BACK = a2 - 3;                       // 「为什么？」回到芯片
  const t = f / 30;
  const inDC = f >= T_DC && f < T_BACK;
  // 芯片外框（第一段、回来以后都有）
  const mf = f < T_DC ? f : MACRO_BACK + (f - T_BACK);
  const r = dieRect(mf);
  const ring = f < T_DC ? prog(f, 8, 12) : prog(f, T_BACK, 8);
  const poly = r.poly.map((p) => p.join(',')).join(' ');
  // 大字：「AI 不打游戏」第 0 帧就在；「却大量使用 GPU」跟着旁白出；「为什么？」最后
  const l2 = prog(f, a1 + sec(0.95), 8);
  const why = prog(f, a2, 8);
  const whip = prog(f, T_DC - 4, 6, easeIO), whipBack = prog(f, T_BACK - 4, 6, easeIO);

  return (
    <AbsoluteFill style={{background: C.bg}}>
      {/* 芯片微距：0 – T_DC */}
      {f < T_DC + 4 && (
        <AbsoluteFill style={{transform: `translateX(${-whip * 1200}px) scale(${1 + t * 0.01})`, filter: whip > 0.02 ? `blur(${whip * 20}px)` : undefined}}>
          <Plate name="MACRO" />
        </AbsoluteFill>
      )}
      {/* 机房：T_DC – T_BACK */}
      {f >= T_DC - 4 && f < T_BACK + 4 && (
        <Sequence from={T_DC - 4 - from} layout="none">
          <AbsoluteFill style={{transform: `translateX(${(1 - prog(f, T_DC - 4, 7, ease)) * 1200 - whipBack * 1200}px)`,
            filter: (f < T_DC + 3 || whipBack > 0.02) ? `blur(${Math.max(1 - prog(f, T_DC - 4, 7), whipBack) * 20}px)` : undefined}}>
            <Plate name="DC" rate={0.9} startFrom={20} />
          </AbsoluteFill>
        </Sequence>
      )}
      {/* 回到芯片（推得更近的那几帧） */}
      {f >= T_BACK - 4 && (
        <Sequence from={T_BACK - 4 - from} layout="none">
          <AbsoluteFill style={{transform: `translateX(${(1 - prog(f, T_BACK - 4, 7, ease)) * 1200}px)`}}>
            <Plate name="MACRO" startFrom={MACRO_BACK} />
          </AbsoluteFill>
        </Sequence>
      )}
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(8,9,11,0.82) 0%, rgba(8,9,11,0.25) 34%, rgba(8,9,11,0) 55%, rgba(8,9,11,0.45) 100%)'}} />
      {!inDC && (
        <svg width={1080} height={1920} style={{position: 'absolute', left: 0, top: 0}}>
          <polygon points={poly} fill="none" stroke={C.ai} strokeWidth={6} strokeLinejoin="round" opacity={ring * (0.75 + 0.25 * Math.sin(t * 4))} />
        </svg>
      )}
      {/* 一个问题 */}
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
