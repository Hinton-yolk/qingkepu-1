@echo off
chcp 65001 >nul
cd /d "%~dp0"
call "%~dp0find_blender.cmd"
if not defined B goto fail
echo.
echo 先渲一帧看看（第 120 帧），确认显卡能用、大约多久一帧。
"%B%" -b --python "%~dp0shot_open.py" -- "%~dp0preview" 1080 1920 128 --gpu --fps 30 120
echo.
echo 完成：preview 文件夹里的 f0120.png。上面 "Time:" 那一行就是这一帧花的时间。
pause
exit /b 0
:fail
pause
exit /b 1
