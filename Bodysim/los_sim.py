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
            my_new_verts = [copy.deepcopy(triangle[i].co) for i in range(3)]

            for i in range(len(my_new_verts)):
                my_new_verts[i].rotate(ob.rotation_euler)
                my_new_verts[i] = my_new_verts[i] + ob.matrix_world.to_translation()

            if geometry.intersect_ray_tri(my_new_verts[0], my_new_verts[1], my_new_verts[2], 
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
        self.sensor_objects = populate_sensor_list(context)
        bpy.app.handlers.frame_change_pre.append(self._stop)
        bpy.context.scene.frame_set(1)
        bpy.ops.screen.animation_play()
        return {'RUNNING_MODAL'}

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
        triangles.append([ob.data.vertices[verts[vert_group][i]] for i in range(3)])
        if len(verts[vert_group]) > 3:
            my_new_verts = [copy.deepcopy(ob.data.vertices[verts[vert_group][i]].co)
                            for i in range(4)]

            for vert in my_new_verts:
                vert.rotate(ob.rotation_euler)

            for i in range(len(my_new_verts)):
                my_new_verts[i] = my_new_verts[i] + ob.matrix_world.to_translation()

            # First check distances between first point to the other two.
            dist_a_b = (my_new_verts[0] - my_new_verts[1]).length
            dist_a_c = (my_new_verts[0] - my_new_verts[2]).length

            other_half = [ob.data.vertices[verts[vert_group][0]],
                          ob.data.vertices[verts[vert_group][3]], 
                          ob.data.vertices[verts[vert_group][2]] if dist_a_c > dist_a_b else
                          ob.data.vertices[verts[vert_group][1]]]

            triangles.append(other_half)

    return triangles

# TODO This method is already defined in simtools panel, so get rid of one of the 
# copies in the future.
def populate_sensor_list(context):
    """Get all the sensors in the scene."""

    print(bpy.data.objects)
    sensor_objects = []
    for i in context.scene.objects['model']['sensor_info']:
        sensor_objects.append(bpy.data.objects['sensor_' + i])
    return sensor_objects
