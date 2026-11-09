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
echo.
echo 开始渲染：02 上集开头测试镜头，1080x1920，30 fps，约 248 帧。
echo 窗口里出现 GPU_DEVICE OPTIX（或 CUDA）就说明在用显卡。中途别关这个窗口。
echo.
"%B%" -b --python shot_open.py -- "%~dp0output" 1080 1920 128 --gpu --fps 30 --video
echo.
echo ===== 完成 =====
echo 结果在 output 文件夹：opening.mp4 和 anchors.json，两个都发回给 Claude。
pause
