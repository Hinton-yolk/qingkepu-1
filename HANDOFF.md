# 交接（新对话先读这个）· 2026-11-10

上一个对话从 11-08 开到 11-10，太长了，为省额度新开一个对话。规则、决定都已经在仓库里，这里只列**进行中的事**和**新对话要知道的背景**。

## 最新进行中（11-10 晚）：光互连 02 下集「新画面版」
- **方向**（用户定）：讲解内容不变，口播一字不改用原稿 y1–y14；只把画面升级成写实 3D（Epic Spaceman 那种质感，但控制成本）。主持人已去掉（「不太协调显得很假」）；信号用金色；五站条常驻；每集 Blender 约 1 小时以内。
- **目录**：`episodes/guanghulian/02-serdes/下集_新风格/`
  - `内容关卡1_脚本与分镜.md`：分镜第三稿 + 转场表（中间段是静帧背景，光带在云端画成动画，换背景用甩镜、光带连续变形）。
  - `配音/`：原稿 14 句重新生成的配音（任务号在 tasks.txt；mp3 在 gitignore，丢了就按任务号的 URL 重新下载，不要重新生成）。
  - `blender/shot_open.py`：场景脚本（A 段手机、B 段服务器主板走线、5 个背景机位；`check=1` 逐帧自查信号和灰尘位置；云端只能用 Cycles 渲草稿，缺 libEGL）。
  - `草稿/`：内容关卡 2 的接触表和带配音样片（关卡 2 已通过）。
  - `交付/ep02x_render_package_v1.zip`：正式版 EEVEE 渲染包（审核已通过），**已发给用户，等用户先跑 preview_eevee.bat 回报速度和 4 张图**，再跑正式渲染，发回 A.mp4、B.mp4、stills（5 张背景 + json）。
- **11-10 深夜**：用户选 r2 + Cycles（显卡）。正式渲染包 v4（`交付/ep02x_render_package_v4.zip`，审核通过）已发，用户整晚跑 `start_render_cycles.bat`（64 采样，预计 2–3 小时），等发回 A.mp4、B.mp4、stills（5 张 + json）。收到后：看降噪闪烁（雾和散景里）；云端合成整片（中间段光带动画、2D 灰尘、字幕、五站条、配乐、调色提色度、相机滚转漂移）；成片前审核 + 监督 + 观众（Codex 要先装、请用户登录）。
- **11-10 晚更新**：用户看了 v1 正式渲染「很塑料」；质量目标定为 Epic Spaceman（CLAUDE.md 3D 一节）。已做「去塑料感」r1 和「Epic 化」r2（逆光光柱、主板铺到远处长满器件、B 段相机水平 + 镜头平移），样张包 `交付/ep02x_lookdev_r1r2.zip` 已发给用户（两轮 × EEVEE / Cycles 显卡，10 张），等回图和每帧耗时，定引擎和风格。
  - 正式包之前要改（审核记的）：r2 的 xray 背景被逆光打白（xray 时关逆光）；close 背景下半张逆光反光太亮；B 第 1 帧信号压在反光上；A 段相机要不要也放平；render_package_win 的 bat 要写死 look=…；以后可以考虑整集真 3D（用户说等样张出来再定）。
- **下一步**：
  - 收到试渲：看 B 段第 2 帧耗时（>20 秒就先调）、灰尘在 EEVEE 里是不是虚的（审核提醒 BLENDED 材质景深可能不对）、板面白横纹、亮度色度（`tools/frame_stats.py`）。
  - 收到正式渲染：在云端合成整片——中间段光带动画（用 stills 的 json 沿走线画，y2→y3 接点要对上 3D 光带的位置和样子）、2D 灰尘层、字幕、五站条、配乐；y12 配音 5.07 秒比 A 段倒放 2.4 秒长，画面不能停住；动效检查 PASS。
  - 成片交付前：审核（最强模型）+ 监督 + 观众（Codex，要先装、请用户登录）。

## 先读
1. `CLAUDE.md`：通用规则。重点看这两节：
   - 「3D 镜头语法」，11-10 新加；
   - 「四个角色」：已改成按节点查，日常检查用 Sonnet。
2. `DECISIONS.md`：读 11-09、11-10 两天的记录，以及「待定事项」。
3. `episodes/guanghulian/要求清单_3D与Blender.md`：监督维护的用户要求清单（3D、Blender 这条线）。

## 进行中：Blender 测试镜头三「光在芯片里走的路有多细？」
- **目录**：`episodes/guanghulian/blender_test_scale/`
  - `SHOTPLAN.md`：分镜第四版，审核已通过；
  - `FACTS.md`：每条事实标了来源等级（〔读〕〔摘〕〔估〕）；
  - `shot_scale.py`：场景脚本。
- **镜头内容**：竖屏 18 秒，一个连续镜头，按对数匀速往里推。依次是：
  1. 交换机；
  2. 光模块，旁边放手机作比例；
  3. 硅光芯片，旁边一粒米；
  4. 芯片边缘的光纤阵列，旁边一根头发；
  5. 离边缘 150 µm 的波导，旁边一个红细胞；
  6. 停在「不到 0.5 µm」的波导上。
- **方向是用户定的**：「反过来推进」，模块那一级的比例物用「一部手机」。
- **现状（11-10 晚）**：第二版渲染包已发给用户，审核「通过（附带建议）」，**等用户在 RTX 2060 上试渲 6 帧**（preview_eevee.bat），再渲整段。
  - 第二版（用户 11-10 定）：「环境最重要」→ 交换机放进机房（开放式机架、左右机柜、身后 7 排机柜指示灯、雾）；前景少量虚化灰尘；全程浅景深；相机滚转；颜色「从暖到冷」（0–4.5 秒暖金、4.5–8 过渡、8 秒起冷调）；跳线黄色护套 + APC 绿色 MPO；手机背面朝上；标签加深色描边。
  - 进度图：`progress_realism_v2_审核后.jpg`（最新）、`progress_realism_v2_暖冷对比.jpg`、`progress_realism_v2_暖到冷.jpg`。参考片学习：`research/参考片实测_录屏两部_1110.md`。
  - 渲染包：`render_package_win/`（脚本在仓库里；assets、assets_dl 在 gitignore，打包前从上级目录拷）。整段先出 PNG 序列（可续渲），再用 Blender 自带编码成 `scale.mp4`（`encode_mp4.py`，编码前核对 540 帧齐全）。
  - 审核留下的建议（等用户 1080 试渲图回来一起看）：17.5 秒双箭头在画面上偏到光带左边（箭头比波导顶面高 0.16 µm，可沿视线往相机挪约 0.33 µm，带一点 x 分量）；光带左侧有一条很淡的平行带，要确认不读成第二条光路；红细胞在 1080 图上再确认不像悬空。
  - 简化（已写进 FACTS 和角注，交付时要告诉用户）：调制器画成直波导两侧电极，没画 MZM 的分束和两臂；模块里激光器耦合和键合线省略；机房没画冷热通道。
- **下一步**：
  - 用户发回 6 张试渲图和每帧时间：看图、按上面的建议改，确认整段时间；
  - 用户发回 `scale.mp4` + `anchors.json`：云端合成（大字问题、角注、结尾一句、角标、配乐），见 SHOTPLAN「合成」；成片交付前是审核 + 监督 + 观众（Codex，要先装、请用户登录）节点。
- **素材**：
  - Poly Haven 的 HDRI 和贴图放在 `blender_test_scale/assets_dl/`（gitignore，新对话要重新下载）：
    - `studio_small_09_2k.hdr`
    - `metal_plate_rough_2k.jpg`
  - 下载地址：`https://dl.polyhaven.org/file/ph-assets/HDRIs/hdr/2k/studio_small_09_2k.hdr`、`https://dl.polyhaven.org/file/ph-assets/Textures/jpg/2k/metal_plate/metal_plate_rough_2k.jpg`。
  - 版图贴图用 `python3 make_layout_texture.py assets/chip_layout.png` 重新生成；硬件贴图用 `python3 make_hw_textures.py`（都在 gitignore 里）。
  - 云端 EEVEE 要先装 `libegl1 libgl1-mesa-dri`（apt），否则报 libEGL 找不到。
  - 用户说过：「过程中你需要哪些素材，只管问我来要，我要的是出片质量！」已经向用户要了两张参考图：交换机 / 光模块的实拍、硅光芯片显微照，还没收到。
- **云端测试**：Blender 5.2.3 在 `/tmp/blender/blender-5.2.3-linux-x64/`，容器重启会丢，要从 download.blender.org 重新下载。云端只渲低清静帧看构图（270×480，16 采样）。

## 渲染的路
- 用户的 Windows + RTX 2060：EEVEE 每帧约 2 秒，Cycles 约 30 秒。默认用 EEVEE。
  - 渲染包形式：双击 `.bat`，通过 `find_blender.cmd` 找 Blender。
- **审核用的模型**（用户 11-10）：渲染包 / 草稿节点的审核也用最强的模型；监督和日常小检查用 Sonnet。
- 用户准备试 **AutoDL 租卡**（RTX 4090）。11-10 已给用户方案（待确认）：EEVEE 为主（草稿和大部分终版在 2060 上），Cycles 只给 A/B 对比后确实更好的少数镜头（候选：开头 0–2 秒、结尾 13.5–18 秒）；默认「渲染包 + 一条命令」，直连 Jupyter 只用于首次配置和排错。镜像选基础镜像 Miniconda、Ubuntu 22.04。AutoDL 当时没有空闲 GPU。
  - **云端连不出 SSH**（实测 22 端口超时），只能走 HTTPS。打算通过实例的 JupyterLab 连：用户把实例域名发过来，token 用 `request_credential` 安全表单收，header 用 `Authorization`，前缀 `Token`。
  - 还没实际连过，第一次只做三件事：装 Blender、确认 GPU、试渲 5 帧。
  - 不要用网上第三方的 AutoDL MCP。
- 租卡不省 Claude 额度，只省时间。

## 其它挂着的事
- **Style Bible**：`episodes/guanghulian/Style_Bible_v1.md` 的 5 个问题，加上「3D 镜头语法」里的几处待定（底色、曝光光颜色、圈、工序时长、回弹、亮度门槛）。用户说「先把样片跑出来，看看效果咱们再定」。
- **「样片」指哪个，还没问清**：可能是测试镜头三，也可能是 Style Bible 里 75 秒样片的前 20 秒。目前按测试镜头三在做。
- **波导测试镜头二**（`episodes/guanghulian/blender_test_waveguide/`）：用户说暂时不发。`composite_waveguide.py` 里的辉光要按「约束在芯区」复查。
- **观众（Codex）**：这台机器上没装。出成片前要先装，再请用户用 `codex login --device-auth` 登录。

## 沟通
- 用中文回复，偶尔夹英文可以，但不要整段纯英文。
- 用户是剑桥材料学博士，芯片与光的行家：数字和器件结构必须准确，拿不准就问用户。
- 省额度：
  - 少开子 agent，只在节点查；
  - 少看大图；
  - 一个镜头告一段落就新开对话。
