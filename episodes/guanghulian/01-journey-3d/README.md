# 白话光互连 01（3D 正式版）：一个比特的旅程：从 GPU 到 GPU

用户 2026-11-12 任务书（原文：`preprod/00_任务书_用户原文.md`）。竖屏 1080×1920，30 fps，Blender（写实硬件）+ Remotion（波形、标注、字幕、合成）。
新对话先读这个文件，再读 `preprod/02_分镜.md` 和 `timeline/timeline.json`。

## 现在到哪一步（2026-11-12）
**阶段 A（前期）已交付，等用户确认；阶段 B（Animatic）刚起步。没有任何成片画面，没有渲过正式帧，没有配音。**

| 项 | 状态 |
|---|---|
| 旁白草案、分镜、资产清单、科学审查表、制作依赖、时间轴 | 已写（v0.2）。等用户确认旁白、开头备选和科学取舍 |
| 科学审查 | 第 1 轮「不通过」（7 处必改），已改；复核结果见 `preprod/03_科学审查表.md` 文末 |
| 监督 | 要求清单已更新（`../要求清单_3D与Blender.md` G 节，76 条）；第一轮意见已处理 |
| S01 机房、S02 GPU 封装、S03 SerDes 的 Blender 场景 | **v0 粗模**：脚本能跑，只在云端用 Cycles CPU 渲过 270×480 的静帧看构图（`previews/`）。不是最终资产 |
| S04–S10 的 Blender 场景 | 没开始（`timeline.json` 里状态是 `planned`） |
| Remotion 工程 | 见 `remotion/README.md` |
| Animatic（全片动态分镜） | 没开始。还缺：S04–S10 的预演场景、临时旁白、低清序列帧 |
| 高质量代表帧、Cycles 序列帧、云 GPU 验证 | 没开始。云 GPU 还没连上（见 `preprod/05_制作依赖.md` 第四节） |
| 观众（Codex） | 没开始。Codex 已装，需要用户登录；要等有 Animatic 才有东西给它看 |
| 封面、标题、`publish.md` | 没开始 |

## 目录
```
preprod/     00 任务书原文 · 01 旁白草案 · 02 分镜 · 03 科学审查表 · 04 资产清单 · 05 制作依赖
FACTS.md     每个数字和结构说法的来源
timeline/    timeline.json（唯一的时间来源）· validate.py（检查镜头衔接、语速、标注越界）
blender/     common.py（公共库）· s01_datacenter.py · s02_gpu_package.py · s03_serdes.py · fetch_assets.sh
remotion/    合成工程
previews/    低清接触表（粗模，只看构图）
```

## 怎么跑
```bash
python3 timeline/validate.py --table                      # 检查时间轴并打印时间表
blender/fetch_assets.sh                                    # 下载 CC0 的 HDRI 和贴图（不进仓库）
blender -b --python-exit-code 1 --python blender/s02_gpu_package.py -- <输出目录> --times 13.1,16.4,22.8 --res 270x480 --samples 24 --anchors
```
- 时间一律是全片时间（秒），帧号是全片帧号：帧 = round(秒 × 30) + 1。输出文件名 `<镜头号>_<帧号 6 位>.png`。
- `--anchors` 另外输出 `anchors_Sxx.json`（标注锚点的屏幕坐标），给 Remotion 贴标签用。
- `--gpu` 在有显卡的机器上用 OptiX / CUDA；`--range a b --step n` 渲一段。已有的帧会跳过，可以续渲。每次渲染写 `render_log_Sxx.json`（设备、采样、每帧耗时）。
- 云端容器重启后 Blender 要重新下载：`https://download.blender.org/release/Blender5.2/blender-5.2.3-linux-x64.tar.xz`。这台容器没有显卡，只能 Cycles CPU（270×480、24 采样，每帧约 5–11 秒）。

## 粗模的已知问题（升级成正式资产前要解决）
**S02 GPU 封装**
- 硅透明化之后露出的连线层底色偏亮偏暖，应该是深蓝底 + 铜线；18.6 秒前后画面发灰，位置感弱。
- 32 条数据线亮和暗的差别在小图里看不清，1080 宽时再查。
- 封装只有外形：没有散热盖 / 导热材料、基板走线、丝印、焊点；电路板的走线纹是程序条纹，不是真实布线。
- 封装下面缺中介层到基板的 C4 凸点、基板到电路板的焊球（镜头不穿到那里，但剖面镜头会需要）。

**S03 SerDes**
- 结尾（36.5–39 秒）镜头已经落到输出通孔和微凸点上。为了看得见，把通孔和微凸点周围 ±36 µm 的连线清掉了：这是示意，真实芯片这里同样布满连线，角注要写。
- 亮的线仍然偏白，要调成更饱和的金色。
- 串行输出线每 0.1 秒闪一次（10 Hz），成片里可能刺眼，要看动态后调节拍或对比。
- 二选一单元、输出驱动只是方块加栅条；连线只有三层，没有通孔阵列和层间关系。
- 微凸点画的是间距 45 µm，FACTS 是「约 40 µm 一档」，定稿时统一。
- 只看过静帧，没看过动态：相机在 35.5–39 秒转向比较大，要出低清序列确认不晕。

**S01 机房**：见 `previews/S01_blockout_v0.jpg` 和 Blender Artist 的报告（记在本文件「交接」一节）。

## 等用户定的事
见 `DECISIONS.md`「待定事项」里 2026-11-12 那一条，以及 `preprod/01_旁白草案.md`、`preprod/03_科学审查表.md` 第一节。

## 交接
（每个阶段结束时补：做了什么、没做什么、下一步。）
