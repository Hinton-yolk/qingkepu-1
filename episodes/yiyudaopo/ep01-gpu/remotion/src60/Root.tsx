import {Composition} from 'remotion';
import {Film} from './Film';
import {FPS, TOTAL} from './lib/core';
import {T2Test} from './tests/T2';
import {T4Test} from './tests/T4';
import {T4v2} from './tests/T4v2';

export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="EP01DirectorLocked60" component={Film} durationInFrames={TOTAL} fps={FPS} width={1080} height={1920} />
    {/* 转场重建测试（导演 11-18 第二轮）：各 6 秒 180 帧 */}
    <Composition id="T2Test" component={T2Test} durationInFrames={180} fps={FPS} width={1080} height={1920} />
    <Composition id="T4Test" component={T4Test} durationInFrames={180} fps={FPS} width={1080} height={1920} />
    <Composition id="T4Reconstruction" component={T4v2} durationInFrames={180} fps={FPS} width={1080} height={1920} />
  </>
);
