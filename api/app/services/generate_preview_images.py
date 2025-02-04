import os
import docker
from datetime import timedelta
from services.s3 import s3
from flask import current_app


def get_files_by_gender(bucket_name, gender, garment_size):
    """Retrieves all blend files and preview files for a given gender.

    Args:
        gender (str): The gender for which the files are retrieved. Must be 'male' or 'female'.

    Returns:
        tuple: A tuple containing two lists:
            - blend_files (list): Paths to the retrieved blend files.
            - preview_files (list): Paths to the retrieved preview files.

    Notes:
        - Only gets the L-sized garment for the given gender since the previews are only generated for L-sized garments.
    """
    objects = list(s3.list_objects(bucket_name, recursive=True))
    blend_files = [
        obj.object_name
        for obj in objects
        if obj.object_name.endswith(".blend")
        and os.path.basename(obj.object_name).startswith(f"{garment_size}_")
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
    """Finds the blend files without corresponding preview images.

    Args:
        blend_files (list): A list of blend file paths.
        preview_files (list): A list of preview file paths.

    Returns:
        list: A list of blend file paths that do not have a corresponding preview image.
    """
    missing_previews = []
    for blend_file in blend_files:
        clothing = blend_file.split("/")[0]
        gender = blend_file.split("/")[1]
        preview_file = f"previews/{clothing}/{gender}.png"
        if preview_file not in preview_files:
            missing_previews.append(blend_file)
    return missing_previews


def generate_preview_imgs(docker_client, bucket_name, missing_previews):
    """Generates preview images for missing blend files using a Blender Docker container.

    Args:
        docker_client: A docker client instance used to interact with the Docker daemon.
        bucket_name (str): The name of the Minio bucket where the blend files are stored.
        missing_previews (list): A list of blend file paths that do not have a corresponding preview image.

    Returns:
        bool: True if the preview images were generated successfully, False otherwise.

    Notes:
        - The Docker container runs with GPU support, which requires a compatible environment.
        - The environment variables MINIO_ENDPOINT, MINIO_ACCESS_KEY, and MINIO_SECRET_KEY must be set.
        - The container has to connect to a configured network named 'virtualfit_app-network'.
        - The volume created by the blender container gets removed after the process is finished.
    """
    try:
        missing_previews_string = ",".join(missing_previews)

        initial_volumes = set(docker_client.volumes.list())

        container = docker_client.containers.run(
            "blender:latest",
            device_requests=[
                docker.types.DeviceRequest(count=-1, capabilities=[["gpu"]])
            ],
            entrypoint="/bin/bash",  # Overriding entrypoint since env doesn't get set without
            command=(
                f"-c 'python3 ./minio_helpers/fetch_generate_preview.py {bucket_name} {missing_previews_string}'"
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

        post_volumes = set(docker_client.volumes.list())
        new_volumes = post_volumes - initial_volumes

        container.remove(force=True)

        for volume in new_volumes:
            volume_name = volume.name
            if volume_name != "virtualfit_minio-data":
                try:
                    volume.remove()
                    current_app.logger.info(f"Volume {volume_name} removed.")
                except Exception as e:
                    current_app.logger.error(
                        f"Failed to remove volume {volume_name}: {e}"
                    )
            else:
                current_app.logger.info(
                    f"Skipping removal of volume '{volume_name}' as it is 'virtualfit_data'."
                )

        return True
    except docker.errors.ImageNotFound:
        current_app.logger.error(
            "The specified Docker image 'smplify-x' was not found."
        )
        return False
    except docker.errors.NotFound as e:
        current_app.logger.error(f"Resource not found: {e}")
        return False
    except docker.errors.APIError as e:
        current_app.logger.error(f"Docker API error: {e}")
        return False
    except Exception as e:
        current_app.logger.error(f"An unexpected error occurred: {e}")
        return False


def generate_presigned_urls(bucket_name, file_paths):
    """Generates presigned URLs for the given file paths.

    Args:
        file_paths (list): A list of file paths to generate presigned URLs for.

    Returns:
        list: A list of presigned URLs for the given file paths.

    Notes:
        - The presigned base domain is replaced to 'http://minio.localhost' according to the nginx reverse proxy.
    """
    expiration_time = timedelta(minutes=10)
    presigned_urls = [
        s3.presigned_get_object(bucket_name, file_path, expiration_time)
        for file_path in file_paths
    ]
    external_url_base = "http://minio.localhost"
    return [
        url.replace(f"http://{os.getenv('MINIO_ENDPOINT')}", external_url_base)
        for url in presigned_urls
    ]
