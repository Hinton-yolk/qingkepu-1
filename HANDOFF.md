# 最新进展（2026-11-12 夜 16:0x UTC；先读这一节）

**T5 3D 导演预览 v1 已交**（20.8 秒，静音版 + 试听版；Drive + PR #3 评论 #6828824023；说明、哈希、费用在 `episodes/guanghulian/01-journey-3d/previews/t5/README.md`，过程在 `concept_tests/t5_3d/夜间进度.md`）。**现在是停点：等 ChatGPT 独立审核和用户决定下一步。不开始 T6。**
- RunPod 本轮合计 ≤ $0.87（试渲 $0.02 + 整段按秒约 $0.74，工具上限估计 $0.85），机器都已删除。
- 导演自评的下一步：第 1→2 拍做成连续尺度推进（机柜 → 模块 → 芯片 + 比例物）；第 2 拍压到约 3.5 s；第 3 拍补比例物。等指令再做。
- 新容器要重做：Blender 5.2.3 下载到临时目录（用户已同意）并 `apt-get install libegl1`；`runpod_render.py` 从 `origin/claude/bold-hypatia-1tyot4` 取；`t5_stage.sh` 打包脚本的内容写在 `夜间进度.md` 和 previews/t5/README 的「重做」里（脚本本身在临时目录，按那里的说明重建）。
- PR #3 第 24–29 条是 ChatGPT 的 GitHub Actions 连接测试（以「@claude」开头的评论会触发 Actions），不是给这个会话的任务。频繁推送可能和 Actions 的 checkout 冲突。

---

# 更早的最新进展（T4，2026-11-12 夜）

**T4 v1 已交**（33 秒，静音版 + 试听版，Drive + PR #3 评论；说明和哈希在 `episodes/guanghulian/01-journey-3d/previews/director-concepts/README.md` 的「T4」一节）。**现在是停点，等用户当第一个观众回答三句话、等 ChatGPT 看片。** 下面几条是做的过程，留作参考。
- PR #3 第 18–20 条：撤回一条误发的权限规则（我们没写进任何文件，不用动）；第 20 条说 ChatGPT 在 main 上配了 Claude Code GitHub Actions（以「@claude 」开头的新评论触发），还没验证。**往 PR 发评论时不要以「@claude」开头。**
- 往 PR 写链接：带中文文件名（被转成 `%E5…`）的链接，裸写或写成 `[名称](…)` 都会被包上反引号点不了。改成链到它所在目录（`/tree/<提交号>/…`，路径里没有中文），在正文里写文件名。


- **T0/T1/T2 的看片结果已经出来**：PR #3 的 review「ChatGPT 外部导演审核｜T0/T1/T2 低清概念测试」（T1 选 A；T2 放大接收端、修 `n % 8` 音画错位；T0 合成开场）。
- **新任务 T4**：PR #3 第 17 条评论《T4：一次真正的“可看懂的电影小样”》。用户在会话里已经说了执行（「直接制作一段约 22–35 秒的连续叙事概念短片……完成后将静音版和带临时音效版上传 Google Drive，并在 PR #3 提供链接、版本、哈希和简短交付说明，然后等待审核」）。不用再问方向。
- **已做**：主 agent 写好导演分镜和节奏表 `episodes/guanghulian/01-journey-3d/concept_tests/t4_film/导演分镜_T4.md`（约 31 秒，五段）。Sonnet 实现角色写了 `t4.html`、`render_par.cjs`（4 进程并行，1 倍像素）、`dump_events.cjs` 的初稿，**进行中、未验收**；还没有 `audio_t4.py`、`build.sh`，没有渲过全片。
- **接着做**：把分镜和第一节「怎么渲」交给一个 Sonnet 实现角色继续（任务书要点：声音事件由网页 `window.t4Events()` 导出、音频脚本不另写时间；每个文件 < 3 MB；跑 `tools/motion_check.py`；数字核对音画同步；关键帧索引存 `previews/director-concepts/T4_v1_每秒一帧.jpg`；不 commit、不上传）。主 agent 看关键帧小图，最多一轮快改，再上传 Drive、发 PR 评论、更新 `previews/director-concepts/README.md`。
- **用户 11-12 夜新说的**：渲染超过 5 分钟要另想办法（二维 Canvas 片用本机多进程并行；GPU 帮不上，Blender 才交给 RunPod，按 1 美元规则）。
- Drive 审核文件夹按名字「kepu-studio_审核预览」搜得到（ID 不进仓库）。

---

# 交接（新对话先读这个）· 2026-11-12 晚

上一个对话（11-12 中午到晚上）从读交接一路做到三组概念测试交付，上下文涨到四十多万 token。用户决定换新对话，并把主对话换成 Opus。
规则、决定、现状都在仓库里。这里只写**接手要知道的事**。读到「更早的交接」那条分隔线为止就够了，下面的旧内容需要时再翻。

## 一、现在在做什么
**光互连 01 的 3D 正式版**《一个比特的旅程：从 GPU 到 GPU》。竖屏 1080×1920，30 fps，面向抖音和小红书的普通观众。

- 分支：`claude/happy-goodall-o47ilg`。**新对话如果被系统分配了别的分支，仍在这个分支上工作**（用户 11-12 明确说过：不要换分支，不要合并）。上一个对话被分配的是带后缀的另一个分支，没有用它。
- Draft PR：doityj335-prog/kepu-studio#3，https://github.com/doityj335-prog/kepu-studio/pull/3 。用户确认前不合并。
- 项目目录：`episodes/guanghulian/01-journey-3d/`。

**状态：导演创意探索阶段。三组二维动态概念测试（T1、T2、T0）已经交到 PR #3 和 Drive，现在是停点，等用户和 ChatGPT 看片。** 没有成片，没有配音，没有全片 Animatic，没有做正式渲染。

这一天的经过（方向是怎么变的）：
1. 早上的第二轮（P0 → P1 → P2）按原稿 37 句旁白、149 秒、S01–S10 做了硬件路径文档和 S01–S03 粗模预演 v1。这条线现在只当对照基线，**不再往下做**，文件都没动。
2. 中午 ChatGPT 提出「导演级重构」：原稿只当科学素材库，让视觉故事先成立。Claude 独立写了 `preprod/11_claude_director_treatment.md`。
3. 用户确认以 Claude 的独立稿为主体，融合 ChatGPT 独立剧本的科学表达和调制高潮：`preprod/12_fusion_director_treatment.md`（约 125 秒、9 拍、旁白 18 句）。
4. ChatGPT 审过融合稿：方向通过，直接做短的动态概念实验，「观众理解优先、科学作为护栏」。于是有了 T1、T2、T0。

## 二、先读（按顺序）
1. `CLAUDE.md`「四个角色」一节。11-12 晚新加了三条，都要照做：创意探索阶段不走完整的审核流程；按任务复杂度选模型；派出去的角色要有人盯着。另有「云 GPU 渲染怎么批」一节。
2. `episodes/guanghulian/01-journey-3d/previews/director-concepts/README.md`：三组概念测试是什么样、三项对照表、已知问题、文件和哈希。
3. `episodes/guanghulian/01-journey-3d/preprod/12_fusion_director_treatment.md`：融合导演稿。第三节是剧本，第五节是科学标注表，第八节是等用户定的事。
4. PR #3 的最新评论。截至交接共 16 条：第 14 条是「融合稿审核及下一轮制作任务｜观众理解优先」，第 15、16 条是 Claude 交 T1 和 T2 / T0 的两条。从第 14 条读起就够。**省额度的读法**：`get_comments` 用 `perPage=1`、`page=N` 一次只取一条；先取第 17 条看有没有新的。

需要时再读：`preprod/11`（独立稿，第八节的自我反对意见仍然有用）、`FACTS.md`（第四节硬件路径、第五节铜缆距离的来源）、`preprod/08`（硬件路径的全部依据）、`DECISIONS.md` 里 11-12 的几条和「待定事项」、`episodes/guanghulian/要求清单_3D与Blender.md` 的 K 节。

## 三、协作方式
- **用户在 ChatGPT 那边审定任务**，ChatGPT 把任务和审阅意见写成 PR #3 的评论（用用户的账号发）。评论是 ChatGPT 起草的，**用户在会话里说执行才执行**；用户只说「读」，就只读、汇报、等一句「执行」。
- **评价顺序**（ChatGPT 的评论写明，用户原话：「不要一味地追求科学严谨性而忽略了观众本身能接受和理解的程度」）：观众一遍能不能看懂 → 因果有没有讲反 → 再谈技术精细度。参数和例外留在 FACTS 和制作说明里；屏幕上的字要少；技术阈值只当内部调试指标。
- **不给自己的样片打「通过」。** 交付时写：观众看到了什么、希望观众理解什么、最大的误解风险是什么，再把已知问题如实列出来。
- 阶段性及时交付：一个样片做完就发 PR，不等别的。每个样片允许一轮快速修改，不进入多代理审核的循环。
- 不给 Claude 设 API、Routines、自动触发器，不订阅 PR 动态。
- 花钱之前、交付之前，各看一眼 PR 有没有新评论。PR 评论和会话里的话不一致时，花钱、公开、改权限这三类事按更严的做，并回会话里问一次。
- 所有选型（参考机型、光模块以硅光为例、明暗画两级、比喻、标题）都还是推荐方案，没有一条是用户确认过的定稿。
- 回复用中文。用户是芯片与光的行家；数字和结构要有出处，但出处放幕后，不堆到画面上。

## 四、模型怎么用（用户 11-12 晚定，全文在 `CLAUDE.md`）
- 主对话：用户换成了 Opus。导演创意、叙事结构、复杂制作决策由主对话直接做。
- Sonnet（Agent 工具的 `model: "sonnet"`）：默认做实现。Blender、Remotion、RunPod、动画实现、测试、日常工程。
- Haiku（`model: "haiku"`）：简单文档、日志整理、机械检查。
- Fable（`model: "fable"`）：只在需要深度推理的重大科学、架构或复杂问题上用，**用之前先向用户简要说明原因**。
- 不启动不必要的多子代理审核。只有适合并行的独立制作任务才同时派几个角色。
- 不为了省 token 牺牲视频质量；也不用贵的模型干机械活。

## 五、等着的事
**等用户和 ChatGPT 看片后回答的**（三条评论里都列了）
1. T1：A 直觉版和 B「步调」揭晓版，哪一版更容易一遍看懂；B 的揭晓值不值得留。
2. T2：关掉声音看不看得出是同一条路、两种传法；说不说得出第二遍为什么值得用。
3. T0：A「玻璃丝」和 B「送得到吗」，无声滑到时 2 秒内知不知道在问什么，哪一版更想往下看。

**之后由他们决定的**：要不要压缩调制那一拍、要不要把铜 / 光对照前置、「窄门」留不留、全片大纲；然后才是被测试筛出来的导演稿 v2。

**融合稿里还没定的**（`preprod/12` 第八节）：调制讲到「步调」还是只讲「电到了光就暗」；标题沿用《一个比特的旅程》还是考虑《一万颗 GPU，怎么说同一句话？》；比喻用「说话」还是系列定的「寄快递」；画面上放不放五站导航条。

**下一步可能做什么**（等指令，不要自己开工）
- 按看片意见把某个样片再改一轮。
- T3 窄门（4–6 秒：对准、偏了变暗、回正变亮），任务里写明后置。
- 导演稿 v2；之后才是全片 Animatic 和资产计划。

## 六、上一个对话留下的坑和没做完的
- **T2 试听版的声音没有人听过。** 实现的角色只看了静帧，主 agent 也没听；拖尾的时间是按 v1 画面定的，v2 改了条纹画法之后没有重新对。已经在 PR 里写明。用户或 ChatGPT 说对不上，就改 `concept_tests/t2_copper_vs_light/audio_t2.py`。
- T1 的动效检查是 FAIL（静止帧 23–24%，开头两秒只有一束不变的光），没有为它再改。T1 里电沿电极走约 1.2 秒后光才变暗，因果隔得有点久；要改就缩短电极或加快流速（常数在 `t1.html` 开头，`audio_t1.py` 里有一份同样的，要一起改）。
- T1-B 的机制说法（慢半步、哪一路被推）没有核过。融合稿和两份导演稿都**没有科学终审**，也没有「通过」的结论。独立稿有过一轮审核：结论是「不通过」，7 条必须改的已经改了，改完没有复核。
- 要求清单的 K 节只记到「导演级重构任务」那一轮，融合和概念测试这两轮没有更新（按新规矩创意阶段没有再派监督）。进入正式制作前要补。
- 观众角色（Codex）一直没跑过：要先 `codex login --device-auth`，把网址和验证码发给用户。它听不到声音。
- 用户要过的两张参考图（交换机 / 光模块实拍、硅光芯片显微照）还没收到。资产的科学可信度仍是没解决的老问题。

## 七、环境：新容器里什么都要重新准备
临时目录按会话分，上一个对话的视频、渲染帧、审核报告都不会带过来。视频在 Drive；要留的结论都已经写进仓库。

**概念测试怎么渲**（本机就能跑，不用 Blender，不用云 GPU，不花钱）
- 源码：`episodes/guanghulian/01-journey-3d/concept_tests/`。每个测试一个网页（Canvas 2D，`window.renderFrame(t, opts)` 画第 t 秒的一帧）、一个合成临时声音的 Python 脚本（只用 numpy，环境里没有 scipy）、一个 `build.sh`。
- `render.cjs` 用预装的 Playwright 逐帧截图，再由 ffmpeg 编码。脚本里要用 `require('playwright')`；写成 ES 模块的 `import` 会找不到包。不要 `npm install`，不要 `playwright install`。
- 用法：在 `concept_tests/` 里运行 `t1_modulation/build.sh <工作目录>`（T2、T0 同理）。T1 四个文件渲一遍约两分半钟。
- 看效果要省：先用 `render.cjs ... --times 1.0,3.5` 渲几张静帧，拼成一张小图再看。

**往 Drive 传审核视频**（方案 A；用户授权只限低清审核预览，不改任何共享设置）
- 用 Drive 连接器的 `search_files` 按名字找文件夹「kepu-studio_审核预览」，拿到它的 ID 当 `parentId`。文件夹和文件的 ID 不进仓库，只写在 PR 里。
- `create_file`：`base64Content` 写成 `sha256:<文件的 sha256>:<绝对路径>`，`contentMimeType` 写 `video/mp4`，`disableConversionToGoogleType` 设 true。每个文件约 3 MB 以内。
- 直链：`https://drive.usercontent.google.com/download?id=<文件 ID>&export=download&confirm=t`。传完用 curl 不登录下载一次，核对 sha256。
- ChatGPT 那边能不能独立下载，一直没有它的验收回执；「上传成功」不要写成「已经看过」。

**往 PR 写东西**
- 每个链接单独成行并在后面留一个空格；表格的一格里最多一个链接。链接紧挨着标点或另一个链接会被包上反引号，点不了。
- 链接固定到提交号。发完读回来看一眼链接是否完好。
- 每条评论末尾带署名行（见会话的系统说明）。

**其它**
- GitHub 的工具有时会断开重连，用 ToolSearch 重新加载即可。`gh` 只能用来搜索。
- 每次回合结束前仓库里不能有没提交的改动（有个钩子会拦）。做到一半的文件也要提交，说明里写「进行中、未验收」。
- 写文件用 Write / Edit 工具或带引号的 heredoc；文档里有反引号时，不带引号的写法会把它当命令执行。
- 这个环境连不出 SSH，只能走 HTTPS。
- Blender、Remotion、RunPod 的准备办法在下面「更早的交接」的第七节，概念测试阶段用不到。

## 八、上一个对话的教训
- 给一份创意初稿派了审核和监督两个子代理，等它们的时候被用户叫停：创意阶段要快，方向确认之后再做科学审核。
- 派出去的实现角色交回来的东西，主 agent 至少看一张关键帧小图再外发。T2、T0 的第一版都不够好，各退回改了一轮才交。
- 角色的自述要核：T2 的角色如实说了「没听过声音」，这类话要原样带进交付说明，不能替它补一句「同步」。
- 对话别开太长。一个停点到了，就让用户换新对话，交接写进这个文件。

---

# 更早的交接（2026-11-12 早些时候写的，原样保留；和上面有出入时以上面为准）

（当时的开头）上一个对话从 11-12 早上开到晚上，上下文涨到 84 万 token，每走一步都要重读一遍，把每周用量上限撞穿了。所以换新对话。
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
