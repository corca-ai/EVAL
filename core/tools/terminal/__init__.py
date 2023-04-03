import os
import time
import subprocess
from datetime import datetime
from typing import Dict, List

from core.tools.base import BaseToolSet, SessionGetter, ToolScope, tool
from core.tools.terminal.syscall import SyscallTracer
from core.tools.terminal.stdout import StdoutTracer
from env import settings
from logger import logger
from ansi import ANSI, Color, Style


class Terminal(BaseToolSet):
    def __init__(self):
        self.sessions: Dict[str, List[SyscallTracer]] = {}

    @tool(
        name="Terminal",
        description="Executes commands in a terminal."
        "If linux errno occurs, we have to solve the problem with the terminal. "
        "Input must be one valid command. "
        "Output will be any output from running that command.",
        scope=ToolScope.SESSION,
    )
    def execute(self, commands: str, get_session: SessionGetter) -> str:
        session, _ = get_session()

        try:
            process = subprocess.Popen(
                commands,
                shell=True,
                cwd=settings["PLAYGROUND_DIR"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            logger.info(ANSI("Realtime Terminal Output").to(Color.magenta()) + ": ")

            output = ""
            tracer = StdoutTracer(
                process,
                on_output=lambda p, o: logger.info(
                    ANSI(p).to(Style.dim()) + " " + o.strip("\n")
                ),
            )
            exitcode, output = tracer.wait_until_stop_or_exit()
        except Exception as e:
            output = str(e)

        logger.debug(
            f"\nProcessed Terminal, Input Commands: {commands} "
            f"Output Answer: {output}"
        )
        return output


if __name__ == "__main__":
    import time

    o = Terminal().execute(
        "sleep 1; echo 1; sleep 2; echo 2; sleep 3; echo 3; sleep 10;",
        lambda: ("", None),
    )
    print(o)

    time.sleep(10)  # see if timer has reset
