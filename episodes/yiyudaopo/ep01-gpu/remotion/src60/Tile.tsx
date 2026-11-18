// 「计算方块」：全片唯一的几何母题。圆角矩形，圆角 = 0.22 × 边长，描边 = 0.045 × 边长，顶边一道细高光，
// 下面一道和抬起高度成正比的投影。三个状态用同一套动作语法：
//   空着（只有描边）→ 计算中（内部从下往上灌满，fill 0→1）→ 算好（整块亮一下，lit 0→1）
// 它只是「一次计算」的示意，不是晶体管、不是 GPU 核心、不是 token。
import React from 'react';
import {C, FONT} from './lib/theme';

export type Kind = 'game' | 'ai' | 'neutral';
const RGB: Record<Kind, string> = {game: C.gameRGB, ai: C.aiRGB, neutral: C.neutralRGB};

export const Tile: React.FC<{
  x: number; y: number; s: number; kind: Kind;
  fill?: number; lit?: number; lift?: number; opacity?: number; label?: string; labelSize?: number; empty?: number;
  style?: React.CSSProperties;
}> = ({x, y, s, kind, fill = 0, lit = 0, lift = 0.5, opacity = 1, label, labelSize, empty = 0, style}) => {
  if (opacity <= 0.001 || s <= 0.5) return null;
  const rgb = RGB[kind];
  const bw = Math.max(1.5, s * 0.045);
  const r = s * 0.22;
  const base = (0.10 + 0.20 * lit) * (1 - empty);
  const glow = lit * (1 - empty);
  return (
    <div style={{position: 'absolute', left: x - s / 2, top: y - s / 2, width: s, height: s, borderRadius: r, opacity,
      border: `${bw}px solid rgba(${rgb},${0.92 - 0.45 * empty})`,
      background: `rgba(${rgb},${base})`,
      boxShadow: `inset 0 ${Math.max(1, s * 0.012)}px 0 rgba(255,255,255,${0.22 * (1 - empty)}), 0 ${s * 0.10 * lift}px ${s * 0.22 * lift}px rgba(0,0,0,${0.45 * lift}), 0 0 ${s * 0.32 * glow}px rgba(${rgb},${0.38 * glow})`,
      overflow: 'hidden', boxSizing: 'border-box', ...style}}>
      {fill > 0 && fill < 1 && (
        <div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height: `${fill * 100}%`, background: `rgba(${rgb},0.42)`,
          borderTop: `${Math.max(1, bw * 0.6)}px solid rgba(${rgb},0.95)`}} />
      )}
      {label !== undefined && (
        <div style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: FONT, fontWeight: 700,
          fontSize: labelSize ?? s * 0.42, color: kind === 'game' ? '#FFF4E2' : '#F7FAFC', opacity: 0.55 + 0.45 * Math.max(lit, fill >= 1 ? 1 : 0)}}>
          {label}
        </div>
      )}
    </div>
  );
};

/** 输入 / 输出的小点：沿直线或弧线走，颜色跟着工作类型 */
export const Dot: React.FC<{x: number; y: number; r: number; kind: Kind; opacity?: number}> = ({x, y, r, kind, opacity = 1}) =>
  opacity <= 0.001 ? null : (
    <div style={{position: 'absolute', left: x - r, top: y - r, width: 2 * r, height: 2 * r, borderRadius: r, opacity,
      background: `rgba(${RGB[kind]},1)`, boxShadow: `0 0 ${r * 1.6}px rgba(${RGB[kind]},0.6)`}} />
  );
