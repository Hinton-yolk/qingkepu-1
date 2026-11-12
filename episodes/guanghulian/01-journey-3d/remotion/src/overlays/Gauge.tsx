// gauge：「进光纤的光」读数。
//   耦合效率 η = exp(−d² / w²)，w = 模场半径（shotConfig.MODE_FIELD_RADIUS_UM，来源 FACTS F11），d = 横向偏移。
//   d 依次停在 0 → 文案里写的各个偏移量 → 0（文案解析不出时用后备值），每一档平分这条标注的时长。
//   左边是截面示意：两个圆形光斑错开，没对上的部分标珊瑚色；右边是百分比读数和偏移量。
import React, { useId } from "react";
import { Easing, interpolate, useCurrentFrame } from "remotion";
import {
  GAUGE_OFFSETS_FALLBACK_UM,
  MODE_FIELD_RADIUS_UM,
  PANEL_HEIGHT,
} from "../shotConfig";
import { STR } from "../strings";
import { C, CLAMP, rgba, SIZE } from "../theme";
import { Overlay } from "../timeline";
import { innerSize, Panel } from "./Panel";

type Props = { overlay: Overlay; duration: number };

/** 从「…偏 2 µm …偏 5 µm …」里取出偏移量 */
const parseOffsets = (text: string) => {
  const out: number[] = [];
  const re = /偏\s*([\d.]+)\s*µm/g;
  let m: RegExpExecArray | null;
  while ((m = re.exec(text))) out.push(parseFloat(m[1]));
  return out.length > 0 ? out : GAUGE_OFFSETS_FALLBACK_UM;
};

export const Gauge: React.FC<Props> = ({ overlay, duration }) => {
  const frame = useCurrentFrame();
  const uid = useId().replace(/:/g, "");
  const { w, h } = innerSize(PANEL_HEIGHT.gauge);
  const colon = overlay.text.indexOf("：");
  const title = colon > 0 ? overlay.text.slice(0, colon) : overlay.text;

  // 各档：0 → 偏移量们 → 0；每档占 1/n 的时长，前 40% 用来移动，其余停住
  const stops = [0, ...parseOffsets(overlay.text), 0];
  const slice = duration / stops.length;
  const idx = Math.min(stops.length - 1, Math.floor(frame / slice));
  const prev = stops[Math.max(0, idx - 1)];
  const d =
    idx === 0
      ? stops[0]
      : interpolate(frame - idx * slice, [0, slice * 0.4], [prev, stops[idx]], {
          ...CLAMP,
          easing: Easing.inOut(Easing.cubic),
        });
  const eta = Math.exp(
    -(d * d) / (MODE_FIELD_RADIUS_UM * MODE_FIELD_RADIUS_UM),
  );
  const pct = Math.round(eta * 100);
  const dMax = Math.max(...stops, 1);

  // 截面示意：1 µm 画多少像素，按最大偏移量让两个光斑都放得下
  const DW = 300;
  const s = Math.min(15, (DW - 16) / (2 * MODE_FIELD_RADIUS_UM + dMax));
  const r = MODE_FIELD_RADIUS_UM * s;
  const cy = 132;
  const fx = 8 + r; // 光纤一侧的圆心（不动）
  const sx = fx + d * s; // 芯片来的光斑（错开 d）

  const opacity = Math.min(
    interpolate(frame, [0, 8], [0, 1], CLAMP),
    interpolate(frame, [duration - 8, duration], [1, 0], CLAMP),
  );

  const RX = DW + 44;
  const barW = w - RX;

  return (
    <Panel height={PANEL_HEIGHT.gauge} opacity={opacity}>
      <svg
        width={DW}
        height={h}
        style={{ position: "absolute", left: 0, top: 0 }}
      >
        <defs>
          <radialGradient id={`spot-${uid}`}>
            <stop offset="0%" stopColor={C.light} stopOpacity={0.95} />
            <stop offset="70%" stopColor={C.light} stopOpacity={0.55} />
            <stop offset="100%" stopColor={C.light} stopOpacity={0.28} />
          </radialGradient>
          <clipPath id={`fiber-${uid}`}>
            <circle cx={fx} cy={cy} r={r} />
          </clipPath>
        </defs>
        {/* 没对上的部分：珊瑚色（漏掉的光） */}
        <circle cx={sx} cy={cy} r={r} fill={rgba(C.alert, 0.5)} />
        {/* 对上的部分：青色，中间亮、边缘渐暗 */}
        <g clipPath={`url(#fiber-${uid})`}>
          <circle cx={sx} cy={cy} r={r} fill={C.ink} />
          <circle cx={sx} cy={cy} r={r} fill={`url(#spot-${uid})`} />
        </g>
        {/* 光纤能接住的范围：奶油色虚线圆 */}
        <circle
          cx={fx}
          cy={cy}
          r={r}
          fill="none"
          stroke={rgba(C.cream, 0.85)}
          strokeWidth={2.5}
          strokeDasharray="9 7"
        />
        {/* 两个圆心 + 偏移量的双箭头 */}
        <circle cx={fx} cy={cy} r={3.5} fill={C.cream} />
        <circle cx={sx} cy={cy} r={3.5} fill={C.cream} />
        {d * s > 14 ? (
          <g
            stroke={C.cream}
            strokeWidth={2}
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <line x1={fx} y1={cy} x2={sx} y2={cy} />
            <path
              d={`M${fx + 8} ${cy - 6} L${fx} ${cy} L${fx + 8} ${cy + 6}`}
            />
            <path
              d={`M${sx - 8} ${cy - 6} L${sx} ${cy} L${sx - 8} ${cy + 6}`}
            />
          </g>
        ) : null}
      </svg>
      {/* 图例 */}
      <div
        style={{
          position: "absolute",
          left: 0,
          top: 228,
          width: DW,
          fontSize: 23,
          lineHeight: "32px",
          color: rgba(C.cream, 0.8),
          whiteSpace: "nowrap",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div
            style={{
              width: 20,
              height: 20,
              boxSizing: "border-box",
              borderRadius: 10,
              border: `2.5px dashed ${rgba(C.cream, 0.85)}`,
            }}
          />
          {STR.spotFiber}
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div
            style={{
              width: 20,
              height: 20,
              borderRadius: 10,
              backgroundColor: rgba(C.light, 0.75),
            }}
          />
          {STR.spotChip}
        </div>
      </div>

      {/* 读数 */}
      <div style={{ position: "absolute", left: RX, top: 0, width: barW }}>
        <div style={{ fontSize: 34, lineHeight: "44px", fontWeight: 700 }}>
          {title}
        </div>
        <div
          style={{
            display: "flex",
            alignItems: "baseline",
            gap: 10,
            height: 132,
            marginTop: 4,
            fontVariantNumeric: "tabular-nums",
          }}
        >
          <span
            style={{
              fontSize: 40,
              color: rgba(C.cream, 0.75),
              opacity: d > 0.05 ? 1 : 0,
            }}
          >
            {STR.approx}
          </span>
          <span
            style={{
              fontSize: 124,
              lineHeight: "132px",
              fontWeight: 700,
              color: C.light,
              minWidth: 210,
              textAlign: "right",
            }}
          >
            {pct}
          </span>
          <span style={{ fontSize: 60, fontWeight: 700, color: C.light }}>
            {STR.percent}
          </span>
        </div>
        {/* 条：青色 = 进去的，珊瑚色 = 漏掉的 */}
        <div
          style={{
            position: "relative",
            width: barW,
            height: 16,
            marginTop: 10,
            borderRadius: 8,
            overflow: "hidden",
            backgroundColor: rgba(C.alert, 0.55),
          }}
        >
          <div
            style={{
              position: "absolute",
              left: 0,
              top: 0,
              bottom: 0,
              width: barW * eta,
              backgroundColor: C.light,
            }}
          />
        </div>
        <div
          style={{
            marginTop: 16,
            fontSize: SIZE.panelLabel + 5,
            lineHeight: "44px",
            fontVariantNumeric: "tabular-nums",
            color: d > 0.05 ? C.cream : rgba(C.cream, 0.7),
          }}
        >
          {STR.offset} {d.toFixed(1)} {STR.unitMicron}
        </div>
      </div>
    </Panel>
  );
};
