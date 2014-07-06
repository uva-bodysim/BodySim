BodySim
=======
Copyright (C) 2014 UVa Center for Wireless Health.

##Installation
If you use git, you can clone the repository:
```
git clone https://github.com/uva-bodysim/BodySim.git
```
otherwise, simply download the zip file [here](https://github.com/uva-bodysim/BodySim/archive/master.zip).

BodySim simulation runs on top of [Blender](http://www.blender.org/) using a set of Python scripts and requires several Python libraries to work. Installation on all platforms requries one to first install Blender.

On Windows, simply download the executable and install. On Linux platforms with package managers, simply run either `sudo apt-get install blender` for Debian based distros (e.g. Ubuntu) or `sudo yum install blender` for RPM based distros (e.g. Fedora).

###Windows, 64 Bit
After installing blender 2.70 (double check the version number as the installer scripts rely on this), install the following dependencies:

1. Enthought Canopy Free, [here](https://www.enthought.com/products/epd/free/). Make sure you **run the program once** to set the default python on your system. Also make sure you install the **FREE** version, not the full one.
2. Enthought Tool Suite, [here](http://www.lfd.uci.edu/~gohlke/pythonlibs/#ets). Search for `ets-x.y.z.win-amd64-py2.7.exe` on the site, download, and install. x.y.z denote the version number, which may change in the future.

Then, double click on the `install.bat` to finish BodySim installation. A desktop shortcut will be provided to start the demo application.

###Linux
After installing Blender using the appropriate package manager (any relatively new version should be fine, e.g. 2.6x), install the following dependencies:

1. Enthought Canopy Full (Academic), [here](https://www.enthought.com/products/canopy/academic/). You will need to register for an account to download this version. Once again, **run the program once** to set the default python on your system. To check this, type in `python` in the terminal and look for 'Enthought'.
2. Python development packages, either via `sudo apt-get python-dev` or `sudo yum install python-devel`.

Then, navigate to the root of the downloaded BodySim folder using the terminal and run `install.sh`. A new desktop entry will be located under the Science category.

If manually installing blender, ensure that it is on your path. To check this, type in `blender` in the terminal and the program should start up.

## Getting Started
For a tour of BodySim's capabilities, check out the [Getting Started](../../wiki/Getting-Started) guide.

Please email Philip Asare at pka6qz@virginia.edu for project related questions or Scott Tepsuporn at spt9np@virginia.edu for software related questions.
