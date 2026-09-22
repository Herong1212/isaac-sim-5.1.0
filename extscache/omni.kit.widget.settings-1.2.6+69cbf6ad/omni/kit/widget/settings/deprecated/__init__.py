"""Settings Omniverse Kit API

Module to work with **Settings** in the Kit. It is built on top of ``carb.settings`` generic setting system.

Example code to create :class:`omni.kit.ui.Widget` to show and edit particular setting:

>>> import omni.kit.settings
>>> import omni.kit.ui
>>> widget = omni.kit.settings.create_setting_widget("some/path/to/param", SettingType.FLOAT)
"""

from .ui import SettingType, create_setting_widget, create_setting_widget_combo  # pragma: no cover
from .model import UiModel, get_ui_model                                         # pragma: no cover
