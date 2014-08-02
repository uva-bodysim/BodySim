import bpy
import copy
from mathutils import *

# Hard coded to check LOS between first two sensors for now.
class LOSSimulationOperator(bpy.types.Operator):
    """Operator that starts the line-of-sight simulation"""

    bl_idname = "bodysim.los_sim"
    bl_label = "Perform a line-of-sight simulation."
    sensor_objects = None
    triangles = None

    @classmethod
    def poll(cls, context):
        return True

    def _stop(self, context):
        ob = bpy.data.objects["model"]
        scene = bpy.context.scene
        intersection = False
        # Now go through each triangle
        ray = self.sensor_objects[0].matrix_world.to_translation() - \
              self.sensor_objects[1].matrix_world.to_translation()
        for triangle in self.triangles:
            if geometry.intersect_ray_tri(triangle[0], triangle[1], triangle[2],
                                 ray, self.sensor_objects[1].matrix_world.to_translation(), True) is not None:
                intersection = True
                break

        print(intersection)

        if scene.frame_current == 101:
            bpy.ops.screen.animation_cancel(restore_frame=True)
            bpy.app.handlers.frame_change_pre.remove(self._stop)
            return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def execute(self, context):
        # Blender can only stop the animation via a frame event handler...
        self.triangles = get_triangles()
        print(str(get_max_height(self.triangles)))
        self.sensor_objects = populate_sensor_list(context)
        bpy.app.handlers.frame_change_pre.append(self._stop)
        bpy.context.scene.frame_set(1)
        bpy.ops.screen.animation_play()
        return {'RUNNING_MODAL'}

def vert_to_real_world(my_vertex, ob):
    new_vert = copy.deepcopy(my_vertex.co)
    new_vert.rotate(ob.rotation_euler)
    new_vert = new_vert + ob.matrix_world.to_translation()
    return new_vert

def get_triangles():
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

def get_max_height(triangles):
    max_z = 0
    min_z = 1000
    for triangle in triangles:
        for vertex in triangle:
            z_position = vertex[2]
            max_z = z_position if z_position > max_z else max_z
            min_z = z_position if z_position < min_z else min_z

    return max_z - min_z

# TODO This method is already defined in simtools panel, so get rid of one of the 
# copies in the future.
def populate_sensor_list(context):
    """Get all the sensors in the scene."""

    print(bpy.data.objects)
    sensor_objects = []
    for i in context.scene.objects['model']['sensor_info']:
        sensor_objects.append(bpy.data.objects['sensor_' + i])
    return sensor_objects
