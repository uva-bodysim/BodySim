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
from queue import Queue, Empty
from threading import Thread
import subprocess
from vertex_group_operator import select_vertex_group, bind_to_text_vg
from multiprocessing import Pool
from xml.etree.ElementTree import ElementTree as ET
from xml.etree.ElementTree import *
q = Queue()

dirname = os.path.dirname

#Imports blender_caller.py
sys.path.insert(0, dirname(dirname(__file__)))

def plot_csv(plot_type, fps, filenames):
    #pool = Pool(processes=1)
    plotter_file_path = os.path.normpath(os.path.dirname(os.path.realpath(__file__)) + "/blender_plotter.py")
    print(plotter_file_path)
    print(filenames)
    pipe = subprocess.Popen(["python", plotter_file_path, plot_type, fps] + filenames, 
            stdout=subprocess.PIPE, bufsize=1)
    return pipe


def run_imu_sims(filenames):
    imu_sim_file_path = os.path.normpath(os.path.dirname(os.path.realpath(__file__)) + "/imu_simulator.py")
    pipe = subprocess.Popen(["python", imu_sim_file_path] + filenames,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1)
    return pipe

def read_most_recent_run():
    f = open(dirname(dirname(__file__)) + os.sep +'mmr', 'r')
    mmr = f.read() + os.sep
    f.close()
    return mmr

def run_channel_sims(filenames):
    channel_sim_file_path = os.path.normpath(os.path.dirname(os.path.realpath(__file__)) + "/channel_simulator.py")
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
        most_recent_run = read_most_recent_run()
        print ("MRR: " + most_recent_run)
        sensor_files = []

        if (self.plot_type == '-imu'):
            sensor_files = glob.glob(os.path.realpath(most_recent_run) + os.sep + 'sim' + os.sep + '*-i.csv')

        if (self.plot_type == '-raw'):
            sensor_files = glob.glob(os.path.realpath(most_recent_run) + os.sep + 'raw' + os.sep + '*csv')

        if (self.plot_type == '-chan'):
            sensor_files = glob.glob(os.path.realpath(most_recent_run) + os.sep + 'sim' + os.sep + '*-c.csv')

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

#Imports blender_caller.py
sys.path.insert(0, dirname(dirname(__file__)))

class IMUGenerateOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "bodysim.generate_imu"
    bl_label = "IMU Generator Operator"

    def execute(self, context):
        most_recent_run = read_most_recent_run()
        print ("MRR: " + most_recent_run)
        sensor_files = glob.glob(os.path.realpath(most_recent_run) + os.sep + 'raw' + os.sep + '*csv')
        print(sensor_files)
        pipe = run_imu_sims(sensor_files)
        pipe.wait()
        return {'FINISHED'}

class ChannelGenerateOperator(bpy.types.Operator):
    """Tooltip"""
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
        sensor_files = glob.glob(os.path.realpath(most_recent_run) + os.sep + 'raw' + os.sep + '*csv')
        print(sensor_files)
        print('running channel sim')
        pipe = run_channel_sims(sensor_files)
        pipe.wait()
        print(pipe)
        print("done")
        return {'FINISHED'}

def read_most_recent_run():
    f = open(dirname(dirname(__file__)) + os.sep +'mmr', 'r')
    mmr = f.read() + os.sep
    f.close()
    return mmr

dirname = os.path.dirname
path_to_this_file = dirname(dirname(os.path.realpath(__file__)))

def main(context):
    scene = bpy.context.scene
    for ob in context.scene.objects:
        print(ob)


class TrackSensorOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "bodysim.track_sensors"
    bl_label = "Track Sensors"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        num_sensors = context.scene.objects['model']['sensors']
        file_name = 'Sensor'
        scene = bpy.context.scene
        sensor_objects = populate_sensor_list(num_sensors)
        track_sensors(1, 100, num_sensors, file_name, sensor_objects, scene)       
        return {'FINISHED'}

class SaveOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "bodysim.save"
    bl_label = "Save Session"

    def execute(self, context):
        tree = ET()
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
        # For what ever reason, tree.write fails.
        #tree.write(path_to_this_file + os.sep + 'sensors-' + time.strftime('%Y%m%d%H%M%S') + '.xml')
        f = open(path_to_this_file + os.sep + 'sensors-' + time.strftime('%Y%m%d%H%M%S') + '.xml', 'wb')
        f.write(tostring(sensors_element))
        f.close()
        return {'FINISHED'}

class LoadOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "bodysim.load"
    bl_label = "Load Session"

    def execute(self, context):
        # TODO Prompt user for the file name and location
        context.scene.objects['model']['sensor_info'] = {}
        sensor_dict = context.scene.objects['model']['sensor_info']
        tree = ET().parse('save_data.xml')

        for sensor in tree.iter('sensor'):
            sensor_subelements = list(sensor)
            context.scene.objects['model']['sensor_info'][sensor.attrib['location']] = (sensor_subelements[0].text,
                                                                                        sensor_subelements[1].text)
            select_vertex_group(sensor.attrib['location'], context)
            bind_to_text_vg(context)


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
        
def save_run_time():
    sim_out_dir = path_to_this_file + os.sep + time.strftime(
            'simout-%Y%m%d%H%M%S')
    f = open(path_to_this_file + os.sep + 'mmr', 'w')
    f.write(sim_out_dir)
    f.close()
    tracking_out_dir = sim_out_dir + os.sep + 'raw'
    os.mkdir(sim_out_dir)
    os.mkdir(tracking_out_dir)
    return tracking_out_dir

def track_sensors(frame_start, frame_end, num_sensors, file_name, sensor_objects, scene):
    """Print location and rotation of sensors along respective paths.

    Rotation in quaternions.

    """
    tracking_out_dir = save_run_time()
    data_files = []
    for i in range(num_sensors):
        data_files.append(open(tracking_out_dir + os.sep + file_name + '_' + str(i) + '.csv', 'w'))
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