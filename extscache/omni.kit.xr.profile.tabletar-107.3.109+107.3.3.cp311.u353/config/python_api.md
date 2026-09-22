# Public API for module omni.kit.xr.profile.tabletar:

## Classes

- class XRProfileCommon
  - def __init__(self)
  - def on_profile_startup(self)
  - def on_profile_shutdown(self)
  - def on_startup(self)
  - def on_shutdown(self)
  - def setup_settings_window(self, components: Any, icons: Union[None, List[str]] = None, show_message: bool = False) -> XRProfileSettingsWindow
  - def setup_zero_conf(self)
  - def set_ar_mode(self, ar_mode)
  - def disable_saving(self)
  - def get_default_render_quality_items(self) -> dict
  - def get_name(self) -> str
  - def get_extension_name(self) -> str
  - def get_profile_name(self) -> str
  - def get_profile_path(self) -> str
  - def get_persistent_path(self) -> str
  - def get_non_persistent_path(self) -> str
  - def get_scene_persistent_path(self) -> str
  - def get_profile(self) -> XRProfile
  - def get_window_name(self) -> str
  - def destroy(self)
  - def on_activate_profile(self)
  - def on_deactivate_profile(self)
  - def on_open_file(self)

- class XRMenuAdvancedFrame(XRSettingsFrame)
  - def get_frame_name(self)
  - def build_ui(self)
  - def is_advanced(self)

- class XRMenuClippingPlanesFrame(XRSettingsFrame)
  - def get_frame_name(self)
  - def build_ui(self)

- class XRMenuDesktopDisplayFrame(XRSettingsFrame)
  - def get_frame_name(self)
  - def build_ui(self)

- class XRMenuGeneralTabletARFrame(XRMenuGeneralFrame)
  - def get_frame_name(self)
  - def is_collapsable(self)

- class XRMenuMatteObjectFrame(XRSettingsFrame)
  - def get_frame_name(self)
  - def build_ui(self)

- class XRMenuNavigationFrame(XRSettingsFrame)
  - def get_frame_name(self)
  - def build_ui(self)

- class XRMenuOutputFrame(XRSettingsFrame)
  - def get_frame_name(self)
  - def build_ui(self)

- class XRMenuScalingFrame(XRSettingsFrame)
  - def get_frame_name(self)
  - def build_ui(self)

- class XRMenuSystemInfo(XRSettingsFrame)
  - def get_frame_name(self)
  - def build_ui(self)
  - def is_info(self)

- class XRMenuViewportSettingsFrame(XRSettingsFrame)
  - def get_frame_name(self)
  - def build_ui(self)

- class XRProfileTabletARExtension(XRProfileCommon, omni.ext.IExt)
  - def on_profile_startup(self)

## Other

- omni.ext: public module
- omni.ui: public module
- omni.usd: public module
