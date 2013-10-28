import bpy
import os
import time

dirname = os.path.dirname
path_to_this_file = dirname(dirname(os.path.realpath(__file__)))

def main(context):
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
        num_sensors = 1
        file_name = 'test'
        scene = bpy.context.scene
        sensor_objects = populate_sensor_list(num_sensors)
        track_sensors(1, 100, 1, 'test', sensor_objects, scene)       
        return {'FINISHED'}


def register():
    bpy.utils.register_class(SimpleOperator)


def unregister():
    bpy.utils.unregister_class(SimpleOperator)
    
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

if __name__ == "__main__":
    register()