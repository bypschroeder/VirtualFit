import os
import re
from minio.error import S3Error
from flask import current_app


def validate_gender(form):
    """Validates the provided gender in the given form..

    Args:
        form: The form containing the gender field.

    Returns:
        str: The validated gender, or None if the validation failed.
    """
    if "gender" not in form:
        return None
    gender = form["gender"]
    if gender not in ["male", "female"]:
        return None
    return gender


def validate_height(form):
    """Validates the provided height in the given form.

    Args:
        form: The form containing the height field.

    Returns:
        float: The validated height, or None if the validation failed.
    """
    if "height" not in form:
        return None
    height = float(form["height"])
    if height < 1.40 or height > 2.20:
        return None
    return height


def validate_image(files):
    """Validates the provided image in the given form files.

    Args:
        files: The form files containing the image field.

    Returns:
        file: The validated image file, or None if the validation failed.
    """
    if "image" not in files:
        return None
    image = files["image"]
    if image.filename == "":
        return None
    return image


def validate_obj(files, s3, bucket_name):
    """Validates the provided obj file in the given form files.

    Args:
        files: The form files containing the obj file.
        s3: The Minio client instance used to interact with the Minio object storage.
        bucket_name (string): The name of the Minio bucket where the obj file is stored.

    Returns:
        str: The key of the obj file in the Minio bucket, or None if the validation failed.
    """
    file_content = files["obj"]
    if not file_content:
        return None

    obj_content = file_content.read()
    try:
        objects = s3.list_objects(bucket_name, recursive=True)
        for obj in objects:
            if obj.object_name.endswith(".obj"):
                data = s3.get_object(bucket_name, obj.object_name)
                stored_content = data.read()

                if obj_content == stored_content:
                    return obj.object_name
    except S3Error as e:
        current_app.logger.error(f"Error occuredd while listing objects: {e}")
        return None
    return None


def validate_garment(form, s3, bucket_name):
    """Validates the provided garment in the given form.

    Args:
        form: The form containing the garment field.
        s3: The Minio client instance used to interact with the Minio object storage.
        bucket_name (string): The name of the Minio bucket where the garment blend file is stored.

    Returns:
        str: The name of the garment, or None if the validation failed.
    """
    if "garment" not in form:
        return None
    garment = form["garment"]

    available_garments = []
    try:
        objects = s3.list_objects(bucket_name, recursive=True)
        for obj in objects:
            if obj.object_name.endswith(".blend") and "previews" not in obj.object_name:
                folder_name = obj.object_name.split("/")[0]
                available_garments.append(folder_name)
    except S3Error as e:
        current_app.logger.error(f"Error occuredd while listing objects: {e}")
        return None

    if garment not in available_garments:
        return None

    return garment


def validate_size(form, s3, bucket_name, garment, gender):
    """Validates the provided size in the given form.

    Args:
        form: The form containing the size field.
        s3: The Minio client instance used to interact with the Minio object storage.
        bucket_name (string): The name of the Minio bucket where the garment blend file is stored.
        garment (string): The name of the garment.
        gender (string): The gender of the person. Must be 'male' or 'female'.

    Returns:
        str: The validated size, or None if the validation failed.
    """
    if "size" not in form:
        return None
    size = form["size"]

    available_sizes = []

    try:
        objects = s3.list_objects(bucket_name, recursive=True)
        for obj in objects:
            if (
                obj.object_name.endswith(".blend")
                and garment in obj.object_name
                and gender in obj.object_name
            ):
                file_name = os.path.basename(obj.object_name)
                file_size = file_name.split("_")[0]
                available_sizes.append(file_size)
    except S3Error as e:
        current_app.logger.error(f"Error occurred while listing objects: {e}")
        return None

    if size not in available_sizes:
        return None

    return size


def validate_quality(form):
    if "quality" not in form:
        return None
    quality = int(form["quality"])
    if quality < 1 or quality > 10:
        return None
    return quality


def validate_color(form):
    if "color" not in form:
        return None
    color = form["color"]
    if not color.startswith("#"):
        return None
    if len(color) not in (4, 7):
        return None
    hex_digits = color[1:]
    if not re.match(r"^[0-9a-fA-F]+$", hex_digits):
        return None
    return color
