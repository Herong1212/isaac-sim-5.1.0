# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import carb
import omni.ui as ui
from omni.kit.property.usd.usd_object_model import MetadataObjectModel
from omni.kit.property.usd.usd_property_widget import UsdPropertiesWidget, UsdPropertiesWidgetBuilder
from omni.kit.window.property.templates import HORIZONTAL_SPACING
from pxr import Kind, Usd, UsdGeom


class Constant:
    def __setattr__(self, name, value):
        raise ValueError(f"Can't change Constant.{name}")  # pragma: no cover

    FONT_SIZE = 14.0
    MIXED = "Mixed"
    MIXED_COLOR = 0xFFCC9E61


class PrimKindWidget(UsdPropertiesWidget):
    def __init__(self):
        super().__init__(title="Kind", collapsed=False, enable_adapter=True)
        self._metadata_model = None
        self._any_item_visible = False

    def on_new_payload(self, payload):
        """
        See PropertyWidget.on_new_payload
        """

        if not super().on_new_payload(payload):  # pragma: no cover
            return False  # pragma: no cover

        if len(self._payload) == 0:
            return False

        for prim_path in self._payload:  # pragma: no cover
            prim = self._get_prim(prim_path)  # pragma: no cover
            if not prim or not prim.IsA(UsdGeom.Imageable):  # pragma: no cover
                return False

        return True

    def reset(self):
        super().reset()
        if self._metadata_model:
            self._metadata_model.clean()
        self._metadata_model = None

    def build_items(self):
        super().build_items()

        # get Kinds
        all_kinds = Kind.Registry.GetAllKinds()
        all_kinds.insert(0, "")

        # http://graphics.pixar.com/usd/docs/USD-Glossary.html#USDGlossary-Kind
        # "model" is considered an abstract type and should not be assigned as any prim's kind.
        all_kinds.remove(Kind.Tokens.model)

        kind = None
        stage = self._payload.get_stage()
        for path in self._payload:
            prim = stage.GetPrimAtPath(path)
            if prim:
                prim_kind = Usd.ModelAPI(prim).GetKind()

                if kind is None:
                    kind = prim_kind
                elif kind != prim_kind:
                    kind = "mixed"
                if prim_kind not in all_kinds:  # pragma: no cover
                    all_kinds.append(prim_kind)  # pragma: no cover
                    carb.log_verbose(f"{path} has invalid Kind:{prim_kind}")  # pragma: no cover

        if kind is None:  # pragma: no cover
            return  # pragma: no cover

        if self._filter.matches("Kind"):
            self._any_item_visible = True
            highlight = self._filter.name
            with ui.HStack(spacing=HORIZONTAL_SPACING):
                UsdPropertiesWidgetBuilder.create_label("Kind", {}, {"highlight": highlight})
                with ui.ZStack():
                    self._metadata_model = MetadataObjectModel(
                        stage, list(self._payload), False, {}, key="kind", default="", options=all_kinds
                    )
                    value_widget = ui.ComboBox(self._metadata_model, name="choices")
                    mixed_overlay = UsdPropertiesWidgetBuilder.create_mixed_text_overlay()
                UsdPropertiesWidgetBuilder.create_control_state(self._metadata_model, value_widget, mixed_overlay)

    def _get_shared_properties_from_selected_prims(self, anchor_prim):
        return None

    def _get_prim(self, prim_path):
        if prim_path:
            stage = self._payload.get_stage()
            if stage:
                return stage.GetPrimAtPath(prim_path)
        return None  # pragma: no cover
