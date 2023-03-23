import os
import shutil

from env import DotEnv
from .base import AbstractUploader


class StaticUploader(AbstractUploader):
    STATIC_DIR = "static"

    def __init__(self, server: str):
        self.server = server

    @staticmethod
    def from_settings(settings: DotEnv) -> "StaticUploader":
        return StaticUploader(settings["SERVER"])

    def get_url(self, uploaded_path: str) -> str:
        return f"{self.server}/{uploaded_path}"

    def upload(self, filepath: str):
        upload_path = os.path.join(StaticUploader.STATIC_DIR, filepath)
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
        shutil.copy(filepath, upload_path)
        return f"{self.server}/{upload_path}"
