import bpy
import math
import bmesh

def clear_scene():
    """
    Clears the current scene of all objects.
    """
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    for collection in bpy.data.collections:
        if collection.name == "Collection":
            bpy.data.collections.remove(collection)

def setup_scene():
    """
    Adds a camera and light to the scene.
    """

    camera_rotation = tuple(math.radians(angle) for angle in (90, 0, 0))
    light_rotation = tuple(math.radians(angle) for angle in (90, 0, 0))

    bpy.ops.object.camera_add(location=(0, -34, 10.5), rotation=camera_rotation)
    bpy.ops.object.light_add(type="SUN", radius=10, location=(0, 0, 0), rotation=light_rotation)

def snap_to_ground_plane(obj):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')

    bm = bmesh.from_edit_mesh(obj.data)
    bm.verts.ensure_lookup_table()

    min_z = float("inf")
    for vert in bm.verts:
        world_coord = obj.matrix_world @ vert.co
        min_z = min(min_z, world_coord.z)

    bpy.ops.object.mode_set(mode='OBJECT')

    obj.location.z -= min_z

def apply_all_transforms(obj):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

def scale_obj(obj, scale_factor):
    obj.scale = (scale_factor, scale_factor, scale_factor)