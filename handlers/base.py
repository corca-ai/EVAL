import os
import requests
import uuid
from typing import Dict
from enum import Enum


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
    def __init__(self, handlers: Dict[FileType, BaseHandler]):
        self.handlers = handlers

    def register(self, filetype: FileType, handler: BaseHandler) -> "FileHandler":
        self.handlers[filetype] = handler
        return self

    def download(self, url: str) -> str:
        filetype = FileType.from_url(url)
        data = requests.get(url).content
        local_filename = os.path.join(
            filetype.value, str(uuid.uuid4())[0:8] + filetype.to_extension()
        )
        with open(local_filename, "wb") as f:
            size = f.write(data)
        print(f"Inputs: {url} ({size//1000}MB)  => {local_filename}")
        return local_filename

    def handle(self, url: str) -> str:
        try:
            return self.handlers[FileType.from_url(url)].handle(self.download(url))
        except Exception as e:
            return "Error: " + str(e)
