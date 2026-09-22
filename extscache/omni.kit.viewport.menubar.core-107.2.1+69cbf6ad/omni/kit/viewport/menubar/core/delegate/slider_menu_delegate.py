# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["SliderMenuDelegate"]

from typing import Optional, Union
import omni.ui as ui

from .abstract_widget_menu_delegate import AbstractWidgetMenuDelegate


class SliderMenuDelegate(AbstractWidgetMenuDelegate):
    """A menu delegate that creates slider within a viewport menubar."""

    def __init__(
        self,
        model: Optional[ui.AbstractValueModel] = None,
        min: Union[float, int, None] = None,  # noqa: A002, PLW0622
        max: Union[float, int, None] = None,  # noqa: A002, PLW0622
        tooltip: Optional[str] = None,
        width: int = 300,
        slider_class: Union[ui.FloatSlider, ui.IntSlider] = ui.FloatSlider,
        show_checkbox_if_min: bool = False,
        default_value_on: Union[float, int, None] = None,
        enabled: bool = True,
        reserve_status: bool = False,
        has_reset: bool = False,
        step: Union[float, int, None] = None,
    ):
        """
        Constructor.

        kwargs:
            model (Optional[ui.AbstractValueModel]): Slider data model, defaults to None.
            min (Union[float, int, None]): Slider min value, defaults to None.
            max (Union[float, int, None]): Slider max value, defaults to None.
            tooltip (Optional[str]): Delegate tooltip, defaults to None.
            width (int): Slider width, in pixels, defaults to 270. Deprecated.
            slider_class (Union[ui.FloatSlider, ui.IntSlider]): Slider class, defaults to ui.FloatSlider.
            show_checkbox_if_min (bool): Show checkbox instead of slider if value equals min, defaults to False.
            default_value_on (Union[float, int, None]): When checkbox is ON, value to display in slider, defaults to None.
            enabled (bool): Delegate enabled state, defaults to True.
            reserve_status (bool): Show additional space before widgets, defaults to False. Used to align with other menu items which have status icon.
            has_reset (bool): Show reset button, defaults to False.
            step (Union[float, int, None]): Slider step value defaults to None means use slider default.
        """
        super().__init__(model=model, enabled=enabled, reserve_status=reserve_status, has_reset=has_reset)
        self.__space = 5
        self.__slider_width = 90
        self.__min = min
        self.__max = max
        self.__tooltip = tooltip or ""
        self.__slider_class = slider_class
        self.__show_checkbox_if_min = show_checkbox_if_min
        self.__default_value_on = default_value_on
        self.__slider = None
        self.__step = step
        self.__checkbox = None
        self.__slider_container = None

    def __del__(self):
        self.destroy()

    def destroy(self) -> None:
        """Release resources."""
        self._model = None

    def build_widget(self, item: ui.MenuHelper) -> None:
        """
        Build a label and a slider.

        Args:
            item (ui.MenuHelper): Menu item.
        """
        ui.Label(item.text, tooltip=self.__tooltip, style_type_name_override="Menu.Item.Label")

        ui.Spacer(width=self.__space)

        with ui.ZStack(content_clipping=True, width=0):
            if self.__show_checkbox_if_min and self.__min is not None:
                self.__checkbox = ui.CheckBox(width=self.__slider_width, visible=False)
                self.__checkbox.model.add_value_changed_fn(self.__on_checkbox_changed)

            self.__slider_container = ui.VStack(width=self.__slider_width)
            with self.__slider_container:
                ui.Spacer()

                kwargs = {"height": 0}
                use_drag = False

                min_value, max_value = self.__min, self.__max
                # If only one of min/max ws provided, warn as the slider might be odd
                if (min_value is None) != (max_value is None):
                    import carb
                    carb.log_warn("SliderMenuDelegate with only one of min/max provided")

                if min_value is not None and self.__max is not None:
                    kwargs["min"] = min_value
                    kwargs["max"] = max_value
                    if max_value - min_value > 100:
                        use_drag = True
                else:
                    use_drag = True
                    if min_value is not None:
                        kwargs["min"] = min_value
                    if max_value is not None:
                        kwargs["max"] = max_value

                if self.__step is not None:
                    kwargs["step"] = self.__step
                elif (self.__slider_class == ui.FloatSlider) and (min_value is not None) and (max_value is not None):
                    kwargs["step"] = self.calculate_step(min_value, max_value, None)

                kwargs["precision"] = 3

                if use_drag:
                    if self.__slider_class == ui.FloatSlider:
                        slider_class = ui.FloatDrag
                    if self.__slider_class == ui.IntSlider:
                        slider_class = ui.IntDrag
                else:
                    slider_class = self.__slider_class

                self.__slider = slider_class(self._model, **kwargs)
                if self.__show_checkbox_if_min and self.__min is not None:
                    self.__slider.model.add_value_changed_fn(self.__on_slider_changed)

                    value = self.__slider.model.as_float
                    if value == self.__min:
                        self.__checkbox.visible = True
                        self.__slider.visible = False

                ui.Spacer()

    @property
    def min(self) -> Union[float, int]:  # noqa: A002, A003, PLW0622
        """Slider min value"""
        return self.__min

    @min.setter
    def min(self, value: Union[float, int]) -> None:  # noqa: A002, A003, PLW0622
        self.__min = value
        if self.__slider:
            self.__slider.min = value

    @property
    def max(self) -> Union[float, int]:  # noqa: A002, A003, PLW0622
        """Slider max value"""
        return self.__max

    @max.setter
    def max(self, value: Union[float, int]) -> None:  # noqa: A002, A003, PLW0622
        self.__max = value
        if self.__slider:
            self.__slider.max = value

    def calculate_step(self, min: float, max: float, slider: ui.Widget) -> float:  # noqa: A002, PLW0622
        """
        Calculate step by min/max.

        Args:
            min (fl0at): Min value.
            max (float): Max value.
            slider (ui.Widget): Slider widget.
        """
        # TODO: Flag to normalize against slider.computed_width
        import math
        exponent = math.floor(math.log10(abs(max - min)))
        return (10 ** exponent) / 100

    def set_range(self, min: float, max: float) -> None:  # noqa: A002, PLW0622
        """
        Set slider value range.

        Args:
            min (fl0at): Min value.
            max (float): Max value.
        """
        self.__min, self.__max = min, max
        slider = self.__slider
        if slider:
            slider.min = self.__min
            slider.max = self.__max
            # Auto compute step based on range and width
            if self.__step is None:
                slider.step = self.calculate_step(min, max, slider)

    def __on_checkbox_changed(self, model: ui.AbstractValueModel) -> None:
        if model.as_bool:
            self.__checkbox.visible = False
            self.__slider.visible = True
            if self.__default_value_on is not None:
                self.__slider.model.set_value(self.__default_value_on)

    def __on_slider_changed(self, model: ui.AbstractValueModel) -> None:
        if self.__min is not None and model.as_float == self.__min:
            self.__checkbox.visible = True
            self.__checkbox.model.set_value(False)
            self.__slider.visible = False
