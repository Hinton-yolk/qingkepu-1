import {AbsoluteFill, Audio, Sequence, staticFile} from 'remotion';
import {Captions} from './Captions';
import {C} from './lib/theme';
import {FPS, SEQ_END, SEQ_START, T} from './lib/time';
import {SeqA} from './seq/SeqA';
import {SeqB} from './seq/SeqB';
import {SeqC} from './seq/SeqC';
import {SeqD} from './seq/SeqD';
import {SeqE} from './seq/SeqE';
import audio from './audio.json';

// 每段在自己的 <Sequence> 里，段内用全片帧号（from 传进去），旁白 cue 直接用全片时间
const SEQS: [string, React.FC<{from: number}>][] = [
  ['A', SeqA],
  ['B', SeqB],
  ['C', SeqC],
  ['D', SeqD],
  ['E', SeqE],
];
const OVERLAP = 12; // 相邻两段重叠的帧数，给转场用（后一段在上层）

export const Film: React.FC = () => (
  <AbsoluteFill style={{background: C.bg}}>
    {SEQS.map(([k, Comp]) => {
      const a = SEQ_START[k];
      const b = SEQ_END[k] + (k === 'E' ? 0 : OVERLAP);
      return (
        <Sequence key={k} from={a} durationInFrames={b - a} name={`Seq ${k}`}>
          <Comp from={a} />
        </Sequence>
      );
    })}
    <Captions />
    {/* 旁白 */}
    {T.lines.map((l) => (
      <Sequence key={l.id} from={Math.round(l.start * FPS)} durationInFrames={Math.ceil((l.end - l.start) * FPS) + 6} name={`VO ${l.id}`}>
        <Audio src={staticFile(l.file)} />
      </Sequence>
    ))}
    {/* 音乐和音效：music.py 合成好的两条整轨（和全片同长） */}
    {audio.music && <Audio src={staticFile('audio/music.wav')} volume={audio.musicGain} />}
    {audio.sfx && <Audio src={staticFile('audio/sfx.wav')} volume={audio.sfxGain} />}
  </AbsoluteFill>
);
