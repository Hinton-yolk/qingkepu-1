# EP.06 人脸解锁 · 人物图片的生成 prompt（给 GPT 生图用）

用户 2026-11-11：「建模太丑了，你给我一个prompt, 我让GPT来生成图片」。

## 怎么用
1. **先生成第 1 张（基础图）**。满意后，后面每一张都**上传第 1 张作参考**，用「编辑这张图」的方式改。这样能保证是同一个人、同一个姿势、同一个位置，片子里切换时不会跳。
2. 每张都要：**竖版 1024×1536、PNG、透明背景**（GPT 生图可以直接选透明背景；不行就用纯色 #ECEBE6 浅灰底）。
3. 生成好后直接发到对话里，我来抠图、放进片子。手机屏幕上的锁、密码键盘、光点都由我在片子里画，图里不要有。
4. 用了 AI 生成的图，发布时勾选「内容由 AI 生成」。

## 共同的风格（每条 prompt 后面都已经带上）
干净的扁平矢量插画、柔和的渐变明暗，不是照片、不是 3D 渲染、不是日漫大眼；东亚年轻女性，黄种人自然肤色（约 #EBCBA5，阴影约 #D6AD84）；不要密集重复的纹理；不要任何文字、水印、品牌标志。

---

## 1. 基础图：素颜侧脸（其他图都以它为参考）

```
A clean, modern flat vector illustration of a young East Asian woman in strict side profile, facing right. Head and shoulders only, the head occupying the upper two thirds of a tall portrait canvas: the top of the head at about 12% from the top, the chin at about 60%, the neck and the top of the shoulders reaching the bottom edge. Natural, friendly expression, eyes open, looking straight ahead to the right, natural eyelashes. Dark brown-black shoulder-length bob with a soft side fringe, hair tucked behind the ear so the ear is visible. Warm natural East Asian skin tone (around #EBCBA5, shadows around #D6AD84), soft, subtle gradient shading, a gentle highlight on the forehead, the nose bridge and the cheek. No makeup: natural pink-beige lips. Simple plain top, no jewellery. Elegant, realistic proportions, not stylised cartoon, not anime, not a 3D render, not a photo. Transparent background. No text, no watermark, no logos, no dense repeating patterns.
```

## 2. 涂口红（开头第一帧）

上传第 1 张作参考：

```
Edit this image: keep the same woman, the same pose, the same position and size on the canvas, the same hair and the same style. She is finishing applying lipstick: her right hand comes up from the bottom of the frame and holds a classic lipstick (black case, gold collar, red bullet) with the thumb and index finger; the red tip touches the middle of her lower lip. The upper lip is already red (#C2303A), the lower lip half done. The hand is drawn naturally and anatomically correct: five fingers, relaxed, the back of the hand and the wrist leading out of the bottom edge of the frame. Light blush and soft brown eyeshadow. Transparent background. No text, no watermark, no logos.
```

## 3. 全妆（化妆那一段；也会被我调成灰度当「红外照片」示意）

上传第 1 张作参考：

```
Edit this image: keep the same woman, the same pose, the same position and size, the same hair and style. She now wears full everyday makeup: red lipstick (#C2303A) on both lips, a soft rosy blush on the cheek, soft brown eyeshadow and defined lashes. No hands in the picture. Transparent background. No text, no watermark, no logos.
```

## 4. 全妆 + 修容（「修容让鼻梁看着更高」那一拍）

上传第 3 张作参考：

```
Edit this image: keep everything exactly the same (the same woman, pose, position, size, makeup), and add visible contour makeup: a soft brown shadow down the side of the nose bridge and under the cheekbone, and a light highlight along the top of the nose bridge, so the nose looks a little higher. The face shape and the outline of the profile must stay exactly the same — only colour and shading change. Transparent background. No text, no watermark, no logos.
```

## 5. 全妆 + 口罩（口罩那一段、结尾闭环）

上传第 3 张作参考：

```
Edit this image: keep the same woman, the same pose, the same position and size, the same hair and eye makeup. She now wears a plain light blue-white disposable face mask, seen from the side, covering the nose (up to the bridge), the mouth and the chin; the ear loop goes behind the ear. The eyes and the eyeshadow stay visible above the mask. No hands. Transparent background. No text, no watermark, no logos.
```

## 6. 拿手机的手（单独一张，所有拿手机的镜头都用它）

不需要参考图：

```
A clean, modern flat vector illustration, the same style as a soft-shaded editorial illustration: a young East Asian woman's right hand holding a modern smartphone upright, the screen facing the viewer. The phone is generic with no brand and no logo: thin black bezels, rounded corners, a small black pill-shaped cut-out at the top centre of the screen, and the screen itself plain solid dark grey with nothing on it. Natural, anatomically correct hand: the thumb resting on the lower left edge, the other fingertips curling around the right edge from behind, the palm and the wrist below the phone, leading out of the bottom edge of the frame. Warm natural East Asian skin tone (around #EBCBA5, shadows around #D6AD84). Phone centred, taking about 60% of the canvas height. Transparent background. No text, no watermark, no logos.
```

---

## 生成后请检查
- 6 张里的人是不是同一个人（脸型、发型、肤色一致），侧脸朝右，位置大小一致。
- 手指数和形状对不对（AI 最容易出错的地方）。
- 图里没有任何文字、品牌、水印。
- 手机屏幕是纯色的，没有图标。
