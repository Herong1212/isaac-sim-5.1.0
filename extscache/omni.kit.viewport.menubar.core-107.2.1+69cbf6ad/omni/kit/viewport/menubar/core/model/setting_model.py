# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["SettingModel"]

import abc
from typing import Any, Union

import carb.dictionary
import carb.settings
import omni.kit.app
import omni.kit.commands
import omni.ui as ui

from .reset_button import ResetHelper

PERSISTENT_SETTINGS_PREFIX = "/persistent"


class SettingModel(ui.AbstractValueModel):
    """
    A data model for simple scalar/POD carb.settings

    Taken from omni.kit.widget.settings

    TODO: Put it to omni.ui
    """

    def __init__(
        self,
        setting_path: str,
        draggable: bool = False,
        min: Union[float, int, None] = None,  # noqa: A002, PLW0622
        max: Union[float, int, None] = None,  # noqa: A002, PLW0622
    ):
        """
        Constructor.

        Args:
            setting_path (str): Path to carb setting.

        Keyword Args:
            draggable (bool): Widget that model bind to can be dragged, defaults to False.
            min (Union[float, int, None]): Min value, defaults to None.
            max (Union[float, int, None]): Max value. defaults to None.
        """
        ui.AbstractValueModel.__init__(self)
        self._settings = carb.settings.get_settings()
        self._path = setting_path
        self.draggable = draggable
        self.min = min
        self.max = max
        self.initialValue = None
        self._reset_button = None
        self._editing = False

        self._update_setting = omni.kit.app.SettingChangeSubscription(self._path, self._on_change)

    @property
    def path(self) -> str:
        """Path to carb setting"""
        return self._path

    def _on_change(owner, value, event_type) -> None:  # noqa: N805
        if event_type == carb.settings.ChangeEventType.CHANGED:
            owner._on_dirty()
            if owner._editing is False:
                owner.on_value_changed()

    def begin_edit(self) -> None:
        """Called when the user starts editing."""
        self._editing = True
        ui.AbstractValueModel.begin_edit(self)
        self.initialValue = self._settings.get(self._path)

    def end_edit(self) -> None:
        """Called when the user finishes editing."""
        ui.AbstractValueModel.end_edit(self)
        omni.kit.commands.execute(
            "ChangeSetting", path=self._path, value=self._settings.get(self._path), prev=self.initialValue
        )
        self.on_value_changed()
        self._editing = False

    def _cast_to_type(self, value: Any, dflt: Any, type_cast: type = None):
        if type_cast is None:
            # Incoming default ay be None, in which case we need to rely on proper type of value
            type_check = dflt if dflt is not None else value
            if isinstance(type_check, float):
                type_cast = float
            # bool needs to be tested before int as bool is a subclass of int from historical reasons
            elif isinstance(type_check, bool):
                type_cast = bool
            elif isinstance(type_check, int):
                type_cast = int
            elif isinstance(type_check, str):
                type_cast = str

        try:
            value = type_cast(value) if (value is not None) else dflt
        except (ValueError, TypeError):
            value = dflt
        return value

    def get_value_as_string(self) -> str:
        """Get value as string"""
        return self._cast_to_type(self._settings.get(self._path), '', str)

    def get_value_as_float(self) -> float:
        """Get value as float"""
        return self._cast_to_type(self._settings.get(self._path), 0.0, float)

    def get_value_as_bool(self) -> bool:
        """Get value as bool"""
        return self._cast_to_type(self._settings.get(self._path), False, bool)

    def get_value_as_int(self) -> int:
        """Get value as int"""
        return self._cast_to_type(self._settings.get(self._path), 0, int)

    def set_value(self, value: Any) -> None:
        """
        Set value.

        Args:
            value (Any): Value to set.
        """
        # Value may come in as a string, so needs to be casted to the correct type
        # 'old_value' should have the correct type info.
        old_value = self._settings.get(self._path)
        value = self._cast_to_type(value, old_value)
        if old_value == value:
            return

        if not self.draggable:
            omni.kit.commands.execute("ChangeSetting", path=self._path, value=value, prev=old_value)
            self.on_value_changed()
            self._on_dirty()
        else:
            self._settings.set(self._path, value)

    def on_value_changed(self) -> None:
        """Callback when value changed"""
        return

    def _on_dirty(self):
        # Tell the widgets that the model value has changed
        self._value_changed()

    def destroy(self) -> None:
        """Release resources."""
        self._reset_button = None
        self._update_setting = None


class AbstractSettingModelWithDefault(SettingModel, ResetHelper):
    """
    Base class for setting model with default value and reset supported.
    """
    def __init__(
        self,
        setting_path: str,
        draggable: bool = False,
        min: Union[float, int, None] = None,  # noqa: A002, PLW0622
        max: Union[float, int, None] = None,  # noqa: A002, PLW0622
    ):
        """
        Constructor.

        Args:
            setting_path (str): Path to carb setting.

        Keyword Args:
            draggable (bool): Widget that model bind to can be dragged, defaults to False.
            min (Union[float, int, None]): Min value, defaults to None.
            max (Union[float, int, None]): Max value, defaults to None.
        """
        SettingModel.__init__(self, setting_path, draggable=draggable, min=min, max=max)
        ResetHelper.__init__(self)

    def on_value_changed(self):
        """Refresh reset button when value changed"""
        self._update_reset_button()

    @abc.abstractmethod
    def get_default(self) -> Any:
        """Get default value"""
        return

    @abc.abstractmethod
    def restore_default(self) -> None:
        """Restore default value"""
        return

    def get_value(self) -> Any:
        """Get current value from carb setting"""
        return self._settings.get(self._path)


class SettingModelWithDefaultPath(AbstractSettingModelWithDefault):
    """
    A setting model to get default value from carb setting path and save/load persistent.

    Setting path starts with PERSISTENT_SETTINGS_PREFIX to save/load current value
    Setting path without PERSISTENT_SETTINGS_PREFIX for default value when reset
    """
    def __init__(
        self,
        setting_path: str,
        draggable: bool = False,
        min: Union[float, int, None] = None,  # noqa: A002, PLW0622
        max: Union[float, int, None] = None,  # noqa: A002, PLW0622
    ):
        """
        Constructor.

        Args:
            setting_path (str): Path to carb setting.

        Keyword Args:
            draggable (bool): Widget that model bind to can be dragged, defaults to False.
            min (Union[float, int, None]): Min value, defaults to None.
            max (Union[float, int, None]): Max value, defaults to None.
        """
        self._default_path = setting_path
        persistent_path = PERSISTENT_SETTINGS_PREFIX + setting_path

        settings = carb.settings.get_settings()
        carb.settings.get_settings().set_default(persistent_path, settings.get(setting_path))
        super().__init__(persistent_path, draggable=draggable, min=min, max=max)

    def restore_default(self) -> None:
        """Restore default value"""
        default_value = self.get_default()
        self._settings.set(self._path, default_value)

    def get_default(self):
        """Get Default value"""
        return self._settings.get(self._default_path)


class SettingModelWithDefaultValue(AbstractSettingModelWithDefault):
    """
    A setting model with default value.
    """
    def __init__(
        self,
        setting_path: str,
        default_value: Any,
        draggable: bool = False,
        min: Union[float, int, None] = None,  # noqa: A002, PLW0622
        max: Union[float, int, None] = None,  # noqa: A002, PLW0622
    ):
        """
        Constructor.

        Args:
            setting_path (str): Path to carb setting.
            default_value (Any): Default value.

        Keyword Args:
            draggable (bool): Widget that model bind to can be dragged, defaults to False.
            min (Union[float, int, None]): Min value, defaults to None.
            max (Union[float, int, None]): Max value, defaults to None.
        """
        self.__default_value = default_value
        super().__init__(setting_path, draggable=draggable, min=min, max=max)

    def get_default(self):
        """Get default value"""
        return self.__default_value

    def restore_default(self) -> None:
        """Restore default value"""
        self._settings.set(self._path, self.__default_value)
