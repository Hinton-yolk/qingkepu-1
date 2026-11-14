# 用 GPT 把灰模画成照片级关键帧（远景 PoC 05 · V3）

## 用法
1. **至少做首帧**：把 `clay_0s_first.png` 发给 GPT，配上「首帧」的提示词。这是 LTX 官方推荐的做法，只给首帧也能跑。
2. **想多试一版的话**，再用同样的方法做中间帧（`clay_3s_mid.png`）和末帧（`clay_6s_last.png`）。三张一起给，画面更稳，但三张的风格要一致：同一个对话里连着生成，让 GPT 保持同样的光线和色调。
3. **尺寸**：最好让 GPT 直接出 **9:16 竖图**（1088×1920 或同比例）。如果它只能出 2:3（比如 1024×1536），也发给我，告诉我它是什么尺寸，我来处理对齐。
4. **最重要的是构图不变**：机柜、通道、灯、线槽的位置和透视要和灰模一模一样，LTX 才能对上运动。如果 GPT 把镜头改了（比如通道变宽、视角变了），就让它重画。
5. 生成好的图直接发给我就行，文件名注明是哪一帧。

## 首帧（0 秒，`clay_0s_first.png`）
```
Turn this grey 3D layout into a real photograph. Keep the exact same composition, camera position, perspective, vanishing point and the position of every object — do not move, add or remove racks, lights or trays, and keep the 9:16 vertical frame.

Scene: the cold aisle of a modern hyperscale data center, shot on a full-frame cinema camera, 24mm lens, eye level, looking straight down the aisle. Two long rows of black 42U server racks face each other, filled with real server fronts: 1U and 2U servers with drive bays, mesh vents and tiny green and blue status LEDs, some network switches. Overhead: a yellow plastic fiber raceway along each row, black cable ladders, and linear LED ceiling lights. Floor: grey raised-floor tiles, the ones in the aisle perforated for cold air, with faint scuffs and reflections. A very light haze in the air. Cool, slightly blue-white light with natural uneven falloff, a few bright LED reflections, mild lens vignetting, natural sensor grain, realistic exposure.

Photorealistic, documentary photo, real materials, subtle imperfections. No people, no text, no logos, no brand names, no signage.
```

## 中间帧（3 秒，`clay_3s_mid.png`）
```
Same data center as the previous image, same lighting, colors, haze and camera style — this is a later frame of the same shot. Turn this grey 3D layout into a real photograph. Keep the exact same composition, camera position, perspective and object positions; do not move, add or remove anything; keep the 9:16 vertical frame.

The camera has moved further down the cold aisle and is starting to turn toward the rack row on the right. Black server racks with real 1U/2U server fronts, drive bays, mesh vents and small green and blue status LEDs; yellow fiber raceway and black cable ladders overhead; linear LED ceiling lights; perforated raised-floor tiles; light haze.

Photorealistic, documentary photo, subtle imperfections. No people, no text, no logos, no brand names.
```

## 末帧（6 秒，`clay_6s_last.png`）
```
Same data center as the previous images, same lighting, colors, haze and camera style — this is the last frame of the same shot. Turn this grey 3D layout into a real photograph. Keep the exact same composition, camera position, perspective and object positions; do not move, add or remove anything; keep the 9:16 vertical frame.

A close, slightly angled view of the right-hand rack row. Real server fronts: 1U and 2U servers with drive caddies, mesh vents and small green and blue status LEDs. In the middle of the frame, at eye level, a 1U network switch with two rows of OSFP ports; most ports hold silver optical transceiver modules with lime-green plastic pull tabs. The port openings are dark — no light comes out of them. Shallow depth of field, focus on the switch, the rest softly out of focus. Yellow fiber raceway at the top edge of the frame.

Photorealistic, documentary photo, subtle imperfections. No people, no text, no logos, no brand names.
```

## 为什么这样写
- 「Keep the exact same composition…」放在最前面：LTX 靠灰模控制运动，关键帧和灰模的构图一旦对不上，生成出来就会错位。
- 末帧写明「接口是暗的，没有光射出来」：真实的光模块端口在没接光纤时不会发出可见光，PoC 04 里 LTX 就在端口里编出过发绿光的条。
- 「No text, no logos」：避免出现真实厂商的标志，也免得 GPT 编出乱码文字。
