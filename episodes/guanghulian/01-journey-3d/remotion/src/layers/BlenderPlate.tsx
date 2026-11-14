// 底层：Blender 图像序列。某一帧不存在 → 用该镜头已有的最近一帧；整个镜头都没有 → 占位卡。
import React from "react";
import { AbsoluteFill, Img, staticFile, useCurrentFrame } from "remotion";
import { nearestFrameFile } from "../lib/manifest";
import { C } from "../theme";
import { Shot, toFrame } from "../timeline";
import { PlaceholderCard } from "./PlaceholderCard";

export const BlenderPlate: React.FC<{ shot: Shot }> = ({ shot }) => {
  const local = useCurrentFrame(); // 镜头内的帧号（从 0 起）
  const film = toFrame(shot.start) + local + 1; // Blender 的全片帧号（从 1 起）

  // 没有 Blender 画面的镜头（片尾卡）：只铺深色底
  if (!shot.blender) {
    return <AbsoluteFill style={{ backgroundColor: C.ink }} />;
  }

  const file = nearestFrameFile(shot.id, film);
  if (!file) {
    return <PlaceholderCard shot={shot} />;
  }

  return (
    <AbsoluteFill style={{ backgroundColor: C.ink }}>
      <Img
        src={staticFile(file)}
        style={{ width: "100%", height: "100%", objectFit: "cover" }}
      />
    </AbsoluteFill>
  );
};
