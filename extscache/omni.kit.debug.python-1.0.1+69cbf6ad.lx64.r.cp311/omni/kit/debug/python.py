"""Provides debugging tools for Python scripts within the Omniverse Kit
framework by integrating with the debugpy module."""

__all__: list[str] = [
    "_wait_for_client",
    "trigger_breakpoint",
    "is_attached",
    "enable_logging",
    "get_listen_address",
]

import os
import sys
import carb.tokens
import carb.settings
import omni.ext
import omni.kit.app
import omni.kit.pipapi

# Try import to allow documentation build without debugpy
try:
    import debugpy  # type: ignore
except ModuleNotFoundError:
    pass


def _print(msg: str) -> None:
    print(f"[omni.kit.debug.python] {msg}")


def _wait_for_client() -> None:
    """Waits for a debugger client to connect before continuing execution."""
    _print("Waiting for debugger to connect...")
    debugpy.wait_for_client()


def trigger_breakpoint() -> None:
    """Invokes a breakpoint in the code.

    This function waits for the debugger to connect before invoking
    a breakpoint.
    """
    _wait_for_client()
    debugpy.breakpoint()


def is_attached() -> bool:
    """Checks if a debugger client is currently connected.

    Returns:
        bool: True if a debugger client is connected, False otherwise.
    """
    return debugpy.is_client_connected()


def enable_logging() -> None:
    """Enables logging for the debug sessions.

    Logs are saved to the path specified in the environment's token settings.
    """
    path = carb.tokens.get_tokens_interface().resolve("${logs}")
    _print(f"Enabled logging to '{path}'")
    debugpy.log_to(path)


class Extension(omni.ext.IExt):
    """A class for managing the startup of a Python debugger extension.

    This class inherits from omni.ext.IExt and overrides the on_startup method
    to configure and initialize the debugpy server based on user-defined
    settings. It handles the setup of logging, server mode (listen or connect),
    host, port, and optional client waiting or immediate breakpoint triggering.
    The class encapsulates functionality to start or connect to a debugging
    session and integrates with the larger ecosystem of debugging tools
    provided by the debugpy module.
    """

    _listen_address = None

    @classmethod
    def get_listen_address(cls) -> str | None:
        """Returns the address on which the debugger is configured to listen.

        Returns:
            The listen address as a string or None if not set
        """
        return cls._listen_address

    def on_startup(self) -> None:
        """Starts up the debugging extension.

        This method sets up the environment for the debugpy server, including
        configuring logging, setting the python executable for debugging, and
        establishing the connection method based on extension settings.

        It can optionally wait for the debugger client to connect and/or
        break at the first line of code after the server is ready.
        """

        # Set the environment variable so it applies to the current Python
        # process on any platform
        os.environ["PYDEVD_DISABLE_FILE_VALIDATION"] = "1"

        settings = carb.settings.get_settings()

        host = settings.get("/exts/omni.kit.debug.python/host")
        port = settings.get("/exts/omni.kit.debug.python/port")
        debugpy_logging = settings.get(
            "/exts/omni.kit.debug.python/debugpyLogging")
        wait_for_client = settings.get(
            "/exts/omni.kit.debug.python/waitForClient")
        break_ = settings.get("/exts/omni.kit.debug.python/break")
        mode = settings.get("/exts/omni.kit.debug.python/mode")

        if debugpy_logging:
            enable_logging()

        # Start debugging server
        python_exe = "python.exe" if sys.platform == "win32" else "bin/python3"
        python_cmd = sys.prefix + "/" + python_exe
        debugpy.configure(python=python_cmd)

        try:
            if mode == "listen":
                Extension._listen_address = debugpy.listen((host, port))
                _print(f"Listening python debugger on: "
                       f"{Extension._listen_address}")
            elif mode == "connect":
                debugpy.connect((host, port))
                _print(f"Connected python debugger on: {host}:{port}")
        except (OSError, RuntimeError) as e:
            _print(f"Error running python debugger: {e}")

        if wait_for_client:
            _wait_for_client()

        if break_:
            trigger_breakpoint()

    def on_shutdown(self) -> None:
        """Shuts down the debugging extension.

        This method cleans up the environment for the debugpy server, including
        disabling logging and disconnecting from any active debugging session.
        """
        debugpy.log_to("")
        debugpy.disconnect()
        del os.environ["PYDEVD_DISABLE_FILE_VALIDATION"]


def get_listen_address() -> str | None:
    """Returns the address on which the debugger is configured to listen.

    Returns:
        The listen address as a string or None if not set
    """
    return Extension.get_listen_address()
