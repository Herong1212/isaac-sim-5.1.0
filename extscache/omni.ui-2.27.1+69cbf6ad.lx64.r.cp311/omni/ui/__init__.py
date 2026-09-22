## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
"""
Omni::UI
--------

Omni::UI is Omniverse's UI toolkit for creating beautiful and flexible graphical user interfaces
in the Kit extensions. Omni::UI provides the basic types necessary to create rich extensions with
a fluid and dynamic user interface in Omniverse Kit. It gives a layout system and includes
widgets for creating visual components, receiving user input, and creating data models. It allows
user interface components to be built around their behavior and enables a declarative flavor of
describing the layout of the application. Omni::UI gives a very flexible styling system that
allows deep customizing the final look of the application.

Typical Example
---------------

Typical example to create a window with two buttons:

.. code-block::

    import omni.ui as ui

    _window_example = ui.Window("Example Window", width=300, height=300)

    with _window_example.frame:
        with ui.VStack():
            ui.Button("click me")

            def move_me(window):
                window.setPosition(200, 200)

            def size_me(window):
                window.width = 300
                window.height = 300

            ui.Button("Move to (200,200)", clicked_fn=lambda w=self._window_example: move_me(w))
            ui.Button("Set size (300,300)", clicked_fn=lambda w=self._window_example: size_me(w))

Detailed Documentation
----------------------

Omni::UI is shipped with the developer documentation that is written with Omni::UI. For detailed documentation, please
see `omni.example.ui` extension. It has detailed descriptions of all the classes, best practices, and real-world usage
examples.

Layout
------

* Arrangement of elements
    * :class:`omni.ui.CollapsableFrame`
    * :class:`omni.ui.Frame`
    * :class:`omni.ui.HStack`
    * :class:`omni.ui.Placer`
    * :class:`omni.ui.ScrollingFrame`
    * :class:`omni.ui.Spacer`
    * :class:`omni.ui.VStack`
    * :class:`omni.ui.ZStack`

* Lengths
    * :class:`omni.ui.Fraction`
    * :class:`omni.ui.Percent`
    * :class:`omni.ui.Pixel`

Widgets
-------

* Base Widgets
    * :class:`omni.ui.Button`
    * :class:`omni.ui.Image`
    * :class:`omni.ui.Label`

* Shapes
    * :class:`omni.ui.Circle`
    * :class:`omni.ui.Line`
    * :class:`omni.ui.Rectangle`
    * :class:`omni.ui.Triangle`

* Menu
    * :class:`omni.ui.Menu`
    * :class:`omni.ui.MenuItem`

* Model-View Widgets
    * :class:`omni.ui.AbstractItemModel`
    * :class:`omni.ui.AbstractValueModel`
    * :class:`omni.ui.CheckBox`
    * :class:`omni.ui.ColorWidget`
    * :class:`omni.ui.ComboBox`
    * :class:`omni.ui.RadioButton`
    * :class:`omni.ui.RadioCollection`
    * :class:`omni.ui.TreeView`

* Model-View Fields
    * :class:`omni.ui.FloatField`
    * :class:`omni.ui.IntField`
    * :class:`omni.ui.MultiField`
    * :class:`omni.ui.StringField`

* Model-View Drags and Sliders
    * :class:`omni.ui.FloatDrag`
    * :class:`omni.ui.FloatSlider`
    * :class:`omni.ui.IntDrag`
    * :class:`omni.ui.IntSlider`

* Model-View ProgressBar
    * :class:`omni.ui.ProgressBar`

* Windows
    * :class:`omni.ui.ToolBar`
    * :class:`omni.ui.Window`
    * :class:`omni.ui.Workspace`

* Web
    * :class:`omni.ui.WebViewWidget`

"""

# Importing TextureFormat here explicitly to maintain backwards compatibility
from omni.gpu_foundation_factory import TextureFormat, RpResource

from ._ui import *
from .color_utils import color
from .constant_utils import constant
from .style_utils import style
from .url_utils import url
from .workspace_utils import dump_workspace
from .workspace_utils import restore_workspace
from .workspace_utils import compare_workspace
from .extension import UIPreferencesExtension

def add_to_namespace(module=None, module_locals=locals()):
    class AutoRemove:
        def __init__(self):
            self.__key = module.__name__.split(".")[-1]
            module_locals[self.__key] = module

        def __del__(self):
            module_locals.pop(self.__key, None)

    if not module:
        return

    return AutoRemove()


# Add the static methods to Workspace
setattr(Workspace, "dump_workspace", dump_workspace)
setattr(Workspace, "restore_workspace", restore_workspace)
setattr(Workspace, "compare_workspace", compare_workspace)

del dump_workspace
del restore_workspace
del compare_workspace


def set_shade(shade_name: str | None = None):
    color.set_shade(shade_name)
    constant.set_shade(shade_name)
    url.set_shade(shade_name)

def set_menu_delegate(delegate: MenuDelegate):
    """
    Set the default delegate to use it when the item doesn't have a
    delegate.
    """
    MenuDelegate.set_default_delegate(delegate)
