// end_card：片尾卡，全屏。第一行是一句话结论，中间是五站小路线图，最后一行是下一篇预告。
// 文案的两行来自标注的 text（用换行分开）；路线图的站名来自 stations。
import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { fitFontSize } from "../lib/text";
import { STATION_SIGNAL } from "../shotConfig";
import { C, CLAMP, FONT_FAMILY, rgba, SAFE, W } from "../theme";
import { Overlay, TL } from "../timeline";

/** 结论句里的「电」「光」两个字按系列的颜色语义上色：金 = 电，青 = 光 */
const Colored: React.FC<{ text: string }> = ({ text }) => (
  <>
    {Array.from(text).map((ch, i) =>
      ch === "电" ? (
        <span key={i} style={{ color: C.electric }}>
          {ch}
        </span>
      ) : ch === "光" ? (
        <span key={i} style={{ color: C.light }}>
          {ch}
        </span>
      ) : (
        <React.Fragment key={i}>{ch}</React.Fragment>
      ),
    )}
  </>
);

export const EndCard: React.FC<{ overlay: Overlay; duration: number }> = ({
  overlay,
  duration,
}) => {
  const frame = useCurrentFrame();
  const [line1, ...rest] = overlay.text.split("\n");
  const line2 = rest.join(" ");
  const n = TL.stations.length;

  // 路线图：站与站之间的线，光的路段是青色，其余金色
  const mapY = 930;
  const x0 = SAFE.left + 90;
  const x1 = SAFE.right - 90;
  const xs = TL.stations.map((_, i) =>
    n === 1 ? W / 2 : x0 + ((x1 - x0) * i) / (n - 1),
  );
  const stub = 60;
  const kind = (i: number) => STATION_SIGNAL[TL.stations[i].id] ?? "electric";
  // 第 i 段（站 i → 站 i+1）的颜色：出发站是「光」或「换乘」之后，下一段是光
  const segColor = (i: number) => {
    const k = kind(i);
    const next = i + 1 < n ? kind(i + 1) : "electric";
    if (k === "light") return C.light;
    if (k === "both") return next === "electric" ? C.electric : C.light;
    return C.electric;
  };
  const total = xs[n - 1] + stub - (xs[0] - stub);
  const draw = interpolate(frame, [10, 52], [0, 1], {
    ...CLAMP,
    easing: Easing.inOut(Easing.cubic),
  });
  const head = xs[0] - stub + total * draw;

  const f1 = fitFontSize(line1, 68, SAFE.width, 700);
  const f2 = fitFontSize(line2, 40, SAFE.width, 400);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: C.ink,
        fontFamily: FONT_FAMILY,
        color: C.cream,
        opacity: interpolate(frame, [0, 8], [0, 1], CLAMP),
      }}
    >
      <div
        style={{
          position: "absolute",
          left: SAFE.left,
          width: SAFE.width,
          top: 610,
          textAlign: "center",
          fontSize: f1,
          fontWeight: 700,
          lineHeight: 1.3,
          whiteSpace: "nowrap",
          opacity: interpolate(frame, [4, 14], [0, 1], CLAMP),
          translate: `0px ${interpolate(frame, [4, 14], [14, 0], { ...CLAMP, easing: Easing.out(Easing.cubic) })}px`,
        }}
      >
        <Colored text={line1} />
      </div>

      <svg
        width={W}
        height={200}
        style={{ position: "absolute", left: 0, top: mapY - 100 }}
      >
        <defs>
          <clipPath id="endcard-draw">
            <rect x={0} y={0} width={head} height={200} />
          </clipPath>
        </defs>
        <g clipPath="url(#endcard-draw)">
          <line
            x1={xs[0] - stub}
            y1={100}
            x2={xs[0]}
            y2={100}
            stroke={C.electric}
            strokeWidth={6}
            strokeLinecap="round"
          />
          {xs.slice(0, -1).map((x, i) => (
            <line
              key={i}
              x1={x}
              y1={100}
              x2={xs[i + 1]}
              y2={100}
              stroke={segColor(i)}
              strokeWidth={6}
            />
          ))}
          <line
            x1={xs[n - 1]}
            y1={100}
            x2={xs[n - 1] + stub}
            y2={100}
            stroke={C.electric}
            strokeWidth={6}
            strokeLinecap="round"
          />
        </g>
        {xs.map((x, i) => {
          const k = interpolate(head, [x - 10, x + 10], [0, 1], CLAMP);
          return (
            <circle
              key={i}
              cx={x}
              cy={100}
              r={6 + 6 * k}
              fill={C.ink}
              stroke={rgba(C.cream, 0.3 + 0.7 * k)}
              strokeWidth={3}
            />
          );
        })}
      </svg>
      {TL.stations.map((st, i) => (
        <div
          key={st.id}
          style={{
            position: "absolute",
            left: xs[i] - 110,
            width: 220,
            top: mapY + 28,
            textAlign: "center",
            fontSize: 32,
            lineHeight: "44px",
            whiteSpace: "nowrap",
            opacity: interpolate(
              head,
              [xs[i] - 10, xs[i] + 10],
              [0.3, 1],
              CLAMP,
            ),
          }}
        >
          {st.name}
        </div>
      ))}

      <div
        style={{
          position: "absolute",
          left: SAFE.left,
          width: SAFE.width,
          top: 1130,
          textAlign: "center",
          fontSize: f2,
          lineHeight: 1.4,
          color: rgba(C.cream, 0.85),
          whiteSpace: "nowrap",
          opacity: interpolate(
            frame,
            [Math.min(48, duration - 20), Math.min(60, duration - 8)],
            [0, 1],
            CLAMP,
          ),
        }}
      >
        {line2}
      </div>
    </AbsoluteFill>
  );
};
