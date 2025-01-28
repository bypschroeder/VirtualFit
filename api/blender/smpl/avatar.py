import bpy
import os


# TODO: import_blend and add_garment is the same
def import_blend(blend_filepath, obj_name):
    """Appends an object from a blend file to the scene.

    Args:
        blend_filepath (str): The path to the blend file.
        obj_name (str): The name of the object to import.

    Raises:
        FileNotFoundError: If the blend file is not found.
        ValueError: If the object is not found.

    Returns:
        bpy.types.Object: The imported object.
    """
    if not os.path.exists(blend_filepath):
        raise FileNotFoundError(f"File {blend_filepath} not found.")

    with bpy.data.libraries.load(blend_filepath, link=False) as (data_from, data_to):
        if obj_name in data_from.objects:
            data_to.objects.append((obj_name))

    obj = bpy.data.objects.get(obj_name)

    if obj:
        bpy.context.collection.objects.link(obj)
        print(f"{obj_name} was appended")
    else:
        raise ValueError(f"Object {obj_name} not found")

    return obj


def import_obj(obj_filepath):
    """Imports an obj file as an object into the scene.

    Args:
        obj_filepath (str): The path to the obj file.
        thickness_inner (float): The inner thickness of the collision.
        thickness_outer (float): The outer thickness of the collision.

    Returns:
        bpy.types.Object: The imported object.
    """
    bpy.ops.wm.obj_import(filepath=obj_filepath)

    obj = bpy.context.selected_objects[0]

    return obj


def join_as_shapes(source_obj, target_obj, shape_key_name):
    """Joins two objects as a shape key on the source object.

    Args:
        source_obj (bpy.types.Object): The source object which the shape key will be added to.
        target_obj (bpy.types.Object): The target object which will be joined.
        shape_key_name (str): The name of the shape key.
    """
    bpy.ops.object.select_all(action="DESELECT")

    source_obj.select_set(True)
    target_obj.select_set(True)

    bpy.context.view_layer.objects.active = source_obj

    bpy.ops.object.join_shapes()

    new_shape_key = source_obj.data.shape_keys.key_blocks[-1]
    new_shape_key.name = shape_key_name

    bpy.data.objects.remove(target_obj)


def animate_shape_key(obj, frame_start, frame_end, shape_key_name):
    """Animates a shape key on an object

    Args:
        obj (bpy.types.Object): The object to animate.
        frame_start (int): The start frame of the animation.
        frame_end (int): The end frame of the animation.
        shape_key_name (str): The name of the shape key to animate.

    Raises:
        ValueError: If the shape key is not found.
    """
    shape_key = obj.data.shape_keys.key_blocks.get(shape_key_name)
    if not shape_key:
        raise ValueError(f"Shape key {shape_key_name} not found.")

    shape_key.value = 0.0
    shape_key.keyframe_insert(data_path="value", frame=frame_start)

    shape_key.value = 1.0
    shape_key.keyframe_insert(data_path="value", frame=frame_end)


def add_collision(obj, thickness_inner, thickness_outer):
    """Adds a collision modifier to an object.

    Args:
        obj (bpy.types.Object): The object to add the collision modifier to.
        thickness_inner (float): The inner thickness of the collision.
        thickness_outer (float): The outer thickness of the collision.

    Raises:
        ValueError: If the object is not found.
    """
    if not obj:
        raise ValueError("Object not Found")
    obj.modifiers.new(name="Collision", type="COLLISION")
    obj.collision.thickness_inner = thickness_inner
    obj.collision.thickness_outer = thickness_outer
