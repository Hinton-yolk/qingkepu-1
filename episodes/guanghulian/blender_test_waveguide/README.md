# Blender 测试镜头二：硅光波导是怎么刻出来的（Branch 式层块工艺，14 秒竖屏）

- `shot_waveguide.py` — 场景（全部程序化建模，兼容 Blender 4.5 / 5.x）。时间轴在脚本的 `T` 字典里。
- `render_package_win/` — 给用户显卡电脑的渲染包（双击 bat）。打包：`scratchpad/blender_render_waveguide_v1.zip`。
- `composite_waveguide.py` — 拿回 `waveguide.mp4 + anchors.json` 后在云端合成：工序条（涂胶 / 曝光 / 显影 / 刻蚀 / 去胶 / 导光）、层名标签（按 3D 锚点画引线）、字幕（y=1400）、角标、代码合成配乐与音效（-14 LUFS）。
  - `python3 composite_waveguide.py <目录> <输出.mp4>` 出成片；`--stills` 只合成已有几帧看排版；`--audio` 只出配乐。
- `FACTS.md` — 片中每个数字的依据和示意说明。
- `lookdev_draft_sheet.jpg` — 云端 432×768、8 采样的草稿静帧加字效果（不是成片画质）。

按规则：Blender 视频只在用户的显卡电脑上渲；云端只做极小的草稿静帧检查构图。成片合成后要过「审核 / 监督 / 观众」再交付。
