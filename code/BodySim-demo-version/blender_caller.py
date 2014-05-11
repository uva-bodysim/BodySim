'''
Put blender_plotter.py in the same directory as the the one you are calling this function from.
'''
import subprocess
import sys
import os

def plot_csv(plot_type, fps, graph_dict):
    plotter_file_path = os.path.normpath(os.path.dirname(os.path.realpath(__file__)) + "/blender_plotter.py")

    # For each unit group of each sensor, create a csv file with the variables belonging to that
    # group.

    # Note: Assuming that the variables are in the the same column order as they appear in
    # in the plugins.xml file.
    # Note: Assuming one independent variable (first column) per simulator

    # pipe = subprocess.Popen(["python", plotter_file_path, plot_type, fps] + filenames,
    #         stdout=subprocess.PIPE, bufsize=1)
    return pipe

