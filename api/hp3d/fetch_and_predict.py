import os
import sys
import subprocess
import shutil
from minio import Minio
from minio.error import S3Error

if len(sys.argv) < 3:
    print(
        "Usage: python3 fetch_and_predict.py <bucket_name> <image_key> <gender> <height>"
    )
    sys.exit(1)

BUCKET_NAME = sys.argv[1]
IMAGE_KEY = sys.argv[2]
GENDER = sys.argv[3]
HEIGHT = sys.argv[4]

IMAGE_DIR = "/data/images"
SAVE_DIR = "/data/output"

client = Minio(
    endpoint=os.getenv("MINIO_ENDPOINT"),
    access_key=os.getenv("MINIO_ACCESS_KEY"),
    secret_key=os.getenv("MINIO_SECRET_KEY"),
    secure=False,
)

try:
    if not client.bucket_exists(BUCKET_NAME):
        print(f"Bucket {BUCKET_NAME} does not exist")
        sys.exit(1)
except S3Error as e:
    print("Failed to check bucket existence: {e}")
    sys.exit(1)

if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

if GENDER not in ["male", "female"]:
    print("Invalid gender")
    sys.exit(1)

print(f"Downloading image from {BUCKET_NAME}/{IMAGE_KEY}")
try:
    image_path = os.path.join(IMAGE_DIR, os.path.basename(IMAGE_KEY))
    client.fget_object(BUCKET_NAME, IMAGE_KEY, image_path)
    print(f"Downloaded image to {image_path}")
except S3Error as e:
    print(f"Failed to download image: {e}")
    sys.exit(1)

print(f"Running prediction on {image_path}")
try:
    subprocess.run(
        [
            "python3",
            "run_predict.py",
            "--gender",
            GENDER,
            "--pose_shape_weights",
            f"model_files/poseMF_shapeGaussian_net_weights_{GENDER}.tar",
            "--image_dir",
            IMAGE_DIR,
            "--save_dir",
            SAVE_DIR,
            "--height",
            HEIGHT,
            "--export_obj",
        ],
        check=True,
    )
    print("Prediction completed successfully and saved to {SAVE_DIR}")
except subprocess.CalledProcessError as e:
    print(f"Prediction failed: {e}")
    sys.exit(1)

output_path = os.path.join(
    SAVE_DIR,
    os.path.splitext(os.path.basename(IMAGE_KEY))[0] + ".obj",
)
upload_path = os.path.join(IMAGE_KEY.split("/")[0], "model.obj")
print(f"Uploading obj to {BUCKET_NAME}/{output_path}")
try:
    client.fput_object(BUCKET_NAME, upload_path, output_path)
    print(f"Uploaded obj to {BUCKET_NAME}/{upload_path}")
except S3Error as e:
    print(f"Failed to upload obj: {e}")
    sys.exit(1)

print(f"Cleaning up temporary files")
try:
    shutil.rmtree(IMAGE_DIR)
    shutil.rmtree(SAVE_DIR)
except Exception as e:
    print(f"Failed to clean up temporary files: {e}")
    sys.exit(1)

print("Done")
