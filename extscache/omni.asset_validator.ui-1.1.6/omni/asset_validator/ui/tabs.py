# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from functools import partial
from typing import Protocol, runtime_checkable

from omni.ui import Frame, HStack, Label, Rectangle, SimpleIntModel, Spacer, VStack, ZStack

from .style import TAB_GROUP_STYLE, TAB_STYLE

__all__ = ["TabBuilder", "TabsWidget"]


@runtime_checkable
class TabBuilder(Protocol):
    def get_name(self) -> str: ...

    def build_fn(self): ...


class TabsWidget:
    def __init__(self, tabs: list[TabBuilder]):
        self.frame = Frame(build_fn=self._build_widget)
        self.tabs = tabs
        self.tab_containers = []
        self.headers = []
        self._model = SimpleIntModel(0)

    def _build_widget(self):
        with ZStack(style=TAB_GROUP_STYLE):
            Rectangle(style_type_name_override="TabGroupBorder")
            with VStack():
                Spacer(height=1)
                with ZStack(height=0, name="TabGroupHeader"):
                    Rectangle(name="TabGroupHeader")
                    with VStack():
                        Spacer(height=2)
                        with HStack(height=0, spacing=4):
                            for i, tab in enumerate(self.tabs):
                                tab_header = ZStack(style=TAB_STYLE)
                                self.headers.append(tab_header)
                                with tab_header:
                                    rect = Rectangle()
                                    rect.set_mouse_released_fn(partial(self._tab_clicked, i))
                                    Label(tab.get_name())
                with ZStack():
                    for i, tab in enumerate(self.tabs):
                        container_frame = Frame(build_fn=tab.build_fn)
                        self.tab_containers.append(container_frame)
                        container_frame.visible = False

        self.select_tab(0)

    def select_tab(self, index: int):
        self._model.set_value(index)
        for i in range(len(self.tabs)):
            flag: bool = i == index
            self.tab_containers[i].visible = flag
            self.headers[i].selected = flag

    def _tab_clicked(self, index, x, y, button, modifier):
        if button == 0:
            self.select_tab(index)

    def subscribe_value_changed_fn(self, func):
        return self._model.subscribe_value_changed_fn(func)

    def destroy(self):
        self.frame.destroy()
