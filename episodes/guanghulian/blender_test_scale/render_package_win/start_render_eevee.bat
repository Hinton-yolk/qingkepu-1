@echo off
chcp 65001 >nul
cd /d "%~dp0"
call "%~dp0find_blender.cmd"
if not defined B goto fail
echo.
echo 渲整段：测试镜头三「光在芯片里走的路有多细？」，18 秒，1080x1920，30 fps，540 帧，EEVEE。
echo 先跑 preview_eevee.bat 看每帧多久：乘 540 就是整段时间。
echo 中途关掉窗口也没关系：再双击一次，已经渲好的帧会跳过，接着渲。
"%B%" -b --python-exit-code 1 --python "%~dp0shot_scale.py" -- "%~dp0output" 1080 1920 64 --fps 30 --video
if errorlevel 1 goto broke
if not exist "%~dp0output\frames\f0540.png" goto broke
echo.
echo 帧渲完了，正在编码成 scale.mp4 ……
"%B%" -b --factory-startup --python-exit-code 1 --python "%~dp0encode_mp4.py" -- "%~dp0output\frames" "%~dp0output\scale.mp4" 30 540
if errorlevel 1 goto broke
if not exist "%~dp0output\scale.mp4" goto broke
echo.
echo ===== 完成 =====
echo 结果在 output 文件夹：scale.mp4 和 anchors.json，两个都发回给 Claude（frames 文件夹很大，不用发）。
pause
exit /b 0
:broke
echo.
echo [!] 渲染出错了：请把这个窗口截图发给 Claude。
:fail
pause
exit /b 1
