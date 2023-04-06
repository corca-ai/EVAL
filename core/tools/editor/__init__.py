from pathlib import Path

from core.tools.base import BaseToolSet, tool
from env import settings
from logger import logger

from .patch import CodePatcher
from .read import CodeReader
from .write import CodeWriter


class CodeEditor(BaseToolSet):
    @tool(
        name="CodeEditor.READ",
        description="Read and understand code. "
        f"Input should be filename and line number group. ex. test.py|1-10 "
        "and the output will be code. ",
    )
    def read(self, inputs: str) -> str:
        try:
            output = CodeReader.read(inputs)
        except Exception as e:
            output = str(e)

        logger.debug(
            f"\nProcessed CodeEditor.READ, Input Commands: {inputs} "
            f"Output Answer: {output}"
        )
        return output

    @tool(
        name="CodeEditor.SUMMARY",
        description="Summary code. "
        "Read the code structured into a tree. "
        "If you set specific line, it will show the code from the specific line. "
        "Input should be filename, depth, and specific line if you want. ex. test.py|2 or test.py|3|print('hello world') "
        "and the output will be list of (line number: code). ",
    )
    def summary(self, inputs: str) -> str:
        try:
            output = CodeReader.summary(inputs)
        except Exception as e:
            output = str(e)

        logger.debug(
            f"\nProcessed CodeEditor.SUMMARY, Input Commands: {inputs} "
            f"Output Answer: {output}"
        )
        return output

    @tool(
        name="CodeEditor.APPEND",
        description="Append code to the existing file. "
        "If the code is completed, use the Terminal tool to execute it, if not, append the code through the this tool. "
        "Input should be filename and code to append. "
        "Input code must be the code that should be appended, NOT whole code. "
        "ex. test.py\nprint('hello world')\n "
        "and the output will be last 3 lines.",
    )
    def append(self, inputs: str) -> str:
        try:
            code = CodeWriter.append(inputs)
            output = (
                "Last 3 line was:\n"
                + "\n".join(code.split("\n")[-3:])
            )
        except Exception as e:
            output = str(e)

        logger.debug(
            f"\nProcessed CodeEditor.APPEND, Input: {inputs} "
            f"Output Answer: {output}"
        )
        return output

    @tool(
        name="CodeEditor.WRITE",
        description="Write code to create a new tool. "
        "If the code is completed, use the Terminal tool to execute it, if not, append the code through the CodeEditor.APPEND tool. "
        "Input should be filename and code. This file must be in playground folder. "
        "ex. test.py\nprint('hello world')\n "
        "and the output will be last 3 lines.",
    )
    def write(self, inputs: str) -> str:
        try:
            code = CodeWriter.write(inputs)
            output = (
                "Last 3 line was:\n"
                + "\n".join(code.split("\n")[-3:])
            )
        except Exception as e:
            output = str(e)

        logger.debug(
            f"\nProcessed CodeEditor.WRITE, Input: {inputs} " f"Output Answer: {output}"
        )
        return output

    @tool(
        name="CodeEditor.PATCH",
        description="Patch the code to correct the error if an error occurs or to improve it. "
        "Input is a list of patches. The patch is separated by {seperator}. ".format(
            seperator=CodePatcher.separator.replace("\n", "\\n")
        )
        + "Each patch has to be formatted like below.\n"
        "<filepath>|<start_line>,<start_col>|<end_line>,<end_col>|<new_code>"
        "Here is an example. If the original code is:\n"
        "print('hello world')\n"
        "and you want to change it to:\n"
        "print('hi corca')\n"
        "then the patch should be:\n"
        "test.py|1,8|1,19|hi corca\n"
        "Code between start and end will be replaced with new_code. "
        "The output will be written/deleted bytes or error message. ",
    )
    def patch(self, patches: str) -> str:
        try:
            w, d = CodePatcher.patch(patches)
            output = f"successfully wrote {w}, deleted {d}"
        except Exception as e:
            output = str(e)

        logger.debug(
            f"\nProcessed CodeEditor.PATCH, Input Patch: {patches} "
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
        try:
            with open(filepath, "w") as f:
                f.write("")
            output = "success"
        except Exception as e:
            output = str(e)

        logger.debug(
            f"\nProcessed CodeEditor.DELETE, Input filename: {inputs} "
            f"Output Answer: {output}"
        )
        return output
