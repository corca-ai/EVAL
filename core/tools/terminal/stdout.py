import os
import time
import subprocess
from datetime import datetime
from typing import Callable, Literal, Optional, Union, Tuple

PipeType = Union[Literal["stdout"], Literal["stderr"]]


class StdoutTracer:
    def __init__(
        self,
        process: subprocess.Popen,
        timeout: int = 30,
        interval: int = 0.1,
        on_output: Callable[[PipeType, str], None] = lambda: None,
    ):
        self.process: subprocess.Popen = process
        self.timeout: int = timeout
        self.interval: int = interval
        self.last_output: datetime = None
        self.on_output: Callable[[PipeType, str], None] = on_output

    def nonblock(self):
        os.set_blocking(self.process.stdout.fileno(), False)
        os.set_blocking(self.process.stderr.fileno(), False)

    def get_output(self, pipe: PipeType) -> str:
        output = None
        if pipe == "stdout":
            output = self.process.stdout.read()
        elif pipe == "stderr":
            output = self.process.stderr.read()

        if output:
            decoded = output.decode()
            self.on_output(pipe, decoded)
            self.last_output = datetime.now()
            return decoded
        return ""

    def last_output_passed(self, seconds: int) -> bool:
        return (datetime.now() - self.last_output).seconds > seconds

    def wait_until_stop_or_exit(self) -> Tuple[Optional[int], str]:
        self.nonblock()
        self.last_output = datetime.now()
        output = ""
        exitcode = None
        while True:
            new_stdout = self.get_output("stdout")
            if new_stdout:
                output += new_stdout

            new_stderr = self.get_output("stderr")
            if new_stderr:
                output += new_stderr

            if self.process.poll() is not None:
                exitcode = self.process.poll()
                break

            if self.last_output_passed(self.timeout):
                self.process.kill()
                break

            time.sleep(self.interval)

        return (exitcode, output)
