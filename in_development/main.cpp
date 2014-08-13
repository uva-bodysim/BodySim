#include "vectmath.h"
#include <stdlib.h>
#include <stdio.h>
#include <iostream>
#include <sstream>
#include <fstream>
#include <string>
#include <cstdlib>
#include <math.h>

using namespace std;

inline bool file_exists (char * c) {
    if (FILE *file = fopen(c, "r")) {
        fclose(file);
        return true;
    } else {
        return false;
    }   
}

float * intersect_ray_tri(vector v1, vector v2, vector v3, vector ray, vector origin) {
    float det, inv_det, u, v, t, absv;
    vector dir, e1, e2, tvec, qvec, pvec;
    NORMV(dir, ray);
    SUBV(e1, v2, v1);
    SUBV(e2, v3, v1);
    CROSSVP(pvec, dir, e2);
    DOTVP(det, e1, pvec);
    if (det > -0.000001f && det < 0.000001f) {
        return 0;
    }

    inv_det = 1.0f / det;
    SUBV(tvec, origin, v1);
    DOTVP(u, tvec, pvec);
    u = u * inv_det;
    if(u < 0.0f || u > 1.0f){
        return 0;
    }
    CROSSVP(qvec, tvec, e1);

    DOTVP(v, dir, qvec);
    v = v * inv_det;

    if (v < 0.0f || u + v > 1.0f) {
        return 0;
    }

    DOTVP(t, e2, qvec);
    t = t * inv_det;
    MULVS(dir, dir, t);
    ADDV(pvec, origin, dir);
    float *result = new float[3];
    result[0] = pvec[0];
    result[1] = pvec[1];
    result[2] = pvec[2];
    return result;
}

bool isInBetw(vector pt, vector begin, vector end) {
    float dot, crossLength, eBLength;
    vector eB, pB, cross;
    SUBV(eB, end, begin);
    SUBV(pB, pt, begin);
    DOTVP(dot, eB, pB);
    CROSSVP(cross, eB, pB);
    ABSV(eBLength, eB);
    ABSV(crossLength, cross);
    return (crossLength < 0.0001f && dot >= 0.0000f && dot < eBLength * eBLength);
}

void sphere_samples(vector * result, int num_points, float radius) {
    float dlong, dz, longitude, z, r;
    dlong = M_PI * (3.0f - sqrt(5.0f));
    dz = 2.0f / ((float)num_points);
    longitude = 0.0f;
    z = 1.0f - dz / 2.0f;
    for(int i = 0; i < num_points; i++) {
        r = sqrt(1.0f - z * z);
        result[i][0] = cos(longitude) * r * radius;
        result[i][1] = sin(longitude) * r * radius;
        result[i][2] = z * radius;
        z = z - dz;
        longitude = longitude + dlong;
    }
}

int main() {
    // Let's read in the file.
    int frame_count = 100;
    vector * sensor_locs = new vector[100];
    ifstream sensor_file("sensor_RightForeArm-1.csv");
    string sensor_line;
    string DELIMITER = ",";
    int count = 0;
    // Skip Header
    getline(sensor_file, sensor_line);
    while(getline(sensor_file, sensor_line)) {
        int delim_pos = sensor_line.find(DELIMITER);
        sensor_line = sensor_line.substr(delim_pos + 1);
        delim_pos = sensor_line.find(DELIMITER);
        for(int i = 0; i < 3; i++) {
            sensor_locs[count][i] = atof(sensor_line.substr(0, delim_pos).c_str());
            delim_pos = sensor_line.find(DELIMITER);
            sensor_line = sensor_line.substr(delim_pos + 1);
        }
        count++;
    }

    int triangle_count = 1498;
    // TODO Set this as an argument to the program.
    vector *** triangles = new vector**[100];
    for (int i = 0; i < 100; i++) {
        triangles[i] = new vector*[1498];
        for(int j = 0; j < 1498; j++){
            triangles[i][j] = new vector[3];
        }
    }
    // vector triangles[100][1498][3];

    for(int i = 0; i < 100; i++) {
        int i_plus_one = i + 1;
        stringstream ss;
        ss << i_plus_one;
        string frame_string;
        ss >>  frame_string;
        string input_file_str;
        input_file_str = "frame" + frame_string + ".csv";
        ifstream input_file(input_file_str.c_str());
        string line;
        string DELIMITER = ",";
        int tri_count = 0;
        while(getline(input_file, line)) {
            int delim_pos = line.find(DELIMITER);
            for(int j = 0; j < 3; j++) {
                for(int k = 0; k < 3; k++) {
                    triangles[i][tri_count][j][k] = atof(line.substr(0, delim_pos).c_str());
                    line = line.substr(delim_pos + 1);
                    delim_pos = line.find(DELIMITER);
                }
            }
            tri_count ++;
        }
    }

    int samples = 300;
    vector * spheres_sample_points = new vector[300];
    sphere_samples(spheres_sample_points, samples, 6.0);

    for (int i = 0; i < frame_count; i++) {
        // Check for interference
        int count = 0;
        for(int j = 0; j < samples; j++) {
            float * result;
            vector res_vect;
            vector ray;
            vector offsetSphere;
            ADDV(offsetSphere, spheres_sample_points[j], sensor_locs[i]);
            SUBV(ray, offsetSphere, sensor_locs[i]);
            for(int k = 0; k < triangle_count; k++) {
                result= intersect_ray_tri(triangles[i][k][0], triangles[i][k][1],
                                  triangles[i][k][2], ray, sensor_locs[i]);
                if(result != 0) {
                    res_vect[0] = result[0]; res_vect[1] = result[1]; res_vect[2] = result[2];
                    if(isInBetw(res_vect, sensor_locs[i], offsetSphere))  {
                        count ++;
                        break;
                    }
                }
            }
            delete result;
        }
        printf("%d\n", count);
    }

    delete sensor_locs;

    return 0;
}
