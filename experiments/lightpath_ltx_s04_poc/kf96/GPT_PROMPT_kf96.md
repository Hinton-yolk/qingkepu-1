# 第 4 张关键帧：LTX 第 96 帧（4.0 秒）· 给 GPT Image 的说明

## 这一帧是什么、为什么要它
- LTX 第 96 帧 = V1.1 S04 局部帧 F120.2（4.0 秒）。相机正在从两台机柜的全景推向接收端（B）的光模块。
- 第一次测试在 3.8–4.3 秒出现了机柜前面板「融化」、4.4–4.7 秒光缆变粗拖影。这一段离第 72 帧和第 120 帧两张关键帧都远，灰模里服务器面板又只是平的灰块，LTX 只能自己编。加这一张照片，就是给这一段一个真实的样子。

## 交给 GPT 的文件
1. **底图（必须）**：`k096_color.png`（1088×1920，9:16）。构图、机位、物体位置都以它为准。
2. **风格参考（建议一起给）**：已批准的三张照片里的 **F090 全景**（机柜、服务器面板、理线槽的样子）和 **F150 接收端特写**（光模块、MPO 插头、光缆的样子）。
3. 灰模 `c096.png`（统一灰）只用来核对几何，不必给 GPT。

## 提示词（直接复制）
```
Turn the attached Blender blockout frame into a photorealistic photograph. Keep the exact framing, camera angle, perspective, object positions, sizes and occlusions of the blockout — do not crop, zoom, rotate, add or remove objects. Output 9:16 portrait.

Match the look of the two attached reference photos exactly (same equipment, same materials, same lighting and colour grade): this frame sits between them in one continuous camera move.

What is in the frame (top to bottom):
- Top: the open-top GPU server in the receiving rack, seen from above at the front: dark-green motherboard with GPU packages, aluminium heatsinks and memory, inside a brushed-steel chassis, exactly like the servers in the wide reference photo.
- Middle: the server's dark powder-coated steel I/O front panel with three OSFP ports. The middle port holds a silver OSFP optical transceiver with an aqua MPO connector and a black ribbed strain-relief boot, exactly like the close-up reference. The two side ports are empty (dark openings with dust plugs).
- One single aqua fibre-optic cable (same colour and thickness as in the references) leaves the connector, bends smoothly down in front of the panel into the perforated brushed-steel horizontal cable tray below, and runs along the tray to the left edge of the frame. It is one continuous cable: no second cable, no loose ends, it does not pass through any surface.
- Lower half: the front of the rack: stacked 2U servers with clean, crisp front panels — perforated black mesh, drive-bay outlines, silver handles on the left, small rows of green status LEDs — and the black rack post on the right. These panels must look like solid, rigid, flat metal with straight edges and regular hole patterns.

Style: real industrial product photography in a data centre, neutral cool studio lighting, brushed aluminium and dark powder-coated steel, subtle reflections, moderate depth of field (the connector in focus, the far top of the frame slightly soft), dark background.
Do not add: text, labels, logos, arrows, glow, light beams, particles, lens flares, extra cables, people.
```

## 拿回来以后核对什么（我来做）
- 和底图叠图：插头、光缆、理线槽、面板边线、机柜立柱的位置是否对得上（偏移超过约 10 像素就请 GPT 重出）。
- 光缆是不是一根、从插头一直连到画面左边，有没有穿过面板或槽沿。
- 服务器前面板是不是规整的金属，没有皱褶、融化的纹理。
- 和 F090、F150 两张照片的颜色、材质、光缆粗细是否一致。
