from env import settings

import requests

from llama_index.readers.database import DatabaseReader
from llama_index import GPTSimpleVectorIndex

from bs4 import BeautifulSoup
from langchain.memory.chat_memory import BaseChatMemory

"""Wrapper around subprocess to run commands."""
import subprocess

from .base import tool, BaseToolSet


class Terminal(BaseToolSet):
    """Executes bash commands and returns the output."""

    @tool(
        name="Terminal",
        description="Executes commands in a terminal."
        "Input should be valid commands, "
        "and the output will be any output from running that command.",
    )
    def inference(self, commands: str) -> str:
        """Run commands and return final output."""
        try:
            output = subprocess.run(
                commands,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            ).stdout.decode()
        except Exception as e:
            output = str(e)

        print(
            f"\nProcessed Terminal, Input Commands: {commands} "
            f"Output Answer: {output}"
        )
        return output


class RequestsGet(BaseToolSet):
    @tool(
        name="requests_get",
        description="A portal to the internet. "
        "Use this when you need to get specific content from a website."
        "Input should be a  url (i.e. https://www.google.com)."
        "The output will be the text response of the GET request.",
    )
    def inference(self, url: str) -> str:
        """Run the tool."""
        html = requests.get(url).text
        soup = BeautifulSoup(html)
        non_readable_tags = soup.find_all(
            ["script", "style", "header", "footer", "form"]
        )

        for non_readable_tag in non_readable_tags:
            non_readable_tag.extract()

        content = soup.get_text("\n", strip=True)

        if len(content) > 300:
            content = content[:300] + "..."

        print(
            f"\nProcessed RequestsGet, Input Url: {url} " f"Output Contents: {content}"
        )

        return content


class WineDB(BaseToolSet):
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
        documents = db.load_data(query=query)
        self.index = GPTSimpleVectorIndex(documents)

    @tool(
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
        output = results.response + "\n\n" + wine

        print(f"\nProcessed WineDB, Input Query: {query} " f"Output Wine: {wine}")

        return output


class ExitConversation(BaseToolSet):
    @tool(
        name="exit_conversation",
        description="A tool to exit the conversation. "
        "Use this when you want to end the conversation. "
        "Input should be a user's query."
        "The output will be a message that the conversation is over.",
    )
    def inference(self, query: str) -> str:
        """Run the tool."""
        # session.clear() # TODO

        print(f"\nProcessed ExitConversation, Input Query: {query} ")

        return f"My original question was: {query}"
