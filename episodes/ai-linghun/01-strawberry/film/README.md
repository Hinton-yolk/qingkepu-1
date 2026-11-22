# EP.01 strawberry · 整片工程（暖光桌面风格）

- `index.html`：three.js 场景 + 2D 字幕层，`window.seek(t)` 是 t 的纯函数；`timeline.js`（上一级目录）驱动。
- 用户 2026-11-21 的要求（见 DECISIONS）：只在第一帧用大标题，之后只有字幕；不要进度条；运镜始终跟随正在演示的东西（`FK` 表：每拍一个焦点 + 取景宽度 + 角度，单调三次插值；景深对焦在焦点上）；终版用 Blender，在 RunPod 上渲。
- 当前范围：前 31.5 秒（到「这种积木，行业里叫 Token。」）；剩下 80 秒待做。

## 命令（在本目录）
- `node render.mjs`（three.js 全段）、`--stills=…`、`--sheet`、`--start= --end=` 只渲一段、`--frames=目录`
- `node render.mjs --export --start=18.4 --end=22.4`：导出 `blender/scene.glb`（--start 时刻的场景）和 `blender/anim.json`（逐帧：25 个运动物体的世界矩阵与可见性、相机、景深焦距、光刃 / 导光管 / 切口灯的强度）
- `node render.mjs --bg=ab --start=18.4 --end=22.4 --frames=out/frames_ab_blender`：用 Blender 渲出的帧（`blender/out/ab/`）作底，叠同一套调色、标注和字幕
- `node render.mjs --overlay`：只出透明的标注 + 字幕层

## Blender（`blender/build.py`）
导入 GLB，按名字换材质（米白：哑光加少量次表面和清漆；黑炭；拉丝铝：金属 + 各向异性；磨砂玻璃：透射、粗糙 0.3；导光管：透明管 + 发光芯；光刃、切口灯按帧打关键帧），暖色太阳光（角直径 4°，软阴影）+ 顶部柔光箱 + 世界环境光；相机按 anim.json 逐帧（与 three.js 同一相机，画面偏移用 shift_y），真景深（f/2.2）和运动模糊（快门 0.4）；Cycles + OpenImageDenoise，AgX。
坐标：three.js Y 朝上、Blender Z 朝上，物体矩阵用 C·M·C⁻¹，相机用 C·M。
RunPod：`python3 ../../../../tools/runpod_render_gql.py run blender/jobs_ab.json --pods 2 --yes`（在仓库根目录跑，路径相对仓库根；key 由网络代理注入，命令行设 `RUNPOD_API_KEY=proxy-injected`）。

## A/B 镜头（2026-11-22）
- 范围：18.4–22.4 秒（第 552–672 帧）：托盘把方块送进分词器 → 光刃切开 → 三块跳上底座。
- three.js：云端 4 核 CPU，约 2 秒一帧。
- Blender：Cycles 128 采样 + 降噪，1080×1920；RunPod 1 台 L40S（社区云 $0.79/时）+ 1 台 4090（Secure Cloud $0.89/时，社区云没空卡），墙钟 9.6 分钟，脚本估计约 $0.27（上限，以账单为准）。
- 本机 CPU 用 bpy 5.3 渲一帧 540×960、16 采样约 11 秒，用于核对对齐（与 three.js 同一帧逐物体对齐）。
- 输出：`out/ab_three.mp4`、`out/ab_blender.mp4`、`out/ab_side_by_side.mp4`（左 three.js、右 Blender，不进仓库）。
- 观察：Blender 的磨砂玻璃有真实折射、光刃照亮台面、阴影更软、米白更像哑光陶瓷、有运动模糊；导光管在 AgX 下偏白、暖光不明显，整体偏暗——终版要调导光管发光颜色 / 强度和曝光。
