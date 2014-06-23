set -e
echo "Uninstalling Bodysim..."

# Delete Bodysim startup folder
sudo rm -rf /usr/share/blender/scripts/startup/Bodysim

# Restore original blender panels
sudo cp installation/__init__Original.py /usr/share/blender/scripts/startup/bl_ui/__init__.py

# Delete Bodysim config folder
rm -rf ~/.bodysim

# Delete shortcut
sudo rm -rf /usr/share/applications/BodySim.desktop

echo "Uninstall Done!"
