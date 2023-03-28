import subprocess
import ptrace.debugger
import signal
import sys


def debug(pid):
    debugger = ptrace.debugger.PtraceDebugger()

    print("Attach the running process %s" % pid)
    process = debugger.addProcess(pid, False)
    # process is a PtraceProcess instance
    print("IP before: %#x" % process.getInstrPointer())

    print("Execute a single step")
    process.singleStep()
    # singleStep() gives back control to the process. We have to wait
    # until the process is trapped again to retrieve the control on the
    # process.
    process.waitSignals(signal.SIGTRAP)
    print("IP after: %#x" % process.getInstrPointer())

    process.detach()
    debugger.quit()


def execute(commands: str) -> str:
    """Run commands and return final output."""
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


print(execute("echo hi"))
