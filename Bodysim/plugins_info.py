"""Universal container for plugin information."""

import bpy
import os
from xml.etree.ElementTree import ElementTree as ET
from xml.etree.ElementTree import *

bodysim_conf_path = os.path.expanduser('~') + os.sep + '.bodysim'

def get_plugins(setTheAttrs):
    """Reads the plugins.xml file for the list of available external
     simulators to run.
     If setTheAttrs is True, this will create a pair of boolean attribute per
     simulation variable for each created sensor. The first attribute controls
     whether or not that variable will be simulated; the second controls whether
     or not that simulated variable will be graphed.
    """

    # TODO Error checking (existance of plugins.xml, duplicate plugins)
    # Hard coded plugin: Trajectory
    unit_map = {}
    plugins_dict = {}
    trajectory_vars = ['x', 'y', 'z', 'w', 'rx', 'ry', 'rz']
    plugins_dict['Trajectory'] = {'file' : None,
                                  'variables' : trajectory_vars,
                                  'extras': {},
                                  'hidden': False}
    for var in trajectory_vars:
        setattr(bpy.types.Object, 'Trajectory' + var, bpy.props.BoolProperty(default=True, name=var))
        setattr(bpy.types.Object, 'GRAPH_Trajectory' + var,
                bpy.props.BoolProperty(default=False, name='Trajectory_' + var))

    unit_map[('frame no.', 'location(cm)', 'location')] = ['Trajectoryx', 'Trajectoryy', 'Trajectoryz']
    unit_map[('frame no.', 'heading (rad)', 'rotation')] = ['Trajectoryw', 'Trajectoryrx', 'Trajectoryry',
                                                            'Trajectoryrz']

    tree = ET().parse(bodysim_conf_path + os.sep + 'plugins.xml')
    for simulator in tree.iter('simulator'):
        simulator_name = simulator.attrib['name']
        simulator_file = simulator.attrib['file']
        hidden = simulator.attrib['hidden']
        will_graph = simulator.attrib['graph']
        variables = []
        requirements_element = simulator.find("requirements") if simulator.find("requirements") else []
        extras_element = simulator.find("extras") if simulator.find("extras") else []
        unitGroups_element = simulator.find("unitGroups") if simulator.find("unitGroups") else []
        extras = {}
        for extra_element in extras_element:
            extras[extra_element.text] = {'description': extra_element.attrib['description'],
                                          'type': extra_element.attrib['type'],
                                          'default': extra_element.attrib['default']}

        for unitGroup in unitGroups_element:
            unitTuple = (simulator.attrib['x'], unitGroup.attrib['y'], unitGroup.attrib['heading'])
            unitgroup_list = [] if not unitTuple in unit_map else unit_map[unitTuple]
            for variable in unitGroup:
                unitgroup_list.append(simulator_name + variable.text)

                variables.append(variable.text)
                # Append simulator name to allow variables of the same name over different
                # simulations.
                if setTheAttrs and not hidden == "true":
                    setattr(bpy.types.Object, simulator_name + variable.text,
                            bpy.props.BoolProperty(default=False, name=variable.text))
                    if will_graph == "true":
                        setattr(bpy.types.Object, 'GRAPH_' + simulator_name + variable.text,
                                bpy.props.BoolProperty(default=False, name=simulator_name + variable.text))

            if not unitTuple in unit_map:
                unit_map[unitTuple] = unitgroup_list

        plugins_dict[simulator_name] = {'file': simulator_file,
                                        'variables': variables,
                                        'requirements': [requirement.text for requirement in requirements_element],
                                        'extras': extras,
                                        'hidden': hidden == "true"}

    return plugins_dict, unit_map

plugins_tuple = get_plugins(True)
# A map of plugins available to simulate.
plugins = plugins_tuple[0]
# A map of the units corresponding to each variable for each simulation.
unit_map = plugins_tuple[1]

def get_sensor_plugin_mapping():
    """For each sensor in the current simulation, gets the variables
     that the user desires to have simulated. Variables are grouped
     by the plugins that keep track of them.
     Because this mapping changes everytime a user loads a new simulation,
     we cannot safely set it once as a variable like the plugins and unit_map.
    """
    context = bpy.context
    model = context.scene.objects['model']
    sim_mapping = {}
    location_map = {}
    for sensor in model['sensor_info']:
        location_map[sensor] = model['sensor_info'][sensor][0]
        for plugin in plugins:
            for variable in plugins[plugin]['variables']:
                if getattr(context.scene.objects['sensor_' + sensor], plugin + variable):
                    if sensor not in sim_mapping:
                        sim_mapping[sensor] = {}

                    if plugin not in sim_mapping[sensor]:
                        sim_mapping[sensor][plugin] = []
                    sim_mapping[sensor][plugin].append(variable)

    return sim_mapping, location_map

def populate_sensor_list():
    """Get all the sensors in the scene. Maps sensor locations to sensor
     names.
    """

    context = bpy.context
    sensor_objects = []
    model = context.scene.objects['model']
    for i in model['sensor_info']:
        sensor_objects.append((bpy.data.objects['sensor_' + i], model['sensor_info'][i][0]))
    return sensor_objects
