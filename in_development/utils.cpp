#include "vectmath.h"
#include <math.h>

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