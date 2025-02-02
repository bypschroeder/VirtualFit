import bpy
import json
import os
import bmesh


def add_garment(garment_filepath, obj_name):
    """Adds a garment to the scene.

    Args:
        garment_filepath (str): The path to the garment blend file.
        obj_name (str): The name of the garment object.

    Raises:
        FileNotFoundError: If the garment blend file is not found.
        ValueError: If the garment object is not found.

    Returns:
        bpy.types.Object: The added garment object.
    """
    if not os.path.exists(garment_filepath):
        raise FileNotFoundError(f"File {garment_filepath} not found.")

    with bpy.data.libraries.load(garment_filepath, link=False) as (data_from, data_to):
        if obj_name in data_from.objects:
            data_to.objects.append(obj_name)

    obj = bpy.data.objects.get(obj_name)

    if obj:
        bpy.context.collection.objects.link(obj)
        print(f"{obj_name} was appended")
    else:
        raise ValueError(f"Object {obj_name} not found")

    return obj


def set_cloth(garment, garment_type):
    """Sets the cloth modifier with its specified settings for the garment type.

    The cloth settings are specified in the cloth_config.json file.

    Args:
        garment (bpy.types.Object): The garment object.
        garment_type (str): The type of the garment. Must be 'T-Shirt', 'Sweatshirt', or 'Hoodie'.
    """
    with open("./clothing/cloth_config.json", "r") as f:
        cloth_config = json.load(f)
    garment_config = cloth_config[garment_type]

    cloth_modifier = garment.modifiers.get("Cloth")

    if not cloth_modifier:
        cloth_modifier = garment.modifiers.new(name="Cloth", type="CLOTH")

    cloth_settings = cloth_modifier.settings
    collision_settings = cloth_modifier.collision_settings

    cloth_settings.quality = garment_config["quality"]
    cloth_settings.time_scale = garment_config["time_scale"]
    cloth_settings.mass = garment_config["mass"]
    cloth_settings.air_damping = garment_config["air_damping"]
    cloth_settings.tension_stiffness = garment_config["tension_stiffness"]
    cloth_settings.compression_stiffness = garment_config["compression_stiffness"]
    cloth_settings.shear_stiffness = garment_config["shear_stiffness"]
    cloth_settings.bending_stiffness = garment_config["bending_stiffness"]
    cloth_settings.tension_damping = garment_config["tension_damping"]
    cloth_settings.compression_damping = garment_config["compression_damping"]
    cloth_settings.shear_damping = garment_config["shear_damping"]
    cloth_settings.bending_damping = garment_config["bending_damping"]

    if garment_config["vertex_group_mass"] is not None:
        cloth_settings.vertex_group_mass = garment_config["vertex_group_mass"]
        cloth_settings.pin_stiffness = garment_config["pin_stiffness"]
    cloth_settings.shrink_min = garment_config["shrink_min"]

    collision_settings.collision_quality = garment_config["collision_quality"]
    collision_settings.distance_min = garment_config["distance_min"]
    collision_settings.use_self_collision = garment_config["use_self_collision"]
    collision_settings.self_distance_min = garment_config["self_distance_min"]


def bake_cloth(start_frame, end_frame):
    """Bakes the cloth animation for the garment.

    Args:
        start_frame (int): The start frame of the cloth animation.
        end_frame (int): The end frame of the cloth animation.
    """
    for scene in bpy.data.scenes:
        for object in scene.objects:
            for modifier in object.modifiers:
                if modifier.type == "CLOTH":
                    modifier.point_cache.frame_start = start_frame
                    modifier.point_cache.frame_end = end_frame
                    with bpy.context.temp_override(
                        scene=scene,
                        active_object=object,
                        point_cache=modifier.point_cache,
                    ):
                        bpy.ops.ptcache.bake(bake=True)
    bpy.context.scene.frame_current = end_frame


def create_proxy(garment, decimation_ratio=0.2):
    """Creates a copy of the garment with decimation applied for faster simulation.

    Args:
        garment (bpy.types.Object): The garment object.
        decimation_ratio (float, optional): The ratio of the decimation. Defaults to 0.2.

    Returns:
        bpy.types.Object: The proxy object.
    """
    proxy = garment.copy()
    proxy.data = garment.data.copy()
    proxy.name = garment.name + "_proxy"
    bpy.context.collection.objects.link(proxy)

    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = proxy
    proxy.select_set(True)

    if "hoodie" in garment.name.lower():
        bpy.ops.object.mode_set(mode="EDIT")

        proxy.vertex_groups.active = proxy.vertex_groups[0]

        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.object.vertex_group_select()
        bpy.ops.mesh.delete(type="FACE")

        bpy.ops.object.mode_set(mode="OBJECT")

    decimate_mod = proxy.modifiers.new(name="Decimate", type="DECIMATE")
    decimate_mod.ratio = decimation_ratio

    bpy.ops.object.modifier_apply(modifier="Decimate")

    for face in proxy.data.polygons:
        face.use_smooth = True

    proxy.hide_render = True

    bpy.context.view_layer.objects.active = proxy
    proxy.select_set(True)

    return proxy


def bind_deform(proxy, garment):
    """Binds the proxy to the garment for deformation.

    Args:
        proxy (bpy.types.Object): The proxy object.
        garment (bpy.types.Object): The garment object.

    Returns:
        bpy.types.Modifier: The surface deform modifier.
    """
    surface_mod = garment.modifiers.new(name="SurfaceDeform", type="SURFACE_DEFORM")
    surface_mod.target = proxy

    bpy.context.view_layer.objects.active = garment
    bpy.ops.object.surfacedeform_bind(modifier=surface_mod.name)

    return surface_mod


def apply_deform(garment, surface_mod, proxy):
    """Applies the surface deform modifier to the garment and deletes the proxy.

    Args:
        garment (bpy.types.Object): The garment object.
        surface_mod (bpy.types.Modifier): The surface deform modifier.
    """
    bpy.context.view_layer.objects.active = garment
    bpy.ops.object.modifier_apply(modifier=surface_mod.name)

    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = proxy
    proxy.select_set(True)
    bpy.ops.object.delete()


def post_process(
    obj,
    thickness,
    seam_shrink,
    levels,
):
    """Post-processes the garment by applying modifiers and modifying its geometry.

    Args:
        obj (bpy.types.Object): The garment object.
        thickness (float): The thickness of the garment.
        levels (int): The number of subdivisions for the garment.
    """
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = obj

    if obj.modifiers.get("Cloth"):
        bpy.ops.object.modifier_apply(modifier="Cloth")

    solidify = obj.modifiers.new(name="Solidify", type="SOLIDIFY")
    solidify.thickness = thickness
    bpy.ops.object.modifier_apply(modifier="Solidify")

    bpy.ops.object.mode_set(mode="EDIT")

    bm = bmesh.from_edit_mesh(obj.data)

    for edge in bm.edges:
        if edge.seam:
            edge.select_set(True)

    bmesh.update_edit_mesh(obj.data)

    bpy.ops.mesh.bevel(
        offset=0.01, offset_pct=0, segments=3, profile=0.5, affect="EDGES"
    )

    bpy.ops.mesh.select_less()
    bpy.ops.transform.shrink_fatten(value=seam_shrink, use_even_offset=True)

    bmesh.update_edit_mesh(obj.data)
    bpy.ops.object.mode_set(mode="OBJECT")

    subdivide = obj.modifiers.new(name="Subdivide", type="SUBSURF")
    subdivide.levels = levels
    subdivide.render_levels = levels

    # Recalculate Normals
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode="OBJECT")
