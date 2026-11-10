@echo off
rem 找 Blender：环境变量 BLENDER → 上次记下的路径（blender_path.txt）→ 常见安装位置 → 都没有就请你把 blender.exe 拖进窗口
set "B="
if defined BLENDER if exist "%BLENDER%" set "B=%BLENDER%"
if defined B goto ok
if not exist "%~dp0blender_path.txt" goto search
set /p B=<"%~dp0blender_path.txt"
if exist "%B%" goto ok
set "B="
:search
for /d %%D in ("%ProgramFiles%\Blender Foundation\Blender*") do if exist "%%~D\blender.exe" set "B=%%~D\blender.exe"
if defined B goto ok
for /d %%D in ("%ProgramFiles(x86)%\Blender Foundation\Blender*") do if exist "%%~D\blender.exe" set "B=%%~D\blender.exe"
if defined B goto ok
for /d %%D in ("%LOCALAPPDATA%\Programs\Blender Foundation\Blender*") do if exist "%%~D\blender.exe" set "B=%%~D\blender.exe"
if defined B goto ok
if exist "%ProgramFiles(x86)%\Steam\steamapps\common\Blender\blender.exe" set "B=%ProgramFiles(x86)%\Steam\steamapps\common\Blender\blender.exe"
if defined B goto ok
for /f "delims=" %%P in ('where blender.exe 2^>nul') do if not defined B set "B=%%P"
if defined B goto ok
for /d %%D in ("%USERPROFILE%\Downloads\blender-*" "%USERPROFILE%\Desktop\blender-*" "C:\blender-*" "D:\blender-*" "D:\Blender*" "D:\Program Files\Blender Foundation\Blender*") do if exist "%%~D\blender.exe" set "B=%%~D\blender.exe"
if defined B goto ok
echo.
echo [!] 没有自动找到 Blender。
echo     请找到 blender.exe：桌面上的 Blender 图标点右键，选「打开文件所在的位置」；
echo     然后把 blender.exe 这个文件拖进这个黑色窗口，按回车。（只需要做一次，之后会记住）
echo.
set /p "B=把 blender.exe 拖到这里，然后按回车："
set "B=%B:"=%"
set "B=%B:blender-launcher.exe=blender.exe%"
if exist "%B%" goto remember
echo.
echo [!] 这个路径找不到文件：%B%
echo     请确认拖进来的是 blender.exe。
set "B="
exit /b 1
:remember
> "%~dp0blender_path.txt" echo %B%
:ok
echo 使用的 Blender：%B%
exit /b 0
