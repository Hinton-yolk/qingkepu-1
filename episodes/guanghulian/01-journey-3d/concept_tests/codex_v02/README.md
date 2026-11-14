# Director-Locked V0.2 — 9秒电控光预演

状态：制作交付，**不自行宣称导演通过**。严格范围为270帧、30fps、9秒，静音，无字幕、图表、位格UI或白闪。主规范 ../../preprod/13_Director-Locked_V0.2_9s.md；SVG只作为blocking参考。

## 来源与隔离
旧版实际源码在 `/workspace/kepu-studio-codex-exp01/episodes/guanghulian/01-journey-3d/concept_tests/codex_exp01/`，不在当前PR的Git树中；其影片在 `/workspace/outputs/codex-exp01/`。旧版是两张底板+Pillow，这次没有沿用。新工程从PR分支e4e0a0a5059415f6d3185462e6b399bfff562830建立，独立工作目录 `/workspace/kepu-studio-codex-v02`，本地分支 `codex/director-locked-v02`。只新增本目录，不修改T5、T6、规范或旧影片。

## 四镜和实现
- S1 F000–044：连续稳定的输入在实体芯片上分成两臂，轻推≤8%。
- S2 F045–089：同位置接分叉，侧移约30px；从F055起，10110010电码沿右侧实体电极向作用段传播。
- S3 F090–194：机位完全锁定；电作用96/108/120/132/144/156/168/180，合束源响应100/112/124/136/148/160/172/184。低位不是消失。两臂局部纹理相位错位、输出强度由示意MZI相对相位函数计算；细节见FACTS.md。
- S4 F195–269：同一合束端接同一弯曲输出路径，小幅向前跟随；已写入的亮暗包络继续上行，输入仍稳定，金色驱动停止，无抵达GPU或成功字卡。

一颗实体芯片、一条输入、两臂、相位段、合束与实体弯曲输出。所有信号场是Blender中的3D网格，逐帧更新顶点属性驱动发光；没有叠加二维底板或把SVG贴成最终画面。相机为透视，俯角32度；三个剪辑边界共享同位置投影，避免地理跳变。不是转台、穿模或交叉溶解。

## 可复现命令
当前环境已有Blender 5.2.3 LTS，与T5同版。Python依赖Pillow、numpy；现有FFmpeg；浏览器检查依赖已有Playwright与系统Chromium。

```bash
# 本目录执行；先测试关键帧及S3小段
BLENDER=/workspace/codex-environment/blender/blender-5.2.3-linux-x64/blender
XDG_CACHE_HOME=/workspace/codex-environment/cache "$BLENDER" -b --factory-startup --python-exit-code 1 --python render.py -- 0,44,89,96,100,112
# 检查少量样本后运行全部；仅复用同版本输出帧。改变场景源码需删除受影响帧。
XDG_CACHE_HOME=/workspace/codex-environment/cache "$BLENDER" -b --factory-startup --python-exit-code 1 --python render.py -- all
"$BLENDER" -b out/director_v02.blend --python-exit-code 1 --python probe.py
python3 encode_review.py
node playback.cjs
```

`shot_timeline.json` 是唯一导演帧表；render.py写出每帧camera transforms、投影锚点、事件状态与耗时到 `out/render_all.json`；保存 `out/director_v02.blend`。可审计原始灰模、曲线/采样样条和各层3D mesh。最后一个场景的mesh光场处于F269，完整时间求值由render.py的update函数复现，不假装.blend内部有完整烘焙关键帧。

## 成本取舍与证据
- EEVEE在无硬件GPU的软件环境首帧约45.7秒，已停止；未使用付费GPU。
- Cycles 540×960、4采样约每帧5秒，改为270×480、2采样、降噪后约1秒/帧，再Lanczos放大为540×960的审核MP4。这是**低清3D预演**，不是原生540渲染或精修。所有270帧均为真实3D渲染，不用最近帧补齐。
- 测试阶段发现并修复光场被波导实体遮挡、电位列传播不连续；重新生成受影响帧。运行日志区分试渲与最终批次；最终批次中的早期帧可复用，记录的耗时不包括所有试错。
- 新增费用 $0：现有CPU、无RunPod、无素材采购、无TTS。实际秒数、编码规格、文件SHA256见out/verification.json、render.log及ffprobe.json。
- 交付主接触表20帧；另提供S3八位前后16帧与每切点6帧邻域，避免主表过密。MP4与.blend/中间帧在out/，不进Git。

## 未完成的验收与风险
浏览器连续播放两轮的机械结果见playback.json（若执行失败应保留错误，不声称通过）；自动播放不是人类首看理解验证。本工具环境只能直接检查静帧/接触表，不能声称作为观众实时看完两轮并理解。**两位不知题目的真人首看者未验证**。对象识别、行动动机、因果先后、空间连续、释放五项均待独立导演评价，不自行打及格分。

仍有风险：显示时延和相位纹理高度示意；微观机制只呈现代表性MZI而不解释材料响应；核心合束处的4帧先后很短，手机首看可能来不及感知；S4仍使用同一整景的小幅跟随，需确认足够形成释放；原生低清可能损失局部相位纹理。科学说明置于README/FACTS，不通过小字救画面。

远程提交及Drive交付以最终执行报告为准：没有可用上传工具时只报告本地真实文件，不能制造URL、扩大分享权限或冒充已上传。完成即停止，等待GPT及用户审核，不制作T5/T6整片。

## 本次实测结果
最终批次记录225.675秒（包含复用帧的近零耗时；不含前面试错、S3小样与EEVEE测试）。规格检查PASS，S3机位固定，三个边界相机变换差0。编码后输出8位采样分别约189/65/190/189/64/65/190/65，亮暗比2.926，输入采样在S3为88.889–89.148。原始参数与结果见verification.json。通用动效检查PASS（静止约1%、最长0.03s），不代表观众理解通过。

Chromium通过本地HTTP连续静音播放两轮，每轮约9秒、解码总计540帧、报告0掉帧。最初file://播放被浏览器策略拦截，未改浏览器策略；改为标准本地HTTP审核页后成功。该机械播放记录不冒充两轮人眼连续审片；我亲眼检查了20帧主接触表及S3因果帧，真人首看仍未验证。

当前工具列表没有Google Drive上传或GitHub PR评论接口；未制造Drive直链、未扩大分享权限。MP4和完整运行记录通过本地交付包提供。源码与接触表按任务要求尝试仅追加到PR #3工作分支；实际提交/推送结果以最终报告为准。
