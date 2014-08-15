#ifndef __UTILS_H__
#define __UTILS_H__

float * intersect_ray_tri(vector v1, vector v2, vector v3, vector ray, vector origin);

bool isInBetw(vector pt, vector begin, vector end);

void sphere_samples(vector * result, int num_points, float radius);

#endif