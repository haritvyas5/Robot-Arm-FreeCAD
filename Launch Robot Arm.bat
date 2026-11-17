@echo off
rem Start the real-Arduino lesson on Windows. Paths with spaces are quoted.
setlocal
cd /d "%~dp0"

rem For a custom installation, uncomment and edit the following line:
rem set "FREECAD_EXE=C:\Program Files\FreeCAD 1.1\bin\FreeCAD.exe"

rem Find FreeCAD in the common installation locations or on PATH.
if defined FREECAD_EXE goto check_freecad
for /d %%D in ("%ProgramFiles%\FreeCAD*") do if exist "%%~fD\bin\FreeCAD.exe" set "FREECAD_EXE=%%~fD\bin\FreeCAD.exe"
if defined FREECAD_EXE goto check_freecad
for /d %%D in ("%LOCALAPPDATA%\Programs\FreeCAD*" "%LOCALAPPDATA%\FreeCAD*") do if exist "%%~fD\bin\FreeCAD.exe" set "FREECAD_EXE=%%~fD\bin\FreeCAD.exe"
if defined FREECAD_EXE goto check_freecad
for /f "delims=" %%F in ('where FreeCAD.exe 2^>nul') do set "FREECAD_EXE=%%F"

:check_freecad
if not defined FREECAD_EXE goto missing_freecad
if not exist "%FREECAD_EXE%" goto missing_freecad
for %%F in ("%FREECAD_EXE%") do set "FREECAD_BIN=%%~dpF"

rem Install only pyserial into this project on the first run.
rem Use FreeCAD's bundled Python if available; otherwise use the Windows Python launcher.
if exist "%~dp0.dependencies\serial\__init__.py" goto launch
set "PYTHONHOME="
set "PYTHONPATH="
if exist "%FREECAD_BIN%python.exe" goto bundled_python
where py >nul 2>nul
if errorlevel 1 goto missing_python
py -3 -m pip install --disable-pip-version-check --target "%~dp0.dependencies" "pyserial==3.5"
if errorlevel 1 goto install_failed
goto launch

:bundled_python
"%FREECAD_BIN%python.exe" -m pip install --disable-pip-version-check --target "%~dp0.dependencies" "pyserial==3.5"
if errorlevel 1 goto install_failed

:launch
rem FreeCAD supplies its own Python runtime; do not inherit another Python home.
set "PYTHONHOME="
set "PYTHONPATH="
start "" "%FREECAD_EXE%" "%~dp0RobotArm.FCMacro"
if errorlevel 1 goto launch_failed
exit /b 0

:missing_freecad
echo FreeCAD was not found. Install it or set FREECAD_EXE near the top of this file.
goto failed

:missing_python
echo Install Python 3 with the Windows py launcher, then run this file again.
echo Alternatively, install pyserial using the command in README.md.
goto failed

:install_failed
echo Could not install pyserial. Check your internet connection and the pip error above.
echo You can use another Python installation with the command in README.md.
goto failed

:launch_failed
echo FreeCAD could not be started. Check FREECAD_EXE near the top of this file.

:failed
pause
exit /b 1
