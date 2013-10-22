"""
Script that binds a cube to a vertex group.
""" 

import bpy

body_obj = bpy.data.objects['model']
cube_obj = bpy.data.objects["Cube"]

# Bind the cube to a vertex group
cube_obj_const = cube_obj.constraints.new(type="CHILD_OF")
cube_obj_const.target = body_obj
cube_obj_const.subtarget = "Head"

# Reset the cube's relative location.
cube_obj.location = (0.0, 0.0, 0.0)
