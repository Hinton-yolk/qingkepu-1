# EP.08 充电寿命 · 手的参考图 prompt（给 GPT 生图用）

做法和 EP.07 一样：GPT 生成参考图 → 我从图里量轮廓、指缝、指甲，**自己画**进片子（不直接贴照片）。
手机、充电线、插头、电量、屏幕画面都由我画（它们要动），**图里不要出现手机和线**，只留出空位。

## 怎么用
1. 每张都**上传 EP.07 的基础图作参考**（`07-shoubiaolvguang/assets/people/arm-top.webp`，那只左小臂俯视），用「同一个人、同样画风」生成，三集看起来是同一个人的手。
2. 先生成第 1 张，满意后第 2、3 张再上传第 1 张一起作参考。
3. 每张：PNG、透明背景（不行就用纯色 #ECEBE6 浅灰底，我来抠）。尺寸按每条写的。
4. 生成好直接发到对话里。用了 AI 生成的图，发布时勾选「内容由 AI 生成」。

## 共同的风格（每条 prompt 里都已带上）
干净的扁平矢量插画、柔和渐变明暗（和 EP.07 同一画风）；年轻东亚女性的手，黄种人自然肤色（约 #EBCBA5，阴影约 #D6AD84）；五根手指、解剖正确、关节和指甲清楚；不要汗毛、皱纹、掌纹这类密集纹理；不要文字、水印、品牌标志。

> **2026-11-16 夜更新**：夜里那段改成了电量曲线图，**第 2 张（拿手机）不再需要**，只生成第 1、3 张。

## 每张图在片子里用在哪
| 图 | 用在 | 秒数 |
|---|---|---|
| 1 右手捏插头（从右边伸进来，前臂从右边出画） | 开头插线、拔下再插；错误猜测那拍快速插拔；结尾闭环再插一次 | 0–7.25、47.25–50.5 |
| 2 右手从右边伸过来拿起手机 | 「等你快起床，才充满」：手伸过来拿起床头的手机 | 45.0–47.25 |
| 3 双手横握手机打游戏（前臂从左右两边出画） | 小提示「边充边打游戏、闷着充」 | 50.5–54.25 |

---

## 1. 右手捏插头（基础图）
横版 1536×1024，上传 EP.07 基础图作参考：

```
Use the same illustration style, the same skin tone and the same hand as the reference image. Draw only a young East Asian woman's right hand and forearm, seen from the front, coming in horizontally from the RIGHT edge of the canvas (the forearm leaves through the right edge, slightly rising towards it; nothing goes below the hand). The hand is pinching a small object between the tip of the thumb and the tip of the index finger, holding it vertically and pushing it upward, as if plugging a charging plug into the bottom of a phone that stands upright above it: the index finger lies along the top and touches the object's right side, the thumb comes underneath and touches its left side. Leave the pinched object completely EMPTY and transparent: just a narrow vertical gap about 5% of the canvas width and 10% of the canvas height between the thumb and index fingertips, at the left end of the hand, at about 45% of the canvas height. Middle, ring and little fingers curled loosely under the palm, not hanging down. Five fingers, anatomically correct, clear knuckles and fingertips, short natural nails, soft gradient shading. Bare hand: no ring, no bracelet, no watch, no sleeve. Warm natural East Asian skin tone (around #EBCBA5, shadows around #D6AD84). Not a photo, not a 3D render, not a cartoon. Transparent background. No phone, no cable, no plug, no text, no watermark, no logos, no hair, wrinkles or dense texture.
```

## 2. 右手从右边伸过来拿手机
横版 1536×1024，上传第 1 张作参考：

```
Use the same illustration style, the same skin tone and the same right hand as the reference image. Seen from the front: the right hand and forearm come in horizontally from the RIGHT edge of the canvas (the forearm leaves through the right edge) to take a smartphone that stands upright on a bedside stand. The hand grips an EMPTY upright rectangle (a phone shape about 22% of the canvas width and 70% of the canvas height, at the left-centre of the canvas): the thumb curves over the front of the rectangle near its top-left corner, the index, middle and ring fingers wrap around its right long side and back, the little finger relaxed. Nothing above the rectangle's top edge. Leave the rectangle completely empty and transparent — the phone will be added later. Five fingers, anatomically correct, clear knuckles and fingertips, short natural nails, soft gradient shading. Bare hand, no jewellery, no sleeve. Transparent background. No phone, no table, no text, no watermark, no logos.
```

## 3. 双手横握手机打游戏
横版 1536×1024，上传第 1 张作参考：

```
Use the same illustration style, the same skin tone and the same hands as the reference image. Both hands of the same young East Asian woman, seen from the front, holding a smartphone horizontally like playing a mobile game: the left hand and forearm come in from the LEFT edge, the right hand and forearm from the RIGHT edge, each forearm sloping slightly down towards its edge (they leave through the side edges, not the bottom edge). The fingers wrap around the back and the short ends of an EMPTY horizontal rectangle (a landscape phone shape about 60% of the canvas width and 30% of the canvas height, centred), and both thumbs rest on its front face near the left and right ends, as if pressing on-screen buttons. Leave the rectangle completely empty and transparent — the phone will be added later. Ten fingers in total, anatomically correct, clear knuckles and thumbnails, soft gradient shading. Bare hands, no jewellery, no sleeves. Transparent background. No phone, no cable, no text, no watermark, no logos.
```

---

## 生成后请检查
- 三张和 EP.07 是不是同一只手的感觉（肤色、手指粗细、画风）。
- 手指数和形状对不对，尤其第 1 张捏的姿势、第 3 张两只拇指。
- 留出的空位里真的什么都没有。
- 图里没有手机、线、文字、品牌、水印。
