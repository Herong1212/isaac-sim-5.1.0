import asyncio
from functools import partial
from typing import List

import carb
import omni
import omni.ui as ui
from omni.kit.property.usd.prim_selection_payload import PrimSelectionPayload
from omni.kit.property.usd.usd_attribute_model import UsdAttributeModel
from omni.kit.property.usd.usd_property_widget import UsdPropertiesWidget, UsdPropertyUiEntry
from omni.kit.property.usd.usd_property_widget_builder import UsdPropertiesWidgetBuilder
from omni.kit.property.usd.widgets import ICON_PATH
from omni.kit.window.property.templates import (
    HORIZONTAL_SPACING,
    LABEL_HEIGHT,
    LABEL_WIDTH,
    SimplePropertyWidget,
    build_frame_header,
)
from omni.warehouse_creator.widgets.WarehouseVariantGrid import WarehouseVariantGridView
from pxr import Gf, Sdf, Tf, Usd

WAREHOUSE_TILES_VARIANTS = ["Straight", "Center", "Corner_In", "Corner_Out"]

VARIANTSET_TITLE = {
    "Straight": "Straight Walls",
    "Center": "Center Pieces",
    "Corner_In": "Corner In",
    "Corner_Out": "Corner Out",
}


class WarehouseVariantWidget(UsdPropertiesWidget):
    def __init__(self, title: str, collapsed: bool = False):
        super().__init__(title, collapsed)
        self._old_payload = []
        self.reset()
        self._request_refresh()

    def _request_refresh(self):
        """Refreshes the entire property window"""
        selection = omni.usd.get_context().get_selection()
        selected_paths = selection.get_selected_prim_paths()
        window = omni.kit.window.property.get_window()._window  # noqa: PLW0212

        selection.clear_selected_prim_paths()
        window.frame.rebuild()
        selection.set_selected_prim_paths(selected_paths, True)
        window.frame.rebuild()

    def _on_usd_changed(self, notice, stage):
        targets = notice.GetChangedInfoOnlyPaths()
        if self._old_payload != self.on_new_payload(
            self._payload
        ):  # if selection didn't change, check if attribute still exists, and force rebuild if so
            self._old_payload = self._prims
            self._request_refresh()
        else:
            super()._on_usd_changed(notice, stage)

    def _get_prim(self, prim_path):
        if prim_path:
            stage = self._payload.get_stage()
            if stage:
                prim = stage.GetPrimAtPath(prim_path)
                if prim:
                    vsets = prim.GetVariantSets().GetNames()
                    for vset in WAREHOUSE_TILES_VARIANTS:
                        if vset in vsets:
                            return prim
        return None

    def on_new_payload(self, payload):
        """
        See PropertyWidget.on_new_payload
        """

        if not super().on_new_payload(payload):
            return False

        prim_paths = self._payload.get_paths()
        prims = [self._get_prim(prim_path) for prim_path in prim_paths]
        self._prims = [p for p in prims if p is not None]
        if not self._prims:
            return False

        return self._prims

    def _variant_selection_changed(self, prims, variantset, variant):
        for prim in prims:
            vset = prim.GetVariantSet(variantset)
            vset.SetVariantSelection(variant)

    def build_items(self):
        self.reset()
        if self._collapsable_frame and not self._collapsable_frame.collapsed and self._prims:
            self._listener = Tf.Notice.Register(
                Usd.Notice.ObjectsChanged, self._on_usd_changed, self._prims[-1].GetStage()
            )
            # super().build_items()
            with ui.VStack():
                vsets = [p.GetVariantSets().GetNames() for p in self._prims]
                vsets = list(
                    set(element for sublist in vsets for element in sublist if element in WAREHOUSE_TILES_VARIANTS)
                )

                for s in vsets:
                    prims = [prim for prim in self._prims if s in prim.GetVariantSets().GetNames()]
                    with ui.CollapsableFrame(VARIANTSET_TITLE[s]):
                        WarehouseVariantGridView(
                            "NvidiaDark",
                            prims,
                            s,
                            selection_changed_fn=partial(self._variant_selection_changed, prims, s),
                        )
