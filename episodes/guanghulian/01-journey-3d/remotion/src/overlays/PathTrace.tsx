// path_trace：路径线本身由 Blender 画，这里只加文字。两种文案各有一种排法：
//   「A → B：金（电）→ 青（光）→ 金（电）」：一行路线名 + 一行图例（色条 + 字），放在内容区上沿
//   「出发 · 电的路 · …」：几个站名。有 anchors JSON 时贴在各自的锚点上（锚点名 = 站名或站 id），
//       没有时沿一条浅弧线排开；按顺序一个一个出现
import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { anchorAt } from "../lib/manifest";
import { pathTraceDefault, STATION_SIGNAL } from "../shotConfig";
import { C, CLAMP, FONT_FAMILY, rgba, SAFE, TEXT_SHADOW, W } from "../theme";
import { Overlay, TL, toFrame } from "../timeline";

type Props = { overlay: Overlay; shotId: string; duration: number };

/** 「金（电）」→ 颜色 + 字。金 = 电，青 = 光；认不出的用奶油色 */
const parseLegend = (seg: string) => {
  const m = /^(.)（(.+)）$/.exec(seg.trim());
  if (!m) return null;
  const color = m[1] === "金" ? C.electric : m[1] === "青" ? C.light : C.cream;
  return { color, label: m[2] };
};

const Legend: React.FC<Props> = ({ overlay, duration }) => {
  const frame = useCurrentFrame();
  const colon = overlay.text.indexOf("：");
  const title = colon > 0 ? overlay.text.slice(0, colon) : overlay.text;
  const segs = (colon > 0 ? overlay.text.slice(colon + 1) : "")
    .split("→")
    .map(parseLegend)
    .filter((s): s is { color: string; label: string } => s !== null);

  const opacity = Math.min(
    interpolate(frame, [0, 8], [0, 1], CLAMP),
    interpolate(frame, [duration - 8, duration], [1, 0], CLAMP),
  );
  // 图例一段一段出现：平分前 60% 的时长
  const step = (duration * 0.6) / Math.max(1, segs.length);

  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        width: W,
        top: SAFE.top + 14,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 4,
        fontFamily: FONT_FAMILY,
        color: C.cream,
        textShadow: TEXT_SHADOW,
        opacity,
      }}
    >
      <div style={{ fontSize: 36, lineHeight: "46px", fontWeight: 700 }}>{title}</div>
      <div style={{ display: "flex", alignItems: "center", gap: 14, fontSize: 30, lineHeight: "40px" }}>
        {segs.map((s, i) => (
          <React.Fragment key={i}>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 10,
                opacity: interpolate(frame, [i * step, i * step + 8], [0.25, 1], CLAMP),
              }}
            >
              <div style={{ width: 86, height: 6, borderRadius: 3, backgroundColor: s.color }} />
              <span>{s.label}</span>
            </div>
          </React.Fragment>
        ))}
      </div>
    </div>
  );
};

const stationColor = (name: string) => {
  const st = TL.stations.find((s) => s.name === name);
  const kind = st ? (STATION_SIGNAL[st.id] ?? "electric") : "electric";
  return { st, colors: kind === "light" ? [C.light, C.light] : kind === "both" ? [C.electric, C.light] : [C.electric, C.electric] };
};

const StationNames: React.FC<Props> = ({ overlay, shotId, duration }) => {
  const frame = useCurrentFrame();
  const film = toFrame(overlay.t) + frame + 1;
  const names = overlay.text.split(" · ").map((s) => s.trim());
  const n = names.length;
  const step = (duration * 0.62) / n;
  const out = interpolate(frame, [duration - 8, duration], [1, 0], CLAMP);

  return (
    <div style={{ position: "absolute", inset: 0, fontFamily: FONT_FAMILY, opacity: out }}>
      {names.map((name, i) => {
        const { st, colors } = stationColor(name);
        const a = anchorAt(shotId, [name, st?.id], film);
        const p = a && a.visible ? a : pathTraceDefault(i, n);
        const x = Math.max(SAFE.left + 80, Math.min(SAFE.right - 80, p.x));
        const y = Math.max(SAFE.top + 70, Math.min(SAFE.bottom - 120, p.y));
        const k = interpolate(frame, [i * step, i * step + 8], [0, 1], CLAMP);
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: x - 110,
              width: 220,
              top: y - 62,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              opacity: k,
              translate: `0px ${interpolate(frame, [i * step, i * step + 8], [10, 0], CLAMP)}px`,
            }}
          >
            <div
              style={{
                fontSize: 36,
                lineHeight: "44px",
                fontWeight: 700,
                color: C.cream,
                textShadow: TEXT_SHADOW,
                whiteSpace: "nowrap",
              }}
            >
              {name}
            </div>
            {/* 站点：左半 / 右半各一种信号色 */}
            <div
              style={{
                width: 16,
                height: 16,
                marginTop: 10,
                borderRadius: 8,
                background: `linear-gradient(90deg, ${colors[0]} 50%, ${colors[1]} 50%)`,
                outline: `3px solid ${rgba(C.ink, 0.8)}`,
              }}
            />
          </div>
        );
      })}
    </div>
  );
};

export const PathTrace: React.FC<Props> = (props) => {
  // 文案里有「：」和「（）」的是路线 + 图例；否则当作一串站名
  if (props.overlay.text.includes("：") && props.overlay.text.includes("（")) {
    return <Legend {...props} />;
  }
  return <StationNames {...props} />;
};
