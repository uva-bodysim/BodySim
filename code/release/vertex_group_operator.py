"""
Script that binds a cube to a vertex group.

The wire frame of the blender object this is working on must
    have the name "model". The vertex groups must be of this
    "model" object.
""" 

import bpy
from mathutils import *
from math import *

'''
Functions
'''

def object_mode():
    bpy.ops.object.mode_set(mode="OBJECT")
    
def edit_mode():
    bpy.ops.object.mode_set(mode="EDIT")
    

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
    print(vg)
    body_obj = bpy.data.objects['model']

    # Bind the obj to a vertex group
    if len(obj.constraints.items()) != 0: 
        print("WARNING: object already has constraint, constraint removed!")
        obj.constraints.clear()
    obj_const = obj.constraints.new(type="CHILD_OF")
    obj_const.target = body_obj
    obj_const.subtarget = vg.name

    # Reset the cube's relative location.
    obj.location = (0.0, 0.0, 0.0)

    cancel_selection()


'''
Panels
'''
# This function is called by the subpanel for the body part
def _draw(self, context):
    layout = self.layout

    #row = layout.row()
    #row.label(text=self.group)
    for _part in self.v_list:
        layout.operator("bodysim.select_body_part", text=_part).part = _part


def draw_body_part_panels():
    #layout = self.layout

    #row = layout.row()
    #row.label(text="HELLO")

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    
    v_list = parse_vertex_group(list_vertex_group())
    for group in v_list:

        subpanel = type("PartSelectPanel%s" % group,
               (bpy.types.Panel, ),
               {"bl_label": group, 
                    "bl_space_type": bl_space_type,
                    "bl_region_type": bl_region_type,
                    "bl_options": {"DEFAULT_CLOSED"},
                    "v_list": v_list[group],
                    "draw": _draw},
               )
        bpy.utils.register_class(subpanel)

        
class AddSensorPanel(bpy.types.Panel):
    """A Custom Panel in the Viewport Toolbar"""
    bl_label = "Add Sensor"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    
    def draw(self, context):
        layout = self.layout
        
        layout.operator("bodysim.bind_sensor", text="Add Sensor")
    
    
'''
Operators
=========
'''

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
        object_mode()
        
        model = context.scene.objects['model']
        
        if('sensors' not in model.keys()):
            model['sensors'] = 0
        
        context.scene.objects.active = None
        # add cube and scale
        bpy.ops.mesh.primitive_cube_add(location=(0,0,0))
        
        sensor = context.active_object
        sensor.scale = Vector((0.05, 0.05, 0.05))
        sensor.name = 'Sensor_' + str(model['sensors'])
        material = bpy.data.materials.new("Red sensor")
        material.diffuse_color = 1,0,0
        sensor.data.materials.append(material)
        
        model['sensors'] += 1
        bpy.context.scene.objects.active = model
        edit_mode()
        bind_to_vertex_group(sensor, context)

        return {'FINISHED'}


class BodySim_DESELECT_BODY_PART(bpy.types.Operator):
    bl_idname = "bodysim.deselect_body_part"
    bl_label = "BodySim Deselect Body Part"

    def execute(self, context):
        bpy.ops.object.mode_set(mode="OBJECT")

        return {'FINISHED'}

def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
    draw_body_part_panels()
