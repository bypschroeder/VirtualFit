from minio.error import S3Error
import os


def validate_gender(form):
    if "gender" not in form:
        return None
    gender = form["gender"]
    if gender not in ["male", "female"]:
        return None
    return gender


def validate_image(files):
    if "image" not in files:
        return None
    image = files["image"]
    if image.filename == "":
        return None
    return image


def validate_obj(files, s3, bucket_name):
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
        print(f"Error occuredd while listing objects: {e}")
        return None
    return None


def validate_garment(form, s3, bucket_name):
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
        print(f"Error occuredd while listing objects: {e}")
        return None

    if garment not in available_garments:
        return None

    return garment


def validate_size(form, s3, bucket_name, garment, gender):
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
        print(f"Error occurred while listing objects: {e}")
        return None

    if size not in available_sizes:
        return None

    return size
