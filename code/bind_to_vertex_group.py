"""
Script that binds a cube to a vertex group.

The wire frame of the blender object this is working on must
    have the name "model". The vertex groups must be of this
    "model" object.
""" 

import bpy


def list_vertex_group():
    """Returns a list of names to vertex groups"""
    return bpy.data.objects["model"].vertex_groups.keys()


def parse_vertex_group(groups):
    """Takes in the list of vertex groups and splits them by body part"""
    categories = {}
    for i in groups:
        body_part = i.split("-")[0]
        if body_part not in categories: categories[body_part] = []
        categories[body_part].append(i)
    return categories


def select_vertex_group(vg_name):
    """Given a vertex group name, selects and displays it on the screen"""
    bpy.ops.object.mode_set(mode="OBJECT")
    obj = bpy.data.objects["model"]
    bpy.context.scene.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="DESELECT")
    bpy.ops.object.vertex_group_set_active(group=vg_name)
    bpy.ops.object.vertex_group_select()
    
def cancel_selection():
    """Go back to object mode after selection"""
    bpy.ops.object.mode_set(mode="OBJECT")

def bind_to_vertex_group(obj):
    """ Binds the object passed in to the currently selected vertex group"""
    vg = bpy.context.object.vertex_groups.active
    body_obj = bpy.data.objects['model']

    # Bind the obj to a vertex group
    obj_const = obj.constraints.new(type="CHILD_OF")
    obj_const.target = body_obj
    obj_const.subtarget = vg.name

    # Reset the cube's relative location.
    cube_obj.location = (0.0, 0.0, 0.0)

    cancel_selection()

if __name__ == "__main__":
    cube_obj = bpy.data.objects["Cube"]
    body_obj = bpy.data.objects['model']
    print("Vertex groups: ")
    print(list_vertex_group())
    print(parse_vertex_group(list_vertex_group()))
    select_vertex_group("Neck-0")
    bind_to_vertex_group(cube_obj)
