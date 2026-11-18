// 一语道破 EP01 · DIRECTOR-LOCKED 60s：一条连续的镜头路径
//   0–5 s    SHOT 01  GPU 微距（Blender OPEN）→ 芯片方框里长出游戏视口
//   5–17 s   SHOT 02  小岛：一块地 → 一个计算方块 → 很多块一起算 → 方块抬起，镜头跟着其中一块往右
//   17–30 s  SHOT 03  AI 问题 → 示意数字 → [2, 3]·[4, 5] = 23 → 收进同一个方块
//   30–42 s  SHOT 04  同一个输入，多组参数，多组结果一起算 → 拉远，左上方露出图形那一组
//   42–51 s  SHOT 05  两组同时算 → 排成两股往下流 → 落进芯片轮廓 → 真芯片在底下浮现（Blender CLOSE）
//   51–60 s  SHOT 06  叠加层在芯片上算 → 沉进芯片 → 稍拉远、倾斜 9° → 答案
import React from 'react';
import {AbsoluteFill, Audio, staticFile} from 'remotion';
import audio from './audio.json';
import {AI} from './layers/AI';
import {Carrier} from './layers/Carrier';
import {Die} from './layers/Die';
import {Game} from './layers/Game';
import {Background, Plates, Texts} from './layers/Stage';

export const Film: React.FC = () => (
  <AbsoluteFill style={{background: '#17191D', overflow: 'hidden'}}>
    <Background />
    <Plates />
    <Game />
    <AI />
    <Die />
    <Carrier />
    <Texts />
    {(audio as {mix: boolean}).mix && <Audio src={staticFile('dl60/mix.wav')} />}
  </AbsoluteFill>
);
