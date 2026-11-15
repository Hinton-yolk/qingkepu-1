import React from "react";
import { Composition } from "remotion";
import { Journey } from "./Journey";
import { FPS, TL, TOTAL_FRAMES } from "./timeline";

// 规格和总帧数都从 timeline.json 算：最后一个镜头的结束时间 × fps。
export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="Journey"
      component={Journey}
      durationInFrames={TOTAL_FRAMES}
      fps={FPS}
      width={TL.meta.width}
      height={TL.meta.height}
      defaultProps={{ showGuides: false }}
    />
  );
};
