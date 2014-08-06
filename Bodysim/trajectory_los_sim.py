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
    triangles = None
    sample_count = bpy.props.IntProperty()
    sphere_samples = None
    sim_dict = None

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

            # Deal with the sphere
            no_los_count = 0
            for sample in self.sphere_samples:
                ray = translation_vector - mathutils.Vector((x + sample[0],
                                                            y + sample[1],
                                                            z + sample[2]))
                # Check if any part of the body interferes with this ray
                for triangle in self.triangles:
                    if not has_los(triangle, ray, translation_vector):
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

                ray = translation_vector - self.sensor_objects[j].matrix_world.to_translation()
                los = True
                for triangle in self.triangles:
                    if not has_los(triangle, ray, translation_vector):
                        los = False
                        break

                direct_los_row = direct_los_row + ',' + str(los)

            # Output the los row
            self.direct_los_data[i].append(direct_los_row + '\n')

        if scene.frame_current == self.frame_end + 1:
            bpy.ops.screen.animation_cancel(restore_frame=True)
            bpy.app.handlers.frame_change_pre.remove(self._stop)
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
            Bodysim.file_operations.execute_simulators(scene.objects['model']['current_simulation_path'],
                                                       sim_dict)
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

def has_los(triangle, ray, origin):
    """Clean wrapper for intersect_ray_tri."""
    return (mathutils.geometry.intersect_ray_tri(triangle[0], triangle[1],
                                                 triangle[2], ray, origin, True)
            is None)

def populate_sensor_list(context):
    """Get all the sensors in the scene."""

    print(bpy.data.objects)
    sensor_objects = []
    for i in context.scene.objects['model']['sensor_info']:
        sensor_objects.append(bpy.data.objects['sensor_' + i])
    return sensor_objects

def vert_to_real_world(my_vertex, ob):
    new_vert = copy.deepcopy(my_vertex.co)
    new_vert.rotate(ob.rotation_euler)
    new_vert = new_vert + ob.matrix_world.to_translation()
    return new_vert

def get_triangles():
    """Converts all vertex groups of the model into triangles if necessary.
       This is needed because some vertex groups have four vertices.
    """
    ob = bpy.data.objects["model"]

    # Dictionary mapping vertex group index to its name
    group_lookup = {g.index: g.name for g in ob.vertex_groups}

    # Dictionary mapping vertex group names to the indicies of vertices that make
    # up the group.
    verts = {name: [] for name in group_lookup.values()}

    # Go through each vertex and see what group it is a part of.
    for v in ob.data.vertices:
       for g in v.groups:
           verts[group_lookup[g.group]].append(v.index)
           
    triangles = []
    for vert_group in verts:
        real_world_vert_group = [vert_to_real_world(ob.data.vertices[verts[vert_group][i]], ob)
                                 for i in range(len(verts[vert_group]))]
        triangles.append([real_world_vert_group[i] for i in range(3)])

        # Must split vertex groups that have four vertices into two triangles.
        # We already have the first triangle, so calculate the second one.
        if len(verts[vert_group]) > 3:
            # First check distances between first point to the other two.
            dist_a_b = (real_world_vert_group[0] - real_world_vert_group[1]).length
            dist_a_c = (real_world_vert_group[0] - real_world_vert_group[2]).length

            other_half = [real_world_vert_group[0],
                          real_world_vert_group[3],
                          real_world_vert_group[2] if dist_a_c > dist_a_b else
                          real_world_vert_group[1]]

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
