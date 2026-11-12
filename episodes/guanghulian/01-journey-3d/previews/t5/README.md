# T5 3D 电影级镜头验证 · 导演预览 v1（2026-11-12）

对应 PR #3 第 22 条 T5 和第 23 条《T5 夜间制作补充》。节奏表：`../../concept_tests/t5_3d/镜头节奏表_T5.md`；过程记录：`../../concept_tests/t5_3d/夜间进度.md`。
视频不进仓库，在 Drive 审核文件夹，直链写在 PR 里。这里不给自己打「通过」：下面是内部技术检查和导演自评，不是观众验证。

## 文件
| 文件 | 字节 | sha256 |
|---|---|---|
| EP01_T5_preview_v1_silent_540x960_30fps.mp4 | 2 917 362 | 5b5d74a571561b0246d2954a79b70bbfc2844822d7ec15cb8da9c06e4a94703d |
| EP01_T5_preview_v1_sound_540x960_30fps.mp4 | 2 696 602 | 883fb098b4bdd59d23e6ebd943eb9e530bf017afe6be2774b6210273d148f8ef |

H.264，540×960，30 fps，20.8 秒（624 帧）；试听版另有 AAC。3D 帧由提交 `21bfebd` 的脚本在 RunPod 渲出（Cycles OPTIX，RTX 4090，shot1 / arrive 32 采样、shot23 40 采样，降噪）；合成由提交 `bcba036` 的 `t5_comp_build.sh` 生成。
关键帧：`T5_shot1_arrive_关键帧.jpg`、`T5_shot23_关键帧.jpg`、`T5_shot23_金色消息修正.jpg`；成片每秒一帧：`T5_preview_v1_每秒一帧.jpg`。

## 内部技术检查（不是观众验证）
- `tools/motion_check.py`：PASS（静止帧 0%，最长静止 0 秒）。
- 试听版 AAC 实测 -15.0 LUFS、true peak -2.5 dBTP。**声音没有人听过。**
- 上传后不登录下载，sha256 一致。

## RunPod 实际用量
- 试渲：RTX A6000 1 台，墙钟 2.0 分钟，约 $0.02。
- 整段：RTX 4090 2 台（Secure，$0.89/时），约 20.5 + 29.5 分钟，按秒约 $0.74；工具的上限估计 $0.85。
- 合计 ≤ $0.87，以 RunPod 账单为准。机器都已删除。

## 重做
1. 3D 帧：`bash <临时目录>/tools/t5_stage.sh <工作目录>` 打包场景（脚本见夜间进度），`runpod_render.py run jobs_full.json --pods 2 --gpu "NVIDIA GeForce RTX 4090,NVIDIA RTX A6000"`。
2. 合成：`bash concept_tests/t5_3d/t5_comp_build.sh <帧根> <输出目录>`。
