# EP01 开场概念样片：冰箱里正在生成的世界

约 20 秒，9:16，30 fps，540×960 渲染、1080×1920 合成。无配音，只有合成的环境声和动作音效。
和旧工程（`../anim01/`）分开，旧版本没有动。

## 文件
- `fridge.py`：Blender 场景和全部动画（Cycles）。厨房、冰箱、门内的雾 / 海 / 林谷；`pose(t)` 是时间的纯函数。
- `post_fridge.py`：2D 文字层（AI 正在写的故事、演示回放标记、底部示意说明、结尾问题）、声音、编码。
- `pack.py`：打 RunPod 渲染包。

## 怎么做的
- 门内是真的三维空间：冰箱背板和后墙在冷藏室那一块开了洞，海和森林在墙后面延伸到远处。门框、内胆、门板正常遮挡。相机横移、推近时，门框和远景之间有视差。
- 房间是封闭的：门内世界的天光只从门洞照进厨房（Cycles 光门户），门里的光会落到厨房地上。
- 海：冷藏室里有一整块透明海水（体积吸收，越深越蓝），水面和墙后面的大海面连在一起。还有低太阳、海面反光、远处的岛和帆船，以及远景雾。
- 森林：墙后面地势往下落成一片林谷，树冠一层层排到远处。树从近到远依次长出来，会轻轻摇；冷藏室里长着几丛蕨，飘着落叶。
- 「还没写定」：门洞里是一层发亮的雾。续写片段落定时，雾从上往下散开，世界随之成立。演示回放时，雾从下往上合回去，海退下。

## 渲染
```bash
# 本机看几个时刻（秒）
blender -b -P fridge.py -- --outdir /tmp/x --res 360 --samples 12 --only 2.6,7.0,17.0
# RunPod（仓库根目录）
python3 episodes/ai/01-yigeyigezi/src/fridge01/pack.py --res 540 --samples 32 --chunks 8
python3 tools/runpod_render_gql.py run episodes/ai/01-yigeyigezi/src/fridge01/out/pack_v1/jobs.json --pods 4 --yes
# 合成
python3 post_fridge.py out/render_v1/frames out/post
```
