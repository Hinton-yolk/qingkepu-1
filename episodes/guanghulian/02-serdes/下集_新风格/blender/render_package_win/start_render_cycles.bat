@echo off
chcp 65001 >nul
cd /d "%~dp0"
call "%~dp0find_blender.cmd"
if not defined B goto fail
echo.
echo 渲正式版（r2 Epic 化 + Cycles 显卡，64 采样）：光互连 02 下集开头两段 + 5 张背景。
echo   A 段 72 帧（手机）、B 段 120 帧（走线）、5 张背景（1188x2112）。预计 2–3 小时，可以放一整晚。
echo   中途关掉窗口也没关系：再双击一次，已经渲好的会跳过，接着渲。
echo.
echo   放一整晚前请确认：1) 不要合上笔记本盖子；2) 设置 - 系统 - 电源：接通电源时「睡眠」设成「从不」；
echo   3) 早上看到没渲完（或者 Windows 更新重启了），再双击一次就会接着渲。
"%B%" -b --python-exit-code 1 --python "%~dp0shot_open.py" -- A "%~dp0output" 1080 1920 64 cycles gpu look=r2 seq
if errorlevel 1 goto broke
"%B%" -b --python-exit-code 1 --python "%~dp0shot_open.py" -- B "%~dp0output" 1080 1920 64 cycles gpu look=r2 seq
if errorlevel 1 goto broke
for %%V in (side count close wide) do (
  "%B%" -b --python-exit-code 1 --python "%~dp0shot_open.py" -- B "%~dp0output\stills" 1188 2112 64 cycles gpu look=r2 view=%%V noband=1
  if errorlevel 1 goto broke
)
"%B%" -b --python-exit-code 1 --python "%~dp0shot_open.py" -- B "%~dp0output\stills" 1188 2112 64 cycles gpu look=r2 view=rx xray=1 noband=1
if errorlevel 1 goto broke
echo.
echo 把两段序列编码成 MP4（编码前会核对帧数齐不齐）……
"%B%" -b --factory-startup --python-exit-code 1 --python "%~dp0encode_mp4.py" -- "%~dp0output\A" "%~dp0output\A.mp4" 30 72
if errorlevel 1 goto broke
"%B%" -b --factory-startup --python-exit-code 1 --python "%~dp0encode_mp4.py" -- "%~dp0output\B" "%~dp0output\B.mp4" 30 120
if errorlevel 1 goto broke
for %%F in (side_normal_noband count_normal_noband close_normal_noband wide_normal_noband rx_normal_xray_noband) do (
  if not exist "%~dp0output\stills\B_%%F.png" goto missing
  if not exist "%~dp0output\stills\B_%%F.json" goto missing
)
echo.
echo ===== 完成 =====
echo 请发回这三样：output\A.mp4、output\B.mp4、output\stills 文件夹（5 张图 + 5 个 json，压成一个 zip）。
echo output\A 和 output\B 两个文件夹里的 PNG 很大，不用发。
pause
exit /b 0
:missing
echo.
echo [!] 背景图不全：请再双击一次 start_render_cycles.bat 补渲，还不行就截图发给 Claude。
pause
exit /b 1
:broke
echo.
echo [!] 渲染出错了：请把这个窗口截图发给 Claude。
:fail
pause
exit /b 1
