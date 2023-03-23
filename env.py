import os
from typing import TypedDict

from dotenv import load_dotenv

load_dotenv()


class DotEnv(TypedDict):
    PORT: int
    LOG_LEVEL: str  # optional
    BOT_NAME: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str
    AWS_S3_BUCKET: str
    WINEDB_HOST: str  # optional
    WINEDB_PASSWORD: str  # optional
    OPENAI_API_KEY: str
    BING_SEARCH_URL: str  # optional
    BING_SUBSCRIPTION_KEY: str  # optional
    SERPAPI_API_KEY: str  # optional


settings: DotEnv = {
    "PORT": int(os.getenv("PORT", 8000)),
    "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
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
