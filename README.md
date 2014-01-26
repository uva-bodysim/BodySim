BodySim
=======

Repository for BodySim Project 
For more information on how to use GIT, check out the following set of resources: 
http://stackoverflow.com/questions/315911/git-for-beginners-the-definitive-practical-guide

##Installation
BodySim simulation runs on top of Blender using a set of Python scripts, and requires several Python libraries to work.

###Ubuntu

1. Install Blender, Python, and required libraries, as well as git (to be able to clone BodySim)
   ```
   sudo apt-get install blender python python-matplotlib wxpythongtk2.8 git
   ```

2. Clone BodySim
   ```
   cd ~
   git clone https://github.com/aksimhal/BodySim.git
   ```

3. Copy the appropriate files to your installation of Blender.

   ```
   sudo mkdir /usr/lib/blender/scripts/startup/BodySim
   sudo cp ~/BodySim/BodySim/* /usr/lib/blender/scripts/startup/BodySim
   ````

4. Open BodySim

   ```
   blender ~/BodySim/code/model-w-all-vertex-groups.blend
   ```


If you have any questions, please email spt9np@virginia.edu or pka6qz@virginia.edu.
