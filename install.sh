set -e

if [ $(id -u) = 0 ]; then
   echo "Please do not run this script as root. It will automatically ask for"
   echo "permissions if required."
   exit
fi

echo "Before installing BodySim, have you installed:"
echo "- Blender, via 'sudo apt-get install blender' or 'sudo yum install blender, "
echo "- Python development packages (python-dev or python-devel),"
echo "- libpng and libpng development packages (libpng and either libpng-dev or"
echo "  libpng-devel), and"
echo "- Enthought Canopy Full (Academic)?"
echo "If not, please install these dependencies first; otherwise the installation"
printf " will fail. See Wiki for more details.\n"
echo "Proceed with installation?"
echo "y / n: "
read -n 1 -r -p "$1"
printf "\n"

if ! [[ $REPLY == "y" ]]
then
    echo "Exiting"
    exit
fi

echo "Installing BodySim..."

# Copy Bodysim scripts into startup folder
version=`blender --help | head -1 | awk '{ print $2 }'`

# Path for Debian distros
scripts_path=/usr/share/blender/scripts

# Debian and RPM have a different installation paths
if [ -f /etc/redhat-release ]
then
    # Path for RPM distros
    scripts_path=/usr/share/blender/$version/scripts
fi

echo "Root priviledges are required to access /usr/share/blender/"
sudo cp -r Bodysim $scripts_path/startup/

# Remove panels
sudo cp installation/__init__Stripped.py $scripts_path/startup/bl_ui/__init__.py

# Copy Bodysim conf folder
cp -r .bodysim ~/

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
sudo cp BodySim.desktop /usr/share/applications/

# Install IMUSim
pip install simpy==2.3.1
pip install installation/imusim-0.2.tar.gz

# Make LOS
make -C installation/los
# Copy to user's plugins directory
cp installation/los/los ~/.bodysim/plugins/los

echo "Installation Done!"
