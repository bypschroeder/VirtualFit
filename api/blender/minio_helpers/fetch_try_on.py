import os
import sys
import subprocess
import shutil
from minio import Minio
from minio.error import S3Error

if len(sys.argv) < 8:
    print(
        "Usage: python3 fetch_try_on.py <obj_bucket_name> <garment_bucket_name> <obj_key> <garment_key> <gender> <quality> <color>"
    )
    sys.exit(1)


print(sys.argv)
OBJ_BUCKET_NAME = sys.argv[1]
GARMENT_BUCKET_NAME = sys.argv[2]
OBJ_KEY = sys.argv[3]
GARMENT_KEY = sys.argv[4]
GENDER = sys.argv[5]
QUALITY = sys.argv[6]
COLOR = sys.argv[7]

DATA_DIR = "/data"

client = Minio(
    endpoint=os.getenv("MINIO_ENDPOINT"),
    access_key=os.getenv("MINIO_ACCESS_KEY"),
    secret_key=os.getenv("MINIO_SECRET_KEY"),
    secure=False,
)

try:
    if not client.bucket_exists(OBJ_BUCKET_NAME) or not client.bucket_exists(
        GARMENT_BUCKET_NAME
    ):
        print(f"Buckets {OBJ_BUCKET_NAME} or {GARMENT_BUCKET_NAME} does not exist")
        sys.exit(1)
except S3Error as e:
    print(f"Failed to check bucket existence: {e}")
    sys.exit(1)

if not os.path.exists(DATA_DIR):
    print(f"Directory {DATA_DIR} does not exist. Creating...")
    os.makedirs(DATA_DIR)

obj_filepath = os.path.join(DATA_DIR, os.path.basename(OBJ_KEY))

print(f"Downloading {OBJ_KEY} from {OBJ_BUCKET_NAME}...")
try:
    client.fget_object(OBJ_BUCKET_NAME, OBJ_KEY, obj_filepath)
    print(f"{OBJ_KEY} downloaded successfully to {DATA_DIR}")
except S3Error as e:
    print(f"Error: Failed to download {OBJ_KEY} from {OBJ_BUCKET_NAME}: {e}")
    sys.exit(1)

garment_filepath = os.path.join(DATA_DIR, os.path.basename(GARMENT_KEY))

print(f"Downloading {GARMENT_KEY} from {GARMENT_BUCKET_NAME}...")
try:
    client.fget_object(GARMENT_BUCKET_NAME, GARMENT_KEY, garment_filepath)
    print(f"{GARMENT_KEY} downloaded successfully to {DATA_DIR}")
except S3Error as e:
    print(f"Error: Failed to download {GARMENT_KEY} from {GARMENT_BUCKET_NAME}: {e}")
    sys.exit(1)

file_name = f"{os.path.splitext(os.path.basename(GARMENT_KEY))[0]}.obj"
output_path = os.path.join(DATA_DIR, file_name)

print("Running blender script...")
try:
    subprocess.run(
        [
            "blender",
            "-b",
            "-P",
            "fit_clothes.py",
            "--",
            "--gender",
            GENDER,
            "--obj",
            obj_filepath,
            "--garment",
            garment_filepath,
            "--quality",
            QUALITY,
            "--color",
            COLOR,
            "--output",
            output_path,
        ],
        check=True,
    )
    print(f"Fit {os.path.basename(GARMENT_KEY)} to {os.path.basename(OBJ_KEY)}")
except subprocess.CalledProcessError as e:
    print(f"Error: Failed to run blender script: {e}")
    sys.exit(1)

print(f"Uploading fitted glb to {OBJ_BUCKET_NAME}...")
upload_path_obj = os.path.join(OBJ_KEY.split("/")[0], file_name)
upload_path_mtl = os.path.join(OBJ_KEY.split("/")[0], file_name.replace(".obj", ".mtl"))
try:
    client.fput_object(OBJ_BUCKET_NAME, upload_path_obj, output_path)
    client.fput_object(
        OBJ_BUCKET_NAME, upload_path_mtl, output_path.replace(".obj", ".mtl")
    )
    print(f"File {output_path} uploaded successfully to {upload_path_obj}")
except S3Error as e:
    print(f"Error: Failed to upload {output_path} to {OBJ_BUCKET_NAME}: {e}")
    sys.exit(1)

print("Cleaning up...")
try:
    shutil.rmtree(DATA_DIR)
    print(f"Directory {DATA_DIR} removed")
except OSError as e:
    print(f"Error: Failed to remove directory {DATA_DIR}: {e}")
    sys.exit(1)

print("Fitting clothes completed successfully")
