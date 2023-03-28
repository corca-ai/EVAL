import subprocess
from ptrace.debugger import (
    PtraceDebugger,
    ProcessExit,
    ProcessSignal,
    NewProcessEvent,
    ProcessExecution,
)
from ptrace.func_call import FunctionCallOptions
from ptrace.tools import signal_to_exitcode


def debug(pid):
    debugger = PtraceDebugger()

    print("Attach the running process %s" % pid)
    process = debugger.addProcess(pid, False)

    process.syscall()
    exitcode = 0
    while True:
        if not debugger:
            break

        try:
            event = process.waitSyscall()
        except ProcessExit as event:
            print(event)
            if event.exitcode is not None:
                exitcode = event.exitcode
            continue
        except ProcessSignal as event:
            print(event)
            event.process.syscall(event.signum)
            exitcode = signal_to_exitcode(event.signum)
            continue
        except NewProcessEvent as event:
            continue
        except ProcessExecution as event:
            continue

        syscall = process.syscall_state.event(
            FunctionCallOptions(
                write_types=False,
                write_argname=False,
                string_max_length=300,
                replace_socketcall=True,
                write_address=False,
                max_array_count=20,
            )
        )
        if syscall:
            print(syscall.name)

        process.syscall()

    process.detach()
    debugger.quit()

    return exitcode


def execute(commands: str) -> str:
    try:
        process = subprocess.Popen(
            commands,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        debug(process.pid)
        process.wait()
        output = process.stdout.read().decode()
    except Exception as e:
        output = str(e)

    return output


print(execute("python3 -m http.server 8000"))
