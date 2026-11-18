import {useCurrentFrame} from 'remotion';
import {C, FONT} from './lib/theme';
import {FPS, T} from './lib/time';

// 字幕：每句旁白按标点切成 ≤ 15 字的小段，按字数比例分配时间。手机上一行读完。
const MAX = 15;
type Chunk = {text: string; a: number; b: number};

// 显示宽度：汉字算 1，拉丁字母 / 数字 / 空格算 0.55
const vlen = (x: string) => [...x.replace(/[，。：；？！、「」]/g, '')].reduce((n, ch) => n + (/[\x00-\x7f]/.test(ch) ? 0.55 : 1), 0);
// 没有标点、又超长的一段，按显示宽度从中间切开（不切断英文词）
const NOSPLIT = ['大量', '矩阵', '计算', '并行', '任务', '处理', '数据', '芯片', '运算', '神经', '网络', '模型', '数字', '结果', '输出', '规则', '光照', '颜色'];
const cut = (p: string): string[] => {
  if (vlen(p) <= MAX) return [p];
  const n = Math.ceil(vlen(p) / MAX), target = vlen(p) / n;
  const out: string[] = []; let cur = '';
  for (const ch of [...p]) {
    const keep = NOSPLIT.some((w) => (cur.slice(-1) + ch) === w);   // 不在词中间断开
    if (vlen(cur) >= target && out.length < n - 1 && !keep && !/[A-Za-z0-9]/.test(ch) && !/[，。：；？！、]/.test(ch)) { out.push(cur); cur = ''; }
    cur += ch;
  }
  out.push(cur);
  return out;
};
const split = (s: string): string[] => {
  const parts = (s.match(/[^，。：；？！、]+[，。：；？！、]?/g) ?? [s]).flatMap(cut);
  const out: string[] = [];
  let cur = '';
  for (const p of parts) {
    const len = vlen;
    if (cur && (len(cur + p) > MAX || /。$/.test(cur))) {
      out.push(cur);
      cur = p;
    } else cur += p;
  }
  if (cur) out.push(cur);
  return out;
};
const clean = (s: string) => s.replace(/[，。；、：]$/g, '').replace(/^[，。；、：]/, '');

// v03：开头两句就是画面上的大字问题，不再重复出字幕
const HIDE = ['A1', 'A2'];
const CHUNKS: Chunk[] = T.lines.filter((l) => !HIDE.includes(l.id)).flatMap((l) => {
  const ps = split(l.text);
  const w = ps.map((p) => Math.max(1, p.replace(/[，。：；？！、「」\s]/g, '').length));
  const tot = w.reduce((x, y) => x + y, 0);
  let t = l.start;
  return ps.map((p, i) => {
    const d = ((l.end - l.start) * w[i]) / tot;
    const c = {text: clean(p), a: t, b: t + d};
    t += d;
    return c;
  });
});

export const Captions: React.FC<{hideIds?: string[]}> = () => {
  const f = useCurrentFrame();
  const t = f / FPS;
  const c = CHUNKS.find((x) => t >= x.a - 0.05 && t < x.b + 0.12);
  if (!c) return null;
  const k = Math.min(1, (t - (c.a - 0.05)) / 0.1);
  return (
    <div style={{position: 'absolute', left: 60, right: 60, top: 1398, display: 'flex', justifyContent: 'center', pointerEvents: 'none'}}>
      <div
        style={{
          fontFamily: FONT.hei, fontWeight: 700, fontSize: 52, lineHeight: 1.25, color: C.ink, letterSpacing: 1,
          textAlign: 'center', opacity: k,
          textShadow: '0 2px 6px rgba(0,0,0,0.9), 0 0 18px rgba(0,0,0,0.65)',
          padding: '6px 22px', background: 'rgba(10,11,13,0.42)', borderRadius: 10,
        }}
      >
        {c.text}
      </div>
    </div>
  );
};
