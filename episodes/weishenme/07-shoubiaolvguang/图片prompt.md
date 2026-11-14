# EP.07 手表绿光 · 手和手臂的生成 prompt（给 GPT 生图用）

用户 2026-11-14 看草稿 v1：「建模不通过，手指小臂这些都太假」。
做法照 EP.06 人脸解锁的先例：人物（手、小臂）用 GPT 生成的图，**手表、绿光、血管剖面、曲线卡片、戒指的光**还是我在片子里画（它们要动、要卡心跳）。

## 怎么用
1. **先生成第 1 张（基础图）**。满意后，第 2–4 张都**上传第 1 张作参考**，用「编辑这张图 / 同一个人、同样画风」的方式生成，保证肤色、手型、画风一致。
2. 每张：**PNG、透明背景**（不行就用纯色 #ECEBE6 浅灰底，我来抠）。尺寸按每条写的横 / 竖。
3. **图里不要手表、不要戒指以外的饰品**：手表我来画（它要翻转、亮绿灯、显示心率）。第 4 张的戒指可以有（只要一枚素色黑戒指，不发光）。
4. 生成好后直接发到对话里，我来抠图、对位、放进片子。用了 AI 生成的图，发布时勾选「内容由 AI 生成」。

## 共同的风格（每条 prompt 后面都已经带上）
干净的扁平矢量插画、柔和的渐变明暗（和 EP.06 人物同一画风），不是照片、不是 3D 渲染、不是卡通；年轻东亚女性的手，黄种人自然肤色（约 #EBCBA5，阴影约 #D6AD84）；手指修长自然、关节和指甲清楚、解剖正确（五根手指）；不要汗毛、皱纹、掌纹这类密集纹理；不要任何文字、水印、品牌标志。

## 每张图在片子里用在哪
| 图 | 用在 | 秒数 |
|---|---|---|
| 1 左小臂俯视（基础图） | 开头表落到手腕上、表盘 ♥ 80；结尾翻回表背面；小提示（腕骨、往手肘挪） | 0–5.25、44–53.5 |
| 2 右手捏东西的手势 | 开头和结尾「捏着表翻过来」（表画在两指之间） | 0–3.1、44.5–47.3 |
| 3 跑步时的手臂（侧面） | 「可你一跑起来呢」：以肘为轴前后甩；侧面钻进表底下 | 5.25–7、26–39.5 |
| 4 同 3，手张开、戴戒指 | 「那戒指那么小」：手张开，镜头滑到戒指 | 39.5–44 |

---

## 1. 基础图：左小臂俯视（其他图都以它为参考）
横版 1536×1024：

```
A clean, modern flat vector illustration with soft gradient shading: a young East Asian woman's left forearm and hand seen from directly above, lying flat and relaxed on an invisible table, palm down, back of the hand facing the viewer. The arm enters from the left edge of the canvas at the elbow and runs horizontally to the right; the hand is on the right, fingers together and gently extended, pointing right, thumb relaxed along the upper side. The whole arm from the elbow to the fingertips fits inside the canvas, the elbow just touching the left edge. The wrist is clearly visible, with the small round bump of the wrist bone (ulnar styloid) showing on the lower side of the wrist. Slender, natural, anatomically correct proportions: the forearm tapers smoothly from the elbow to the wrist, natural knuckles, short natural nails. Bare skin: no watch, no bracelet, no jewellery, no sleeve. Warm natural East Asian skin tone (around #EBCBA5, shadows around #D6AD84), a soft highlight along the top of the forearm. Not a photo, not a 3D render, not a cartoon. Transparent background. No text, no watermark, no logos, no hair, wrinkles or dense repeating texture.
```

## 2. 右手捏东西的手势（开头 / 结尾捏着表翻面）
竖版 1024×1536，上传第 1 张作参考：

```
Use the same illustration style, the same skin tone and the same hand shape as the reference image. Draw only the woman's right hand seen from directly above, coming down from the top edge of the canvas (the wrist leaves through the top edge), as if it is holding a small object between the thumb and the index and middle fingers: the thumb on the left side and the index and middle fingertips on the right side of an EMPTY gap about the size of a smartwatch (about 30% of the canvas width), centred in the lower half of the canvas. Leave that gap completely empty and transparent — the object will be added later. Ring and little fingers curled loosely. Natural, anatomically correct: five fingers, clear knuckles and fingertips, short natural nails, soft shading. Transparent background. No watch, no object, no text, no watermark, no logos.
```

## 3. 跑步时的手臂（侧面）
竖版 1024×1536，上传第 1 张作参考：

```
Use the same illustration style, the same skin tone and the same arm as the reference image. Now the woman's left arm seen exactly from the side while she is running: the upper arm comes down from the top edge of the canvas (a short plain sleeve of a light grey sports T-shirt at the very top), the elbow bent at about 90 degrees in the middle of the canvas, the forearm pointing forward to the right and slightly up, the hand in a loose relaxed fist at the right, thumb on top. Natural rounded elbow, a forearm that tapers smoothly to the wrist, the wrist clearly visible and straight. Bare wrist: no watch, no bracelet. Natural, anatomically correct, slender, soft gradient shading. Transparent background. No body, no face, no text, no watermark, no logos.
```

## 4. 同第 3 张，手张开、戴一枚戒指
竖版 1024×1536，上传第 3 张作参考：

```
Edit this image: keep everything exactly the same — the same arm, the same pose, the same position and size on the canvas, the same style. Only the hand changes: it opens from the fist into a relaxed open hand, fingers together and gently extended forward to the right, palm facing down, thumb relaxed. On the index finger, at the base of the finger, a plain matte black smart ring (a simple smooth band, no light, no logo). Five fingers, anatomically correct, clear knuckles and fingertips. Transparent background. No watch, no text, no watermark, no logos.
```

---

## 生成后请检查
- 4 张是不是同一只手的感觉（肤色、手指粗细、画风一致）。
- 手指数和形状对不对（AI 最容易出错的地方），尤其第 2 张捏东西的手势、第 4 张张开的手。
- 第 2 张中间留的空位里真的什么都没有（表由我画进去）。
- 图里没有手表、文字、品牌、水印。
