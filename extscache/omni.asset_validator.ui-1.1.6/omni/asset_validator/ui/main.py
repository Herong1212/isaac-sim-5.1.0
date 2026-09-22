# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import carb
from omni.asset_validator.core import add_registry_rule_callback
from omni.ui import Spacer, VStack

from .asset import AssetWidget
from .capabilities import CapabilitiesWidget
from .categories import CategoriesWidget
from .commands import ClearFn, ValidatorCommandsWidget
from .features import FeaturesWidget
from .model import ApplicationModel
from .options import OptionMode
from .panels import PanelWidget
from .profiles import ProfilesWidget
from .report import ResultsWidget
from .settings import SettingsWidget
from .tabs import TabsWidget


class CategoriesTab:

    def get_name(self):
        return "Categories"

    def build_fn(self):
        CategoriesWidget()


class FeaturesTab:

    def get_name(self):
        return "Features"

    def build_fn(self):
        FeaturesWidget()


class CapabilitiesTab:

    def get_name(self):
        return "Requirements"

    def build_fn(self):
        CapabilitiesWidget()


class ProfilesTab:

    def get_name(self):
        return "Profiles"

    def build_fn(self):
        ProfilesWidget()


class MainWidget:
    def __init__(self, model: ApplicationModel):
        self._model = model
        self._subscription = None
        self._enable_capabilities = carb.settings.get_settings().get(
            "exts/omni.asset_validator.ui/capabilities/enabled"
        )
        with VStack():
            AssetWidget()
            with VStack():
                self._panel = PanelWidget(
                    menu_build_fn=self._menu_build_fn,
                    view_build_fn=lambda: ResultsWidget(),
                )
                self._panel_subscription = add_registry_rule_callback(self._update_panel)
                Spacer(height=10)
                ValidatorCommandsWidget()

    def _update_panel(self) -> None:
        self._panel.rebuild()
        ClearFn(self._model).apply()

    def _menu_build_fn(self) -> None:
        with VStack():
            SettingsWidget()
            if self._enable_capabilities:
                tabs = TabsWidget([CategoriesTab(), CapabilitiesTab()])
                self._subscription = tabs.subscribe_value_changed_fn(self._update_mode)
            else:
                CategoriesTab().build_fn()

    def _update_mode(self, value):
        if value.as_int == 0:
            self._model.options_mode = OptionMode.CATEGORIES
        elif value.as_int == 1:
            self._model.options_mode = OptionMode.CAPABILITIES

    def destroy(self) -> None:
        self._model = None
        self._subscription = None
        self._panel = None
        self._panel_subscription = None
