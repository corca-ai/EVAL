import os
from typing import TypedDict

from dotenv import load_dotenv

load_dotenv()


class DotEnv(TypedDict):
    BOT_NAME: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str
    AWS_S3_BUCKET: str
    WINEDB_HOST: str
    WINEDB_PASSWORD: str
    OPENAI_API_KEY: str
    BING_SEARCH_URL: str
    BING_SUBSCRIPTION_KEY: str
    SERPAPI_API_KEY: str


settings: DotEnv = {
    "BOT_NAME": os.getenv("BOT_NAME", "Orca"),
    "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID"),
    "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY"),
    "AWS_REGION": os.getenv("AWS_REGION"),
    "AWS_S3_BUCKET": os.getenv("AWS_S3_BUCKET"),
    "WINEDB_HOST": os.getenv("WINEDB_HOST"),
    "WINEDB_PASSWORD": os.getenv("WINEDB_PASSWORD"),
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    "BING_SEARCH_URL": os.getenv("BING_SEARCH_URL"),
    "BING_SUBSCRIPTION_KEY": os.getenv("BING_SUBSCRIPTION_KEY"),
    "SERPAPI_API_KEY": os.getenv("SERPAPI_API_KEY"),
}
