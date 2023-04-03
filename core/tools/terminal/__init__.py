import time
import subprocess
from datetime import datetime
from tempfile import TemporaryFile
from typing import Dict, List

from core.tools.base import BaseToolSet, SessionGetter, ToolScope, tool
from core.tools.terminal.syscall import SyscallTracer
from env import settings
from logger import logger
from ansi import ANSI, Color, dim_multiline


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
            with TemporaryFile() as fp:
                process = subprocess.Popen(
                    commands,
                    shell=True,
                    cwd=settings["PLAYGROUND_DIR"],
                    stdout=fp,
                    stderr=fp,
                )

                output = ""
                last_stdout = datetime.now()
                while True:
                    fp.seek(0)
                    new_output = fp.read().decode()
                    if new_output != output:
                        logger.info(
                            ANSI("Terminal Output").to(Color.magenta())
                            + ": "
                            + dim_multiline(new_output[len(output) :])
                        )
                        output = new_output
                        last_stdout = datetime.now()

                    if (datetime.now() - last_stdout).seconds > 10:
                        process.kill()
                        break

                    time.sleep(0.1)

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
