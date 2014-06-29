"""
Script that binds a cube to a vertex group.

The wire frame of the blender object this is working on must
    have the name "model". The vertex groups must be of this
    "model" object.
""" 

import bpy
import os
import Bodysim.sensor_addition
import Bodysim.vertex_operations
import Bodysim.current_sensors_panel
import Bodysim.plugins_info
from bpy.props import FloatVectorProperty, StringProperty
from xml.etree.ElementTree import ElementTree as ET
from xml.etree.ElementTree import *

current_graph_panel = None

def update_color(self, context):
    context.scene.objects.active = context.scene.objects[self.name]
    while self.data.materials:
        self.data.materials.pop()

    material = bpy.data.materials.new("SensorColor")
    material.diffuse_color = context.scene.objects[self.name].sensor_color
    self.data.materials.append(material)

bpy.types.Object.sensor_color = FloatVectorProperty(name="sensor_color",
    subtype='COLOR',
    default=(1.0, 1.0, 1.0),
    min=0.0, max=1.0,
    description="color picker",
    update=update_color,
    )

bpy.types.Object.sensor_name = StringProperty(name="sensor_name")

class BodySim_LOCATE_BODY_PART(bpy.types.Operator):
    bl_idname = "bodysim.locate_body_part"
    bl_label = "BodySim Locate Body Part"
    part = bpy.props.StringProperty()

    def execute(self, context):
        Bodysim.vertex_operations.select_vertex_group(self.part, context)
        bpy.ops.view3d.view_selected()
        return {'FINISHED'}

class Bodysim_EDIT_SENSOR(bpy.types.Operator):
    bl_idname = "bodysim.edit_sensor"
    bl_label = "BodySim Edit Sensor"
    part = bpy.props.StringProperty()

    def execute(self, context):
        model = context.scene.objects['model']
        model['current_vg'] = self.part
        Bodysim.sensor_addition.redraw_addSensorPanel(Bodysim.sensor_addition._draw_sensor_properties_page)
        Bodysim.sensor_addition.draw_plugins_subpanels(Bodysim.plugins_info.plugins)
        return {'FINISHED'}

class BodySim_SELECT_BODY_PART(bpy.types.Operator):
    bl_idname = "bodysim.select_body_part"
    bl_label = "BodySim Select Body Part"
    part = bpy.props.StringProperty()
    
    def execute(self, context):
        Bodysim.vertex_operations.select_vertex_group(self.part, context)
        return {'FINISHED'}


class BodySim_DELETE_SENSOR(bpy.types.Operator):
    bl_idname = "bodysim.delete_sensor"
    bl_label = "BodySim Delete Sensor"
    part = bpy.props.StringProperty()

    def execute(self, context):
        Bodysim.vertex_operations.object_mode()
        context.scene.objects.active = None
        model = context.scene.objects['model']
        bpy.context.scene.objects.active = model
        for sensor in model['sensor_info']:
            bpy.data.objects["sensor_" + sensor].select = False

        bpy.data.objects["sensor_" + self.part].select = True
        bpy.ops.object.delete()
        model['sensor_info'].pop(self.part)
        if model['sensor_info']:
            Bodysim.current_sensors_panel.draw_sensor_list_panel(model['sensor_info'])
        else:
            Bodysim.current_sensors_panel.draw_sensor_list_panel(None)
        return {'FINISHED'}


class BodySim_CLEAR_SELECTION(bpy.types.Operator):
    bl_idname = "bodysim.clear_selection"
    bl_label = "Clear selected sensors"

    def execute(self, context):
        Bodysim.vertex_operations.cancel_selection()
        bpy.ops.view3d.view_all()
        return {'FINISHED'}

def draw_GraphSelectionPanel(part):
    bl_label = "Graph Sensors"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "objectmode"

    global current_graph_panel

    current_graph_panel = type("GraphingPanel", (bpy.types.Panel,),{
    "bl_label": "Graph Sensor " + part,
    "bl_space_type": bl_space_type,
    "bl_region_type": bl_region_type,
    "part": part,
    "draw": _draw_selected_simvars},)

    bpy.utils.register_class(current_graph_panel)

def _draw_selected_simvars(self, context):
    layout = self.layout
    column = layout.column()
    plugins = Bodysim.plugins_info.plugins
    for simulator in plugins:
        for variable in plugins[simulator]['variables']:
            if getattr(context.scene.objects['sensor_' + self.part], simulator + variable):
                column.prop(context.scene.objects['sensor_' + self.part], 'GRAPH_' + simulator + variable)

    column.operator("bodysim.graph_return", text = "Return")

class GraphButton(bpy.types.Operator):
    bl_idname = "bodysim.graph_select"
    bl_label = "Select variables to graph"
    part = bpy.props.StringProperty()

    def execute(self, context):
        bpy.utils.unregister_class(Bodysim.current_sensors_panel.current_sensor_panel)
        draw_GraphSelectionPanel(self.part)
        return {'FINISHED'}

class ReturnToCurrentSensors(bpy.types.Operator):
    bl_idname = "bodysim.graph_return"
    bl_label = "Return to current sensor list"

    def execute(self, context):
        bpy.utils.unregister_class(current_graph_panel)
        bpy.utils.register_class(Bodysim.current_sensors_panel.current_sensor_panel)
        return {'FINISHED'}

class BodySim_RESET_SENSORS(bpy.types.Operator):
    bl_idname = "bodysim.reset_sensors"
    bl_label = "BodySim Reset All Sensors"

    def execute(self, context):
        Bodysim.vertex_operations.object_mode()
        model = context.scene.objects['model']
        context.scene.objects.active = None
        model['sensor_info'] = {}
        bpy.context.scene.objects.active = model
        sensors_to_delete = [item.name for item in bpy.data.objects if item.name.startswith("Sensor")]

        for sensor in sensors_to_delete:
            bpy.data.objects[sensor].select = True

        bpy.ops.object.delete()
        Bodysim.vertex_operations.edit_mode()
        Bodysim.vertex_operations.cancel_selection()
        if not hasattr(bpy.types, "CurrentSensorsPanel"):
            bpy.utils.register_class(CurrentSensorsPanel)
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
