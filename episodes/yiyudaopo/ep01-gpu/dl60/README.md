# 一语道破 EP01 · DIRECTOR-LOCKED 60s

导演锁定版 60 秒新片（不是旧片的剪辑）。标题：AI 又不打游戏，为什么还要用显卡？
1080×1920，30 fps，1800 帧（0000–1799），无旁白、无人声，原创器乐 + 音效。

## 文件
| 内容 | 位置 |
|---|---|
| 3D 场景（开头 OPEN、结尾 CLOSE，同一块加速器模组、同一支 50 mm 镜头） | `blender/dl60_scenes.py`（模组几何复用 `../blender/ep01_scenes.py` 的 `build_module`） |
| 逐帧芯片锚点（Remotion 叠加层对齐用） | `blender/out/anchors_*.json` → 复制到 `../remotion/src60/anchors/` |
| 底片编码 | `blender/encode.py` |
| RunPod 渲染任务 | `blender/jobs_runpod_hq*.json`、日志 `blender/runpod_hq*.log` |
| 2D / 合成（Remotion，全部可确定性重渲） | `../remotion/src60/`：`lib/plan.ts`（关键时间、世界坐标、虚拟相机）、`lib/island.ts`（小岛与地块）、`layers/`（Game / Carrier / AI / Die / Stage）、`Tile.tsx`（计算方块母题） |
| 配乐与音效 | `audio/dl60_audio.py` → `../remotion/public/dl60/mix.wav` |
| 出片 + 转场片段 + 接触表 + 动效检查 | `render60.sh` |
| 事实表 | `FACTS_dl60.md` |
| 制作报告 | `docs/执行报告_v01.md` |

## 重渲步骤
```bash
# 1) 3D 底片（本机 CPU 只适合低清预览；成片走 RunPod，见 jobs_runpod_hq.json）
blender -b --python-exit-code 1 --python dl60/blender/dl60_scenes.py -- anchors OPEN dl60/blender/out/anchors_OPEN.json
blender -b --python-exit-code 1 --python dl60/blender/dl60_scenes.py -- anchors CLOSE dl60/blender/out/anchors_CLOSE.json
python3 tools/runpod_render_gql.py run episodes/yiyudaopo/ep01-gpu/dl60/blender/jobs_runpod_hq.json --pods 3 --max-hours 1.5   # 在仓库根目录
python3 dl60/blender/encode.py hq_OPEN hq_CLOSE
# 2) 声音
python3 dl60/audio/dl60_audio.py
# 3) 出片
bash dl60/render60.sh
```
改相机或时间点时，`dl60_scenes.py` 的 `DIEW_K / DIEW_V` 和 `src60/lib/plan.ts` 的同名常量必须一起改（2D 相机在 48.5 秒交给 3D 底片）。
`dl60_audio.py` 顶部的 `T` 照抄 `plan.ts` 的 `T`，改画面时间点要同步。
