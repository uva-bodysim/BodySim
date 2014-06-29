import bpy
from mathutils import *
from math import *

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

def bind_to_text_vg(context, color_tuple):
    object_mode()
        
    model = context.scene.objects['model']
    
    if('sensor_info' not in model.keys()):
        model['sensor_info'] = {}

    if('current_vg' not in model.keys()):
        model['current_vg'] = ""
    
    context.scene.objects.active = None
    # add cube and scale
    bpy.ops.mesh.primitive_cube_add(location=(0,0,0))
    
    sensor = context.active_object
    sensor.scale = Vector((0.05, 0.05, 0.05))

    if color_tuple:
        material = bpy.data.materials.new("SensorColor")
        material.diffuse_color = color_tuple
        sensor.data.materials.append(material)
        context.scene.objects[sensor.name].sensor_color = color_tuple
    
    # TODO Change the motion type and color
    bpy.context.scene.objects.active = model
    edit_mode()
    sensor.name = 'sensor_' + context.object.vertex_groups.active.name
    model['current_vg'] = context.object.vertex_groups.active.name
    bind_to_vertex_group(sensor, context)
    object_mode()
    return sensor.name

def select_vertex_group(vg_name, context):
    """Given a vertex group name, selects and displays it on the screen"""
    bpy.ops.object.mode_set(mode="OBJECT")
    obj = bpy.data.objects["model"]
    context.scene.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="DESELECT")
    bpy.ops.object.vertex_group_set_active(group=vg_name)
    bpy.ops.object.vertex_group_select()
    model = context.scene.objects['model']
    model['sensor_selected'] = True

def object_mode():
    bpy.ops.object.mode_set(mode="OBJECT")
    
def edit_mode():
    bpy.ops.object.mode_set(mode="EDIT")

    
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
