import {AbsoluteFill, interpolate, Sequence, useCurrentFrame} from 'remotion';
import macro from '../anchors/MACRO.json';
import {C, FONT} from '../lib/theme';
import {cue, ease, easeIO, prog, sec} from '../lib/time';
import {Note, Plate, Tag} from '../lib/ui';

// A 段（钩子）：手机上问 AI「黑洞是什么？」→ 回答一个字一个字冒出来 → 甩镜到数据中心冷通道 → 推到 GPU 模组微距
export const QUESTION = '黑洞是什么？';
const ANSWER = '黑洞是时空中引力极强的区域，强到连光都无法逃脱。它通常在大质量恒星耗尽燃料、核心坍缩之后形成。';
export const T_DC = sec(5.55);      // 甩到数据中心
export const T_MACRO = sec(8.95);   // 切到模组微距
const PH = {x: 120, y: 560, w: 840, h: 1290, r: 64}; // 手机外框（屏幕坐标）

/** 手机里的对话界面（通用聊天应用，不仿任何品牌） */
export const ChatScreen: React.FC<{f: number; typed: number; sent: number; answered: number}> = ({f, typed, sent, answered}) => {
  const q = QUESTION.slice(0, typed);
  const caret = Math.floor(f / 8) % 2 === 0;
  const sentK = interpolate(sent, [0, 1], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const ans = ANSWER.slice(0, answered);
  return (
    <div style={{position: 'absolute', inset: 0, background: '#0F1114', borderRadius: PH.r - 14, overflow: 'hidden', fontFamily: FONT.hei}}>
      {/* 顶栏 */}
      <div style={{position: 'absolute', top: 0, left: 0, right: 0, height: 150, borderBottom: `1px solid ${C.line}`, display: 'flex', alignItems: 'flex-end', padding: '0 0 26px 48px', gap: 18}}>
        <div style={{width: 46, height: 46, borderRadius: 23, background: 'linear-gradient(135deg,#3a3f48,#20242a)', border: `2px solid ${C.line}`}} />
        <div style={{color: C.ink, fontSize: 38, fontWeight: 700}}>AI 助手</div>
      </div>
      {/* 用户的问题气泡 */}
      <div style={{position: 'absolute', right: 44, top: interpolate(sentK, [0, 1], [900, 200]), opacity: sentK,
        background: '#2B3038', color: C.ink, fontSize: 46, padding: '22px 34px', borderRadius: '34px 34px 8px 34px'}}>
        {QUESTION}
      </div>
      {/* 回答：逐字流出 */}
      {answered > 0 && (
        <div style={{position: 'absolute', left: 48, right: 70, top: 330, color: '#DCD8D0', fontSize: 44, lineHeight: 1.62, letterSpacing: 0.5}}>
          {ans}
          <span style={{display: 'inline-block', width: 20, height: 40, marginLeft: 6, verticalAlign: -6, background: C.ink, opacity: answered < ANSWER.length ? 0.9 : caret ? 0.8 : 0}} />
        </div>
      )}
      {/* 输入框 */}
      <div style={{position: 'absolute', left: 36, right: 36, bottom: 120, height: 104, borderRadius: 52, background: '#1C1F25', border: `2px solid ${C.line}`,
        display: 'flex', alignItems: 'center', padding: '0 36px', color: C.ink, fontSize: 44}}>
        <span style={{opacity: sent > 0.2 ? 0 : 1}}>{q}</span>
        {sent < 0.2 && <span style={{display: 'inline-block', width: 3, height: 46, marginLeft: 4, background: C.ink, opacity: caret ? 1 : 0}} />}
        {typed === 0 && <span style={{color: C.dim}}>问点什么</span>}
        <div style={{position: 'absolute', right: 14, width: 76, height: 76, borderRadius: 38, background: typed >= QUESTION.length && sent < 0.2 ? C.ink : '#2A2E35',
          display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#111', fontSize: 40, fontWeight: 700}}>↑</div>
      </div>
    </div>
  );
};

/** 大字问题（第一帧就在） */
const BigQ: React.FC<{l1: string; l2: string; o: number; y?: number; accent?: string}> = ({l1, l2, o, y = 190, accent = C.game}) => (
  <div style={{position: 'absolute', left: 0, right: 0, top: y, textAlign: 'center', opacity: o, fontFamily: FONT.title, color: C.ink,
    textShadow: '0 4px 24px rgba(0,0,0,0.8)'}}>
    <div style={{fontSize: 104, lineHeight: 1.12}}>{l1}</div>
    <div style={{fontSize: 104, lineHeight: 1.12, color: accent}}>{l2}</div>
  </div>
);

export const SeqA: React.FC<{from: number}> = ({from}) => {
  const f = useCurrentFrame() + from; // 全片帧号
  // ---------- 手机段 0–4.75 s ----------
  const typed = Math.min(QUESTION.length, 1 + Math.floor(Math.max(0, f - 6) / 6));
  const sent = prog(f, sec(2.3), 9);
  const ansStart = sec(2.85);
  const answered = Math.max(0, Math.floor((f - ansStart) * 1.0));
  const push = prog(f, sec(2.6), sec(2.9), easeIO);                      // 慢慢推近回答
  const pre = f / 30;                                                     // 开头就有的很慢的推近和漂移，画面一开始就在动
  const whip = prog(f, T_DC - 7, 9, easeIO);                             // 甩镜：手机往上甩出
  const titleO = 1 - prog(f, cue('A2') + sec(0.9), 10);
  // 灯光：左上一盏暖色台灯，手机屏幕的冷光打在桌面上
  const phone = (
    <AbsoluteFill style={{background: 'radial-gradient(120% 70% at 18% 8%, #2a241c 0%, #121214 46%, #0a0a0c 100%)'}}>
      <div style={{position: 'absolute', inset: 0, transform: `translateY(${-whip * 2300}px)`, filter: whip > 0.02 ? `blur(${whip * 26}px)` : undefined}}>
        <div style={{position: 'absolute', inset: 0, transform: `scale(${1 + push * 0.16 + pre * 0.006}) translate(${push * 30 + 18 * Math.cos(pre * 1.4)}px, ${-push * 120 + 14 * Math.sin(pre * 1.4)}px)`, transformOrigin: '50% 40%'}}>
          {/* 桌面反光 */}
          <div style={{position: 'absolute', left: PH.x - 60, top: PH.y + PH.h - 80, width: PH.w + 120, height: 260, borderRadius: '50%',
            background: 'radial-gradient(closest-side, rgba(120,140,170,0.16), transparent)'}} />
          {/* 机身 */}
          <div style={{position: 'absolute', left: PH.x, top: PH.y, width: PH.w, height: PH.h, borderRadius: PH.r,
            background: 'linear-gradient(160deg,#3b3e44 0%,#16171a 38%,#0d0e10 100%)', boxShadow: '0 40px 120px rgba(0,0,0,0.75), inset 0 0 0 2px #4a4d53'}}>
            <div style={{position: 'absolute', inset: 14}}>
              <ChatScreen f={f} typed={typed} sent={sent} answered={answered} />
            </div>
            {/* 屏幕玻璃的一道斜反光 */}
            <div style={{position: 'absolute', inset: 14, borderRadius: PH.r - 14, pointerEvents: 'none',
              background: 'linear-gradient(115deg, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0.0) 28%, rgba(255,255,255,0) 100%)'}} />
          </div>
        </div>
      </div>
      <div style={{position: 'absolute', inset: 0, transform: `translate(${7 * Math.sin(pre * 1.1)}px, ${6 * Math.cos(pre * 1.1)}px) scale(${1 + pre * 0.008})`}}>
        <BigQ l1="AI 又不打游戏" l2="为什么还要用显卡？" o={titleO} />
      </div>
    </AbsoluteFill>
  );

  // ---------- 数据中心 4.75–8.95 s ----------
  const dcIn = prog(f, T_DC - 2, 10, ease);
  const dcLabel = prog(f, cue('A4') + sec(2.3), 12);
  const dc = (
    <Sequence from={T_DC - from - 2} durationInFrames={T_MACRO - T_DC + 14} layout="none">
      <AbsoluteFill style={{transform: `translateY(${(1 - dcIn) * 1400}px)`, filter: dcIn < 0.98 ? `blur(${(1 - dcIn) * 22}px)` : undefined}}>
        <Plate name="DC" />
        <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(8,9,11,0.55) 0%, rgba(8,9,11,0) 22%, rgba(8,9,11,0) 70%, rgba(8,9,11,0.6) 100%)'}} />
        <Tag x={64} y={1290} text="数据中心 · GPU 服务器" opacity={dcLabel} size={40} />
        <div style={{position: 'absolute', left: 64, top: 1322, width: 420 * dcLabel, height: 3, background: C.ink, opacity: 0.7 * dcLabel}} />
        <Note top={1490} opacity={dcLabel * 0.85}>示意场景</Note>
      </AbsoluteFill>
    </Sequence>
  );

  // ---------- GPU 模组微距 8.95 s – B 段 ----------
  const mIn = prog(f, T_MACRO, 9, ease);
  const mf = Math.max(0, Math.min(macro.frames.length - 1, f - T_MACRO));
  const die = macro.frames[mf].die;
  const cx = ((die[0][0] + die[1][0] + die[2][0] + die[3][0]) / 4) * 1080;
  const cy = ((die[0][1] + die[1][1] + die[2][1] + die[3][1]) / 4) * 1920;
  const tagO = prog(f, cue('A5') + sec(0.5), 10);
  const q2 = prog(f, cue('A5') + sec(1.4), 12);
  const macroLayer = (
    <Sequence from={T_MACRO - from} layout="none">
      <AbsoluteFill style={{opacity: mIn, transform: `scale(${1.08 - 0.08 * mIn})`}}>
        <Plate name="MACRO" />
        <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(8,9,11,0.7) 0%, rgba(8,9,11,0) 30%, rgba(8,9,11,0) 72%, rgba(8,9,11,0.55) 100%)'}} />
        {/* 指向大芯片的标签：跟着 Blender 相机投影走 */}
        <div style={{position: 'absolute', left: cx, top: cy, width: 16, height: 16, marginLeft: -8, marginTop: -8, borderRadius: 8, border: `3px solid ${C.ink}`, opacity: tagO}} />
        <div style={{position: 'absolute', left: cx + 8, top: cy - 8, width: 140 * tagO, height: 3, background: C.ink, transform: 'rotate(-35deg)', transformOrigin: '0 50%', opacity: tagO}} />
        <Tag x={cx + 120} y={cy - 100} text="GPU 芯片" opacity={tagO} size={44} />
        <BigQ l1="画游戏的芯片" l2="怎么成了 AI 的主力？" o={q2} y={180} accent={C.ai} />
        <Note top={1490} opacity={tagO * 0.85}>示意：通用 AI 加速器模组，非特定型号</Note>
      </AbsoluteFill>
    </Sequence>
  );

  return (
    <AbsoluteFill>
      {f < T_DC + 10 && phone}
      {f >= T_DC - 2 && f < T_MACRO + 14 && dc}
      {f >= T_MACRO && macroLayer}
    </AbsoluteFill>
  );
};
