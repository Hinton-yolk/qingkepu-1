光互连 02 下集 · 新画面版 · EEVEE 渲染包（正式版开头两段 + 5 张背景）· 2026-11-10

0. 需要 Blender 5.x（官网 blender.org/download 下载；和云端测试用的 5.2.3 一致最好）。
   第一次运行会让你把 blender.exe 拖进窗口；也可以把测试镜头三渲染包里的 blender_path.txt 复制到这个文件夹，就不用再拖。
1. 解压到不含中文的路径（例如 D:\Render\ep02x\）。
2. 渲之前：插上电源；Windows「设置 → 系统 → 屏幕 → 显示卡」里把 blender.exe 设成「高性能（NVIDIA）」；笔记本垫高散热。
3. 先双击 preview_eevee.bat：试渲 4 张，看 B 段第 2 帧的 FRAME_TIME（第 1 帧含着色器编译，不准）。
   把窗口截图和 preview 里的 4 张图发给 Claude。B 段第 2 帧超过约 20 秒，先别跑正式版，告诉 Claude。
4. 速度没问题就双击 start_render_eevee.bat：A 段 72 帧 + B 段 120 帧 + 5 张背景，共 197 张，
   预计 45–60 分钟（以试渲第 2 帧的耗时为准）。中途停了可以再双击，已渲好的会跳过。
5. 渲完会自动编码成 output\A.mp4 和 output\B.mp4。发回：A.mp4、B.mp4、stills 文件夹（压成 zip，约几十 MB）。
   output\A、output\B 里的 PNG 很大（几百 MB），不用发。

这一版画的是：桌上的手机（消息变乱码）→ 信号飞出去 → AI 服务器主板上的一对差分走线（金色光带是示意：两根线之间的电压差）。
背景图不带光带和灰尘：中间讲解段的光带动画、灰尘、字幕、五站条、配乐都在云端合成。
素材：assets_dl 里的 HDRI 来自 Poly Haven（CC0）；assets 里的图是脚本生成的。
