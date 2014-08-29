@ECHO OFF

NET SESSION >nul 2>&1
IF NOT %ERRORLEVEL% EQU 0 (
    ECHO Please run the script with admin privileges.
    PAUSE
    EXIT
)

:: Determine version
CD C:\Program Files\Blender Foundation\Blender
set var="none"
for /d %%d in (2.*) do (
    set var=%%d
)
echo Detected Blender version %var%.
if %var% == "none" (
    echo Error: No blender version detected under C:\Program Files\Blender Foundation\Blender
    pause
)

:: Uninstall Bodysim
ECHO "Unstalling Bodysim..."
:: Delete Bodysim startup folder
RD /S/Q "C:\Program Files\Blender Foundation\Blender\%var%\scripts\startup\Bodysim"
:: Restore original Blender panels
XCOPY %~dp0\installation\__init__Original.py /Y "C:\Program Files\Blender Foundation\Blender\%var%\scripts\startup\bl_ui\__init__.py"
:: Delete Bodysim config folder
RD /S/Q %USERPROFILE%\.bodysim

:: Delete Shortcut
DEL %USERPROFILE%\Desktop\BodySim.lnk

ECHO "Uninstall Done!"
PAUSE
