// hook_title：开头的大字问题。两行，字大，放在画面下半部（走廊地面的位置），带一点透视倾斜。
// 第 0 帧就完整可见（第一帧 = 实物 + 大字问题），没有淡入；全程缓慢放大，保证第一帧就在动；最后几帧淡出。
import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { fitFontSize } from "../lib/text";
import { C, CLAMP, FONT_FAMILY, rgba, SAFE, SIZE, W } from "../theme";
import { Overlay } from "../timeline";

export const HookTitle: React.FC<{ overlay: Overlay; duration: number }> = ({
  overlay,
  duration,
}) => {
  const frame = useCurrentFrame();
  const lines = overlay.text.split("\n");
  const last = lines.length - 1;
  const maxW = SAFE.width - 70; // 透视倾斜后底边会略宽，留一点余量
  const sizes = lines.map((l, i) =>
    fitFontSize(l, i === last ? SIZE.hookMain : SIZE.hookLead, maxW, 700),
  );
  const shadow = `0 3px 0 ${rgba(C.ink, 0.9)}, 0 6px 22px ${rgba(C.ink, 0.85)}, 0 0 8px ${rgba(C.ink, 0.8)}`;

  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        width: W,
        top: 930,
        height: 300,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        perspective: 1500,
        opacity: interpolate(frame, [duration - 8, duration], [1, 0], CLAMP),
      }}
    >
      <div
        style={{
          transform: "rotateX(22deg)",
          transformOrigin: "50% 100%",
          scale: interpolate(frame, [0, duration], [1, 1.045], CLAMP),
          fontFamily: FONT_FAMILY,
          fontWeight: 700,
          color: C.cream,
          textAlign: "center",
          textShadow: shadow,
          whiteSpace: "nowrap",
        }}
      >
        {lines.map((l, i) => (
          <div key={i} style={{ fontSize: sizes[i], lineHeight: 1.22 }}>
            {l}
          </div>
        ))}
      </div>
    </div>
  );
};
