"""Simple script that samples a sphere's surface non-uniformly."""

import bpy
import mathutils
import math

num_lines = 12

# This should be the height of the body
radius = 5.0

two_pi = math.pi * 2

# TODO Allow the sphere's center to be anywhere, not just at the origin.

rotations = int(math.ceil(num_lines / 2.0))
alpha = 1 / num_lines * two_pi
q = mathutils.Quaternion((math.cos(alpha/2), math.sqrt(1 - math.cos(alpha/2)**2), 0, 0))
for i in range(num_lines):
    rotate_angle = i * alpha

    # Point on the x-y plane.
    origin_vect = mathutils.Vector((math.cos(rotate_angle) * radius, math.sin(rotate_angle) * radius, 0))
    print(str((math.cos(rotate_angle) * radius, math.sin(rotate_angle) * radius, 0)))

    # Rotate the point, but only if it does not fold onto itself.
    if rotate_angle > 0.001 and (rotate_angle > math.pi + 0.001 or rotate_angle < math.pi - 0.001):
        for j in range(1, rotations):
            origin_vect.rotate(q)
            print(str((origin_vect[0], origin_vect[1], origin_vect[2])))
