import bpy
import os
import sys
from mathutils import Vector


# Add all subdirectories of the script directory to the system path so Blender can find the modules
def add_subdirs_to_sys_path(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if os.path.basename(dirpath) == "__pycache__":
            continue
        sys.path.append(dirpath)


script_dir = os.path.dirname(os.path.abspath(__file__))
add_subdirs_to_sys_path(script_dir)

from _helpers.ArgumentParserForBlender import ArgumentParserForBlender
from _helpers.scene import clear_scene, setup_scene, scale_obj
from _helpers.export import export_preview
from clothing.fit_garment import add_garment, post_process
from config.config_loader import load_config

script_dir = os.path.dirname(os.path.abspath(__file__))
add_subdirs_to_sys_path(script_dir)

config = load_config()

bpy.context.preferences.view.show_splash = False

parser = ArgumentParserForBlender()
parser.add_argument("--blend", type=str, required=True, help="Path to the blend file")
parser.add_argument(
    "--output", type=str, required=True, help="Path where to preview should be saved"
)
args = parser.parse_args()

blend = args.blend
output = args.output

clear_scene()

mesh_name = blend.split("/")[-1].split(".")[0]
print(blend, mesh_name)
obj = add_garment(blend, mesh_name)

scale_obj(obj, 10)
bpy.context.view_layer.objects.active = obj
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

local_bbox_center = 0.0125 * sum((Vector(b) for b in obj.bound_box), Vector())
global_bbox_center = obj.matrix_world @ local_bbox_center

bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")

obj.location = (0, 0, 0)

if "T-Shirt" in mesh_name:
    thickness = config["garment"]["T-Shirt"]["thickness"]
    levels = config["garment"]["T-Shirt"]["levels"]
elif "Sweatshirt" in mesh_name:
    thickness = config["garment"]["Sweatshirt"]["thickness"]
    levels = config["garment"]["Sweatshirt"]["levels"]
elif "Hoodie" in mesh_name:
    thickness = config["garment"]["Hoodie"]["thickness"]
    levels = config["garment"]["Hoodie"]["levels"]
else:
    thickness = -0.01

post_process(obj, thickness, levels)

setup_scene(
    camera_location=(0, -21, 0),
    camera_rotation=(90, 0, 0),
    light_rotation=(90, 0, 0),
)

resolution_x = config["export"]["preview"]["resolution_x"]
resolution_y = config["export"]["preview"]["resolution_y"]
samples = config["export"]["preview"]["samples"]
export_preview(output, resolution_x, resolution_y, samples)
