"""Pip Omniverse Kit API

Module to enable usage of ``pip install`` in Omniverse Kit environment. It wraps ``pip install`` calls and reroutes package installation into
user specified environment folder.

Package folder is selected from config string at path: `/app/omni.kit.pipapi/archiveDirs` and added into :mod:`sys.path`.
"""
__all__ = ["ExtensionManagerPip", "install", "call_pip", "remove_archive_directory", "add_archive_directory"]
import carb
import carb.profiler
import carb.settings
import carb.tokens
import omni.ext
import omni.kit.app
import importlib
import logging
import typing
import os
import json
import sys
from contextlib import contextmanager
from pathlib import Path
import functools

logger = logging.getLogger(__name__)


DEFAULT_ENV_PATH = "../../target-deps/pip3-envs/default"
CACHE_FILE_NAME = ".install_cache.json"
USE_INTERNAL_PIP = False
ALLOW_ONLINE_INDEX_KEY = "/exts/omni.kit.pipapi/allowOnlineIndex"

_user_env_path = ""

# pip additional dirs/links (pip install --find-links)
_archive_dirs = set()

_install_check_ignore_version = True


# print() instead of carb.log_info when this env var is set:
_debug_log = bool(os.getenv("OMNI_KIT_PIPAPI_DEBUG", default=False))

_attempted_to_upgrade_pip = False

_settings_iface = None

_started = False

# Temporary helper-decorator for profiling
def profile(f=None, mask=1, zone_name=None, add_args=True):
    def profile_internal(f):
        @functools.wraps(f)
        def wrapper(*args, **kwds):
            if zone_name is None:
                active_zone_name = f.__name__
            else:
                active_zone_name = zone_name
            if add_args:
                active_zone_name += str(args) + str(kwds)
            carb.profiler.begin(mask, active_zone_name)
            try:
                r = f(*args, **kwds)
            finally:
                carb.profiler.end(mask)
            return r
        return wrapper
    if f is None:
        return profile_internal
    else:
        return profile_internal(f)


def _get_setting(path, default=None):
    # It can be called at import time during doc generation, enable that `_started` check:
    if not _started:
        return default

    global _settings_iface
    if not _settings_iface:
        _settings_iface = carb.settings.get_settings()
    setting = _settings_iface.get(path)
    return setting if setting is not None else default


def _log_info(s):
    s = f"[omni.kit.pipapi] {s}"
    if _debug_log:
        print(s)
    else:
        carb.log_info(s)


def _log_error(s):
    logger.error(s)


@functools.lru_cache()
def _initialize():
    env_path = _get_setting("/exts/omni.kit.pipapi/envPath")
    env_path = carb.tokens.get_tokens_interface().resolve(env_path)
    path = Path(env_path).resolve()
    if not path.exists():
        path.mkdir(parents=True)
    global _user_env_path
    _user_env_path = str(path)
    import sys

    global _install_check_ignore_version
    _install_check_ignore_version = _get_setting("/exts/omni.kit.pipapi/installCheckIgnoreVersion", default=True)

    global _attempted_to_upgrade_pip
    _attempted_to_upgrade_pip = not _get_setting("/exts/omni.kit.pipapi/tryUpgradePipOnFirstUse", default=False)

    global _archive_dirs
    for archive_dir in _get_setting("/exts/omni.kit.pipapi/archiveDirs", default=[]):
        add_archive_directory(archive_dir)

    sys.path.append(_user_env_path)
    _log_info(f"Python UserEnvPath: {_user_env_path}")
    _load_cache()


@contextmanager
def _change_envvar(name: str, value: str):
    """Change environment variable for the execution block and then revert it back.

    This function is a context manager.

    Example:

    .. code-block:: python

        with _change_envvar("PYTHONPATH", "C:/hello"):
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


def call_pip(args: typing.List[str], surpress_output: bool = False) -> int:
    """Call pip with given arguments.

    Args:
        args (list): list of arguments to pass to pip
        surpress_output (bool): if True, surpress pip output
    Returns:
            int: return code of pip call"""
    if USE_INTERNAL_PIP:
        try:
            from pip import main as pipmain
        except:
            from pip._internal import main as pipmain
        return pipmain(args)
    else:
        import subprocess

        with _change_envvar("PYTHONPATH", _user_env_path):
            python_exe = "python.exe" if sys.platform == "win32" else "bin/python3"
            cmd = [sys.prefix + "/" + python_exe, "-m", "pip"] + args
            print("calling pip install: {}".format(" ".join(cmd)))

            # Capture output and print it only if pip install failed:
            p = subprocess.Popen(cmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
            output, _ = p.communicate()
            output = output.decode(errors="replace").replace("\r\n", "\n").replace("\r", "\n")
            message = f"pip install returned {p.returncode}, output:\n{output}"
            if p.returncode != 0 and not surpress_output:
                print(message)
            else:
                carb.log_info(message)

            return p.returncode


def add_archive_directory(path: str, root: str = None):
    """
    Add pip additional dirs/links (for pip install --find-links).
    """
    global _archive_dirs
    path = carb.tokens.get_tokens_interface().resolve(path)
    if not os.path.isabs(path) and root is not None:
        path = os.path.join(root, path)
    path = os.path.normcase(path)
    _log_info(f"Add archive dir: '{path}'")
    _archive_dirs.add(path)


def remove_archive_directory(path: str):
    """
    Remove pip additional dirs/links.
    """
    global _archive_dirs
    _archive_dirs.remove(path)


def _try_import(module: str, log_error: bool = False):
    try:
        importlib.import_module(module)
    except ImportError as e:
        if log_error:
            logger.error(f"Failed to import python module {module}. Error: {e}")
        return False
    return True


@profile
def install(
    package: str,
    module: str = None,
    ignore_import_check: bool = False,
    ignore_cache: bool = False,
    version: str = None,
    use_online_index: bool = True,
    surpress_output: bool = False,
    extra_args: typing.List[str] = None,
) -> bool:
    """
    Install pacakage using pip into user specified env path. Install calls for particular package name persistently cache
    to avoid overhead for future calls when package is already installed. Cache is stored in the `.install_cache.json` file in the user specified env path folder.

    Args:
        package(str): Package name to install. It is basically a command to pip install, it can include version and other flags.
        module(str): Module name to import, by default module assumed to be equal to package.
        ignore_import_check(bool, optional): If ``True`` ignore attempt to import module and call to ``pip`` anyway - can be slow.
        ignore_cache(bool, optional): If ``True`` ignore caching and call to ``pip`` anyway - can be slow.
        version (str, optional): Package version.
        use_online_index(bool, optional): If ``True`` and package can't be found in any of archive directories try to use default pip index.
        surpress_output(bool, optional): If ``True`` pip process output to stdout and stderr will be surpressed, as well as warning when install failed.
        extra_args(List[str], optional): a list of extra arguments to pass to the Pip process

    Returns:
        ``True`` if installation was successfull.
    """
    _initialize()

    # Support both install("foo==1.2.3") and install("foo", version="1.2.3") syntax
    if "==" not in package and version:
        package = f"{package}=={version}"

    # By default module == package
    if module is None:
        module = package.split("==")[0]

    # Trying to import beforehand saves a lot of time, because pip run takes long time even if package is already installed.
    if not ignore_import_check and _try_import(module):
        return True

    # We have our own cache of install() calls saved into separate json file, that is the fastest early out.
    if not ignore_cache and _is_in_cache(package):
        return True

    # Use now pkg_resources module to check if it was already installed. It checks that it was installed by other means,
    # like just zipping packages and adding it to sys.path somewhere. That allows to check for package name instead of
    # module (e.g. 'Pillow' instead of 'PIL'). We need to call explicitly on it to initialize and gather packages every time.
    # Import it here instead of on the file root because it has long import time.
    import pkg_resources

    pkg_resources._initialize_master_working_set()
    installed = {pkg.key for pkg in pkg_resources.working_set}
    package_name = package.lower()
    if _install_check_ignore_version:
        package_name = package_name.split("==")[0]
    if package_name in installed:
        return True

    # We are about to try installing, lets upgrade pip first (it will be done only once). Flag protects from recursion.
    global _attempted_to_upgrade_pip
    if not _attempted_to_upgrade_pip:
        _attempted_to_upgrade_pip = True
        install("--upgrade --no-index pip", ignore_import_check=True, use_online_index=False)

    installed = False

    common_args = ["--isolated", "install", "--target=" + _user_env_path]
    if extra_args:
        common_args.extend(extra_args)
    common_args.extend(package.split())

    for archive_dir in _archive_dirs:
        _log_info(f"Attempting to install '{package}' from local acrhive: '{archive_dir}'")
        rc = call_pip(
            common_args + ["--no-index", f"--find-links={archive_dir}"],
            surpress_output=(surpress_output or use_online_index),
        )
        if rc == 0:
            importlib.invalidate_caches()
            installed = True
            break

    if not installed and use_online_index:
        allow_online = _get_setting(ALLOW_ONLINE_INDEX_KEY, default=True)
        if allow_online:
            _log_info(f"Attempting to install '{package}' from online index")
            rc = call_pip(common_args, surpress_output=surpress_output)
            if rc == 0:
                importlib.invalidate_caches()
                installed = True
        else:
            _log_error(
                f"Attempting to install '{package}' from online index, while '{ALLOW_ONLINE_INDEX_KEY}' is set to false. That prevents from accidentally going to online index. Enable it if it is intentional."
            )

    if installed and not ignore_import_check:
        installed = _try_import(module, log_error=True)

    if installed:
        _log_info(f"'{package}' was installed successfully.")
        _add_to_cache(package)
    else:
        if not surpress_output:
            logger.warning(f"'{package}' failed to install.")

    return installed


_cached_install_calls_file = None
_cached_install_calls = {}


def _load_cache():
    global _cached_install_calls
    global _cached_install_calls_file
    _cached_install_calls_file = Path(_user_env_path, CACHE_FILE_NAME)
    try:
        with _cached_install_calls_file.open("r") as f:
            _cached_install_calls = json.load(f)
    except (IOError, ValueError):
        _cached_install_calls = {}


def _add_to_cache(package):
    _cached_install_calls[package] = True
    with _cached_install_calls_file.open("w") as f:
        json.dump(_cached_install_calls, f)


def _is_in_cache(package) -> bool:
    return package in _cached_install_calls


class ExtensionManagerPip(omni.ext.IExt):
    def on_startup(self, ext_id):
        # Hook in extension manager in "before extension enable" events if extension specifies "python/pipapi" config key.
        manager = omni.kit.app.get_app().get_extension_manager()
        self._hook = manager.get_hooks().create_extension_state_change_hook(
            ExtensionManagerPip.on_before_ext_enabled,
            omni.ext.ExtensionStateChangeType.BEFORE_EXTENSION_ENABLE,
            ext_dict_path="python/pipapi",
            hook_name="python.pipapi",
        )
        global _started
        _started = True

    def on_shutdown(self):
        self._hook = None

    @staticmethod
    @profile(zone_name="pipapi hook", add_args=False)
    def on_before_ext_enabled(ext_id: str, *_):
        ExtensionManagerPip._process_ext_pipapi_config(ext_id)

    @staticmethod
    def _process_ext_pipapi_config(ext_id: str):
        # Get extension config
        manager = omni.kit.app.get_app().get_extension_manager()
        d = manager.get_extension_dict(ext_id)
        pip_dict = d.get("python", {}).get("pipapi", {})

        # Add archive path. Relative path will be resolved relative to extension folder path.
        for path in pip_dict.get("archiveDirs", []):
            add_archive_directory(path, d["path"])

        # Allows module names to be different to package names
        modules = pip_dict.get("modules", [])

        # Allows extra PIP repositores to be added
        extra_args = []
        for line in pip_dict.get("repositories", []):
            extra_args.extend(["--extra-index-url", line])

        # Allow extra args
        extra_args += pip_dict.get("extra_args", [])

        # Allow to ignore import check
        ignore_import_check = pip_dict.get("ignore_import_check", False)

        # Install packages (requirements)
        use_online_index = pip_dict.get("use_online_index", False)

        requirements = pip_dict.get("requirements", [])
        if requirements:
            # If use_online_index is not set, just ignore those entries. Otherwise they hide slowdowns on pip access for local only
            # search, which is not really used currently.
            if not use_online_index:
                logger.warning(f"extension {ext_id} has a [python.pipapi] entry, but use_online_index=true is not set. It doesn't do anything and can be removed.")
                return

            for idx, line in enumerate(requirements):
                module = modules[idx] if len(modules) > idx else None
                install(line, module, extra_args=extra_args, use_online_index=use_online_index, ignore_import_check=ignore_import_check)
