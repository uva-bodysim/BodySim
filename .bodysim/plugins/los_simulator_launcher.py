import sys
import os
import subprocess
import time

current_path = os.path.dirname(os.path.abspath(__file__))
frame_start = sys.argv[1]
frame_end = sys.argv[2]
trajectory_path = sys.argv[3]
triangle_path = sys.argv[4]
triangle_count = sys.argv[5]
height = sys.argv[6]
sample_count = sys.argv[7]
sensor_list = sys.argv[8:]

# Make the folder for the LOS sim results.
sim_path = trajectory_path.split("Trajectory")[0]

os.mkdir(sim_path + "LOS")

print (current_path + os.sep + 'los ' + frame_start + ' ' + frame_end + ' ' +
                      triangle_count + ' ' + triangle_path + ' ' +
                      sample_count + ' ' + height + ' ' + trajectory_path + ' ' +
                      str(len(sensor_list)) + ' ' + ' '.join(sensor_list))

# Execute the CPP LOS Checker, assuming it is in same directory as this file.
start = time.clock()
subprocess.check_call((current_path + os.sep + 'los ' + frame_start + ' ' + frame_end + ' ' +
                      triangle_count + ' ' + triangle_path + ' ' +
                      sample_count + ' ' + height + ' ' + trajectory_path + ' ' +
                      str(len(sensor_list)) + ' ' + ' '.join(sensor_list)), shell=True)
elapsed = (time.clock() - start)
print 'verts ' + str(triangle_count) + ' sample_count ' + str(sample_count) + ' sensors ' + str(len(sensor_list)) + ' time ' + str(elapsed)
