"""Holds simulation parameters for use with external plugins."""

import os
dbl_quotes = '"'
start_frame = 0
end_frame = 100
# TODO Set this somewhere else.
fps = 30
extras_values = {}
trajectory_path = ""
# This will hold temporary tringle data; will be overwritten each run.
triangles_path = os.path.expanduser('~') + os.sep + '.bodysim' + os.sep + 'triangles'
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
        if sensor_name is not None:
            path = path + 'sensor_' + sensor_name + '.csv'
        return dbl_quotes + path + dbl_quotes
    elif param == "triangles":
        return dbl_quotes + triangles_path + dbl_quotes
    else:
        return str(extras_values[plugin][param]["value"])
