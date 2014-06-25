"""
Provides operator to show error messages to the user.

"""

import bpy

class BodysimMessageOperator(bpy.types.Operator):
    bl_idname = "bodysim.message"
    bl_label = "Message"
    msg_type = bpy.props.StringProperty()
    message = bpy.props.StringProperty()
 
    def execute(self, context):
        self.report({'INFO'}, self.message)
        print(self.message)
        return {'FINISHED'}
 
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_popup(self, width=600, height=200)
 
    def draw(self, context):
        self.layout.label("Message")
        col = self.layout.split().column(align=True)
        col.prop(self, "msg_type")
        col.prop(self, "message")

def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
