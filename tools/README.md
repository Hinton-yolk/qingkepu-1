# 工具

## motion_check.py：动效量化检查
交成片前必须跑一次（`CLAUDE.md`「交出成片前的自检循环」第 4 步）。

```bash
python3 tools/motion_check.py <film.mp4> <name> --end=<片尾卡开始的秒数>
```

- 通过标准（片尾卡之前的正片）：静止帧 < 15%，任意 5 秒窗口静止 < 30%，最长静止 ≤ 0.6 秒。FAIL 时「动效质量」最多 6 分。
- 原理：把视频转成 30 fps、135×240 的灰度图，逐帧求平均差，差值 < 0.15 算静止。60 fps 的片子也会先降到 30 fps，阈值不变。
- 低于 30 fps 的片子（例如 24）按原帧率分析，阈值按帧间隔放大（24 fps 时 0.1875）。原因：24 → 30 会每 5 帧重复 1 帧，凭空多出 20% 的「静止帧」（2026-11-11 光互连 02 下集 y6 试镜头遇到）。
- 依赖：`ffmpeg`、`numpy`。`librosa` 可选，只用来输出「音乐 BPM、画面变化卡在节拍上的比例」那一行；没装就显示 nan，不影响 PASS / FAIL。需要时 `pip install librosa`。

### 来历
原版由「如果」系列的会话在 2026-11-04 写成（`/home/user/studio-tools/motion_check.py`），从那次会话的记录里逐条还原。2026-11-06 存进仓库时做了三处修改：
1. 分析前先把视频统一转成 30 fps。原版把帧率写死成 30，60 fps 的片子（例如光互连）时间轴会算错。
2. librosa 改为可选依赖。
3. 完全静止、没有任何画面变化的片子不再崩溃，会正常给出 FAIL。

## gemini_watch.py：让 Gemini 看视频（流式）
看参考视频、竞品视频，或者让 Gemini 复查自己的成片时用。

```bash
python3 tools/gemini_watch.py "<YouTube 链接或本地视频文件>" -q "问题" [--start 6:20 --end 7:30] [--out 答案.md]
```

- **为什么要流式**：云端会话的网络代理在约 30 秒没有回应时会掐断请求。Gemini 看完整视频常常超过 30 秒，
  所以 watch skill 自带的 Gemini 模式会报 `HTTP 502: upstream request failed`。流式接口通常在 30 秒内就开始返回。
- **自动换模型**：某个模型拥堵（503）、太慢（30 秒 502）或这个 Key 用不了（404）时，按顺序换下一个。
  默认顺序 `gemini-3.5-flash, gemini-3.6-flash, gemini-3.7-flash, gemini-flash-latest`（2026-11-09 实测 3.5 最稳），
  可以用 `--models` 或环境变量 `WATCH_GEMINI_MODELS` 改。
- **视频去哪了**：YouTube 链接直接交给 Google，这里不下载；本地文件上传到 Gemini Files API，用完立刻删除
  （删不掉的 48 小时内自动过期）。不要用它处理不想离开本机的视频，那种情况用 watch skill 的本地模式。
- **Key**：读 `GEMINI_API_KEY` 环境变量，再读 `~/.config/watch/.env`。云端环境里真 Key 存在环境的 Network secrets 中，
  由代理注入 `x-goog-api-key` 请求头；本地找不到 Key 时脚本自动用占位值，新会话不用任何配置。
- **只用标准库**，不用装依赖。
- Gemini 的回答是它对视频的描述，**不是核实过的事实**；要引用进脚本或 FACTS.md 的数字，先对照原视频。

## heartbeat_watch.sh：心跳监视
派出去的角色或后台任务可能中途停下而不发通知。把它放在后台跑，盯着若干文件或目录；超过设定的时间没有变化就退出并说明是谁停了，主 agent 会被叫醒。

```bash
tools/heartbeat_watch.sh <名字> <停滞秒数> <路径> [路径…] [-- <进程关键字>]
```

- 给了进程关键字时，那个进程正常结束它就安静退出（退出码 0）；停滞时退出码 3。
- 它只在本次会话里跑，不是定时任务。

## preview_manifest.py：视频审核交付的规格表
把预览视频交给外部审阅时，PR 里「视频审核交付」一节要写文件大小、sha256、时长、宽高、帧率、音轨和对应提交。这个脚本读本地文件生成那张表，不上传任何东西。

```bash
python3 tools/preview_manifest.py <视频文件> --commit <生成视频时的代码提交> [--url 直链] [--row 键=值 …] [--note 说明]
```

## frame_stats.py：画面亮度和色度
「3D 镜头语法」里「微观世界的样子」「工序台的样子」两条的色度阈值用它测。

```bash
python3 tools/frame_stats.py <图片或视频> [秒 ...] [--crop 宽:高:x:y]
```

- 色度 C = max(R,G,B) − min(R,G,B)，取全帧平均。
- 不用 HSV 饱和度：它在暗像素上会被放大，近黑的深蓝也会显得「很饱和」。
- 测录屏时用 `--crop` 裁掉浏览器界面。
- 同时输出平均亮度：「微观世界的样子」还有一个亮度门槛（平均亮度 ≥ 0.25，建议值，待用户定）。

## runpod_render.py：租云显卡渲 Blender（2026-11-10）
- 从云端会话直接驱动 RunPod，全程 HTTPS：REST API 建 pod → pod 上起一个带口令的小 HTTP 服务（经 `https://<pod>-8000.proxy.runpod.net`）→ 上传场景包（约 7 MB）→ 装 Blender 5.2.3 Linux 版 → 按任务表渲染 → 渲好一张拉回一张 → 删 pod。
- 不用网络卷和 S3：S3 要用密钥本地签名，代理注入不了；不用网络卷还能租便宜的 Community Cloud。
- 防扣钱：脚本退出（包括出错）时删掉自己建的 pod；每个 pod 到 `--max-hours` 自删（未在真机验证）；`kill-all` 兜底。
- 先 `plan` 看分配和估价，`run ... --yes` 才真的租。02 下集的任务表：`episodes/guanghulian/02-serdes/下集_新风格/blender/runpod_jobs.json`（和 Windows 渲染包同一套参数）。
- API key 不进仓库：云端会话由代理注入 `rest.runpod.io` 的 Authorization 头；自己电脑上用环境变量 `RUNPOD_API_KEY`。
- 冒烟测试（11-10）：Secure Cloud 上的 RTX 3090（当时 Community Cloud、Secure Cloud 都没有空闲的 4090），每小时 0.5 美元。从建机器到删机器共 1.4 分钟：装环境和 Blender 约 1 分钟，B 段第 60 帧（1080×1920，Cycles 64 采样，含合成节点的辉光和雾）渲了 12.6 秒，花费约 1–2 美分。OptiX、EGL、合成节点在云上都正常。

## flicker_check.py：降噪闪烁检查（2026-11-10）
Cycles 低采样 + 降噪的序列，在雾、散景、暗部容易出现成团蠕动的低频闪烁。收到渲染后先跑它，再亲眼看放大图。

```bash
python3 tools/flicker_check.py <视频或 PNG 目录> <输出目录> [--step 1] [--amp 12]
```

- 做法：相邻三帧用光流对齐到中间帧（相机在动也能比），只看低频（先模糊掉 2 px 以下的细节），量中间帧和前后帧平均值的差；光流对不上的地方（遮挡、运动模糊的亮信号）挡掉不算。
- 输出：`flicker.json`（整帧中位数、95 分位、暗部、3×6 分区、逐帧）、`heat_mean.jpg`（哪里最闪）、最闪 3 帧的「原帧 | 差 × 放大倍数」对比图。
- 合成样本试过：干净序列 0.23，加了成团逐帧噪声的 1.58（单位：亮度的 1/255）。
- 判读门槛（< 0.6 基本看不出，> 1.2 手机上也看得到）是〔建议〕值，没用真实渲染校准过，以亲眼看放大图为准。
- mp4 压缩会抹掉一部分闪烁，有 PNG 序列时优先测 PNG。依赖：`numpy`、`opencv-python-headless`、`ffmpeg`。

## polyhaven.py / polyhaven_blender.py：Poly Haven 素材（HDRI、贴图、模型）
用户 2026-11-14：「为了更高效的让你借助 blender 建模，请你接入 poly haven 的 API」。

```bash
python3 tools/polyhaven.py search textures metal          # 按关键词搜（hdris / textures / models）
python3 tools/polyhaven.py info metal_plate                # 详情和可下载的贴图
python3 tools/polyhaven.py get studio_small_09 --res 2k    # 下载（HDRI / 贴图 / 模型都用 get）
```
Blender 脚本里：
```python
import sys; sys.path.insert(0, '<仓库>/tools'); import polyhaven_blender as ph
ph.set_world_hdri('studio_small_09', res='2k', strength=0.1, camera_sees=(0.004, 0.005, 0.007))
mat = ph.pbr_material('metal_plate', res='2k')     # 按素材标注的真实尺寸平铺
objs = ph.import_model('<模型id>', res='1k')
```
- API 不需要 key。条款要求请求带能标识软件名的 User-Agent，脚本固定用 `kepu-studio-asset-fetch/1.0`，不带个人信息；两次请求至少间隔 0.25 秒，资产列表缓存 24 小时。
- 素材是 CC0，用在视频里不需要署名。条款只对「在产品里实时展示 API 内容」要求注明来源，我们不涉及。
- 下载到 `assets/polyhaven/<类型>/<id>/<分辨率>/`（不进仓库），核对 md5，旁边写 `manifest.json`（许可、作者、来源链接）。新容器要重新下载。
- 局限：Poly Haven 几乎没有电子硬件模型（光模块、电路板要自己建），主要用它的 HDRI、金属和地面贴图。
