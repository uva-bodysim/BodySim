"""Holds simulation parameters for use with external plugins."""

import os
# This is set when a single sim from a batch has been run so we do not keep
# generating triangles for future runs. Must be reset everytime a new 
# model is loaded!
all_frames_recorded = False
dbl_quotes = '"'
simulation_name = ""
start_frame = 1
end_frame = 100
# TODO Set this somewhere else.
fps = 30
# NOTE: For now, non-hidden sims cannot define unique extra parameters for each
# sensor. This functionality may be added if needed in the future.
extras_values = {}
trajectory_path = ""
# This will hold temporary tringle data; will be overwritten each run.
triangles_path = os.path.expanduser('~') + os.sep + '.bodysim' + os.sep + 'triangles' + os.sep
triangle_count = 0
height = 0.0

def get_params(param, sensor_name, plugin=None):
    """Return the requested parameter as a string."""
    if param == "frameStart":
        return str(start_frame)
    elif param == "frameEnd":
        return str(end_frame)
    elif param == "fps":
        return str(fps)
    elif param == "height":
        return str(height)
    elif param == "Trajectory":
        path = trajectory_path + os.sep
        path = path.replace('\\', r'\\')
        if sensor_name is not None:
            path = path + 'sensor_' + sensor_name + '.csv'
        return dbl_quotes + path + dbl_quotes
    elif param == "triangles":
        path = triangles_path.replace('\\', r'\\')
        print(path)
        return dbl_quotes + path + dbl_quotes
    elif param == "triangleCount":
        return str(triangle_count)
    else:
        return str(extras_values[plugin][param]["value"])
