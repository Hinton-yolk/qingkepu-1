光互连 02 上集开头 · Blender 渲染包（Windows + NVIDIA 显卡）· 2026-11-09 第二版：右边换成 USB 2.0 A 型插头（4 个触点）

【准备，只做一次】
1. 安装 Blender 4.5 LTS（免费）：https://www.blender.org/download/lts/4-5/
   选 Windows Installer，按默认位置安装（C:\Program Files\Blender Foundation\Blender 4.5\）。
2. 建议先更新 NVIDIA 显卡驱动（GeForce Experience 或 nvidia.cn 下载）。驱动太旧时 Blender 找不到显卡，会退回用 CPU，很慢。
3. 把这个文件夹解压到一个不含中文的路径，比如 C:\render\blender_render_02_opening\。

【渲染】
4. （可选）先双击 preview_frame.bat：只渲一帧，确认显卡能用。
   窗口里出现 "GPU_DEVICE OPTIX" 或 "GPU_DEVICE CUDA" 就对了；如果是 "GPU_DEVICE none"，说明没用上显卡，先更新驱动。
   看 "Time:" 那一行，就是一帧的时间；乘 248 大约就是整段的时间（RTX 显卡一般每帧几秒，整段十几到几十分钟）。
5. 双击 start_render.bat，开始渲这个镜头（只是 02 上集开头这 8.25 秒，不是整集，30 fps，1080x1920）。渲染时电脑会比较忙，窗口别关。
6. 完成后，output 文件夹里有两个文件：
   - opening.mp4（画面，没有字、没有声音，几十 MB）
   - anchors.json（每一帧插头在画面里的位置，给加字用）
   两个都发回给 Claude（聊天里上传，或放进仓库 episodes/guanghulian/02-serdes/blender_test/gpu_output/）。
   之后加大字问题、标签、字幕和配音都在云端做，不用你再操作。

【常见问题】
- 显示「没有自动找到 Blender」：按提示把 blender.exe 拖进黑窗口、按回车，之后会记住（存在 blender_path.txt 里）。
  blender.exe 在哪：桌面 Blender 图标右键 →「打开文件所在的位置」；如果桌面图标是 blender-launcher.exe 也没关系，拖进来会自动换成同一文件夹里的 blender.exe。
- 双击后窗口一闪就没了：右键 start_render.bat →「编辑」看看路径；或者把 Blender 的 blender.exe 拖进一个命令行窗口确认能打开。
- 杀毒软件拦截 .bat：选「仍要运行」。这两个 .bat 只做一件事：用 Blender 在后台运行 shot_open.py。
- shot_open.py 是整个场景（桌子、并口线、USB-C、灯光、镜头）的代码，Claude 写的，不需要你改。
