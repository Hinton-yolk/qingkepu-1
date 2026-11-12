// 一个镜头里各块叠加内容怎么互相让位。全部由 timeline.json + 锚点数据算出来，没有状态：
//   角注叠多高 → 图表面板的下沿往上让 → 标签不能低于面板上沿 / 角注上沿
//   标签停在锚点旁边：不挡锚点、不压开头大字、不压路线上的字、互相不压，同一时刻最多 MAX_LABELS 个
import {
  DEFAULT_SLOTS,
  HOOK_BOX,
  LABEL_GAP,
  LABEL_LOST_FADE,
  LABEL_NEAR_MARGIN,
  LabelSlot,
  MAX_LABELS,
  PANEL_HEIGHT,
  panelRect,
  SCALE_ONLY_WHEN_PLACEHOLDER,
  SHOT_SLOTS,
  WAVEFORM_VARIANT,
} from "../shotConfig";
import { H, PANEL_BOTTOM, SAFE, SIZE, W } from "../theme";
import { Overlay, Shot, toFrame } from "../timeline";
import {
  clampRect,
  contains,
  inflate,
  inside,
  overlapArea,
  Pt,
  Rect,
} from "./geom";
import { anchorSample, hasFrames, resolveAnchorName } from "./manifest";
import { pathChips, pathGeometry, pathSections } from "./pathTrace";
import { splitHeadBody, splitTwoLines, textWidth } from "./text";

const PANELS = ["waveform", "timing_diagram", "gauge"];
const ANCHORED = ["label", "term", "scale", "alert"];

/** 标注在镜头内的起止帧 [from, to) */
export const localSpan = (shot: Shot, o: Overlay) => {
  const s = toFrame(shot.start);
  return { from: toFrame(o.t) - s, to: toFrame(o.t + o.dur) - s };
};

// ---------- 角注 ----------
export const NOTE = {
  lineH: 38,
  padY: 5,
  padLeft: 14,
  padRight: 14,
  border: 4,
  gap: 6,
  bottom: SAFE.bottom - 4, // 最下面一条的下沿
};
const NOTE_MAX_W = SAFE.width - NOTE.padLeft - NOTE.padRight - NOTE.border;

const noteCache = new WeakMap<
  Overlay,
  { lines: string[]; natural: boolean; height: number }
>();

/** 一条角注怎么折行、占多高。一行放不下折两行；两行也放不下（极长）就交给浏览器自己折。 */
export const measureNote = (o: Overlay) => {
  let m = noteCache.get(o);
  if (!m) {
    const lines = splitTwoLines(o.text, SIZE.note, NOTE_MAX_W);
    const natural = lines.some((l) => textWidth(l, SIZE.note) > NOTE_MAX_W);
    const count = natural
      ? Math.ceil(textWidth(o.text, SIZE.note) / (NOTE_MAX_W * 0.94))
      : lines.length;
    m = { lines, natural, height: count * NOTE.lineH + NOTE.padY * 2 };
    noteCache.set(o, m);
  }
  return m;
};

const notesOf = (shot: Shot) => shot.overlays.filter((o) => o.type === "note");

/** 某一帧在场的角注一共叠多高（没有角注时是 0） */
export const noteStackHeight = (shot: Shot, local: number) => {
  const on = notesOf(shot).filter((n) => {
    const { from, to } = localSpan(shot, n);
    return local >= from && local < to;
  });
  if (on.length === 0) return 0;
  return (
    on.reduce((s, n) => s + measureNote(n).height, 0) +
    NOTE.gap * (on.length - 1)
  );
};

/** [from, to) 这段时间里角注最高叠到多高 */
const maxNoteStack = (shot: Shot, from: number, to: number) => {
  // 高度只在某条角注出现的那一帧变大：查这段的第一帧和其间每条角注的起始帧
  const checks = [
    from,
    ...notesOf(shot)
      .map((n) => localSpan(shot, n).from)
      .filter((f) => f > from && f < to),
  ];
  return Math.max(0, ...checks.map((f) => noteStackHeight(shot, f)));
};

// ---------- 图表面板 ----------
export const isPanel = (o: Overlay) => PANELS.includes(o.type);

const panelHeight = (shot: Shot, o: Overlay) => {
  if (o.type === "waveform")
    return PANEL_HEIGHT[WAVEFORM_VARIANT[shot.id] ?? "degrade"];
  if (o.type === "timing_diagram") return PANEL_HEIGHT.timing_diagram;
  return PANEL_HEIGHT.gauge;
};

/**
 * 这块面板的下沿：默认在角注带上面（PANEL_BOTTOM）；它在场期间角注叠得更高（两三条同时出现）时，整块往上让。
 * 一块面板全程只有一个位置，不会中途跳。
 */
export const panelBottomFor = (shot: Shot, o: Overlay) => {
  const { from, to } = localSpan(shot, o);
  const stack = maxNoteStack(shot, from, to);
  return Math.min(PANEL_BOTTOM, NOTE.bottom - stack - 10);
};

export const panelRectFor = (shot: Shot, o: Overlay): Rect =>
  panelRect(panelHeight(shot, o), panelBottomFor(shot, o));

// ---------- 开头大字、路线上的字（标签要让开的东西） ----------
const hookActiveAt = (shot: Shot, local: number) =>
  shot.overlays.some((o) => {
    if (o.type !== "hook_title") return false;
    const { from, to } = localSpan(shot, o);
    return local >= from && local < to;
  });

export const PATH_CHIP = { padX: 14, h: 62 };

/** 路线文案拆成几个字：「电 → 光 → 电」→ ["电", "光", "电"] */
export const pathWords = (o: Overlay) => {
  const colon = o.text.indexOf("：");
  return (colon >= 0 ? o.text.slice(colon + 1) : o.text)
    .split("→")
    .map((s) => s.trim())
    .filter((s) => s.length > 0);
};

export const pathChipSizes = (o: Overlay) =>
  pathWords(o).map((w) => ({
    w: Math.ceil(textWidth(w, SIZE.pathChar, 700)) + PATH_CHIP.padX * 2,
    h: PATH_CHIP.h,
  }));

/** 某一帧路线上那几个字的位置（没有 path_* 锚点、或这一帧没有路线标注时是空数组） */
export const pathChipsAt = (shot: Shot, local: number) => {
  if (pathSections(shot.id).length === 0) return [];
  const film = toFrame(shot.start) + local + 1;
  return shot.overlays.flatMap((o) => {
    if (o.type !== "path_trace" || !o.text.includes("→")) return [];
    const { from, to } = localSpan(shot, o);
    if (local < from || local >= to) return [];
    return pathChips(
      pathGeometry(shot.id, film),
      pathChipSizes(o),
      hookActiveAt(shot, local),
    );
  });
};

/** 某一帧标签要让开的矩形：开头大字、路线上的字 */
const obstaclesAt = (shot: Shot, local: number): Rect[] => [
  ...(hookActiveAt(shot, local) ? [inflate(HOOK_BOX, 8)] : []),
  ...pathChipsAt(shot, local).map((c) => inflate(c.rect, 6)),
];

/** 引线不往这些东西下面画：开头大字、在场的图表面板（锚点被它们盖住了） */
const coversAt = (shot: Shot, local: number): Rect[] => [
  ...(hookActiveAt(shot, local) ? [HOOK_BOX] : []),
  ...shot.overlays
    .filter((o) => {
      if (!isPanel(o)) return false;
      const { from, to } = localSpan(shot, o);
      return local >= from && local < to;
    })
    .map((o) => panelRectFor(shot, o)),
];

// ---------- 贴物体的标签 ----------
export const LABEL_CHIP = { padX: 16, padY: 9, gap: 2, maxTextW: 640 };

type TextBlock = { size: number; lineH: number; lines: string[]; w: number };

const fitBlock = (
  text: string,
  base: number,
  min: number,
  weight: number,
  lineK: number,
): TextBlock => {
  const maxW = LABEL_CHIP.maxTextW;
  const w = textWidth(text, base, weight);
  let size = base;
  let lines = [text];
  if (w > maxW) {
    size = Math.max(min, Math.floor((base * maxW) / w));
    // 缩到下限还放不下：折两行（只在词之间断）
    if (textWidth(text, size, weight) > maxW)
      lines = splitTwoLines(text, size, maxW, weight);
  }
  return {
    size,
    lineH: Math.round(size * lineK),
    lines,
    w: Math.max(...lines.map((l) => textWidth(l, size, weight))),
  };
};

export type LabelSpec = {
  key: number; // 在 shot.overlays 里的下标
  overlay: Overlay;
  kind: "label" | "term" | "scale" | "alert";
  from: number; // 镜头内帧号
  to: number;
  head: TextBlock;
  body: (TextBlock & { weight: number }) | null;
  w: number;
  h: number;
  anchorName: string | null; // anchors JSON 里对上的锚点名；null = 没对上，用默认位置
  slot: LabelSlot;
  bounds: Rect; // 整块标签不能出这个范围
};

type Cand = {
  id: string;
  place: (a: Pt, w: number, h: number) => { x: number; y: number };
};
const G = LABEL_GAP;
// 先后顺序 = 同样好时优先用哪个
const CANDS: Cand[] = [
  { id: "ru", place: (a, _w, h) => ({ x: a.x + G.dx, y: a.y - G.dy - h }) },
  { id: "lu", place: (a, w, h) => ({ x: a.x - G.dx - w, y: a.y - G.dy - h }) },
  { id: "rd", place: (a) => ({ x: a.x + G.dx, y: a.y + G.dy }) },
  { id: "ld", place: (a, w) => ({ x: a.x - G.dx - w, y: a.y + G.dy }) },
  { id: "u", place: (a, w, h) => ({ x: a.x - w / 2, y: a.y - G.v - h }) },
  { id: "d", place: (a, w) => ({ x: a.x - w / 2, y: a.y + G.v }) },
  { id: "r", place: (a, _w, h) => ({ x: a.x + G.h, y: a.y - h / 2 }) },
  { id: "l", place: (a, w, h) => ({ x: a.x - G.h - w, y: a.y - h / 2 }) },
];

type Plan = {
  cand: Cand;
  /** 每一帧（下标 = 帧号 − from）：用哪一帧的锚点位置（锚点不在画面附近时 = 时间上最近的、在画面附近的那一帧）；-1 = 全程都不在 */
  src: Int32Array;
};

type ShotLabels = { specs: LabelSpec[]; plans: Plan[]; dropped: Overlay[] };
const shotCache = new WeakMap<Shot, ShotLabels>();

const filmOf = (shot: Shot, local: number) => toFrame(shot.start) + local + 1;

/**
 * 标签用的锚点位置。
 *   near     在相机前面，而且在画面内或画面外 LABEL_NEAR_MARGIN 以内：标签还贴着它（物体有大小，原点刚出画时物体多半还看得见）
 *   inFrame  真的在画面内：才画引线
 *   pt       收进画面内的位置（「最近的画面内位置」）
 */
const anchorState = (shot: Shot, spec: LabelSpec, local: number) => {
  const s = spec.anchorName
    ? anchorSample(shot.id, spec.anchorName, filmOf(shot, local))
    : null;
  if (!s)
    return {
      pt: { x: spec.slot.x, y: spec.slot.y },
      near: !spec.anchorName,
      inFrame: false,
    };
  const m = LABEL_NEAR_MARGIN;
  return {
    pt: {
      x: Math.max(0, Math.min(W, s.x)),
      y: Math.max(0, Math.min(H, s.y)),
    },
    near: s.front && s.x >= -m && s.x <= W + m && s.y >= -m && s.y <= H + m,
    inFrame: s.inFrame,
  };
};

const anchorPt = (shot: Shot, spec: LabelSpec, local: number): Pt =>
  anchorState(shot, spec, local).pt;

/** 让标签不挡住自己的锚点：挡住了就往最近的一侧挪开 */
const clearAnchor = (r: Rect, a: Pt, bounds: Rect): Rect => {
  if (!contains(inflate(r, G.clear), a)) return r;
  const moves: Rect[] = [
    { ...r, y: a.y - G.clear - r.h },
    { ...r, y: a.y + G.clear },
    { ...r, x: a.x - G.clear - r.w },
    { ...r, x: a.x + G.clear },
  ].filter((m) => inside(m, bounds));
  if (moves.length === 0) return r;
  const dist = (m: Rect) => Math.abs(m.x - r.x) + Math.abs(m.y - r.y);
  return moves.reduce((best, m) => (dist(m) < dist(best) ? m : best));
};

/** 只看自己：锚点 + 摆法 → 位置（收进范围、不挡锚点） */
const selfRect = (spec: LabelSpec, cand: Cand, a: Pt): Rect => {
  const p = cand.place(a, spec.w, spec.h);
  const r = clampRect({ x: p.x, y: p.y, w: spec.w, h: spec.h }, spec.bounds);
  return clearAnchor(r, a, spec.bounds);
};

/**
 * 这一帧的最终位置：r0 压到了别的东西（blockers：开头大字、路线上的字、先放好的标签）或挡住了自己的锚点时，
 * 试着贴到每个挡路的东西的上 / 下 / 左 / 右，取挪得最少、又谁都不压的那个；实在没有，取压得最少的。
 */
const resolve = (
  r0: Rect,
  a: Pt | null,
  blockers: Rect[],
  bounds: Rect,
): Rect => {
  const coversAnchor = (r: Rect) =>
    a !== null && contains(inflate(r, G.clear - 1), a);
  const overlap = (r: Rect) =>
    blockers.reduce((sum, b) => sum + overlapArea(r, b), 0);
  if (overlap(r0) === 0 && !coversAnchor(r0)) return r0;
  const around = (b: Rect): Rect[] => [
    { ...r0, y: b.y - r0.h },
    { ...r0, y: b.y + b.h },
    { ...r0, x: b.x - r0.w },
    { ...r0, x: b.x + b.w },
  ];
  const cands = [
    ...blockers.flatMap(around),
    ...(a
      ? around({
          x: a.x - G.clear,
          y: a.y - G.clear,
          w: G.clear * 2,
          h: G.clear * 2,
        })
      : []),
  ].map((c) => clampRect(c, bounds));
  const moved = (r: Rect) => Math.abs(r.x - r0.x) + Math.abs(r.y - r0.y);
  const clean = cands.filter((c) => overlap(c) === 0 && !coversAnchor(c));
  if (clean.length > 0)
    return clean.reduce((best, c) => (moved(c) < moved(best) ? c : best));
  const badness = (r: Rect) => overlap(r) + (coversAnchor(r) ? 1e6 : 0);
  return [r0, ...cands].reduce((best, c) =>
    badness(c) < badness(best) ? c : best,
  );
};

const buildShot = (shot: Shot): ShotLabels => {
  const placeholder = !hasFrames(shot.id);
  const waveforms = shot.overlays.filter((o) => o.type === "waveform");
  const degrade = (WAVEFORM_VARIANT[shot.id] ?? "degrade") === "degrade";
  const slots = SHOT_SLOTS[shot.id] ?? DEFAULT_SLOTS;

  const wanted = shot.overlays
    .map((o, key) => ({ o, key }))
    .filter(({ o }) => {
      if (!ANCHORED.includes(o.type)) return false;
      // 落在「由清楚到模糊」波形时间内的 alert 由那条波形画在判决门限旁
      if (
        o.type === "alert" &&
        degrade &&
        waveforms.some(
          (w) => o.t >= w.t - 1e-6 && o.t + o.dur <= w.t + w.dur + 1e-6,
        )
      )
        return false;
      // scale 在分镜里是 Blender 内的 3D 立体字：有了 Blender 帧就不重复画
      if (o.type === "scale" && SCALE_ONLY_WHEN_PLACEHOLDER && !placeholder)
        return false;
      return true;
    });

  const specs: LabelSpec[] = [];
  const dropped: Overlay[] = [];
  // 先出现的先占位置；同一时刻最多 MAX_LABELS 个，后来的不画
  const sorted = wanted
    .map((w, order) => ({ ...w, order }))
    .sort((a, b) => a.o.t - b.o.t || a.order - b.order);
  for (const { o, key, order } of sorted) {
    const { from, to } = localSpan(shot, o);
    if (specs.filter((s) => s.from <= from && from < s.to).length >= MAX_LABELS) {
      dropped.push(o);
      continue;
    }
    const kind = o.type as LabelSpec["kind"];
    // scale 类的「A · B」是并列的两个尺寸，不分主次；其余拆成主名 + 说明
    const parts =
      kind === "scale"
        ? (() => {
            const p = o.text.split(" · ");
            return {
              head: p[0],
              body: p.length > 1 ? p.slice(1).join(" · ") : null,
            };
          })()
        : splitHeadBody(o.text);
    const head = fitBlock(
      parts.head,
      kind === "term" ? SIZE.term : SIZE.labelHead,
      SIZE.labelHeadMin,
      700,
      1.26,
    );
    const bodyWeight = kind === "scale" ? 700 : 400;
    const body = parts.body
      ? {
          ...fitBlock(
            parts.body,
            kind === "scale" ? SIZE.labelHead : SIZE.labelBody,
            kind === "scale" ? SIZE.labelHeadMin : SIZE.labelBodyMin,
            bodyWeight,
            1.3,
          ),
          weight: bodyWeight,
        }
      : null;
    const w =
      Math.ceil(Math.max(head.w, body ? body.w : 0)) + LABEL_CHIP.padX * 2;
    const h =
      head.lineH * head.lines.length +
      (body ? body.lineH * body.lines.length + LABEL_CHIP.gap : 0) +
      LABEL_CHIP.padY * 2;

    // 下沿：在场的图表面板上沿、角注上沿，取这条标签全程里最高的那个（全程一个值，不会中途跳）
    const tops = shot.overlays
      .filter((p) => isPanel(p) && p.t < o.t + o.dur && o.t < p.t + p.dur)
      .map((p) => panelRectFor(shot, p).y);
    const bottom =
      Math.min(
        PANEL_BOTTOM,
        NOTE.bottom - maxNoteStack(shot, from, to) - 4,
        ...tops,
      ) - 6;
    specs.push({
      key,
      overlay: o,
      kind,
      from,
      to,
      head,
      body,
      w,
      h,
      anchorName: resolveAnchorName(shot.id, o),
      slot: slots[order % slots.length],
      bounds: {
        x: SAFE.left,
        y: SAFE.top,
        w: SAFE.width,
        h: bottom - SAFE.top,
      },
    });
  }

  // 每条标签定一种摆法（右上 / 左上 / …），全程不换，免得中途左右翻
  const plans: Plan[] = [];
  specs.forEach((spec, i) => {
    const n = Math.max(1, spec.to - spec.from);
    const src = new Int32Array(n).fill(-1);
    if (spec.anchorName) {
      const on: boolean[] = [];
      for (let k = 0; k < n; k++) {
        on.push(anchorState(shot, spec, spec.from + k).near);
      }
      // 不在画面附近的帧：找时间上最近的、在画面附近的帧（一样近取前面的）
      let last = -1;
      for (let k = 0; k < n; k++) {
        if (on[k]) last = k;
        src[k] = last;
      }
      let next = -1;
      for (let k = n - 1; k >= 0; k--) {
        if (on[k]) next = k;
        if (!on[k] && next >= 0 && (src[k] < 0 || next - k < k - src[k]))
          src[k] = next;
      }
    } else {
      for (let k = 0; k < n; k++) src[k] = k;
    }

    let cand: Cand;
    if (!spec.anchorName) {
      const id =
        (spec.slot.side === "right" ? "r" : "l") +
        (spec.slot.vert === "up" ? "u" : "d");
      cand = CANDS.find((c) => c.id === id) ?? CANDS[0];
    } else {
      // 在锚点可见的那些帧里取几帧，给每种摆法打分：被安全区挤得离锚点多远、压到别的东西多少
      const valid = [...new Set(Array.from(src).filter((k) => k >= 0))];
      const samples =
        valid.length <= 6
          ? valid
          : Array.from(
              { length: 6 },
              (_, j) => valid[Math.round((j * (valid.length - 1)) / 5)],
            );
      let best = { cost: Infinity, cand: CANDS[0] };
      CANDS.forEach((c, ci) => {
        let cost = ci * 4;
        for (const k of samples) {
          const local = spec.from + k;
          const a = anchorPt(shot, spec, local);
          const ideal = c.place(a, spec.w, spec.h);
          const r = selfRect(spec, c, a);
          cost += Math.abs(r.x - ideal.x) + Math.abs(r.y - ideal.y);
          if (contains(inflate(r, G.clear - 2), a)) cost += 3000;
          for (const ob of obstaclesAt(shot, local))
            cost += overlapArea(r, ob) / 40;
          // 已经定了摆法的（先出现的）标签
          for (let j = 0; j < i; j++) {
            const other = specs[j];
            if (local < other.from || local >= other.to) continue;
            const os = plans[j].src[local - other.from];
            if (os < 0) continue;
            const or = selfRect(
              other,
              plans[j].cand,
              anchorPt(shot, other, other.from + os),
            );
            cost += overlapArea(inflate(r, 8), or) / 40;
          }
        }
        if (cost < best.cost) best = { cost, cand: c };
      });
      cand = best.cand;
    }
    plans.push({ cand, src });
  });

  return { specs, plans, dropped };
};

const shotLabels = (shot: Shot) => {
  let s = shotCache.get(shot);
  if (!s) {
    s = buildShot(shot);
    shotCache.set(shot, s);
  }
  return s;
};

export type PlacedLabel = {
  spec: LabelSpec;
  rect: Rect;
  /** 引线指向哪（屏幕坐标）；null = 不画引线（没对上锚点、锚点不在画面内、或锚点被大字 / 面板盖住） */
  target: Pt | null;
  /** 0–1：锚点离开画面附近后淡出、回来再淡入 */
  presence: number;
};

/** 某一帧在场的标签各放哪 */
export const layoutLabels = (shot: Shot, local: number): PlacedLabel[] => {
  const { specs, plans } = shotLabels(shot);
  const obstacles = obstaclesAt(shot, local);
  const covers = coversAt(shot, local);
  const placed: PlacedLabel[] = [];
  specs.forEach((spec, i) => {
    if (local < spec.from || local >= spec.to) return;
    const k = local - spec.from;
    const from = plans[i].src[k];
    if (from < 0) return; // 锚点全程不在画面附近：不画（画出来也不知道指的是什么）
    const presence = Math.max(0, 1 - Math.abs(from - k) / LABEL_LOST_FADE);
    if (presence <= 0) return;
    const st = anchorState(shot, spec, spec.from + from);
    const a = st.pt;
    const rect = resolve(
      selfRect(spec, plans[i].cand, a),
      spec.anchorName ? a : null,
      [...obstacles, ...placed.map((p) => inflate(p.rect, 8))],
      spec.bounds,
    );

    const live = from === k && spec.anchorName !== null && st.inFrame;
    const inZone =
      a.y >= SAFE.top - 50 && a.y <= Math.min(H, SAFE.bottom + 30);
    const target =
      live &&
      inZone &&
      !covers.some((c) => contains(c, a)) &&
      !contains(inflate(rect, 4), a)
        ? a
        : null;
    placed.push({ spec, rect, target, presence });
  });
  return placed;
};

/** 因为「同一时刻最多 MAX_LABELS 个」没有画出来的标注（调试用） */
export const droppedLabels = (shot: Shot) => shotLabels(shot).dropped;
