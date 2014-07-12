set -e
echo "Uninstalling Bodysim..."

version=`blender --help | head -1 | awk '{ print $2 }'`
scripts_path=/usr/share/blender/scripts
if [ -f /etc/redhat-release ]
then
    # Path for RPM distros
    scripts_path=/usr/share/blender/$version/scripts
fi

# Delete Bodysim startup folder
sudo rm -rf $scripts_path/startup/Bodysim

# Restore original blender panels
sudo cp installation/__init__Original.py $scripts_path/startup/bl_ui/__init__.py

# Delete Bodysim config folder
rm -rf ~/.bodysim

# Delete shortcut
sudo rm -rf /usr/share/applications/BodySim.desktop

echo "Uninstall Done!"
