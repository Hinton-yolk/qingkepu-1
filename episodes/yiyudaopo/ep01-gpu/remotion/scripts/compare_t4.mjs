import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';
import path from 'node:path';
const O = process.argv[2];
const serveUrl = await bundle({entryPoint: path.resolve('src60/index.ts'), publicDir: path.resolve('public')});
for (const [id, fr, name] of [['T4FinalMatch', 179, 't4_f179'], ['EP01DirectorLocked60', 1529, 'film_f1529'], ['EP01DirectorLocked60', 1530, 'film_f1530'], ['T4FinalMatch', 0, 'f000'], ['T4FinalMatch', 90, 'f090'], ['T4FinalMatch', 135, 'f135'], ['T4FinalMatch', 150, 'f150']]) {
  const composition = await selectComposition({serveUrl, id});
  await renderStill({serveUrl, composition, frame: fr, output: path.join(O, /^f\d/.test(name) ? 'frames' : 'compare', name + '.png'), chromiumOptions: {gl: 'swangle'}});
}
