from env import settings

from typing import Dict
import requests

from llama_index.readers.database import DatabaseReader
from llama_index import GPTSimpleVectorIndex

from bs4 import BeautifulSoup
from langchain.agents.agent import AgentExecutor

import subprocess

from .base import tool, BaseToolSet, ToolScope


class Terminal(BaseToolSet):
    @tool(
        name="Terminal",
        description="Executes commands in a terminal."
        "You can install packages with pip, apt, etc."
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


class CodeEditor(BaseToolSet):
    @tool(
        name="CodeEditor.WRITE",
        description="Writes and appends code."
        "It can be used to write or append code in any language. "
        "If the code is completed, use the Terminal tool to execute it, if not, append the code through the CodeEditor tool."
        "Input should be filename, status, code. Status will be 'complete' or 'incomplete'. ex. 'test.py|complete\nprint('hello world')\n"
        "and the output will be status and last line. status will be 'complete' or 'incomplete' or 'error'.",
    )
    def write(self, inputs: str) -> str:
        """Save codes to file and return success or failure."""
        filename, status_and_code = inputs.split("|", 1)
        status, code = status_and_code.split("\n", 1)

        if status != "complete" and status != "incomplete":
            return "error: status must be complete or incomplete"

        try:
            with open(filename, "a") as f:
                f.write(code)
            output = status + "\nLast line was:" + code.split("\n")[-1]
        except Exception as e:
            output = "error"
        print(
            f"\nProcessed CodeEditor, Input Codes: {code} " f"Output Answer: {output}"
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
        name="Wine Recommendation",
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
        name="Exit Conversation",
        description="A tool to exit the conversation. "
        "Use this when you want to exit the conversation. "
        "Input should be a user's session."
        "The output will be a message that the conversation is over.",
        scope=ToolScope.SESSION,
    )
    def exit(self, *args, session: str) -> str:
        """Run the tool."""
        self.executors.pop(session)

        print(f"\nProcessed ExitConversation.")

        return f"Exit conversation."
