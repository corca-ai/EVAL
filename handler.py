import os
import requests
import uuid
from typing import Callable, Dict
from enum import Enum

from PIL import Image

import pandas as pd

from utils import IMAGE_PROMPT, DATAFRAME_PROMPT


class FileType(Enum):
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DATAFRAME = "dataframe"
    UNKNOWN = "unknown"


class Handler:
    def __init__(self, handle_func: Dict[FileType, Callable]):
        self.handle_func = handle_func

    def handle(self, i: int, file_name: str) -> str:
        """
        Parse file type from file name (ex. image, audio, video, dataframe, etc.)
        """
        file_type = file_name.split("?")[0]

        if file_type.endswith(".png") or file_type.endswith(".jpg"):
            return self.handle_image(i, file_name)
        elif file_type.endswith(".mp3") or file_type.endswith(".wav"):
            return self.handle_audio(i, file_name)
        elif file_type.endswith(".mp4") or file_type.endswith(".avi"):
            return self.handle_video(i, file_name)
        elif file_type.endswith(".csv"):
            return self.handle_dataframe(i, file_name)
        else:
            return self.handle_unknown(i, file_name)

    def handle_image(self, i: int, remote_filename: str) -> str:
        img_data = requests.get(remote_filename).content
        local_filename = os.path.join("image", str(uuid.uuid4())[0:8] + ".png")
        with open(local_filename, "wb") as f:
            size = f.write(img_data)
        print(f"Inputs: {remote_filename} ({size//1000}MB)  => {local_filename}")
        img = Image.open(local_filename)
        width, height = img.size
        ratio = min(512 / width, 512 / height)
        width_new, height_new = (round(width * ratio), round(height * ratio))
        img = img.resize((width_new, height_new))
        img = img.convert("RGB")
        img.save(local_filename, "PNG")
        print(f"Resize image form {width}x{height} to {width_new}x{height_new}")
        try:
            description = self.handle_func[FileType.IMAGE](local_filename)
        except Exception as e:
            return "Error: " + str(e)

        return IMAGE_PROMPT.format(
            i=i, filename=local_filename, description=description
        )

    def handle_audio(self, i: int, remote_filename: str) -> str:
        return ""

    def handle_video(self, i: int, remote_filename: str) -> str:
        return ""

    def handle_dataframe(self, i: int, remote_filename: str) -> str:
        content = requests.get(remote_filename).content
        local_filename = os.path.join("dataframe/", str(uuid.uuid4())[0:8] + ".csv")
        with open(local_filename, "wb") as f:
            size = f.write(content)
        print(f"Inputs: {remote_filename} ({size//1000}MB)  => {local_filename}")
        df = pd.read_csv(local_filename)
        try:
            description = str(df.describe())
        except Exception as e:
            return "Error: " + str(e)

        return DATAFRAME_PROMPT.format(
            i=i, filename=local_filename, description=description
        )

    def handle_unknown(self, i: int, file: str) -> str:
        return ""
