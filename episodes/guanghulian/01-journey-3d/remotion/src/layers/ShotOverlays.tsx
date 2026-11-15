// 科学叠加层：把一个镜头的 overlays 按 type 分给各个组件。时间全部来自 timeline.json。
//   waveform → Waveform      timing_diagram → TimingDiagram     gauge → Gauge
//   label / term / scale / alert → AnchoredLabels              note → NoteStack
//   hook_title → HookTitle   path_trace → PathTrace            end_card → 在 Journey 里单独放最上层
// 叠放顺序（从下到上）：路线 → 开头大字 → 图表面板 → 贴物体的标签 → 角注。
// 谁让谁（位置怎么算）在 lib/shotLayout。
import React from "react";
import { Sequence } from "remotion";
import { panelBottomFor } from "../lib/shotLayout";
import { AnchoredLabels } from "../overlays/AnchoredLabel";
import { Gauge } from "../overlays/Gauge";
import { HookTitle } from "../overlays/HookTitle";
import { NoteStack } from "../overlays/NoteStack";
import { PanelBottom } from "../overlays/Panel";
import { PathTrace } from "../overlays/PathTrace";
import { TimingDiagram } from "../overlays/TimingDiagram";
import { Waveform } from "../overlays/Waveform";
import { WAVEFORM_VARIANT } from "../shotConfig";
import { durFrames, Overlay, Shot, toFrame } from "../timeline";

const LAYER_ORDER = [
  "path_trace",
  "hook_title",
  "waveform",
  "timing_diagram",
  "gauge",
];

export const ShotOverlays: React.FC<{ shot: Shot }> = ({ shot }) => {
  const shotStart = toFrame(shot.start);
  const overlays = shot.overlays;
  const waveforms = overlays.filter((o) => o.type === "waveform");
  const variant = WAVEFORM_VARIANT[shot.id] ?? "degrade";

  // alert 落在某条波形的时间内 → 交给那条波形画在判决门限旁（不再单独贴标签；lib/shotLayout 里同样跳过）
  const claimed = new Map<Overlay, Overlay>(); // alert → waveform
  for (const a of overlays.filter((o) => o.type === "alert")) {
    const wf = waveforms.find(
      (w) => a.t >= w.t - 1e-6 && a.t + a.dur <= w.t + w.dur + 1e-6,
    );
    if (wf && variant === "degrade") claimed.set(a, wf);
  }

  const notes = overlays.filter((o) => o.type === "note");

  const seq = (
    o: Overlay,
    i: number,
    node: (duration: number) => React.ReactNode,
  ) => {
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

  // 图表面板：下沿随同时在场的角注往上让
  const panel = (o: Overlay, node: React.ReactNode) => (
    <PanelBottom.Provider value={panelBottomFor(shot, o)}>
      {node}
    </PanelBottom.Provider>
  );

  const layered = overlays
    .map((o, i) => ({ o, i }))
    .filter(({ o }) => LAYER_ORDER.includes(o.type))
    .sort(
      (a, b) =>
        LAYER_ORDER.indexOf(a.o.type) - LAYER_ORDER.indexOf(b.o.type) ||
        a.i - b.i,
    );

  return (
    <>
      {layered.map(({ o, i }) => {
        switch (o.type) {
          case "path_trace":
            return seq(o, i, (duration) => (
              <PathTrace overlay={o} shot={shot} duration={duration} />
            ));
          case "hook_title":
            return seq(o, i, (duration) => (
              <HookTitle overlay={o} duration={duration} />
            ));
          case "waveform": {
            const alert =
              [...claimed.entries()].find(([, wf]) => wf === o)?.[0] ?? null;
            return seq(o, i, (duration) =>
              panel(
                o,
                <Waveform
                  overlay={o}
                  duration={duration}
                  variant={variant}
                  alert={alert}
                />,
              ),
            );
          }
          case "timing_diagram":
            return seq(o, i, (duration) =>
              panel(o, <TimingDiagram overlay={o} duration={duration} />),
            );
          case "gauge":
            return seq(o, i, (duration) =>
              panel(o, <Gauge overlay={o} duration={duration} />),
            );
          default:
            return null;
        }
      })}

      <AnchoredLabels shot={shot} />

      {notes.length > 0 ? <NoteStack shot={shot} notes={notes} /> : null}
    </>
  );
};
