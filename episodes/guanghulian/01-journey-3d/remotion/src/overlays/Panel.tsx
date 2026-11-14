// 图表面板的底：内容区下部一块半透明深色底，细边。波形、时序图、读数都画在它里面。
import React, { useContext } from "react";
import { panelRect } from "../shotConfig";
import { C, FONT_FAMILY, PANEL_BOTTOM, rgba } from "../theme";

export const PANEL_PAD = 22;

/**
 * 面板的下沿。默认在角注带上面；同时在场的角注叠得更高时，ShotOverlays 用它把整块面板往上让
 * （值由 lib/shotLayout.panelBottomFor 算，一块面板全程一个值）。
 */
export const PanelBottom = React.createContext(PANEL_BOTTOM);

export const Panel: React.FC<{
  height: number;
  opacity: number;
  children: React.ReactNode;
}> = ({ height, opacity, children }) => {
  const r = panelRect(height, useContext(PanelBottom));
  return (
    <div
      style={{
        position: "absolute",
        left: r.x,
        top: r.y,
        width: r.w,
        height: r.h,
        boxSizing: "border-box",
        padding: PANEL_PAD,
        backgroundColor: rgba(C.ink, 0.82),
        border: `1.5px solid ${rgba(C.cream, 0.16)}`,
        borderRadius: 14,
        opacity,
        fontFamily: FONT_FAMILY,
        color: C.cream,
      }}
    >
      <div style={{ position: "relative", width: "100%", height: "100%" }}>
        {children}
      </div>
    </div>
  );
};

/** 面板内的尺寸 */
export const innerSize = (height: number) => {
  const r = panelRect(height);
  return { w: r.w - PANEL_PAD * 2, h: r.h - PANEL_PAD * 2 };
};

/** 面板里的小标题：左边一小段颜色条，说明这条线是电还是光。suffix = 标题后面的小字（图内小注） */
export const RowLabel: React.FC<{
  x: number;
  y: number;
  text: string;
  swatch?: string;
  fontSize: number;
  opacity?: number;
  suffix?: string;
  suffixSize?: number;
}> = ({ x, y, text, swatch, fontSize, opacity = 1, suffix, suffixSize }) => (
  <div
    style={{
      position: "absolute",
      left: x,
      top: y,
      height: 36,
      display: "flex",
      alignItems: "center",
      gap: 12,
      fontSize,
      lineHeight: "36px",
      whiteSpace: "nowrap",
      opacity,
    }}
  >
    {swatch ? (
      <div
        style={{
          width: 26,
          height: 5,
          borderRadius: 3,
          backgroundColor: swatch,
        }}
      />
    ) : null}
    <span>{text}</span>
    {suffix ? (
      <span
        style={{
          marginLeft: -6,
          fontSize: suffixSize ?? fontSize,
          color: rgba(C.cream, 0.78),
        }}
      >
        {suffix}
      </span>
    ) : null}
  </div>
);
