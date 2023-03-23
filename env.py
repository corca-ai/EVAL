import os
from typing import TypedDict

from dotenv import load_dotenv

load_dotenv()


class DotEnv(TypedDict):
    OPENAI_API_KEY: str

    PORT: int
    SERVER: str

    LOG_LEVEL: str  # optional
    BOT_NAME: str  # optional
    AWS_ACCESS_KEY_ID: str  # optional
    AWS_SECRET_ACCESS_KEY: str  # optional
    AWS_REGION: str  # optional
    AWS_S3_BUCKET: str  # optional
    WINEDB_HOST: str  # optional
    WINEDB_PASSWORD: str  # optional
    BING_SEARCH_URL: str  # optional
    BING_SUBSCRIPTION_KEY: str  # optional
    SERPAPI_API_KEY: str  # optional


PORT = int(os.getenv("PORT", 8000))
settings: DotEnv = {
    "PORT": PORT,
    "SERVER": os.getenv("SERVER", f"http://localhost:{PORT}"),
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
    "BOT_NAME": os.getenv("BOT_NAME", "Orca"),
    "WINEDB_HOST": os.getenv("WINEDB_HOST"),
    "WINEDB_PASSWORD": os.getenv("WINEDB_PASSWORD"),
    "BING_SEARCH_URL": os.getenv("BING_SEARCH_URL"),
    "BING_SUBSCRIPTION_KEY": os.getenv("BING_SUBSCRIPTION_KEY"),
    "SERPAPI_API_KEY": os.getenv("SERPAPI_API_KEY"),
}
