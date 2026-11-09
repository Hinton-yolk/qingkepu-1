@echo off
chcp 65001 >nul
cd /d "%~dp0"
set "B="
if exist "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe" set "B=C:\Program Files\Blender Foundation\Blender 4.5\blender.exe"
if not defined B for /d %%D in ("C:\Program Files\Blender Foundation\Blender*") do if exist "%%D\blender.exe" set "B=%%D\blender.exe"
if not defined B for /f "delims=" %%P in ('where blender 2^>nul') do set "B=%%P"
if not defined B (
  echo [!] 没找到 Blender。请先安装 Blender 4.5 LTS（默认安装位置），再双击本文件。
  echo     下载：https://www.blender.org/download/lts/4-5/
  pause
  exit /b 1
)
echo 使用的 Blender：%B%
echo 先渲一帧看看（第 120 帧），用来确认显卡能用、大约多久一帧。
"%B%" -b --python shot_open.py -- "%~dp0preview" 1080 1920 128 --gpu --fps 30 120
echo.
echo 完成：preview\f0120.png。上面 "Time:" 那一行就是这一帧花的时间。
pause
