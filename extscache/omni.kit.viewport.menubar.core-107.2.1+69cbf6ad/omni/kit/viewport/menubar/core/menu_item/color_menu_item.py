import asyncio
from typing import List, Optional

import carb.settings
import omni.kit.app
import omni.ui as ui

from ..delegate.color_menu_delegate import ColorMenuDelegate
from ..model.list_model import ColorModel


__all__ = ["AbstractColorMenuItem", "FloatArraySettingColorMenuItem"]


class AbstractColorMenuItem(ui.MenuItem):
    """
    Base menu item to show/change colors.
    """
    def __init__(self, colors: List[float], name: str = "", default: Optional[List[float]] = None, has_reset: bool = False):
        """
        Constructor.

        Args:
            colors (List[float]): Colors attached to this menu item.

        Keyword Args:
            name (str): Text of menu item. Default empty string.
            default Optional[List[float]. Default colors when reset. Default None.
            has_reset (bool): Show reset button, defaults to False.
        """
        self.model = ColorModel(colors, default=default, on_color_changed_fn=self.on_color_changed)
        super().__init__(name, delegate=ColorMenuDelegate(model=self.model, has_reset=has_reset), hide_on_click=False)

    def destroy(self) -> None:
        """Release resources."""
        if self.model:
            self.model.destroy()
            self.model = None

    def on_color_changed(self, colors: List[float]) -> None:
        """
        Callback when colors changed.

        Args:
            colors colors: List[float]: Changed colors.
        """
        return

    def reset(self) -> None:
        """Callback when reset colors"""
        return


class FloatArraySettingColorMenuItem(AbstractColorMenuItem):
    """ A menu item to show/change colors from carb.settings"""
    def __init__(self, setting_path: str, default: List[float], name: str = "", start_index: int = 0, has_reset: bool = False):
        """
        Constructor.

        Args:
            setting_path (str): Colors setting path.

        Keyword Args:
            default Optional[List[float]. Default colors when reset, defaults to None.
            name (str): Menu item text, defaults to "".
            start_index (int): Index of this color in data array from setting path, defaults to 0.
            has_reset (bool): Show reset button, defaults to False.
        """
        self._settings = carb.settings.get_settings()
        self.__path = setting_path
        self.__start_index = start_index
        self.__default = default
        self.__color_size = len(default)

        # Future used to collapse carb-settings change events for individual color components
        self.__future = None

        # Fill in default color if the setting key does not exists at all
        color_array = self._settings.get(self.__path)
        if color_array is None:
            color_array = [0] * (start_index + self.__color_size)
            for index, value in enumerate(self.__default):
                color_array[start_index + index] = value
            self._settings.set(self.__path, color_array)

        self.__color_subs = []
        self.__create_color_subs()

        super().__init__(self._get_color(), default=self.__default, name=name, has_reset=has_reset)

    def __del__(self):
        self.destroy()

    def destroy(self) -> None:
        """Release resources"""
        self.__color_subs.clear()
        super().destroy()

    def __get_color_paths(self):
        for i in range(self.__start_index, self.__start_index + self.__color_size):
            yield f"{self.__path}/{i}"

    def __create_color_subs(self):
        # Create the carb-settings event watchers on the individual color components
        self.__color_subs = [omni.kit.app.SettingChangeSubscription(path, self.__on_change) for path in self.__get_color_paths()]

    def __on_change(self, item: carb.dictionary.Item, event_type: carb.settings.ChangeEventType) -> None:
        # Since the value is a color (3/4 elements), batch the model updated into a single call

        # Skip any event thats not a change
        if event_type != carb.settings.ChangeEventType.CHANGED:
            return

        # Check if an operation is already waiting to run
        if self.__future and not self.__future.done():
            return

        # Create the Future to signal the model is up to date
        self.__future = asyncio.Future()

        async def update_model():
            if not self.__future.done():
                self.__future.set_result(True)
            colors = self._get_color()
            if colors != self.model.colors:
                self.model.colors = colors
        asyncio.ensure_future(update_model())

    def _get_color(self) -> List[float]:
        return [self._settings.get(path) for path in self.__get_color_paths()]

    def on_color_changed(self, colors: List[float]) -> None:
        """
        Callback when colors changed.

        Args:
            colors colors: List[float]: Changed colors.
        """
        setting_colors = self._settings.get(self.__path)
        if setting_colors is None:
            # TODO: create default here? or required be filled outside
            return

        if setting_colors[self.__start_index : self.__start_index + self.__color_size] != colors:
            for index, value in enumerate(colors):
                setting_colors[self.__start_index + index] = value

            # Kill the change subscription before the carb.settings.set call.
            # This is to optimize the array change, which will delete and recreate elemetns individually.
            # This is particularly noticable for large arrays (1000+), but since colors are arrays of 4 do it always.
            try:
                self.__color_subs = None
                self._settings.set(self.__path, setting_colors)
            finally:
                self.__create_color_subs()

    def reset(self) -> None:
        """Callback when reset colors"""
        self.model.restore_default()
