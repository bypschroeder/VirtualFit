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
from _helpers.scene import setup_scene, clear_scene, snap_to_ground_plane, apply_all_transforms, scale_obj
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
parser.add_argument("--garment", type=str, required=True, help="Path to the .blend file of the garment")
parser.add_argument("--output", type=str, required=True, help="Path to the output directory")
args = parser.parse_args()

gender = args.gender
obj_filepath = args.obj
garment_filepath = args.garment
output_dir = args.output

if not os.path.exists(obj_filepath):
    raise FileNotFoundError(f"File {obj_filepath} not found.")
if not os.path.exists(garment_filepath):
    raise FileNotFoundError(f"File {garment_filepath} not found.")

# Setup scene
clear_scene()
setup_scene()

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
animate_shape_key(avatar, 0, 50, shape_key_name)

# Add garment and simulate cloth
garment_name = garment_filepath.split("/")[-1].split(".")[0]
garment = add_garment(garment_filepath, garment_name)
garment_type = garment_name.split("_")[-1]
set_cloth(garment, garment_type)
bake_cloth(0, 80)
post_process(garment, -0.1, 2)

# Export
os.makedirs(output_dir, exist_ok=True)
render_path = os.path.join(output_dir, f"{garment_name}_{gender}.png")
export_img(render_path, config["export"]["img_format"] ,config["export"]["img_type"], config["export"]["transparent_bg"])

format = config["export"]["3D_format"]
type = config["export"]["3D_type"]
obj_path = os.path.join(output_dir, f"{garment_name}_{gender}.{format.lower()}")
export_3D(obj_path, format, type)