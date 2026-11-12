# 交接（新对话先读这个）· 2026-11-12

上一个对话从 11-12 早上开到晚上，上下文涨到 84 万 token，每走一步都要重读一遍，把每周用量上限撞穿了。所以换新对话。
规则、决定、现状都在仓库里，这里只写**新对话接手要知道的事**。11-10 的旧交接保留在文末。

## 一、现在在做什么
**光互连 01 的 3D 正式版**《一个比特的旅程：从 GPU 到 GPU》，Blender + Remotion，竖屏 1080×1920，30 fps。

- 分支：`claude/happy-goodall-o47ilg`。**新对话如果被分配了别的分支，先问用户**；这条线的 Draft PR 开在这个分支上。
- Draft PR：doityj335-prog/kepu-studio#3，https://github.com/doityj335-prog/kepu-studio/pull/3 。用户确认前不合并。
- 任务入口：Issue #2，https://github.com/doityj335-prog/kepu-studio/issues/2 。
- 项目目录：`episodes/guanghulian/01-journey-3d/`。

**状态：第二轮（P0 → P1 → P2）已交付，等 ChatGPT 审核和用户确认。没有成片，没有配音，没有全片 Animatic。**

## 二、先读（按顺序，读这五个就能接上）
1. `CLAUDE.md`：通用规则。11-12 新加了两处：「云 GPU 渲染怎么批」、「四个角色」里的「派出去的角色和后台任务要有人盯着」。
2. `episodes/guanghulian/01-journey-3d/README.md`：现状表、粗模的已知问题、交接记录。
3. `episodes/guanghulian/01-journey-3d/preprod/09_第二轮导演修订说明.md`：这一轮做了什么、已修和没修的、等用户定的事、测试输出。
4. `episodes/guanghulian/01-journey-3d/preprod/10_第二轮复盘_耽误的事和改进.md`：上一个对话犯的八个错和该怎么做。**务必读第三节。**
5. PR #3 的说明和最新评论。

需要时再读：`preprod/08`（硬件路径和导演决策表）、`preprod/02_分镜.md`、`timeline/timeline.json`（唯一的时间来源）、`FACTS.md`、`DECISIONS.md` 里 11-12 的几条、`episodes/guanghulian/要求清单_3D与Blender.md`（G–J 节）。

## 三、协作方式
- **用户在 ChatGPT 那边审定任务**，ChatGPT 把任务和审阅意见写成 PR #3 的评论（用用户的账号发），用户再到 Claude 这边说「读 PR #3 最新评论」。评论是 ChatGPT 起草的；用户让执行才执行。
- **不给 Claude 设 API、Routines、自动触发器**，不订阅 PR 动态。
- **PR 评论和会话里的话不一致时**：花钱、公开、改权限这三类事按更严的做，并回到会话里问用户一次。
- **花钱之前、交付之前，各读一遍 PR 和 Issue 的新评论。** 上一个对话漏读了一条，两批云渲染没按要求报批。
- 所有选型（参考机型、光口位置、开头版本、Q1–Q7）目前都是推荐方案，**没有一条是用户确认过的**。不要把它们写成定稿。
- 内部「通过」要写明审的是什么、没覆盖什么。粗模预演不叫成片，也不叫 Animatic。
- 回复用中文。用户是芯片与光的行家，数字和结构必须有出处。

## 四、等着的事
**等别人的**
- ChatGPT 对 PR #3 第二轮交付的审核。
- ChatGPT 那边能不能直接下载 Drive 上的审核视频，还没有验收（用户说会装 Drive 插件后再试）。验收通过之前，不把视频交接的做法写成长期规范。

**等用户定的**（全表在 `preprod/09` 第四节、`preprod/06` 第五节、`preprod/10` 第四节）
1. 参考机型和路径：GPU 的接口 → 网卡 → 内部铜缆 → 机箱后部光口（只核了一款机型）。
2. 串化电路画在 GPU 芯片上，网卡里的第二次串化只用角注交代（Q2）；光模块以含 DSP 的单模硅光模块为例（Q4）；明暗画两级并加注（Q3）。
3. 把原稿的「跑得越快」改成「数据发得越快」。
4. 开头用哪个分镜备选、第一句怎么写；第一个机制演示在 23 秒以后接不接受。
5. S03 结尾要不要继续修到真正穿出芯片；n37 要不要。
6. 临时旁白用什么（Fish Audio 收费）；Cycles 还是 EEVEE；Remotion 是否在免费授权范围；RTX 4090 模型的来源。
7. 复盘里提的七件流程上的事（一轮任务的大小、文档文件名要不要改英文、PR #1 的云渲染工具要不要先合并，等等）。

**下一步可能做什么**（等用户或 ChatGPT 的指令，不要自己开工）
- 按审核意见修 S01–S03：S03 结尾的「一对线 → 一对凸点」、微观段偏暗、S02 在 15.2 秒的速度跳变、标签位置。
- 建 S04–S10 的预演场景，拼全片 Animatic。
- 观众（Codex）还没跑过：要先 `codex login --device-auth`，把网址和验证码发给用户。

## 五、怎么省额度（上一个对话的教训）
- **对话别开太长。** 一个阶段做完就让用户换新对话；交接写进这个文件。
- **派角色时写明模型。** 建模、合成、日常审核、监督用 Sonnet（Agent 工具的 `model: "sonnet"`）；只有事实调研、科学审查、成片前的最终审核用最强的模型。上一个对话里 Blender 和 Remotion 的角色没指定模型，全用了最强的。
- **监督每个节点开一个新的**，只给它这一轮的材料和清单的位置，不要在同一个监督身上反复续活。
- 少看大图；接触表一张小图能看清就不开大图。读 PR 正文很贵，核对链接用下面第七节的办法。

## 六、盯住派出去的东西
- 每派一个角色或后台任务，同时在后台跑 `tools/heartbeat_watch.sh <名字> <秒数> <路径…> [-- <进程关键字>]`。它退出就会叫醒主 agent。
- 任务书里要求角色每做完一轮往进度文件里写一行。
- 说「谁停了」之前先看进程和文件，没看过就说不知道。
- 角色被系统中止后不一定能续上；续不上就由主 agent 接手，并马上告诉用户。

## 七、环境：新容器里什么都要重新准备
临时目录是按会话分的，上一个对话的渲染帧、视频、Blender 都不会带过来。

| 要用的东西 | 怎么准备 |
|---|---|
| Blender 5.2.3 | 从 `https://download.blender.org/release/Blender5.2/blender-5.2.3-linux-x64.tar.xz` 下载解压。本机没有显卡，只能 Cycles CPU，只适合渲几张小静帧 |
| HDRI 和贴图 | `episodes/guanghulian/01-journey-3d/blender/fetch_assets.sh` |
| Remotion | 在 `remotion/` 里 `npm install`。浏览器用预装的 `/opt/pw-browsers/chromium`，不要让它自己下载 |
| Blender 渲好的帧 | 不在仓库里。放到 `remotion/public/frames/<镜头号>/`，锚点放 `remotion/public/anchors/`，然后 `npm run scan` |
| 预演 v1 的视频 | 母版没有保存下来。审核版四个文件在用户 Drive 的「kepu-studio_审核预览」文件夹里，直链在 PR #3 的说明里；仓库里有逐秒和对照的接触表（`previews/S01-S03_animatic_v1/`） |
| 云渲染工具 | `tools/runpod_render.py` 在 PR #1 的分支里，这个分支没有：`git fetch origin claude/bold-hypatia-1tyot4`，再 `git show origin/claude/bold-hypatia-1tyot4:tools/runpod_render.py > <工作目录>/tools/runpod_render.py`。然后 `python3 blender/cloud_stage.py <工作目录> S02,S03` 生成场景包和任务表 |

**云渲染**（规则在 `CLAUDE.md`「云 GPU 渲染怎么批」：一批预计不超过 1 美元直接跑，超过先报给用户）
- 只租 RTX 4090：`--gpu "NVIDIA GeForce RTX 4090"`。RTX 5090 上 Blender 找不到显卡，原因没查。
- 先渲两三帧，看日志里是不是 `OPTIX:NVIDIA GeForce RTX 4090`，再放整批。实测 540×960、24 采样：S02 约 3.7 秒一帧，S03 约 2.5 秒一帧；S01 没有显卡的实测数。
- 便宜的 Community Cloud 经常没有空机器，会落到 Secure Cloud（每小时约 0.89 美元），估价按这个算。
- 渲完确认 `runpod_render.py list` 是空的。

**往 Drive 传审核视频**（方案 A；用户授权只限低清审核预览）
- 文件夹「kepu-studio_审核预览」在用户已有的一个共享文件夹里，权限是继承来的「知道链接可查看」。**不改任何共享设置。** 文件夹和文件的 ID 不进仓库，用 Drive 连接器按名字找。
- 用 Drive 连接器的 `create_file`，`base64Content` 写成 `sha256:<文件的 sha256>:<绝对路径>`，`contentMimeType` 写 `video/mp4`，`disableConversionToGoogleType` 设 true。
- 每个文件约 3 MB 以内。整段压低码率一个，再按镜头分段各一个。
- 直链写法：`https://drive.usercontent.google.com/download?id=<文件 ID>&export=download&confirm=t`。传完不登录下载一次，核对 sha256。
- 规格表用 `tools/preview_manifest.py <视频> --commit <生成时的代码提交>` 生成。
- 直链和 ID 只写在 PR 里，不写进仓库的文件。

**往 PR 写东西**
- 每个链接单独成行，或者后面留一个空格。链接紧挨着标点或另一个链接会被自动包上反引号，点不了。表格的同一格里不放两个链接。
- 发完要核对。省额度的办法：`gh api -X GET search/issues -f q='repo:doityj335-prog/kepu-studio type:pr <标题里的词>' --jq '.items[] | select(.number==3) | .body'` 存成文件，数反引号和链接的个数。
- 每条评论末尾带署名行（见会话的系统说明）。

**其它**
- 这个环境连不出 SSH，只能走 HTTPS。
- 每次回合结束前，仓库里不能有没提交的改动（有个钩子会拦）。角色改到一半的文件也会被要求提交，提交说明里写明「进行中、未验收」。
- 写文件用脚本文件或带引号的写法；文档里有反引号时，不带引号的写法会把它当命令执行。

---

# 更早的交接（2026-11-10，原样保留）

上一个对话从 11-08 开到 11-10，太长了，为省额度新开一个对话。规则、决定都已经在仓库里，这里只列**进行中的事**和**新对话要知道的背景**。

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
- **现状**：真实感改造做了第一版。
  - 已做：Poly Haven HDRI 打光、倒角、程序生成的芯片版图贴图（`make_layout_texture.py`）、金属粗糙度、浅景深、淡入淡出、按屏幕字号算的 3D 标签、只在光上加辉光（AOV 遮罩）。
  - 进度图：`progress_realism_v1.jpg`。
  - 微观段（13–17.5 秒）效果不错。
- **下一步**：
  - 交换机和模块段「模型感」还重：补端口笼子开口、模块散热纹、电路板走线和焊盘，整体再调一次光；
  - 改完给用户看几张对比静帧，用户认可后再出 EEVEE 渲染包；
  - 渲染包发出前是一个审核节点。
- **素材**：
  - Poly Haven 的 HDRI 和贴图放在 `blender_test_scale/assets_dl/`（gitignore，新对话要重新下载）：
    - `studio_small_09_2k.hdr`
    - `metal_plate_rough_2k.jpg`
  - 下载地址：`https://dl.polyhaven.org/file/ph-assets/HDRIs/hdr/2k/studio_small_09_2k.hdr`、`https://dl.polyhaven.org/file/ph-assets/Textures/jpg/2k/metal_plate/metal_plate_rough_2k.jpg`。
  - 版图贴图用 `python3 make_layout_texture.py assets/chip_layout.png` 重新生成（也在 gitignore 里）。
  - 用户说过：「过程中你需要哪些素材，只管问我来要，我要的是出片质量！」已经向用户要了两张参考图：交换机 / 光模块的实拍、硅光芯片显微照，还没收到。
- **云端测试**：Blender 5.2.3 在 `/tmp/blender/blender-5.2.3-linux-x64/`，容器重启会丢，要从 download.blender.org 重新下载。云端只渲低清静帧看构图（270×480，16 采样）。
- **旧的 `render_package_win/`（v1）已作废**：审核查出端口悬空、标签太小等问题，不要再发。

## 渲染的路
- 用户的 Windows + RTX 2060：EEVEE 每帧约 2 秒，Cycles 约 30 秒。默认用 EEVEE。
  - 渲染包形式：双击 `.bat`，通过 `find_blender.cmd` 找 Blender。
- 用户准备试 **AutoDL 租卡**（RTX 4090）。
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
