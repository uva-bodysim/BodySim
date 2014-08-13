"""Output location information."""

import bpy
import copy
import math
import os
import mathutils
import Bodysim.file_operations

class OutputLocationOperator(bpy.types.Operator):
    """Writes location information to file."""

    bl_idname = "bodysim.output_locs"
    bl_label = "Output locations."

    frame_start = 1# bpy.props.IntProperty()
    frame_end = 100 #bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return True

    def _stop(self, context):
        scene = bpy.context.scene
        # Create a new file to hold info for this frame.
        triangles = get_triangles()
        with open('frame' + str(scene.frame_current) + '.csv', 'w') as f:
            for triangle in triangles:
                f.write(",".join([str(dim) for point in triangle for dim in point]) + '\n')

        if scene.frame_current == self.frame_end:
            bpy.ops.screen.animation_cancel(restore_frame=True)
            bpy.app.handlers.frame_change_pre.remove(self._stop)
            return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def execute(self, context):
        # Blender can only stop the animation via a frame event handler...

        bpy.app.handlers.frame_change_pre.append(self._stop)
        bpy.context.scene.frame_set(self.frame_start)
        bpy.ops.screen.animation_play()

        return {'RUNNING_MODAL'}

def get_triangles():
    """Converts all vertex groups of the model into triangles if necessary.
       This is needed because some vertex groups have four vertices.
    """
    ob = bpy.data.objects["model"]

    triangles = []

    # http://blender.stackexchange.com/questions/3462/vertex-coordinate-after-pose-change
    # Need to apply modifiers to the object, creating a mesh that will store
    # coordinate information of all vertices for the current frame.
    modified_mesh = ob.to_mesh(scene=bpy.context.scene, apply_modifiers=True,
                               settings='PREVIEW')
    modified_mesh.transform(ob.matrix_world)

    for polygon in modified_mesh.polygons:
        polygon_vertex_list = [modified_mesh.vertices[vert_index].co
                               for vert_index in polygon.vertices]
        triangles.append([polygon_vertex_list[i] for i in range(3)])

        if len(polygon_vertex_list) > 3:
            dist_a_b = (polygon_vertex_list[0] - polygon_vertex_list[1]).length
            dist_a_c = (polygon_vertex_list[0] - polygon_vertex_list[2]).length
            dist_a_d = (polygon_vertex_list[0] - polygon_vertex_list[3]).length
            other_half = [polygon_vertex_list[3]]
            max_dist = max(dist_a_b, dist_a_c, dist_a_d)

            if max_dist == dist_a_b:
                other_half.extend([polygon_vertex_list[0], polygon_vertex_list[1]])

            elif max_dist == dist_a_c:
                other_half.extend([polygon_vertex_list[0], polygon_vertex_list[2]])

            elif max_dist == dist_a_d:
                other_half.extend([polygon_vertex_list[1], polygon_vertex_list[2]])

            else:
                bpy.ops.bodysim.message('INVOKE_DEFAULT', msg_type = "Error",
                                        message = 'LOS determination failed.')
                raise Exception("Something went wrong with Max function.")

            triangles.append(other_half)

    return triangles
