# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import carb
from omni.asset_validator.core import Requirement

from .options import OptionModel


def _get_url(path: str) -> str:
    url = carb.settings.get_settings().get("exts/omni.asset_validator.ui/capabilities/url")
    return f"{url}/{path}"


class RequirementModel(OptionModel):
    def __init__(self, requirement: Requirement, selected: bool, enabled: bool):
        super().__init__(
            requirement,
            requirement.display_name or requirement.code,
            requirement.message or "",
            url=_get_url(requirement.path) if requirement.path else None,
            selected=selected,
            enabled=enabled,
        )
