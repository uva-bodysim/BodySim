"""
Checks for interference between two cubes without using the Blender Game Engine,
assuming the interfering object is also a cube.
"""

import bpy
import copy
import mathutils

# List of vertices that make up each face of a standard cube.
FACE_LIST = [[0, 1, 4, 5],
             [1, 2, 5, 6],
             [2, 3, 6, 7],
             [0, 3, 4, 7],
             [0, 1, 2, 3],
             [4, 5, 6, 7]]

intersect_ray_tri = mathutils.geometry.intersect_ray_tri

def main():
    """ Check for interference between cubes."""

    tri_list = square_face_list_to_tri_list(FACE_LIST)
    cube_object_1 = bpy.data.objects["cube_0"]
    cube_object_2 = bpy.data.objects["cube_1"]
    cube_int_object = bpy.data.objects["cube_int"]
    print(has_interference(tri_list, cube_object_1, cube_object_2,
                           cube_int_object))

def square_face_list_to_tri_list(face_list):
    """Convert list of faces (via a list of vertices) to list of triangles."""

    tri_list = []
    for face in face_list:
        tri_vertices_1 = [face[0], face[1], face[2]]
        tri_vertices_2 = [face[1], face[2], face[3]]
        tri_list.append(tri_vertices_1)
        tri_list.append(tri_vertices_2)
    return tri_list

def has_interference(tri_list, cube_object_1, cube_object_2, interfering_object):
    """
    Checks for interference between two cubes without Blender Game Engine.

    Assuming that the interfering object is also a cube.
    """

    ray = cube_object_1.matrix_world.to_translation() - \
          cube_object_2.matrix_world.to_translation()
    for tri in tri_list:
        verts = get_mesh_vertex_location(tri[0], tri[1], tri[2], cube_object_2)

        if intersect_ray_tri(verts[0], verts[1], verts[2], ray,
                             cube_object_1.matrix_world.to_translation(),True) is not None:
            for tri in tri_list:
                int_verts = get_mesh_vertex_location(tri[0], tri[1], tri[2], interfering_object)
                if intersect_ray_tri(int_verts[0], int_verts[1], int_verts[2], ray,
                                     cube_object_1.matrix_world.to_translation(), True) is not None:
                    return True
    return False

def get_mesh_vertex_location(v0, v1, v2, object):
    """Get the location in real space of the vertex an object."""

    vertex_loc_0 = copy.deepcopy(object.data.vertices[v0].co)
    vertex_loc_1 = copy.deepcopy(object.data.vertices[v1].co)
    vertex_loc_2 = copy.deepcopy(object.data.vertices[v2].co)

    vertex_loc_0.rotate(object.rotation_euler)
    vertex_loc_1.rotate(object.rotation_euler)
    vertex_loc_2.rotate(object.rotation_euler)

    vertex_loc_0 = vertex_loc_0 + object.matrix_world.to_translation()
    vertex_loc_1 = vertex_loc_1 + object.matrix_world.to_translation()
    vertex_loc_2 = vertex_loc_2 + object.matrix_world.to_translation()

    return vertex_loc_0, vertex_loc_1, vertex_loc_2

if __name__ == '__main__':
    main()
