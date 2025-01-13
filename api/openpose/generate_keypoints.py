import os
import sys
import subprocess
import shutil
from minio import Minio
from minio.error import S3Error

if len(sys.argv) < 2:
    print("Usage: python3 generate_keypoints.py <bucket_name> <image_key>")
    sys.exit(1)

BUCKET_NAME = sys.argv[1]
IMAGE_KEY = sys.argv[2]

IMAGE_DIR = "/data/images"
WRITE_JSON = "/data/keypoints"

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

if not os.path.exists(IMAGE_DIR):
    print(f"Directory {IMAGE_DIR} does not exist. Creating...")
    os.makedirs(IMAGE_DIR)

if not os.path.exists(WRITE_JSON):
    print(f"File {WRITE_JSON} does not exist. Creating...")
    os.makedirs(WRITE_JSON)

print(f"Downloading {IMAGE_KEY} from {BUCKET_NAME}...")
try:
    client.fget_object(
        BUCKET_NAME, IMAGE_KEY, os.path.join(IMAGE_DIR, os.path.basename(IMAGE_KEY))
    )
    print(f"File downloaded successfully to {IMAGE_DIR}")
except S3Error as e:
    print(f"Error: Failed to download {IMAGE_KEY} from {BUCKET_NAME}: {e}")
    sys.exit(1)

print("Running Openpose...")
try:
    subprocess.run(
        [
            "/openpose/build/examples/openpose/openpose.bin",
            "--image_dir",
            IMAGE_DIR,
            "--write_json",
            WRITE_JSON,
            "--face",
            "--hand",
            "--display",
            "0",
            "--render_pose",
            "0",
        ],
        check=True,
    )
    print(f"Openpose results saved to {WRITE_JSON}")
except subprocess.CalledProcessError as e:
    print(f"Error: Failed to run Openpose: {e}")
    sys.exit(1)

print(f"Uploading JSON result to {BUCKET_NAME}")
for json_file in os.listdir(WRITE_JSON):
    if json_file.endswith(".json"):
        json_path = os.path.join(WRITE_JSON, json_file)
        upload_path = os.path.join(os.path.basename(WRITE_JSON), json_file)
        try:
            client.fput_object(BUCKET_NAME, upload_path, json_path)
            print(f"File {json_file} uploaded successfully to {BUCKET_NAME}")
        except S3Error as e:
            print(f"Error: Failed to upload file {json_file}: {e}")
            sys.exit(1)

print("Cleaning up...")
try:
    shutil.rmtree(IMAGE_DIR)
    shutil.rmtree(WRITE_JSON)
    print(f"Directory {IMAGE_DIR} and {WRITE_JSON} removed")
except OSError as e:
    print(f"Error: Failed to remove directories: {e}")
    sys.exit(1)

print("Keypoints generation completed successfully")
