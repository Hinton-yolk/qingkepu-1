// 全片合成。分层（从下到上）：
//   a. Blender 图像序列（没有就是占位卡）  b. 科学叠加层  c. 五站进度条  d. 字幕  e. 片尾卡（全屏，盖住以上各层）
// 所有时间来自 timeline.json；这里没有任何写死的镜头时间或文案。
import React from "react";
import { AbsoluteFill, Sequence } from "remotion";
import { BlenderPlate } from "./layers/BlenderPlate";
import { Guides } from "./layers/Guides";
import { ShotOverlays } from "./layers/ShotOverlays";
import { StationBar } from "./layers/StationBar";
import { Subtitles } from "./layers/Subtitles";
import { EndCard } from "./overlays/EndCard";
import { C } from "./theme";
import { durFrames, shotFrames, TL, toFrame } from "./timeline";

export type JourneyProps = {
  /** 调试：显示安全区、五站条、字幕位置的参考线 */
  showGuides: boolean;
};

export const Journey: React.FC<JourneyProps> = ({ showGuides }) => {
  return (
    <AbsoluteFill style={{ backgroundColor: C.ink }}>
      {/* a + b：逐镜头 */}
      {TL.shots.map((shot) => {
        const { from, duration } = shotFrames(shot);
        return (
          <Sequence key={shot.id} name={`${shot.id} ${shot.name}`} from={from} durationInFrames={duration}>
            <BlenderPlate shot={shot} />
            <ShotOverlays shot={shot} />
          </Sequence>
        );
      })}

      {/* c：五站进度条 */}
      <StationBar />

      {/* d：字幕 */}
      <Subtitles />

      {/* e：片尾卡 */}
      {TL.shots.flatMap((shot) =>
        shot.overlays
          .filter((o) => o.type === "end_card")
          .map((o, i) => {
            const duration = durFrames(o.t, o.dur);
            return (
              <Sequence key={`${shot.id}-end-${i}`} name="片尾卡" from={toFrame(o.t)} durationInFrames={duration}>
                <EndCard overlay={o} duration={duration} />
              </Sequence>
            );
          }),
      )}

      {showGuides ? <Guides /> : null}
    </AbsoluteFill>
  );
};
