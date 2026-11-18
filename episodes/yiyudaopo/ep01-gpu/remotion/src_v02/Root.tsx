import {Composition} from 'remotion';
import {Film} from './Film';
import {FPS, TOTAL_FRAMES} from './lib/time';

export const RemotionRoot: React.FC = () => (
  <Composition id="EP01Pilot" component={Film} durationInFrames={TOTAL_FRAMES} fps={FPS} width={1080} height={1920} />
);
