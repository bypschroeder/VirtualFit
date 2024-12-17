import bpy

def import_obj(obj_filepath):
    bpy.ops.wm.obj_import(filepath=obj_filepath)

    obj = bpy.context.selected_objects[0]

    obj.modifiers.new(name="Collision", type="COLLISION")
    obj.collision.thickness_inner = 0.001
    obj.collision.thickness_outer = 0.001

    return obj

def join_as_shapes(source_obj, target_obj, shape_key_name):
    bpy.ops.object.select_all(action='DESELECT')

    source_obj.select_set(True)
    target_obj.select_set(True)

    bpy.context.view_layer.objects.active = source_obj

    bpy.ops.object.join_shapes()

    new_shape_key = source_obj.data.shape_keys.key_blocks[-1]
    new_shape_key.name = shape_key_name

    bpy.data.objects.remove(target_obj)

def animate_shape_key(obj, frame_start, frame_end, shape_key_name):
    shape_key = obj.data.shape_keys.key_blocks.get(shape_key_name)
    if not shape_key:
        raise ValueError(f"Shape key {shape_key_name} not found.")
    
    shape_key.value = 0.0
    shape_key.keyframe_insert(data_path="value", frame=frame_start)

    shape_key.value = 1.0
    shape_key.keyframe_insert(data_path="value", frame=frame_end)