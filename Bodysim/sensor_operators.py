"""
Provides operators for different sensor actions (e.g. delete, select, edit).
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

# Keeps track of the current graphing panel. This panel is unregistered (replaced with the current_sensors_panel) when
# user wants to return to the current_sensors_panel. See current_sensors_panel for more details.
current_graph_panel = None

def update_color(self, context):
    """Updates the currently active sensor's color when user is selecting a color."""
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
    """Operator that zooms into the desired vertex group."""
    bl_idname = "bodysim.locate_body_part"
    bl_label = "BodySim Locate Body Part"
    part = bpy.props.StringProperty()

    def execute(self, context):
        Bodysim.vertex_operations.select_vertex_group(self.part, context)
        bpy.ops.view3d.view_selected()
        return {'FINISHED'}

class Bodysim_EDIT_SENSOR(bpy.types.Operator):
    """Operator that takes the user back to the configuration page of AddSensorPanel to change sensor configuration."""
    bl_idname = "bodysim.edit_sensor"
    bl_label = "BodySim Edit Sensor"
    part = bpy.props.StringProperty()

    def execute(self, context):
        model = context.scene.objects['model']
        model['current_vg'] = self.part
        Bodysim.sensor_addition.redraw_addSensorPanel(Bodysim.sensor_addition._draw_sensor_properties_page)
        Bodysim.sensor_addition.draw_plugins_subpanels(Bodysim.plugins_info.plugins)
        return {'FINISHED'}

class BodySim_DELETE_SENSOR(bpy.types.Operator):
    """Operator that removes a sensor from a simulation."""
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

class GraphButton(bpy.types.Operator):
    """Operator that takes user to the graphing panel for a specified sensor."""
    bl_idname = "bodysim.graph_select"
    bl_label = "Select variables to graph"
    part = bpy.props.StringProperty()

    def execute(self, context):
        bpy.utils.unregister_class(Bodysim.current_sensors_panel.current_sensor_panel)
        draw_GraphSelectionPanel(self.part)
        return {'FINISHED'}

def draw_GraphSelectionPanel(part):
    """Draws the list of variables that can be graphed for the current sensor."""
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
    """Draws the individual checkboxes for each graphable variable.
    Only variables that have been selected during sensor addition will be shown.
    """
    layout = self.layout
    column = layout.column()
    plugins = Bodysim.plugins_info.plugins
    for simulator in plugins:
        for variable in plugins[simulator]['variables']:
            if getattr(context.scene.objects['sensor_' + self.part], simulator + variable):
                column.prop(context.scene.objects['sensor_' + self.part], 'GRAPH_' + simulator + variable)

    column.operator("bodysim.graph_return", text = "Return")

class ReturnToCurrentSensors(bpy.types.Operator):
    """Returns the user from the graphing panel to the CurrentSensorsPanel."""
    bl_idname = "bodysim.graph_return"
    bl_label = "Return to current sensor list"

    def execute(self, context):
        bpy.utils.unregister_class(current_graph_panel)
        bpy.utils.register_class(Bodysim.current_sensors_panel.current_sensor_panel)
        return {'FINISHED'}

class BodySim_RESET_SENSORS(bpy.types.Operator):
    """Operator that removes all sensors from a simulation.
    Note that after a simulation has been run, it becomes read-only. Therefore, calling this after a simulation has been
    run does remove sensors from CurrentSensorsPanel but the user can always reload the simulation to bring back the 
    sensors.
    """
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

def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
