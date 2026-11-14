# Blender PoC 03 · Cycles 写实静帧，对标 Seedance 2.5

问题：如果全部用 Blender Cycles 渲染，写实程度能不能接近 Seedance 2.5？
做法：选 Seedance 2.5 那段（PoC 01）最好看的一帧当目标，用代码建模 + Cycles 渲一张 1080×1920 静帧，并排对比。
全程本机 CPU，费用 $0。

## 文件
| 文件 | 内容 |
|---|---|
| `refs/target_seedance25_f100.png` | 目标帧：Seedance 2.5 第 100 帧（4.17 s），480×854 |
| `refs/ref1–5.jpg` | 用户给的 800G OSFP 参考图（缩小存档） |
| `build_hero.py` | 场景脚本：OSFP 模块、笼子、网卡、元件、台面、灯光、相机全部由代码生成 |
| `make_pcb_texture.py` | 程序生成电路板走线 / 焊盘贴图 |
| `grade.py` | 后期调色：冷暗部、反差、柔光、暗角、颗粒 |
| `hero_1080.png` | 终版静帧（调色后） |
| `compare.jpg` | 目标帧和终版的并排对比 |
| `FACTS.md` | 尺寸、形态判断和待核项 |

重做（本目录）：
```bash
python3 ../../tools/polyhaven.py get studio_small_09 --res 2k
```
```bash
python3 make_pcb_texture.py
```
```bash
blender -b --factory-startup --python-exit-code 1 --python build_hero.py -- still --res 1080 --spp 96 --out out/hero_1080_raw.png
```
```bash
python3 grade.py out/hero_1080_raw.png hero_1080.png
```
