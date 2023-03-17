import os
import requests
import uuid
from typing import Callable
from enum import Enum

from PIL import Image

import pandas as pd

from utils import IMAGE_PROMPT, DATAFRAME_PROMPT
from tools import IMAGE_MODEL


class FileType(Enum):
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DATAFRAME = "dataframe"
    UNKNOWN = "unknown"


def handle(file_name: str) -> Callable:
    """
    Parse file type from file name (ex. image, audio, video, dataframe, etc.)
    """
    file_name = file_name.split("?")[0]

    if file_name.endswith(".png") or file_name.endswith(".jpg"):
        return handle_image
    elif file_name.endswith(".mp3") or file_name.endswith(".wav"):
        return handle_audio
    elif file_name.endswith(".mp4") or file_name.endswith(".avi"):
        return handle_video
    elif file_name.endswith(".csv"):
        return handle_dataframe
    else:
        return handle_unknown


def handle_image(i: int, file: str) -> str:
    img_data = requests.get(file).content
    filename = os.path.join("image", str(uuid.uuid4())[0:8] + ".png")
    with open(filename, "wb") as f:
        size = f.write(img_data)
    print(f"Inputs: {file} ({size//1000}MB)  => {filename}")
    img = Image.open(filename)
    width, height = img.size
    ratio = min(512 / width, 512 / height)
    width_new, height_new = (round(width * ratio), round(height * ratio))
    img = img.resize((width_new, height_new))
    img = img.convert("RGB")
    img.save(filename, "PNG")
    print(f"Resize image form {width}x{height} to {width_new}x{height_new}")
    try:
        description = IMAGE_MODEL.inference(filename)
    except Exception as e:
        return {"text": "image upload", "response": str(e), "additional": []}

    return IMAGE_PROMPT.format(i=i, filename=filename, description=description)


def handle_audio(i: int, file: str) -> str:
    return ""


def handle_video(i: int, file: str) -> str:
    return ""


def handle_dataframe(i: int, file: str) -> str:
    content = requests.get(file).content
    filename = os.path.join("dataframe/", str(uuid.uuid4())[0:8] + ".csv")
    with open(filename, "wb") as f:
        size = f.write(content)
    print(f"Inputs: {file} ({size//1000}MB)  => {filename}")
    df = pd.read_csv(filename)
    try:
        description = str(df.describe())
    except Exception as e:
        return {"text": "image upload", "response": str(e), "additional": []}

    return DATAFRAME_PROMPT.format(i=i, filename=filename, description=description)


def handle_unknown(i: int, file: str) -> str:
    return ""
