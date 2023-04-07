"""
patch protocol:

<filepath>|<line>,<col>|<line>,<col>|<content>
---~~~+++===+++~~~---
<filepath>|<line>,<col>|<line>,<col>|<content>
---~~~+++===+++~~~---
...
---~~~+++===+++~~~---

let say original code is:
```
import requests

def crawl_news(keyword):
    url = f"https://www.google.com/search?q={keyword}+news"
    response = requests.get(url)

    news = []
    for result in response:
        news.append(result.text)

    return news
```

and we want to change it to:
```
import requests
from bs4 import BeautifulSoup

def crawl_news(keyword):
    url = f"https://www.google.com/search?q={keyword}+news"
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    news_results = soup.find_all("div", class_="BNeawe vvjwJb AP7Wnd")

    news_titles = []
    for result in news_results:
        news_titles.append(result.text)

    return news_titles
```

then the command will be:
test.py|2,1|2,1|from bs4 import BeautifulSoup

---~~~+++===+++~~~---
test.py|5,5|5,33|html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    news_results = soup.find_all("div", class_="BNeawe vvjwJb AP7Wnd")
---~~~+++===+++~~~---
test.py|7,5|9,13|news_titles = []
    for result in news_results:
        news_titles
---~~~+++===+++~~~---
test.py|11,16|11,16|_titles
"""

import os
import re
from pathlib import Path
from typing import Tuple

from env import settings

from .verify import verify


class Position:
    separator = ","

    def __init__(self, line: int, col: int):
        self.line: int = line
        self.col: int = col

    def __str__(self):
        return f"(Ln {self.line}, Col {self.col})"

    @staticmethod
    def from_str(pos: str) -> "Position":
        line, col = pos.split(Position.separator)
        return Position(int(line) - 1, int(col) - 1)


class PatchCommand:
    separator = "|"

    def __init__(self, filepath: str, start: Position, end: Position, content: str):
        self.filepath: str = filepath
        self.start: Position = start
        self.end: Position = end
        self.content: str = content

    def read_lines(self) -> list[str]:
        with open(self.filepath, "r") as f:
            lines = f.readlines()
        return lines

    def write_lines(self, lines: list[str]) -> int:
        with open(self.filepath, "w") as f:
            f.writelines(lines)
        return sum([len(line) for line in lines])

    @verify
    def execute(self) -> Tuple[int, int]:
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        lines = self.read_lines()
        before = sum([len(line) for line in lines])

        lines[self.start.line] = (
            lines[self.start.line][: self.start.col]
            + self.content
            + lines[self.end.line][self.end.col :]
        )
        lines = lines[: self.start.line + 1] + lines[self.end.line + 1 :]

        after = self.write_lines(lines)

        written = len(self.content)
        deleted = before - after + written

        return written, deleted

    @staticmethod
    def from_str(command: str) -> "PatchCommand":
        match = re.search(
            r"(.*)\|([0-9]*),([0-9]*)\|([0-9]*),([0-9]*)(\||\n)(.*)",
            command,
            re.DOTALL,
        )
        filepath = match.group(1)
        start_line = match.group(2)
        start_col = match.group(3)
        end_line = match.group(4)
        end_col = match.group(5)
        content = match.group(7)
        return PatchCommand(
            filepath,
            Position.from_str(f"{start_line},{start_col}"),
            Position.from_str(f"{end_line},{end_col}"),
            content,
        )


class CodePatcher:
    separator = "\n---~~~+++===+++~~~---\n"

    @staticmethod
    def sort_commands(commands: list[PatchCommand]) -> list[PatchCommand]:
        return sorted(commands, key=lambda c: c.start.line, reverse=True)

    @staticmethod
    def patch(bulk_command: str) -> Tuple[int, int]:
        commands = [
            PatchCommand.from_str(command)
            for command in bulk_command.split(CodePatcher.separator)
            if command != ""
        ]
        commands = CodePatcher.sort_commands(commands)

        written, deleted = 0, 0
        for command in commands:
            if command:
                w, d = command.execute()
                written += w
                deleted += d
        return written, deleted


if __name__ == "__main__":
    commands = """test.py|2,1|2,1|from bs4 import BeautifulSoup

---~~~+++===+++~~~---
test.py|5,5|5,33|html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    news_results = soup.find_all("div", class_="BNeawe vvjwJb AP7Wnd")
---~~~+++===+++~~~---
test.py|7,5|9,13|news_titles = []
    for result in news_results:
        news_titles
---~~~+++===+++~~~---
test.py|11,16|11,16|_titles
"""

    example = """import requests

def crawl_news(keyword):
    url = f"https://www.google.com/search?q={keyword}+news"
    response = requests.get(url)

    news = []
    for result in response:
        news.append(result.text)

    return news
"""
    testfile = "test.py"
    with open(testfile, "w") as f:
        f.write(example)

    patcher = CodePatcher()
    written, deleted = patcher.patch(commands)
    print(f"written: {written}, deleted: {deleted}")
