import docker
import os


def simulate_cloth(
    docker_client, obj_bucket_name, garment_bucket_name, obj_key, garment_key, gender
):
    try:
        container = docker_client.containers.run(
            "blender:latest",
            device_requests=[
                docker.types.DeviceRequest(count=-1, capabilities=[["gpu"]])
            ],
            command=(
                f"python3 ./minio_helpers/fetch_try_on.py {obj_bucket_name} {garment_bucket_name} {obj_key} {garment_key} {gender}"
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
