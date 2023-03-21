import json
import re
from typing import Dict

from langchain.output_parsers.base import BaseOutputParser

from prompts.input import EVAL_FORMAT_INSTRUCTIONS


class EvalOutputParser(BaseOutputParser):
    def get_format_instructions(self) -> str:
        return EVAL_FORMAT_INSTRUCTIONS

    def parse(self, text: str) -> Dict[str, str]:
        regex = r"Action: (.*?)[\n]*Action Input: (.*)"
        match = re.search(regex, text, re.DOTALL)
        if not match:
            raise ValueError(f"Could not parse LLM output: `{text}`")
        action = match.group(1).strip()
        action_input = match.group(2)
        return {"action": action, "action_input": action_input.strip(" ").strip('"')}
