# 定妆静帧：「把纸桌拍成真的」（2026-11-11）

方向和约束见 `DECISIONS.md` 11-11 最后一条、`HANDOFF.md`「下一步」。这里是那张定妆静帧的场景和做法。

## 文件
- `make_textures.py`：屏幕内容（方波 +「四个？还是五个？」）和三条纸条的贴图（PIL）。
- `scene.py`：Blender 场景（全部代码建模，按真实尺寸，单位米）+ 渲染设置。
- `post.py`：后期，只加高光晕、轻微暗角、细颗粒。
- `定妆静帧_v1.jpg`：成品（1080×1920）。无损 PNG 没进仓库。
- `对照_两个模型各做一张.jpg`：同一份任务说明，Opus 5.5 独立试做的一张（右，540×960 试渲画质）和本目录这张（左）并排。Opus 那次约 13 万 token、10 分钟、试渲 8 次，脚本没进仓库。

## 重新出图
```bash
# 1. 素材（都不进仓库）：Blender 5.2.3；Poly Haven CC0 贴图；Noto 字体（OFL）
#    wood_table_001 的 diff / rough / nor_gl（4k jpg）、painted_plaster_wall 的 diff / nor_gl（2k jpg）
#      https://dl.polyhaven.org/file/ph-assets/Textures/jpg/4k/wood_table_001/wood_table_001_diff_4k.jpg  （其余同理）
#    NotoSerifSC-Medium.otf → 存成 NotoSerifSC.otf；NotoSansSC-Bold.otf
#      https://raw.githubusercontent.com/notofonts/noto-cjk/main/Serif/SubsetOTF/SC/NotoSerifSC-Medium.otf
#      https://raw.githubusercontent.com/notofonts/noto-cjk/main/Sans/SubsetOTF/SC/NotoSansSC-Bold.otf
python3 make_textures.py <素材目录> <tex目录>
# 2. 试构图 / 灯光：270×480、48 采样，云端 4 核 CPU 约 10 秒一张
blender -b -P scene.py -- <tex目录> <素材目录> out/t.png 25 48
#    调灯时加 top=1 看正上方俯视的光斑；其它参数 key=value（pitch yaw dist fstop el az slat exposure sun sky screen）
# 3. 高清：1080×1920、600 采样（自适应）+ OIDN，云端 4 核 CPU，实测 15 分钟（当时另有试渲在抢 CPU）
blender -b -P scene.py -- <tex目录> <素材目录> out/final.png 100 600
python3 post.py out/final.png out/final_post.png out/final_540.jpg
```

## 场景里有什么（都按真实尺寸）
- 封闭房间，左墙一扇窗，窗上 50 mm 叶片的百叶（间距 45 mm）。**唯一的灯是窗外的太阳**（高度角 24°，光盘 0.53°，暖色）+ 从同一扇窗进来的天光；平板屏幕自发光。没有别的灯、没有雾、没有辉光。
- 桌面：Poly Haven `wood_table_001`（CC0）。墙：`painted_plaster_wall`（CC0）。
- 平板 248.6 × 179.5 × 6.1 mm，64° 斜靠在三本书上；屏幕内容是一张 2D 图贴在玻璃上。
- 三条纸条（约 24 × 6 cm，纸厚 0.11 mm，两头略翘）。主纸条是用户确认过的原文「连续五个 1，就是一段连在一起、没有缝隙的高电平。」，「五个 1」上有荧光笔。
- 两枚红图钉 + 一根红线（直径约 1 mm，绕在针上拉直）；马克杯、开着盖的荧光笔。
- 相机：50 mm、f/2.8，离桌面约 0.82 m，俯角 52°。主纸条和屏幕中心离相机的距离只差约 3 cm，所以两处都在焦内；前景纸条和后面的杯子、书自然虚掉。
- 色彩：AgX，不加 look。

## 还没做 / 已知的简化
- 屏幕玻璃很干净，没有指纹和灰；桌面没有灰尘和杂物痕迹。
- 两条配角纸条的字是按口播写的，不是用户确认过的纸条原文（它们在焦外，只当环境）。
- 红线只连到平板脚下的图钉，没有连到屏幕上（真东西钉不进屏幕）。
- 平板底边金属倒角上有两处小红点，是图钉和红线的反光。
