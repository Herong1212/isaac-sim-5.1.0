# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.
import asyncio
from typing import List

import carb
import carb.settings
import omni.kit.commands
from omni.kit.viewport.utility import get_active_viewport_window
from pxr import Usd, UsdLux

from .constants import ENVIRONMENT_PRIM_ROOT, EnvironmentSettings, SkyType
from .scene_template import SceneTemplateHelper
from .sky import SkyHelper
from .warning_window import WarningMessage, WarningWindow


def delete_lights(light_prims: List[Usd.Prim]):
    omni.kit.commands.execute("DeletePrimsCommand", paths=[prim.GetPath().pathString for prim in light_prims])
    # Return False to close warning dialog
    return False


def check_lights(stage: Usd.Stage, check_env_root: bool = True):
    prims = stage.Traverse(Usd.TraverseInstanceProxies(Usd.PrimIsActive and Usd.PrimIsDefined and Usd.PrimIsLoaded))
    light_prims: List[Usd.Prim] = []
    for prim in prims:
        if (
            prim.IsA(UsdLux.DistantLight)
            or prim.IsA(UsdLux.DomeLight)
            or prim.IsA(UsdLux.RectLight)
            or prim.IsA(UsdLux.DiskLight)
            or prim.IsA(UsdLux.SphereLight)
            or prim.IsA(UsdLux.CylinderLight)
        ):
            path = prim.GetPath().pathString
            if path.startswith(ENVIRONMENT_PRIM_ROOT):
                if check_env_root:
                    path = path[len(ENVIRONMENT_PRIM_ROOT) + 1 :]
                    if len(path.split("/")) == 1:
                        # Only check lights under env root
                        light_prims.append(prim)
            else:
                light_prims.append(prim)

    if light_prims:
        messages = [
            WarningMessage(f"{len(light_prims)} extra light(s) found!"),
            "\n",
        ]
        for prim in light_prims:
            messages.append(WarningMessage(f"\t{prim.GetPath().pathString}", highlight=True))
            messages.append("\n")
        messages.extend(["Do you want to delete these exising lights?"])

        warn_window = WarningWindow(
            "Extra Lights Warning",
            messages=messages,
            buttons=[("Delete", lambda p=light_prims: delete_lights(p)), ("Keep", None)],
        )

        viewport_window = get_active_viewport_window()
        if viewport_window:

            async def __adjust_position():
                while warn_window.frame.computed_width < 10:
                    await omni.kit.app.get_app().next_update_async()
                warn_window.position_x = (
                    viewport_window.position_x + (viewport_window.width - warn_window.frame.computed_width) / 2
                )
                warn_window.position_y = (
                    viewport_window.position_y + (viewport_window.height - warn_window.frame.computed_height) / 2
                )

            asyncio.ensure_future(__adjust_position())


def clean_environment(type: SkyType, url: str) -> None:
    stage = omni.usd.get_context().get_stage()
    if not stage:
        return

    (exist_sky_path, exist_asset_path) = SkyHelper.find_sky()
    if exist_asset_path:
        if exist_asset_path == url:
            carb.log_warn(f"[Sky Browser] Sky {url} is the current sky, do nothing.")
            return

    if type == SkyType.SCENE:
        # For a new scene template, clean old env

        # Remove scene template including sub layer
        SceneTemplateHelper().remove_current_scene_template()

        # Remove env prim
        env_prim = stage.GetPrimAtPath(ENVIRONMENT_PRIM_ROOT)
        if env_prim:
            omni.kit.commands.execute("DeletePrimsCommand", paths=[ENVIRONMENT_PRIM_ROOT])
    elif exist_sky_path:
        # Clean sky only
        omni.kit.commands.execute("DeletePrimsCommand", paths=[exist_sky_path])


def apply_environment(stage: Usd.Stage, type: str, url: str) -> str:
    # OM-66383: Make sure env root is Xform
    environment_root_prim = stage.GetPrimAtPath(ENVIRONMENT_PRIM_ROOT)
    if not environment_root_prim:
        stage.DefinePrim(ENVIRONMENT_PRIM_ROOT, "Xform")

    if type == SkyType.DYNAMIC:
        return SkyHelper.create_dynamic_sky(url)
    elif type == SkyType.HDRI:
        return SkyHelper.create_hdri_sky(url)
    elif type == SkyType.SCENE:
        carb.log_info(f"[Env] apply template: {url}")
        return SceneTemplateHelper().apply_scene_template(url)


def import_environment(type: SkyType, url: str) -> str:
    """Imports an environment into the current USD stage.

    Cleans the existing environment and, if light warnings are enabled, checks for extra lights before applying the new environment based on the provided type and url. Returns an empty string if no USD stage is available.

    Args:
        type (SkyType): Environment sky type to import.
        url (str): File path or url of the environment to import.

    Returns:
        str: Result of the environment application, or an empty string if no stage is available.
    """
    stage = omni.usd.get_context().get_stage()
    if not stage:
        return ""

    clean_environment(type, url)

    if carb.settings.get_settings().get(EnvironmentSettings.SHOW_LIGHT_WARNING):
        check_lights(stage)

    apply_environment(stage, type, url)


def register_actions(extension_id):
    try:
        import omni.kit.actions.core

        action_registry = omni.kit.actions.core.get_action_registry()
        actions_tag = "Environment"

        action_registry.register_action(
            extension_id,
            "import",
            lambda type, url: import_environment(type, url),
            display_name="Environment->Import",
            description="Import environment files to stage",
            tag=actions_tag,
        )
    except ImportError:
        pass


def deregister_actions(extension_id):
    try:
        import omni.kit.actions.core

        action_registry = omni.kit.actions.core.get_action_registry()
        action_registry.deregister_all_actions_for_extension(extension_id)
    except ImportError:
        pass
