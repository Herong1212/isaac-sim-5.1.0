# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""This module provides the PrimTransformManipulator class for interactive transformation of USD prims in a viewport."""


import copy
from typing import List, Union

import carb.dictionary
import carb.events
import carb.settings
import omni.ext
import omni.usd
from omni.kit.manipulator.selector import ManipulatorBase
from omni.kit.manipulator.tool.snap import SnapProviderManager
from omni.kit.manipulator.tool.snap import settings_constants as snap_c
from omni.kit.manipulator.transform import Constants as transform_c
from omni.kit.manipulator.transform import (
    OpSettingsListener,
    SnapSettingsListener,
    TransformManipulator,
    get_default_style,
)
from pxr import Sdf, Usd, UsdGeom

from .model import PrimRotateChangedGesture, PrimScaleChangedGesture, PrimTransformModel, PrimTranslateChangedGesture
from .toolbar_registry import get_toolbar_registry

TRANSFORM_GIZMO_HIDDEN_OVERRIDE = "/app/transform/gizmoHiddenOverride"


class PrimTransformManipulator(ManipulatorBase):
    """A class responsible for creating and managing a transform manipulator for USD prims.

    This manipulator allows for the interactive transformation of prims within a USD stage via a viewport. It supports translation, rotation, and scaling operations both globally and locally. It also integrates with snapping tools for precise control over the transformations.

    Args:
        usd_context_name (str): The name of the USD context in which the manipulator will operate.
        viewport_api: The API for the viewport that the manipulator will interact with. If None, it indicates legacy mode.
        name (str): The name identifier for the manipulator instance.
        model (Optional[:obj:`PrimTransformModel`]): The data model that the manipulator will use to apply transformations. If None, a new model is created.
        size (float): The scale factor for the manipulator's visual representation in the viewport."""

    def __init__(
        self,
        usd_context_name: str = "",
        viewport_api=None,
        name="omni.kit.manipulator.prim.core",
        model: PrimTransformModel = None,
        size: float = 1.0,
    ):
        """Constructor for the PrimTransformManipulator class."""
        super().__init__(name=name, usd_context_name=usd_context_name)
        self._dict = carb.dictionary.get_dictionary()
        self._settings = carb.settings.get_settings()
        self._usd_context = omni.usd.get_context(usd_context_name)
        self._selection = self._usd_context.get_selection()
        self._model_is_external = model is not None
        self._model = model if self._model_is_external else PrimTransformModel(usd_context_name, viewport_api)
        self._legacy_mode = viewport_api is None  # if no viewport_api is supplied, it is from VP1
        self._snap_manager = SnapProviderManager(viewport_api=viewport_api)
        # ENABLE TO WORK WITH USDRT
        # Currently selection does not return ordered fabric/all prims
        # workaround to pass tests:
        self.support_fabric = True

        if self._legacy_mode:
            self._manipulator = None
            try:
                from omni.kit.manipulator.viewport import ManipulatorFactory

                self._manipulator = ManipulatorFactory.create_manipulator(
                    TransformManipulator,
                    size=size,
                    model=self._model,
                    enabled=False,
                    gestures=[
                        PrimTranslateChangedGesture(
                            self._snap_manager, usd_context_name=usd_context_name, viewport_api=viewport_api
                        ),
                        PrimRotateChangedGesture(usd_context_name=usd_context_name, viewport_api=viewport_api),
                        PrimScaleChangedGesture(usd_context_name=usd_context_name, viewport_api=viewport_api),
                    ],
                    tool_registry=get_toolbar_registry(),
                )
            except ModuleNotFoundError:
                pass
        else:
            self._manipulator = TransformManipulator(
                size=size,
                model=self._model,
                enabled=False,
                gestures=[
                    PrimTranslateChangedGesture(
                        self._snap_manager, usd_context_name=usd_context_name, viewport_api=viewport_api
                    ),
                    PrimRotateChangedGesture(usd_context_name=usd_context_name, viewport_api=viewport_api),
                    PrimScaleChangedGesture(usd_context_name=usd_context_name, viewport_api=viewport_api),
                ],
                tool_registry=get_toolbar_registry(),
                tool_button_additional_payload={"viewport_api": viewport_api, "usd_context_name": usd_context_name},
            )

        # Hide the old C++ imguizmo when omni.ui.scene manipulator is enabled
        self._prev_transform_hidden_override = self._settings.get(TRANSFORM_GIZMO_HIDDEN_OVERRIDE)
        self._settings.set(TRANSFORM_GIZMO_HIDDEN_OVERRIDE, True)

        self._set_default_settings()
        self._create_local_global_styles()

        self._op_settings_listener = OpSettingsListener()
        self._op_settings_listener_sub = self._op_settings_listener.subscribe_listener(self._on_op_listener_changed)

        self._snap_settings_listener = SnapSettingsListener(
            enabled_setting_path=None,
            move_x_setting_path=snap_c.SNAP_TRANSLATE_SETTING_PATH,
            move_y_setting_path=snap_c.SNAP_TRANSLATE_SETTING_PATH,
            move_z_setting_path=snap_c.SNAP_TRANSLATE_SETTING_PATH,
            rotate_setting_path=snap_c.SNAP_ROTATE_SETTING_PATH,
            scale_setting_path=snap_c.SNAP_SCALE_SETTING_PATH,
            provider_setting_path=snap_c.SNAP_PROVIDER_NAME_SETTING_PATH,
        )
        self._snap_settings_listener_sub = self._snap_settings_listener.subscribe_listener(
            self._on_snap_listener_changed
        )

        if self._manipulator:
            self._enabled: bool = self._manipulator.enabled
        else:
            self._enabled = False
        self._prim_style_applied: bool = False

        self._set_style()

    def __del__(self):
        self.destroy()

    def destroy(self):
        """Cleans up resources and internal data."""
        super().destroy()

        self._op_settings_listener_sub = None
        self._snap_settings_listener_sub = None
        if self._op_settings_listener:
            self._op_settings_listener.destroy()
            self._op_settings_listener = None
        if self._manipulator:
            if self._legacy_mode:
                try:
                    from omni.kit.manipulator.viewport import ManipulatorFactory

                    ManipulatorFactory.destroy_manipulator(self._manipulator)
                except ModuleNotFoundError:
                    pass
            else:
                self._manipulator.destroy()
            self._manipulator = None
        if self._model and not self._model_is_external:
            self._model.destroy()
        self._model = None

        if self._snap_manager:
            self._snap_manager.destroy()
            self._snap_manager = None

        # restore imguizmo visibility
        self._settings.set(TRANSFORM_GIZMO_HIDDEN_OVERRIDE, self._prev_transform_hidden_override)

    @property
    def model(self) -> PrimTransformModel:
        """Gets the PrimTransformModel associated with this manipulator.

        Returns:
            :obj:`PrimTransformModel`: The model used by the manipulator."""
        return self._model

    @property
    def snap_manager(self) -> SnapProviderManager:
        """Gets the SnapProviderManager for this manipulator.

        Returns:
            :obj:`SnapProviderManager`: The snap manager used by the manipulator."""
        return self._snap_manager

    @property
    def enabled(self):
        """Gets the current enabled state of the manipulator.

        Returns:
            bool: The current enabled state."""
        if self._manipulator:
            return self._manipulator.enabled
        return False

    @enabled.setter
    def enabled(self, value: bool):
        """Sets the enabled state of the manipulator.

        Args:
            value (bool): The new enabled state to set."""
        if value != self._enabled:
            self._enabled = value
            self._update_manipulator_enable()

    def _set_default_settings(self):
        self._settings.set_default_string(transform_c.TRANSFORM_OP_SETTING, transform_c.TRANSFORM_OP_MOVE)
        self._settings.set_default_string(transform_c.TRANSFORM_MOVE_MODE_SETTING, transform_c.TRANSFORM_MODE_GLOBAL)
        self._settings.set_default_string(transform_c.TRANSFORM_ROTATE_MODE_SETTING, transform_c.TRANSFORM_MODE_GLOBAL)

    def _create_local_global_styles(self):
        COLOR_LOCAL = 0x8A248AE3

        local_style = get_default_style()
        local_style["Translate.Point"]["color"] = COLOR_LOCAL
        local_style["Rotate.Arc::screen"]["color"] = COLOR_LOCAL
        local_style["Scale.Point"]["color"] = COLOR_LOCAL

        self._styles = {
            transform_c.TRANSFORM_MODE_GLOBAL: get_default_style(),
            transform_c.TRANSFORM_MODE_LOCAL: local_style,
        }
        self._snap_styles = copy.deepcopy(self._styles)
        self._snap_styles[transform_c.TRANSFORM_MODE_GLOBAL]["Translate.Focal"]["visible"] = True
        self._snap_styles[transform_c.TRANSFORM_MODE_LOCAL]["Translate.Focal"]["visible"] = True

    def on_selection_changed(self, stage: Usd.Stage, selection: Union[List[Sdf.Path], None], *args, **kwargs) -> bool:
        """Handles selection changes in the scene.

        Args:
            stage (:obj:`Usd.Stage`): The stage where selection changed.
            selection (Union[List[:obj:`Sdf.Path`], None]): The new selection list.
            args: Variable length argument list.

        Keyword Args:
            time (float): The timestamp of the selection event.
            reason (str): The reason for the selection change.

        Returns:
            bool: Whether selection change was handled."""
        if self.model:
            if not self.model.get_da().is_ready():
                return False
        if selection is None:
            if self.model:
                self.model.on_selection_changed([])
            return False

        selection_prioterized = []
        for sdf_path in selection:
            sdf_path_prioritized = self.model.get_da().get_sdf_path_by_priority(sdf_path)
            selection_prioterized.append(sdf_path_prioritized)

        if self.model:
            # Fabric priority: if path is existing in Fabric, remove it from USD selection list
            self.model.on_selection_changed(selection_prioterized)

        for path in selection_prioterized:
            prim = self.model.get_da().get_prim_at_path(path)
            if self.model.get_da().is_a_xformable(prim):
                return True

        return False

    def _update_manipulator_enable(self) -> None:
        if not self._manipulator:
            return

        is_enabled: bool = self._prim_style_applied and self._enabled
        if not self._manipulator.enabled and is_enabled:
            self._manipulator.enabled = True
        elif self._manipulator.enabled and not is_enabled:
            self._manipulator.enabled = False

    def _set_style(self) -> None:
        if not self._manipulator:
            return

        def set_manipulator_style(styles, mode: str):
            # An unknown style will return false here.
            if mode in styles:
                self._manipulator.style = styles[mode]
                return True
            else:
                return False

        if self._op_settings_listener.selected_op == transform_c.TRANSFORM_OP_MOVE:
            styles = (
                self._snap_styles
                if self._snap_settings_listener.snap_enabled and self._snap_settings_listener.snap_to_surface
                else self._styles
            )
            self._prim_style_applied = set_manipulator_style(styles, self._op_settings_listener.translation_mode)
        elif self._op_settings_listener.selected_op == transform_c.TRANSFORM_OP_ROTATE:
            self._prim_style_applied = set_manipulator_style(self._styles, self._op_settings_listener.rotation_mode)
        elif self._op_settings_listener.selected_op == transform_c.TRANSFORM_OP_SCALE:
            self._prim_style_applied = set_manipulator_style(self._styles, transform_c.TRANSFORM_MODE_LOCAL)
        else:
            # unknown op disables.
            self._prim_style_applied = False

        self._update_manipulator_enable()

    def _on_op_listener_changed(self, type: OpSettingsListener.CallbackType, value: str):
        if (
            type == OpSettingsListener.CallbackType.OP_CHANGED
            or type == OpSettingsListener.CallbackType.TRANSLATION_MODE_CHANGED
            or type == OpSettingsListener.CallbackType.ROTATION_MODE_CHANGED
        ):
            self._set_style()

    def _on_snap_listener_changed(self, setting_val_name: str, value: str):
        if setting_val_name == "snap_enabled" or setting_val_name == "snap_to_surface":
            self._set_style()
