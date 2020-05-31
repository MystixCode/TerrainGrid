import bpy, bmesh, mathutils, os
from bpy import context as C
##Attention!: before using script move terrain so that its corner is at x=0,y=0 in positiv direction and apply transforms!
os.system('cls' if os.name == 'nt' else "printf '\033c'")
print("## terrain grid start\n################################################")
print(" - bisect and separate mesh")
chunksize = 16
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(C.object.data)
edges = []
x, y, z = bpy.context.active_object.dimensions
bsaxis = None
if y>x:
    bsaxis = int(y)
else:
    bsaxis = int(x)  
for i in range(0, bsaxis, chunksize):
        ret = bmesh.ops.bisect_plane(bm, geom=bm.verts[:]+bm.edges[:]+bm.faces[:], plane_co=(i,0,0), plane_no=(-1,0,0))
        bmesh.ops.split_edges(bm, edges=[e for e in ret['geom_cut'] if isinstance(e, bmesh.types.BMEdge)])
for i in range(chunksize, bsaxis, chunksize):
        ret = bmesh.ops.bisect_plane(bm, geom=bm.verts[:]+bm.edges[:]+bm.faces[:], plane_co=(0,i,0), plane_no=(0,1,0))
        bmesh.ops.split_edges(bm, edges=[e for e in ret['geom_cut'] if isinstance(e, bmesh.types.BMEdge)])
bmesh.update_edit_mesh(C.object.data)
bpy.ops.mesh.separate(type='LOOSE')
bpy.ops.object.mode_set(mode='OBJECT')

print(" - set origin for new objects")
for ob in bpy.data.objects: 
    bpy.ops.object.select_all(action='DESELECT')
    if ob.type == 'MESH':
        ob.select_set(True)
        mw = ob.matrix_world 
        verts = [ mw @ v.co for v in ob.data.vertices ] # Global coordinates of vertices
        minX = min( [ co.x for co in verts ] ) 
        minY = min( [ co.y for co in verts ] ) 
        bpy.context.scene.cursor.location = (minX, minY, 0.0)
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)

print(" - join objects if on top of eachother")
for ob in bpy.context.view_layer.objects:
    bpy.ops.object.select_all(action='DESELECT') 
    if ob.type == 'MESH':
        for ob2 in bpy.context.view_layer.objects:
            if ob2.type == 'MESH' and ob != ob2:
                if ob.location.x.is_integer() and ob.location.y.is_integer():
                    if ob.location.x <= ob2.location.x and ob.location.x +chunksize > ob2.location.x and ob.location.y <= ob2.location.y and ob.location.y +chunksize > ob2.location.y:
                        ob2.select_set(True)
                        ob.select_set(True)
                        bpy.context.view_layer.objects.active = ob     
                        bpy.ops.object.join()

print(" - rename and duplicate for collisionshapes for godot")
for objy in bpy.data.objects:
    bpy.ops.object.select_all(action='DESELECT')
    if objy.type == 'MESH':
        objy.name = "chunk" + str(objy.location.x) + "_" + str(objy.location.y)
        objy.data.name = "chunk" + str(objy.location.x) + "_" + str(objy.location.y)
        objy.select_set(True)
        bpy.ops.object.duplicate()
        for objz in bpy.context.selected_objects:
            objz.name = objy.name + "-colonly"
            objz.data.name = objy.name + "-colonly"
            objz.parent = objy
            objz.matrix_parent_inverse = objy.matrix_world.inverted()
print("terrain grid done")
#bpy.ops.object.transform_apply(location = True, scale = True, rotation = True)
