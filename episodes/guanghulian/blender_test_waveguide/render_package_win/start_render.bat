@echo off
chcp 65001 >nul
cd /d "%~dp0"
call "%~dp0find_blender.cmd"
if not defined B goto fail
echo.
echo 开始渲染：测试镜头二「硅光波导是怎么刻出来的」，14 秒，1080x1920，30 fps，共 420 帧。
echo 窗口里出现 GPU_DEVICE OPTIX（或 CUDA）就说明在用显卡。中途别关这个窗口。
echo.
"%B%" -b --python-exit-code 1 --python "%~dp0shot_waveguide.py" -- "%~dp0output" 1080 1920 128 --gpu --fps 30 --video
if errorlevel 1 goto broke
if not exist "%~dp0output\waveguide.mp4" goto broke
echo.
echo ===== 完成 =====
echo 结果在 output 文件夹：waveguide.mp4 和 anchors.json，两个都发回给 Claude。
pause
exit /b 0
:broke
echo.
echo [!] 渲染出错了：没有生成 output\waveguide.mp4。请把这个窗口截图发给 Claude。
:fail
pause
exit /b 1
