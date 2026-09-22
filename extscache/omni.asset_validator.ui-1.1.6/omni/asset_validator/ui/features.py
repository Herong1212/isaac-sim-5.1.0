# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

import carb
from omni.asset_validator.core import Feature, FeatureRegistry, RequirementsRegistry

from .model import ApplicationModel
from .options import OptionGroup, OptionsItemModel, OptionsModel, OptionsWidget
from .requirements import RequirementModel

__all__ = ["FeaturesModel", "FeaturesWidget"]


def _get_url(path: str) -> str:
    url = carb.settings.get_settings().get("exts/omni.asset_validator.ui/capabilities/url")
    return f"{url}/{path}"


class FeatureModel(OptionGroup):
    def __init__(self, feature: Feature):
        super().__init__(f"{feature.name}@{feature.version}", _get_url(feature.path) if feature.path else None)


class FeaturesModel(OptionsModel):

    def initialize(self) -> None:
        selected: bool = False
        registry = RequirementsRegistry()
        self.clear()
        for feature in FeatureRegistry():
            if not feature.requirements:
                continue
            if all(registry.get_validator(requirement) is None for requirement in feature.requirements):
                continue
            feature_model = FeatureModel(feature)
            for requirement in feature.requirements:
                feature_model.append(
                    RequirementModel(requirement, selected, registry.get_validator(requirement) is not None)
                )
            self.append(feature_model)

    def reset(self) -> None:
        selected: bool = False
        for capability in self:
            for requirement in capability:
                requirement.selected = selected


class FeaturesWidget(OptionsWidget):
    def __init__(self, model: FeaturesModel | None = None):
        super().__init__(model=OptionsItemModel(model or ApplicationModel.get().features_model))
