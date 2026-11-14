// label / term / scale / alert：贴在物体旁边的短标签。
//   样子：深色半透明衬底 + 细描边 + 字（主行 ≥ 34 px，副行 ≥ 28 px），一条引线从锚点连到衬底边上。
//   位置：lib/shotLayout.layoutLabels 逐帧算。对上了 anchors JSON 里的锚点就跟着锚点走、停在它旁边不挡住它；
//         没对上就放在默认位置，不画引线。锚点出画或转到相机背后时，标签停在最后的位置淡出。
//   文字能拆成「主名 + 说明」的（见 lib/text.splitHeadBody）排两行。alert 用珊瑚色；其余用奶油色。
// 一个镜头一个 AnchoredLabels：按当前帧决定哪些标签在场（同一时刻最多 MAX_LABELS 个）。
import React from "react";
import { Easing, interpolate, useCurrentFrame } from "remotion";
import { closestOnRect } from "../lib/geom";
import { LABEL_CHIP, layoutLabels } from "../lib/shotLayout";
import {
  BACKING,
  C,
  CLAMP,
  FONT_FAMILY,
  H,
  rgba,
  TEXT_SHADOW_SOFT,
  W,
} from "../theme";
import { Shot } from "../timeline";

export const AnchoredLabels: React.FC<{ shot: Shot }> = ({ shot }) => {
  const frame = useCurrentFrame(); // 镜头内帧号
  const placed = layoutLabels(shot, frame);
  if (placed.length === 0) return null;

  return (
    <div style={{ position: "absolute", inset: 0, fontFamily: FONT_FAMILY }}>
      {placed.map(({ spec, rect, target, presence }) => {
        const f = frame - spec.from;
        const duration = spec.to - spec.from;
        const color = spec.kind === "alert" ? C.alert : C.cream;
        const drawK = interpolate(f, [0, 7], [0, 1], {
          ...CLAMP,
          easing: Easing.out(Easing.cubic),
        });
        const edge = target ? closestOnRect(rect, target) : null;
        const leaderLen =
          target && edge ? Math.hypot(edge.x - target.x, edge.y - target.y) : 0;

        return (
          <div
            key={spec.key}
            style={{
              position: "absolute",
              inset: 0,
              opacity:
                presence *
                interpolate(f, [duration - 6, duration], [1, 0], CLAMP),
            }}
          >
            {target && edge ? (
              <svg
                width={W}
                height={H}
                style={{ position: "absolute", inset: 0 }}
              >
                {leaderLen > 10 ? (
                  <>
                    {/* 深色衬线，保证压在亮画面上也看得见 */}
                    <line
                      x1={target.x}
                      y1={target.y}
                      x2={edge.x}
                      y2={edge.y}
                      stroke={rgba(C.ink, 0.85)}
                      strokeWidth={7}
                      strokeLinecap="round"
                      strokeDasharray={leaderLen}
                      strokeDashoffset={leaderLen * (1 - drawK)}
                    />
                    <line
                      x1={target.x}
                      y1={target.y}
                      x2={edge.x}
                      y2={edge.y}
                      stroke={color}
                      strokeWidth={3}
                      strokeLinecap="round"
                      strokeDasharray={leaderLen}
                      strokeDashoffset={leaderLen * (1 - drawK)}
                    />
                  </>
                ) : null}
                <circle
                  cx={target.x}
                  cy={target.y}
                  r={8}
                  fill={color}
                  stroke={rgba(C.ink, 0.9)}
                  strokeWidth={3.5}
                  opacity={drawK}
                />
              </svg>
            ) : null}
            <div
              style={{
                position: "absolute",
                left: rect.x,
                top: rect.y,
                width: rect.w,
                height: rect.h,
                boxSizing: "border-box",
                padding: `${LABEL_CHIP.padY - 1.5}px ${LABEL_CHIP.padX - 1.5}px`,
                backgroundColor: rgba(C.ink, BACKING.chip),
                border: `1.5px solid ${rgba(color, 0.6)}`,
                borderRadius: 10,
                color,
                textShadow: TEXT_SHADOW_SOFT,
                whiteSpace: "nowrap",
                opacity: interpolate(f, [3, 9], [0, 1], CLAMP),
                translate: interpolate(
                  f,
                  [3, 9],
                  ["0px 8px", "0px 0px"],
                  CLAMP,
                ),
              }}
            >
              {spec.head.lines.map((l, i) => (
                <div
                  key={`h${i}`}
                  style={{
                    fontSize: spec.head.size,
                    lineHeight: `${spec.head.lineH}px`,
                    fontWeight: 700,
                  }}
                >
                  {l}
                </div>
              ))}
              {spec.body
                ? spec.body.lines.map((l, i) => (
                    <div
                      key={`b${i}`}
                      style={{
                        marginTop: i === 0 ? LABEL_CHIP.gap : 0,
                        fontSize: spec.body!.size,
                        lineHeight: `${spec.body!.lineH}px`,
                        fontWeight: spec.body!.weight,
                        opacity: spec.kind === "scale" ? 1 : 0.94,
                      }}
                    >
                      {l}
                    </div>
                  ))
                : null}
            </div>
          </div>
        );
      })}
    </div>
  );
};
