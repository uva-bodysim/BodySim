import bpy

''' Extract all vertices corresponding to the
    original vertex groups of the object, "obj" 
    and store as dictionary {vertex_group_name: [vertices]}
'''
    
def extract_v_group_vertices(obj):
    group_lookup = {g.index: g.name for g in obj.vertex_groups}
    verts = {name: [] for name in group_lookup.values()}
    for v in obj.data.vertices:
        in_group = False
        for g in v.groups:
            in_group = True
            verts[group_lookup[g.group]].append(v.index)

        if not in_group:
            v.select = True


# select the human model
ob = bpy.data.objects['model']

# ensure we are in "Object Mode" so functions will work properly
bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

# orgnaize vertices (needed to organize polygons)
ob_verts = extract_v_group_vertices(ob)

bpy.ops.object.mode_set(mode='EDIT', toggle=False)