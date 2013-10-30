"""
Script that binds a cube to a vertex group.

The wire frame of the blender object this is working on must
    have the name "model". The vertex groups must be of this
    "model" object.
""" 

import bpy


def list_vertex_group():
    """Returns a list of names to vertex groups"""
    return bpy.data.objects["model"].vertex_groups.keys()


def parse_vertex_group(groups):
    """Takes in the list of vertex groups and splits them by body part"""
    categories = {}
    for i in groups:
        body_part = i.split("-")[0]
        if body_part not in categories: categories[body_part] = []
        categories[body_part].append(i)
    return categories


def select_vertex_group(vg_name, context):
    """Given a vertex group name, selects and displays it on the screen"""
    bpy.ops.object.mode_set(mode="OBJECT")
    obj = bpy.data.objects["model"]
    context.scene.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="DESELECT")
    bpy.ops.object.vertex_group_set_active(group=vg_name)
    bpy.ops.object.vertex_group_select()
    
def cancel_selection():
    """Go back to object mode after selection"""
    bpy.ops.object.mode_set(mode="OBJECT")

def bind_to_vertex_group(obj, context):
    """ Binds the object passed in to the currently selected vertex group"""
    vg = context.object.vertex_groups.active
    body_obj = bpy.data.objects['model']

    # Bind the obj to a vertex group
    if len(obj.constraints.items()) != 0: 
        print("WARNING: object already has constraint, constraint removed!")
        obj.constraints.clear()
    obj_const = obj.constraints.new(type="CHILD_OF")
    obj_const.target = body_obj
    obj_const.subtarget = vg.name

    # Reset the cube's relative location.
    cube_obj.location = (0.0, 0.0, 0.0)

    cancel_selection()

'''
#Previous testing code
if __name__ == "__main__":
    cube_obj = bpy.data.objects["Cube"]
    body_obj = bpy.data.objects['model']
    print("Vertex groups: ")
    print(list_vertex_group())
    print(parse_vertex_group(list_vertex_group()))
    select_vertex_group("Neck-0")
    bind_to_vertex_group(cube_obj)
'''

class CustomPanel(bpy.types.Panel):
    """A Custom Panel in the Viewport Toolbar"""
    bl_label = "Custom Panel HERE"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label(text="HELLO")
        
        v_list = parse_vertex_group(list_vertex_group())
        for group in v_list:
            row = layout.row()
            row.label(text=group)
            for _part in v_list[group]:
                layout.operator("bodysim.select_body_part", text=_part).part = _part
                        
        # layout.operator("mesh.primitive_plane_add", text="Plane", icon='MESH_PLANE')
        # layout.operator("mesh.primitive_torus_add", text="Torus", icon='MESH_TORUS')
        # layout.operator("", text="Button 1", icon='MESH_TORUS')
        # layout.operator("", text="Button 2", icon='MESH_TORUS')
        # In theory - have another operator as the first argument, 
        # choose a button name, choose a button icon
        # col.operator("mesh.primitive_plane_add", text="Button 3", icon='MESH_TORUS')
        
class BodySim_SELECT_BODY_PART(bpy.types.Operator):
    bl_idname = "bodysim.select_body_part"
    bl_label = "BodySim Select Body Part"
    part = bpy.props.StringProperty()
    
    def execute(self, context):
        select_vertex_group(self.part, context)
            
        return {'FINISHED'}

class BodySim_BIND_SENSOR(bpy.types.Operator):
    bl_idname = "bodysim.bind_sensor"
    bl_label = "BodySim Bind Sensor"

    def execute(self, context):
        sensor = bpy.ops.mesh.primitive_cube_add(location=(0,0,0))
        bind_to_vertex_group(sensor, context)

        return {'FINISHED'}


class BodySim_DESELECT_BODY_PART(bpy.types.Operator):
    bl_idname = "bodysim.deselect_body_part"
    bl_label = "BodySim Deselect Body Part"

    def execute(self, context):
        bpy.ops.object.mode_set(mode="OBJECT")

        return {'FINISHED'}


global classlist
classlist = []
v_list = parse_vertex_group(list_vertex_group())
for bodypart in v_list:
    exec(
'''
class TempCustomPanel%s(bpy.types.Panel):
    """A Custom Panel in the Viewport Toolbar"""
    bl_label = "Custom Panel %s"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label(text=bodypart)
        
        for _part in v_list[bodypart]:
            layout.operator("bodysim.select_body_part", text=_part).part = _part

classlist.append(TempCustomPanel%s)
'''%(bodypart, bodypart, bodypart)
    )

def register():
    global classlist
    bpy.utils.register_class(BodySim_SELECT_BODY_PART)
    bpy.utils.register_class(BodySim_BIND_SENSOR)
    bpy.utils.register_class(BodySim_DESELECT_BODY_PART)

    for c in classlist:
        bpy.utils.register_class(c)


def unregister():
    bpy.utils.unregister_class(CustomPanel)

if __name__ == "__main__":
    register()
    #bpy.utils.register_module(__name__)
