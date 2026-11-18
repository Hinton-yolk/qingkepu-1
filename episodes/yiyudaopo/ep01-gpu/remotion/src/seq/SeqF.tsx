import {AbsoluteFill, Img, Sequence, staticFile, useCurrentFrame} from 'remotion';
import chip from '../anchors/CHIP.json';
import {C, FONT} from '../lib/theme';
import {cue, ease, easeIO, lerp, prog, sec} from '../lib/time';
import {Drift, Note, Plate} from '../lib/ui';

// F 段（显存瓶颈）：接 E 段的写实芯片 → 显存框、计算区框「变形」成一张大的 2D 系统图：
// 上：显存（6 摞，HBM）；中：数据通道；下：计算单元。数据块沿通道往下送，送到哪一列，哪一列的计算单元就亮（因果看得见）。
// → 通道变窄：数据来得稀，大部分计算单元在等（右上角的「在干活」比例是按画面上真亮着的格子实时算的）
// → 容量变大、通道变宽：又都忙起来 → 回到写实芯片：HBM 紧挨着计算芯片、接口很宽。
type P = number[];
const RATE_E = 0.8;                                   // 和 E 段 CHIP 底片的播放速度一致
const STACK = {x0: 140, w: 120, gap: 16, y: 300, h: 330, n: 6};
const stackX = (i: number) => STACK.x0 + i * (STACK.w + STACK.gap);
const LANE0 = {y0: 668, y1: 930, x0: 170, x1: 910};
const GRID = {cols: 8, rows: 4, s: 84, pitch: 98, y0: 960};
const gridX0 = 540 - (GRID.cols * GRID.pitch) / 2 + (GRID.pitch - GRID.s) / 2;
const cellXY = (c: number, r: number) => ({x: gridX0 + c * GRID.pitch, y: GRID.y0 + r * GRID.pitch});
const PURPLE = '#9C7BD8';

export const SeqF: React.FC<{from: number}> = ({from}) => {
  const f = useCurrentFrame() + from;
  const f1 = cue('F1'), f2 = cue('F2'), f3 = cue('F3'), f4 = cue('F4'), f5 = cue('F5'), f6 = cue('F6'), f7 = cue('F7');
  const T_CHIP = cue('E1') + sec(3.0);
  // 写实芯片 → 2D
  const plateFrame = Math.max(0, Math.min(chip.frames.length - 1, Math.floor((f - T_CHIP) * RATE_E)));
  const fr = chip.frames[plateFrame] as {die: P[]; hbmq: P[][]};
  const morph = prog(f, from + sec(0.5), sec(1.1), easeIO);
  const back = prog(f, f7 + sec(0.2), sec(0.9), easeIO);           // F7：回到写实芯片
  // 数据：填满显存、通道、计算
  const fill = (i: number, k: number) => prog(f, f1 + sec(0.3) + (k * STACK.n + i) * 1.1, 6);
  const lanesOn = prog(f, f3, 10);
  const starve = prog(f, f5 + sec(0.3), 18, easeIO);                // 通道变窄
  const widen = prog(f, f6 + sec(0.6), 20, easeIO);                 // 容量、带宽变大
  const nLanes = Math.round(lerp(lerp(8, 2, starve), 12, widen));
  const period = lerp(lerp(0.42, 0.85, starve), 0.3, widen);         // 每条通道多久送一块
  const travel = 0.55;
  const tNow = (f - f3) / 30;
  const factory = prog(f, f4, 10) * (1 - prog(f, f6, 10));
  const capK = 1 + 0.22 * widen;
  const LANE = {...LANE0, y0: LANE0.y0 + STACK.h * 0.22 * widen};
  // 计算单元：每条通道负责一列（或几列）；一块数据送到，这一列的一个格子亮 0.6 秒
  // 一块数据送到某条通道的底部，这条通道负责的那一列计算单元就能干 0.45 秒的活
  const BUSY = 0.42;
  const busyOf = (c: number, _r: number) => {
    if (lanesOn <= 0) return 0;
    let v = 0;
    for (let j = 0; j < nLanes; j++) {
      if (Math.floor((j * GRID.cols) / nLanes) !== c) continue;
      const ph = ((j * 0.37) % 1) * period;
      const kLast = Math.floor((tNow - travel - ph) / period);
      for (let k = kLast; k >= Math.max(0, kLast - 2); k--) {
        const dt = tNow - (ph + k * period + travel);
        if (dt >= 0 && dt < BUSY) v = Math.max(v, 1 - (dt / BUSY) * 0.5);
      }
    }
    return v;
  };
  let busyCount = 0;
  const cells = Array.from({length: GRID.cols * GRID.rows}, (_, k) => {
    const c = k % GRID.cols, r = Math.floor(k / GRID.cols);
    const b = busyOf(c, r);
    if (b > 0.25) busyCount++;
    return {c, r, b};
  });
  const util = Math.round((busyCount / cells.length) * 100);
  const uiIn = morph * (1 - back);

  // 2D 元素的「来源框」：从写实画面里的 HBM、计算区投影框长出来
  const bbox = (q: P[]) => {
    const xs = q.map((p) => p[0] * 1080), ys = q.map((p) => p[1] * 1920);
    return {x: Math.min(...xs), y: Math.min(...ys), w: Math.max(...xs) - Math.min(...xs), h: Math.max(...ys) - Math.min(...ys)};
  };
  const dieB = bbox(fr.die);
  const endF = chip.frames[chip.frames.length - 1] as {die: P[]; hbm: P[]; hbmq: P[][]};
  const dcEnd = [endF.die.reduce((a, d) => a + d[0], 0) / 4 * 1080, endF.die.reduce((a, d) => a + d[1], 0) / 4 * 1920];

  return (
    <AbsoluteFill style={{background: C.bg}}>
      {/* 写实芯片：接 E 段，继续播放；F7 再回到底片最后一帧 */}
      <Sequence from={0} layout="none">
        <AbsoluteFill style={{opacity: 1 - morph}}>
          <Plate name="CHIP" rate={RATE_E} startFrom={Math.max(0, Math.floor((from - T_CHIP) * RATE_E))} />
        </AbsoluteFill>
      </Sequence>
      {back > 0 && (
        <AbsoluteFill style={{opacity: back, transform: `scale(${1 + 0.05 * prog(f, f7, sec(6), (x) => x)}) translateY(${-24 * prog(f, f7, sec(6), (x) => x)}px)`, transformOrigin: `${dcEnd[0]}px ${dcEnd[1]}px`}}>
          <Img src={staticFile('plates/CHIP_last.png')} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
          <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(8,9,11,0.78) 0%, rgba(8,9,11,0.15) 30%, rgba(8,9,11,0) 66%, rgba(8,9,11,0.6) 100%)'}} />
          <svg width={1080} height={1920} style={{position: 'absolute', left: 0, top: 0}}>
            {endF.hbmq.map((q, i) => {
              const pts = q.map((p) => [p[0] * 1080, p[1] * 1920]);
              const hc = [endF.hbm[i][0] * 1080, endF.hbm[i][1] * 1920];
              const ex = lerp(hc[0], dcEnd[0], 0.4), ey = lerp(hc[1], dcEnd[1], 0.4);
              const nx = -(ey - hc[1]), ny = ex - hc[0], nl = Math.hypot(nx, ny) || 1;
              const wire = prog(f, f7 + sec(1.3) + i * 3, 10);
              return (
                <g key={i}>
                  <polygon points={pts.map((p) => p.join(',')).join(' ')} fill="rgba(156,123,216,0.18)" stroke={PURPLE} strokeWidth={4} opacity={back} />
                  {/* 很宽的接口：一束并排的短线 */}
                  {Array.from({length: 9}, (_, k) => {
                    const o = (k - 4) * 6;
                    const u = (((f - f7) / 22 + k * 0.11 + i * 0.07) % 1);
                    return (
                      <g key={k}>
                        <line x1={hc[0] + (nx / nl) * o} y1={hc[1] + (ny / nl) * o} x2={lerp(hc[0], ex, wire) + (nx / nl) * o} y2={lerp(hc[1], ey, wire) + (ny / nl) * o}
                          stroke={C.ink} strokeWidth={2.5} opacity={0.85} />
                        {wire > 0.9 && <circle cx={lerp(hc[0], ex, u) + (nx / nl) * o} cy={lerp(hc[1], ey, u) + (ny / nl) * o} r={4.5} fill={C.ai} />}
                      </g>
                    );
                  })}
                </g>
              );
            })}
            <polygon points={endF.die.map((p) => [p[0] * 1080, p[1] * 1920].join(',')).join(' ')} fill="rgba(240,160,64,0.12)" stroke={C.game} strokeWidth={5} opacity={back} />
          </svg>
          <div style={{position: 'absolute', left: 60, right: 60, top: 1150, textAlign: 'center', opacity: prog(f, f7 + sec(1.8), 12), fontFamily: FONT.hei, fontWeight: 700, fontSize: 44, color: C.ink,
            textShadow: '0 2px 12px rgba(0,0,0,0.95)', lineHeight: 1.4}}>
            HBM：好几层存储芯片叠在一起<br />紧挨着计算芯片，接口很宽
          </div>
        </AbsoluteFill>
      )}

      {/* 2D 系统图 */}
      {uiIn > 0 && (
        <Drift from={from} amp={0.5} push={0.0006}>
          <AbsoluteFill style={{opacity: uiIn}}>
            {/* 显存 */}
            <div style={{position: 'absolute', left: 60, top: 196, fontFamily: FONT.hei, fontWeight: 700, fontSize: 48, color: C.ink}}>
              显存（HBM）<span style={{fontSize: 38, color: C.sub, opacity: factory}}>　像仓库</span>
            </div>
            <div style={{position: 'absolute', right: 140, top: 206, display: 'flex', gap: 24, fontFamily: FONT.hei, fontWeight: 700, fontSize: 34, opacity: prog(f, f1 + sec(0.6), 10)}}>
              <span style={{color: C.ai}}>■ 参数</span><span style={{color: PURPLE}}>■ 中间数据</span>
            </div>
            {Array.from({length: STACK.n}, (_, i) => {
              const src = bbox(fr.hbmq[i]);
              const h = STACK.h * capK, y = STACK.y;                    // 容量变大：往下长，不挤标题
              const X = lerp(src.x, stackX(i), morph), Y = lerp(src.y, y, morph), Wd = lerp(src.w, STACK.w, morph), Hd = lerp(src.h, h, morph);
              const layers = Math.round(8 * capK);
              return (
                <div key={i} style={{position: 'absolute', left: X, top: Y, width: Wd, height: Hd, borderRadius: 10, border: `4px solid ${C.sub}`, background: '#16191E', overflow: 'hidden'}}>
                  {Array.from({length: layers}, (_, k) => {
                    const lh = Hd / layers;
                    const isParam = (k + i) % 3 !== 0;
                    return <div key={k} style={{position: 'absolute', left: 6, right: 6, bottom: 4 + k * lh, height: lh - 6, borderRadius: 4,
                      background: isParam ? C.ai : PURPLE, opacity: 0.85 * fill(i, Math.min(k, 7)) * morph}} />;
                  })}
                </div>
              );
            })}
            <div style={{position: 'absolute', left: 36, top: 330, fontFamily: FONT.hei, fontWeight: 700, fontSize: 38, color: C.ink, opacity: widen, writingMode: 'vertical-rl'}}>容量 ↑</div>
            {/* 通道 */}
            <svg width={1080} height={1920} style={{position: 'absolute', left: 0, top: 0}}>
              {Array.from({length: 12}, (_, j) => {
                const on = j < nLanes;
                const x = lerp(LANE.x0, LANE.x1, (j + 0.5) / Math.max(nLanes, 1));
                return <line key={j} x1={x} y1={LANE.y0} x2={x} y2={LANE.y1} stroke={on ? C.sub : 'transparent'} strokeWidth={on ? 6 : 0} strokeDasharray={factory > 0.5 ? '18 10' : undefined}
                  strokeDashoffset={-(f * 2) % 28} opacity={lanesOn * 0.6} />;
              })}
            </svg>
            {lanesOn > 0 && Array.from({length: nLanes}, (_, j) => {
              const x = lerp(LANE.x0, LANE.x1, (j + 0.5) / nLanes);
              const ph = ((j * 0.37) % 1) * period;
              return Array.from({length: 3}, (_, k) => {
                const kk = Math.floor((tNow - ph) / period) - k;
                if (kk < 0) return null;
                const u = (tNow - ph - kk * period) / travel;
                if (u < 0 || u > 1) return null;
                const y = lerp(LANE.y0, LANE.y1, u);
                const col = (kk + j) % 3 === 0 ? PURPLE : C.ai;
                return <div key={j + '-' + k} style={{position: 'absolute', left: x - 22, top: y - 24, width: 44, height: 48, borderRadius: 8, background: col, border: `3px solid ${C.ink}`, opacity: lanesOn}} />;
              });
            })}
            <div style={{position: 'absolute', left: 40, top: 760, fontFamily: FONT.hei, fontWeight: 700, fontSize: 36, color: C.sub, opacity: lanesOn * (1 - widen), writingMode: 'vertical-rl'}}>
              {factory > 0.5 ? '传送带' : '读取'}
            </div>
            <div style={{position: 'absolute', left: 36, top: 730, fontFamily: FONT.hei, fontWeight: 700, fontSize: 38, color: C.ink, opacity: widen, writingMode: 'vertical-rl'}}>带宽 ↑</div>
            {/* 计算单元 */}
            <div style={{position: 'absolute', left: 60, top: GRID.y0 - 2 - 0, transform: 'translateY(-100%)', fontFamily: FONT.hei, fontWeight: 700, fontSize: 40, color: C.game, opacity: lanesOn}}>
              计算单元<span style={{fontSize: 34, color: C.sub, opacity: factory}}>　像机器</span>
            </div>
            <div style={{position: 'absolute', right: 140, top: GRID.y0 - 50, fontFamily: FONT.hei, fontWeight: 700, fontSize: 36, color: util > 50 ? C.game : C.sub, opacity: lanesOn}}>
              在干活：{util}%
            </div>
            {cells.map(({c, r, b}, k) => {
              const p = cellXY(c, r);
              const src = dieB;
              const X = lerp(src.x + (c / GRID.cols) * src.w, p.x, morph), Y = lerp(src.y + (r / GRID.rows) * src.h, p.y, morph);
              const Sz = lerp(src.w / GRID.cols, GRID.s, morph);
              const idle = lanesOn > 0.5 && b < 0.1;
              return (
                <div key={k} style={{position: 'absolute', left: X, top: Y, width: Sz, height: Sz, borderRadius: 12,
                  border: `4px solid ${b > 0.1 ? C.game : idle && starve > 0.5 && widen < 0.5 ? '#5C6370' : '#6B5326'}`,
                  background: b > 0.1 ? `rgba(240,160,64,${0.3 + 0.6 * b})` : '#1A1D22', display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontFamily: FONT.hei, fontSize: 34, color: C.sub}}>
                  {idle && starve > 0.5 && widen < 0.5 ? '⏳' : ''}
                </div>
              );
            })}
            <div style={{position: 'absolute', left: 0, right: 0, top: 1320, textAlign: 'center', fontFamily: FONT.hei, fontWeight: 700, fontSize: 44, color: C.ink,
              opacity: starve * (1 - widen)}}>数据来得慢，计算单元只能等</div>
          </AbsoluteFill>
        </Drift>
      )}
      <Note top={1490} opacity={uiIn * prog(f, f5, 10) * 0.9}>示意；不是所有计算都卡在显存上，要看任务</Note>
      <Note top={1490} opacity={back * 0.9}>示意：通用 AI 加速器，非特定型号</Note>
    </AbsoluteFill>
  );
};
