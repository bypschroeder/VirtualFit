import os
import docker
import docker.errors
import docker.types
from minio.error import S3Error
from flask import current_app


def generate_model(docker_client, s3_client, bucket_name, image_key, gender, height):
    """Generates a 3D model using the HP3D Docker container.

    Args:
        docker_client: A docker client instance used to interact with the Docker daemon.
        s3_client: A Minio client instance used to interact with the Minio object storage.
        bucket_name (str): The name of the Minio bucket where the image file is stored.
        image_key (str): The key of the image file in the Minio bucket.
        gender (str): The gender of the person for which the 3D model is generated. Must be 'male' or 'female'.
        height (float): The height of the person for which the 3D model is generated.

    Returns:
        bool: True if the 3D model generation was successful, False otherwise.

    Notes:
        - The Docker container runs with GPU support, which requires a compatible environment.
        - The environment variables MINIO_ENDPOINT, MINIO_ACCESS_KEY, and MINIO_SECRET_KEY must be set.
        - The container has to connect to a configured network named 'virtualfit_app-network'.
    """
    try:
        try:
            s3_client.stat_object(bucket_name, image_key)
        except S3Error as e:
            current_app.logger.error(
                f"Image file {image_key} no found in bucket {bucket_name}: {e}"
            )
            return False

        docker_client.containers.run(
            "hp3d:latest",
            device_requests=[
                docker.types.DeviceRequest(count=-1, capabilities=[["gpu"]])
            ],
            command=(
                f"python3 fetch_and_predict.py {bucket_name} {image_key} {gender} {height}"
            ),
            network="virtualfit_app-network",
            remove=True,
            environment={
                "MINIO_ENDPOINT": os.getenv("MINIO_ENDPOINT"),
                "MINIO_ACCESS_KEY": os.getenv("MINIO_ACCESS_KEY"),
                "MINIO_SECRET_KEY": os.getenv("MINIO_SECRET_KEY"),
            },
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


def shape_obj_smooth(docker_client, s3_client, bucket_name, obj_key):
    """Smoothens an OBJ file using the Blender Docker container

    Args:
        docker_client: A docker client instance used to interact with the Docker daemon.
        s3_client: A Minio client instance used to interact with the Minio object storage.
        bucket_name (str): The name of the Minio bucket where the OBJ file is stored.
        obj_key (str): The key of the OBJ file in the Minio bucket.

    Returns:
        bool: True if the smoothing was successful, False otherwise.

    Notes:
        - The Docker container runs with GPU support, which requires a compatible environment.
        - The environment variables MINIO_ENDPOINT, MINIO_ACCESS_KEY, and MINIO_SECRET_KEY must be set.
        - The container has to connect to a configured network named 'virtualfit_app-network'.
        - The volume created by the blender container gets removed after the process is finished.
    """
    try:
        try:
            s3_client.stat_object(bucket_name, obj_key)
        except S3Error as e:
            current_app.logger.error(
                f"OBJ file {obj_key} not found in bucket {bucket_name}: {e}"
            )
            return False

        initial_volumes = set(docker_client.volumes.list())

        container = docker_client.containers.run(
            "blender:latest",
            device_requests=[
                docker.types.DeviceRequest(count=-1, capabilities=[["gpu"]])
            ],
            entrypoint="/bin/bash",
            command=(
                f"-c 'python3 ./minio_helpers/fetch_shade_smooth.py {bucket_name} {obj_key}'"
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
        current_app.ogger.error("The specified Docker image 'blender' was not found.")
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
