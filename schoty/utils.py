import re
from pathlib import Path
import shutil
from subprocess import PIPE, Popen

GIT_CMD = shutil.which('git')


def _communicate(proc, timeout=15):
    try:
        outs, errs = proc.communicate(timeout=timeout)
    except TimeoutExpired:
        proc.kill()
        outs, errs = proc.communicate()
    return outs.decode("utf-8"), errs.decode("utf-8")


def _render_cmd(cmd):
    cmd_tmp = []
    for el in cmd:
        if isinstance(el, Path):
            el = el.as_posix()
        cmd_tmp.append(el)

    return ' '.join(cmd_tmp)


def _check_output(proc, timeout=15, cmd=None):
    outs, errs = _communicate(proc, timeout)
    outs = outs + errs
    for line in outs.splitlines():
        if re.match('^fatal: .*', line):
            if cmd is None:
                raise RuntimeError(outs)
            else:
                raise RuntimeError(_render_cmd(cmd) + '\n' + outs)
    else:
        return outs
