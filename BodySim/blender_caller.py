'''
Put blender_plotter.py in the same directory as the the one you are calling this function from.
'''
import subprocess
import sys
import os

def plot_csv(plot_type, fps, filenames):
    plotter_file_path = os.path.normpath(os.path.dirname(os.path.realpath(__file__)) + "/blender_plotter.py")
    pipe = subprocess.Popen(["python", plotter_file_path, plot_type, fps] + filenames,
            stdout=subprocess.PIPE, bufsize=1)
    return pipe


def run_imu_sims(filenames):
    imu_sim_file_path = os.path.normpath(os.path.dirname(os.path.realpath(__file__)) + "/imu_simulator.py")
    pipe = subprocess.Popen(["python", imu_sim_file_path] + filenames,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1)
    return pipe

def run_channel_sims(filenames):
    channel_sim_file_path = os.path.normpath(os.path.dirname(os.path.realpath(__file__)) + "/channel_simulator.py")
    pipe = subprocess.Popen(["python", channel_sim_file_path] + filenames,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1)
    return pipe

'''
if __name__ == "__main__":
    proc = plot_csv(sys.argv[1])
    while True:
        line = proc.stdout.readline()
        if line != '':
            print line
'''
