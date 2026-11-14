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
npm run still -- 46s --tag=试A    # 文件名后面加 _试A（同一帧出几个版本对比用）
npm run draft                     # 全片 540×960 低码率预览 → out/journey_draft_540x960.mp4
npm run render                    # 全片 1080×1920 成片 → out/journey_1080x1920.mp4
npm run sheet -- ../previews/x.jpg   # 把 out/stills/ 里的单帧拼成接触表（要 Python + Pillow）
npm run sheet -- ../previews/x.jpg --cols 5 --cell 360x640 --title "说明"   # 每格大小、表头
npm run lint                      # ESLint + TypeScript 检查
npm run typecheck                 # 只做 TypeScript 检查
```

- `draft` / `render` 后面可以接 Remotion 的参数，例如只渲一段：`npm run draft -- --frames=1320-1499`。
- 每个命令开始前会自动运行 `npm run scan`（见下）。它除了列出每个镜头找到几帧，还会列出**每条标注对上了哪个锚点**（没对上的、锚点全程不在画面内的都会写明），放进新锚点后先看这份对照。
- 浏览器：`remotion.config.ts` 会找机器上预装的 Chromium（环境变量 `REMOTION_CHROME` → `/opt/pw-browsers/chromium` → `/opt/pw-browsers/chromium-*/chrome-linux64/chrome`），用 `chrome-for-testing` 模式启动，不让 Remotion 自己下载浏览器。别的机器上找不到时，用 `REMOTION_CHROME=/path/to/chrome` 指定。
- 单帧输出在 `out/stills/t<秒>_f<Remotion 帧号>[_标签].png`。`out/` 和 `node_modules/` 不进仓库。

## 目录结构

```
remotion/
  package.json  remotion.config.ts  tsconfig.json
  scripts/
    scan-frames.mjs      构建前扫描 public/ → src/generated/manifest.json（渲染时不探测文件系统）
    still.mjs            出单帧
    contact_sheet.py     拼接触表（--cols、--cell 宽x高、--title）
  public/
    frames/<镜头号>/      Blender 图像序列（不进仓库）
    anchors/             anchors_<镜头号>.json（不进仓库）
    audio/               可选：旁白、音乐（不进仓库）
  src/
    index.ts  Root.tsx   注册合成 Journey；规格和总帧数从 timeline.json 算
    Journey.tsx          全片分层
    timeline.ts          导入 timeline.json + 类型 + 秒 → 帧
    theme.ts             颜色（来自 JSON）、字体名常量 FONT_FAMILY、安全区、字号
    strings.ts           图里的固定用字（坐标轴、图例、图内小注、占位卡），集中在一处方便审核；清单见下面「图内固定用字」
    shotConfig.ts        版式配置：波形画哪一种、标签默认位置和间距、面板高度、开头大字的位置、路线的画法、模场半径等
    lib/                 signal.ts（伪随机比特、低通）  text.ts（量字宽、折行）  manifest.ts（帧清单、锚点、锚点名匹配）
                         geom.ts（矩形、线段裁剪）  pathTrace.ts（路线折线）  shotLayout.ts（谁让谁：角注 / 面板 / 标签的位置）
    layers/              BlenderPlate  PlaceholderCard  ShotOverlays  StationBar  Subtitles  AudioTracks  Guides
    overlays/            Waveform  TimingDiagram  Gauge  AnchoredLabel  NoteStack  HookTitle  PathTrace  EndCard  Panel
    generated/           manifest.json（scan 生成，不进仓库）
```

## 分层（从下到上）

| 层 | 组件 | 说明 |
|---|---|---|
| a 底层 | `layers/BlenderPlate` | Blender 图像序列。某一帧没有 → 用该镜头已有的最近一帧；整个镜头一帧都没有 → `PlaceholderCard`（深色底 + 斜纹 + 镜头号、镜头名、尺度、相机、状态，标「占位 · 非成片画面」）。`blender` 为 null 的镜头（片尾卡）只铺深色底 |
| b 科学叠加 | `layers/ShotOverlays` → `overlays/*` | 按 `overlays[].type` 分给各组件，见下表 |
| c 五站条 | `layers/StationBar` | 一条半透明深色衬底条（y = 154–250，中心约在 `safe_zone.station_bar_y`），站名 36 px。当前镜头的 `station`：站名垫信号色实心底、字变深色加粗、圆点放大；走过的站是实的奶油色，没到的站字淡、圆点空心；`station` 为 null 时没有当前站。信号色：电的站金色，光的站青色，换乘和抵达金到青（`shotConfig.STATION_SIGNAL`） |
| d 字幕 | `layers/Subtitles` | `narration` 逐句。**所有字幕同一条衬底条**：宽度固定 = 内容区宽（x = 60–1020），中心在 y = `safe_zone.subtitle_y`，字在条内居中，衬底不透明度 0.72；一行放不下折两行（只在词之间断，优先在标点后），两行时条以同一条中线上下各长一点；出入各 3 帧 |
| e 片尾卡 | `overlays/EndCard` | 全屏，盖住以上各层 |
| 声音（可选） | `layers/AudioTracks` | `public/audio` 里有文件才有，见「声音」 |

### overlay 类型 → 组件

| type | 组件 | 做什么 |
|---|---|---|
| `waveform` | `Waveform` | 三种画法，按镜头在 `shotConfig.WAVEFORM_VARIANT` 里指定（S04 `degrade`、S05 `restore`、S06 `eo`；没写的按 `degrade`）。**degrade**：同一段 PRBS7 比特，「出发时」方正、「到达时」经两级一阶低通变圆钝，模糊程度从标注开始渐增、到同镜头的 `alert` 出现时到头；右侧是眼图（最近 22 个比特叠加）由开到合；`alert` 出现时判决门限、门限附近的判决点、眼图中线变珊瑚色，`alert` 的文字画在眼图下面。**restore**：左糊右清两条，中间一个箭头。**eo**：上金（电信号）下青（光强）对齐，比特边沿有贯通上下的细虚线。小标题从标注的 `text` 拆（` / `、`→`、`：`） |
| `timing_diagram` | `TimingDiagram` | 文案里「并行」在前画并行 → 串行，「串行」在前画串行 → 并行。并行线 8 条（`TIMING_LANES`），演示 4 拍（`TIMING_WORDS`）；并行那一行的标题后面有小字「（图里只画 8 条）」（数字跟着 `TIMING_LANES`），免得和 3D 画面里的条数对不上。亮 = 1、暗 = 0；一条「现在」竖线匀速从左扫到右；串行线每送出 / 收到一位，就和对应的那条并行线之间连一条竖线。横轴标「时间」 |
| `gauge` | `Gauge` | η = exp(−d²/w²)，w = 4.6 µm（`MODE_FIELD_RADIUS_UM`，FACTS F11）。d 依次停在 0 → 文案里「偏 N µm」的各个值 → 0，每档平分标注时长（前 40% 移动，其余停住）。左：两个圆形光斑错开，没对上的部分珊瑚色；右：百分比、进度条、偏移量。标题取 `text` 里「：」之前的部分 |
| `label` `term` `scale` `alert` | `AnchoredLabel`（位置在 `lib/shotLayout`） | 深色半透明衬底（0.8）+ 细描边 + 字，一条引线从锚点连到衬底边上。主行 38 px（`term` 42），太长时缩到不小于 34；副行 30 px，不小于 28；再放不下折两行。能拆成「主名 + 说明」的排两行（` · `、`：`、末尾的「（…）」）。**对上了锚点就停在锚点旁边、不挡住它**；没对上用默认位置（`shotConfig.DEFAULT_SLOTS`），不画引线。让开开头大字、路线上的字、图表面板、角注，互相不压；同一时刻最多 3 个（`MAX_LABELS`，多出来的、开始得晚的不画）。详见下面「锚点」。`alert` 是珊瑚色；落在 `degrade` 波形时间内的 `alert` 交给波形画。`scale` 在分镜里是 Blender 内的 3D 立体字：该镜头已有 Blender 帧时 Remotion 不再画（`SCALE_ONLY_WHEN_PLACEHOLDER`） |
| `note` | `NoteStack` | 角注，28 px，深色衬底（0.72），贴内容区下沿（最下面一条的下沿 y = 1316）；同一时刻多条时竖排，先出现的在上。角注只往上长，不会压到字幕；它叠得高时，同时在场的图表面板整块往上让（`lib/shotLayout.panelBottomFor`） |
| `hook_title` | `HookTitle` | 开头大字问题，两行，固定在 `shotConfig.HOOK_BOX`（x = 140–940，y = 984–1224：走廊地面上、角注上面），带透视倾斜。字后面有一块半透明暗垫，字本身加深色描边和投影（地面很亮）。第 0 帧就完整可见（没有淡入），全程缓慢放大，最后 8 帧淡出。它在场时，标签和路线上的字都让开这一块 |
| `path_trace` | `PathTrace`（几何在 `lib/pathTrace`） | **「电 → 光 → 电」（有箭头）= 路线图**：沿 anchors JSON 里的 `path_*` 取样点画一条 2D 虚线，电的段金色、光的段青色，线宽 6 px，带深色描边；标注开始后 2.7 秒内从 A 端画到 B 端（画的那一头有个小圆点），之后保持，最后 8 帧淡出；每段中点旁放一个带衬底的字（44 px）。3D 里的发光管有的段被机柜挡住，这条线把整条路线补全，所以画成虚线（是示意）。没有 `path_*` 锚点时退回成内容区上沿的一行图例。取样点的命名见下面「锚点」。**「出发 · 电的路 · …」（没有箭头）= 几个站名**，有锚点贴锚点（锚点名 = 站名或站 id），没有时沿一条浅弧线排开 |
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
- **锚点名怎么对上标注**（`lib/manifest.resolveAnchorName`，`npm run scan` 会把结果列出来）：
  1. 标注写了 `anchor_key`（时间轴里可选的字段，专门指定锚点名）→ 只认它；
  2. 否则先试标注的 `anchor` 字段原文（例如 `"gpu_a"`、`"大芯片"`、`"串化电路旁"`），再试 `text` 原文；
  3. 每个候选先按原文精确比；都没有，再按「不分大小写、去掉空格」比一遍。
  也就是说，Blender 那边 `export_anchors(path, shot, cam, {"gpu_a": obj, …})` 的键直接用 `timeline.json` 里这条标注的 `anchor` 字符串即可。
- **对上了**：标签跟着锚点走，停在它旁边（右上 / 左上 / 右下 / 左下 / 正上 / 正下 / 正右 / 正左八种摆法里，挑一种在这条标签全程里被安全区挤得最少、压到别的东西最少的；一条标签全程只用一种，不会中途左右翻），引线从锚点连到衬底边上。
- **没对上**：退回默认位置（`shotConfig.DEFAULT_SLOTS`，按镜头里标签的先后轮流取），只有衬底和字，不画引线。
- **锚点不在画面内时**（`shotConfig.LABEL_NEAR_MARGIN` / `LABEL_LOST_FADE`）：
  - 刚出画（离画面边不到 120 px）：标签留着，停在离锚点最近的画面内位置，不画引线；
  - 出得更远，或转到相机背后（z ≤ 0）：标签停在最后的位置，8 帧淡出，不跟着乱飞；锚点回来再淡入；
  - 标注在场期间锚点一帧都不在画面附近：这条标签不画（scan 的对照里会写明）；
  - 锚点在画面内，但落在五站条 / 字幕那两条带里，或被开头大字、图表面板盖住：标签照常，不画引线。
- **路线取样点**（`path_trace` 的「电 → 光 → 电」用，配置在 `shotConfig.PATH_TRACE`）：
  - 锚点名 `path_<段>_<序号>`：`path_e1_00 … path_e1_NN`（A 端电）、`path_o_00 …`（光）、`path_e2_00 …`（B 端电）；序号沿 A → B 递增，位数不限。段名以 `e` 开头画金色，以 `o` 开头画青色；先后顺序是 e1 → o → e2。
  - 文案里的字按顺序配给各段（第 1 个字 → e1，第 2 个 → o，第 3 个 → e2）。
  - z ≤ 0（在相机背后）的点跳过；折线在那里断开，不把它两边的点直接连起来。贴近相机、投影到画面外很远的点会被裁到画面附近。
  - 相邻两段的首尾没有重合时，用前一段的颜色把缝补上；最好让上一段的最后一个点和下一段的第一个点在同一个位置。
  - 取样密度：折线是直线段连起来的，拐弯处多给几个点；整条 30–60 个点足够。
  - 只有不分段的 `path_00 … path_NN` 时没法上色，按「没有取样点」处理，退回图例。
- `path_trace` 的站名（「出发 · 电的路 · …」）：锚点名用站名（`"出发"`…）或站 id（`"st1"`…）。
- 图表面板（波形、时序图、读数）现在不跟锚点，固定在内容区下部。

### 声音（可选）

```
public/audio/narration.wav        整条旁白，从 0 秒起
public/audio/n01.wav …            逐句旁白，文件名 = narration[].id，各自从 narration[].start 起（有整条时不用逐句）
public/audio/music.wav            音乐，从 0 秒起，音量 0.25（约 −12 dB）
```

认 wav / mp3 / m4a / aac / ogg。本工程不生成配音。响度（−14 LUFS）不在这里做，成片后另行处理。

## 版式约定

- 安全区：内容（标签、图表）在 y = 310–1320、x = 60–1020 之内；五站条的衬底条 y = 154–250；字幕条中心 y = 1400（一行 1356–1444，两行 1325–1475）。数值来自 `timeline.json` 的 `meta.safe_zone`。
- 字号（1080 宽；预演是 540 宽，所以压在画面上的字都按「缩一半还读得出」定，`theme.ts` 的 `SIZE`）：五站条 36；标签主行 38（不小于 34）、副行 30（不小于 28）；路线上的字 44；角注 28；字幕 48；开头大字 112 / 68（按 `HOOK_BOX` 的宽度缩）。
- 衬底（`theme.ts` 的 `BACKING`，都是深色底 `colors.ink` 的不透明度）：标签和路线上的字 0.8，角注 0.72，字幕条 0.72，五站条 0.7，开头大字的暗垫 0.56，图表面板 0.82。
- 谁让谁（`lib/shotLayout`）：
  - 角注贴内容区下沿往上叠；默认占最下面 88 px，图表面板的下沿在 y = 1232。面板在场期间角注叠得更高时，面板整块往上让（一块面板全程一个位置）。
  - 标签不低于同时在场的面板上沿和角注上沿；让开开头大字和路线上的字；标签之间不相叠。
  - 路线上的字让开开头大字。
  - 叠放顺序（从下到上）：路线 → 开头大字 → 图表面板 → 标签 → 角注 → 五站条 → 字幕。
- 字体：`theme.ts` 的 `FONT_FAMILY`，现在排第一的是系统里的「WenQuanYi Zen Hei」（只有一个字重，粗体是浏览器合成的）。换成系列字体只改这一个常量（如果用字体文件，再用 `@remotion/fonts` 加载）。
- 图里不在时间轴上的固定用字都在 `src/strings.ts`，改字只改那里（并同步下面这张表）。

## 图内固定用字（供科学审查逐条核对）

这些字不在 `timeline.json` 里，是本工程加在图上的，全部集中在 `src/strings.ts`。除此之外，画面上的字（标签、角注、字幕、图表小标题、路线上的「电 / 光」、五站名、片尾卡）都直接取自 `timeline.json`。

| 键 | 用字 | 出现在哪 | 含义 |
|---|---|---|---|
| `threshold` | 判决门限 | 波形图（S04「出发时 / 到达时」、S05「进 / 出」）左下角，是图里那条水平虚线的图例（S04 里 `alert` 出现后和虚线一起变珊瑚色） | 接收端判断 0 还是 1 的电压分界线：波形高于它判 1，低于它判 0 |
| `eye` | 逐位叠起来看（眼图） | 波形图（S04）右侧小图的标题 | 把「到达时」的波形按一个比特的时长切开、叠在一起画；中间的空白（眼）越小越难分清 0 和 1 |
| `timeAxis` | 时间 | 时序图（S03、S09）底部横轴的右端 | 说明横轴是时间，不是空间位置 |
| `timingLanes` | （图里只画 8 条） | 时序图（S03、S09）并行那一行标题后面的小字；数字 = `shotConfig.TIMING_LANES` | 图里并行线的条数是为了看得清而减少的，和 3D 画面里画的条数（时间轴标注写「示意画 32 条」）不是一回事 |
| `offset` | 偏移 | 对接读数（S07）右下：「偏移 2.0 µm」 | 波导出来的光斑中心和光纤芯中心错开的横向距离 |
| `unitMicron` | µm | 对接读数（S07），跟在偏移量后面 | 微米 |
| `approx` | 约 | 对接读数（S07）百分比前面；偏移不为 0 时才出现 | 百分比是按高斯模场估算的近似值（η = exp(−d²/w²)，w = 4.6 µm，FACTS F11） |
| `percent` | % | 对接读数（S07）的大数字后面 | 进光纤的光占「对准时」的百分之几（相对值，不是绝对耦合效率） |
| `spotFiber` | 光纤能接住的范围 | 对接读数（S07）左侧截面示意的图例：虚线圆 | 光纤的模场范围（示意） |
| `spotChip` | 芯片来的光斑 | 对接读数（S07）左侧截面示意的图例：青色实心圆 | 从芯片波导出来、经模斑转换器放大后的光斑（示意） |
| `arrow` | → | 路线图例（S01；只有在没有 `path_*` 取样锚点、退回图例时才出现），两段之间 | 信号走的先后顺序 |
| `placeholderTag` | 占位 · 非成片画面 | 占位卡（还没有 Blender 帧的镜头）左上角 | 这一屏不是成片画面 |
| `placeholderHint` | 此处为 Blender 画面，尚未渲染 | 占位卡说明行 | 同上 |
| `placeholderStatus` `placeholderScale` `placeholderCamera` | 状态 / 尺度 / 相机 | 占位卡说明行的字段名，后面跟 `timeline.json` 里该镜头的 `status` / `scale` / `camera` | 只在占位卡上出现，成片里没有 |

图里另有两处不是文字、但带含义的画法，一并请审查：路线图的**虚线**表示「示意的路线，不是实物」；五站条、路线、图例里**金 = 电、青 = 光**（和角注「金 = 电、青 = 光，颜色为示意」一致）。

## 已知限制

1. `public/frames` 里现在只有上一版 S01–S03 的低清帧（10 fps）和旧锚点，S04 以后都是占位卡。标签和路线这一轮是对着旧帧、旧锚点调的；新版帧和锚点放进来后，先看 `npm run scan` 的对照，再出一遍接触表看构图。旧锚点里没有 `nic_a`、`差分输出`（旧名是 `output`），这两条现在落在默认位置。
2. 图表面板不跟 3D 锚点。分镜里 S05 写的是波形「锚在 3D 位置上」，现在是固定在下部的两块，中间一个箭头。
3. 时序图并行线画 8 条，时间轴标注写「示意画 32 条」（手机上 32 条看不清）。条数等导演定，改 `TIMING_LANES` 即可，图里那行小字会跟着变。串行 → 并行那张图里，最后一组比特收齐后的并行输出落在图外，没有画出来。
4. 读数显示的是公式算出来的整数（偏 2 µm → 83%，偏 5 µm → 31%），时间轴文案写的是「约 80%」「约 30%」。
5. 「图内固定用字」表里的字是本工程自己加的，不在时间轴里，需要导演和科学审查确认。
6. 波形是示意：两级一阶低通（最糊时各 0.57 个比特宽，最坏情况眼高约剩 13%），不是按真实走线的损耗曲线算的；电 / 光波形是两级（NRZ），和角注「实际常用四级」一致。
7. **镜头之间是硬切，「1 帧暗场」转场不做。** 时间轴里没有结构化的转场字段（`transition_out` 是一句话），这里不从那句话里猜。要做的话：Blender 渲进画面，或者时间轴加字段后再在这里实现。
8. 路线图（`path_trace`）是在假的取样锚点上测的（旧锚点里没有 `path_*`；测试用的点是在屏幕上把旧锚点连起来造的，测完已删）。真实取样点放进来后要看：线和 3D 发光管是否对得上、三个字的位置、和大字 / 标签是否相压。
9. 开头大字的位置是固定的（`HOOK_BOX`），不跟画面。GPU 的锚点如果正好落在这一块里，标签会让到大字外面、不画引线；路线的线如果经过这一块，会从大字底下穿过（线在下，字在上）。新版 S01 的构图定了以后，可能要挪 `HOOK_BOX`。
10. 0.3–3.2 秒同屏的东西很多（大字、路线和三个字、最多两个标签、角注、字幕、五站条），互相不压，但信息量偏大；要不要错开时间由导演定（改时间轴）。
11. 标签的位置是逐帧按锚点算的，没有做平滑：锚点在两帧之间跳（例如 S01 9 秒处的快速摇镜），标签会跟着跳。摆法（右上 / 左上…）一条标签全程不变，但被别的东西挤开时的让位方向是逐帧选的，极少数情况下可能换边。
12. 图表面板里的字没有动（小标题 29 px、小字 24 px），在 540 宽的预演里偏小；要加大需要重排面板。
13. 没有按 Remotion 的 Studio 可视化编辑（`Interactive.*`、内联关键帧）来写：这里的版式都由数据驱动，Studio 里只用来预览。

## 授权

Remotion 不是 MIT 协议。个人，以及 3 人及以下的团队 / 公司可以免费使用（含商用）；4 人及以上的公司需要购买公司授权。条款以 <https://github.com/remotion-dev/remotion/blob/main/LICENSE.md> 为准。其余依赖（React 等）是 MIT。本工程没有引入任何第三方素材。
