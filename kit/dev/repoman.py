import os
import time


os.environ["TIME_STARTED"] = str(int(time.time()))  # setting the time the process started.
os.environ["REPOMAN_START_TIME"] = str(int(time.time()))  # setting the time the process started.

import sys
import io
import contextlib

import packmanapi
from repoman_bootstrapper import repoman_bootstrap

REPO_ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../..")
REPO_DEPS_FILE = os.path.join(REPO_ROOT, "deps/repo-deps.packman.xml")


def replace_python_process():
    """Replace python version with 3.11.

    We currently run with packman that is on 3.10, but we need 3.11. We can replace using "[repo.python_executable]" feature of repo_man,
    but it adds more overhead. It starts and configures the tool first and then runs again.
    """

    if sys.version_info.minor == 11:
        return

    import platform

    operating_system = platform.system().lower()
    arch = platform.machine()
    if arch == "AMD64":
        arch = "x86_64"

    platform_host = f"{operating_system}-{arch}"
    is_windows = operating_system == "windows"
    python_path = packmanapi.install("python", f"3.11.10+nv3-{platform_host}")["python"]
    python_exec = python_path + "/" + ("python" if is_windows else "python")

    if is_windows:
        import subprocess
        try:
            r = subprocess.run([python_exec] + sys.argv)
            sys.exit(r.returncode)
        except Exception as e:
            print(e)
            sys.exit(1)
    else:
        os.execv(python_exec, [python_exec] + sys.argv)


def bootstrap():
    """
    Bootstrap all omni.repo modules.

    Pull with packman from repo.packman.xml and add them all to python sys.path to enable importing.
    """
    replace_python_process()
    with contextlib.redirect_stdout(io.StringIO()):
        deps = packmanapi.pull(REPO_DEPS_FILE)
    for dep_path in deps.values():
        if dep_path not in sys.path:
            sys.path.append(dep_path)


if __name__ == "__main__":
    repoman_bootstrap()
    bootstrap()
    import omni.repo.man
    omni.repo.man.main(REPO_ROOT)
