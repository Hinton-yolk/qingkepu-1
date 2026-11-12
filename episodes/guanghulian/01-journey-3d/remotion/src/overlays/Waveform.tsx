// waveform：波形 / 眼图。三种画法（哪个镜头用哪种见 shotConfig.WAVEFORM_VARIANT）：
//   degrade  同一段伪随机比特：「出发时」方正，「到达时」经过低通变圆钝，随时间从清楚到模糊；右边是眼图，由开到合；
//            同镜头的 alert 出现时，判决门限和门限附近的判决点变珊瑚色
//   restore  左糊右清两条（DSP 两侧）
//   eo       上金（电信号）下青（光强）两条对齐
// 小标题文字从标注的 text 拆出来；颜色只用金（电）、青（光）、珊瑚（出错）和奶油色。
import React from "react";
import { Easing, interpolate, useCurrentFrame } from "remotion";
import { eyeDelay, sampleWave, TAU_MAX, toPath, valueAt } from "../lib/signal";
import { PANEL_HEIGHT, WaveformVariant } from "../shotConfig";
import { STR } from "../strings";
import { C, CLAMP, rgba, SIZE } from "../theme";
import { Overlay, toFrame } from "../timeline";
import { innerSize, Panel, RowLabel } from "./Panel";

const SPU = 32; // 每个比特取多少个采样点

type Props = {
  overlay: Overlay;
  duration: number; // 帧
  variant: WaveformVariant;
  alert?: Overlay | null; // 同镜头里落在这段波形时间内的 alert
};

const panelFade = (frame: number, duration: number) =>
  Math.min(
    interpolate(frame, [0, 8], [0, 1], CLAMP),
    interpolate(frame, [duration - 8, duration], [1, 0], CLAMP),
  );

// ---------------------------------------------------------------- degrade
const Degrade: React.FC<Props> = ({ overlay, duration, alert }) => {
  const frame = useCurrentFrame();
  const { w, h } = innerSize(PANEL_HEIGHT.degrade);
  const parts = overlay.text.split(" / ");
  const labelTx = parts[0] ?? overlay.text;
  const labelRx = parts[1] ?? "";

  const alertAt = alert
    ? toFrame(alert.t) - toFrame(overlay.t)
    : Math.round(duration * 0.5);
  const alertEnd = alert
    ? alertAt + (toFrame(alert.t + alert.dur) - toFrame(alert.t))
    : duration;
  // 模糊程度：从几乎不糊，到 alert 出现时最糊，之后保持
  const tau =
    TAU_MAX *
    interpolate(frame, [10, Math.max(20, alertAt)], [0.06, 1], {
      ...CLAMP,
      easing: Easing.inOut(Easing.quad),
    });
  const alertK = Math.min(
    interpolate(frame, [alertAt, alertAt + 8], [0, 1], CLAMP),
    interpolate(frame, [alertEnd - 6, alertEnd], [1, 0], CLAMP),
  );

  // 左列：两条波形。时间向左流（新的比特从右边进来）
  const LW = 560;
  const UI = 9;
  const t0 = 4 + frame / 11;
  const tx = sampleWave({ t0, ui: UI, spu: SPU, tau: 0, edge: 0.08 });
  const rx = sampleWave({ t0, ui: UI, spu: SPU, tau, edge: 0.08 });
  const TX = { top: 50, bot: 118 };
  const RX = { top: 200, bot: 284 };
  const thY = (RX.top + RX.bot) / 2;

  // 判决点：每个比特在「眼睛」张得最大的时刻取一次值
  const delay = eyeDelay(tau);
  const dots: { x: number; y: number; bad: boolean }[] = [];
  for (let n = Math.ceil(t0 - 1); n <= t0 + UI; n++) {
    const ts = n + 0.5 + delay;
    if (ts < t0 + 0.15 || ts > t0 + UI - 0.15) continue;
    const v = valueAt(rx, t0, SPU, ts);
    dots.push({
      x: ((ts - t0) / UI) * LW,
      y: RX.bot + (RX.top - RX.bot) * v,
      bad: Math.abs(v - 0.5) < 0.2,
    });
  }

  // 右列：眼图。把最近走过的 22 个比特，各取前后共 2 个 UI，叠在一起
  const EX = 596;
  const EW = w - EX;
  const EYE = { top: 52, bot: 276 };
  const eyeMid = (EYE.top + EYE.bot) / 2;
  const newest = Math.floor(t0 + UI) - 2;
  const eyePaths: string[] = [];
  for (let m = 0; m < 22; m++) {
    const n = newest - m;
    const seg = sampleWave({
      t0: n + 0.5 + delay - 1,
      ui: 2,
      spu: 24,
      tau,
      edge: 0.08,
    });
    eyePaths.push(toPath(seg, EX + 6, EX + EW - 6, EYE.bot - 14, EYE.top + 14));
  }

  const thColor = alertK > 0.01 ? C.alert : rgba(C.cream, 0.6);

  return (
    <Panel height={PANEL_HEIGHT.degrade} opacity={panelFade(frame, duration)}>
      <RowLabel
        x={0}
        y={0}
        text={labelTx}
        swatch={C.electric}
        fontSize={SIZE.panelLabel}
      />
      <RowLabel
        x={0}
        y={150}
        text={labelRx}
        swatch={C.electric}
        fontSize={SIZE.panelLabel}
      />
      <RowLabel
        x={EX}
        y={0}
        text={STR.eye}
        fontSize={SIZE.panelSmall}
        opacity={0.75}
      />
      <svg
        width={w}
        height={h}
        style={{ position: "absolute", left: 0, top: 0 }}
      >
        <defs>
          <clipPath id="wf-left">
            <rect x={0} y={36} width={LW} height={h - 36} />
          </clipPath>
        </defs>
        {/* 出发时：方正 */}
        <g clipPath="url(#wf-left)">
          <path
            d={toPath(tx, 0, LW, TX.bot, TX.top)}
            fill="none"
            stroke={C.electric}
            strokeWidth={5}
            strokeLinejoin="round"
          />
          {/* 到达时：圆钝 */}
          <rect
            x={0}
            y={thY - 17}
            width={LW}
            height={34}
            fill={rgba(C.alert, 0.2 * alertK)}
          />
          <line
            x1={0}
            y1={thY}
            x2={LW}
            y2={thY}
            stroke={thColor}
            strokeWidth={2}
            strokeDasharray="10 8"
          />
          <path
            d={toPath(rx, 0, LW, RX.bot, RX.top)}
            fill="none"
            stroke={C.electric}
            strokeWidth={5}
            strokeLinejoin="round"
            strokeLinecap="round"
          />
          {dots.map((d, i) => (
            <circle
              key={i}
              cx={d.x}
              cy={d.y}
              r={d.bad ? 9 : 5}
              fill={d.bad ? C.alert : C.cream}
              stroke={C.ink}
              strokeWidth={2}
              opacity={alertK * (d.bad ? 1 : 0.55)}
            />
          ))}
        </g>
        {/* 门限图例 */}
        <line
          x1={0}
          y1={322}
          x2={44}
          y2={322}
          stroke={thColor}
          strokeWidth={2}
          strokeDasharray="10 8"
        />
        {/* 眼图 */}
        <rect
          x={EX}
          y={EYE.top}
          width={EW}
          height={EYE.bot - EYE.top}
          rx={8}
          fill={rgba(C.cream, 0.04)}
          stroke={rgba(C.cream, 0.18)}
          strokeWidth={1.5}
        />
        <rect
          x={EX + 6}
          y={eyeMid - 20}
          width={EW - 12}
          height={40}
          fill={rgba(C.alert, 0.2 * alertK)}
        />
        {eyePaths.map((d, i) => (
          <path
            key={i}
            d={d}
            fill="none"
            stroke={C.electric}
            strokeWidth={2.5}
            opacity={0.5}
          />
        ))}
        <line
          x1={EX + 6}
          y1={eyeMid}
          x2={EX + EW - 6}
          y2={eyeMid}
          stroke={thColor}
          strokeWidth={2}
          strokeDasharray="10 8"
        />
      </svg>
      <div
        style={{
          position: "absolute",
          left: 56,
          top: 304,
          fontSize: SIZE.panelSmall,
          lineHeight: "36px",
          color: alertK > 0.01 ? C.alert : rgba(C.cream, 0.7),
        }}
      >
        {STR.threshold}
      </div>
      {alert ? (
        <div
          style={{
            position: "absolute",
            left: EX,
            width: EW,
            top: 292,
            textAlign: "center",
            fontSize: 46,
            fontWeight: 700,
            lineHeight: "64px",
            color: C.alert,
            opacity: alertK,
            scale: interpolate(frame, [alertAt, alertAt + 8], [0.86, 1], {
              ...CLAMP,
              easing: Easing.out(Easing.cubic),
            }),
          }}
        >
          {alert.text}
        </div>
      ) : null}
    </Panel>
  );
};

// ---------------------------------------------------------------- restore
const Restore: React.FC<Props> = ({ overlay, duration }) => {
  const frame = useCurrentFrame();
  const { w, h } = innerSize(PANEL_HEIGHT.restore);
  const parts = overlay.text.split("→").map((s) => s.trim());
  const labelIn = parts[0] ?? overlay.text;
  const labelOut = parts[1] ?? "";

  const SW = 392; // 每一侧波形的宽度
  const GAP = w - SW * 2;
  const UI = 6.5;
  const LAT = 2; // 出口比入口晚 2 个比特（处理要时间；示意）
  const t0 = 20 + frame / 11;
  const tau = TAU_MAX;
  const delay = eyeDelay(tau);
  const blurred = sampleWave({ t0, ui: UI, spu: SPU, tau, edge: 0.08 });
  const clean = sampleWave({
    t0: t0 - LAT - delay,
    ui: UI,
    spu: SPU,
    tau: 0,
    edge: 0.1,
  });
  const Y = { top: 62, bot: 150 };
  const thY = (Y.top + Y.bot) / 2;
  const outK = interpolate(frame, [16, 30], [0, 1], CLAMP);
  const RX0 = SW + GAP;

  const dots: { x: number; y: number }[] = [];
  for (let n = Math.ceil(t0 - 1); n <= t0 + UI; n++) {
    const ts = n + 0.5 + delay;
    if (ts < t0 + 0.2 || ts > t0 + UI - 0.2) continue;
    dots.push({
      x: ((ts - t0) / UI) * SW,
      y: Y.bot + (Y.top - Y.bot) * valueAt(blurred, t0, SPU, ts),
    });
  }

  return (
    <Panel height={PANEL_HEIGHT.restore} opacity={panelFade(frame, duration)}>
      <RowLabel
        x={0}
        y={0}
        text={labelIn}
        swatch={C.electric}
        fontSize={SIZE.panelLabel}
      />
      <RowLabel
        x={RX0}
        y={0}
        text={labelOut}
        swatch={C.electric}
        fontSize={SIZE.panelLabel}
        opacity={outK}
      />
      <svg
        width={w}
        height={h}
        style={{ position: "absolute", left: 0, top: 0 }}
      >
        <defs>
          <clipPath id="wf-in">
            <rect x={0} y={40} width={SW} height={h - 40} />
          </clipPath>
          <clipPath id="wf-out">
            <rect x={RX0} y={40} width={SW} height={h - 40} />
          </clipPath>
        </defs>
        <g clipPath="url(#wf-in)">
          <line
            x1={0}
            y1={thY}
            x2={SW}
            y2={thY}
            stroke={rgba(C.cream, 0.55)}
            strokeWidth={2}
            strokeDasharray="10 8"
          />
          <path
            d={toPath(blurred, 0, SW, Y.bot, Y.top)}
            fill="none"
            stroke={C.electric}
            strokeWidth={5}
            strokeLinejoin="round"
          />
          {dots.map((d, i) => (
            <circle
              key={i}
              cx={d.x}
              cy={d.y}
              r={5}
              fill={C.cream}
              stroke={C.ink}
              strokeWidth={2}
              opacity={0.8}
            />
          ))}
        </g>
        {/* 中间：从左到右的箭头（DSP 在这里重新判决） */}
        <g
          opacity={0.3 + 0.5 * outK}
          stroke={C.cream}
          strokeWidth={3}
          fill="none"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <line x1={SW + 28} y1={thY} x2={RX0 - 30} y2={thY} />
          <path
            d={`M${RX0 - 46} ${thY - 14} L${RX0 - 30} ${thY} L${RX0 - 46} ${thY + 14}`}
          />
        </g>
        <g clipPath="url(#wf-out)" opacity={outK}>
          <path
            d={toPath(clean, RX0, RX0 + SW, Y.bot, Y.top)}
            fill="none"
            stroke={C.electric}
            strokeWidth={5}
            strokeLinejoin="round"
          />
        </g>
      </svg>
      <div
        style={{
          position: "absolute",
          left: 0,
          top: 166,
          fontSize: SIZE.panelSmall,
          lineHeight: "36px",
          color: rgba(C.cream, 0.7),
        }}
      >
        <span style={{ letterSpacing: 2, marginRight: 10 }}>- - -</span>
        {STR.threshold}
      </div>
    </Panel>
  );
};

// ---------------------------------------------------------------- eo
const Eo: React.FC<Props> = ({ overlay, duration }) => {
  const frame = useCurrentFrame();
  const { w, h } = innerSize(PANEL_HEIGHT.eo);
  // 「电信号 / 光强：同步」→ 上行标题、下行标题、右上角的短语
  const parts = overlay.text.split(" / ");
  const labelE = parts[0] ?? overlay.text;
  const rest = parts[1] ?? "";
  const colon = rest.indexOf("：");
  const labelO = colon > 0 ? rest.slice(0, colon) : rest;
  const badge = colon > 0 ? rest.slice(colon + 1) : "";

  const UI = 11;
  const t0 = 40 + frame / 10;
  const elec = sampleWave({ t0, ui: UI, spu: SPU, tau: 0, edge: 0.16 });
  // 光强：跟着电信号走；暗的时候不是全黑（消光比有限，示意）
  const opt = sampleWave({ t0, ui: UI, spu: SPU, tau: 0.05, edge: 0.16 }).map(
    (v) => 0.1 + 0.9 * v,
  );
  const E = { top: 50, bot: 116 };
  const O = { top: 192, bot: 270 }; // bot 对应光强 0
  const optK = interpolate(frame, [10, 22], [0, 1], CLAMP);

  const edges: number[] = [];
  for (let n = Math.ceil(t0); n <= t0 + UI; n++)
    edges.push(((n - t0) / UI) * w);

  const optLine = toPath(opt, 0, w, O.bot, O.top);
  const optFill = `${optLine}L${w} ${O.bot}L0 ${O.bot}Z`;

  return (
    <Panel height={PANEL_HEIGHT.eo} opacity={panelFade(frame, duration)}>
      <RowLabel
        x={0}
        y={0}
        text={labelE}
        swatch={C.electric}
        fontSize={SIZE.panelLabel}
      />
      <RowLabel
        x={0}
        y={140}
        text={labelO}
        swatch={C.light}
        fontSize={SIZE.panelLabel}
        opacity={optK}
      />
      {badge ? (
        <div
          style={{
            position: "absolute",
            right: 0,
            top: 0,
            fontSize: SIZE.panelLabel,
            lineHeight: "36px",
            fontWeight: 700,
            opacity: interpolate(frame, [26, 36], [0, 1], CLAMP),
          }}
        >
          {badge}
        </div>
      ) : null}
      <svg
        width={w}
        height={h}
        style={{ position: "absolute", left: 0, top: 0 }}
      >
        <defs>
          <clipPath id="wf-eo">
            <rect x={0} y={40} width={w} height={h - 40} />
          </clipPath>
        </defs>
        <g clipPath="url(#wf-eo)">
          {/* 每个比特边沿一条细虚线，上下贯通：看得出两条线同时变 */}
          {edges.map((x, i) => (
            <line
              key={i}
              x1={x}
              y1={E.top - 6}
              x2={x}
              y2={O.bot}
              stroke={rgba(C.cream, 0.16 * optK)}
              strokeWidth={1.5}
              strokeDasharray="6 7"
            />
          ))}
          <path
            d={toPath(elec, 0, w, E.bot, E.top)}
            fill="none"
            stroke={C.electric}
            strokeWidth={5}
            strokeLinejoin="round"
          />
          <g opacity={optK}>
            <path d={optFill} fill={rgba(C.light, 0.2)} />
            <path
              d={optLine}
              fill="none"
              stroke={C.light}
              strokeWidth={5}
              strokeLinejoin="round"
            />
            <line
              x1={0}
              y1={O.bot}
              x2={w}
              y2={O.bot}
              stroke={rgba(C.cream, 0.35)}
              strokeWidth={1.5}
            />
          </g>
        </g>
      </svg>
    </Panel>
  );
};

export const Waveform: React.FC<Props> = (props) => {
  if (props.variant === "restore") return <Restore {...props} />;
  if (props.variant === "eo") return <Eo {...props} />;
  return <Degrade {...props} />;
};
