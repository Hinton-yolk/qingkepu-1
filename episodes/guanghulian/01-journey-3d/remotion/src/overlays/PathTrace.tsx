// path_trace：路线。按文案分两种：
//   「电 → 光 → 电」（有箭头）：路线图。
//       有 path_* 取样锚点时：沿这些点画一条 2D 虚线，电的两段金色、光的一段青色，带深色描边；
//         标注开始后 drawSeconds 秒内从 A 端画到 B 端，之后保持，结束前淡出；三段各自的中点旁放一个字。
//         3D 里的发光管有的段被机柜挡住，这条线把整条路线补全，所以画成虚线（是示意，不是实物）。
//       没有 path_* 锚点时：退回成内容区上沿的一行图例（色条 + 字）。
//   「出发 · 电的路 · …」（没有箭头）：几个站名，有锚点贴锚点（锚点名 = 站名或站 id），没有时沿一条浅弧线排开。
// 取样点的命名、线宽、虚线等见 shotConfig.PATH_TRACE；几何在 lib/pathTrace。
import React from "react";
import { Easing, interpolate, useCurrentFrame } from "remotion";
import { pointAtLength, toPathD, truncatePolyline } from "../lib/geom";
import { anchorSample } from "../lib/manifest";
import {
  pathChips,
  pathGeometry,
  PathKind,
  pathSections,
} from "../lib/pathTrace";
import { localSpan, pathChipSizes, pathWords } from "../lib/shotLayout";
import {
  PATH_TRACE,
  pathTraceDefault,
  SIGNAL_WORDS,
  STATION_SIGNAL,
} from "../shotConfig";
import {
  BACKING,
  C,
  CLAMP,
  FONT_FAMILY,
  H,
  rgba,
  SAFE,
  SIZE,
  TEXT_SHADOW_SOFT,
  W,
} from "../theme";
import { FPS, Overlay, Shot, TL, toFrame } from "../timeline";

type Props = { overlay: Overlay; shot: Shot; duration: number };

const kindColor = (k: PathKind) => (k === "light" ? C.light : C.electric);

/** 文案里的一个字 → 颜色。「电」「光」（或旧写法「金（电）」）；认不出的用奶油色 */
const wordColor = (word: string) => {
  const hit = Object.keys(SIGNAL_WORDS).find((k) => word.includes(k));
  return hit ? kindColor(SIGNAL_WORDS[hit]) : C.cream;
};
/** 「金（电）」→「电」 */
const wordLabel = (word: string) => /^.（(.+)）$/.exec(word)?.[1] ?? word;

// ---------- 路线图：沿取样锚点画线 ----------
const Route: React.FC<Props> = ({ overlay, shot, duration }) => {
  const frame = useCurrentFrame();
  const film = toFrame(overlay.t) + frame + 1;
  const local = localSpan(shot, overlay).from + frame;
  const geo = pathGeometry(shot.id, film);
  const words = pathWords(overlay).map(wordLabel);
  const hookActive = shot.overlays.some((o) => {
    if (o.type !== "hook_title") return false;
    const s = localSpan(shot, o);
    return local >= s.from && local < s.to;
  });
  const chips = pathChips(geo, pathChipSizes(overlay), hookActive);

  // 画到多长了：匀速略带收尾，drawSeconds 秒画完
  const drawn =
    geo.total *
    interpolate(frame, [0, PATH_TRACE.drawSeconds * FPS], [0, 1], {
      ...CLAMP,
      easing: Easing.out(Easing.quad),
    });
  const drawing = drawn < geo.total - 0.5;

  const lines: React.ReactNode[] = [];
  let acc = 0;
  let head: { x: number; y: number; color: string } | null = null;
  for (let i = 0; i < geo.pieces.length; i++) {
    const piece = geo.pieces[i];
    const startAt = acc;
    acc += piece.len;
    if (drawn <= startAt) break;
    const part = Math.min(piece.len, drawn - startAt);
    const pts =
      part >= piece.len ? piece.pts : truncatePolyline(piece.pts, part);
    if (pts.length < 2) continue;
    const color = kindColor(geo.sections[piece.section].kind);
    const d = toPathD(pts);
    const dash = PATH_TRACE.dash.join(" ");
    lines.push(
      <g key={i} fill="none" strokeLinecap="round" strokeLinejoin="round">
        <path
          d={d}
          stroke={rgba(C.ink, 0.88)}
          strokeWidth={PATH_TRACE.outlineWidth}
          strokeDasharray={dash}
        />
        <path
          d={d}
          stroke={color}
          strokeWidth={PATH_TRACE.lineWidth}
          strokeDasharray={dash}
        />
      </g>,
    );
    if (drawing && part < piece.len) {
      const p = pointAtLength(piece.pts, part).p;
      head = { x: p.x, y: p.y, color };
    }
  }

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        fontFamily: FONT_FAMILY,
        opacity: interpolate(frame, [duration - 8, duration], [1, 0], CLAMP),
      }}
    >
      <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
        {lines}
        {/* 正在画的那一头：一个小圆点（跟着「一个比特」走） */}
        {head ? (
          <circle
            cx={head.x}
            cy={head.y}
            r={9}
            fill={head.color}
            stroke={rgba(C.ink, 0.9)}
            strokeWidth={3.5}
          />
        ) : null}
      </svg>
      {chips.map((chip) => {
        const word = words[chip.section];
        if (!word) return null;
        const color = kindColor(geo.sections[chip.section].kind);
        return (
          <div
            key={chip.section}
            style={{
              position: "absolute",
              left: chip.rect.x,
              top: chip.rect.y,
              width: chip.rect.w,
              height: chip.rect.h,
              boxSizing: "border-box",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              backgroundColor: rgba(C.ink, BACKING.chip),
              border: `2px solid ${rgba(color, 0.85)}`,
              borderRadius: 12,
              fontSize: SIZE.pathChar,
              fontWeight: 700,
              lineHeight: 1,
              color,
              textShadow: TEXT_SHADOW_SOFT,
              whiteSpace: "nowrap",
              // 线画过这一段的中点，字才出现
              opacity: interpolate(drawn - chip.at, [0, 36], [0, 1], CLAMP),
            }}
          >
            {word}
          </div>
        );
      })}
    </div>
  );
};

// ---------- 路线图的退路：一行图例 ----------
const Legend: React.FC<Props> = ({ overlay, duration }) => {
  const frame = useCurrentFrame();
  const colon = overlay.text.indexOf("：");
  const title = colon > 0 ? overlay.text.slice(0, colon) : null;
  const segs = pathWords(overlay).map((w) => ({
    color: wordColor(w),
    label: wordLabel(w),
  }));
  // 图例一段一段出现：平分 drawSeconds
  const step = (PATH_TRACE.drawSeconds * FPS) / Math.max(1, segs.length);

  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        width: W,
        top: SAFE.top + 10,
        display: "flex",
        justifyContent: "center",
        fontFamily: FONT_FAMILY,
        opacity: Math.min(
          interpolate(frame, [0, 8], [0, 1], CLAMP),
          interpolate(frame, [duration - 8, duration], [1, 0], CLAMP),
        ),
      }}
    >
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 2,
          padding: "8px 22px 10px",
          backgroundColor: rgba(C.ink, BACKING.chip),
          border: `1.5px solid ${rgba(C.cream, 0.4)}`,
          borderRadius: 12,
          color: C.cream,
          textShadow: TEXT_SHADOW_SOFT,
          whiteSpace: "nowrap",
        }}
      >
        {title ? (
          <div style={{ fontSize: 36, lineHeight: "46px", fontWeight: 700 }}>
            {title}
          </div>
        ) : null}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 14,
            fontSize: SIZE.pathChar,
            fontWeight: 700,
            lineHeight: "58px",
          }}
        >
          {segs.map((s, i) => (
            <React.Fragment key={i}>
              {i > 0 ? (
                <span style={{ color: rgba(C.cream, 0.7), fontWeight: 400 }}>
                  →
                </span>
              ) : null}
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 10,
                  opacity: interpolate(
                    frame,
                    [i * step, i * step + 8],
                    [0.3, 1],
                    CLAMP,
                  ),
                }}
              >
                <div
                  style={{
                    width: 72,
                    height: 8,
                    borderRadius: 4,
                    backgroundColor: s.color,
                  }}
                />
                <span style={{ color: s.color }}>{s.label}</span>
              </div>
            </React.Fragment>
          ))}
        </div>
      </div>
    </div>
  );
};

// ---------- 几个站名 ----------
const stationColor = (name: string) => {
  const st = TL.stations.find((s) => s.name === name);
  const kind = st ? (STATION_SIGNAL[st.id] ?? "electric") : "electric";
  return {
    st,
    colors:
      kind === "light"
        ? [C.light, C.light]
        : kind === "both"
          ? [C.electric, C.light]
          : [C.electric, C.electric],
  };
};

const StationNames: React.FC<Props> = ({ overlay, shot, duration }) => {
  const frame = useCurrentFrame();
  const film = toFrame(overlay.t) + frame + 1;
  const names = overlay.text.split(" · ").map((s) => s.trim());
  const n = names.length;
  const step = (duration * 0.62) / n;

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        fontFamily: FONT_FAMILY,
        opacity: interpolate(frame, [duration - 8, duration], [1, 0], CLAMP),
      }}
    >
      {names.map((name, i) => {
        const { st, colors } = stationColor(name);
        const a =
          anchorSample(shot.id, name, film) ??
          (st ? anchorSample(shot.id, st.id, film) : null);
        const p = a && a.inFrame ? a : pathTraceDefault(i, n);
        const x = Math.max(SAFE.left + 80, Math.min(SAFE.right - 80, p.x));
        const y = Math.max(SAFE.top + 70, Math.min(SAFE.bottom - 120, p.y));
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: x - 110,
              width: 220,
              top: y - 70,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              opacity: interpolate(
                frame,
                [i * step, i * step + 8],
                [0, 1],
                CLAMP,
              ),
              translate: interpolate(
                frame,
                [i * step, i * step + 8],
                ["0px 10px", "0px 0px"],
                CLAMP,
              ),
            }}
          >
            <div
              style={{
                padding: "4px 14px",
                backgroundColor: rgba(C.ink, BACKING.chip),
                border: `1.5px solid ${rgba(C.cream, 0.5)}`,
                borderRadius: 10,
                fontSize: SIZE.labelHead,
                lineHeight: "48px",
                fontWeight: 700,
                color: C.cream,
                textShadow: TEXT_SHADOW_SOFT,
                whiteSpace: "nowrap",
              }}
            >
              {name}
            </div>
            {/* 站点：左半 / 右半各一种信号色 */}
            <div
              style={{
                width: 18,
                height: 18,
                marginTop: 10,
                borderRadius: 9,
                background: `linear-gradient(90deg, ${colors[0]} 50%, ${colors[1]} 50%)`,
                outline: `3px solid ${rgba(C.ink, 0.85)}`,
              }}
            />
          </div>
        );
      })}
    </div>
  );
};

export const PathTrace: React.FC<Props> = (props) => {
  // 有箭头的是路线图（有取样锚点就画线，没有就退回图例）；否则当作一串站名
  if (props.overlay.text.includes("→")) {
    return pathSections(props.shot.id).length > 0 ? (
      <Route {...props} />
    ) : (
      <Legend {...props} />
    );
  }
  return <StationNames {...props} />;
};
