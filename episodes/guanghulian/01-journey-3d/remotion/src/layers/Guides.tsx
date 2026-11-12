// 调试用参考线：安全区、五站条、字幕的位置。默认不显示；Studio 里把 showGuides 打开，或 still 时加 --guides。
import React from "react";
import { C, H, PANEL_BOTTOM, rgba, SAFE, W } from "../theme";

export const Guides: React.FC = () => {
  const line = (y: number, key: string) => (
    <line key={key} x1={0} y1={y} x2={W} y2={y} stroke={rgba(C.alert, 0.7)} strokeWidth={2} strokeDasharray="10 8" />
  );
  return (
    <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
      {line(SAFE.stationY, "station")}
      {line(SAFE.top, "top")}
      {line(PANEL_BOTTOM, "panel")}
      {line(SAFE.bottom, "bottom")}
      {line(SAFE.subtitleY, "subtitle")}
      <rect
        x={SAFE.left}
        y={SAFE.top}
        width={SAFE.width}
        height={SAFE.bottom - SAFE.top}
        fill="none"
        stroke={rgba(C.alert, 0.7)}
        strokeWidth={2}
      />
    </svg>
  );
};
