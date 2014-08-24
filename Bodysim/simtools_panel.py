"""Generates the Sim Tools panel to allow saving and loading of a
 session, graphing of variables, creation of new simulations, and
 keeping track of past simulations.
"""
import bpy
import os
import time
try:
    import Bodysim.file_operations
    import Bodysim.vertex_operations
    import Bodysim.current_sensors_panel
    import Bodysim.sim_params
except ImportError:
    raise ImportError()
sim_dict = {}
simulation_ran = False
temp_sim_ran = False
sim_list = []

class WriteSessionToFileInterface(bpy.types.Operator):
    """Operator that first validates the name of the session to save
     and then saves the session file.
    """

    bl_idname = "bodysim.save_session_to_file"
    bl_label = "Save to file"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):

        if not self.filepath[-4:] == '.xml':
            bpy.ops.bodysim.message('INVOKE_DEFAULT',
             msg_type = "Error", message = 'The session file must be saved with an xml extension.')
            return {'FINISHED'}

        if os.path.exists(self.filepath):
            bpy.ops.bodysim.error_message('INVOKE_DEFAULT',
             msg_type = "Error", message = 'A folder already exists with the desired session name.')
            return {'FINISHED'}            

        model = context.scene.objects['model']
        model['session_path'] = self.filepath[:-4]

        # Handle the case when simulations have been run before a session is saved.
        Bodysim.file_operations.save_session_to_file(temp_sim_ran,self.filepath)
        
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        self.filepath = 'session' + time.strftime('-%Y%m%d%H%M%S') + '.xml'
        return {'RUNNING_MODAL'}

class ReadFileInterface(bpy.types.Operator):
    """Operator that launches interface to load a saved session
     file.
    """

    bl_idname = "bodysim.read_from_file"
    bl_label = "Read from file"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        global sim_list

        model = context.scene.objects['model']
        model['sensor_info'] = {}
        model['session_path'] = self.filepath[:-4]
        sim_list = Bodysim.file_operations.read_session_file(self.filepath)
        draw_previous_run_panel(sim_list)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class NewSimulationOperator(bpy.types.Operator):
    """Operator that clears all existing sensors to allow user to
     create a new simulation.
    """

    bl_idname = "bodysim.new_sim"
    bl_label = "Create a new simulation"

    def execute(self, context):
        global simulation_ran
        model = context.scene.objects['model']

        if 'sensor_info' not in model:
            return {'FINISHED'}

        if model['sensor_info'] and not simulation_ran:
            bpy.ops.bodysim.not_ran_sim_dialog('INVOKE_DEFAULT')
        else:
            bpy.ops.bodysim.reset_sensors('INVOKE_DEFAULT')
        return {'FINISHED'}

class NotRanSimDialogOperator(bpy.types.Operator):
    """Operator that is invoked when user wants to clear sensors
     without running a simulation on them yet.
    """

    bl_idname = "bodysim.not_ran_sim_dialog"
    bl_label = "Simulation not ran yet on these sensors."


    def execute(self, context):
        bpy.ops.bodysim.reset_sensors('INVOKE_DEFAULT')
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text="Are you sure you want to reset?")

class DryRunOperator(bpy.types.Operator):
    """Operator for animating the model without logging sensor data."""

    bl_idname = "bodysim.dry_run"
    bl_label = "Dry Run"

    @classmethod
    def poll(cls, context):
        return True

    def _stop(self, context):
        scene = bpy.context.scene
        if scene.frame_current == scene.frame_end:
            bpy.ops.screen.animation_cancel(restore_frame=True)
            bpy.app.handlers.frame_change_pre.remove(self._stop)
            return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def execute(self, context):
        # Blender can only stop the animation via a frame event handler...
        bpy.context.scene.frame_set(1)
        bpy.app.handlers.frame_change_pre.append(self._stop)
        bpy.ops.screen.animation_play()

        return {'RUNNING_MODAL'}

class RunSimulationOperator(bpy.types.Operator):
    """Operator that  first checks to see if sensors were added before
     allowing the user to name a simulation and running it.
    """

    bl_idname = "bodysim.run_sim"
    bl_label = "Run Simulation"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        model = context.scene.objects['model']
        if 'sensor_info' not in model or not model['sensor_info']:
            bpy.ops.bodysim.message('INVOKE_DEFAULT', 
                msg_type = "Error", message = 'No sensors were added.')
            return {'CANCELLED'}

        bpy.ops.bodysim.simulation_dialog('INVOKE_DEFAULT')
        return {'FINISHED'}

class SimulationDialogOperator(bpy.types.Operator):
    """Operator that launches popup for naming the simulation, choosing a frame
     range, and number of samples. After error checking, it finally runs the
     simulation.
    """

    bl_idname = "bodysim.simulation_dialog"
    bl_label = "Enter properties for this simulation."
    simulation_name = bpy.props.StringProperty(name="Name: ", )
    samples = bpy.props.IntProperty(name="LOS Free Space Samples: ",
                                    default=300,
                                    min=1)
    start_frame = bpy.props.IntProperty(name="Start Frame No.: ", default=1,
                                        min=1)
    end_frame = bpy.props.IntProperty(name="End Frame No.: ", default=100,
                                      min=1)

    def execute(self, context):
        global simulation_ran
        global temp_sim_ran
        global sim_list
        Bodysim.sim_params.start_frame = self.start_frame
        Bodysim.sim_params.end_frame = self.end_frame
        simulation_ran = False
        model = context.scene.objects['model']
        scene = bpy.context.scene

        if 'session_path' not in model:
            session_path = Bodysim.file_operations.bodysim_conf_path + os.sep + 'tmp'
            os.mkdir(Bodysim.file_operations.bodysim_conf_path + os.sep + 'tmp')
            Bodysim.file_operations.set_session_element(session_path)
            temp_sim_ran = True
        else:
            session_path =  model['session_path']

        path = session_path + os.sep + self.simulation_name
        model['current_simulation_path'] = path

        # Make sure the named simulation does not already exist.
        if os.path.exists(path):
            bpy.ops.bodysim.message('INVOKE_DEFAULT', msg_type = "Error",
                                    message = 'A simulation with that name already exists!')
            return {'CANCELLED'}

        # Frame range error checking
        if self.end_frame <= self.start_frame:
            bpy.ops.bodysim.message('INVOKE_DEFAULT', msg_type = "Error",
                                    message = 'Invalid frame range.')
            return {'CANCELLED'}

        if self.end_frame > scene.frame_end or self.start_frame > scene.frame_end:
            bpy.ops.bodysim.message('INVOKE_DEFAULT', msg_type = "Error",
                                    message = 'Scene only has ' + str(scene.frame_end) + ' frames.')
            return {'CANCELLED'}

        sim_list.append(self.simulation_name)
        draw_previous_run_panel(sim_list)
        os.mkdir(path)
        os.mkdir(path + os.sep + 'Trajectory')
        Bodysim.sim_params.trajectory_path = path + os.sep + 'Trajectory'
        sensor_dict = context.scene.objects['model']['sensor_info']

        Bodysim.file_operations.write_simulation_xml(self.simulation_name,
                                                     sensor_dict,
                                                     path,
                                                     session_path)

        bpy.ops.bodysim.track_sensors('EXEC_DEFAULT', frame_start=self.start_frame,
                                      frame_end=self.end_frame, path=path,
                                      sample_count=self.samples)
        simulation_ran = True
        return {'FINISHED'}

    def invoke(self, context, event):
        model = context.scene.objects['model']
        self.simulation_name = "simulation_" + str(len(sim_list))
        return context.window_manager.invoke_props_dialog(self)

class LoadSimulationOperator(bpy.types.Operator):
    """Loads a previously run simulation along with corresponding
     sensor data.
     This will create boolean attributes (one per simulated variable) for each
     created sensor object. A True value means that the specified variable
     will be simulated on that sensor.
    """

    bl_idname = "bodysim.load_simulation"
    bl_label = "Load a simulation."

    simulation_name = bpy.props.StringProperty()

    def execute(self, context):
        # TODO Check if there were any unsaved modifications first.
        bpy.ops.bodysim.reset_sensors('INVOKE_DEFAULT')
        # Navigate to correct folder to load the correct sensors.xml
        model = context.scene.objects['model']
        sensor_xml_path = model['session_path'] + os.sep + self.simulation_name + os.sep + 'sensors.xml'
        model['current_simulation_path'] = model['session_path'] + os.sep + self.simulation_name
        sensor_map = Bodysim.file_operations.load_simulation(sensor_xml_path)

        for sensor_location in sensor_map:
            model['sensor_info'][sensor_location] = (sensor_map[sensor_location]['name'],
                                                     sensor_map[sensor_location]['colors'])
            Bodysim.vertex_operations.select_vertex_group(sensor_location, context)
            Bodysim.vertex_operations.bind_sensor_to_active_vg(context,
                tuple([float(color) for color in sensor_map[sensor_location]['colors'].split(',')]))

            context.scene.objects['sensor_' + sensor_location].sensor_name = sensor_map[sensor_location]['name']

            for variable in sensor_map[sensor_location]['variables']:
                setattr(context.scene.objects['sensor_' + sensor_location], variable, True)

            Bodysim.current_sensors_panel.draw_sensor_list_panel(model['sensor_info'])

        return {'FINISHED'}

class DeleteSimulationOperator(bpy.types.Operator):
    """Operator that deletes a simulation from the current session."""

    bl_idname = "bodysim.delete_simulation"
    bl_label = "Deletes a simulation."

    simulation_name = bpy.props.StringProperty()

    def execute(self, context):
        global sim_list

        model = context.scene.objects['model']
        Bodysim.file_operations.remove_simulation(model['session_path'], self.simulation_name)
        if self.simulation_name in model['current_simulation_path']:
            # Clear the sensor panel if this simulation is currently loaded.
            bpy.ops.bodysim.reset_sensors('INVOKE_DEFAULT')
        sim_list = Bodysim.file_operations.read_session_file(model['session_path'] + '.xml')
        draw_previous_run_panel(sim_list)
        return {'FINISHED'}

def draw_previous_run_panel(list_of_simulations):
    """Draws the list of previously run simulations; one row of buttons
     per simulation.
     Using this panel, the user can load or delete previous
     simulations. Note that this panel is updated a) when loading
     a session and b) after successful execution of a simulation.
    """

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def _draw_previous_run_buttons(self, context):
        """Function that draws the individual rows of previous
         simulations.
        """

        layout = self.layout
        for _previousRun in self.sim_runs:
            row = layout.row(align = True)
            row.alignment = 'EXPAND'
            row.operator("bodysim.load_simulation", text = _previousRun).simulation_name = _previousRun
            row.operator("bodysim.delete_simulation", text = "Delete").simulation_name = _previousRun

    panel = type("SimulationSelectPanel", (bpy.types.Panel,),{
        "bl_label": "Previous Simulations",
        "bl_space_type": bl_space_type,
        "bl_region_type": bl_region_type,
        "sim_runs": list_of_simulations,
        "draw": _draw_previous_run_buttons},)

    bpy.utils.register_class(panel)

class SimTools(bpy.types.Panel):
    """Panel that allows user to save and load sessions, run
     simulations, and graph variables.
    """

    bl_label = "Sim Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
 
    def draw(self, context):
        self.layout.operator("bodysim.save_session_to_file", text = "Save Session")
        self.layout.operator("bodysim.read_from_file", text = "Load Session")
        self.layout.operator("bodysim.dry_run", text = "Dry Run")
        self.layout.operator("bodysim.run_sim", text = "Run Simulation")
        self.layout.operator("bodysim.graph", text = "Graph Variables")
        self.layout.operator("bodysim.new_sim", text = "New Simulation")

if __name__ == "__main__":
    bpy.utils.register_module(__name__)
