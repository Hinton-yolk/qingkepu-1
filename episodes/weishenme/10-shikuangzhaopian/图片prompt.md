# EP.10 实况照片 · 手的参考图 prompt（给 GPT 生图用）

用户 2026-11-23 看草稿 v1.1：「手的建模也要优化」。观众（Codex）也说过：「两只手的握姿太对称，拇指像贴在屏幕边上，有点假，也让我看不清哪一下按了快门」。
做法和 EP.07、EP.08 一样：GPT 生成参考图 → 我从图里量轮廓、指缝、指甲，**自己画**进片子（不直接贴照片）。
手机、屏幕里的烟花、快门按钮都由我画（它们要动），**图里不要出现手机**，只留出空位。

## 怎么用
1. 第 1 张**上传 EP.08 的双手参考图作参考**（`08-chongdian/assets/people/hands-pinch.webp`；没有就用 EP.07 的 `07-shoubiaolvguang/assets/people/arm-top.webp`），用「同一个人、同样画风」生成，几集看起来是同一个人的手。
2. 第 2 张**上传第 1 张作参考**，用「编辑这张图，只改右手拇指」的方式生成：两张除了右手拇指，其他完全一样（我要拿两张对位，做「拇指抬起 → 按下」的动作）。
3. 每张：PNG、透明背景（不行就用纯色 #ECEBE6 浅灰底，我来抠）。横版 1536×1024。
4. 生成好直接发到对话里。用了 AI 生成的图，发布时勾选「内容由 AI 生成」。

## 共同的风格（每条 prompt 里都已带上）
干净的扁平矢量插画、柔和渐变明暗（和 EP.07、EP.08 同一画风）；年轻东亚女性的手，黄种人自然肤色（约 #EBCBA5，阴影约 #D6AD84）；五根手指、解剖正确、关节和指甲清楚；不要汗毛、皱纹、掌纹这类密集纹理；不要文字、水印、品牌标志。

## 每张图在片子里用在哪
| 图 | 用在 | 秒数 |
|---|---|---|
| 1 双手横握手机拍照，右手拇指**按在**快门上 | 开头按快门；结尾回到开头再按一次；小提示（编辑实况照片） | 0–6.75、31.25–41 |
| 2 同第 1 张，只是右手拇指**抬起**、悬在快门上方 | 按下之前的那一下（拇指抬起 → 按下），让「哪一下按了快门」看得清 | 0–0.75、31.25–32 |

---

## 1. 双手横握手机拍照，右手拇指按快门（基础图）
横版 1536×1024，上传 EP.08 双手参考图作参考：

```
Use the same illustration style, the same skin tone and the same hands as the reference image. Both hands of the same young East Asian woman, seen from the front, holding a smartphone horizontally to take a photo of fireworks at night: the left hand and forearm come in from the LEFT edge, the right hand and forearm from the RIGHT edge, each forearm sloping slightly down towards its edge (they leave through the side edges, not the bottom edge). The two hands are NOT symmetrical, like a real person taking a photo: the left hand cradles the left short end of an EMPTY horizontal rectangle (a landscape phone shape about 60% of the canvas width and 30% of the canvas height, centred), its fingers spread behind the back and its thumb lying relaxed along the left edge of the front face, not pressing anything; the right hand holds the right end a little lower, its index finger resting on the top edge, and its thumb pressing down firmly on the front face near the right end, at about 75% of the rectangle's height from the top, the thumb pad flat on the surface and the thumb joint slightly bent, as if pressing a camera shutter button. Leave the rectangle completely empty and transparent — the phone will be added later. Ten fingers in total, anatomically correct, clear knuckles and thumbnails, soft gradient shading. Bare hands, no jewellery, no sleeves. Warm natural East Asian skin tone (around #EBCBA5, shadows around #D6AD84). Not a photo, not a 3D render, not a cartoon. Transparent background. No phone, no screen, no text, no watermark, no logos, no hair, wrinkles or dense texture.
```

## 2. 同第 1 张，右手拇指抬起
横版 1536×1024，上传第 1 张作参考：

```
Edit this image: keep everything exactly the same — the same two hands, the same pose, the same position and size on the canvas, the same style, the same empty rectangle. Only the right thumb changes: it is lifted about one centimetre off the front face, hovering just above the same spot where it was pressing, the thumb tip slightly raised and the joint a little straighter, ready to press. Ten fingers, anatomically correct. Transparent background. No phone, no text, no watermark, no logos.
```

---

## 生成后请检查
- 两张是不是只差右手拇指（其他位置、大小都一样）。
- 手指数和形状对不对，尤其两只拇指。
- 左右手不对称、像真的在拍照；右手拇指在空位的右下部、正面上。
- 留出的空位里真的什么都没有；图里没有手机、文字、品牌、水印。
