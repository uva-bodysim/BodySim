BodySim
=======
Copyright (C) 2014 [UVa Center for Wireless Health](http://wirelesshealth.virginia.edu/content/bodysim).

##Installation
If you use git and would like to try the bleeding edge version, you can clone the repository:
```
git clone https://github.com/uva-bodysim/BodySim.git
```
or download a zipped version [here](https://github.com/uva-bodysim/BodySim/archive/master.zip). Otherwise, simply download the [latest stable version](https://github.com/uva-bodysim/BodySim/releases) and unzip the archive to a temporary location.

BodySim simulation runs on top of [Blender](http://www.blender.org/) using a set of Python scripts and requires several Python libraries to work. Installation on all platforms requires one to first install Blender.

On Windows, simply download the executable and install. On Linux platforms with package managers, simply run either `sudo apt-get install blender` for Debian based distros (e.g. Ubuntu) or `sudo yum install blender` for RPM based distros (e.g. Fedora).

###Windows, 64 Bit
After installing blender 2.x (at least 2.60 is recommended), install the following dependencies:

1. Enthought Canopy Free, [here](https://www.enthought.com/products/epd/free/). Make sure you **run the program once** to set the default python on your system. Also make sure you install the **FREE** version, not the full one.
2. Enthought Tool Suite, found under `installation/ets-4.4.2.win-amd64-py2.7.exe`. Make sure you select Enthought Canopy's python when it asks where to install the tool suite.

Then, double click on the `install.bat` in the unzipped directory to finish BodySim installation. A desktop shortcut will be provided to start the demo application.

###Linux
*NOTE: IMUSim no longer works with these instructions under Linux. A fix may be released in the future. You may still use BodySim to simulate trajectory data and run other external simulations.*

After installing Blender using the appropriate package manager (again, any relatively new version should be fine, i.e. 2.6x or newer), install the following dependencies:

1. Enthought Canopy Full (Academic), [here](https://www.enthought.com/products/canopy/academic/). You will need to register for an account to download this version. Once again, **run the program once** to set the default python on your system. To check this, type in `python` in the terminal and look for 'Enthought'.
2. Python development packages, either via `sudo apt-get install python-dev` or `sudo yum install python-devel`.
3. libpng and libpng development packages, either via `sudo apt-get install libpng libpng-dev` or `sudo yum install libpng libpng-devel`.
4. g++, via `sudo apt-get install g++` or `sudo yum install gcc-c++`.

Then, navigate to the root of the downloaded BodySim folder using the terminal and run (without `sudo`) `bash install.sh`. A new desktop entry will be located under the 'Science' or 'Education' category, although for some distributions like Cinnamon, the entry may be found under 'Other'.

If manually installing blender, ensure that it is on your path. To check this, type in `blender` in the terminal and the program should start up.

## Getting Started
For a tour of BodySim's capabilities, check out the [Getting Started](../../wiki/Getting-Started) guide.

Please email Philip Asare at pka6qz@virginia.edu for project related questions or Scott Tepsuporn at spt9np@virginia.edu for software related questions.
