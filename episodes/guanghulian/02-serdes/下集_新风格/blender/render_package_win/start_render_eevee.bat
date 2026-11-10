@echo off
chcp 65001 >nul
cd /d "%~dp0"
call "%~dp0find_blender.cmd"
if not defined B goto fail
echo.
echo 渲正式版：光互连 02 下集开头两段 + 5 张背景。
echo   A 段 72 帧（手机）、B 段 120 帧（走线）、5 张背景（1188x2112），共 197 张。先跑 preview_eevee.bat 看每帧多久。
echo   中途关掉窗口也没关系：再双击一次，已经渲好的会跳过，接着渲（没渲完整的帧会自动删掉重渲）。
"%B%" -b --python-exit-code 1 --python "%~dp0shot_open.py" -- A "%~dp0output" 1080 1920 32 seq
if errorlevel 1 goto broke
"%B%" -b --python-exit-code 1 --python "%~dp0shot_open.py" -- B "%~dp0output" 1080 1920 32 seq
if errorlevel 1 goto broke
for %%V in (side count close wide) do (
  "%B%" -b --python-exit-code 1 --python "%~dp0shot_open.py" -- B "%~dp0output\stills" 1188 2112 32 view=%%V noband=1
  if errorlevel 1 goto broke
)
"%B%" -b --python-exit-code 1 --python "%~dp0shot_open.py" -- B "%~dp0output\stills" 1188 2112 32 view=rx xray=1 noband=1
if errorlevel 1 goto broke
echo.
echo 把两段序列编码成 MP4（用 Blender 自带的编码，不用另装软件；编码前会核对帧数齐不齐）……
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
echo [!] 背景图不全（stills 文件夹里少了图或 json）：请再双击一次 start_render_eevee.bat 补渲，还不行就截图发给 Claude。
pause
exit /b 1
:broke
echo.
echo [!] 渲染出错了：请把这个窗口截图发给 Claude。
:fail
pause
exit /b 1
