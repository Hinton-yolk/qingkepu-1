import {AbsoluteFill, OffthreadVideo, staticFile, useCurrentFrame} from 'remotion';
import plates from '../plates.json';
import {C, FONT} from './theme';

/** Blender 底片：有渲染好的 mp4 就放，没有就放一张明确标注的占位卡（不停工） */
export const Plate: React.FC<{name: 'DC' | 'MACRO' | 'CHIP'; startFrom?: number; style?: React.CSSProperties; rate?: number}> = ({
  name, startFrom = 0, style, rate = 1,
}) => {
  const f = useCurrentFrame();
  if ((plates as Record<string, boolean>)[name]) {
    return (
      <AbsoluteFill style={style}>
        <OffthreadVideo src={staticFile(`plates/${name}.mp4`)} startFrom={startFrom} playbackRate={rate} muted
          style={{width: '100%', height: '100%', objectFit: 'cover'}} />
      </AbsoluteFill>
    );
  }
  return (
    <AbsoluteFill style={{...style, background: `repeating-linear-gradient(45deg, #15171b 0 40px, #191b20 40px 80px)`}}>
      <div style={{position: 'absolute', top: 820, width: '100%', textAlign: 'center', color: C.sub, fontFamily: FONT.hei, fontSize: 40}}>
        占位 · Blender 镜头 {name} 渲染中<br />
        <span style={{fontSize: 28, color: C.dim}}>frame {f}</span>
      </div>
    </AbsoluteFill>
  );
};

/** 角落的小注：「示意」「简化」之类，行家看了不会误会 */
export const Note: React.FC<{children: React.ReactNode; opacity?: number; top?: number; left?: number; right?: number; align?: 'left' | 'right'}> = ({
  children, opacity = 1, top = 1490, left, right, align = 'left',
}) => (
  <div style={{position: 'absolute', top, left: left ?? (align === 'left' ? 64 : undefined), right: right ?? (align === 'right' ? 64 : undefined),
    fontFamily: FONT.hei, fontSize: 29, color: C.sub, opacity, letterSpacing: 1, textAlign: align}}>
    {children}
  </div>
);

/** 小标签：细线 + 文字 */
export const Tag: React.FC<{x: number; y: number; text: string; color?: string; opacity?: number; size?: number; anchor?: 'left' | 'center' | 'right'}> = ({
  x, y, text, color = C.ink, opacity = 1, size = 34, anchor = 'left',
}) => (
  <div style={{position: 'absolute', left: x, top: y, transform: `translate(${anchor === 'left' ? 0 : anchor === 'center' ? -50 : -100}%, -50%)`,
    fontFamily: FONT.hei, fontWeight: 700, fontSize: size, color, opacity, whiteSpace: 'nowrap',
    textShadow: '0 2px 8px rgba(0,0,0,0.85)'}}>
    {text}
  </div>
);

/** 段落角标：左上角小字，告诉观众现在在讲哪一边（游戏 / AI），也是系列识别 */
export const Kicker: React.FC<{text: string; color: string; opacity?: number}> = ({text, color, opacity = 1}) => (
  <div style={{position: 'absolute', left: 64, top: 205, display: 'flex', alignItems: 'center', gap: 16, opacity}}>
    <div style={{width: 14, height: 14, borderRadius: 7, background: color}} />
    <div style={{fontFamily: FONT.hei, fontWeight: 700, fontSize: 34, color, letterSpacing: 4}}>{text}</div>
  </div>
);

/** 2D 舞台的「镜头呼吸」：讲解停顿时不加新信息，但画面不死（工作室规则：最长静止 ≤ 0.6 秒）。
 *  慢推 + 很轻的摇摆，周期错开，看起来像手持稳定器上的镜头，不像动画抖动。 */
export const Drift: React.FC<{children: React.ReactNode; from: number; amp?: number; push?: number; origin?: string}> = ({children, from, amp = 1, push = 0.0025, origin = '50% 45%'}) => {
  const f = useCurrentFrame();
  const t = f / 30;
  const w = 1.25, ph = from * 0.37;
  // 匀速的慢圆周（速度永不为 0）+ 线性慢推：像漂浮的镜头，不像抖动
  const x = amp * 14 * Math.cos(t * w + ph);
  const y = amp * 11 * Math.sin(t * w + ph);
  const s = 1 + push * t;
  return <AbsoluteFill style={{transform: `translate(${x}px, ${y}px) scale(${s})`, transformOrigin: origin}}>{children}</AbsoluteFill>;
};
