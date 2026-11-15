// path_trace 的几何：把 anchors JSON 里沿路线取样的点连成折线，分段上色，并算出「电 / 光」几个字放哪。
// 锚点名的约定见 shotConfig.PATH_TRACE。全是纯函数：同一帧每次算出来都一样。
import { HOOK_BOX, PATH_TRACE } from "../shotConfig";
import { H, PANEL_BOTTOM, SAFE, W } from "../theme";
import {
  clampRect,
  clipPolyline,
  inflate,
  intersects,
  pointAtLength,
  polyLength,
  Pt,
  Rect,
} from "./geom";
import { anchorNameList, anchorSample } from "./manifest";

export type PathKind = "electric" | "light";
export type PathSection = { id: string; kind: PathKind; names: string[] };

const RE = /^path_([a-z]+\d*)_(\d+)$/i;

const sectionCache: Record<string, PathSection[]> = {};

/** 该镜头的路线分几段、每段有哪些取样点（按序号排好）。没有 path_* 锚点时是空数组。 */
export const pathSections = (shotId: string): PathSection[] => {
  if (!sectionCache[shotId]) {
    const by: Record<string, { n: number; name: string }[]> = {};
    for (const name of anchorNameList(shotId)) {
      const m = RE.exec(name);
      if (!m) continue;
      (by[m[1].toLowerCase()] ??= []).push({ n: parseInt(m[2], 10), name });
    }
    const order = PATH_TRACE.sectionOrder;
    const rank = (id: string) => {
      const i = order.indexOf(id);
      return i < 0 ? order.length : i;
    };
    sectionCache[shotId] = Object.keys(by)
      .sort((a, b) => rank(a) - rank(b) || a.localeCompare(b))
      .map((id) => ({
        id,
        kind: id.startsWith("o") ? "light" : "electric",
        names: by[id].sort((a, b) => a.n - b.n).map((p) => p.name),
      }));
  }
  return sectionCache[shotId];
};

/** 一小段可以画的折线（已裁到画面附近），属于第 section 段 */
export type PathPiece = { section: number; pts: Pt[]; len: number };

export type PathGeometry = {
  sections: PathSection[];
  pieces: PathPiece[]; // 按 A → B 的顺序
  total: number; // 所有小段的总长（屏幕像素）
  /** 每一段：在整条线上从多长开始、自己多长 */
  spans: { start: number; len: number }[];
};

// 画线用的范围：比画面略大一圈。贴近相机的点投影后可能跑到几万像素外，裁掉以后「画到哪了」才是按看得见的长度算的。
const VIEW: Rect = { x: -60, y: -60, w: W + 120, h: H + 120 };

/**
 * 某一帧的路线折线。
 *   - z ≤ 0（在相机背后）的点跳过；折线在那里断开，不把它两边的点直接连起来（那样会凭空横穿画面）。
 *   - 相邻两段之间如果首尾没有重合，用前一段的颜色把缝补上。
 */
export const pathGeometry = (shotId: string, film: number): PathGeometry => {
  const sections = pathSections(shotId);
  const pieces: PathPiece[] = [];
  const spans: { start: number; len: number }[] = [];
  let total = 0;

  sections.forEach((sec, si) => {
    const samples = sec.names.map((n) => anchorSample(shotId, n, film));
    // 补缝：下一段的第一个点
    const next = sections[si + 1];
    if (next && next.names.length > 0) {
      samples.push(anchorSample(shotId, next.names[0], film));
    }
    const runs: Pt[][] = [];
    let cur: Pt[] = [];
    for (const s of samples) {
      if (!s || !s.front) {
        if (cur.length > 1) runs.push(cur);
        cur = [];
        continue;
      }
      const last = cur[cur.length - 1];
      if (last && Math.hypot(last.x - s.x, last.y - s.y) < 0.5) continue;
      cur.push({ x: s.x, y: s.y });
    }
    if (cur.length > 1) runs.push(cur);

    const start = total;
    for (const run of runs) {
      for (const pts of clipPolyline(run, VIEW)) {
        const len = polyLength(pts);
        if (len < 0.5) continue;
        pieces.push({ section: si, pts, len });
        total += len;
      }
    }
    spans.push({ start, len: total - start });
  });

  return { sections, pieces, total, spans };
};

export type PathChip = {
  section: number;
  rect: Rect;
  /** 这一段在整条线上的中点位置（长度）：线画到这里，字才出现 */
  at: number;
};

/**
 * 「电 / 光 / 电」每个字放哪：各段落在内容区里那一部分的中点旁边，离线 charGap 远，不压线。
 * 这一段不在内容区里（出画、被五站条或字幕带挡住）就不放。
 * hookActive：开头大字在场时让开它。sizes[i] = 第 i 个字的衬底大小。
 */
export const pathChips = (
  geo: PathGeometry,
  sizes: { w: number; h: number }[],
  hookActive: boolean,
): PathChip[] => {
  const bounds: Rect = {
    x: SAFE.left,
    y: SAFE.top,
    w: SAFE.width,
    h: PANEL_BOTTOM - SAFE.top,
  };
  const place = inflate(bounds, -30);
  const hook = inflate(HOOK_BOX, 10);
  const out: PathChip[] = [];

  geo.sections.forEach((_, si) => {
    const size = sizes[si];
    if (!size) return;
    // 这一段落在内容区里的部分
    const parts = geo.pieces
      .filter((p) => p.section === si)
      .flatMap((p) => clipPolyline(p.pts, place));
    const lens = parts.map(polyLength);
    const sum = lens.reduce((a, b) => a + b, 0);
    if (sum < 24) return;
    let rest = sum / 2;
    let k = 0;
    while (k < parts.length - 1 && rest > lens[k]) {
      rest -= lens[k];
      k++;
    }
    const { p, tx, ty } = pointAtLength(parts[k], rest);

    // 往线的哪一侧放：线比较平就放上面；线比较竖就放靠画面中间的一侧
    let nx = -ty;
    let ny = tx;
    if (Math.abs(ny) > 0.35 ? ny > 0 : (W / 2 - p.x) * nx < 0) {
      nx = -nx;
      ny = -ny;
    }
    const rectFor = (sx: number, sy: number): Rect =>
      clampRect(
        {
          x: p.x + sx * PATH_TRACE.charGap - size.w / 2,
          y: p.y + sy * PATH_TRACE.charGap - size.h / 2,
          w: size.w,
          h: size.h,
        },
        bounds,
      );
    const busy = (r: Rect) =>
      (hookActive && intersects(r, hook)) ||
      out.some((c) => intersects(inflate(r, 6), c.rect));
    let rect = rectFor(nx, ny);
    if (busy(rect)) {
      const flipped = rectFor(-nx, -ny);
      if (!busy(flipped)) rect = flipped;
      else if (hookActive && intersects(rect, hook)) {
        // 两侧都压到大字：挪到大字上面
        rect = clampRect({ ...rect, y: hook.y - size.h - 4 }, bounds);
      }
    }
    const span = geo.spans[si];
    out.push({ section: si, rect, at: span.start + span.len / 2 });
  });
  return out;
};
