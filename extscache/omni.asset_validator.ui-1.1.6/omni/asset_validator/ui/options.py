# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from __future__ import annotations

import functools
import webbrowser
from collections import defaultdict
from enum import IntEnum
from typing import Any, TypeVar

from omni.ui import (
    AbstractItem,
    AbstractItemModel,
    AbstractValueModel,
    Alignment,
    Button,
    CheckBox,
    CollapsableFrame,
    HStack,
    Label,
    SimpleIntModel,
    Spacer,
    Triangle,
    VStack,
)

__all__ = [
    "OptionGroup",
    "OptionModel",
    "OptionsItemModel",
    "OptionsModel",
    "OptionsWidget",
    "OptionMode",
    "OptionModeModel",
]

T = TypeVar("T")


class OptionMode(IntEnum):
    CATEGORIES = 0
    CAPABILITIES = 1
    PROFILES = 2
    FEATURES = 3


class OptionModeModel(SimpleIntModel):
    def __init__(self) -> None:
        super().__init__(OptionMode.CATEGORIES.value)

    @property
    def mode(self) -> OptionMode:
        return OptionMode(self.get_value_as_int())

    @mode.setter
    def mode(self, mode: OptionMode) -> None:
        self.set_value(mode.value)


class OptionModel(AbstractValueModel):
    """
    Option model. Consist of value and its properties.
    """

    def __init__(
        self,
        value: Any,
        name: str,
        description: str | None = None,
        url: str | None = None,
        selected: bool | None = False,
        enabled: bool | None = True,
    ):
        super().__init__()
        self._value = value
        self._name = name
        self._description = description or ""
        self._url = url or ""
        self._selected = selected
        self._enabled = enabled

    @property
    def value(self) -> Any:
        return self._value

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def url(self) -> str:
        return self._url

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def selected(self) -> bool:
        return self._selected

    @selected.setter
    def selected(self, value) -> None:
        if self.enabled:
            self._selected = value
            self._value_changed()

    def set_value(self, value: bool) -> None:
        self.selected = value

    def get_value_as_bool(self) -> bool:
        return self.selected


class OptionGroup:
    def __init__(self, name: str, url: str | None = None, options: list[OptionModel] | None = None):
        self._name = name
        self._url = url
        self._options = options or []

    @property
    def name(self) -> str:
        return self._name

    @property
    def url(self) -> str | None:
        return self._url

    def __len__(self):
        return len(self._options)

    def __getitem__(self, item):
        return self._options[item]

    def append(self, option: OptionModel) -> None:
        self._options.append(option)

    def get(self, value) -> OptionModel | None:
        for option in self:
            if option.value == value:
                return option
        return None


class OptionsModel:
    def __init__(self, groups: list[OptionGroup] | None = None):
        self._groups = groups or []
        self.initialize()

    def initialize(self) -> None: ...

    def reset(self) -> None: ...

    def __len__(self):
        return len(self._groups)

    def __getitem__(self, item):
        return self._groups[item]

    def clear(self) -> None:
        self._groups.clear()

    def append(self, group: OptionGroup) -> None:
        self._groups.append(group)

    def get(self, value) -> OptionModel | None:
        for group in self:
            if option := group.get(value):
                return option
        return None


class OptionItem(AbstractItem):
    """
    An item with OptionModel.
    """

    def __init__(self, model: OptionModel | OptionGroup):
        super().__init__()
        self._model = model

    @property
    def model(self) -> OptionModel | OptionGroup:
        return self._model


class OptionsItemModel(AbstractItemModel):
    """
    The model for OptionsWidget. The input is a generic data tree.
    """

    def __init__(self, model: OptionsModel):
        super().__init__()

        self._item_to_children = defaultdict(list)
        for value in model:
            item = OptionItem(value)
            self._item_to_children[None].append(item)
            for child in value:
                child_item = OptionItem(child)
                self._item_to_children[item].append(child_item)

    def get_item_children(self, item: AbstractItem | None) -> list[AbstractItem]:
        """Override"""
        return self._item_to_children[item]

    def get_item_value_model(self, item: AbstractItem | None, *_):
        """Override"""
        return item.model


class OptionsWidget:
    def __init__(self, model: OptionsItemModel):
        self._model = model
        with VStack(height=0):
            with HStack(height=30):
                self._create_toggle_button(enable=True)
                self._create_toggle_button(enable=False)

            Spacer(width=0, height=10)
            for item in model.get_item_children(None):
                with CollapsableFrame(
                    item.model.name, build_header_fn=functools.partial(self._build_header_fn, item.model)
                ):
                    with VStack():
                        with HStack(height=30):
                            self._create_toggle_button(enable=True, item=item)
                            self._create_toggle_button(enable=False, item=item)
                        Spacer(height=10)
                        for child_item in model.get_item_children(item):
                            with HStack(height=18):
                                CheckBox(
                                    child_item.model,
                                    width=20,
                                    tooltip=child_item.model.description,
                                    enabled=child_item.model.enabled,
                                )
                                Label(
                                    child_item.model.name,
                                    tooltip=child_item.model.description,
                                )
                                if child_item.model.url:
                                    Button(
                                        width=20,
                                        height=20,
                                        image_url="resources/glyphs/link.svg",
                                        clicked_fn=functools.partial(self._open_url, url=child_item.model.url),
                                    )
                            Spacer(height=10)

    def _create_toggle_button(self, enable: bool, item: OptionItem | None = None) -> None:
        action = "Enable" if enable else "Disable"
        Button(
            f"{action} All",
            clicked_fn=functools.partial(self._toggle_option, enable=enable, item=item),
        )

    def _toggle_option(self, enable: bool = True, item: OptionItem | None = None) -> None:
        if item is None:
            for item in self._model.get_item_children(None):
                for child in self._model.get_item_children(item):
                    child.model.selected = enable
        else:
            for child in self._model.get_item_children(item):
                child.model.selected = enable

    def _open_url(self, url: str) -> None:
        webbrowser.open(url)

    def _build_header_fn(self, model: OptionGroup, collapsed: bool, title: str) -> None:
        alignment = Alignment.CENTER_BOTTOM if not collapsed else Alignment.RIGHT_CENTER
        with HStack():
            with VStack(width=10):
                Spacer()
                with HStack():
                    Spacer(width=3)
                    Triangle(alignment=alignment, width=8, height=8, style={"background_color": 0xFFFFFFFF})
                    Spacer(width=7)
                Spacer()
            Label(model.name)
            Spacer()
            if model.url:
                with HStack(content_clipping=True, width=16):
                    Button(
                        width=16,
                        height=16,
                        image_url="resources/glyphs/link.svg",
                        clicked_fn=functools.partial(self._open_url, url=model.url),
                    )
