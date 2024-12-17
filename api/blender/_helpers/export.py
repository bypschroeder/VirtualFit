import bpy

def export_img(filepath, file_format, export_type, transparent_bg=False):
    scene = bpy.context.scene
    camera = next((obj for obj in scene.objects if obj.type == "CAMERA"), None)

    bpy.context.scene.camera = camera
    bpy.context.scene.render.filepath = filepath

    bpy.context.scene.render.filepath = filepath
    bpy.context.scene.render.image_settings.file_format = file_format
    bpy.context.scene.render.image_settings.color_mode = "RGBA"

    bpy.context.scene.render.resolution_x = 1080
    bpy.context.scene.render.resolution_y = 1080

    if transparent_bg:
        bpy.context.scene.render.film_transparent = True
    
    for obj in bpy.data.objects:
        if obj.type != "LIGHT" and obj.type != "CAMERA":
            obj.hide_render = True
        else:
            obj.hide_render = False

    if export_type == "FULL":
        for obj in bpy.data.objects:
            obj.hide_render = False 
    elif export_type == "GARMENT":
        for obj in bpy.data.objects:
            if obj.type == "MESH" and not obj.name.startswith("SMPLX"):
                obj.hide_render = False
    elif export_type == "AVATAR":
        for obj in bpy.data.objects:
            if obj.name.startswith("SMPLX"):
                obj.hide_render = False
    else:
        raise ValueError(f"Invalid export type: {export_type}")

    bpy.ops.render.render(write_still=True)
    print(f"Rendered image to {filepath}")

def export_3D(filepath, file_format, export_type):
    bpy.ops.object.select_all(action="DESELECT")

    if export_type == "FULL":
        for obj in bpy.data.objects:
            obj.select_set(True)
    elif export_type == "GARMENT":
        for obj in bpy.data.objects:
            if obj.type == "MESH" and not obj.name.startswith("SMPLX"):
                obj.select_set(True)
    elif export_type == "AVATAR":
        for obj in bpy.data.objects:
            if obj.name.startswith("SMPLX"):
                obj.select_set(True)
    else:
        raise ValueError(f"Invalid export type: {export_type}")

    if file_format == "OBJ":
        bpy.ops.wm.obj_export(export_selected_objects=True, filepath=filepath, export_materials=False)
    elif file_format == "USD":
        bpy.ops.wm.usd_export(selected_objects_only=True, filepath=filepath, export_materials=False)
    else:
        raise ValueError(f"Invalid file format: {file_format}")