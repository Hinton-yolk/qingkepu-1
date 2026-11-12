// 字幕：narration 逐句，中心在 y = subtitle_y。深色半透明条 + 奶油色字；一行放不下自动折两行；出入各 3 帧淡变。
import React from "react";
import { interpolate, Sequence, useCurrentFrame } from "remotion";
import { fitFontSize, splitTwoLines } from "../lib/text";
import { C, CLAMP, FONT_FAMILY, rgba, SAFE, SIZE, W } from "../theme";
import { durFrames, Narration, TL, toFrame } from "../timeline";

const FADE = 3;
const PAD_X = 26;
const MAX_TEXT_W = SAFE.width - PAD_X * 2;

const Line: React.FC<{ n: Narration; duration: number }> = ({ n, duration }) => {
  const frame = useCurrentFrame();
  const lines = splitTwoLines(n.text, SIZE.subtitle, MAX_TEXT_W, 700);
  // 折两行后还是太宽（极长的一句）就缩字号
  const fontSize = Math.min(
    ...lines.map((l) => fitFontSize(l, SIZE.subtitle, MAX_TEXT_W, 700)),
  );
  const lineH = Math.round(fontSize * 1.32);
  const boxH = lines.length * lineH + 24;

  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        width: W,
        top: SAFE.subtitleY - boxH / 2,
        display: "flex",
        justifyContent: "center",
        opacity: Math.min(
          interpolate(frame, [0, FADE], [0, 1], CLAMP),
          interpolate(frame, [duration - FADE, duration], [1, 0], CLAMP),
        ),
      }}
    >
      <div
        style={{
          backgroundColor: rgba(C.ink, 0.66),
          borderRadius: 10,
          padding: `12px ${PAD_X}px`,
          fontFamily: FONT_FAMILY,
          fontSize,
          fontWeight: 700,
          lineHeight: `${lineH}px`,
          color: C.cream,
          textAlign: "center",
          whiteSpace: "nowrap",
        }}
      >
        {lines.map((l, i) => (
          <div key={i}>{l}</div>
        ))}
      </div>
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
