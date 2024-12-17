import bpy
import json

def add_garment(garment_filepath, obj_name):
    with bpy.data.libraries.load(garment_filepath, link=False) as (data_from, data_to):
        if obj_name in data_from.objects:
            data_to.objects.append(obj_name)

    obj = bpy.data.objects.get(obj_name)

    if obj:
        bpy.context.collection.objects.link(obj)
        print(f"{obj_name} was appended")
    else:
        raise ValueError(f"Object {obj_name} not found.")

    return obj

def set_cloth(garment, garment_type):
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
    for scene in bpy.data.scenes:
        for object in scene.objects:
            for modifier in object.modifiers:
                if modifier.type == "CLOTH":
                    modifier.point_cache.frame_start = start_frame
                    modifier.point_cache.frame_end = end_frame
                    with bpy.context.temp_override(scene=scene,
                                                   active_object=object,
                                                   point_cache=modifier.point_cache):
                        bpy.ops.ptcache.bake(bake=True)
    bpy.context.scene.frame_current = end_frame

def post_process(obj, thickness, levels):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier="Cloth")

    solidify = obj.modifiers.new(name="Solidify", type="SOLIDIFY")
    solidify.thickness = thickness

    subdivide = obj.modifiers.new(name="Subdivide", type="SUBSURF")
    subdivide.levels = levels
    subdivide.render_levels = levels