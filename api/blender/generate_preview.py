import bpy
import os
import sys
from mathutils import Vector
import bmesh


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

script_dir = os.path.dirname(os.path.abspath(__file__))
add_subdirs_to_sys_path(script_dir)

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
    thickness = -0.01
elif "Sweatshirt" in mesh_name:
    thickness = -0.03
elif "Hoodie" in mesh_name:
    thickness = -0.05
else:
    thickness = -0.001

post_process(obj, thickness, levels=2)

setup_scene(
    camera_location=(0, -21, 0),
    camera_rotation=(90, 0, 0),
    light_rotation=(90, 0, 0),
)

export_preview(output)
