光互连 02 下集 · 正式渲染包 v4（r2 Epic 化 + Cycles 显卡）· 2026-11-10

1. 解压到不含中文的路径（例如 D:\Render\ep02x_v4\）。把上一个包里的 blender_path.txt 复制过来，就不用再拖 blender.exe。
2. 插上电源，笔记本垫高散热。双击 start_render_cycles.bat，放一整晚：A 段 72 帧 + B 段 120 帧 + 5 张背景，
   用显卡（OptiX）、64 采样，预计 2–3 小时。中途停了可以再双击，已渲的会跳过。
3. 渲完会自动编码成 output\A.mp4 和 output\B.mp4。发回：A.mp4、B.mp4、stills 文件夹（压成 zip）。
   output\A、output\B 里的 PNG 很大，不用发。

这一版：用户选的 r2（Epic 化）+ Cycles。主板铺到远处长满器件；暖色逆光从散热器鳍片缝隙漏出成光柱；远处器件上有小状态灯；
B 段相机水平（竖线不歪）；信号是金色。中间讲解段的光带动画、灰尘、字幕、五站条、配乐、调色都在云端合成。
