@echo off
chcp 65001 >nul
cd /d "%~dp0"
call "%~dp0find_blender.cmd"
if not defined B goto fail
echo.
echo EEVEE（实时引擎）试渲两帧：第 140 帧（紫外光照射）和第 385 帧（波导亮起来），1080x1920。
echo 第一帧包含一次性的着色器编译，会慢一些；看第二帧的时间才准。
"%B%" -b --python-exit-code 1 --python "%~dp0shot_waveguide.py" -- "%~dp0preview_eevee" 1080 1920 64 --eevee --fps 30 140 385
if errorlevel 1 goto broke
if not exist "%~dp0preview_eevee\f0385.png" goto broke
echo.
echo 完成：preview_eevee 文件夹里的 f0140.png 和 f0385.png。
echo 上面 "FRAME_TIME" 两行是每帧花的时间；"EEVEE_GPU" 那行应该写着 NVIDIA。
echo 请把这个窗口截图，连同两张图一起发给 Claude。
pause
exit /b 0
:broke
echo.
echo [!] 出错了：没有生成 preview_eevee\f0385.png。请把这个窗口截图发给 Claude。
:fail
pause
exit /b 1
