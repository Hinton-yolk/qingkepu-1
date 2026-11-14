@echo off
chcp 65001 >nul
cd /d "%~dp0"
call "%~dp0find_blender.cmd"
if not defined B goto fail
echo.
echo 质感样张（两轮一起）：r1 = 去塑料感；r2 = Epic 化（逆光光柱、主板铺到远处长满器件）。
echo 每一轮都用 EEVEE 和 Cycles（显卡）各渲 B 段第 45、120 帧；另外 A 段第 40 帧两个引擎各一张。
echo 看 FRAME_TIME：同一次里的第 2 帧才准（第 1 帧含编译）。
echo.
echo ===== 1/6  r1 EEVEE =====
"%B%" -b --python-exit-code 1 --python "%~dp0shot_open.py" -- B "%~dp0lookdev\r1_eevee" 1080 1920 32 look=r1 45 120
if errorlevel 1 goto broke
echo ===== 2/6  r2 EEVEE =====
"%B%" -b --python-exit-code 1 --python "%~dp0shot_open.py" -- B "%~dp0lookdev\r2_eevee" 1080 1920 32 look=r2 45 120
if errorlevel 1 goto broke
echo ===== 3/6  A 段 EEVEE =====
"%B%" -b --python-exit-code 1 --python "%~dp0shot_open.py" -- A "%~dp0lookdev\A_eevee" 1080 1920 32 40
if errorlevel 1 goto broke
echo ===== 4/6  r1 Cycles（显卡） =====
"%B%" -b --python-exit-code 1 --python "%~dp0shot_open.py" -- B "%~dp0lookdev\r1_cycles" 1080 1920 64 cycles gpu look=r1 45 120
if errorlevel 1 goto broke
echo ===== 5/6  r2 Cycles（显卡） =====
"%B%" -b --python-exit-code 1 --python "%~dp0shot_open.py" -- B "%~dp0lookdev\r2_cycles" 1080 1920 64 cycles gpu look=r2 45 120
if errorlevel 1 goto broke
echo ===== 6/6  A 段 Cycles（显卡） =====
"%B%" -b --python-exit-code 1 --python "%~dp0shot_open.py" -- A "%~dp0lookdev\A_cycles" 1080 1920 64 cycles gpu 40
if errorlevel 1 goto broke
echo.
echo 完成：lookdev 文件夹里 6 个子文件夹、共 10 张图。请把 lookdev 文件夹压缩发给 Claude，
echo 再截窗口截图（要看得见每张的 FRAME_TIME 和 CYCLES_DEVICE 那一行；窗口往上翻，截两三张也行）。
pause
exit /b 0
:broke
echo.
echo [!] 出错了：请把这个窗口截图发给 Claude。
:fail
pause
exit /b 1
