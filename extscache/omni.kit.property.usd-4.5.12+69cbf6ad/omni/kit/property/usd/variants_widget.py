# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["VariantsWidget"]

import omni.ui as ui
from pxr import Tf, Usd

from .usd_property_widget import UsdPropertiesWidget
from .usd_property_widget_builder import UsdPropertiesWidgetBuilder
from .variants_model import VariantSetModel


class VariantsWidget(UsdPropertiesWidget):
    """
    A class to represent the variants widget.
    """

    def __init__(self):
        super().__init__(title="Variants", collapsed=False, multi_edit=False, enable_adapter=True)
        self._any_item_visible = False
        self._listener = None

    def reset(self):
        """
        Resets the variants widget.
        """

        if self._listener:
            self._listener.Revoke()
            self._listener = None
        super().reset()

    def on_new_payload(self, payload):
        """
        See PropertyWidget.on_new_payload
        """

        if not super().on_new_payload(payload):
            return False

        if not self._payload:  # pragma: no cover
            return False

        for prim_path in self._payload:
            prim = self._get_prim(prim_path)

            if not prim:  # pragma: no cover
                return False

            if not prim.HasVariantSets():
                return False

        return True

    def build_items(self):
        """
        Builds the items for the variants widget.
        """

        self.reset()

        if len(self._payload) == 0:  # pragma: no cover
            return

        last_prim = self._get_prim(self._payload[-1])
        if not last_prim:  # pragma: no cover
            return

        stage = last_prim.GetStage()
        if not stage:  # pragma: no cover
            return

        self._listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, self._on_usd_changed, stage)

        vsets = last_prim.GetVariantSets()
        set_names = set(vsets.GetNames())

        # remove any lists elements that are not common
        for prim_path in self._payload:
            prim = self._get_prim(prim_path)
            set_names = set_names & set(prim.GetVariantSets().GetNames())

        with ui.VStack():
            for name in set_names:
                if self._filter.matches(name):
                    self._build_variant_set(stage, last_prim.GetPath(), name)
                    self._any_item_visible = True

    def _build_variant_set(self, stage, prim_path, name):
        """
        Builds the variant set.

        Args:
            stage: The stage.
            prim_path: The prim path.
            name: The name.
        """

        with ui.HStack():
            filter_text = self._filter.name
            UsdPropertiesWidgetBuilder.create_label(name, additional_label_kwargs={"highlight": filter_text})
            model = VariantSetModel(stage, self._payload.get_paths(), name, False)
            with ui.ZStack(alignment=ui.Alignment.CENTER):
                combo_widget = ui.ComboBox(model)
                combo_widget.identifier = f"combo_variant_{name.lower()}"
                mixed_widget = UsdPropertiesWidgetBuilder.create_mixed_text_overlay()
                mixed_widget.identifier = f"mixed_variant_{name.lower()}"

            if model.is_ambiguous():
                mixed_widget.visible = True
