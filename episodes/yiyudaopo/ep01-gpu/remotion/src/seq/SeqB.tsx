import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {C, FONT} from '../lib/theme';
import {area, buildScene, Cam, LIGHT, project, Proj, shadeColor} from '../lib/terrain';
import {cue, ease, easeIO, lerp, prog, sec} from '../lib/time';
import {Drift, Kicker, Note} from '../lib/ui';

// v02 B 段：先给效果、后给细节。
// 小岛 → 很多块同时在算（分块各自闪）→ 三块：数不同、规则相同 → 排队一块一块 vs 一起算 → GPU 擅长大量并行任务。
// 着色仍是 terrain.ts 里真实的漫反射（亮度 ∝ n·l），只是向量不再上屏。
const TRIS = buildScene();
export const VP = {x: 30, y: 272, w: 1020, h: 1040};
const COLS = 4, ROWS = 5, TILES = COLS * ROWS;
const r2 = (x: number) => Math.round(x * 100) / 100;

export const camAt = (f: number): Cam => {
  const t = (f - cue('B1')) / 30;
  return {az: 0.3 + 0.045 * t, el: 0.47, dist: 10.6, fov: 0.8, target: [0.2, 0.6, 0]};
};
const cen = (p: Proj) => [(p.pts[0][0] + p.pts[1][0] + p.pts[2][0]) / 3, (p.pts[0][1] + p.pts[1][1] + p.pts[2][1]) / 3];
const tileOf = (p: Proj) => {
  const [x, y] = cen(p);
  return Math.max(0, Math.min(ROWS - 1, Math.floor((y / VP.h) * ROWS))) * COLS + Math.max(0, Math.min(COLS - 1, Math.floor((x / VP.w) * COLS)));
};
// 每块分块一个固定的「相位」，让它们各自闪（很多地方同时在算，不是一个接一个）
const phase = (i: number) => ((i * 7919) % 97) / 97;

/** 三块示例三角形：在不同分块里、正对相机、亮度差得开 */
const PICKS = (() => {
  const P = project(TRIS, camAt(cue('B3')), VP.w, VP.h).filter((p) => p.facing && p.tri.kind === 'land' && area(p.pts) > 900);
  const out: Proj[] = [];
  for (const target of [0.88, 0.5, 0.68]) {
    let best: Proj | null = null, d = 9;
    for (const p of P) {
      const [x, y] = cen(p);
      if (x < 140 || x > VP.w - 140 || y < 260 || y > VP.h - 160) continue;
      if (out.some((q) => tileOf(q) === tileOf(p) || Math.hypot(cen(q)[0] - x, cen(q)[1] - y) < 260)) continue;
      const dd = Math.abs(p.shade - target) - area(p.pts) / 1e5;
      if (dd < d) { d = dd; best = p; }
    }
    if (best) out.push(best);
  }
  return out.map((p) => p.tri.id);
})();

const GameView: React.FC<{f: number; lit: (p: Proj) => number; flash: (i: number) => number; focus: number}> = ({f, lit, flash, focus}) => {
  const P = project(TRIS, camAt(f), VP.w, VP.h);
  return (
    <svg width={VP.w} height={VP.h} style={{position: 'absolute', left: 0, top: 0}}>
      <defs>
        <linearGradient id="sky2" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#8DB3C9" /><stop offset="0.55" stopColor="#D9CDB0" /><stop offset="1" stopColor="#E9D3A5" />
        </linearGradient>
      </defs>
      <rect width={VP.w} height={VP.h} fill="url(#sky2)" />
      <circle cx={VP.w * 0.84} cy={VP.h * 0.1} r={40} fill={C.sun} opacity={0.95} />
      {P.map((p) => {
        if (!p.facing && p.tri.kind !== 'water') return null;
        const L = lit(p), ti = tileOf(p);
        const k = PICKS.includes(p.tri.id) ? 1 : 1 - focus * 0.45;
        const on = shadeColor(p.tri.base, p.shade, k), off = shadeColor(p.tri.base, p.shade, 0.3 * k);
        const fl = flash(ti);
        const d = `M${p.pts[0][0]},${p.pts[0][1]}L${p.pts[1][0]},${p.pts[1][1]}L${p.pts[2][0]},${p.pts[2][1]}Z`;
        return (
          <g key={p.tri.id}>
            <path d={d} fill={L >= 1 ? on : off} stroke={L >= 1 ? on : off} strokeWidth={0.8} />
            {L > 0 && L < 1 && <path d={d} fill={on} opacity={L} />}
            {fl > 0 && <path d={d} fill="#FFF3D6" opacity={0.28 * fl} />}
          </g>
        );
      })}
    </svg>
  );
};

export const SeqB: React.FC<{from: number}> = ({from}) => {
  const f = useCurrentFrame() + from;
  const inK = prog(f, from, 12, ease);
  const b2 = cue('B2'), b3 = cue('B3'), b4 = cue('B4'), b5 = cue('B5');
  // B2：分块出现，各块按自己的节奏闪 → 很多地方同时在算
  const grid = prog(f, b2 + sec(0.2), 12) * (1 - prog(f, cue('C1') - 10, 8));
  const busy = prog(f, b2 + sec(0.5), 8) * (1 - prog(f, b3, 8));
  const busyFlash = (i: number) => {
    if (busy <= 0) return 0;
    const ph = ((f / 30) / 0.9 + phase(i)) % 1;
    return busy * Math.max(0, 1 - ph * 4);
  };
  // B3：三块示例
  const ex = prog(f, b3 + sec(0.1), 12) * (1 - prog(f, b4, 8));
  const focus = ex;
  // B4：先暗，前 1.3 秒一块一块排队点亮，然后剩下的一起亮
  const dark = prog(f, b4, 6);
  const Q0 = b4 + sec(0.3), QSTEP = 4, QN = 6;            // 排队亮 6 块
  const ALL = b4 + sec(1.55);                              // 「一起算」
  const tileLit = (i: number) => {
    if (f < b4) return 1;
    if (i < QN && f >= Q0 + i * QSTEP) return prog(f, Q0 + i * QSTEP, 3);
    return prog(f, ALL, 5, ease);
  };
  const lit = (p: Proj) => (dark < 1 ? 1 : tileLit(tileOf(p)));
  const allFlash = prog(f, ALL, 3) * (1 - prog(f, ALL + 4, 10));
  // B5：整幅画面按批一起脉动两次
  const pulse = (k: number) => prog(f, b5 + sec(0.3 + k * 0.8), 3) * (1 - prog(f, b5 + sec(0.4 + k * 0.8), 9));
  const flash = (i: number) => Math.max(busyFlash(i), allFlash, pulse(0), pulse(1), f >= b4 && f < ALL && i < QN ? prog(f, Q0 + i * QSTEP, 2) * (1 - prog(f, Q0 + i * QSTEP + 2, 6)) : 0);
  const banner = prog(f, b5 + sec(1.6), 12);
  const Pp = project(TRIS.filter((t) => PICKS.includes(t.id)), camAt(f), VP.w, VP.h);

  return (
    <AbsoluteFill style={{background: `rgba(12,13,16,${inK})`}}>
      <Kicker text="游戏画面" color={C.game} opacity={inK} />
      <Drift from={from} amp={0.8} push={0.0012}>
        <div style={{position: 'absolute', left: VP.x, top: VP.y, width: VP.w, height: VP.h, borderRadius: 28, overflow: 'hidden',
          boxShadow: `0 0 0 2px ${C.line}`, opacity: inK, transform: `scale(${lerp(0.9, 1, inK)})`}}>
          <GameView f={f} lit={lit} flash={flash} focus={focus} />
          {/* 分块 */}
          <svg width={VP.w} height={VP.h} style={{position: 'absolute', left: 0, top: 0}}>
            {Array.from({length: TILES}, (_, i) => {
              const c = i % COLS, r = Math.floor(i / COLS);
              const fl = flash(i);
              return <rect key={i} x={c * (VP.w / COLS) + 3} y={r * (VP.h / ROWS) + 3} width={VP.w / COLS - 6} height={VP.h / ROWS - 6} rx={10}
                fill="none" stroke={fl > 0.4 ? C.game : 'rgba(255,255,255,0.8)'} strokeWidth={fl > 0.4 ? 6 : 3} opacity={grid * (0.6 + 0.4 * fl) * (1 - ex * 0.7)} />;
            })}
            {/* B3：三块示例，同一条规则、不同的数 */}
            {ex > 0 && Pp.map((p, k) => {
              const [x, y] = cen(p);
              const bx = VP.w / 2, by = 92;
              return (
                <g key={k} opacity={ex}>
                  <path d={`M${p.pts[0][0]},${p.pts[0][1]}L${p.pts[1][0]},${p.pts[1][1]}L${p.pts[2][0]},${p.pts[2][1]}Z`} fill="none" stroke={C.op} strokeWidth={4} />
                  <line x1={bx} y1={by + 40} x2={x} y2={y} stroke={C.op} strokeWidth={3} strokeDasharray="10 8" opacity={0.8} />
                  <rect x={x - 70} y={y + 26} width={140} height={66} rx={14} fill="rgba(12,13,16,0.85)" stroke={C.game} strokeWidth={3} />
                  <text x={x} y={y + 72} textAnchor="middle" fontFamily={FONT.num} fontWeight={700} fontSize={42} fill={C.ink}>{r2(p.shade).toFixed(2)}</text>
                </g>
              );
            })}
          </svg>
          {ex > 0 && (
            <div style={{position: 'absolute', left: 0, right: 0, top: 50, textAlign: 'center', opacity: ex}}>
              <span style={{fontFamily: FONT.hei, fontWeight: 700, fontSize: 46, color: C.ink, background: 'rgba(12,13,16,0.85)', padding: '10px 28px', borderRadius: 14,
                border: `3px solid ${C.op}`}}>同一条规则，算出不同的亮度</span>
            </div>
          )}
          {/* B4：排队 → 一起算 */}
          {f >= b4 && f < b5 + sec(0.2) && (
            <div style={{position: 'absolute', left: 0, right: 0, top: VP.h / 2 - 60, textAlign: 'center', fontFamily: FONT.title, fontSize: 104,
              color: f < ALL ? C.sub : C.op, opacity: f < ALL ? prog(f, Q0, 6) : 1 - prog(f, b5, 6), textShadow: '0 4px 24px rgba(0,0,0,0.9)'}}>
              {f < ALL ? '排队？' : '一起算'}
            </div>
          )}
          {/* B5：GPU 擅长大量并行任务 */}
          <div style={{position: 'absolute', left: 0, right: 0, bottom: 44, textAlign: 'center', opacity: banner, transform: `translateY(${(1 - banner) * 20}px)`}}>
            <span style={{fontFamily: FONT.hei, fontWeight: 700, fontSize: 50, color: C.ink, background: 'rgba(12,13,16,0.88)', padding: '14px 30px', borderRadius: 16,
              border: `3px solid ${C.game}`}}>GPU：大量并行任务，一起算</span>
          </div>
        </div>
      </Drift>
      <Note top={1490} opacity={prog(f, b3, 10) * 0.9}>示意：每块按同一公式算亮度（漫反射）；真实渲染步骤更多，有些要等前一步</Note>
    </AbsoluteFill>
  );
};
