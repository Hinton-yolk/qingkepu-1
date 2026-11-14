// 版式用的平面几何小工具：矩形、线段裁剪、折线长度。都是纯函数。
export type Pt = { x: number; y: number };
export type Rect = { x: number; y: number; w: number; h: number };

export const inflate = (r: Rect, d: number): Rect => ({
  x: r.x - d,
  y: r.y - d,
  w: r.w + d * 2,
  h: r.h + d * 2,
});

export const intersects = (a: Rect, b: Rect) =>
  a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h;

export const overlapArea = (a: Rect, b: Rect) => {
  const w = Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x);
  const h = Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y);
  return w > 0 && h > 0 ? w * h : 0;
};

export const contains = (r: Rect, p: Pt) =>
  p.x >= r.x && p.x <= r.x + r.w && p.y >= r.y && p.y <= r.y + r.h;

/** 把 r 整块挪进 bounds 里（r 比 bounds 大时贴左上） */
export const clampRect = (r: Rect, bounds: Rect): Rect => ({
  ...r,
  x: Math.max(bounds.x, Math.min(bounds.x + bounds.w - r.w, r.x)),
  y: Math.max(bounds.y, Math.min(bounds.y + bounds.h - r.h, r.y)),
});

export const inside = (r: Rect, bounds: Rect) =>
  r.x >= bounds.x - 0.5 &&
  r.y >= bounds.y - 0.5 &&
  r.x + r.w <= bounds.x + bounds.w + 0.5 &&
  r.y + r.h <= bounds.y + bounds.h + 0.5;

/** 矩形边框上离 p 最近的点（p 在矩形外时） */
export const closestOnRect = (r: Rect, p: Pt): Pt => ({
  x: Math.max(r.x, Math.min(r.x + r.w, p.x)),
  y: Math.max(r.y, Math.min(r.y + r.h, p.y)),
});

/** 线段 pq 裁到矩形里（Liang–Barsky）；完全在外面返回 null */
export const clipSegment = (p: Pt, q: Pt, r: Rect): [Pt, Pt] | null => {
  const dx = q.x - p.x;
  const dy = q.y - p.y;
  let t0 = 0;
  let t1 = 1;
  const edges: [number, number][] = [
    [-dx, p.x - r.x],
    [dx, r.x + r.w - p.x],
    [-dy, p.y - r.y],
    [dy, r.y + r.h - p.y],
  ];
  for (const [pp, qq] of edges) {
    if (pp === 0) {
      if (qq < 0) return null;
      continue;
    }
    const t = qq / pp;
    if (pp < 0) {
      if (t > t1) return null;
      if (t > t0) t0 = t;
    } else {
      if (t < t0) return null;
      if (t < t1) t1 = t;
    }
  }
  return [
    { x: p.x + dx * t0, y: p.y + dy * t0 },
    { x: p.x + dx * t1, y: p.y + dy * t1 },
  ];
};

/** 折线裁到矩形里：可能被切成几段 */
export const clipPolyline = (pts: Pt[], r: Rect): Pt[][] => {
  const out: Pt[][] = [];
  let cur: Pt[] = [];
  for (let i = 0; i < pts.length - 1; i++) {
    const c = clipSegment(pts[i], pts[i + 1], r);
    if (!c) {
      if (cur.length > 1) out.push(cur);
      cur = [];
      continue;
    }
    const [a, b] = c;
    const last = cur[cur.length - 1];
    if (!last || Math.hypot(last.x - a.x, last.y - a.y) > 0.01) {
      if (cur.length > 1) out.push(cur);
      cur = [a];
    }
    cur.push(b);
  }
  if (cur.length > 1) out.push(cur);
  return out;
};

export const polyLength = (pts: Pt[]) => {
  let s = 0;
  for (let i = 0; i < pts.length - 1; i++)
    s += Math.hypot(pts[i + 1].x - pts[i].x, pts[i + 1].y - pts[i].y);
  return s;
};

/** 折线上离起点 d 远的那一点，和那里的方向（单位向量） */
export const pointAtLength = (
  pts: Pt[],
  d: number,
): { p: Pt; tx: number; ty: number } => {
  let rest = Math.max(0, d);
  for (let i = 0; i < pts.length - 1; i++) {
    const a = pts[i];
    const b = pts[i + 1];
    const len = Math.hypot(b.x - a.x, b.y - a.y);
    if (len < 1e-6) continue;
    if (rest <= len || i === pts.length - 2) {
      const u = Math.min(1, rest / len);
      return {
        p: { x: a.x + (b.x - a.x) * u, y: a.y + (b.y - a.y) * u },
        tx: (b.x - a.x) / len,
        ty: (b.y - a.y) / len,
      };
    }
    rest -= len;
  }
  return { p: pts[0], tx: 1, ty: 0 };
};

/** 折线从起点起的前 d 长 */
export const truncatePolyline = (pts: Pt[], d: number): Pt[] => {
  const out: Pt[] = [pts[0]];
  let rest = d;
  for (let i = 0; i < pts.length - 1; i++) {
    const a = pts[i];
    const b = pts[i + 1];
    const len = Math.hypot(b.x - a.x, b.y - a.y);
    if (rest >= len) {
      out.push(b);
      rest -= len;
      continue;
    }
    if (rest > 0) {
      const u = rest / len;
      out.push({ x: a.x + (b.x - a.x) * u, y: a.y + (b.y - a.y) * u });
    }
    break;
  }
  return out;
};

export const toPathD = (pts: Pt[]) =>
  pts
    .map((p, i) => `${i === 0 ? "M" : "L"}${p.x.toFixed(1)} ${p.y.toFixed(1)}`)
    .join(" ");
