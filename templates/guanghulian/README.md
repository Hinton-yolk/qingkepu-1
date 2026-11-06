# 白话光互连 · 项目骨架

做新一集时，把这里的东西拷进新目录：

- `engine/`：画面引擎（每帧都是 `window.seek(t)` 的纯函数）＋字体（`engine/lib/fonts`，含思源黑体 GB2312 子集、霞鹜文楷等）。
  - `engine/desk/film.js`：通用的「剪报调查桌」渲染器——撕边纸条、荧光笔（同一摞每一轮换色：黄→粉→青）、红笔圈/划线、红线、黑卡片、Kurzgesagt 式放大镜头、五站进度条、旁白版的压暗和重点字幕（深色撕边条＋米白字）。读 `window.DESK_PATH` 指向的时间表 json。
  - `engine/desk/film_land.js`：同一个渲染器的 B 站横屏版（`FILM_SIZE=[1920,1080]` 时自动换取景、进度条、字幕位置）。
  - `engine/desk/cards_base.js`：卡片里的通用画法（波形、方波、数字格、标签）。每集自己的机制卡片写在 `cards_epN.js`。
- `scripts/`：
  - `make_script_example.py`：口播稿（每句 id、文字、字幕断句 sub）→ `script.json`；配音用 Fish Audio「科普」声音 `83bc284d2a3848c8a37f6d9a9ab11cd8`。
  - `align.py`：测每句旁白的停顿 → `align.json`（时间表据此把「说到哪个词」对到秒）。
  - `build_desk_voice_example.py`：第三篇的旁白版时间表，是新一集的起点（纸条剪裁、摆放、镜头、按旁白划重点、卡片时间点、字幕取舍、检查）。
  - `render.mjs` / `stills.mjs`：逐帧渲染和抽静帧（`FILM=<名> FW=1920 FH=1080` 出横屏）；`render_chunked.sh`：60 fps 分段出片、拼接、混音、-14 LUFS；`sheet_from_mp4.py`：成片接触表。
- `audio/`：`score_example.py` 合成配乐和音效（读同一份时间表），`mix.py` 把旁白铺上去并侧链压低配乐，之后 `ffmpeg -af acompressor=threshold=-20dB:ratio=3:attack=8:release=150:makeup=1`。
- `covers/`：`cover.mjs`（抖音/小红书竖版封面）、`cover_bili.mjs`（B 站 4:3/16:9 封面），背景就是片子里的那张卡片。
- `系列规则.md`：制作规则（素材只用文字、镜头、配色、旁白、字幕、混音）。最新的系列决定以仓库根目录的 `DECISIONS.md` 和 `.claude/skills/series-guanghulian/` 为准。

依赖：Node + playwright（Chromium）、ffmpeg、Python（numpy、scipy、Pillow、PyMuPDF）、pandoc（文章 docx 转文本）。
