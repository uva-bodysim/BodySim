// Original code by Geoffrey Biggs, taken from the PCL tutorial in
// http://pointclouds.org/documentation/tutorials/pcl_visualizer.php

// Simple Kinect viewer that also allows to write the current scene to a .pcd
// when pressing SPACE.

#include <iostream>

#include <pcl/io/openni_grabber.h>
#include <pcl/io/pcd_io.h>
#include <pcl/visualization/cloud_viewer.h>
#include <pcl/console/parse.h>

using namespace std;
using namespace pcl;

PointCloud<PointXYZRGBA>::Ptr cloudptr(new PointCloud<PointXYZRGBA>);
PointCloud<PointXYZ>::Ptr fallbackCloud(new PointCloud<PointXYZ>);
boost::shared_ptr<visualization::CloudViewer> viewer;
Grabber* kinectGrabber;
unsigned int filesSaved = 0;
bool saveCloud(false), noColour(false);

void
printUsage(const char* programName)
{
    cout << "Usage: " << programName << " [options]"
         << endl
         << endl
         << "Options:\n"
         << endl
         << "\t<none>     start capturing from a Kinect device.\n"
         << "\t-v NAME    visualize the given .pcd file.\n"
         << "\t-h         shows this help.\n";
}

void
grabberCallback(const PointCloud<PointXYZRGBA>::ConstPtr& cloud)
{
    if (! viewer->wasStopped())
        viewer->showCloud(cloud);
        
    if (saveCloud)
    {
        stringstream stream;
        stream << "inputCloud" << filesSaved << ".pcd";
        string filename = stream.str();
        if (io::savePCDFile(filename, *cloud, true) == 0)
        {
            filesSaved++;
            cout << "Saved " << filename << "." << endl;
        }
        else PCL_ERROR("Problem saving %s.\n", filename.c_str());
        
        saveCloud = false;
    }
}

void
keyboardEventOccurred(const visualization::KeyboardEvent& event,
    void* nothing)
{
    if (event.getKeySym() == "space" && event.keyDown())
        saveCloud = true;
}

boost::shared_ptr<visualization::CloudViewer>
createViewer()
{
    boost::shared_ptr<visualization::CloudViewer> v
        (new visualization::CloudViewer("3D Viewer"));
    v->registerKeyboardCallback(keyboardEventOccurred);
    
    return(v);
}

int
main(int argc, char** argv)
{
    if (console::find_argument(argc, argv, "-h") >= 0)
    {
        printUsage(argv[0]);
        return 0;
    }
    
    bool justVisualize(false);
    string filename;
    if (console::find_argument(argc, argv, "-v") >= 0)
    {
        if (argc != 3)
        {
            printUsage(argv[0]);
            return 0;
        }
        
        filename = argv[2];
        justVisualize = true;
    }
    else if (argc != 1)
    {
        printUsage(argv[0]);
        return 0;
    }
    
    if (justVisualize)
    {
        try
        {
            io::loadPCDFile<PointXYZRGBA>(filename.c_str(), *cloudptr);
        }
        catch (PCLException e1)
        {
            try
            {
                io::loadPCDFile<PointXYZ>(filename.c_str(), *fallbackCloud);
            }
            catch (PCLException e2)
            {
                return -1;
            }
            
            noColour = true;
        }
        
        cout << "Loaded " << filename << "." << endl;
        if (noColour)
            cout << "This file has no RGBA colour information present." << endl;
    }
    else
    {
        kinectGrabber = new OpenNIGrabber();
        if (kinectGrabber == 0)
            return false;
        boost::function<void (const PointCloud<PointXYZRGBA>::ConstPtr&)> f =
            boost::bind(&grabberCallback, _1);
        kinectGrabber->registerCallback(f);
    }
    
    viewer = createViewer();
    
    if (justVisualize)
    {
        if (noColour)
            viewer->showCloud(fallbackCloud);
        else viewer->showCloud(cloudptr);
    }
    else kinectGrabber->start();
    
    while (! viewer->wasStopped())
        boost::this_thread::sleep(boost::posix_time::seconds(1));
    
    if (! justVisualize)
        kinectGrabber->stop();
}
