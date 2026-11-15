# Seedance Prompt · PoC 02：环绕镜头 + 光模块插入

对应 Blockout（提交 4b4566a）。本文件只写 Prompt，没有运行 Seedance。

## 使用前
- 上传顺序：先上传 `blockout.mp4`，在 Prompt 里就是 @视频1；再上传 800G OSFP 参考图，就是 @图片1 到 @图片N。平台要是用别的引用写法，把名字换掉就行。
- 规格：竖屏 9:16，6 秒；能选就用最高画质。
- **挡板高度要你先定**（见文末「挡板的取舍」）。默认用 A 段（跟 Blockout 一样，挡板矮）；想按标准 PCIe 挡板拍，把 Prompt 里的【挡板】一段换成 B 段。

## 最终 Prompt（中文，直接复制）

```
【参考素材怎么用】
@视频1 是灰盒动态预演，只用来确定三件事：物体的空间布局、光模块的直线插入动作、摄影机的弧线运动和时间节奏。它的颜色和体块不是外观：蓝色长方体是光模块；中灰色中空盒是金属模块笼子（两个并排）；深钢灰色竖板是网卡的金属挡板，往下连着机箱后壁；绿色平板是网卡电路板；炭灰色大方块是芯片散热器；黑色、赭色小块是芯片和元件。不要保留灰盒的纯色、黑色描边和简化形状。
@图片1 至 @图片N 是 800G OSFP 光模块和配套硬件的实物参考，决定所有外观细节：模块外壳、散热鳍片、拉环、前端光纤接口，笼子入口的簧片，电路板和元件。细节以参考图为准，不要自行发明结构、文字或标志。

【这个镜头的核心】
一个连续镜头里有两条互不干扰的运动：
1. 摄影机绕着固定不动的模块笼子走一段约 60° 的弧线，同时缓缓下降、靠近；
2. 光模块在世界中沿笼子轴线笔直滑入，朝向始终不变，不随镜头转动。
挡板、两个端口、电路板、散热器在世界中纹丝不动。观众应该同时感到「镜头在绕着走」和「模块在往里进」，两者不混在一起。

【场景】
竖屏 9:16，6 秒，一镜到底，不剪辑。
服务器背面，一块双口网卡的端口区。笼子装在电路板的边缘，入口和金属挡板平齐，两个方形端口并排开在挡板上。光模块在挡板外侧，与左边那个端口严格同轴，即将从机箱外面插进去；右边的端口始终空着。
【挡板】挡板很矮，只比端口略高一点，越过它的上沿可以看到后面的笼子、电路板、一排小元件和远处的芯片散热器，层层后退。
画面中不出现手或工具。

【光线】
光源固定在世界里，不跟着镜头走：一盏冷白色硬光从左上方掠过挡板和模块，机箱深处有一点暖色的微弱逆光，勾出散热器和元件的轮廓。镜头绕行时，高光在挡板的金属面和模块的鳍片上缓缓流动，背景的轮廓光一层层错开——让观众从光的变化里感到镜头真的在空间中移动。低调、高反差，暗部保留细节。

【动作与镜头】（时间和路径跟随 @视频1）
0–1.5 秒：镜头从左前方的高处开始，第一帧就在沿弧线向右平稳移动。模块静止在端口前。前景的挡板和后面的散热器明显错开。
1.5–4.5 秒：模块沿笼子轴线笔直、匀速地滑进左边的端口，穿过挡板开口，越来越深；与此同时，镜头继续绕行、下降、靠近。模块的朝向在世界中保持不变，参照不动的挡板就能看出它在往里进。约 4 秒时，镜头从模块正前方经过，此时模块离挡板只剩一小段，正在减速。
4.5 秒：模块到位，轻轻一顿，稳稳停住，没有反弹。只剩前端和拉环露在挡板外面。
4.5–6 秒：模块完全静止。镜头继续绕到右前方的低机位，平稳减速后停下。最后的构图：模块前端在画面中央，左右是金属挡板，右边是那个空着的端口，后上方是失焦的散热器。

【质感】
真实微距产品摄影：中等景深，主体清晰，远景柔和失焦；金属拉丝纹理、细微划痕和冲压边缘清晰可辨；轻微自然的运动模糊。色调偏冷的青灰，点缀少量暖金色反光。

【避免】
模块不能旋转、变形、跟着镜头转，也不能穿过挡板或笼子的实体部分；挡板、端口和电路板不能移动、漂移或变形；右边的空端口不要插入模块；不要出现手、工具、发光的激光束、数据流粒子、全息界面、文字、标志字样、火花或爆炸；不要甩镜、急推、变焦或绕满一圈；不要卡通、塑料或廉价 CG 感。
```

## 挡板的取舍（替换【挡板】那一段）

**A（默认，和 Blockout 一致）**：
```
【挡板】挡板很矮，只比端口略高一点，越过它的上沿可以看到后面的笼子、电路板、一排小元件和远处的芯片散热器，层层后退。
```

**B（标准 PCIe 挡板，更接近常见服务器网卡）**：
```
【挡板】网卡的金属挡板是一块完整的竖直钢板，高度以参考图为准，上面有通风孔；从机箱外面只能看到挡板正面、两个端口和旁边相邻槽位的挡板，电路板被挡在后面。@视频1 里露在挡板上方的电路板、元件和散热器只表示「后面有一块网卡」，实际画面中被挡板遮住，空间层次改由挡板的通风孔、相邻槽位的挡板和机箱后壁提供。
```

- A 和 Blockout 完全一致，Seedance 最容易照做；但标准 PCIe 网卡的挡板要高得多，A 的「矮挡板」需要一个说得通的实物。一种可能是 OCP 3.0 这类面板很矮的网卡形态，但 **OSFP 端口能不能装在这类面板上，我没有核实**，需要你判断。
- B 符合常见的 PCIe 网卡，但和 Blockout 不一致：画面里看不到电路板，Seedance 也更可能被两边的信息拉扯。

## 备用：英文版（默认 A 段）

```
[How to use the references]
@Video1 is a graybox motion previs. Use it ONLY for spatial layout, the module's straight-line insertion, and the camera's arc move and timing. Its colors and blocks are not the look: the blue box is the optical transceiver; the mid-gray hollow boxes are two side-by-side metal module cages; the dark steel-gray vertical plate is the NIC's metal bracket, continuing down as the chassis rear wall; the green slab is the NIC circuit board; the large charcoal block is a chip heatsink; small black and ochre blocks are chips and components. Do not keep the flat colors, outlines or simplified shapes.
@Image1–@ImageN are real 800G OSFP references and define every visual detail: housing, heatsink fins, pull tab, front fiber ports, cage springs, board and components. Follow them; do not invent structures, text or logos.

[The core of this shot]
Two independent motions in one continuous shot:
1. The camera travels an arc of about 60° around the fixed module cage while slowly descending and moving closer.
2. The transceiver slides straight in along the cage axis; its orientation stays fixed in the world and never turns with the camera.
The bracket, both ports, the board and the heatsink stay absolutely still in the world. The viewer should feel both "the camera is circling" and "the module is going in", without the two blending together.

[Scene]
Vertical 9:16, 6 seconds, one continuous take, no cuts.
The rear of a server: the port area of a dual-port NIC. The cages sit at the edge of the board, their openings flush with the metal bracket; two square ports side by side in the bracket. The transceiver waits outside the bracket, perfectly coaxial with the left port, about to be inserted from outside the chassis. The right port stays empty throughout.
[Bracket] The bracket is low, only slightly taller than the ports; over its top edge you can see the cages, the board, a row of small components and a distant chip heatsink, receding in layers.
No hands or tools in frame.

[Light]
Lights are fixed in the world, not attached to the camera: a hard cool-white key grazes the bracket and module from upper left; a faint warm backlight deep inside the chassis rims the heatsink and components. As the camera circles, highlights glide across the bracket's metal face and the module's fins, and the background rim lights shift layer by layer — the light itself tells the viewer the camera is truly moving through space. Low-key, high contrast, detail kept in the shadows.

[Action and camera — timing and path follow @Video1]
0–1.5s: the camera starts high at front-left and is already moving along the arc to the right from the first frame. The module waits motionless in front of the port. The foreground bracket and the background heatsink visibly slide past each other.
1.5–4.5s: the module glides straight and steadily into the left port, through the bracket opening, deeper and deeper; meanwhile the camera keeps circling, descending and closing in. The module's orientation never changes in the world; against the still bracket it clearly reads as going in. Around 4s the camera passes directly in front of the module, which is now only a short distance from the bracket and slowing down.
4.5s: the module seats with a tiny, precise stop — no bounce. Only its front end and pull tab remain outside the bracket.
4.5–6s: the module is completely still. The camera continues to a low front-right position and eases to rest. Final frame: the module's front end centered, metal bracket to both sides, the empty port on the right, an out-of-focus heatsink behind and above.

[Texture]
Real macro product cinematography: moderate depth of field, subject sharp, background softly out of focus; brushed metal grain, fine scratches and stamped edges visible; subtle natural motion blur. Cool cyan-gray grade with small warm-gold glints.

[Avoid]
The module must not rotate, deform, turn with the camera, or pass through solid parts of the bracket or cage; the bracket, ports and board must not move, drift or deform; do not put a module into the empty right port; no hands, tools, glowing laser beams, data particles, holographic UI, text, logos, sparks or explosions; no whip pans, crash zooms, zooming or full orbits; no cartoon, plastic or cheap CG look.
```

## 导演思路
- **让光替镜头作证**。环绕镜头最怕被模型简化成「原地摇」或「物体在转」。光源固定在世界里，镜头一绕，高光就在金属面上流动，背景的轮廓光一层层错开。这是真实摄影机移动才会有的现象，比任何「camera orbit」字样都更能把 Seedance 拉向真实的空间运动。
- **给模块一个不动的参照面**。整段只靠挡板判断模块在不在动：镜头怎么转，挡板都不动，模块离它越来越近、穿过它的开口。所以 Prompt 反复强调挡板、端口和电路板纹丝不动。
- **两条运动分开写**，最后用「核心」一段单独再说一次。这是这次实验最容易失败的地方，值得占用 Prompt 的篇幅。
- **结尾换了一个方向看**：开头左前高处俯看全局，结尾右前低处平视前端，像从「旁观装配」变成「凑近看结果」。空着的右口和刚插好的左口并排，是一个安静的对照。
- 延续 PoC 01 的冷青灰色调和「到位一顿」，两段放在一起是同一个世界。

## 参考素材的分工
| 来自 Blockout（@视频1） | 来自实物参考图（@图片1–N） |
|---|---|
| 布局：双口、笼子在板边、入口与挡板平齐、模块在机箱外同轴待插 | 光模块外观：外壳、鳍片、拉环、前端接口 |
| 模块的动作：1.5–4.5 秒直线插入，4.5 秒停稳 | 笼子入口簧片、电路板、元件、散热器的样子 |
| 摄影机：绕笼口约 60°（左前高 → 右前低），同时下降、靠近，约 4 秒越过插入轴线 | 挡板的样子（A 方案高度跟 Blockout，B 方案跟参考图） |
| 时间节奏和最终构图 | 到位后露在外面的长度（以实物为准） |

Prompt 自己补的：世界固定的光源和流动的高光、景深、质感、到位的「顿」、避免清单。

## 试过以后可能要调的
- **模块跟着镜头转、或者粘在画面上**：把【这个镜头的核心】挪到 Prompt 最前面；再加一句「模块相对挡板在动，挡板相对画面在动，这是两件事」。
- **镜头退化成原地摇或变焦**：加一句「摄影机的位置在移动，不是原地转头；前景挡板和背景散热器之间的错位越来越大」。
- **右边空口也被插上了模块**：在【避免】里把这一条移到最前面。
- **出现手**：把「画面中不出现手或工具」也放进【避免】的开头。
