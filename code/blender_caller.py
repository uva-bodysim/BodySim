'''
Put blender_plotter.py in the same directory as the the one you are calling this function from.
'''
import subprocess

def plot_csv(filename):
    pipe = subprocess.Popen(["python", "blender_plotter.py", filename],
            stdout=subprocess.PIPE, bufsize=1)
