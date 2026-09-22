import os
import asyncio
import omni.kit.app
import carb.settings
import omni.kit.app
import omni.ui as ui
from omni.kit.window.preferences import PreferenceBuilder, PERSISTENT_SETTINGS_PREFIX, SettingType
from ..material_config_utils import SETTING_USERALLOWLIST, SETTING_USERBLOCKLIST
from .material_config_widget import EditableListWidget
from .material_path_widget import MdlDefaultPathListWidget
from .material_path_widget import MdlCustomPathListWidget
from .render_context_widget import RenderContextWidget


class MaterialPreferences(PreferenceBuilder):
    def __init__(self):
        super().__init__("Material")

        settings = carb.settings.get_settings()

        if settings.get(PERSISTENT_SETTINGS_PREFIX + "/app/material/dragDropMaterialPath") is None:
            settings.set_default_string(PERSISTENT_SETTINGS_PREFIX + "/app/material/dragDropMaterialPath", "Relative")

        if settings.get("/app/mdl/nostdpath") is None:
            settings.set_default_bool("/app/mdl/nostdpath", False)

        PreferenceBuilder.__init__(self, "Material")

    def _show_message(self, msg:str, hide_after_timeout: bool=False):
        try:
            import omni.kit.notification_manager

            async def show_msg(msg):
                await omni.kit.app.get_app().next_update_async()
                omni.kit.notification_manager.post_notification(msg, hide_after_timeout=hide_after_timeout)

            asyncio.ensure_future(show_msg(msg))
        except:
            carb.log_warn(msg)


    def build(self):
        """ Material """
        with ui.VStack(height=0):
            """ Material """
            with self.add_frame("Material"):
                with ui.VStack():
                    self.create_setting_widget_combo(
                        "Binding Strength",
                        PERSISTENT_SETTINGS_PREFIX + "/app/stage/materialStrength",
                        ["weakerThanDescendants", "strongerThanDescendants"],
                    )
                    self.create_setting_widget_combo(
                        "Drag/Drop Path",
                        PERSISTENT_SETTINGS_PREFIX + "/app/material/dragDropMaterialPath",
                        ["Absolute", "Relative"],
                    )

            self.spacer()

            with self.add_frame("Render Context / Material Network") as frame:
                frame.set_tooltip("If a UsdShade.Material prim contains definitions for multiple contexts, this list defines the order in which those contexts are selected.")
                RenderContextWidget(self._show_message)

            self.spacer()

            """ Material Cache """
            cache_path = omni.kit.material.library.get_cache_filename()
            if not os.path.exists(cache_path):
                cache_path = "\"${cache}/material_cache.json\" not found"

            def clean_and_update(button):
                try:
                    os.remove(cache_path)
                except (OSError, FileNotFoundError):
                    pass

                button.enabled = False
                self._show_message("Material cache has been cleared.", hide_after_timeout=True)

            with self.add_frame("Material Cache"):
                with ui.VStack():
                    ui.Label(cache_path)
                    self.spacer()
                    button = ui.Button("Clear Cache", width=20, height=20, enabled=os.path.exists(cache_path))
                    button.set_clicked_fn(lambda b=button: clean_and_update(b))
                    self.spacer()

            self.spacer()

            with self.add_frame("Properties"):
                with ui.VStack():
                    settings = carb.settings.get_settings()

                    setting_path = PERSISTENT_SETTINGS_PREFIX + "/app/properties/material/displayBaseShader"

                    if settings.get(setting_path) is None:
                        settings.set_default_bool(setting_path, True)

                    args = {
                        "tooltip": "If enabled the the input parameters from the base shader(s) of the UsdShade network will be displayed under"\
                            " 'Shader' when displaying the Material prim properties."
                    }

                    self.create_setting_widget(
                        "Display Base Shader Properties on Material Prim",
                        setting_path,
                        SettingType.BOOL,
                        **args
                    )

                    # This setting provides control over which texture colorspaces are forced to "raw".
                    # It's controlled by adding the following annotation to the corresponding texture2d MDL parameter:
                    #   anno::usage("roughness")
                    # If the usage annotation is set and the value it contains is in the list specified by the mdlForceRawForUsage setting then the colorspace will be set
                    # to raw unless specifically overridden.
                    # Set in kit\kit\source\extensions\omni.kit.material.library\python\omni\kit\material\library\material_library.py
                    setting_path = PERSISTENT_SETTINGS_PREFIX + "/app/properties/material/mdlForceRawForUsage"

                    args = {
                        "tooltip": "Force the default colorspace value to 'raw' for MDL parameters of type 'texture_2d' whose annotation anno::usage values appear in this"\
                            " comma seperated list of values."
                    }

                    self.create_setting_widget(
                        "Force raw colorspace",
                        setting_path,
                        SettingType.STRING,
                        **args
                    )

            self.spacer()

            with self.add_frame("MaterialX"):
                with ui.VStack():
                    ui.Label("Changing the following requires restarting the application", style={"color":omni.ui.color.red}, alignment=ui.Alignment.LEFT)
                    materialx_settings_prefix = PERSISTENT_SETTINGS_PREFIX + f"/app/material/materialx/"

                    bool_options = [
                        ("disableDeduplication", "Disable Deduplication", "By default MDL code is generated for UsdShade networks whose topology is unique, networks with identical topology will share the same underlying MDL.  If this is enabled a unique MDL file will be created for each UsdShade network."),
                        ("exportDocument", "Export Document", "Serialize the reconstituted MaterialX document"),
                        ("validate", "Validate", "Run the MaterialX document validator on the reconstituted MaterialX document."),
                        ("serialGeneration", "Serial Generation", "By default the MaterialX MDL code generation is done in parallel by spawning tasks, if this is enabled code generation will be done serially.")
                    ]

                    for name, display_name, tooltip in bool_options:
                        setting_path = f"{materialx_settings_prefix}{name}"
                        if settings.get(setting_path) is None:
                            settings.set_default_bool(setting_path, False)

                        args = {"tooltip": tooltip}

                        self.create_setting_widget(
                            display_name,
                            setting_path,
                            SettingType.BOOL,
                            **args
                        )

                    setting_path = f"{materialx_settings_prefix}tempDirectory"
                    if settings.get(setting_path) is None:
                        settings.set_default_string(setting_path, "")

                    args = {"tooltip": "By default the MDL created by the MaterialX code generator is serialzed to a temporary location. Setting this value will result in serialized data to be written to an alternate location. Additionally the files will not be cleaned up upon application close."}

                    self.create_setting_widget(
                        "Export Directory",
                        setting_path,
                        SettingType.ASSET,
                        **args
                    )

            self.spacer()

            """ Material Search Path """
            with self.add_frame("Material Search Path"):
                with ui.VStack(height=0):
                    """ Default Paths """
                    default_path_frame = self.add_frame("Default Paths")
                    # default_path_frame.collapsed = True
                    default_path_frame.collapsed = False
                    with default_path_frame:
                        with ui.VStack():
                            self.create_setting_widget(
                                "Ignore Standard Paths",
                                "/app/mdl/nostdpath",
                                SettingType.BOOL
                            )

                            self.spacer()

                            with ui.HStack():
                                ui.Spacer(width=5)
                                self._mdl_default_paths = MdlDefaultPathListWidget()

                    self.spacer()

                    """ Custom  Paths """
                    with self.add_frame("Custom Paths (requires app restart)"):
                        self._mdl_custom_paths = MdlCustomPathListWidget()

            self.spacer()

            """ Material Graph """
            if self._isExtensionEnabled("omni.kit.window.material_graph"): # pragma: no cover
                with self.add_frame("Material Graph"):
                    with ui.VStack(height=0):
                        """ User Allow List """
                        user_allow_list_frame = self.add_frame("User Allow List")
                        with user_allow_list_frame:
                            self._user_allow_list_widget = EditableListWidget(setting_path=SETTING_USERALLOWLIST)

                        self.spacer()

                        """ User Block List """
                        user_block_list_frame = self.add_frame("User Block List")
                        with user_block_list_frame:
                            self._user_block_list_widget = EditableListWidget(setting_path=SETTING_USERBLOCKLIST)
            self.spacer()

            """ Distill and Bake """
            if self._isExtensionEnabled("omni.mdl.distill_and_bake"): # pragma: no cover
                from omni.mdl.distill_and_bake import MdlDistillAndBake
                distill = MdlDistillAndBake()
                settings = carb.settings.get_settings()
                if settings.get("/app/distill_and_bake/baking_resolution") is None:
                    settings.set_default_int("/app/distill_and_bake/baking_resolution", distill.get_baking_resolution_default())
                if settings.get("/app/distill_and_bake/baking_samples") is None:
                    settings.set_default_int("/app/distill_and_bake/baking_samples", distill.get_baking_samples_default())
                if settings.get("/app/distill_and_bake/baking_to_new_material") is None:
                    settings.set_default_bool("/app/distill_and_bake/baking_to_new_material", distill.get_baking_to_new_material_default())
                with self.add_frame("Distill and Bake"):
                    with ui.VStack():
                        self.create_setting_widget(
                            "Baking Resolution",
                            "/app/distill_and_bake/baking_resolution",
                            SettingType.INT,
                            range_from=distill.get_baking_resolution_min(),
                            range_to=distill.get_baking_resolution_max()
                            )
                        self.create_setting_widget(
                            "Baking Samples",
                            "/app/distill_and_bake/baking_samples",
                            SettingType.INT,
                            range_from=distill.get_baking_samples_min(),
                            range_to=distill.get_baking_samples_max()
                            )
                        self.create_setting_widget(
                            "Baking to new Material",
                            "/app/distill_and_bake/baking_to_new_material",
                            SettingType.BOOL
                            )


    def _isExtensionEnabled(self, name):
        manager = omni.kit.app.get_app().get_extension_manager()
        for ext in manager.get_extensions():
            if ext["name"] == name and ext["enabled"] == True:
                return True

        return False
