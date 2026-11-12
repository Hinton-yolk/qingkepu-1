// timing_diagram：并行 ↔ 串行的时序示意。横轴是时间（不是空间）。
//   并行 → 串行（文案里「并行」在前）：上半 N 条并行线，一拍同时换一排值；下半 1 条串行线，一拍一个。
//       同一组比特从上半「排」到下半：串行线每送出一个，就从对应的那条并行线上引一条竖线下来（依次轮到每一条线）。
//   串行 → 并行（文案里「串行」在前）：上下对调。串行线一个一个进来，各自落到对应的并行线上先存着，
//       等这一组收齐，下一拍一起出现在并行线上。
// 画法：亮 = 1，暗 = 0（和同镜头的角注一致）；一条竖线（「现在」）从左扫到右，扫过的地方才画出来。
// 都是电信号，所以只用金色。
import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { bitAt } from "../lib/signal";
import { PANEL_HEIGHT, TIMING_LANES, TIMING_WORDS } from "../shotConfig";
import { STR } from "../strings";
import { C, CLAMP, rgba, SIZE } from "../theme";
import { Overlay } from "../timeline";
import { innerSize, Panel, RowLabel } from "./Panel";

type Props = { overlay: Overlay; duration: number };

const LANE_H = 20;
const LANE_PITCH = 24;
const SERIAL_H = 36;
const BITS_OFFSET = 9; // 从伪随机序列的第几位取数（固定）

export const TimingDiagram: React.FC<Props> = ({ overlay, duration }) => {
  const frame = useCurrentFrame();
  const { w, h } = innerSize(PANEL_HEIGHT.timing_diagram);
  const N = TIMING_LANES;
  const K = TIMING_WORDS;

  const parts = overlay.text.split("→").map((s) => s.trim());
  const p2s = (parts[0] ?? "").includes("并行") || !(parts[0] ?? "").includes("串行");
  const labelTop = parts[0] ?? overlay.text;
  const labelBot = parts[1] ?? "";

  const X0 = 6;
  const AXIS_PAD = 86; // 右边留给箭头和「时间」
  const colW = (w - X0 - AXIS_PAD) / K;
  const sub = colW / N;
  const blockH = N * LANE_PITCH;

  // 纵向排版：小标题 / 上半 / 连线区 / 下半 / 小标题 / 时间轴
  const topY = 46;
  const topH = p2s ? blockH : SERIAL_H;
  const botH = p2s ? SERIAL_H : blockH;
  const gap = 34;
  const botY = topY + topH + gap;
  const botLabelY = botY + botH + 6;
  const axisY = h - 12;

  // 「现在」：匀速从左扫到右（时间均匀地流），最后停 1 秒看全图
  const tau = interpolate(frame, [10, Math.max(20, duration - 34)], [0, K], CLAMP);
  const cursorX = X0 + tau * colW;

  const bit = (word: number, lane: number) => bitAt(BITS_OFFSET + word * N + lane);
  const laneY = (blockTop: number, i: number) => blockTop + i * LANE_PITCH;
  const parTop = p2s ? topY : botY;
  const serTop = p2s ? botY : topY;

  const cells: React.ReactNode[] = [];
  const links: React.ReactNode[] = [];

  // 并行线：每一拍，所有的线同时换成新的一排值
  for (let k = 0; k < K; k++) {
    // 串行 → 并行时，第 k 组要等收齐（下一拍）才出现在并行线上
    const showFrom = p2s ? k : k + 1;
    if (tau <= showFrom || showFrom >= K) continue;
    const grown = Math.min(1, tau - showFrom) * colW;
    for (let i = 0; i < N; i++) {
      cells.push(
        <rect
          key={`p${k}-${i}`}
          x={X0 + showFrom * colW + 2}
          y={laneY(parTop, i)}
          width={Math.max(0, grown - 4)}
          height={LANE_H}
          rx={3}
          fill={rgba(C.electric, bit(k, i) ? 0.95 : 0.16)}
        />,
      );
    }
  }

  // 串行线：一拍一个
  for (let j = 0; j < K * N; j++) {
    const s = j / N;
    if (tau <= s) break;
    const k = Math.floor(j / N);
    const i = j % N;
    const grown = Math.min(1 / N, tau - s) * colW;
    const x = X0 + s * colW;
    cells.push(
      <rect
        key={`s${j}`}
        x={x + 1.5}
        y={serTop}
        width={Math.max(0, grown - 3)}
        height={SERIAL_H}
        rx={3}
        fill={rgba(C.electric, bit(k, i) ? 0.95 : 0.16)}
      />,
    );

    // 对应关系：这一位来自 / 去往第 i 条并行线
    const cx = x + sub / 2;
    const ly = laneY(parTop, i) + LANE_H / 2;
    const sy = p2s ? serTop : serTop + SERIAL_H;
    const current = tau - s < 1 / N;
    const sameWord = Math.floor(tau - 1e-6) === k;
    const a = current ? 0.95 : sameWord ? 0.42 : 0.16;
    links.push(
      <g key={`l${j}`} opacity={a}>
        <line x1={cx} y1={ly} x2={cx} y2={sy} stroke={C.cream} strokeWidth={current ? 2.5 : 1.5} />
        <circle cx={cx} cy={ly} r={current ? 5.5 : 3.5} fill={C.cream} />
        {!p2s && k + 1 < K ? (
          // 存着，等下一拍一起出：一条很淡的虚线拉到下一拍的起点
          <line
            x1={cx}
            y1={ly}
            x2={X0 + (k + 1) * colW}
            y2={ly}
            stroke={C.cream}
            strokeWidth={1.2}
            strokeDasharray="3 5"
            opacity={0.6}
          />
        ) : null}
      </g>,
    );
  }

  // 每一拍的边界
  const beats: React.ReactNode[] = [];
  for (let k = 0; k <= K; k++) {
    const x = X0 + k * colW;
    beats.push(
      <line
        key={k}
        x1={x}
        y1={topY - 6}
        x2={x}
        y2={axisY}
        stroke={rgba(C.cream, 0.2)}
        strokeWidth={1.5}
        strokeDasharray="5 7"
      />,
    );
  }

  const opacity = Math.min(
    interpolate(frame, [0, 8], [0, 1], CLAMP),
    interpolate(frame, [duration - 8, duration], [1, 0], CLAMP),
  );
  const axisEnd = w - 62;

  return (
    <Panel height={PANEL_HEIGHT.timing_diagram} opacity={opacity}>
      <RowLabel x={0} y={0} text={labelTop} swatch={C.electric} fontSize={SIZE.panelLabel} />
      <RowLabel x={0} y={botLabelY} text={labelBot} swatch={C.electric} fontSize={SIZE.panelLabel} />
      <svg width={w} height={h} style={{ position: "absolute", left: 0, top: 0 }}>
        {/* 每条线的底轨 */}
        {Array.from({ length: N }).map((_, i) => (
          <rect
            key={`t${i}`}
            x={X0}
            y={laneY(parTop, i)}
            width={K * colW}
            height={LANE_H}
            rx={3}
            fill={rgba(C.cream, 0.05)}
          />
        ))}
        <rect x={X0} y={serTop} width={K * colW} height={SERIAL_H} rx={3} fill={rgba(C.cream, 0.05)} />
        {beats}
        {cells}
        {links}
        {/* 「现在」 */}
        {tau < K ? (
          <line
            x1={cursorX}
            y1={topY - 6}
            x2={cursorX}
            y2={botY + botH + 4}
            stroke={rgba(C.cream, 0.75)}
            strokeWidth={2}
          />
        ) : null}
        {/* 时间轴 */}
        <line x1={X0} y1={axisY} x2={axisEnd} y2={axisY} stroke={rgba(C.cream, 0.7)} strokeWidth={2} />
        <path
          d={`M${axisEnd - 12} ${axisY - 8} L${axisEnd} ${axisY} L${axisEnd - 12} ${axisY + 8}`}
          fill="none"
          stroke={rgba(C.cream, 0.7)}
          strokeWidth={2}
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
      <div
        style={{
          position: "absolute",
          right: 0,
          top: axisY - 18,
          fontSize: SIZE.panelSmall,
          lineHeight: "36px",
          color: rgba(C.cream, 0.8),
        }}
      >
        {STR.timeAxis}
      </div>
    </Panel>
  );
};
