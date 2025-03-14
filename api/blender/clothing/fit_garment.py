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


def set_color(garment, color):
    """Sets the color of the garment.

    Args:
        garment (bpy.types.Object): The garment object.
        color (str): The color of the garment in Hex format.

    Raises:
        ValueError: If the color is not in Hex format.
    """
    if not color.startswith("#"):
        raise ValueError("Color must be in Hex format")

    if not garment.data.materials:
        mat = bpy.data.materials.new(name="Material")
        garment.data.materials.append(mat)
    else:
        mat = garment.data.materials[0]

    if not mat.use_nodes:
        mat.use_nodes = True

    nodes = mat.node_tree.nodes

    bsdf = nodes.get("Principled BSDF")
    if not bsdf:
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        output = nodes.get("Material Output")
        if output:
            mat.node_tree.links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

    color = color.lstrip("#")
    rgb = tuple(int(color[i : i + 2], 16) / 255 for i in (0, 2, 4))
    bsdf.inputs["Base Color"].default_value = (*rgb, 1)


def set_cloth(garment, cloth_config):
    """Sets the cloth modifier with its specified settings for the garment type.

    The cloth settings are specified in the cloth_config.json file.

    Args:
        garment (bpy.types.Object): The garment object.
        garment_type (str): The type of the garment. Must be 'T-Shirt', 'Sweatshirt', or 'Hoodie'.
    """
    cloth_modifier = garment.modifiers.get("Cloth")

    if not cloth_modifier:
        cloth_modifier = garment.modifiers.new(name="Cloth", type="CLOTH")

    cloth_settings = cloth_modifier.settings
    collision_settings = cloth_modifier.collision_settings

    cloth_settings.quality = cloth_config["quality"]
    cloth_settings.time_scale = cloth_config["time_scale"]
    cloth_settings.mass = cloth_config["mass"]
    cloth_settings.air_damping = cloth_config["air_damping"]
    cloth_settings.tension_stiffness = cloth_config["tension_stiffness"]
    cloth_settings.compression_stiffness = cloth_config["compression_stiffness"]
    cloth_settings.shear_stiffness = cloth_config["shear_stiffness"]
    cloth_settings.bending_stiffness = cloth_config["bending_stiffness"]
    cloth_settings.tension_damping = cloth_config["tension_damping"]
    cloth_settings.compression_damping = cloth_config["compression_damping"]
    cloth_settings.shear_damping = cloth_config["shear_damping"]
    cloth_settings.bending_damping = cloth_config["bending_damping"]

    if cloth_config["vertex_group_mass"] is not None:
        cloth_settings.vertex_group_mass = cloth_config["vertex_group_mass"]
        cloth_settings.pin_stiffness = cloth_config["pin_stiffness"]
    cloth_settings.shrink_min = cloth_config["shrink_min"]

    collision_settings.collision_quality = cloth_config["collision_quality"]
    collision_settings.distance_min = cloth_config["distance_min"]
    collision_settings.use_self_collision = cloth_config["use_self_collision"]
    collision_settings.self_distance_min = cloth_config["self_distance_min"]


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
        proxy (bpy.types.Object): The proxy object.
    """
    bpy.context.view_layer.objects.active = garment
    bpy.ops.object.modifier_apply(modifier=surface_mod.name)

    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = proxy
    proxy.select_set(True)
    bpy.ops.object.delete()


def post_process(
    obj,
    seams_bevel=0.01,
    shrink_seams=-0.01,
    thickness=-0.01,
    subdivisions=2,
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
        offset=seams_bevel, offset_pct=0, segments=3, profile=0.5, affect="EDGES"
    )

    bpy.ops.mesh.select_less()
    bpy.ops.transform.shrink_fatten(value=shrink_seams, use_even_offset=True)

    bmesh.update_edit_mesh(obj.data)
    bpy.ops.object.mode_set(mode="OBJECT")

    subdivide = obj.modifiers.new(name="Subdivide", type="SUBSURF")
    subdivide.levels = subdivisions
    subdivide.render_levels = subdivisions
    bpy.ops.object.modifier_apply(modifier="Subdivide")
