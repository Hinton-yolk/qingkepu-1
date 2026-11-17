import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {C, FONT} from '../lib/theme';
import {cue, ease, easeIO, lerp, prog, sec} from '../lib/time';
import {Drift, Kicker, Note} from '../lib/ui';
import {LV, NV, PROD, SUM} from './SeqB';

// D 段：把 B 段（游戏算亮度）和 C 段（AI 算下一层）的两道算式摆在一起 → 它们的「形状」一样：成对相乘、再相加
// → 这样的乘加有一大批、互不等待 → CPU 和 GPU 把芯片面积花在不同的地方（直接画计算，不用工人比喻）
// → 结论：GPU 擅长 AI，不是因为会画游戏，而是 AI 的很多计算正好是 GPU 擅长的形状
const f2 = (x: number) => x.toFixed(2);

/** 一道算式：terms = [[a,b],...]，hi(i) 让第 i 个乘号亮，plus 让加号亮，box 把数字换成空框（只剩形状） */
const Formula: React.FC<{terms: [string, string][]; result: string; color: string; hiMul: (i: number) => number; plus: number; box: number; size?: number}> = ({
  terms, result, color, hiMul, plus, box, size = 50,
}) => (
  <div style={{display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, fontFamily: FONT.num, fontWeight: 700, fontSize: size, color: C.ink, whiteSpace: 'nowrap'}}>
    {terms.map(([a, b], i) => (
      <span key={i} style={{display: 'flex', alignItems: 'center', gap: 6}}>
        {i > 0 && <span style={{color: plus > 0.5 ? C.op : C.sub, textShadow: plus > 0.5 ? `0 0 16px ${C.op}` : undefined, margin: '0 6px'}}>+</span>}
        <Cell v={a} color={color} box={box} size={size} />
        <span style={{color: hiMul(i) > 0.5 ? C.op : C.sub, transform: `scale(${1 + 0.5 * hiMul(i)})`, textShadow: hiMul(i) > 0.5 ? `0 0 16px ${C.op}` : undefined}}>×</span>
        <Cell v={b} color={C.ink} box={box} size={size} />
      </span>
    ))}
    <span style={{color: C.sub, margin: '0 6px', opacity: 1 - box}}>=</span>
    <span style={{color, opacity: 1 - box}}>{result}</span>
  </div>
);
const Cell: React.FC<{v: string; color: string; box: number; size: number}> = ({v, color, box, size}) => (
  <span style={{position: 'relative', display: 'inline-block', minWidth: size * 0.62 * v.length * (1 - box) + size * 0.9 * box, textAlign: 'center'}}>
    <span style={{opacity: 1 - box, color}}>{v}</span>
    <span style={{position: 'absolute', left: '50%', top: '50%', width: size * 0.8, height: size * 0.8, transform: 'translate(-50%,-50%)', border: `4px solid ${C.op}`,
      borderRadius: 8, opacity: box}} />
  </span>
);

// GPU 示意版图：8×4 个流多处理器块，每块 8×4 个运算单元（32 条通道）+ 一条控制/调度 + 一条缓存
export const GPU_BOX = {x: 100, y: 800, w: 880, h: 500};
export const GPU_GRID = {cols: 6, rows: 4};
export const GpuDie: React.FC<{f: number; build: number; fire: number; instr: number; label?: number}> = ({f, build, fire, instr, label = 1}) => {
  const {x, y, w, h} = GPU_BOX;
  const bw = (w - 40) / GPU_GRID.cols, bh = (h - 80) / GPU_GRID.rows;
  return (
    <div style={{position: 'absolute', left: x, top: y, width: w, height: h, borderRadius: 16, border: `3px solid ${C.ink}`, background: '#101216', opacity: build > 0 ? 1 : 0}}>
      <div style={{position: 'absolute', left: 20, top: -58, fontFamily: FONT.hei, fontWeight: 700, fontSize: 40, color: C.ink, opacity: label}}>GPU</div>
      {/* 顶上一条：共享缓存、调度（示意） */}
      <div style={{position: 'absolute', left: 20, right: 20, top: 16, height: 30, borderRadius: 6, background: '#262A31', opacity: build,
        fontFamily: FONT.hei, fontSize: 22, color: C.sub, display: 'flex', alignItems: 'center', paddingLeft: 12}}>缓存 · 调度</div>
      {Array.from({length: GPU_GRID.cols * GPU_GRID.rows}, (_, b) => {
        const c = b % GPU_GRID.cols, r = Math.floor(b / GPU_GRID.cols);
        const appear = prog(build * 60, (c + r) * 3, 10);
        return (
          <div key={b} style={{position: 'absolute', left: 20 + c * bw + 4, top: 60 + r * bh + 4, width: bw - 8, height: bh - 8, borderRadius: 6, background: '#181B21',
            border: `1px solid ${C.line}`, opacity: appear}}>
            <div style={{position: 'absolute', left: 4, right: 4, top: 4, height: 8, borderRadius: 2, background: instr > 0.1 ? `rgba(255,255,255,${0.25 + 0.6 * instr})` : '#2F343C'}} />
            {Array.from({length: 32}, (_, k) => {
              const kc = k % 8, kr = Math.floor(k / 8);
              const cw = (bw - 8 - 10) / 8, ch = (bh - 8 - 22) / 4;
              return (
                <div key={k} style={{position: 'absolute', left: 5 + kc * cw, top: 17 + kr * ch, width: cw - 2, height: ch - 2, borderRadius: 2,
                  background: fire > 0.05 ? `rgba(240,160,64,${0.25 + 0.75 * fire})` : '#5A4325'}} />
              );
            })}
          </div>
        );
      })}
    </div>
  );
};

// CPU 示意版图：8 个大核心（每个：大块控制、少量运算单元、私有缓存）+ 一大块共享缓存
const CPU_BOX = {x: 100, y: 250, w: 880, h: 470};
const INSTR = [['读', '比较', '跳转', '×'], ['如果', '读', '写', '+'], ['×', '跳转', '比较', '读'], ['写', '如果', '+', '跳转'], ['比较', '写', '读', '如果'], ['+', '读', '如果', '写'], ['跳转', '×', '写', '比较'], ['读', '+', '跳转', '如果']];
const CpuDie: React.FC<{f: number; build: number; active: number; hiArea: number; stream: number}> = ({f, build, active, hiArea, stream}) => {
  const {x, y, w, h} = CPU_BOX;
  const cw = (w - 60) / 4, ch = (h - 220) / 2;
  return (
    <div style={{position: 'absolute', left: x, top: y, width: w, height: h, borderRadius: 16, border: `3px solid ${C.ink}`, background: '#101216', opacity: build}}>
      <div style={{position: 'absolute', left: 20, top: -58, fontFamily: FONT.hei, fontWeight: 700, fontSize: 40, color: C.ink}}>CPU</div>
      {Array.from({length: 8}, (_, i) => {
        const c = i % 4, r = Math.floor(i / 4);
        const L = 20 + c * (cw + 7), T = 20 + r * (ch + 10);
        const tick = Math.floor(f / 7 + i * 1.7) % 4;
        return (
          <div key={i} style={{position: 'absolute', left: L, top: T, width: cw, height: ch, borderRadius: 8, background: '#181B21', border: `2px solid ${active > 0.5 ? C.sub : C.line}`}}>
            {/* 控制（占一大块） */}
            <div style={{position: 'absolute', left: 6, top: 6, width: cw - 12, height: ch * 0.42, borderRadius: 4, background: `rgba(104,120,150,${0.35 + 0.45 * hiArea})`,
              fontFamily: FONT.hei, fontSize: 22, color: C.ink, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>控制</div>
            {/* 少量运算单元 */}
            {Array.from({length: 4}, (_, k) => (
              <div key={k} style={{position: 'absolute', left: 6 + k * ((cw - 12) / 4), top: ch * 0.42 + 12, width: (cw - 12) / 4 - 4, height: ch * 0.16, borderRadius: 3,
                background: active > 0.5 && k === tick ? C.game : '#5A4325'}} />
            ))}
            {/* 私有缓存 */}
            <div style={{position: 'absolute', left: 6, bottom: 6, width: cw - 12, height: ch * 0.24, borderRadius: 4, background: `rgba(80,90,105,${0.35 + 0.45 * hiArea})`,
              fontFamily: FONT.hei, fontSize: 18, color: C.sub, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>缓存</div>
            {/* 每个核心收到的指令各不相同，还有分支 */}
            {stream > 0 && (
              <div style={{position: 'absolute', left: 0, right: 0, top: -2, height: ch * 0.42, display: 'flex', alignItems: 'center', justifyContent: 'center', opacity: stream}}>
                <span style={{fontFamily: FONT.hei, fontWeight: 700, fontSize: 30, color: C.op, background: 'rgba(16,18,22,0.9)', padding: '2px 10px', borderRadius: 6,
                  border: `2px solid ${INSTR[i][tick] === '如果' || INSTR[i][tick] === '跳转' ? C.game : C.line}`}}>{INSTR[i][tick]}</span>
              </div>
            )}
          </div>
        );
      })}
      {/* 共享的大缓存 */}
      <div style={{position: 'absolute', left: 20, right: 20, bottom: 20, height: 150, borderRadius: 8, background: `rgba(80,90,105,${0.3 + 0.5 * hiArea})`,
        fontFamily: FONT.hei, fontSize: 30, color: C.ink, display: 'flex', alignItems: 'center', justifyContent: 'center', border: `2px solid ${hiArea > 0.5 ? C.sub : 'transparent'}`}}>共享缓存</div>
    </div>
  );
};

export const SeqD: React.FC<{from: number}> = ({from}) => {
  const f = useCurrentFrame() + from;
  const slideIn = prog(f, from, 14, easeIO);
  // D1–D4：两道算式
  const d2 = cue('D2'), d3 = cue('D3'), d4 = cue('D4');
  const topIn = prog(f, from + 2, 12), botIn = prog(f, from + 8, 12);
  const mulTop = (i: number) => prog(f, d2 + sec(0.95 + i * 0.3), 3) * (1 - prog(f, d2 + sec(1.2 + i * 0.3), 6));
  const plusTop = prog(f, d2 + sec(1.8), 3) * (1 - prog(f, d2 + sec(2.5), 8));
  const mulBot = (i: number) => prog(f, d3 + sec(0.75 + i * 0.32), 3) * (1 - prog(f, d3 + sec(1.0 + i * 0.32), 6));
  const plusBot = prog(f, d3 + sec(1.5), 3) * (1 - prog(f, d3 + sec(2.2), 8));
  const boxK = prog(f, d4 + sec(0.15), 14, easeIO);          // 数字换成空框：只剩形状
  const merge = prog(f, d4 + sec(0.9), 16, easeIO);         // 两道往中间合成一道
  const batch = prog(f, d4 + sec(1.6), 14);                 // 复制成一大批
  const batchFire = (Math.floor((f - d4) / 6) % 2 === 0 ? 1 : 0.55) * batch;
  const partOut = prog(f, cue('D5') - 8, 10);
  // D5：CPU
  const d5 = cue('D5'), d5b = cue('D5b'), d6 = cue('D6'), d7 = cue('D7'), d8 = cue('D8');
  const cpuIn = prog(f, d5 - 4, 14);
  const cpuActive = prog(f, d5 + sec(0.6), 6);
  const cpuArea = prog(f, d5b + sec(0.2), 10) * (1 - prog(f, d5b + sec(2.6), 10));
  const cpuStream = prog(f, d5b + sec(2.7), 8);
  // D6：GPU
  const gpuBuild = prog(f, d6 - 4, 24);
  const instr = prog(f, d6 + sec(2.3), 6);
  const gpuFire = prog(f, d6 + sec(3.4), 5) * (0.75 + 0.25 * Math.sin((f - d6) * 0.9));
  const dieOut = prog(f, d7 - 6, 12);
  // D7–D8：结论
  const notLine = prog(f, d7 + sec(0.3), 10);
  const strike = prog(f, d7 + sec(2.2), 10, ease);
  const claimUp = prog(f, d8, 12, easeIO);
  const gridIn = prog(f, d8 + 12, 8);                    // 标题升到顶以后，两块方阵才出现（不和标题叠）
  const fit = prog(f, d8 + sec(0.9), 22, easeIO);
  const fitFlash = prog(f, d8 + sec(1.75), 4) * (1 - prog(f, d8 + sec(2.6), 14));
  const endTxt = prog(f, d8 + sec(1.9), 12);

  const topTerms: [string, string][] = NV.map((v, i) => [f2(v), f2(LV[i])]);
  const botTerms: [string, string][] = [['2', '4'], ['3', '5']];

  return (
    <AbsoluteFill style={{background: C.bg, transform: `translateX(${(1 - slideIn) * 1080}px)`}}>
      {/* D1–D4 */}
      <Drift from={from}>
      {partOut < 1 && (
        <AbsoluteFill style={{opacity: 1 - partOut}}>
          <div style={{position: 'absolute', left: 40, right: 40, top: lerp(300, 560, merge), height: 340, borderRadius: 22, border: `3px solid ${C.game}`, opacity: topIn * (1 - merge),
            background: 'rgba(240,160,64,0.05)'}}>
            <div style={{position: 'absolute', left: 30, top: 24, fontFamily: FONT.hei, fontWeight: 700, fontSize: 38, color: C.game}}>游戏 · 算一块的亮度</div>
            <div style={{position: 'absolute', left: 0, right: 0, top: 150}}>
              <Formula terms={topTerms} result={f2(SUM)} color={C.game} hiMul={mulTop} plus={plusTop} box={boxK} size={37} />
            </div>
            <div style={{position: 'absolute', left: 30, top: 250, fontFamily: FONT.num, fontSize: 28, color: C.sub, opacity: 1 - boxK}}>
              {PROD.map(f2).join(' + ')} = {f2(SUM)}
            </div>
          </div>
          <div style={{position: 'absolute', left: 40, right: 40, top: lerp(780, 560, merge), height: 340, borderRadius: 22, border: `3px solid ${C.ai}`, opacity: botIn * (1 - merge),
            background: 'rgba(104,168,255,0.05)'}}>
            <div style={{position: 'absolute', left: 30, top: 24, fontFamily: FONT.hei, fontWeight: 700, fontSize: 38, color: C.ai}}>AI · 算下一层的一个数（示意数字）</div>
            <div style={{position: 'absolute', left: 0, right: 0, top: 150}}>
              <Formula terms={botTerms} result="23" color={C.ai} hiMul={mulBot} plus={plusBot} box={boxK} size={60} />
            </div>
          </div>
          {/* 合成的那一道：只剩形状 */}
          <div style={{position: 'absolute', left: 0, right: 0, top: lerp(700, 300, batch), opacity: merge, transform: `scale(${lerp(1.15, 1, batch)})`}}>
            <div style={{textAlign: 'center', fontFamily: FONT.hei, fontWeight: 700, fontSize: 44, color: C.ink, marginBottom: 26}}>
              <span style={{color: C.game}}>游戏</span> 和 <span style={{color: C.ai}}>AI</span>：同一个形状
            </div>
            <Formula terms={[['□', '□'], ['□', '□'], ['□', '□']]} result="" color={C.op} hiMul={() => 0} plus={0} box={1} size={80} />
            <div style={{textAlign: 'center', fontFamily: FONT.hei, fontSize: 38, color: C.sub, marginTop: 20}}>成对相乘，再相加 = <b style={{color: C.op}}>乘加</b></div>
          </div>
          {/* 一大批，互不等待 */}
          {batch > 0 && (
            <div style={{position: 'absolute', left: 90, top: 660, width: 900, height: 600, opacity: batch}}>
              {Array.from({length: 8 * 8}, (_, k) => {
                const c = k % 8, r = Math.floor(k / 8);
                const isGame = (c * 7 + r * 3) % 5 < 2;
                const a = prog(f, d4 + sec(1.6) + (c + r) * 1.2, 8);
                return (
                  <div key={k} style={{position: 'absolute', left: c * 112, top: r * 70, width: 100, height: 58, borderRadius: 8, opacity: a,
                    border: `2px solid ${isGame ? C.game : C.ai}`, background: isGame ? `rgba(240,160,64,${0.12 + 0.25 * batchFire})` : `rgba(104,168,255,${0.12 + 0.25 * batchFire})`,
                    fontFamily: FONT.num, fontWeight: 700, fontSize: 28, color: C.ink, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>×+</div>
                );
              })}
            </div>
          )}
          <div style={{position: 'absolute', left: 0, right: 0, top: 1240, textAlign: 'center', fontFamily: FONT.hei, fontWeight: 700, fontSize: 50, color: C.ink, textShadow: '0 2px 12px rgba(0,0,0,0.95)',
            opacity: prog(f, d4 + sec(2.0), 10)}}>同一步里：一大批，<span style={{color: C.op}}>同时算</span>
            <div style={{fontSize: 38, fontWeight: 700, color: C.sub, marginTop: 8}}>步与步之间，仍要按顺序</div></div>
        </AbsoluteFill>
      )}

      {/* D5–D6：两种芯片把面积花在哪（示意） */}
      {cpuIn > 0 && dieOut < 1 && (
        <AbsoluteFill style={{opacity: 1 - dieOut}}>
          <CpuDie f={f} build={cpuIn} active={cpuActive} hiArea={cpuArea} stream={cpuStream} />
          <div style={{position: 'absolute', left: 260, top: 186, fontFamily: FONT.hei, fontSize: 32, color: C.sub, opacity: cpuActive}}>
            8 个核心，也在同时干活（示意）
          </div>
          <div style={{position: 'absolute', left: 100, right: 100, top: 760, textAlign: 'center', fontFamily: FONT.hei, fontWeight: 700, fontSize: 40, color: C.ink,
            opacity: prog(f, d5b + sec(2.9), 10) * (1 - gpuBuild)}}>
            每个核心可以各干各的，<span style={{color: C.game}}>随时分支</span>
          </div>
          {gpuBuild > 0 && <GpuDie f={f} build={gpuBuild} fire={gpuFire} instr={instr} />}
          {instr > 0 && (
            <div style={{position: 'absolute', left: GPU_BOX.x + 120, top: GPU_BOX.y - 66, display: 'flex', alignItems: 'center', gap: 16, opacity: instr}}>
              <span style={{fontFamily: FONT.hei, fontWeight: 700, fontSize: 32, color: '#111', background: C.op, padding: '4px 16px', borderRadius: 8}}>一条指令：乘加</span>
              <span style={{fontFamily: FONT.hei, fontSize: 32, color: C.game, opacity: prog(f, d6 + sec(3.3), 8)}}>→ 一大批数据同时算</span>
            </div>
          )}
          <Note top={1490} opacity={prog(f, d5b, 10) * 0.9}>面积比例为示意；GPU 也不是什么活都比 CPU 快</Note>
        </AbsoluteFill>
      )}

      {/* D7–D8：结论 */}
      {notLine > 0 && (
        <AbsoluteFill>
          <div style={{position: 'absolute', left: 0, right: 0, top: lerp(560, 300, claimUp), textAlign: 'center', fontFamily: FONT.title, color: C.ink, opacity: notLine}}>
            <div style={{fontSize: 100}}>GPU 擅长 AI</div>
            <div style={{position: 'relative', display: 'inline-block', fontSize: 76, color: C.sub, marginTop: 20}}>
              不是因为它会画游戏
              <div style={{position: 'absolute', left: -10, top: '54%', height: 8, width: `${strike * 104}%`, background: C.warn, borderRadius: 4}} />
            </div>
          </div>
          {claimUp > 0 && (
            <>
              {/* GPU 的运算单元阵列（下）和一批 AI 的乘加（上，落下来正好对上） */}
              <div style={{position: 'absolute', left: 140, top: 850, width: 800, height: 420, borderRadius: 14, border: `3px solid ${C.ink}`, opacity: gridIn, background: '#101216'}}>
                {Array.from({length: 8 * 4}, (_, k) => {
                  const c = k % 8, r = Math.floor(k / 8);
                  return <div key={k} style={{position: 'absolute', left: 22 + c * 96, top: 24 + r * 98, width: 84, height: 84, borderRadius: 6,
                    background: fitFlash > 0 ? `rgba(240,160,64,${0.3 + 0.7 * fitFlash})` : fit > 0.98 ? 'rgba(240,160,64,0.45)' : '#5A4325'}} />;
                })}
                <div style={{position: 'absolute', left: 20, top: -56, fontFamily: FONT.hei, fontWeight: 700, fontSize: 36, color: C.ink}}>GPU 的运算单元</div>
              </div>
              <div style={{position: 'absolute', left: 140, top: lerp(560, 850, fit), width: 800, height: 420, opacity: gridIn * (fit < 0.99 ? 1 : 1 - fitFlash * 0.5)}}>
                {Array.from({length: 8 * 4}, (_, k) => {
                  const c = k % 8, r = Math.floor(k / 8);
                  return <div key={k} style={{position: 'absolute', left: 22 + c * 96, top: 24 + r * 98, width: 84, height: 84, borderRadius: 6, border: `3px solid ${C.ai}`,
                    background: 'rgba(104,168,255,0.18)', fontFamily: FONT.num, fontWeight: 700, fontSize: 30, color: C.ink, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>×+</div>;
                })}
                <div style={{position: 'absolute', left: 20, top: -56, fontFamily: FONT.hei, fontWeight: 700, fontSize: 36, color: C.ai, opacity: 1 - fit}}>AI 的一批乘加</div>
              </div>
              <div style={{position: 'absolute', left: 0, right: 0, top: 640, textAlign: 'center', fontFamily: FONT.hei, fontWeight: 700, fontSize: 46, color: C.ink, opacity: endTxt}}>
                <span style={{color: C.ai}}>AI 的很多计算</span>，正好是 GPU 擅长的形状
              </div>
            </>
          )}
        </AbsoluteFill>
      )}
      </Drift>
    </AbsoluteFill>
  );
};
