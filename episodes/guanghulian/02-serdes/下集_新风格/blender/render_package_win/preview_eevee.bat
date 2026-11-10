@echo off
chcp 65001 >nul
cd /d "%~dp0"
call "%~dp0find_blender.cmd"
if not defined B goto fail
echo.
echo 试渲 3 帧（EEVEE，1080x1920）：手机变乱码、走线、一张背景。看每帧的 FRAME_TIME。
echo 第一帧含一次性的着色器编译，会慢一些；看后两帧才准。
"%B%" -b --python-exit-code 1 --python "%~dp0shot_open.py" -- A "%~dp0preview" 1080 1920 32 40
if errorlevel 1 goto broke
"%B%" -b --python-exit-code 1 --python "%~dp0shot_open.py" -- B "%~dp0preview" 1080 1920 32 110
if errorlevel 1 goto broke
"%B%" -b --python-exit-code 1 --python "%~dp0shot_open.py" -- B "%~dp0preview" 1188 2112 32 view=side noband=1
if errorlevel 1 goto broke
echo.
echo 完成：preview 文件夹里 3 张图。请把这个窗口截图（要看得见 FRAME_TIME 和 GPU 那几行）和 3 张图一起发给 Claude。
pause
exit /b 0
:broke
echo.
echo [!] 出错了：请把这个窗口截图发给 Claude。
:fail
pause
exit /b 1
