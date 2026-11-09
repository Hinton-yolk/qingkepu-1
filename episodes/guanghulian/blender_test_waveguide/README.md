# Blender 测试镜头二：硅光波导是怎么刻出来的（Branch 式层块工艺，14 秒竖屏）

- `shot_waveguide.py` — 场景（全部程序化建模，兼容 Blender 4.5 / 5.x）。时间轴在脚本的 `T` 字典里。
- `render_package_win/` — 给用户显卡电脑的渲染包（双击 bat）。打包：`scratchpad/blender_render_waveguide_v1.zip`。
- `composite_waveguide.py` — 拿回 `waveguide.mp4 + anchors.json` 后在云端合成：工序条（涂胶 / 曝光 / 显影 / 刻蚀 / 去胶 / 导光）、层名标签（按 3D 锚点画引线）、字幕（y=1400）、角标、代码合成配乐与音效（-14 LUFS）。
  - `python3 composite_waveguide.py <目录> <输出.mp4>` 出成片；`--stills` 只合成已有几帧看排版；`--audio` 只出配乐。
- `FACTS.md` — 片中每个数字的依据和示意说明。
- `lookdev_draft_sheet.jpg` — 云端 432×768、8 采样的草稿静帧加字效果（不是成片画质）。

按规则：Blender 视频只在用户的显卡电脑上渲；云端只做极小的草稿静帧检查构图。成片合成后要过「审核 / 监督 / 观众」再交付。

## 渲染速度实测（用户的 RTX 2060，1080×1920，第 385 帧，2026-11-09）
| 引擎 | 设置 | 每帧 | 整段 420 帧 |
|---|---|---|---|
| Cycles | 128 采样、8 次反弹（v1 包） | 约 30 秒 | 约 3.5 小时 |
| Cycles | 64 采样、4 次反弹（现在的默认） | 估计 13–15 秒（云端实测比上一行快约 2.2 倍） | 约 1.5–2 小时 |
| EEVEE | 64 抗锯齿采样，`--eevee` | **约 2 秒** | **约 15 分钟** |
EEVEE 画质对比待用户发回 preview_eevee 的两张图后确认。
