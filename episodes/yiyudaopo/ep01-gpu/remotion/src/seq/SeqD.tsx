import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {C, FONT} from '../lib/theme';
import {cue, ease, easeIO, lerp, prog, sec} from '../lib/time';
import {Drift, Note} from '../lib/ui';
import {batchXY, COLS, TILES} from './SeqB';

// v03 D 段（高潮）：
// D1–D2 游戏那批（琥珀）和 AI 那几行（蓝）→ 变成同一种任务格子，合成一批
// D3 同一批任务复制两份：上半 CPU（6 个强核心，各自取任务、各自做，也能接形状不同的活）
// D4 下半 GPU（很多运算单元，一整排任务一起进、一起做完）——定性示意，不是速度测试
// D5–D6 GPU 半边铺满全屏，游戏和 AI 的计算一起流进运算单元：用画面给答案，旁白只说一遍结论
export const GPU_BOX = {x: 100, y: 800, w: 880, h: 500};
export const GPU_GRID = {cols: 6, rows: 4};
/** E 段用的 GPU 示意版图 */
export const GpuDie: React.FC<{f: number; build: number; fire: number; instr: number; label?: number}> = ({build, fire, label = 1}) => {
  const {x, y, w, h} = GPU_BOX;
  const bw = (w - 40) / GPU_GRID.cols, bh = (h - 80) / GPU_GRID.rows;
  return (
    <div style={{position: 'absolute', left: x, top: y, width: w, height: h, borderRadius: 16, border: `3px solid ${C.ink}`, background: '#101216', opacity: build > 0 ? 1 : 0}}>
      <div style={{position: 'absolute', left: 20, top: -64, fontFamily: FONT.hei, fontWeight: 700, fontSize: 46, color: C.ink, opacity: label}}>GPU</div>
      <div style={{position: 'absolute', left: 20, right: 20, top: 16, height: 30, borderRadius: 6, background: '#262A31'}} />
      {Array.from({length: GPU_GRID.cols * GPU_GRID.rows}, (_, b) => {
        const c = b % GPU_GRID.cols, r = Math.floor(b / GPU_GRID.cols);
        return (
          <div key={b} style={{position: 'absolute', left: 20 + c * bw + 4, top: 60 + r * bh + 4, width: bw - 8, height: bh - 8, borderRadius: 6, background: '#181B21', border: `1px solid ${C.line}`}}>
            {Array.from({length: 32}, (_, k) => {
              const kc = k % 8, kr = Math.floor(k / 8), cw = (bw - 18) / 8, ch = (bh - 18) / 4;
              return <div key={k} style={{position: 'absolute', left: 5 + kc * cw, top: 5 + kr * ch, width: cw - 2, height: ch - 2, borderRadius: 2,
                background: fire > 0.05 ? `rgba(240,160,64,${0.25 + 0.75 * fire})` : '#5A4325'}} />;
            })}
          </div>
        );
      })}
    </div>
  );
};

const Task: React.FC<{x: number; y: number; s: number; color: string; o?: number; glow?: number; label?: boolean; shape?: 'sq' | 'dia' | 'bar'}> = ({x, y, s, color, o = 1, glow = 0, label = false, shape = 'sq'}) => (
  <div style={{position: 'absolute', left: x - (shape === 'bar' ? s : s / 2), top: y - s / 2, width: shape === 'bar' ? s * 2 : s, height: s, borderRadius: shape === 'dia' ? 6 : s * 0.2,
    transform: shape === 'dia' ? 'rotate(45deg) scale(0.8)' : undefined, border: `${Math.max(2, s * 0.06)}px solid ${color}`, opacity: o,
    background: `${color}${Math.round(0x30 + 0x90 * glow).toString(16).padStart(2, '0')}`, display: 'flex', alignItems: 'center', justifyContent: 'center',
    fontFamily: FONT.num, fontWeight: 700, fontSize: s * 0.4, color: C.ink, boxShadow: glow > 0.3 ? `0 0 ${s * 0.4 * glow}px ${color}` : undefined}}>{label ? '×+' : ''}</div>
);

const N = 40;                                  // 一批任务的数量
const taskColor = (i: number) => (i % 5 < 2 ? C.ai : C.game);
const CPU = {y0: 230, h: 520}, GPUB = {y0: 830, h: 520};
const QX = 70, QY = (band: {y0: number}) => band.y0 + 110;     // 队列左上
const qPos = (band: {y0: number}, i: number) => ({x: QX + (i % 5) * 44 + 20, y: QY(band) + Math.floor(i / 5) * 44 + 20});

export const SeqD: React.FC<{from: number}> = ({from}) => {
  const f = useCurrentFrame() + from;
  const slideIn = prog(f, from, 12, easeIO);
  const d2 = cue('D2'), d3 = cue('D3'), d4 = cue('D4'), d5 = cue('D5'), d6 = cue('D6');
  // ---- D1–D2：两边并成一批
  const sameShape = prog(f, d2 + sec(1.0), 14, easeIO);
  const merge = prog(f, d2 + sec(2.4), 20, easeIO);
  const split = prog(f, d3 - 10, 18, easeIO);             // 一批复制成两份，飞向 CPU、GPU 的队列
  // ---- D3：CPU 6 个核心，各取各的
  const cpuOn = prog(f, d3 - 4, 10);
  const CORES = 6;
  const cpuT = Math.max(0, (f - d3 - sec(0.6)) / 30);
  const cpuDur = (core: number) => 0.85 + (core % 3) * 0.18;     // 每个核心一个任务要多久（各不相同）
  const cpuDone = (core: number) => Math.floor(cpuT / cpuDur(core));
  // 第 i 个任务给哪个核心、第几轮：按核心轮流取
  const cpuTaken = Array.from({length: CORES}, (_, c) => Math.min(Math.ceil(N / CORES), cpuDone(c) + (cpuT > 0 ? 1 : 0)));
  const cpuGone = cpuTaken.reduce((a, b) => a + b, 0);
  // ---- D4：GPU 一整排一起进
  const gpuOn = prog(f, d4 - 4, 10);
  const gpuT = Math.max(0, (f - d4 - sec(0.7)) / 30);
  const WAVE = 0.9, LANES = 16;
  const gpuWave = Math.floor(gpuT / WAVE);
  const gpuGone = Math.min(N, (gpuT > 0 ? gpuWave + 1 : 0) * LANES);
  const wavePh = (gpuT % WAVE) / WAVE;
  // ---- D5–D6：GPU 铺满，游戏和 AI 的计算一起流进去
  const full = prog(f, d5 - 4, 24, easeIO);
  const flowT = (f - d5) / 30;

  // D1–D2 两组格子的位置
  const gridPos = (i: number, top: boolean) => {
    if (top) { const p = batchXY(i); return {x: p.x, y: p.y + lerp(0, -40, merge)}; }
    return {x: 160 + (i % COLS) * 190, y: 1060 + Math.floor(i / COLS) * 58 + lerp(0, 0, merge)};
  };
  const mergedPos = (i: number) => ({x: 300 + (i % 8) * 68, y: 640 + Math.floor(i / 8) * 68});

  return (
    <AbsoluteFill style={{background: C.bg, transform: `translateX(${(1 - slideIn) * 1080}px)`}}>
      <Drift from={from} amp={0.5} push={0.0008}>
        {/* D1–D2 */}
        {split < 1 && (
          <AbsoluteFill style={{opacity: 1 - split}}>
            {Array.from({length: TILES}, (_, i) => {
              const a = gridPos(i, true), b = mergedPos(i * 2);
              return <Task key={'g' + i} x={lerp(a.x, b.x, merge)} y={lerp(a.y, b.y, merge)} s={lerp(93, 58, merge)} color={C.game} label={sameShape > 0.5} glow={sameShape * 0.4} />;
            })}
            {Array.from({length: TILES}, (_, i) => {
              const a = gridPos(i, false), b = mergedPos(i * 2 + 1);
              // AI 这边：一开始是「一行参数 → 一个输出」的长条，变成同样的方格
              return <Task key={'a' + i} x={lerp(a.x, b.x, merge)} y={lerp(a.y, b.y, merge)} s={lerp(46, 58, merge)} color={C.ai} label={sameShape > 0.5} glow={sameShape * 0.4}
                shape={sameShape < 0.5 ? 'bar' : 'sq'} />;
            })}
            <div style={{position: 'absolute', left: 0, right: 0, top: 280, textAlign: 'center', fontFamily: FONT.hei, fontWeight: 700, fontSize: 52, color: C.ink, opacity: merge}}>
              规则相同 · 可以同时算
            </div>
          </AbsoluteFill>
        )}

        {/* D3–D4：同一批任务，CPU 和 GPU 各做一遍 */}
        {split > 0 && full < 1 && (
          <AbsoluteFill style={{opacity: 1 - full}}>
            {/* CPU 半边 */}
            <div style={{position: 'absolute', left: 30, top: CPU.y0, width: 1020, height: CPU.h, borderRadius: 26, border: `3px solid ${C.sub}`, background: '#13161A', opacity: Math.max(0.35, cpuOn)}}>
              <div style={{position: 'absolute', left: 30, top: 18, fontFamily: FONT.title, fontSize: 64, color: C.ink}}>CPU</div>
            </div>
            {Array.from({length: CORES}, (_, c) => {
              const X = 370 + (c % 3) * 225, Y = CPU.y0 + 150 + Math.floor(c / 3) * 200;
              const ph = cpuT > 0 ? (cpuT % cpuDur(c)) / cpuDur(c) : 0;
              const odd = c === 4 && cpuDone(c) % 3 === 1;          // 偶尔接一个不一样的活：灵活
              return (
                <div key={c} style={{opacity: Math.max(0.35, cpuOn)}}>
                  <div style={{position: 'absolute', left: X - 95, top: Y - 85, width: 190, height: 170, borderRadius: 24, border: `4px solid ${C.ink}`, background: '#1B1F25'}} />
                  {cpuT > 0 && cpuDone(c) < Math.ceil(N / CORES) && <Task x={X} y={Y} s={74} color={odd ? '#9C7BD8' : taskColor(c + cpuDone(c) * CORES)} glow={0.3 + 0.5 * ph} label={!odd} shape={odd ? 'dia' : 'sq'} />}
                  <svg width={1080} height={1920} style={{position: 'absolute', left: 0, top: 0}}>
                    <circle cx={X} cy={Y} r={62} fill="none" stroke={C.game} strokeWidth={7} strokeDasharray={`${ph * 390} 400`} transform={`rotate(-90 ${X} ${Y})`} opacity={cpuT > 0 ? 0.9 : 0} />
                  </svg>
                </div>
              );
            })}
            <div style={{position: 'absolute', left: 370 - 95, top: CPU.y0 + CPU.h - 52, fontFamily: FONT.hei, fontWeight: 700, fontSize: 36, color: C.sub, opacity: cpuOn}}>几个强大的核心，各自取任务</div>
            {/* GPU 半边 */}
            <div style={{position: 'absolute', left: 30, top: GPUB.y0, width: 1020, height: GPUB.h, borderRadius: 26, border: `3px solid ${C.sub}`, background: '#13161A', opacity: Math.max(0.35, gpuOn)}}>
              <div style={{position: 'absolute', left: 30, top: 18, fontFamily: FONT.title, fontSize: 64, color: C.ink}}>GPU</div>
            </div>
            {Array.from({length: 4 * 16}, (_, k) => {
              const c = k % 16, r = Math.floor(k / 16);
              const X = 330 + c * 42, Y = GPUB.y0 + 130 + r * 82;
              const busy = gpuT > 0 && gpuWave * LANES < N && r === gpuWave % 4;
              return <div key={k} style={{position: 'absolute', left: X - 17, top: Y - 30, width: 34, height: 60, borderRadius: 8, opacity: Math.max(0.35, gpuOn),
                border: `3px solid ${busy ? C.game : '#5A4325'}`, background: busy ? `rgba(240,160,64,${0.35 + 0.5 * wavePh})` : '#1B1F25'}} />;
            })}
            <div style={{position: 'absolute', left: 310, top: GPUB.y0 + GPUB.h - 52, fontFamily: FONT.hei, fontWeight: 700, fontSize: 36, color: C.sub, opacity: gpuOn}}>很多运算单元，一整排一起做</div>
            {/* 两份同样的队列 */}
            {Array.from({length: N}, (_, i) => {
              const src = mergedPos(i);
              const qc = qPos(CPU, i), qg = qPos(GPUB, i);
              const goneC = i < cpuGone, goneG = i < gpuGone;
              return (
                <div key={i}>
                  <Task x={lerp(src.x, qc.x, split)} y={lerp(src.y, qc.y, split)} s={lerp(58, 36, split)} color={taskColor(i)} o={goneC ? 0 : 1} />
                  <Task x={lerp(src.x, qg.x, split)} y={lerp(src.y, qg.y, split)} s={lerp(58, 36, split)} color={taskColor(i)} o={goneG ? 0 : 1} />
                </div>
              );
            })}
          </AbsoluteFill>
        )}

        {/* D5–D6：GPU 铺满，游戏和 AI 的计算源源流进运算单元 */}
        {full > 0 && (
          <AbsoluteFill style={{opacity: full}}>
            {Array.from({length: 12 * 14}, (_, k) => {
              const c = k % 12, r = Math.floor(k / 12);
              const X = 100 + c * 80, Y = 300 + r * 76;
              const wave = Math.floor(flowT / 0.45) % 14;
              const busy = flowT > 0 && (r === wave || r === (wave + 7) % 14);
              return <div key={k} style={{position: 'absolute', left: X - 30, top: Y - 30, width: 60, height: 60, borderRadius: 10,
                border: `3px solid ${busy ? (c % 5 < 2 ? C.ai : C.game) : '#4A3920'}`, background: busy ? (c % 5 < 2 ? 'rgba(104,168,255,0.55)' : 'rgba(240,160,64,0.55)') : '#191C21'}} />;
            })}
            {/* 上方流进来的任务：琥珀 = 游戏，蓝 = AI */}
            {Array.from({length: 24}, (_, k) => {
              const t = ((flowT * 0.9 + k / 24) % 1);
              const x = 100 + (k % 12) * 80;
              return <Task key={k} x={x} y={lerp(120, 300, t)} s={44} color={k % 5 < 2 ? C.ai : C.game} o={Math.sin(t * Math.PI)} />;
            })}
            <div style={{position: 'absolute', left: 60, top: 170, fontFamily: FONT.title, fontSize: 64, color: C.ink, opacity: prog(f, d5, 10) * 0.9}}>GPU</div>
          </AbsoluteFill>
        )}
      </Drift>
      <Note top={1490} opacity={split * (1 - full) * 0.9}>示意：同一批任务；GPU 的运算单元不等于 CPU 的核心</Note>
    </AbsoluteFill>
  );
};
