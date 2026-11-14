# Seedance Prompt · PoC 01：光模块插入

对应 Blockout v2（提交 a69d359）。本文件只写 Prompt，没有运行 Seedance。

## 使用前
- 上传顺序：先上传 `blockout.mp4`，在 Prompt 里就是 @视频1；再上传 800G OSFP 参考图，就是 @图片1 到 @图片N。
- 如果平台对参考素材用别的写法（例如按上传顺序编号、或叫「参考视频 1」），把 Prompt 里的 @视频1、@图片1 换成对应的名字就行。
- 规格：竖屏 9:16，6 秒；平台能选的话用最高画质。

## 最终 Prompt（中文，直接复制）

```
【参考素材怎么用】
@视频1 是一段灰盒动态预演，只用来确定：物体之间的空间关系、主体的动作、摄影机路径和时间节奏。它的颜色和体块不是外观——蓝色长方体是光模块，灰色中空盒是金属模块笼子，绿色平板是网卡电路板，黑色是背景。不要保留灰盒的纯色、黑色描边和简化形状。
@图片1 至 @图片N 是 800G OSFP 光模块和配套硬件的实物参考，决定所有外观：模块外形和比例、金属外壳、散热鳍片、拉环、前端光纤接口、笼子的结构和入口簧片、电路板颜色与元件、设备环境。细节以参考图为准，不要自行发明结构、文字或标志。

【场景】
竖屏 9:16，6 秒，一个连续镜头，不剪辑。
服务器机箱内部的微距世界：一块网卡电路板向画面深处延伸，板上的金属模块笼子张着方形入口。一只 800G OSFP 光模块与笼子严格同轴，停在入口正前方，即将被送进去。
环境暗而有层次：远处是失焦的机箱结构和线缆，化成柔和的暗色光斑；侧光里有极细的微尘缓缓浮动。

【光线】
一束冷白色的硬质侧顶光从画面左后方掠过，在模块的金属外壳和散热鳍片上刻出一道道锐利的高光线；电路板上的焊盘和元件边缘闪着细小的反光点。右前方一盏很弱的暖色补光托住模块前端。低调、高反差的产品电影光，暗部保留细节，不发灰。

【动作与镜头】（时间和路径跟随 @视频1）
0–1.2 秒：镜头从斜前上方缓缓推近，交代笼子入口和模块的同轴关系。模块静止。
1.2–1.7 秒：镜头几乎停住。模块开始沿笼子轴线平稳滑入，入口边缘的金属簧片上映出它推进的倒影。
1.7–4.0 秒：镜头跟着模块露在外面的那一端缓慢跟进、靠近，并向侧面轻移，前景元件和背景之间产生明显视差。模块推进时，外壳上的高光沿着散热鳍片一格一格向前滑过，让运动有节拍感。模块匀速进入，不旋转、不晃动。
4.0 秒：模块到位，轻轻一顿，稳稳停住，像一次精确的机械咬合，没有反弹。只剩前端和拉环留在笼子外面。
4.0–6.0 秒：模块完全静止，镜头继续推向它的前端面，焦点从笼子入口平稳移到前端的光纤接口上，背景进一步虚化。最后镜头减速，停在前端面：空着的光纤端口安静地朝向观众，等待光纤接入。

【质感】
真实微距摄影：浅景深，焦外柔和，轻微自然的运动模糊；金属的拉丝纹理、细微划痕和加工痕迹清晰可辨。色调是偏冷的青灰，点缀少量暖金色反光。

【避免】
不要发光的激光束、数据流粒子、全息界面、文字、标志字样、火花或爆炸特效；不要甩镜、急推、绕圈或穿模；不要出现手；模块不能变形、旋转或穿过笼子外壁；不要卡通感、塑料感或廉价的 CG 渲染感。
```

## 备用：英文版（中文版效果不理想时试）

```
[How to use the references]
@Video1 is a graybox motion previs. Use it ONLY for spatial layout, the subject's motion, the camera path and timing. Its colors and blocks are not the look: the blue box is the optical transceiver, the gray hollow box is the metal module cage, the green slab is the NIC circuit board, black is background. Do not keep its flat colors, outlines or simplified shapes.
@Image1–@ImageN are real 800G OSFP references and define every visual detail: module shape and proportions, metal housing, heatsink fins, pull tab, front fiber ports, cage structure and EMI springs at the opening, board color and components, surrounding hardware. Follow them; do not invent structures, text or logos.

[Scene]
Vertical 9:16, 6 seconds, one continuous shot, no cuts.
A macro world inside a server chassis. A NIC board recedes into depth; a metal OSFP cage on it opens its square mouth. An 800G OSFP transceiver hovers in front of the opening, perfectly coaxial, about to slide in. Dark, layered surroundings: out-of-focus chassis structures and cables melt into soft bokeh; fine dust drifts through the side light.

[Light]
A hard, cool-white top-side key from back-left grazes the scene, carving crisp specular lines along the metal housing and heatsink fins; solder pads and component edges glint. A faint warm fill from front-right holds the module's front end. Low-key, high-contrast product-film lighting with detail kept in the shadows.

[Action and camera — timing and path follow @Video1]
0–1.2s: slow push-in from a high front three-quarter angle, establishing the coaxial alignment. Module still.
1.2–1.7s: camera nearly holds. The module begins to glide along the cage axis; its reflection slides across the springs at the opening.
1.7–4.0s: camera slowly follows the module's exposed end, closing in with a gentle lateral drift that creates strong foreground/background parallax. As the module advances, highlights travel fin by fin along the housing, giving the motion a rhythm. Steady insertion, no rotation, no wobble.
4.0s: the module seats with a tiny, precise mechanical stop — no bounce. Only the front end and pull tab remain outside.
4.0–6.0s: module completely still; camera keeps pushing toward its front face, focus shifting smoothly from the cage mouth to the fiber ports while the background falls further out of focus. The camera eases to rest on the front face: the empty fiber ports face the viewer, waiting for fiber.

[Texture]
Real macro cinematography: shallow depth of field, soft bokeh, subtle natural motion blur; brushed-metal grain, fine scratches and machining marks visible. Cool cyan-gray grade with small warm-gold glints.

[Avoid]
No glowing laser beams, data-stream particles, holographic UI, text, logos, sparks or explosions; no whip pans, crash zooms, orbiting or clipping through objects; no hands; the module must not deform, rotate or pass through the cage walls; no cartoon, plastic or cheap CG look.
```

## 导演思路
- **把它拍成一次「精密的握手」，不拍成产品转台。** 借的是高级腕表、相机镜头广告的微距语言：暗环境、掠射硬光、浅景深。观众看到的不是「一个零件」，而是两个精密金属件准确对接的那一下。
- **用光替运动打拍子。** 灰盒里的模块是匀速滑动，单看容易平。让一束掠射光沿散热鳍片一格一格扫过，同样的滑动就有了节奏感和质感。这也是 Seedance 最擅长的东西：材质和高光。
- **到位那一下要「顿」，不要「弹」。** 一个很小的机械停顿，给出「咬合了」的触感。这是整段唯一的重音，比加任何特效都有力。
- **结尾落在「空着的光纤端口」上。** 不画发光的激光：真实的光模块端口在接上光纤之前不会发出可见光，画出来行家会一眼看出不对。用「等待光纤」的空端口收尾，既符合物理事实，也留了一个钩子：光从哪里来？刚好接系列下一步要讲的内容。
- **色彩守系列习惯**：冷青灰为主，暖金只做点缀。既不出戏，又和「青色给光、金色给电」的色板一致。

## 参考素材的分工
| 来自 Blockout（@视频1） | 来自实物参考图（@图片1–N） |
|---|---|
| 物体之间的空间关系：模块和笼子同轴，笼子坐在电路板上 | 光模块的外形、比例、金属外壳、散热鳍片、拉环、前端接口 |
| 主体动作：1.2–4.0 秒沿轴线滑入，4.0 秒停稳，之后静止 | 笼子的结构、入口簧片、电路板颜色和元件 |
| 摄影机路径：斜前上方 → 稳住 → 跟随靠近、侧移 → 推向前端面 | 设备环境（机箱内部、线缆） |
| 时间节奏和最终构图：模块前端为主，保留少量笼子和电路板 | 到位后露在外面的长度（以实物为准，灰盒里的约 19% 只是示意） |

Prompt 自己补的部分：光线、氛围、镜头质感、到位时的「顿」、结尾焦点转移，以及「避免」清单。

## 可能需要调整的地方（试过再改）
- 如果 Seedance 把灰盒的蓝色、灰色也带进画面：在【参考素材怎么用】里再强调一次「忽略 @视频1 的颜色」，或者降低视频参考的权重（如果平台有这个选项）。
- 如果镜头运动偏离 Blockout：把【动作与镜头】的时间点压缩成三段（建立 / 插入 / 推近），减少它要记的细节。
- 如果出现光束或粒子：把「避免」那一段挪到 Prompt 开头。
