import os
import sys
import subprocess
import shutil
from minio import Minio
from minio.error import S3Error

if len(sys.argv) < 4:
    print(
        "Usage: python3 generate_mesh.py <bucket_name> <image_key> <keypoints_key> <gender>"
    )
    sys.exit(1)

BUCKET_NAME = sys.argv[1]
IMAGE_KEY = sys.argv[2]
KEYPOINTS_KEY = sys.argv[3]
GENDER = sys.argv[4]

MINIO_ENDPOINT = "minio:9000"
ACCESS_KEY = "admin"
SECRET_KEY = "password"
DATA_FOLDER = "/data"
OUTPUT_FOLDER = "/data/output"

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

if not os.path.exists(f"{DATA_FOLDER}/images"):
    print(f"Directory {DATA_FOLDER}/images does not exist. Creating...")
    os.makedirs(f"{DATA_FOLDER}/images")

if not os.path.exists(f"{DATA_FOLDER}/keypoints"):
    print(f"Directory {DATA_FOLDER}/keypoints does not exist. Creating...")
    os.makedirs(f"{DATA_FOLDER}/keypoints")

print(f"Downloading {IMAGE_KEY} and {KEYPOINTS_KEY} from {BUCKET_NAME}...")
try:
    client.fget_object(
        BUCKET_NAME,
        IMAGE_KEY,
        os.path.join(f"{DATA_FOLDER}/images", os.path.basename(IMAGE_KEY)),
    )
    client.fget_object(
        BUCKET_NAME,
        KEYPOINTS_KEY,
        os.path.join(f"{DATA_FOLDER}/keypoints", os.path.basename(KEYPOINTS_KEY)),
    )
    print(f"Files downloaded successfully to {DATA_FOLDER}")
except S3Error as e:
    print(
        f"Error: Failed to download {IMAGE_KEY} or {KEYPOINTS_KEY} from {BUCKET_NAME}: {e}"
    )
    sys.exit(1)

print("Running SMPLify-X...")
try:
    subprocess.run(
        [
            "python3",
            "smplifyx/main.py",
            "--config",
            "cfg_files/fit_smplx.yaml",
            "--data_folder",
            DATA_FOLDER,
            "--output_folder",
            OUTPUT_FOLDER,
            "--visualize",
            "False",
            "--gender",
            GENDER,
            "--model_folder",
            "../smplx/models",
            "--vposer_ckpt",
            "../vposer/V02_05",
            "--part_segm_fn",
            "smplx_parts_segm.pkl",
        ],
        check=True,
    )
    print(f"SMPLify-X results saved to {OUTPUT_FOLDER}")
except subprocess.CalledProcessError as e:
    print(f"Error: Failed to run SMPLify-X: {e}")
    sys.exit(1)

print(f"Uploading SMPLify-X output to {BUCKET_NAME}...")
for root, dirs, files in os.walk(OUTPUT_FOLDER):
    for file in files:
        if file.endswith(".pkl") or file.endswith(".obj"):
            base_name = os.path.splitext(os.path.basename(IMAGE_KEY))[0]
            new_name = f"{base_name}.{os.path.splitext(file)[1][1:]}"
            upload_path = os.path.join(os.path.basename(OUTPUT_FOLDER), new_name)
            filepath = os.path.join(root, file)
            try:
                print(f"Uploading {filepath} to {BUCKET_NAME}...")
                client.fput_object(BUCKET_NAME, upload_path, filepath)
                print(f"File {filepath} uploaded successfully to {upload_path}")
            except S3Error as e:
                print(f"Error: Failed to upload {filepath} to {BUCKET_NAME}: {e}")
                sys.exit(1)

print("Cleaning up...")
try:
    shutil.rmtree(DATA_FOLDER)
    print(f"Directory {DATA_FOLDER} removed")
except OSError as e:
    print(f"Error: Failed to remove directory {DATA_FOLDER}")
    sys.exit(1)

print("Mesh generation completed successfully")
