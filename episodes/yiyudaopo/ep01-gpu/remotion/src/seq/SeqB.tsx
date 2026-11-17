import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import macro from '../anchors/MACRO.json';
import {C, FONT} from '../lib/theme';
import {area, buildScene, Cam, LIGHT, project, Proj, shadeColor} from '../lib/terrain';
import {cue, ease, easeIO, lerp, prog, sec} from '../lib/time';
import {Kicker, Note} from '../lib/ui';
import {T_MACRO} from './SeqA';

// B 段：游戏画面由三角形拼成 → 挑一块，演示它的亮度怎么算（三对数相乘再相加）→ 同一束光、同一个公式、
// 不同的数 → 画面按屏幕分块，一块一批同时算（GPU 当初就是为这个设计的）
const TRIS = buildScene();
export const VP = {x: 40, y: 250, w: 1000, h: 820};
const r2 = (x: number) => Math.round(x * 100) / 100;
const f2 = (x: number) => x.toFixed(2);

export const camAt = (f: number): Cam => {
  const orbit = prog(f, cue('B1') - sec(0.4), cue('B2') - cue('B1') + sec(0.4), easeIO); // B2 开始时停住
  const drift = Math.max(0, f - cue('B2')) * 0.00012;                                    // 停住后极慢的漂移，画面不死
  return {az: lerp(0.25, 0.7, orbit) + drift, el: lerp(0.42, 0.5, orbit), dist: lerp(12.5, 10.8, orbit), fov: 0.78, target: [0.2, 0.7, 0]};
};

// 被挑出来演示的那块：停住时，正对相机、受光中等、在画面中间附近、面积够大的一块地面
const pick = (() => {
  const P = project(TRIS, camAt(cue('B2')), VP.w, VP.h);
  let best: Proj | null = null, score = -1;
  for (const p of P) {
    if (!p.facing || p.tri.kind !== 'land' || p.tri.base[2] > 110) continue;
    const cx = (p.pts[0][0] + p.pts[1][0] + p.pts[2][0]) / 3, cy = (p.pts[0][1] + p.pts[1][1] + p.pts[2][1]) / 3;
    if (p.shade < 0.55 || p.shade > 0.93) continue;
    const s = area(p.pts) * Math.exp(-(((cx - VP.w * 0.45) / 260) ** 2) - (((cy - VP.h * 0.52) / 220) ** 2));
    if (s > score) { score = s; best = p; }
  }
  return best!.tri.id;
})();
const PT = TRIS.find((t) => t.id === pick)!;
export const NV = PT.n.map(r2) as [number, number, number];
export const LV = LIGHT.map(r2) as [number, number, number];
export const PROD = NV.map((v, i) => r2(v * LV[i]));
export const SUM = r2(PROD[0] + PROD[1] + PROD[2]);

/** 画游戏画面。lit(t) 返回 0..1：这块三角形「已经算好亮度」的程度（B5 分批点亮用） */
export const GameView: React.FC<{f: number; wire: number; focus: number; lit?: (p: Proj) => number; dimOthers?: number}> = ({f, wire, focus, lit, dimOthers = 0}) => {
  const P = project(TRIS, camAt(f), VP.w, VP.h);
  return (
    <svg width={VP.w} height={VP.h} style={{position: 'absolute', left: 0, top: 0}}>
      <defs>
        <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#8DB3C9" />
          <stop offset="0.55" stopColor="#D9CDB0" />
          <stop offset="1" stopColor="#E9D3A5" />
        </linearGradient>
      </defs>
      <rect width={VP.w} height={VP.h} fill="url(#sky)" opacity={lit ? 0.25 + 0.75 * (1 - dimOthers) : 1 - dimOthers * 0.75} />
      {/* 太阳：方向和公式里的光线 l 一致（右上方） */}
      <circle cx={VP.w * 0.83} cy={VP.h * 0.13} r={34} fill={C.sun} opacity={0.9 * (1 - dimOthers * 0.5)} />
      {P.map((p) => {
        if (!p.facing && p.tri.kind !== 'water') return null;
        const isPick = p.tri.id === pick;
        const L = lit ? lit(p) : 1;
        const k = isPick ? 1.15 : 1 - dimOthers * 0.5;
        const fill = L >= 1 ? shadeColor(p.tri.base, p.shade, k) : `rgb(${Math.round(14 + 0 * L)},${Math.round(15)},${Math.round(18)})`;
        const d = `M${p.pts[0][0]},${p.pts[0][1]}L${p.pts[1][0]},${p.pts[1][1]}L${p.pts[2][0]},${p.pts[2][1]}Z`;
        return (
          <g key={p.tri.id}>
            <path d={d} fill={fill} stroke={fill} strokeWidth={0.8} />
            {L > 0 && L < 1 && <path d={d} fill={shadeColor(p.tri.base, p.shade, k)} opacity={L} />}
            {wire > 0 && <path d={d} fill="none" stroke="rgba(255,255,255,0.55)" strokeWidth={1} opacity={wire * (isPick ? 0 : 1 - dimOthers * 0.7)} />}
            {isPick && focus > 0 && <path d={d} fill="none" stroke={C.op} strokeWidth={1.6} strokeLinejoin="round" opacity={focus} />}
          </g>
        );
      })}
    </svg>
  );
};

/** 竖排一对数相乘：上面 n，下面 l，结果落下来 */
const Num: React.FC<{v: string; color: string; o?: number; size?: number; glow?: number}> = ({v, color, o = 1, size = 56, glow = 0}) => (
  <span style={{fontFamily: FONT.num, fontSize: size, color, opacity: o, fontWeight: 700, textShadow: glow ? `0 0 ${18 * glow}px ${color}` : undefined}}>{v}</span>
);

export const SeqB: React.FC<{from: number}> = ({from}) => {
  const f = useCurrentFrame() + from;
  // 开场：A 段大芯片的方框，长成游戏视口（同一个矩形带过去）
  const mf = Math.min(macro.frames.length - 1, from - T_MACRO);
  const die = macro.frames[mf].die;
  const xs = die.map((d) => d[0] * 1080), ys = die.map((d) => d[1] * 1920);
  const r0 = {x: Math.min(...xs), y: Math.min(...ys), w: Math.max(...xs) - Math.min(...xs), h: Math.max(...ys) - Math.min(...ys)};
  const m = prog(f, from, 16, easeIO);
  const rect = {x: lerp(r0.x, VP.x, m), y: lerp(r0.y, VP.y, m), w: lerp(r0.w, VP.w, m), h: lerp(r0.h, VP.h, m)};
  const bgIn = prog(f, from, 10);

  const wire = prog(f, cue('B1') + sec(1.6), sec(1.0)) * (1 - prog(f, cue('B2') + sec(0.2), 10));
  const focus = prog(f, cue('B2') + sec(0.1), 10);
  const dimOthers = prog(f, cue('B2') + sec(0.1), 14) * (1 - prog(f, cue('B5') - 6, 8));

  // B2：法线和光线两支箭头（画在被挑中的三角形上）
  const P = project([PT], camAt(f), VP.w, VP.h)[0];
  const cx = (P.pts[0][0] + P.pts[1][0] + P.pts[2][0]) / 3, cy = (P.pts[0][1] + P.pts[1][1] + P.pts[2][1]) / 3;
  // 法线箭头：把三角形中心沿法线 n 移 1.1 个单位，投影到屏幕上（真的法线方向，不是随手画的）
  const c3 = [0, 1, 2].map((k) => (PT.p[0][k] + PT.p[1][k] + PT.p[2][k]) / 3) as [number, number, number];
  const tipT = {...PT, p: [c3.map((v, k) => v + PT.n[k] * 0.9), c3, c3] as typeof PT.p};
  const tipP = project([tipT], camAt(f), VP.w, VP.h)[0].pts[0];
  // B2 推近被挑中的那块，B4 退回全景
  const zoom = prog(f, cue('B2') + sec(0.1), 18, easeIO) * (1 - prog(f, cue('B4') + sec(0.1), 16, easeIO));
  const Z = lerp(1, 3.2, zoom);
  const zx = lerp(0, VP.w / 2 - cx * Z, zoom), zy = lerp(0, VP.h * 0.55 - cy * Z, zoom);
  const arrows = prog(f, cue('B2') + sec(0.8), 14) * (1 - prog(f, cue('B4') + sec(0.2), 10));

  // B3：公式面板
  const B3 = cue('B3');
  const panelIn = prog(f, cue('B2') + sec(1.4), 12) * (1 - prog(f, cue('B4') + sec(0.1), 10));
  const mul = [0, 1, 2].map((i) => prog(f, B3 + sec(0.15 + i * 0.42), 9));
  const add = prog(f, B3 + sec(1.65), 10);
  const sumGlow = prog(f, B3 + sec(1.9), 8) * (1 - prog(f, B3 + sec(2.8), 12));

  // B4：同一束光 l，广播到一整批三角形，每块的 n 不同
  const B4 = cue('B4');
  const gridIn = prog(f, B4 + sec(0.1), 14);
  const fan = prog(f, B4 + sec(0.9), 20);
  // B5：画面分块，一块一批同时点亮
  const B5 = cue('B5');
  const W0 = B5 + sec(0.15), WAVE = 9;
  const tiles = 6;
  const tileOf = (p: Proj) => {
    const cxp = (p.pts[0][0] + p.pts[1][0] + p.pts[2][0]) / 3, cyp = (p.pts[0][1] + p.pts[1][1] + p.pts[2][1]) / 3;
    const col = Math.max(0, Math.min(2, Math.floor((cxp / VP.w) * 3))), row = Math.max(0, Math.min(1, Math.floor((cyp / VP.h) * 2)));
    return row * 3 + col;
  };
  const inB5 = f >= B5 - 6;
  const dark = prog(f, B5 - 6, 6);
  const lit = inB5 ? (p: Proj) => (dark < 1 ? 1 - dark : prog(f, W0 + tileOf(p) * WAVE, 4, ease)) : undefined;
  const wave = Math.floor((f - W0) / WAVE);
  const tileFlash = (i: number) => (f >= W0 + i * WAVE && f < W0 + i * WAVE + WAVE ? 1 - (f - W0 - i * WAVE) / WAVE : 0);
  const gpuTag = prog(f, B5 + sec(2.6), 12);
  const note = prog(f, B5 + sec(0.5), 12);

  const cellRows = 4, cellCols = 6;
  const LAND = TRIS.filter((t) => t.kind !== 'water' && t.p[0][1] > 0.1);
  const cellNs = Array.from({length: cellRows * cellCols}, (_, i) => LAND[(i * 53 + 7) % LAND.length]);

  return (
    <AbsoluteFill style={{background: interpolate(bgIn, [0, 1], [0, 1]) > 0 ? `rgba(12,13,16,${bgIn})` : undefined}}>
      <Kicker text="游戏画面" color={C.game} opacity={prog(f, from + 10, 12)} />
      {/* 视口 */}
      <div style={{position: 'absolute', left: rect.x, top: rect.y, width: rect.w, height: rect.h, borderRadius: lerp(4, 26, m), overflow: 'hidden',
        boxShadow: `0 0 0 2px ${C.line}`}}>
        <div style={{transform: `scale(${rect.w / VP.w}, ${rect.h / VP.h})`, transformOrigin: '0 0', opacity: m}}>
         <div style={{transform: `translate(${zx}px, ${zy}px) scale(${Z})`, transformOrigin: '0 0'}}>
          <GameView f={f} wire={wire} focus={focus} dimOthers={dimOthers} lit={lit} />
          {/* 法线 n、光线 l */}
          {arrows > 0 && (
            <svg width={VP.w} height={VP.h} style={{position: 'absolute', left: 0, top: 0}}>
              <defs>
                <marker id="ah" markerWidth="10" markerHeight="10" refX="6" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 Z" fill={C.op} /></marker>
                <marker id="ahs" markerWidth="10" markerHeight="10" refX="6" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 Z" fill={C.sun} /></marker>
              </defs>
              <line x1={cx} y1={cy} x2={lerp(cx, tipP[0], arrows)} y2={lerp(cy, tipP[1], arrows)} stroke={C.op} strokeWidth={5 / Z} markerEnd="url(#ah)" />
              <text x={tipP[0] - 40 / Z} y={tipP[1] - 22 / Z} fill={C.op} fontFamily={FONT.hei} fontWeight={700} fontSize={36 / Z} opacity={arrows}>朝向</text>
              <line x1={(VP.w * 0.83 - 20 - zx) / Z} y1={(VP.h * 0.13 + 30 - zy) / Z} x2={lerp((VP.w * 0.83 - 20 - zx) / Z, cx + 6, arrows)} y2={lerp((VP.h * 0.13 + 30 - zy) / Z, cy - 4, arrows)}
                stroke={C.sun} strokeWidth={5 / Z} strokeDasharray={`${14 / Z} ${10 / Z}`} markerEnd="url(#ahs)" />
            </svg>
          )}
         </div>
          {arrows > 0 && <div style={{position: 'absolute', left: VP.w * 0.83 - 250, top: VP.h * 0.13 - 22, fontFamily: FONT.hei, fontWeight: 700, fontSize: 36, color: C.sun, opacity: arrows, textShadow: '0 2px 8px rgba(0,0,0,0.6)'}}>光从这来 →</div>}
          {/* B5 分块边界和当前一批的闪光 */}
          {inB5 && f >= W0 && (
            <svg width={VP.w} height={VP.h} style={{position: 'absolute', left: 0, top: 0}}>
              {Array.from({length: tiles}, (_, i) => (
                <rect key={i} x={(i % 3) * (VP.w / 3) + 2} y={Math.floor(i / 3) * (VP.h / 2) + 2} width={VP.w / 3 - 4} height={VP.h / 2 - 4}
                  fill="none" stroke={C.op} strokeWidth={3} opacity={0.15 + 0.85 * tileFlash(i)} rx={6} />
              ))}
            </svg>
          )}
        </div>
      </div>

      {/* B3 公式：三对数，竖着对应相乘，再相加 */}
      {panelIn > 0 && (
        <div style={{position: 'absolute', left: 40, right: 40, top: 1100, height: 330, opacity: panelIn, fontFamily: FONT.hei}}>
          <div style={{position: 'absolute', left: 0, top: 18, width: 160, color: C.op, fontSize: 34, fontWeight: 700}}>朝向</div>
          <div style={{position: 'absolute', left: 0, top: 104, width: 160, color: C.sun, fontSize: 34, fontWeight: 700}}>光线</div>
          {[0, 1, 2].map((i) => {
            const x = 190 + i * 250;
            return (
              <div key={i} style={{position: 'absolute', left: x, top: 0, width: 200, textAlign: 'center'}}>
                <div><Num v={f2(NV[i])} color={C.op} /></div>
                <div style={{height: 14}} />
                <div><Num v={f2(LV[i])} color={C.sun} /></div>
                <div style={{position: 'absolute', left: 0, right: 0, top: 70, color: C.sub, fontSize: 40, opacity: mul[i]}}>×</div>
                <div style={{position: 'absolute', left: 20, right: 20, top: 168, height: 3, background: C.line, opacity: mul[i]}} />
                <div style={{position: 'absolute', left: 0, right: 0, top: 180 + (1 - mul[i]) * -40, opacity: mul[i]}}>
                  <Num v={f2(PROD[i])} color={C.game} glow={mul[i] * (1 - add)} />
                </div>
                {i < 2 && <div style={{position: 'absolute', left: 205, top: 186, color: C.ink, fontSize: 52, opacity: add}}>+</div>}
              </div>
            );
          })}
          <div style={{position: 'absolute', left: 0, top: 192, color: C.sub, fontSize: 30, opacity: mul[0]}}>相乘</div>
          <div style={{position: 'absolute', left: 190, top: 268, opacity: add, display: 'flex', alignItems: 'baseline', gap: 18}}>
            <span style={{color: C.ink, fontSize: 40, fontWeight: 700}}>相加 =</span>
            <Num v={f2(SUM)} color={C.op} size={72} glow={sumGlow} />
            <span style={{color: C.sub, fontSize: 34}}>→ 这一块的亮度</span>
          </div>
        </div>
      )}

      {/* B4–B5 一整批：左边是同一束光 l，右边每格是一块三角形（各自的 n 不同） */}
      {gridIn > 0 && (
        <div style={{position: 'absolute', left: 40, top: 1110, width: 1000, height: 320, opacity: gridIn * (1 - prog(f, cue('C1') - sec(0.5), 8))}}>
          <div style={{position: 'absolute', left: 0, top: 70, width: 150, textAlign: 'center', fontFamily: FONT.hei}}>
            <div style={{color: C.sun, fontSize: 30, fontWeight: 700}}>同一束光</div>
            {LV.map((v, i) => <div key={i}><Num v={f2(v)} color={C.sun} size={40} /></div>)}
          </div>
          <svg width={1000} height={320} style={{position: 'absolute', left: 0, top: 0}}>
            {Array.from({length: cellRows}, (_, r) => (
              <path key={r} d={`M150,${160} C 200,160 190,${36 + r * 76} ${200 + 790 * fan},${36 + r * 76}`} stroke={C.sun} strokeWidth={2} fill="none" opacity={0.55 * fan} />
            ))}
          </svg>
          {cellNs.map((t, i) => {
            const r = Math.floor(i / cellCols), c = i % cellCols;
            const appear = prog(f, B4 + sec(0.3) + (c + r * 2) * 1.2, 8);
            const flash = inB5 ? tileFlash(Math.min(tiles - 1, wave)) : 0;
            const v = r2(Math.max(0, t.n[0] * LIGHT[0] + t.n[1] * LIGHT[1] + t.n[2] * LIGHT[2]));
            return (
              <div key={i} style={{position: 'absolute', left: 205 + c * 132, top: r * 76 + 4, width: 120, height: 64, borderRadius: 10,
                background: flash > 0 ? `rgba(240,160,64,${0.22 + 0.5 * flash})` : C.bg2, border: `2px solid ${flash > 0.3 ? C.game : C.line}`, opacity: appear,
                display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10, fontFamily: FONT.num}}>
                <svg width={26} height={24}><path d="M2,22 L13,2 L24,22 Z" fill={shadeColor(t.base, Math.max(0, v))} /></svg>
                <div style={{color: C.ink, fontSize: 30, fontWeight: 700}}>{f2(v)}</div>
              </div>
            );
          })}
        </div>
      )}
      {inB5 && f >= W0 && f < W0 + tiles * WAVE + 10 && (
        <div style={{position: 'absolute', left: 40 + ((Math.min(tiles - 1, Math.max(0, wave)) % 3) + 0.5) * (VP.w / 3), top: 250 + (Math.floor(Math.min(tiles - 1, Math.max(0, wave)) / 3) + 0.5) * (VP.h / 2),
          transform: 'translate(-50%,-50%)', fontFamily: FONT.hei, fontWeight: 700, fontSize: 40, color: C.op, textShadow: '0 2px 10px rgba(0,0,0,0.9)'}}>
          一批，同时算
        </div>
      )}
      <div style={{position: 'absolute', left: 0, right: 0, top: 985, textAlign: 'center', opacity: gpuTag * (1 - prog(f, cue('C1') - sec(0.5), 8)),
        transform: `translateY(${(1 - gpuTag) * 20}px)`}}>
        <span style={{fontFamily: FONT.hei, fontWeight: 700, fontSize: 44, color: C.ink, background: 'rgba(12,13,16,0.85)', padding: '10px 26px', borderRadius: 12, border: `2px solid ${C.game}`}}>
          GPU：为成批的同类计算而设计
        </span>
      </div>
      <Note top={1585} opacity={note * 0.9}>简化：只演示漫反射亮度；真实渲染还有很多步骤，有些要等前一步的结果</Note>
      <Note top={1585} opacity={prog(f, cue('B1') + sec(1.8), 10) * (1 - note) * 0.9}>示意：真实游戏画面的三角形多得多</Note>
    </AbsoluteFill>
  );
};
