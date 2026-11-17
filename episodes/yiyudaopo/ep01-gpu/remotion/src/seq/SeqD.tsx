import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {C, FONT} from '../lib/theme';
import {cue, ease, easeIO, lerp, prog, sec} from '../lib/time';
import {Drift} from '../lib/ui';

// v02 D 段（揭晓，放在全片中点）：
// 游戏的一批分块 和 AI 的一批行 → 变成同一种格子：大量、相似、可以同时算
// → CPU 全屏：几个强核心，各自处理形状各异的任务（也在并行）→ GPU 全屏：很多运算单元，一大批相同的运算一波波吞下
// → 公平的两句：CPU 也能并行；分支多的活儿 GPU 不一定快（一部分单元在等）
// → AI 的矩阵运算落进 GPU 的阵列，正好对上 → 结论
export const GPU_BOX = {x: 100, y: 800, w: 880, h: 500};
export const GPU_GRID = {cols: 6, rows: 4};
/** E 段用的 GPU 示意版图（v01 的组件，保留） */
export const GpuDie: React.FC<{f: number; build: number; fire: number; instr: number; label?: number}> = ({build, fire, instr, label = 1}) => {
  const {x, y, w, h} = GPU_BOX;
  const bw = (w - 40) / GPU_GRID.cols, bh = (h - 80) / GPU_GRID.rows;
  return (
    <div style={{position: 'absolute', left: x, top: y, width: w, height: h, borderRadius: 16, border: `3px solid ${C.ink}`, background: '#101216', opacity: build > 0 ? 1 : 0}}>
      <div style={{position: 'absolute', left: 20, top: -64, fontFamily: FONT.hei, fontWeight: 700, fontSize: 46, color: C.ink, opacity: label}}>GPU</div>
      <div style={{position: 'absolute', left: 20, right: 20, top: 16, height: 30, borderRadius: 6, background: '#262A31', opacity: build}} />
      {Array.from({length: GPU_GRID.cols * GPU_GRID.rows}, (_, b) => {
        const c = b % GPU_GRID.cols, r = Math.floor(b / GPU_GRID.cols);
        return (
          <div key={b} style={{position: 'absolute', left: 20 + c * bw + 4, top: 60 + r * bh + 4, width: bw - 8, height: bh - 8, borderRadius: 6, background: '#181B21', border: `1px solid ${C.line}`}}>
            <div style={{position: 'absolute', left: 4, right: 4, top: 4, height: 8, borderRadius: 2, background: instr > 0.1 ? `rgba(255,255,255,${0.25 + 0.6 * instr})` : '#2F343C'}} />
            {Array.from({length: 32}, (_, k) => {
              const kc = k % 8, kr = Math.floor(k / 8), cw = (bw - 18) / 8, ch = (bh - 30) / 4;
              return <div key={k} style={{position: 'absolute', left: 5 + kc * cw, top: 17 + kr * ch, width: cw - 2, height: ch - 2, borderRadius: 2,
                background: fire > 0.05 ? `rgba(240,160,64,${0.25 + 0.75 * fire})` : '#5A4325'}} />;
            })}
          </div>
        );
      })}
    </div>
  );
};

const Big: React.FC<{y: number; o: number; children: React.ReactNode; size?: number; color?: string}> = ({y, o, children, size = 104, color = C.ink}) => (
  <div style={{position: 'absolute', left: 0, right: 0, top: y, textAlign: 'center', fontFamily: FONT.title, fontSize: size, color, opacity: o, lineHeight: 1.12,
    transform: `translateY(${(1 - o) * 24}px)`, textShadow: '0 4px 20px rgba(0,0,0,0.8)'}}>{children}</div>
);
const Sub: React.FC<{y: number; o: number; children: React.ReactNode; color?: string}> = ({y, o, children, color = C.sub}) => (
  <div style={{position: 'absolute', left: 40, right: 40, top: y, textAlign: 'center', fontFamily: FONT.hei, fontWeight: 700, fontSize: 48, color, opacity: o}}>{children}</div>
);
/** 一格运算（×+） */
const Cell: React.FC<{x: number; y: number; s: number; color: string; a: number; glow?: number; label?: boolean}> = ({x, y, s, color, a, glow = 0, label = true}) => (
  <div style={{position: 'absolute', left: x, top: y, width: s, height: s, borderRadius: s * 0.16, border: `3px solid ${color}`, opacity: a,
    background: `${color}${Math.round(0x22 + 0x80 * glow).toString(16).padStart(2, '0')}`, display: 'flex', alignItems: 'center', justifyContent: 'center',
    fontFamily: FONT.num, fontWeight: 700, fontSize: s * 0.42, color: C.ink, boxShadow: glow > 0.3 ? `0 0 ${18 * glow}px ${color}` : undefined}}>{label ? '×+' : ''}</div>
);

// CPU：每个核心收到的任务形状各不相同（判断、循环、读写、计算），长短不一
const TASKS = [
  {w: 150, c: '#9C7BD8', t: '判断'}, {w: 90, c: C.game, t: '×+'}, {w: 200, c: '#5FB3A0', t: '读写'}, {w: 120, c: '#D07A9A', t: '循环'}, {w: 170, c: '#9C7BD8', t: '跳转'},
];

export const SeqD: React.FC<{from: number}> = ({from}) => {
  const f = useCurrentFrame() + from;
  const t = (f - from) / 30;
  const slideIn = prog(f, from, 14, easeIO);
  const d1 = cue('D1'), d2 = cue('D2'), d3 = cue('D3'), d4 = cue('D4'), d5 = cue('D5'), d6 = cue('D6'), d7 = cue('D7'), d8 = cue('D8');
  // ---- D1–D2：两边对上
  const pIn = prog(f, from + 4, 12);
  const toCells = prog(f, d2 + sec(0.4), 14, easeIO);   // 两边的内容都变成同一种格子
  const merge = prog(f, d2 + sec(2.3), 18, easeIO);     // 两块合成一块
  const sameTxt = prog(f, d2 + sec(2.9), 12);
  const beat = (Math.floor((f - d2) / 9) % 2 === 0 ? 1 : 0.35) * prog(f, d2 + sec(3.2), 4);   // 一起闪：同时算
  const partOut = prog(f, d3 - 8, 8);
  // ---- D3：CPU
  const cpuIn = prog(f, d3 - 6, 12) * (1 - prog(f, d4 - 6, 8));
  // ---- D4：GPU
  const gpuIn = prog(f, d4 - 6, 12) * (1 - prog(f, d5 - 6, 8));
  const wave = Math.floor((f - d4 - sec(0.6)) / 12);
  // ---- D5：公平的两句
  const fairIn = prog(f, d5 - 6, 12) * (1 - prog(f, d6 - 6, 8));
  const fair2 = prog(f, d5 + sec(1.7), 10);
  // ---- D6：AI 的矩阵运算落进 GPU 阵列
  const fitIn = prog(f, d6 - 6, 12) * (1 - prog(f, d7 - 6, 10));
  const fit = prog(f, d6 + sec(1.2), 22, easeIO);
  const fitFlash = prog(f, d6 + sec(1.95), 4) * (1 - prog(f, d6 + sec(2.8), 14));
  // ---- D7–D8：结论
  const c7 = prog(f, d7, 12);
  const strike = prog(f, d7 + sec(1.6), 10, ease);
  const c8 = prog(f, d8 + sec(0.2), 12);

  // D1–D2 的两块面板
  const PW = 1000, PH = 420;
  const topY = lerp(270, 600, merge), botY = lerp(760, 600, merge);
  const miniGrid = (kind: 'game' | 'ai', y0: number) => {
    const color = kind === 'game' ? C.game : C.ai;
    const cols = 8, rows = 3, s = 86, gap = 26;
    const x0 = (1080 - (cols * s + (cols - 1) * gap)) / 2;
    return Array.from({length: cols * rows}, (_, i) => {
      const c = i % cols, r = Math.floor(i / cols);
      const busy = kind === 'game' ? ((t * 1.1 + ((i * 37) % 11) / 11) % 1 < 0.25 ? 1 : 0) : 0;
      return <Cell key={kind + i} x={x0 + c * (s + gap)} y={y0 + 120 + r * (s + 20)} s={s} color={color} a={1} glow={Math.max(busy * (1 - toCells), beat)} label={toCells > 0.5} />;
    });
  };

  return (
    <AbsoluteFill style={{background: C.bg, transform: `translateX(${(1 - slideIn) * 1080}px)`}}>
      <Drift from={from} amp={0.9} push={0.001}>
        {/* D1–D2 */}
        {partOut < 1 && (
          <AbsoluteFill style={{opacity: 1 - partOut}}>
            <div style={{position: 'absolute', left: 40, top: topY, width: PW, height: PH, borderRadius: 26, border: `4px solid ${C.game}`, opacity: pIn * (1 - merge),
              background: 'rgba(240,160,64,0.06)'}}>
              <div style={{position: 'absolute', left: 30, top: 22, fontFamily: FONT.hei, fontWeight: 700, fontSize: 46, color: C.game}}>游戏：很多块</div>
            </div>
            <div style={{position: 'absolute', left: 40, top: botY, width: PW, height: PH, borderRadius: 26, border: `4px solid ${C.ai}`, opacity: pIn * (1 - merge),
              background: 'rgba(104,168,255,0.06)'}}>
              <div style={{position: 'absolute', left: 30, top: 22, fontFamily: FONT.hei, fontWeight: 700, fontSize: 46, color: C.ai}}>AI：很多行</div>
            </div>
            <div style={{opacity: pIn}}>
              {miniGrid('game', topY)}
              {miniGrid('ai', botY)}
            </div>
            <Big y={250} o={sameTxt}>看起来不同</Big>
            <Big y={1040} o={sameTxt} color={C.op} size={88}>都是大量、相似、<br />可以同时算的运算</Big>
          </AbsoluteFill>
        )}

        {/* D3：CPU */}
        {cpuIn > 0 && (
          <AbsoluteFill style={{opacity: cpuIn}}>
            <Big y={200} o={1}>CPU</Big>
            <Sub y={340} o={1}>很灵活：各种任务、复杂控制</Sub>
            {Array.from({length: 8}, (_, i) => {
              const c = i % 2, r = Math.floor(i / 2);
              const X = 60 + c * 500, Y = 470 + r * 200, W = 460, H = 170;
              // 每个核心的任务流：形状和长度不同，速度不同
              const speed = 120 + (i * 37) % 70;
              const off = ((t * speed + i * 140) % 600);
              return (
                <div key={i} style={{position: 'absolute', left: X, top: Y, width: W, height: H, borderRadius: 22, border: `3px solid ${C.sub}`, background: '#15181D', overflow: 'hidden'}}>
                  <div style={{position: 'absolute', left: 16, top: 10, fontFamily: FONT.hei, fontWeight: 700, fontSize: 30, color: C.dim}}>核心 {i + 1}</div>
                  {[0, 1, 2].map((k) => {
                    const task = TASKS[(i + k * 2) % TASKS.length];
                    const x = ((off + k * 230) % 690) - 220;
                    return (
                      <div key={k} style={{position: 'absolute', left: x, top: 64, width: task.w * 0.8, height: 80, borderRadius: task.t === '判断' ? 4 : 16,
                        transform: task.t === '判断' ? 'skewX(-14deg)' : undefined, background: task.c, opacity: 0.9,
                        display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: FONT.hei, fontWeight: 700, fontSize: 34, color: '#111'}}>{task.t}</div>
                    );
                  })}
                </div>
              );
            })}
          </AbsoluteFill>
        )}

        {/* D4：GPU */}
        {gpuIn > 0 && (
          <AbsoluteFill style={{opacity: gpuIn}}>
            <Big y={200} o={1}>GPU</Big>
            <Sub y={340} o={1}>更多资源给并行运算</Sub>
            {Array.from({length: 12 * 11}, (_, i) => {
              const c = i % 12, r = Math.floor(i / 12);
              const blk = Math.floor(r / 4) * 3 + Math.floor(c / 4);   // 9 块一组一组地吞
              const w = wave >= 0 ? (wave + blk) % 3 : -1;
              const hot = w === 0 ? 1 : w === 1 ? 0.45 : 0.15;
              return <Cell key={i} x={70 + c * 80} y={470 + r * 76} s={64} color={C.game} a={1} glow={f > d4 + sec(0.6) ? hot : 0.1} label={false} />;
            })}
          </AbsoluteFill>
        )}

        {/* D5：公平的两句 */}
        {fairIn > 0 && (
          <AbsoluteFill style={{opacity: fairIn}}>
            <div style={{position: 'absolute', left: 60, top: 260, width: 960, height: 470, borderRadius: 26, border: `3px solid ${C.sub}`, background: '#14171B'}}>
              <div style={{position: 'absolute', left: 34, top: 24, fontFamily: FONT.hei, fontWeight: 700, fontSize: 52, color: C.ink}}>CPU 也能并行</div>
              {Array.from({length: 8}, (_, i) => (
                <div key={i} style={{position: 'absolute', left: 40 + (i % 4) * 225, top: 130 + Math.floor(i / 4) * 160, width: 200, height: 130, borderRadius: 18,
                  border: `3px solid ${C.sub}`, background: `rgba(240,160,64,${0.25 + 0.35 * ((Math.floor(t * 3) + i) % 2)})`}} />
              ))}
            </div>
            <div style={{position: 'absolute', left: 60, top: 780, width: 960, height: 520, borderRadius: 26, border: `3px solid ${C.sub}`, background: '#14171B', opacity: fair2}}>
              <div style={{position: 'absolute', left: 34, top: 24, fontFamily: FONT.hei, fontWeight: 700, fontSize: 52, color: C.ink}}>分支多的活儿，GPU 不一定快</div>
              {Array.from({length: 32}, (_, i) => {
                const waiting = (i % 8) >= 4;                         // 一组里一半走这条分支、一半走另一条：轮流等
                const turn = Math.floor(t * 2) % 2 === 0;
                const active = waiting ? !turn : turn;
                return <div key={i} style={{position: 'absolute', left: 40 + (i % 8) * 112, top: 130 + Math.floor(i / 8) * 92, width: 96, height: 76, borderRadius: 12,
                  border: `3px solid ${active ? C.game : C.dim}`, background: active ? 'rgba(240,160,64,0.55)' : '#22262C'}} />;
              })}
              <div style={{position: 'absolute', right: 34, bottom: 22, fontFamily: FONT.hei, fontWeight: 700, fontSize: 40, color: C.sub}}>灰色：在等另一条分支</div>
            </div>
          </AbsoluteFill>
        )}

        {/* D6：AI 的矩阵运算落进 GPU 的阵列 */}
        {fitIn > 0 && (
          <AbsoluteFill style={{opacity: fitIn}}>
            <Sub y={240} o={1} color={C.ink}>AI 的很多矩阵运算</Sub>
            <Sub y={1300 - 70} o={fit} color={C.ink}>恰好适合 GPU 的设计</Sub>
            <div style={{position: 'absolute', left: 120, top: 760, width: 840, height: 430, borderRadius: 18, border: `3px solid ${C.ink}`, background: '#101216'}}>
              <div style={{position: 'absolute', left: 20, top: -60, fontFamily: FONT.hei, fontWeight: 700, fontSize: 40, color: C.sub}}>GPU 的运算单元</div>
              {Array.from({length: 32}, (_, k) => (
                <div key={k} style={{position: 'absolute', left: 24 + (k % 8) * 101, top: 24 + Math.floor(k / 8) * 100, width: 88, height: 88, borderRadius: 10,
                  background: fitFlash > 0 ? `rgba(240,160,64,${0.3 + 0.7 * fitFlash})` : fit > 0.98 ? 'rgba(240,160,64,0.5)' : '#5A4325'}} />
              ))}
            </div>
            <div style={{position: 'absolute', left: 120, top: lerp(330, 760, fit), width: 840, height: 430}}>
              {Array.from({length: 32}, (_, k) => (
                <Cell key={k} x={24 + (k % 8) * 101} y={24 + Math.floor(k / 8) * 100} s={88} color={C.ai} a={1} glow={0.2} />
              ))}
            </div>
          </AbsoluteFill>
        )}

        {/* D7–D8 结论 */}
        {c7 > 0 && (
          <AbsoluteFill>
            <Big y={420} o={c7}>GPU 适合 AI</Big>
            <div style={{position: 'absolute', left: 0, right: 0, top: 580, textAlign: 'center', opacity: c7}}>
              <span style={{position: 'relative', display: 'inline-block', fontFamily: FONT.title, fontSize: 80, color: C.sub}}>
                不是因为会画游戏
                <span style={{position: 'absolute', left: -10, top: '54%', height: 9, width: `${strike * 106}%`, background: C.warn, borderRadius: 4}} />
              </span>
            </div>
            <Big y={800} o={c8} size={84} color={C.op}>而是它擅长的计算方式</Big>
            <Big y={900} o={c8} size={84} color={C.ai}>在 AI 时代有了新用途</Big>
          </AbsoluteFill>
        )}
      </Drift>
    </AbsoluteFill>
  );
};
