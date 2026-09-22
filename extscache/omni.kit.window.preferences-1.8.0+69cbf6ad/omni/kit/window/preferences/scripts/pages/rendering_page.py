import carb
import carb.settings
import omni.kit.app
import omni.ui as ui
from ..preferences_window import PreferenceBuilder, SettingType, PERSISTENT_SETTINGS_PREFIX
from typing import Any
from typing import Dict
from typing import Optional


class RenderingPreferences(PreferenceBuilder):
    def post_notification(message: str, info: bool = False, duration: int = 3):
        import omni.kit.notification_manager as nm

        if info:
            type = nm.NotificationStatus.INFO
        else:
            type = nm.NotificationStatus.WARNING

        nm.post_notification(message, status=type, duration=duration)

    def __init__(self):
        super().__init__("Rendering")

        self._persistentMultiGPUPath = PERSISTENT_SETTINGS_PREFIX + "/renderer/multiGpu/enabled"
        self._persistentOpacityMicromapPath = PERSISTENT_SETTINGS_PREFIX + "/renderer/raytracingOmm/enabled"
        self._persistentRtpt = PERSISTENT_SETTINGS_PREFIX + "/rtx/modes/rt2/enabled"
        self._persistentRt = PERSISTENT_SETTINGS_PREFIX + "/rtx/modes/rt/enabled"
        self._persistentPt = PERSISTENT_SETTINGS_PREFIX + "/rtx/modes/pt/enabled"

        settings = carb.settings.get_settings()

        self._sub_opacity_micromap_changed = omni.kit.app.SettingChangeSubscription(
            self._persistentOpacityMicromapPath,
            self._on_opacity_micromap_changed
        )

        self._sub_rtpt_changed = omni.kit.app.SettingChangeSubscription(
            self._persistentRtpt,
            self._on_renderers_changed
        )

        self._sub_rt_changed = omni.kit.app.SettingChangeSubscription(
            self._persistentRt,
            self._on_renderers_changed
        )

        self._sub_pt_changed = omni.kit.app.SettingChangeSubscription(
            self._persistentPt,
            self._on_renderers_changed
        )

        self._persistentPlaceholderTextureColorPath = PERSISTENT_SETTINGS_PREFIX + "/rtx/resourcemanager/placeholderTextureColor"
        if settings.get(self._persistentPlaceholderTextureColorPath) is None:
            settings.set_float_array(self._persistentPlaceholderTextureColorPath, [0,1,1])
        # Note: No SettingChangeSubscription because it shows the same popup like 6 times when the color is changed

        self._persistentGeometryStreamingAndCachingEnable = PERSISTENT_SETTINGS_PREFIX + "/UJITSO/geometry";
        if settings.get(self._persistentGeometryStreamingAndCachingEnable) is None:
            settings.set_default_float(self._persistentGeometryStreamingAndCachingEnable, False)

        self._sub_geometry_streaming_changed = omni.kit.app.SettingChangeSubscription(
            self._persistentGeometryStreamingAndCachingEnable,
            self._on_geometry_streaming_changed
        )

        self._enableFabricSceneDelegatePath = "/app/useFabricSceneDelegate"
        self._sub_fabric_delegate_changed = omni.kit.app.SettingChangeSubscription(
            self._enableFabricSceneDelegatePath,
            self._on_fabric_delegate_changed
        )

        self._fabricMergeSubcomponents = "/app/usdrt/population/utils/mergeSubcomponents"
        if settings.get(self._fabricMergeSubcomponents) is None:
            settings.set_default_bool(self._fabricMergeSubcomponents, False)

        self._fabricMergeInstances = "/app/usdrt/population/utils/mergeInstances"
        if settings.get(self._fabricMergeInstances) is None:
            settings.set_default_bool(self._fabricMergeInstances, False)

        self._fabricMergeMaterials = "/app/usdrt/population/utils/mergeMaterials"
        if settings.get(self._fabricMergeMaterials) is None:
            settings.set_default_bool(self._fabricMergeMaterials, True)

        self._fabricReadMaterials = "/app/usdrt/population/utils/readMaterials"
        if settings.get(self._fabricReadMaterials) is None:
            settings.set_default_bool(self._fabricReadMaterials, True)

        self._fabricReadLights = "/app/usdrt/population/utils/readLights"
        if settings.get(self._fabricReadLights) is None:
            settings.set_default_bool(self._fabricReadLights, True)

        self._fabricReadPrimvars = "/app/usdrt/population/utils/readPrimvars"
        if settings.get(self._fabricReadPrimvars) is None:
            settings.set_default_bool(self._fabricReadPrimvars, True)

        self._fabricInferDisplayColorFromMaterial = "/app/usdrt/population/utils/inferDisplayColorFromMaterial"
        if settings.get(self._fabricInferDisplayColorFromMaterial) is None:
            settings.set_default_bool(self._fabricInferDisplayColorFromMaterial, False)

        self._fabricUseHydraBlendShape = "/app/usdrt/scene_delegate/useHydraBlendShape"
        if settings.get(self._fabricUseHydraBlendShape) is None:
            settings.set_default_bool(self._fabricUseHydraBlendShape, False)

    def build(self):
        with ui.VStack(height=0):

            """ Hydra Scene Delegate """
            with self.add_frame("Fabric Scene Delegate"):
                with ui.VStack():
                    self.create_setting_widget("Enable Fabric delegate (preview feature, requires scene reload)",
                        self._enableFabricSceneDelegatePath,
                        SettingType.BOOL,
                        tooltip="Enable Fabric Hydra scene delegate for faster load times on large scenes.\n"
                                "This is a preview release of this new feature and some scene interactions will be limited.\n"
                                "You should expect faster load times and playback of USD animation.")
                    with ui.CollapsableFrame(title="Advanced Fabric Scene Delegate Settings", collapsed=True):
                        with ui.VStack():
                            self.create_setting_widget("Merge subcomponents",
                                self._fabricMergeSubcomponents,
                                SettingType.BOOL,
                                tooltip="Fabric Scene Delegate will merge all meshes within USD subcomponents.\n"
                                        "This does NOT affect the USD stage, only the Fabric representation.")
                            self.create_setting_widget("Merge instances",
                                self._fabricMergeInstances,
                                SettingType.BOOL,
                                tooltip="Fabric Scene Delegate will merge all meshes within USD scene graph instances.\n"
                                        "This does NOT affect the USD stage, only the Fabric representation.")
                            self.create_setting_widget("Merge materials",
                                self._fabricMergeMaterials,
                                SettingType.BOOL,
                                tooltip="Fabric Scene Delegate will identify unique materials and drop all duplicates.\n"
                                        "This does NOT affect the USD stage, only the Fabric representation.")
                            self.create_setting_widget("Read materials",
                                self._fabricReadMaterials,
                                SettingType.BOOL,
                                tooltip="When off, Fabric Scene Delegate will not read any material from USD, which can speed up load time.\n"
                                        "This does NOT affect the USD stage, only the Fabric representation.")
                            self.create_setting_widget("Infer displayColor from material",
                                self._fabricInferDisplayColorFromMaterial,
                                SettingType.BOOL,
                                tooltip="When on, Fabric Scene Delegate will read material info to infer mesh displayColor.\n"
                                        "This does NOT affect the USD stage, only the Fabric representation.")
                            self.create_setting_widget("Read lights",
                                self._fabricReadLights,
                                SettingType.BOOL,
                                tooltip="When off, Fabric Scene Delegate will not read any lights from USD.\n"
                                        "This does NOT affect the USD stage, only the Fabric representation.")
                            self.create_setting_widget("Read primvars",
                                self._fabricReadPrimvars,
                                SettingType.BOOL,
                                tooltip="When off, Fabric Scene Delegate will not read any mesh primvar from USD.\n"
                                        "This does NOT affect the USD stage, only the Fabric representation.")
                            self.create_setting_widget("Use Hydra BlendShape",
                                self._fabricUseHydraBlendShape,
                                SettingType.BOOL,
                                tooltip="Fabric Scene Delegate will compute hydra BlendShape.\n"
                                        "This will be effective after next stage loading.")

            self.spacer()

            """ Texture Streaming """
            with self.add_frame("Texture Streaming"):
                with ui.VStack():
                    self.create_setting_widget(
                        "Placeholder Texture Color (requires app restart)",
                        self._persistentPlaceholderTextureColorPath,
                        SettingType.COLOR3,
                        tooltip="Sets the color of the placeholder texture which is used while actual textures are loaded."
                                "\nRequires app restart to take effect."
                    )

            self.spacer()

            """ Geometry Streaming """
            with self.add_frame("RTX Geometry Streaming (experimental)"):
                with ui.VStack():
                    self.create_setting_widget(
                        "Enable geometry streaming (requires app restart)",
                        self._persistentGeometryStreamingAndCachingEnable,
                        SettingType.BOOL,
                        tooltip="This enables caching and streaming of static geometry in the RenderDelegate."
                                "\nRequires app restart to take effect."
                    )

            self.spacer()

            """ Multi-GPU """
            with self.add_frame("Multi-GPU"):
                with ui.VStack():
                    with ui.HStack(height=24):
                        self.label("Multi-GPU")

                        settings = carb.settings.get_settings()
                        mgpu = str(settings.get(self._persistentMultiGPUPath))
                        index = 0
                        if mgpu == "True":
                            index = 1
                        elif mgpu == "False":
                            index = 2
                        widget = ui.ComboBox(index, "Auto", "True", "False")
                        widget.model.add_item_changed_fn(self._on_multigpu_changed)

            self.spacer()

            # Add a setting to allow users to opt back out of any forced compatability mode setting
            if self.__check_extension_loaded("omni.kit.compatibility_mode"):
                with self.add_frame("Compatability Mode"):
                    with ui.VStack():
                        self.create_setting_widget(
                            "Enable Compatability Mode",
                            "/persistent/exts/omni.kit.compatibility_mode/forceCompatibilityMode",
                            SettingType.BOOL,
                            tooltip="Launch in compatability mode with only Storm as a renderer. (Requires restart)"
                        )

                self.spacer()

            """ Opacity MicroMap """
            with self.add_frame("Opacity MicroMap"):
                with ui.VStack():
                    self.create_setting_widget(
                        "Enable Opacity MicroMap",
                        self._persistentOpacityMicromapPath,
                        SettingType.BOOL,
                        tooltip="Opacity MicroMaps improve efficiency of rendering translucent objects."
                                "\nThis feature requires an Ada Lovelace architecture GPU."
                                "\nRequires app restart to take effect."
                    )

            self.spacer()

            """ RTX Renderers """
            with self.add_frame("RTX Renderers"):
                with ui.VStack():
                    self.create_setting_widget(
                        "Enable RTX - Real-Time 2.0",
                        self._persistentRtpt,
                        SettingType.BOOL,
                        tooltip="Enables RTX - Real-Time 2.0."
                                "\nRequires app restart to take effect."
                    )
                    self.create_setting_widget(
                        "Enable RTX - Real-Time",
                        self._persistentRt,
                        SettingType.BOOL,
                        tooltip="Enables RTX - Real-Time."
                                "\nRequires app restart to take effect."
                    )
                    self.create_setting_widget(
                        "Enable RTX - Interactive (Path Tracing)",
                        self._persistentPt,
                        SettingType.BOOL,
                        tooltip="Enables RTX - Interactive (Path Tracing)."
                                "\nRequires app restart to take effect."
                    )


    def _on_opacity_micromap_changed(self, value: bool, event_type: carb.settings.ChangeEventType):
        if event_type == carb.settings.ChangeEventType.CHANGED:
            msg = "Opacity MicroMap settings has been changed. You will need to restart Omniverse for this to take effect."
            try:
                import asyncio
                import omni.kit.notification_manager
                import omni.kit.app

                async def show_msg():
                    await omni.kit.app.get_app().next_update_async()
                    omni.kit.notification_manager.post_notification(msg, hide_after_timeout=False)

                asyncio.ensure_future(show_msg())
            except:
                carb.log_warn(msg)

    def _on_geometry_streaming_changed(self, value: bool, event_type: carb.settings.ChangeEventType):
        if event_type == carb.settings.ChangeEventType.CHANGED:
            msg = "RTX geometry streaming settings has been changed. You will need to restart Omniverse for this to take effect."
            try:
                import asyncio
                import omni.kit.notification_manager
                import omni.kit.app

                async def show_msg():
                    await omni.kit.app.get_app().next_update_async()
                    omni.kit.notification_manager.post_notification(msg, hide_after_timeout=False)

                asyncio.ensure_future(show_msg())
            except:
                carb.log_warn(msg)

    def _on_material_distilling_changed(self, value: bool, event_type: carb.settings.ChangeEventType):
        if event_type == carb.settings.ChangeEventType.CHANGED:
            msg = "Material distilling settings has been changed. You will need to restart Omniverse for this to take effect."
            try:
                import asyncio
                import omni.kit.notification_manager
                import omni.kit.app

                async def show_msg():
                    await omni.kit.app.get_app().next_update_async()
                    omni.kit.notification_manager.post_notification(msg, hide_after_timeout=False)

                asyncio.ensure_future(show_msg())
            except:
                carb.log_warn(msg)

    def _on_fabric_delegate_changed(self, value: str, event_type: carb.settings.ChangeEventType):
        import omni.usd

        if event_type == carb.settings.ChangeEventType.CHANGED:
            stage = omni.usd.get_context().get_stage()
            if not stage or stage.GetRootLayer().anonymous:
                return

            msg = "Hydra scene delegate changed. You will need to reload your stage for this to take effect."
            try:
                import asyncio
                import omni.kit.notification_manager
                import omni.kit.app

                async def show_msg():
                    await omni.kit.app.get_app().next_update_async()
                    omni.kit.notification_manager.post_notification(msg, hide_after_timeout=True, duration=2)

                asyncio.ensure_future(show_msg())
            except:
                carb.log_warn(msg)

    def _on_multigpu_changed(self, model, item):
        current_index = model.get_item_value_model().as_int
        settings = carb.settings.get_settings()
        if current_index == 0:
            # this is a string not a bool and will have no effect
            settings.set_string(self._persistentMultiGPUPath, "auto")
        elif current_index == 1:
            settings.set_bool(self._persistentMultiGPUPath, True)
        elif current_index == 2:
            settings.set_bool(self._persistentMultiGPUPath, False)

        # print restart message
        RenderingPreferences.post_notification(f"You need to restart {omni.kit.app.get_app().get_app_name()} for changes to take effect", info=True)

    def _on_renderers_changed(self, value: bool, event_type: carb.settings.ChangeEventType):
        if event_type == carb.settings.ChangeEventType.CHANGED:
            msg = "You will need to restart Omniverse for this to take effect."
            try:
                import asyncio
                import omni.kit.notification_manager
                import omni.kit.app

                async def show_msg():
                    await omni.kit.app.get_app().next_update_async()
                    omni.kit.notification_manager.post_notification(msg, hide_after_timeout=True, duration=2)

                asyncio.ensure_future(show_msg())
            except:
                carb.log_warn(msg)

    def __check_extension_loaded(self, ext_id: str):
        manager = omni.kit.app.get_app().get_extension_manager()
        for ext in manager.get_extensions():
            if ext.get("enabled") and ext.get("id").startswith(ext_id):
                return True
        return False
