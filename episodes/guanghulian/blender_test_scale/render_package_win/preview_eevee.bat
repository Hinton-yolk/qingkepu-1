@echo off
chcp 65001 >nul
cd /d "%~dp0"
call "%~dp0find_blender.cmd"
if not defined B goto fail
echo.
echo 试渲 5 帧（EEVEE，1080x1920）：0.5 秒 交换机、5.5 秒 模块内部、9.5 秒 光纤和头发、14.5 秒 红细胞、17.5 秒 波导。
echo 第一帧含一次性的着色器编译，会慢一些；看后面几帧的 FRAME_TIME 才准。
"%B%" -b --python-exit-code 1 --python "%~dp0shot_scale.py" -- "%~dp0preview" 1080 1920 64 --fps 30 16 166 286 436 526
if errorlevel 1 goto broke
if not exist "%~dp0preview\f0526.png" goto broke
echo.
echo 完成：preview 文件夹里 5 张图。请把这个窗口截图和 5 张图一起发给 Claude。
pause
exit /b 0
:broke
echo.
echo [!] 出错了：请把这个窗口截图发给 Claude。
:fail
pause
exit /b 1
