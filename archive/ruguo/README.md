# 「如果……会怎样」系列 · 项目源码存档

系列已暂停（见 `DECISIONS.md` 第 4 条）。导演原则在 `../ruguo-director-principles.md`。
每个目录是一个项目的源码：`render.mjs`、画面代码、工具脚本、字体、配音台词与 Fish 配音 mp3、`SCRIPT.md` / `FACTS.md` / `CREDITS`。
成片、wav、渲染帧（`out/`、`review/`、`frames/`、`stills/`）不在仓库里。

| 目录 | 内容 |
|---|---|
| `wifi-eyes/` | 01 如果眼睛能看见 Wi-Fi：第一版（v1/v2，`STORYBOARD.md`） |
| `wifi-eyes-short/` | 01 的约 50 秒短版 |
| `wifi-eyes-v3/` | 01 重做：四问结构的 2D 草稿 |
| `wifi-iso/` | 01 正式版：6 段式、等轴测 / 蓝图 / 全息画风 |
| `wifi-whitemodel/` | 01「白模投影」三个方向的风格帧 |
| `wifi-takashimadaira/` | 01「白模投影 · 高岛平团地」正片（A 方向） |
| `earth-stop/` | 02 如果地球突然停止自转 |
| `shrink-1cm/` | 03 如果你突然缩小到一厘米 |

## 没进仓库的大文件
`wifi-whitemodel/data/udx/bldg/` 下 6 个 PLATEAU 建筑 CityGML（32–118 MB）：
`53394525`、`53394535`、`53394541`、`53394542`、`53395542`、`53395543`（`_bldg_6697_op.gml`）。
可用 `wifi-whitemodel/tools_fetch.py` 从 PLATEAU 公开数据重新下载（脚本里读的目录文件是当时会话的临时文件，重跑前要先重新取一份 PLATEAU 数据目录）。
`wifi-takashimadaira/data/` 里已经是处理好的小文件，渲染正片不需要这些 GML。
