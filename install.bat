@ECHO OFF

NET SESSION >nul 2>&1
IF NOT %ERRORLEVEL% EQU 0 (
    ECHO Please run the script with admin privileges.
    EXIT
)

IF "%1" == "\i" (
    :: Install Bodysim
    ECHO "Installing Bodysim..."
    :: Copy Bodysim scripts into startup folder
    MKDIR "C:\Program Files\Blender Foundation\Blender\2.70\scripts\startup\Bodysim"
    XCOPY %CD%\Bodysim "C:\Program Files\Blender Foundation\Blender\2.70\scripts\startup\Bodysim"
    :: Remove unnecessary panels
    XCOPY %CD%\installation\__init__Stripped.py /Y "C:\Program Files\Blender Foundation\Blender\2.70\scripts\startup\bl_ui\__init__.py"
    :: Install IMUSim (TODO)
    ECHO "Installation Done!"
    ) ELSE (

IF "%1" == "\u" (
    :: Uninstall Bodysim
    ECHO "Unstalling Bodysim..."
    :: Delete Bodysim startup folder
    RD /S/Q "C:\Program Files\Blender Foundation\Blender\2.70\scripts\startup\Bodysim"
    :: Restore original Blender panels
    XCOPY %CD%\installation\__init__Original.py /Y "C:\Program Files\Blender Foundation\Blender\2.70\scripts\startup\bl_ui\__init__.py"
    :: Uninstall IMUSim (TODO)
    ECHO "Uninstall Done!"
    ) ELSE (
    ECHO install.bat usage...
    ECHO /i install
    ECHO /u uninstall
    ))
