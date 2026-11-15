# LTX PoC 04：LTX-2.5 Layout-To-Render（灰模动画 → 写实视频）

拿 Blender PoC 03 的 6 秒插入动画（OSFP 模块插进网卡笼子）做灰模，用 LTX-2.5 的 IC-LoRA「Layout-To-Render」生成写实视频，
和 PoC 03 的 Cycles 成片比一比：同样的运动，质感和成本差多少。

两个变体（`in/run.sh`）：
- **V1**：灰模 + 首帧（Cycles 第 0 秒）；
- **V2**：灰模 + 首帧 + 中间帧（3.0 秒，LTX 第 72 帧）+ 末帧（6.0 秒，第 144 帧）。

## 输入（2026-11-14 在云端容器 CPU 上渲，花费 0）
不进仓库（mp4 / 大 png），按下面的命令重新生成。都放进 `in/` 旁边的同一个目录，和 `run.sh` 一起打包上传。

| 文件 | 内容 | 怎么来 |
|---|---|---|
| `clay_24.mp4` | 1088×1920，24 fps，145 帧，6.04 秒；Workbench 统一灰，无雾、散景、景深、动态模糊 | `build_hero.py -- clay --w 1088 --h 1920 --out <目录>/f` 渲 30 fps 的 180 帧（CPU 约 4.5 秒一帧，共 14 分钟），再 `ffmpeg -framerate 30 -i f%04d.png -vf "tpad=stop=1:stop_mode=clone,fps=24" -frames:v 145`（最后一帧补一份，让第 145 帧落在 6.0 秒） |
| `kf_first.png` / `kf_mid.png` / `kf_last.png` | Cycles 64 采样，1088×1920，和灰模同尺寸、同视场 | `build_hero.py -- frames 1,91,180 --res 1088 --spp 64 --w 1088 --h 1920 --out <目录>`，分别是 30 fps 的第 1、91、180 帧（0、3.0、5.97 秒） |

- 关键帧和灰模必须同尺寸：Blender 按宽度定视场，1080 宽和 1088 宽的视场不一样，叠不上。为此 `build_hero.py` 的 `--w/--h` 现在对所有模式生效（原来只在 clay 模式里）。
- 新容器先准备素材：`mkdir -p experiments/blender_poc03/assets_dl && python3 experiments/blender_poc03/make_pcb_texture.py`；`python3 tools/polyhaven.py get studio_small_09 --res 2k`。
- `build_hero.py` 每次运行都会重存 `scene_hero.blend`（frames 模式还会重存 `scene_hero_anim.blend`）。只是出输入素材的话，渲完用 `git checkout` 还原，不提交。

## 在 RunPod 上跑
```bash
python3 experiments/ltx_poc04/runpod_ltx.py run <输入目录> <输出目录> --max-hours 1.5
```
不加 `--yes` 不会租卡（直接退出）；真跑要加 `--yes`。前提：
- RunPod API key 存在云端环境的网络密钥里（代理注入 `rest.runpod.io`），脚本里写占位值；
- 用户在 RunPod 控制台建一个名为 `hf_token` 的 Secret（Hugging Face token；LTX-2.5 是 gated 模型）；
- pod 的传输地址 `<pod>-8000.proxy.runpod.net` 要能连上（环境是 Unrestricted，或放行了 `*.proxy.runpod.net`）。
- 费用：H100 每小时约 2–3 美元；估计 20–35 分钟（装环境 3–6 分钟、下载约 70 GB 权重 3–12 分钟、两版生成各 2–6 分钟），约 0.7–1.6 美元，**超过 1 美元，开跑前报用户批**。

## 结果（2026-11-14，第五次开机跑通）
- **机器**：RunPod A100-SXM4-80GB，每小时 $2.19。墙钟 15.4 分钟，约 **$0.56**（脚本的上限估计，以账单为准）：开机 + 装环境约 1 分钟，下载权重约 4 分钟，V1 生成 294 秒，V2 生成 260 秒，标记检测约 1 分钟。机器已删除。
- 前四次失败（共约 $0.48）：H100 SXM 每小时 $4.39 超出报价，开机即删；LTX-2 仓库没有 `uv.lock`，`--frozen` 装不上；Hugging Face 账号还没获得 LTX-2.5 权限（403）；slim 镜像没有 C 编译器，Triton 编译失败。四处都已修进脚本。**五次合计约 $1.04**。
- **输出**：两版都是 1088×1920、24 fps、145 帧（6.04 秒），带一条 LTX 生成的音轨（没用）。隐形标记：视频检测到（bit accuracy 1.0），音频检测不稳（0.5）。不进仓库，sha256：
  - `v1_first.mp4` a0f00eb612b10ff43df8ef13e2bbe1e33478308acac3dd0c160711c733ded42c
  - `v2_keys.mp4` 71cdbde5e36940f57ee627b607e62804dd669fd13515e54888b887c49878d492
- **对比**：`deliver/对比_灰模_Cycles_V1_V2.mp4`（四联，360 宽）、`deliver/对比_五个时刻.jpg`（上 Cycles、中 V1、下 V2）、`deliver/放大_末帧接口_V1左_V2右.jpg`。
- **主 agent 看到的**（没派审核，PoC 不算成片）：
  - 两版都跟住了灰模：插入的位置、速度、相机推近和 Cycles 版一致，没有看到模块变形或穿模。
  - V1（只给首帧）：板子、笼子的细节最锐利，散景比 Cycles 多；末帧模块端口里多出一对发绿光的长条（模型自己编的，真实 OSFP 的光口里不会亮），要用的话得处理。
  - V2（三张关键帧）：颜色、景深最接近 Cycles；端口内部是暗的，和 Cycles 一致；后半段对焦比 Cycles 软一些。
  - 4.4–4.9 秒每 4 帧有一次较大的跳变：灰模本身就有，是 30 fps 降到 24 fps 的节奏，不是 LTX 引入的。下次灰模直接按 24 fps 渲（`FPS=24`、145 帧）。
  - `tools/motion_check.py` 对 24 fps 片子会误报（它先补成 30 fps，每 4 帧多一帧重复）：两版都报 22% 静止；按原生 24 fps 算，静止帧只有 2.8%。
- **成本对比**：Cycles 6 秒约 $0.48（两台 4090，16 分钟）；LTX 一次跑两版约 $0.56，其中只有约 9 分钟是在生成，单版生成约 $0.17。权重每次重新下载，换成网络存储能省 4 分钟。
