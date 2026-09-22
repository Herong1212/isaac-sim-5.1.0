from functools import partial

import omni.graph.core as og
import omni.ui as ui
from omni.graph.ui import ComputeNodeWidget
from omni.kit.property.usd.usd_attribute_widget import UsdPropertyUiEntry
from pxr import Sdf, Usd


class CustomLayout:
    def __init__(self, parent_widget: ComputeNodeWidget):
        self.parent_widget = parent_widget

        # This custom layout only works with newer versions of ComputeNodeWidget.
        self.enable = hasattr(self.parent_widget, "apply_default_layout")

    def apply(self, props: list[UsdPropertyUiEntry]) -> list[UsdPropertyUiEntry] | None:
        """Use this method to modify the list of properties to be displayed."""
        # Set up things normally.
        props = self.parent_widget.apply_default_layout(props)

        # Find the prop for the enableImpulse attr.
        enable_impulse_prop = next((p for p in props if p.prop_name == "state:enableImpulse"), None)
        if enable_impulse_prop:
            # Move it to the start of the list.
            self.parent_widget.move_elements_to_beginning([enable_impulse_prop], props)
            # Put it in with the Inputs.
            enable_impulse_prop.override_display_group("Inputs")
            # Build custom UI for it.
            enable_impulse_prop.build_fn = self._build_enable_impulse_ui
        return props

    @staticmethod
    def _build_enable_impulse_ui(
        stage: Usd.Stage,
        attr_name: str,
        metadata: dict,
        property_type: type[Usd.Attribute] | type[Usd.Relationship],
        prim_paths: list[Sdf.Path],
        additional_label_kwargs: dict = None,
        additional_widget_kwargs: dict = None,
    ) -> list[ui.AbstractValueModel]:
        with ui.HStack(height=0):
            ui.Spacer()
            with ui.VStack(height=0, width=0):
                ui.Button(
                    "Send Impulse",
                    width=140,
                    height=0,
                    style={"padding": 5},
                    clicked_fn=partial(CustomLayout._on_click, attr_name, prim_paths),
                )
                ui.Spacer(height=10, width=0)
            ui.Spacer()

    @staticmethod
    def _on_click(attr_name: str, prim_paths: list[Sdf.Path]):
        for prim_path in prim_paths:
            og.Controller.attribute("state:enableImpulse", prim_path).set(True)
