import os
import boto3

from env import settings


def upload(file_name: str):
    return upload_file(file_name, settings["AWS_S3_BUCKET"])


def upload_file(file_name, bucket, object_name=None):
    if object_name is None:
        object_name = os.path.basename(file_name)

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=settings["AWS_SECRET_ACCESS_KEY"],
    )
    s3_client.upload_file(file_name, bucket, object_name)

    return f"https://{bucket}.s3.{settings['AWS_REGION']}.amazonaws.com/{object_name}"
