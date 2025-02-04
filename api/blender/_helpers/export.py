import bpy


def export_3D(output_path, materials=False):
    """Exports the 3D model to the specified file format.

    Args:
        output_path (str): The path where the 3D model should be exported.
        materials (bool, optional): Whether to export the materials. Defaults to False.
    """
    bpy.ops.wm.obj_export(filepath=output_path, export_materials=materials)


def export_preview(output_path, resolution_x, resolution_y, samples):
    """Exports a preview image of the 3D model.

    Args:
        output_path (str): The path where the preview image should be exported.
    """
    bpy.context.scene.eevee.taa_render_samples = samples

    bpy.context.scene.render.resolution_x = resolution_x
    bpy.context.scene.render.resolution_y = resolution_y
    bpy.context.scene.render.film_transparent = True

    bpy.context.scene.render.filepath = output_path

    scene = bpy.context.scene
    camera = next((obj for obj in scene.objects if obj.type == "CAMERA"), None)
    bpy.context.scene.camera = camera

    bpy.ops.render.render(write_still=True)
    print(f"Rendered image to {output_path}")
