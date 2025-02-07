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

# Parse command line arguments
parser = ArgumentParserForBlender()
parser.add_argument("--blend", type=str, required=True, help="Path to the blend file")
parser.add_argument(
    "--output", type=str, required=True, help="Path where to preview should be saved"
)

args = parser.parse_args()
blend = args.blend
output = args.output

# Load base config
config = load_config(os.path.abspath("./config/config.json"))

# Set base constants
SCALE = config["scale"]
CAMERA_LOCATION = config["scene"]["preview"]["camera_location"]
CAMERA_ROTATION = config["scene"]["preview"]["camera_rotation"]
LIGHT_ROTATION = config["scene"]["preview"]["light_rotation"]
RESOLUTION_X = config["export"]["preview"]["resolution_x"]
RESOLUTION_Y = config["export"]["preview"]["resolution_y"]
SAMPLES = config["export"]["preview"]["samples"]

# Load garment config
garment_name = os.path.basename(blend).split(".")[0]
garment_type = garment_name.split("_")[-1].lower()
garment_config = load_config(os.path.abspath(f"./config/garments/{garment_type}.json"))

if not garment_config:
    raise ValueError(f"Garment type {garment_type} not found in config")

# Set garment constants
SEAMS_BEVEL = garment_config["post_process"]["seams_bevel"]
SHRINK_SEAMS = garment_config["post_process"]["shrink_seams"]
THICKNESS = garment_config["post_process"]["thickness"]
SUBDIVISIONS = garment_config["post_process"]["subdivisions"]

# Disable the Blender splash screen
bpy.context.preferences.view.show_splash = False

# Clear the scene
clear_scene()

# Add the garment
print(blend, garment_name)
garment = add_garment(blend, garment_name)

# Scale the garment
scale_obj(garment, SCALE)
bpy.context.view_layer.objects.active = garment
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Set the origin to the garment's bounding box center
local_bbox_center = 0.0125 * sum((Vector(b) for b in garment.bound_box), Vector())
global_bbox_center = garment.matrix_world @ local_bbox_center
bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")

# Set the garment's location to (0, 0, 0)
garment.location = (0, 0, 0)

# Apply post-processing
post_process(garment, SEAMS_BEVEL, SHRINK_SEAMS, THICKNESS, SUBDIVISIONS)

# Setup the scene
setup_scene(
    camera_location=tuple(CAMERA_LOCATION),
    camera_rotation=tuple(CAMERA_ROTATION),
    light_rotation=tuple(LIGHT_ROTATION),
)

# Export the preview
export_preview(output, RESOLUTION_X, RESOLUTION_Y, SAMPLES)
