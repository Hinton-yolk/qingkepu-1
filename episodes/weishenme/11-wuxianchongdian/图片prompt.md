# EP.11 无线充电 · 手的参考图 prompt（给 GPT 生图用）

做法和 EP.07、EP.08 一样：GPT 生成参考图，我从图里量出轮廓、指缝和指甲，**自己画**进片子，不直接贴照片。
手机、充电板都由我来画（它们要动、要做成玻璃质感），所以**图里不要出现手机**，只留出空位。

> **待用户定**：新一季的物体是半透明玻璃，手要不要也做成玻璃质感？
> 我的建议是**手保持真人皮肤**（黄种人肤色、扁平柔和明暗，和 EP.07、EP.08 同一只手）：
> - 手是「人」，玻璃只给「物」，观众一眼分得开；
> - 玻璃手容易显得假、像模型，用户以前批评过「画面做的很假」。
> 下面的 prompt 按「真人皮肤」写。

## 怎么用
1. **上传 EP.07 的基础图作参考**：`07-shoubiaolvguang/assets/people/arm-top.webp`。用「同一个人、同样画风」生成，几集看起来是同一个人的手。
2. 输出 PNG、透明背景（不行就用纯色 #ECEBE6 浅灰底，我来抠）。尺寸 1536×1024。
3. 生成好直接发到对话里。用了 AI 生成的图，发布时勾选「内容由 AI 生成」。

## 用在哪
| 图 | 用在 | 秒数 |
|---|---|---|
| 右手从上方捏着手机两侧，把它平放到桌上的充电板上（斜俯视） | 开头放手机；结尾闭环再放一次；小提示里把手机挪正 | 0–2.75、47.5–50.25、50.25–54.25 |

---

## 右手把手机放到充电板上
横版 1536×1024，上传 EP.07 基础图作参考：

```
Use the same illustration style, the same skin tone and the same hand as the reference image. Draw only a young East Asian woman's right hand and forearm, seen from above at about 50 degrees (a three-quarter top-down view, like looking down at a desk). The forearm comes in from the upper-RIGHT edge of the canvas and leaves through that edge. The hand is lowering a smartphone flat onto a desk, holding it from above by its two long sides: the thumb presses on the LEFT long side, the index, middle and ring fingers curve over the RIGHT long side, the fingertips just touching the edges, the little finger relaxed. The phone itself is an EMPTY, transparent flat rectangle lying almost horizontal (in this perspective about 30% of the canvas width and 45% of the canvas height, centred slightly left of the middle) — leave it completely empty, it will be added later. Nothing under the rectangle. Five fingers, anatomically correct, clear knuckles and fingertips, short natural nails, soft gradient shading. Bare hand: no ring, no bracelet, no watch, no sleeve. Warm natural East Asian skin tone (around #EBCBA5, shadows around #D6AD84). Not a photo, not a 3D render, not a cartoon. Transparent background. No phone, no charger, no desk, no text, no watermark, no logos, no hair, wrinkles or dense texture.
```

## 生成后请检查
- 和 EP.07、EP.08 是不是同一只手的感觉（肤色、手指粗细、画风）。
- 拇指和其余手指分别搭在空位的左右两条长边上，姿势像是「从上往下放」。
- 留出的空位里真的什么都没有；图里没有手机、充电板、文字、品牌、水印。
