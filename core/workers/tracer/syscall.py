import signal
import subprocess
from typing import Optional, Tuple

from ptrace.debugger import (
    NewProcessEvent,
    ProcessExecution,
    ProcessExit,
    ProcessSignal,
    PtraceDebugger,
    PtraceProcess,
)
from ptrace.func_call import FunctionCallOptions
from ptrace.syscall import PtraceSyscall
from ptrace.tools import signal_to_exitcode
from .base import BaseTracer, OnOutputHandler


class SyscallTimeoutException(Exception):
    def __init__(self, pid: int, *args) -> None:
        super().__init__(f"deadline exceeded while waiting syscall for {pid}", *args)


class SyscallTracer(BaseTracer):
    def __init__(
        self,
        process: subprocess.Popen,
        timeout: int = 30,
        on_output: OnOutputHandler = lambda: None,
    ):
        super().__init__(process, on_output)
        self.debugger: PtraceDebugger = PtraceDebugger()
        self.pid: int = process.pid
        self.timeout: int = timeout
        self.process: PtraceProcess = None

    def is_waiting(self, syscall: PtraceSyscall) -> bool:
        if syscall.name.startswith("wait"):
            return True
        return False

    def attach(self):
        self.process = self.debugger.addProcess(self.pid, False)

    def detach(self):
        self.process.detach()
        self.debugger.quit()

    def set_timer(self, timeout: int):
        def handler(signum, frame):
            raise SyscallTimeoutException(self.process.pid)

        signal.signal(signal.SIGALRM, handler)
        signal.alarm(timeout)

    def reset_timer(self):
        signal.alarm(0)

    def wait_syscall_with_timeout(self, timeout: int):
        self.set_timer(timeout)
        self.process.waitSyscall()
        self.reset_timer()

    def wait_until_stop_or_exit(self) -> Tuple[Optional[int], str]:
        self.process.syscall()
        exitcode = None
        reason = ""
        while True:
            if not self.debugger:
                break

            try:
                self.wait_syscall_with_timeout(self.timeout)
            except ProcessExit as event:
                if event.exitcode is not None:
                    exitcode = event.exitcode
                continue
            except ProcessSignal as event:
                event.process.syscall(event.signum)
                exitcode = signal_to_exitcode(event.signum)
                reason = event.reason
                continue
            except NewProcessEvent as event:
                continue
            except ProcessExecution as event:
                continue
            except Exception as e:
                reason = str(e)
                break

            syscall = self.process.syscall_state.event(
                FunctionCallOptions(
                    write_types=False,
                    write_argname=False,
                    string_max_length=300,
                    replace_socketcall=True,
                    write_address=False,
                    max_array_count=20,
                )
            )

            self.process.syscall()

            if syscall is None:
                continue

            if syscall.result:
                continue

        self.reset_timer()

        return exitcode, reason
