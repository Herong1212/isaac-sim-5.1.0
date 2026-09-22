import os
import glob
import hashlib
import shutil
import platform
import subprocess
import threading
import contextlib
from functools import lru_cache, wraps
from time import monotonic
from pathlib import Path

from typing import Tuple

import omni.ext
import carb
import carb.settings
import carb.tokens


def _get_setting(path, default=None):
    setting = carb.settings.get_settings().get(path)
    return setting if setting is not None else default


def _info(s):
    carb.log_info(s)


_print_lock = threading.Lock()


def _print_mt(s):
    _print(s, threadsafe=True)


def _print(s, threadsafe=False):
    if threadsafe:
        with _print_lock:
            print(f"[omni.kit.registry.nucleus] [tid: {threading.get_ident()}] {s}")
    else:
        print(f"[omni.kit.registry.nucleus]: {s}")


def _error(s):
    carb.log_error(s)


def _warn(s):
    carb.log_warn(s)


_info_exec_time_indent = 0


def info_exec_time(operation_name=None):
    def _print_exec_time(f):
        @wraps(f)
        def wrap(*args, **kw):
            global _info_exec_time_indent
            ts = monotonic()
            _info_exec_time_indent += 1
            result = f(*args, **kw)
            te = monotonic()
            name = operation_name if operation_name else f"func:{f.__name__}"
            _info("{}> {} took: {:2.4f}s".format("-" * _info_exec_time_indent, name, te - ts))
            _info_exec_time_indent -= 1
            return result

        return wrap

    return _print_exec_time


@lru_cache()
def is_windows():
    return platform.system().lower() == "windows"


def run_process(args) -> Tuple[int, str]:
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf8")
    std, _ = p.communicate()
    return p.returncode, std


@contextlib.contextmanager
def change_envvar(name: str, value: str):
    """Change environment variable for the execution block and then revert it back.

    This function is a context manager.

    Example:

    .. code-block:: python

        with omni.repo.man.change_envvar("PYTHONPATH", "C:/hello"):
            print(os.environ.get("PYTHONPATH"))

    Args:
        name (str): Env var to change.
        value: new value
    """

    old_value = os.environ.get(name, None)
    os.environ[name] = value
    try:
        yield
    finally:
        if old_value is None:
            del os.environ[name]
        else:
            os.environ[name] = old_value


def get_dict_value_by_path(d, path, default=None):
    """Get value from dict by / seprated path, e.g. get_dict_value_by_path(d, "a/b/c")"""
    for key in path.split("/"):
        if not isinstance(d, dict):
            return default
        d = d.get(key)
        if d is None:
            return default
    return d


def new_dict_with_filter(src, keys):
    """Create new dict with only keys from src dict. Keys are / seprated path, e.g.

    ```py

        assert new_dict_with_filter({"a": {"b": 1, "c":3}}, ["a/c"]) == {'a': {'c': 3}}

    ```
    """

    dst = {}
    for path in keys:
        d1 = src
        d2 = dst
        path = path.split("/")
        for i, key in enumerate(path):
            is_last = i == len(path) - 1
            d1 = d1.get(key)
            if d1 is None:
                break
            if not is_last and not isinstance(d1, dict):
                break

            if is_last:
                d2[key] = d1
            else:
                d2 = d2.setdefault(key, {})

    return dst


def get_extension_name(ext_id: str) -> str:
    """Convert 'omni.foo-tag-1.2.3' to 'omni.foo-tag'"""
    a, b, *_ = ext_id.split("-") + [""]

    def _looks_like_version(s):
        return s.split(".")[0].isdigit()

    if b and not _looks_like_version(b):
        return f"{a}-{b}"
    return a


def get_ext_fullname_version(ext_id):
    """For omni.foo-tag-1.2.3 return omni.foo-tag, 1.2.3"""
    name = get_extension_name(ext_id)
    version = ext_id[len(name) + 1 :]
    return name, version


def get_ext_name_tag_version(ext_id):
    """For omni.foo-tag-1.2.3 return omni.foo, tag, 1.2.3"""
    fullname, version = get_ext_fullname_version(ext_id)
    parts = fullname.split("-", maxsplit=1)
    return parts[0], parts[1] if len(parts) > 1 else None, version


def _remove_authors_from_extension_config(ext_config_path):
    import re

    _info(f"Found '{ext_config_path}' to remove authors in")

    # Find and replace:
    content = None
    with open(ext_config_path, "r") as f:
        content = f.read()

    changed = False

    # Replace actual setting with regexp:
    p = re.compile(r"authors\"?\s*?=\s*?\[[\s\S]*?\]")
    if p.search(content):
        _info(f"Replacing authors in: '{ext_config_path}'")
        content = p.sub('authors = ["NVIDIA"]', content)
        changed = True

    # Remove repository
    p = re.compile(r"repository\s*?=\s*?\"[\s\S]*?\"")
    if p.search(content):
        _info(f"Removing repository in: '{ext_config_path}'")
        content = p.sub('repository = ""', content)
        changed = True

    if changed:
        _info(f"writing {ext_config_path}")
        with open(ext_config_path, "w") as f:
            f.write(content)


def remove_authors_from_extension(ext_path):
    """Remove authors from extension.toml or kit file.

    Files are modified in place.
    """
    if os.path.isfile(ext_path):
        _remove_authors_from_extension_config(ext_path)
    else:
        for p in ["extension.toml", "config/extension.toml"]:
            ext_config_path = os.path.join(ext_path, p)
            if os.path.exists(ext_config_path):
                _remove_authors_from_extension_config(ext_config_path)


def mask_password(password):
    return "*" * len(password) if password else ""


@info_exec_time()
def zip_extension(ext_id: str, ext_path: str, output_folder: str):
    _print_mt(f"zipping: '{ext_path}' into '{output_folder}'")
    archive_path = omni.ext.pack_extension(ext_id, ext_path, output_folder)
    _print_mt(f"created zip: '{archive_path}'")
    return archive_path


def md5_file(path):
    with open(path, "rb") as f:
        file_hash = hashlib.md5()
        chunk = f.read(8192)
        while chunk:
            file_hash.update(chunk)
            chunk = f.read(8192)
    return file_hash.hexdigest()


def sha1_str(s):
    return hashlib.sha1(s.encode()).hexdigest()


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


def sha1_folder(path, exclude_files=set(), hash_length=16) -> str:
    hash = hashlib.sha1()
    for p in glob.glob(f"{path}/**", recursive=True):
        if not os.path.isfile(p) or os.path.basename(p) in exclude_files:
            continue
        if Path(p).parts[-2] == "__pycache__":
            continue
        hash_file(p, hash)
    return hash.hexdigest()[:hash_length]


def sha1_file(path, hash_length=16) -> str:
    hash = hashlib.sha1()
    hash_file(path, hash)
    return hash.hexdigest()[:hash_length]


def is_file_deletable(file_path):
    # folder needs write and execute permission
    if os.access(os.path.dirname(file_path), os.W_OK | os.X_OK):
        try:
            # file can be opened for append
            with open(file_path, "a") as f:
                return f.writable()
        except OSError:
            pass
    return False


def check_dir_deletable(dir_path, error_fn=_error):
    for root, _, files in os.walk(dir_path):
        for file in files:
            filename = os.path.join(root, file)
            if not is_file_deletable(filename):
                error_fn(f"Skipping deletion of: {dir_path}. Can't delete file (no permissions / locked): {filename}")
                return False
    return True


def rmpath(path, log_errors=True):
    def onerror(func, path, exc_info):
        # Is the error an access error? Try to change readonly to writeable and try again.
        # Helps with "Access is denied" on windows.
        import stat

        if not os.access(path, os.W_OK):
            os.chmod(path, stat.S_IWUSR)
            func(path)
        else:
            raise

    error_fn = _error if log_errors else _info

    try:
        if os.path.isfile(path):
            if not is_file_deletable(path):
                error_fn(f"Can't delete file (no permissions / locked): {path}")
                return False
            os.remove(path)
        else:
            if os.path.exists(path):
                # Traverse all files and see if anything is locked - can't be deleted. That would happen if other app
                # runs and holds dll or other file locked.
                if not check_dir_deletable(path, error_fn=error_fn):
                    return False

                # try remove configs first explicitly. That will invalidate extension. If futher file deletion fails,
                # we would know that extension is corrupted in the cache.
                for p in ["extension.toml", "config/extension.toml"]:
                    cfg_path = os.path.join(path, p)
                    if os.path.exists(cfg_path):
                        os.remove(cfg_path)

                # Remove everything now
                shutil.rmtree(path, onerror=onerror)
        return True
    except Exception as e:
        _error(f"Failed to remove cache path {path}: {e}")
        return False


def dir_has_any_files(path: str) -> bool:
    for entry in os.scandir(path):
        if entry.is_file():
            return True
        elif dir_has_any_files(entry.path):
            return True
    return False
