# 光互连 01（3D 版）· Remotion 合成与动态标注层

全片的合成工程：把 Blender 图像序列铺在底层，上面叠科学示意（波形、时序图、读数）、贴物体的标签、角注、五站进度条、字幕和片尾卡。

- 规格：1080×1920，30 fps，总帧数 = 最后一个镜头的结束时间 × fps（现在 4470 帧）。
- **唯一的时间来源是 `../timeline/timeline.json`**。代码里没有任何镜头时间或镜头文案；`src/timeline.ts` 用相对路径直接导入这份 JSON，改了 JSON 重新渲染（或刷新预览）就生效。
- 颜色只取 `timeline.json` 的 `colors`：金 = 电，青 = 光，珊瑚 = 出错 / 强调，其余是奶油色和深色底的透明度变化。没有粒子、没有大面积辉光、没有镜头抖动。
- Remotion 不重画 Blender 已经做的写实模型。

## 怎么跑

```bash
cd episodes/guanghulian/01-journey-3d/remotion
npm install

npm run studio                    # 预览（无界面的机器上加：-- --no-open）
npm run still -- 1380             # 出单帧：Remotion 帧号（从 0 起，= 秒 × 30）
npm run still -- 46s 49s b1381    # 也可以写秒数，或 Blender 的全片帧号（b 开头，从 1 起）；可一次出多帧
npm run still -- 46s --guides     # 叠上安全区参考线
npm run draft                     # 全片 540×960 低码率预览 → out/journey_draft_540x960.mp4
npm run render                    # 全片 1080×1920 成片 → out/journey_1080x1920.mp4
npm run sheet -- ../previews/x.jpg   # 把 out/stills/ 里的单帧拼成接触表（要 Python + Pillow）
npm run typecheck                 # TypeScript 检查
```

- `draft` / `render` 后面可以接 Remotion 的参数，例如只渲一段：`npm run draft -- --frames=1320-1499`。
- 每个命令开始前会自动运行 `npm run scan`（见下）。
- 浏览器：`remotion.config.ts` 会找机器上预装的 Chromium（环境变量 `REMOTION_CHROME` → `/opt/pw-browsers/chromium` → `/opt/pw-browsers/chromium-*/chrome-linux64/chrome`），用 `chrome-for-testing` 模式启动，不让 Remotion 自己下载浏览器。别的机器上找不到时，用 `REMOTION_CHROME=/path/to/chrome` 指定。
- 单帧输出在 `out/stills/t<秒>_f<Remotion 帧号>.png`。`out/` 和 `node_modules/` 不进仓库。

## 目录结构

```
remotion/
  package.json  remotion.config.ts  tsconfig.json
  scripts/
    scan-frames.mjs      构建前扫描 public/ → src/generated/manifest.json（渲染时不探测文件系统）
    still.mjs            出单帧
    contact_sheet.py     拼接触表
  public/
    frames/<镜头号>/      Blender 图像序列（不进仓库）
    anchors/             anchors_<镜头号>.json（不进仓库）
    audio/               可选：旁白、音乐（不进仓库）
  src/
    index.ts  Root.tsx   注册合成 Journey；规格和总帧数从 timeline.json 算
    Journey.tsx          全片分层
    timeline.ts          导入 timeline.json + 类型 + 秒 → 帧
    theme.ts             颜色（来自 JSON）、字体名常量 FONT_FAMILY、安全区、字号
    strings.ts           图表里的固定用字（坐标轴、图例、占位卡），集中在一处方便审核
    shotConfig.ts        按镜头的版式：波形画哪一种、标签默认位置、面板高度、模场半径等
    lib/                 signal.ts（伪随机比特、低通）  text.ts（量字宽、折行）  manifest.ts（帧清单、锚点）
    layers/              BlenderPlate  PlaceholderCard  ShotOverlays  StationBar  Subtitles  AudioTracks  Guides
    overlays/            Waveform  TimingDiagram  Gauge  AnchoredLabel  NoteStack  HookTitle  PathTrace  EndCard  Panel
    generated/           manifest.json（scan 生成，不进仓库）
```

## 分层（从下到上）

| 层 | 组件 | 说明 |
|---|---|---|
| a 底层 | `layers/BlenderPlate` | Blender 图像序列。某一帧没有 → 用该镜头已有的最近一帧；整个镜头一帧都没有 → `PlaceholderCard`（深色底 + 斜纹 + 镜头号、镜头名、尺度、相机、状态，标「占位 · 非成片画面」）。`blender` 为 null 的镜头（片尾卡）只铺深色底 |
| b 科学叠加 | `layers/ShotOverlays` → `overlays/*` | 按 `overlays[].type` 分给各组件，见下表 |
| c 五站条 | `layers/StationBar` | y = `safe_zone.station_bar_y`。当前镜头的 `station` 高亮；为 null 时都不高亮。圆点颜色：电的站金色，光的站青色，换乘和抵达半金半青（`shotConfig.STATION_SIGNAL`） |
| d 字幕 | `layers/Subtitles` | `narration` 逐句，中心在 y = `safe_zone.subtitle_y`；深色半透明条 + 奶油色字；一行放不下折两行（只在词之间断，优先在标点后）；出入各 3 帧 |
| e 片尾卡 | `overlays/EndCard` | 全屏，盖住以上各层 |
| 声音（可选） | `layers/AudioTracks` | `public/audio` 里有文件才有，见「声音」 |

### overlay 类型 → 组件

| type | 组件 | 做什么 |
|---|---|---|
| `waveform` | `Waveform` | 三种画法，按镜头在 `shotConfig.WAVEFORM_VARIANT` 里指定（S04 `degrade`、S05 `restore`、S06 `eo`；没写的按 `degrade`）。**degrade**：同一段 PRBS7 比特，「出发时」方正、「到达时」经两级一阶低通变圆钝，模糊程度从标注开始渐增、到同镜头的 `alert` 出现时到头；右侧是眼图（最近 22 个比特叠加）由开到合；`alert` 出现时判决门限、门限附近的判决点、眼图中线变珊瑚色，`alert` 的文字画在眼图下面。**restore**：左糊右清两条，中间一个箭头。**eo**：上金（电信号）下青（光强）对齐，比特边沿有贯通上下的细虚线。小标题从标注的 `text` 拆（` / `、`→`、`：`） |
| `timing_diagram` | `TimingDiagram` | 文案里「并行」在前画并行 → 串行，「串行」在前画串行 → 并行。并行线 8 条（`TIMING_LANES`），演示 4 拍（`TIMING_WORDS`）。亮 = 1、暗 = 0；一条「现在」竖线匀速从左扫到右；串行线每送出 / 收到一位，就和对应的那条并行线之间连一条竖线。横轴标「时间」 |
| `gauge` | `Gauge` | η = exp(−d²/w²)，w = 4.6 µm（`MODE_FIELD_RADIUS_UM`，FACTS F11）。d 依次停在 0 → 文案里「偏 N µm」的各个值 → 0，每档平分标注时长（前 40% 移动，其余停住）。左：两个圆形光斑错开，没对上的部分珊瑚色；右：百分比、进度条、偏移量。标题取 `text` 里「：」之前的部分 |
| `label` `term` `scale` `alert` | `AnchoredLabel` | 细引线 + 小字。能拆成「主名 + 说明」的排两行（` · `、`：`、末尾的「（…）」）。有锚点数据跟着锚点走，没有用默认位置（`shotConfig.DEFAULT_SLOTS` / `SHOT_SLOTS`，按该镜头里标签的先后轮流取）。始终留在安全区内，并让开同时在场的图表面板。`alert` 是珊瑚色；落在 `degrade` 波形时间内的 `alert` 交给波形画。`scale` 在分镜里是 Blender 内的 3D 立体字：该镜头已有 Blender 帧时 Remotion 不再画（`SCALE_ONLY_WHEN_PLACEHOLDER`） |
| `note` | `NoteStack` | 角注，27 px，贴内容区下沿（末行约 y = 1290–1316），很淡的深色衬底；同一时刻多条时竖排 |
| `hook_title` | `HookTitle` | 开头大字问题，两行，画面下半部，带透视倾斜。第 0 帧就完整可见（没有淡入），全程缓慢放大，最后 8 帧淡出 |
| `path_trace` | `PathTrace` | 只加文字。「A → B：金（电）→ 青（光）→ …」画成路线名 + 色条图例；「出发 · 电的路 · …」画成几个站名，有锚点贴锚点（锚点名 = 站名或站 id），没有时沿一条浅弧线排开 |
| `end_card` | `EndCard` | 第一行结论（「电」「光」两字上金 / 青）、五站小路线图（光的路段青色）、第二行预告 |

## 怎么放 Blender 帧

```
public/frames/<镜头号>/<镜头号>_<全片帧号 6 位>.png
例：public/frames/S04/S04_001381.png        （.jpg / .jpeg / .webp 也认）
```

- 全片帧号 = round(秒 × 30) + 1，和 `blender/common.py` 的 `F()`、`render()` 的输出命名一致。Remotion 帧号（从 0 起）+ 1 = 全片帧号。
- 分辨率不限（低清预演帧会被放大铺满）；帧不全没关系（缺的帧用最近一帧）。
- 放完运行任意一个 npm 命令（或 `npm run scan`），终端会列出每个镜头找到了几帧。**Studio 开着的时候新增了帧，要再跑一次 `npm run scan`。**

### 锚点

```
public/anchors/anchors_<镜头号>.json      或者和帧放一起：public/frames/<镜头号>/anchors_<镜头号>.json
```

- 格式就是 `blender/common.py` 的 `export_anchors()` 输出：`{width, height, step, frames: {"<全片帧号>": {"<锚点名>": [x, y, z, 是否可见]}}}`，左上原点。`step` > 1 时两帧之间线性插值；`width` / `height` 不是 1080×1920 时按比例换算。
- **锚点名怎么对上标注**：依次试 ① 标注的 `anchor_key` 字段（时间轴里现在没有，导演可以加）；② 标注的 `anchor` 字段原文（例如 `"走线旁"`、`"DSP 芯片旁"`）；③ 标注的 `text` 原文。也就是说，Blender 那边 `export_anchors(path, shot, cam, {"走线旁": obj, …})` 的键直接用 `timeline.json` 里这条标注的 `anchor` 字符串即可。
- `path_trace` 的站名：锚点名用站名（`"出发"`…）或站 id（`"st1"`…）。
- 锚点不可见（出画或在相机背后）时，标签只留文字，不画引线。
- 图表面板（波形、时序图、读数）现在不跟锚点，固定在内容区下部。

### 声音（可选）

```
public/audio/narration.wav        整条旁白，从 0 秒起
public/audio/n01.wav …            逐句旁白，文件名 = narration[].id，各自从 narration[].start 起（有整条时不用逐句）
public/audio/music.wav            音乐，从 0 秒起，音量 0.25（约 −12 dB）
```

认 wav / mp3 / m4a / aac / ogg。本工程不生成配音。响度（−14 LUFS）不在这里做，成片后另行处理。

## 版式约定

- 安全区：内容（标签、图表）在 y = 310–1320、x = 60–1020 之内；五站条 y = 200；字幕中心 y = 1400。数值来自 `timeline.json` 的 `meta.safe_zone`。
- 内容区最下面 88 px 留给角注，图表面板的下沿在 y = 1232。
- 字体：`theme.ts` 的 `FONT_FAMILY`，现在排第一的是系统里的「WenQuanYi Zen Hei」（只有一个字重，粗体是浏览器合成的）。换成系列字体只改这一个常量（如果用字体文件，再用 `@remotion/fonts` 加载）。
- 图表里不在时间轴上的固定用字（「时间」「判决门限」「偏移」等）都在 `src/strings.ts`，改字只改那里。

## 已知限制

1. 现在 `public/frames` 是空的，所有镜头都是占位卡。标签、图表的位置是按「不挡占位说明、互不重叠」摆的默认位置；有了真实画面和锚点之后要再看一遍构图。
2. 图表面板不跟 3D 锚点。分镜里 S05 写的是波形「锚在 3D 位置上」，现在是固定在下部的两块，中间一个箭头。
3. 时序图并行线画 8 条，分镜写的是 32 条（手机上 32 条看不清）。要改就改 `TIMING_LANES`。串行 → 并行那张图里，最后一组比特收齐后的并行输出落在图外，没有画出来。
4. 读数显示的是公式算出来的整数（偏 2 µm → 83%，偏 5 µm → 31%），时间轴文案写的是「约 80%」「约 30%」。
5. 眼图的小标题「逐位叠起来看（眼图）」、读数的两条图例、「判决门限」是本工程自己加的字，不在时间轴里，需要导演和科学审查确认。
6. 波形是示意：两级一阶低通（最糊时各 0.57 个比特宽，最坏情况眼高约剩 13%），不是按真实走线的损耗曲线算的；电 / 光波形是两级（NRZ），和角注「实际常用四级」一致。
7. 镜头之间是硬切。分镜里 4 处「1 帧暗场」现在没有做：时间轴里还没有结构化的转场字段（`transition_out` 是一句话）。Blender 渲进画面，或者时间轴加字段后在这里实现，二者选一。
8. 同一时刻多条角注竖排的逻辑写了，但现在的时间轴里没有同时出现的角注，没有实际出过图。
9. 没有按 Remotion 的 Studio 可视化编辑（`Interactive.*`、内联关键帧）来写：这里的版式都由数据驱动，Studio 里只用来预览。

## 授权

Remotion 不是 MIT 协议。个人，以及 3 人及以下的团队 / 公司可以免费使用（含商用）；4 人及以上的公司需要购买公司授权。条款以 <https://github.com/remotion-dev/remotion/blob/main/LICENSE.md> 为准。其余依赖（React 等）是 MIT。本工程没有引入任何第三方素材。
