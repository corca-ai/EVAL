import re
import time
from typing import Dict

from ansi import ANSI, Color, Style, dim_multiline
from core.prompts.input import EVAL_FORMAT_INSTRUCTIONS
from langchain.output_parsers.base import BaseOutputParser
from logger import logger


class EvalOutputParser(BaseOutputParser):
    def get_format_instructions(self) -> str:
        return EVAL_FORMAT_INSTRUCTIONS

    def parse(self, text: str) -> Dict[str, str]:
        regex = r"Action: (.*?)[\n]Plan:(.*)[\n]What I Did:(.*)[\n]What Should I Do:(.*)[\n]Action Input: (.*)"
        match = re.search(regex, text, re.DOTALL)
        if not match:
            raise Exception("parse error")

        action = match.group(1).strip()
        plan = match.group(2)
        what_i_did = match.group(3)
        what_should_i_do = match.group(4)
        action_input = match.group(5)

        logger.info(ANSI("Plan").to(Color.blue().bright()) + ": " + plan)
        logger.info(ANSI("What I Did").to(Color.blue()) + ": " + what_i_did)
        logger.info(ANSI("What Should I Do").to(Color.blue()) + ": " + what_should_i_do)
        time.sleep(1)
        logger.info(
            ANSI("Action").to(Color.cyan()) + ": " + ANSI(action).to(Style.bold())
        )
        time.sleep(1)
        logger.info(ANSI("Input").to(Color.cyan()) + ": " + dim_multiline(action_input))
        time.sleep(1)
        return {
            "action": action,
            "action_input": action_input.strip(" ").strip('"'),
        }

    def __str__(self):
        return "EvalOutputParser"
