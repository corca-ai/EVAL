from typing import Optional

from ptrace.debugger import (
    PtraceDebugger,
    PtraceProcess,
    ProcessExit,
    ProcessSignal,
    NewProcessEvent,
    ProcessExecution,
)
from ptrace.syscall import PtraceSyscall
from ptrace.func_call import FunctionCallOptions
from ptrace.tools import signal_to_exitcode


class SyscallTracer:
    def __init__(self, pid: int):
        self.debugger: PtraceDebugger = PtraceDebugger()
        self.pid: int = pid
        self.process: PtraceProcess = None

    def should_stop(self, syscall: Optional[PtraceSyscall]) -> bool:
        if syscall is None:
            return False
        if syscall.name.startswith("wait"):
            return True
        return False

    def attach(self):
        self.process = self.debugger.addProcess(self.pid, False)

    def detach(self):
        self.process.detach()
        self.debugger.quit()

    def wait_until_stop_or_exit(self) -> Optional[int]:
        exitcode = None
        while True:
            if not self.debugger:
                break

            try:
                self.process.syscall()
                event = self.process.waitSyscall()
            except ProcessExit as event:
                if event.exitcode is not None:
                    exitcode = event.exitcode
                continue
            except ProcessSignal as event:
                event.process.syscall(event.signum)
                exitcode = signal_to_exitcode(event.signum)
                continue
            except NewProcessEvent as event:
                continue
            except ProcessExecution as event:
                continue

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
            if self.should_stop(syscall):
                self.detach()
                break

        return exitcode
