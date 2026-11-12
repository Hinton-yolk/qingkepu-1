// note：角注。小字（28 px），深色衬底，贴着内容区下沿（最下面一条的下沿在 y = 1316）；同一时刻有多条时竖着排，先出现的在上。
// 一个镜头一个 NoteStack：按当前帧决定哪些角注在场，逐条淡入淡出。
// 叠多高由 lib/shotLayout 量（measureNote）：图表面板和标签据此往上让，角注自己不会压到字幕（它只往上长）。
import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { localSpan, measureNote, NOTE } from "../lib/shotLayout";
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
import { Overlay, Shot } from "../timeline";

const FADE = 6;

export const NoteStack: React.FC<{ shot: Shot; notes: Overlay[] }> = ({
  shot,
  notes,
}) => {
  const frame = useCurrentFrame(); // 镜头内帧号
  const visible = notes
    .map((n) => ({ n, ...localSpan(shot, n) }))
    .filter(({ from, to }) => frame >= from && frame < to);

  if (visible.length === 0) return null;

  return (
    <div
      style={{
        position: "absolute",
        left: SAFE.left,
        width: SAFE.width,
        bottom: `calc(100% - ${NOTE.bottom}px)`,
        display: "flex",
        flexDirection: "column",
        gap: NOTE.gap,
        fontFamily: FONT_FAMILY,
      }}
    >
      {visible.map(({ n, from, to }, i) => {
        const m = measureNote(n);
        return (
          <div
            key={i}
            style={{
              opacity: Math.min(
                interpolate(frame, [from, from + FADE], [0, 1], CLAMP),
                interpolate(frame, [to - FADE, to], [1, 0], CLAMP),
              ),
              fontSize: SIZE.note,
              lineHeight: `${NOTE.lineH}px`,
              color: rgba(C.cream, 0.96),
              textShadow: TEXT_SHADOW_SOFT,
              alignSelf: "flex-start",
              maxWidth: "100%",
              boxSizing: "border-box",
              backgroundColor: rgba(C.ink, BACKING.note),
              borderRadius: 6,
              borderLeft: `${NOTE.border}px solid ${rgba(C.cream, 0.6)}`,
              padding: `${NOTE.padY}px ${NOTE.padRight}px ${NOTE.padY}px ${NOTE.padLeft}px`,
              whiteSpace: m.natural ? "normal" : "nowrap",
            }}
          >
            {m.natural ? n.text : m.lines.map((l, j) => <div key={j}>{l}</div>)}
          </div>
        );
      })}
    </div>
  );
};
