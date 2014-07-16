"""Put qt_plotter.py in the same directory as the the one you are
 calling this function from.
This is used to launch the plotter using the external python (i.e. not
 blender's).
"""

import subprocess
import os

def plot_csv(fps, curr_sim_path, graph_dict):
    plotter_file_path = os.path.normpath(os.path.dirname(os.path.realpath(__file__)) + "/qt_plotter.py")

    pipe = subprocess.Popen(["python", plotter_file_path, fps, curr_sim_path, str(graph_dict)],
             stdout=subprocess.PIPE, bufsize=1)
    return pipe

