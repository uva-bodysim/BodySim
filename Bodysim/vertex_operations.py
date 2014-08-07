"""Provides operations on vertex groups of the model."""

import bpy
from mathutils import *

def list_vertex_group():
    """Returns a list of names to vertex groups"""

    return bpy.data.objects["model"].vertex_groups.keys()

def parse_vertex_group(groups):
    """Takes in the list of vertex groups and splits them by body
     part.
    """

    categories = {}
    for i in groups:
        body_part = i.split("-")[0]
        if body_part not in categories: categories[body_part] = []
        categories[body_part].append(i)
    return categories

def bind_sensor_to_active_vg(context, color_tuple):
    """Binds a sensor to the active vertex group
     Optionally adds color to the sensor if color_tuple is specified.
    """

    object_mode()

    model = context.scene.objects['model']
    
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
    
    bpy.context.scene.objects.active = model
    edit_mode()
    sensor.name = 'sensor_' + context.object.vertex_groups.active.name
    model['current_vg'] = context.object.vertex_groups.active.name
    _bind_to_vertex_group(sensor, context)
    object_mode()
    return sensor.name

def _bind_to_vertex_group(obj, context):
    """Binds the object passed in to the currently selected vertex
     group.
    """

    vg = context.object.vertex_groups.active
    body_obj = bpy.data.objects['model']

    # Bind the obj to a vertex group
    if len(obj.constraints.items()) != 0: 
        print("WARNING: object already has constraint, constraint removed!")
        obj.constraints.clear()
    obj_const = obj.constraints.new(type="CHILD_OF")
    obj_const.target = body_obj
    obj_const.subtarget = vg.name

    # Reset the cube's relative location. Add extra 0.05 at the end so the sensor
    # is not half buried in the body.
    obj.location = (0.0, 0.0, 0.05)

    cancel_selection()

def select_vertex_group(vg_name, context):
    """Given a vertex group name vg_name, selects and displays it on
     the screen.
    """

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

