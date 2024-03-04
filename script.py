import bpy

scene = bpy.context.scene

for obj in scene.objects:
    if obj.children:
        for child in obj.children:
            bpy.ops.object.empty_add(
                location = child.matrix_local.to_translation(),
                rotation = child.matrix_local.to_euler(),
                scale = child.matrix_local.to_scale())
            empty = bpy.context.active_object
            empty.name = f'Socket_{child.name}'
            empty.parent = obj
            
export_coll = bpy.data.collections.new("EXPORT")
bpy.context.scene.collection.children.link(export_coll)

for obj in scene.objects:
    if obj.type != 'EMPTY':
        obj_copy = obj.copy()
        # export_coll.objects.link(obj_copy)
        bpy.ops.object.move_to_collection(collection_index=len(bpy.data.collections.values()))
        
        if obj.children:
            for child in obj.children:
                child_copy = child.copy()
                child_copy.parent = obj_copy
        
        obj_copy.location = (0, 0, 0)
        obj_copy.rotation_euler = (0, 0, 0)
            