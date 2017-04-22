
from pathlib import Path
from subprocess import Popen, PIPE
import shutil

GIT_CMD = shutil.which('git')


def _communicate(proc, timeout=15):
    try:
        outs, errs = proc.communicate(timeout=timeout)
    except TimeoutExpired:
        proc.kill()
        outs, errs = proc.communicate()
    return outs.decode("utf-8"), errs.decode("utf-8")
