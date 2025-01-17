import os
import docker
from datetime import timedelta
from services.s3 import s3, BUCKETS_TO_CREATE


def get_files_by_gender(gender):
    objects = list(s3.list_objects(BUCKETS_TO_CREATE[1], recursive=True))
    blend_files = [
        obj.object_name
        for obj in objects
        if obj.object_name.endswith(".blend")
        and os.path.basename(obj.object_name).startswith("L_")
        and obj.object_name.split("/")[1] == gender
    ]
    preview_files = [
        obj.object_name
        for obj in objects
        if obj.object_name.startswith("previews")
        and obj.object_name.endswith(".png")
        and os.path.basename(obj.object_name) == f"{gender}.png"
    ]
    return blend_files, preview_files


def find_missing_previews(blend_files, preview_files):
    missing_previews = []
    for blend_file in blend_files:
        clothing = blend_file.split("/")[0]
        gender = blend_file.split("/")[1]
        preview_file = f"previews/{clothing}/{gender}.png"
        if preview_file not in preview_files:
            missing_previews.append(blend_file)
    return missing_previews


def generate_preview_imgs(docker_client, bucket_name, missing_previews):
    try:
        missing_previews_string = ",".join(missing_previews)

        container = docker_client.containers.run(
            "blender:latest",
            device_requests=[
                docker.types.DeviceRequest(count=-1, capabilities=[["gpu"]])
            ],
            command=(
                f"python3 ./minio_helpers/fetch_generate_preview.py {bucket_name} {missing_previews_string}"
            ),
            network="virtualfit_app-network",
            detach=True,
            environment={
                "MINIO_ENDPOINT": os.getenv("MINIO_ENDPOINT"),
                "MINIO_ACCESS_KEY": os.getenv("MINIO_ACCESS_KEY"),
                "MINIO_SECRET_KEY": os.getenv("MINIO_SECRET_KEY"),
            },
        )

        container.wait()

        volume_names = []
        container_info = docker_client.api.inspect_container(container.id)
        for mount in container_info["Mounts"]:
            if mount["Type"] == "volume":
                volume_names.append(mount["Name"])

        container.remove(force=True)

        for volume_name in volume_names:
            if volume_name != "virtualfit_minio-data":
                try:
                    docker_client.volumes.get(volume_name).remove()
                    print(f"Removed volume {volume_name}")
                except Exception as e:
                    print(f"Failed to remove volume {volume_name}: {e}")
            else:
                print(
                    f"Skipping removal of volume {volume_name} (it's the virtualfit_data volume)"
                )
        return True
    except docker.errors.ImageNotFound:
        print("The specified Docker image 'smplify-x' was not found.")
        return False
    except docker.errors.NotFound as e:
        print(f"Resource not found: {e}")
        return False
    except docker.errors.APIError as e:
        print(f"Docker API error: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False


def generate_presigned_urls(file_paths):
    expiration_time = timedelta(minutes=10)
    presigned_urls = [
        s3.presigned_get_object(BUCKETS_TO_CREATE[1], file_path, expiration_time)
        for file_path in file_paths
    ]
    external_url_base = "http://minio.localhost"
    return [
        url.replace("http://minio:9000", external_url_base) for url in presigned_urls
    ]
