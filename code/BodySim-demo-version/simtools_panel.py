"""
IMPORTANT!
Script that creates the Sim Tools panel. Note that the operators that it uses
must be registered first before this panel can be registered. These files are:
    graph_operator.py (for plotting, both IMU and motion)
    IMUGenerateOperator.py (for IMU data generation)
    TrackSensorOperator.py (for motion data generation)
"""
import bpy
import os
import time
import sys
import glob
import shutil
import builtins
try:
    import Bodysim.vertex_group_operator
    import Bodysim.file_operations
except ImportError:
    raise ImportError()
from xml.etree.ElementTree import ElementTree as ET
from xml.etree.ElementTree import *
dirname = os.path.dirname
path_to_this_file = dirname(os.path.realpath(__file__))
builtins.sim_dict = {}
session_element = None
simulation_ran = False
temp_sim_ran = False
NUMBER_OF_BASE_PLUGINS = 1
sim_list = []

class SaveOperator(bpy.types.Operator):
    bl_idname = "bodysim.save"
    bl_label = "Save Session"

    def execute(self, context):
        bpy.ops.bodysim.save_session_to_file('INVOKE_DEFAULT')
        return {'FINISHED'}

class WriteSessionToFileOperator(bpy.types.Operator):
    bl_idname = "bodysim.save_session_to_file"
    bl_label = "Save to file"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        global session_element
        global temp_sim_ran
        if not self.filepath[-4:] == '.xml':
            bpy.ops.bodysim.message('INVOKE_DEFAULT',
             msg_type = "Error", message = 'The session file must be saved with an xml extension.')
            return {'FINISHED'}

        if os.path.exists(self.filepath):
            bpy.ops.bodysim.error_message('INVOKE_DEFAULT',
             msg_type = "Error", message = 'A folder already exists with the desired session name.')
            return {'FINISHED'}            

        tree = ET()
        model = context.scene.objects['model']
        model['session_path'] = self.filepath[:-4]

        # Handle the case when simulations have been run before a session is saved.
        if temp_sim_ran:
            session_element.set('directory', self.filepath.split(os.sep)[-1][:-4])
            os.remove(path_to_this_file + os.sep + 'tmp.xml')
            shutil.move(path_to_this_file + os.sep + 'tmp', self.filepath[:-4])

        else:
            session_element = Element('session', {'directory' : self.filepath.split(os.sep)[-1][:-4]})
            os.mkdir(self.filepath[:-4])

        Bodysim.file_operations.update_session_file(session_element, model['session_path'])
        
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        self.filepath = 'session' + time.strftime('-%Y%m%d%H%M%S') + '.xml'
        return {'RUNNING_MODAL'}


class LoadOperator(bpy.types.Operator):

    bl_idname = "bodysim.load"
    bl_label = "Load Session"

    def execute(self, context):
        bpy.ops.bodysim.read_from_file('INVOKE_DEFAULT')
        return {'FINISHED'}

class ReadFileOperator(bpy.types.Operator):
    bl_idname = "bodysim.read_from_file"
    bl_label = "Read from file"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        global session_element
        model = context.scene.objects['model']
        model['sensor_info'] = {}
        model['session_path'] = self.filepath[:-4]
        tree = ET().parse(self.filepath)
        session_element = tree

        # simulations_element = Element('simulations')
        for simulation in tree.iter('simulation'):
            sim_list.append(list(simulation)[0].text)

        draw_previous_run_panel(sim_list)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class NewSimulationOperator(bpy.types.Operator):
    bl_idname = "bodysim.new_sim"
    bl_label = "Create a new simulation"

    def execute(self, context):
        # TODO Let the user pick a previous simulation to use as a template.
        # For now, this will clear all sensors.
        global simulation_ran
        if context.scene.objects['model']['sensor_info'] and not simulation_ran:
            bpy.ops.bodysim.not_ran_sim_dialog('INVOKE_DEFAULT')
        else:
            bpy.ops.bodysim.reset_sensors('INVOKE_DEFAULT')
        return {'FINISHED'}

class NotRanSimDialogOperator(bpy.types.Operator):
    bl_idname = "bodysim.not_ran_sim_dialog"
    bl_label = "Simulation not ran yet on these sensors."


    def execute(self, context):
        bpy.ops.bodysim.reset_sensors('INVOKE_DEFAULT')
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text="Are you sure you want to reset?")

class RunSimulationOperator(bpy.types.Operator):
    bl_idname = "bodysim.run_sim"
    bl_label = "Run Simulation"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        bpy.ops.bodysim.name_simulation('INVOKE_DEFAULT')
        return {'FINISHED'}

class NameSimulationDialogOperator(bpy.types.Operator):
    bl_idname = "bodysim.name_simulation"
    bl_label = "Enter a name for this simulation."

    simulation_name = bpy.props.StringProperty(name="Name: ", )

    def execute(self, context):
        global session_element
        global simulation_ran
        global temp_sim_ran
        global sim_list
        simulation_ran = True
        model = context.scene.objects['model']
        num_sensors = len(model['sensor_info'])

        if 'session_path' not in model:
            session_path = path_to_this_file + os.sep + 'tmp'
            os.mkdir(path_to_this_file + os.sep + 'tmp')
            session_element = Element('session', {'directory' : session_path})
            temp_sim_ran = True
        else:
            session_path =  model['session_path']

        path = session_path + os.sep + self.simulation_name
        model['current_simulation_path'] = path
        if os.path.exists(path):
            bpy.ops.bodysim.message('INVOKE_DEFAULT',
             msg_type = "Error", message = 'A simulation with that name already exists!')
            return {'CANCELLED'}

        sim_list.append(self.simulation_name)
        draw_previous_run_panel(sim_list)
        os.mkdir(path)
        os.mkdir(path + os.sep + 'Trajectory')
        tree = ET()
        if model['simulation_count'] == 0:
            simulations_element = Element('simulations')

        # TODO Most of this work is being duplicated inside write_simulation_xml.
        curr_simulation_element = Element('simulation')
        curr_simulation_name_element = Element('name')
        curr_simulation_name_element.text = self.simulation_name
        curr_simulation_element.append(curr_simulation_name_element)
        session_element.append(curr_simulation_element)
        Bodysim.file_operations.update_session_file(session_element, session_path)

        sensor_dict = context.scene.objects['model']['sensor_info']
        sensors_element = Element('sensors')

        builtins.sim_dict = get_sensor_plugin_mapping(context)

        Bodysim.file_operations.write_simulation_xml(self.simulation_name, sensor_dict, builtins.sim_dict, path)

        model['simulation_count'] += 1
        scene = bpy.context.scene
        sensor_objects = populate_sensor_list(num_sensors, context)
        track_sensors(1, 100, num_sensors, sensor_objects, scene, path + os.sep + 'Trajectory')
        Bodysim.file_operations.execute_simulators(context.scene.objects['model']['current_simulation_path'], path_to_this_file, builtins.sim_dict)
        return {'FINISHED'}

    def invoke(self, context, event):
        model = context.scene.objects['model']
        if 'simulation_count' not in model: 
            model['simulation_count'] = 0
        self.simulation_name = "simulation_" + str(model['simulation_count'])
        return context.window_manager.invoke_props_dialog(self)

def populate_sensor_list(num_sensors, context):
    """ Get all the sensors in the scene."""
    print(bpy.data.objects)
    sensor_objects = []
    for i in context.scene.objects['model']['sensor_info']:
        sensor_objects.append(bpy.data.objects['sensor_' + i])
    return sensor_objects

def get_sensor_plugin_mapping(context):
    plugins = Bodysim.file_operations.get_plugins(path_to_this_file, False)[0]
    model = context.scene.objects['model']
    sim_dict = {}
    for sensor in model['sensor_info']:
        for plugin in plugins:
            for variable in plugins[plugin]['variables']:
                if getattr(context.scene.objects['sensor_' + sensor], plugin + variable):
                    if sensor not in sim_dict:
                        sim_dict[sensor] = {}

                    if plugin not in sim_dict[sensor]:
                        sim_dict[sensor][plugin] = []
                    sim_dict[sensor][plugin].append(variable)

    return sim_dict


def track_sensors(frame_start, frame_end, num_sensors, sensor_objects, scene, path):
    """Print location and rotation of sensors along respective paths.

    Rotation in quaternions.

    """
    data_files = []
    for i in sensor_objects:
        data_files.append(open(path + os.sep + i.name + '.csv', 'w'))

    for i in range(frame_end - frame_start + 1):
        current_frame = frame_start + i
        scene.frame_current = current_frame
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.object.mode_set(mode='OBJECT')

        # Refresh frame. Resolution must be low for window update to be fast.
        bpy.ops.render.render()
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

        for j in range(num_sensors):
            # World space coordinates
            translation_vector = sensor_objects[
                j].matrix_world.to_translation()
            x = translation_vector[0]
            y = translation_vector[1]
            z = translation_vector[2]

            # Rotation
            rotation_vector = sensor_objects[
                j].matrix_world.to_quaternion()
            w = rotation_vector[0]
            rx = rotation_vector[1]
            ry = rotation_vector[2]
            rz = rotation_vector[3]

            # Buffer to file
            output = "{0},{1},{2},{3},{4},{5},{6},{7}\n".format(
                current_frame, x, y, z, w, rx, ry, rz)
            data_files[j].write(output)

    # Close files
    for i in range(num_sensors):
        data_files[i].flush()
        data_files[i].close()

class LoadSimulationOperator(bpy.types.Operator):
    bl_idname = "bodysim.load_simulation"
    bl_label = "Load a simulation."

    simulation_name = bpy.props.StringProperty()

    def execute(self, context):
        # TODO Check if there were any unsaved modifications first.
        bpy.ops.bodysim.reset_sensors('INVOKE_DEFAULT')
        # Navigate to correct folder to load the correct sensors.xml
        model = context.scene.objects['model']
        sensor_xml_path = model['session_path'] + os.sep + self.simulation_name + os.sep + 'sensors.xml'
        model['current_simulation_path'] = model['session_path'] + os.sep + self.simulation_name
        print(sensor_xml_path)
        tree = ET().parse(sensor_xml_path)

        for sensor in tree.iter('sensor'):
            sensor_subelements = list(sensor)

            model['sensor_info'][sensor.attrib['location']] = (sensor_subelements[0].text)

            Bodysim.vertex_group_operator.select_vertex_group(sensor.attrib['location'], context)

            Bodysim.vertex_group_operator.bind_to_text_vg(context, tuple([float(color) for color in sensor_subelements[0].text.split(',')]))

            # Loop through plugins, if there are any
            if len(list(sensor)) > 1:
                for simulator in list(sensor)[1]:
                    # Loop through variables
                    for variable in simulator:
                        setattr(context.scene.objects['sensor_' + sensor.attrib['location']], simulator.attrib['name'] + variable.text, True)

            Bodysim.vertex_group_operator.draw_sensor_list_panel(model['sensor_info'])

        builtins.sim_dict = get_sensor_plugin_mapping(context)

        return {'FINISHED'}


def _drawPreviousRunButtons(self, context):
    layout = self.layout

    for _previousRun in self.sim_runs:
        layout.operator("bodysim.load_simulation", text = _previousRun).simulation_name = _previousRun

def draw_previous_run_panel(list_of_simulations):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    panel = type("SimulationSelectPanel", (bpy.types.Panel,),{
        "bl_label": "Previous Simulations",
        "bl_space_type": bl_space_type,
        "bl_region_type": bl_region_type,
        "sim_runs": list_of_simulations,
        "draw": _drawPreviousRunButtons},)

    bpy.utils.register_class(panel)

class SimTools(bpy.types.Panel):
    bl_label = "Sim Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
 
    def draw(self, context):
        self.layout.operator("bodysim.run_sim", text = "Run Simulation")
        self.layout.operator("bodysim.graph", text = "Graph Variables")
        self.layout.operator("bodysim.save", text = "Save Session")
        self.layout.operator("bodysim.load", text = "Load Session")
        self.layout.operator("bodysim.new_sim", text = "New Simulation")

if __name__ == "__main__":
    global path_to_this_file
    bpy.utils.register_module(__name__)
    path_to_this_file = dirname(dirname(os.path.realpath(__file__)))
