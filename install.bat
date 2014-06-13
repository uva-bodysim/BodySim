@ECHO OFF

NET SESSION >nul 2>&1
IF NOT %ERRORLEVEL% EQU 0 (
    ECHO Please run the script with admin privileges.
    pause
)

:: Install Bodysim
ECHO "Installing Bodysim..."

:: Copy Bodysim scripts into startup folder
MKDIR "C:\Program Files\Blender Foundation\Blender\2.70\scripts\startup\Bodysim"
XCOPY %CD%\Bodysim "C:\Program Files\Blender Foundation\Blender\2.70\scripts\startup\Bodysim"

:: Remove unnecessary panels
XCOPY %CD%\installation\__init__Stripped.py /Y "C:\Program Files\Blender Foundation\Blender\2.70\scripts\startup\bl_ui\__init__.py"

:: Copy Bodysim conf folder
MKDIR %USERPROFILE%\.bodysim
XCOPY %CD%\.bodysim %USERPROFILE%\.bodysim

:: Create launcher
ECHO "C:\Program Files\Blender Foundation\Blender\2.70\scripts\startup\Bodysim " %USERPROFILE%\.bodysim\demo.blend > %USERPROFILE%\Desktop\Bodysim.bat

:: Install IMUSim (TODO)
ECHO "Installation Done!"
pause
