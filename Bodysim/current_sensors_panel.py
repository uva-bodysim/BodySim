"""
Generates the CurrentSensorsPanel which displays the list of
sensors currently added to a simulation.
"""

import bpy

"""
Keeps track of the CurrentSensorsPanel. This panel is unregistered
 (replaced with the graphing panel) when the user wants to select which
 variables he/she wants to graph. See sensor_operators.py for more
 details.
"""
current_sensor_panel = None

class CurrentSensorsPanel(bpy.types.Panel):
    """Panel that displays the sensors of a given simulation."""

    bl_label = "Current Sensors"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        layout.label("No sensors yet.")

def draw_sensor_list_panel(sensor_dict):
    """Draws the list of sensors currently ready for simulation."""

    bl_label = "Current Sensors"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "objectmode"

    def _draw_single_sensor_buttons(self, context):
        """Draws the individual entries for each simulation.
        Each entry includes the name and color of the sensor, as well
         as the position and individual buttons for deletion and a
         button to bring up selection of variables to graph after the
         simulation has run.
        """

        layout = self.layout
        for sensor in self.sensor_dict:
            col = layout.column(align = True)
            col.enabled = False
            col.prop(context.scene.objects['sensor_' + sensor], "sensor_name")
            row = layout.row(align = True)
            row.alignment = 'EXPAND'
            row.operator("bodysim.locate_body_part", text = sensor).part = sensor
            row.prop(context.scene.objects['sensor_' + sensor], "sensor_color")
            row.operator("bodysim.edit_sensor", text = "Edit").part = sensor
            row.operator("bodysim.delete_sensor", text = "Delete").part = sensor
            row.operator("bodysim.graph_select", text = "Graph Selection").part = sensor

    global current_sensor_panel
    if sensor_dict:
        current_sensor_panel = type("CurrentSensorsPanel", (bpy.types.Panel,),{
            "bl_label": bl_label,
            "bl_space_type": bl_space_type,
            "bl_region_type": bl_region_type,
            "sensor_dict": sensor_dict,
            "draw": _draw_single_sensor_buttons},)
        bpy.utils.register_class(current_sensor_panel)

    else:
        bpy.utils.register_class(CurrentSensorsPanel)

