# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import contextlib
import os

import omni.kit.menu.utils
import omni.ui
from omni.asset_validator.core import ValidationEngine
from pxr import Sdf, Usd, UsdGeom

from .asset import AssetMode
from .main import MainWidget
from .model import ApplicationModel
from .style import FRAME_STYLE

_ICON_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "icons")
"""Path to the icons directory."""

_VALIDATOR_ICON_PATH = os.path.join(_ICON_PATH, "assetValidatorDark.18x18.png")
"""Path to the validator icon."""


class AssetValidatorUI:

    # ComboBox requires it to be int
    def __init__(self, model: ApplicationModel) -> None:
        self.__model = model
        self.__build_window()
        self.__connect_main_menu()

        # OMPE-22957: USD Composer Missing Asset Validator When Right-Clicking Stage Panel
        # Optional extensions.
        with contextlib.suppress(Exception):
            self.__connect_content_browser()
        with contextlib.suppress(Exception):
            self.__connect_stage_window()
        with contextlib.suppress(Exception):
            self.__connect_layer_window()

    def shutdown(self) -> None:
        self.__disconnect_main_menu()
        with contextlib.suppress(Exception):
            self.__disconnect_content_browser()
        with contextlib.suppress(Exception):
            self.__disconnect_stage_window()
        with contextlib.suppress(Exception):
            self.__disconnect_layer_window()
        self.__destroy_window()

    @property
    def visible(self) -> bool:
        return self.__window.visible

    @visible.setter
    def visible(self, flag: bool) -> None:
        self.__window.visible = flag

    def __build_frame(self) -> None:
        MainWidget(self.__model)

    def __build_window(self) -> None:
        self.__window = omni.ui.Window("Asset Validator", width=1200, height=700, visible=False)
        self.__window.frame.set_style(FRAME_STYLE)
        self.__window.frame.set_build_fn(self.__build_frame)

    def __destroy_window(self) -> None:
        self.__window.destroy()
        self.__window = None

    def __validate_uri_callback(self, uri: str) -> None:
        self.__model.mode = AssetMode.Uri
        self.__model.uri = uri
        self.visible = True

    def __validate_stage_callback(self, stage: Usd.Stage) -> None:
        self.__model.mode = AssetMode.Stage
        self.__model.stage = stage
        self.visible = True

    def __validate_layer_callback(self, layer: Sdf.Layer, mode: AssetMode) -> None:
        self.__model.mode = mode
        if mode is AssetMode.Uri:
            self.__model.uri = layer.identifier
        elif mode is AssetMode.Stage:
            anon_stage = Usd.Stage.CreateInMemory(layer.GetDisplayName())
            app_stage = omni.usd.get_context().get_stage()
            anon_stage.SetMetadata(UsdGeom.Tokens.upAxis, app_stage.GetMetadata(UsdGeom.Tokens.upAxis))
            anon_stage.SetMetadata(UsdGeom.Tokens.metersPerUnit, app_stage.GetMetadata(UsdGeom.Tokens.metersPerUnit))
            anon_stage.GetSessionLayer().subLayerPaths.insert(0, layer.identifier)
            if layer.HasDefaultPrim():
                anon_stage.SetDefaultPrim(anon_stage.GetPseudoRoot().GetPrimAtPath(layer.defaultPrim))
            self.__model.stage = anon_stage
        self.visible = True

    def __connect_main_menu(self) -> None:
        """Creates the menu `Window / Asset Validator`"""
        self.__menu_action = omni.kit.actions.core.Action(
            "omni.asset_validator.ui",
            "toggle",
            self.__toggle_window,
        )
        omni.kit.actions.core.get_action_registry().register_action(self.__menu_action)

        self.__menu_list = [
            omni.kit.menu.utils.MenuItemDescription(
                name=self.__window.title,
                ticked=True,
                ticked_fn=lambda: self.visible,
                onclick_action=("omni.asset_validator.ui", "toggle"),
            )
        ]
        omni.kit.menu.utils.add_menu_items(self.__menu_list, "Window")

        self.__window.set_visibility_changed_fn(lambda _: omni.kit.menu.utils.refresh_menu_items("Window"))

    def __toggle_window(self) -> None:
        self.visible = not self.visible

    def __disconnect_main_menu(self) -> None:
        """"""
        self.__window.set_visibility_changed_fn(None)

        omni.kit.menu.utils.remove_menu_items(self.__menu_list, "Window")
        self.__menu_list = None

        omni.kit.actions.core.get_action_registry().deregister_all_actions_for_extension("omni.asset_validator.ui")
        self.__menu_action = None

    def __connect_content_browser(self):
        import omni.kit.window.content_browser

        content_browser = omni.kit.window.content_browser.get_content_window()
        content_browser.add_context_menu(
            "Validate USD",
            glyph=_VALIDATOR_ICON_PATH,
            click_fn=lambda _, path: self.__validate_uri_callback(path),
            show_fn=lambda path: ValidationEngine.is_asset_supported(path),
        )
        content_browser.add_context_menu(
            "Search for USD files and Validate",
            glyph=_VALIDATOR_ICON_PATH,
            click_fn=lambda _, path: self.__validate_uri_callback(path),
            show_fn=lambda path: content_browser.window.widget.api.context_menu._context["item"].is_folder,
        )

    def __disconnect_content_browser(self):
        import omni.kit.window.content_browser

        content_browser = omni.kit.window.content_browser.get_content_window()
        content_browser.delete_context_menu("Validate USD")
        content_browser.delete_context_menu("Search for USD files and Validate")

    def __connect_stage_window(self):
        import omni.kit.context_menu

        context_menu = omni.kit.context_menu.get_instance()
        menu_dict = {
            "name": "Validate Stage",
            "glyph": _VALIDATOR_ICON_PATH,
            "onclick_fn": lambda objects: self.__validate_stage_callback(objects["stage"]),
            "show_fn": lambda objects: not context_menu.is_prim_selected(objects),
        }
        self.__stageContextMenuConnections = omni.kit.context_menu.add_menu(menu_dict, "MENU", "omni.kit.widget.stage")

    def __disconnect_stage_window(self):
        self.__stageContextMenuConnections = None

    def __connect_layer_window(self):
        import omni.kit.widget.layers

        self.__layerContextMenuConnections = []
        self.__layerContextMenuConnections.append(
            omni.kit.widget.layers.ContextMenu.add_menu(
                [
                    {"name": ""},
                    {
                        "name": "Validate Layer (w/unsaved changes)",
                        "glyph": _VALIDATOR_ICON_PATH,
                        "onclick_fn": lambda objects: self.__validate_layer_callback(
                            layer=omni.kit.widget.layers.ContextMenu._get_layer_item(objects).layer,
                            mode=AssetMode.Stage,
                        ),
                        "show_fn": [
                            omni.kit.widget.layers.ContextMenu.is_layer_item,
                            omni.kit.widget.layers.ContextMenu.is_not_from_session_layer_tree,
                            omni.kit.widget.layers.ContextMenu.is_layer_dirty,
                        ],
                    },
                    {
                        "name": "Validate Layer (in-memory)",
                        "glyph": _VALIDATOR_ICON_PATH,
                        "onclick_fn": lambda objects: self.__validate_layer_callback(
                            layer=omni.kit.widget.layers.ContextMenu._get_layer_item(objects).layer,
                            mode=AssetMode.Stage,
                        ),
                        "show_fn": [
                            omni.kit.widget.layers.ContextMenu.is_layer_item,
                            omni.kit.widget.layers.ContextMenu.is_not_from_session_layer_tree,
                            lambda objects: not omni.kit.widget.layers.ContextMenu.is_layer_dirty(objects),
                        ],
                    },
                    {
                        "name": "Validate Layer (from file)",
                        "glyph": _VALIDATOR_ICON_PATH,
                        "onclick_fn": lambda objects: self.__validate_layer_callback(
                            layer=omni.kit.widget.layers.ContextMenu._get_layer_item(objects).layer,
                            mode=AssetMode.Uri,
                        ),
                        "show_fn": [
                            omni.kit.widget.layers.ContextMenu.is_layer_item,
                            omni.kit.widget.layers.ContextMenu.is_not_anonymous_layer,
                        ],
                    },
                ]
            )
        )

    def __disconnect_layer_window(self):
        self.__layerContextMenuConnections = None
