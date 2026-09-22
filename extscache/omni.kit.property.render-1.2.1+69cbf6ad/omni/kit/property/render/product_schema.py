from omni.kit.property.usd.usd_property_widget import MultiSchemaPropertiesWidget
from pxr import UsdRender


class ProductSchemaAttributesWidget(MultiSchemaPropertiesWidget):
    def on_new_payload(self, payload):
        """
        See PropertyWidget.on_new_payload
        """
        if not super().on_new_payload(payload):
            return False

        if not self._payload or len(self._payload) == 0:
            return False

        used = []
        for prim_path in self._payload:
            prim = self._get_prim(prim_path)
            if not prim or not prim.IsA(self._schema):
                return False
            used += [
                attr
                for attr in prim.GetAttributes()
                if attr.GetName() in self._schema_attr_names and not attr.IsHidden()
            ]

        return used

    def _customize_props_layout(self, attrs):
        from omni.kit.property.usd.custom_layout_helper import (
            CustomLayoutFrame,
            CustomLayoutGroup,
            CustomLayoutProperty,
        )

        frame = CustomLayoutFrame(hide_extra=False)

        with frame:
            with CustomLayoutGroup("Render Product"):
                CustomLayoutProperty("resolution", "Resolution")
                CustomLayoutProperty("camera", "Camera")
                CustomLayoutProperty("orderedVars", "Ordered Vars")

                # https://github.com/PixarAnimationStudios/USD/commit/dbbe38b94e6bf113acbb9db4c85622fe12a344a5
                if hasattr(UsdRender.Tokens, "disableMotionBlur"):
                    CustomLayoutProperty("disableMotionBlur", "Disable Motion Blur")
                if hasattr(UsdRender.Tokens, "disableDepthOfField"):
                    CustomLayoutProperty("disableDepthOfField", "Disable Depth Of Field")

        return frame.apply(attrs)
