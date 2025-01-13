import os
from minio import Minio
from minio.error import S3Error
from minio.lifecycleconfig import LifecycleConfig, Rule, Filter, Expiration

BUCKETS_TO_CREATE = ["data", "clothes"]

s3 = Minio(
    endpoint=os.getenv("MINIO_ENDPOINT"),
    access_key=os.getenv("MINIO_ACCESS_KEY"),
    secret_key=os.getenv("MINIO_SECRET_KEY"),
    secure=False,
)


def set_lifecycle(bucket_name):
    try:
        rule = Rule(
            rule_id="delete-after-1-day",
            status="Enabled",
            expiration=Expiration(days=1),
            rule_filter=Filter(prefix=""),
        )
        lifecycle = LifecycleConfig(rules=[rule])
        s3.set_bucket_lifecycle(bucket_name, lifecycle)
        print(f"Lifecycle rule set for bucket '{bucket_name}'")
    except S3Error as e:
        print(f"Failed to set lifecycle rule for bucket '{bucket_name}': {e}")


def create_buckets():
    for bucket_name in BUCKETS_TO_CREATE:
        try:
            if not s3.bucket_exists(bucket_name):
                s3.make_bucket(bucket_name)
                print(f"Created bucket {bucket_name}")
                if not bucket_name != BUCKETS_TO_CREATE[1]:
                    set_lifecycle(bucket_name)
            else:
                print(f"Bucket {bucket_name} already exists")
        except S3Error as e:
            print(f"Failed to create bucket: {e}")
