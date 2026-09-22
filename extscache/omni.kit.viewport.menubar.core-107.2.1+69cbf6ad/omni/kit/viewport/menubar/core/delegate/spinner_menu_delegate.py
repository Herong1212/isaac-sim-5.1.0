# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["SpinnerMenuDelegate"]

from typing import Union, Optional
import omni.ui as ui
from omni.ui import color as cl

SPINNER_STYLE = {
    "Spinner.Field": {"background_color": 0, "color": cl.viewport_menubar_light},
    "Spinner.Field:disabled": {"color": cl.viewport_menubar_medium},
    "Spinner.Arrow": {"background_color": cl.viewport_menubar_light},
    "Spinner.Arrow:disabled": {"background_color": cl.viewport_menubar_medium},
}


class SpinnerMenuDelegate(ui.MenuDelegate):
    """
    A menu delegate that creates a spinner within a viewport menubar.

    Use slider instead of spinner if omni.kit.widget.spinner not enabled.
    """

    def __init__(
        self,
        model: Optional[ui.AbstractValueModel] = None,
        tooltip: Optional[str] = None,
        width: Optional[ui.Length] = None,
        height: ui.Length = 0,
        min: Union[float, int, None] = None,  # noqa: PLW0622, A002
        max: Union[float, int, None] = None,  # noqa: PLW0622, A002
        step: Union[float, int] = 1,
        enabled: bool = True,
        text: bool = True,
        icon_name: Optional[str] = None,
        icon_width: ui.Length = 30,
        icon_height: ui.Length = 30,
        use_in_menubar: bool = False,
        precision: Optional[int] = 1,
    ):
        """
        Constructor.

        Args:
            model (Optional[ui.AbstractValueModel]): Spinner data model, defaults to None
            tooltip (Optional[str]): Spinner tooltip, defaults to None.
            width (Optional[ui.Length]): Delegate width, defaults to None means ui.Fraction(1).
            height (ui.Length): Delegate Height, defaults to 0 means auto height.
            min (Union[float, int, None]): Spinner min value, defaults to None.
            max (Union[float, int, None]): Spinner max value, defaults to None.
            step (Union[float, int]): Spinner step value, defaults to 1.
            enabled (bool): Delegate starts enabled, defaults to True.
            text (bool): Show text before spinner, defaults to True.
            icon_name (Optional[str]): Name of additional icon to be displayed before text, defaults to None means no additional icon.
            icon_width (ui.Length): Width of additional icon. Only available when icon_name is valid, defaults to 30 pixels.
            icon_height (ui.Length): Height of additional icon. Only available when icon_name is valid, defaults to 30 pixels.
            use_in_menubar (bool): Show menu item in menu bar, defaults to False.
            precision (Optional[int]): Data precision, defaults to 1.
        """
        super().__init__()
        self.__width = width if width is not None else ui.Fraction(1)
        self.__height = height
        self.__spinner_width = 60
        self.__model = model
        self.__tooltip = tooltip or ""
        self._min = min
        self._max = max
        self._step = step
        self._precision = precision

        self.__enabled = enabled
        self.__frame: Optional[ui.Widget] = None
        self.__spinner = None

        self.__text = text
        self.__icon_name = icon_name
        self.__icon_width = icon_width
        self.__icon_height = icon_height
        self.__use_in_menubar = use_in_menubar

    def __del__(self):
        self.destroy()

    def destroy(self) -> None:
        """Release resources."""
        self.__model = None

    @property
    def enabled(self) -> bool:
        """Delegate enabled state."""
        return self.__enabled

    @enabled.setter
    def enabled(self, value) -> None:
        self.__enabled = value
        if self.__frame:
            self.__frame.enabled = value
            self.__frame.enabled = value

    def build_item(self, item: ui.MenuItem) -> None:
        """
        Build a spinner.

        Use slider instead if omni.kit.widget.spinner not enabled.

        Args:
            item (ui.MenuItem): Menu item.
        """
        extra_kwargs = {"style_type_name_override": "Menu.Item"} if not self.__use_in_menubar else {}
        self.__frame = ui.Frame(width=self.__width, enabled=self.__enabled, **extra_kwargs)
        with self.__frame:
            with ui.HStack(height=self.__height):
                if self.__icon_name:
                    ui.ImageWithProvider(style_type_name_override="Menu.Item.Icon", tooltip=self.__tooltip, name=self.__icon_name, width=self.__icon_width, height=self.__icon_height)
                if self.__text:
                    ui.Label(item.text, tooltip=self.__tooltip, style_type_name_override="Menu.Item.Label")
                with ui.VStack(width=self.__spinner_width):
                    ui.Spacer()

                    try:
                        from omni.kit.widget.spinner import FloatSpinner

                        self.__spinner = FloatSpinner(
                            self.__model, min=self._min, max=self._max, step=self._step, style=SPINNER_STYLE
                        )
                    except ModuleNotFoundError:
                        args = {"height": 0}
                        if self.__model:
                            args['model'] = self.__model
                        if self._min is not None:
                            args['min'] = self._min
                        if self._max is not None:
                            args['max'] = self._max
                        if self._step is not None:
                            args['step'] = self._step
                        if self._precision is not None:
                            args["precision"] = self._precision

                        # Enable draggable to show correct value when dragging in slider
                        if hasattr(self.__model, "draggable"):
                            self.__model.draggable = True
                        if self._min is not None and self._max is not None:
                            self.__spinner = ui.FloatSlider(**args)
                        else:
                            self.__spinner = ui.FloatDrag(**args)

                    ui.Spacer()
                ui.Spacer(width=5)

        self.__spinner.enabled = self.__enabled
