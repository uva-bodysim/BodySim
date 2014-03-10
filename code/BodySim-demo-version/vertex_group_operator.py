"""
Script that binds a cube to a vertex group.

The wire frame of the blender object this is working on must
    have the name "model". The vertex groups must be of this
    "model" object.
""" 

import bpy
from mathutils import *
from math import *

# List of vertices for a model.
# Note that this must be cleared each time a new model is loaded (different
# vertx groups).
panel_list = []

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

def bind_to_text_vg(context):
    object_mode()
        
    model = context.scene.objects['model']
    
    if('sensors' not in model.keys()):
        model['sensors'] = 0

    if('sensor_info' not in model.keys()):
        model['sensor_info'] = {}
    
    context.scene.objects.active = None
    # add cube and scale
    bpy.ops.mesh.primitive_cube_add(location=(0,0,0))
    
    sensor = context.active_object
    sensor.scale = Vector((0.05, 0.05, 0.05))
    sensor.name = 'Sensor_' + str(model['sensors'])
    material = bpy.data.materials.new("Red sensor")
    material.diffuse_color = 1,0,0
    sensor.data.materials.append(material)

    # TODO Change the motion type and color
    bpy.context.scene.objects.active = model
    edit_mode()
    model['sensor_info'][context.object.vertex_groups.active.name] = ('motion', 'red', str(model['sensors']))
    bind_to_vertex_group(sensor, context)
    object_mode()
    model['sensors'] += 1
    
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
def _draw(self, context):
    layout = self.layout
    for _part in self.v_list:
        layout.operator("bodysim.select_body_part", text=_part).part = _part


def draw_body_part_panels():

    global panel_list

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "objectmode"
    if not panel_list:
        v_list = parse_vertex_group(list_vertex_group())
        for group in v_list:

            subpanel = type("PartSelectPanel%s" % group,
                   (bpy.types.Panel, ),
                   {"bl_label": group,
                        "bl_space_type": bl_space_type,
                        "bl_region_type": bl_region_type,
                        "bl_context": bl_context,
                        "bl_options": {"DEFAULT_CLOSED"},
                        "v_list": v_list[group],
                        "draw": _draw},
                   )
            panel_list.append(subpanel)
            bpy.utils.register_class(subpanel)
    else:
        for panel in panel_list:
            bpy.utils.register_class(panel)

class AddSensorPanel(bpy.types.Panel):
    """A Custom Panel in the Viewport Toolbar"""
    bl_label = "Add Sensor"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "objectmode"
    
    def draw(self, context):
        layout = self.layout
        layout.operator("bodysim.new_sensor", text="Add Sensor")
        layout.operator("bodysim.reset_sensors", text="Reset Sensors")

def _drawSingleSensorButtons(self, context):
    layout = self.layout
    for sensor in self.sensor_dict:
        row = layout.row(align = True)
        row.alignment = 'EXPAND'
        row.operator("bodysim.select_body_part", text = sensor).part = sensor
        row.operator("bodysim.delete_sensor", text = "Delete").part = sensor

def draw_sensor_list_panel(sensor_dict):
    bl_label = "Current Sensors"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "objectmode"

    panel = type("CurrentSensorsPanel", (bpy.types.Panel,),{
        "bl_label": bl_label,
        "bl_space_type": bl_space_type,
        "bl_region_type": bl_region_type,
        "sensor_dict": sensor_dict,
        "draw": _drawSingleSensorButtons},)

    bpy.utils.register_class(panel)
    
class CurrentSensorsPanel(bpy.types.Panel):
    bl_label = "Current Sensors"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        layout.label("No sensors yet.")

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
        bind_to_text_vg(context)
        model = context.scene.objects['model']
        draw_sensor_list_panel(model['sensor_info'])
        return {'FINISHED'}

class BodySim_DELETE_SENSOR(bpy.types.Operator):
    bl_idname = "bodysim.delete_sensor"
    bl_label = "BodySim Delete Sensor"
    part = bpy.props.StringProperty()

    def execute(self, context):
        object_mode()
        context.scene.objects.active = None
        model = context.scene.objects['model']
        bpy.context.scene.objects.active = model
        bpy.data.objects["Sensor_" +  model['sensor_info'][self.part][2]].select = True
        bpy.ops.object.delete()
        edit_mode()
        cancel_selection()
        del model['sensor_info'][self.part]
        draw_sensor_list_panel(model['sensor_info'])
        return {'FINISHED'}

def _draw_sensor_properties(self, context):
    layout = self.layout
    layout.operator("bodysim.sensor_properties", text="Next")

class BodySim_NEW_SENSOR(bpy.types.Operator):
    bl_idname = "bodysim.new_sensor"
    bl_label = "Create a new sensor"

    def execute(self, context):
        redraw_addSensorPanel(_draw_sensor_properties)
        draw_body_part_panels()
        return {'FINISHED'}

def _draw_sensor_properties_page(self, context):
    layout = self.layout
    layout.operator("bodysim.bind_sensor", text="Add Sensor")

def redraw_addSensorPanel(draw_function):
    bl_label = "Add Sensor"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "objectmode"

    panel = type("AddSensorPanel", (bpy.types.Panel,),{
    "bl_label": "Add Sensor",
    "bl_space_type": bl_space_type,
    "bl_region_type": bl_region_type,
    "draw": draw_function},)

    bpy.utils.register_class(panel)

class BodySim_SENSOR_PROPERTIES(bpy.types.Operator):
    bl_idname = "bodysim.sensor_properties"
    bl_label = "Bodysim Properties"

    def execute(self, context):
        redraw_addSensorPanel(_draw_sensor_properties_page)
        for panel in panel_list:
            bpy.utils.unregister_class(panel)
        return {'FINISHED'}

class BodySim_RESET_SENSORS(bpy.types.Operator):
    bl_idname = "bodysim.reset_sensors"
    bl_label = "BodySim Reset All Sensors"

    def execute(self, context):
        object_mode()
        model = context.scene.objects['model']
        context.scene.objects.active = None
        model['sensors'] = 0
        model['sensor_info'] = {}
        bpy.context.scene.objects.active = model
        sensors_to_delete = [item.name for item in bpy.data.objects if item.name.startswith("Sensor")]

        for sensor in sensors_to_delete:
            bpy.data.objects[sensor].select = True

        bpy.ops.object.delete()
        edit_mode()
        cancel_selection()
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
