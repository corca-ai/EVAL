import os

import boto3

from env import DotEnv

from .base import AbstractUploader


class S3Uploader(AbstractUploader):
    def __init__(self, accessKey: str, secretKey: str, region: str, bucket: str):
        self.accessKey = accessKey
        self.secretKey = secretKey
        self.region = region
        self.bucket = bucket
        self.client = boto3.client(
            "s3",
            aws_access_key_id=self.accessKey,
            aws_secret_access_key=self.secretKey,
        )

    @staticmethod
    def from_settings(settings: DotEnv) -> "S3Uploader":
        return S3Uploader(
            settings["AWS_ACCESS_KEY_ID"],
            settings["AWS_SECRET_ACCESS_KEY"],
            settings["AWS_REGION"],
            settings["AWS_S3_BUCKET"],
        )

    def get_url(self, object_name: str) -> str:
        return f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{object_name}"

    def upload(self, filepath: str) -> str:
        object_name = os.path.basename(filepath)
        self.client.upload_file(filepath, self.bucket, object_name)
        return self.get_url(object_name)
