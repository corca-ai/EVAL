import re
from typing import Dict

from langchain.output_parsers.base import BaseOutputParser

from core.prompts.input import EVAL_FORMAT_INSTRUCTIONS


class EvalOutputParser(BaseOutputParser):
    def get_format_instructions(self) -> str:
        return EVAL_FORMAT_INSTRUCTIONS

    def parse(self, text: str) -> Dict[str, str]:
        regex = r"Action: (.*?)[\n]Plan:(.*)Action Input: (.*)"
        match = re.search(regex, text, re.DOTALL)
        if not match:
            raise Exception("parse error")
        action = match.group(1).strip()
        action_input = match.group(3)
        return {"action": action, "action_input": action_input.strip(" ").strip('"')}

    def __str__(self):
        return "EvalOutputParser"
