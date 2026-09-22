import glob
import hashlib
import os
import shutil
import sys
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import List, Tuple

import carb
import carb.settings
import carb.tokens
import omni.ext

from .gitlab import is_running_in_gitlab
from .teamcity import is_running_in_teamcity

_settings_iface = None


class Colors:
    """ANSI colors to change TTY font color. Using the high intensity colors, they look nicer"""

    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"


class TestReturnCode:
    """Return codes used by omni.kit.test"""

    UNIT_TESTS_FAILED = 13
    UNIT_TEST_TIMEOUT = 15
    EXT_TESTS_FAILED = 21


def get_setting(path, default=None):
    global _settings_iface
    if not _settings_iface:
        _settings_iface = carb.settings.get_settings()
    setting = _settings_iface.get(path)
    return setting if setting is not None else default


def get_local_timestamp():
    return (
        # ':' is not path-friendly on windows
        datetime.now()
        .isoformat(timespec="seconds")
        .replace(":", "-")
    )


@lru_cache()
def _split_argv() -> Tuple[List[str], List[str]]:
    """Return list of argv before `--` and after (processed and unprocessed)"""
    try:
        index = sys.argv.index("--")
        return list(sys.argv[:index]), list(sys.argv[index + 1 :])
    except ValueError:
        return list(sys.argv), []


def get_argv() -> List[str]:
    return _split_argv()[0]


def get_unprocessed_argv() -> List[str]:
    return _split_argv()[1]


def resolve_path(path, root) -> str:
    path = carb.tokens.get_tokens_interface().resolve(path)
    if not os.path.isabs(path):
        path = os.path.join(root, path)
    return os.path.normpath(path)


@lru_cache()
def _get_passed_test_output_path():
    return get_setting("/exts/omni.kit.test/testOutputPath", default=None)


@lru_cache()
def get_global_test_output_path():
    """Get global extension test output path. It is shared for all extensions."""

    # If inside test process, we have testoutput for actual extension, just go on folder up:
    output_path = _get_passed_test_output_path()
    if output_path:
        return os.path.abspath(os.path.join(output_path, ".."))

    # If inside ext test runner process, use setting:
    output_path = carb.tokens.get_tokens_interface().resolve(
        get_setting("/exts/omni.kit.test/testExtOutputPath", default="")
    )
    output_path = os.path.abspath(output_path)
    return output_path


@lru_cache()
def get_test_output_path():
    """Get local extension test output path. It is unique for each extension test process."""
    output_path = _get_passed_test_output_path()

    # If not passed we probably not inside test process, default to global
    if not output_path:
        return get_global_test_output_path()

    output_path = os.path.abspath(carb.tokens.get_tokens_interface().resolve(output_path))
    return output_path


@lru_cache()
def get_ext_test_id() -> str:
    return str(get_setting("/exts/omni.kit.test/extTestId", default=""))


@lru_cache()
def is_etm_run() -> bool:
    return bool(os.getenv("ETM_ACTIVE"))


def cleanup_folder(path):
    try:
        for p in glob.glob(f"{path}/*"):
            if os.path.isdir(p):
                if omni.ext.is_link(p):
                    omni.ext.destroy_link(p)
                else:
                    shutil.rmtree(p)
            else:
                os.remove(p)
    except Exception as exc:  # pylint: disable=broad-except
        carb.log_warn(f"Unable to clean up files: {path}: {exc}")


def ext_id_to_fullname(ext_id: str) -> str:
    return omni.ext.get_extension_name(ext_id)


def clamp(value, min_value, max_value):
    return max(min(value, max_value), min_value)


@lru_cache()
def is_running_on_ci():
    return is_running_in_teamcity() or is_running_in_gitlab()


def call_git(args, cwd=None):
    import subprocess

    cmd = ["git"] + args
    carb.log_verbose("run process: {}".format(cmd))
    try:
        res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        if res.returncode != 0:
            carb.log_warn(f"Error running process: {cmd}. Result: {res}. Stderr: {res.stderr}")
        return res
    except FileNotFoundError:
        carb.log_warn("Failed calling git")
    except PermissionError:
        carb.log_warn("No permission to execute git")


def _hash_file_impl(path, hash, as_text):
    mode = "r" if as_text else "rb"
    encoding = "utf-8" if as_text else None
    with open(path, mode, encoding=encoding) as f:
        while True:
            data = f.readline().encode("utf-8") if as_text else f.read(65536)
            if not data:
                break
            hash.update(data)


def hash_file(path, hash):
    # Try as text first, to avoid CRLF/LF mismatch on both platforms
    try:
        return _hash_file_impl(path, hash, as_text=True)
    except UnicodeDecodeError:
        return _hash_file_impl(path, hash, as_text=False)


def sha1_path(path, hash_length=16) -> str:
    exclude_files = ["extension.gen.toml"]
    hash = hashlib.sha1()
    if os.path.isfile(path):
        hash_file(path, hash)
    else:
        for p in glob.glob(f"{path}/**", recursive=True):
            if not os.path.isfile(p) or os.path.basename(p) in exclude_files:
                continue
            if Path(p).parts[-2] == "__pycache__":
                continue
            hash_file(p, hash)
    return hash.hexdigest()[:hash_length]


def sha1_list(strings: List[str], hash_length=16) -> str:
    hash = hashlib.sha1()
    for s in strings:
        hash.update(s.encode("utf-8"))
    return hash.hexdigest()[:hash_length]
