# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from functools import cache
from typing import Any

from omni.asset_validator.core import AssetType, CapabilityRegistry, Issue, IssueGroupBy, ValidationEngine
from omni.ui import AbstractValueModel
from pxr import Usd

__all__ = ["ApplicationModel"]


class _GroupByRule:
    def __call__(self, issues: list[Issue]) -> list[tuple[Any, Issue]]:
        def rule_name(issue: Issue) -> tuple[str, Issue]:
            rule_name: str = issue.rule.__name__ if issue.rule else ""
            return rule_name, issue

        return list(map(rule_name, issues))


class _GroupByRequirement:
    def __init__(self):
        self._code_to_requirement = {
            requirement.code: requirement.display_name
            for capability in CapabilityRegistry()
            for requirement in capability.requirements
        }

    def __call__(self, issues: list[Issue]) -> list[tuple[Any, Issue]]:
        def requirement_name(issue: Issue) -> tuple[str, Issue]:
            requirement_name: str = self._code_to_requirement.get(issue.code, issue.code)
            return requirement_name, issue

        return list(map(requirement_name, issues))


class _GroupByCapability:
    def __init__(self):
        self._code_to_capability = {
            requirement.code: f"{capability.name} - {requirement.display_name}"
            for capability in CapabilityRegistry()
            for requirement in capability.requirements
        }

    def __call__(self, issues: list[Issue]) -> list[tuple[Any, Issue]]:
        def capability_name(issue: Issue) -> tuple[str, Issue]:
            capability_name: str = self._code_to_capability.get(issue.code, issue.code)
            return capability_name, issue

        return list(map(capability_name, issues))


@dataclass
class ApplicationModel:
    """The main application model that holds all UI state.

    This class serves as the central data model for the Asset Validator application, managing all UI-related state including:

    - Asset information (URI, stage, validation mode)
    - Configuration settings (categories, capabilities)
    - User preferences (variant handling, root-only validation, persistence)
    - Validation results

    The model uses Omni UI's value models (AbstractValueModel and SimpleBoolModel) to enable reactive UI updates.

    Attributes:
        uri_model (AbstractValueModel): Model holding the asset URI
        stage_model (AbstractValueModel): Model holding the USD stage
        mode_model (AbstractValueModel): Model holding the validation mode
        categories_model (AbstractValueModel): Model holding validation categories
        capabilities_model (AbstractValueModel): Model holding validation capabilities
        features_model (AbstractValueModel): Model holding validation features
        profiles_model (AbstractValueModel): Model holding validation profiles
        options_mode_model (AbstractValueModel): Model holding whether we validate categories or capabilities.
        settings_model (AbstractValueModel): Model holding settings
        filters_model (AbstractValueModel): Model holding filters
        results_model (AbstractValueModel): Model holding validation results
    """

    # Asset
    uri_model: AbstractValueModel
    stage_model: AbstractValueModel
    mode_model: AbstractValueModel
    # Configurations
    categories_model: AbstractValueModel
    capabilities_model: AbstractValueModel
    features_model: AbstractValueModel
    profiles_model: AbstractValueModel
    options_mode_model: AbstractValueModel
    # Settings
    settings_model: AbstractValueModel
    filters_model: AbstractValueModel
    # Results
    results_model: AbstractValueModel
    _tasks: set[asyncio.Task] = field(init=False, default_factory=set)

    # Asset
    @property
    def uri(self) -> str:
        """Get the asset URI."""
        return self.uri_model.uri

    @uri.setter
    def uri(self, value: str) -> None:
        """Set the asset URI."""
        self.uri_model.uri = value

    @property
    def stage(self) -> Usd.Stage:
        """Get the asset stage."""
        return self.stage_model.stage

    @stage.setter
    def stage(self, value: Usd.Stage) -> None:
        """Set the asset stage."""
        self.stage_model.stage = value

    @property
    def mode(self):
        return self.mode_model.mode

    @mode.setter
    def mode(self, value) -> None:
        self.mode_model.mode = value

    @property
    def asset(self) -> AssetType:
        """Get the asset."""
        from .asset import AssetMode

        if self.mode is AssetMode.Uri:
            return self.uri
        elif self.mode is AssetMode.Stage:
            return self.stage
        else:
            return None

    @asset.setter
    def asset(self, value: AssetType) -> None:
        """Set the asset."""
        from .asset import AssetMode

        if isinstance(value, str):
            self.mode = AssetMode.Uri
            self.uri = value
        elif isinstance(value, Usd.Stage):
            self.mode = AssetMode.Stage
            self.stage = value
        else:
            raise ValueError(f"Invalid asset type: {type(value)}")

    def reset_asset(self) -> None:
        """Reset the asset."""
        self.uri = ""
        self.stage = None

    # Configurations
    @property
    def options_mode(self):
        """Get the options mode."""
        return self.options_mode_model.mode

    @options_mode.setter
    def options_mode(self, mode):
        self.options_mode_model.mode = mode

    @property
    def group_by(self) -> IssueGroupBy:
        """Get the group by."""
        from .options import OptionMode

        if self.options_mode is OptionMode.CATEGORIES:
            return _GroupByRule()
        elif self.options_mode is OptionMode.FEATURES:
            return _GroupByRequirement()
        elif self.options_mode is OptionMode.CAPABILITIES:
            return _GroupByRequirement()
        elif self.options_mode is OptionMode.PROFILES:
            return _GroupByCapability()

    def create_engine(self) -> ValidationEngine:
        """Create a validation engine."""
        from .options import OptionMode

        engine = ValidationEngine(init_rules=False, variants=self.settings_model.variants)
        if self.options_mode is OptionMode.CATEGORIES:
            for category in self.categories_model:
                for rule in category:
                    if rule.selected:
                        engine.enable_rule(rule.value)
        elif self.options_mode is OptionMode.FEATURES:
            for feature in self.features_model:
                for requirement in feature:
                    if requirement.selected:
                        engine.enable_requirement(requirement.value)
        elif self.options_mode is OptionMode.CAPABILITIES:
            for capability in self.capabilities_model:
                for requirement in capability:
                    if requirement.selected:
                        engine.enable_requirement(requirement.value)
        elif self.options_mode is OptionMode.PROFILES:
            for profile in self.profiles_model:
                for capability in profile:
                    if capability.selected:
                        engine.enable_capability(capability.value)
        return engine

    # Results
    @property
    def results(self):
        """Get the results model."""
        return self.results_model

    def reset_selection(self) -> None:
        """Reset the selection."""
        self.categories_model.reset()
        self.capabilities_model.reset()
        self.features_model.reset()
        self.profiles_model.reset()
        self.results_model.clear()

    def add_task(self, task: asyncio.Task) -> None:
        """Add a task to the model."""
        task.add_done_callback(self._tasks.discard)
        self._tasks.add(task)

    def has_tasks(self) -> bool:
        return bool(self._tasks)

    async def wait_tasks(self) -> None:
        await asyncio.gather(*self._tasks)

    # Instance
    @classmethod
    @cache
    def get(cls) -> ApplicationModel:
        """Get the application model singleton"""
        return cls.create()

    @classmethod
    def create(cls) -> ApplicationModel:
        """Create a new application model."""
        from .asset import ModeModel, StageModel, UriModel
        from .capabilities import CapabilitiesModel
        from .categories import CategoriesModel
        from .features import FeaturesModel
        from .filters import FiltersModel
        from .options import OptionModeModel
        from .profiles import ProfilesModel
        from .results import ResultsModel
        from .settings import SettingsModel

        return ApplicationModel(
            uri_model=UriModel(),
            stage_model=StageModel(),
            mode_model=ModeModel(),
            categories_model=CategoriesModel(),
            capabilities_model=CapabilitiesModel(),
            features_model=FeaturesModel(),
            profiles_model=ProfilesModel(),
            options_mode_model=OptionModeModel(),
            settings_model=SettingsModel(),
            filters_model=FiltersModel(),
            results_model=ResultsModel(),
        )
