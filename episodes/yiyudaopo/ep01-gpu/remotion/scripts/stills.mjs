// 抽帧看图：node scripts/stills.mjs <输出目录> <scale> 秒1 秒2 ...（只打包一次，比 remotion still 快）
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';
import path from 'node:path';
const [out, scale, ...secs] = process.argv.slice(2);
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts')});
const composition = await selectComposition({serveUrl, id: 'EP01Pilot'});
for (const s of secs) {
  const frame = Math.min(composition.durationInFrames - 1, Math.round(parseFloat(s) * 30));
  const output = path.join(out, `t${parseFloat(s).toFixed(2).padStart(6, '0')}.png`);
  await renderStill({serveUrl, composition, frame, output, scale: parseFloat(scale), chromiumOptions: {gl: 'swangle'}});
  console.log(output);
}
