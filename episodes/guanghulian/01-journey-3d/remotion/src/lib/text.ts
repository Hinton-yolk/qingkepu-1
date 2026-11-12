// 文字排版的小工具：量宽度、字幕折两行、把「名字：说明」拆成两行。
import { measureText } from "@remotion/layout-utils";
import { FONT_FAMILY } from "../theme";

export const textWidth = (
  text: string,
  fontSize: number,
  fontWeight: number | string = 400,
) =>
  measureText({
    text,
    fontFamily: FONT_FAMILY,
    fontSize,
    fontWeight: String(fontWeight),
  }).width;

/** 让一行字不超过 maxWidth：返回合适的字号（不超过 base） */
export const fitFontSize = (
  text: string,
  base: number,
  maxWidth: number,
  fontWeight: number | string = 400,
) => {
  const w = textWidth(text, base, fontWeight);
  return w <= maxWidth ? base : Math.floor((base * maxWidth) / w);
};

const BREAK_AFTER = "，。；：、？！,;:!?";
const NO_LINE_START = "，。；：、？！,;:!?”’）》」』%";
const NO_LINE_END = "“‘（《「『";

/** 可以断行的位置（字符下标）：词与词之间。用浏览器自带的中文分词；没有分词器时退到「任意两个字之间」。 */
const wordBreaks = (text: string): Set<number> | null => {
  const Seg = (
    Intl as unknown as {
      Segmenter?: new (
        locale: string,
        opts: { granularity: "word" },
      ) => { segment: (s: string) => Iterable<{ segment: string }> };
    }
  ).Segmenter;
  if (!Seg) return null;
  const out = new Set<number>();
  let n = 0;
  for (const part of new Seg("zh", { granularity: "word" }).segment(text)) {
    n += Array.from(part.segment).length;
    out.add(n);
  }
  return out;
};

/**
 * 字幕 / 角注：一行放得下就一行；放不下折成两行。
 * 只在词与词之间断（不把「转换」这样的词拆开）；优先在靠近中间的标点后面断；不让标点落在行首。
 */
export const splitTwoLines = (
  text: string,
  fontSize: number,
  maxWidth: number,
  fontWeight: number | string = 400,
): string[] => {
  const full = textWidth(text, fontSize, fontWeight);
  if (full <= maxWidth) return [text];
  const chars = Array.from(text);
  const allowed = wordBreaks(text);
  let best: { i: number; score: number } | null = null;
  for (let i = 1; i < chars.length; i++) {
    const prev = chars[i - 1];
    const next = chars[i];
    if (allowed && !allowed.has(i)) continue;
    if (NO_LINE_START.includes(next) || NO_LINE_END.includes(prev)) continue;
    if (/[A-Za-z0-9]/.test(prev) && /[A-Za-z0-9]/.test(next)) continue;
    const left = chars.slice(0, i).join("").trimEnd();
    const right = chars.slice(i).join("").trimStart();
    const wl = textWidth(left, fontSize, fontWeight);
    const wr = textWidth(right, fontSize, fontWeight);
    if (wl > maxWidth || wr > maxWidth) continue;
    // 越均衡越好；在标点后面断有加分
    const balance = Math.abs(wl - wr) / full;
    const score = balance - (BREAK_AFTER.includes(prev) ? 0.45 : 0);
    if (!best || score < best.score) best = { i, score };
  }
  if (!best) return [text]; // 实在分不开：调用方会缩小字号或交给浏览器折行
  return [
    chars.slice(0, best.i).join("").trimEnd(),
    chars.slice(best.i).join("").trimStart(),
  ];
};

/**
 * 把一条短标签拆成「主名 + 说明」两行：
 *   「DSP · 数字信号处理芯片」→ DSP ｜ 数字信号处理芯片
 *   「激光器：稳定的连续光」→ 激光器 ｜ 稳定的连续光
 *   「GPU 芯片（示例结构）」→ GPU 芯片 ｜ （示例结构）
 * 拆不出来就只有一行。
 */
export const splitHeadBody = (
  text: string,
): { head: string; body: string | null } => {
  const dot = text.indexOf(" · ");
  if (dot > 0) return { head: text.slice(0, dot), body: text.slice(dot + 3) };
  const colon = text.indexOf("：");
  if (colon > 0 && colon < text.length - 1) {
    return { head: text.slice(0, colon), body: text.slice(colon + 1) };
  }
  const m = /^(.+?)(（[^（）]+）)$/.exec(text);
  if (m) return { head: m[1], body: m[2] };
  return { head: text, body: null };
};
