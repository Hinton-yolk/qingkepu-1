import {Composition} from 'remotion';
import {Film} from './Film';
import {FPS, TOTAL} from './lib/core';

export const RemotionRoot: React.FC = () => (
  <Composition id="EP01DirectorLocked60" component={Film} durationInFrames={TOTAL} fps={FPS} width={1080} height={1920} />
);
