// 字幕：narration 逐句。所有字幕用同一条衬底条：
//   位置  条的中心在 y = subtitle_y；一行或两行都以这条线为中心
//   宽度  条宽固定 = 内容区宽（左右各留 60 px），不随字数变；字在条内居中
//   衬底  深色，不透明度 BACKING.subtitle（0.72），亮画面上也读得清
// 一行放不下折两行（只在词之间断，优先在标点后）；出入各 3 帧淡变。
// 上一版衬底是「包着字」的：两行的句子折成两行差不多长的短行，框就比别的句子窄、比别的句子高，
// 两行一样长时看上去还像左对齐。现在条宽固定，就没有这个差别了。
import React from "react";
import { interpolate, Sequence, useCurrentFrame } from "remotion";
import { fitFontSize, splitTwoLines } from "../lib/text";
import {
  BACKING,
  C,
  CLAMP,
  FONT_FAMILY,
  rgba,
  SAFE,
  SIZE,
  TEXT_SHADOW_SOFT,
} from "../theme";
import { durFrames, Narration, TL, toFrame } from "../timeline";

const FADE = 3;
const PAD_X = 28;
const PAD_Y = 12;
const BAR_W = SAFE.width;
const MAX_TEXT_W = BAR_W - PAD_X * 2;

const Line: React.FC<{ n: Narration; duration: number }> = ({
  n,
  duration,
}) => {
  const frame = useCurrentFrame();
  const lines = splitTwoLines(n.text, SIZE.subtitle, MAX_TEXT_W, 700);
  // 折两行后还是太宽（极长的一句）就缩字号
  const fontSize = Math.min(
    ...lines.map((l) => fitFontSize(l, SIZE.subtitle, MAX_TEXT_W, 700)),
  );
  const lineH = Math.round(fontSize * 1.32);
  const boxH = lines.length * lineH + PAD_Y * 2;

  return (
    <div
      style={{
        position: "absolute",
        left: SAFE.left,
        width: BAR_W,
        top: SAFE.subtitleY - boxH / 2,
        height: boxH,
        boxSizing: "border-box",
        padding: `${PAD_Y}px ${PAD_X}px`,
        backgroundColor: rgba(C.ink, BACKING.subtitle),
        borderRadius: 12,
        fontFamily: FONT_FAMILY,
        fontSize,
        fontWeight: 700,
        lineHeight: `${lineH}px`,
        color: C.cream,
        textAlign: "center",
        textShadow: TEXT_SHADOW_SOFT,
        whiteSpace: "nowrap",
        opacity: Math.min(
          interpolate(frame, [0, FADE], [0, 1], CLAMP),
          interpolate(frame, [duration - FADE, duration], [1, 0], CLAMP),
        ),
      }}
    >
      {lines.map((l, i) => (
        <div key={i}>{l}</div>
      ))}
    </div>
  );
};

export const Subtitles: React.FC = () => {
  return (
    <>
      {TL.narration.map((n) => {
        const duration = durFrames(n.start, n.end - n.start);
        return (
          <Sequence
            key={n.id}
            name={`字幕 ${n.id}`}
            from={toFrame(n.start)}
            durationInFrames={duration}
            layout="none"
          >
            <Line n={n} duration={duration} />
          </Sequence>
        );
      })}
    </>
  );
};
