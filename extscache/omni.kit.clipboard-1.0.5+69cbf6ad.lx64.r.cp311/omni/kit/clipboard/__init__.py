
__all__ = ["copy", "paste"]

import omni.appwindow

def copy(value_str):
    """
    Platform-independent copy functionality.  Works for headless environments too.

    Args:
        value_str (str): String to put in the clipboard.
    """
    _app_window_factory = omni.appwindow.acquire_app_window_factory_interface()
    _app_window = _app_window_factory.get_default_window()
    _app_window.set_clipboard(value_str)

def paste():
    """
    Platform-independent paste functionality.  Works for headless environments too.

    Returns:
        str: Value pulled from the clipboard.
    """
    _app_window_factory = omni.appwindow.acquire_app_window_factory_interface()
    _app_window = _app_window_factory.get_default_window()
    return _app_window.get_clipboard()
