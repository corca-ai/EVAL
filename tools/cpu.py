from env import settings

import requests

from llama_index.readers.database import DatabaseReader
from llama_index import GPTSimpleVectorIndex

from langchain.memory.chat_memory import BaseChatMemory

"""Wrapper around subprocess to run commands."""
import subprocess
from typing import List, Union

from .base import tool, BaseToolSet


class Terminal(BaseToolSet):
    """Executes bash commands and returns the output."""

    def __init__(self, strip_newlines: bool = False, return_err_output: bool = False):
        """Initialize with stripping newlines."""
        self.strip_newlines = strip_newlines
        self.return_err_output = return_err_output

    @tool(
        name="Terminal",
        description="Executes commands in a terminal."
        "Input should be valid commands, "
        "and the output will be any output from running that command. This result should always be wrapped in a code block.",
    )
    def inference(self, commands: Union[str, List[str]]) -> str:
        """Run commands and return final output."""
        if isinstance(commands, str):
            commands = [commands]
        commands = ";".join(commands)
        try:
            output = subprocess.run(
                commands,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            ).stdout.decode()
        except Exception as e:
            if self.return_err_output:
                return e.stdout.decode()
            return str(e)
        if self.strip_newlines:
            output = output.strip()
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
        text = requests.get(url).text

        if len(text) > 100:
            text = text[:100] + "..."
        return text


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
        # CAST(type AS VARCHAR), 'nameEn', 'nameKo', vintage, nationality, province, CAST(size AS VARCHAR), 'grapeVariety', price, image, description, code, winery, alcohol, pairing
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
        return results.response + "\n\n" + wine


class ExitConversation(BaseToolSet):
    @tool(
        name="exit_conversation",
        description="A tool to exit the conversation. "
        "Use this when you want to end the conversation. "
        "Input should be a user's query and user's session."
        "The output will be a message that the conversation is over.",
    )
    def inference(self, query: str, session: str) -> str:
        """Run the tool."""
        # session.clear() # TODO

        return f"My original question was: {query}"
