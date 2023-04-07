from pathlib import Path

from env import settings


def verify(func):
    def wrapper(*args, **kwargs):
        try:
            filepath = args[0].filepath
        except:
            raise Exception("This tool doesn't have filepath. Please check your code.")
        if not str(Path(filepath).resolve()).startswith(
            str(Path(settings["PLAYGROUND_DIR"]).resolve())
        ):
            return "You can't access file outside of playground."
        return func(*args, **kwargs)

    return wrapper
