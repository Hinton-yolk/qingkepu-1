// 五站进度条：一条半透明深色衬底条，中心在 y ≈ station_bar_y（抖音「推荐 / 关注」栏下方），不进内容区。
//   站名 36 px（540 宽的预演里也读得出）。当前站：站名垫一块信号色的实心底、字变深色加粗，下面的圆点放大；
//   走过的站：字和圆点是实的奶油色；还没到的站：字淡、圆点空心。station 为 null 的镜头没有当前站。
//   信号色：电的站金色，光的站青色，换乘和抵达是金到青（shotConfig.STATION_SIGNAL）。
import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { STATION_SIGNAL } from "../shotConfig";
import {
  BACKING,
  C,
  CLAMP,
  FONT_FAMILY,
  rgba,
  SAFE,
  SIZE,
  TEXT_SHADOW_SOFT,
  W,
} from "../theme";
import { TL, toFrame } from "../timeline";

const signalColors = (stationId: string): [string, string] => {
  const kind = STATION_SIGNAL[stationId] ?? "electric";
  if (kind === "light") return [C.light, C.light];
  if (kind === "both") return [C.electric, C.light];
  return [C.electric, C.electric];
};

// 衬底条：y = stationY − 46 … stationY + 50
const STRIP_TOP = SAFE.stationY - 46;
const STRIP_H = 96;
const NAME_CY = SAFE.stationY - 13; // 站名一行的中线
const NAME_H = 50;
const LINE_Y = SAFE.stationY + 31; // 圆点和连线
const PILL_PAD = 18;

export const StationBar: React.FC = () => {
  const frame = useCurrentFrame();
  const n = TL.stations.length;
  const x0 = SAFE.left + 96;
  const x1 = SAFE.right - 96;
  const xs = TL.stations.map((_, i) =>
    n === 1 ? W / 2 : x0 + ((x1 - x0) * i) / (n - 1),
  );

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
  // 走到第几站了：最后一个已经点亮过的站
  const lastStarted = activation.reduce(
    (acc, a, i) => (frame >= a ? i : acc),
    -1,
  );

  return (
    <div style={{ position: "absolute", inset: 0, fontFamily: FONT_FAMILY }}>
      <div
        style={{
          position: "absolute",
          left: SAFE.left - 20,
          width: SAFE.width + 40,
          top: STRIP_TOP,
          height: STRIP_H,
          borderRadius: 18,
          backgroundColor: rgba(C.ink, BACKING.station),
        }}
      />
      <svg
        width={W}
        height={STRIP_TOP + STRIP_H}
        style={{ position: "absolute", left: 0, top: 0 }}
      >
        <line
          x1={xs[0]}
          y1={LINE_Y}
          x2={xs[n - 1]}
          y2={LINE_Y}
          stroke={rgba(C.cream, 0.4)}
          strokeWidth={3}
        />
        {/* 已经走过的那一截 */}
        {lastStarted > 0 ? (
          <line
            x1={xs[0]}
            y1={LINE_Y}
            x2={xs[lastStarted]}
            y2={LINE_Y}
            stroke={rgba(C.cream, 0.85)}
            strokeWidth={3}
          />
        ) : null}
        {TL.stations.map((st, i) => {
          const isActive = i === activeIdx;
          const k = isActive
            ? interpolate(frame - activation[i], [0, 8], [0, 1], CLAMP)
            : 0;
          const [c1, c2] = signalColors(st.id);
          const passed = i <= lastStarted && !isActive;
          const r = 6 + 5 * k;
          return (
            <g key={st.id}>
              <circle
                cx={xs[i]}
                cy={LINE_Y}
                r={r}
                fill={passed ? C.cream : C.ink}
                stroke={isActive ? C.ink : rgba(C.cream, passed ? 1 : 0.75)}
                strokeWidth={isActive ? 3 : 2.5}
              />
              {isActive ? (
                <>
                  {/* 左半 / 右半各一种信号色：换乘站是金到青 */}
                  <path
                    d={`M${xs[i]} ${LINE_Y - r} A${r} ${r} 0 0 0 ${xs[i]} ${LINE_Y + r} Z`}
                    fill={c1}
                    opacity={k}
                  />
                  <path
                    d={`M${xs[i]} ${LINE_Y - r} A${r} ${r} 0 0 1 ${xs[i]} ${LINE_Y + r} Z`}
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
        const passed = i <= lastStarted && !isActive;
        const [c1, c2] = signalColors(st.id);
        return (
          <div
            key={st.id}
            style={{
              position: "absolute",
              left: xs[i] - 110,
              width: 220,
              top: NAME_CY - NAME_H / 2,
              height: NAME_H,
              display: "flex",
              justifyContent: "center",
            }}
          >
            <div
              style={{
                position: "relative",
                padding: `0 ${PILL_PAD}px`,
                height: NAME_H,
                fontSize: SIZE.station,
                lineHeight: `${NAME_H}px`,
                whiteSpace: "nowrap",
              }}
            >
              {/* 当前站的实心底 */}
              <div
                style={{
                  position: "absolute",
                  inset: 0,
                  borderRadius: NAME_H / 2,
                  background:
                    c1 === c2
                      ? c1
                      : `linear-gradient(90deg, ${c1} 30%, ${c2} 70%)`,
                  opacity: k,
                }}
              />
              <span
                style={{
                  position: "relative",
                  color: rgba(C.cream, passed ? 1 : 0.8),
                  textShadow: TEXT_SHADOW_SOFT,
                  opacity: 1 - k,
                }}
              >
                {st.name}
              </span>
              <span
                style={{
                  position: "absolute",
                  left: 0,
                  right: 0,
                  top: 0,
                  textAlign: "center",
                  fontWeight: 700,
                  color: C.ink,
                  opacity: k,
                }}
              >
                {st.name}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
};
