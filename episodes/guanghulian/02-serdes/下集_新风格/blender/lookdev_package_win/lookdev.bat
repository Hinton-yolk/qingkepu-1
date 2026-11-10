@echo off
chcp 65001 >nul
cd /d "%~dp0"
call "%~dp0find_blender.cmd"
if not defined B goto fail
echo.
echo 质感样张：同一画面用 EEVEE 和 Cycles（显卡）各渲一遍，看哪个不塑料、各要多久。
echo 每个引擎渲 B 段两帧（第 45、120 帧）+ A 段一帧（第 40 帧）。看 FRAME_TIME：B 段第 2 帧才准。
echo.
echo ===== 1/4  EEVEE：B 段 =====
"%B%" -b --python-exit-code 1 --python "%~dp0shot_open.py" -- B "%~dp0lookdev\eevee" 1080 1920 32 45 120
if errorlevel 1 goto broke
echo ===== 2/4  EEVEE：A 段 =====
"%B%" -b --python-exit-code 1 --python "%~dp0shot_open.py" -- A "%~dp0lookdev\eevee" 1080 1920 32 40
if errorlevel 1 goto broke
echo ===== 3/4  Cycles（显卡）：B 段 =====
"%B%" -b --python-exit-code 1 --python "%~dp0shot_open.py" -- B "%~dp0lookdev\cycles" 1080 1920 64 cycles gpu 45 120
if errorlevel 1 goto broke
echo ===== 4/4  Cycles（显卡）：A 段 =====
"%B%" -b --python-exit-code 1 --python "%~dp0shot_open.py" -- A "%~dp0lookdev\cycles" 1080 1920 64 cycles gpu 40
if errorlevel 1 goto broke
echo.
echo 完成：lookdev 文件夹里 eevee、cycles 各 3 张图。请把 lookdev 文件夹压缩发给 Claude，
echo 再截一张窗口截图（要看得见每张的 FRAME_TIME 和 CYCLES_DEVICE 那一行）。
pause
exit /b 0
:broke
echo.
echo [!] 出错了：请把这个窗口截图发给 Claude。
:fail
pause
exit /b 1
