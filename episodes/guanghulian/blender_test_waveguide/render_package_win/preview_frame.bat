@echo off
chcp 65001 >nul
cd /d "%~dp0"
call "%~dp0find_blender.cmd"
if not defined B goto fail
echo.
echo 先渲一帧看看（第 385 帧，波导亮起来那一刻），确认显卡能用、大约多久一帧。
"%B%" -b --python-exit-code 1 --python "%~dp0shot_waveguide.py" -- "%~dp0preview" 1080 1920 64 --gpu --fps 30 385
if errorlevel 1 goto broke
if not exist "%~dp0preview\f0385.png" goto broke
echo.
echo 完成：preview 文件夹里的 f0385.png。上面 "Time:" 那一行就是这一帧花的时间。
pause
exit /b 0
:broke
echo.
echo [!] 出错了：没有生成 preview\f0385.png。请把这个窗口截图发给 Claude。
:fail
pause
exit /b 1
