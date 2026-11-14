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
