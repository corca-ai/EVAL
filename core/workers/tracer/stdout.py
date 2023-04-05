import os
import time
import subprocess
from datetime import datetime
from typing import Literal, Optional, Union, Tuple
from .base import BaseTracer, OnOutputHandler

PipeType = Union[Literal["stdout"], Literal["stderr"]]


class StdoutTracer(BaseTracer):
    def __init__(
        self,
        process: subprocess.Popen,
        timeout: int = 30,
        on_output: OnOutputHandler = lambda: None,
        interval: int = 0.1,
    ):
        super().__init__(process, on_output)
        self.process: subprocess.Popen = process
        self.timeout: int = timeout
        self.interval: int = interval
        self.last_output: datetime = None

    def last_output_passed(self, seconds: int) -> bool:
        return (datetime.now() - self.last_output).seconds > seconds

    def wait_until_stop_or_exit(self) -> Tuple[Optional[int], str]:
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
                break

            time.sleep(self.interval)

        return (exitcode, output)
