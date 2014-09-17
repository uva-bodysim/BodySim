"""
Contains file writing, reading, and execution methods for simulations and sessions.
"""

import bpy
import os
import shutil
from xml.etree.ElementTree import ElementTree as ET
from xml.etree.ElementTree import *
import subprocess
import Bodysim.plugins_info
import Bodysim.sim_params
NUMBER_OF_BASE_PLUGINS = 1
session_element = None

class SimulationState:
    """Acts as an enum to identify the state of the simulation."""
    Saved, Ran, Batched = range(3)

# Folder containing plugins
bodysim_conf_path = os.path.expanduser('~') + os.sep + '.bodysim'

def indent(elem, level=0):
    """Properly indents XML file."""

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

def write_simulation_xml(name, sensor_dict, sim_path, session_path, sim_state):
    """Writes the list of sensors and simulated variables to a
     simulation XML file.
    """

    global session_element

    curr_simulation_element = Element('simulation',
                                      {'in_batch': str(sim_state),
                                       'frame_start': str(Bodysim.sim_params.start_frame),
                                       'frame_end': str(Bodysim.sim_params.end_frame)})
    curr_simulation_name_element = Element('name')
    curr_simulation_name_element.text = name
    curr_simulation_element.append(curr_simulation_name_element)
    # Now append extras to the element
    extras_values = Bodysim.sim_params.extras_values
    for plugin in extras_values:
        curr_extras_element = Element('extras', {'plugin': plugin})
        for extra in extras_values[plugin]:
            curr_extra_element = Element('extra', {'param': extra})
            curr_value_element = Element('value')
            curr_value_element.text = str(extras_values[plugin][extra]["value"])
            curr_extra_element.extend([curr_value_element])
            curr_extras_element.extend([curr_extra_element])
        curr_simulation_element.extend([curr_extras_element])

    session_element.append(curr_simulation_element)
    update_session_file(session_element, session_path)

    sensors_element = Element('sensors')

    for location, color_and_name in sensor_dict.iteritems():
        curr_sensor_element = Element('sensor', {'location': location, 'name': color_and_name[0]})
        curr_sensor_color_element = Element('color')
        curr_sensor_color_element.text = color_and_name[1]

        # Add information about plugins
        sim_dict = Bodysim.plugins_info.get_sensor_plugin_mapping()
        if len(sim_dict[location]) > NUMBER_OF_BASE_PLUGINS:
            for plugin in sim_dict[location]:
                if plugin == 'Trajectory':
                    continue
                curr_sensor_type_element = Element('plugins_used')
                curr_plugin_element = Element('plugin', {'name': plugin})
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
    with open(sim_path + os.sep + 'sensors.xml', 'wb') as f:
        f.write(tostring(sensors_element))

def update_session_file(session_element, session_path):
    """Updates the session file. Called when a new simulation is added
     to the session.
    """

    with open(session_path + '.xml', 'wb') as f:
        indent(session_element)
        f.write(tostring(session_element))

def execute_simulators(current_sim_path):
    """Run simulators depending sensor and variables selected."""

    plugins = Bodysim.plugins_info.plugins
    # Use in case path has spaces
    dbl_quotes = '"'
    sim_dict = Bodysim.plugins_info.get_sensor_plugin_mapping()
    for sensor in sim_dict:
        if len(sim_dict[sensor]) > NUMBER_OF_BASE_PLUGINS:
            for simulator in sim_dict[sensor]:
                # Ignore if BASE plugin
                if not simulator == 'Trajectory':
                    command = ("python " + dbl_quotes + bodysim_conf_path
                               + os.sep + "plugins" + os.sep
                               + plugins[simulator]['file'] + dbl_quotes)

                    for requirement in plugins[simulator]['requirements']:
                        command = command + ' ' + Bodysim.sim_params.get_params(requirement, sensor)

                    # Deal with extras
                    for extra in plugins[simulator]['extras']:
                        command = command + ' ' + Bodysim.sim_params.get_params(extra, sensor, plugin)

                    args = " ".join(sim_dict[sensor][simulator])

                    # Run the simulator
                    try:
                        subprocess.check_call(command + ' ' + args, shell=True)

                    except:
                        bpy.ops.bodysim.message('INVOKE_DEFAULT', msg_type = "Error",
                                                message = 'An external simulation encountered an error.')
                        return

    # Execute "hidden" sims.
    for plugin in plugins:
        if plugins[plugin]["hidden"]:
            command = ("python " + dbl_quotes + bodysim_conf_path
                       + os.sep + "plugins" + os.sep
                       + plugins[plugin]['file'] + dbl_quotes)

            for requirement in plugins[plugin]['requirements']:
                command = command + ' ' + Bodysim.sim_params.get_params(requirement, None, plugin)

            # Deal with extras
            for extra in plugins[plugin]['extras']:
                command = command + ' ' + Bodysim.sim_params.get_params(extra, None, plugin)

            sensors = " ".join(sim_dict)

            try:
                print(command + ' ' + sensors)
                subprocess.check_call(command + ' ' + sensors, shell=True)
            except:
                bpy.ops.bodysim.message('INVOKE_DEFAULT', msg_type = "Error",
                                        message = 'An external simulation encountered an error.')
                return


    bpy.ops.bodysim.message('INVOKE_DEFAULT', msg_type = "Sucess!",
                            message = 'All simulations finished.')

def read_session_file(path, simulation_state):
    """Reads the session file to get a list of simulations."""

    global session_element

    sim_list = []
    tree = ET().parse(path)
    session_element = tree

    for simulation in tree.iter('simulation'):
        if (simulation_state == int(simulation.attrib['in_batch'])):
            sim_list.append(list(simulation)[0].text)

    return sim_list

def set_session_element(path):
    """Initializes the session element."""

    global session_element
    session_element = Element('session', {'directory' : path})

def save_session_to_file(temp_sim_ran, path):
    """Saves the session file and creates the session directory.
     Saves data in tmp folder if a simulation was ran without first saving the
     session file.
     When user saves, any data in tmp will be moved to the specifed location.
    """

    global session_element

    if temp_sim_ran:
        session_element.set('directory', path.split(os.sep)[-1][:-4])
        os.remove(bodysim_conf_path + os.sep + 'tmp.xml')
        shutil.move(bodysim_conf_path + os.sep + 'tmp', path[:-4])
    else:
        set_session_element(path.split(os.sep)[-1][:-4])
        os.mkdir(path[:-4])

    update_session_file(session_element, path[:-4])

def load_simulation(sensor_xml_path):
    """Loads a simulation file and returns a dictionary mapping
     sensors to simulated variables.
    """

    tree = ET().parse(sensor_xml_path)
    sensor_map = {}

    for sensor in tree.iter('sensor'):
        sensor_map[sensor.attrib['location']] = {}
        sensor_map[sensor.attrib['location']]['name'] = sensor.attrib['name']
        sensor_map[sensor.attrib['location']]['colors'] = list(sensor)[0].text
        sensor_map[sensor.attrib['location']]['variables'] = []
        if len(list(sensor)) > NUMBER_OF_BASE_PLUGINS:
            for simulator in list(sensor)[NUMBER_OF_BASE_PLUGINS]:
                for variable in simulator:
                    sensor_map[sensor.attrib['location']]['variables'].append(simulator.attrib['name'] + variable.text)

    return sensor_map

def populate_sim_params(simulation_name):
    """Populates simulation parameters from session.xml file.
     Returns True if the simulation loaded was saved. (Batch simulations
     have been saved by definition.)
    """
    # First, clear the extras
    Bodysim.sim_params.extras_values = {}
    is_saved = False
    for simulation in session_element.iter('simulation'):
        is_saved = (simulation.attrib['in_batch'] == str(SimulationState.Saved) or
                    simulation.attrib['in_batch'] == str(SimulationState.Batched))
        if simulation.find('name').text == simulation_name:
            Bodysim.sim_params.start_frame = simulation.attrib["frame_start"]
            Bodysim.sim_params.end_frame = simulation.attrib["frame_end"]
            for extra_plugin in simulation.iter('extras'):
                Bodysim.sim_params.extras_values[extra_plugin.attrib['plugin']] = {}
                for extra in extra_plugin.iter('extra'):
                    Bodysim.sim_params.extras_values[extra_plugin.attrib['plugin']][extra.attrib['param']] = {}
                    Bodysim.sim_params.extras_values[extra_plugin.attrib['plugin']][extra.attrib['param']]['value'] = extra[0].text

    return is_saved

def remove_simulation(session_path, simulation_name):
    """Removes the simulation from the session file and the session
     folder. Returns the state of the deleted simulation.
    """
    deleted_state = SimulationState.Saved
    tree = ET().parse(session_path + '.xml')
    for simulation in tree.findall('simulation'):
        if (simulation.find('name').text == simulation_name):
            deleted_state = int(simulation.attrib['in_batch'])
            tree.remove(simulation)

    indent(tree)

    with open(session_path + '.xml', 'wb') as f:
        f.write(tostring(tree))

    shutil.rmtree(session_path + os.sep + simulation_name)

    return deleted_state

def update_simulation_state(session_path, simulation_name, new_state):
    """Updates the state of the simulation."""
    tree = ET().parse(session_path + '.xml')
    for simulation in tree.findall('simulation'):
        if (simulation.find('name').text == simulation_name):
            simulation.attrib['in_batch'] = str(new_state)

    indent(tree)

    with open(session_path + '.xml', 'wb') as f:
        f.write(tostring(tree))

def write_results(data, sensor_objects, sim_path):
    """Writes simulation results to csv file."""
    for i in range(len(sensor_objects)):
        with open(sim_path + os.sep + sensor_objects[i].name + '.csv', 'w') as f:
            for output_line in data[i]:
                f.write(output_line);
