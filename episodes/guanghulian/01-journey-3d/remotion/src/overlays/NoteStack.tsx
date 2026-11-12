// note：角注。小字，贴着内容区下沿（最后一行落在 y ≈ 1290–1316）；同一时刻有多条时竖着排。
// 一个镜头一个 NoteStack：按当前帧决定哪些角注在场，逐条淡入淡出。
import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { splitTwoLines, textWidth } from "../lib/text";
import { C, CLAMP, FONT_FAMILY, rgba, SAFE, SIZE, TEXT_SHADOW } from "../theme";
import { Overlay, Shot, toFrame } from "../timeline";

const FADE = 6;

export const NoteStack: React.FC<{ shot: Shot; notes: Overlay[] }> = ({
  shot,
  notes,
}) => {
  const frame = useCurrentFrame(); // 镜头内帧号
  const shotStart = toFrame(shot.start);

  const visible = notes
    .map((n) => {
      const from = toFrame(n.t) - shotStart;
      const to = toFrame(n.t + n.dur) - shotStart;
      const k = Math.min(
        interpolate(frame, [from, from + FADE], [0, 1], CLAMP),
        interpolate(frame, [to - FADE, to], [1, 0], CLAMP),
      );
      return { n, k, on: frame >= from && frame < to };
    })
    .filter((v) => v.on);

  if (visible.length === 0) return null;

  return (
    <div
      style={{
        position: "absolute",
        left: SAFE.left,
        width: SAFE.width,
        bottom: `calc(100% - ${SAFE.bottom - 4}px)`,
        display: "flex",
        flexDirection: "column",
        gap: 6,
        fontFamily: FONT_FAMILY,
      }}
    >
      {visible.map(({ n, k }, i) => {
        // 一行放不下时在标点后面折成两行（不把词拆开）；两行也放不下的极长角注才交给浏览器自己折
        const maxW = SAFE.width - 32;
        const lines = splitTwoLines(n.text, SIZE.note, maxW);
        const natural = lines.some((l) => textWidth(l, SIZE.note) > maxW);
        return (
          <div
            key={i}
            style={{
              opacity: k,
              fontSize: SIZE.note,
              lineHeight: "36px",
              color: rgba(C.cream, 0.82),
              textShadow: TEXT_SHADOW,
              // 很淡的深色衬底：压在亮画面上也读得清
              alignSelf: "flex-start",
              maxWidth: "100%",
              boxSizing: "border-box",
              backgroundColor: rgba(C.ink, 0.5),
              borderRadius: 4,
              borderLeft: `3px solid ${rgba(C.cream, 0.45)}`,
              padding: "0 12px 0 14px",
              whiteSpace: natural ? "normal" : "nowrap",
            }}
          >
            {natural ? n.text : lines.map((l, j) => <div key={j}>{l}</div>)}
          </div>
        );
      })}
    </div>
  );
};
