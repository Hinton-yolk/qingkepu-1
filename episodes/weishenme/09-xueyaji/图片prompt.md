# EP.09 血压计 · 参考图 prompt（给 GPT 生图用）

做法和 EP.07 / EP.08 一样：GPT 生成参考图 → 我从图里量轮廓，**自己画**进片子（不直接贴照片）。
袖带、软管、血压计、桌子、椅子、心脏高度虚线都由我画（它们要动），**图里不要出现这些**。

## 怎么用
1. 每张都**上传 EP.08 的小臂图作参考**（`08-chongdian/assets/people/arm-flat.webp`），用「同一个人、同样画风」生成，几集看起来是同一个人。
2. 先生成第 1 张；第 2、3 张上传第 2 张（侧面坐姿）一起作参考，保证是同一个人、同一件衣服。
3. 每张：PNG、透明背景（不行就用纯色 #ECEBE6 浅灰底，我来抠）。尺寸按每条写的。
4. 生成好直接发到对话里。用了 AI 生成的图，发布时勾选「内容由 AI 生成」。

## 共同的风格（每条 prompt 里都已带上）
和参考图同一画风、同一肤色；年轻东亚女性，黄种人自然肤色（约 #EBCBA5，阴影约 #D6AD84）；手指解剖正确；不要汗毛、皱纹、掌纹这类密集纹理；衣服纯色、没有花纹和格纹（防密恐）；不要文字、水印、品牌标志。
上臂露出来：袖带要直接贴着皮肤（这也是正确的量法）。

## 每张图在片子里用在哪
| 图 | 用在 | 秒数 |
|---|---|---|
| 1 一整条胳膊平放（肩在左、手在右，手心朝上） | 开头量两次、钻进去前的推近、闭环回到开头那一帧 | 0–9.5、46–48 |
| 2 侧面坐姿，胳膊往前平放（和心脏一样高） | 「胳膊放得多高？」、小提示「坐好歇 5 分钟、胳膊和心脏一样高」 | 39.5–41.5、44–56 |
| 3 同一个人侧面坐姿，胳膊自然垂下 | 「胳膊比心脏低，读数就偏高」 | 41.5–44 |

胳膊抬高那一拍，我用第 2 张的胳膊转上去画，不用另生成。

---

## 1. 一整条胳膊平放（手心朝上）
横版 1536×1024，上传 EP.08 小臂图作参考：

```
Use the same illustration style, the same skin tone and the same arm as the reference image. Draw one whole bare left arm of the same young East Asian woman, lying flat and horizontal across the canvas as if resting on a table for a blood pressure measurement, seen from slightly above the front. The shoulder and upper arm come in from the LEFT edge of the canvas (the arm leaves through the left edge at about 45% of the canvas height), then the elbow, the forearm and the hand towards the right; the elbow is almost straight, only very slightly bent. Palm facing UP, fingers relaxed and slightly curled, the hand ending at about 85% of the canvas width. The whole upper arm is bare (sleeveless or the sleeve is pushed above the left edge, not visible) and clearly visible, about one third of the arm's length, because a blood pressure cuff will be added on it later. Five fingers, anatomically correct, clear knuckles and fingertips, short natural nails, soft gradient shading. No ring, no bracelet, no watch. Warm natural East Asian skin tone (around #EBCBA5, shadows around #D6AD84). Transparent background. No cuff, no tube, no device, no table, no text, no watermark, no logos, no hair, wrinkles or dense texture.
```

## 2. 侧面坐姿，胳膊往前平放
竖版 1024×1536，上传 EP.08 小臂图作参考：

```
Use the same illustration style and the same skin tone as the reference image. A young East Asian woman seen exactly from the side (profile), facing RIGHT, sitting upright on an invisible chair with her back straight and supported, relaxed and calm. Show the upper body from the top of the head down to the hips and the tops of the thighs (thighs horizontal, going right; cut off at the bottom edge around the knees). Her near arm (the left arm) reaches forward and rests on an invisible table surface: the upper arm goes forward and slightly down from the shoulder, the forearm and hand lie flat and horizontal pointing right, palm up, and the upper arm near the elbow is at the height of the middle of her chest (heart level). She wears a plain short-sleeved T-shirt in one solid muted colour (no print, no pattern, no stripes) so the upper arm is bare. Simple tidy hair tied back, calm face. Clean flat illustration with soft gradient shading, five fingers, anatomically correct. Warm natural East Asian skin tone (around #EBCBA5, shadows around #D6AD84). Transparent background. No chair, no table, no cuff, no device, no text, no watermark, no logos, no dense texture.
```

## 3. 同一个人侧面坐姿，胳膊自然垂下
竖版 1024×1536，上传第 2 张作参考：

```
Use exactly the same woman, the same clothes, the same sitting posture, the same framing and the same style as the reference image (profile, facing RIGHT, sitting upright, upper body down to the knees). The only change: her near arm (the left arm) now hangs straight down relaxed beside her body, the hand beside her hip with the palm facing her thigh, fingers relaxed. Nothing else changes: same head position, same back, same thighs. Five fingers, anatomically correct. Transparent background. No chair, no table, no cuff, no device, no text, no watermark, no logos.
```

---

## 生成后请检查
- 三张是不是同一个人的感觉（肤色、胳膊粗细、画风），和 EP.08 的手接近。
- 第 1 张上臂露得够多（要套袖带），手心朝上，手指数对。
- 第 2、3 张除了胳膊，其他完全一样（头、背、腿位置不动），这样我能直接让胳膊动。
- 衣服纯色、没有花纹；图里没有椅子、桌子、袖带、文字、水印。

---

## 2026-11-18 用户发回三张图
- 第 1 张 → `assets/people/arm-flat-palmup.webp`（2000×667，透明底）：可用。上臂露出约一掌半，够套袖带。
- 第 2 张 → `assets/people/side-arm-raised.webp`（1216×1293，透明底）：GPT 画成了**胳膊伸直、举到肩那么高**（不是放在桌上、和心脏一样高）。正好用在「抬得比心脏高」那一拍。
- 第 3 张 → `assets/people/side-arm-down.webp`（1216×1294）：胳膊垂下，可用。底是画上去的灰白格子（不是真透明），我按颜色抠。
- **还缺一张**：胳膊放在桌上、袖带和心脏一样高（第 4 张，见下）。

## 4. 侧面坐姿，胳膊肘弯着放在垫高的桌上（和心脏一样高）
竖版 1024×1536，上传第 3 张（胳膊垂下那张）作参考：

```
Use exactly the same woman, the same clothes, the same sitting posture, the same framing and the same style as the reference image (profile, facing RIGHT, sitting upright, upper body down to the knees). The only change is her near arm (the left arm, the one closest to the viewer): it is NOT straight and NOT raised to shoulder height. The upper arm points forward and only slightly downward from the shoulder (about 30 degrees below horizontal), so that the MIDDLE of the upper arm is at the height of the middle of her chest (heart level). The elbow is bent, and the forearm lies flat and horizontal pointing forward (to the right), resting on an invisible raised cushion at the height of her lower chest, palm facing up, fingers relaxed. The far arm stays resting on her thigh exactly as in the reference. Head, back and legs do not move. Five fingers, anatomically correct. Real transparent background (not a checkerboard pattern). No chair, no table, no cushion, no cuff, no device, no text, no watermark, no logos.
```
- 第 4 张 → `assets/people/side-arm-heart.webp`：可用。上臂从肩往前稍向下、肘微弯、前臂平伸手心朝上；上臂中段大约在胸口中间那一层。
