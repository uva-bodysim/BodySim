import bpy
import sys
import glob
import os 
dirname = os.path.dirname

#Imports blender_caller.py
sys.path.insert(0, dirname(dirname(__file__)))
import blender_caller

class IMUGenerateOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "bodysim.generate_imu"
    bl_label = "IMU Generator Operator"

    def execute(self, context):
        most_recent_run = read_most_recent_run()
        print ("MRR: " + most_recent_run)
        sensor_files = glob.glob(os.path.realpath(most_recent_run) + os.sep + 'raw' + os.sep + '*csv')
        print(sensor_files)
        pipe = blender_caller.run_imu_sims(sensor_files)
        pipe.wait()
        return {'FINISHED'}

def register():
    bpy.utils.register_class(IMUGenerateOperator)

def unregister():
    bpy.utils.unregister_class(IMUGenerateOperator)

def read_most_recent_run():
    f = open(dirname(dirname(__file__)) + os.sep +'mmr', 'r')
    mmr = f.read() + os.sep
    f.close()
    return mmr

if __name__ == "__main__":
    register()