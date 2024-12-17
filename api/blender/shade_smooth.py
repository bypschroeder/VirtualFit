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
from _helpers.scene import clear_scene
from smpl.avatar import import_obj
from _helpers.export import export_3D

config = load_config()

bpy.context.preferences.view.show_splash = False

parser = ArgumentParserForBlender()
parser.add_argument("--obj", type=str, required=True, help="Path to the .obj file")
args = parser.parse_args()

obj_filepath = args.obj

if not os.path.exists(obj_filepath):
    raise FileNotFoundError(f"File {obj_filepath} not found.")

clear_scene()

obj = import_obj(obj_filepath)
mesh = obj.data

for f in mesh.polygons:
    f.use_smooth = True

format = config["export"]["3D_format"]
type = config["export"]["3D_type"]
obj_path = obj_filepath.replace(".obj", "_smooth.obj")
export_3D(obj_path, format, type)