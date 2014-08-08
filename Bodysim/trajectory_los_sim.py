"""Tracks sensor loctation, rotation, and LOS info."""

import bpy
import copy
import math
import os
import mathutils
import Bodysim.file_operations

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

    # Stores free space wireless channel model data
    body_interference_data = []

    # Stores direct LOS data between sensors
    direct_los_data = []

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

            # Deal with the sphere
            no_los_count = 0
            for sample in self.sphere_samples:
                sample_vector = mathutils.Vector((x + sample[0], y + sample[1],
                                                  z + sample[2]))
                # Check if any part of the body interferes with this ray
                for triangle in triangles:
                    if not has_los(triangle, translation_vector, sample_vector):
                        no_los_count += 1
                        break

            # Output the ratio of lines that got blocked to the total number of samples.
            output = "{0},{1}\n".format(scene.frame_current, no_los_count / self.sample_count)
            self.body_interference_data[i].append(output)

            # Deal with direct LOS between this and other sensors
            # TODO Should probably add a header to label columns
            direct_los_row = str(scene.frame_current)
            for j in range(len(self.sensor_objects)):
                if j == i:
                    continue

                los = True
                for triangle in triangles:
                    if not has_los(triangle, translation_vector,
                                   self.sensor_objects[j].matrix_world.to_translation()):
                        los = False
                        break

                direct_los_row = direct_los_row + ',' + str(los)

            # Output the los row
            self.direct_los_data[i].append(direct_los_row + '\n')

        if scene.frame_current == self.frame_end + 1:
            bpy.ops.screen.animation_cancel(restore_frame=True)
            bpy.app.handlers.frame_change_pre.remove(self._stop)

            # Write trajectory and wireless channel data.
            Bodysim.file_operations.write_results(self.trajectory_data, 
                                                  self.sensor_objects,
                                                  self.path + os.sep + 'Trajectory')
            Bodysim.file_operations.write_results(self.body_interference_data,
                                                  self.sensor_objects,
                                                  self.path + os.sep + 'BodyInterference')
            Bodysim.file_operations.write_results(self.direct_los_data,
                                                  self.sensor_objects,
                                                  self.path + os.sep + 'DirectLOS')

            # Run the external simulators once all results have been written.
            Bodysim.file_operations.execute_simulators(scene.objects['model']['current_simulation_path'])
            return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def execute(self, context):
        self.triangles = get_triangles()
        # In blender, the z - "dimension" is strangely at index 1, not 2;
        # The matrix world z is at index 2...
        self.sphere_samples = get_sphere_samples(self.sample_count,
                                                max(bpy.data.objects["model"].dimensions))
        # Blender can only stop the animation via a frame event handler...
        self.sensor_objects = populate_sensor_list(context)
        for i in range(len(self.sensor_objects)):
            self.trajectory_data.append([])
            self.body_interference_data.append([])
            self.direct_los_data.append([])
            # Make the headers
            self.trajectory_data[i].append("frame,x,y,z,w,rx,ry,rz\n")
            self.body_interference_data[i].append("frame,no_los-to-total-ratio\n")
            direct_los_header = "frame"
            for j in range(len(self.sensor_objects)):
                if i != j:
                    direct_los_header = direct_los_header + ',' + self.sensor_objects[j].name

            direct_los_header = direct_los_header + '\n'
            self.direct_los_data[i].append(direct_los_header)

        bpy.app.handlers.frame_change_pre.append(self._stop)
        bpy.context.scene.frame_set(self.frame_start)
        bpy.ops.screen.animation_play()

        return {'RUNNING_MODAL'}

def has_los(triangle, pt1, pt2):
    """Checks if there is LOS of between two points and a possible intefering
        triangle.
        First, see if the RAY (pt1 - pt2) intersects with the triangle.
        Then, see if that point of intersection lies on the SEGMENT (pt1 - pt2).
    """
    poss_interf = mathutils.geometry.intersect_ray_tri(triangle[0], triangle[1],
                                                       triangle[2], pt1 - pt2,
                                                       pt1, True)
    if poss_interf:
        return not isInBetween(poss_interf, pt1, pt2)

    return True

def isInBetween(pt, begin, end, tolerance=0.001):
    """Checks if pt is on the line segment defined by begin and end vertices.

     The closer tolerance is closer to 0, the more precise the result is.

     Must check 1) cross prod(end - begin) and (pt - begin) = 0
                2) dot prod (end - begin) and (pt - begin) is not negative
                3) dot prod (end - begin) and (pt - begin) > dist(begin, end)^2
     for a point to be between the defined line segment.
    """
    dot_product = (end - begin).dot(pt - begin)
    return ((((end - begin).cross(pt - begin)).magnitude < tolerance) and
            dot_product >= 0 and
            dot_product < (end - begin).length * (end - begin).length)

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

def get_sphere_samples(numberOfPoints=45, radius=10):
    """ Returns a list of 3-tuple x,y,z samples of the surface of a sphere.
        converted from:  http://web.archive.org/web/20120421191837/http://www.cgafaq.info/wiki/Evenly_distributed_points_on_sphere ) 
    """
    dlong = math.pi * (3.0 - math.sqrt(5.0))  # ~2.39996323 
    dz   =  2.0 / numberOfPoints
    longitude =  0.0
    z    =  1.0 - dz / 2.0
    ptsOnSphere =[]
    for k in range( 0, numberOfPoints): 
        r    = math.sqrt(1.0 - z * z)
        ptNew = (math.cos(longitude) * r * radius, math.sin(longitude) * r * radius, z * radius)
        ptsOnSphere.append(ptNew)
        z    = z - dz
        longitude = longitude + dlong
    return ptsOnSphere
