from .extension import ViewportWindowExtension

# Expose our public classes for from omni.kit.viewport.window import ViewportWindow
__all__ = ['ViewportWindow', 'get_viewport_window_instances', 'set_viewport_window_default_style']

from .window import ViewportWindow

def get_viewport_window_instances(usd_context_name: str | None = ''):
    """
    Get all known ViewportWindow instances, optionally filtering with a UsdContext name.

    Args:
        usd_context_name (str, None): An optional argument to limit enumeration to ViewportWindows attached to a
            specific UsdContext.
    Returns:
        An iterable object for enumerating all found ViewportWindow instances.
    """
    return ViewportWindow.get_instances(usd_context_name)


def set_viewport_window_default_style(style: dict, overwrite: bool = False, usd_context_name: str | None = '', apply: bool = True):
    """
    Set the default style for all ViewportWindows, optionally filtering based on the UsdContext the ViewportWindow
    is attached to.

    Args:
        style (dict): An omni.ui style dictionary
        overwrite (bool): Whether to overwrite any existing style or augment it.
        usd_context_name (str, None): An optional argument to limit application to ViewportWindows attached to a
            specific UsdContext.
        apply (bool): Whether to apply the style to existing ViewportWindows, or not.
    """
    return ViewportWindow.set_default_style(style, overwrite, usd_context_name, apply)
