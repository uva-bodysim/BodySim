import bpy
import time
import os
import Bodysim.file_operations
import Bodysim.simtools_panel
import Bodysim.status_panel

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
        Bodysim.simtools_panel.drawSimToolsPanel()
        model = context.scene.objects['model']
        model['session_path'] = self.filepath[:-4]

        # Handle the case when simulations have been run before a session is saved.
        Bodysim.file_operations.save_session_to_file(self.filepath)
        model = context.scene.objects['model']
        model['sensor_info'] = {}
        Bodysim.status_panel.reset_state()
        Bodysim.status_panel.session = model['session_path']
        Bodysim.status_panel.draw_status_panel()
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
        Bodysim.simtools_panel.drawSimToolsPanel()
        model = context.scene.objects['model']
        model['sensor_info'] = {}
        model['session_path'] = self.filepath[:-4]
        Bodysim.simtools_panel.sim_list = Bodysim.file_operations.read_session_file(self.filepath,
                                                                                    Bodysim.file_operations.SimulationState.Ran)
        Bodysim.simtools_panel.draw_previous_run_panel(Bodysim.simtools_panel.sim_list)

        Bodysim.simtools_panel.batch_list = Bodysim.file_operations.read_session_file(self.filepath,
                                                                                      Bodysim.file_operations.SimulationState.Batched)
        Bodysim.simtools_panel.draw_batch_panel(Bodysim.simtools_panel.batch_list)

        Bodysim.simtools_panel.saved_list = Bodysim.file_operations.read_session_file(self.filepath,
                                                                                      Bodysim.file_operations.SimulationState.Saved)
        Bodysim.simtools_panel.draw_saved_panel(Bodysim.simtools_panel.saved_list)
        Bodysim.status_panel.reset_state()
        Bodysim.status_panel.session = model['session_path']
        Bodysim.status_panel.draw_status_panel()
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class SessionTools(bpy.types.Panel):
    """Panel that allows user to save and load sessions. """

    bl_label = "Session Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
 
    def draw(self, context):
        self.layout.operator("bodysim.save_session_to_file", text = "New Session")
        self.layout.operator("bodysim.read_from_file", text = "Load Session")

if __name__ == "__main__":
    bpy.utils.register_module(__name__)
