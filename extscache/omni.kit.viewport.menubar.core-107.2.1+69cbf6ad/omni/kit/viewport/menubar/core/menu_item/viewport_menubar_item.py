# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["ViewportMenubar"]

import asyncio
from dataclasses import dataclass, field, fields
from functools import partial
from typing import Dict, List, Optional

import omni.kit.app
import omni.ui as ui

from ..style import VIEWPORT_MENUBAR_STYLE
from ..viewport_menu_model import (
    AbstractViewportMenubarItem,
    AbstractViewportMenuItem,
    MenuDisplayStatus,
    ViewportMenuModel,
    pop_from_scope,
    push_to_scope,
)
from .viewport_menu_spacer import ViewportMenuSpacer


@dataclass
class MenubarContext:
    frame: ui.Frame = None
    background_rectangle: ui.Rectangle = None
    resize_future: asyncio.Future = None
    spacer_width: float = -1
    sub_menu_expand: Dict = field(default_factory=dict)

    def __init__(self, **kwargs):
        names = {f.name for f in fields(self)}
        for k, v in kwargs.items():
            if k in names:
                setattr(self, k, v)
        if not hasattr(self, "sub_menu_expand"):
            self.sub_menu_expand = {}


class ViewportMenubar(AbstractViewportMenubarItem):
    """Default viewport menubar, at the top of viewport."""
    def __init__(
        self,
        name: str = "",
        direction: ui.Direction = ui.Direction.LEFT_TO_RIGHT,
        spacing: ui.Length = 10,
        style: Optional[Dict] = None,
        background_visible: bool = False,
        visible_setting_path: Optional[str] = None,
    ):
        """
        Constructor.

        Args:
            name (str): Viewport menubar name.
            direction (ui.Direction): Layout direction of menu items in this menubar, defaults to ui.Direction.LEFT_TO_RIGHT.
            spacing (ui.Length): Spacing between items, defaults to 10 pixels.
            style (Optional[Dict]): Additional UI style, defaults to None.
            background_visible (bool): Show background for menu bar, defaults to False.
            visible_setting_path (Optional[str]): Setting path for menu bar visibility, defaults to None.
        """
        self._direction = direction
        self.__spacing = spacing
        self._style = VIEWPORT_MENUBAR_STYLE.copy()
        if style:
            self._style.update(style)
        self.__background_visible: bool = background_visible
        self.__show_separator: bool = False

        self.__context: Dict[int, MenubarContext] = {}

        self.__clip_size = {}
        self.__available_clip_levels = []
        self.__menu_items = []

        super().__init__(name=name, visible_setting_path=visible_setting_path)

    @property
    def visible(self) -> bool:
        """Menu bar visibility"""
        return self.visible_model.as_bool

    @visible.setter
    def visible(self, value: bool) -> None:
        old_value = self.visible_model.as_bool
        if old_value != value:
            self.visible_model.set_value(value)
            ViewportMenuModel()._item_changed(None)  # noqa PLW0212

    @property
    def background_visible(self) -> bool:
        """Menu bar background visibility"""
        return self.__background_visible

    @background_visible.setter
    def background_visible(self, visible: bool) -> None:
        self.__background_visible = visible
        for context in self.__context.values():
            context.background_rectangle.visible = self.__background_visible

    @property
    def style(self) -> Dict:
        """Menu bar UI style"""
        return self._style

    @property
    def spacing(self) -> ui.Length:
        """Spacing for menu item in this viewport menu bar"""
        return self.__spacing

    @spacing.setter
    def spacing(self, value: ui.Length) -> None:
        self.__spacing = value
        for context in self.__context.values():
            context.frame.rebuild()

    @property
    def show_separator(self) -> bool:
        """If show separator in viewport menu bar"""
        return self.__show_separator

    @show_separator.setter
    def show_separator(self, visible: bool) -> None:
        self.__show_separator = visible
        for context in self.__context.values():
            context.frame.rebuild()

    def destroy(self) -> None:
        """Release resources"""
        for context in self.__context.values():
            if context.resize_future and not context.resize_future.done():
                context.resize_future.cancel()
        self.__context = {}
        super().destroy()

    def build_fn(self, menu_items: List[AbstractViewportMenuItem], factory_args: Dict, content_clipping: bool = True):
        """
        Callback to build menu bar.

        Args:
            menu_items (List[AbstractViewportMenuItem]): Menu items.
            factory_args (dict): Argument related to viewport for this menu bar.

        Keyword Args:
            content_clipping (bool): Menubar content clipping, defaults to True.
        """
        # Using Frame with horizontal_clipping to prevent expanding of widgets when the menu bar is big
        extra_kwargs = {}
        if self._direction == ui.Direction.LEFT_TO_RIGHT:
            extra_kwargs = {"height": 0}
        elif self._direction == ui.Direction.TOP_TO_BOTTOM:
            extra_kwargs = {"width": 0}

        viewport_api_id = factory_args['viewport_api'].id

        self.__context[viewport_api_id] = MenubarContext()
        with ui.ZStack(style=self._style, height=0):
            self.__context[viewport_api_id].background_rectangle = ui.Rectangle(style_type_name_override="MenuBar.Window", visible=self.__background_visible)
            self.__context[viewport_api_id].frame = ui.Frame(horizontal_clipping=True, **extra_kwargs)
            with self.__context[viewport_api_id].frame:
                self._build_menubar(menu_items, factory_args, content_clipping=content_clipping)

        self.__menu_items = menu_items

        self.__available_clip_levels = [MenuDisplayStatus.EXPAND, MenuDisplayStatus.LABEL]
        self.__clip_size = {}
        for level in self.__available_clip_levels:
            self.__clip_size[level] = {}

        self.__context[viewport_api_id].frame.set_computed_content_size_changed_fn(partial(self.__resize_menubar, factory_args))

    def _build_menubar(self, menu_items: List[AbstractViewportMenuItem], factory_args: Dict, content_clipping=True):
        viewport_api_id = factory_args['viewport_api'].id

        # Filter out all hidden children
        visible_menu_items = [item for item in menu_items if item.visible_model.as_bool]
        # If all that remains is an empty list or a list of only ViewportMenuSpacer, then no menu
        if sum(1 for item in visible_menu_items if not isinstance(item, ViewportMenuSpacer)) == 0:
            self.__context[viewport_api_id].frame.clear()
            return

        with ui.Menu(direction=self._direction, menu_compatibility=False, content_clipping=content_clipping):
            first = True
            for item in visible_menu_items:
                if not first:
                    if self.__show_separator:
                        ui.Separator(
                            delegate=ui.MenuDelegate(
                                on_build_item=lambda _: ui.Line(
                                    width=0,
                                    alignment=ui.Alignment.H_CENTER,
                                    style_type_name_override="Menu.Separator",
                                )
                            )
                        )
                    else:
                        if self._direction == ui.Direction.LEFT_TO_RIGHT:
                            ui.Spacer(width=self.__spacing)
                        else:
                            ui.Spacer(height=self.__spacing)
                first = False
                item.build_fn(factory_args)
                if item.expand_model:
                    self.__context[viewport_api_id].sub_menu_expand[item] = item.expand_model.subscribe_value_changed_fn(lambda _, f=factory_args: self.__on_menu_expand_changed(f))

    def invalidate(self) -> None:
        """Callback to refresh menu bar"""
        return

    def __enter__(self):
        # Clean all existing child items
        # For multiple viewport window, menu contrainer may build multiple times
        # Make sure child items not duplicated
        # self._clean()

        push_to_scope(self)

    def __exit__(self, exc_type, exc_value, traceback):
        pop_from_scope()

    def __resize_menubar(self, factory_args: dict) -> None:
        viewport_api_id = factory_args['viewport_api'].id
        if self.__context[viewport_api_id].resize_future and not self.__context[viewport_api_id].resize_future.done():
            return

        self.__context[viewport_api_id].resize_future = asyncio.ensure_future(self.__resize_menubar_async(factory_args))

    async def __resize_menubar_async(self, factory_args: dict) -> None:
        try:
            viewport_api_id = factory_args['viewport_api'].id
        except ReferenceError as e:
            import carb
            carb.log_warn(f"Failed to get viewport_api_id: {e}")
            return
        menu_items = [item for item in self.__menu_items if item.visible_model.as_bool and not isinstance(item, ViewportMenuSpacer)]
        # We need to know spacer size to check if items need resize
        # Here use the default spacer item
        spacer_items = [item for item in self.__menu_items if isinstance(item, ViewportMenuSpacer) and item.order_model.as_int == 0]
        if spacer_items:
            spacer_item = spacer_items[0]
        else:
            return

        resize_again = True
        while resize_again:
            spacer_width = spacer_item.get_computed_width(factory_args)
            resize_again = False

            if spacer_width == 0:
                # No more space left, check if something need to contract
                resize_again = self.__check_contract(menu_items, factory_args)
            elif spacer_width < self.__context[viewport_api_id].spacer_width or self.__context[viewport_api_id].spacer_width < 0:
                # Spacer becomes small, check contract

                # Some menu items such as Camera settings, maybe not expanded but need to check if enough space for expand settings
                # Otherwise need to hide expand button
                require_size = 0
                for item in menu_items:
                    require_size += item.get_require_size(factory_args, expand=False)
                if require_size > spacer_width:
                    resize_again = self.__check_contract(menu_items, factory_args)

            elif spacer_width > self.__context[viewport_api_id].spacer_width:
                # Spacer becomes bigger, check if we can expand menu items
                require_size = 0
                expand_items: List[AbstractViewportMenuItem] = []
                for item in menu_items:
                    require_size += item.get_require_size(factory_args, expand=True)
                    expand_items.append(item)
                if require_size < spacer_width:
                    for item in expand_items:
                        item.expand(factory_args)
                    resize_again = True

            self.__context[viewport_api_id].spacer_width = spacer_width
            if resize_again:
                # Already resized, wait for menubar updated
                # Need at least 2 frames for a new Viewport window
                for _ in range(2):
                    await omni.kit.app.get_app().next_update_async()

    def __check_contract(self, menu_items: List[AbstractViewportMenuItem], factory_args: dict) -> bool:
        contract_items: Dict[MenuDisplayStatus, List[AbstractViewportMenuItem]] = {}

        # Figure how to contract
        # Since there are different display status for different menu items
        # Contract expand first and lable next
        max_contract_status = MenuDisplayStatus.MIN

        for item in menu_items:
            display_status = item.get_display_status(factory_args)
            if display_status == MenuDisplayStatus.MIN:
                # Already in min display status, nothing to contract
                continue

            if item.can_contract(factory_args):
                # Record items can contract here but contract later
                if display_status not in contract_items:
                    contract_items[display_status] = []
                contract_items[display_status].append(item)
                max_contract_status = max(display_status, max_contract_status)

        contracted = False
        # Only contract for one status: expand or label
        if max_contract_status != MenuDisplayStatus.MIN:
            for item in contract_items[max_contract_status]:
                item.contract(factory_args)
                contracted = True

        return contracted

    def __on_menu_expand_changed(self, factory_args: Dict):
        # OM-64798: Menu item expand status changed, need to reset saved spacer width
        viewport_api_id = factory_args['viewport_api'].id
        spacer_items = [item for item in self.__menu_items if isinstance(item, ViewportMenuSpacer) and item.order_model.as_int == 0]
        if spacer_items:
            spacer_item = spacer_items[0]

            async def __update_spacer_width():
                await omni.kit.app.get_app().next_update_async()
                self.__context[viewport_api_id].spacer_width = spacer_item.get_computed_width(factory_args)
            asyncio.ensure_future(__update_spacer_width())
        else:
            return
