import docker
import os
from flask import current_app


def simulate_cloth(
    docker_client,
    obj_bucket_name,
    garment_bucket_name,
    obj_key,
    garment_key,
    gender,
    quality,
    color,
):
    """Simulates the cloth using a Blender Docker container.

    Args:
        docker_client: The Docker client instance used to interact with the Docker daemon.
        obj_bucket_name (string): The name of the Minio bucket where the obj file is stored.
        garment_bucket_name (string): The name of the Minio bucket where the garment blend file is stored.
        obj_key (string): The key of the obj file in the Minio bucket.
        garment_key (string): The key of the garment blend file in the Minio bucket.
        gender (string): The gender of the person for which the cloth is simulated. Must be 'male' or 'female'.
        quality (int): The quality of the cloth simulation. Must be between 1 and 10.
        color (string): The color of the garment. Must be a valid Hex color code.

    Returns:
        bool: True if the cloth simulation was successful, False otherwise.

    Notes:
        - The Docker container runs with GPU support, which requires a compatible environment.
        - The environment variables MINIO_ENDPOINT, MINIO_ACCESS_KEY, and MINIO_SECRET_KEY must be set.
        - The container has to connect to a configured network named 'virtualfit_app-network'.
        - The volume created by the blender container gets removed after the process is finished.
    """
    try:
        initial_volumes = set(docker_client.volumes.list())

        container = docker_client.containers.run(
            "blender:latest",
            device_requests=[
                docker.types.DeviceRequest(count=-1, capabilities=[["gpu"]])
            ],
            entrypoint="/bin/bash",
            command=(
                f"-c 'python3 ./minio_helpers/fetch_try_on.py {obj_bucket_name} {garment_bucket_name} {obj_key} {garment_key} {gender} {quality} \"{color}\"'"
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
