// 占位卡：这个镜头还没有任何 Blender 帧时铺在底层。明确标「占位 · 非成片画面」，不冒充成片。
import React from "react";
import { AbsoluteFill } from "remotion";
import { STR } from "../strings";
import { C, FONT_FAMILY, H, rgba, SAFE, W } from "../theme";
import { Shot } from "../timeline";

export const PlaceholderCard: React.FC<{ shot: Shot }> = ({ shot }) => {
  return (
    <AbsoluteFill style={{ backgroundColor: C.ink, fontFamily: FONT_FAMILY }}>
      {/* 斜纹：一眼看出这是占位，不是画面 */}
      <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
        <defs>
          <pattern
            id={`hatch-${shot.id}`}
            width={56}
            height={56}
            patternUnits="userSpaceOnUse"
            patternTransform="rotate(35)"
          >
            <line
              x1={0}
              y1={0}
              x2={0}
              y2={56}
              stroke={rgba(C.cream, 0.045)}
              strokeWidth={14}
            />
          </pattern>
        </defs>
        <rect width={W} height={H} fill={`url(#hatch-${shot.id})`} />
      </svg>

      {/* 大号镜头号水印 */}
      <div
        style={{
          position: "absolute",
          left: 0,
          width: W,
          top: 800,
          textAlign: "center",
          fontSize: 300,
          fontWeight: 700,
          lineHeight: 1,
          color: rgba(C.cream, 0.05),
          letterSpacing: 8,
        }}
      >
        {shot.id}
      </div>

      {/* 说明块：放在内容区上部，避开标签和图表面板 */}
      <div
        style={{
          position: "absolute",
          left: SAFE.left,
          width: SAFE.width,
          top: 428,
          color: rgba(C.cream, 0.62),
        }}
      >
        <div
          style={{ display: "flex", alignItems: "center", gap: 18, height: 50 }}
        >
          <div
            style={{
              flexShrink: 0,
              fontSize: 25,
              lineHeight: "40px",
              padding: "0 14px",
              border: `2px dashed ${rgba(C.cream, 0.7)}`,
              color: rgba(C.cream, 0.92),
              borderRadius: 6,
            }}
          >
            {STR.placeholderTag}
          </div>
          <div
            style={{
              fontSize: 31,
              fontWeight: 700,
              color: rgba(C.cream, 0.82),
              whiteSpace: "nowrap",
              overflow: "hidden",
              textOverflow: "ellipsis",
            }}
          >
            {shot.id} {shot.name}
          </div>
        </div>
        <div
          style={{
            fontSize: 24,
            lineHeight: "36px",
            marginTop: 6,
            whiteSpace: "pre",
            overflow: "hidden",
            textOverflow: "ellipsis",
          }}
        >
          {[
            `${STR.placeholderStatus} ${shot.status}`,
            STR.placeholderHint,
            `${STR.placeholderScale} ${shot.scale}`,
          ].join("  ·  ")}
        </div>
        <div
          style={{
            fontSize: 22,
            lineHeight: "30px",
            marginTop: 2,
            color: rgba(C.cream, 0.45),
            display: "-webkit-box",
            WebkitLineClamp: 2,
            WebkitBoxOrient: "vertical",
            overflow: "hidden",
          }}
        >
          {STR.placeholderCamera}：{shot.camera}
        </div>
      </div>
    </AbsoluteFill>
  );
};
