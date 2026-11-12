// 科学叠加层：把一个镜头的 overlays 按 type 分给各个组件。时间全部来自 timeline.json。
//   waveform → Waveform      timing_diagram → TimingDiagram     gauge → Gauge
//   label / term / scale / alert → AnchoredLabel               note → NoteStack
//   hook_title → HookTitle   path_trace → PathTrace            end_card → 在 Journey 里单独放最上层
import React from "react";
import { Sequence } from "remotion";
import { hasFrames } from "../lib/manifest";
import { AnchoredLabel } from "../overlays/AnchoredLabel";
import { Gauge } from "../overlays/Gauge";
import { HookTitle } from "../overlays/HookTitle";
import { NoteStack } from "../overlays/NoteStack";
import { PathTrace } from "../overlays/PathTrace";
import { TimingDiagram } from "../overlays/TimingDiagram";
import { Waveform } from "../overlays/Waveform";
import {
  DEFAULT_SLOTS,
  PANEL_HEIGHT,
  panelRect,
  SCALE_ONLY_WHEN_PLACEHOLDER,
  SHOT_SLOTS,
  WAVEFORM_VARIANT,
} from "../shotConfig";
import { PANEL_BOTTOM } from "../theme";
import { durFrames, Overlay, Shot, toFrame } from "../timeline";

const ANCHORED = ["label", "term", "scale", "alert"];
const PANELS = ["waveform", "timing_diagram", "gauge"];

const overlaps = (a: Overlay, b: Overlay) => a.t < b.t + b.dur && b.t < a.t + a.dur;

const panelHeight = (shot: Shot, o: Overlay) => {
  if (o.type === "waveform") return PANEL_HEIGHT[WAVEFORM_VARIANT[shot.id] ?? "degrade"];
  if (o.type === "timing_diagram") return PANEL_HEIGHT.timing_diagram;
  return PANEL_HEIGHT.gauge;
};

export const ShotOverlays: React.FC<{ shot: Shot }> = ({ shot }) => {
  const shotStart = toFrame(shot.start);
  const overlays = shot.overlays;
  const panels = overlays.filter((o) => PANELS.includes(o.type));
  const waveforms = overlays.filter((o) => o.type === "waveform");

  // alert 落在某条波形的时间内 → 交给那条波形画在判决门限旁（不再单独贴标签）
  const claimed = new Map<Overlay, Overlay>(); // alert → waveform
  for (const a of overlays.filter((o) => o.type === "alert")) {
    const wf = waveforms.find((w) => a.t >= w.t - 1e-6 && a.t + a.dur <= w.t + w.dur + 1e-6);
    if (wf && (WAVEFORM_VARIANT[shot.id] ?? "degrade") === "degrade") claimed.set(a, wf);
  }

  const placeholder = !hasFrames(shot.id);
  const anchored = overlays.filter(
    (o) =>
      ANCHORED.includes(o.type) &&
      !claimed.has(o) &&
      !(o.type === "scale" && SCALE_ONLY_WHEN_PLACEHOLDER && !placeholder),
  );
  const slots = SHOT_SLOTS[shot.id] ?? DEFAULT_SLOTS;
  const notes = overlays.filter((o) => o.type === "note");

  const seq = (o: Overlay, i: number, node: (duration: number) => React.ReactNode) => {
    const duration = durFrames(o.t, o.dur);
    return (
      <Sequence
        key={`${o.type}-${i}`}
        name={`${o.type}｜${o.text.slice(0, 14)}`}
        from={toFrame(o.t) - shotStart}
        durationInFrames={duration}
      >
        {node(duration)}
      </Sequence>
    );
  };

  return (
    <>
      {overlays.map((o, i) => {
        switch (o.type) {
          case "waveform": {
            const alert = [...claimed.entries()].find(([, wf]) => wf === o)?.[0] ?? null;
            return seq(o, i, (duration) => (
              <Waveform
                overlay={o}
                duration={duration}
                variant={WAVEFORM_VARIANT[shot.id] ?? "degrade"}
                alert={alert}
              />
            ));
          }
          case "timing_diagram":
            return seq(o, i, (duration) => <TimingDiagram overlay={o} duration={duration} />);
          case "gauge":
            return seq(o, i, (duration) => <Gauge overlay={o} duration={duration} />);
          case "hook_title":
            return seq(o, i, (duration) => <HookTitle overlay={o} duration={duration} />);
          case "path_trace":
            return seq(o, i, (duration) => (
              <PathTrace overlay={o} shotId={shot.id} duration={duration} />
            ));
          default:
            return null;
        }
      })}

      {anchored.map((o, k) => {
        // 同时在场的图表面板里最高的那个：标签不能压到它
        const tops = panels.filter((p) => overlaps(p, o)).map((p) => panelRect(panelHeight(shot, p)).y);
        const bottomLimit = (tops.length > 0 ? Math.min(...tops) : PANEL_BOTTOM) - 6;
        return seq(o, 100 + k, (duration) => (
          <AnchoredLabel
            overlay={o}
            shotId={shot.id}
            duration={duration}
            slot={slots[k % slots.length]}
            bottomLimit={bottomLimit}
          />
        ));
      })}

      {notes.length > 0 ? <NoteStack shot={shot} notes={notes} /> : null}
    </>
  );
};
