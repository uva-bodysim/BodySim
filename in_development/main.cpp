#include "vectmath.h"
#include "utils.h"
#include <stdlib.h>
#include <stdio.h>
#include <iostream>
#include <sstream>
#include <fstream>
#include <string>
#include <cstdlib>

int main(int argc, char **argv) {
    // We'll be dealing with only one simulation at a time.
    // ARGUMENTS: frame start, frame end, triangle count, frame path,
    // Sphere sample count, sphere radius, trajectory sim path, sensor count, and
    // List of sensors to simulate, separated by white space and starting in "sensor_"
    // Paths must be absolute and end in appropriate os.sep.

    int frame_start = atoi(argv[1]);
    int frame_end = atoi(argv[2]);
    int anim_length = frame_end - frame_start + 1;
    int triangle_count = atoi(argv[3]);
    std::string frame_path = argv[4];
    int sample_count = atoi(argv[5]);
    float sphere_radius = atof(argv[6]);
    std::string trajectory_path = argv[7];
    int sensor_count = atoi(argv[8]);

    std::string sensor_line;
    std::string DELIMITER = ",";


    // Load all the sensor trajectory data.
    vector ** sensor_locs = new vector*[sensor_count];
    for(int i = 9; i < 9 + sensor_count; i++) {
        sensor_locs[i - 9] = new vector[anim_length];
        // Read in the file. Make sure os.sep is supplied because C++ can't tell
        std::string sensor_file_path = trajectory_path + argv[i] + ".csv";
        std::ifstream sensor_file(sensor_file_path.c_str());
        // Skip Header
        getline(sensor_file, sensor_line);
        int count = 0;
        while(getline(sensor_file, sensor_line)) {
            int delim_pos = sensor_line.find(DELIMITER);
            sensor_line = sensor_line.substr(delim_pos + 1);
            delim_pos = sensor_line.find(DELIMITER);
            for(int j = 0; j < 3; j++) {
                sensor_locs[i - 9][count][j] = atof(sensor_line.substr(0, delim_pos).c_str());
                delim_pos = sensor_line.find(DELIMITER);
                sensor_line = sensor_line.substr(delim_pos + 1);
            }
            count ++;
        }
    }


    // Read in the frames.
    vector *** triangles = new vector**[anim_length];
    for(int i = 0; i < anim_length; i++) {
        std::stringstream ss;
        std::string frame_number_str;
        ss << (i + 1);
        ss >> frame_number_str;
        std::string frame_line;
        std::string frame_file_str = frame_path + "frame" + frame_number_str + ".csv";
        std::ifstream frame_file(frame_file_str.c_str());
        triangles[i] = new vector*[triangle_count];
        for(int j = 0; j < triangle_count; j++) {
            triangles[i][j] = new vector[3];
            getline(frame_file, frame_line);
            int delim_pos = frame_line.find(DELIMITER);
            for(int k = 0; k < 3; k++) {
                for(int l = 0; l < 3; l++) {
                    triangles[i][j][k][l] = atof(frame_line.substr(0, delim_pos).c_str());
                    frame_line = frame_line.substr(delim_pos + 1);
                    delim_pos = frame_line.find(DELIMITER);
                }
            }
        }
    }

    // Create sphere.
    vector * spheres_sample_points = new vector[300];
    sphere_samples(spheres_sample_points, sample_count, sphere_radius);

    // Prepare results storage.
    float ** body_interference = new float *[sensor_count];
    for(int i = 0; i < sensor_count; i++) {
        body_interference[i] = new float[anim_length];
    }

    bool *** direct_interference = new bool **[sensor_count];
    for(int i = 0; i < sensor_count; i++) {
        direct_interference[i] = new bool *[anim_length];
        for(int j = 0; j < anim_length; j++) {
            direct_interference[i][j] = new bool[sensor_count - 1];
        }
    }

    float sample_count_flt = (float) sample_count;

    // LOS Calcs.
    // TODO Parallelize this section.
    for(int i = 0; i < sensor_count; i++) {
        for(int j = 0; j < anim_length; j++) {
            // Check for body interference
            int count = 0;
            for(int k = 0; k < sample_count; k++) {
                float * result;
                vector res_vect;
                vector ray;
                vector offsetSphere;
                ADDV(offsetSphere, spheres_sample_points[k], sensor_locs[i][j]);
                SUBV(ray, offsetSphere, sensor_locs[i][j]);
                for(int l = 0; l < triangle_count; l++) {
                    result = intersect_ray_tri(triangles[j][l][0], triangles[j][l][1],
                                      triangles[j][l][2], ray, sensor_locs[i][j]);
                    if(result != 0) {
                        res_vect[0] = result[0]; res_vect[1] = result[1]; res_vect[2] = result[2];
                        if(isInBetw(res_vect, sensor_locs[i][j], offsetSphere))  {
                            count ++;
                            break;
                        }
                    }
                }
                delete result;
            }

            // Check for direct LOS to other sensors.
            bool skipped = false;
            for(int k = 0; k < sensor_count; k++) {
                if(i == k) {
                    skipped = true;
                    continue;
                }
                vector ray;
                vector res_vect;
                float * result;
                SUBV(ray, sensor_locs[i][k], sensor_locs[i][j]);
                bool has_los = true;
                for(int l = 0; l < triangle_count; l++) {
                    result = intersect_ray_tri(triangles[j][l][0], triangles[j][l][1],
                                               triangles[j][l][2], ray, sensor_locs[i][j]);
                    if(result != 0) {
                        res_vect[0] = result[0]; res_vect[1] = result[1]; res_vect[2] = result[2];
                        if(isInBetw(res_vect, sensor_locs[i][j], sensor_locs[i][k]))  {
                            has_los = false;
                            break;
                        }
                    }
                }
                delete result;
                direct_interference[i][j][skipped ? (k+1):k] = has_los;
            }
            body_interference[i][j] = (float)count / sample_count_flt;
        }
    }
}
