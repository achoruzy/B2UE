import bpy

scene = bpy.context.scene

for obj in scene.objects:
    if len(obj.children):
        for child in obj.children:
            bpy.ops.object.empty_add(
                location = (child.location - obj.location)[:],
                rotation = child.rotation_euler[:],
                scale = child.scale[:])
            empty = bpy.context.active_object
            empty.name = f'Socket_{child.name}'
            empty.parent = obj