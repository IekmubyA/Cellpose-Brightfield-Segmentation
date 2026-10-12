@echo off
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0"
title Cellpose Simple - GUI Launcher

rem Tkinter is bundled with most standard Windows Python installations.
rem This launcher does not install Cellpose, PyTorch or CUDA.
set "PYTHON_GUI="
where py.exe >nul 2>&1
if not errorlevel 1 (
  py -3 -c "import tkinter" >nul 2>&1
  if not errorlevel 1 set "PYTHON_GUI=py -3"
)
if not defined PYTHON_GUI (
  where python.exe >nul 2>&1
  if not errorlevel 1 (
    python -c "import tkinter" >nul 2>&1
    if not errorlevel 1 set "PYTHON_GUI=python"
  )
)
if defined PYTHON_GUI goto START_GUI

echo No working Python with tkinter was found automatically.
echo.
echo You can use an existing Python by entering its full python.exe path.
echo Press Enter to skip this step and see Python installation options.
set "CUSTOM_PY="
set /p "CUSTOM_PY=Path to python.exe (optional): "
if not defined CUSTOM_PY goto OFFER_INSTALL
if not exist "%CUSTOM_PY%" goto INVALID_PY
"%CUSTOM_PY%" -c "import tkinter" >nul 2>&1
if errorlevel 1 goto INVALID_PY
"%CUSTOM_PY%" "%~dp0Cellpose_Simple_GUI_EN.py"
if errorlevel 1 goto GUI_FAILED
exit /b 0

:INVALID_PY
echo.
echo Could not use this interpreter or tkinter is missing.
echo For a standard Windows Python installation, Tcl/Tk must be enabled.
echo.
goto OFFER_INSTALL

:OFFER_INSTALL
echo Python for Windows normally includes tkinter (Tcl/Tk).
echo You may install Python independently; this does not install Cellpose.
echo.
where winget.exe >nul 2>&1
if errorlevel 1 goto MANUAL
choice /c YN /n /m "Install Python 3.11 using Windows Package Manager now? [Y/N]: "
if errorlevel 2 goto MANUAL
winget install --id Python.Python.3.11 --exact --source winget --accept-package-agreements --accept-source-agreements
if errorlevel 1 goto INSTALL_FAIL
echo.
echo Python installation completed. Please close and reopen this BAT file.
pause
exit /b 0

:INSTALL_FAIL
echo Python installation was not completed successfully.
:MANUAL
echo Download a standard Python installer from https://www.python.org/downloads/windows/
echo Enable the Tcl/Tk and IDLE component, then run this BAT again.
pause
exit /b 1

:START_GUI
%PYTHON_GUI% "%~dp0Cellpose_Simple_GUI_EN.py"
if errorlevel 1 goto GUI_FAILED
exit /b 0

:GUI_FAILED
echo.
echo The GUI terminated with an error. See the messages above.
pause
exit /b 1
