import os
import docker
import docker.errors
import docker.types


def generate_keypoints(client, data_folder, volume, volume_bind):
    try:
        if not os.path.exists(f"{data_folder}/images"):
            print("The 'images' folder does not exist.")
            return False

        client.containers.run(
            "openpose",
            device_requests=[
                docker.types.DeviceRequest(count=-1, capabilities=[["gpu"]])
            ],
            command=(
                f"/openpose/build/examples/openpose/openpose.bin "
                f"--image_dir {data_folder}/images "
                f"--write_json {data_folder}/keypoints "
                f"--face --hand --display 0 --render_pose 0"
            ),
            remove=True,
            volumes={volume: {"bind": volume_bind, "mode": "rw"}},
        )

        return True
    except docker.errors.ImageNotFound:
        print("The specified Docker image 'openpose' was not found.")
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


def generate_mesh(gender, client, data_folder, volume, volume_bind):
    try:
        if not os.path.exists(f"{data_folder}/keypoints"):
            print("The 'keypoints' folder does not exist.")
            return False

        client.containers.run(
            "smplify-x",
            device_requests=[
                docker.types.DeviceRequest(count=-1, capabilities=[["gpu"]])
            ],
            command=(
                f"python3 smplifyx/main.py "
                f"--config cfg_files/fit_smplx.yaml "
                f"--data_folder {data_folder} "
                f"--output_folder {data_folder}/smplify-x_results "
                f"--visualize=False "
                f"--gender={gender} "
                f"--model_folder ../smplx/models "
                f"--vposer_ckpt ../vposer/V02_05 "
                f"--part_segm_fn smplx_parts_segm.pkl"
            ),
            remove=True,
            volumes={volume: {"bind": volume_bind, "mode": "rw"}},
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


def shape_obj_smooth(obj_file_path, client, volume, volume_bind):
    try:
        if not os.path.exists(obj_file_path):
            return False

        client.containers.run(
            "blender",
            device_requests=[
                docker.types.DeviceRequest(count=-1, capabilities=[["gpu"]])
            ],
            command=(f"blender -b -P shade_smooth.py -- --obj {obj_file_path}"),
            remove=True,
            volumes={volume: {"bind": volume_bind, "mode": "rw"}},
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
