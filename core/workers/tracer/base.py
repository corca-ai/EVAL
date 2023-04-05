import os
import time
import subprocess
from datetime import datetime
from typing import Callable, Literal, Optional, Union, Tuple
from abc import ABC, abstractmethod

PipeType = Union[Literal["stdout"], Literal["stderr"]]
OnOutputHandler = Callable[[PipeType, str], None]


class BaseTracer(ABC):
    def __init__(
        self,
        process: subprocess.Popen,
        on_output: OnOutputHandler = lambda: None,
    ):
        self.process: subprocess.Popen = process
        self.on_output: OnOutputHandler = on_output
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

    @abstractmethod
    def wait_until_stop_or_exit(self) -> Tuple[Optional[int], str]:
        pass
