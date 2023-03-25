"""
write protocol:

<filepath>
<content>
"""
import os


class WriteCommand:
    separator = "\n"

    def __init__(self, filepath: str, content: int):
        self.filepath: str = filepath
        self.content: str = content
        self.mode: str = "w"

    def with_mode(self, mode: str) -> "WriteCommand":
        self.mode = mode
        return self

    def execute(self) -> str:
        # make sure the directory exists
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        with open(self.filepath, self.mode) as f:
            f.write(self.content)
        return self.content

    @staticmethod
    def from_str(command: str) -> "WriteCommand":
        filepath = command.split(WriteCommand.separator)[0]
        return WriteCommand(filepath, command[len(filepath) + 1 :])


class CodeWriter:
    @staticmethod
    def write(command: str) -> str:
        return WriteCommand.from_str(command).with_mode("w").execute()

    @staticmethod
    def append(command: str) -> str:
        return WriteCommand.from_str(command).with_mode("a").execute()
