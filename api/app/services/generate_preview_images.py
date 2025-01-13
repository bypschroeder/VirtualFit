import os
import docker
from flask import jsonify


def move_blend_to_volume(client, volume_name, volume_bind):
    try:
        container = client.containers.run(
            "blender",
            volumes={volume_name: {"bind": volume_bind, "mode": "rw"}},
            device_requests=[
                docker.types.DeviceRequest(count=-1, capabilities=[["gpu"]])
            ],
            command="bash -c 'mv /vf_blender/clothing/models/* /clothes/blend'",
            detach=True,
            environment={
                "MINIO_ENDPOINT": os.getenv("MINIO_ENDPOINT"),
                "MINIO_ACCESS_KEY": os.getenv("MINIO_ACCESS_KEY"),
                "MINIO_SECRET_KEY": os.getenv("MINIO_SECRET_KEY"),
            },
        )
        container.wait()

        volume_names = []
        container_info = client.api.inspect_container(container.id)
        for mount in container_info["Mounts"]:
            if mount["Type"] == "volume":
                volume_names.append(mount["Name"])

        container.remove(force=True)

        for volume_name in volume_names:
            if volume_name != "virtualfit_data":
                try:
                    client.volumes.get(volume_name).remove()
                    print(f"Volume {volume_name} removed.")
                except Exception as e:
                    print(f"Failed to remove volume {volume_name}: {e}")
            else:
                print(
                    f"Skipping removal of volume '{volume_name}' as it is 'virtualfit_data'."
                )

        return True
    except docker.errors.APIError as e:
        return jsonify({"error": f"Docker API error: {e}"}), 500


def get_missing_previews(blend_path, preview_path):
    blend_files = []
    for root, dirs, files in os.walk(blend_path):
        for file in files:
            if file.endswith(".blend") and file.startswith("L_"):
                blend_files.append(os.path.join(root, file))

    preview_files = []
    for root, dirs, files in os.walk(preview_path):
        for file in files:
            if file.endswith(".png"):
                preview_files.append(os.path.join(root, file))

    missing_previews = {}
    for blend_file in blend_files:
        relative_path = os.path.relpath(blend_file, blend_path)
        parts = relative_path.split(os.sep)

        if len(parts) >= 3:
            category, gender, _ = parts
        else:
            continue

        preview_path = os.path.join(preview_path, f"{category}/{gender}.png")
        if not os.path.exists(preview_path):
            missing_previews[blend_file] = preview_path

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
