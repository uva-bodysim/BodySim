@ECHO OFF

NET SESSION >nul 2>&1
IF NOT %ERRORLEVEL% EQU 0 (
    ECHO Please run the script with admin privileges.
    PAUSE
    EXIT
)

:: Remind the user to install Blender and other dependencies first.
ECHO Before installing BodySim, have you installed:
ECHO - Blender 2.70,
ECHO - Enthought Canopy Free, and
ECHO - Enthought Tool Suite?
ECHO If not, please install these dependencies first, otherwise the installation will fail.
ECHO See Wiki for more details.
ECHO.
ECHO Proceed with installation?
set /p input= yes or no: 
ECHO.

IF not %input%==yes (
    ECHO Installation aborted.
    PAUSE
    EXIT
)

:: Install Bodysim
ECHO "Installing Bodysim..."

:: Copy Bodysim scripts into startup folder
MKDIR "C:\Program Files\Blender Foundation\Blender\2.70\scripts\startup\Bodysim"
XCOPY %~dp0\Bodysim "C:\Program Files\Blender Foundation\Blender\2.70\scripts\startup\Bodysim"

:: Remove unnecessary panels
XCOPY %~dp0\installation\__init__Stripped.py /Y "C:\Program Files\Blender Foundation\Blender\2.70\scripts\startup\bl_ui\__init__.py"

:: Copy Bodysim conf folder
MKDIR %USERPROFILE%\.bodysim
XCOPY /e %~dp0\.bodysim %USERPROFILE%\.bodysim

:: Create launcher... first creates a vb script used to create the shortcut
set SCRIPT="%TEMP%\%RANDOM%-%RANDOM%-%RANDOM%-%RANDOM%.vbs"
echo Set oWS = WScript.CreateObject("WScript.Shell") >> %SCRIPT%
echo sLinkFile = "%USERPROFILE%\Desktop\BodySim.lnk" >> %SCRIPT%
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %SCRIPT%
echo oLink.TargetPath = "%USERPROFILE%\.bodysim\demo.blend" >> %SCRIPT%
echo oLink.WorkingDirectory = "%USERPROFILE%\.bodysim\" >> %SCRIPT%
echo oLink.IconLocation = "%USERPROFILE%\.bodysim\bodysim.ico" >> %SCRIPT%
echo oLink.Save >> %SCRIPT%
cscript /nologo %SCRIPT%
del %SCRIPT%

:: Install IMUSim
pip install simpy==2.3.1
CD %~dp0\installation
python setup.py install
:: Copy the maths folder into the appdata path; the pyd files were not copied in the previous step.
XCOPY /e /Y %CD%\imusim\maths %LOCALAPPDATA%\Enthought\Canopy\User\Lib\site-packages\imusim-0.2-py2.7.egg\imusim\maths

ECHO "Installation Done!"
PAUSE
