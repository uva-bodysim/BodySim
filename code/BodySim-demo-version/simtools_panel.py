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
from queue import Queue, Empty
from threading import Thread
import subprocess
from vertex_group_operator import select_vertex_group, bind_to_text_vg
from multiprocessing import Pool
from xml.etree.ElementTree import ElementTree as ET
from xml.etree.ElementTree import *
q = Queue()
dirname = os.path.dirname
path_to_this_file = dirname(dirname(os.path.realpath(__file__)))
session_element = None
simulation_ran = False
temp_sim_ran = False
current_simulation_path = None

#Imports blender_caller.py
sys.path.insert(0, dirname(dirname(__file__)))

def plot_csv(plot_type, fps, filenames):
    #pool = Pool(processes=1)
    plotter_file_path = path_to_this_file + os.sep + "blender_plotter.py"
    print(plotter_file_path)
    print(filenames)
    pipe = subprocess.Popen(["python", plotter_file_path, plot_type, fps] + filenames, 
            stdout=subprocess.PIPE, bufsize=1)
    return pipe


def run_imu_sims(filenames):
    imu_sim_file_path = path_to_this_file + os.sep + "imu_simulator.py")
    pipe = subprocess.Popen(["python", imu_sim_file_path] + filenames,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1)
    return pipe

def run_channel_sims(filenames):
    channel_sim_file_path = path_to_this_file + os.sep + "channel_simulator.py")
    pipe = subprocess.Popen(["python", channel_sim_file_path] + filenames,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1)
    return pipe


class GraphOperator(bpy.types.Operator):
    """Get input from graph."""
    bl_idname = "bodysim.plot_motion"
    bl_label = "Graph Modal Operator"
    plot_type = bpy.props.StringProperty()    
    _timer = None
    _pipe = None
    _thread = None

    def modal(self, context, event):
        scene = bpy.context.scene
        if event.type == 'ESC':
            return self.cancel(context)

        if event.type == 'TIMER':
            try:
                line = q.get_nowait()
            except Empty:
                pass
            else:
                # Stop the operator if the graph window is closed.
                if str(line.strip()) == "b'quit'":
                    return self.cancel(context)

                # Move the animation to the desired frame.
                scene.frame_current = int(float(line))
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.render.render()
                bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

        return {'PASS_THROUGH'}

    def execute(self, context):
        # Get the files ending with .csv extension.'
        global current_simulation_path
        most_recent_run = current_simulation_path
        sensor_files = []

        if (self.plot_type == '-imu'):
            sensor_files = glob.glob(current_simulation_path + os.sep + 'sim' + os.sep + '*-i.csv')

        if (self.plot_type == '-raw'):
            sensor_files = glob.glob(current_simulation_path + os.sep + 'raw' + os.sep + '*csv')

        if (self.plot_type == '-chan'):
            sensor_files = glob.glob(current_simulation_path + os.sep + 'sim' + os.sep + '*-c.csv')

        self._pipe = plot_csv(self.plot_type, str(30), sensor_files)
        
        # A separate thread must be started to keep track of the blocking pipe
        # so the script does not freeze blender.
        self._thread = Thread(target=enqueue_output, args=(self._pipe.stdout, q))
        self._thread.daemon = True
        self._thread.start()
        self._timer = context.window_manager.event_timer_add(0.2, context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        context.window_manager.event_timer_remove(self._timer)
        return {'CANCELLED'}

def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        queue.put(line)
    out.close()

class IMUGenerateOperator(bpy.types.Operator):
    bl_idname = "bodysim.generate_imu"
    bl_label = "IMU Generator Operator"

    def execute(self, context):
        most_recent_run = read_most_recent_run()
        print ("MRR: " + most_recent_run)
        sensor_files = glob.glob(current_simulation_path + os.sep + 'raw' + os.sep + '*csv')
        print(sensor_files)
        pipe = run_imu_sims(sensor_files)
        pipe.wait()
        return {'FINISHED'}

class ChannelGenerateOperator(bpy.types.Operator):
    bl_idname = "bodysim.generate_channel"
    bl_label = "Channel Generator Operator"

    '''
    @classmethod
    def poll(self, context):
        return context.scene.objects['model']['sensors'] > 1
    '''

    def execute(self, context):
        most_recent_run = read_most_recent_run()
        print ("MRR: " + most_recent_run)
        sensor_files = glob.glob(current_simulation_path + os.sep + 'raw' + os.sep + '*csv')
        print(sensor_files)
        print('running channel sim')
        pipe = run_channel_sims(sensor_files)
        pipe.wait()
        print(pipe)
        print("done")
        return {'FINISHED'}

def main(context):
    scene = bpy.context.scene
    for ob in context.scene.objects:
        print(ob)


class BodysimMessageOperator(bpy.types.Operator):
    bl_idname = "bodysim.message"
    bl_label = "Message"
    msg_type = bpy.props.StringProperty()
    message = bpy.props.StringProperty()
 
    def execute(self, context):
        self.report({'INFO'}, self.message)
        print(self.message)
        return {'FINISHED'}
 
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_popup(self, width=600, height=200)
 
    def draw(self, context):
        self.layout.label("Message")
        col = self.layout.split().column(align=True)
        col.prop(self, "msg_type")
        col.prop(self, "message")

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

        update_session_file(session_element, model['session_path'], context)
        
        
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        self.filepath = 'session' + time.strftime('-%Y%m%d%H%M%S') + '.xml'
        return {'RUNNING_MODAL'}

def update_session_file(session_element, session_path, context):
    with open(session_path + '.xml', 'wb') as f:
        indent(session_element)
        f.write(tostring(session_element))
        f.close()

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

        sim_list = []
        # simulations_element = Element('simulations')
        for simulation in tree.iter('simulation'):
            sim_list.append(list(simulation)[0].text)

        draw_previous_run_panel(sim_list)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

    
def populate_sensor_list(num_sensors):
    """ Get all the sensors in the scene."""
    sensor_objects = []
    for i in range(num_sensors):
        sensor_objects.append(bpy.data.objects["Sensor_" + str(i)])
    return sensor_objects
        
class TrackSensorOperator(bpy.types.Operator):
    bl_idname = "bodysim.track_sensors"
    bl_label = "Track Sensors"

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
        global current_simulation_path
        simulation_ran = True
        model = context.scene.objects['model']
        num_sensors = model['sensors']

        if 'session_path' not in model:
            session_path = path_to_this_file + os.sep + 'tmp'
            os.mkdir(path_to_this_file + os.sep + 'tmp')
            session_element = Element('session', {'directory' : session_path})
            temp_sim_ran = True
        else:
            session_path =  model['session_path']

        path = session_path + os.sep + self.simulation_name
        current_simulation_path = path
        os.mkdir(path)
        os.mkdir(path + os.sep + 'raw')
        tree = ET()
        if model['simulation_count'] == 0:
            simulations_element = Element('simulations')

        curr_simulation_element = Element('simulation')
        curr_simulation_name_element = Element('name')
        curr_simulation_name_element.text = self.simulation_name
        curr_simulation_element.append(curr_simulation_name_element)
        session_element.append(curr_simulation_element)
        update_session_file(session_element, session_path, context)

        sensor_dict = context.scene.objects['model']['sensor_info']
        sensors_element = Element('sensors')
        for location, info in sensor_dict.iteritems():
            curr_sensor_element = Element('sensor', {'location' : location})
            curr_sensor_type_element = Element('type')
            curr_sensor_type_element.text = info[0]
            curr_sensor_color_element = Element('color')
            curr_sensor_color_element.text = info[1]
            curr_sensor_element.extend([curr_sensor_type_element, curr_sensor_color_element])
            sensors_element.append(curr_sensor_element)
        indent(sensors_element)
        file = open(path + os.sep + 'sensors.xml', 'wb')
        file.write(tostring(sensors_element))
        model['simulation_count'] += 1
        scene = bpy.context.scene
        sensor_objects = populate_sensor_list(num_sensors)
        track_sensors(1, 100, num_sensors, sensor_objects, scene, path + os.sep + 'raw')
        return {'FINISHED'}

    def invoke(self, context, event):
        model = context.scene.objects['model']
        if 'simulation_count' not in model: 
            model['simulation_count'] = 0
        self.simulation_name = "simulation_" + str(model['simulation_count'])
        return context.window_manager.invoke_props_dialog(self)

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

def track_sensors(frame_start, frame_end, num_sensors, sensor_objects, scene, path):
    """Print location and rotation of sensors along respective paths.

    Rotation in quaternions.

    """
    data_files = []
    for i in range(num_sensors):
        data_files.append(open(path + os.sep + 'sensor_' + str(i) + '.csv', 'w'))
        print(os.path.realpath(data_files[i].name))

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
        global current_simulation_path
        # TODO Check if there were any unsaved modifications first.
        bpy.ops.bodysim.reset_sensors('INVOKE_DEFAULT')
        # Navigate to correct folder to load the correct sensors.xml
        model = context.scene.objects['model']
        sensor_xml_path = model['session_path'] + os.sep + self.simulation_name + os.sep + 'sensors.xml'
        current_simulation_path = model['session_path'] + os.sep + self.simulation_name
        tree = ET().parse(sensor_xml_path)

        for sensor in tree.iter('sensor'):
            sensor_subelements = list(sensor)

            context.scene.objects['model']['sensor_info'][sensor.attrib['location']] = (sensor_subelements[0].text,
                                                                                        sensor_subelements[1].text)

            select_vertex_group(sensor.attrib['location'], context)
            bind_to_text_vg(context)

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
        self.layout.operator("bodysim.track_sensors", text = "Run Motion Simulation")
        self.layout.operator("bodysim.generate_imu", text = "Run IMU Simulation")
        self.layout.operator("bodysim.generate_channel", text = "Run Channel Simulation")
        self.layout.operator("bodysim.plot_motion", text = "Plot Motion Data").plot_type = "-raw"
        self.layout.operator("bodysim.plot_motion", text = "Plot IMU Data").plot_type = "-imu"
        self.layout.operator("bodysim.plot_motion", text = "Plot Channel Data").plot_type = "-chan"
        self.layout.operator("bodysim.save", text = "Save Session")
        self.layout.operator("bodysim.load", text = "Load Session")
        self.layout.operator("bodysim.new_sim", text = "New Simulation")

def register():
    bpy.utils.register_class(TrackSensorOperator)
    bpy.utils.register_class(IMUGenerateOperator)
    bpy.utils.register_class(GraphOperator)
    bpy.utils.register_class(SimTools)

def unregister():
    bpy.utils.unregister_class(SimTools)
    bpy.utils.unregister_class(GraphOperator)
    bpy.utils.unregister_class(IMUGenerateOperator)
    bpy.utils.unregister_class(TrackSensorOperator)

bpy.utils.register_module(__name__)