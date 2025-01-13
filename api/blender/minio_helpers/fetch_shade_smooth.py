import os
import sys
import subprocess
import shutil
from minio import Minio
from minio.error import S3Error

if len(sys.argv) < 2:
    print("Usage: python3 ./smooth_obj/download_and_execute,py <bucket_name> <obj_key>")
    sys.exit(1)

BUCKET_NAME = sys.argv[1]
OBJ_KEY = sys.argv[2]

OBJ_DIR = "/data"

# client = Minio(
#     endpoint=os.getenv("MINIO_ENDPOINT"),
#     access_key=os.getenv("MINIO_ACCESS_KEY"),
#     secret_key=os.getenv("MINIO_SECRET_KEY"),
#     secure=False,
# )

client = Minio(
    endpoint="minio:9000",
    access_key="admin",
    secret_key="password",
    secure=False,
)

try:
    if not client.bucket_exists(BUCKET_NAME):
        print(f"Bucket {BUCKET_NAME} does not exist")
        sys.exit(1)
except S3Error as e:
    print(f"Failed to check bucket existence: {e}")
    sys.exit(1)

if not os.path.exists(OBJ_DIR):
    print(f"Directory {OBJ_DIR} does not exist. Creating...")
    os.makedirs(OBJ_DIR)

obj_filepath = os.path.join(OBJ_DIR, os.path.basename(OBJ_KEY))

print(f"Downloading {OBJ_KEY} from {BUCKET_NAME}...")
try:
    client.fget_object(BUCKET_NAME, OBJ_KEY, obj_filepath)
    print(f"{OBJ_KEY} downloaded successfully to {OBJ_DIR}")
except S3Error as e:
    print(f"Error: Failed to download {OBJ_KEY} from {BUCKET_NAME}: {e}")
    sys.exit(1)

print(f"Running blender script...")
try:
    subprocess.run(
        [
            "blender",
            "-b",
            "-P",
            "shade_smooth.py",
            "--",
            "--obj",
            obj_filepath,
        ],
        check=True,
    )
    print(f"Smooth object saved to {OBJ_DIR}")
except subprocess.CalledProcessError as e:
    print(f"Error: Failed to run blender script: {e}")
    sys.exit(1)

print(f"Uploading smooth object to {BUCKET_NAME}")
upload_path = f"{os.path.splitext(OBJ_KEY)[0]}_smooth.obj"
smooth_obj_path = obj_filepath.replace(".obj", "_smooth.obj")
try:
    client.fput_object(BUCKET_NAME, upload_path, smooth_obj_path)
    print(f"File {smooth_obj_path} uploaded successfully to {upload_path}")
except S3Error as e:
    print(f"Error: Failed to upload {smooth_obj_path} to {BUCKET_NAME}: {str(e)}")
    sys.exit(1)

print("Cleaning up...")
try:
    shutil.rmtree(OBJ_DIR)
    print(f"Directory {OBJ_DIR} removed")
except OSError as e:
    print(f"Error: Failed to remove directory {OBJ_DIR}: {e}")
    sys.exit(1)

print("Smoothing obj completed successfully")
