# 白话光互连 · 各集源码

| 目录 | 内容 |
|---|---|
| `01-why-light/` | 第一篇《AI芯片互连为什么要从电换成光？》：正片 v3、旁白版、B 站横屏版 |
| `02-serdes/` | 第二篇《第一站 出发：SerDes》：正片、旁白样片 v1–v5、旁白完整版、B 站横屏版 |
| `03-copper-blur/` | 第三篇《电的路：信号为什么越跑越模糊？》：正片 v2（200G/400G/800G…）、旁白版 |
| `04-retimer-dsp/` | 第四篇《检修站：模糊的信号怎么修回来？》：正片 |
| `articles/` | 五篇文章原稿（01 只有 PDF，附抽出的文本；02–05 有 Word 原件和转好的 Markdown） |
| `标题与简介.md`、`B站_第*篇_标题简介.md` | 抖音／小红书／B 站的标题、简介、标签、章节 |

每集目录里：
- `代码工程/epN/`（第一篇是 `full/`）：场景代码（`film.js`、`cards_*.js`）和时间表 json；`eras_*.js` 选片子：正片、旁白版（`*v*`）、横屏版（`*b`）。
- `tools/build_desk*.py`：时间表生成（唯一真源，画面和配乐都读它生成的 json）。
- `配音/`：口播稿 `script*.json`（逐句文字＋字幕断句）、停顿对齐 `align*.json`。配音 wav 没放，按口播稿用 Fish Audio 重新生成即可。
- `配乐/`：配乐、音效、混音脚本。
- `素材/`：文章 PDF、逐字坐标 `chars2.json`、页面高清图 `hi-*.png`（剪纸条用）。
- `covers/`、`output/`：封面、文案、说明、字幕 srt。
- `render_*.sh`：出片命令。

引擎和字体不在每集里重复放：运行前把 `templates/guanghulian/engine/` 里的 `engine.js`、`index.html`、`transitions.js`、`lib/`、`scenes/` 拷（或链接）进该集的 `代码工程/`。
成片、配音 wav、渲染帧都没放（按规则不进仓库），用上面的脚本可以重新生成。
