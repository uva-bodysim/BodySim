import bpy
from bpy.props import FloatVectorProperty, StringProperty
import Bodysim.vertex_operations
import Bodysim.current_sensors_panel
import Bodysim.plugins_info

# List of vertices for a model.
# Note that this must be cleared each time a new model is loaded (different
# vertx groups).
panel_list = []

plugin_panel_list = []

class AddSensorPanel(bpy.types.Panel):
    """A Custom Panel in the Viewport Toolbar"""
    bl_label = "Add Sensor"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "objectmode"
    
    def draw(self, context):
        _drawAddSensorFirstPage(self, context)

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

def _drawAddSensorFirstPage(self, context):
    layout = self.layout
    layout.operator("bodysim.new_sensor", text="Add Sensor")
    layout.operator("bodysim.reset_sensors", text="Reset Sensors")
    layout.operator("bodysim.clear_selection", text="Clear Selection")
    model = context.scene.objects['model']

class BodySim_NEW_SENSOR(bpy.types.Operator):
    bl_idname = "bodysim.new_sensor"
    bl_label = "Create a new sensor"
    
    def execute(self, context):
        redraw_addSensorPanel(_draw_bind_button)
        draw_body_part_panels()
        return {'FINISHED'}


def _draw_bind_button(self, context):
    layout = self.layout
    layout.operator("bodysim.bind_sensor", text="Next")
    layout.operator("bodysim.cancel_add", text="Cancel")

def draw_body_part_panels():
    global panel_list
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "objectmode"
    if not panel_list:
        v_list = Bodysim.vertex_operations.parse_vertex_group(Bodysim.vertex_operations.list_vertex_group())
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

def _draw(self, context):
    layout = self.layout
    for _part in self.v_list:
        layout.operator("bodysim.select_body_part", text=_part).part = _part


# Bind sensor, draw proprety page V2, and remove the panel list.
class BodySim_BIND_SENSOR(bpy.types.Operator):
    bl_idname = "bodysim.bind_sensor"
    bl_label = "BodySim Bind Sensor"

    def execute(self, context):
        model = context.scene.objects['model']
        if 'sensor_selected' not in model or not model['sensor_selected']:
            bpy.ops.bodysim.message('INVOKE_DEFAULT',
             msg_type = "Error", message = 'Please first select a location to add sensor.')
            return {'FINISHED'}
        model['sensor_selected'] = False
        sensor_name = Bodysim.vertex_operations.bind_to_text_vg(context, None)
        context.scene.objects.active = context.scene.objects[sensor_name]
        model['last_bound_sensor'] = sensor_name
        redraw_addSensorPanel(_draw_sensor_properties_page)
        draw_plugins_subpanels(Bodysim.plugins_info.plugins)
        for panel in panel_list:
            bpy.utils.unregister_class(panel)
        return {'FINISHED'}

class BodySim_CANCEL_ADD_SENSOR(bpy.types.Operator):
    bl_idname = "bodysim.cancel_add"
    bl_label = "Bodysim Cancel Add Sensor"

    def execute(self, context):
        # Unselect all selected sensors. Also remove the last bound sensor!
        model = context.scene.objects['model']
        Bodysim.vertex_operations.edit_mode()
        Bodysim.vertex_operations.cancel_selection()

        if 'last_bound_sensor' not in model:
            for panel in panel_list:
                bpy.utils.unregister_class(panel)

        redraw_addSensorPanel(_drawAddSensorFirstPage)
        if 'last_bound_sensor' in model and model['last_bound_sensor']:
            for subpanel in plugin_panel_list:
                bpy.utils.unregister_class(subpanel)

            Bodysim.vertex_operations.object_mode()
            context.scene.objects.active = None
            bpy.context.scene.objects.active = model
            bpy.data.objects[model['last_bound_sensor']]
            bpy.ops.object.delete()
            Bodysim.vertex_operations.edit_mode()
            Bodysim.vertex_operations.cancel_selection()

            return {'FINISHED'}

        if 'sensor_info' in model:
            Bodysim.current_sensors_panel.draw_sensor_list_panel(model['sensor_info'])

        return {'FINISHED'}

# Adds the sensor to the panel list
class BodySim_FINALIZE(bpy.types.Operator):
    bl_idname = "bodysim.finalize"
    bl_label = "Add sensor to the panel"

    sensorColor = bpy.props.FloatVectorProperty()
    sensorName = bpy.props.StringProperty()

    def execute(self, context):
        for subpanel in plugin_panel_list:
            bpy.utils.unregister_class(subpanel)
        sensor = context.active_object
        r = round(self.sensorColor[0], 3)
        g = round(self.sensorColor[1], 3)
        b = round(self.sensorColor[2], 3)
        material = bpy.data.materials.new("SensorColor")
        material.diffuse_color = r, g, b
        sensor.data.materials.append(material)
        model = context.scene.objects['model']
        model['sensor_info'][model['current_vg']] = (self.sensorName , str(r) + ',' + str(g) + ',' + str(b))
        if 'last_bound_sensor' in model:
            del model['last_bound_sensor']
        redraw_addSensorPanel(_drawAddSensorFirstPage)
        Bodysim.current_sensors_panel.draw_sensor_list_panel(model['sensor_info'])
        return {'FINISHED'}

def _draw_sensor_properties_page(self, context):
    layout = self.layout
    model = context.scene.objects['model']
    col = layout.column()
    prop = col.operator("bodysim.finalize", text="Finalize")
    col.operator("bodysim.cancel_add", text = "Cancel")
    col.prop(context.scene.objects['sensor_' + model['current_vg']], "sensor_color")
    col.prop(context.scene.objects['sensor_' + model['current_vg']], "sensor_name")
    prop.sensorColor = context.scene.objects['sensor_' + model['current_vg']].sensor_color
    prop.sensorName = context.scene.objects['sensor_' + model['current_vg']].sensor_name

def _draw_plugin_panels(self, context):
    model = context.scene.objects['model']
    layout = self.layout
    for var in self.var_list:
        # Hard coded plugin: Trajectory
        if self.sim_name == 'Trajectory':
            layout.enabled = False
            layout.prop(context.scene.objects['sensor_' + model['current_vg']], self.sim_name + var)
        else:
            layout.prop(context.scene.objects['sensor_' + model['current_vg']], self.sim_name + var)

def draw_plugins_subpanels(plugins):
    global plugin_panel_list
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "objectmode"
    if not plugin_panel_list:
        for simulator in Bodysim.plugins_info.plugins:
            subpanel = type("SimulationSubPanel%s" % simulator,
                (bpy.types.Panel,),
                {"bl_label": simulator,
                            "bl_space_type": bl_space_type,
                            "bl_region_type": bl_region_type,
                            "bl_context": bl_context,
                            "bl_options": {"DEFAULT_CLOSED"},
                            "sim_name": simulator,
                            "var_list": plugins[simulator]['variables'],
                            "draw" : _draw_plugin_panels},
                        )
            plugin_panel_list.append(subpanel)
            bpy.utils.register_class(subpanel)
    else:
        for subpanel in plugin_panel_list:
            bpy.utils.register_class(subpanel)


def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
