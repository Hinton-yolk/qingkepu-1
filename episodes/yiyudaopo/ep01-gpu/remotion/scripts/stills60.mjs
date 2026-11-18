// 抽帧看图（导演锁定版 60 秒）：node scripts/stills60.mjs <输出目录> <scale> 秒1 秒2 ...（只打包一次）
// 再生成一张接触表 sheet.jpg（每行 6 张，带时间）
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';
import {execFileSync} from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
const [out, scale, ...secs] = process.argv.slice(2);
fs.mkdirSync(out, {recursive: true});
const serveUrl = await bundle({entryPoint: path.resolve('src60/index.ts'), publicDir: path.resolve('public')});
const composition = await selectComposition({serveUrl, id: 'EP01DirectorLocked60'});
const files = [];
for (const s of secs) {
  const frame = Math.min(composition.durationInFrames - 1, Math.round(parseFloat(s) * 30));
  const output = path.join(out, `f${String(frame).padStart(4, '0')}.png`);
  await renderStill({serveUrl, composition, frame, output, scale: parseFloat(scale), chromiumOptions: {gl: 'swangle'}});
  files.push([output, frame]);
}
execFileSync('python3', ['-c', `
import sys
from PIL import Image, ImageDraw
fs = sys.argv[2:]; out = sys.argv[1]
ims = [Image.open(f) for f in fs]; w, h = ims[0].size; cols = min(6, len(ims)); rows = (len(ims) + cols - 1) // cols
S = Image.new('RGB', (cols * (w + 6), rows * (h + 30)), (40, 40, 40)); d = ImageDraw.Draw(S)
for i, (im, f) in enumerate(zip(ims, fs)):
    x, y = (i % cols) * (w + 6), (i // cols) * (h + 30)
    S.paste(im, (x, y + 26)); fr = int(f.split('/f')[-1][:4]); d.text((x + 4, y + 6), f'{fr/30:.2f}s  f{fr}', fill=(255, 255, 255))
S.save(out, quality=85)
`, path.join(out, 'sheet.jpg'), ...files.map((f) => f[0])]);
console.log('sheet', path.join(out, 'sheet.jpg'));
