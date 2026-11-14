# 远景 PoC 05：数据中心冷通道，Cycles 对 LTX

DECISIONS 11-14 记的下一步：「测一个远景氛围镜头，看 LTX 在它擅长的地方比 Cycles 好多少」（用户：「我们再测试一个远景的」）。

## 镜头
- 数据中心冷通道：两排 42U 机柜面对面，中间是开孔通风地板，头顶是黄色光纤槽、黑色梯架和条形灯，空气里有薄雾。服务器、存储、交换机面板是程序生成的贴图（`make_panel_textures.py`，示意，不是某个真实型号），带绿、蓝、琥珀色指示灯。
- 相机从通道口匀速推进约 3.3 m，后半段转向右侧第 5 台机柜第 27U 的一台 1U 交换机（OSFP 口插着绿色拉环模块，呼应插入镜头）。
- 24 fps、145 帧（6.04 秒）、1088×1920，按原生 24 fps 渲染（PoC 04 的教训：不再从 30 fps 降帧）。
- 脚本：`build_aisle.py`。`frames` / `anim` 出 Cycles，`clay` 出 Workbench 灰模，灰模和 Cycles 同场景、同相机、同尺寸。

## 三版
| 版本 | 怎么出 | 机器 / 用时 / 费用 |
|---|---|---|
| **Cycles** | 96 采样 + 降噪，薄雾体积，动态模糊 | RunPod 两台 RTX 4090，墙钟 12.1 分钟，约 **$0.36**，每帧约 8–9 秒 |
| **LTX V1** | 灰模 + Cycles 首帧 | RunPod A100-SXM4-80GB（$2.19/时），两版共墙钟 17.1 分钟，约 **$0.62**；下载权重 255 秒，V1 生成 314 秒、V2 277 秒 |
| **LTX V2** | 灰模 + Cycles 首、中、末三帧（第 0、72、144 帧） | 同上 |

- 灰模在本机 CPU 上用 Workbench 渲，145 帧，费用 0。
- 费用都是脚本按单价和墙钟时长估的上限，以 RunPod 账单为准。所有机器都已删除。
- LTX 打开了隐形标记：两版视频都检测到（bit accuracy 1.0），音频检测不稳（0.5），和 PoC 04 一样。原始结果见 `deliver/marks.txt`。

## 对比（`deliver/`）
- `compare_clay_cycles_v1_v2.mp4`：四联（灰模 / Cycles / V1 / V2），每联 360 宽；
- `对比_五个时刻_上Cycles_中V1_下V2.jpg`：0、1.5、3、4.5、6 秒；
- `放大_末帧交换机_Cycles_V1_V2.jpg`：结尾交换机附近的局部。

## 看到的
- **三版都跟住了灰模**：推进速度、转向、终点构图一致。
- **Cycles**：面板细节清楚（硬盘托架、指示灯、交换机的 OSFP 口和绿色拉环）；运动平稳，逐帧差值没有突变。只有第 51 帧通道远处的地板单帧变暗（亮度差 2.7/255），大约是降噪的偶发误差，正常播放时很难察觉。
- **LTX V1（只给首帧）**：
  - 指示灯更绿、更显眼，有一点「电影感」；
  - 但**改动了结构**：约 4.5 秒，通道尽头变成一个浅灰色房间的墙角，左边那排机柜被截短；
  - 结尾的交换机变糊，面板被重画成一条条发绿光的横带，**认不出 OSFP 口**。
- **LTX V2（三帧约束）**：几乎就是 Cycles 的复制，雾和反光略有差别。没有比 Cycles 更好看，只是多花了钱和时间。

## 结论（建议，待用户定）
- **这个远景里，LTX 没有比 Cycles 好**：V1 好看的部分不多，还改了结构；V2 只是在复刻 Cycles。
- 原因在测试设计：LTX 的外观来自关键帧，而关键帧就是我们的 Cycles 帧，所以它很难超过 Cycles。这个场景又是规则的机柜、面板，正好是程序建模的强项，Cycles 本身已经够好。
- **LTX 真正可能有优势的情况**：用 Cycles 做起来很费劲的画面，比如人、手、真实的杂乱环境；同时首帧换成**图像模型生成的写实图**，而不是 Cycles 帧。如果还想测，下一次应该按这个方向设计。
- 在那之前，**远景和近景都用 Cycles** 更省事：确定性强，单次约 $0.36 / 6 秒，不需要额外查编出来的结构。

## 视频文件（不进仓库，sha256）
- `out/aisle_cycles_1088.mp4` 80fe3079d466e2037dc37819e7b1986b3cfba8b225c370442244a89e1be06d22
- `ltx_out/v1_first.mp4` 3f0d1ec8e579afa637319519d8985707c27e9c49e771516e7cf8319f0ced0197
- `ltx_out/v2_keys.mp4` 4e16eaeee17c907f66614df2ebfe9cb4728d1983b05c1b87ba473a34e5dc48c7

## 重做
在本目录执行：
```bash
python3 make_panel_textures.py
```
```bash
blender -b --factory-startup --python-exit-code 1 --python build_aisle.py -- clay --clay --out out/clay/f
```
```bash
ffmpeg -framerate 24 -i out/clay/f%04d.png -c:v libx264 -crf 14 -pix_fmt yuv420p -an ltx_in/clay_24.mp4
```
- Cycles：用 `tools/runpod_render.py`（在 `claude/bold-hypatia-1tyot4` 分支）跑 `anim --spp 96 --gpu`，分 4 段；
- LTX：在仓库的 `experiments` 目录执行下面这条：
```bash
python3 ltx_poc04/runpod_ltx.py run farshot_poc05/ltx_in farshot_poc05/ltx_out --gpu "NVIDIA A100-SXM4-80GB,NVIDIA A100 80GB PCIe" --max-hours 1.0 --yes
```
