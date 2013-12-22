#include <iostream>
#include <pcl/point_cloud.h>
#include <pcl/point_types.h>
#include <pcl/io/pcd_io.h>
#include <pcl/filters/passthrough.h>
#include <pcl/filters/approximate_voxel_grid.h>
#include <math.h>
#include <pcl/visualization/pcl_visualizer.h>
#include <boost/thread/thread.hpp>
#include <pcl/filters/radius_outlier_removal.h>

//finds the minimum z distance between camera and object
float findMinZ(pcl::PointCloud<pcl::PointXYZRGBA>::Ptr cloud){
  for(size_t i = 0; i< cloud->points.size(); i++){
     //approximates center point within x-y frame and returns z-value
     if(cloud->points[i].x >= -0.05 && cloud->points[i].y >= -0.05\
        && cloud->points[i].x <= 0.05 && cloud->points[i].y <= 0.05 )
       return cloud->points[i].z;
  }
  return -100.0; //this signifies an error
}

//Remove floor points
void removeFloorPoints( pcl::PointCloud<pcl::PointXYZRGBA>::Ptr my_cloud, pcl::PointCloud<pcl::PointXYZRGBA>::Ptr filtered_cloud ) {
  float maxY = -9999999;

  for( size_t i=0; i < my_cloud->points.size(); ++i )
  {
    if( my_cloud->points[i].y > maxY ) {
      maxY = my_cloud->points[i].y;
    }
  }
  std::cout << "Max Y = " << maxY << std::endl;

  pcl::PassThrough<pcl::PointXYZRGBA> removeFloor;
  removeFloor.setInputCloud(my_cloud);
  removeFloor.setFilterFieldName("y");
  removeFloor.setFilterLimits(-9999999, maxY - 0.2);
  removeFloor.filter(*filtered_cloud);
}

//sets up parameters for filter then filters result
void filterDimension(pcl::PassThrough<pcl::PointXYZRGBA> f, pcl::PointCloud<pcl::PointXYZRGBA>::Ptr input_cloud, pcl::PointCloud<pcl::PointXYZRGBA>::Ptr filtered_cloud, std::string field, float limit) {
  f.setInputCloud (input_cloud);
  f.setFilterFieldName (field);
  f.setFilterLimits (-limit, limit);
  f.filter (*filtered_cloud);
}

int main (int argc, char** argv)
{
 pcl::PointCloud<pcl::PointXYZRGBA>::Ptr input_cloud (new pcl::PointCloud<pcl::PointXYZRGBA>);
 pcl::PointCloud<pcl::PointXYZRGBA>::Ptr filtered_cloud (new pcl::PointCloud<pcl::PointXYZRGBA>);
  
  //read in .pcd file from command line
  if ( argc > 3 ) {
    std::cout << "usage: " << argv[0] << " <filename.pcd> <filename.pcd>\n" << std::endl;
  }
  else {
    if(pcl::io::loadPCDFile<pcl::PointXYZRGBA> (argv[1], *input_cloud) == -1) {
      PCL_ERROR ("Could not read file\n");
      return (-1);
    }
    std::cout << "Loaded " << input_cloud->size() << " data points from " << argv[1] << std::endl;
  }

  //Set up limits for filter for isolating human body from pointcloud
  //*Note: Kinect should be set up no more than 1.75m above gorund level
  //*Note: all dimensions in meters

  float x;
  float y;
  float z;
  float minZ;
  std::cout << "Enter a x-limit for the filter: ";
  std::cin >> x;
  std::cout << "Enter height of kinect: ";
  std::cin >> y;
  std::cout << "Enter a depth value to add to Min z-value: ";
  std::cin >> z;
  minZ = findMinZ(input_cloud);
  std::cout << "Min Z = " << minZ << ", X-limit = " << x << ", Y-limit = " << y << std::endl;
  z = z + minZ;

  //Set up filters for each of the dimensions
  pcl::PassThrough<pcl::PointXYZRGBA> passX;
  filterDimension(passX, input_cloud, filtered_cloud, "x", x);
  pcl::PassThrough<pcl::PointXYZRGBA> passY;
  filterDimension(passY, filtered_cloud, filtered_cloud, "y", y);
  pcl::PassThrough<pcl::PointXYZRGBA> passZ;
  filterDimension(passZ, filtered_cloud, filtered_cloud, "z", z);

  removeFloorPoints(filtered_cloud, filtered_cloud);

  // Filtering input scan to roughly 10% of original size to increase speed of registration
  pcl::PointCloud<pcl::PointXYZRGBA>::Ptr final_filtered_cloud (new pcl::PointCloud<pcl::PointXYZRGBA>);
  pcl::ApproximateVoxelGrid<pcl::PointXYZRGBA> approximate_voxel_filter;
  approximate_voxel_filter.setLeafSize (0.01, 0.01, 0.01); //base values were all set to 0.2 for 100,000p point cloud from tutorial
  approximate_voxel_filter.setInputCloud (filtered_cloud);
  approximate_voxel_filter.filter (*final_filtered_cloud);
  std::cout << "Filtered cloud contains " << final_filtered_cloud->size ()
            << " data points from " << filtered_cloud << std::endl;

  pcl::PointCloud<pcl::PointXYZRGBA>::Ptr final_filtered_cloud2 (new pcl::PointCloud<pcl::PointXYZRGBA>);

  pcl::RadiusOutlierRemoval<pcl::PointXYZRGBA> filterOutliers;
  filterOutliers.setInputCloud (final_filtered_cloud);
  filterOutliers.setRadiusSearch (.02);
  filterOutliers.setMinNeighborsInRadius (5);
  filterOutliers.filter (*final_filtered_cloud2);

  //save .pcd file
  pcl::io::savePCDFileASCII ("filtered_cloud.pcd", *final_filtered_cloud2);

  return (0);
}
