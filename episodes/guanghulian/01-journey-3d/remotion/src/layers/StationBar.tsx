// 五站进度条：y = station_bar_y（抖音「推荐 / 关注」栏下方）。细线、低调；当前站高亮，station 为 null 的镜头都不高亮。
import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { STATION_SIGNAL } from "../shotConfig";
import {
  C,
  CLAMP,
  FONT_FAMILY,
  rgba,
  SAFE,
  SIZE,
  TEXT_SHADOW,
  W,
} from "../theme";
import { TL, toFrame } from "../timeline";

const signalColors = (stationId: string): [string, string] => {
  const kind = STATION_SIGNAL[stationId] ?? "electric";
  if (kind === "light") return [C.light, C.light];
  if (kind === "both") return [C.electric, C.light];
  return [C.electric, C.electric];
};

export const StationBar: React.FC = () => {
  const frame = useCurrentFrame();
  const n = TL.stations.length;
  const x0 = SAFE.left + 70;
  const x1 = SAFE.right - 70;
  const xs = TL.stations.map((_, i) =>
    n === 1 ? W / 2 : x0 + ((x1 - x0) * i) / (n - 1),
  );
  const lineY = SAFE.stationY + 30;

  // 当前镜头、当前站
  const shot = TL.shots.find(
    (s) => frame >= toFrame(s.start) && frame < toFrame(s.end),
  );
  const activeIdx = shot
    ? TL.stations.findIndex((s) => s.id === shot.station)
    : -1;

  // 每一站第一次点亮的帧（用来做 8 帧的过渡）
  const activation = TL.stations.map((st) => {
    const first = TL.shots.find((s) => s.station === st.id);
    return first ? toFrame(first.start) : Infinity;
  });
  // 走过的站：这一站之后已经有别的站点亮过
  const lastStarted = activation.reduce(
    (acc, a, i) => (frame >= a ? i : acc),
    -1,
  );

  return (
    <div style={{ position: "absolute", inset: 0, fontFamily: FONT_FAMILY }}>
      <svg
        width={W}
        height={SAFE.stationY + 80}
        style={{ position: "absolute", left: 0, top: 0 }}
      >
        <line
          x1={xs[0]}
          y1={lineY}
          x2={xs[n - 1]}
          y2={lineY}
          stroke={rgba(C.cream, 0.28)}
          strokeWidth={2}
        />
        {TL.stations.map((st, i) => {
          const isActive = i === activeIdx;
          const k = isActive
            ? interpolate(frame - activation[i], [0, 8], [0, 1], CLAMP)
            : 0;
          const [c1, c2] = signalColors(st.id);
          const passed = i <= lastStarted && !isActive;
          const r = 5 + 3 * k;
          return (
            <g key={st.id}>
              <circle
                cx={xs[i]}
                cy={lineY}
                r={r}
                fill={passed ? rgba(C.cream, 0.55) : C.ink}
                stroke={rgba(C.cream, isActive ? 0 : 0.5)}
                strokeWidth={2}
              />
              {isActive ? (
                <>
                  {/* 左半 / 右半各一种信号色：换乘站是金到青 */}
                  <path
                    d={`M${xs[i]} ${lineY - r} A${r} ${r} 0 0 0 ${xs[i]} ${lineY + r} Z`}
                    fill={c1}
                    opacity={k}
                  />
                  <path
                    d={`M${xs[i]} ${lineY - r} A${r} ${r} 0 0 1 ${xs[i]} ${lineY + r} Z`}
                    fill={c2}
                    opacity={k}
                  />
                </>
              ) : null}
            </g>
          );
        })}
      </svg>
      {TL.stations.map((st, i) => {
        const isActive = i === activeIdx;
        const k = isActive
          ? interpolate(frame - activation[i], [0, 8], [0, 1], CLAMP)
          : 0;
        return (
          <div
            key={st.id}
            style={{
              position: "absolute",
              left: xs[i] - 100,
              width: 200,
              top: SAFE.stationY - 26,
              textAlign: "center",
              fontSize: SIZE.station,
              lineHeight: "40px",
              fontWeight: isActive ? 700 : 400,
              color: rgba(C.cream, 0.5 + 0.5 * k),
              textShadow: TEXT_SHADOW,
              whiteSpace: "nowrap",
            }}
          >
            {st.name}
          </div>
        );
      })}
    </div>
  );
};
