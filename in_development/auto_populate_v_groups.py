import bpy

''' Create a new vertex group in the object, "obj"
    with name, "name" using vertices of the polygon, "poly"
'''
def create_new_group(name, obj, poly):
    group = obj.vertex_groups.new(name)
    vert_list = [v for v in poly.vertices]
    group.add(vert_list, 1.0, 'ADD')

''' Extract all vertices corresponding to the
    original vertex groups of the object, "obj" 
    and store as dictionary {vertex_group_name: [vertices]}
'''
    
def extract_v_group_vertices(obj):
    group_lookup = {g.index: g.name for g in obj.vertex_groups}
    verts = {name: [] for name in group_lookup.values()}
    for v in obj.data.vertices:
        for g in v.groups:
            verts[group_lookup[g.group]].append(v.index)
    return verts 
        
# testing function  
def extract_v_group_poly(obj, verts):
    polys = obj.data.polygons
    polys_extracted = dict()
    for v in verts.items():
        polys_extracted[v[0]] = [(p, p.vertices.data.area) for p in polys if set(p.vertices).issubset(v[1])]
    return polys_extracted

# testing function
def extract_v_group_poly_filtered(obj, verts, cutoff):
    polys = obj.data.polygons
    polys_extracted = dict()
    for v in verts.items():
        polys_extracted[v[0]] = [(p, p.vertices.data.area) for p in polys if (set(p.vertices).issubset(v[1]) and p.vertices.data.area < cutoff)]
    return polys_extracted

''' Extract the polygons corresponding the vertex groups of the object, "obj"
    and store as dictionary {vertex_group_name: [polygons]}. 
    Ensure each polygon is assigned to only one vertex_group 
'''
def extract_v_group_poly_pruned(obj, verts):
    polys = [p for p in obj.data.polygons]
    polys_extracted = {name: [] for name in verts.keys()}
    for p in polys:
        for v in verts.items():
            if(set(p.vertices).issubset(v[1])):
                polys_extracted[v[0]].append(p)
                polys.remove(p) # ensure single assignment
                break
    return polys_extracted

''' Create a vertex group for each polygon and name it relative to the
    original vertex group (part of the body) from which it was created
'''
def populate_vertex_groups(obj, poly):
    for g in poly.items():
        for i in range(len(g[1])):
            create_new_group(g[0] + '-'+ str(i), obj, g[1][i])
            
# select the human model
ob = bpy.data.objects['model']

# ensure we are in "Object Mode" so functions will work properly
bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

# orgnaize vertices (needed to organize polygons)
ob_verts = extract_v_group_vertices(ob)

# organize polygons
ob_poly_p = extract_v_group_poly_pruned(ob, ob_verts)

# create a vertex group per polygon
populate_vertex_groups(ob, ob_poly_p)