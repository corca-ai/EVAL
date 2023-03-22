from env import settings

from typing import Dict
import requests

from llama_index.readers.database import DatabaseReader
from llama_index import GPTSimpleVectorIndex

from bs4 import BeautifulSoup
from langchain.agents.agent import AgentExecutor

import subprocess

from tools.base import tool, BaseToolSet, ToolScope
from logger import logger


class Terminal(BaseToolSet):
    @tool(
        name="Terminal",
        description="Executes commands in a terminal."
        "You can install packages with pip, apt, etc."
        "Input should be valid commands, "
        "and the output will be any output from running that command.",
    )
    def execute(self, commands: str) -> str:
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

        logger.debug(
            f"\nProcessed Terminal, Input Commands: {commands} "
            f"Output Answer: {output}"
        )
        return output


class CodeEditor(BaseToolSet):
    @tool(
        name="CodeEditor.READ",
        description="Read and understand code. "
        "Input should be filename and line number group. ex. test.py,1-10 "
        "and the output will be code. ",
    )
    def read(self, inputs: str) -> str:
        filename, line = inputs.split(",")
        line = line.split("-")
        if len(line) == 1:
            line = int(line[0])
        else:
            line = [int(i) for i in line]

        try:
            with open(filename, "r") as f:
                code = f.readlines()
            if isinstance(line, int):
                code = code[line - 1]
            else:
                code = "".join(code[line[0] - 1 : line[1]])
            output = code
        except Exception as e:
            output = str(e)

        logger.debug(
            f"\nProcessed CodeEditor.READ, Input Commands: {inputs} "
            f"Output Answer: {output}"
        )
        return output

    @tool(
        name="CodeEditor.WRITE",
        description="Write code to create a new tool. "
        "You must check the file's contents before writing. This tool only supports append code.  "
        "If the code is completed, use the Terminal tool to execute it, if not, append the code through the CodeEditor tool. "
        "Input should be filename and code. "
        "ex. test.py\nprint('hello world')\n "
        "and the output will be last 3 line.",
    )
    def write(self, inputs: str) -> str:
        filename, code = inputs.split("\n", 1)

        try:
            with open(filename, "a") as f:
                f.write(code)
            output = "Last 3 line was:\n" + "\n".join(code.split("\n")[-3:])
        except Exception as e:
            output = str(e)

        logger.debug(
            f"\nProcessed CodeEditor, Input Codes: {code} " f"Output Answer: {output}"
        )
        return output

    @tool(
        name="CodeEditor.PATCH",
        description="Correct the error throught the code patch if an error occurs. "
        "Input should be list of filename, line number, new line (Be sure to consider indentations.) Seperated by -||-."
        "ex. \"test.py-||-1-||-print('hello world')\ntest.py-||-2-||-print('hello world')\n\" "
        "and the output will be success or error message. ",
    )
    def patch(self, patches: str) -> str:
        for patch in patches.split("\n"):
            filename, line_number, new_line = patch.split("-||-")  # TODO: fix this
            try:
                with open(filename, "r") as f:
                    lines = f.readlines()
                lines[int(line_number) - 1] = new_line + "\n"
                with open(filename, "w") as f:
                    f.writelines(lines)
                output = "success"
            except Exception as e:
                output = str(e)
        logger.debug(
            f"\nProcessed CodeEditor, Input Patch: {patches} "
            f"Output Answer: {output}"
        )
        return output

    @tool(
        name="CodeEditor.DELETE",
        description="Delete code in file for a new start. "
        "Input should be filename."
        "ex. test.py "
        "Output will be success or error message.",
    )
    def delete(self, inputs: str) -> str:
        filename = inputs
        try:
            with open(filename, "w") as f:
                f.write("")
            output = "success"
        except Exception as e:
            output = str(e)

        logger.debug(
            f"\nProcessed CodeEditor, Input filename: {inputs} "
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
    def get(self, url: str) -> str:
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

        logger.debug(
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
    def recommend(self, query: str) -> str:
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

        logger.debug(
            f"\nProcessed WineDB, Input Query: {query} " f"Output Wine: {wine}"
        )

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

        logger.debug(f"\nProcessed ExitConversation.")

        return f"Exit conversation."
