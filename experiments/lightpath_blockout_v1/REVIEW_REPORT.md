# PROJECT LIGHTPATH — 一次跨越 · 30 秒 Blender Blockout V1.0 · 导演审阅包

任务书：用户在会话里转来的《PROJECT LIGHTPATH — 30s Cinematic Blockout V1.0》（导演 ChatGPT，执行 Claude）。
本目录只做 Blender 灰盒。没有做写实模型、Cycles、AI 图像、LTX、Seedance，没有用云 GPU，费用 $0。
没有改动任何已有 PoC 目录（`experiments/` 下其它目录原样）。

## 1. 交付清单
| 要求 | 文件 | 规格（ffprobe 实测见第 7 节） |
|---|---|---|
| A 总预览 | `deliver/lightpath_blockout_30s.mp4` | 720×1280，30 fps，900 帧，30.000 秒，H.264，无音轨 |
| B 六个单镜头 | `deliver/shots/S01_departure.mp4` … `S06_arrival.mp4` | 各 150 帧 / 5.000 秒 |
| C Blender 工程 | `lightpath_blockout.blend`（由 `build_scene.py` 生成） | Blender 5.2.3；主场景 `LIGHTPATH_master` + 6 个镜头场景 |
| D 参考帧 | `deliver/reference_frames/S0x_F001_first.png`、`S0x_F###_hero.png`、`S0x_F150_last.png` | 相机原图 720×1280，不裁切、不加任何叠加 |
| E 审阅包 | `deliver/contact_sheet_30s.jpg`、本报告、`OBJECTS.md` | 接触表每镜 6 帧（局部 F001/030/060/090/120/150） |
| 哈希 | `deliver/SHA256SUMS.txt` | |

重做：在本目录运行
```bash
blender -b --factory-startup --python-exit-code 1 --python build_scene.py -- anim
```
```bash
python3 package.py
```
本机 4 核 CPU、Workbench 软件渲染，三个进程并行约 35 分钟出 900 帧（`-- anim 1 300` 这样分段）。

## 2. 画面约定
- Workbench 灰盒：物体纯色、棚拍基础光、黑色轮廓线、轻微腔体阴影和投影。没有景深、运动模糊、字幕、标签、UI、旁白。
- 硬件中性灰；PCB 暗绿；阻焊下的走线是浅一点的绿（**不画成铜色**，免得和琥珀色的电信号混）。
- 电信号：克制的琥珀色。光信号：克制的青色（红外光本来看不见，青色是示意）。
- **同一个 8 位数据包 `1 0 1 1 0 0 1 0`** 贯穿全片：在走线上是琥珀色的四段短条，在波导和光纤里是青色的四段短条，回到电路板上又是琥珀色。观众不需要读懂比特，只看到「同一个图样换了一种载体」。
- 每一段信号指示都画在真实的物理路径上（走线、键合线、片上馈线、波导、光纤纤芯），不在空中飞，不是发光小球。
- 每一拍里信号都按恒定速度走；各镜头的速度不同（每镜相当于不同的慢放倍率，真实传播是纳秒级）。同一个镜头内，同一个比特在电和光里**时长相同、长度不同**（光在硅波导里比电在 PCB 上慢，所以光段的短条更短）——这一点是对的物理，不是误差。

## 3. 空间布局（一个连续的世界）
- 两个开放式四柱机柜并排：A 在左（x = −32），B 在右（x = +32），前面朝 +Y（相机所在的通道）。两侧还有四个远景机柜。
- 两台**同型号**的 2U 服务器装在各自机柜的最上层，顶盖拿掉（维护状态）。板上：后部是主机 CPU 和内存，中间是两颗 GPU（GPU A / GPU B 是左边那颗），前面是 NIC，最前面板边是三个 OSFP 笼子，入口和机箱 I/O 面板平齐略伸出。
- 光模块从机箱外插入笼子，前脸朝外，MPO 插头插在前脸上（按 11-14 决定，装配方向在灰模阶段就核对过）。
- 光纤：A 模块前脸 → 向前 → 下弯进顶层服务器下面的 1U 理线槽 → 沿槽横穿到 B 机柜 → 上弯 → B 模块前脸。全长约 100 cm，弯曲半径约 3.5 cm。
- A 板上数据向 +Y 走（GPU → NIC → 笼子），B 板上向 −Y 走（笼子 → NIC → GPU）。相机在电路段总是跟在信号后面，所以信号在画面里一直「往前、往画面上方」走。

（第 4–8 节在成片渲完、逐帧看过之后填写。）
