@echo off
chcp 65001 >nul
cd /d "%~dp0"
call "%~dp0find_blender.cmd"
if not defined B goto fail
echo.
echo 渲正式版：光互连 02 下集开头两段 + 5 张背景。
echo   A 段 72 帧（手机）、B 段 120 帧（走线）、5 张背景（1188x2112）。先跑 preview_eevee.bat 看每帧多久。
echo   中途关掉窗口也没关系：再双击一次，已经渲好的帧会跳过，接着渲。
"%B%" -b --python-exit-code 1 --python "%~dp0shot_open.py" -- A "%~dp0output" 1080 1920 32 seq
if errorlevel 1 goto broke
"%B%" -b --python-exit-code 1 --python "%~dp0shot_open.py" -- B "%~dp0output" 1080 1920 32 seq
if errorlevel 1 goto broke
for %%V in (side count close wide) do (
  if not exist "%~dp0output\stills\B_%%V_normal_noband.png" "%B%" -b --python-exit-code 1 --python "%~dp0shot_open.py" -- B "%~dp0output\stills" 1188 2112 32 view=%%V noband=1
)
if not exist "%~dp0output\stills\B_rx_normal_xray_noband.png" "%B%" -b --python-exit-code 1 --python "%~dp0shot_open.py" -- B "%~dp0output\stills" 1188 2112 32 view=rx xray=1 noband=1
echo.
echo ===== 完成 =====
echo 请把整个 output 文件夹压缩成一个 zip 发回给 Claude（A、B 两个文件夹的 PNG + stills 里的图和 json）。
pause
exit /b 0
:broke
echo.
echo [!] 渲染出错了：请把这个窗口截图发给 Claude。
:fail
pause
exit /b 1
