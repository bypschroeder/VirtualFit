import bpy
import math
import bmesh


def clear_scene():
    """Clears the current scene of all objects."""
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()

    for collection in bpy.data.collections:
        if collection.name == "Collection":
            bpy.data.collections.remove(collection)


def setup_scene(camera_location, camera_rotation, light_rotation):
    """Sets up the scene with a camera and light.

    Args:
        camera_location (tuple): The location of the camera. Must be a tuple of x, y, and z coordinates.
        camera_rotation (tuple): The rotation of the camera. Must be a tuple of x, y, and z angles in degrees.
        light_rotation (tuple): The rotation of the light. Must be a tuple of x, y, and z angles in degrees.
    """
    c_rotation = tuple(math.radians(angle) for angle in camera_rotation)
    l_rotation = tuple(math.radians(angle) for angle in light_rotation)

    bpy.ops.object.camera_add(location=camera_location, rotation=c_rotation)
    bpy.ops.object.light_add(
        type="SUN", radius=10, location=(0, 0, 0), rotation=l_rotation
    )


def snap_to_ground_plane(obj):
    """Snaps an object to the ground plane.

    Args:
        obj (bpy.types.Object): The object to snap to the ground plane.
    """
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")

    bm = bmesh.from_edit_mesh(obj.data)
    bm.verts.ensure_lookup_table()

    min_z = float("inf")
    for vert in bm.verts:
        world_coord = obj.matrix_world @ vert.co
        min_z = min(min_z, world_coord.z)

    bpy.ops.object.mode_set(mode="OBJECT")

    obj.location.z -= min_z


def apply_all_transforms(obj):
    """Applies all transformations to an object.

    Args:
        obj (bpy.types.Object): The object to apply all transformations to.
    """
    if bpy.context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")

    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)


def scale_obj(obj, scale_factor):
    """Scales an object by a given factor.

    Args:
        obj (bpy.types.Object): The object to scale.
        scale_factor (float): The factor by which to scale the object.
    """
    obj.scale = (scale_factor, scale_factor, scale_factor)

    if bpy.context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")

    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
