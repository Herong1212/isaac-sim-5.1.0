import carb
import carb.settings
import omni.kit.app
from functools import partial
from ..preferences_window import PreferenceBuilder, PERSISTENT_SETTINGS_PREFIX, SettingType


class StagePreferences(PreferenceBuilder):
    def __init__(self):
        super().__init__("Stage")

        self._update_setting = {}

        settings = carb.settings.get_settings()

        if settings.get(PERSISTENT_SETTINGS_PREFIX + "/app/stage/timeCodeRange") is None:
            settings.set_float_array(PERSISTENT_SETTINGS_PREFIX + "/app/stage/timeCodeRange", [0, 100])

        if settings.get(PERSISTENT_SETTINGS_PREFIX + "/app/stage/timeCodesPerSecond") is None:
            settings.set_default_float(PERSISTENT_SETTINGS_PREFIX + "/app/stage/timeCodesPerSecond", 60.0)

        if settings.get(PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/PrimCreationWithDefaultXformOps") is None:
            settings.set_default_bool(
                PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/PrimCreationWithDefaultXformOps", True
            )

        if settings.get(PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/DefaultXformOpType") is None:
            settings.set_default_string(
                PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/DefaultXformOpType", "Scale, Rotate, Translate"
            )

        if settings.get(PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/DefaultRotationOrder") is None:
            settings.set_default_string(PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/DefaultRotationOrder", "XYZ")

        # OM-47905: Default camera rotation order should be YXZ.
        if settings.get(PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/DefaultCameraRotationOrder") is None:
            settings.set_default_string(PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/DefaultCameraRotationOrder", "YXZ")

        if settings.get(PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/DefaultXformOpOrder") is None:
            settings.set_default_string(
                PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/DefaultXformOpOrder",
                "xformOp:translate, xformOp:rotate, xformOp:scale",
            )

        if settings.get(PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/DefaultXformOpPrecision") is None:
            settings.set_default_string(
                PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/DefaultXformOpPrecision", "Double"
            )

        if settings.get(PERSISTENT_SETTINGS_PREFIX + "/app/stage/dragDropImport") is None:
            settings.set_default_string(
                PERSISTENT_SETTINGS_PREFIX + "/app/stage/dragDropImport", "payload"
            )

        if settings.get(PERSISTENT_SETTINGS_PREFIX + "/app/stage/nestedGprimsAuthoring") is None:
            settings.set_default_bool(
                PERSISTENT_SETTINGS_PREFIX + "/app/stage/nestedGprimsAuthoring", False
            )

        if settings.get(PERSISTENT_SETTINGS_PREFIX + "/app/stage/movePrimInPlace") is None:
            settings.set_default_int(
                PERSISTENT_SETTINGS_PREFIX + "/app/stage/movePrimInPlace", 1
            )

        if settings.get(PERSISTENT_SETTINGS_PREFIX + "/app/file/save/showSaveOptionsAutomatically") is None:
            settings.set_default_bool(
                PERSISTENT_SETTINGS_PREFIX + "/app/file/save/showSaveOptionsAutomatically", False
            )

        # OMPE-31959: Add default unicode normalization method if not set
        if settings.get(PERSISTENT_SETTINGS_PREFIX + "/app/stage/unicodeNormalizationMethod") is None:
            settings.set_default_string(
                PERSISTENT_SETTINGS_PREFIX + "/app/stage/unicodeNormalizationMethod", 'NFC'
            )

    def build(self):
        import omni.ui as ui

        """ New Stage """
        with ui.VStack(height=0):
            with self.add_frame("New Stage"):
                with ui.VStack():

                    self.create_setting_widget_combo(
                        "Default Up Axis", PERSISTENT_SETTINGS_PREFIX + "/app/stage/upAxis", ["Y", "Z"]
                    )

                    self.create_setting_widget(
                        "Default Animation Rate (TimeCodesPerSecond)",
                        PERSISTENT_SETTINGS_PREFIX + "/app/stage/timeCodesPerSecond",
                        SettingType.FLOAT
                    ).model.set_range(0.01, 999999)

                    self.create_setting_widget(
                        "Default Meters Per Unit",
                        PERSISTENT_SETTINGS_PREFIX + "/simulation/defaultMetersPerUnit",
                        SettingType.FLOAT,
                        range_from=0.001,
                        range_to=1.0,
                        speed=0.001,
                        identifier="default_meters_per_unit"
                    )

                    time_code_range_model = self.create_setting_widget(
                        "Default Time Code Range",
                        PERSISTENT_SETTINGS_PREFIX + "/app/stage/timeCodeRange",
                        SettingType.DOUBLE2,
                        immediate_mode=False
                    ).model

                    self._setup_time_code_range_constraint(time_code_range_model)

                    self.create_setting_widget(
                        "Default DefaultPrim Name",
                        PERSISTENT_SETTINGS_PREFIX + "/app/stage/defaultPrimName",
                        SettingType.STRING,
                    )
                    self.create_setting_widget_combo(
                        "Interpolation Type",
                        PERSISTENT_SETTINGS_PREFIX + "/app/stage/interpolationType",
                        ["Linear", "Held"],
                    )

                    self.create_setting_widget(
                        "Enable Static Material Network Topology",
                        "/omnihydra/staticMaterialNetworkTopology",
                        SettingType.BOOL,
                    )

                    self._create_prim_creation_settings_widgets()

            self.spacer()

            """ Authoring """
            with self.add_frame("Authoring"):
                with ui.VStack():
                    self.create_setting_widget_combo(
                        "Keep Prim World Transfrom When Reparenting",
                        PERSISTENT_SETTINGS_PREFIX + "/app/stage/movePrimInPlace",
                        {
                            "Keep Prim Transform": 0,
                            "Inherit Parent Transform": 1,
                            "Ask": 2,
                        },
                        setting_is_index=True,
                    )

                    self.create_setting_widget(
                        'Set "Instanceable" When Creating Reference',
                        PERSISTENT_SETTINGS_PREFIX + "/app/stage/instanceableOnCreatingReference",
                        SettingType.BOOL,
                    )
                    self.create_setting_widget(
                        "Transform Gizmo Manipulates Scale/Rotate/Translate Separately (New)",
                        PERSISTENT_SETTINGS_PREFIX + "/app/transform/gizmoUseSRT",
                        SettingType.BOOL,
                    )
                    self.create_setting_widget(
                        "Camera Controller Manipulates Scale/Rotate/Translate Separately (New)",
                        PERSISTENT_SETTINGS_PREFIX + "/app/camera/controllerUseSRT",
                        SettingType.BOOL,
                    )
                    self.create_setting_widget(
                        "Allow nested gprims authoring",
                        PERSISTENT_SETTINGS_PREFIX + "/app/stage/nestedGprimsAuthoring",
                        SettingType.BOOL,
                    )

                    # OMPE-31959: Add Unicode normalization method setting, default to NFC, and Disabled to disable normalization
                    widget = self.create_setting_widget_combo(
                        "Unicode Normalization Method",
                        PERSISTENT_SETTINGS_PREFIX + "/app/stage/unicodeNormalizationMethod",
                        ["NFC", "Disabled"],
                        allow_non_items=True,
                    )
                    widget.tooltip = "Select the Unicode normalization method to use when renaming prims.\n" \
                        "NFC: Use Unicode NFC normalization.\n" \
                        "Disabled: Disable normalization.\n\n" \
                        "NOTE: This only impacts renaming prim names in stage widget and property widget, and will not have an effect\n"\
                        "when the user uses Stage.DefinePrim or MovePrim kit command."

            self.spacer()

            """ Import """
            with self.add_frame("Import"):
                with ui.VStack():
                    self.create_setting_widget_combo(
                        "Drag & Drop USD Method",
                        PERSISTENT_SETTINGS_PREFIX + "/app/stage/dragDropImport",
                        ["payload", "reference"],
                    )

            self.spacer()

            """ Logging """
            with self.add_frame("Logging"):
                with ui.VStack():
                    self.create_setting_widget(
                        "Mute USD Coding Error from USD Diagnostic Manager",
                        PERSISTENT_SETTINGS_PREFIX + "/app/usd/muteUsdCodingError",
                        SettingType.BOOL,
                    )

            self.spacer()

            """ Compatibility """
            with self.add_frame("Compatibility"):
                with ui.VStack():
                    self.create_setting_widget(
                        "Support unprefixed UsdLux attributes (USD <= 20.11)",
                        PERSISTENT_SETTINGS_PREFIX + "/app/usd/usdLuxUnprefixedCompat",
                        SettingType.BOOL,
                    )

            """ Save options """
            with self.add_frame("Save options"):
                with ui.VStack():
                    self.create_setting_widget(
                        "Show save options atuomatically",
                        PERSISTENT_SETTINGS_PREFIX + "/app/file/save/showSaveOptionsAutomatically",
                        SettingType.BOOL,
                    )

    def __del__(self):
        super().__del__()
        self._update_setting = {}

    def _setup_time_code_range_constraint(self, model):
        if model is None:
            carb.log_warn("Invalid argument")
            return
        items = model.get_item_children()
        if len(items) != 2:
            carb.log_warn("Range setting expects a pair of values")
            return
        start_item, end_item = items
        init_start, init_end = (start_item.model.get_value_as_float(), end_item.model.get_value_as_float())
        # unless user has an invalid configuration already, we will keep user's
        # original configuration
        if init_start == init_end:
            init_start = init_end - 1
        elif init_start > init_end:
            init_start, init_end = init_end, init_start
        start_item.model.set_value(init_start)
        end_item.model.set_value(init_end)
        start_item.model.set_range(float("-inf"), init_end)
        end_item.model.set_range(init_start, float("inf"))
        def fn_update_start_constraint(a, item=start_item, op_item=end_item):
            op_item.model.set_range(item.model.get_value_as_float() + 1.0, float("inf"))
        def fn_update_end_constraint(a, item=end_item, op_item=start_item):
            op_item.model.set_range(float("-inf"), item.model.get_value_as_float() - 1.0)
        start_item.model.add_end_edit_fn(fn_update_start_constraint)
        end_item.model.add_end_edit_fn(fn_update_end_constraint)

    def _create_prim_creation_settings_widgets(self):

        self.create_setting_widget(
            "Start with Transform Op on Prim Creation",
            PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/PrimCreationWithDefaultXformOps",
            SettingType.BOOL,
        )

        def _on_prim_creation_with_default_xform_ops_change(item, event_type, owner):
            if event_type == carb.settings.ChangeEventType.CHANGED:
                owner._update_prim_creation_with_default_xform_ops()

        self._update_setting["PrimCreationWithDefaultXformOps"] = omni.kit.app.SettingChangeSubscription(
            PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/PrimCreationWithDefaultXformOps",
            partial(_on_prim_creation_with_default_xform_ops_change, owner=self),
        )

        widget = self.create_setting_widget_combo(
            " Default Transform Op Type",
            PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/DefaultXformOpType",
            ["Scale, Rotate, Translate", "Scale, Orient, Translate", "Transform"],
        )

        def _on_default_xform_op_type_change(item, event_type, owner):
            if event_type == carb.settings.ChangeEventType.CHANGED:
                owner._update_prim_creation_with_default_xform_ops()

        self._update_setting["DefaultXformOpType"] = omni.kit.app.SettingChangeSubscription(
            PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/DefaultXformOpType",
            partial(_on_default_xform_op_type_change, owner=self),
        )
        self._widget_default_xform_op_type = widget

        widget = self.create_setting_widget_combo(
            " Default Camera Rotation Order",
            PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/DefaultCameraRotationOrder",
            ["XYZ", "XZY", "YZX", "YXZ", "ZXY", "ZYX"],
        )
        self._widget_default_camera_rotation_order = widget

        widget = self.create_setting_widget_combo(
            " Default Rotation Order",
            PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/DefaultRotationOrder",
            ["XYZ", "XZY", "YZX", "YXZ", "ZXY", "ZYX"],
        )
        self._widget_default_rotation_order = widget

        widget = self.create_setting_widget_combo(
            " Default Xform Op Order",
            PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/DefaultXformOpOrder",
            [
                "xformOp:translate, xformOp:rotate, xformOp:scale",
                "xformOp:translate, xformOp:orient, xformOp:scale",
                "xformOp:transform",
            ],
        )
        self._widget_default_xform_op_order = widget

        widget = self.create_setting_widget_combo(
            " Default Xform Precision",
            PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/DefaultXformOpPrecision",
            ["Float", "Double"],
        )
        self._widget_default_xform_op_precision = widget

        self._update_prim_creation_with_default_xform_ops()

    def _update_prim_creation_with_default_xform_ops(self):
        settings = carb.settings.get_settings()
        if settings.get_as_bool(PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/PrimCreationWithDefaultXformOps"):
            self._widget_default_xform_op_type.enabled = True
            default_xform_ops = settings.get_as_string(
                PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/DefaultXformOpType"
            )
            if default_xform_ops == "Scale, Orient, Translate":
                self._widget_default_rotation_order.enabled = False
                self._widget_default_camera_rotation_order.enabled = False
                settings.set_string(
                    PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/DefaultXformOpOrder",
                    "xformOp:translate, xformOp:orient, xformOp:scale",
                )
            elif default_xform_ops == "Transform":
                self._widget_default_rotation_order.enabled = False
                self._widget_default_camera_rotation_order.enabled = False
                settings.set_string(
                    PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/DefaultXformOpOrder", "xformOp:transform"
                )
            else:
                self._widget_default_rotation_order.enabled = True
                self._widget_default_camera_rotation_order.enabled = True
                settings.set_string(
                    PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/DefaultXformOpOrder",
                    "xformOp:translate, xformOp:rotate, xformOp:scale",
                )

            self._widget_default_xform_op_order.enabled = False
            self._widget_default_xform_op_precision.enabled = True
        else:
            self._widget_default_xform_op_type.enabled = False
            self._widget_default_rotation_order.enabled = False
            self._widget_default_camera_rotation_order.enabled = False
            self._widget_default_xform_op_order.enabled = False
            self._widget_default_xform_op_precision.enabled = False
