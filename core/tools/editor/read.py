"""
read protocol:

<filepath>|<start line>-<end line>
"""
from pathlib import Path
from typing import List, Optional, Tuple

from env import settings


class Line:
    def __init__(self, content: str, line_number: int, depth: int):
        self.__content: str = content
        self.__line_number: int = line_number
        self.__depth: int = depth
        self.__children: List[Line] = []

    def get_content(self) -> str:
        return self.__content

    def get_depth(self) -> int:
        return self.__depth

    def append_child(self, child: "Line") -> None:
        self.__children.append(child)

    def find_by_lte_depth(self, depth: int) -> List["Line"]:
        if self.__depth > depth:
            return []

        lines: List[Line] = [self]
        for child in self.__children:
            lines += child.find_by_lte_depth(depth)
        return lines

    def find_by_content(self, content: str) -> List["Line"]:
        if content in self.__content:
            return [self]

        lines: List[Line] = []
        for child in self.__children:
            lines += child.find_by_content(content)
        return lines

    def find_last_lines(self) -> List["Line"]:
        if len(self.__children) == 0:
            return [self]
        else:
            return [self, *self.__children[-1].find_last_lines()]

    def print(self, depth: int = 0) -> None:
        print(f"{'  ' * depth}{self}", end="")
        for child in self.__children:
            child.print(depth + 1)

    def __repr__(self):
        return f"{self.__line_number}: {self.__content}"


class CodeTree:
    def __init__(self):
        self.root: Line = Line("\n", -1, -1)

    def append(self, content: str, line_number: int) -> None:
        last_lines: List[Line] = self.root.find_last_lines()
        new_leading_spaces: int = self.__get_leading_spaces(content)

        previous_line: Line = self.root
        previous_leading_spaces: int = -1
        for line in last_lines:
            leading_spaces = self.__get_leading_spaces(line.get_content())
            if (
                previous_leading_spaces < new_leading_spaces
                and new_leading_spaces <= leading_spaces
            ):
                break
            previous_line, previous_leading_spaces = line, leading_spaces

        new_line_depth: int = previous_line.get_depth() + 1
        previous_line.append_child(Line(content, line_number, new_line_depth))

    def find_from_root(self, depth: int) -> List[Line]:
        return self.root.find_by_lte_depth(depth)

    def find_from_parent(self, depth: int, parent_content: str) -> List[Line]:
        lines: List[Line] = self.root.find_by_content(parent_content)
        if len(lines) == 0:
            return []
        parent = lines[0]
        return parent.find_by_lte_depth(depth + parent.get_depth())

    def print(self):
        print("Code Tree:")
        print("=================================")
        self.root.print()
        print("=================================")

    def __get_leading_spaces(self, content: str) -> int:
        return len(content) - len(content.lstrip())


class ReadCommand:
    separator = "|"

    def __init__(self, filepath: str, start: int, end: int):
        self.filepath: str = str(Path(settings["PLAYGROUND_DIR"]) / Path(filepath))
        self.start: int = start
        self.end: int = end

    def execute(self) -> str:
        if not str(Path(self.filepath).resolve()).startswith(
            str(Path(settings["PLAYGROUND_DIR"]).resolve())
        ):
            return "You can't write file outside of current directory."

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


class SummaryCommand:
    separator = "|"

    def __init__(self, filepath: str, depth: int, parent_content: Optional[str] = None):
        self.filepath: str = str(Path(settings["PLAYGROUND_DIR"]) / Path(filepath))
        self.depth: int = depth
        self.parent_content: Optional[str] = parent_content

    def execute(self) -> str:
        if not str(Path(self.filepath).resolve()).startswith(
            str(Path(settings["PLAYGROUND_DIR"]).resolve())
        ):
            return "You can't write file outside of current directory."

        with open(self.filepath, "r") as f:
            code = f.readlines()

        code_tree = CodeTree()
        for i, line in enumerate(code):
            if line.strip() != "":
                code_tree.append(line, i + 1)

        # code_tree.print()

        if self.parent_content is None:
            lines = code_tree.find_from_root(self.depth)
        else:
            lines = code_tree.find_from_parent(self.depth, self.parent_content)
        return "".join([str(line) for line in lines])

    @staticmethod
    def from_str(command: str) -> "SummaryCommand":
        command_list: List[str] = command.split(SummaryCommand.separator)
        filepath: str = command_list[0]
        depth: int = int(command_list[1])
        parent_content: str | None = command_list[2] if len(command_list) == 3 else None
        return SummaryCommand(
            filepath=filepath, depth=depth, parent_content=parent_content
        )


class CodeReader:
    @staticmethod
    def read(command: str) -> str:
        return ReadCommand.from_str(command).execute()

    @staticmethod
    def summary(command: str) -> str:
        return SummaryCommand.from_str(command).execute()


if __name__ == "__main__":
    summary = CodeReader.summary("read.py|1|class ReadCommand:")
    print(summary)
