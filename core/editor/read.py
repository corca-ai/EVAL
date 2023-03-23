"""
read protocol:

<filepath>|<start line>-<end line>
"""


class ReadCommand:
    separator = "|"

    def __init__(self, filepath: str, start: int, end: int):
        self.filepath: str = filepath
        self.start: int = start
        self.end: int = end

    def execute(self):
        with open(self.filepath, "r") as f:
            code = f.readlines()
        if self.start == self.end:
            code = code[self.start - 1]
        else:
            code = "".join(code[self.start - 1 : self.end])
        return code

    @staticmethod
    def from_str(command: str) -> "ReadCommand":
        filepath, line = command.split(ReadCommand.separator)
        start, end = line.split("-")
        return ReadCommand(filepath, int(start), int(end))


class CodeReader:
    @staticmethod
    def read(command: str) -> str:
        return ReadCommand.from_str(command).execute()
