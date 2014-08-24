"""Tracks sensor loctation, rotation, and body vertex locations."""

import bpy
import copy
import math
import os
import shutil
import mathutils
import Bodysim.file_operations
import Bodysim.sim_params

class TrackSensorOperator(bpy.types.Operator):
    """Logs location and rotation of sensors along respective paths.
     Rotation in quaternions.
    """

    bl_idname = "bodysim.track_sensors"
    bl_label = "Track Sensors"

    frame_start = bpy.props.IntProperty()
    frame_end = bpy.props.IntProperty()
    path = bpy.props.StringProperty()
    sensor_objects = None
    trajectory_data = []
    sample_count = bpy.props.IntProperty()
    sphere_samples = None

    @classmethod
    def poll(cls, context):
        return True

    def _stop(self, context):
        scene = bpy.context.scene
        for i in range(len(self.sensor_objects)):
            # World space coordinates
            translation_vector = self.sensor_objects[
                i].matrix_world.to_translation()
            x = translation_vector[0]
            y = translation_vector[1]
            z = translation_vector[2]

            # Rotation
            rotation_vector = self.sensor_objects[
                i].matrix_world.to_quaternion()
            w = rotation_vector[0]
            rx = rotation_vector[1]
            ry = rotation_vector[2]
            rz = rotation_vector[3]

            # Store trajectory data
            output = "{0},{1},{2},{3},{4},{5},{6},{7}\n".format(
                scene.frame_current, x, y, z, w, rx, ry, rz)
            self.trajectory_data[i].append(output)

            triangles = get_triangles()
            with open(Bodysim.sim_params.triangles_path + os.sep + 'frame' + str(scene.frame_current) + '.csv', 'w') as f:
                for triangle in triangles:
                    f.write(",".join([str(dim) for point in triangle for dim in point]) + '\n')

        if scene.frame_current == self.frame_end:
            bpy.ops.screen.animation_cancel(restore_frame=True)
            bpy.app.handlers.frame_change_pre.remove(self._stop)

            # Write trajectory and wireless channel data.
            Bodysim.file_operations.write_results(self.trajectory_data,
                                                  self.sensor_objects,
                                                  self.path + os.sep + 'Trajectory')

            # Run the external simulators once all results have been written.
            Bodysim.file_operations.execute_simulators(scene.objects['model']['current_simulation_path'])
            return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def execute(self, context):
        # In blender, the z - "dimension" is strangely at index 1, not 2;
        # The matrix world z is at index 2...
        Bodysim.sim_params.height = max(bpy.data.objects["model"].dimensions)

        self.sensor_objects = populate_sensor_list(context)
        for i in range(len(self.sensor_objects)):
            self.trajectory_data.append([])
            self.trajectory_data[i].append("frame,x,y,z,w,rx,ry,rz\n")

        # Remove all existing triangle data in triangles_path
        if os.path.exists(Bodysim.sim_params.triangles_path):
            shutil.rmtree(Bodysim.sim_params.triangles_path)

        os.mkdir(Bodysim.sim_params.triangles_path)

        # Blender can only stop the animation via a frame event handler...
        bpy.app.handlers.frame_change_pre.append(self._stop)
        bpy.context.scene.frame_set(self.frame_start)
        bpy.ops.screen.animation_play()

        return {'RUNNING_MODAL'}


def populate_sensor_list(context):
    """Get all the sensors in the scene."""

    print(bpy.data.objects)
    sensor_objects = []
    for i in context.scene.objects['model']['sensor_info']:
        sensor_objects.append(bpy.data.objects['sensor_' + i])
    return sensor_objects

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
