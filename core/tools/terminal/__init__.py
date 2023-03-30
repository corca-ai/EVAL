import subprocess
from typing import Dict, List

from tempfile import TemporaryFile

from env import settings
from logger import logger
from core.tools.base import tool, BaseToolSet, ToolScope, SessionGetter
from core.tools.terminal.syscall import SyscallTracer


class Terminal(BaseToolSet):
    def __init__(self):
        self.sessions: Dict[str, List[SyscallTracer]] = {}

    @tool(
        name="Terminal",
        description="Executes commands in a terminal."
        "If linux errno occurs, we have to solve the problem with the terminal. "
        "It can't execute interactive operations or blocking operations. "
        "Input should be valid commands, "
        "and the output will be any output from running that command.",
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

                tracer = SyscallTracer(process.pid)
                tracer.attach()
                exitcode, reason = tracer.wait_until_stop_or_exit()
                logger.debug(f"Stopped terminal execution: {exitcode} {reason}")

                fp.seek(0)
                output = fp.read().decode()
        except Exception as e:
            output = str(e)

        if len(output) > 1000:
            output = output[:1000] + "..."

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
