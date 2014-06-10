import bpy, math
 
def addTwistedCylinder(context, r, nseg, vstep, nplanes, twist):
    verts = []
    faces = []
    w = 2*math.pi/nseg
    a = 0
    da = twist*math.pi/180
    for j in range(nplanes+1):    
        z = j*vstep
        a += da
        for i in range(nseg):
            verts.append((r*math.cos(w*i+a), r*math.sin(w*i+a), z))
            if j > 0:
                i0 = (j-1)*nseg
                i1 = j*nseg
                for i in range(1, nseg):
                    faces.append((i0+i-1, i0+i, i1+i, i1+i-1))
                faces.append((i0+nseg-1, i0, i1, i1+nseg-1))
 
    me = bpy.data.meshes.new("TwistedCylinder")
    me.from_pydata(verts, [], faces)
    ob = bpy.data.objects.new("TwistedCylinder", me)
    context.scene.objects.link(ob)
    context.scene.objects.active = ob
    return ob
 
#
#    User interface
#
 
from bpy.props import *
 
class MESH_OT_primitive_twisted_cylinder_add(bpy.types.Operator):
    '''Add a twisted cylinder'''
    bl_idname = "mesh.primitive_twisted_cylinder_add"
    bl_label = "Add twisted cylinder"
    bl_options = {'REGISTER', 'UNDO'}
 
    radius = FloatProperty(name="Radius",
            default=1.0, min=0.01, max=100.0)
    nseg = IntProperty(name="Major Segments",
            description="Number of segments for one layer",
            default=12, min=3, max=256)
    vstep = FloatProperty(name="Vertical step",
            description="Distance between subsequent planes",
            default=1.0, min=0.01, max=100.0)
    nplanes = IntProperty(name="Planes",
            description="Number of vertical planes",
            default=4, min=2, max=256)
    twist = FloatProperty(name="Twist angle",
            description="Angle between subsequent planes (degrees)",
            default=15, min=0, max=90)
 
    location = FloatVectorProperty(name="Location")
    rotation = FloatVectorProperty(name="Rotation")
    # Note: rotation in radians!
 
    def execute(self, context):
        ob = addTwistedCylinder(context, 
            self.radius, self.nseg, self.vstep, self.nplanes, self.twist)
        ob.location = self.location
        ob.rotation_euler = self.rotation
        #context.scene.objects.link(ob)
        #context.scene.objects.active = ob
        return {'FINISHED'}
 
#
#    Registration
#    Makes it possible to access the script from the Add > Mesh menu
#
 
def menu_func(self, context):
    self.layout.operator("mesh.primitive_twisted_cylinder_add", 
        text="Twisted cylinder", 
        icon='MESH_TORUS')
 
def register():
   bpy.utils.register_module(__name__)
   bpy.types.INFO_MT_mesh_add.prepend(menu_func)
 
def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_mesh_add.remove(menu_func)
 
if __name__ == "__main__":
    register()