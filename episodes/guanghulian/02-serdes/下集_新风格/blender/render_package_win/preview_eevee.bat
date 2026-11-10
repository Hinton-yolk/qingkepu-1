@echo off
chcp 65001 >nul
cd /d "%~dp0"
call "%~dp0find_blender.cmd"
if not defined B goto fail
echo.
echo 试渲（EEVEE）：B 段 2 帧放在同一次里渲，看第 2 帧的 FRAME_TIME 才准（第 1 帧含着色器编译）。
echo 另外 A 段 1 帧、背景 1 张，只用来看画面。
"%B%" -b --python-exit-code 1 --python "%~dp0shot_open.py" -- B "%~dp0preview" 1080 1920 32 60 110
if errorlevel 1 goto broke
"%B%" -b --python-exit-code 1 --python "%~dp0shot_open.py" -- A "%~dp0preview" 1080 1920 32 40
if errorlevel 1 goto broke
"%B%" -b --python-exit-code 1 --python "%~dp0shot_open.py" -- B "%~dp0preview" 1188 2112 32 view=side noband=1
if errorlevel 1 goto broke
echo.
echo 完成：preview 文件夹里 4 张图。请把这个窗口截图（要看得见 FRAME_TIME 和 GPU 那几行）和 4 张图一起发给 Claude。
echo B 段第 2 帧（f0110）超过约 20 秒的话，先别跑正式版，告诉 Claude。
pause
exit /b 0
:broke
echo.
echo [!] 出错了：请把这个窗口截图发给 Claude。
:fail
pause
exit /b 1
