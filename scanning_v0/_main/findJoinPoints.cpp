#include <iostream>
#include <pcl/point_cloud.h>
#include <pcl/point_types.h>
#include <pcl/io/pcd_io.h>
#include <math.h>
#include <pcl/visualization/pcl_visualizer.h>
#include <boost/thread/thread.hpp>
#include <pcl/registration/ia_ransac.h>
#include <pcl/registration/icp.h>

Eigen::Matrix4f getRyMatrix(float theta, float x, float z){
	float PI = 3.1415926535; //Fill out correct value here
	float theta_rad = (theta * PI) / 180.0;
	Eigen::Matrix4f rotMat;
	rotMat << cos(theta_rad), 0,  sin(theta_rad), 0, 0, 1, 0, 0, -1*sin(theta_rad), 0, cos(theta_rad), 0, x, 0, z, 1;
	std::cout << "z: " << z << " x: " << x << std::endl;
  return rotMat;
}

/*  Structure for the extreme points in the 12 o'clock point cloud */
struct extremePoints{
	int pos_x0;
	int neg_x0; 
};

/*
 * Find the most positive X point for the 4 o'clock point cloud 
 */
int findPosX(pcl::PointCloud<pcl::PointXYZRGBA>::Ptr cloud_4o){

	size_t max_index = 0; // index of point with most positive X
	float current_max = cloud_4o->points[0].x; // value of current most positive X point
	
	// bubble out the maximum X value
	for(size_t i = 1; i < cloud_4o->points.size(); i++){
		if(cloud_4o->points[i].y && cloud_4o->points[i].x > current_max){
			current_max = cloud_4o->points[i].x;
			max_index = i;
		}
	}
	
	// store most positive point
	pcl::PointXYZRGBA pos_x = cloud_4o->points[max_index]; 
	return max_index;
}

/*
 * Find the most negative X point for the 8 o'clock point cloud
 */
int findNegX(pcl::PointCloud<pcl::PointXYZRGBA>::Ptr cloud_8o){

	size_t min_index = 0; // index of point with most positive X
	float current_min = cloud_8o->points[0].x; // value of current most positive X point
	
	// bubble out the minimum X value
	for(size_t i = 1; i < cloud_8o->points.size(); i++){
		if(cloud_8o->points[i].y < 0 && cloud_8o->points[i].x < current_min){
			current_min = cloud_8o->points[i].x;
			min_index = i;
		}
	}
	return min_index;
}

/*
 * Find the most negative X and most positive X points for the 12 o'clock point cloud
 */
extremePoints findCriticalPoints(pcl::PointCloud<pcl::PointXYZRGBA>::Ptr cloud_12o){
	
	extremePoints x0s;
	
	x0s.pos_x0 = findPosX(cloud_12o);
	x0s.neg_x0 = findNegX(cloud_12o);
	
	return x0s;
}

int main( int argc, char** argv) {

  pcl::PointCloud<pcl::PointXYZRGBA>::Ptr cloud_4o (new pcl::PointCloud<pcl::PointXYZRGBA>);
  pcl::PointCloud<pcl::PointXYZRGBA>::Ptr cloud_8o (new pcl::PointCloud<pcl::PointXYZRGBA>);
  pcl::PointCloud<pcl::PointXYZRGBA>::Ptr cloud_12o (new pcl::PointCloud<pcl::PointXYZRGBA>);

  int index_4o;
  int index_8o;
  extremePoints index_12o; 

  //program accepts 2 .pcd files. *change to 3 later
  if ( argc > 4 ) {
    std::cout << "usage: " << argv[0] << " <filename.pcd> <filename.pcd>\n" << std::endl;
  }
  else {
    if(pcl::io::loadPCDFile<pcl::PointXYZRGBA> (argv[1], *cloud_4o) == -1) {
      PCL_ERROR ("Could not read file\n");
      return (-1);
    }
    if(pcl::io::loadPCDFile<pcl::PointXYZRGBA> (argv[2], *cloud_8o) == -1) {
      PCL_ERROR ("Could not read file\n");
      return (-1);
    }
    if(pcl::io::loadPCDFile<pcl::PointXYZRGBA> (argv[3], *cloud_12o) == -1) {
      PCL_ERROR ("Could not read file\n");
      return (-1);
    }
  }

  index_4o = findPosX(cloud_4o);
  index_8o = findNegX(cloud_8o);
  index_12o = findCriticalPoints(cloud_12o);

  Eigen::Matrix4f rotate_4o = getRyMatrix(-120,0,0);
  Eigen::Matrix4f rotate_8o = getRyMatrix(120,0,0);

  pcl::PointCloud<pcl::PointXYZRGBA>::Ptr cloud_4o_final (new pcl::PointCloud<pcl::PointXYZRGBA>);
  pcl::PointCloud<pcl::PointXYZRGBA>::Ptr cloud_8o_final (new pcl::PointCloud<pcl::PointXYZRGBA>);

  pcl::transformPointCloud(*cloud_4o, *cloud_4o_final, rotate_4o);
  pcl::transformPointCloud(*cloud_8o, *cloud_8o_final, rotate_8o);

  float trans_4o_x = cloud_12o->points[index_12o.neg_x0].x-cloud_4o_final->points[index_4o].x;
  float trans_4o_z = cloud_12o->points[index_12o.neg_x0].z-cloud_4o_final->points[index_4o].z;

  float trans_8o_x = cloud_12o->points[index_12o.pos_x0].x-cloud_8o_final->points[index_8o].x;
  float trans_8o_z = cloud_12o->points[index_12o.pos_x0].z-cloud_8o_final->points[index_8o].z;

  //Eigen::Matrix4f translate_4o = getRyMatrix(0, 100,100);//trans_4o_x, trans_4o_z);
  //Eigen::Matrix4f translate_8o = getRyMatrix(0, 100,100);//trans_8o_x, trans_8o_z);

  //pcl::transformPointCloud(*cloud_4o_temp, *cloud_4o, translate_4o);
  //pcl::transformPointCloud(*cloud_8o_temp, *cloud_8o, translate_8o);

  for(size_t i = 0; i< cloud_4o_final->points.size(); i++){
    cloud_4o_final->points[i].x+=trans_4o_x; 
    cloud_4o_final->points[i].z+=trans_4o_z; 
  }
  for(size_t i = 0; i< cloud_8o_final->points.size(); i++){
    cloud_8o_final->points[i].x+=trans_8o_x; 
    cloud_8o_final->points[i].z+=trans_8o_z; 
  }

  // Initializing point cloud visualizer
  boost::shared_ptr<pcl::visualization::PCLVisualizer>
  viewer_final (new pcl::visualization::PCLVisualizer ("3D Viewer"));
  viewer_final->setBackgroundColor (0, 0, 0);

  // 4o
  pcl::visualization::PointCloudColorHandlerCustom<pcl::PointXYZRGBA>
  color_4o (cloud_4o_final, 255, 0, 0);
  viewer_final->addPointCloud<pcl::PointXYZRGBA> (cloud_4o_final, color_4o, "output cloud 1");
  viewer_final->setPointCloudRenderingProperties (pcl::visualization::PCL_VISUALIZER_POINT_SIZE,
                                                  1, "output cloud 1");

  // 8o
  pcl::visualization::PointCloudColorHandlerCustom<pcl::PointXYZRGBA>
  color_8o (cloud_8o_final, 0, 255, 0);
  viewer_final->addPointCloud<pcl::PointXYZRGBA> (cloud_8o_final, color_8o, "output cloud 2");
  viewer_final->setPointCloudRenderingProperties (pcl::visualization::PCL_VISUALIZER_POINT_SIZE,
                                                  1, "output cloud 2");

  // 12o
  pcl::visualization::PointCloudColorHandlerCustom<pcl::PointXYZRGBA>
  color_12o (cloud_12o, 255, 255, 0);
  viewer_final->addPointCloud<pcl::PointXYZRGBA> (cloud_12o, color_12o, "output cloud 3");
  viewer_final->setPointCloudRenderingProperties (pcl::visualization::PCL_VISUALIZER_POINT_SIZE,
                                                  1, "output cloud 3");

  // Starting visualizer
  viewer_final->addCoordinateSystem (1.0);
  viewer_final->initCameraParameters ();

  // Wait until visualizer window is closed.
  while (!viewer_final->wasStopped ())
  {
    viewer_final->spinOnce (100);
    boost::this_thread::sleep (boost::posix_time::microseconds (100000));
  }


  return 0;
}

