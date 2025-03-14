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
    set_color,
    create_proxy,
    set_cloth,
    bake_cloth,
    bind_deform,
    apply_deform,
    post_process,
)
from _helpers.export import export_3D

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
parser.add_argument("--color", type=str, default="#C2C2C2", help="Color of the garment")
parser.add_argument(
    "--output", type=str, required=True, help="Path where the obj file should be saved"
)

args = parser.parse_args()
gender = args.gender
obj_filepath = args.obj
garment_filepath = args.garment
quality = args.quality
color = args.color
output_path = args.output

if not os.path.exists(obj_filepath):
    raise FileNotFoundError(f"File {obj_filepath} not found.")
if not os.path.exists(garment_filepath):
    raise FileNotFoundError(f"File {garment_filepath} not found.")
if quality < 1 or quality > 10:
    raise ValueError(f"Quality must be between 0 and 10, but is {quality}.")

# Load base config
config = load_config(os.path.abspath("./config/config.json"))

# Set base constants
BASE_MESH_PATH = config["base_mesh_path"]
AVATAR_THICKNESS_INNER = config["avatar"]["thickness_inner"]
AVATAR_THICKNESS_OUTER = config["avatar"]["thickness_outer"]
SCALE = config["scale"]
ANIMATION_START_FRAME = config["animation"]["start_frame"]
ANIMATION_END_FRAME = config["animation"]["end_frame"]

# Load garment config
garment_name = os.path.basename(garment_filepath).split(".")[0]
garment_type = garment_name.split("_")[-1].lower()
garment_config = load_config(os.path.abspath(f"./config/garments/{garment_type}.json"))

# Set garment constants
CLOTH_CONFIG = garment_config["cloth_settings"]
SEAMS_BEVEL = garment_config["post_process"]["seams_bevel"]
SHRINK_SEAMS = garment_config["post_process"]["shrink_seams"]
THICKNESS = garment_config["post_process"]["thickness"]
SUBDIVISIONS = garment_config["post_process"]["subdivisions"]

# Disable the Blender splash screen
bpy.context.preferences.view.show_splash = False

# Setup scene
clear_scene()
# setup_scene(
#     camera_location=(0, -34, -10.5),
#     camera_rotation=(90, 0, 0),
#     light_rotation=(90, 0, 0),
# ) # Not needed if no image is rendered

# Create base avatar
avatar = import_blend(
    f"{BASE_MESH_PATH}/SMPL_{gender}.blend",
    f"SMPL_{gender}",
)
add_collision(avatar, AVATAR_THICKNESS_INNER, AVATAR_THICKNESS_OUTER)
scale_obj(avatar, SCALE)
snap_to_ground_plane(avatar)
apply_all_transforms(avatar)

# Import generated obj
generated_obj = import_obj(obj_filepath)
scale_obj(generated_obj, SCALE)
snap_to_ground_plane(generated_obj)
apply_all_transforms(generated_obj)

# Join the avatar and generated obj as shape keys
shape_key_name = "Generated_Pose"
join_as_shapes(avatar, generated_obj, shape_key_name)
animate_shape_key(
    avatar, ANIMATION_START_FRAME + 5, ANIMATION_END_FRAME, shape_key_name
)

# Add garment and simulate cloth
garment = add_garment(garment_filepath, garment_name)
set_color(garment, color)
scale_obj(garment, SCALE)
apply_all_transforms(garment)

# Create proxy and simulate cloth
garment_type = garment_name.split("_")[-1]
if quality == 10:
    set_cloth(garment, CLOTH_CONFIG)
    bake_cloth(ANIMATION_START_FRAME, ANIMATION_END_FRAME)
else:
    cloth_quality = quality / 10  # decimation ratio is from 0 to 1
    proxy = create_proxy(garment, cloth_quality)  # proxy of garment
    set_cloth(proxy, CLOTH_CONFIG)  # simulate cloth on proxy
    surface_mod = bind_deform(
        proxy, garment
    )  # bind proxy to garment so it gets deformed based on proxy cloth simulation
    bake_cloth(ANIMATION_START_FRAME, ANIMATION_END_FRAME)
    apply_deform(garment, surface_mod, proxy)  # apply deform to garment


if not garment_config:
    raise ValueError(f"Garment type {garment_type} not found in config")

post_process(garment, SEAMS_BEVEL, SHRINK_SEAMS, THICKNESS, SUBDIVISIONS)

# Export
scale_obj(avatar, 1 / SCALE)
scale_obj(garment, 1 / SCALE)
export_3D(output_path, materials=True)
