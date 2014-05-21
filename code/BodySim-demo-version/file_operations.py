"""
Contains file writing, reading, and execution methods.

"""

import bpy
import glob
import os
import sys
import builtins
from queue import Queue, Empty
from threading import Thread
from xml.etree.ElementTree import ElementTree as ET
from xml.etree.ElementTree import *
import subprocess
# TODO This should be shared between simtools panel
NUMBER_OF_BASE_PLUGINS = 1

def indent(elem, level=0):
    """
    Properly indents XML file.
    """

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

def write_simulation_xml(name, sensor_dict, sim_dict, path):
    """
    Writes the list of sensors and simulated variables to a simulation XML file.
    """

    tree = ET()
    curr_simulation_element = Element('simulation')
    curr_simulation_name_element = Element('name')
    curr_simulation_name_element.text = name
    curr_simulation_element.append(curr_simulation_name_element)


    sensors_element = Element('sensors')

    for location, color in sensor_dict.iteritems():
        curr_sensor_element = Element('sensor', {'location' : location})
        curr_sensor_color_element = Element('color')
        curr_sensor_color_element.text = color

        # Add information about plugins
        if len(sim_dict[location]) > NUMBER_OF_BASE_PLUGINS:
            for plugin in sim_dict[location]:
                if plugin == 'Trajectory':
                    continue
                curr_sensor_type_element = Element('plugins_used')
                curr_plugin_element = Element('plugin', {'name' : plugin})
                curr_sensor_type_element.extend([curr_plugin_element])
                for variable in sim_dict[location][plugin]:
                    curr_variable_element = Element('variable')
                    curr_variable_element.text = variable
                    curr_plugin_element.extend([curr_variable_element])

            curr_sensor_element.extend([curr_sensor_color_element, curr_sensor_type_element])

        else:
            curr_sensor_element.extend([curr_sensor_color_element])

        sensors_element.append(curr_sensor_element)

        indent(sensors_element)
        file = open(path + os.sep + 'sensors.xml', 'wb')
        file.write(tostring(sensors_element))
        file.flush()
        file.close()

def get_plugins(path, setTheAttrs):
    """
    Reads the plugins.xml file for the list of available external simulators to run.
    """
    # TODO Error checking (existance of plugins.xml, duplicate plugins)
    # Hard coded plugin: Trajectory
    unit_map = {}
    plugins_dict = {}
    trajectory_vars = ['x', 'y', 'z', 'w', 'rx', 'ry', 'rz']
    plugins_dict['Trajectory'] = {'file' : None, 'variables' : trajectory_vars}
    for var in trajectory_vars:
        setattr(bpy.types.Object, 'Trajectory' + var, bpy.props.BoolProperty(default=True, name=var))
        setattr(bpy.types.Object, 'GRAPH_Trajectory' + var, bpy.props.BoolProperty(default=False, name='Trajectory_' + var))

    unit_map[('frame no.', 'location(cm)')] = ['Trajectoryx', 'Trajectoryy', 'Trajectoryz']
    unit_map[('frame no.', 'heading (rad)')] = ['Trajectoryw', 'Trajectoryrx', 'Trajectoryry', 'Trajectoryrz']

    tree = ET().parse(path + os.sep + 'plugins.xml')
    for simulator in tree.iter('simulator'):
        simulator_name = simulator.attrib['name']
        simulator_file = simulator.attrib['file']
        variables = []
        for unitGroup in simulator:
            unitTuple = (unitGroup.attrib['x'], unitGroup.attrib['y'])
            unitgroup_list = [] if not unitTuple in unit_map else unit_map[unitTuple]
            for variable in unitGroup:
                unitgroup_list.append(simulator_name + variable.text)

                variables.append(variable.text)
                # Append simulator name to allow variables of the same name over different
                # simulations.
                if setTheAttrs:
                    setattr(bpy.types.Object, simulator_name + variable.text, bpy.props.BoolProperty(default=False, name=variable.text))
                    setattr(bpy.types.Object, 'GRAPH_' + simulator_name + variable.text, bpy.props.BoolProperty(default=False, name=simulator_name + variable.text))

            if not unitTuple in unit_map:
                unit_map[unitTuple] = unitgroup_list 

        plugins_dict[simulator_name] = {'file' : simulator_file, 'variables' : variables}

    return (plugins_dict, unit_map)

def update_session_file(session_element, session_path):
    with open(session_path + '.xml', 'wb') as f:
        indent(session_element)
        f.write(tostring(session_element))
        f.close()

def execute_simulators(current_sim_path, bodysim_base_path, sim_dict):
    """
    Run simulators depending sensor and variables selected.

    """
    plugins = get_plugins(bodysim_base_path, False)[0]
    # TODO Put fps somewhere else. Should it be set by the user?
    fps = 30
    for sensor in sim_dict:
        if len(sim_dict[sensor]) > NUMBER_OF_BASE_PLUGINS:
            for simulator in sim_dict[sensor]:
                # Ignore if BASE plugin
                if not simulator == 'Trajectory':
                    args = " ".join(sim_dict[sensor][simulator])

                    # Use in case path has spaces
                    dbl_quotes = '"'

                    # Run the simulator
                    subprocess.check_call("python " + dbl_quotes + bodysim_base_path + os.sep + "plugins" + os.sep
                     + plugins[simulator]['file'] + dbl_quotes + ' ' + dbl_quotes
                     + current_sim_path + os.sep + 'Trajectory' + os.sep + 'sensor_' + sensor + '.csv'
                     + dbl_quotes + ' ' + str(fps) + ' ' + args)
