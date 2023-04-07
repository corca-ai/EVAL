import os
import uuid
import shutil
from pathlib import Path
from enum import Enum
from pathlib import Path
from typing import Dict
import requests

from env import settings


class FileType(Enum):
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DATAFRAME = "dataframe"
    UNKNOWN = "unknown"

    @staticmethod
    def from_filename(url: str) -> "FileType":
        filename = url.split("?")[0]

        if filename.endswith(".png") or filename.endswith(".jpg"):
            return FileType.IMAGE
        elif filename.endswith(".mp3") or filename.endswith(".wav"):
            return FileType.AUDIO
        elif filename.endswith(".mp4") or filename.endswith(".avi"):
            return FileType.VIDEO
        elif filename.endswith(".csv"):
            return FileType.DATAFRAME
        else:
            return FileType.UNKNOWN

    @staticmethod
    def from_url(url: str) -> "FileType":
        return FileType.from_filename(url.split("?")[0])

    def to_extension(self) -> str:
        if self == FileType.IMAGE:
            return ".png"
        elif self == FileType.AUDIO:
            return ".mp3"
        elif self == FileType.VIDEO:
            return ".mp4"
        elif self == FileType.DATAFRAME:
            return ".csv"
        else:
            return ".unknown"


class BaseHandler:
    def handle(self, filename: str) -> str:
        raise NotImplementedError


class FileHandler:
    def __init__(self, handlers: Dict[FileType, BaseHandler], path: Path):
        self.handlers = handlers
        self.path = path

    def register(self, filetype: FileType, handler: BaseHandler) -> "FileHandler":
        self.handlers[filetype] = handler
        return self

    def download(self, url: str) -> str:
        filetype = FileType.from_url(url)
        data = requests.get(url).content
        local_filename = os.path.join(
            filetype.value, str(uuid.uuid4())[0:8] + filetype.to_extension()
        )
        os.makedirs(os.path.dirname(local_filename), exist_ok=True)
        with open(local_filename, "wb") as f:
            size = f.write(data)
        print(f"Inputs: {url} ({size//1000}MB)  => {local_filename}")
        return local_filename

    def handle(self, url: str) -> str:
        try:
            if url.startswith(settings["SERVER"]):
                local_filename = url[len(settings["SERVER"]) + 1 :]
                src = self.path / local_filename
                dst = self.path / settings["PLAYGROUND_DIR"] / local_filename
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy(src, dst)
            else:
                local_filename = self.download(url)
            return self.handlers[FileType.from_url(url)].handle(local_filename)
        except Exception as e:
            return "Error: " + str(e)
