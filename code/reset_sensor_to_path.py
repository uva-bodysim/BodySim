import bpy

cubes = 3
scene = bpy.context.scene

for i in range(cubes):
    bpy.data.objects["Cube_" + str(i)].constraints.clear() 
