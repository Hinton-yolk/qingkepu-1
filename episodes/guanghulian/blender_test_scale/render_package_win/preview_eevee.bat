@echo off
chcp 65001 >nul
cd /d "%~dp0"
call "%~dp0find_blender.cmd"
if not defined B goto fail
echo.
echo 试渲 6 帧（EEVEE，1080x1920）：0.5 秒 机房和交换机、2.8 秒 模块和手机、5.0 秒 穿过面板、7.5 秒 芯片边缘、13.3 秒 红细胞、17.5 秒 波导。
echo 第一帧含一次性的着色器编译，会慢一些；看后面几帧的 FRAME_TIME 才准。
"%B%" -b --python-exit-code 1 --python "%~dp0shot_scale.py" -- "%~dp0preview" 1080 1920 64 --fps 30 16 85 151 226 400 526
if errorlevel 1 goto broke
if not exist "%~dp0preview\f0526.png" goto broke
echo.
echo 完成：preview 文件夹里 6 张图。请把这个窗口截图和 6 张图一起发给 Claude。
pause
exit /b 0
:broke
echo.
echo [!] 出错了：请把这个窗口截图发给 Claude。
:fail
pause
exit /b 1
