// hook_title：开头的大字问题。两行，字大，放在走廊地面的位置（shotConfig.HOOK_BOX），带一点透视倾斜。
// 第 0 帧就完整可见（第一帧 = 实物 + 大字问题），没有淡入；全程缓慢放大，保证第一帧就在动；最后几帧淡出。
// 地面很亮：字后面垫一块半透明的暗垫（和字一起倾斜，像铺在地上），字本身再加深色描边和投影。
// 大字的位置固定；它在场时，标签和路线上的字让开这一块（lib/shotLayout、lib/pathTrace）。
import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { fitFontSize } from "../lib/text";
import { HOOK_BOX } from "../shotConfig";
import {
  BACKING,
  C,
  CLAMP,
  FONT_FAMILY,
  outlineShadow,
  rgba,
  SIZE,
} from "../theme";
import { Overlay } from "../timeline";

const PAD_X = 34;

export const HookTitle: React.FC<{ overlay: Overlay; duration: number }> = ({
  overlay,
  duration,
}) => {
  const frame = useCurrentFrame();
  const lines = overlay.text.split("\n");
  const last = lines.length - 1;
  // 全程放大到 1.03 倍后仍不出 HOOK_BOX
  const maxW = (HOOK_BOX.w - PAD_X * 2) / 1.03;
  const sizes = lines.map((l, i) =>
    fitFontSize(l, i === last ? SIZE.hookMain : SIZE.hookLead, maxW, 700),
  );
  const shadow = `${outlineShadow(3)}, 0 5px 0 ${rgba(C.ink, 0.9)}, 0 8px 22px ${rgba(C.ink, 0.9)}`;

  return (
    <div
      style={{
        position: "absolute",
        left: HOOK_BOX.x,
        top: HOOK_BOX.y,
        width: HOOK_BOX.w,
        height: HOOK_BOX.h,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        perspective: 1500,
        opacity: interpolate(frame, [duration - 8, duration], [1, 0], CLAMP),
      }}
    >
      <div
        style={{
          transform: "rotateX(20deg)",
          transformOrigin: "50% 100%",
          scale: interpolate(frame, [0, duration], [1, 1.03], CLAMP),
          padding: `6px ${PAD_X}px 10px`,
          backgroundColor: rgba(C.ink, BACKING.hook),
          boxShadow: `0 0 28px 14px ${rgba(C.ink, BACKING.hook)}`,
          borderRadius: 22,
          fontFamily: FONT_FAMILY,
          fontWeight: 700,
          color: C.cream,
          textAlign: "center",
          textShadow: shadow,
          whiteSpace: "nowrap",
        }}
      >
        {lines.map((l, i) => (
          <div key={i} style={{ fontSize: sizes[i], lineHeight: 1.2 }}>
            {l}
          </div>
        ))}
      </div>
    </div>
  );
};
