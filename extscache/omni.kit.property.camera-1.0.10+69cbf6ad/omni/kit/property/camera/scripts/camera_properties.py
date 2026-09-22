import omni.ext
import omni.kit.app
from omni.kit.property.usd.usd_property_widget import (
    MultiSchemaPropertiesWidget,
    UsdPropertyUiEntry,
    create_primspec_asset,
    create_primspec_bool,
    create_primspec_float,
    create_primspec_string,
    create_primspec_token,
)
from pxr import Sdf, UsdGeom, Vt


class CameraPropertyExtension(omni.ext.IExt):
    def __init__(self):
        self._registered = False
        super().__init__()

    def on_startup(self, ext_id):
        self._register_widget()

    def on_shutdown(self):
        if self._registered:
            self._unregister_widget()

    def _register_widget(self):
        import omni.kit.window.property as p

        w = p.get_window()
        if w:
            w.register_widget(
                "prim",
                "camera",
                CameraSchemaAttributesWidget(
                    "Camera",
                    UsdGeom.Camera,
                    [],
                    [
                        "cameraProjectionType",
                        "fthetaWidth",
                        "fthetaHeight",
                        "fthetaCx",
                        "fthetaCy",
                        "openCVFx",
                        "openCVFy",
                        "fthetaMaxFov",
                        "fthetaPolyA",
                        "fthetaPolyB",
                        "fthetaPolyC",
                        "fthetaPolyD",
                        "fthetaPolyE",
                        "fthetaPolyF",
                        "p0",
                        "p1",
                        "s0",
                        "s1",
                        "s2",
                        "s3",
                        "interpupillaryDistance",  # Only required for 'omniDirectionalStereo'
                        "isLeftEye",  # Only required for 'omniDirectionalStereo'
                        "generalizedProjectionDirectionTexturePath",  # Only required for projection type 'generalizedProjection'
                        "generalizedProjectionNDCTexturePath",  # Only required for projection type 'generalizedProjection'
                        "cameraSensorType",
                        "sensorModelPluginName",
                        "sensorModelConfig",
                        "sensorModelSignals",
                        "crossCameraReferenceName",
                    ],
                    [],
                ),
            )

            self._registered = True

    def _unregister_widget(self):
        import omni.kit.window.property as p

        w = p.get_window()
        if w:
            w.unregister_widget("prim", "camera")
            self._registered = False


class CameraSchemaAttributesWidget(MultiSchemaPropertiesWidget):
    """A widget for editing and displaying camera schema attributes within a property window.

    This widget is designed to manage and display properties specific to camera schemas, including standard attributes and custom fisheye lens settings. It supports filtering attributes based on the schema, including or excluding specific ones, and adds custom schema attributes related to camera projection types and sensor models.

        Args:
            title (str): Title of the widgets on the Collapsable Frame.
            schema: The USD IsA schema or applied API schema to filter attributes.
            schema_subclasses (list): List of subclasses to include in the schema filtering.
            include_list (list, optional): List of additional schema names to add to the filter. Defaults to None.
            exclude_list (list, optional): List of schema names to remove from the filter. Defaults to None."""

    def __init__(
        self, title: str, schema, schema_subclasses: list, include_list: list = None, exclude_list: list = None
    ):
        """Initialize the widget."""
        super().__init__(
            title,
            schema,
            schema_subclasses,
            include_list if include_list else [],
            exclude_list if exclude_list else [],
            group_api_schemas=True,
        )

        # custom attributes
        cpt_tokens = Vt.TokenArray(
            9,
            (
                "pinhole",
                "pinholeOpenCV",
                "fisheyePolynomial",
                "fisheyeSpherical",
                "fisheyeKannalaBrandtK3",
                "fisheyeOpenCV",
                "fisheyeRadTanThinPrism",
                "omniDirectionalStereo",
                "generalizedProjection",
            ),
        )
        cst_tokens = Vt.TokenArray(4, ("camera", "radar", "lidar", "rtxsensor"))

        self.add_custom_schema_attribute(
            "cameraProjectionType",
            lambda p: p.IsA(UsdGeom.Camera),
            None,
            "Projection Type",
            create_primspec_token(cpt_tokens, "pinhole"),
        )
        self.add_custom_schema_attribute(
            "fthetaWidth", lambda p: p.IsA(UsdGeom.Camera), None, "", create_primspec_float(1936.0)
        )
        self.add_custom_schema_attribute(
            "fthetaHeight", lambda p: p.IsA(UsdGeom.Camera), None, "", create_primspec_float(1216.0)
        )
        self.add_custom_schema_attribute(
            "fthetaCx", lambda p: p.IsA(UsdGeom.Camera), None, "", create_primspec_float(970.942444)
        )
        self.add_custom_schema_attribute(
            "fthetaCy", lambda p: p.IsA(UsdGeom.Camera), None, "", create_primspec_float(600.374817)
        )
        self.add_custom_schema_attribute(
            "openCVFx", lambda p: p.IsA(UsdGeom.Camera), None, "", create_primspec_float(731.787878)
        )
        self.add_custom_schema_attribute(
            "openCVFy", lambda p: p.IsA(UsdGeom.Camera), None, "", create_primspec_float(731.787879)
        )
        self.add_custom_schema_attribute(
            "fthetaMaxFov", lambda p: p.IsA(UsdGeom.Camera), None, "", create_primspec_float(200.0)
        )
        self.add_custom_schema_attribute(
            "fthetaPolyA", lambda p: p.IsA(UsdGeom.Camera), None, "", create_primspec_float(0.0)
        )
        self.add_custom_schema_attribute(
            "fthetaPolyB", lambda p: p.IsA(UsdGeom.Camera), None, "", create_primspec_float(2.45417095720768e-3)
        )
        self.add_custom_schema_attribute(
            "fthetaPolyC", lambda p: p.IsA(UsdGeom.Camera), None, "", create_primspec_float(3.72747912535942e-8)
        )
        self.add_custom_schema_attribute(
            "fthetaPolyD", lambda p: p.IsA(UsdGeom.Camera), None, "", create_primspec_float(-1.43520517692508e-9)
        )
        self.add_custom_schema_attribute(
            "fthetaPolyE", lambda p: p.IsA(UsdGeom.Camera), None, "", create_primspec_float(9.76061787817672e-13)
        )
        self.add_custom_schema_attribute(
            "fthetaPolyF", lambda p: p.IsA(UsdGeom.Camera), None, "", create_primspec_float(0.0)
        )
        self.add_custom_schema_attribute(
            "p0", lambda p: p.IsA(UsdGeom.Camera), None, "", create_primspec_float(-0.0003672190538065101)
        )
        self.add_custom_schema_attribute(
            "p1", lambda p: p.IsA(UsdGeom.Camera), None, "", create_primspec_float(-0.0007413905358394097)
        )
        self.add_custom_schema_attribute(
            "s0", lambda p: p.IsA(UsdGeom.Camera), None, "", create_primspec_float(-0.0005839984838196491)
        )
        self.add_custom_schema_attribute(
            "s1", lambda p: p.IsA(UsdGeom.Camera), None, "", create_primspec_float(-0.0002193412417918993)
        )
        self.add_custom_schema_attribute(
            "s2", lambda p: p.IsA(UsdGeom.Camera), None, "", create_primspec_float(0.0001936268547567258)
        )
        self.add_custom_schema_attribute(
            "s3", lambda p: p.IsA(UsdGeom.Camera), None, "", create_primspec_float(-0.0002042473404798113)
        )
        self.add_custom_schema_attribute(
            "interpupillaryDistance", lambda p: p.IsA(UsdGeom.Camera), None, "", create_primspec_float(6.4)
        )
        self.add_custom_schema_attribute(
            "isLeftEye", lambda p: p.IsA(UsdGeom.Camera), None, "", create_primspec_bool(False)
        )
        self.add_custom_schema_attribute(
            "generalizedProjectionDirectionTexturePath",
            lambda p: p.IsA(UsdGeom.Camera),
            None,
            "",
            create_primspec_asset(),
        )
        self.add_custom_schema_attribute(
            "generalizedProjectionNDCTexturePath", lambda p: p.IsA(UsdGeom.Camera), None, "", create_primspec_asset()
        )
        self.add_custom_schema_attribute(
            "shutterTimeTexturePath", lambda p: p.IsA(UsdGeom.Camera), None, "", create_primspec_asset()
        )
        self.add_custom_schema_attribute(
            "sensorModelPluginName", lambda p: p.IsA(UsdGeom.Camera), None, "", create_primspec_string()
        )
        self.add_custom_schema_attribute(
            "sensorModelConfig", lambda p: p.IsA(UsdGeom.Camera), None, "", create_primspec_string()
        )
        self.add_custom_schema_attribute(
            "sensorModelSignals", lambda p: p.IsA(UsdGeom.Camera), None, "", create_primspec_string()
        )
        self.add_custom_schema_attribute(
            "crossCameraReferenceName", lambda p: p.IsA(UsdGeom.Camera), None, "", create_primspec_string()
        )
        self.add_custom_schema_attribute(
            "cameraSensorType",
            lambda p: p.IsA(UsdGeom.Camera),
            None,
            "Sensor Type",
            create_primspec_token(cst_tokens, "camera"),
        )

    def on_new_payload(self, payload):
        """Handles a new payload for the widget.

        Args:
            payload (dict): The new payload to be handled by the widget.
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

            cam_proj_type_attr = prim.GetAttribute("cameraProjectionType")
            if prim.IsA(UsdGeom.Camera) and cam_proj_type_attr.GetTypeName() == Sdf.ValueTypeNames.Token:
                tokens = cam_proj_type_attr.GetMetadata("allowedTokens")
                if not tokens:
                    cam_proj_type_attr.SetMetadata(
                        "allowedTokens",
                        [
                            "pinhole",
                            "pinholeOpenCV",
                            "fisheyePolynomial",
                            "fisheyeSpherical",
                            "fisheyeKannalaBrandtK3",
                            "fisheyeOpenCV",
                            "fisheyeRadTanThinPrism",
                            "omniDirectionalStereo",
                            "generalizedProjection",
                        ],
                    )

            if self.is_custom_schema_attribute_used(prim):
                used.append(None)

            cam_sensor_type_attr = prim.GetAttribute("cameraSensorType")
            if prim.IsA(UsdGeom.Camera) and cam_sensor_type_attr.GetTypeName() == Sdf.ValueTypeNames.Token:
                tokens = cam_sensor_type_attr.GetMetadata("allowedTokens")
                if not tokens:
                    cam_sensor_type_attr.SetMetadata("allowedTokens", ["camera", "radar", "lidar", "rtxsensor"])

        return used

    def _customize_props_layout(self, attrs):
        from omni.kit.property.usd.custom_layout_helper import (
            CustomLayoutFrame,
            CustomLayoutGroup,
            CustomLayoutProperty,
        )

        self.add_custom_schema_attributes_to_props(attrs)

        frame = CustomLayoutFrame(hide_extra=False)
        with frame:
            with CustomLayoutGroup("Lens"):
                CustomLayoutProperty("focalLength", "Focal Length")
                CustomLayoutProperty("focusDistance", "Focus Distance")
                CustomLayoutProperty("fStop", "fStop")
                CustomLayoutProperty("projection", "Projection")
                CustomLayoutProperty("stereoRole", "Stereo Role")

            with CustomLayoutGroup("Horizontal Aperture"):
                CustomLayoutProperty("horizontalAperture", "Aperture")
                CustomLayoutProperty("horizontalApertureOffset", "Offset")

            with CustomLayoutGroup("Vertical Aperture"):
                CustomLayoutProperty("verticalAperture", "Aperture")
                CustomLayoutProperty("verticalApertureOffset", "Offset")

            with CustomLayoutGroup("Clipping"):
                CustomLayoutProperty("clippingPlanes", "Clipping Planes")
                CustomLayoutProperty("clippingRange", "Clipping Range")

            with CustomLayoutGroup("Fisheye Lens", collapsed=True):
                CustomLayoutProperty("cameraProjectionType", "Projection Type")
                CustomLayoutProperty("fthetaWidth", "Nominal Width")
                CustomLayoutProperty("fthetaHeight", "Nominal Height")
                CustomLayoutProperty("fthetaCx", "Optical Center X")
                CustomLayoutProperty("fthetaCy", "Optical Center Y")
                CustomLayoutProperty("openCVFx", "OpenCV Fx")
                CustomLayoutProperty("openCVFy", "OpenCV Fy")
                CustomLayoutProperty("fthetaMaxFov", "Max FOV")
                CustomLayoutProperty("fthetaPolyA", "Poly k0")
                CustomLayoutProperty("fthetaPolyB", "Poly k1")
                CustomLayoutProperty("fthetaPolyC", "Poly k2")
                CustomLayoutProperty("fthetaPolyD", "Poly k3")
                CustomLayoutProperty("fthetaPolyE", "Poly k4")
                CustomLayoutProperty("fthetaPolyF", "Poly k5")
                CustomLayoutProperty("p0", "p0")
                CustomLayoutProperty("p1", "p1")
                CustomLayoutProperty("s0", "s0")
                CustomLayoutProperty("s1", "s1")
                CustomLayoutProperty("s2", "s2")
                CustomLayoutProperty("s3", "s3")
                CustomLayoutProperty("interpupillaryDistance", "Interpupillary Distance (cm)")
                CustomLayoutProperty("isLeftEye", "Is left eye")
                CustomLayoutProperty(
                    "generalizedProjectionDirectionTexturePath",
                    "Generalized Projection Direction Texture",
                )
                CustomLayoutProperty("generalizedProjectionNDCTexturePath", "Generalized Projection NDC Texture")

            with CustomLayoutGroup("Shutter", collapsed=True):
                CustomLayoutProperty("shutter:open", "Open")
                CustomLayoutProperty("shutter:close", "Close")
                CustomLayoutProperty("shutterTimeTexturePath", "Rolling Shutter Texture")

            with CustomLayoutGroup("Sensor Model", collapsed=True):
                CustomLayoutProperty("cameraSensorType", "Sensor Type")
                CustomLayoutProperty("sensorModelPluginName", "Sensor Plugin Name")
                CustomLayoutProperty("sensorModelConfig", "Sensor Config")
                CustomLayoutProperty("sensorModelSignals", "Sensor Signals")

            with CustomLayoutGroup("Synthetic Data Generation", collapsed=True):
                CustomLayoutProperty("crossCameraReferenceName", "Cross Camera Reference")

        return frame.apply(attrs)

    def get_additional_kwargs(self, ui_prop: UsdPropertyUiEntry):
        """Get additional kwargs for building the label or UI widget.

        Args:
            ui_prop (UsdPropertyUiEntry): The UI property entry to process.
        """
        additional_widget_kwargs = None
        return None, additional_widget_kwargs
