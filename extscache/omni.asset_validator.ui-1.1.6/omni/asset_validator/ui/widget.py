# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

__all__ = ["AssetValidatorWidget"]

from collections.abc import Callable

import omni.ui
import omni.usd
from omni.asset_validator.core import add_registry_rule_callback

from .asset import AssetWidget
from .categories import CategoriesWidget
from .commands import ClearFn, ValidatorCommandsWidget
from .model import ApplicationModel
from .report import ResultsWidget
from .settings import SettingsWidget

__all__ = ["AssetValidatorWidget", "EmbeddedValidatorWidget"]


class EmbeddedValidatorWidget:
    """
    An embedded widget for the extensions depending on the asset validator.
    """

    def __init__(
        self,
        *,
        model: ApplicationModel | None = None,
        offset_x_changed_fn: Callable[[omni.ui.Length], None] | None = None,
        show_mode_widget: bool = True,
    ) -> None:
        self.__model = model or ApplicationModel.get()
        self.__offset_x_changed_fn = offset_x_changed_fn
        self.__show_mode_widget = show_mode_widget
        self._subscription = add_registry_rule_callback(self._update_categories)
        self.__build_widget()

    @property
    def offset_x(self):
        return self.__placer.offset_x

    @offset_x.setter
    def offset_x(self, value):
        self.__placer.offset_x = value

    def reset(self, reset_assets: bool = False, reset_rules: bool = False) -> None:
        if reset_assets:
            self.__model.uri = ""
            self.__model.stage = None
        if reset_rules:
            self.__model.categories_model.reset()
            self.__model.results.clear()

    def __build_widget(self) -> None:
        with omni.ui.VStack():
            AssetWidget(visible=self.__show_mode_widget)

            with omni.ui.HStack():
                with omni.ui.ZStack(width=0):
                    self.__placer = omni.ui.Placer(
                        offset_x=300,
                        draggable=True,
                        drag_axis=omni.ui.Axis.X,
                        offset_x_changed_fn=self.__offset_x_changed_fn,
                    )
                    with self.__placer:
                        omni.ui.Rectangle(width=4, name="splitter")

                    with omni.ui.HStack():
                        self._panel = omni.ui.ScrollingFrame(build_fn=self._build_categories)
                        omni.ui.Spacer(width=4)

                with omni.ui.VStack():
                    SettingsWidget()
                    with omni.ui.VStack():
                        ResultsWidget()

            omni.ui.Spacer(width=0, height=10)
            ValidatorCommandsWidget()

    def _build_categories(self) -> None:
        CategoriesWidget(model=self.__model.categories_model)

    def _update_categories(self) -> None:
        self._panel.rebuild()
        self._panel.scroll_y = 0
        ClearFn(self.__model).apply()

    def destroy(self) -> None:
        self.__placer = None
        self._subscription = None


AssetValidatorWidget = EmbeddedValidatorWidget
"""
.. deprecated:: 0.24.0
   Use :class:`EmbeddedValidatorWidget` instead.
"""
