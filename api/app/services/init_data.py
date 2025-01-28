import os
from minio.error import S3Error
from flask import current_app


def upload_data(s3_client, bucket_name, data_path, app):
    """Uploads all files from a given directory to a Minio bucket.

    Args:
        s3_client: A Minio client instance used to interact with the Minio object storage.
        bucket_name (str): The name of the Minio bucket where the files are uploaded to.
        data_path (str): The path to the directory containing the files to be uploaded.
    """
    for root, dirs, files in os.walk(data_path):
        for file in files:
            local_file_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_file_path, data_path)

            try:
                s3_client.stat_object(bucket_name, relative_path)
                app.logger.info(f"File '{relative_path}' already exists")
                continue
            except S3Error as e:
                if e.code == "NoSuchKey":
                    s3_client.fput_object(bucket_name, relative_path, local_file_path)
                    app.logger.info(f"Uploaded file '{relative_path}' to {bucket_name}")
                else:
                    app.logger.error(
                        f"Error: Failed to upload file '{relative_path}': {e}"
                    )

    app.logger.info(f"Uploaded all files from {data_path} to {bucket_name}")
