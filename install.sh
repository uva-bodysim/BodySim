set -e
echo "Before installing BodySim, have you installed:"
echo "- Blender, either via 'sudo apt-get install blender' or 'sudo yum install blender, "
echo "- Python development packages (python-dev or python-devel), and"
echo "- Enthought Canopy Full (Academic)?"
echo "If not, please install these dependencies first; otherwise the installation will fail."
printf "See Wiki for more details.\n"
echo "Proceed with installation?"
echo "y / n: "
read -n 1 -r -p "$1"
printf "\n"
echo $REPLY
if ! [[ $REPLY == "y" ]]
then
    echo "Exiting"
    exit
fi

echo "Installing BodySim..."

# Copy Bodysim scripts into startup folder
echo "Root priviledges are required to access /usr/share/blender/scripts/startup/"
sudo mkdir -p /usr/share/blender/scripts/startup/Bodysim
sudo cp -r Bodysim /usr/share/blender/scripts/startup/Bodysim

# Remove panels
sudo cp installation/__init__Stripped.py /usr/share/blender/scripts/startup/bl_ui/__init__.py

# Copy Bodysim conf folder
mkdir -p ~/.bodysim
cp -r .bodysim ~/.bodysim

# Create Launcher... for whatever reason we cannot access environment vars from .desktop.
echo """[Desktop Entry]
Name=BodySim
Comment=Simulator for Body Sensor Networks
Keywords=scientific;
Exec=blender $HOME/.bodysim/demo.blend
Icon=$HOME/.bodysim/bodysim.png
Terminal=True
Type=Application
Categories=Science;""" > BodySim.desktop

# Copy launcher
sudo cp BodySim.desktop /usr/share/applications/BodySim.desktop

# Install IMUSim
pip install simpy==2.3.1
pip install installation/imusim-0.2.tar.gz

echo "Installation Done!"
