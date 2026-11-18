import {AbsoluteFill, Sequence, useCurrentFrame} from 'remotion';
import rack from '../anchors/RACK.json';
import srv from '../anchors/SERVER.json';
import {C, FONT} from '../lib/theme';
import {cue, ease, easeIO, lerp, prog, sec} from '../lib/time';
import {Note, Plate} from '../lib/ui';

// H 段（下一个瓶颈 + 收尾）：
// H1–H3 服务器里的 8 块 GPU 从真实位置「变形」成一张大示意图：各自算 → 经互连交换数据 → 传得快 / 传得慢 两条时间线对比（慢了就等）
// H4–H9 写实：一台服务器 → 机柜 → 一排排机柜（Blender 灰模级底片）；连线只画在机柜层面（服务器 → 柜顶交换机 → 柜与柜之间），不碰芯片
// → 回到开头的问题 → 计算 · 存储 · 通信 → 片尾卡：下一集 GPU 之间怎么「说话」
type P = number[];
const TILE = {w: 400, h: 200, gapX: 120, gapY: 34, x0: 80, y0: 300};
const tileXY = (i: number) => ({x: TILE.x0 + (i % 2) * (TILE.w + TILE.gapX), y: TILE.y0 + Math.floor(i / 2) * (TILE.h + TILE.gapY)});
const HUB = {x: TILE.x0 + TILE.w + 10, w: TILE.gapX - 20};

export const SeqH: React.FC<{from: number}> = ({from}) => {
  const f = useCurrentFrame() + from;
  const h2 = cue('H2'), h3 = cue('H3'), h4 = cue('H4'), h5 = cue('H5'), h6 = cue('H6'), h7 = cue('H7'), h8 = cue('H8'), h9 = cue('H9'), h10 = cue('H10'), h11 = cue('H11');
  const t = (f - from) / 30;
  // 8 块 GPU：从 G 段最后一帧的真实位置长出来
  const last = srv.frames[srv.frames.length - 1] as {mods: P[]};
  const grow = prog(f, from, 18, easeIO);
  const compute = (i: number) => (Math.floor(t * 3 + i * 0.7) % 3 !== 0 ? 1 : 0.4);
  const exch = prog(f, h2 + sec(1.1), 10) * (1 - prog(f, h3, 10));
  const timelines = prog(f, h3 + sec(0.2), 16, easeIO);
  const schemOut = prog(f, h4 - 6, 12);
  // 写实：服务器 → 机柜 → 一排排机柜
  const RSTART = h4 - 6;
  const rRate = (rack.frames.length - 1) / Math.max(1, h10 - RSTART);
  const rf = rack.frames[Math.max(0, Math.min(rack.frames.length - 1, Math.floor((f - RSTART) * rRate)))] as {tops: P[]; servers: P[]};
  const linksA = prog(f, h4 + sec(0.6), 14);
  const linksB = prog(f, h5, 30);
  const q7 = prog(f, h7, 10) * (1 - prog(f, h10 - 4, 8));
  const a8 = prog(f, h8 + sec(0.4), 10) * (1 - prog(f, h10 - 4, 8));
  const tri = (k: number) => prog(f, h9 + sec(2.2 + k * 0.45), 8) * (1 - prog(f, h10 - 4, 8));
  const card = prog(f, h10, 14);
  const inView = (p: P) => p[2] > 0.05 && p[0] > -0.1 && p[0] < 1.1 && p[1] > -0.1 && p[1] < 1.1;
  const px = (p: P) => [p[0] * 1080, p[1] * 1920];

  return (
    <AbsoluteFill style={{background: C.bg}}>
      {/* 写实：一排排机柜 */}
      {f >= RSTART && (
        <Sequence from={RSTART - from} layout="none">
          <AbsoluteFill style={{opacity: schemOut * (1 - card), transform: `scale(${1 + 0.006 * Math.max(0, f - h6) / 30})`, transformOrigin: '50% 40%'}}>
            <Plate name="RACK" rate={rRate} />
            <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(8,9,11,0.7) 0%, rgba(8,9,11,0.1) 30%, rgba(8,9,11,0) 62%, rgba(8,9,11,0.6) 100%)'}} />
            <svg width={1080} height={1920} style={{position: 'absolute', left: 0, top: 0}}>
              {/* 服务器 → 本机柜顶上的交换机 */}
              {rf.servers.map((s, k) => {
                const ti = Math.floor(k / 4);
                const tp = rf.tops[ti];
                if (!inView(s) || !inView(tp)) return null;
                const a = px(s), b = px(tp);
                return <line key={'s' + k} x1={a[0]} y1={a[1]} x2={b[0]} y2={b[1]} stroke={C.ai} strokeWidth={3} opacity={0.75 * linksA} />;
              })}
              {/* 机柜与机柜之间：沿着顶上的线槽 */}
              {rf.tops.map((tp, k) => {
                const nx = rf.tops[k + 1];
                if (!nx || k === 13 || !inView(tp) || !inView(nx)) return null;
                const a = px(tp), b = px(nx);
                const lit = prog(f, h5 + (k % 14) * 1.5, 8) * linksB;
                const u = (((f - h5) / 26 + k * 0.17) % 1);
                return (
                  <g key={'t' + k}>
                    <line x1={a[0]} y1={a[1]} x2={b[0]} y2={b[1]} stroke={C.ai} strokeWidth={5} opacity={lit} />
                    {lit > 0.5 && <circle cx={lerp(a[0], b[0], u)} cy={lerp(a[1], b[1], u)} r={8} fill={C.ink} opacity={lit} />}
                  </g>
                );
              })}
              {/* 跨过通道：两排机柜顶部之间（走顶上的线槽） */}
              {[2, 6, 10].map((k) => {
                const a = rf.tops[k], b = rf.tops[14 + k];
                if (!inView(a) || !inView(b)) return null;
                const A = px(a), B = px(b);
                return <path key={'x' + k} d={`M${A[0]},${A[1]} Q ${(A[0] + B[0]) / 2},${Math.min(A[1], B[1]) - 120} ${B[0]},${B[1]}`} fill="none" stroke={C.ai} strokeWidth={5} opacity={linksB * 0.9} />;
              })}
              {rf.tops.map((tp, k) => inView(tp) && <circle key={'c' + k} cx={px(tp)[0]} cy={px(tp)[1]} r={9} fill={C.ai} opacity={linksA} />)}
            </svg>
            {/* 回到开头的问题 + 答案 */}
            <div style={{position: 'absolute', left: 0, right: 0, top: 200, textAlign: 'center', fontFamily: FONT.title, fontSize: 104, color: C.ink, opacity: q7,
              textShadow: '0 4px 28px rgba(0,0,0,0.95)'}}>AI 为什么需要 <span style={{color: C.ai}}>GPU</span>？</div>
            <div style={{position: 'absolute', left: 0, right: 0, top: 350, textAlign: 'center', fontFamily: FONT.hei, fontWeight: 700, fontSize: 50, color: C.game, opacity: a8,
              textShadow: '0 2px 14px rgba(0,0,0,0.95)'}}>大量可以并行的数值计算</div>
            <div style={{position: 'absolute', left: 0, right: 0, top: 1150, display: 'flex', justifyContent: 'center', gap: 34}}>
              {[['计算', C.game], ['存储', '#9C7BD8'], ['通信', C.ai]].map(([w, c], k) => (
                <div key={k} style={{opacity: tri(k), transform: `scale(${lerp(0.8, 1, tri(k))})`, fontFamily: FONT.title, fontSize: 84, color: c as string,
                  padding: '10px 34px', borderRadius: 20, border: `4px solid ${c}`, background: 'rgba(10,11,13,0.82)'}}>{w}</div>
              ))}
            </div>
          </AbsoluteFill>
        </Sequence>
      )}

      {/* H1–H3：服务器里的 8 块 GPU */}
      {schemOut < 1 && (
        <AbsoluteFill style={{opacity: 1 - schemOut}}>
          {/* 互连（示意） */}
          <div style={{position: 'absolute', left: HUB.x, top: TILE.y0, width: HUB.w, height: 4 * TILE.h + 3 * TILE.gapY, borderRadius: 16,
            background: 'rgba(104,168,255,0.12)', border: `3px solid ${C.ai}`, opacity: grow * (1 - timelines * 0.4)}}>
            <div style={{position: 'absolute', left: 0, right: 0, top: '44%', textAlign: 'center', fontFamily: FONT.hei, fontWeight: 700, fontSize: 32, color: C.ai, writingMode: 'vertical-rl', margin: '0 auto'}}>互连</div>
          </div>
          {Array.from({length: 8}, (_, i) => {
            const src = last.mods[i] ? px(last.mods[i]) : [540, 900];
            const p = tileXY(i);
            const s = lerp(0.18, 1, grow);
            const X = lerp(src[0] - TILE.w / 2, p.x, grow), Y = lerp(src[1] - TILE.h / 2, p.y, grow);
            const shrink = lerp(1, 0.5, timelines);
            return (
              <div key={i} style={{position: 'absolute', left: X, top: lerp(Y, 230 + Math.floor(i / 2) * 118, timelines), width: TILE.w * s, height: TILE.h * s * shrink, borderRadius: 18,
                border: `4px solid ${C.ink}`, background: '#16191E', overflow: 'hidden'}}>
                <div style={{position: 'absolute', left: 18, top: 10, fontFamily: FONT.hei, fontWeight: 700, fontSize: 34 * shrink, color: C.ink}}>GPU {i + 1}</div>
                {Array.from({length: 12}, (_, k) => (
                  <div key={k} style={{position: 'absolute', left: 18 + (k % 6) * 60, top: 60 * shrink + Math.floor(k / 6) * 62 * shrink, width: 50, height: 50 * shrink, borderRadius: 8,
                    background: compute(i + k) > 0.5 && exch < 0.5 ? 'rgba(240,160,64,0.75)' : '#3A2E1C'}} />
                ))}
              </div>
            );
          })}
          {/* 交换数据：数据块经互连从一块 GPU 送到另一块 */}
          {exch > 0 && Array.from({length: 8}, (_, i) => {
            const a = tileXY(i), b = tileXY((i + 3) % 8);
            const u = ((t * 0.9 + i * 0.13) % 1);
            const ax = a.x + (i % 2 ? 0 : TILE.w), bx = b.x + ((i + 3) % 2 ? 0 : TILE.w);
            const midX = HUB.x + HUB.w / 2;
            const x = u < 0.5 ? lerp(ax, midX, u * 2) : lerp(midX, bx, (u - 0.5) * 2);
            const y = u < 0.5 ? lerp(a.y + TILE.h / 2, (a.y + b.y) / 2 + TILE.h / 2, u * 2) : lerp((a.y + b.y) / 2 + TILE.h / 2, b.y + TILE.h / 2, (u - 0.5) * 2);
            return <div key={i} style={{position: 'absolute', left: x - 22, top: y - 22, width: 44, height: 44, borderRadius: 8, background: C.ai, border: `3px solid ${C.ink}`, opacity: exch}} />;
          })}
          {/* H3：传得快 / 传得慢 */}
          {timelines > 0 && (
            <div style={{position: 'absolute', left: 60, top: 760, width: 960, opacity: timelines}}>
              {[['芯片之间传得快', 0.18], ['芯片之间传得慢', 0.62]].map(([lab, ex], row) => (
                <div key={row} style={{position: 'relative', height: 250}}>
                  <div style={{fontFamily: FONT.hei, fontWeight: 700, fontSize: 42, color: C.ink, marginBottom: 14}}>{lab}</div>
                  {Array.from({length: 4}, (_, k) => {
                    const seg = 1 / 4, comp = seg * (1 - (ex as number)), wait = seg * (ex as number);
                    const reveal = prog(f, h3 + sec(0.6 + row * 0.6), sec(1.6), (x) => x);
                    return (
                      <div key={k} style={{position: 'absolute', left: k * seg * 960, top: 66, width: seg * 960 * reveal, height: 110, display: 'flex', overflow: 'hidden', borderRadius: 10}}>
                        <div style={{width: `${(comp / seg) * 100}%`, background: 'rgba(240,160,64,0.85)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: FONT.hei, fontWeight: 700, fontSize: 30, color: '#111'}}>{k === 0 ? '算' : ''}</div>
                        <div style={{width: `${(wait / seg) * 100}%`, background: row === 1 ? '#4A4F57' : C.ai, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: FONT.hei, fontWeight: 700, fontSize: 30, color: C.ink}}>{k === 0 ? (row === 1 ? '等' : '传') : ''}</div>
                      </div>
                    );
                  })}
                </div>
              ))}
            </div>
          )}
          <Note top={1490} opacity={grow * 0.9}>示意：服务器里 GPU 之间的互连；具体连法因系统而异</Note>
        </AbsoluteFill>
      )}

      {/* 片尾卡 */}
      {card > 0 && (
        <AbsoluteFill style={{opacity: card, background: C.bg}}>
          <svg width={1080} height={1920} style={{position: 'absolute', left: 0, top: 0}}>
            {[300, 780].map((x, k) => (
              <g key={k}>
                <rect x={x - 110} y={560} width={220} height={220} rx={26} fill="#16191E" stroke={C.ink} strokeWidth={5} />
                <rect x={x - 70} y={600} width={140} height={140} rx={12} fill="rgba(240,160,64,0.35)" stroke={C.game} strokeWidth={4} />
                <text x={x} y={830} textAnchor="middle" fontFamily="Noto Sans CJK SC" fontWeight={700} fontSize={40} fill={C.ink}>GPU</text>
              </g>
            ))}
            <line x1={410} y1={670} x2={670} y2={670} stroke={C.ai} strokeWidth={6} strokeDasharray="20 14" strokeDashoffset={-f * 2} />
            <rect x={lerp(410, 646, ((f - h10) / 40) % 1)} y={652} width={36} height={36} rx={6} fill={C.ai} />
          </svg>
          <div style={{position: 'absolute', left: 0, right: 0, top: 930, textAlign: 'center', fontFamily: FONT.hei, fontWeight: 700, fontSize: 44, color: C.sub, opacity: card}}>下一集</div>
          <div style={{position: 'absolute', left: 0, right: 0, top: 1000, textAlign: 'center', fontFamily: FONT.title, fontSize: 100, color: C.ink, lineHeight: 1.15, opacity: prog(f, h11, 12)}}>
            GPU 之间<br />怎么「说话」？
          </div>
          <div style={{position: 'absolute', left: 0, right: 0, top: 220, textAlign: 'center', fontFamily: FONT.hei, fontWeight: 700, fontSize: 40, color: C.sub, letterSpacing: 6}}>一语道破 · EP01</div>
          <div style={{position: 'absolute', left: 0, right: 0, top: 285, textAlign: 'center', fontFamily: FONT.hei, fontSize: 40, color: C.dim}}>AI 为什么需要 GPU</div>
        </AbsoluteFill>
      )}
    </AbsoluteFill>
  );
};
