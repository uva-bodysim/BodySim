@ECHO OFF

NET SESSION >nul 2>&1
IF NOT %ERRORLEVEL% EQU 0 (
    ECHO Please run the script with admin privileges.
    PAUSE
    EXIT
)

:: Uninstall Bodysim
ECHO "Unstalling Bodysim..."
:: Delete Bodysim startup folder
RD /S/Q "C:\Program Files\Blender Foundation\Blender\2.70\scripts\startup\Bodysim"
:: Restore original Blender panels
XCOPY %CD%\installation\__init__Original.py /Y "C:\Program Files\Blender Foundation\Blender\2.70\scripts\startup\bl_ui\__init__.py"
:: Delete Bodysim config folder
RD /S/Q %USERPROFILE%\.bodysim

:: Delete Shortcut
DEL %USERPROFILE%\Desktop\Bodysim.bat

ECHO "Uninstall Done!"
PAUSE
