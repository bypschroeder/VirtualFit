import os
from minio.error import S3Error


def upload_data(s3_client, bucket_name, data_path):
    for root, dirs, files in os.walk(data_path):
        for file in files:
            local_file_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_file_path, data_path)

            try:
                s3_client.stat_object(bucket_name, relative_path)
                print(f"File '{relative_path}' already exists")
                continue
            except S3Error as e:
                if e.code == "NoSuchKey":
                    s3_client.fput_object(bucket_name, relative_path, local_file_path)
                    print(f"Uploaded file '{relative_path}' to {bucket_name}")
                else:
                    print(f"Error: Failed to upload file '{relative_path}': {e}")
                    return False

    print(f"Uploaded all files from {data_path} to {bucket_name}")
