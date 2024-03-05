import bpy

export_coll = bpy.data.collections.new("EXPORT_OBJECTS")
bpy.context.scene.collection.children.link(export_coll)

scene = bpy.context.scene
obj_list = scene.objects

for obj in obj_list:
    
    obj_copy = obj.copy()
    obj_copy.data = obj.data.copy()
    obj_copy.parent = None
    obj_copy.name = f'SM_{obj.name}'
    
    export_coll.objects.link(obj_copy)
        
    if obj.children:
        for child in obj.children:
            bpy.ops.object.empty_add(
                location = child.matrix_local.to_translation(),
                rotation = child.matrix_local.to_euler(),
                scale = child.matrix_local.to_scale())
            empty = bpy.context.active_object
            empty.name = f'Socket_{child.name}'
            empty.parent = obj_copy

            bpy.context.scene.collection.objects.unlink(empty)
            export_coll.objects.link(empty)
        
    obj_copy.location = (0, 0, 0)
    obj_copy.rotation_euler = (0, 0, 0)
            