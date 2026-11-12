// 声音（可选）：public/audio 里有文件才会出现，没有就整层为空。本工程不生成配音，只负责摆放。
//   narration.*      整条旁白，从 0 秒起
//   <旁白 id>.*      逐句旁白（n01.wav …），各自从 narration[].start 起；有整条旁白时不用逐句的
//   music.*          音乐，从 0 秒起，音量压到人声下方约 12 dB
import { Audio } from "@remotion/media";
import React from "react";
import { Sequence, staticFile } from "remotion";
import { MANIFEST } from "../lib/manifest";
import { TL, toFrame } from "../timeline";

/** 音乐相对人声的音量：−12 dB ≈ 0.25（仓库规则：音乐在人声下方约 12 dB） */
const MUSIC_VOLUME = 0.25;

export const AudioTracks: React.FC = () => {
  const { narration, music, lines } = MANIFEST.audio;
  return (
    <>
      {music ? <Audio src={staticFile(music)} volume={MUSIC_VOLUME} /> : null}
      {narration ? (
        <Audio src={staticFile(narration)} />
      ) : (
        TL.narration
          .filter((n) => lines[n.id])
          .map((n) => (
            <Sequence
              key={n.id}
              name={`旁白 ${n.id}`}
              from={toFrame(n.start)}
              layout="none"
            >
              <Audio src={staticFile(lines[n.id])} />
            </Sequence>
          ))
      )}
    </>
  );
};
