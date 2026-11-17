import {AbsoluteFill, interpolate, Sequence, useCurrentFrame} from 'remotion';
import macro from '../anchors/MACRO.json';
import {C, FONT} from '../lib/theme';
import {cue, ease, easeIO, lerp, prog, sec} from '../lib/time';
import {Note, Plate, Tag} from '../lib/ui';

// v02 A 段（钩子）：第 0 帧就是 GPU 模组微距 + 大字问题 + 一张对话卡（问题已经发出、回答正在流出）
// → 「背后可能有 GPU 在帮它计算」：一条光从对话卡落到大芯片上 → 「奇怪了」甩到机房 → 「为什么还要用显卡？」
export const QUESTION = '黑洞是什么？';
const ANSWER = '黑洞是时空中引力极强的区域，强到连光都无法逃脱……';
export const T_MACRO = 0;           // B 段的开场用不到它了，保留导出给旧代码

const BigQ: React.FC<{o: number; y?: number; scale?: number}> = ({o, y = 150, scale = 1}) => (
  <div style={{position: 'absolute', left: 0, right: 0, top: y, textAlign: 'center', opacity: o, fontFamily: FONT.title, color: C.ink,
    textShadow: '0 4px 28px rgba(0,0,0,0.9)', transform: `scale(${scale})`, transformOrigin: '50% 0%'}}>
    <div style={{fontSize: 112, lineHeight: 1.1}}>AI 又不打游戏</div>
    <div style={{fontSize: 112, lineHeight: 1.1, color: C.game}}>为什么还要用显卡？</div>
  </div>
);

export const SeqA: React.FC<{from: number}> = ({from}) => {
  const f = useCurrentFrame() + from;
  const T_DC = cue('A2') - 4;                      // 「奇怪了」：甩到机房
  const t = f / 30;
  // ---------- 0 – T_DC：GPU 微距 + 对话卡 ----------
  const answered = Math.max(0, Math.floor((f - 6) * 0.9));
  const cardIn = prog(f, 0, 8);
  const link = prog(f, cue('A1') + sec(1.3), 14, easeIO);       // 「背后可能有 GPU」：光落到芯片
  const ring = prog(f, cue('A1') + sec(1.8), 10);
  const mf = Math.min(macro.frames.length - 1, f);
  const die = macro.frames[mf].die;
  const cx = ((die[0][0] + die[1][0] + die[2][0] + die[3][0]) / 4) * 1080;
  const cy = ((die[0][1] + die[1][1] + die[2][1] + die[3][1]) / 4) * 1920;
  const CARD = {x: 90, y: 560, w: 900, h: 330};
  const startX = CARD.x + CARD.w / 2, startY = CARD.y + CARD.h;
  const whip = prog(f, T_DC - 6, 8, easeIO);
  const macroLayer = (
    <AbsoluteFill style={{transform: `translateY(${-whip * 2200}px)`, filter: whip > 0.02 ? `blur(${whip * 24}px)` : undefined}}>
      <Plate name="MACRO" />
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(8,9,11,0.82) 0%, rgba(8,9,11,0.35) 34%, rgba(8,9,11,0.1) 60%, rgba(8,9,11,0.55) 100%)'}} />
      {/* 对话卡：问题已发出，回答正在流出（不等打字） */}
      <div style={{position: 'absolute', left: CARD.x, top: CARD.y, width: CARD.w, height: CARD.h, borderRadius: 34, opacity: cardIn,
        background: 'rgba(18,20,24,0.78)', border: '2px solid rgba(255,255,255,0.12)', boxShadow: '0 30px 80px rgba(0,0,0,0.6)',
        transform: `translateY(${(1 - cardIn) * 30 + 6 * Math.sin(t * 1.3)}px)`, fontFamily: FONT.hei}}>
        <div style={{position: 'absolute', left: 34, top: 26, fontSize: 30, color: C.sub, fontWeight: 700}}>AI 助手</div>
        <div style={{position: 'absolute', right: 34, top: 24, background: '#2B3038', color: C.ink, fontSize: 46, padding: '14px 28px', borderRadius: '30px 30px 8px 30px'}}>{QUESTION}</div>
        <div style={{position: 'absolute', left: 34, right: 40, top: 128, color: '#DCD8D0', fontSize: 42, lineHeight: 1.55}}>
          {ANSWER.slice(0, answered)}
          <span style={{display: 'inline-block', width: 18, height: 38, marginLeft: 4, verticalAlign: -6, background: C.ink, opacity: Math.floor(f / 8) % 2 ? 0.2 : 0.9}} />
        </div>
      </div>
      {/* 对话卡 → GPU 芯片：一条光 */}
      <svg width={1080} height={1920} style={{position: 'absolute', left: 0, top: 0}}>
        <line x1={startX} y1={startY} x2={lerp(startX, cx, link)} y2={lerp(startY, cy, link)} stroke={C.ai} strokeWidth={5} strokeLinecap="round" opacity={0.9 * link} />
        <circle cx={lerp(startX, cx, link)} cy={lerp(startY, cy, link)} r={12} fill={C.ai} opacity={link * (1 - ring * 0.6)} />
        <circle cx={cx} cy={cy} r={40 + 30 * ring} fill="none" stroke={C.ai} strokeWidth={5} opacity={ring * 0.9} />
      </svg>
      <Tag x={cx} y={cy + 110} text="GPU" anchor="center" opacity={ring} size={56} color={C.ai} />
    </AbsoluteFill>
  );

  // ---------- T_DC – B：机房（一排排 GPU 服务器） ----------
  const dcIn = prog(f, T_DC - 2, 9, ease);
  const dcLen = (from + 0) * 0 + 400;
  const dcRate = 0.82;                              // 底片只有约 4 秒能用，略放慢
  const dc = (
    <Sequence from={T_DC - 2 - from} durationInFrames={dcLen} layout="none">
      <AbsoluteFill style={{transform: `translateY(${(1 - dcIn) * 1500}px)`, filter: dcIn < 0.98 ? `blur(${(1 - dcIn) * 22}px)` : undefined}}>
        <Plate name="DC" rate={dcRate} />
        <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(8,9,11,0.75) 0%, rgba(8,9,11,0.1) 36%, rgba(8,9,11,0) 70%, rgba(8,9,11,0.55) 100%)'}} />
        <Tag x={540} y={1280} text="数据中心里，一排排 GPU 服务器" anchor="center" size={44} opacity={prog(f, T_DC + sec(0.6), 10)} />
        <Note top={1490} opacity={prog(f, T_DC + sec(0.6), 10) * 0.85}>示意场景；通用 AI 加速器模组，非特定型号</Note>
      </AbsoluteFill>
    </Sequence>
  );
  // 大字问题：第 0 帧就在；说到 A3 时再强调一次
  const q3 = prog(f, cue('A3'), 10);
  const qScale = 1 + 0.06 * q3 * (1 - prog(f, cue('A3') + sec(0.6), 12));
  return (
    <AbsoluteFill style={{background: C.bg}}>
      {f < T_DC + 8 && macroLayer}
      {f >= T_DC - 2 && dc}
      <BigQ o={1 - prog(f, cue('B1') - 8, 8)} y={interpolate(f, [0, 90], [150, 140], {extrapolateRight: 'clamp'})} scale={qScale} />
    </AbsoluteFill>
  );
};
