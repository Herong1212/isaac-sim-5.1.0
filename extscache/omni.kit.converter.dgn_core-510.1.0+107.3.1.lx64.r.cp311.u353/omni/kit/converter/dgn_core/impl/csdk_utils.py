# SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.
import os
from pathlib import Path

import carb
import carb.tokens
import omni.connect.core
import omni.kit.app

__all__ = [
    "initialize_connect_sdk",
]


class SettingsConstants:
    """
    Store settings constants shared across extensions.
    """

    APP_NAME_PATH = "/app/name"  # carb settings path
    APP_VERSION_PATH = "/app/version"  # carb settings path
    CLIENT_NAME_PATH = "/omni.connect.core/client/name"  # carb settings path
    CLIENT_VERSION_PATH = "/omni.connect.core/client/version"  # carb settings path


def set_app_data(app_name: str, app_version: str, client_name: str, client_version: str) -> None:
    """Use carb settings to set app name / version and client name / version metadata."""
    carb.settings.get_settings().set_string(SettingsConstants.APP_NAME_PATH, app_name)
    carb.settings.get_settings().set_string(SettingsConstants.APP_VERSION_PATH, app_version)
    carb.settings.get_settings().set_string(SettingsConstants.CLIENT_NAME_PATH, client_name)
    carb.settings.get_settings().set_string(SettingsConstants.CLIENT_VERSION_PATH, client_version)


def initialize_connect_sdk(core_ext_name: str) -> None:
    """Initializes the Connect SDK"""
    # set CARB_APP_PATH to extension root. Otherwise we'd get errors in Connect SDK
    # regarding cannot find CARB_APP_PATH
    carb.log_info(f"STARTUP {core_ext_name}")
    if "CARB_APP_PATH" not in os.environ:
        g_token = carb.tokens.get_tokens_interface()
        extension_root = Path(g_token.resolve(f"${{{core_ext_name}}}"))
        os.environ["CARB_APP_PATH"] = str(extension_root)

    # Call _set_app_data for omni.connect.core to correctly startup since we aren't using the omni.connect.client.toml
    app_name = omni.kit.app.get_app().get_app_name()
    app_version = omni.kit.app.get_app().get_app_version()
    manager = omni.kit.app.get_app().get_extension_manager()
    ext_id = manager.get_extension_id_by_module(core_ext_name)
    ext_version = manager.get_extension_dict(ext_id)["package"]["version"]
    set_app_data(app_name, app_version, core_ext_name, ext_version)
