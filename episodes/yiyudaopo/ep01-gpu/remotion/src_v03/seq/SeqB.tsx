import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {C, FONT} from '../lib/theme';
import {buildScene, Cam, project, Proj, shadeColor} from '../lib/terrain';
import {cue, ease, easeIO, lerp, prog, sec} from '../lib/time';
import {Drift, Note} from '../lib/ui';
import {dieRect, MACRO_BACK} from './SeqA';

// v03 B 段（约 11 秒）：芯片的方框长成游戏画面 → 一块要算光照 → 每一块都要算（同一条规则）→ 一起算（一起亮）
// → 这些分块抬起来，变成一批相同的「计算任务」（D 段要用的那批格子）。
// 着色仍是 terrain.ts 里真实的漫反射（亮度 ∝ n·l），只是不再显示数值。
const TRIS = buildScene();
export const VP = {x: 20, y: 190, w: 1040, h: 1170};
export const COLS = 4, ROWS = 5, TILES = COLS * ROWS;
/** B5 结束时这批任务格子在屏幕上的位置（D 段从这里接） */
export const BATCH = {x0: 160, y0: 520, s: 150, gap: 40};
export const batchXY = (i: number) => ({x: BATCH.x0 + (i % COLS) * (BATCH.s + BATCH.gap), y: BATCH.y0 + Math.floor(i / COLS) * (BATCH.s + BATCH.gap) * 0.62});

const camAt = (f: number): Cam => {
  const t = (f - cue('B1')) / 30;
  return {az: 0.35 + 0.07 * t, el: 0.46 + 0.006 * t, dist: 9.6 - 0.05 * t, fov: 0.82, target: [0.2, 0.55, 0]};
};
const cen = (p: Proj) => [(p.pts[0][0] + p.pts[1][0] + p.pts[2][0]) / 3, (p.pts[0][1] + p.pts[1][1] + p.pts[2][1]) / 3];
const tileOf = (p: Proj) => {
  const [x, y] = cen(p);
  return Math.max(0, Math.min(ROWS - 1, Math.floor((y / VP.h) * ROWS))) * COLS + Math.max(0, Math.min(COLS - 1, Math.floor((x / VP.w) * COLS)));
};
const FIRST = 2 * COLS + 1;                       // 第一个被点亮的分块（画面中间、山脚）
const ring = (i: number) => Math.hypot((i % COLS) - (FIRST % COLS), Math.floor(i / COLS) - Math.floor(FIRST / COLS));

export const SeqB: React.FC<{from: number}> = ({from}) => {
  const f = useCurrentFrame() + from;
  const b2 = cue('B2'), b3 = cue('B3'), b4 = cue('B4'), b5 = cue('B5');
  // 芯片方框 → 视口
  const r0 = dieRect(MACRO_BACK + (from - (cue('A2') - 3)));
  const m = prog(f, from, 14, easeIO);
  const rect = {x: lerp(r0.x, VP.x, m), y: lerp(r0.y, VP.y, m), w: lerp(r0.w, VP.w, m), h: lerp(r0.h, VP.h, m)};
  // 一块 → 每一块 → 一起算
  const dim = prog(f, b2, 8);                                     // 先压暗：都还没算
  const one = prog(f, b2 + sec(0.4), 8);                          // 第一块算好
  const spread = (i: number) => prog(f, b2 + sec(1.3) + ring(i) * 3, 8);   // 每一块都要算：从第一块往外扩
  const stamp = (i: number) => prog(f, b3 + sec(0.2) + ring(i) * 1.5, 6);  // 同一条规则印到每一块
  const ALL = b4 + sec(1.25);                                     // 「可以一起算」
  const allLit = prog(f, ALL, 5, ease);
  const flash = prog(f, ALL, 2) * (1 - prog(f, ALL + 3, 10));
  const tileLit = (i: number) => (i === FIRST ? one : allLit);
  const lit = (p: Proj) => (dim < 1 ? 1 : tileLit(tileOf(p)));
  // B5：分块抬起来变成一批任务格子，小岛退暗
  const lift = prog(f, b5 + sec(0.1), 20, easeIO);
  const P = project(TRIS, camAt(f), VP.w, VP.h);
  const tw = VP.w / COLS, th = VP.h / ROWS;

  return (
    <AbsoluteFill style={{background: `rgba(12,13,16,${prog(f, from + 8, 10)})`}}>
      <Drift from={from} amp={0.9} push={0.0015}>
        <div style={{position: 'absolute', left: rect.x, top: rect.y, width: rect.w, height: rect.h, borderRadius: lerp(6, 30, m), overflow: 'hidden',
          boxShadow: `0 0 0 3px ${m < 0.98 ? C.ai : C.line}`, opacity: 1 - lift * 0.82}}>
          <div style={{transform: `scale(${rect.w / VP.w}, ${rect.h / VP.h})`, transformOrigin: '0 0', opacity: lerp(0.55, 1, m)}}>
            <svg width={VP.w} height={VP.h} style={{position: 'absolute', left: 0, top: 0}}>
              <defs>
                <linearGradient id="sky3" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0" stopColor="#8DB3C9" /><stop offset="0.55" stopColor="#D9CDB0" /><stop offset="1" stopColor="#E9D3A5" />
                </linearGradient>
              </defs>
              <rect width={VP.w} height={VP.h} fill="url(#sky3)" opacity={1 - dim * 0.55 * (1 - allLit)} />
              <circle cx={VP.w * 0.84} cy={VP.h * 0.09} r={42} fill={C.sun} />
              {P.map((p) => {
                if (!p.facing && p.tri.kind !== 'water') return null;
                const L = lit(p);
                const on = shadeColor(p.tri.base, p.shade), off = shadeColor(p.tri.base, p.shade, 0.3);
                const d = `M${p.pts[0][0]},${p.pts[0][1]}L${p.pts[1][0]},${p.pts[1][1]}L${p.pts[2][0]},${p.pts[2][1]}Z`;
                return (
                  <g key={p.tri.id}>
                    <path d={d} fill={L >= 1 ? on : off} stroke={L >= 1 ? on : off} strokeWidth={0.8} />
                    {L > 0 && L < 1 && <path d={d} fill={on} opacity={L} />}
                  </g>
                );
              })}
              {flash > 0 && <rect width={VP.w} height={VP.h} fill="#FFF3D6" opacity={0.3 * flash} />}
              {/* 分块：第一块先亮起一个框，然后每一块都出现框（都要算），框角上印同一条规则（一个小太阳） */}
              {Array.from({length: TILES}, (_, i) => {
                const c = i % COLS, r = Math.floor(i / COLS);
                const show = i === FIRST ? one : spread(i);
                const hot = i === FIRST ? one * (1 - spread(0) * 0.5) : 0;
                return (
                  <g key={i} opacity={show * (1 - lift)}>
                    <rect x={c * tw + 5} y={r * th + 5} width={tw - 10} height={th - 10} rx={14} fill="none"
                      stroke={hot > 0.3 || allLit > 0.5 ? C.game : 'rgba(255,255,255,0.85)'} strokeWidth={hot > 0.3 ? 8 : 4} />
                    <g opacity={stamp(i)} transform={`translate(${c * tw + 38}, ${r * th + 38}) scale(${lerp(1.6, 1, stamp(i))})`}>
                      <circle r={17} fill={C.sun} stroke="#6B5320" strokeWidth={3} />
                      {[0, 1, 2, 3, 4, 5, 6, 7].map((k) => (
                        <line key={k} x1={Math.cos(k * 0.785) * 22} y1={Math.sin(k * 0.785) * 22} x2={Math.cos(k * 0.785) * 30} y2={Math.sin(k * 0.785) * 30} stroke={C.sun} strokeWidth={4} />
                      ))}
                    </g>
                  </g>
                );
              })}
            </svg>
          </div>
        </div>
        {/* B5：分块抬起来，变成一批同样的计算任务 */}
        {lift > 0 && Array.from({length: TILES}, (_, i) => {
          const c = i % COLS, r = Math.floor(i / COLS);
          const sx = VP.x + c * tw + tw / 2, sy = VP.y + r * th + th / 2;
          const tgt = batchXY(i);
          const k = prog(f, b5 + sec(0.1) + ring(i) * 1.2, 18, easeIO);
          const w = lerp(tw - 10, BATCH.s * 0.62, k), h = lerp(th - 10, BATCH.s * 0.62, k);
          return (
            <div key={i} style={{position: 'absolute', left: lerp(sx, tgt.x, k) - w / 2, top: lerp(sy, tgt.y, k) - h / 2, width: w, height: h, borderRadius: 14,
              border: `4px solid ${C.game}`, background: `rgba(240,160,64,${0.12 + 0.3 * k})`, opacity: lift,
              display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: FONT.num, fontWeight: 700, fontSize: 40, color: C.ink}}>
              <span style={{opacity: k}}>×+</span>
            </div>
          );
        })}
      </Drift>
      <Note top={1490} opacity={prog(f, b3, 10) * (1 - lift) * 0.9}>示意：每块按同一公式算亮度（漫反射）</Note>
    </AbsoluteFill>
  );
};
