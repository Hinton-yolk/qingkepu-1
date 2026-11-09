@echo off
chcp 65001 >nul
cd /d "%~dp0"
call "%~dp0find_blender.cmd"
if not defined B goto fail
echo.
echo 开始渲染：02 上集开头测试镜头（只有开头这 8.25 秒），1080x1920，30 fps，约 248 帧。
echo 窗口里出现 GPU_DEVICE OPTIX（或 CUDA）就说明在用显卡。中途别关这个窗口。
echo.
"%B%" -b --python "%~dp0shot_open.py" -- "%~dp0output" 1080 1920 128 --gpu --fps 30 --video
echo.
echo ===== 完成 =====
echo 结果在 output 文件夹：opening.mp4 和 anchors.json，两个都发回给 Claude。
pause
exit /b 0
:fail
pause
exit /b 1
