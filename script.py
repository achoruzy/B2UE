import bpy

export_coll = bpy.data.collections.new("EXPORT")
bpy.context.scene.collection.children.link(export_coll)

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
            

for obj in scene.objects:
    if obj.type != 'EMPTY':
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.duplicate()
        print(obj.name)
        # export_coll.objects.link(obj_copy)
        # bpy.ops.object.move_to_collection(collection_index=len(bpy.data.collections.values()))
        
        # if obj.children:
        #     for child in obj.children:
        #         if child.type == 'EMPTY':
        #             child_copy = child.copy()
        #             child.parent = obj_copy
        
        # bpy.context.active_object.location = (0, 0, 0)
        # bpy.context.active_object.rotation_euler = (0, 0, 0)
            