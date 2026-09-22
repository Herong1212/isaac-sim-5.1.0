import asyncio
from functools import partial
from itertools import chain
from typing import List

import omni.kit.app
from omni import ui
from omni.ui import scene as sc

from ..models import CategoryItem
from . import CategoryDelegate
from .style import ICON_PATH

FULL_LINE_HEIGHT = 20


class VLine(ui.Line):
    def __init__(self, half: bool = False):
        return super().__init__(
            height=FULL_LINE_HEIGHT / 2 if half else FULL_LINE_HEIGHT,
            width=0,
            alignment=ui.Alignment.LEFT,
            style_type_name_override="TreeView.Branch.Line"
        )


class TreeCategoryDelegate(CategoryDelegate):
    """
    Delegate to represent category items in a hierarchical structure.

    Kwargs:
        hide_zero_count (bool): Hide category count if count is 0. Default False.
    """

    def __init__(self, hide_zero_count: bool=False, *args, **kwargs):
        self.__hide_zero_count = hide_zero_count
        self._transform = {}
        self._rotate_future = {}
        super().__init__(*args, **kwargs)

    def build_widget(
        self, model: ui.AbstractItemModel, item: CategoryItem, index: int = 0, level: int = 0, expanded: bool = False
    ):
        """
        Create a widget per category item
        Args:
            model (AbstractItemModel): Category data model
            item (CategoryItem): Category item
            index (int): ignore
            level (int): ignore
            expand (int): ignore
        """
        with ui.HStack(mouse_pressed_fn=partial(self._on_category_item_click, item)):
            ui.Label(
                self.get_label(item),
                alignment=ui.Alignment.LEFT_CENTER,
                style_type_name_override="TreeView.Item.Name"
            )

            show_count = True
            if self.__hide_zero_count:
                try:
                    count = int(self.get_count(item))
                    show_count = count > 0
                except:
                    pass

            if item.loading:
                ui.Spacer()
                with sc.SceneView(width=FULL_LINE_HEIGHT, height=FULL_LINE_HEIGHT).scene:
                    self._transform[item] = sc.Transform()
                    with self._transform[item]:
                        sc.Image(f"{ICON_PATH}/omni_logo_24.png", width=2.0, height=2.0)

                async def _rotate():
                    angle = [0]
                    while True:
                        delta = await omni.kit.app.get_app().next_update_async()
                        angle[0] -= delta * 1.5
                        transform = sc.Matrix44.get_rotation_matrix(0, 0, angle[0])
                        self._transform[item].transform = transform

                self._rotate_future[item] = asyncio.ensure_future(_rotate())
            else:
                if item in self._rotate_future and self._rotate_future[item]:
                    self._rotate_future[item].cancel()
                    self._rotate_future[item] = None
                if show_count:
                    ui.Label(
                        f"{self.get_count(item)}",
                        alignment=ui.Alignment.RIGHT_CENTER,
                        style_type_name_override="TreeView.Item.Count",
                    )

        return

    def build_branch(
        self,
        model: ui.AbstractItemModel,
        item: CategoryItem,
        column_id: int = 0,
        level: int = 0,
        expanded: bool = False,
    ):
        """
        Create a branch widget that opens or closes subtree
        Args:
            model (AbstractItemModel): Category data model
            item (CategoryItem): Category item
            column_id (int): ignore
            level (int): Level of the hierarchy the current item is at, from 0 to n.
            expand (int): Indicates whether we will see child categories expanded or not.
        """
        with ui.HStack(height=FULL_LINE_HEIGHT, spacing=0):
            ui.Spacer(width=5)  # Extra left margin for all

            if not item.children:
                ui.Spacer(width=2)
                if level == 0 and item.name.upper() == "ALL":  # No decoration for ALL root
                    return

                if level == 0:
                    # Just a simple dot
                    ui.Circle(width=4, alignment=ui.Alignment.RIGHT_CENTER,
                              style_type_name_override="TreeView.Branch.Line")
                    ui.Spacer(width=8)
                    return

                ui.Spacer(width=3)
                if level > 1:
                    for i in range(1, level):
                        # OM-83328: Always show line here
                        VLine()
                        ui.Spacer(width=15)

                with ui.ZStack():
                    # vertical line
                    with ui.HStack():
                        if not item.is_last_child:
                            # Full vertical line
                            VLine()
                        else:
                            # Half vertical line for L-shaped branch
                            with ui.VStack():
                                VLine(half=True)
                                ui.Spacer(height=6)
                        ui.Spacer()

                    # horiz line
                    ui.Line(width=16, style_type_name_override="TreeView.Branch.Line")

                    # dot
                    with ui.HStack():
                        ui.Spacer()
                        ui.Circle(width=4, alignment=ui.Alignment.RIGHT_CENTER,
                                  style_type_name_override="TreeView.Branch.Line")

                ui.Spacer(width=10)  # more space after dot than +/-

            else:
                if level > 0:
                    item.children[-1].is_last_child = True

                    ui.Spacer(width=5)
                    for i in range(0, level):
                        # OM-83328: Always show line here
                        VLine()
                        if i != level -1:
                            ui.Spacer(width=15)
                    ui.Spacer(width=10)

                self.draw_expanded_symbol(expanded)

    def draw_expanded_symbol(self, expanded: bool) -> None:
        if expanded:
            # Minus sign
            with ui.VStack(width=8):
                ui.Spacer()
                with ui.HStack():
                    ui.Spacer(width=2)
                    ui.Line(width=7, style_type_name_override="TreeView.Item")
                ui.Spacer()
        else:
            # Plus sign
            with ui.ZStack(width=8):
                # horiz line
                with ui.VStack(width=8):
                    ui.Spacer()
                    with ui.HStack():
                        ui.Spacer(width=2)
                        ui.Line(width=7, style_type_name_override="TreeView.Item")
                    ui.Spacer()
                # vertical line
                with ui.HStack():
                    ui.Spacer(width=1)
                    ui.Spacer()
                    with ui.VStack():
                        ui.Spacer(height=.1)
                        ui.Spacer()
                        ui.Line(height=7, alignment=ui.Alignment.H_CENTER, style_type_name_override="TreeView.Item")
                        ui.Spacer()
                    ui.Spacer()
        ui.Spacer(width=5)

    def get_label(self, item: CategoryItem) -> str:
        return item.name.upper().split("/")[-1]

    def _on_category_item_click(self, item: CategoryItem, x, y, button, key_mod):
        if button == 1:
            self._on_item_right_click(item)

    def _on_item_right_click(self, item: CategoryItem):
        pass
