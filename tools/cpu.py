from utils import prompts
from env import settings

import requests

from llama_index.readers.database import DatabaseReader
from llama_index import GPTSimpleVectorIndex

from langchain.memory.chat_memory import BaseChatMemory


class RequestsGet:
    @prompts(
        name="requests_get",
        description="A portal to the internet. "
        "Use this when you need to get specific content from a website."
        "Input should be a  url (i.e. https://www.google.com)."
        "The output will be the text response of the GET request.",
    )
    def inference(self, url: str) -> str:
        """Run the tool."""
        text = requests.get(url).text

        if len(text) > 100:
            text = text[:100] + "..."
        return text


class WineDB:
    def __init__(self):
        db = DatabaseReader(
            scheme="postgresql",  # Database Scheme
            host=settings["WINEDB_HOST"],  # Database Host
            port="5432",  # Database Port
            user="alphadom",  # Database User
            password=settings["WINEDB_PASSWORD"],  # Database Password
            dbname="postgres",  # Database Name
        )
        self.columns = ["nameEn", "nameKo", "description"]
        concat_columns = str(",'-',".join([f'"{i}"' for i in self.columns]))
        query = f"""
            SELECT
                Concat({concat_columns})
            FROM wine
        """
        # CAST(type AS VARCHAR), 'nameEn', 'nameKo', vintage, nationality, province, CAST(size AS VARCHAR), 'grapeVariety', price, image, description, code, winery, alcohol, pairing
        documents = db.load_data(query=query)
        self.index = GPTSimpleVectorIndex(documents)

    @prompts(
        name="Wine Recommendataion",
        description="A tool to recommend wines based on a user's input. "
        "Inputs are necessary factors for wine recommendations, such as the user's mood today, side dishes to eat with wine, people to drink wine with, what things you want to do, the scent and taste of their favorite wine."
        "The output will be a list of recommended wines."
        "The tool is based on a database of wine reviews, which is stored in a database.",
    )
    def inference(self, query: str) -> str:
        """Run the tool."""
        results = self.index.query(query)
        wine = "\n".join(
            [
                f"{i}:{j}"
                for i, j in zip(
                    self.columns, results.source_nodes[0].source_text.split("-")
                )
            ]
        )
        return results.response + "\n\n" + wine


class ExitConversation:
    def __init__(self, memory: BaseChatMemory):
        self.memory = memory

    @prompts(
        name="exit_conversation",
        description="A tool to exit the conversation. "
        "Use this when you want to end the conversation. "
        "The output will be a message that the conversation is over.",
    )
    def inference(self, query: str) -> str:
        """Run the tool."""
        self.memory.chat_memory.messages = []
        return ""
