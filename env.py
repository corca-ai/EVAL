import os
from dotenv import load_dotenv
from typing import TypedDict

load_dotenv()


class DotEnv(TypedDict):
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str
    AWS_S3_BUCKET: str
    WINEDB_HOST: str
    WINEDB_PASSWORD: str


settings: DotEnv = {
    "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID"),
    "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY"),
    "AWS_REGION": os.getenv("AWS_REGION"),
    "AWS_S3_BUCKET": os.getenv("AWS_S3_BUCKET"),
    "WINEDB_HOST": os.getenv("WINEDB_HOST"),
    "WINEDB_PASSWORD": os.getenv("WINEDB_PASSWORD"),
}
