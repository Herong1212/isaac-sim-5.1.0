import abc
from typing import Optional

import omni.ui as ui

from ..model.reset_button import ResetButton

MENU_ARROW_SIZE = 8


class AbstractWidgetMenuDelegate(ui.MenuDelegate):
    """Base class for menu delegate which has widgets"""
    def __init__(
        self,
        model: Optional[ui.AbstractItemModel] = None,
        width: Optional[ui.Length] = None,
        height: Optional[ui.Length] = None,
        enabled: bool = True,
        has_reset: bool = False,
        reserve_status: bool = False,
        use_in_menubar: bool = False,
        content_clipping: bool = True,
        visible: bool = True,
    ):
        """
        Constructor.

        Args:
            model (Optional[ui.AbstractItemModel]): Delegate data model, defaults to None.
            width (ui.Length): Delegate width, defaults to None means ui.Fraction(1).
            height (ui.Length): Delegate height, defaults to None means ui.Fraction(1).
            enabled (bool): Delegate enabled state, defaults to True.
            has_reset (bool): Show reset button, defaults to False.
            reserve_status (bool): Show additional space before widgets, defaults to False. Used to align with other menu items which have status icon.
            use_in_menubar (bool): Show delegate in menu bar, defaults to False.
            content_clipping (bool): Delegate content clipping, defaults to True.
            visible (bool): Delegate visibility, defaults to True.
        """
        super().__init__()
        self._model = model
        self.__width = width if width is not None else ui.Fraction(1)
        self.__height = height if height is not None else ui.Fraction(1)
        self.__enabled = enabled
        self.__has_reset = has_reset
        self.__reserve_status = reserve_status
        self.__use_in_menubar = use_in_menubar
        self.__content_clipping = content_clipping
        self.__visible = visible

        self.__frame: Optional[ui.Widget] = None
        self._reset_button: Optional[ResetButton] = None

    def destroy(self) -> None:
        """Override to release resources."""
        return

    def build_item(self, item: ui.MenuItem) -> None:
        """
        Callback to build menu item.

        Args:
            item (ui.MenuItem): Menu item.
        """
        extra_kwargs = {"style_type_name_override": "Menu.Item"} if not self.__use_in_menubar else {}
        self.__frame = ui.Frame(width=self.__width, enabled=self.__enabled, visible=self.__visible, **extra_kwargs)
        with self.__frame:
            with ui.HStack(height=self.__height, content_clipping=self.__content_clipping):
                if self.__reserve_status:
                    ui.Spacer(width=16)

                self.build_widget(item)

                if isinstance(item, ui.Menu):
                    # For menu, show arrow for children
                    ui.Spacer(width=10)
                    with ui.VStack(width=MENU_ARROW_SIZE / 2):
                        ui.Spacer()
                        ui.Triangle(
                            height=MENU_ARROW_SIZE,
                            alignment=ui.Alignment.RIGHT_CENTER,
                            style_type_name_override="MenuBar.Item.Triangle",
                        )
                        ui.Spacer()
                    ui.Spacer(width=3)

                if self.__has_reset:
                    ui.Spacer(width=4)
                    with ui.VStack(width=0):
                        ui.Spacer(height=2)
                        self._reset_button = ResetButton([self._model])
                        self._model.set_reset_button(self._reset_button)
                        ui.Spacer()

    @abc.abstractmethod
    def build_widget(self, item: ui.MenuHelper) -> None:
        """
        Callback to build widgets.

        Args:
            item (ui.MenuHelper): Menu item.
        """
        return

    @property
    def visible(self) -> bool:
        """Delegate visibility"""
        return self.__frame.visible if self.__frame else self.__visible

    @visible.setter
    def visible(self, value: bool) -> None:
        self.__visible = value
        if self.__frame:
            self.__frame.visible = value

    @property
    def enabled(self) -> bool:
        """Delegate enabled status"""
        return self.__enabled

    @enabled.setter
    def enabled(self, value) -> None:
        self.__enabled = value
        if self.__frame:
            self.__frame.enabled = value
