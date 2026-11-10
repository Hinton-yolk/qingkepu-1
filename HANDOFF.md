# 交接（新对话先读这个）· 2026-11-10

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
- **11-10 第二个对话（用户喊了暂停）**：交换机和模块段的真实感改造第一版代码已写好（`shot_scale.py` + 新的 `make_hw_textures.py`），**渲出来的帧还没看过，也还没调光**。
  - 改了：面板冲孔、空心笼口、MPO 插头和尾套、跳线分到两侧、机柜方孔立柱、挂耳和螺丝；透明上盖下面能看到主板、交换芯片散热片、风扇、电源；上下两排端口改成对齐（原来错开半格）；手机做了圆角、金属边框、前摄开孔；模块电路板加了走线、过孔、丝印；两排金手指；DSP 改成焊球层 + 基板 + 金属盖；加了 0402 电容；光纤带落到板上（原来悬空约 0.6 mm）；V 形槽块不再陷进板里；穿过面板以后，旁边的笼子、主板、后面的连接器留在画面里。
  - 没核来源、要进 FACTS 或问用户的：QSFP-DD 两排金手指哪排短；1U 交换机的风扇和电源布局。
  - 贴图要先运行 `python3 make_hw_textures.py` 生成（在 gitignore 里）。云端 EEVEE 要先装 `libegl1 libgl1-mesa-dri`。
- **下一步**：
  - 看改动后的帧，再调一次光（第一版代码的改动见上一条）；
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
