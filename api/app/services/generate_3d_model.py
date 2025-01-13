import os
import docker
import docker.errors
import docker.types
from minio.error import S3Error
from urllib.parse import unquote


def generate_keypoints(docker_client, s3_client, bucket_name, image_key):
    try:
        try:
            s3_client.stat_object(bucket_name, image_key)
        except S3Error as e:
            print(f"Image file {image_key} no found in bucket {bucket_name}: {e}")
            return False

        docker_client.containers.run(
            "openpose:latest",
            device_requests=[
                docker.types.DeviceRequest(count=-1, capabilities=[["gpu"]])
            ],
            command=(f"python3 generate_keypoints.py {bucket_name} {image_key}"),
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


def generate_mesh(
    docker_client, s3_client, bucket_name, image_key, keypoints_key, gender
):
    try:
        try:
            s3_client.stat_object(bucket_name, keypoints_key)
            s3_client.stat_object(bucket_name, image_key)
        except S3Error as e:
            print(
                f"Keypoints file {keypoints_key} or image file {image_key} not found in bucket {bucket_name}: {e}"
            )
            return False

        docker_client.containers.run(
            "smplify-x:latest",
            device_requests=[
                docker.types.DeviceRequest(count=-1, capabilities=[["gpu"]])
            ],
            command=(
                f"python3 generate_mesh.py {bucket_name} {image_key} {keypoints_key} {gender}"
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


def shape_obj_smooth(docker_client, s3_client, bucket_name, obj_key):
    try:
        try:
            s3_client.stat_object(bucket_name, obj_key)
        except S3Error as e:
            print(f"OBJ file {obj_key} not found in bucket {bucket_name}: {e}")
            return False

        container = docker_client.containers.run(
            "blender:latest",
            device_requests=[
                docker.types.DeviceRequest(count=-1, capabilities=[["gpu"]])
            ],
            command=(
                f"python3 ./minio_helpers/fetch_shade_smooth.py {bucket_name} {obj_key}"
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
                    print(f"Volume {volume_name} removed.")
                except Exception as e:
                    print(f"Failed to remove volume {volume_name}: {e}")
            else:
                print(
                    f"Skipping removal of volume '{volume_name}' as it is 'virtualfit_data'."
                )

        return True
    except docker.errors.ImageNotFound:
        print("The specified Docker image 'blender' was not found.")
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
