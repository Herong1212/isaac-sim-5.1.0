# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

import carb
from omni.asset_validator.core import Capability, CapabilityRegistry, RequirementsRegistry

from .model import ApplicationModel
from .options import OptionGroup, OptionsItemModel, OptionsModel, OptionsWidget
from .requirements import RequirementModel

__all__ = ["CapabilitiesModel", "CapabilitiesWidget"]


def _get_url(path: str) -> str:
    url = carb.settings.get_settings().get("exts/omni.asset_validator.ui/capabilities/url")
    return f"{url}/{path}"


class CapabilityModel(OptionGroup):
    def __init__(self, capability: Capability):
        super().__init__(
            f"{capability.name}@{capability.version}", _get_url(capability.path) if capability.path else None
        )


class CapabilitiesModel(OptionsModel):

    def initialize(self) -> None:
        selected: bool = False
        registry = RequirementsRegistry()
        self.clear()
        for capability in CapabilityRegistry():
            if not capability.requirements:
                continue
            if all(registry.get_validator(requirement) is None for requirement in capability.requirements):
                continue
            capability_model = CapabilityModel(capability)
            for requirement in capability.requirements:
                capability_model.append(
                    RequirementModel(requirement, selected, registry.get_validator(requirement) is not None)
                )
            self.append(capability_model)

    def reset(self) -> None:
        selected: bool = False
        for capability in self:
            for requirement in capability:
                requirement.selected = selected


class CapabilitiesWidget(OptionsWidget):
    def __init__(self, model: CapabilitiesModel | None = None):
        super().__init__(model=OptionsItemModel(model or ApplicationModel.get().capabilities_model))
