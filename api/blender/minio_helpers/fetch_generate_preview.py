import os
import sys
import subprocess
import shutil
from minio import Minio
from minio.error import S3Error

if len(sys.argv) < 2:
    print("Usage: python3 fetch_generate_preview.py <bucket_name> <missing_previews>")
    sys.exit(1)

BUCKET_NAME = sys.argv[1]
MISSING_PREVIEWS = sys.argv[2]
missing_previews_paths = MISSING_PREVIEWS.split(",")

CLOTHES_DIR = "/data"

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

if not os.path.exists(CLOTHES_DIR):
    print(f"Directory {CLOTHES_DIR} does not exist. Creating...")
    os.makedirs(CLOTHES_DIR)

print(f"Downloading files from {BUCKET_NAME}...")
try:
    objects = client.list_objects(BUCKET_NAME, recursive=True)

    for obj in objects:
        object_name = obj.object_name
        if object_name in missing_previews_paths:
            local_file_path = os.path.join(CLOTHES_DIR, object_name)

            local_dir = os.path.dirname(local_file_path)
            if not os.path.exists(local_dir):
                os.makedirs(local_dir)

            client.fget_object(BUCKET_NAME, object_name, local_file_path)
            print(f"Downloaded {object_name} to {local_file_path}")
    print("Selected files downloaded successfully")
except S3Error as e:
    print(f"Error: Failed to download files: {e}")
    sys.exit(1)

print("Running blender scripts...")
for root, dirs, files in os.walk(CLOTHES_DIR):
    for file in files:
        if file.endswith(".blend"):
            blend_file_path = os.path.join(root, file)

            output_root_dir = os.path.join(root, "/previews")
            os.makedirs(output_root_dir, exist_ok=True)

            relative_path = os.path.relpath(blend_file_path, CLOTHES_DIR)
            clothing = relative_path.split("/")[0]
            gender = relative_path.split("/")[1]
            output_file_path = f"{output_root_dir}/{clothing}/{gender}.png"

            try:
                subprocess.run(
                    [
                        "blender",
                        "-b",
                        "-P",
                        "generate_preview.py",
                        "--",
                        "--blend",
                        blend_file_path,
                        "--output",
                        output_file_path,
                    ],
                    check=True,
                )
                print(
                    f"Generated preview for {blend_file_path} saved to {output_file_path}"
                )
            except subprocess.CalledProcessError as e:
                print("Error: Failed to run blender script: {e}")
                sys.exit(1)

            print(f"Uploading {output_file_path} to {BUCKET_NAME}")
            upload_path = f"previews/{clothing}/{gender}.png"
            try:
                client.fput_object(BUCKET_NAME, upload_path, output_file_path)
                print(f"File {output_file_path} uploaded successfully to {upload_path}")
            except S3Error as e:
                print(
                    f"Error: Failed to upload {output_file_path} to {BUCKET_NAME}: {e}"
                )
                sys.exit(1)

print("Cleaning up...")
try:
    shutil.rmtree(CLOTHES_DIR)
    print(f"Directory {CLOTHES_DIR} removed")
except OSError as e:
    print(f"Error: Failed to remove directory {CLOTHES_DIR}: {e}")
    sys.exit(1)

print("Generating Previews completed successfully")
