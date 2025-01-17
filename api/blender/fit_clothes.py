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
from smpl.avatar import import_obj, join_as_shapes, animate_shape_key
from clothing.fit_garment import add_garment, set_cloth, bake_cloth, post_process
from _helpers.export import export_img, export_3D

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
    "--output", type=str, required=True, help="Path to the output directory"
)
args = parser.parse_args()

gender = args.gender
obj_filepath = args.obj
garment_filepath = args.garment
output_path = args.output

if not os.path.exists(obj_filepath):
    raise FileNotFoundError(f"File {obj_filepath} not found.")
if not os.path.exists(garment_filepath):
    raise FileNotFoundError(f"File {garment_filepath} not found.")

# Setup scene
clear_scene()
setup_scene(
    camera_location=(0, -34, -10.5),
    camera_rotation=(90, 0, 0),
    light_rotation=(90, 0, 0),
)

# Create avatar and animate to generated obj
avatar = import_obj(f"./smpl/base_mesh/{gender}.obj")
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
bpy.context.view_layer.objects.active = garment
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

garment_type = garment_name.split("_")[-1]
set_cloth(garment, garment_type)
bake_cloth(0, 70)

thickness_settings = {
    "T-Shirt": -0.01,
    "Sweatshirt": -0.03,
    "Hoodie": -0.05,
}
post_process(garment, thickness_settings.get(garment_type), 2)

# Export
scale_obj(avatar, 0.1)
scale_obj(garment, 0.1)
format = config["export"]["3D_format"]
type = config["export"]["3D_type"]
export_3D(output_path, format, type)
