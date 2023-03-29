import subprocess
from typing import Dict, List, Optional

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
from tempfile import TemporaryFile

from core.tools.base import tool, BaseToolSet, ToolScope, SessionGetter
from logger import logger


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
                    stdout=fp,
                )

                tracer = self.sessions.get(session) or SyscallTracer(process.pid)
                self.sessions[session] = tracer

                tracer.attach()
                tracer.wait_until_stop_or_exit()

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
    o = Terminal().execute("echo 1; sleep 3", lambda: ("", None))
    print(o)
