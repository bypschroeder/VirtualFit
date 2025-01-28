import os
from minio import Minio
from minio.error import S3Error
from minio.lifecycleconfig import LifecycleConfig, Rule, Filter, Expiration
from flask import current_app

s3 = Minio(
    endpoint=os.getenv("MINIO_ENDPOINT"),
    access_key=os.getenv("MINIO_ACCESS_KEY"),
    secret_key=os.getenv("MINIO_SECRET_KEY"),
    secure=False,
)


def set_lifecycle(bucket_name, app):
    """Sets a lifecycle rule for a given bucket to delete its contents after 1 day.

    Args:
        bucket_name (str): The name of the bucket to set the lifecycle rule for.
    """
    try:
        rule = Rule(
            rule_id="delete-after-1-day",
            status="Enabled",
            expiration=Expiration(days=1),
            rule_filter=Filter(prefix=""),
        )
        lifecycle = LifecycleConfig(rules=[rule])
        s3.set_bucket_lifecycle(bucket_name, lifecycle)
        app.logger.info(f"Lifecycle rule set for bucket '{bucket_name}'")
    except S3Error as e:
        app.logger.error(
            f"Failed to set lifecycle rule for bucket '{bucket_name}': {e}"
        )


def create_buckets(buckets, app):
    """Creates the specified buckets if they don't exist.

    Args:
        buckets (list): A list of bucket names to create.
    """
    for bucket_name in buckets:
        try:
            if not s3.bucket_exists(bucket_name):
                s3.make_bucket(bucket_name)
                app.logger.info(f"Created bucket {bucket_name}")
                if not bucket_name != app.config["BUCKETS"][1]:
                    set_lifecycle(bucket_name, app)
            else:
                app.logger.info(f"Bucket {bucket_name} already exists")
        except S3Error as e:
            app.logger.error(f"Failed to create bucket: {e}")
