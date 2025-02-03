import bpy
import os
import sys


# Add all subdirectories of the script directory to the system path so Blender can find the modules
def add_subdirs_to_sys_path(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if os.path.basename(dirpath) == "__pycache__":
            continue
        sys.path.append(dirpath)


script_dir = os.path.dirname(os.path.abspath(__file__))
add_subdirs_to_sys_path(script_dir)

from config.config_loader import load_config
from _helpers.ArgumentParserForBlender import ArgumentParserForBlender
from _helpers.scene import (
    setup_scene,
    clear_scene,
    snap_to_ground_plane,
    apply_all_transforms,
    scale_obj,
)
from smpl.avatar import (
    import_blend,
    import_obj,
    join_as_shapes,
    animate_shape_key,
    add_collision,
)
from clothing.fit_garment import (
    add_garment,
    create_proxy,
    set_cloth,
    bake_cloth,
    bind_deform,
    apply_deform,
    post_process,
)
from _helpers.export import export_3D

# Load the config file
config = load_config()

# Disable the Blender splash screen
bpy.context.preferences.view.show_splash = False

# Parse command line arguments
parser = ArgumentParserForBlender()
parser.add_argument("--gender", type=str, required=True, help="Gender of the avatar")
parser.add_argument("--obj", type=str, required=True, help="Path to the .obj file")
parser.add_argument(
    "--garment", type=str, required=True, help="Path to the .blend file of the garment"
)
parser.add_argument(
    "--quality", type=int, default=5, help="Quality of the cloth simulation (0-10)"
)
parser.add_argument(
    "--output", type=str, required=True, help="Path where the obj file should be saved"
)
args = parser.parse_args()

gender = args.gender
obj_filepath = args.obj
garment_filepath = args.garment
quality = args.quality
output_path = args.output

if not os.path.exists(obj_filepath):
    raise FileNotFoundError(f"File {obj_filepath} not found.")
if not os.path.exists(garment_filepath):
    raise FileNotFoundError(f"File {garment_filepath} not found.")
if quality < 1 or quality > 10:
    raise ValueError(f"Quality must be between 0 and 10, but is {quality}.")

# Setup scene
clear_scene()
setup_scene(
    camera_location=(0, -34, -10.5),
    camera_rotation=(90, 0, 0),
    light_rotation=(90, 0, 0),
)

# Create avatar and animate to generated obj
avatar = import_blend(
    f"/vf_blender/smpl/base_mesh/SMPL_{gender}.blend",
    f"SMPL_{gender}",
)
add_collision(avatar, 0.001, 0.001)
scale_obj(avatar, 10)
snap_to_ground_plane(avatar)
apply_all_transforms(avatar)
generated_obj = import_obj(obj_filepath)
scale_obj(generated_obj, 10)
snap_to_ground_plane(generated_obj)
apply_all_transforms(generated_obj)

shape_key_name = "Generated_Pose"
join_as_shapes(avatar, generated_obj, shape_key_name)
animate_shape_key(avatar, 5, 50, shape_key_name)

# Add garment and simulate cloth
garment_name = garment_filepath.split("/")[-1].split(".")[0]
garment = add_garment(garment_filepath, garment_name)
scale_obj(garment, 10)
apply_all_transforms(garment)

# Create proxy and simulate cloth
garment_type = garment_name.split("_")[-1]
if quality == 10:
    set_cloth(garment, garment_type)
    bake_cloth(0, 70)
else:
    cloth_quality = quality / 10  # decimation ratio is from 0 to 1
    proxy = create_proxy(garment, cloth_quality)  # proxy of garment
    set_cloth(proxy, garment_type)  # simulate cloth on proxy
    surface_mod = bind_deform(
        proxy, garment
    )  # bind proxy to garment so it gets deformed based on proxy cloth simulation
    bake_cloth(0, 70)
    apply_deform(garment, surface_mod, proxy)  # apply deform to garment


garment_config = config["garment"].get(garment_type)
if not garment_config:
    raise ValueError(f"Garment type {garment_type} not found in config")

thickness = garment_config.get("thickness")
levels = garment_config.get("levels")
shrink = garment_config.get("shrink")  # How much the seams are shrunk
post_process(garment, thickness, shrink, levels)

# Export
scale_obj(avatar, 0.1)
scale_obj(garment, 0.1)
format = config["export"]["3D"]["format"]
export_3D(output_path, format)
