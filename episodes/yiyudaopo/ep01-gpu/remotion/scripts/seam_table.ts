// T4 第 179 帧（= 全片第 1529 帧）和 GPU 镜头第一帧（全片第 1530 帧）里 20 个格子的屏幕位置、边长、颜色（从源码算）
import {DIE, dieQuad, dieToScreen, SLOT, slotXY} from '../src60/lib/plan';
import {quadScale} from '../src60/lib/homography';
import {lockedTile} from '../src60/layers/Die';
const row = (f: number) => {
  const t = f / 30, q = dieQuad(t, f), k = quadScale(q, DIE.w);
  return Array.from({length: 20}, (_, i) => { const [lx, ly] = slotXY(i); const [x, y] = dieToScreen(t, f, lx, ly); const L = lockedTile(i, t); return {i, x, y, s: L.s * k, kind: L.kind, lit: L.lit}; });
};
const a = row(1529), b = row(1530);
console.log('| 格（行, 列） | 颜色 | T4 f179 中心 (x, y) / 边长 px | GPU f1530 中心 (x, y) / 边长 px | 位移 px |\n|---|---|---|---|---|');
a.forEach((p, i) => { const q = b[i]; console.log(`| (${Math.floor(i / SLOT.cols)}, ${i % SLOT.cols}) | ${p.kind === 'game' ? '琥珀' : '冷白'} | (${p.x.toFixed(1)}, ${p.y.toFixed(1)}) / ${p.s.toFixed(1)} | (${q.x.toFixed(1)}, ${q.y.toFixed(1)}) / ${q.s.toFixed(1)} | ${Math.hypot(q.x - p.x, q.y - p.y).toFixed(2)} |`); });
const qa = dieQuad(1529 / 30, 1529), qb = dieQuad(1530 / 30, 1530);
console.log(`\n芯片四角 f1529：${qa.map((p) => `(${p[0].toFixed(1)}, ${p[1].toFixed(1)})`).join(' ')}\n芯片四角 f1530：${qb.map((p) => `(${p[0].toFixed(1)}, ${p[1].toFixed(1)})`).join(' ')}`);
