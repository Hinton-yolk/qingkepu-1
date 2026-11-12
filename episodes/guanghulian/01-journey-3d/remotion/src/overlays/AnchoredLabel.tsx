// label / term / scale / alert：贴在物体旁边的短标签。细引线 + 小字，没有标题条。
//   有 anchors JSON（Blender 导出的每帧屏幕坐标）时跟着锚点走；没有时用按镜头给的默认位置（shotConfig）。
//   文字能拆成「主名 + 说明」的（见 lib/text.splitHeadBody）排两行：主名在横线上，说明在横线下。
//   alert 用珊瑚色；其余用奶油色。整块始终留在安全区内，并且不压到同时出现的图表面板。
import React from "react";
import { Easing, interpolate, useCurrentFrame } from "remotion";
import { anchorAt, anchorNames } from "../lib/manifest";
import { splitHeadBody, textWidth } from "../lib/text";
import { LabelSlot, LEADER } from "../shotConfig";
import { C, CLAMP, FONT_FAMILY, H, rgba, SAFE, SIZE, TEXT_SHADOW, W } from "../theme";
import { Overlay, toFrame } from "../timeline";

type Props = {
  overlay: Overlay;
  shotId: string;
  duration: number; // 帧
  slot: LabelSlot; // 没有锚点数据时的默认位置
  bottomLimit: number; // 文字不能低于这条线（同时有图表面板时 = 面板上沿）
};

const HEAD_H = 52;
const BODY_H = 42;

export const AnchoredLabel: React.FC<Props> = ({
  overlay,
  shotId,
  duration,
  slot,
  bottomLimit,
}) => {
  const frame = useCurrentFrame();
  const start = toFrame(overlay.t);
  const film = start + frame + 1;
  const names = anchorNames(overlay);

  const isAlert = overlay.type === "alert";
  const isTerm = overlay.type === "term";
  const isScale = overlay.type === "scale";
  const color = isAlert ? C.alert : C.cream;

  // 文字：scale 类的「A · B」是并列的两个尺寸，不分主次；其余拆成主名 + 说明
  const parts = isScale
    ? (() => {
        const p = overlay.text.split(" · ");
        return { head: p[0], body: p.length > 1 ? p.slice(1).join(" · ") : null };
      })()
    : splitHeadBody(overlay.text);
  const headSize = isTerm ? SIZE.term : SIZE.labelHead;
  const bodySize = isScale ? SIZE.labelHead : SIZE.labelBody;
  const bodyWeight = isScale ? 700 : 400;
  const maxTextW = 600;
  const headFit = Math.min(1, maxTextW / textWidth(parts.head, headSize, 700));
  const bodyFit = parts.body ? Math.min(1, maxTextW / textWidth(parts.body, bodySize, bodyWeight)) : 1;
  const headFs = Math.floor(headSize * headFit);
  const bodyFs = Math.floor(bodySize * bodyFit);
  const headW = textWidth(parts.head, headFs, 700);
  const bodyW = parts.body ? textWidth(parts.body, bodyFs, bodyWeight) : 0;
  const lineW = Math.max(headW, bodyW) + 14;

  // 锚点：有数据就跟着走；方向在这条标签的中点时刻定一次，免得中途左右翻
  const live = anchorAt(shotId, names, film);
  const mid = anchorAt(shotId, names, start + Math.round(duration / 2) + 1);
  const ax = live ? live.x : slot.x;
  const ay = live ? live.y : slot.y;
  const side = mid ? (mid.x < W / 2 ? "right" : "left") : slot.side;
  const bodyH = parts.body ? BODY_H : 0;
  const vert = mid
    ? mid.y - LEADER.dy - HEAD_H < SAFE.top + 8
      ? "down"
      : "up"
    : slot.vert;

  // 横线（文字的基线）位置：从锚点斜着引出，再限制在安全区内
  const dir = side === "right" ? 1 : -1;
  let ex = ax + dir * LEADER.dx;
  let ey = ay + (vert === "up" ? -LEADER.dy : LEADER.dy);
  ey = Math.max(SAFE.top + HEAD_H + 4, Math.min(bottomLimit - bodyH - 6, ey));
  if (side === "right") ex = Math.max(SAFE.left, Math.min(SAFE.right - lineW, ex));
  else ex = Math.min(SAFE.right, Math.max(SAFE.left + lineW, ex));
  const lineX0 = side === "right" ? ex : ex - lineW;

  // 锚点不可见（出画或在相机背后）时不画引线和圆点，只留文字
  const anchorOk =
    (live ? live.visible : true) && ay > SAFE.top - 40 && ay < SAFE.bottom + 40 && ax > 0 && ax < W;

  const drawK = interpolate(frame, [0, 7], [0, 1], { ...CLAMP, easing: Easing.out(Easing.cubic) });
  const textK = interpolate(frame, [3, 9], [0, 1], CLAMP);
  const outK = interpolate(frame, [duration - 6, duration], [1, 0], CLAMP);

  const leaderLen = Math.hypot(ex - ax, ey - ay);

  return (
    <div style={{ position: "absolute", inset: 0, opacity: outK, fontFamily: FONT_FAMILY }}>
      <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
        {anchorOk ? (
          <>
            {/* 深色衬线，保证压在亮画面上也看得见 */}
            <line x1={ax} y1={ay} x2={ex} y2={ey} stroke={rgba(C.ink, 0.6)} strokeWidth={5} strokeDasharray={leaderLen} strokeDashoffset={leaderLen * (1 - drawK)} />
            <line
              x1={ax}
              y1={ay}
              x2={ex}
              y2={ey}
              stroke={color}
              strokeWidth={2}
              strokeDasharray={leaderLen}
              strokeDashoffset={leaderLen * (1 - drawK)}
            />
            <circle cx={ax} cy={ay} r={6} fill={C.ink} stroke={color} strokeWidth={2.5} opacity={drawK} />
          </>
        ) : null}
        <line
          x1={lineX0}
          y1={ey}
          x2={lineX0 + lineW}
          y2={ey}
          stroke={rgba(C.ink, 0.6)}
          strokeWidth={5}
          opacity={textK}
        />
        <line
          x1={side === "right" ? ex : ex - lineW * textK}
          y1={ey}
          x2={side === "right" ? ex + lineW * textK : ex}
          y2={ey}
          stroke={color}
          strokeWidth={2}
        />
      </svg>
      <div
        style={{
          position: "absolute",
          left: lineX0,
          width: lineW,
          top: ey - HEAD_H,
          height: HEAD_H,
          display: "flex",
          alignItems: "flex-end",
          justifyContent: side === "right" ? "flex-start" : "flex-end",
          fontSize: headFs,
          fontWeight: 700,
          lineHeight: `${HEAD_H - 4}px`,
          color,
          textShadow: TEXT_SHADOW,
          whiteSpace: "nowrap",
          opacity: textK,
          translate: `0px ${interpolate(frame, [3, 9], [8, 0], CLAMP)}px`,
        }}
      >
        {parts.head}
      </div>
      {parts.body ? (
        <div
          style={{
            position: "absolute",
            left: lineX0,
            width: lineW,
            top: ey + 5,
            height: BODY_H,
            textAlign: side === "right" ? "left" : "right",
            fontSize: bodyFs,
            fontWeight: bodyWeight,
            lineHeight: `${BODY_H - 4}px`,
            color: isScale ? color : rgba(color === C.cream ? C.cream : color, 0.92),
            textShadow: TEXT_SHADOW,
            whiteSpace: "nowrap",
            opacity: textK,
          }}
        >
          {parts.body}
        </div>
      ) : null}
    </div>
  );
};
